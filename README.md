# iDM Heat Pump Integration for Home Assistant

This is a Home Assistant custom integration for controlling iDM heat pumps with Navigator 2.0 control system using Modbus TCP.

## Features

- Climate entity for controlling heating/cooling modes
- Temperature sensors for monitoring outside temperature, heating circuit temperature, etc.
- Humidity sensor
- Status sensors for monitoring system mode, heat pump mode, error state
- Demand switches for direct control of heating, cooling, and DHW demands
- Full configuration via the Home Assistant UI

## Requirements

- Home Assistant
- iDM heat pump with Navigator 2.0 control system connected to your network with a static IP address
- Python package `pymodbus` (automatically installed)

## Installation

### HACS (Home Assistant Community Store)

1. Make sure you have [HACS](https://hacs.xyz/) installed
2. Add this repository as a custom repository in HACS
   - Go to HACS → Integration → three dots in the top right → Custom repositories
   - Enter the URL of this repository and select "Integration" as the category
3. Click "Install" on the iDM Heat Pump integration
4. Restart Home Assistant

### Manual Installation

1. Download the latest release
2. Unzip and copy the `idm_heatpump` folder to your `custom_components` folder in your Home Assistant configuration directory
3. Restart Home Assistant

## Configuration

### Through the UI

1. Go to Configuration → Integrations
2. Click the "+ Add Integration" button
3. Search for "iDM Heat Pump"
4. Enter the IP address of your iDM heat pump
5. Configure other options as needed

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| host | string | required | IP address of the iDM heat pump |
| port | integer | 502 | Modbus TCP port |
| scan_interval | integer | 30 | Data update interval in seconds |

## Entities

### Climate Entity

The integration creates a climate entity for controlling the heat pump's heating and cooling modes.

- **Supported features**: Temperature setting
- **HVAC modes**: Off, Heat, Cool, Auto
- **Attributes**: Outside temperature, humidity, system mode, heat pump mode, error state

### Sensors

The integration creates the following sensors:

- **Outside Temperature**: Current outside temperature
- **Heating Circuit Temperature**: Current heating circuit temperature
- **Humidity**: Current humidity level
- **System Mode**: Current system operating mode (Standby, Automatic, Away, DHW Only, Heating/Cooling Only)
- **Heat Pump Mode**: Current heat pump mode (Off, Heating, Cooling, DHW, Defrosting)
- **Error State**: Current error state

### Switches

The integration creates the following switches:

- **Heating Demand**: Toggle heating demand
- **Cooling Demand**: Toggle cooling demand
- **DHW Demand**: Toggle domestic hot water demand

## Services

The integration adds the following services:

### Reset Error

```yaml
service: idm_heatpump.reset_error
target:
  entity_id: climate.idm_heat_pump
```

### Temperature Boost

```yaml
service: idm_heatpump.set_temperature_boost
target:
  entity_id: climate.idm_heat_pump
data:
  temperature: 24
  duration: 60  # minutes
```

## Modbus Registers

This integration uses the following Modbus registers for communicating with the iDM heat pump:

| Register | Description | Type | Access |
|----------|-------------|------|--------|
| 1000 | Outside Temperature | FLOAT | Read |
| 1364 | Heating Circuit A Temperature | FLOAT | Read |
| 1392 | Humidity | FLOAT | Read |
| 1005 | System Mode | UCHAR | Read/Write |
| 1090 | Heat Pump Mode | UCHAR | Read |
| 1099 | Error State | UCHAR | Read |
| 1710 | Heating Demand | BOOL | Read/Write |
| 1711 | Cooling Demand | BOOL | Read/Write |
| 1712 | DHW Demand | BOOL | Read/Write |
| 1694 | Target Temperature Heating | UCHAR | Read/Write |
| 1695 | Target Temperature Cooling | UCHAR | Read/Write |
| 1393 | Heating Circuit Mode | UCHAR | Read/Write |

For a complete list of available registers, refer to the iDM Heat Pump documentation.

## Troubleshooting

- Ensure your iDM heat pump is properly connected to your network and has a static IP address
- Check that the Modbus TCP port (default: 502) is open and accessible
- Verify that the Navigator control system is version 2.0 or newer
- If you encounter connection issues, try increasing the scan interval
- Check the Home Assistant logs for more detailed error messages

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.