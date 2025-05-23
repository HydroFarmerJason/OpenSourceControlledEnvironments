# Freight Farm to Container Farm Control System Conversion Guide

## Overview

This guide details how to convert an existing freight farm or shipping container growing system to use the open-source Container Farm Control System. This conversion maintains existing infrastructure while adding intelligent, customizable control.

## ⚠️ Safety First

**CRITICAL SAFETY REQUIREMENTS:**
- **Hire a licensed electrician** for all high-voltage work (120V/240V)
- **Install emergency stops** at both container ends
- **Maintain all existing safety systems** (GFCI, grounding, disconnects)
- **Test everything** before connecting live power
- **Use lockout/tagout procedures** during installation

## Pre-Conversion Assessment

### 1. Existing System Inventory

**Document Current Setup:**
- [ ] Electrical panel configuration (120V/240V distribution)
- [ ] Lighting systems (LED arrays, ballasts, controls)
- [ ] HVAC equipment (fans, heaters, air conditioning)
- [ ] Water/irrigation systems (pumps, valves, filters)
- [ ] Existing sensors (if any)
- [ ] Control systems to be replaced
- [ ] Network infrastructure

**Power Analysis:**
```
Typical Freight Farm Power Consumption:
- LED Lighting: 8-12kW (multiple arrays)
- HVAC System: 2-4kW (fans, climate control)
- Water Systems: 0.5-1kW (pumps, circulation)
- Total: 10-17kW continuous
```

### 2. Infrastructure Requirements

**Electrical Capacity:**
- Verify main panel capacity (typically 200A service)
- Ensure adequate circuit breakers for new control equipment
- Check grounding system integrity
- Confirm GFCI protection on all 120V circuits

**Environmental Considerations:**
- Container insulation condition
- Ventilation adequacy
- Water drainage systems
- Structural mounting points for new equipment

## Hardware Requirements

### Control System Components

| Component | Quantity | Purpose | Estimated Cost |
|-----------|----------|---------|----------------|
| Raspberry Pi 4B (4GB) | 1 | Main controller | $55 |
| Industrial microSD (32GB) | 1 | OS and data storage | $25 |
| 8-Channel Relay Board | 1-2 | Equipment control | $15-30 |
| Dual Power Supply (5V/12V) | 1 | Control system power | $45 |
| Contactors (30A, 120V coil) | 4-6 | High current switching | $120-180 |
| Environmental Sensors | 1 set | Climate monitoring | $100 |
| pH/EC Monitoring Kit | 1 | Nutrient monitoring | $150 |
| Industrial Enclosure | 1 | Control panel housing | $80 |

**Total Control System Cost: $590-665**

### Sensor Package

**Environmental Monitoring:**
- BME280: Temperature, humidity, pressure (I2C)
- MH-Z19B: CO2 monitoring (UART)
- DS18B20: Multiple temperature zones (1-Wire)
- TSL2591: Light intensity monitoring (I2C)

**Water/Nutrient Monitoring:**
- pH probe with ADS1115 ADC
- EC/TDS probe with temperature compensation
- Water level sensors for reservoirs
- Flow rate sensors for irrigation monitoring

**Zone-Specific Sensors:**
```
Recommended Sensor Placement:
- Intake air: Temperature, humidity, CO2
- Growing zone center: Temperature, humidity, light
- Exhaust air: Temperature, humidity
- Water reservoir: Temperature, pH, EC
- Nutrient tanks: Level sensors
```

## Conversion Process

### Phase 1: Planning and Preparation

**1. System Shutdown and Safety**
```bash
# Complete system shutdown procedure
1. Turn off all LED lighting systems
2. Shut down HVAC equipment
3. Stop all water/nutrient pumps
4. Disconnect main power at panel
5. Install lockout/tagout devices
6. Verify zero energy state with multimeter
```

**2. Control Panel Installation**
- Mount industrial enclosure in accessible location
- Install DIN rail for component mounting
- Run dedicated 120V circuit for control power
- Install Ethernet connection for network access

### Phase 2: Low-Voltage Control Installation

**1. Raspberry Pi Setup**
```bash
# Install Container Farm Control System
sudo ./setup.sh

# Configure hardware interfaces
sudo raspi-config
# Enable I2C, SPI, 1-Wire, UART
```

**2. Sensor Installation**

**Environmental Sensors:**
```
BME280 Wiring (I2C):
VIN → 3.3V (Pi Pin 1)
GND → Ground (Pi Pin 6)
SCL → GPIO 3 (Pi Pin 5)
SDA → GPIO 2 (Pi Pin 3)

MH-Z19B CO2 Sensor (UART):
VIN → 5V (Pi Pin 2)
GND → Ground (Pi Pin 6)
TX → GPIO 15 (Pi Pin 10)
RX → GPIO 14 (Pi Pin 8)
```

**Temperature Zones (1-Wire):**
```
DS18B20 Chain Wiring:
VDD → 3.3V (Pi Pin 1)
GND → Ground (Pi Pin 6)
DQ → GPIO 4 (Pi Pin 7) + 4.7kΩ pullup
```

