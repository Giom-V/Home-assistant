from __future__ import annotations

import logging
import re
from typing import Any

import homeassistant.helpers.device_registry as dr
import homeassistant.helpers.entity_registry as er
from homeassistant.components.light import DOMAIN as LIGHT_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.config_entries import SOURCE_INTEGRATION_DISCOVERY, SOURCE_USER
from homeassistant.const import CONF_ENTITY_ID, CONF_PLATFORM, CONF_UNIQUE_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import discovery_flow
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.typing import ConfigType

from .common import SourceEntity, create_source_entity
from .const import (
    CONF_MANUFACTURER,
    CONF_MODE,
    CONF_MODEL,
    CONF_SENSORS,
    DATA_DISCOVERY_MANAGER,
    DISCOVERY_POWER_PROFILES,
    DISCOVERY_SOURCE_ENTITY,
    DOMAIN,
    MANUFACTURER_WLED,
    CalculationStrategy,
)
from .errors import ModelNotSupportedError
from .helpers import get_or_create_unique_id
from .power_profile.factory import get_power_profile
from .power_profile.library import ModelInfo, ProfileLibrary
from .power_profile.power_profile import PowerProfile

_LOGGER = logging.getLogger(__name__)


async def get_power_profile_by_source_entity(hass: HomeAssistant, source_entity: SourceEntity) -> PowerProfile | None:
    """Given a certain entity, lookup the manufacturer and model and return the power profile."""
    try:
        discovery_manager: DiscoveryManager = hass.data[DOMAIN][DATA_DISCOVERY_MANAGER]
    except KeyError:
        discovery_manager = DiscoveryManager(hass, {})
    model_info = await discovery_manager.extract_model_info_from_entity(source_entity.entity_entry)
    if not model_info:
        return None
    profiles = await discovery_manager.discover_entity(source_entity, model_info)
    return profiles[0] if profiles else None


