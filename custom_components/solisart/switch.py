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

from .const import (
    DOMAIN,
    HOLIDAY_MODE,
    SOLISART_ID,
    SWITCH_ENTITIES,
    SWITCH_IS_ON,
    URL_UPDATE,
)
from .solisart import encodeXML

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

    switches = []
    for switch_entry in SWITCH_ENTITIES:
        switches.append(
            SolisartSwitch(
                coordinator,
                switch_entry[
                    0
                ],  # Would there be a better way to do that instead of listing each value of the array?
                switch_entry[1],
                switch_entry[2],
                switch_entry[3],
                switch_entry[4],
                switch_entry[5],
            )
        )

    add_entities(switches, True)


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
        return self._attr_name  # TODO: find how to get better HA ids

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        # TODO: Check if the value exists in the data
        return self.coordinator.data[HOLIDAY_MODE] == SWITCH_IS_ON

    async def async_turn_on(self):
        url = URL_UPDATE

        payload = {
            "id": SOLISART_ID,
            "xml": "PHZhbGV1cnM+PHZhbGV1ciBkb25uZWU9IjEzNSIgdmFsZXVyPSJNUT09IiAvPjwvdmFsZXVycz4=",  # encodeXML([[HOLIDAY_MODE, 1]])
        }
        headers = {}

        session = self.hass.data[DOMAIN]["session"]
        response = await self.hass.async_add_executor_job(
            lambda: session.request("POST", url, headers=headers, data=payload)
        )

        # TODO: force data update
        await self.coordinator.async_refresh()

    async def async_turn_off(self):
        url = URL_UPDATE

        payload = {
            "id": SOLISART_ID,
            "xml": "PHZhbGV1cnM+PHZhbGV1ciBkb25uZWU9IjEzNSIgdmFsZXVyPSJNQT09IiAvPjwvdmFsZXVycz4=",
        }
        headers = {}

        session = self.hass.data[DOMAIN]["session"]
        response = await self.hass.async_add_executor_job(
            lambda: session.request("POST", url, headers=headers, data=payload)
        )

        # TODO: force data update


# TODO: Make a generic SwitchEntity with name and icon
class SolisartSwitch(CoordinatorEntity, SwitchEntity):
    """Generic sensor for a switch exposed by Solisart."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        icon: str,
        id: int,
        value_is_on: str,
        value_turn_on: str,
        value_turn_off: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._name = self._attr_name
        self._attr_icon = icon
        self._solisart_id = id
        self._value_is_on = value_is_on
        self._value_turn_on = value_turn_on
        self._value_turn_off = value_turn_off

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._attr_name  # TODO: find how to get better HA ids

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        # TODO: Check if the value exists in the data
        return self.coordinator.data[self._solisart_id] == self._value_is_on

    async def async_turn_on(self):
        """Send the "turn on" command to the server ."""
        url = URL_UPDATE

        payload = {
            "id": SOLISART_ID,
            "xml": encodeXML([[self._solisart_id, self._value_turn_on]]),
        }
        headers = {}

        session = self.hass.data[DOMAIN]["session"]
        response = await self.hass.async_add_executor_job(
            lambda: session.request("POST", url, headers=headers, data=payload)
        )

        # TODO: force a delayed data update or force status
        # await self.coordinator.async_refresh() is too fast

    async def async_turn_off(self):
        """Send the "turn off" command to the server ."""
        url = URL_UPDATE

        payload = {
            "id": SOLISART_ID,
            "xml": encodeXML([[self._solisart_id, self._value_turn_off]]),
        }
        headers = {}

        session = self.hass.data[DOMAIN]["session"]
        response = await self.hass.async_add_executor_job(
            lambda: session.request("POST", url, headers=headers, data=payload)
        )

        # TODO: force a delayed data update or force status
