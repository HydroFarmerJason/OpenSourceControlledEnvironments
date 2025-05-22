Container Farm Control System

Enhanced Interactive Setup Wizard and Control Platform

OVERVIEW

The Container Farm Control System is a comprehensive, open-source solution designed to provide local control and monitoring for container farms, greenhouses, and controlled growing environments. Originally developed in response to the shutdown of Farmhand.ag, this system prioritizes user autonomy, data sovereignty, and ethical growing practices while maintaining full functionality for commercial, educational, therapeutic, and research applications.

This enhanced version includes specialized features for diverse user communities including educators, agritherapists, researchers, community organizers, and commercial growers. The system operates entirely offline when desired, ensuring complete control over your growing environment and data.

KEY FEATURES

Complete Environmental Control
- Temperature, humidity, CO2, pH, and EC monitoring
- Automated lighting, ventilation, and irrigation control
- Advanced sensor integration via I2C, 1-Wire, and analog interfaces
- Customizable automation rules and PID controllers
- Real-time alerts and notifications

Multi-User Role Support
- Educational settings with student activity logging
- Therapeutic programs with accessibility accommodations
- Commercial operations with production optimization
- Research environments with advanced data collection
- Community gardens with participant management

Accessibility and Inclusion
- High-contrast displays for visual impairments
- Simplified interfaces for motor skill limitations
- Cognitive accommodations with visual instruction guides
- Voice control preparation for future accessibility features
- Touch-safe interface options for therapeutic settings

Data Sovereignty and Privacy
- Complete offline operation capability
- Local data storage with no cloud dependencies
- Configurable privacy levels from local-only to research sharing
- Automated backup systems with multiple scheduling options
- Full user control over data collection and sharing

Educational Integration
- Grade-appropriate dashboard configurations
- Student activity tracking and assessment tools
- Curriculum alignment with educational standards
- Photo journaling for growth documentation
- Lesson plan integration and management

Therapeutic Applications
- Horticultural therapy specific configurations
- Progress tracking for therapeutic outcomes
- Sensory experience integration
- Participant-appropriate interface simplification
- Documentation tools for therapy session records

SYSTEM REQUIREMENTS

Hardware Requirements
- Raspberry Pi 4 with 4GB RAM minimum (8GB recommended)
- 32GB microSD card or SSD storage
- Compatible environmental sensors (temperature, humidity, CO2, pH, EC)
- Relay boards for automation control
- Optional webcam for photo documentation
- Network connection for setup and updates

Software Requirements
- Raspberry Pi OS (Bullseye or newer)
- Mycodo environmental regulation system
- Python 3.7 or newer
- InfluxDB for data storage
- Nginx web server
- SQLite for configuration management

Supported Hardware
- DS18B20 temperature sensors
- BME280/SHT31 temperature and humidity sensors
- MH-Z19 CO2 sensors
- ADS1115 analog-to-digital converters
- pH and EC sensors via ADC
- 8-channel relay boards
- USB and Pi Camera modules
- Various I2C sensor modules

INSTALLATION

Quick Start Installation

1. Download and flash Raspberry Pi OS to your SD card
2. Enable SSH and configure basic network settings
3. Clone or download this repository to your Raspberry Pi
4. Run the enhanced setup wizard: sudo ./enhanced_setup_wizard.sh
5. Follow the interactive prompts to configure your system
6. Complete hardware connections based on your selected configuration
7. Access the web interface at your Raspberry Pi's IP address

The setup wizard will automatically:
- Update your system packages
- Enable required hardware interfaces (I2C, 1-Wire, SPI, UART)
- Install Mycodo and all dependencies
- Configure sensors and automation based on your selections
- Set up appropriate dashboards for your use case
- Configure backup and maintenance schedules
- Apply accessibility settings if needed
DEPENDENCIES AND TESTING

The setup scripts require root privileges and an internet connection to install packages via apt and pip. Package versions are not pinned, so behavior may change over time. Run the scripts on a fresh Raspberry Pi OS image and review them before execution. Most scripts should be executed with sudo.


CONFIGURATION OPTIONS

The setup wizard provides several configuration paths:

