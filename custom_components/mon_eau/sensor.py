# custom_components/mon_eau/sensor.py
"""Capteurs Mon Eau. Chacun expose `mon_eau_kind` (lu par les cartes) et la date
de sa mesure."""
from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_KIND,
    CONF_COMMUNE,
    CONF_HYDRO,
    DOMAIN,
    GRAVITE_AUCUNE,
    GRAVITE_ORDRE,
    MODEL_BAIGNADE,
    MODEL_EAU_POTABLE,
    MODEL_NAPPE,
    MODEL_RIVIERE,
    MODEL_SECHERESSE,
    SITUATIONS_HYDRO,
    TENDANCE_ETATS,
)
from .entity import MonEauEntity, parse_date

VIGICRUES_SITE = "https://www.vigicrues.gouv.fr"


def device_riviere_principal(data: dict) -> tuple[str, str, str] | None:
    """Device de la première station hydro — la santé rivière s'y rattache."""
    hydros = data.get(CONF_HYDRO) or []
    if not hydros:
        return None
    hydro = hydros[0]
    return (f"riviere_{hydro['code']}", f"Rivière {hydro['libelle']}", MODEL_RIVIERE)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]
    data = entry.data
    commune = data[CONF_COMMUNE]
    entities: list[SensorEntity] = []

    for key, coord in coordinators.items():
        if key.startswith("eau_potable"):
            reseau = coord.reseau
            device = (
                key,
                f"Eau du robinet {reseau['nom']}" if reseau else f"Eau du robinet {commune['nom']}",
                MODEL_EAU_POTABLE,
            )
            entities.append(DernierPrelevementSensor(coord, entry.entry_id, *device))
            entities += [
                EauPotableParametreSensor(coord, entry.entry_id, *device, kind=kind, unit=unit)
                for kind, unit in (
                    ("nitrates", "mg/L"),
                    ("pesticides", "µg/L"),
                    ("e_coli", "n/(100mL)"),
                    ("enterocoques", "n/(100mL)"),
                )
            ]

        elif key.startswith("hydro_"):
            station = coord.station
            device = (f"riviere_{station['code']}", f"Rivière {station['libelle']}", MODEL_RIVIERE)
            grandeurs = station.get("grandeurs") or ["H", "Q"]
            if "H" in grandeurs:
                entities.append(HydroSensor(coord, entry.entry_id, *device, kind="hauteur", unit="m"))
                entities.append(
                    TendanceSensor(
                        coord, entry.entry_id, *device,
                        key="tendance_hauteur", horizon="h24",
                        getter=lambda d: d.get("tendances_hauteur"),
                    )
                )
            if "Q" in grandeurs:
                entities.append(HydroSensor(coord, entry.entry_id, *device, kind="debit", unit="m³/s"))
                entities.append(SituationHydrologiqueSensor(coord, entry.entry_id, *device))
            entities.append(
                FraicheurSensor(
                    coord, entry.entry_id, *device,
                    key="derniere_mesure_riviere", kind="fraicheur_hydro",
                    getter=lambda d: d.get("date_hauteur") or d.get("date_debit"),
                )
            )
            if coord.troncon:
                entities.append(VigilanceCruesSensor(coord, entry.entry_id, *device))

        elif key == "temperature":
            device = device_riviere_principal(data) or (
                "riviere_sante", f"Rivière {coord.station['libelle']}", MODEL_RIVIERE
            )
            entities.append(TemperatureContinueSensor(coord, entry.entry_id, *device))

        elif key == "qualite":
            device = device_riviere_principal(data) or (
                "riviere_sante", f"Rivière {coord.station['libelle']}", MODEL_RIVIERE
            )
            if "temperature" not in coordinators:
                entities.append(
                    QualiteSensor(
                        coord, entry.entry_id, *device,
                        key="temperature_eau", kind="temperature",
                        unit=UnitOfTemperature.CELSIUS,
                        device_class=SensorDeviceClass.TEMPERATURE,
                    )
                )
            entities.append(
                QualiteSensor(coord, entry.entry_id, *device, key="oxygene", kind="oxygene", unit="mg/L")
            )
            entities.append(
                QualiteSensor(coord, entry.entry_id, *device, key="ph", kind="ph", unit=None)
            )
            entities.append(
                QualiteSensor(
                    coord, entry.entry_id, *device,
                    key="nitrates_riviere", kind="nitrates_riviere", unit="mg/L",
                )
            )
            entities.append(
                FraicheurSensor(
                    coord, entry.entry_id, *device,
                    key="dernier_releve_sante", kind="fraicheur_sante",
                    getter=_date_sante,
                )
            )

        elif key.startswith("nappe_"):
            piezo = coord.piezo
            device = (f"nappe_{piezo['code_bss']}", f"Nappe {piezo['libelle']}", MODEL_NAPPE)
            entities.append(NappeSensor(coord, entry.entry_id, *device, kind="profondeur_nappe"))
            entities.append(NappeSensor(coord, entry.entry_id, *device, kind="niveau_ngf"))
            # Une nappe bouge lentement : l'état porte sur 7 jours
            entities.append(
                TendanceSensor(
                    coord, entry.entry_id, *device,
                    key="tendance_nappe", horizon="j7",
                    getter=lambda d: d.get("tendances"),
                )
            )
            entities.append(SituationNappeSensor(coord, entry.entry_id, *device))
            entities.append(RemplissageNappeSensor(coord, entry.entry_id, *device))
            entities.append(
                FraicheurSensor(
                    coord, entry.entry_id, *device,
                    key="derniere_mesure_nappe", kind="fraicheur_nappe",
                    getter=lambda d: d.get("date"),
                )
            )

        elif key == "secheresse":
            device = ("secheresse", f"Sécheresse {commune['nom']}", MODEL_SECHERESSE)
            entities.append(GraviteSecheresseSensor(coord, entry.entry_id, *device))
            entities.append(
                FraicheurSensor(
                    coord, entry.entry_id, *device,
                    key="dernier_arrete", kind="fraicheur_secheresse",
                    getter=_date_arrete,
                )
            )

        elif key.startswith("baignade_"):
            site = coord.site
            device = (f"baignade_{site['site']}", f"Baignade {site['libelle']}", MODEL_BAIGNADE)
            entities.append(ClassementBaignadeSensor(coord, entry.entry_id, *device))
            entities.append(DernierControleBaignadeSensor(coord, entry.entry_id, *device))

    async_add_entities(entities)


