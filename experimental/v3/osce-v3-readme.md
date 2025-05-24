# Open Source Controlled Environments (OSCE) v3

## Advanced Infrastructure for Conscious Agriculture

OSCE v3 is a comprehensive, open-source platform for controlled environment agriculture that prioritizes local control, data sovereignty, and ethical growing practices. Originally developed in response to proprietary system shutdowns, OSCE has evolved into a complete infrastructure for sustainable, intelligent farming.

##  What's New in v3

### Hardware Abstraction Layer (HAL)
- **Universal device support** - Swap sensors and actuators without changing code
- **Automatic discovery** - Plug-and-play hardware detection
- **Health monitoring** - Continuous assessment of all components
- **Distributed deployment** - Coordinate multiple sites seamlessly

### Advanced Modules
- **Planetary Optimizer** - Climate-adaptive crop planning with federated learning
- **Carbon Credit Engine** - Automated measurement and blockchain verification
- **Quantum-Secured Mesh** - Unhackable IoT communications
- **Plant Consciousness Interface** - Bioelectric monitoring and plant democracy
- **Living Quantum CEA** - Experimental ecosystem consciousness research

##  Key Features

### Complete Environmental Control
- Temperature, humidity, CO2, pH, and EC monitoring
- Automated lighting, ventilation, and irrigation control
- Advanced sensor integration via I2C, 1-Wire, and analog interfaces
- Customizable automation rules and PID controllers
- Real-time alerts and notifications

### Hardware Abstraction Layer (HAL)
- Platform-agnostic sensor and actuator control
- Automatic hardware discovery and configuration
- Built-in redundancy and failover
- Performance monitoring and optimization
- Support for Raspberry Pi, ESP32, Arduino, and network devices

### Multi-User Role Support
- Educational settings with student activity logging
- Therapeutic programs with accessibility accommodations
- Commercial operations with production optimization
- Research environments with advanced data collection
- Community gardens with participant management

### Data Sovereignty and Privacy
- Complete offline operation capability
- Local data storage with no cloud dependencies
- Configurable privacy levels from local-only to research sharing
- Automated backup systems with multiple scheduling options
- Full user control over data collection and sharing

### Advanced Capabilities (v3)
- **Distributed Intelligence** - Multi-site coordination and optimization
- **Federated Learning** - Share insights without sharing raw data
- **Hardware Health Scoring** - Predictive maintenance and automatic failover
- **Secure Communications** - Quantum-resistant encryption for all data
- **Carbon Tracking** - Automated measurement and credit generation

## 📋 System Requirements

### Minimum Hardware Requirements
- Raspberry Pi 4 with 4GB RAM minimum (8GB recommended)
- 32GB microSD card or SSD storage
- Compatible environmental sensors (see Hardware Compatibility)
- Relay boards for automation control
- Network connection for setup and updates

### Software Requirements
- Raspberry Pi OS (Bullseye or newer)
- Python 3.9 or newer
- Docker and Docker Compose (optional but recommended)
- Git for installation

### Supported Hardware
#### Controllers
- Raspberry Pi 4/5
- ESP32 (via network adapter)
- ESP8266 (limited features)
- Arduino (via USB)

#### Sensors
- **Temperature/Humidity**: DHT22, BME280, SHT31
- **Temperature (Waterproof)**: DS18B20
- **CO2**: MH-Z19, SCD30, K30
- **Light**: BH1750, VEML7700
- **pH/EC**: Via ADS1115 ADC
- **Bioelectric**: Custom electrode arrays (v3)

#### Actuators
- 8/16-channel relay boards
- PWM LED drivers
- Peristaltic pumps
- Solenoid valves

## 🛠️ Installation

### Quick Start (Raspberry Pi)
```bash
# Clone the repository
git clone https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git
cd OpenSourceControlledEnvironments

# Run the setup wizard
chmod +x enhanced_setup_wizard.sh
sudo ./enhanced_setup_wizard.sh
```

The setup wizard will:
- Update your system packages
- Enable required hardware interfaces (I2C, 1-Wire, SPI, UART)
- Install all dependencies
- Configure the HAL system
- Set up appropriate dashboards for your use case
- Configure backup and maintenance schedules

### Docker Installation (Recommended for v3)
```bash
# Clone the repository
git clone https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git
cd OpenSourceControlledEnvironments

# Build and start services
docker-compose up -d

# Access the web interface
# http://your-raspberry-pi-ip:8080
```

