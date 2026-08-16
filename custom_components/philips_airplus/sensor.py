"""Sensor platform for Philips Air+ (CX3550/01).

  * timer_remaining   D03211  minutes (read-only countdown of the auto-off timer)
  * rssi              rssi    dBm   (DIAGNOSTIC, disabled by default)
  * runtime           Runtime seconds (DIAGNOSTIC, disabled by default)
  * free_memory       free_memory bytes (DIAGNOSTIC, disabled by default)

The timer countdown (D03211) is **read-only**: writing it is ignored by the
device (it sets the value itself when the timer is activated via D03110). So
it is exposed as a sensor, not a Number.
"""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import SIGNAL_STRENGTH_DECIBELS_MILLIWATT, UnitOfInformation, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    D_FREE_MEMORY,
    D_RSSI,
    D_RUNTIME,
    D_TIMER_MIN,
    DOMAIN,
    MANUFACTURER,
    MODEL_CX3550,
)
from .coordinator import PhilipsAirplusCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    for coordinator in store["coordinators"].values():
        async_add_entities(
            [
                PhilipsAirplusTimerRemaining(coordinator),
                PhilipsAirplusRssiSensor(coordinator),
                PhilipsAirplusRuntimeSensor(coordinator),
                PhilipsAirplusFreeMemorySensor(coordinator),
            ]
        )


class _AirplusSensor(CoordinatorEntity, SensorEntity):
    """Common base."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PhilipsAirplusCoordinator) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator

    @property
    def device_info(self) -> DeviceInfo:
        di = self.coordinator.device_info or {}
        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.device_id)},
            name=di.get("name") or di.get("device_alias"),
            manufacturer=MANUFACTURER,
            model=di.get("modelid") or MODEL_CX3550,
            sw_version=di.get("swversion"),
            serial_number=di.get("mac"),
        )

    @property
    def available(self) -> bool:
        return self.coordinator.device_available

    def _rep(self) -> dict:
        return self.coordinator.data or {}

    def _num(self, code: str):
        try:
            return int(self._rep().get(code))
        except (TypeError, ValueError):
            return None


class PhilipsAirplusTimerRemaining(_AirplusSensor):
    """Remaining minutes of the auto-off timer (D03211, read-only countdown)."""

    _attr_translation_key = "timer_remaining"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: PhilipsAirplusCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_timer_remaining"

    @property
    def native_value(self):
        return self._num(D_TIMER_MIN)


class PhilipsAirplusRssiSensor(_AirplusSensor):
    """WiFi signal strength (rssi, dBm)."""

    _attr_translation_key = "rssi"
    _attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH
    _attr_native_unit_of_measurement = SIGNAL_STRENGTH_DECIBELS_MILLIWATT
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: PhilipsAirplusCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_rssi"

    @property
    def native_value(self):
        return self._num(D_RSSI)


class PhilipsAirplusRuntimeSensor(_AirplusSensor):
    """Device uptime (Runtime, seconds)."""

    _attr_translation_key = "runtime"
    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.SECONDS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: PhilipsAirplusCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_runtime"

    @property
    def native_value(self):
        return self._num(D_RUNTIME)


class PhilipsAirplusFreeMemorySensor(_AirplusSensor):
    """Free heap memory (free_memory, bytes)."""

    _attr_translation_key = "free_memory"
    _attr_device_class = SensorDeviceClass.DATA_SIZE
    _attr_native_unit_of_measurement = UnitOfInformation.BYTES
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_entity_registry_enabled_default = False

    def __init__(self, coordinator: PhilipsAirplusCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_free_memory"

    @property
    def native_value(self):
        return self._num(D_FREE_MEMORY)