# ======================================================================
# Fraîcheur des données (un capteur timestamp par groupe)
# ======================================================================

class FraicheurSensor(MonEauEntity, SensorEntity):
    """Date de la donnée la plus récente du groupe."""

    _attr_device_class = SensorDeviceClass.TIMESTAMP
    _attr_icon = "mdi:clock-check-outline"

    def __init__(
        self, coordinator, entry_id, device_key, device_name, device_model, key, kind, getter
    ) -> None:
        super().__init__(coordinator, entry_id, device_key, device_name, key, device_model)
        self._kind = kind
        self._getter = getter

    @property
    def native_value(self):
        try:
            return parse_date(self._getter(self.coordinator.data or {}))
        except (KeyError, TypeError, ValueError):
            return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {ATTR_KIND: self._kind}


def _date_sante(data: dict) -> str | None:
    dates = [m.get("date") for m in data.values() if isinstance(m, dict) and m.get("date")]
    return max(dates) if dates else None


def _date_arrete(data: dict) -> str | None:
    dates = [
        z.get("arrete_debut")
        for z in (data.get("par_type") or {}).values()
        if z.get("arrete_debut")
    ]
    return max(dates) if dates else None


# ======================================================================
# Eau potable
# ======================================================================

class DernierPrelevementSensor(MonEauEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "dernier_prelevement", device_model
        )

    @property
    def native_value(self):
        return parse_date((self.coordinator.data or {}).get("date_prelevement"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            ATTR_KIND: "prelevement",
            "source": data.get("source"),
            "reseau": data.get("reseau"),
            "distributeur": data.get("distributeur"),
        }


class EauPotableParametreSensor(MonEauEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator, entry_id, device_key, device_name, device_model, kind: str, unit: str
    ) -> None:
        super().__init__(coordinator, entry_id, device_key, device_name, kind, device_model)
        self._kind = kind
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = {
            "nitrates": "mdi:molecule",
            "pesticides": "mdi:flask-outline",
            "e_coli": "mdi:bacteria-outline",
            "enterocoques": "mdi:bacteria-outline",
        }[kind]

    def _mesure(self) -> dict:
        return ((self.coordinator.data or {}).get("parametres") or {}).get(self._kind) or {}

    @property
    def native_value(self):
        return self._mesure().get("valeur")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        mesure = self._mesure()
        return {
            ATTR_KIND: self._kind,
            "resultat_texte": mesure.get("texte"),
            "limite": mesure.get("limite"),
            "limite_texte": mesure.get("limite_texte"),
            "date_prelevement": mesure.get("date"),
            "source": mesure.get("source"),
        }


# ======================================================================
# Rivière
# ======================================================================

class HydroSensor(MonEauEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator, entry_id, device_key, device_name, device_model, kind: str, unit: str
    ) -> None:
        super().__init__(coordinator, entry_id, device_key, device_name, kind, device_model)
        self._kind = kind
        self._attr_native_unit_of_measurement = unit
        self._attr_icon = "mdi:waves" if kind == "hauteur" else "mdi:water-pump"

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get(self._kind)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        attrs = {
            ATTR_KIND: self._kind,
            "date_observation": data.get(f"date_{self._kind}"),
            "station": self.coordinator.station.get("libelle"),
        }
        if self._kind == "debit":
            attrs["normales"] = data.get("normales")
            attrs["rapport_normale"] = data.get("rapport_normale")
            attrs["situation"] = data.get("situation")
        elif self._kind == "hauteur":
            attrs["tendances"] = data.get("tendances_hauteur")
        return attrs


class TendanceSensor(MonEauEntity, SensorEntity):
    """Monte/descend/stable et vitesse, sur l'horizon adapté à la dynamique du milieu."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = TENDANCE_ETATS

    @property
    def icon(self) -> str:
        etat = self.native_value or ""
        if etat.startswith("monte"):
            return "mdi:trending-up"
        if etat.startswith("descend"):
            return "mdi:trending-down"
        return "mdi:trending-neutral"

    def __init__(
        self, coordinator, entry_id, device_key, device_name, device_model, key, horizon, getter
    ) -> None:
        super().__init__(coordinator, entry_id, device_key, device_name, key, device_model)
        self._horizon = horizon
        self._getter = getter

    def _tendances(self) -> dict | None:
        return self._getter(self.coordinator.data or {})

    @property
    def native_value(self):
        tendance = (self._tendances() or {}).get(self._horizon)
        if not tendance:
            return None
        if tendance["direction"] == "stable":
            return "stable"
        return f"{tendance['direction']}_{tendance.get('vitesse') or 'lente'}"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        tendances = self._tendances() or {}
        return {
            ATTR_KIND: "tendance",
            "horizon": self._horizon,
            "delta_m": (tendances.get(self._horizon) or {}).get("delta_m"),
            "tendances": tendances,
        }


class SituationHydrologiqueSensor(MonEauEntity, SensorEntity):
    """Débit actuel comparé aux percentiles saisonniers sur 15 ans."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = SITUATIONS_HYDRO
    _attr_icon = "mdi:chart-bell-curve"

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "situation_hydrologique", device_model
        )

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("situation")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            ATTR_KIND: "situation",
            "normales": data.get("normales"),
            "rapport_normale": data.get("rapport_normale"),
        }


