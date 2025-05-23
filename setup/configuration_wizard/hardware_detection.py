#!/bin/bash
# Container Farm Control System - Integration Script
# This script installs and integrates all the new features into the main setup wizard
# Run this to update your existing setup with all the new enhancements

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Base directories
INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"
DOCS_DIR="${INSTALL_DIR}/docs"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo)${NC}"
  exit 1
fi

# Display welcome banner
clear
echo -e "${BLUE}${BOLD}"
echo "============================================================"
echo "     Container Farm Control System - Feature Integration    "
echo "============================================================"
echo -e "${NC}"
echo -e "This script will install and integrate all new features:"
echo -e "- Student Activity Logger"
echo -e "- Multilingual Support"
echo -e "- Offline Curriculum Binder"
echo -e "- Voice UI Placeholder"
echo -e "- Stakeholder Report Generator"
echo -e "- Hardware Kit Support"
echo -e "${YELLOW}This will update your existing setup_wizard.sh and add new scripts.${NC}"
echo

# Confirm before proceeding
read -p "Continue with integration? (y/n): " do_continue
if [[ "$do_continue" != "y" && "$do_continue" != "Y" ]]; then
  echo -e "${YELLOW}Integration cancelled.${NC}"
  exit 0
fi

# Backup existing setup wizard
SETUP_WIZARD="${SCRIPTS_DIR}/setup_wizard.sh"
if [ -f "$SETUP_WIZARD" ]; then
  BACKUP_FILE="${SCRIPTS_DIR}/setup_wizard.sh.bak.$(date +%Y%m%d_%H%M%S)"
  echo -e "${YELLOW}Creating backup of existing setup wizard...${NC}"
  cp "$SETUP_WIZARD" "$BACKUP_FILE"
  echo -e "${GREEN}Backup created: $BACKUP_FILE${NC}"
fi

# Install required packages
echo -e "\n${YELLOW}Installing required packages...${NC}"
apt update
apt install -y python3-pip qrencode imagemagick jq zip unzip python3-pil
pip3 install qrcode pillow

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p "${INSTALL_DIR}/logs/student_logs"
mkdir -p "${INSTALL_DIR}/i18n"
mkdir -p "${INSTALL_DIR}/reports"
mkdir -p "${INSTALL_DIR}/voice_control"
mkdir -p "${INSTALL_DIR}/hardware_kits"

# Copy all the new scripts
echo -e "\n${YELLOW}Installing new scripts...${NC}"

# 1. Student Activity Logger
cat > "${SCRIPTS_DIR}/student_activity.sh" << 'EOF'
#!/bin/bash
# Simple wrapper script for the student activity logger

# Pass all arguments to the Python script
python3 /opt/container-farm-control/scripts/log_activity.py "$@"
EOF
chmod +x "${SCRIPTS_DIR}/student_activity.sh"

# 2. Language switcher wrapper
cat > "${SCRIPTS_DIR}/change_language.sh" << 'EOF'
#!/bin/bash
# Simple wrapper script for language switching

# Pass all arguments to the switch language script
/opt/container-farm-control/scripts/switch_language.sh "$@"
EOF
chmod +x "${SCRIPTS_DIR}/change_language.sh"

# 3. Lesson plan manager wrapper
cat > "${SCRIPTS_DIR}/manage_lessons.sh" << 'EOF'
#!/bin/bash
# Simple wrapper script for the lesson plan manager

# Pass all arguments to the Python script
python3 /opt/container-farm-control/scripts/lesson_manager.py "$@"
EOF
chmod +x "${SCRIPTS_DIR}/manage_lessons.sh"

# 4. Voice control wrapper
cat > "${SCRIPTS_DIR}/voice_control.sh" << 'EOF'
#!/bin/bash
# Simple wrapper script for voice control

# Pass all arguments to the Python script
python3 /opt/container-farm-control/scripts/voice_interface.py "$@"
EOF
chmod +x "${SCRIPTS_DIR}/voice_control.sh"

# 5. Report generator wrapper
cat > "${SCRIPTS_DIR}/generate_report.sh" << 'EOF'
#!/bin/bash
# Simple wrapper script for the stakeholder report generator

