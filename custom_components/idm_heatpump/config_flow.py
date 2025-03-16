"""Config flow for iDM Heat Pump integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pymodbus.client import ModbusTcpClient  # Updated import

from homeassistant import config_entries
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> bool:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)

    # Create client with modern PyModbus syntax
    client = ModbusTcpClient(host=host, port=port)
    try:
        return await hass.async_add_executor_job(client.connect)
    except Exception as exc:
        _LOGGER.error("Error connecting to iDM Heat Pump: %s", exc)
        return False
    finally:
        await hass.async_add_executor_job(client.close)


class IdmHeatPumpConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for iDM Heat Pump."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            can_connect = await validate_input(self.hass, user_input)

            if can_connect:
                return self.async_create_entry(
                    title=user_input.get(CONF_NAME, DEFAULT_NAME),
                    data=user_input,
                )
            else:
                errors["base"] = "cannot_connect"

        # Show configuration form
        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                ): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return IdmHeatPumpOptionsFlow(config_entry)


class IdmHeatPumpOptionsFlow(config_entries.OptionsFlow):
    """iDM Heat Pump config flow options handler."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            ): int,
        }

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(options),
        )