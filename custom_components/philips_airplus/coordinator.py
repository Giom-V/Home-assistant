"""DataUpdateCoordinator for one Philips Air+ fan (push primary, reconcile poll).

The device pushes shadow deltas over the persistent MQTT connection; the
DeviceConnection feeds ``reported`` here from the paho thread via
``threadsafe_set_data``. Entities are ``CoordinatorEntity`` with
``should_poll=False`` and read ``coordinator.data``.

A periodic ``update_interval`` republishes ``shadow/get`` so device-side
changes (physical buttons on the unit, or a push missed while reconnecting)
surface in HA — the push path is primary, the poll is a reconcile safety net.
"""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import D_CONNECT_TYPE, REFRESH_INTERVAL

_LOGGER = logging.getLogger(__name__)


class PhilipsAirplusCoordinator(DataUpdateCoordinator):
    """Holds the latest ``reported`` shadow state for one device."""

    def __init__(self, hass: HomeAssistant, device_id: str, device_info: dict, connection) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"philips_airplus_{device_id}",
            update_interval=timedelta(seconds=REFRESH_INTERVAL),  # reconcile poll (push is primary)
        )
        self.device_id = device_id
        self.device_info = device_info  # deviceList device_info dict (name, mac, modelid, ...)
        self.connection = connection
        self.connected = False
        self.data: dict = {}

    async def async_update_data(self) -> dict:
        """Reconcile: ask the shadow for its current reported state. The reply lands
        async on /get/accepted via threadsafe_set_data; return what's cached now."""
        if self.connected:
            self.connection.request_shadow_get()
        return self.data

    @property
    def device_available(self) -> bool:
        """Whether entities should show as available.

        ``connected`` only means our own MQTT socket reached the AWS IoT
        broker — that succeeds even when the physical fan itself is offline
        (WiFi down, unplugged). Once a shadow read has arrived, defer to its
        ``ConnectType`` field (the device's own reported connectivity,
        confirmed maintained server-side — it's the same signal the Philips
        app shows "not available" from). Before the first read, fall back to
        the socket state so entities don't flicker unavailable while it
        arrives (typically under a second after connect).
        """
        if not self.connected:
            return False
        if not self.data:
            return True
        return self.data.get(D_CONNECT_TYPE) == "Online"

    # ---- push entry point (called from the HA loop by DeviceConnection) ----
    def threadsafe_set_data(self, reported: dict) -> None:
        """Set the latest reported state and notify entities. Runs on the HA loop."""
        self.data = reported or {}
        self.last_update_success = True
        self.async_update_listeners()

    # ---- connection state (called from the paho thread) ----
    def set_connection_state(self, connected: bool, error: str | None = None) -> None:
        """Update availability. Threadsafe — called from the paho network thread."""
        self.hass.loop.call_soon_threadsafe(self._set_connection_state, connected, error)

    def _set_connection_state(self, connected: bool, error: str | None) -> None:
        changed = self.connected != connected
        self.connected = connected
        if changed:
            if connected:
                _LOGGER.info("Philips Air+ %s: online", self.device_id)
            else:
                _LOGGER.info("Philips Air+ %s: offline (%s)", self.device_id, error or "disconnected")
            self.async_update_listeners()

    # ---- command helper used by entities ----
    async def async_set_desired(self, desired: dict) -> None:
        await self.connection.async_set_desired(desired)