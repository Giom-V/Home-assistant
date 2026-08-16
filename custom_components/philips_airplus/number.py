"""Number platform for Philips Air+ (CX3550/01).

  * timer  D03110  auto-off timer duration in HOURS (0 = off, 1..12h)

The device encodes the duration directly in D03110 as (hours + 1): 2=1h .. 13=12h,
0=off. Writing it both activates and sizes the timer; the remaining-minutes
countdown (D03211) is read-only and exposed as a sensor (see sensor.py).
"""
from __future__ import annotations

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    D_TIMER_ACT,
    DOMAIN,
    MANUFACTURER,
    MODEL_CX3550,
    TIMER_CODE_OFFSET,
    TIMER_HOURS_MAX,
    TIMER_HOURS_MIN,
    TIMER_OFF,
    UNIT_TIMER_HOURS,
)
from .coordinator import PhilipsAirplusCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    for coordinator in store["coordinators"].values():
        async_add_entities([PhilipsAirplusTimerNumber(coordinator)])


class PhilipsAirplusTimerNumber(CoordinatorEntity, NumberEntity):
    """Auto-off timer duration in hours (D03110; 0 = off, 1..12h)."""

    _attr_has_entity_name = True
    _attr_translation_key = "timer_hours"
    _attr_entity_category = EntityCategory.CONFIG
    _attr_device_class = NumberDeviceClass.DURATION
    _attr_native_unit_of_measurement = UNIT_TIMER_HOURS
    _attr_native_min_value = TIMER_HOURS_MIN
    _attr_native_max_value = TIMER_HOURS_MAX
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: PhilipsAirplusCoordinator) -> None:
        super().__init__(coordinator)
        self.coordinator = coordinator
        self._attr_unique_id = f"{coordinator.device_id}_timer_hours"

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

    @property
    def native_value(self) -> float | None:
        rep = self.coordinator.data or {}
        try:
            code = int(rep.get(D_TIMER_ACT))
        except (TypeError, ValueError):
            return None
        # 0 = off; valid on-codes are 2..13 (1..12h). Code 1 is out of range
        # (the device coerces it), so treat anything < 2 as off.
        return 0 if code < 2 else code - TIMER_CODE_OFFSET

    async def async_set_native_value(self, value: float) -> None:
        hours = int(round(value))
        code = TIMER_OFF if hours < 1 else hours + TIMER_CODE_OFFSET
        await self.coordinator.async_set_desired({D_TIMER_ACT: code})
