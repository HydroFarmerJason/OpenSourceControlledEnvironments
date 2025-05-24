# Hardware Compatibility Guide

## Overview

This guide provides detailed information about hardware components tested and verified to work with the Container Farm Control System. All components are organized by category with specific part numbers, suppliers, and configuration details.

## Compatibility Legend

| Symbol | Status | Description |
|--------|--------|-------------|
|  | **Fully Tested** | Verified working with complete setup examples |
|  | **Community Tested** | Reported working by community members |
|  | **Experimental** | Basic functionality confirmed, may need tweaking |
|  | **Not Compatible** | Known incompatibility issues |
|  | **Configuration Required** | Requires specific setup steps |

---

## Raspberry Pi Models

| Model | Status | RAM | Notes | Recommended Use |
|-------|--------|-----|-------|----------------|
| **Raspberry Pi 4B** |  | 4GB+ | **Recommended** - Best performance | All configurations |
| **Raspberry Pi 4B** |  | 2GB | Good for basic monitoring | Basic/Educational |
| **Raspberry Pi 3B+** |  | 1GB | May struggle with complex dashboards | Basic monitoring only |
| **Raspberry Pi Zero 2W** |  | 512MB | Limited to basic sensors | Minimal setups |
| **Raspberry Pi 5** |  | 4GB+ | Early testing, GPIO compatibility pending | Future support |

### Storage Requirements
- **Minimum:** 32GB microSD card (Class 10)
- **Recommended:** 64GB+ SSD via USB 3.0
- **For Research/Commercial:** 128GB+ SSD with backup drive

---

## Temperature Sensors

### DS18B20 Digital Temperature Sensors

| Part Number | Supplier | Status | Price Range | Notes |
|-------------|----------|--------|-------------|-------|
| DS18B20 | Adafruit #381 |  | $9.95 | TO-92 package, most common |
| DS18B20 Waterproof | Adafruit #381 |  | $9.95 | 1m cable, food-safe coating |
| DS18B20 High Temp | Maxim DS18B20+ |  | $4-6 | -55°C to +125°C range |

**Wiring:**
```
DS18B20 → Raspberry Pi
VDD (Red)    → 3.3V (Pin 1)
DQ (Yellow)  → GPIO 4 (Pin 7) + 4.7kΩ pullup resistor
GND (Black)  → Ground (Pin 6)
```

**Configuration:**
- Protocol: 1-Wire
- Default GPIO: 4
- Multiple sensors: Supported (up to 10+ on same pin)
- Resolution: 9-12 bit (0.5°C to 0.0625°C)

### BME280 Environmental Sensor

| Part Number | Supplier | Status | Address | Features |
|-------------|----------|--------|---------|----------|
| BME280 | Adafruit #2652 |  | 0x76/0x77 | Temp, Humidity, Pressure |
| BME280 | SparkFun SEN-13676 |  | 0x76/0x77 | Pre-soldered headers |
| BME680 | Adafruit #3660 |  | 0x76/0x77 | Adds gas sensor |

**Wiring (I2C):**
```
BME280 → Raspberry Pi
VIN → 3.3V (Pin 1)
GND → Ground (Pin 6)
SCL → GPIO 3/SCL (Pin 5)
SDA → GPIO 2/SDA (Pin 3)
```

---

## Humidity Sensors

### DHT22/DHT11 Series

| Model | Status | Accuracy | Range | Price |
|-------|--------|----------|-------|-------|
| **DHT22** |  | ±2% RH | 0-100% RH, -40-80°C | $5-10 |
| DHT11 |  | ±5% RH | 20-90% RH, 0-50°C | $2-5 |
| DHT21 |  | ±3% RH | 0-100% RH, -40-80°C | $8-12 |

**Wiring:**
```
DHT22 → Raspberry Pi
VCC → 3.3V (Pin 1)
DATA → GPIO 17 (Pin 11) + 10kΩ pullup
GND → Ground (Pin 9)
```

### SHT30/SHT31 (I2C)

