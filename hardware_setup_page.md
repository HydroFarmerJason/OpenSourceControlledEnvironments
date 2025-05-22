---
layout: default
title: Hardware Setup Guide
---

# Hardware Setup Guide

This guide provides instructions for connecting sensors, relays, and other hardware components to your Raspberry Pi for container farm control.

## Core Hardware Components

### Raspberry Pi Setup

1. Mount your Raspberry Pi inside a weatherproof enclosure
2. Ensure proper ventilation to prevent overheating
3. Connect power supply (5V/3A recommended for Raspberry Pi 4/5)
4. Connect Ethernet cable for network connectivity (recommended over WiFi for reliability)

### Power Distribution

Create a power distribution system that includes:

1. Appropriate circuit protection (fuses or circuit breakers)
2. Separated power circuits for:
   - Low voltage components (Raspberry Pi, sensors)
   - High voltage components (pumps, fans, lights) controlled via relays

## Sensor Connection

### Temperature and Humidity Sensors

#### DHT22/AM2302 Digital Sensor

```
┌─────────────┐
│ DHT22/AM2302│
│   ┌─┐       │
│   │ │       │
│   └─┘       │
│    │        │
│ 1  2  3     │
└─┬──┬──┬─────┘
  │  │  │
  │  │  └── Not connected
  │  └──── Data to GPIO pin (e.g., GPIO4)
  └────── VCC to 3.3V
        GND to GND
```

Wiring:
- Connect VCC to 3.3V power on Raspberry Pi
- Connect GND to ground on Raspberry Pi
- Connect DATA to GPIO4 (or another free GPIO pin)
- Add a 10K ohm pull-up resistor between DATA and VCC

#### DS18B20 Temperature Sensor (1-Wire)

```
┌────────────┐
│   DS18B20  │
│    ┌───┐   │
│    │   │   │
│    └───┘   │
│     │      │
│  1  2  3   │
└──┬──┬──┬───┘
   │  │  │
   │  │  └── VDD to 3.3V
   │  └──── DATA to GPIO4 (with 4.7K pull-up resistor)
   └────── GND to GND
```

Wiring:
- Connect VDD to 3.3V power on Raspberry Pi
- Connect GND to ground on Raspberry Pi
- Connect DATA to GPIO4 (configured for 1-Wire)
- Add a 4.7K ohm pull-up resistor between DATA and VDD

### CO2 Sensors

#### MH-Z19 CO2 Sensor (UART)

```
┌─────────────┐
│    MH-Z19   │
│    ┌───┐    │
│    │   │    │
│    └───┘    │
│     │       │
│  1  2  3... │
└──┬──┬──┬────┘
   │  │  │
   │  │  └── Vin to 5V
   │  └──── GND to GND
   └────── TX to RX (GPIO15)
        RX to TX (GPIO14)
```

Wiring:
- Connect Vin to 5V power on Raspberry Pi
- Connect GND to ground on Raspberry Pi
- Connect TX from sensor to RX on Pi (GPIO15)
- Connect RX from sensor to TX on Pi (GPIO14)

### pH and EC Sensors

pH and EC sensors typically require analog inputs, which the Raspberry Pi doesn't have natively. Use an analog-to-digital converter (ADC) such as the ADS1115:

```
┌────────────┐    ┌─────────┐    ┌──────────┐
│  pH Sensor │    │ ADS1115 │    │Raspberry │
│   ┌───┐    │    │  ┌───┐  │    │    Pi    │
│   │   │    │    │  │   │  │    │          │
│   └───┘    │    │  └───┘  │    │          │
│    │       │    │   │     │    │          │
└────┼───────┘    └───┼─────┘    └──────────┘
     │                │
     └────────────────┘
          Analog         I2C
          Connection     Connection
```

Wiring:
1. Connect ADS1115 to Raspberry Pi:
   - VDD to 3.3V
   - GND to GND
   - SCL to SCL (GPIO3)
   - SDA to SDA (GPIO2)

2. Connect pH sensor to ADS1115:
   - pH probe to A0
   - Reference electrode to GND

3. Connect EC sensor to ADS1115:
   - EC probe to A1
   - Reference electrode to GND

## Relay Connection

### Control Relay Modules (for AC devices)

For controlling high voltage equipment (pumps, fans, lighting, etc.), use relay modules with proper isolation:

```
┌────────────┐    ┌─────────┐    ┌──────────┐
│   Device   │    │  Relay  │    │Raspberry │
│  (AC/DC)   │    │ Module  │    │    Pi    │
│            │    │         │    │          │
└─────┬──────┘    └────┬────┘    └──────────┘
      │                │
      └────────────────┘
           Power           Control
           Connection      Connection
```

Wiring:
1. Connect relay module to Raspberry Pi:
   - VCC to 3.3V (ensure relay is 3.3V compatible) or 5V with level shifter
   - GND to GND
   - IN1, IN2, etc. to GPIO pins (e.g., GPIO17, GPIO18)

2. Connect devices to relay outputs:
   - Common (COM) to power source
   - Normally Open (NO) or Normally Closed (NC) to device
   - Ensure proper electrical safety practices for high voltage connections

### 3.3V Logic Level Compatibility

Most Raspberry Pi GPIO pins operate at 3.3V logic level. For relay modules requiring 5V logic:

1. Use a level shifter between GPIO pins and relay inputs
2. Or use optically isolated relay modules compatible with 3.3V logic

## Complete System Wiring

### Example Wiring Diagram

![Wiring Diagram](../assets/images/wiring-diagram.svg)

## Weatherproof Enclosure

For container farm environments with high humidity:

1. Use a NEMA-rated enclosure (NEMA 4X recommended for wet environments)
2. Include cable glands for all wire penetrations
3. Consider adding:
   - Small fan for ventilation
   - Silica gel packets to absorb moisture
   - Thermal insulation if mounted in direct sunlight

## Power Safety

1. Include a master power switch for emergency shutoff
2. Use appropriate fusing for each circuit
3. Consider adding a UPS (Uninterruptible Power Supply) for critical systems

## Testing Your Connections

We've created a sensor testing script that can help verify your hardware connections:

```bash
# Download the script
wget https://raw.githubusercontent.com/your-username/container-farm-control-system/main/scripts/setup_sensors.sh

# Make it executable
chmod +x setup_sensors.sh

# Run the script
sudo ./setup_sensors.sh
```

This script will help detect and test:
- I2C devices (including ADS1115 ADC)
- 1-Wire temperature sensors
- DHT22/AM2302 sensors

## Next Steps

After completing the hardware connections, proceed to [Software Configuration](software-configuration.html) to set up Mycodo to recognize and control your hardware.
