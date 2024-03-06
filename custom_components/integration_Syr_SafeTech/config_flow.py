"""Config flow for SafeTech integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    POLL_INTERVAL,
    TIMEOUT,
    CONF_HTTP_TIMEOUT,
    CONF_POLL_INTERVAL,
    CONF_IP,
)
from .SafeTech import SafeTech

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_IP): str}
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    my_SafeTech = SafeTech(data[CONF_IP])

    if not await my_SafeTech.test_connection():
        _LOGGER.info("Tests for SafeTech: Connection failed")
        raise CannotConnect
    _LOGGER.debug("Tests for SafeTech: Connection successful")

    if not await my_SafeTech.test_authentication():
        _LOGGER.info("Tests for SafeTech: Authentication failed")
        raise InvalidAuth
    _LOGGER.debug("Tests for SafeTech: Authentication successful")

    return {"title": "SafeTech", "ip": data[CONF_IP]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SafeTech."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        await self.async_set_unique_id(user_input[CONF_IP])
        self._abort_if_unique_id_configured()

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(
                title=info["title"] + ":" + info[CONF_IP], data=user_input
            )

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_import(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        _LOGGER.warning(
            "SafeTech ip from yaml File imported to Config Flow. Please remove your config from yaml file. It is not longer needed and yaml support will be removed in future!"
        )
        return await self.async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)

    async def async_step_import(self, import_info: dict[str, Any]) -> FlowResult:
        """Set the config entry up from yaml."""
        return self.async_create_entry(title="", data=import_info)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        timeout = TIMEOUT
        poll_interval = POLL_INTERVAL
        if user_input is not None:
            # _LOGGER.info("Option Flow 2:%s", repr(user_input))
            return self.async_create_entry(title="", data=user_input)

        if CONF_HTTP_TIMEOUT in self.options:
            timeout = self.options[CONF_HTTP_TIMEOUT]
        if CONF_POLL_INTERVAL in self.options:
            poll_interval = self.options[CONF_POLL_INTERVAL]

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HTTP_TIMEOUT,
                        default=timeout,
                    ): vol.All(vol.Coerce(int), vol.Clamp(min=5, max=300)),
                    vol.Required(
                        CONF_POLL_INTERVAL,
                        default=poll_interval,
                    ): vol.All(vol.Coerce(int), vol.Clamp(min=1, max=300)),
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