# Pass all arguments to the Python script
python3 /opt/container-farm-control/scripts/generate_report.py "$@"
EOF
chmod +x "${SCRIPTS_DIR}/generate_report.sh"

# Create post-installation hook in the main setup_wizard.sh
echo -e "\n${YELLOW}Adding new features to main setup wizard...${NC}"

# Create the hook code to inject
HOOK_CODE=$(cat << 'EOT'

# STEP 12: Additional Features Menu (ENHANCED)
clear
echo -e "${BLUE}${BOLD}STEP 12: Additional Features${NC}"
echo
echo -e "Your Container Farm system supports several additional features"
echo -e "you can enable based on your needs."
echo

FEATURES_TO_ENABLE=()

# Student Activity Logger
if [ "$goal_name" == "educational" ] || [ "$user_role" == "educator" ]; then
  echo -e "${CYAN}Student Activity Logger:${NC}"
  echo -e "Track student interactions with the system for educational assessment."
  read -p "Enable Student Activity Logger? (y/n): " enable_feature
  if [[ "$enable_feature" == "y" || "$enable_feature" == "Y" ]]; then
    FEATURES_TO_ENABLE+=("student_activity_logger")
    echo "enabled" > "${CONFIG_DIR}/student_logger.txt"
    echo -e "${GREEN}Student Activity Logger will be enabled.${NC}"
  fi
  echo
fi

# Multilingual Support
echo -e "${CYAN}Multilingual Support:${NC}"
echo -e "Support for multiple languages in the user interface."
echo -e "Currently supported: English, Spanish, French"
read -p "Enable Multilingual Support? (y/n): " enable_feature
if [[ "$enable_feature" == "y" || "$enable_feature" == "Y" ]]; then
  FEATURES_TO_ENABLE+=("multilingual_support")
  
  # Ask for default language
  echo -e "\nSelect default language:"
  echo -e "1) English (en)"
  echo -e "2) Spanish (es)"
  echo -e "3) French (fr)"
  read -p "Select language [1-3, default=1]: " lang_choice
  
  case $lang_choice in
    2) echo "es" > "${CONFIG_DIR}/language.txt" ;;
    3) echo "fr" > "${CONFIG_DIR}/language.txt" ;;
    *) echo "en" > "${CONFIG_DIR}/language.txt" ;;
  esac
  
  echo -e "${GREEN}Multilingual Support will be enabled.${NC}"
fi
echo

# Curriculum Binder
if [ "$goal_name" == "educational" ] || [ "$user_role" == "educator" ] || [ "$user_role" == "therapist" ] || [ "$user_role" == "agritherapist" ]; then
  echo -e "${CYAN}Offline Curriculum Binder:${NC}"
  echo -e "Organize and manage lesson plans and curriculum materials."
  read -p "Enable Curriculum Binder? (y/n): " enable_feature
  if [[ "$enable_feature" == "y" || "$enable_feature" == "Y" ]]; then
    FEATURES_TO_ENABLE+=("curriculum_binder")
    echo "enabled" > "${CONFIG_DIR}/curriculum_binder.txt"
    echo -e "${GREEN}Curriculum Binder will be enabled.${NC}"
  fi
  echo
fi

# Voice Control
echo -e "${CYAN}Voice Control Preparation:${NC}"
echo -e "Prepare for future voice control capabilities (placeholder)."
read -p "Enable Voice Control Preparation? (y/n): " enable_feature
if [[ "$enable_feature" == "y" || "$enable_feature" == "Y" ]]; then
  FEATURES_TO_ENABLE+=("voice_control")
  echo "enabled" > "${CONFIG_DIR}/voice_control.txt"
  echo -e "${GREEN}Voice Control Preparation will be enabled.${NC}"
fi
echo

# Stakeholder Reporting
echo -e "${CYAN}Stakeholder Report Generator:${NC}"
echo -e "Generate professional reports for stakeholders with project data."
read -p "Enable Stakeholder Report Generator? (y/n): " enable_feature
if [[ "$enable_feature" == "y" || "$enable_feature" == "Y" ]]; then
  FEATURES_TO_ENABLE+=("stakeholder_reports")
  echo "enabled" > "${CONFIG_DIR}/stakeholder_reports.txt"
  echo -e "${GREEN}Stakeholder Report Generator will be enabled.${NC}"
