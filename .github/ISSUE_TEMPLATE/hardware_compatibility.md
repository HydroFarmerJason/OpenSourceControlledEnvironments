---
name: Hardware compatibility report
about: Report testing results for new hardware
title: '[HARDWARE] Testing: [Hardware Name]'
labels: 'hardware'
assignees: ''
---

**Hardware Information**
- Component Name: [e.g. BME680 Environmental Sensor]
- Manufacturer: [e.g. Bosch]
- Supplier: [e.g. Adafruit #3660]
- Price: [e.g. $22.50]
- Datasheet/Link: [URL to product page or datasheet]

**Testing Results**
- [ ] Basic functionality confirmed
- [ ] Integration with existing system successful
- [ ] 24-hour stability test completed
- [ ] Documentation updated

**Configuration Details**
```
Interface: [I2C/SPI/1-Wire/Analog/UART]
Address/Pin: [0x77 or GPIO 4]
Voltage: [3.3V/5V]
Current Draw: [mA]
```

**Wiring Information**
```
Component Pin → Raspberry Pi
VIN → 3.3V (Pin 1)
GND → Ground (Pin 6)
SCL → GPIO 3 (Pin 5)
SDA → GPIO 2 (Pin 3)
```

**Code Example**
```python
# Paste working code example here
```

**Performance Notes**
- Accuracy: [e.g. ±2% RH, ±0.3°C]
- Response time: [e.g. 8 seconds]
- Any quirks or special considerations

**Photos**
Please attach photos of:
- [ ] Wiring setup
- [ ] Working sensor readings
- [ ] Any custom mounting/enclosure

**Recommendation**
- [ ]  Fully recommended - works perfectly
- [ ]  Recommended with notes - works but has limitations
- [ ]  Experimental - basic functionality only
- [ ]  Not recommended - significant issues

**Additional Notes**
Any other information that would help other users.
