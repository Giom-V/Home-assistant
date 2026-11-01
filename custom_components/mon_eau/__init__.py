# custom_components/mon_eau/__init__.py
"""Mon Eau — l'eau autour de chez soi : robinet, rivière, nappe, sécheresse."""
from __future__ import annotations

import logging
import os

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_BAIGNADE,
    CONF_COMMUNE,
    CONF_FEATURES,
    CONF_HYDRO,
    CONF_PIEZO,
    CONF_QUALITE,
    CONF_RESEAU,
    CONF_RESEAU_COMMUNE,
    CONF_TEMPERATURE,
    CONF_TRONCON,
    DOMAIN,
    FEATURE_BAIGNADE,
    FEATURE_EAU_POTABLE,
    FEATURE_NAPPE,
    FEATURE_RIVIERE,
    FEATURE_SECHERESSE,
)
from .coordinator import (
    BaignadeCoordinator,
    EauPotableCoordinator,
    HydroCoordinator,
    NappeCoordinator,
    QualiteRiviereCoordinator,
    SecheresseCoordinator,
    TemperatureCoordinator,
)

_LOGGER = logging.getLogger(__name__)
PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

_CARD_URL = "/mon_eau_cards"
_CARD_FILE = "mon-eau-cards.js"


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Enregistre le fichier JS des cartes Lovelace packagées."""
    card_dir = hass.config.path("custom_components", "mon_eau", "lovelace")

    if not await hass.async_add_executor_job(os.path.isdir, card_dir):
        _LOGGER.warning("Mon Eau: dossier lovelace/ introuvable — cartes indisponibles")
        return True

    try:
        await hass.http.async_register_static_paths(
            [StaticPathConfig(_CARD_URL, card_dir, cache_headers=True)]
        )
        add_extra_js_url(hass, f"{_CARD_URL}/{_CARD_FILE}")
        _LOGGER.debug("Mon Eau: cartes servies depuis %s", card_dir)
    except Exception:
        _LOGGER.exception("Mon Eau: erreur lors de l'enregistrement des cartes Lovelace")

    return True


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """v1 → v2 : les sélections uniques deviennent des listes."""
    if entry.version == 1:
        data = {**entry.data}
        troncon = data.pop(CONF_TRONCON, None)
        hydro = data.get(CONF_HYDRO)
        data[CONF_HYDRO] = [{**hydro, "troncon": troncon}] if hydro else []
        for cle in (CONF_RESEAU, CONF_PIEZO, CONF_BAIGNADE):
            valeur = data.get(cle)
            data[cle] = [valeur] if valeur else []
        hass.config_entries.async_update_entry(entry, data=data, version=2)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})
    data = entry.data
    features: list[str] = data.get(CONF_FEATURES, [])
    commune: dict = data[CONF_COMMUNE]

    coordinators: dict[str, object] = {}

    if FEATURE_EAU_POTABLE in features:
        reseaux = data.get(CONF_RESEAU) or []
        if data.get(CONF_RESEAU_COMMUNE, not reseaux):
            coordinators["eau_potable_commune"] = EauPotableCoordinator(hass, commune, None)
        for reseau in reseaux:
            coordinators[f"eau_potable_{reseau['code']}"] = EauPotableCoordinator(
                hass, commune, reseau
            )
    if FEATURE_RIVIERE in features:
        for station in data.get(CONF_HYDRO) or []:
            coordinators[f"hydro_{station['code']}"] = HydroCoordinator(
                hass, station, station.get("troncon")
            )
        if data.get(CONF_QUALITE):
            coordinators["qualite"] = QualiteRiviereCoordinator(hass, data[CONF_QUALITE])
        if data.get(CONF_TEMPERATURE):
            coordinators["temperature"] = TemperatureCoordinator(
                hass, data[CONF_TEMPERATURE]
            )
    if FEATURE_NAPPE in features:
        for piezo in data.get(CONF_PIEZO) or []:
            coordinators[f"nappe_{piezo['code_bss']}"] = NappeCoordinator(hass, piezo)
    if FEATURE_SECHERESSE in features:
        coordinators["secheresse"] = SecheresseCoordinator(hass, commune)
    if FEATURE_BAIGNADE in features:
        for site in data.get(CONF_BAIGNADE) or []:
            coordinators[f"baignade_{site['site']}"] = BaignadeCoordinator(hass, site)

    # Aucun coordinator ne bloque seul le démarrage (ex. réseau d'eau potable
    # sans résultat) : ses entités restent indisponibles. On ne réessaie
    # l'entrée entière que si TOUT a échoué (réseau coupé, APIs en panne).
    for coordinator in coordinators.values():
        await coordinator.async_refresh()
    if coordinators and not any(c.last_update_success for c in coordinators.values()):
        raise ConfigEntryNotReady("Aucune source Mon Eau n'a répondu")

    _purger_devices_retires(hass, entry, coordinators, data)

    hass.data[DOMAIN][entry.entry_id] = coordinators
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


def _purger_devices_retires(
    hass: HomeAssistant, entry: ConfigEntry, coordinators: dict, data: dict
) -> None:
    """Supprime les devices des stations/réseaux retirés via l'options flow."""
    attendus: set[str] = set()
    for key in coordinators:
        if key.startswith("hydro_"):
            attendus.add(f"riviere_{key.removeprefix('hydro_')}")
        elif key in ("qualite", "temperature"):
            hydros = data.get(CONF_HYDRO) or []
            attendus.add(f"riviere_{hydros[0]['code']}" if hydros else "riviere_sante")
        else:
            attendus.add(key)
    identifiants = {(DOMAIN, f"{entry.entry_id}_{key}") for key in attendus}

    registre = dr.async_get(hass)
    for device in dr.async_entries_for_config_entry(registre, entry.entry_id):
        if not device.identifiers & identifiants:
            registre.async_update_device(device.id, remove_config_entry_id=entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinators = hass.data[DOMAIN].pop(entry.entry_id)
        for coordinator in coordinators.values():
            await coordinator.async_shutdown()
    return unloaded
