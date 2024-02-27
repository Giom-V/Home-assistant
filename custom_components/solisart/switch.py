"""Solisart sensors."""
from __future__ import annotations

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from .solisart import encodeXML

from .const import DOMAIN, HOLIDAY_MODE, HOLIDAY_MODE_ON, SOLISART_ID, URL_UPDATE

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

    add_entities([SolisartHolidayModeSwitch(coordinator)], True)


class SolisartHolidayModeSwitch(CoordinatorEntity, SwitchEntity):
    """Sensor for the holiday mode."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "Mode vacances Solisart"
        self._name = self._attr_name
        self._attr_icon = "mdi:home-export-outline"

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._attr_name #TODO: find how to get better HA ids

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        # TODO: Check if the value exists in the data
        return self.coordinator.data[HOLIDAY_MODE] == HOLIDAY_MODE_ON

    async def async_turn_on(self):
        url = URL_UPDATE

        payload = {
            "id": SOLISART_ID,
            "xml": encodeXML([[HOLIDAY_MODE, 1]])
        }
        headers = {}

        session = self.hass.data[DOMAIN]["session"]
        response = await self.hass.async_add_executor_job(lambda : session.request("POST", url, headers=headers, data=payload))

        #TODO: force data update
        await self.coordinator.async_refresh()

    async def async_turn_off(self):
        url = URL_UPDATE

        payload = {
            "id": SOLISART_ID,
            "xml": "PHZhbGV1cnM+PHZhbGV1ciBkb25uZWU9IjEzNSIgdmFsZXVyPSJNQT09IiAvPjwvdmFsZXVycz4="
        }
        headers = {}

        session = self.hass.data[DOMAIN]["session"]
        response = await self.hass.async_add_executor_job(lambda : session.request("POST", url, headers=headers, data=payload))

        #TODO: force data update
