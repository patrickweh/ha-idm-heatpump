"""Constants for the iDM Heat Pump integration."""
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Dict, Any, List, Union

from homeassistant.components.climate import HVACAction, HVACMode
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfEnergy,
    UnitOfPower,
    PERCENTAGE,
    Platform,
)

DOMAIN = "idm_heatpump"

# Default values
DEFAULT_NAME = "iDM Heat Pump"
DEFAULT_PORT = 502
DEFAULT_SCAN_INTERVAL = 30

# Platform definitions - now including NUMBER platform
PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]

# Access types
class AccessType(Enum):
    """Register access type."""
    RO = auto()  # Read Only
    RW = auto()  # Read/Write

# Data types
class DataType(Enum):
    """Register data type."""
    UCHAR = auto()   # Unsigned char (8-bit)
    WORD = auto()    # Word (16-bit unsigned integer)
    FLOAT = auto()   # 32-bit float
    INT = auto()     # 16-bit signed integer

@dataclass
class RegisterDefinition:
    """Definition of a Modbus register."""
    address: int
    data_type: DataType
    access_type: AccessType
    name: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    unit: Optional[str] = None
    device_class: Optional[str] = None
    state_class: Optional[str] = None
    icon: Optional[str] = None
    entity_category: Optional[str] = None
    description: Optional[str] = None
    options: Optional[Dict[int, str]] = None