System Complexity Levels
- Basic Monitoring: Temperature, humidity, and simple automation
- Complete Farm Control: Full environmental control with all sensors
- Hydroponic System: Specialized nutrient and pH management

Primary Use Cases
- Commercial Production: Optimized for crop yield and efficiency
- Educational: Student-friendly interfaces with learning tools
- Social Impact: Simplified interfaces for community programs
- Research: Advanced data logging and experimental controls

User Role Configurations
- Educator: Classroom-appropriate settings with student tracking
- Technician: Technical interfaces for maintenance personnel
- Farmer: Production-focused automation and monitoring
- Researcher: Advanced data collection and analysis tools
- Therapist: Therapeutic program support with documentation
- Agritherapist: Specialized horticultural therapy features
- Community Organizer: Multi-user community garden management

Privacy and Data Options
- Local Only: All data remains on device with no external connections
- Backup Ready: Optional USB or network backups without cloud storage
- Research Sharing: Optional anonymous system statistics sharing

ACCESSIBILITY FEATURES

The system includes comprehensive accessibility accommodations:

Visual Impairments
- High-contrast dashboard themes
- Large font size options
- Audio feedback capabilities
- Screen reader compatibility
- Color-coded interface elements

Motor Skill Accommodations
- Simplified control interfaces
- Large button sizing with increased spacing
- Alternative input methods
- Touch-safe interface guards
- Reduced complexity interaction modes

Cognitive Accommodations
- Simplified dashboard views
- Visual instruction guides
- Consistent color-coding systems
- Step-by-step activity prompts
- Clear task organization

THERAPEUTIC APPLICATIONS

Specialized features for horticultural therapy include:

Participant Engagement
- Visual plant growth tracking
- Simple task-based interfaces
- Sensory experience integration
- Progress documentation tools
- Customizable activity prompts

Therapeutic Documentation
- Session note templates
- Participant observation logs
- Progress tracking metrics
- Photo journal integration
- Outcome measurement tools

Accessibility Integration
- Adaptive interfaces based on participant needs
- Multi-sensory feedback options
- Simplified control mechanisms
- Safety-focused design considerations
- Therapeutic goal alignment

EDUCATIONAL FEATURES

Purpose-built educational tools include:

Classroom Integration
- Student activity logging and tracking
- Grade-appropriate interface configurations
- Curriculum standard alignment
- Data export for classroom analysis
- Safety considerations for school environments

Learning Documentation
- Photo journaling for growth observation
- Data collection templates
- Experiment tracking capabilities
- Student progress monitoring
- Assessment integration tools

Lesson Plan Support
- Pre-built educational activities
- Cross-curricular connection opportunities
- Student-led inquiry support
- Real-time data visualization
- Scientific method integration

HARDWARE SETUP

The system supports various sensor configurations:

Basic Monitoring Setup
- DS18B20 temperature sensor on GPIO 4
- DHT22 humidity sensor on GPIO 17
- Single relay for light control on GPIO 23
- Single relay for fan control on GPIO 24

Complete Farm Control Setup
- Multiple DS18B20 temperature sensors on GPIO 4
- BME280 environmental sensor via I2C
- MH-Z19 CO2 sensor via UART
- 8-channel relay board on GPIOs 5, 6, 13, 19, 20, 21, 26, 16
- Optional webcam for monitoring

Hydroponic System Setup
- All sensors from complete setup
- ADS1115 ADC for analog sensors via I2C
- pH sensor connected to ADS1115 A0
- EC sensor connected to ADS1115 A1
- Additional pumps for nutrient dosing

Safety considerations are built into all configurations with special attention to educational and therapeutic environments.

SOFTWARE ARCHITECTURE

The system utilizes a layered architecture:

Core System Layer
- Raspberry Pi OS as the foundation
- Mycodo for environmental regulation
- InfluxDB for time-series data storage
- SQLite for configuration management

Application Layer
- Web-based dashboard interface
- Sensor management and calibration
- Automation rule engine
- Alert and notification system

User Interface Layer
- Role-specific dashboard configurations
- Accessibility-adapted interfaces
- Mobile-responsive design
- Multi-language support framework

Integration Layer
- Hardware abstraction for sensors
- Backup and recovery systems
- Update and maintenance tools
- Documentation and reporting

DATA MANAGEMENT

