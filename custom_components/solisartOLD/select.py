"""Solisart temperature inputs."""

from __future__ import annotations

import logging

import unidecode

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, MODE_SELECTS, MODES, SOLISART_ID, URL_UPDATE
from .solisart import decodeValue, encodeXML

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Solisart"


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the select platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    mode_selects = []
    mode_selects.extend(
        [
            SolisartModeSelect(coordinator, mode_select[0], mode_select[1], MODES)
            for mode_select in MODE_SELECTS
        ]
    )
    add_entities(mode_selects, True)


def modeID2modeName(id: str) -> str:
    for mode_name, mode_value in MODES:
        if id == mode_value:
            return mode_name
    return None


def modeName2modeId(name: str) -> id:
    for mode_name, mode_value in MODES:
        if name == mode_name:
            return mode_value
    return None


class SolisartModeSelect(CoordinatorEntity, SelectEntity):
    """Generic select for a heating modes exposed by Solisart."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        name: str,
        solisart_id: int,
        options: list,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = DEFAULT_NAME + " " + unidecode.unidecode(name)
        self._name = name
        self._solisart_id = solisart_id
        self._attr_options = [option[0] for option in options]

    @property
    def name(self) -> str:
        """Return the name of the input."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._attr_name  # TODO: find how to get better HA ids

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        # TODO: Check if the value exists in the data
        self._attr_current_option = modeID2modeName(
            decodeValue(self.coordinator.data[self._solisart_id])
        )
        return self._attr_current_option

    async def async_select_option(self, option: str) -> None:
        """Send the temperature value to the server."""
        url = URL_UPDATE

        payload = {
            "id": SOLISART_ID,
            "xml": encodeXML([[self._solisart_id, str(modeName2modeId(option))]]),
        }
        headers = {}

        # print(encodeXML([[self._solisart_id, str(modeName2modeId(option))]]))

        session = self.hass.data[DOMAIN]["session"]
        response = await self.hass.async_add_executor_job(
            lambda: session.request("POST", url, headers=headers, data=payload)
        )

        # TODO: report errors
