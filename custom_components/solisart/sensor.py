"""Solisart sensors."""
from __future__ import annotations

import logging

import unidecode

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    C2_FIRST_FLOOR,
    C3_GROUND_FLOOR,
    C5_WATER_SUN,
    C6_SPA,
    C7_UNDERFLOOR,
    DOMAIN,
    PUMP_SENSORS,
    T1_PANELS_OUT,
    T2_PANELS_IN,
    TEMPERATURE_SENSORS,
    V3V_HEAT_PUMP,
)

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "Solisart"

async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN]["coordinator"]

    temp_sensors = []
    for temp_sensor in TEMPERATURE_SENSORS:
        temp_sensors.append(SolisartTemperatureSensor(coordinator, temp_sensor[0], temp_sensor[1]))
    add_entities(temp_sensors, True)

    pump_sensors = []
    for pump_sensor in PUMP_SENSORS:
        pump_sensors.append(SolisartPumpSensor(coordinator, pump_sensor[0], pump_sensor[1]))
    add_entities(pump_sensors, True)

    add_entities([SolisartSolarEfficiencySensor(coordinator)], True)

class SolisartTemperatureSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor for a temperature exposed by Solisart."""

    def __init__(self, coordinator: DataUpdateCoordinator, name: str, value_id: int) -> None:
        super().__init__(coordinator)
        self._attr_name = DEFAULT_NAME+" "+unidecode.unidecode(name)
        self._name = name
        self._value_id = value_id
        self._attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
        self._attr_device_class = SensorDeviceClass.TEMPERATURE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._attr_name #TODO: find how to get better HA ids

    @property
    def state(self) -> float:
        """Return the state of the sensor."""
        # TODO: Check if the value exists in the data
        return self.coordinator.data[self._value_id].replace(" dC","")

class SolisartPumpSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor for a pump exposed by Solisart."""

    # TODO: Manage the valves differently, but I couldn't find a better device class

    def __init__(self, coordinator: DataUpdateCoordinator, name: str, value_id: int) -> None:
        super().__init__(coordinator)
        self._attr_name = DEFAULT_NAME+" "+unidecode.unidecode(name)
        self._name = name
        self._value_id = value_id
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._attr_name #TODO: find how to get better HA ids

    @property
    def state(self) -> float:
        """Return the state of the sensor."""
        # TODO: Check if the value exists in the data
        return self.coordinator.data[self._value_id].replace("pC","")

class SolisartSolarEfficiencySensor(CoordinatorEntity, SensorEntity):
    """Sensor that estimates the amount of energy provided by the solar panels."""

    def __init__(self, coordinator: DataUpdateCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_name = "Efficacité panneaux solaires"
        self._name = self._attr_name
        self._attr_device_class = SensorDeviceClass.IRRADIANCE
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._name

    @property
    def unique_id(self) -> str:
        """Return a unique, Home Assistant friendly identifier for this entity."""
        return self._attr_name #TODO: find how to get better HA ids

    @property
    def state(self) -> float:
        """Return the state of the sensor."""
        # TODO: Check if the values exist in the data
        return( (
                    float(self.coordinator.data[C5_WATER_SUN].replace("pC","")) +
                    ( 1 - float(self.coordinator.data[V3V_HEAT_PUMP].replace("pC","") ) / 100 )
                        * (
                            float(self.coordinator.data[C7_UNDERFLOOR].replace("pC","")) +
                            float(self.coordinator.data[C2_FIRST_FLOOR].replace("pC","")) +
                            float(self.coordinator.data[C3_GROUND_FLOOR].replace("pC","")) +
                            float(self.coordinator.data[C6_SPA].replace("pC",""))
                        )
                )
                * (
                    float(self.coordinator.data[T1_PANELS_OUT].replace(" dC","")) -
                    float(self.coordinator.data[T2_PANELS_IN].replace(" dC",""))
                )
        )