The system prioritizes data sovereignty with multiple options:

Local Storage
- All data stored locally by default
- InfluxDB for sensor measurements
- SQLite for system configuration
- Photo storage for documentation

Backup Options
- Automated local backups
- USB drive backup capability
- Network storage integration
- Configurable retention policies

Data Export
- CSV export for analysis
- PDF report generation
- Photo documentation packages
- System configuration backups

Privacy Controls
- Granular data sharing controls
- Anonymous system statistics option
- Complete offline operation mode
- User-controlled data retention

AUTOMATION CAPABILITIES

Comprehensive automation features include:

Environmental Control
- Temperature regulation with heating and cooling
- Humidity control with humidifiers and dehumidifiers
- CO2 supplementation based on plant needs
- Lighting control with customizable photoperiods

Nutrient Management
- pH monitoring and automatic adjustment
- EC monitoring for nutrient levels
- Automated nutrient dosing systems
- Water level monitoring and refilling

Safety Systems
- Emergency shutdown procedures
- Alert notifications for critical conditions
- Backup sensor monitoring
- System health checks

MAINTENANCE AND SUPPORT

Built-in maintenance features include:

Automated Maintenance
- System health monitoring
- Sensor calibration reminders
- Software update notifications
- Backup verification systems

Diagnostic Tools
- Sensor connectivity testing
- System performance monitoring
- Error log analysis
- Hardware status reporting

Update Management
- Automated security updates
- Feature update notifications
- Configuration backup before updates
- Rollback capabilities for stability

ETHICAL CONSIDERATIONS

This project operates under strong ethical principles:

Core Values
- User autonomy and data sovereignty
- Transparency in system operation
- Respect for privacy and consent
- Support for sustainable practices

Design Philosophy
- Local control over cloud dependency
- Open source transparency
- Community-driven development
- Educational and therapeutic priority

Responsible Use
- Not intended for surveillance applications
- Designed to enhance rather than replace human judgment
- Supportive of community and cooperative goals
- Aligned with sustainable growing practices

LICENSE AND LEGAL

The project uses a dual-license approach to balance openness with proper attribution:

Documentation License
All documentation, guides, and educational materials are licensed under Creative Commons Attribution-ShareAlike 4.0 International.

Code License
All software code and scripts are licensed under the MIT License.

See license.md for full terms.
COMMUNITY AND CONTRIBUTION

This project welcomes contributions from the growing community:

How to Contribute
- Submit bug reports and feature requests
- Contribute code improvements and new features
- Share configuration examples and use cases
- Provide documentation improvements
- Test and validate new hardware compatibility

Community Guidelines
- Respectful and inclusive communication
- Focus on practical solutions for growers
- Priority for accessibility and educational use
- Commitment to ethical and sustainable practices

SUPPORT AND RESOURCES

Multiple support channels are available:

Documentation
- Comprehensive setup guides
- Hardware compatibility lists
- Troubleshooting procedures
- Best practices documentation

Community Support
- User forums and discussion groups
- Knowledge sharing platforms
- Peer-to-peer assistance
- Experience sharing opportunities

Technical Support
- GitHub issue tracking
- Configuration assistance
- Hardware compatibility verification
- Software update guidance

FUTURE DEVELOPMENT

Planned enhancements include:

Technical Improvements
- Enhanced voice control capabilities
- Mobile application development
- Advanced analytics integration
- Expanded hardware compatibility

Feature Additions
- Multi-language interface expansion
- Additional therapeutic program tools
- Enhanced educational curriculum integration
- Advanced research data analysis tools

Community Features
- User contribution platform
- Configuration sharing system
- Best practices documentation
- Success story sharing

This Container Farm Control System represents a commitment to user autonomy, educational access, therapeutic support, and sustainable growing practices. By providing a comprehensive, locally-controlled alternative to cloud-based systems, it ensures that growers maintain full control over their operations and data while supporting diverse community needs from education to therapy to commercial production.

The system's emphasis on accessibility, ethical use, and community support makes it suitable for a wide range of applications while maintaining the core principle that technology should serve users rather than extracting value from them. Whether used in classrooms, therapy programs, research facilities, or commercial operations, this system prioritizes user needs and community values above all else.
