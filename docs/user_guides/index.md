---
layout: default
title: Container Farm Control System
---

# Container Farm Control System

## A Raspberry Pi & Mycodo Solution for Ex-Farmhand Users

![Raspberry Pi Farm Control System](assets/images/header-image.jpg)

This project provides a complete guide and resources for implementing a local control system for container farms that previously operated with the farmhand.ag platform (discontinued April 2025). The solution uses Raspberry Pi hardware and Mycodo environmental regulation software to maintain essential monitoring and automation capabilities for Freight Farms or other container farm systems.

## Overview

This control system provides a local, open-source alternative to the cloud-based farmhand.ag platform, offering:

- **Works offline** — no reliance on cloud services
- **Environmental monitoring** of temperature, humidity, CO₂, pH, EC, and lighting
- **Automated control** of farm systems via relays and PID controllers
- **Data logging** with a local InfluxDB database
- **Web-based dashboard** accessible via local network
- **Customizable automation** for specific growing conditions

## Quick Navigation

- [Getting Started](pages/getting-started.html)
- [Hardware Setup](pages/hardware-setup.html)
- [Software Configuration](pages/software-configuration.html)
- [System Integration](pages/system-integration.html)
- [Troubleshooting](pages/troubleshooting.html)
- [Ethics Statement](pages/ethics.html)

## Hardware Requirements

- Raspberry Pi 4 or 5 with 4GB+ RAM
- 32GB or larger microSD card or SSD
- 5V power supply for Raspberry Pi
- Network connection (Ethernet recommended)
- Weatherproof enclosure
- Relay boards compatible with 3.3V signaling
- Environmental sensors (temperature, humidity, CO₂, pH, EC, etc.)
- Analog-to-digital converters (if using analog sensors)

## Software Stack

- Raspberry Pi OS (64-bit recommended)
- Mycodo environmental regulation system
- InfluxDB for time-series data storage
- Optional: SSH access, VPN for remote management

## Getting Started

Ready to build your own system? Start with our [installation guide](pages/installation.html) or download the [master setup script](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/blob/main/scripts/master_setup.sh) to automate the process.

## Contributing

Contributions are welcome! Please read our [contributing guidelines](pages/contributing.html) for details on how to submit contributions.

## License

This project uses a dual-license approach:
- **Documentation** is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](license.md)
- **Code and scripts** are licensed under the [MIT License](license.md)

## Acknowledgments

- [Mycodo Project](https://github.com/kizniche/Mycodo)
- [Raspberry Pi Foundation](https://www.raspberrypi.org/)
- Container farm operators who shared their experiences

Originally created by Jason DeLooze.
