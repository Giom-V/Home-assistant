from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_COLOR_TEMP_KELVIN,
    ColorMode,
    LightEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, LOGGER
from .coordinator import DLightDataUpdateCoordinator

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up dlights for coordinator."""

    LOGGER.debug(
        "Setup dLight: %s for %s (%s)",
        config_entry.entry_id,
        config_entry.data[CONF_HOST],
        config_entry.data[CONF_DEVICE_ID],
    )

    coordinator: DLightDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([DLight(coordinator)])


class DLight(LightEntity, CoordinatorEntity[DLightDataUpdateCoordinator]):
    """Representation of a dLight."""

    _attr_name = None
    _attr_has_entity_name = True

    def __init__(self, coordinator: DLightDataUpdateCoordinator) -> None:
        """Initialize a dLight."""
        super().__init__(coordinator=coordinator)
        LOGGER.debug("light.__init__: %s", coordinator.device_id)

        self._attr_min_color_temp_kelvin = 2600
        self._attr_max_color_temp_kelvin = 6000

        self._attr_unique_id = coordinator.device_id
        self._attr_name = coordinator.name
        self._attr_supported_color_modes = {ColorMode.COLOR_TEMP}
        self._attr_color_mode = ColorMode.COLOR_TEMP

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.device_id)},
            serial_number=coordinator.device_id,
            manufacturer="dLight",
            model=coordinator.discovery["device_model"],
            name=coordinator.name,
            sw_version=coordinator.discovery["sw_version"],
            hw_version=coordinator.discovery["hw_version"],
        )

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return "mdi:desk-lamp"

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 1..255."""
        return round((self.coordinator.data.brightness * 255) / 100, 0)

    @property
    def color_temp_kelvin(self) -> int | None:
        """Return the CT color value in Kelvin."""
        return self.coordinator.data.temperature

    @property
    def is_on(self) -> bool:
        """Return the state of the light."""
        return self.coordinator.data.on

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        LOGGER.debug("async_turn_on(%s)", kwargs)

        temperature = kwargs.get(ATTR_COLOR_TEMP_KELVIN)

        brightness = None
        if ATTR_BRIGHTNESS in kwargs:
            brightness = round((kwargs[ATTR_BRIGHTNESS] / 255) * 100)

        await self.coordinator.async_turn_on(temperature, brightness)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn device off."""
        LOGGER.debug("async_turn_off(%s)", kwargs)

        await self.coordinator.async_turn_off()
