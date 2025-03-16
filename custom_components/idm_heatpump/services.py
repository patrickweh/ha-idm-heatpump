"""Services for the iDM Heat Pump integration."""
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_component import EntityComponent

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Service constants
SERVICE_RESET_ERROR = "reset_error"
SERVICE_TEMPERATURE_BOOST = "set_temperature_boost"

# Service schemas
RESET_ERROR_SCHEMA = vol.Schema({})

TEMPERATURE_BOOST_SCHEMA = vol.Schema({
    vol.Required("temperature"): vol.All(vol.Coerce(float), vol.Range(min=15, max=30)),
    vol.Required("duration"): vol.All(vol.Coerce(int), vol.Range(min=30, max=240)),
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up iDM Heat Pump services."""

    async def reset_error(call: ServiceCall) -> None:
        """Reset error state service."""
        # Get coordinator from first entry (could be improved to specify entry_id)
        if not hass.data[DOMAIN]:
            _LOGGER.error("No iDM Heat Pump entries found")
            return

        entry_id = next(iter(hass.data[DOMAIN]))
        coordinator = hass.data[DOMAIN][entry_id]["coordinator"]

        # Write 0 to the error register to reset
        await hass.async_add_executor_job(
            coordinator.write_uint16, "error_state", 0
        )

        # Refresh data
        await coordinator.async_request_refresh()

    async def set_temperature_boost(call: ServiceCall) -> None:
        """Temperature boost service."""
        # Get coordinator from first entry
        if not hass.data[DOMAIN]:
            _LOGGER.error("No iDM Heat Pump entries found")
            return

        entry_id = next(iter(hass.data[DOMAIN]))
        coordinator = hass.data[DOMAIN][entry_id]["coordinator"]

        temperature = call.data["temperature"]
        duration = call.data["duration"]

        # Set the boost value in a register
        # This is an example - adjust according to your heat pump's capabilities
        # In a real implementation, you'd need to find the right register for this
        _LOGGER.info(f"Setting temperature boost to {temperature}°C for {duration} minutes")

        # This service would need to be properly implemented based on
        # specific registers in the heat pump for temporary boost mode

        # Refresh data
        await coordinator.async_request_refresh()

    # Register services
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_ERROR, reset_error, schema=RESET_ERROR_SCHEMA
    )

    hass.services.async_register(
        DOMAIN, SERVICE_TEMPERATURE_BOOST, set_temperature_boost, schema=TEMPERATURE_BOOST_SCHEMA
    )

async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload iDM Heat Pump services."""
    if hass.services.has_service(DOMAIN, SERVICE_RESET_ERROR):
        hass.services.async_remove(DOMAIN, SERVICE_RESET_ERROR)

    if hass.services.has_service(DOMAIN, SERVICE_TEMPERATURE_BOOST):
        hass.services.async_remove(DOMAIN, SERVICE_TEMPERATURE_BOOST)