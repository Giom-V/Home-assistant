#!/usr/bin/env python3
"""dLight integration"""

from __future__ import annotations

import json
import logging
import socket

import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (SUPPORT_BRIGHTNESS, SUPPORT_COLOR_TEMP, ATTR_BRIGHTNESS, ATTR_COLOR_TEMP, PLATFORM_SCHEMA, LightEntity)
from homeassistant.const import CONF_HOST, CONF_DEVICE_ID, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DOMAIN = 'dlight'
_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_DEVICE_ID): cv.string,
    vol.Optional(CONF_PORT, default=3333): cv.port,
})

def get_query_device_info(device_id):
    return {
        "commandId": "1",
        "deviceId": device_id,
        "commandType": "QUERY_DEVICE_INFO",
    }

def get_query_device_states(device_id):
    return {
        "commandId": "2",
        "deviceId": device_id,
        "commandType": "QUERY_DEVICE_STATES",
    }

def get_execute(device_id):
    return {
        "commandId": "3",
        "deviceId": device_id,
        "commandType": "EXECUTE",
    }

def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    add_entities([dLight(config[CONF_HOST], config[CONF_PORT], config[CONF_DEVICE_ID])], True)

class dLight(LightEntity):
    """Representation of a dLight."""

    def __init__(self, host, port, device_id) -> None:
        """Initialize a dLight."""
        self._host = host
        self._port = port
        self._device_id = device_id

    @property
    def supported_features(self):
        return SUPPORT_BRIGHTNESS | SUPPORT_COLOR_TEMP

    @property
    def min_mireds(self):
        """Return the minimum color temperature in mireds for the dLight.

        This is calculated as 1000000 / 2600."""
        return 167

    @property
    def max_mireds(self):
        """Return the maximum color temperature in mireds for the dLight.

        This is calculated as 1000000 / 6000."""
        return 384

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return self._device_id

    @property
    def name(self) -> str:
        """Display name of this light."""
        return f"dLight {self._device_id}"

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return self._brightness * 255 / 100

    @property
    def color_temp(self):
        """Return the color temperature of the light in mireds."""
        return int(1000000 / self._temperature)

    @property
    def is_on(self) -> bool | None:
        """Return true if light is on."""
        return self._on

    def turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        values = { "on": True }
        if ATTR_BRIGHTNESS in kwargs:
            values[ATTR_BRIGHTNESS] = int(float(kwargs[ATTR_BRIGHTNESS]) / 255 * 100)
        if ATTR_COLOR_TEMP in kwargs:
            values["color"] = { "temperature": int(1000000 / float(kwargs[ATTR_COLOR_TEMP])) }

        self.set_values(**values)

    def turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        self.set_values(on=False)

    def update(self) -> None:
        """Fetch new state data for this light."""
        self._on, self._brightness, self._temperature = self.get_states()

    def get_states(self):
        states = self.make_call(get_query_device_states(self._device_id))['states']
        return states['on'], states['brightness'], states['color']['temperature']

    def make_call(self, query):
        jquery = json.dumps(query)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._host, self._port))
            s.sendall(bytes(jquery, encoding='UTF-8'))
            data = s.recv(8*1024)
            recv = data.decode('UTF-8')
        # TODO: Parse the result if SUCCESS and set cached values
        return json.loads(recv[4:])

    def set_values(self, **kwargs):
        query = get_execute(self._device_id).copy()
        query['commands'] = [kwargs]
        return self.make_call(query)
