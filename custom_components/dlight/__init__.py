"""The dlight integration."""
from __future__ import annotations

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.LIGHT]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up dlight from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    try:
        setup = hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        await asyncio.wait_for(setup, timeout=5.0)
    except asyncio.TimeoutError:
        raise ConfigEntryNotReady

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        _LOGGER.info("Unloaded")

    return unload_ok