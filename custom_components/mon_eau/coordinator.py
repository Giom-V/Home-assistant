# custom_components/mon_eau/coordinator.py
"""Coordinators Mon Eau — un par source, intervalles adaptés à la fraîcheur réelle."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from . import api
from .const import (
    DIS_PARAMS,
    GRAVITE_ORDRE,
    GRAVITE_AUCUNE,
    RIVER_QUALITY_PARAMS,
    SCAN_BAIGNADE_HORS_SAISON,
    SCAN_BAIGNADE_SAISON,
    SCAN_EAU_POTABLE,
    NORMALES_ANNEES,
    NORMALES_FENETRE_JOURS,
    SCAN_HYDRO,
    SCAN_NAPPE,
    SCAN_NORMALES,
    SCAN_QUALITE,
    SCAN_SECHERESSE,
    SCAN_TEMP_CONTINUE,
    SCAN_TENDANCES,
    SCAN_VIGILANCE,
    TENDANCE_HORIZONS,
    VIGIEAU_TYPES,
    VIGILANCE_LEVELS,
)

_LOGGER = logging.getLogger(__name__)


class MonEauCoordinator(DataUpdateCoordinator):
    """Base commune : session partagée + nom préfixé."""

    def __init__(self, hass: HomeAssistant, name: str, scan_seconds: int) -> None:
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name=f"Mon Eau {name}",
            update_interval=timedelta(seconds=scan_seconds),
        )


# ======================================================================
# Eau potable — hybride orobnat (frais) + Hub'eau (fondation)
# ======================================================================

class EauPotableCoordinator(MonEauCoordinator):
    def __init__(self, hass: HomeAssistant, commune: dict, reseau: dict | None) -> None:
        super().__init__(hass, "eau potable", SCAN_EAU_POTABLE)
        self.commune = commune
        self.reseau = reseau

    async def _async_update_data(self) -> dict[str, Any]:
        rows = await api.dis_derniers_resultats(
            self.session, self.commune["code"], (self.reseau or {}).get("code")
        )
        data = self._depuis_hubeau(rows)

        # Surcouche ARS (plus fraîche, nécessite un réseau précis), repli silencieux
        if self.reseau:
            try:
                bulletin = await api.orobnat_dernier_bulletin(
                    self.session,
                    self.commune["region"],
                    self.commune["departement"],
                    self.commune["code"],
                    self.reseau["code"],
                )
            except Exception:
                _LOGGER.debug("orobnat: échec du scraping, repli Hub'eau", exc_info=True)
                bulletin = None
            if bulletin:
                data = self._fusionner_orobnat(data, bulletin)
        return data

    def _depuis_hubeau(self, rows: list[dict]) -> dict[str, Any]:
        if not rows:
            raise UpdateFailed("Aucun résultat eau potable pour cette commune/ce réseau")

        dernier = rows[0]  # tri desc : première ligne = dernier prélèvement
        parametres: dict[str, dict] = {}
        for row in rows:
            kind = DIS_PARAMS.get(row.get("code_parametre") or "")
            if not kind or kind in parametres:
                continue
            parametres[kind] = {
                "valeur": api.to_float(row.get("resultat_numerique")),
                "texte": row.get("resultat_alphanumerique"),
                "unite": row.get("libelle_unite"),
                "limite": api.parse_limite(row.get("limite_qualite_parametre")),
                "limite_texte": row.get("limite_qualite_parametre"),
                "date": row.get("date_prelevement"),
                "source": "hubeau",
            }

        conformites = {
            "limites_bacteriologie": dernier.get("conformite_limites_bact_prelevement"),
            "limites_physico_chimie": dernier.get("conformite_limites_pc_prelevement"),
            "references_bacteriologie": dernier.get("conformite_references_bact_prelevement"),
            "references_physico_chimie": dernier.get("conformite_references_pc_prelevement"),
        }
        conclusion = dernier.get("conclusion_conformite_prelevement")
        conforme: bool | None = None
        if conformites["limites_bacteriologie"] or conformites["limites_physico_chimie"]:
            conforme = conformites["limites_bacteriologie"] != "N" and conformites[
                "limites_physico_chimie"
            ] != "N"
        elif conclusion:
            conforme = "non conforme" not in conclusion.lower()

        return {
            "date_prelevement": dernier.get("date_prelevement"),
            "source": "hubeau",
            "conforme": conforme,
            "conclusion": conclusion,
            "conformites": conformites,
            "distributeur": api.joli_libelle(dernier.get("nom_distributeur")),
            "reseau": (self.reseau or {}).get("nom"),
            "parametres": parametres,
        }

    @staticmethod
    def _fusionner_orobnat(data: dict, bulletin: dict) -> dict:
        """Le bulletin ARS plus récent fournit verdict, date et valeurs parsées."""
        date_ars = (bulletin.get("date_prelevement") or "")[:19]
        date_hubeau = (data.get("date_prelevement") or "")[:19]
        if not date_ars or date_ars <= date_hubeau:
            return data

        data = dict(data)
        data["date_prelevement"] = bulletin["date_prelevement"]
        data["source"] = "ars_orobnat"
        if bulletin.get("conforme") is not None:
            data["conforme"] = bulletin["conforme"]
        if bulletin.get("conclusion"):
            data["conclusion"] = bulletin["conclusion"]
        oui_non = {True: "C", False: "N"}
        conformites = dict(data.get("conformites") or {})
        if bulletin.get("conformite_bacteriologie") is not None:
            conformites["limites_bacteriologie"] = oui_non[bulletin["conformite_bacteriologie"]]
        if bulletin.get("conformite_physico_chimie") is not None:
            conformites["limites_physico_chimie"] = oui_non[bulletin["conformite_physico_chimie"]]
        data["conformites"] = conformites

        parametres = dict(data["parametres"])
        for kind, mesure in (bulletin.get("parametres") or {}).items():
            ancien = parametres.get(kind, {})
            parametres[kind] = {
                **ancien,
                "valeur": mesure["valeur"],
                "texte": mesure.get("texte"),
                "date": mesure.get("date"),
                "source": "ars_orobnat",
            }
        data["parametres"] = parametres
        return data


# ======================================================================
# Rivière — hydrométrie temps réel + vigilance crues
# ======================================================================

class HydroCoordinator(MonEauCoordinator):
    def __init__(self, hass: HomeAssistant, hydro: dict, troncon: dict | None) -> None:
        super().__init__(hass, "hydrométrie", SCAN_HYDRO)
        self.station = hydro
        self.troncon = troncon
        self._vigilance: dict[str, Any] = {}
        self._vigilance_maj: datetime | None = None
        self._normales: dict | None = None
        self._normales_maj: datetime | None = None
        self._tendances: dict | None = None
        self._tendances_maj: datetime | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        data = await api.hydro_dernieres_observations(self.session, self.station["code"])
        if data["hauteur"] is None and data["debit"] is None:
            raise UpdateFailed("Aucune observation hydrométrique récente")

        data["vigilance_niveau"] = None
        data["vigilance"] = None
        data["troncon"] = (self.troncon or {}).get("libelle")
        data["prevision"] = None

        if self.troncon:
            await self._rafraichir_vigilance()
            data.update(self._vigilance)
            # Prévision Vigicrues : vide hors épisode
            if (data.get("vigilance_niveau") or 1) >= 2:
                data["prevision"] = await api.vigicrues_prevision(
                    self.session, self.station["code"]
                )

        grandeurs = self.station.get("grandeurs") or ["H", "Q"]
        if "Q" in grandeurs:
            await self._rafraichir_normales()
            data["normales"] = self._normales
            if self._normales and data["debit"] is not None:
                data["situation"] = api.situation_hydrologique(data["debit"], self._normales)
                data["rapport_normale"] = round(
                    data["debit"] / self._normales["normale"] * 100
                )
            else:
                data["situation"] = None
                data["rapport_normale"] = None
        if "H" in grandeurs:
            await self._rafraichir_tendances()
            data["tendances_hauteur"] = self._tendances
        return data

    async def _rafraichir_normales(self) -> None:
        """Percentiles saisonniers sur NORMALES_ANNEES d'historique QmnJ (hebdomadaire)."""
        now = dt_util.utcnow()
        if self._normales_maj and (now - self._normales_maj).total_seconds() < SCAN_NORMALES:
            return
        date_min = (dt_util.now() - timedelta(days=NORMALES_ANNEES * 365)).strftime("%Y-%m-%d")
        try:
            debits = await api.hydro_debits_journaliers(
                self.session, self.station["code"], date_min
            )
        except api.MonEauApiError as err:
            _LOGGER.debug("Débits journaliers indisponibles: %s", err)
            self._normales_maj = now  # inutile de réessayer à chaque refresh
            return
        aujourd_hui = dt_util.now()
        jour_annee = (aujourd_hui.month - 1) * 30.44 + aujourd_hui.day
        self._normales = api.stats_normales(debits, jour_annee, NORMALES_FENETRE_JOURS)
        self._normales_maj = now

    async def _rafraichir_tendances(self) -> None:
        """Tendances de hauteur 24 h / 7 j / 15 j (toutes les SCAN_TENDANCES secondes)."""
        now = dt_util.utcnow()
        if self._tendances_maj and (now - self._tendances_maj).total_seconds() < SCAN_TENDANCES:
            return
        date_min = (now - timedelta(days=16)).strftime("%Y-%m-%dT%H:%M:%S")
        try:
            points = await api.hydro_hauteurs_periode(
                self.session, self.station["code"], date_min
            )
        except api.MonEauApiError as err:
            _LOGGER.debug("Hauteurs 15 j indisponibles: %s", err)
            self._tendances_maj = now
            return
        self._tendances = api.calcul_tendances(points, TENDANCE_HORIZONS)
        self._tendances_maj = now

    async def _rafraichir_vigilance(self) -> None:
        """Geojson ~2 Mo : récupéré au plus toutes les SCAN_VIGILANCE secondes."""
        now = dt_util.utcnow()
        if self._vigilance_maj and (now - self._vigilance_maj).total_seconds() < SCAN_VIGILANCE:
            return
        try:
            troncons = await api.vigicrues_niveaux(self.session)
        except api.MonEauApiError as err:
            _LOGGER.debug("Vigicrues injoignable: %s", err)
            return
        info = troncons.get(self.troncon["code"])
        if info:
            niveau = info.get("niveau")
            self._vigilance = {
                "vigilance_niveau": niveau,
                "vigilance": VIGILANCE_LEVELS.get(niveau),
            }
        self._vigilance_maj = now


