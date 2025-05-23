---
layout: default
title: Importing Mycodo Configurations
---

# Importing Mycodo Configurations

This guide explains how to use the pre-configured Mycodo export files to quickly set up your container farm control system with common configurations.

## Available Configurations

We provide several ready-to-use Mycodo configurations in the repository:

### 1. Basic Monitoring Configuration

**File:** `basic_monitoring.mycodo`

A simple setup for monitoring essential environmental parameters:
- DHT22 temperature & humidity sensor
- DS18B20 temperature sensors (up to 3)
- Data logging and dashboard with basic graphs

**Best for:** Getting started with basic environmental monitoring before implementing control systems.

### 2. Complete Farm Control Configuration

**File:** `complete_farm_control.mycodo`

A comprehensive setup for a full container farm operation:
- Temperature & humidity monitoring and control
- CO2 monitoring and ventilation control
- Light cycle automation
- Data logging and complete dashboard
- Alert notifications for out-of-range conditions

**Best for:** Full container farm operations with climate control needs.

### 3. Hydroponic System Configuration

**File:** `hydroponic_system.mycodo`

A specialized configuration for hydroponic growing:
- Temperature monitoring
- pH & EC monitoring and control
- Nutrient dosing automation
- Water level monitoring
- Pump scheduling
- Alert notifications for critical parameters

**Best for:** NFT, DWC, or similar hydroponic systems.

## How to Import a Configuration

1. Ensure Mycodo is installed and running on your Raspberry Pi
2. Download the appropriate `.mycodo` file from the repository
3. Log in to your Mycodo web interface
4. Navigate to `[Gear Icon] → Export/Import`

   ![Mycodo Export/Import Menu](../assets/images/mycodo-export-import-menu.jpg)

5. Under "Import Settings", click "Choose File"
6. Select the `.mycodo` file you downloaded
7. Click "Import"

   ![Mycodo Import Screen](../assets/images/mycodo-import-screen.jpg)

8. After the import completes, you'll need to adjust the configuration to match your hardware setup

## Post-Import Configuration

After importing a configuration, you'll need to make several adjustments:

### 1. Sensor Configuration

For each sensor, you'll need to update:
- GPIO pin assignments to match your wiring
- I2C addresses if different from default
- Sensor-specific parameters (e.g., DS18B20 locations)

Navigate to `Setup → Input` to configure each sensor.

### 2. Output Configuration

For each relay output, you'll need to update:
- GPIO pin assignments to match your relay wiring
- Ensure safety settings match your requirements

Navigate to `Setup → Output` to configure each output.

### 3. PID Controller Configuration

If using PID controllers, you'll need to:
- Link sensors and outputs correctly
- Adjust setpoints for your specific crops
- Fine-tune PID parameters if needed

Navigate to `Data → Function` to edit PID controllers.

### 4. Alert Configuration

Update email addresses and alert thresholds to match your needs.

## Testing Your Configuration

After making adjustments, test each component independently:

1. Verify sensor readings manually
2. Test each output in manual mode
3. Test PID controllers with a small measurement range
4. Test alert conditions with safe thresholds

## Creating Your Own Export Files

Once you've customized your system, consider creating your own export file:

1. Navigate to `[Gear Icon] → Export/Import`
2. Click "Export Mycodo Settings"
3. Save the `.mycodo` file
4. Consider contributing your configuration to the repository

## Troubleshooting Import Issues

If you encounter problems with importing:

- Ensure your Mycodo version is compatible (8.x recommended)
- Try importing a minimal configuration first
- Check for errors in the Mycodo logs (`/var/log/mycodo/mycodo.log`)
- Disable conflicting inputs or functions before importing
