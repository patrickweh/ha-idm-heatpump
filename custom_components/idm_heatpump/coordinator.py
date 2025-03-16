"""DataUpdateCoordinator for the iDM Heat Pump integration."""
import logging
from datetime import timedelta
import struct
import math

# Updated imports for PyModbus v3
from pymodbus.client import ModbusTcpClient
from pymodbus.constants import Endian

from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import (
    DOMAIN,
    REGISTERS,
    DataType,
    AccessType,
    HVAC_MODE_MAP,
)

_LOGGER = logging.getLogger(__name__)

class IdmDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the iDM heat pump."""

    def __init__(self, hass, host, port, update_interval):
        """Initialize the coordinator."""
        # Updated ModbusTcpClient initialization for PyModbus v3
        self.client = ModbusTcpClient(host=host, port=port)
        self._hass = hass

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    def read_float(self, register_key):
        """Read a 32-bit float value from the specified register key."""
        if register_key not in REGISTERS:
            _LOGGER.error(f"Unknown register key: {register_key}")
            return None

        register_def = REGISTERS[register_key]
        if register_def.data_type != DataType.FLOAT:
            _LOGGER.error(f"Register {register_key} is not a float type")
            return None

        return self._read_float_by_address(register_def.address)

    def _read_float_by_address(self, address):
        """Read a 32-bit float value from the specified Modbus register address."""
        try:
            # Updated for PyModbus v3
            result = self.client.read_input_registers(address=address, count=2)
            if result.isError():
                _LOGGER.error(f"Error reading register {address}: {result}")
                return None

            # Extract the registers
            registers = result.registers
            if not registers or len(registers) < 2:
                _LOGGER.error(f"Not enough registers returned from {address}")
                return None

            _LOGGER.debug(f"Raw registers from {address}: {registers}")

            # Always use swapped registers method as it's confirmed to work with this heat pump
            try:
                # Swapped registers (high word in second register, low word in first register)
                combined = (registers[1] << 16) | registers[0]
                value = struct.unpack('!f', struct.pack('!I', combined))[0]

                # Check if value is NaN or infinity
                if math.isnan(value) or math.isinf(value):
                    _LOGGER.debug(f"Invalid float value from register {address}: {value}")
                    return None

                return value

            except Exception as e:
                _LOGGER.error(f"Error unpacking float from registers: {e}")
                return None

        except Exception as e:
            _LOGGER.error(f"Exception reading register {address}: {e}")
            return None

    def read_uint16(self, register_key):
        """Read a 16-bit unsigned integer from the specified register key."""
        if register_key not in REGISTERS:
            _LOGGER.error(f"Unknown register key: {register_key}")
            return None

        register_def = REGISTERS[register_key]
        if register_def.data_type not in [DataType.WORD, DataType.UCHAR]:
            _LOGGER.error(f"Register {register_key} is not a word or uchar type")
            return None

        return self._read_uint16_by_address(register_def.address)

    def _read_uint16_by_address(self, address):
        """Read a 16-bit unsigned integer from the specified Modbus register address."""
        try:
            # Updated for PyModbus v3
            result = self.client.read_input_registers(address=address, count=1)
            if result.isError():
                _LOGGER.error(f"Error reading register {address}: {result}")
                return None

            # For uint16, we can just use the register value directly
            return result.registers[0]
        except Exception as e:
            _LOGGER.error(f"Exception reading register {address}: {e}")
            return None

    def read_uchar(self, register_key):
        """Read an 8-bit unsigned char from the specified register key."""
        if register_key not in REGISTERS:
            _LOGGER.error(f"Unknown register key: {register_key}")
            return None

        register_def = REGISTERS[register_key]
        if register_def.data_type != DataType.UCHAR:
            _LOGGER.error(f"Register {register_key} is not a uchar type")
            return None

        # Get the 16-bit value
        value = self._read_uint16_by_address(register_def.address)

        # For UCHAR we only care about the lower 8 bits
        if value is not None:
            return value & 0xFF  # Mask to get only the lower 8 bits

        return None

    def write_uint16(self, register_key, value):
        """Write a 16-bit unsigned integer to the specified register key."""
        if register_key not in REGISTERS:
            _LOGGER.error(f"Unknown register key: {register_key}")
            return False

        register_def = REGISTERS[register_key]
        if register_def.data_type not in [DataType.WORD, DataType.UCHAR]:
            _LOGGER.error(f"Register {register_key} is not a word or uchar type")
            return False

        if register_def.access_type != AccessType.RW:
            _LOGGER.error(f"Register {register_key} is not writable")
            return False

        # Check value bounds if defined
        if register_def.min_value is not None and value < register_def.min_value:
            _LOGGER.warning(f"Value {value} below minimum {register_def.min_value} for register {register_key}")
            value = register_def.min_value

        if register_def.max_value is not None and value > register_def.max_value:
            _LOGGER.warning(f"Value {value} above maximum {register_def.max_value} for register {register_key}")
            value = register_def.max_value

        # For UCHAR type, ensure the value fits in 8 bits
        if register_def.data_type == DataType.UCHAR and value > 255:
            _LOGGER.warning(f"Value {value} exceeds maximum for UCHAR (255), truncating")
            value = value & 0xFF  # Ensure value fits in 8 bits

        return self._write_uint16_by_address(register_def.address, value)

    def _write_uint16_by_address(self, address, value):
        """Write a 16-bit unsigned integer to the specified Modbus register address."""
        try:
            # Updated for PyModbus v3
            result = self.client.write_register(address=address, value=value)
            if result.isError():
                _LOGGER.error(f"Error writing to register {address}: {result}")
                return False
            return True
        except Exception as e:
            _LOGGER.error(f"Exception writing to register {address}: {e}")
            return False

    def write_uchar(self, register_key, value):
        """Write an 8-bit unsigned char to the specified register key."""
        if register_key not in REGISTERS:
            _LOGGER.error(f"Unknown register key: {register_key}")
            return False

        register_def = REGISTERS[register_key]
        if register_def.data_type != DataType.UCHAR:
            _LOGGER.error(f"Register {register_key} is not a uchar type")
            return False

        if register_def.access_type != AccessType.RW:
            _LOGGER.error(f"Register {register_key} is not writable")
            return False

        # Check value bounds if defined
        if register_def.min_value is not None and value < register_def.min_value:
            _LOGGER.warning(f"Value {value} below minimum {register_def.min_value} for register {register_key}")
            value = register_def.min_value

        if register_def.max_value is not None and value > register_def.max_value:
            _LOGGER.warning(f"Value {value} above maximum {register_def.max_value} for register {register_key}")
            value = register_def.max_value

        # Ensure value fits in 8 bits
        if value > 255:
            _LOGGER.warning(f"Value {value} exceeds maximum for UCHAR (255), truncating")
            value = value & 0xFF

        # For UCHAR, we still write to a 16-bit register, but only use the lower 8 bits
        return self._write_uint16_by_address(register_def.address, value)

    def write_float(self, register_key, value):
        """Write a 32-bit float value to the specified register key."""
        if register_key not in REGISTERS:
            _LOGGER.error(f"Unknown register key: {register_key}")
            return False

        register_def = REGISTERS[register_key]
        if register_def.data_type != DataType.FLOAT:
            _LOGGER.error(f"Register {register_key} is not a float type")
            return False

        if register_def.access_type != AccessType.RW:
            _LOGGER.error(f"Register {register_key} is not writable")
            return False

        # Check value bounds if defined
        if register_def.min_value is not None and value < register_def.min_value:
            _LOGGER.warning(f"Value {value} below minimum {register_def.min_value} for register {register_key}")
            value = register_def.min_value

        if register_def.max_value is not None and value > register_def.max_value:
            _LOGGER.warning(f"Value {value} above maximum {register_def.max_value} for register {register_key}")
            value = register_def.max_value

        return self._write_float_by_address(register_def.address, value)

    def _write_float_by_address(self, address, value):
        """Write a 32-bit float value to the specified Modbus register address."""
        try:
            # Manual conversion of float to registers
            # Convert float to 32-bit binary representation
            packed = struct.pack('!f', value)
            # Unpack as 32-bit integer
            combined = struct.unpack('!I', packed)[0]
            # Split into two 16-bit values
            registers = [(combined >> 16) & 0xFFFF, combined & 0xFFFF]

            # Write the registers
            result = self.client.write_registers(address=address, values=registers)
            if result.isError():
                _LOGGER.error(f"Error writing to register {address}: {result}")
                return False
            return True
        except Exception as e:
            _LOGGER.error(f"Exception writing to register {address}: {e}")
            return False

    async def _async_update_data(self):
        """Fetch data from the heat pump."""
        # Use executor to run the sync client in a thread
        return await self._hass.async_add_executor_job(self._fetch_data)

    def _fetch_data(self):
        """Fetch data from the heat pump synchronously."""
        try:
            # Connect to the heat pump
            self.client.connect()

            # Initialize data dictionary
            data = {}

            # Read all defined registers
            for key, reg_def in REGISTERS.items():
                if reg_def.data_type == DataType.FLOAT:
                    value = self._read_float_by_address(reg_def.address)
                    # Check if the value is -1, which indicates "not available" for certain types of data
                    # that logically can't be negative (like temperatures above absolute zero, energy values, etc.)
                    if value == -1 and reg_def.min_value is not None and reg_def.min_value >= 0:
                        value = None
                    data[key] = value
                elif reg_def.data_type == DataType.WORD:
                    value = self._read_uint16_by_address(reg_def.address)
                    # Check if the value is 65535 (0xFFFF) or -1, which might indicate "not available" for Word types
                    if value in [65535, -1] and reg_def.min_value is not None and reg_def.min_value >= 0:
                        value = None
                    data[key] = value
                elif reg_def.data_type == DataType.UCHAR:
                    value = self._read_uint16_by_address(reg_def.address) & 0xFF  # Read as WORD and mask to 8 bits
                    # Check for "not available" values
                    if value == 255 and reg_def.min_value is not None and reg_def.min_value >= 0:
                        value = None
                    data[key] = value
                # Add support for other data types as needed

            # With the correct decoding method, we shouldn't have negative energy values anymore
            # But let's keep this as a safety check for energy sensors
            for key in ["energy_heating", "energy_cooling", "energy_dhw", "energy_total", "energy_meter_total"]:
                if key in data and data[key] is not None and data[key] < 0:
                    _LOGGER.warning(f"Unexpected negative value for {key}: {data[key]}")
                    data[key] = 0  # Replace negative values with zero

            # Add string representations for enum-like values that have options defined
            for key, reg_def in REGISTERS.items():
                if reg_def.options and key in data and data[key] is not None:
                    str_key = f"{key}_str"
                    data[str_key] = reg_def.options.get(data[key], "Unknown")

            # Determine current HVAC state based on heat pump mode
            heat_pump_mode = data.get("heat_pump_mode")
            if heat_pump_mode == 0:
                data["hvac_state"] = HVACAction.OFF
            elif heat_pump_mode == 1:
                data["hvac_state"] = HVACAction.HEATING
            elif heat_pump_mode == 2:
                data["hvac_state"] = HVACAction.COOLING
            else:
                data["hvac_state"] = HVACAction.IDLE

            # Determine the current HVAC mode based on system mode
            system_mode = data.get("system_mode")
            if system_mode == 0:  # Standby
                data["hvac_mode"] = HVACMode.OFF
            elif system_mode == 1:  # Automatic
                if heat_pump_mode == 1:  # Heating
                    data["hvac_mode"] = HVACMode.HEAT
                elif heat_pump_mode == 2:  # Cooling
                    data["hvac_mode"] = HVACMode.COOL
                else:
                    data["hvac_mode"] = HVACMode.AUTO
            elif system_mode == 5:  # Heating/Cooling Only
                if heat_pump_mode == 1:  # Heating
                    data["hvac_mode"] = HVACMode.HEAT
                elif heat_pump_mode == 2:  # Cooling
                    data["hvac_mode"] = HVACMode.COOL
                else:
                    data["hvac_mode"] = HVACMode.AUTO
            else:
                data["hvac_mode"] = HVACMode.OFF

            _LOGGER.debug(f"Fetched {len(data)} data points from heat pump")
            return data
        except Exception as e:
            _LOGGER.error(f"Error fetching data: {e}")
            return {}
        finally:
            self.client.close()