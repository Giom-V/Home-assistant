import asyncio
import logging

from typing import Any

from datetime import timedelta
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
import homeassistant.util.color as color_util
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP,
    ColorMode,
    LightEntity,
)

from .const import DOMAIN
from . import dlight

_LOGGER = logging.getLogger(__name__)


SCAN_INTERVAL = timedelta(seconds=5)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up dlights dynamically through discovery."""

    devices = await dlight.discover_devices(hass)
    entities: list[DLight] = [DLight(device) for device in devices]
    # for device in devices:
    #     entities.append(DLight(device))

    async_add_entities(entities)


class DLight(LightEntity):
    """Representation of a dLight."""

    def __init__(self, discovery: dlight.DLightDiscovery) -> None:
        """Initialize a dLight."""
        self._discovery = discovery
        self._attr_unique_id = self._discovery.deviceId
        self._attr_name = self._discovery.deviceModel + " " + self._discovery.deviceId
        self._available = True

    @property
    def device_info(self) -> DeviceInfo:
        """Information about this entity/device."""
        return DeviceInfo(
            identifiers={(DOMAIN, str(self._discovery.deviceId))},
            name=self.name,
            sw_version=self._discovery.swVersion,
            hw_version=self._discovery.hwVersion,
            model=self._discovery.deviceModel,
        )

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:desk-lamp"

    @property
    def supported_color_modes(self):
        """Flag supported color modes."""
        return {ColorMode.BRIGHTNESS, ColorMode.COLOR_TEMP}

    @property
    def min_color_temp_kelvin(self) -> int:
        """Return the warmest color_temp_kelvin that this light supports."""
        return 2600

    @property
    def max_color_temp_kelvin(self) -> int:
        """Return the coldest color_temp_kelvin that this light supports."""
        return 6000

    @property
    def available(self) -> bool:
        return self._available

    def _update_state(self, states: dict[str, Any]) -> None:
        """Update internal state based on response from lamp"""
        self._available = True

        if "on" in states:
            self._attr_is_on = states["on"]
        if "brightness" in states:
            self._attr_brightness = int(
                round(255 * (int(states["brightness"]) / 100), 0)
            )
        if "color" in states:
            self._attr_color_temp_kelvin = states["color"]["temperature"]

    def _mark_state_as_unavailable(self) -> None:
        self._attr_is_on = None
        self._attr_brightness = None
        self._attr_color_temp_kelvin = None
        self._available = False

    async def async_update(self):
        """Poll device state"""
        try:
            result = await dlight.get_state(self._discovery)
            self._update_state(result["states"])
        except dlight.DLightRequestUnsuccessfulException:
            _LOGGER.warning("Async Update Failed: %s\n%s", self._discovery, result)
            self._mark_state_as_unavailable()
        except (asyncio.TimeoutError, OSError):
            # Device is unavailable
            # TODO - schedule a new device discovery in case the IP has changed.
            self._mark_state_as_unavailable()

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        dlight_config: dict[str, Any] = {"on": True}
        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(float(kwargs[ATTR_BRIGHTNESS]) / 255 * 100)
            dlight_config[ATTR_BRIGHTNESS] = brightness
        if ATTR_COLOR_TEMP in kwargs:
            temp = color_util.color_temperature_kelvin_to_mired(
                float(kwargs[ATTR_COLOR_TEMP])
            )
            dlight_config["color"] = {"temperature": temp}

        try:
            result = await dlight.set_values(self._discovery, dlight_config)
            self._update_state(result)
        except Exception as e:
            _LOGGER.warning("Async Turn On Failed: %s\n%s", self._discovery, e)

    async def async_turn_off(self, **kwargs):
        """Turn device off."""
        dlight_config: dict[str, Any] = {"on": False}

        try:
            result = await dlight.set_values(self._discovery, dlight_config)
            self._update_state(result)
        except Exception as e:
            _LOGGER.warning("Async Turn Off Failed: %s\n%s", self._discovery, e)