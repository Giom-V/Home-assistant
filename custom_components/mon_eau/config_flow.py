# custom_components/mon_eau/config_flow.py
"""Config flow et options flow : plateformes → commune → réseaux → stations.
Les listes sont triées par distance et filtrées sur la fraîcheur réelle des
données ; les étapes de sélection sont partagées avec l'options flow, qui
pré-remplit les choix actuels."""
from __future__ import annotations

import asyncio
import copy
import logging
from datetime import timedelta

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
)
from homeassistant.util import dt as dt_util

from . import api
from .const import (
    ALL_FEATURES,
    CONF_BAIGNADE,
    CONF_COMMUNE,
    CONF_FEATURES,
    CONF_HYDRO,
    CONF_PIEZO,
    CONF_QUALITE,
    CONF_RESEAU,
    CONF_RESEAU_COMMUNE,
    CONF_TEMPERATURE,
    DOMAIN,
    FEATURE_BAIGNADE,
    FEATURE_EAU_POTABLE,
    FEATURE_NAPPE,
    FEATURE_RIVIERE,
    FRESH_TEMP_DAYS,
    PIEZO_ACTIVE_DAYS,
)

_LOGGER = logging.getLogger(__name__)

AUCUNE = "__aucune__"


def _tri_par_distance(stations: list[dict], lat: float, lon: float) -> list[dict]:
    """Trie par distance à la commune ; les stations sans coordonnées passent en fin."""
    def cle(s: dict) -> float:
        s_lat, s_lon = s.get("lat"), s.get("lon")
        if s_lat is None or s_lon is None or abs(s_lat) > 90 or abs(s_lon) > 180:
            return 9999.0
        d = api.distance_km(lat, lon, s_lat, s_lon)
        s["distance"] = round(d, 1)
        return d

    return sorted(stations, key=cle)


def _label(s: dict, extra: str | None = None) -> str:
    parts = [s["libelle"]]
    if s.get("distance") is not None and s["distance"] < 9999:
        parts.append(f"{s['distance']} km")
    if extra:
        parts.append(extra)
    return " — ".join(parts)


