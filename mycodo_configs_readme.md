# Mycodo Export Files

This directory contains pre-configured Mycodo export files (`.mycodo` files) that can be imported directly into your Mycodo installation to quickly set up common container farm configurations.

## Available Configurations

### 1. basic_monitoring.mycodo
A simple configuration for basic environmental monitoring:
- DHT22 temperature & humidity sensor
- DS18B20 temperature sensors (up to 3)
- Data logging and dashboard with basic graphs

### 2. complete_farm_control.mycodo
A comprehensive configuration for a complete container farm:
- Temperature & humidity monitoring and control
- CO2 monitoring and ventilation control
- Light cycle automation
- Data logging and complete dashboard
- Alert notifications for out-of-range conditions

### 3. hydroponic_system.mycodo
Specialized configuration for hydroponic systems:
- Temperature monitoring
- pH & EC monitoring
- Nutrient dosing control
- Water level monitoring
- Pump scheduling
- Alert notifications for critical parameters

## How to Import

1. Log in to your Mycodo web interface
2. Navigate to `[Gear Icon] → Export/Import`
3. Under "Import Settings", click "Choose File"
4. Select the appropriate `.mycodo` file from this directory
5. Click "Import"

## Important Notes

- After importing, you will need to adjust GPIO pin assignments to match your hardware setup
- For PID controllers, you'll need to adjust the Output IDs to match your relay setup
- Default setpoints are configured for typical leafy greens; adjust as needed for your crops
- Test all functions in manual mode before enabling automatic control

## Customizing Export Files

If you create a configuration you'd like to share:

1. Set up your Mycodo instance as desired
2. Navigate to `[Gear Icon] → Export/Import`
3. Click "Export Mycodo Settings" and save the `.mycodo` file
4. Consider contributing back to this repository by submitting a pull request
