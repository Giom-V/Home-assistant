# custom_components/mon_eau/entity.py
"""Base commune des entités Mon Eau : device, unique_id, parsing de dates."""
from __future__ import annotations

from datetime import datetime

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


def parse_date(value: str | None) -> datetime | None:
    """ISO → datetime aware (les dates orobnat sont naïves : heure locale)."""
    from homeassistant.util import dt as dt_util

    if not value:
        return None
    parsed = dt_util.parse_datetime(value)
    if parsed is None:
        parsed_date = dt_util.parse_date(value)
        if parsed_date is None:
            return None
        parsed = datetime.combine(parsed_date, datetime.min.time())
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt_util.get_default_time_zone())
    return parsed


class MonEauEntity(CoordinatorEntity):
    """Entité rattachée à un device Mon Eau (commune, rivière, nappe ou sécheresse)."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        entry_id: str,
        device_key: str,
        device_name: str,
        key: str,
        device_model: str | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_{device_key}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{entry_id}_{device_key}")},
            name=device_name,
            manufacturer="Mon Eau",
            model=device_model or "Données publiques françaises",
        )