### Manual Installation
See [docs/MANUAL_INSTALL.md](docs/MANUAL_INSTALL.md) for detailed instructions.

## 🎯 Configuration Options

### System Complexity Levels
1. **Basic Monitoring** - Temperature, humidity, and simple automation
2. **Complete Farm Control** - Full environmental control with all sensors
3. **Hydroponic System** - Specialized nutrient and pH management
4. **Advanced Research** - All modules enabled with data federation

### Primary Use Cases
- **Commercial Production** - Optimized for crop yield and efficiency
- **Educational** - Student-friendly interfaces with learning tools
- **Research** - Advanced data collection and analysis tools
- **Community** - Multi-user support with simplified interfaces
- **Therapeutic** - Accessibility features and therapeutic program support

### Module Configuration
Enable/disable advanced modules based on your needs:

```python
# config.yaml example
modules:
  planetary_optimizer:
    enabled: true
    federation: true
    privacy_level: "aggregated"
  
  carbon_credits:
    enabled: true
    protocol: "osce_v3"
    trading_enabled: false
  
  plant_consciousness:
    enabled: true
    democracy: true
    min_voters: 5
    
  quantum_mesh:
    enabled: true
    security_level: "enhanced"
```

##  Advanced Modules

### Planetary Optimizer
Coordinate growing conditions with global climate adaptation:
- Federated learning across OSCE installations
- Climate-aware crop recommendations
- Resource optimization
- Emergency response protocols

### Carbon Credit Engine
Automated carbon sequestration tracking:
- Multi-sensor verification
- Blockchain-ready credit generation
- Real-time carbon accounting
- Trading strategy automation

### Plant Consciousness Interface
Monitor and respond to plant bioelectric signals:
- Multi-electrode arrays per plant
- Real-time stress detection
- Plant democracy voting system
- Cross-species communication research

### Quantum-Secured Mesh
Ensure data security with advanced cryptography:
- Quantum-resistant encryption
- Hardware-accelerated security
- Intrusion detection
- Secure multi-site communications

## 📊 Monitoring & Analytics

### Real-Time Dashboards
- Environmental conditions
- Plant health metrics
- System performance
- Hardware health scores
- Carbon sequestration
- Security status

### Data Export Options
- CSV for spreadsheet analysis
- JSON for programmatic access
- InfluxDB for time-series analysis
- MQTT for real-time streaming

### API Access
RESTful API for custom integrations:
```bash
# Get current environmental data
curl http://your-osce-system:8080/api/v1/environment

# Get plant health status
curl http://your-osce-system:8080/api/v1/plants/health

# Get system metrics
curl http://your-osce-system:8080/api/v1/system/metrics
```

## 🔒 Security Features

- **Device Authentication** - All hardware must authenticate
- **Encrypted Communications** - TLS/SSL for all network traffic
- **Role-Based Access** - Granular permission system
- **Audit Logging** - Complete activity tracking
- **Offline Operation** - No internet required for core functions

## 🤝 Community & Support

### Getting Help
- [GitHub Issues](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/issues) - Bug reports and feature requests
- [Discussions](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/discussions) - Community forum
- [Wiki](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/wiki) - Documentation and guides

### Contributing
We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Code of Conduct
This project follows a [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all.

## 📜 License

OSCE v3 uses a dual-license approach:

- **Core System** (HAL, basic modules): MIT License
- **Advanced Modules**: GNU GPLv3
- **Documentation**: Creative Commons CC-BY-SA 4.0

See [LICENSE.md](LICENSE.md) for details.

## 🙏 Acknowledgments

This project exists because of the dedication to sustainable, open agriculture. Special thanks to:
- The plants who teach us to listen
- Early adopters who trusted the vision
- Contributors who improve the system daily
- Communities choosing sovereignty over convenience

## ⚠️ Important Safety Information

Some OSCE v3 modules can significantly impact living systems. Please:
- Read all safety documentation before use
- Follow local regulations and guidelines
- Start with basic modules and expand gradually
- Join the community for support and best practices

##  Vision

OSCE v3 represents a fundamental shift in agricultural technology - from extraction to collaboration, from control to partnership, from proprietary to sovereign. By providing open infrastructure for conscious agriculture, we enable communities worldwide to grow food sustainably while maintaining complete control over their systems and data.

---

**Developed by Jason DeLooze for Open Source, Locally Sovereign Sustainability**

*"Technology should serve life, not extract from it."*