class VigilanceCruesSensor(MonEauEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["verte", "jaune", "orange", "rouge"]
    _attr_translation_key = "vigilance_crues"
    _attr_icon = "mdi:shield-alert-outline"

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "vigilance_crues", device_model
        )

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("vigilance")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            ATTR_KIND: "vigilance",
            "niveau": data.get("vigilance_niveau"),
            "troncon": data.get("troncon"),
            "prevision": data.get("prevision"),
            "bulletin_url": VIGICRUES_SITE,
        }


class TemperatureContinueSensor(MonEauEntity, SensorEntity):
    """Température de l'API continue (stations rares, temps réel)."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "temperature_eau", device_model
        )

    @property
    def native_value(self):
        valeur = (self.coordinator.data or {}).get("valeur")
        return round(valeur, 1) if valeur is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            ATTR_KIND: "temperature",
            "date_mesure": (self.coordinator.data or {}).get("date"),
            "source": "temperature_continue",
            "station": self.coordinator.station.get("libelle"),
        }


class QualiteSensor(MonEauEntity, SensorEntity):
    """Mesure « santé rivière » : ponctuelle, publiée en différé."""

    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        coordinator,
        entry_id,
        device_key,
        device_name,
        device_model,
        key: str,
        kind: str,
        unit: str | None,
        device_class: SensorDeviceClass | None = None,
    ) -> None:
        super().__init__(coordinator, entry_id, device_key, device_name, key, device_model)
        self._kind = kind
        self._attr_native_unit_of_measurement = unit
        if device_class:
            self._attr_device_class = device_class
        if kind == "ph":
            self._attr_icon = "mdi:ph"
        elif kind == "oxygene":
            self._attr_icon = "mdi:gas-cylinder"

    def _mesure(self) -> dict:
        # Le coordinator qualité indexe par kind court ("temperature", "nitrates"...)
        kind_court = "nitrates" if self._kind == "nitrates_riviere" else self._kind
        return (self.coordinator.data or {}).get(kind_court) or {}

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success and bool(self._mesure())

    @property
    def native_value(self):
        return self._mesure().get("valeur")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        mesure = self._mesure()
        return {
            ATTR_KIND: self._kind,
            "date_mesure": mesure.get("date"),
            "source": "qualite_rivieres",
            "station": self.coordinator.station.get("libelle"),
        }


# ======================================================================
# Nappe phréatique
# ======================================================================

class NappeSensor(MonEauEntity, SensorEntity):
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "m"

    def __init__(
        self, coordinator, entry_id, device_key, device_name, device_model, kind: str
    ) -> None:
        super().__init__(coordinator, entry_id, device_key, device_name, kind, device_model)
        self._kind = kind
        self._attr_icon = (
            "mdi:arrow-collapse-down" if kind == "profondeur_nappe" else "mdi:altimeter"
        )

    @property
    def native_value(self):
        cle = "profondeur" if self._kind == "profondeur_nappe" else "niveau_ngf"
        valeur = (self.coordinator.data or {}).get(cle)
        return round(valeur, 2) if valeur is not None else None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            ATTR_KIND: self._kind,
            "date_mesure": data.get("date"),
            "temps_reel": data.get("temps_reel"),
            "code_bss": self.coordinator.piezo.get("code_bss"),
            "tendances": data.get("tendances"),  # sur le niveau : monte = recharge
            "situation": data.get("situation"),
            "ecart_normale_m": data.get("ecart_normale_m"),
        }


class RemplissageNappeSensor(MonEauEntity, SensorEntity):
    """Position du niveau dans la plage historique observée (0 % = record bas)."""

    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"
    _attr_icon = "mdi:water-percent"

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "remplissage_nappe", device_model
        )

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("remplissage")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        plage = data.get("plage") or {}
        return {
            ATTR_KIND: "remplissage",
            "niveau_min_historique_m": plage.get("min"),
            "niveau_max_historique_m": plage.get("max"),
        }


class SituationNappeSensor(MonEauEntity, SensorEntity):
    """Niveau actuel comparé aux percentiles saisonniers du piézomètre."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = SITUATIONS_HYDRO
    _attr_icon = "mdi:chart-bell-curve"

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "situation_nappe", device_model
        )

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("situation")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            ATTR_KIND: "situation",
            "normales": data.get("normales"),
            "ecart_normale_m": data.get("ecart_normale_m"),
        }