Install sensors at strategic locations:
- Sensor 1: Intake air temperature
- Sensor 2: Growing zone ambient
- Sensor 3: Canopy temperature
- Sensor 4: Exhaust air temperature
- Sensor 5: Water reservoir temperature

**3. Relay Board Installation**

**GPIO to Relay Mapping:**
```python
RELAY_CONFIG = {
    'lighting_zone_1': {'gpio': 5, 'relay': 1},
    'lighting_zone_2': {'gpio': 6, 'relay': 2},
    'exhaust_fan': {'gpio': 13, 'relay': 3},
    'intake_fan': {'gpio': 19, 'relay': 4},
    'circulation_fan': {'gpio': 20, 'relay': 5},
    'water_pump': {'gpio': 21, 'relay': 6},
    'nutrient_pump_a': {'gpio': 26, 'relay': 7},
    'nutrient_pump_b': {'gpio': 16, 'relay': 8}
}
```

### Phase 3: High-Voltage Integration

**⚠️ LICENSED ELECTRICIAN REQUIRED FOR THIS PHASE**

**1. Contactor Installation**
Install contactors between existing equipment and relay controls:

```
Lighting Control:
120V Hot → Contactor Line → LED Driver Input
Relay Output → Contactor Coil (120V)
Neutral → Contactor Coil Return
```

**2. Equipment Integration**

**LED Lighting Systems:**
- Identify existing LED drivers/ballasts
- Install contactors rated for driver input current
- Maintain existing dimming controls if desired
- Add current monitoring for diagnostics

**HVAC Equipment:**
- Install contactors for fan motor control
- Maintain existing variable speed drives if present
- Add temperature interlocks for safety
- Install manual override switches

**Water/Nutrient Systems:**
- Install pump contactors with overload protection
- Add flow switches for pump monitoring
- Install pressure relief valves
- Maintain existing filtration systems

### Phase 4: Safety Systems Integration

**1. Emergency Stop Circuit**
```
E-Stop Button → Safety Relay → All Contactors
- Normally closed E-stop contacts
- Safety relay with forced-guided contacts
- Independent of Raspberry Pi control
- Manual reset required after activation
```

**2. Interlock Systems**
- High temperature shutdown (independent thermostat)
- Low water level protection
- Door interlocks for personnel safety
- Fire suppression system integration

**3. Alarm and Notification**
```python
ALARM_THRESHOLDS = {
    'temperature_high': 35.0,  # °C
    'temperature_low': 10.0,   # °C
    'humidity_high': 85.0,     # %
    'humidity_low': 30.0,      # %
    'co2_high': 2000,          # ppm
    'ph_high': 7.0,
    'ph_low': 5.0,
    'ec_high': 3.0,            # mS/cm
    'ec_low': 0.5              # mS/cm
}
```

## Software Configuration

### 1. System Setup

**Initial Configuration:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Container Farm Control System
cd /home/pi/container-farm
sudo ./setup.sh

# Configure hardware
sudo nano /boot/config.txt
# Add: dtparam=i2c_arm=on
#      dtparam=spi=on
#      enable_uart=1
#      dtoverlay=w1-gpio
```

### 2. Sensor Calibration

**pH Probe Calibration:**
```python
# Two-point calibration procedure
CALIBRATION_SOLUTIONS = {
    'ph4': 4.00,
    'ph7': 7.00,
    'ph10': 10.00
}

# Calibration steps:
# 1. Clean probe with distilled water
# 2. Immerse in pH 7.00 solution
# 3. Record ADC reading
# 4. Repeat with pH 4.00 solution
# 5. Calculate slope and offset
```

**EC Probe Calibration:**
```python
# Single-point calibration
CALIBRATION_STANDARD = 1.413  # mS/cm at 25°C

# Temperature compensation formula:
# EC_25 = EC_measured / (1 + 0.02 * (temp - 25))
```

### 3. Automation Rules

**Basic Growing Program:**
```python
DAILY_SCHEDULE = {
    'lights_on': '06:00',
    'lights_off': '22:00',  # 16-hour photoperiod
    'irrigation_cycles': [
        '08:00', '12:00', '16:00', '20:00'
    ],
    'nutrient_check': '10:00',
    'data_backup': '02:00'
}

