"""Solisart sensors."""
from __future__ import annotations

import logging

import unidecode

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, HEAT_PUMP_ON, HEAT_PUMP_STATUS

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Solisart"

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the binary sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    add_entities([SolisartHeatPumpBinarySensor(coordinator)], True)


class SolisartHeatPumpBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Sensor for the heat pump status."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "Pompe à chaleur en fonctionnement"
        self._name = self._attr_name
        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self._attr_icon = "mdi:heat-pump-outline"

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._attr_name  # TODO: find how to get better HA ids

    @property
    def is_on(self):
        """Return the state of the sensor."""
        # TODO: Check if the value exists in the data
        return self.coordinator.data[HEAT_PUMP_STATUS] == HEAT_PUMP_ON
