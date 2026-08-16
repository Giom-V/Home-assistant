"""Philips Air+ (CX3550/01) Home Assistant integration.

Cloud-only Philips Air+ fans (e.g. CX3550/01 "Series 3000") are controlled via an
AWS IoT device shadow over MQTT-over-WSS. This integration reverse-engineers the
Philips air-matters/gaoda auth chain (signed ``getToken`` -> 7-day JWT ->
``deviceList`` -> ``mqttInfo`` -> 1h single-use WSS URL) and drives the shadow.

One config entry per account (the ``user_id``); devices are auto-discovered via
``deviceList``. Each device gets its own persistent MQTT connection + coordinator.
"""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from . import airmatters_auth as auth
from .const import CONF_MSECRET, CONF_USER_ID, DOMAIN, JWT_REFRESH_MARGIN
from .coordinator import PhilipsAirplusCoordinator
from .device_connection import DeviceConnection

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["fan", "switch", "sensor", "number"]


class PhilipsAirplusData:
    """Account-level holder: user_id + msecret + cached JWT + device discovery.

    JWT and device-list calls are blocking (urllib); callers must run them in
    an executor (``hass.async_add_executor_job``).
    """

    def __init__(self, hass: HomeAssistant, user_id: str, msecret: str) -> None:
        self.hass = hass
        self.user_id = user_id
        self.msecret = msecret
        self._jwt: str | None = None

    @property
    def username(self) -> str:
        return "PHILIPS:" + self.user_id

    def get_jwt(self) -> str:
        """Return a valid JWT, refreshing from the signed getToken when near expiry.

        Blocking — call from an executor job.
        """
        if self._jwt and auth.jwt_seconds_left(self._jwt) > JWT_REFRESH_MARGIN:
            return self._jwt
        _LOGGER.info("Philips Air+: refreshing JWT for user %s", self.user_id[:8])
        self._jwt = auth.get_jwt(self.username, self.msecret)
        return self._jwt

    def get_device_list(self) -> list[dict]:
        """Return the account's bound devices. Blocking — call from an executor."""
        return auth.get_device_list(self.get_jwt())


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a Philips Air+ account from a config entry."""
    user_id = entry.data[CONF_USER_ID]
    msecret = entry.data.get(CONF_MSECRET)
    if not msecret:
        # Pre-0.2.0 entries only stored user_id (msecret was still hardcoded
        # in the integration). Trigger reauth instead of a raw KeyError so
        # the user gets the normal "re-authenticate" prompt, which now walks
        # them through the one-time APK upload to backfill it.
        raise ConfigEntryAuthFailed("Missing msecret — re-authentication required")
    data = PhilipsAirplusData(hass, user_id, msecret)

    # Auth check (signed getToken -> JWT). A failure here is a credential
    # problem -> reauth, not a retry.
    try:
        jwt = await hass.async_add_executor_job(data.get_jwt)
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Philips Air+: auth failed for user %s: %s", user_id[:8], err)
        raise ConfigEntryAuthFailed(f"Philips Air+ authentication failed: {err}") from err

    # Discover devices. A failure here is usually transient (503 LB) -> retry.
    try:
        devices = await hass.async_add_executor_job(lambda: auth.get_device_list(jwt))
    except Exception as err:  # noqa: BLE001
        _LOGGER.warning("Philips Air+: device discovery failed for user %s: %s", user_id[:8], err)
        raise ConfigEntryNotReady(f"Philips Air+ device discovery failed: {err}") from err

    if not devices:
        raise ConfigEntryNotReady("No Philips Air+ devices found for this account")

    coordinators: dict[str, PhilipsAirplusCoordinator] = {}
    for dev in devices:
        device_id = dev.get("device_id")
        if not device_id:
            continue
        dev_info = dev.get("device_info", {}) or {}
        coordinator = PhilipsAirplusCoordinator(hass, device_id, dev_info, connection=None)
        connection = DeviceConnection(hass, device_id, coordinator, data)
        coordinator.connection = connection
        coordinators[device_id] = coordinator
        _LOGGER.info(
            "Philips Air+: discovered %s (%s, %s)",
            device_id, dev_info.get("name", "?"), dev_info.get("modelid", "?"),
        )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "data": data,
        "coordinators": coordinators,
    }

    # Connect each device (best-effort; reconnect handles transient failures).
    for coordinator in coordinators.values():
        hass.async_create_task(coordinator.connection.async_connect())

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry and tear down all device connections."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        store = hass.data[DOMAIN].pop(entry.entry_id, None)
        if store:
            for coordinator in store["coordinators"].values():
                await coordinator.connection.async_shutdown()
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Clean up when the entry is deleted."""
    store = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if store:
        for coordinator in store["coordinators"].values():
            await coordinator.connection.async_shutdown()