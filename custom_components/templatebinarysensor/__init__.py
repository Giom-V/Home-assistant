"""
templatebinarysensor component

For more details about this component, please refer to
https://github.com/dlashua/templatebinarysensor
"""
import os
from datetime import timedelta
import logging
import voluptuous as vol
from homeassistant import config_entries
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers import discovery
from homeassistant.util import Throttle

from .const import DOMAIN_DATA, DOMAIN, ISSUE_URL, PLATFORMS, REQUIRED_FILES, VERSION

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up this component using YAML is not supported."""
    return True


async def async_setup_entry(hass, config_entry):
    """Set up this integration using UI."""
    # Check that all required files are present
    file_check = await check_files(hass)
    if not file_check:
        return False

    # Add sensor
    hass.async_add_job(
        hass.config_entries.async_forward_entry_setup(config_entry, "binary_sensor")
    )
    return True


async def check_files(hass):
    """Return bool that indicates if all files are present."""
    # Verify that the user downloaded all files.
    base = f"{hass.config.path()}/custom_components/{DOMAIN}/"
    missing = []
    for file in REQUIRED_FILES:
        fullpath = "{}{}".format(base, file)
        if not os.path.exists(fullpath):
            missing.append(file)

    if missing:
        _LOGGER.critical("The following files are missing: %s", str(missing))
        returnvalue = False
    else:
        returnvalue = True

    return returnvalue


async def async_remove_entry(hass, config_entry):
    """Handle removal of an entry."""
    try:
        await hass.config_entries.async_forward_entry_unload(
            config_entry, "binary_sensor"
        )
        _LOGGER.info("Successfully removed binary_sensor")
    except ValueError:
        pass