# ======================================================================
# Rivière — température continue (si station vivante)
# ======================================================================

class TemperatureCoordinator(MonEauCoordinator):
    def __init__(self, hass: HomeAssistant, station: dict) -> None:
        super().__init__(hass, "température rivière", SCAN_TEMP_CONTINUE)
        self.station = station

    async def _async_update_data(self) -> dict[str, Any]:
        mesure = await api.temp_derniere_mesure(self.session, self.station["code"])
        if mesure is None:
            raise UpdateFailed("Aucune mesure de température")
        return mesure


# ======================================================================
# Rivière — santé (qualité des cours d'eau)
# ======================================================================

class QualiteRiviereCoordinator(MonEauCoordinator):
    def __init__(self, hass: HomeAssistant, station: dict) -> None:
        super().__init__(hass, "qualité rivière", SCAN_QUALITE)
        self.station = station

    async def _async_update_data(self) -> dict[str, Any]:
        analyses = await api.qualite_dernieres_analyses(
            self.session, self.station["code"], list(RIVER_QUALITY_PARAMS)
        )
        return {
            kind: analyses[code]
            for code, kind in RIVER_QUALITY_PARAMS.items()
            if code in analyses
        }


# ======================================================================
# Nappe phréatique
# ======================================================================

class NappeCoordinator(MonEauCoordinator):
    def __init__(self, hass: HomeAssistant, piezo: dict) -> None:
        super().__init__(hass, "nappe", SCAN_NAPPE)
        self.piezo = piezo
        self._normales: dict | None = None
        self._plage: dict | None = None  # min/max historiques du niveau NGF
        self._normales_maj: datetime | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        mesure = await api.nappes_derniere_mesure(self.session, self.piezo["code_bss"])
        if mesure is None:
            raise UpdateFailed("Aucune mesure piézométrique")
        # Tendances du niveau NGF : monte = la nappe se recharge
        mesure["tendances"] = api.calcul_tendances(
            mesure.pop("points", []), TENDANCE_HORIZONS
        )

        await self._rafraichir_normales()
        mesure["normales"] = self._normales
        mesure["plage"] = self._plage
        niveau = mesure.get("niveau_ngf")
        if self._normales and niveau is not None:
            mesure["situation"] = api.situation_hydrologique(niveau, self._normales)
            mesure["ecart_normale_m"] = round(niveau - self._normales["normale"], 2)
        else:
            mesure["situation"] = None
            mesure["ecart_normale_m"] = None

        # Remplissage = position dans la plage historique (0 % = record bas)
        mesure["remplissage"] = None
        if self._plage and niveau is not None:
            etendue = self._plage["max"] - self._plage["min"]
            if etendue > 0.1:
                taux = (niveau - self._plage["min"]) / etendue * 100
                mesure["remplissage"] = round(max(0.0, min(100.0, taux)), 1)
        return mesure

    async def _rafraichir_normales(self) -> None:
        """Percentiles saisonniers du niveau NGF sur NORMALES_ANNEES (hebdomadaire)."""
        now = dt_util.utcnow()
        if self._normales_maj and (now - self._normales_maj).total_seconds() < SCAN_NORMALES:
            return
        date_min = (dt_util.now() - timedelta(days=NORMALES_ANNEES * 365)).strftime("%Y-%m-%d")
        try:
            niveaux = await api.nappes_niveaux_journaliers(
                self.session, self.piezo["code_bss"], date_min
            )
        except api.MonEauApiError as err:
            _LOGGER.debug("Chronique piézométrique indisponible: %s", err)
            self._normales_maj = now
            return
        aujourd_hui = dt_util.now()
        jour_annee = (aujourd_hui.month - 1) * 30.44 + aujourd_hui.day
        self._normales = api.stats_normales(niveaux, jour_annee, NORMALES_FENETRE_JOURS)
        valeurs = [v for _, v in niveaux]
        if valeurs:
            self._plage = {"min": round(min(valeurs), 2), "max": round(max(valeurs), 2)}
        self._normales_maj = now


