"""Config flow for dlight."""
import logging


from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_flow

from .const import DOMAIN

from . import dlight

_LOGGER = logging.getLogger(__name__)


async def _async_has_devices(hass: HomeAssistant) -> bool:
    """Return if there are devices that can be discovered."""
    devices = await dlight.discover_devices(hass)
    return len(devices) > 0


config_entry_flow.register_discovery_flow(DOMAIN, "dlight", _async_has_devices)