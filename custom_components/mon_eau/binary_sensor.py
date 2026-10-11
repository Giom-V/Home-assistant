# custom_components/mon_eau/binary_sensor.py
"""Capteurs binaires Mon Eau : conformité de l'eau potable, restrictions sécheresse."""
from __future__ import annotations

from datetime import timedelta
from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_KIND,
    CONF_COMMUNE,
    DOMAIN,
    MODEL_BAIGNADE,
    MODEL_EAU_POTABLE,
    MODEL_SECHERESSE,
    STALE_DAYS_EAU_POTABLE,
)
from .entity import MonEauEntity, parse_date


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinators = hass.data[DOMAIN][entry.entry_id]
    commune = entry.data[CONF_COMMUNE]
    entities: list[BinarySensorEntity] = []

    for key, coord in coordinators.items():
        if key.startswith("eau_potable"):
            reseau = coord.reseau
            entities.append(
                ConformiteBinarySensor(
                    coord,
                    entry.entry_id,
                    key,
                    f"Eau du robinet {reseau['nom']}"
                    if reseau
                    else f"Eau du robinet {commune['nom']}",
                    MODEL_EAU_POTABLE,
                )
            )
        elif key == "secheresse":
            entities.append(
                RestrictionsBinarySensor(
                    coord,
                    entry.entry_id,
                    "secheresse",
                    f"Sécheresse {commune['nom']}",
                    MODEL_SECHERESSE,
                )
            )
        elif key.startswith("baignade_"):
            site = coord.site
            entities.append(
                BaignadeBinarySensor(
                    coord,
                    entry.entry_id,
                    f"baignade_{site['site']}",
                    f"Baignade {site['libelle']}",
                    MODEL_BAIGNADE,
                )
            )

    async_add_entities(entities)


class ConformiteBinarySensor(MonEauEntity, BinarySensorEntity):
    """PROBLEM : on = eau non conforme au dernier prélèvement."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "conformite", device_model
        )

    @property
    def is_on(self) -> bool | None:
        conforme = (self.coordinator.data or {}).get("conforme")
        return None if conforme is None else not conforme

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        date = parse_date(data.get("date_prelevement"))
        anciennes = (
            date is not None
            and dt_util.utcnow() - date > timedelta(days=STALE_DAYS_EAU_POTABLE)
        )
        return {
            ATTR_KIND: "conformite",
            "conclusion": data.get("conclusion"),
            "conformites": data.get("conformites"),
            "date_prelevement": data.get("date_prelevement"),
            "donnees_anciennes": anciennes,
            "source": data.get("source"),
            "reseau": data.get("reseau"),
            "distributeur": data.get("distributeur"),
        }


class BaignadeBinarySensor(MonEauEntity, BinarySensorEntity):
    """PROBLEM : on = interdiction ou dernier contrôle mauvais."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "baignade", device_model
        )

    @property
    def is_on(self) -> bool | None:
        data = self.coordinator.data or {}
        if data.get("interdiction"):
            return True
        dernier = data.get("dernier_controle")
        if not dernier:
            return None if data.get("en_saison") else False
        return (dernier.get("qualite") or "").lower().startswith("mauvais")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {
            ATTR_KIND: "baignade",
            "en_saison": data.get("en_saison"),
            "interdiction": data.get("interdiction"),
            "qualite_dernier_controle": (data.get("dernier_controle") or {}).get("qualite"),
        }


class RestrictionsBinarySensor(MonEauEntity, BinarySensorEntity):
    """PROBLEM : on = restrictions d'usage en vigueur (alerte ou plus)."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(self, coordinator, entry_id, device_key, device_name, device_model) -> None:
        super().__init__(
            coordinator, entry_id, device_key, device_name, "restrictions", device_model
        )

    @property
    def is_on(self) -> bool | None:
        gravite = (self.coordinator.data or {}).get("gravite")
        if gravite is None:
            return None
        return gravite in ("alerte", "alerte_renforcee", "crise")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        data = self.coordinator.data or {}
        return {ATTR_KIND: "restrictions", "gravite": data.get("gravite")}