| Model | Supplier | Status | Address | Accuracy |
|-------|----------|--------|---------|----------|
| SHT31-D | Adafruit #2857 |  | 0x44/0x45 | ±2% RH, ±0.3°C |
| SHT30 | Various |  | 0x44/0x45 | ±3% RH, ±0.3°C |

---

## CO2 Sensors

### MH-Z19 Series

| Model | Status | Range | Interface | Price Range |
|-------|--------|-------|-----------|-------------|
| **MH-Z19B** |  | 0-5000 ppm | UART/PWM | $15-25 |
| MH-Z19C |  | 0-5000 ppm | UART/PWM | $20-30 |
| MH-Z14A |  | 0-5000 ppm | UART/PWM | $25-35 |

**UART Wiring:**
```
MH-Z19B → Raspberry Pi
VIN → 5V (Pin 2)
GND → Ground (Pin 6)
TX → GPIO 15/RX (Pin 10)
RX → GPIO 14/TX (Pin 8)
```

**Configuration:**
- Baud rate: 9600
- Enable UART: Add `enable_uart=1` to `/boot/config.txt`
- Disable Bluetooth: Add `dtoverlay=disable-bt` to avoid conflicts

### SCD30 (I2C)

| Part Number | Supplier | Status | Features |
|-------------|----------|--------|----------|
| SCD30 | Adafruit #4867 |  | CO2, Temperature, Humidity |
| SCD41 | Sensirion |  | Smaller footprint, lower power |

---

## pH and EC Sensors

### Analog pH Sensors

| Sensor | Supplier | Status | Range | Interface |
|--------|----------|--------|-------|-----------|
| **DFRobot pH Kit** | DFRobot SEN0161 |  | 0-14 pH | Analog via ADS1115 |
| Atlas pH Kit | Atlas Scientific |  | 0.001-14.000 pH | I2C/UART |
| Gravity pH Sensor | DFRobot |  | 0-14 pH | Analog |

### EC/TDS Sensors

| Sensor | Supplier | Status | Range | Notes |
|--------|----------|--------|-------|-------|
| **DFRobot EC Kit** | DFRobot DFR0300 |  | 0-20 mS/cm | Includes temperature compensation |
| Atlas EC Kit | Atlas Scientific |  | 0.07-500,000+ μS/cm | High precision |
| TDS Meter Sensor | Various |  | 0-1000 ppm | Basic TDS measurement |

**ADC Requirements:**
Both pH and EC sensors require analog-to-digital conversion:

| ADC | Channels | Resolution | Status | Price |
|-----|----------|------------|--------|-------|
| **ADS1115** | 4 | 16-bit |  | $10-15 |
| ADS1015 | 4 | 12-bit |  | $8-12 |
| MCP3008 | 8 | 10-bit |  | $3-5 |

---

## Relay Control Boards

### Standard Relay Modules

| Channels | Supplier | Status | Voltage | Current Rating |
|----------|----------|--------|---------|----------------|
| **8-Channel** | Various |  | 5V/12V/24V | 10A @ 250VAC |
| 4-Channel | Adafruit #2935 |  | 5V | 10A @ 250VAC |
| 2-Channel | Various |  | 5V | 10A @ 250VAC |
| 16-Channel | Various |  | 5V | Requires I2C expander |

**GPIO Pin Assignments (8-Channel):**
```
Relay 1 → GPIO 5  (Pin 29) - Lights
Relay 2 → GPIO 6  (Pin 31) - Exhaust Fan
Relay 3 → GPIO 13 (Pin 33) - Circulation Fan
Relay 4 → GPIO 19 (Pin 35) - Heater
Relay 5 → GPIO 20 (Pin 38) - pH Up Pump
Relay 6 → GPIO 21 (Pin 40) - pH Down Pump
Relay 7 → GPIO 26 (Pin 37) - Nutrient A Pump
Relay 8 → GPIO 16 (Pin 36) - Nutrient B Pump
```

### Solid State Relays (SSR)

| Type | Rating | Status | Use Case |
|------|--------|--------|----------|
| **Fotek SSR-25DA** | 25A |  | Heating elements |
| Random Turn-On SSR | 10-40A |  | LED grow lights |
| Zero-Cross SSR | 10-40A |  | AC motors, fans |

---

## Cameras and Monitoring

