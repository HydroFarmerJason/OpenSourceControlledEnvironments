# Container Farm Control System - Enhanced Version

This enhanced version of the Container Farm Control System is designed to provide a comprehensive solution for managing container farms in educational, therapeutic, research, and community settings. It includes all the core functions of the original system along with several new features designed to improve usability, accessibility, and effectiveness.

## New Features

### 1. Student Activity Logger
- Tracks student interactions with the system
- Creates detailed logs of actions for assessment
- Includes activity visualization for instructor dashboard
- Supports student authentication and personalized logging

### 2. Multilingual Support
- Supports English, Spanish, and French (expandable)
- Configurable language preferences for all UI elements
- Translation framework for easy addition of new languages
- Region-specific formatting for dates, numbers, and measurements

### 3. Offline Curriculum Binder
- Organizes lesson plans and curriculum materials
- Supports PDF and Markdown document import
- Searchable catalog with grade level and subject filters
- Automatically detects and tags educational content

### 4. Voice UI Placeholder
- Simulates future voice control capabilities
- Command hooks for testing "Water plants", "Lights on", etc.
- Option to use microphone input with speech recognition
- Framework for future voice assistant integration

### 5. Export for Stakeholders Generator
- Creates professional reports for stakeholders
- Combines project information, growth data, and photos
- Includes system performance metrics and impact data
- Multiple report formats for different audiences (education, therapy, research)

### 6. Hardware Kit Support
- Rapid deployment for pre-configured hardware kits
- QR code scanning for automatic setup
- Pre-wired GPIO pin mapping
- Support for educational, therapeutic, and research kits

## Setup & Installation

To install the enhanced version:

1. Clone this repository:
```bash
git clone https://github.com/USERNAME/container-farm-control.git
```

2. Run the installation script:
```bash
cd container-farm-control
sudo ./setup_wizard.sh
```

3. Follow the interactive setup process to configure your system.

4. At the "Additional Features" step, select which enhancements you want to enable.

## System Requirements

- Raspberry Pi 4 (2GB+ RAM recommended)
- Raspbian OS (Bullseye or newer)
- Internet connection for initial setup
- Compatible sensors and relays (see hardware guide)
- Webcam (optional, for photo documentation)
- Microphone (optional, for voice control testing)

## Usage Examples

### Student Activity Logging

```bash
# Log student activity
sudo /opt/container-farm-control/scripts/student_activity.sh "Jane Smith" "Adjusted Light Cycle" "Changed from 12 to 16 hours"

# View student logs
cat /opt/container-farm-control/logs/student_logs/jane_smith.txt
```

### Changing Language

```bash
# Switch to Spanish
sudo /opt/container-farm-control/scripts/change_language.sh es

# Switch to French
sudo /opt/container-farm-control/scripts/change_language.sh fr

# Switch to English
sudo /opt/container-farm-control/scripts/change_language.sh en
```

### Managing Lesson Plans

```bash
# Import a lesson plan
sudo /opt/container-farm-control/scripts/manage_lessons.sh import /path/to/lesson.pdf

# List all lesson plans
sudo /opt/container-farm-control/scripts/manage_lessons.sh list

# Search for specific topics
sudo /opt/container-farm-control/scripts/manage_lessons.sh list --search "hydroponics"
```

### Using Voice Control

```bash
# Start interactive voice control simulator
sudo /opt/container-farm-control/scripts/voice_control.sh

# Test specific command
sudo /opt/container-farm-control/scripts/voice_control.sh --text "turn on the lights"

# Try microphone input (if dependencies installed)
sudo /opt/container-farm-control/scripts/voice_control.sh --listen
```

### Generating Reports

```bash
# Generate basic report
sudo /opt/container-farm-control/scripts/generate_report.sh --basic

# Generate education-focused report
sudo /opt/container-farm-control/scripts/generate_report.sh --educational

# Generate custom report (interactive)
sudo /opt/container-farm-control/scripts/generate_report.sh --custom
```

### Setting Up Hardware Kits

```bash
# Run hardware kit wizard
sudo /opt/container-farm-control/scripts/kit_setup_wizard.sh

# List available kits
sudo python3 /opt/container-farm-control/scripts/apply_pin_map.py --list

# Scan QR code from kit
sudo python3 /opt/container-farm-control/scripts/scan_kit_qr.py --scan
```

## Directory Structure

```
/opt/container-farm-control/
├── configs/              # System configuration files
├── scripts/              # System scripts
├── docs/                 # Documentation
│   ├── lesson_plans/     # Curriculum materials
│   └── therapy_resources/# Therapeutic resources
├── logs/                 # System and activity logs
│   └── student_logs/     # Student activity logs
├── dashboards/           # Dashboard configurations
├── backups/              # System backups
├── i18n/                 # Language files
├── reports/              # Generated reports
├── photo_log/            # Growth documentation photos
├── hardware_kits/        # Hardware kit definitions
└── voice_control/        # Voice control resources
```

## Customization

The Container Farm Control System is designed to be customizable for different use cases:

### For Educators
- Configure grade-appropriate dashboards
- Import curriculum materials
- Set up student tracking
- Align with educational standards

### For Therapists
- Enable accessibility features
- Configure therapeutic goal tracking
- Customize sensory experiences
- Set up participant dashboards

### For Researchers
- Enable advanced data logging
- Configure experimental controls
- Set up data export pipelines
- Integrate with analysis tools

### For Community Gardens
- Configure multi-user access
- Set up community dashboards
- Integrate with food security metrics
- Enable participant logging

## Contributing

Contributions to the Container Farm Control System are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin new-feature`
5. Submit a pull request

## License

This project uses a dual-license model. Code is licensed under the MIT License and documentation is licensed under CC BY-SA 4.0. See license.md for details.

## Acknowledgments

- The original Farmhand.ag team for inspiration
- The agricultural education community
- Horticultural therapy practitioners
- The open-source community for their incredible tools and libraries

## Contact

For questions, support, or collaboration, please contact:
- Project Lead: [Your Name]
- Email: [Your Email]
- Website: [Your Website]