class DiscoveryManager:
    """This class is responsible for scanning the HA instance for entities and their manufacturer / model info
    It checks if any of these devices is supported in the powercalc library
    When entities are found it will dispatch a discovery flow, so the user can add them to their HA instance.
    """

    def __init__(self, hass: HomeAssistant, ha_config: ConfigType) -> None:
        self.hass = hass
        self.ha_config = ha_config
        self.power_profiles: dict[str, PowerProfile | None] = {}
        self.manually_configured_entities: list[str] | None = None
        self.initialized_flows: set[str] = set()
        self.library: ProfileLibrary | None = None

    async def start_discovery(self) -> None:
        """Start the discovery procedure."""

        for entry in self.hass.config_entries.async_entries(DOMAIN):
            if entry.unique_id:
                self.initialized_flows.update({entry.unique_id, str(entry.data.get(CONF_ENTITY_ID))})

        _LOGGER.debug("Start auto discovering entities")
        entity_registry = er.async_get(self.hass)
        for entity_entry in list(entity_registry.entities.values()):
            source_entity = await create_source_entity(entity_entry.entity_id, self.hass)
            try:
                model_info = await self.extract_model_info_from_entity(source_entity.entity_entry)
                if not model_info:
                    continue

                power_profiles = await self.discover_entity(source_entity, model_info)
                if not power_profiles:
                    continue

                unique_id = get_or_create_unique_id(
                    {},
                    source_entity,
                    power_profiles[0] if power_profiles else None,
                )
                if self._is_already_discovered(source_entity, unique_id):
                    _LOGGER.debug(
                        "%s: Already setup with discovery, skipping new discovery",
                        source_entity.entity_id,
                    )
                    continue
                self._init_entity_discovery(source_entity, model_info, unique_id, power_profiles, {})
            except Exception:
                _LOGGER.exception(
                    "%s: Error during auto discovery",
                    source_entity.entity_id,
                )

        _LOGGER.debug("Done auto discovering entities")

    async def _get_library(self) -> ProfileLibrary:
        """Get the powercalc library instance."""
        if not self.library:
            self.library = await ProfileLibrary.factory(self.hass)
        return self.library

    async def discover_entity(
        self,
        source_entity: SourceEntity,
        model_info: ModelInfo,
    ) -> list[PowerProfile] | None:
        """Discover a single entity in Powercalc library and start the discovery flow if supported."""

        library = await self._get_library()
        if source_entity.entity_entry is None:  # pragma: no cover
            return None

        if self.is_wled_light(model_info, source_entity.entity_entry):
            await self.init_wled_flow(model_info, source_entity)
            return None

        manufacturer = await library.find_manufacturer(model_info)
        if not manufacturer:
            _LOGGER.debug(
                "%s: Manufacturer not found in library, skipping discovery",
                source_entity.entity_entry.entity_id,
            )
            return None

        models = await library.find_models(manufacturer, model_info)
        if not models:
            _LOGGER.debug(
                "%s: Model not found in library, skipping discovery",
                source_entity.entity_entry.entity_id,
            )
            return None

        power_profiles = []
        for model in models:
            model_info = ModelInfo(manufacturer, model)
            profile = await get_power_profile(self.hass, {}, model_info=model_info)
            if not profile:  # pragma: no cover
                continue
            if not await self.is_entity_supported(source_entity.entity_entry, model_info, profile):
                continue
            power_profiles.append(profile)

        return power_profiles

    async def init_wled_flow(self, model_info: ModelInfo, source_entity: SourceEntity) -> None:
        """Initialize the discovery flow for a WLED light."""
        unique_id = f"pc_{source_entity.device_entry.id}" if source_entity.device_entry else get_or_create_unique_id({}, source_entity, None)
        if self._is_already_discovered(source_entity, unique_id):
            _LOGGER.debug(
                "%s: Already setup with discovery, skipping new discovery (unique_id=%s)",
                source_entity.entity_id,
                unique_id,
            )
            return

        self._init_entity_discovery(
            source_entity,
            model_info,
            unique_id,
            power_profiles=None,
            extra_discovery_data={
                CONF_MODE: CalculationStrategy.WLED,
            },
        )

    @staticmethod
    def is_wled_light(model_info: ModelInfo, entity_entry: er.RegistryEntry) -> bool:
        """Check if the entity is a WLED light."""
        return (
            model_info.manufacturer == MANUFACTURER_WLED
            and entity_entry.domain == LIGHT_DOMAIN
            and not re.search("master|segment", str(entity_entry.original_name), flags=re.IGNORECASE)
            and not re.search("master|segment", str(entity_entry.entity_id), flags=re.IGNORECASE)
        )

    async def is_entity_supported(
        self,
        entity_entry: er.RegistryEntry,
        model_info: ModelInfo | None = None,
        power_profile: PowerProfile | None = None,
        log_profile_loading_errors: bool = True,
    ) -> bool:
        if not self.should_process_entity(entity_entry):
            return False

        if not model_info:
            model_info = await self.extract_model_info_from_entity(entity_entry)
        if not model_info or not model_info.manufacturer or not model_info.model:
            return False

        if not power_profile:
            try:
                power_profile = await get_power_profile(self.hass, {}, model_info, log_errors=log_profile_loading_errors)
            except ModelNotSupportedError:
                return False

        return power_profile.is_entity_domain_supported(entity_entry) if power_profile else False

    def should_process_entity(self, entity_entry: er.RegistryEntry) -> bool:
        """Do some validations on the registry entry to see if it qualifies for discovery."""
        if entity_entry.disabled:
            return False

        if entity_entry.entity_category in [
            EntityCategory.CONFIG,
            EntityCategory.DIAGNOSTIC,
        ]:
            return False

        has_user_config = self._is_user_configured(entity_entry.entity_id)
        if has_user_config:
            _LOGGER.debug(
                "%s: Entity is manually configured, skipping auto configuration",
                entity_entry.entity_id,
            )
            return False

        return True

    async def extract_model_info_from_entity(self, entity_entry: er.RegistryEntry | None) -> ModelInfo | None:
        """Try to auto discover manufacturer and model from the known device information."""
        if not entity_entry or not entity_entry.device_id:
            return None

        model_info = await self.get_model_information(entity_entry)
        if not model_info:
            _LOGGER.debug(
                "%s: Cannot autodiscover model, manufacturer or model unknown from device registry",
                entity_entry.entity_id,
            )
            return None

        # Make sure we don't have a literal / in model_id,
        # so we don't get issues with sublut directory matching down the road
        # See github #658
        if "/" in model_info.model:
            model_info = ModelInfo(
                model_info.manufacturer,
                model_info.model.replace("/", "#slash#"),
                model_info.model_id,
            )

        _LOGGER.debug(
            "%s: Found model information on device (manufacturer=%s, model=%s, model_id=%s)",
            entity_entry.entity_id,
            model_info.manufacturer,
            model_info.model,
            model_info.model_id,
        )
        return model_info

    async def get_model_information(self, entity_entry: er.RegistryEntry) -> ModelInfo | None:
        """See if we have enough information in device registry to automatically setup the power sensor."""
        if entity_entry.device_id is None:
            return None
        device_registry = dr.async_get(self.hass)
        device_entry = device_registry.async_get(entity_entry.device_id)
        if device_entry is None or device_entry.manufacturer is None or device_entry.model is None:
            return None

        manufacturer = str(device_entry.manufacturer)
        model = str(device_entry.model)
        model_id = device_entry.model_id if hasattr(device_entry, "model_id") else None

        if len(manufacturer) == 0 or len(model) == 0:
            return None

        return ModelInfo(manufacturer, model, model_id)

    @callback
    def _init_entity_discovery(
        self,
        source_entity: SourceEntity,
        model_info: ModelInfo,
        unique_id: str,
        power_profiles: list[PowerProfile] | None,
        extra_discovery_data: dict | None,
    ) -> None:
        """Dispatch the discovery flow for a given entity."""

        discovery_data: dict[str, Any] = {
            CONF_ENTITY_ID: source_entity.entity_id,
            DISCOVERY_SOURCE_ENTITY: source_entity,
            CONF_UNIQUE_ID: unique_id,
        }

        if power_profiles:
            discovery_data[DISCOVERY_POWER_PROFILES] = power_profiles
            if len(power_profiles) == 1:
                power_profile = power_profiles[0]
                discovery_data[CONF_MANUFACTURER] = power_profile.manufacturer
                discovery_data[CONF_MODEL] = power_profile.model

        if CONF_MANUFACTURER not in discovery_data:
            discovery_data[CONF_MANUFACTURER] = model_info.manufacturer
        if CONF_MODEL not in discovery_data:
            discovery_data[CONF_MODEL] = model_info.model or model_info.model_id

        if extra_discovery_data:
            discovery_data.update(extra_discovery_data)

        self.initialized_flows.update({unique_id, source_entity.entity_id})

        _LOGGER.debug("%s: Initiating discovery flow, unique_id=%s", source_entity.entity_id, unique_id)

        discovery_flow.async_create_flow(
            self.hass,
            DOMAIN,
            context={"source": SOURCE_INTEGRATION_DISCOVERY},
            data=discovery_data,
        )

    def _is_user_configured(self, entity_id: str) -> bool:
        """Check if user have setup powercalc sensors for a given entity_id.
        Either with the YAML or GUI method.
        """
        if not self.manually_configured_entities:
            self.manually_configured_entities = self._load_manually_configured_entities()

        return entity_id in self.manually_configured_entities

    def _load_manually_configured_entities(self) -> list[str]:
        """Looks at the YAML and GUI config entries for all the configured entity_id's."""
        entities = []

        # Find entity ids in yaml config (Legacy)
        if SENSOR_DOMAIN in self.ha_config:  # pragma: no cover
            sensor_config = self.ha_config.get(SENSOR_DOMAIN)
            platform_entries = [item for item in sensor_config or {} if isinstance(item, dict) and item.get(CONF_PLATFORM) == DOMAIN]
            for entry in platform_entries:
                entities.extend(self._find_entity_ids_in_yaml_config(entry))

        # Find entity ids in yaml config (New)
        domain_config: ConfigType = self.ha_config.get(DOMAIN, {})
        if CONF_SENSORS in domain_config:
            sensors = domain_config[CONF_SENSORS]
            for sensor_config in sensors:
                entities.extend(self._find_entity_ids_in_yaml_config(sensor_config))

        # Add entities from existing config entries
        entities.extend(
            [str(entry.data.get(CONF_ENTITY_ID)) for entry in self.hass.config_entries.async_entries(DOMAIN) if entry.source == SOURCE_USER],
        )

        return entities

    def _find_entity_ids_in_yaml_config(self, search_dict: dict) -> list[str]:
        """Takes a dict with nested lists and dicts,
        and searches all dicts for a key of the field
        provided.
        """
        found_entity_ids: list[str] = []
        self._extract_entity_ids(search_dict, found_entity_ids)
        return found_entity_ids

    def _extract_entity_ids(self, search_dict: dict, found_entity_ids: list[str]) -> None:
        """Helper function to recursively extract entity IDs."""
        for key, value in search_dict.items():
            if key == CONF_ENTITY_ID:
                found_entity_ids.append(value)
            elif isinstance(value, dict):
                self._extract_entity_ids(value, found_entity_ids)
            elif isinstance(value, list):
                self._process_list_items(value, found_entity_ids)

    def _process_list_items(self, items: list, found_entity_ids: list[str]) -> None:
        """Helper function to process list items."""
        for item in items:
            if isinstance(item, dict):
                self._extract_entity_ids(item, found_entity_ids)

    def _is_already_discovered(self, source_entity: SourceEntity, unique_id: str) -> bool:
        """Prevent duplicate discovery flows."""
        unique_ids_to_check = [unique_id, source_entity.entity_id, source_entity.unique_id]
        if unique_id.startswith("pc_"):
            unique_ids_to_check.append(unique_id[3:])
        unique_ids_to_check.extend([f"pc_{uid}" for uid in unique_ids_to_check])

        return any(unique_id in self.initialized_flows for unique_id in unique_ids_to_check)