### Official Raspberry Pi Cameras

| Model | Status | Resolution | Features | Price |
|-------|--------|------------|----------|-------|
| **Pi Camera v2** |  | 8MP | 1080p video, excellent software support | $25 |
| Pi Camera v3 |  | 12MP | 4K video, autofocus | $35 |
| Pi HQ Camera |  | 12MP | C/CS mount lenses, professional quality | $50 |
| Pi Camera NoIR |  | 8MP | Infrared capability for night monitoring | $25 |

### USB Cameras

| Type | Status | Resolution | Notes |
|------|--------|------------|-------|
| Logitech C920 |  | 1080p | Excellent compatibility |
| Logitech C270 |  | 720p | Budget option |
| ELP USB Camera |  | Various | Wide angle options available |

---

## Power and Electrical

### Power Supplies

| Rating | Type | Status | Recommended For |
|--------|------|--------|----------------|
| **5V 3A** | Official Pi PSU |  | Pi 4 + basic sensors |
| 5V 5A | Switched PSU |  | Pi + relay board + sensors |
| 12V 2A + 5V 3A | Dual rail |  | Systems with 12V pumps/fans |
| 24V 1A + 5V 3A | Dual rail |  | Professional solenoid valves |

### Level Shifters & Buffers

| Part | Purpose | Status | Notes |
|------|---------|--------|-------|
| **74AHCT125** | 3.3V to 5V logic |  | For 5V relay boards |
| TXS0108E | Bidirectional |  | I2C level shifting |
| BSS138 | Simple MOSFET |  | Single signal conversion |

---

## Pumps and Actuators

### Water Pumps

| Type | Flow Rate | Voltage | Status | Use Case |
|------|-----------|---------|--------|----------|
| **Peristaltic Pump** | 0.1-2 L/min | 12V |  | Precise nutrient dosing |
| Submersible Pump | 2-10 L/min | 12V/24V |  | Water circulation |
| Diaphragm Pump | 1-5 L/min | 12V |  | Self-priming applications |

### Solenoid Valves

| Size | Pressure | Voltage | Status | Application |
|------|----------|---------|--------|-------------|
| **1/4" NPT** | 0-120 PSI | 12V/24V |  | Irrigation control |
| 1/2" NPT | 0-150 PSI | 24V |  | Main water lines |
| 3/8" Barb | 0-100 PSI | 12V |  | Hydroponic systems |

---

## Lighting Control

### LED Drivers

| Type | Rating | Status | Dimming | Notes |
|------|--------|--------|---------|-------|
| **Mean Well LPV-60-12** | 60W 12V |  | PWM | Reliable, cost-effective |
| Mean Well HLG-80H-24A | 80W 24V |  | 0-10V/PWM | Constant current |
| DIY Buck Converter | Variable |  | PWM | Budget option |

### Light Sensors

| Sensor | Range | Interface | Status | Use Case |
|--------|-------|-----------|--------|----------|
| **TSL2591** | 188 μLux - 88k Lux | I2C |  | Full spectrum, high dynamic range |
| BH1750 | 1-65535 Lux | I2C |  | Simple light measurement |
| LDR + ADC | Variable | Analog |  | Basic light detection |

---

## Networking and Communication

### Wireless Modules

| Module | Protocol | Status | Range | Use Case |
|--------|----------|--------|-------|----------|
| **Built-in WiFi** | 802.11n |  | 50m | Standard connectivity |
| ESP32 | WiFi/Bluetooth |  | 100m | Remote sensor nodes |
| LoRa Module | 915MHz |  | 1-10km | Long-range communication |

### Ethernet Options

| Type | Speed | Status | Notes |
|------|-------|--------|-------|
| **Built-in Ethernet** | 1Gbps |  | Pi 4 only |
| USB Ethernet | 100Mbps-1Gbps |  | For Pi models without ethernet |

---

## Configuration Examples by Use Case

### Basic Monitoring Setup ($50-100)
```
- Raspberry Pi 4B (2GB) - $35
- DS18B20 Temperature Sensor - $10
- DHT22 Humidity Sensor - $10
- 2-Channel Relay Board - $8
- Power Supply - $15
- microSD Card (32GB) - $10
```

