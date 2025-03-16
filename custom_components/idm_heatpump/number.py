"""Number platform for iDM Heat Pump integration."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.number import (
    NumberEntity,
    NumberDeviceClass,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .const import (
    REGISTERS,
    DataType,
    AccessType,
)

_LOGGER = logging.getLogger(__name__)

# Filter to find registers suitable for number entities
def get_number_registers():
    """Get all register keys suitable for number entities."""
    return [
        key for key, reg in REGISTERS.items()
        if (reg.access_type == AccessType.RW and
            (reg.data_type in [DataType.FLOAT, DataType.WORD, DataType.UCHAR]) and
            reg.min_value is not None and
            reg.max_value is not None and
            # Exclude binary registers (min=0, max=1) as they should be switches
            not (reg.min_value == 0 and reg.max_value == 1))
    ]

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up iDM heat pump number entities from a config entry."""
    # Get coordinator from hass data
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Create number entities for all suitable registers
    numbers = []

    for register_key in get_number_registers():
        register_def = REGISTERS[register_key]

        # Create appropriate number entity based on data type
        if register_def.data_type == DataType.FLOAT:
            numbers.append(
                IdmFloatNumber(
                    coordinator=coordinator,
                    register_key=register_key,
                    entry_id=entry.entry_id,
                )
            )
        elif register_def.data_type == DataType.WORD:
            numbers.append(
                IdmIntNumber(
                    coordinator=coordinator,
                    register_key=register_key,
                    entry_id=entry.entry_id,
                )
            )
        elif register_def.data_type == DataType.UCHAR:
            numbers.append(
                IdmUCharNumber(
                    coordinator=coordinator,
                    register_key=register_key,
                    entry_id=entry.entry_id,
                )
            )

    # Add number entities
    async_add_entities(numbers, True)


class IdmBaseNumber(CoordinatorEntity, NumberEntity):
    """Base number entity for iDM heat pump."""

    def __init__(self, coordinator, register_key, entry_id):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._register_key = register_key
        self._entry_id = entry_id
        self._register_def = REGISTERS[register_key]

        # Set attributes based on register definition
        self._attr_native_min_value = self._register_def.min_value
        self._attr_native_max_value = self._register_def.max_value
        self._attr_native_unit_of_measurement = self._register_def.unit

        # Set mode to slider for most numbers
        self._attr_mode = NumberMode.AUTO

        # Set step based on data type
        if self._register_def.data_type == DataType.FLOAT:
            self._attr_native_step = 0.5  # Default step for float values
        else:
            self._attr_native_step = 1  # Integer step for WORD/UCHAR values

        # Set device class if applicable
        if self._register_def.unit == UnitOfTemperature.CELSIUS:
            self._attr_device_class = NumberDeviceClass.TEMPERATURE

    @property
    def name(self):
        """Return the name of the number entity."""
        return self._register_def.name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._entry_id}_number_{self._register_key}"

    @property
    def icon(self):
        """Return the icon."""
        return self._register_def.icon


class IdmFloatNumber(IdmBaseNumber):
    """Number entity for float values in iDM heat pump."""

    @property
    def native_value(self):
        """Return the current value."""
        return self.coordinator.data.get(self._register_key)

    async def async_set_native_value(self, value):
        """Set new value."""
        success = await self.hass.async_add_executor_job(
            self.coordinator.write_float, self._register_key, value
        )

        if success:
            # Request a data refresh
            await self.coordinator.async_request_refresh()


class IdmIntNumber(IdmBaseNumber):
    """Number entity for integer values in iDM heat pump."""

    @property
    def native_value(self):
        """Return the current value."""
        return self.coordinator.data.get(self._register_key)

    async def async_set_native_value(self, value):
        """Set new value."""
        # Convert to int for WORD registers
        int_value = int(value)

        success = await self.hass.async_add_executor_job(
            self.coordinator.write_uint16, self._register_key, int_value
        )

        if success:
            # Request a data refresh
            await self.coordinator.async_request_refresh()


class IdmUCharNumber(IdmBaseNumber):
    """Number entity for unsigned char values in iDM heat pump."""

    @property
    def native_value(self):
        """Return the current value."""
        return self.coordinator.data.get(self._register_key)

    async def async_set_native_value(self, value):
        """Set new value."""
        # Convert to int for UCHAR registers and ensure it's in range 0-255
        int_value = int(value) & 0xFF

        success = await self.hass.async_add_executor_job(
            self.coordinator.write_uchar, self._register_key, int_value
        )

        if success:
            # Request a data refresh
            await self.coordinator.async_request_refresh()