fi
echo

# Hardware Kit Support
echo -e "${CYAN}Hardware Kit Support:${NC}"
echo -e "Support for pre-configured hardware kits with automatic setup."
read -p "Enable Hardware Kit Support? (y/n): " enable_feature
if [[ "$enable_feature" == "y" || "$enable_feature" == "Y" ]]; then
  FEATURES_TO_ENABLE+=("hardware_kits")
  echo "enabled" > "${CONFIG_DIR}/hardware_kits.txt"
  echo -e "${GREEN}Hardware Kit Support will be enabled.${NC}"
  
  # Ask about using a pre-wired kit
  echo -e "\nAre you using a pre-wired hardware kit? (y/n): " using_kit
  read -p "Using a pre-wired kit? (y/n): " using_kit
  if [[ "$using_kit" == "y" || "$using_kit" == "Y" ]]; then
    echo "kit" > "${CONFIG_DIR}/setup_mode.txt"
    echo -e "${YELLOW}After setup is complete, run:${NC}"
    echo -e "${CYAN}sudo ${SCRIPTS_DIR}/kit_setup_wizard.sh${NC}"
  fi
fi
echo

# Install selected features
if [ ${#FEATURES_TO_ENABLE[@]} -gt 0 ]; then
  echo -e "${YELLOW}Installing selected features...${NC}"
  
  for feature in "${FEATURES_TO_ENABLE[@]}"; do
    case $feature in
      student_activity_logger)
        echo -e "- Setting up Student Activity Logger..."
        mkdir -p "${INSTALL_DIR}/logs/student_logs"
        ;;
      multilingual_support)
        echo -e "- Setting up Multilingual Support..."
        mkdir -p "${INSTALL_DIR}/i18n"
        ;;
      curriculum_binder)
        echo -e "- Setting up Curriculum Binder..."
        mkdir -p "${DOCS_DIR}/lesson_plans"
        ;;
      voice_control)
        echo -e "- Setting up Voice Control Preparation..."
        mkdir -p "${INSTALL_DIR}/voice_control"
        ;;
      stakeholder_reports)
        echo -e "- Setting up Stakeholder Report Generator..."
        mkdir -p "${INSTALL_DIR}/reports"
        ;;
      hardware_kits)
        echo -e "- Setting up Hardware Kit Support..."
        mkdir -p "${INSTALL_DIR}/hardware_kits"
        ;;
    esac
  done
  
  echo -e "\n${GREEN}Selected features installed successfully.${NC}"
else
  echo -e "${YELLOW}No additional features selected.${NC}"
fi

echo
read -p "Press Enter to continue..." dummy

EOT
)

# Function to modify the setup_wizard.sh file
modify_setup_wizard() {
  # Check if setup_wizard.sh exists
  if [ ! -f "$SETUP_WIZARD" ]; then
    echo -e "${RED}Error: setup_wizard.sh not found at $SETUP_WIZARD${NC}"
    return 1
  }
  
  # Check if the hook has already been added
  if grep -q "STEP 12: Additional Features Menu (ENHANCED)" "$SETUP_WIZARD"; then
    echo -e "${YELLOW}Additional features menu already present in setup_wizard.sh.${NC}"
    return 0
  }
  
  # Find where to insert the hook (after STEP 11)
  if grep -q "STEP 11: .*System Configuration" "$SETUP_WIZARD"; then
    # Create a temporary file
    TEMP_FILE=$(mktemp)
    
    # Insert the hook after STEP 11 section
    awk -v hook="$HOOK_CODE" '
      /STEP 11: .*System Configuration/ {
        print $0
        flag = 1
        next
      }
      flag && /^echo/ && /Reboot/ {
        print hook
        flag = 0
      }
      { print $0 }
    ' "$SETUP_WIZARD" > "$TEMP_FILE"
    
    # Replace the original file
    mv "$TEMP_FILE" "$SETUP_WIZARD"
    chmod +x "$SETUP_WIZARD"
    
    echo -e "${GREEN}Additional features menu added to setup_wizard.sh${NC}"
    return 0
  else
    echo -e "${RED}Error: Could not find insertion point in setup_wizard.sh${NC}"
    return 1
  fi
}