### Complete Hydroponic System ($200-400)
```
- Raspberry Pi 4B (4GB) - $55
- BME280 Environmental Sensor - $20
- MH-Z19B CO2 Sensor - $20
- DFRobot pH Kit - $45
- DFRobot EC Kit - $40
- ADS1115 ADC - $15
- 8-Channel Relay Board - $15
- Pi Camera v2 - $25
- Peristaltic Pumps (4x) - $80
- Power Supplies - $30
- Enclosure & Wiring - $50
```

### Educational Classroom Setup ($150-250)
```
- Raspberry Pi 4B (4GB) - $55
- BME280 or SHT31 - $20
- DS18B20 Sensors (3x) - $30
- 4-Channel Relay Board - $12
- Pi Camera v2 - $25
- Basic grow lights - $40
- Simple pumps (2x) - $30
- Educational enclosure - $40
```

---

## Troubleshooting Common Issues

### I2C Problems
**Symptom:** Device not detected
```bash
# Check if I2C is enabled
sudo raspi-config
# Enable I2C under Interface Options

# Scan for devices
sudo i2cdetect -y 1
```

### GPIO Permission Issues
**Symptom:** Permission denied accessing GPIO
```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER
# Logout and login again
```

### Sensor Reading Errors
**Symptom:** Inconsistent readings
- Check power supply stability (use multimeter)
- Verify wiring connections
- Add decoupling capacitors for sensitive sensors
- Ensure proper grounding

### Relay Not Switching
**Symptom:** Relay LED lights but no switching
- Check relay coil voltage (should match GPIO output)
- Use level shifter for 5V relays
- Verify relay current rating vs GPIO capability
- Check for proper common ground

---

## Supplier Recommendations

### Primary Suppliers (Global)
- **Adafruit** - Excellent documentation and support
- **SparkFun** - Good tutorials and breakout boards
- **Digi-Key** - Professional components, fast shipping
- **Mouser** - Wide selection, technical datasheets

### Budget Options
- **AliExpress** - Bulk sensors, longer shipping
- **Amazon** - Quick delivery, variable quality
- **eBay** - Surplus and vintage components

### Specialized Hydroponic Suppliers
- **Atlas Scientific** - High-precision pH/EC sensors
- **DFRobot** - Affordable sensor kits
- **Gravity Series** - Plug-and-play sensor ecosystem

---

## Testing and Validation

### Hardware Test Checklist
- [ ] I2C devices detected (`sudo i2cdetect -y 1`)
- [ ] GPIO pins respond (`gpio readall`)
- [ ] 1-Wire sensors enumerated (`ls /sys/bus/w1/devices/`)
- [ ] UART communication working
- [ ] Camera detection (`vcgencmd get_camera`)
- [ ] Relay switching verified
- [ ] Sensor readings stable over 24 hours

### Performance Benchmarks
| Configuration | CPU Usage | RAM Usage | Storage/Day |
|---------------|-----------|-----------|-------------|
| Basic (3 sensors) | 5-15% | 200MB | 10MB |
| Standard (8 sensors) | 15-25% | 400MB | 50MB |
| Complete (15+ sensors) | 25-40% | 800MB | 200MB |

---

## Future Hardware Support

### Planned Additions
- Support for newer Raspberry Pi models
- Additional CO2 sensor options
- Wireless soil moisture sensors
- Advanced spectral light sensors
- Integration with commercial greenhouse controllers

### Community Requests
- Solar panel integration
- Battery backup systems
- Weather station compatibility
- Multi-zone control systems

---

## Contributing Hardware Information

### How to Submit New Hardware
1. Test hardware with setup script
2. Document wiring and configuration
3. Provide photos of working setup
4. Submit pull request with updates to this document
5. Include pricing and supplier information

### Required Testing
- [ ] Basic functionality verification
- [ ] 72-hour stability test
- [ ] Integration with existing sensors
- [ ] Documentation of any special configuration
- [ ] Photos of physical setup

---

*Last updated: {{ current_date }}*  
*Community contributions welcome via GitHub Issues and Pull Requests*