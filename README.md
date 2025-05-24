#  OSCE - Open Source Controlled Environments

<div align="center">

![OSCE Logo](https://img.shields.io/badge/OSCE-2.1-green?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-yellow?style=for-the-badge)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production--Ready-success?style=for-the-badge)

**The WordPress of IoT for Controlled Environment Agriculture**

Created by Jason DeLooze for Locally Sovereign Sustainability (Open Source)
osce@duck.com

[Installation](#-quick-start) • [Features](#-features) • [Documentation](#-documentation) • [Community](#-community) • [Contributing](#-contributing)

</div>

---

##  Transform Your Growing Operation in 5 Minutes

OSCE is a production-ready, modular platform that makes advanced Controlled Environment Agriculture (CEA) accessible to everyone—from hobbyists to commercial operations. Like WordPress revolutionized websites, OSCE revolutionizes IoT for agriculture.

###  Why OSCE?

| Traditional IoT | OSCE Platform |
|-----------------|---------------|
| Days to setup | **5 minutes** to operational |
| Vendor lock-in | **100% open source** |
| Limited hardware support | **Universal hardware** compatibility |
| Complex programming | **Natural language** automation |
| Isolated systems | **Federated network** ready |
| Manual monitoring | **AI-powered** optimization |

##  Quick Start

```bash
# One-line installation (Linux/MacOS)
curl -sSL https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/raw/main/install.sh | bash -s -- --version 2.1

# Your system is now running at https://localhost:8080
```

**First-time setup? See our [5-minute quickstart guide](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments)**

## OSCE v2.1 Updates Summary

The 2025 release introduces OSCE v2.1 with expanded real-time harmony features. The unified installer now sets up PHAL v2.1, HiveMindFFT v2.1, and Quantum Planetary Awareness v2.1 automatically. The dashboard has been refreshed for live WebSocket data.

Key highlights:
- 3D FFT consensus engine with role-weighted voting
- Real-time planetary state recognition with Schumann resonance monitoring
- Predictive permissions and device health recovery
- Live dashboard with harmony meter and spectrum toggle
- AI copilot SDK for predictive orchestration
- Federation ready with post-quantum encryption and blockchain audit trails


## Getting Started

### Minimum Requirements
- **Hardware**: Raspberry Pi 3+ or equivalent (2GB RAM, 10GB storage)
- **Software**: Docker, Docker Compose
- **Network**: Internet connection for initial setup

### Installation Options

#### Option 1: Quick Install (Recommended)
```bash
curl -sSL https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/raw/main/install.sh | bash -s -- --version 2.1
```

#### Option 2: Manual Installation
```bash
git clone https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git
cd OpenSourceControlledEnvironments
./install.sh --interactive
```

#### Option 3: Docker Only
```bash
docker run -d -p 8080:8080 hydrofarmer/osce:latest
```

## Example: Your First Automation
```python
# Add a temperature sensor
await env.add_sensor("greenhouse_temp", type="DHT22", pin=4)

# Create a natural language rule
env.add_rule("if greenhouse_temp > 28°C then turn exhaust_fan on")

# That's it! No complex programming required
```

## Hive Mind Demonstration
Experience multi-agent coordination with our FFT-based hive mind:
```bash
python osce-hivemind-fft.py
```

## Example Scripts
Explore advanced functionality using the scripts in the repository root:

 - `osce-unified-setup-v2.py` – Primary v2 bootstrap with PHAL, HiveMind FFT, and Quantum Planetary Awareness.
 - `osce_unified_setup.py` – Original unified setup leveraging the IoT Abstract Resource Model.
 - `osce_hal_enhanced.py` – Enhanced hardware abstraction layer with monitoring and security.
 - `osce_complete_example.py` – Comprehensive demonstration of a multi-site deployment.
 - `osce.core.living_quantum_monitor` – Evidence-led monitoring for quantum CEA experiments.

Run any script with `python <script>` to see it in action.
##  Features

###  Core Capabilities

- **Universal Hardware Support**
  - Raspberry Pi, ESP32, Arduino, and more
  - Auto-discovery of sensors and actuators
  - Hot-swappable components

- **AI-Powered Automation**
  - Natural language rule creation
  - Predictive maintenance
  - Growth optimization ML models

- **Enterprise Security**
  - Zero-trust architecture
  - Blockchain audit trails
  - Quantum-ready encryption

- **Comprehensive Monitoring**
  - Real-time dashboards
  - Automated compliance reporting
  - Mobile app support

- **Federation & Scaling**
  - Multi-site management
  - Automatic failover
  - Global collaboration network

- **Unified Hive Mind**
  - Frequency-domain agent coordination via FFT
  - Bridges digital decisions with physical actions
  - Demonstration: `osce-hivemind-fft.py`

Run any script with `python <script>` to see it in action.

##  Plugin Ecosystem

Extend OSCE with our growing plugin marketplace:

- **Weather Integration** - Proactive climate control
- **AI Plant Health** - Disease detection via camera
- **Market Prices** - Optimize growing based on demand
- **Solar Management** - Integrate renewable energy
- **Notifications** - SMS, Email, Slack, Teams

[Browse all plugins →](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/wiki/plugins)

##  Development

### Building from Source

```bash
# Clone the repository
git clone https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git
cd OpenSourceControlledEnvironments

# Setup development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Run tests
pytest

# Start development server
python -m osce.main --dev
```

### Creating a Plugin

```python
# my_plugin/plugin.yaml
id: my-awesome-plugin
name: My Awesome Plugin
version: 1.0.0
author: Your Name

# my_plugin/main.py
class Plugin:
    def __init__(self, osce):
        self.osce = osce
        
    async def activate(self):
        # Your plugin logic here
        self.osce.log("My plugin is active!")
```

##  Performance

Benchmarked on Raspberry Pi 4 (4GB):

- **Startup Time**: < 30 seconds
- **Sensor Response**: < 100ms
- **Rule Execution**: < 50ms
- **Concurrent Devices**: 100+
- **Data Points/Day**: 1M+

##  Security

OSCE takes security seriously:

-  Regular security audits
-  Automated vulnerability scanning
-  Responsible disclosure program
-  End-to-end encryption option
-  GDPR/CCPA compliant

Report security issues to: security@osce.io

##  Contributing

We love contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

### Ways to Contribute

1. ** Report Bugs**: [Issue Tracker](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/issues)
2. ** Suggest Features**: [Feature Requests](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/discussions/categories/ideas)
3. ** Improve Docs**: Always appreciated!
4. ** Submit PRs**: Fork, code, test, PR
5. ** Translate**: Help us go global
6. ** Create Tutorials**: Share your knowledge

##  License

OSCE is open source under the [MIT License](LICENSE). Use it freely in personal and commercial projects.

##  Acknowledgments

Built with  by the OSCE Community

Special thanks to:
- All our contributors and testers
- The open-source projects we build upon
- Growers worldwide sharing their knowledge

---

<div align="center">

** Growing the future, together **

[Website](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments) • [Documentation](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/wiki) • [Community](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/discussions) • [Donate](https://github.com/sponsors/HydroFarmerJason)

</div>