# Apply the modification
modify_setup_wizard

# Create integration documentation file
cat > "${DOCS_DIR}/new_features.md" << 'EOF'
# Container Farm Control System - New Features

This document describes the new features that have been added to the Container Farm Control System. These features enhance the system's capabilities for educational use, therapeutic applications, and general usability.

## Student Activity Logger

The Student Activity Logger tracks student interactions with the Container Farm, creating a record of their activities for educational assessment.

### Usage

```bash
# Log a student activity
sudo /opt/container-farm-control/scripts/student_activity.sh "Student Name" "Action" "Details"

# View logged activities
cat /opt/container-farm-control/logs/student_logs/all_activities.txt

# View a specific student's activities
cat /opt/container-farm-control/logs/student_logs/student_name.txt
```

## Multilingual Support

Multilingual Support allows the Container Farm to present information in multiple languages, making it accessible to diverse user groups.

### Usage

```bash
# Change the system language
sudo /opt/container-farm-control/scripts/change_language.sh es  # For Spanish
sudo /opt/container-farm-control/scripts/change_language.sh en  # For English
sudo /opt/container-farm-control/scripts/change_language.sh fr  # For French

# List available languages
sudo /opt/container-farm-control/scripts/change_language.sh
```

## Offline Curriculum Binder

The Curriculum Binder organizes and manages lesson plans and educational materials for use with the Container Farm.

### Usage

```bash
# Import a lesson plan
sudo /opt/container-farm-control/scripts/manage_lessons.sh import /path/to/lesson.pdf

# List available lessons
sudo /opt/container-farm-control/scripts/manage_lessons.sh list

# Search for lessons by keyword
sudo /opt/container-farm-control/scripts/manage_lessons.sh list --search "hydroponics"

# Filter lessons by grade level
sudo /opt/container-farm-control/scripts/manage_lessons.sh list --grade elementary

# Import all lessons from a directory
sudo /opt/container-farm-control/scripts/manage_lessons.sh batch /path/to/lessons
```

## Voice Control Placeholder

The Voice Control Placeholder simulates future voice control capabilities for the Container Farm.

### Usage

```bash
# Start interactive voice control simulator
sudo /opt/container-farm-control/scripts/voice_control.sh

# Process a specific command
sudo /opt/container-farm-control/scripts/voice_control.sh --text "turn on the lights"

# Try listening mode (if dependencies are installed)
sudo /opt/container-farm-control/scripts/voice_control.sh --listen
```

## Stakeholder Report Generator

The Stakeholder Report Generator creates professional reports for stakeholders with project information, growth data, and impact metrics.

### Usage

```bash
# Generate a basic report
sudo /opt/container-farm-control/scripts/generate_report.sh --basic

# Generate an education-focused report
sudo /opt/container-farm-control/scripts/generate_report.sh --educational

# Generate a therapy-focused report
sudo /opt/container-farm-control/scripts/generate_report.sh --therapy

# Generate a custom report interactively
sudo /opt/container-farm-control/scripts/generate_report.sh --custom
```

## Hardware Kit Support

Hardware Kit Support allows for rapid deployment of pre-configured hardware kits with automatic setup.

### Usage

```bash
# Run the hardware kit setup wizard
sudo /opt/container-farm-control/scripts/kit_setup_wizard.sh

# List available hardware kits
sudo python3 /opt/container-farm-control/scripts/apply_pin_map.py --list

# Apply a specific kit configuration
sudo python3 /opt/container-farm-control/scripts/apply_pin_map.py --apply kit_id

# Generate QR codes for hardware kits
sudo python3 /opt/container-farm-control/scripts/generate_kit_qr.py --all
```

## Integration with Setup Wizard

All these features are integrated into the main setup wizard. When running the setup wizard, you will be presented with an additional "Features" step where you can enable or disable each feature.

To run the setup wizard:

```bash
sudo /opt/container-farm-control/scripts/setup_wizard.sh
```

## Feature Status

You can check the status of each feature by examining the configuration files:

