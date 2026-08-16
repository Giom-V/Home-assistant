"""Switch platform for Philips Air+ (CX3550/01).

Two CONFIG-category switches per fan:
  * beep           D03130  100=on / 0=off  (key-tone on button press)
  * timer          D03110    2=on / 0=off  (activate the auto-off timer)

The remaining timer minutes (D03211) is a read-only countdown, exposed as a
sensor (see sensor.py) — it is not settable (writes are ignored by the device).
"""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    BEEP_OFF,
    BEEP_ON,
    D_BEEP,
    D_TIMER_ACT,
    DOMAIN,
    MANUFACTURER,
    MODEL_CX3550,
    TIMER_OFF,
    TIMER_ON,
)
from .coordinator import PhilipsAirplusCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    for coordinator in store["coordinators"].values():
        async_add_entities([PhilipsAirplusBeepSwitch(coordinator), PhilipsAirplusTimerSwitch(coordinator)])


class _AirplusSwitch(CoordinatorEntity, SwitchEntity):
    """Common base: availability + device info derived from the coordinator."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

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

    def _int(self, code: str, default: int = 0) -> int:
        try:
            return int(self._rep().get(code, default))
        except (TypeError, ValueError):
            return default


class PhilipsAirplusBeepSwitch(_AirplusSwitch):
    """Key-tone on/off (D03130)."""

    _attr_translation_key = "beep"

    def __init__(self, coordinator: PhilipsAirplusCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_beep"

    @property
    def is_on(self) -> bool:
        return self._int(D_BEEP) == BEEP_ON

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_desired({D_BEEP: BEEP_ON})

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_desired({D_BEEP: BEEP_OFF})


class PhilipsAirplusTimerSwitch(_AirplusSwitch):
    """Auto-off timer activate (D03110). The countdown lives in sensor.py."""

    _attr_translation_key = "timer"

    def __init__(self, coordinator: PhilipsAirplusCoordinator) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device_id}_timer"

    @property
    def is_on(self) -> bool:
        # Any non-zero D03110 = timer running (2=1h .. 13=12h); the Number entity
        # sets the duration, so match on != off rather than the 1h default value.
        return self._int(D_TIMER_ACT) != TIMER_OFF

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_desired({D_TIMER_ACT: TIMER_ON})

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_desired({D_TIMER_ACT: TIMER_OFF})