# ======================================================================
# Baignade — qualité des eaux de baignade (ARS)
# ======================================================================

class BaignadeCoordinator(MonEauCoordinator):
    def __init__(self, hass: HomeAssistant, site: dict) -> None:
        super().__init__(hass, "baignade", SCAN_BAIGNADE_SAISON)
        self.site = site

    async def _async_update_data(self) -> dict[str, Any]:
        annee = dt_util.now().year
        data = await api.baignades_site_details(
            self.session, self.site["dptddass"], self.site["site"], annee
        )
        if data is None:
            raise UpdateFailed("Page du site de baignade non reconnue")

        aujourd_hui = dt_util.now().strftime("%Y-%m-%d")
        data["en_saison"] = data["saison_debut"] <= aujourd_hui <= data["saison_fin"]

        # Détail bactério du dernier prélèvement (best effort, une requête de plus)
        dernier = data.get("dernier_controle")
        if dernier and dernier.get("plv"):
            try:
                detail = await api.baignades_controle_details(
                    self.session, self.site["dptddass"], self.site["site"],
                    dernier["plv"], annee,
                )
            except Exception:
                detail = None
            if detail:
                dernier.update(detail)

        # Hors saison, inutile d'interroger 4 fois par jour
        interval = SCAN_BAIGNADE_SAISON if data["en_saison"] else SCAN_BAIGNADE_HORS_SAISON
        self.update_interval = timedelta(seconds=interval)
        return data


