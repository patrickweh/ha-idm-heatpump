"""Switch platform for iDM Heat Pump integration."""
import logging
from typing import Any, List, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .const import (
    REGISTERS,
    AccessType,
    DataType,
)

_LOGGER = logging.getLogger(__name__)

# Filter to find registers suitable for switch entities
def get_switch_registers():
    """Get all register keys suitable for switch entities."""
    return [
        key for key, reg in REGISTERS.items()
        if (reg.access_type == AccessType.RW and
            reg.min_value is not None and
            reg.max_value is not None and
            reg.min_value == 0 and
            reg.max_value == 1)
    ]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up iDM heat pump switch entities from a config entry."""
    # Get coordinator from hass data
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Create switch entities for all binary registers (min=0, max=1)
    switches = []

    for register_key in get_switch_registers():
        switches.append(
            IdmGenericSwitch(
                coordinator=coordinator,
                register_key=register_key,
                entry_id=entry.entry_id,
            )
        )

    # Add switch entities
    async_add_entities(switches, True)


class IdmGenericSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control demand states for iDM heat pump."""

    def __init__(self, coordinator, register_key, entry_id):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._register_key = register_key
        self._entry_id = entry_id
        self._register_def = REGISTERS[register_key]

    @property
    def name(self):
        """Return the name of the switch."""
        return self._register_def.name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._entry_id}_{self._register_key}"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        value = self.coordinator.data.get(self._register_key)
        return bool(value) if value is not None else None

    async def async_turn_on(self, **kwargs):
        """Turn the switch on."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.write_uint16, self._register_key, 1
        )

        if success:
            # Request a data refresh
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs):
        """Turn the switch off."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.write_uint16, self._register_key, 0
        )

        if success:
            # Request a data refresh
            await self.coordinator.async_request_refresh()

    @property
    def icon(self):
        """Return the icon."""
        return self._register_def.icon