class EtapesSelectionMixin:
    """Étapes de sélection communes au config flow et à l'options flow.

    Attend : self._data (config en cours), self._stations, self._reseaux,
    self.hass — et self._creer_entree() pour terminer."""

    _ORDRE = ["commune_choix", "reseau", "hydro", "qualite", "temperature", "piezo", "baignade"]

    @property
    def _session(self):
        return async_get_clientsession(self.hass)

    @property
    def _commune(self) -> dict:
        return self._data[CONF_COMMUNE]

    async def _etape_suivante(self, courante: str) -> ConfigFlowResult:
        features = self._data[CONF_FEATURES]
        suivantes = self._ORDRE[self._ORDRE.index(courante) + 1 :]
        for etape in suivantes:
            if etape == "reseau" and FEATURE_EAU_POTABLE in features:
                return await self.async_step_reseau()
            if etape in ("hydro", "qualite", "temperature") and FEATURE_RIVIERE in features:
                return await getattr(self, f"async_step_{etape}")()
            if etape == "piezo" and FEATURE_NAPPE in features:
                return await self.async_step_piezo()
            if etape == "baignade" and FEATURE_BAIGNADE in features:
                return await self.async_step_baignade()
        return self._creer_entree()

    @staticmethod
    def _completer(options_stations: list[dict], actuelles: list[dict], champ: str) -> None:
        """Garde les sélections actuelles dans la liste même si le sondage les a exclues."""
        codes = {s[champ] for s in options_stations}
        for station in actuelles:
            if station and station.get(champ) and station[champ] not in codes:
                options_stations.append(station)

    # ------------------------------------------------------------------
    # Réseaux d'eau potable
    # ------------------------------------------------------------------

    async def async_step_reseau(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            choix = user_input["reseau"]
            reseaux = [r for r in self._reseaux if r["code"] in choix]
            self._data[CONF_RESEAU] = reseaux
            self._data[CONF_RESEAU_COMMUNE] = AUCUNE in choix or not reseaux
            return await self._etape_suivante("reseau")

        try:
            self._reseaux = await api.dis_liste_reseaux(self._session, self._commune["code"])
        except api.MonEauApiError as err:
            _LOGGER.warning("Mon Eau — liste des réseaux impossible: %s", err)
            errors["base"] = "cannot_connect"
            self._reseaux = []
        self._completer(self._reseaux, self._data.get(CONF_RESEAU) or [], "code")

        options = [SelectOptionDict(value=AUCUNE, label="Toute la commune (dernier prélèvement)")]
        options += [
            SelectOptionDict(
                value=r["code"],
                label=f"{r['nom']} — {r['quartier']}" if r.get("quartier") else r["nom"],
            )
            for r in self._reseaux
        ]
        actuels = [r["code"] for r in self._data.get(CONF_RESEAU) or []]
        defaut = actuels + ([AUCUNE] if self._data.get(CONF_RESEAU_COMMUNE, not actuels) else [])
        return self.async_show_form(
            step_id="reseau",
            data_schema=vol.Schema(
                {
                    vol.Required("reseau", default=defaut): SelectSelector(
                        SelectSelectorConfig(
                            options=options, multiple=True, mode=SelectSelectorMode.DROPDOWN
                        )
                    )
                }
            ),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Stations hydrométriques (+ tronçon vigilance déterminé tout seul)
    # ------------------------------------------------------------------

    async def async_step_hydro(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        commune = self._commune

        if user_input is not None:
            stations = [s for s in self._stations["hydro"] if s["code"] in user_input["station"]]
            await self._attacher_troncons(stations)
            self._data[CONF_HYDRO] = stations
            return await self._etape_suivante("hydro")

        vivantes: list[dict] = []
        try:
            stations = await api.hydro_liste_stations(self._session, commune["departement"])
            candidates = _tri_par_distance(stations, commune["lat"], commune["lon"])[:20]
            # Le référentiel ment (« en_service » sans observations) : on sonde chaque station
            observations = await asyncio.gather(
                *(
                    api.hydro_dernieres_observations(self._session, s["code"])
                    for s in candidates
                ),
                return_exceptions=True,
            )
            seuil = (dt_util.utcnow() - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ")
            for station, obs in zip(candidates, observations):
                if not isinstance(obs, dict):
                    continue
                date = obs.get("date_hauteur") or obs.get("date_debit")
                if not date or date < seuil:
                    continue
                station["grandeurs"] = [
                    g
                    for g, cle in (("H", "hauteur"), ("Q", "debit"))
                    if obs.get(cle) is not None
                ]
                vivantes.append(station)
        except api.MonEauApiError as err:
            _LOGGER.warning("Mon Eau — liste des stations hydro impossible: %s", err)
            errors["base"] = "cannot_connect"
        self._completer(vivantes, self._data.get(CONF_HYDRO) or [], "code")
        self._stations["hydro"] = vivantes

        options = [
            SelectOptionDict(
                value=s["code"],
                label=_label(s, " + ".join(s.get("grandeurs") or ["H", "Q"])),
            )
            for s in vivantes
        ]
        actuels = [s["code"] for s in self._data.get(CONF_HYDRO) or []]
        defaut = actuels or ([vivantes[0]["code"]] if vivantes else [])
        return self.async_show_form(
            step_id="hydro",
            data_schema=vol.Schema(
                {
                    vol.Required("station", default=defaut): SelectSelector(
                        SelectSelectorConfig(
                            options=options, multiple=True, mode=SelectSelectorMode.DROPDOWN
                        )
                    )
                }
            ),
            errors=errors,
        )

    async def _attacher_troncons(self, stations: list[dict]) -> None:
        """Tronçon de vigilance crues le plus proche de chaque station (silencieux si échec)."""
        a_faire = [s for s in stations if "troncon" not in s]
        if not a_faire:
            return
        try:
            troncons = await api.vigicrues_niveaux(self._session)
        except api.MonEauApiError:
            _LOGGER.debug("Vigicrues injoignable pendant le config flow")
            return
        for station in a_faire:
            lat = station.get("lat") or self._commune["lat"]
            lon = station.get("lon") or self._commune["lon"]
            trouve = api.vigicrues_troncon_le_plus_proche(troncons, lat, lon)
            station["troncon"] = (
                {"code": trouve[0], "libelle": trouve[1]} if trouve else None
            )

    # ------------------------------------------------------------------
    # Station qualité rivière (celles avec analyses récentes seulement)
    # ------------------------------------------------------------------

    async def async_step_qualite(self, user_input: dict | None = None) -> ConfigFlowResult:
        commune = self._commune
        if user_input is not None:
            self._data[CONF_QUALITE] = (
                None
                if user_input["station"] == AUCUNE
                else next(
                    s for s in self._stations["qualite"] if s["code"] == user_input["station"]
                )
            )
            return await self._etape_suivante("qualite")

        date_min = (dt_util.now() - timedelta(days=550)).strftime("%Y-%m-%d")
        stations: list[dict] = []
        try:
            analyses, toutes = await asyncio.gather(
                api.qualite_analyses_recentes(
                    self._session, commune["lat"], commune["lon"], date_min
                ),
                api.qualite_stations_proches(self._session, commune["lat"], commune["lon"]),
            )
            coords = {s["code"]: s for s in toutes}
            vues: dict[str, dict] = {}
            for a in analyses:
                code = a.get("code_station")
                if not code or code in vues:
                    continue
                base = coords.get(code, {})
                vues[code] = {
                    "code": code,
                    "libelle": api.joli_libelle(a.get("libelle_station"))
                    or base.get("libelle")
                    or code,
                    "lat": base.get("lat"),
                    "lon": base.get("lon"),
                    "derniere": a.get("date_prelevement"),
                }
            stations = _tri_par_distance(list(vues.values()), commune["lat"], commune["lon"])[:15]
        except api.MonEauApiError as err:
            _LOGGER.warning("Mon Eau — stations qualité rivières injoignables: %s", err)

        actuelle = self._data.get(CONF_QUALITE)
        self._completer(stations, [actuelle] if actuelle else [], "code")
        self._stations["qualite"] = stations
        options = [
            SelectOptionDict(
                value=s["code"],
                label=_label(s, f"dernier relevé {s['derniere']}" if s.get("derniere") else None),
            )
            for s in stations
        ]
        options.append(SelectOptionDict(value=AUCUNE, label="Aucune station"))
        defaut = (actuelle or {}).get("code") or (stations[0]["code"] if stations else AUCUNE)
        return self.async_show_form(
            step_id="qualite",
            data_schema=vol.Schema(
                {
                    vol.Required("station", default=defaut): SelectSelector(
                        SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN)
                    )
                }
            ),
        )

    # ------------------------------------------------------------------
    # Station température continue (rarement disponible : API quasi morte)
    # ------------------------------------------------------------------

    async def async_step_temperature(self, user_input: dict | None = None) -> ConfigFlowResult:
        commune = self._commune
        if user_input is not None:
            self._data[CONF_TEMPERATURE] = (
                None
                if user_input["station"] == AUCUNE
                else next(
                    s for s in self._stations["temperature"] if s["code"] == user_input["station"]
                )
            )
            return await self._etape_suivante("temperature")

        vivantes: list[dict] = []
        try:
            stations = await api.temp_liste_stations(self._session, commune["departement"])
            # Les métadonnées ne disent pas si la station est vivante : sonder la chronique
            seuil = (dt_util.now() - timedelta(days=FRESH_TEMP_DAYS)).strftime("%Y-%m-%d")
            mesures = await asyncio.gather(
                *(api.temp_derniere_mesure(self._session, s["code"]) for s in stations),
                return_exceptions=True,
            )
            for station, mesure in zip(stations, mesures):
                if (
                    isinstance(mesure, dict)
                    and mesure.get("date")
                    and mesure["date"][:10] >= seuil
                ):
                    station["derniere"] = mesure["date"][:10]
                    vivantes.append(station)
        except api.MonEauApiError as err:
            _LOGGER.warning("Mon Eau — API température injoignable: %s", err)

        actuelle = self._data.get(CONF_TEMPERATURE)
        self._completer(vivantes, [actuelle] if actuelle else [], "code")
        self._stations["temperature"] = _tri_par_distance(
            vivantes, commune["lat"], commune["lon"]
        )

        if not self._stations["temperature"]:
            # Cas général : aucune station vivante, on saute l'étape
            self._data[CONF_TEMPERATURE] = None
            return await self._etape_suivante("temperature")

        options = [
            SelectOptionDict(
                value=s["code"],
                label=_label(s, f"mesure du {s['derniere']}" if s.get("derniere") else None),
            )
            for s in self._stations["temperature"]
        ]
        options.append(SelectOptionDict(value=AUCUNE, label="Aucune station"))
        defaut = (actuelle or {}).get("code") or AUCUNE
        return self.async_show_form(
            step_id="temperature",
            data_schema=vol.Schema(
                {
                    vol.Required("station", default=defaut): SelectSelector(
                        SelectSelectorConfig(options=options, mode=SelectSelectorMode.DROPDOWN)
                    )
                }
            ),
        )

    # ------------------------------------------------------------------
    # Piézomètres (nappe phréatique)
    # ------------------------------------------------------------------

    async def async_step_piezo(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        commune = self._commune

        if user_input is not None:
            self._data[CONF_PIEZO] = [
                {"code_bss": s["code_bss"], "libelle": s["libelle"]}
                for s in self._stations["piezo"]
                if s["code_bss"] in user_input["station"]
            ]
            return await self._etape_suivante("piezo")

        actifs: list[dict] = []
        try:
            stations = await api.nappes_liste_stations(self._session, commune["departement"])
            seuil = (dt_util.now() - timedelta(days=PIEZO_ACTIVE_DAYS)).strftime("%Y-%m-%d")
            actifs = [
                s for s in stations if (s.get("date_fin_mesure") or "") >= seuil
            ]
        except api.MonEauApiError as err:
            _LOGGER.warning("Mon Eau — liste des piézomètres impossible: %s", err)
            errors["base"] = "cannot_connect"

        actifs = _tri_par_distance(actifs, commune["lat"], commune["lon"])[:15]
        self._completer(actifs, self._data.get(CONF_PIEZO) or [], "code_bss")
        self._stations["piezo"] = actifs
        options = [
            SelectOptionDict(
                value=s["code_bss"],
                label=_label(
                    s,
                    f"mesuré jusqu'au {s['date_fin_mesure']}" if s.get("date_fin_mesure") else None,
                ),
            )
            for s in actifs
        ]
        actuels = [s["code_bss"] for s in self._data.get(CONF_PIEZO) or []]
        defaut = actuels or ([actifs[0]["code_bss"]] if actifs else [])
        return self.async_show_form(
            step_id="piezo",
            data_schema=vol.Schema(
                {
                    vol.Required("station", default=defaut): SelectSelector(
                        SelectSelectorConfig(
                            options=options, multiple=True, mode=SelectSelectorMode.DROPDOWN
                        )
                    )
                }
            ),
            errors=errors,
        )

    # ------------------------------------------------------------------
    # Sites de baignade (ARS)
    # ------------------------------------------------------------------

    async def async_step_baignade(self, user_input: dict | None = None) -> ConfigFlowResult:
        commune = self._commune

        if user_input is not None:
            self._data[CONF_BAIGNADE] = [
                s for s in self._stations["baignade"] if s["site"] in user_input["site"]
            ]
            return await self._etape_suivante("baignade")

        sites: list[dict] = []
        try:
            communes = await api.baignades_communes(self._session, commune["departement"])
            listes = await asyncio.gather(
                *(
                    api.baignades_sites(self._session, commune["departement"], c["insee"])
                    for c in communes
                ),
                return_exceptions=True,
            )
            for c, liste in zip(communes, listes):
                if isinstance(liste, list):
                    for s in liste:
                        sites.append({**s, "commune": c["nom"]})
        except api.MonEauApiError as err:
            _LOGGER.warning("Mon Eau — sites de baignade injoignables: %s", err)

        sites.sort(key=lambda s: (s.get("commune") or "", s["libelle"]))
        self._completer(sites, self._data.get(CONF_BAIGNADE) or [], "site")
        self._stations["baignade"] = sites

        if not sites:
            self._data[CONF_BAIGNADE] = []
            return await self._etape_suivante("baignade")

        options = [
            SelectOptionDict(
                value=s["site"],
                label=f"{s['libelle']} — {s['commune']}" if s.get("commune") else s["libelle"],
            )
            for s in sites
        ]
        actuels = [s["site"] for s in self._data.get(CONF_BAIGNADE) or []]
        defaut = actuels or [sites[0]["site"]]
        return self.async_show_form(
            step_id="baignade",
            data_schema=vol.Schema(
                {
                    vol.Required("site", default=defaut): SelectSelector(
                        SelectSelectorConfig(
                            options=options, multiple=True, mode=SelectSelectorMode.DROPDOWN
                        )
                    )
                }
            ),
        )


class MonEauConfigFlow(EtapesSelectionMixin, ConfigFlow, domain=DOMAIN):
    """Une entrée par commune."""

    VERSION = 2

    def __init__(self) -> None:
        self._data: dict = {}
        self._communes: list[dict] = []
        self._reseaux: list[dict] = []
        self._stations: dict[str, list[dict]] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> MonEauOptionsFlow:
        return MonEauOptionsFlow(config_entry)

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_FEATURES] = user_input[CONF_FEATURES]
            return await self.async_step_commune()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_FEATURES, default=ALL_FEATURES): SelectSelector(
                        SelectSelectorConfig(
                            options=ALL_FEATURES,
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                            translation_key="features",
                        )
                    )
                }
            ),
        )

    async def async_step_commune(self, user_input: dict | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._communes = await api.geo_search_communes(
                    self._session, user_input["recherche"]
                )
            except api.MonEauApiError as err:
                _LOGGER.warning("Mon Eau — recherche de commune impossible: %s", err)
                errors["base"] = "cannot_connect"
            else:
                if not self._communes:
                    errors["base"] = "commune_introuvable"
                else:
                    return await self.async_step_commune_choix()

        return self.async_show_form(
            step_id="commune",
            data_schema=vol.Schema({vol.Required("recherche"): TextSelector()}),
            errors=errors,
        )

    async def async_step_commune_choix(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            commune = next(c for c in self._communes if c["code"] == user_input["commune"])
            await self.async_set_unique_id(commune["code"])
            self._abort_if_unique_id_configured()
            self._data[CONF_COMMUNE] = commune
            return await self._etape_suivante("commune_choix")

        options = [
            SelectOptionDict(
                value=c["code"],
                label=f"{c['nom']} ({c['code_postal']}, {c['departement']})",
            )
            for c in self._communes
        ]
        return self.async_show_form(
            step_id="commune_choix",
            data_schema=vol.Schema(
                {
                    vol.Required("commune"): SelectSelector(
                        SelectSelectorConfig(options=options, mode=SelectSelectorMode.LIST)
                    )
                }
            ),
        )

    def _creer_entree(self) -> ConfigFlowResult:
        return self.async_create_entry(
            title=f"Mon Eau — {self._commune['nom']}",
            data=self._data,
        )


class MonEauOptionsFlow(EtapesSelectionMixin, OptionsFlow):
    """Modifier plateformes, réseaux et stations sans recréer l'entrée."""

    def __init__(self, entry: ConfigEntry) -> None:
        self._entry = entry
        self._data: dict = copy.deepcopy(dict(entry.data))
        self._reseaux: list[dict] = []
        self._stations: dict[str, list[dict]] = {}

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        if user_input is not None:
            self._data[CONF_FEATURES] = user_input[CONF_FEATURES]
            return await self._etape_suivante("commune_choix")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_FEATURES, default=self._data.get(CONF_FEATURES, ALL_FEATURES)
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=ALL_FEATURES,
                            multiple=True,
                            mode=SelectSelectorMode.LIST,
                            translation_key="features",
                        )
                    )
                }
            ),
        )

    def _creer_entree(self) -> ConfigFlowResult:
        self.hass.config_entries.async_update_entry(self._entry, data=self._data)
        self.hass.config_entries.async_schedule_reload(self._entry.entry_id)
        return self.async_create_entry(title="", data={})