# Register definitions
REGISTERS = {
    # Basic system values
    "outside_temp": RegisterDefinition(
        address=1000,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Outside Temperature",
        min_value=-50.0,
        max_value=50.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "outside_temp_averaged": RegisterDefinition(
        address=1002,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Outside Temperature (Averaged)",
        min_value=-50.0,
        max_value=50.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "internal_message": RegisterDefinition(
        address=1004,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Internal Message",
    ),
    "system_mode": RegisterDefinition(
        address=1005,
        data_type=DataType.WORD,
        access_type=AccessType.RW,
        name="System Mode",
        min_value=0,
        max_value=5,
        options={
            0: "Standby",
            1: "Automatic",
            2: "Away",
            4: "DHW Only",
            5: "Heating/Cooling Only",
        },
    ),
    "smart_grid_status": RegisterDefinition(
        address=1006,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Smart Grid Status",
    ),

    # Temperature registers
    "buffer_temp": RegisterDefinition(
        address=1008,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Buffer Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "cooling_buffer_temp": RegisterDefinition(
        address=1010,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Cooling Buffer Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "dhw_temp_bottom": RegisterDefinition(
        address=1012,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="DHW Temperature Bottom",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "dhw_temp_top": RegisterDefinition(
        address=1014,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="DHW Temperature Top",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "dhw_outlet_temp": RegisterDefinition(
        address=1030,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="DHW Outlet Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "dhw_target_temp": RegisterDefinition(
        address=1032,
        data_type=DataType.UCHAR,  # Changed to UCHAR as per your example
        access_type=AccessType.RW,
        name="DHW Target Temperature",
        min_value=35.0,
        max_value=95.0,  # Updated range as per your example
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer",
    ),
    "dhw_on_temp": RegisterDefinition(
        address=1033,
        data_type=DataType.UCHAR,  # Changed to UCHAR
        access_type=AccessType.RW,
        name="DHW On Temperature",
        min_value=35.0,
        max_value=95.0,  # Updated range to match
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-plus",
    ),
    "dhw_off_temp": RegisterDefinition(
        address=1034,
        data_type=DataType.UCHAR,  # Changed to UCHAR
        access_type=AccessType.RW,
        name="DHW Off Temperature",
        min_value=35.0,
        max_value=95.0,  # Updated range to match
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        icon="mdi:thermometer-minus",
    ),
    "heat_pump_flow_temp": RegisterDefinition(
        address=1050,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heat Pump Flow Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "heat_pump_return_temp": RegisterDefinition(
        address=1052,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heat Pump Return Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "hgl_flow_temp": RegisterDefinition(
        address=1054,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="HGL Flow Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "source_inlet_temp": RegisterDefinition(
        address=1056,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Source Inlet Temperature",
        min_value=-20.0,
        max_value=50.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "source_outlet_temp": RegisterDefinition(
        address=1058,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Source Outlet Temperature",
        min_value=-20.0,
        max_value=50.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "air_intake_temp": RegisterDefinition(
        address=1060,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Air Intake Temperature",
        min_value=-50.0,
        max_value=50.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # Operational state registers
    "heat_pump_mode": RegisterDefinition(
        address=1090,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Heat Pump Mode",
        options={
            0: "Off",
            1: "Heating",
            2: "Cooling",
            4: "DHW",
            8: "Defrosting",
        },
    ),
    "heating_demand": RegisterDefinition(
        address=1091,
        data_type=DataType.WORD,
        access_type=AccessType.RW,
        name="Heating Demand",
        min_value=0,
        max_value=1,
    ),
    "cooling_demand": RegisterDefinition(
        address=1092,
        data_type=DataType.WORD,
        access_type=AccessType.RW,
        name="Cooling Demand",
        min_value=0,
        max_value=1,
    ),
    "dhw_demand": RegisterDefinition(
        address=1093,
        data_type=DataType.WORD,
        access_type=AccessType.RW,
        name="DHW Demand",
        min_value=0,
        max_value=1,
    ),
    "evu_contact": RegisterDefinition(
        address=1098,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="EVU Contact",
        min_value=0,
        max_value=1,
    ),
    "error_state": RegisterDefinition(
        address=1099,
        data_type=DataType.WORD,
        access_type=AccessType.RW,
        name="Error State",
    ),

    # Component status registers
    "compressor1_status": RegisterDefinition(
        address=1100,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Compressor 1 Status",
        min_value=0,
        max_value=1,
    ),
    "compressor2_status": RegisterDefinition(
        address=1101,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Compressor 2 Status",
        min_value=0,
        max_value=1,
    ),
    "loading_pump_status": RegisterDefinition(
        address=1104,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Loading Pump Status",
        min_value=0,
        max_value=1,
    ),
    "source_pump_status": RegisterDefinition(
        address=1105,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Source Pump Status",
        min_value=0,
        max_value=1,
    ),
    "groundwater_pump_status": RegisterDefinition(
        address=1106,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Groundwater Pump Status",
        min_value=0,
        max_value=1,
    ),

    # Valve status registers
    "valve_circuit_heat_cool": RegisterDefinition(
        address=1110,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Valve Circuit Heat/Cool",
        min_value=0,
        max_value=1,
    ),
    "valve_buffer_heat_cool": RegisterDefinition(
        address=1111,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Valve Buffer Heat/Cool",
        min_value=0,
        max_value=1,
    ),
    "valve_heating_dhw": RegisterDefinition(
        address=1112,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Valve Heating/DHW",
        min_value=0,
        max_value=1,
    ),

    # Circuit temperature registers
    "heating_circuit_a_temp": RegisterDefinition(
        address=1350,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heating Circuit A Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "heating_circuit_b_temp": RegisterDefinition(
        address=1352,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heating Circuit B Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "heating_circuit_a_room_temp": RegisterDefinition(
        address=1364,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heating Circuit A Room Temperature",
        min_value=0.0,
        max_value=40.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "heating_circuit_b_room_temp": RegisterDefinition(
        address=1366,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heating Circuit B Room Temperature",
        min_value=0.0,
        max_value=40.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "heating_circuit_a_target_temp": RegisterDefinition(
        address=1378,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heating Circuit A Target Temperature",
        min_value=0.0,
        max_value=40.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "heating_circuit_b_target_temp": RegisterDefinition(
        address=1380,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heating Circuit B Target Temperature",
        min_value=0.0,
        max_value=40.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # Humidity and mode registers
    "humidity": RegisterDefinition(
        address=1392,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Humidity",
        min_value=0.0,
        max_value=100.0,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "heating_circuit_mode": RegisterDefinition(
        address=1393,
        data_type=DataType.WORD,
        access_type=AccessType.RW,
        name="Heating Circuit Mode",
        options={
            0: "Off",
            1: "Schedule",
            2: "Normal",
            3: "Eco",
            4: "Manual Heating",
            5: "Manual Cooling",
        },
    ),
    "heating_circuit_active_mode": RegisterDefinition(
        address=1498,
        data_type=DataType.WORD,
        access_type=AccessType.RO,
        name="Heating Circuit Active Mode",
    ),

    # External temperature registers for room/heating circuits
    "external_room_temp_a": RegisterDefinition(
        address=1650,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="External Room Temperature A",
        min_value=0.0,
        max_value=40.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "external_room_temp_b": RegisterDefinition(
        address=1652,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="External Room Temperature B",
        min_value=0.0,
        max_value=40.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "external_outside_temp": RegisterDefinition(
        address=1690,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="External Outside Temperature",
        min_value=-50.0,
        max_value=50.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "external_humidity": RegisterDefinition(
        address=1692,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="External Humidity",
        min_value=0.0,
        max_value=100.0,
        unit=PERCENTAGE,
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # Demand registers
    "target_temp_heating": RegisterDefinition(
        address=1694,
        data_type=DataType.FLOAT,
        access_type=AccessType.RW,
        name="Target Temperature Heating",
        min_value=15.0,
        max_value=30.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "target_temp_cooling": RegisterDefinition(
        address=1695,
        data_type=DataType.WORD,
        access_type=AccessType.RW,
        name="Target Temperature Cooling",
        min_value=15,
        max_value=30,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # Energy measurement registers
    "energy_heating": RegisterDefinition(
        address=1748,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Energy Heating",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "energy_total": RegisterDefinition(
        address=1750,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Energy Total",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "energy_cooling": RegisterDefinition(
        address=1752,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Energy Cooling",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "energy_dhw": RegisterDefinition(
        address=1754,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Energy DHW",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),

    "defrosting_energy": RegisterDefinition(
        address=1756,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Defrosting Energy",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "passive_cooling_energy": RegisterDefinition(
        address=1758,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Passive Cooling Energy",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "solar_energy": RegisterDefinition(
        address=1760,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Solar Energy",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "electric_heating_energy": RegisterDefinition(
        address=1762,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Electric Heating Element Energy",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "current_power": RegisterDefinition(
        address=1790,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heat Pump Current Power",
        min_value=0.0,
        max_value=20.0,
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "solar_current_power": RegisterDefinition(
        address=1792,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Solar Current Power",
        min_value=0.0,
        max_value=20.0,
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "solar_collector_temp": RegisterDefinition(
        address=1850,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Solar Collector Temperature",
        min_value=-20.0,
        max_value=150.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "solar_collector_return_temp": RegisterDefinition(
        address=1852,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Solar Collector Return Temperature",
        min_value=-20.0,
        max_value=150.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "solar_loading_temp": RegisterDefinition(
        address=1854,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Solar Loading Temperature",
        min_value=-20.0,
        max_value=150.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "glt_heat_storage_temp": RegisterDefinition(
        address=1716,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="GLT Heat Storage Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "glt_cold_storage_temp": RegisterDefinition(
        address=1718,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="GLT Cold Storage Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "glt_dhw_bottom_temp": RegisterDefinition(
        address=1720,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="GLT DHW Bottom Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "glt_dhw_top_temp": RegisterDefinition(
        address=1722,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="GLT DHW Top Temperature",
        min_value=0.0,
        max_value=100.0,
        unit=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),

    # PV system registers
    "pv_surplus": RegisterDefinition(
        address=74,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="PV Surplus",
        min_value=0.0,
        max_value=20.0,
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "e_heizstab_power": RegisterDefinition(
        address=76,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="E-Heizstab Power",
        min_value=0.0,
        max_value=20.0,
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "pv_production": RegisterDefinition(
        address=78,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="PV Production",
        min_value=0.0,
        max_value=20.0,
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "heat_pump_power_consumption": RegisterDefinition(
        address=4122,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Heat Pump Power Consumption",
        min_value=0.0,
        max_value=20.0,
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "thermal_output": RegisterDefinition(
        address=4126,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Thermal Output",
        min_value=0.0,
        max_value=25.0,
        unit=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "energy_meter_total": RegisterDefinition(
        address=4128,
        data_type=DataType.FLOAT,
        access_type=AccessType.RO,
        name="Energy Meter Total",
        min_value=0.0,
        max_value=1000000.0,
        unit=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
}

# Helper function to get a register definition by address
def get_register_by_address(address: int) -> Optional[str]:
    """Get register key by address."""
    for key, reg in REGISTERS.items():
        if reg.address == address:
            return key
    return None

# Map Home Assistant HVAC modes to iDM system modes
HVAC_MODE_MAP = {
    HVACMode.OFF: 0,  # Standby
    HVACMode.HEAT: 1, # Automatic (with heating)
    HVACMode.COOL: 2, # Automatic (with cooling)
    HVACMode.AUTO: 1, # Automatic
}

# Filter registers by device class for automatic entity creation
def get_registers_by_device_class(device_class: str) -> List[str]:
    """Get all register keys with a specific device class."""
    return [key for key, reg in REGISTERS.items() if reg.device_class == device_class]

# Define which register keys to use for switches (those with RW access that are boolean)
SWITCH_REGISTERS = [
    key for key, reg in REGISTERS.items()
    if (reg.access_type == AccessType.RW and
        reg.data_type == DataType.WORD and
        reg.min_value is not None and
        reg.max_value is not None and
        reg.min_value == 0 and
        reg.max_value == 1)
]