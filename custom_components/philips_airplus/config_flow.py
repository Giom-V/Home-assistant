"""Config flow for Philips Air+.

Three steps, each feeding the next:

1. ``user`` — upload the user's own Philips Air+ APK. The gaoda mSecret is
   extracted locally (``apk_extract.py``) and never leaves this instance.
2. ``email`` — enter the account email; triggers an emailed OTP.
3. ``otp`` — enter the code; derives the gaoda ``user_id`` (``oneid_login.py``)
   and validates the full chain (signed ``getToken`` + ``deviceList``) before
   creating the entry.

No password, no APK/constants ever committed anywhere — see README/disclaimer.
"""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components.file_upload import process_uploaded_file
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from . import PhilipsAirplusData, apk_extract, oneid_login
from .const import CONF_EMAIL, CONF_MSECRET, CONF_USER_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Flow-local fields (transient — not persisted to the config entry).
CONF_APK_FILE = "apk_file"
CONF_OTP_CODE = "code"

APK_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_APK_FILE): selector.FileSelector(
            selector.FileSelectorConfig(accept=".apk,.apkm,.xapk")
        ),
    }
)
EMAIL_SCHEMA = vol.Schema({vol.Required(CONF_EMAIL): str})
OTP_SCHEMA = vol.Schema({vol.Required(CONF_OTP_CODE): str})


def _short(uid: str) -> str:
    return uid[:8] + "…" if uid else ""


async def _validate(
    hass: HomeAssistant, user_id: str, msecret: str
) -> tuple[PhilipsAirplusData, list[dict]]:
    """Validate credentials + discover devices. Raises ValueError on failure."""
    data = PhilipsAirplusData(hass, user_id, msecret)
    try:
        devices = await hass.async_add_executor_job(data.get_device_list)
    except Exception as err:  # noqa: BLE001
        raise ValueError(f"auth_failed: {err}") from err
    if not devices:
        raise ValueError("no_devices")
    return data, devices


class PhilipsAirplusConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Philips Air+."""

    VERSION = 2

    def __init__(self) -> None:
        self._msecret: str | None = None
        self._email: str | None = None
        self._vtoken: str | None = None
        self._philips_reauth_id: str | None = None

    # ---- step 1: APK upload -> mSecret ---------------------------------
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """First step: upload the user's own Philips Air+ APK."""
        errors: dict[str, str] = {}
        if user_input is not None:
            file_id = user_input[CONF_APK_FILE]

            def _extract() -> str:
                with process_uploaded_file(self.hass, file_id) as file_path:
                    return apk_extract.extract_msecret(str(file_path))

            try:
                self._msecret = await self.hass.async_add_executor_job(_extract)
            except apk_extract.ApkExtractError as err:
                _LOGGER.debug("APK extraction failed: %s", err)
                errors["base"] = "extract_failed"
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error reading uploaded APK")
                errors["base"] = "extract_failed"
            else:
                return await self.async_step_email()
        return self.async_show_form(step_id="user", data_schema=APK_SCHEMA, errors=errors)

    # ---- step 2: email -> request OTP -----------------------------------
    async def async_step_email(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Second step: email address, triggers the OTP."""
        errors: dict[str, str] = {}
        if user_input is not None:
            email = user_input[CONF_EMAIL].strip()
            try:
                self._vtoken = await self.hass.async_add_executor_job(
                    oneid_login.request_otp, email
                )
            except oneid_login.OneIdError as err:
                _LOGGER.debug("OTP request failed: %s", err)
                errors["base"] = "otp_request_failed"
            else:
                self._email = email
                return await self.async_step_otp()
        return self.async_show_form(step_id="email", data_schema=EMAIL_SCHEMA, errors=errors)

    # ---- step 3: OTP code -> user_id -> validate -> create/update entry
    async def async_step_otp(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Third step: the emailed code. Validates the full chain on success."""
        errors: dict[str, str] = {}
        if user_input is not None:
            code = user_input[CONF_OTP_CODE].strip()
            try:
                user_id = await self.hass.async_add_executor_job(
                    oneid_login.verify_otp, self._email, code, self._vtoken
                )
                await _validate(self.hass, user_id, self._msecret)
            except oneid_login.OneIdError as err:
                _LOGGER.debug("OTP verify failed: %s", err)
                errors["base"] = "otp_verify_failed"
            except ValueError as err:
                msg = str(err)
                if msg.startswith("auth_failed"):
                    errors["base"] = "auth_failed"
                elif msg == "no_devices":
                    errors["base"] = "no_devices"
                else:
                    errors["base"] = "unknown"
            else:
                entry_data = {
                    CONF_USER_ID: user_id,
                    CONF_MSECRET: self._msecret,
                    CONF_EMAIL: self._email,
                }
                if self._philips_reauth_id:
                    entry = self.hass.config_entries.async_get_entry(self._philips_reauth_id)
                    if entry is None:
                        return self.async_abort(reason="reauth_missing")
                    self.hass.config_entries.async_update_entry(entry, data=entry_data)
                    await self.hass.config_entries.async_reload(entry.entry_id)
                    return self.async_abort(reason="reauth_successful")

                await self.async_set_unique_id(user_id)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Philips Air+ ({self._email})",
                    data=entry_data,
                )
        return self.async_show_form(
            step_id="otp",
            data_schema=OTP_SCHEMA,
            errors=errors,
            description_placeholders={"email": self._email or ""},
        )

    # ---- reauth: reuse the stored mSecret when we have one, redo email+OTP
    async def async_step_reauth(
        self, entry_data: dict[str, Any] | None = None
    ) -> FlowResult:
        """Re-authenticate (auth failure, or a pre-0.2.0 entry missing msecret)."""
        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])  # type: ignore[index]
        if entry is None:
            return self.async_abort(reason="reauth_missing")
        self._philips_reauth_id = entry.entry_id
        msecret = entry.data.get(CONF_MSECRET)
        if msecret:
            # APK constants essentially never rotate — skip straight to email+OTP.
            self._msecret = msecret
            return await self.async_step_email()
        # Pre-0.2.0 entry: no msecret was ever stored, need the APK step too.
        return await self.async_step_user()