# ======================================================================
# Sécheresse — VigiEau + ONDE
# ======================================================================

class SecheresseCoordinator(MonEauCoordinator):
    def __init__(self, hass: HomeAssistant, commune: dict) -> None:
        super().__init__(hass, "sécheresse", SCAN_SECHERESSE)
        self.commune = commune

    async def _async_update_data(self) -> dict[str, Any]:
        zones = await api.vigieau_zones(self.session, self.commune["code"])

        par_type: dict[str, dict] = {}
        pire: str | None = None
        usages: list[dict] = []
        for zone in zones:
            type_ressource = VIGIEAU_TYPES.get(zone.get("type") or "")
            gravite = zone.get("niveauGravite")
            if not type_ressource or not gravite:
                continue
            arrete = zone.get("arrete") or {}
            par_type[type_ressource] = {
                "gravite": gravite,
                "zone": zone.get("nom"),
                "arrete_debut": arrete.get("dateDebutValidite"),
                "arrete_fin": arrete.get("dateFinValidite"),
                "arrete_pdf": arrete.get("cheminFichier"),
            }
            if pire is None or self._rang(gravite) > self._rang(pire):
                pire = gravite
                usages = [
                    {
                        "nom": u.get("nom"),
                        "description": (u.get("description") or "").strip() or None,
                    }
                    for u in zone.get("usages") or []
                    if u.get("nom")
                ]

        date_min = (dt_util.now() - timedelta(days=60)).strftime("%Y-%m-%d")
        try:
            onde = await api.onde_resume(self.session, self.commune["departement"], date_min)
        except api.MonEauApiError as err:
            _LOGGER.debug("ONDE injoignable: %s", err)
            onde = None

        return {
            "gravite": pire or GRAVITE_AUCUNE,
            "par_type": par_type,
            "usages": usages,
            "onde": onde,
        }

    @staticmethod
    def _rang(gravite: str) -> int:
        try:
            return GRAVITE_ORDRE.index(gravite)
        except ValueError:
            return -1