CLIMATE_TARGETS = {
    'day_temp': {'min': 22, 'max': 26},    # °C
    'night_temp': {'min': 18, 'max': 22},  # °C
    'humidity': {'min': 50, 'max': 70},    # %
    'co2_day': {'min': 800, 'max': 1200}, # ppm
    'co2_night': {'min': 400, 'max': 600}  # ppm
}
```

## Testing and Commissioning

### 1. System Testing Checklist

**Control System Tests:**
- [ ] Raspberry Pi boots and connects to network
- [ ] All sensors report valid readings
- [ ] Relay outputs switch correctly
- [ ] Database logging functions
- [ ] Web interface accessible
- [ ] Backup systems functional

**Safety System Tests:**
- [ ] Emergency stop functions correctly
- [ ] High temperature alarms trigger
- [ ] Low water level protection works
- [ ] Manual overrides functional
- [ ] All interlocks verified

**Equipment Integration Tests:**
- [ ] LED lighting controls properly
- [ ] Fans respond to temperature
- [ ] Pumps cycle on schedule
- [ ] Nutrient dosing accurate
- [ ] Climate maintains targets

### 2. Performance Validation

**Data Collection Period:**
Run system for 7 days minimum before full operation:
- Monitor all sensor readings
- Verify climate stability
- Check nutrient consumption rates
- Validate irrigation timing
- Confirm system reliability

**Optimization Phase:**
- Adjust PID parameters for climate control
- Calibrate nutrient dosing rates
- Fine-tune irrigation schedules
- Optimize lighting schedules for crop type

## Maintenance and Monitoring

### 1. Preventive Maintenance Schedule

**Weekly:**
- Clean pH and EC probes
- Check water reservoir levels
- Inspect all electrical connections
- Review system logs for errors

**Monthly:**
- Calibrate pH and EC probes
- Clean air intake filters
- Check pump performance
- Update system software

**Quarterly:**
- Comprehensive system backup
- Relay contact inspection
- Sensor accuracy verification
- Emergency system testing

### 2. Remote Monitoring Setup

**Network Configuration:**
```bash
# Static IP configuration
sudo nano /etc/dhcpcd.conf
# Add:
# interface eth0
# static ip_address=192.168.1.100/24
# static routers=192.168.1.1
# static domain_name_servers=8.8.8.8

# VPN setup for remote access
sudo apt install wireguard
# Configure WireGuard for secure remote access
```

**Alert System:**
```python
NOTIFICATION_CONFIG = {
    'email': {
        'smtp_server': 'smtp.gmail.com',
        'port': 587,
        'recipients': ['farmer@example.com']
    },
    'sms': {
        'service': 'twilio',
        'numbers': ['+1234567890']
    },
    'triggers': {
        'critical': ['high_temp', 'low_water', 'system_failure'],
        'warning': ['sensor_offline', 'maintenance_due'],
        'info': ['harvest_ready', 'nutrient_low']
    }
}
```

## Troubleshooting Common Issues

### 1. Sensor Problems

**I2C Device Not Found:**
```bash
# Check I2C bus
sudo i2cdetect -y 1

# If device missing:
# 1. Check wiring connections
# 2. Verify power supply voltage
# 3. Check for address conflicts
# 4. Test with known-good sensor
```

**Temperature Sensor Errors:**
```bash
# Check 1-Wire devices
ls /sys/bus/w1/devices/

# If no devices found:
# 1. Verify 4.7kΩ pullup resistor
# 2. Check wiring to GPIO 4
# 3. Ensure device tree overlay loaded
# 4. Test sensor with multimeter
```

### 2. Control Issues

**Relays Not Switching:**
- Check GPIO pin assignment in software
- Verify relay board power supply (5V)
- Test with multimeter across relay contacts
- Check for blown fuses in relay circuits

**High-Voltage Equipment Not Responding:**
- Verify contactor coil energization
- Check contactor contact condition
- Ensure proper line voltage supply
- Test manual operation of equipment

### 3. Network Problems

**Web Interface Inaccessible:**
```bash
# Check service status
sudo systemctl status nginx
sudo systemctl status container-farm

# Check network connectivity
ip addr show
ping google.com

# Restart services if needed
sudo systemctl restart nginx
sudo systemctl restart container-farm
```

## Cost Analysis

### Conversion Cost Breakdown

**Control System Hardware:** $590-665
**Professional Installation:** $1,000-2,000
**Sensors and Monitoring:** $500-800
**Safety Equipment:** $300-500
**Total Conversion Cost:** $2,390-3,965

### Return on Investment

**Benefits:**
- Reduced labor costs (automated monitoring)
- Improved crop yields (precise control)
- Lower energy costs (optimized schedules)
- Enhanced crop quality (stable environment)
- Data-driven optimization

**Typical Payback Period:** 6-18 months depending on operation size

## Advanced Features

### 1. Machine Learning Integration

**Predictive Analytics:**
- Crop growth modeling
- Yield prediction algorithms
- Pest/disease early detection
- Resource optimization

### 2. Multi-Container Management

**Centralized Control:**
- Multiple container coordination
- Resource sharing optimization
- Centralized data analysis
- Fleet management dashboard

### 3. Integration with External Systems

**Supply Chain Integration:**
- Automated ordering systems
- Harvest scheduling
- Quality tracking
- Traceability systems

---

## Conclusion

Converting a freight farm to the Container Farm Control System provides:
- Complete control over growing environment
- Data sovereignty and privacy
- Cost-effective monitoring and automation
- Scalable and customizable platform
- Open-source flexibility

The conversion process requires careful planning, professional electrical work, and thorough testing, but results in a powerful, flexible growing system that can be continuously improved and customized for specific crops and growing methods.

---

*For technical support during conversion, consult the project documentation and community forums. Always prioritize safety and use qualified professionals for electrical work.*