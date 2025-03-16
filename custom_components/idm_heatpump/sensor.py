"""Sensor platform for iDM Heat Pump integration."""
import logging
import math
from typing import Any, Dict, List, Optional

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .const import (
    REGISTERS,
    DataType,
    AccessType,
    get_registers_by_device_class,
    SensorDeviceClass,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up iDM heat pump sensor entities from a config entry."""
    # Get coordinator from hass data
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # Create sensor entities for all registers with sensor device classes
    sensors = []

    # Add all sensor entities dynamically based on register definitions
    for key, reg_def in REGISTERS.items():
        # Skip registers that have both device_class and are writable (RW)
        # since these will be exposed as number entities
        if reg_def.device_class is not None and reg_def.access_type == AccessType.RW:
            if reg_def.min_value is not None and reg_def.max_value is not None:
                # Skip this register as it will be exposed as a number entity
                continue

        # Add regular sensors that are read-only or don't have min/max values defined
        if reg_def.device_class is not None:
            sensors.append(
                IdmGenericSensor(
                    coordinator=coordinator,
                    register_key=key,
                    entry_id=entry.entry_id,
                )
            )

    # Add status sensors for system mode, heat pump mode, error state, etc.
    # These are registers with options defined but no device class
    for key, reg_def in REGISTERS.items():
        if reg_def.options and reg_def.device_class is None:
            sensors.append(
                IdmStatusSensor(
                    coordinator=coordinator,
                    register_key=key,
                    entry_id=entry.entry_id,
                )
            )

    # Add HVAC state and mode sensors
    sensors.append(
        IdmHvacStateSensor(
            coordinator=coordinator,
            entry_id=entry.entry_id,
        )
    )

    # Add sensor entities
    async_add_entities(sensors, True)


class IdmGenericSensor(CoordinatorEntity, SensorEntity):
    """Generic sensor for iDM heat pump."""

    def __init__(self, coordinator, register_key, entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._register_key = register_key
        self._entry_id = entry_id
        self._register_def = REGISTERS[register_key]

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._register_def.name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._entry_id}_{self._register_key}"

    @property
    def device_class(self):
        """Return the device class."""
        return self._register_def.device_class

    @property
    def state_class(self):
        """Return the state class."""
        return self._register_def.state_class

    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self.coordinator.data.get(self._register_key)

        # Check if value is None, NaN, or special value -1 for registers that can't logically be negative
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None

        # Special case: value is -1 and should be treated as "not available"
        # Only applies to registers that have a minimum value >= 0 (logically can't be negative)
        if value == -1 and self._register_def.min_value is not None and self._register_def.min_value >= 0:
            return None

        # For TOTAL_INCREASING state class, ensure non-negative values
        if (self._register_def.state_class == SensorStateClass.TOTAL_INCREASING and
                isinstance(value, (int, float)) and value < 0):
            if abs(value) < 0.1:  # Small enough to be a rounding error
                return 0
            else:
                # For larger negative values, return None to avoid tracking errors
                return None

        # Round float values to 2 decimal places
        if isinstance(value, float):
            return round(value, 2)

        return value

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._register_def.unit

    @property
    def icon(self):
        """Return the icon."""
        return self._register_def.icon


class IdmStatusSensor(IdmGenericSensor):
    """Status sensor for iDM heat pump with string value display."""

    @property
    def native_value(self):
        """Return the state of the sensor as a string representation."""
        value = self.coordinator.data.get(self._register_key)

        if value is None:
            return None

        # Use the string representation if available
        str_key = f"{self._register_key}_str"
        if str_key in self.coordinator.data:
            return self.coordinator.data[str_key]

        # Fall back to options lookup
        if self._register_def.options:
            return self._register_def.options.get(value, f"Unknown ({value})")

        return value


class IdmHvacStateSensor(CoordinatorEntity, SensorEntity):
    """HVAC state sensor for iDM heat pump."""

    def __init__(self, coordinator, entry_id):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id

    @property
    def name(self):
        """Return the name of the sensor."""
        return "iDM HVAC State"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self._entry_id}_hvac_state"

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get("hvac_state")