```bash
cat /opt/container-farm-control/configs/student_logger.txt
cat /opt/container-farm-control/configs/language.txt
cat /opt/container-farm-control/configs/curriculum_binder.txt
cat /opt/container-farm-control/configs/voice_control.txt
cat /opt/container-farm-control/configs/stakeholder_reports.txt
cat /opt/container-farm-control/configs/hardware_kits.txt
```

## Additional Documentation

Each feature has its own detailed documentation:

- Student Activity Logger: `/opt/container-farm-control/docs/student_activity_logger.md`
- Multilingual Support: `/opt/container-farm-control/docs/multilingual_support.md`
- Curriculum Binder: `/opt/container-farm-control/docs/lesson_plans/index.md`
- Voice Control: `/opt/container-farm-control/docs/voice_control.md`
- Stakeholder Reports: `/opt/container-farm-control/docs/stakeholder_reports.md`
- Hardware Kits: `/opt/container-farm-control/hardware_kits/README.md`
EOF

# Create a master documentation index
cat > "${DOCS_DIR}/index.md" << 'EOF'
# Container Farm Control System Documentation

Welcome to the Container Farm Control System documentation. This system is designed to provide autonomous control for container farming environments, with special features for educational, therapeutic, and research applications.

## Core Documentation

- [Project Overview](about_project.txt)
- [System Summary](project_summary.txt)
- [New Features Guide](new_features.md)

## User Guides

- [Getting Started Guide](getting_started.md)
- [Dashboard User Guide](dashboard_guide.md)
- [Maintenance Guide](maintenance_guide.md)

## Feature-Specific Documentation

- [Student Activity Logger](student_activity_logger.md)
- [Multilingual Support](multilingual_support.md)
- [Curriculum Binder](lesson_plans/index.md)
- [Voice Control](voice_control.md)
- [Stakeholder Reports](stakeholder_reports.md)
- [Hardware Kits](../hardware_kits/README.md)

## Role-Specific Documentation

### For Educators
- [Classroom Integration Guide](educational/classroom_integration.md)
- [Student Assessment Guide](educational/student_assessment.md)
- [Curriculum Alignment](educational/curriculum_alignment.md)

### For Therapists
- [Therapeutic Application Guide](therapy/therapeutic_applications.md)
- [Accessibility Guide](therapy/accessibility_guide.md)
- [Session Planning Guide](therapy/session_planning.md)

### For Researchers
- [Data Collection Guide](research/data_collection.md)
- [Experimental Design](research/experimental_design.md)
- [API Documentation](research/api_documentation.md)

### For Community Gardens
- [Community Engagement Guide](community/engagement_guide.md)
- [Food Security Applications](community/food_security.md)
- [Multi-User Management](community/multi_user_management.md)

## Technical Documentation

- [System Architecture](technical/architecture.md)
- [Sensor Configuration](technical/sensor_configuration.md)
- [Network Configuration](technical/network_configuration.md)
- [Backup and Recovery](technical/backup_recovery.md)
- [Troubleshooting Guide](technical/troubleshooting.md)

## Support and Community

- [GitHub Repository](#) <!-- Add your GitHub repository URL here -->
- [Community Forum](#) <!-- Add your community forum URL here -->
- [Report Issues](#) <!-- Add your issue tracker URL here -->
- [Contribute](#) <!-- Add your contribution guidelines URL here -->
EOF

# Final output
echo -e "\n${GREEN}${BOLD}Integration completed successfully!${NC}"
echo -e "\nNew features added to Container Farm Control System:"
echo -e "- Student Activity Logger"
echo -e "- Multilingual Support"
echo -e "- Offline Curriculum Binder"
echo -e "- Voice UI Placeholder"
echo -e "- Stakeholder Report Generator"
echo -e "- Hardware Kit Support"
echo
echo -e "${YELLOW}Documentation:${NC}"
echo -e "- ${DOCS_DIR}/new_features.md - Overview of all new features"
echo -e "- ${DOCS_DIR}/index.md - Main documentation index"
echo
echo -e "${YELLOW}To apply these features to an existing installation, run:${NC}"
echo -e "${CYAN}sudo ${SCRIPTS_DIR}/setup_wizard.sh${NC}"
echo -e "And proceed to Step 12: Additional Features"
echo
echo -e "${GREEN}Thank you for using Container Farm Control System!${NC}"
echo
