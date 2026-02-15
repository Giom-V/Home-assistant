"""C.A.F.E. - Visual automation editor for Home Assistant."""
from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .panel import async_register_panel, async_unregister_panel

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the C.A.F.E. component."""
    # This will be called when the integration is loaded
    # But actual setup happens in async_setup_entry
    return True


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up C.A.F.E. from a config entry."""

    # Register the panel (frontend)
    await async_register_panel(hass)

    _LOGGER.info("C.A.F.E. integration set up successfully")

    return True


async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    """Unload a config entry."""
    async_unregister_panel(hass)
    return True
