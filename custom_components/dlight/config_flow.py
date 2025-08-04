"""Config flow for dlight."""
from dataclasses import asdict
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_DEVICE_ID, CONF_FRIENDLY_NAME, CONF_HOST
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)

from . import dlight
from . import coordinator
from .const import CONF_MANUAL, CONF_DISCOVERED_LIGHTS, CONF_DISCOVERY, DOMAIN, LOGGER


class DLightFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a dLight config flow."""

    VERSION = 1

    host: str
    device_id: str
    device_info: dlight.DLightDiscovery

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""

        existing: dict[
            str : coordinator.DLightDataUpdateCoordinator
        ] = self.hass.data.setdefault(DOMAIN, {})
        existing = [c.device_id for c in existing.values()]
        LOGGER.info("Existing: %s", existing)

        if user_input is None:
            devices = await dlight.discover_devices(self.hass)
            devices = [d for d in devices if d.device_id not in existing]
            LOGGER.info("Discovered: %s", devices)
            return self._async_show_setup_form(devices=devices)
        elif (
            CONF_DISCOVERED_LIGHTS in user_input
            and user_input[CONF_DISCOVERED_LIGHTS] == CONF_MANUAL
        ):
            return self._async_show_setup_form()

        if CONF_DISCOVERED_LIGHTS in user_input:
            device_info = user_input[CONF_DISCOVERED_LIGHTS].split("|")
            self.host = device_info[0]
            self.device_id = device_info[1]
        else:
            self.host = user_input[CONF_HOST]
            self.device_id = user_input[CONF_DEVICE_ID]

        try:
            self.device_info = await self.hass.async_add_executor_job(
                lambda: dlight.get_device_info(self.host, self.device_id)
            )
            LOGGER.info("Discovered dLight: %s", self.device_info)
        except Exception as e:
            LOGGER.error(
                "Error getting device info for %s %s",
                self.host,
                self.device_id,
                exc_info=e,
            )
            return self._async_show_setup_form({"base": "cannot_connect"})

        return self._async_create_entry()

    @callback
    def _async_show_setup_form(
        self,
        errors: dict[str, str] | None = None,
        devices: list[dlight.DLightDiscovery] = None,
    ) -> FlowResult:
        """Show the setup form to the user."""
        if devices:
            options = [
                SelectOptionDict(
                    value=f"{device.addr}|{device.device_id}",
                    label=f"{device.addr} [{device.device_id}]",
                )
                for device in devices
            ]
            options.append(
                SelectOptionDict(
                    value=CONF_MANUAL,
                    label="Manually Configure dLight",
                )
            )
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema(
                    {
                        vol.Required(CONF_DISCOVERED_LIGHTS): SelectSelector(
                            SelectSelectorConfig(
                                options=options,
                                multiple=False,
                            )
                        ),
                    }
                ),
                errors=errors or {},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                    vol.Required(CONF_DEVICE_ID): str,
                }
            ),
            errors=errors or {},
        )

    @callback
    def _async_create_entry(self) -> FlowResult:
        name = "dLight " + self.device_id
        return self.async_create_entry(
            title=name,
            data={
                CONF_HOST: self.host,
                CONF_DEVICE_ID: self.device_id,
                CONF_FRIENDLY_NAME: name,
                CONF_DISCOVERY: asdict(self.device_info),
            },
        )


# async def _async_has_devices(hass: HomeAssistant) -> bool:
#     """Return if there are devices that can be discovered."""
#     devices = await dlight.discover_devices(hass)
#     return len(devices) > 0

# config_entry_flow.register_discovery_flow(DOMAIN, "dlight", _async_has_devices)
