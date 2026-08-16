"""Diagnostics support for Philips Air+.

Redacts the account user_id and device-identifying fields (DeviceId, ProductId,
serial) from the downloaded diagnostic dumps. The SigV4 WSS URLs are not stored
in the integration (they are single-use and fetched on demand), so they never
appear in diagnostics.
"""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.redact import async_redact_data

from .const import CONF_EMAIL, CONF_MSECRET, CONF_USER_ID, DOMAIN

# Keys in the config-entry data / runtime to mask.
TO_REDACT = {
    CONF_USER_ID, CONF_MSECRET, CONF_EMAIL,
    "user_id", "msecret", "email", "jwt", "refresh_token", "registration_id",
}
# Keys inside the shadow `reported` payload to mask.
TO_REDACT_REPORTED = {"DeviceId", "ProductId", "D01S0D", "D01S03", "registration_id"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry (account-level)."""
    store = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinators = store.get("coordinators", {})
    data: dict[str, Any] = {
        "entry": {
            "title": entry.title,
            "unique_id": entry.unique_id,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
        },
        "devices": [],
    }
    for device_id, coordinator in coordinators.items():
        data["devices"].append(
            {
                "device_id": device_id,
                "connected": coordinator.connected,
                "device_available": coordinator.device_available,
                "device_info": async_redact_data(coordinator.device_info or {}, {"mac"}),
                "reported": async_redact_data(coordinator.data or {}, TO_REDACT_REPORTED),
            }
        )
    return data


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: dr.DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a single device."""
    store = hass.data.get(DOMAIN, {}).get(entry.entry_id, {})
    coordinators = store.get("coordinators", {})
    # Match the device by its integration identifier.
    device_id = None
    for ident in device.identifiers:
        if ident[0] == DOMAIN:
            device_id = ident[1]
            break
    coordinator = coordinators.get(device_id)
    if coordinator is None:
        return {
            "device": {
                "name": device.name,
                "name_by_user": device.name_by_user,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "sw_version": device.sw_version,
            }
        }

    ent_reg = er.async_get(hass)
    entities = [
        {
            "entity_id": e.entity_id,
            "unique_id": e.unique_id,
            "disabled": e.disabled_by is not None,
        }
        for e in ent_reg.entities.get_entries_for_device_id(device.id)
    ]
    return {
        "device_id": device_id,
        "connected": coordinator.connected,
        "device_info": async_redact_data(coordinator.device_info or {}, {"mac"}),
        "reported": async_redact_data(coordinator.data or {}, TO_REDACT_REPORTED),
        "entities": entities,
    }