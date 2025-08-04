"""DataUpdateCoordinator for dLight."""
from dataclasses import dataclass
import math
from typing import Any

from homeassistant.components.light import ATTR_BRIGHTNESS
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_DEVICE_ID, CONF_FRIENDLY_NAME, CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from . import dlight
from .const import (
    CONF_DISCOVERY,
    DOMAIN,
    LOGGER,
    MAX_TIMEOUT_BACKOFF_COUNT,
    SCAN_INTERVAL,
)


@dataclass
class DLightData:
    """Lamp Discovery Response model."""

    on: bool
    brightness: int
    temperature: int


class DLightDataUpdateCoordinator(DataUpdateCoordinator[DLightData]):
    """Class to manage fetching dLight data."""

    config_entry: ConfigEntry
    host: str
    device_id: str
    discovery: dlight.DLightDiscovery

    _poll_target_skip_count: int
    _poll_skipped: int

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        LOGGER.debug("coordinator.__init__(%s)", entry.data)

        self.config_entry = entry
        self.host = entry.data[CONF_HOST]
        self.device_id = entry.data[CONF_DEVICE_ID]
        self.discovery = entry.data[CONF_DISCOVERY]
        self.name = entry.data[CONF_FRIENDLY_NAME]

        self._poll_target_skip_count = 0
        self._poll_skipped = 0

        super().__init__(
            hass,
            LOGGER,
            name=f"{DOMAIN}_{entry.data[CONF_HOST]}",
            update_interval=SCAN_INTERVAL,
            always_update=False,
        )

        LOGGER.info(
            "Init dLight Coordinator for %s (device_id: %s, host: %s)",
            self.logged_name(),
            self.device_id,
            self.host,
        )

    async def _async_update_data(self) -> DLightData:
        """Fetch data from the dLight device."""
        LOGGER.debug("_async_update_data(%s): %s", self.device_id, self.data)

        if self._poll_skipped < self._poll_target_skip_count:
            self._poll_skipped += 1
            raise UpdateFailed(
                f"Skipping poll due to backoff skip {self._poll_skipped} of {self._poll_target_skip_count} for {self.logged_name()}"
            )
        else:
            self._poll_skipped = 0

        try:
            response = await self.hass.async_add_executor_job(
                lambda: dlight.get_state(self.host, self.device_id)
            )

            LOGGER.debug(
                "Fetched new device state for %s: %s", self.logged_name(), response
            )

            if response["status"] == "SUCCESS":
                # Reset backoff counters
                self._poll_target_skip_count = 0
                self._poll_skipped = 0

                device_state = response["states"]
                data = DLightData(
                    on=device_state["on"],
                    brightness=int(device_state["brightness"]),
                    temperature=device_state["color"]["temperature"],
                )

                LOGGER.debug("Returning _async_update_data() -> %s", data)
                return data
            elif response["status"] == "TIMEOUT":
                self._poll_target_skip_count = min(
                    MAX_TIMEOUT_BACKOFF_COUNT, self._poll_target_skip_count + 1
                )
                raise TimeoutError(
                    f"Update Failed due to Timeout, will skip next {self._poll_target_skip_count} polls {self.logged_name()}\n\t{response}"
                )
            else:
                raise UpdateFailed(f"Update Failed: {self.logged_name()}\n\t{response}")
        except Exception as err:
            raise UpdateFailed(err) from err

    def logged_name(self) -> str:
        """Get the name to log for this device."""
        return f"{self.host} ({self.device_id})"

    async def async_turn_on(self, temperature: int, brightness: int) -> bool:
        """Turn the device on."""
        dlight_config: dict[str, Any] = {"on": True}
        if brightness:
            dlight_config[ATTR_BRIGHTNESS] = brightness
        if temperature:
            # dLight only supports 100k increments in color temp
            temperature = math.floor(temperature / 100) * 100
            dlight_config["color"] = {"temperature": temperature}

        LOGGER.debug("turn_on(send): %s", dlight_config)
        result = await self.hass.async_add_executor_job(
            lambda: dlight.set_values(self.host, self.device_id, dlight_config)
        )
        LOGGER.debug("turn_on(recv): %s", result)

        await self._update_state(result)
        return True

    async def async_turn_off(self) -> bool:
        """Turn the device off."""
        dlight_config: dict[str, Any] = {"on": False}

        LOGGER.debug("turn_off(send): %s", dlight_config)
        result = dlight.set_values(self.host, self.device_id, dlight_config)
        LOGGER.debug("turn_off(recv): %s", result)
        if result["status"] != "SUCCESS":
            LOGGER.warning("Turn Off Failed: %s\n\t%s", self._discovery, result)
            return False

        await self._update_state(result)
        return True

    async def _update_state(self, states: dict[str, Any]) -> None:
        """Update internal state based on response from lamp."""

        on = self.data.on
        brightness = self.data.brightness
        color = self.data.temperature

        if "on" in states:
            on = states["on"]
        if "brightness" in states:
            brightness = int(states["brightness"])
        if "color" in states:
            color = int(states["color"]["temperature"])

        new_data = DLightData(
            on=on,
            brightness=brightness,
            temperature=color,
        )
        LOGGER.debug("update_state(data): %s", new_data)
        self.async_set_updated_data(new_data)
