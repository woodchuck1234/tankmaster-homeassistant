# TankMaster for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

A Home Assistant custom integration for TankMaster water tank monitoring devices.

## Features

- **Real-time Monitoring**: Track your water tank levels in real-time
- **Multiple Sensors**: Monitor level percentage, volume, capacity, and temperature
- **Easy Setup**: Simple configuration through Home Assistant UI
- **HACS Compatible**: Install and update easily through HACS

## Sensors

This integration provides the following sensors:

- **Level**: Tank fill level as a percentage (0-100%)
- **Volume**: Current water volume in liters
- **Capacity**: Total tank capacity in liters
- **Temperature**: Water temperature in Celsius

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Click on "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL: `https://github.com/woodchuck1234/tankmaster-homeassistant`
6. Select category: "Integration"
7. Click "Add"
8. Find "TankMaster" in the integration list and click "Download"
9. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/tankmaster` directory to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "+ Add Integration"
3. Search for "TankMaster"
4. Enter your TankMaster device details:
   - **Name**: A friendly name for your tank
   - **Host**: IP address or hostname of your TankMaster device
   - **Port**: Port number (default: 80)
5. Click "Submit"

## Usage

After configuration, the integration will create a device with multiple sensors. You can:

- Add sensor cards to your dashboard to display tank levels
- Create automations based on tank levels (e.g., notify when tank is low)
- View historical data in the sensor history

### Example Dashboard Card

```yaml
type: entities
entities:
  - entity: sensor.tankmaster_level
  - entity: sensor.tankmaster_volume
  - entity: sensor.tankmaster_capacity
  - entity: sensor.tankmaster_temperature
title: Water Tank Status
```

### Example Automation

```yaml
automation:
  - alias: "Low Tank Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.tankmaster_level
        below: 20
    action:
      - service: notify.notify
        data:
          message: "Warning: Water tank level is below 20%"
```

## Development

This integration is currently in development. The data fetching mechanism needs to be implemented based on your specific TankMaster device's API.

To contribute:

1. Fork this repository
2. Make your changes
3. Submit a pull request

## TODO

- [ ] Implement actual TankMaster device communication protocol
- [ ] Add connection validation in config flow
- [ ] Add device discovery support
- [ ] Add additional sensor types if supported by device
- [ ] Add support for multiple tanks

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/woodchuck1234/tankmaster-homeassistant).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial integration and is not affiliated with or endorsed by TankMaster. Use at your own risk.