# ======================================================================
# Baignade
# ======================================================================

class ClassementBaignadeSensor(MonEauEntity, SensorEntity):
    """Classement européen du site (année précédente, le plus récent disponible)."""

    _attr_icon = "mdi:swim"

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "classement_baignade", device_model
        )

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("classement")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            ATTR_KIND: "classement",
            "annee_classement": data.get("annee_classement"),
            "classement_annee_en_cours": data.get("classement_annee"),
            "historique": data.get("historique_classements"),
            "saison_debut": data.get("saison_debut"),
            "saison_fin": data.get("saison_fin"),
            "en_saison": data.get("en_saison"),
            "interdiction": data.get("interdiction"),
        }


class DernierControleBaignadeSensor(MonEauEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "dernier_controle_baignade",
            device_model,
        )

    def _dernier(self) -> dict:
        return (self.coordinator.data or {}).get("dernier_controle") or {}

    @property
    def native_value(self):
        return parse_date(self._dernier().get("date"))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        dernier = self._dernier()
        return {
            ATTR_KIND: "controle",
            "qualite": dernier.get("qualite"),
            "e_coli": dernier.get("e_coli"),
            "enterocoques": dernier.get("enterocoques"),
            "controles": [
                {"date": c.get("date"), "qualite": c.get("qualite")}
                for c in data.get("controles") or []
            ],
        }


# ======================================================================
# Sécheresse
# ======================================================================

class GraviteSecheresseSensor(MonEauEntity, SensorEntity):
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [GRAVITE_AUCUNE, *GRAVITE_ORDRE]
    _attr_icon = "mdi:water-alert-outline"

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "gravite_secheresse", device_model
        )

    @property
    def native_value(self):
        return (self.coordinator.data or {}).get("gravite")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            ATTR_KIND: "gravite",
            "par_type": data.get("par_type"),
            "usages": data.get("usages"),
            "onde": data.get("onde"),
        }
