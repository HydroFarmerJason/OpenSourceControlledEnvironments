# GitHub Issue Templates

## File: `.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug'
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**System Information:**
 - Raspberry Pi Model: [e.g. Pi 4B 4GB]
 - OS Version: [e.g. Raspberry Pi OS Bullseye]
 - Container Farm Version: [e.g. v1.0.0]
 - Python Version: [e.g. 3.9.2]

**Hardware Configuration:**
 - Sensors: [list connected sensors]
 - Relays: [relay board model]
 - Other hardware: [any other relevant hardware]

**Error Logs**
If applicable, paste relevant error messages or log files:
```
[paste logs here]
```

**Additional context**
Add any other context about the problem here.
```

## File: `.github/ISSUE_TEMPLATE/feature_request.md`

```markdown
---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: 'enhancement'
assignees: ''
---

**Is your feature request related to a problem? Please describe.**
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

**Describe the solution you'd like**
A clear and concise description of what you want to happen.

**Describe alternatives you've considered**
A clear and concise description of any alternative solutions or features you've considered.

**Use Case**
How would this feature be used? What type of user would benefit?
- [ ] Educational (classroom use)
- [ ] Therapeutic (horticultural therapy)
- [ ] Commercial (production farming)
- [ ] Research (data collection/analysis)
- [ ] Hobby (home growing)

**Additional context**
Add any other context or screenshots about the feature request here.

**Implementation Ideas**
If you have ideas about how this could be implemented, please share them here.
```

## File: `.github/ISSUE_TEMPLATE/hardware_compatibility.md`

```markdown
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
```

## File: `.github/ISSUE_TEMPLATE/support_request.md`

```markdown
---
name: Support request
about: Get help with installation or configuration
title: '[HELP] '
labels: 'help wanted'
assignees: ''
---

**What are you trying to accomplish?**
Describe what you're trying to set up or achieve.

**What have you tried?**
List the steps you've already taken.

**Where are you stuck?**
Describe exactly where the process is failing or what's confusing.

**System Setup**
- Raspberry Pi Model: [e.g. Pi 4B 4GB]
- Installation method: [setup.sh/manual/other]
- Use case: [educational/therapeutic/commercial/research/hobby]

**Error Messages**
If you're getting errors, paste them here:
```
[paste error messages here]
```

**Configuration**
If relevant, share your configuration files (remove any sensitive information):
```json
[paste relevant config here]
```

**Photos**
If hardware-related, photos of your setup can be very helpful.

**Urgency**
- [ ] Not urgent - learning/experimenting
- [ ] Moderate - working on project with deadline
- [ ] High - production system down
- [ ] Educational - need for class/workshop

**Experience Level**
- [ ] Beginner - new to Raspberry Pi/electronics
- [ ] Intermediate - some experience with Pi projects
- [ ] Advanced - experienced with embedded systems
```
