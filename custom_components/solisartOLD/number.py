"""Solisart temperature inputs."""

from __future__ import annotations

import logging

import unidecode

from homeassistant.components.number import NumberDeviceClass, NumberEntity
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    MAX_OFFSET,
    MAX_TEMPERATURE,
    MIN_OFFSET,
    MIN_TEMPERATURE,
    OFFSET_INPUTS,
    SOLISART_ID,
    TEMP_INPUTS,
    URL_UPDATE,
)
from .solisart import decodeValue, encodeXML

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Solisart"


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the number platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    temp_inputs = []
    temp_inputs.extend(
        [
            SolisartTemperatureInputNumber(
                coordinator,
                temp_input[0],
                temp_input[1],
                MIN_TEMPERATURE,
                MAX_TEMPERATURE,
            )
            for temp_input in TEMP_INPUTS
        ]
    )

    add_entities(temp_inputs, True)

    offset_inputs = []
    for offset_input in OFFSET_INPUTS:
        offset_inputs.append(
            SolisartTemperatureInputNumber(
                coordinator, offset_input[0], offset_input[1], MIN_OFFSET, MAX_OFFSET
            )
        )
    add_entities(offset_inputs, True)


class SolisartTemperatureInputNumber(CoordinatorEntity, NumberEntity):
    """Generic sensor for a temperature input exposed by Solisart."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        solisart_id: int,
        min: float,
        max: float,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = DEFAULT_NAME + " " + unidecode.unidecode(name)
        self._name = name
        self._solisart_id = solisart_id
        self._attr_native_step = 0.1
        self._attr_native_min_value = min
        self._attr_native_max_value = max
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = NumberDeviceClass.TEMPERATURE

    @property
    def name(self) -> str:
        """Return the name of the input."""
        return self._name

    @property
    def native_step(self) -> float:
        """Return the steps of the input."""
        return self._attr_native_step

    @property
    def native_min_value(self) -> float:
        """Return the min value of the input."""
        return self._attr_native_min_value

    @property
    def native_max_value(self) -> float:
        """Return the max value of the input."""
        return self._attr_native_max_value

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._attr_name  # TODO: find how to get better HA ids

    @property
    def state(self) -> float:
        """Return the state of the sensor."""
        # TODO: Check if the value exists in the data
        self._attr_native_value = decodeValue(self.coordinator.data[self._solisart_id])
        return self._attr_native_value

    async def async_set_native_value(self, value: float) -> None:
        """Send the temperature value to the server."""
        # TODO: All of that should be a shered function in solisart.py

        url = URL_UPDATE

        payload = {
            "id": SOLISART_ID,
            "xml": encodeXML([[self._solisart_id, str(value)]]),
        }
        headers = {}

        # print(encodeXML([[self._solisart_id, str(value)]]))

        session = self.hass.data[DOMAIN]["session"]
        response = await self.hass.async_add_executor_job(
            lambda: session.request("POST", url, headers=headers, data=payload)
        )

        # TODO: report errors
