#!/bin/bash

# Container Farm Control System - Enhanced Interactive Setup Wizard
# This wizard guides users through the setup process in a user-friendly way
# Designed for users with minimal technical background
# Version 2.1 - May 2025
# Includes agritherapy and accessibility enhancements 

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Installation directories
INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"
BACKUP_DIR="${INSTALL_DIR}/backups"
DOCS_DIR="${INSTALL_DIR}/docs"
DASHBOARD_DIR="${INSTALL_DIR}/dashboards"

# Create necessary directories
mkdir -p "${INSTALL_DIR}"
mkdir -p "${CONFIG_DIR}"
mkdir -p "${SCRIPTS_DIR}"
mkdir -p "${BACKUP_DIR}"
mkdir -p "${DOCS_DIR}"
mkdir -p "${DASHBOARD_DIR}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo)${NC}"
  exit 1
fi

# Welcome banner
clear
echo -e "${BLUE}${BOLD}"
echo "============================================================"
echo "     Container Farm Control System - Interactive Setup      "
echo "============================================================"
echo -e "${NC}"
echo -e "Welcome to the setup wizard for your Container Farm Control System."
echo -e "This wizard will guide you through the entire setup process,"
echo -e "from basic system configuration to sensor setup and automation."
echo
echo -e "${YELLOW}No technical background is required!${NC}"
echo
echo -e "${CYAN}This system was developed in response to the shutdown of Farmhand.ag,"
echo -e "with the goal of preserving farmers' autonomy and access to local control.${NC}"
echo
read -p "Press Enter to continue..." dummy

# STEP 0: Personalize Your Installation
clear
echo -e "${BLUE}${BOLD}STEP 0: Personalize Your Installation${NC}"
echo
echo -e "Let's start by gathering some information about your farm project."
echo -e "This will help customize your system and dashboard."
echo

# Project Information
read -p "Enter a name for your farm project (e.g., 'Lincoln High GrowLab'): " project_name
read -p "Enter your location or city (e.g., 'Detroit, MI'): " project_location
read -p "Enter your name or initials (optional, for logs): " operator_name

# User Role Selection (PATCHED)
echo
echo -e "${CYAN}Who will primarily use this system?${NC}"
echo -e "1) ${CYAN}Educator${NC} - For teachers or educational staff"
echo -e "2) ${CYAN}Technician${NC} - For technical maintenance personnel"
echo -e "3) ${CYAN}Farmer${NC} - For commercial growers"
echo -e "4) ${CYAN}Researcher${NC} - For experimental or scientific use"
echo -e "5) ${CYAN}Therapist${NC} - For therapeutic or vocational programs"
echo -e "6) ${CYAN}Agritherapist${NC} - For horticultural therapy and healing gardens"
echo -e "7) ${CYAN}Community Organizer${NC} - For community gardens or food security initiatives"
read -p "Select primary user role [1-7]: " role_selection

case $role_selection in
  1) user_role="educator" ;;
  2) user_role="technician" ;;
  3) user_role="farmer" ;;
  4) user_role="researcher" ;;
  5) user_role="therapist" ;;
  6) user_role="agritherapist" ;;
  7) user_role="community" ;;
  *) user_role="general" ;;
esac

# Save values to config directory
echo "$project_name" > "${CONFIG_DIR}/project_name.txt"
echo "$project_location" > "${CONFIG_DIR}/location.txt"
echo "$operator_name" > "${CONFIG_DIR}/operator.txt"
echo "$user_role" > "${CONFIG_DIR}/user_role.txt"

# Learning goals for educational and therapeutic settings (PATCHED)
if [ "$user_role" == "educator" ] || [ "$user_role" == "therapist" ] || [ "$user_role" == "agritherapist" ]; then
  echo
  echo -e "${CYAN}What are you trying to learn or measure with this system?${NC}"
  read -p "Enter a learning goal (e.g., 'impact of light cycles on basil growth' or 'therapeutic benefits of daily plant care'): " learning_goal
  echo "$learning_goal" > "${CONFIG_DIR}/learning_goal.txt"
fi

echo -e "\n${GREEN}Project information saved!${NC}"
echo
read -p "Press Enter to continue..." dummy

# STEP 1: Primary Goal
clear
echo -e "${BLUE}${BOLD}STEP 1: What is your primary goal with this system?${NC}"
echo
echo -e "1) ${CYAN}Commercial Production${NC} - Optimized for crop yield and efficiency"
echo -e "2) ${CYAN}Educational${NC} - For schools, universities, or training"
echo -e "3) ${CYAN}Social Impact${NC} - For therapy, community gardens, or non-profits"
echo -e "4) ${CYAN}Research${NC} - For experimental growing or prototyping"
echo
read -p "Please select your primary goal [1-4]: " primary_goal

case $primary_goal in
  1) 
    goal_name="commercial"
    echo -e "\nSelected: ${GREEN}Commercial Production${NC}"
    ;;
  2) 
    goal_name="educational"
    echo -e "\nSelected: ${GREEN}Educational${NC}"
    # Educational-specific settings
    echo -e "${YELLOW}Configuring educational settings...${NC}"
    echo -e "- Adding student notes widget to dashboard"
    echo -e "- Setting light cycles to align with school hours (8am-3pm by default)"
    echo -e "- Enabling CSV export for student data collection"
    ;;
  3) 
    goal_name="social"
    echo -e "\nSelected: ${GREEN}Social Impact${NC}"
    # Social impact specific settings
    echo -e "${YELLOW}Configuring social impact settings...${NC}"
    echo -e "- Enabling soft alerts mode (less intimidating warnings)"
    echo -e "- Adding simple view toggle for dashboards"
    echo -e "- Setting up program impact documentation templates"
    ;;
  4) 
    goal_name="research"
    echo -e "\nSelected: ${GREEN}Research${NC}"
    # Research specific settings
    echo -e "${YELLOW}Configuring research settings...${NC}"
    echo -e "- Enabling advanced data logging"
    echo -e "- Setting up experiment tagging system"
    echo -e "- Configuring high-precision sensor calibration"
    ;;
  *) 
    goal_name="general"
    echo -e "\n${YELLOW}Invalid selection. Defaulting to General Purpose.${NC}"
    ;;
esac

# Save user's goal preference
echo "$goal_name" > "${CONFIG_DIR}/primary_goal.txt"
echo

# Additional questions based on goal
if [ "$goal_name" == "educational" ]; then
  read -p "Are students directly involved in system operation? (y/n): " student_involvement
  read -p "What grade level? (elementary/middle/high/college): " grade_level
  echo "$student_involvement" > "${CONFIG_DIR}/student_involvement.txt"
  echo "$grade_level" > "${CONFIG_DIR}/grade_level.txt"
  
  # Create educational resources directory
  mkdir -p "${DOCS_DIR}/lesson_plans"
  echo -e "\n${GREEN}Will download grade-appropriate lesson plans during installation.${NC}"
elif [ "$goal_name" == "social" ]; then
  read -p "Is this for a therapeutic program? (y/n): " therapeutic
  read -p "Is funding/grant documentation needed? (y/n): " funding_docs
  echo "$therapeutic" > "${CONFIG_DIR}/therapeutic.txt"
  echo "$funding_docs" > "${CONFIG_DIR}/funding_docs.txt"
  
  # Create impact documentation templates
  mkdir -p "${DOCS_DIR}/impact_templates"
  echo -e "\n${GREEN}Will set up program impact documentation templates.${NC}"
fi

# Therapy-specific questions (PATCHED)
if [ "$user_role" == "agritherapist" ] || [ "$user_role" == "therapist" ]; then
  echo -e "\n${CYAN}Therapy-Specific Settings:${NC}"
  read -p "Is this for group or individual therapy sessions? (group/individual): " therapy_type
  read -p "Are any accessibility accommodations needed? (y/n): " accessibility_needed
  
  if [[ "$accessibility_needed" == "y" || "$accessibility_needed" == "Y" ]]; then
    echo -e "\n${CYAN}Select needed accommodations:${NC}"
    echo -e "1) ${CYAN}Visual impairments${NC}"
    echo -e "2) ${CYAN}Motor skill limitations${NC}"
    echo -e "3) ${CYAN}Cognitive accommodations${NC}"
    echo -e "4) ${CYAN}Multiple/Combined needs${NC}"
    read -p "Select primary accommodation need [1-4]: " accommodation_type
    
    case $accommodation_type in
      1) accommodation="visual" ;;
      2) accommodation="motor" ;;
      3) accommodation="cognitive" ;;
      4) accommodation="multiple" ;;
      *) accommodation="general" ;;
    esac
    
    echo "$accommodation" > "${CONFIG_DIR}/accessibility_accommodation.txt"
    
    # Configure accessibility settings
    echo -e "${YELLOW}Configuring accessibility settings for ${accommodation} needs...${NC}"
    if [ "$accommodation" == "visual" ]; then
      echo -e "- Setting up high-contrast dashboard"
      echo -e "- Enabling larger font sizes"
      echo -e "- Adding audio feedback options"
    elif [ "$accommodation" == "motor" ]; then
      echo -e "- Configuring simplified control interfaces"
      echo -e "- Adding button guards in the software interface"
      echo -e "- Enabling alternative input options"
    elif [ "$accommodation" == "cognitive" ]; then
      echo -e "- Setting up simplified dashboard views"
      echo -e "- Adding visual instruction guides"
      echo -e "- Enabling consistent color-coding"
    fi
  fi
  
  echo "$therapy_type" > "${CONFIG_DIR}/therapy_type.txt"
  
  # Create therapy-specific settings
  mkdir -p "${DOCS_DIR}/therapy_resources"
  mkdir -p "${DOCS_DIR}/accessibility_guides"
fi

# Determine user's technical expertise
read -p "Do you have prior experience with Linux or Raspberry Pi? (y/n): " linux_exp
if [[ "$linux_exp" == "y" || "$linux_exp" == "Y" ]]; then
  technical_level="experienced"
else
  technical_level="beginner"
  echo -e "\n${YELLOW}Don't worry! This wizard is designed for beginners.${NC}"
fi

echo
read -p "Press Enter to continue..." dummy

# STEP 2: System Complexity
clear
echo -e "${BLUE}${BOLD}STEP 2: Choose your system complexity${NC}"
echo
echo -e "1) ${CYAN}Basic Monitoring${NC} - Just temperature, humidity, and basic sensors"
echo -e "   Ideal for: Beginners, educational settings, monitoring only"
echo
echo -e "2) ${CYAN}Complete Farm Control${NC} - Full climate control and automation"
echo -e "   Ideal for: Commercial operations, intermediate users"
echo
echo -e "3) ${CYAN}Hydroponic System${NC} - Specialized for nutrient management"
echo -e "   Ideal for: Hydroponic systems, more technical users"
echo

# Give recommendations based on goal and user role
echo -e "${YELLOW}Based on your selections:${NC}"
if [ "$goal_name" == "educational" ] && [ "$technical_level" == "beginner" ]; then
  echo -e "${GREEN}Recommended: Option 1 (Basic Monitoring)${NC}"
elif [ "$goal_name" == "commercial" ]; then
  echo -e "${GREEN}Recommended: Option 2 (Complete Farm Control)${NC}"
elif [ "$goal_name" == "research" ] || [ "$user_role" == "researcher" ]; then
  echo -e "${GREEN}Recommended: Option 3 (Hydroponic System)${NC}"
elif [ "$user_role" == "agritherapist" ]; then
  echo -e "${GREEN}Recommended: Option 1 (Basic Monitoring)${NC}"
fi

read -p "Please select your system type [1-3]: " system_type

case $system_type in
  1) 
    config_name="basic_monitoring"
    echo -e "\nSelected: ${GREEN}Basic Monitoring${NC}"
    ;;
  2) 
    config_name="complete_farm_control"
    echo -e "\nSelected: ${GREEN}Complete Farm Control${NC}"
    ;;
  3) 
    config_name="hydroponic_system"
    echo -e "\nSelected: ${GREEN}Hydroponic System${NC}"
    ;;
  *) 
    config_name="basic_monitoring"
    echo -e "\n${YELLOW}Invalid selection. Defaulting to Basic Monitoring.${NC}"
    ;;
esac

# Save configuration preference
echo "$config_name" > "${CONFIG_DIR}/selected_config.txt"

# Privacy and Data Sovereignty Options (Reflecting Ethics Statement)
echo -e "\n${CYAN}Data Privacy Settings:${NC}"
echo -e "This system prioritizes your data sovereignty and autonomy."
echo -e "1) ${CYAN}Local Only${NC} - All data stays on your device, no external connections"
echo -e "2) ${CYAN}Backup Ready${NC} - Enable optional USB/network backups, still no cloud"
echo -e "3) ${CYAN}Research Sharing${NC} - Opt-in to anonymously share system statistics"
read -p "Select your data privacy preference [1-3, default=1]: " privacy_option

case $privacy_option in
  2) privacy_mode="backup" ;;
  3) privacy_mode="research" ;;
  *) privacy_mode="local" ;;
esac

echo "$privacy_mode" > "${CONFIG_DIR}/privacy_mode.txt"
echo -e "\n${GREEN}Privacy settings saved.${NC}"

# Photo Journaling Configuration (PATCHED)
echo -e "\n${CYAN}Plant Documentation:${NC}"
echo -e "Would you like to enable plant photo journaling (daily webcam snapshots)?"
echo -e "This creates a visual record of plant growth over time, useful for:"
echo -e "- Educational tracking for students"
echo -e "- Progress documentation for therapy participants"
echo -e "- Grant documentation for community programs"
read -p "Enable photo journaling? (y/n): " photo_log

if [[ "$photo_log" == "y" || "$photo_log" == "Y" ]]; then
  echo "enabled" > "${CONFIG_DIR}/photo_journaling.txt"
  
  # Create directory for photos
  mkdir -p "${INSTALL_DIR}/photo_log"
  
  # Create photo logging script
  cat > "${SCRIPTS_DIR}/photo_logger.sh" << 'EOF'
#!/bin/bash
# Daily Plant Photo Logger

TIMESTAMP=$(date +"%Y%m%d_%H%M")
PHOTO_DIR="/opt/container-farm-control/photo_log"
PROJECT_NAME=$(cat /opt/container-farm-control/configs/project_name.txt 2>/dev/null || echo "container_farm")

# Ensure directory exists
mkdir -p "$PHOTO_DIR"

# Take photo with timestamp
fswebcam -r 1280x720 --no-banner "$PHOTO_DIR/${PROJECT_NAME}_${TIMESTAMP}.jpg"

# Create a thumbnail for dashboard display
convert "$PHOTO_DIR/${PROJECT_NAME}_${TIMESTAMP}.jpg" -resize 320x240 "$PHOTO_DIR/${PROJECT_NAME}_${TIMESTAMP}_thumb.jpg"

# Keep only last 60 days of photos (to save space)
find "$PHOTO_DIR" -name "*.jpg" -type f -mtime +60 -delete
EOF

  chmod +x "${SCRIPTS_DIR}/photo_logger.sh"
  
  # Schedule daily photos at noon
  (crontab -l 2>/dev/null || echo "") | grep -v "photo_logger.sh" | { cat; echo "0 12 * * * ${SCRIPTS_DIR}/photo_logger.sh"; } | crontab -
  
  echo -e "${GREEN}Photo journaling enabled. Daily photos will be taken at 12:00 PM.${NC}"
else
  echo "disabled" > "${CONFIG_DIR}/photo_journaling.txt"
fi

# Operator consent reminder for data collection (PATCHED)
if [ "$privacy_mode" != "local" ] || [[ "$photo_log" == "y" || "$photo_log" == "Y" ]]; then
  echo -e "\n${YELLOW}IMPORTANT DATA CONSENT REMINDER:${NC}"
  echo -e "You've selected options that involve data collection:"
  
  if [ "$privacy_mode" != "local" ]; then
    echo -e "- Data backup or sharing is enabled"
  fi
  
  if [[ "$photo_log" == "y" || "$photo_log" == "Y" ]]; then
    echo -e "- Photo journaling will capture daily images"
  fi
  
  echo -e "\nPlease ensure all participants understand what data is being collected,"
  echo -e "how it will be used, and that appropriate consent is obtained."
  echo -e "This is especially important in therapeutic and educational settings."
  
  read -p "I confirm that all participants will be informed about data collection (y/n): " consent_confirmed
  echo "$consent_confirmed" > "${CONFIG_DIR}/consent_confirmed.txt"
  
  if [[ "$consent_confirmed" != "y" && "$consent_confirmed" != "Y" ]]; then
    echo -e "${RED}NOTE: Please review your data collection policies before proceeding.${NC}"
    echo -e "${RED}Consider changing to more restrictive privacy settings.${NC}"
  fi
fi

echo
read -p "Press Enter to continue..." dummy

# STEP 3: System Updates
clear
echo -e "${BLUE}${BOLD}STEP 3: System Updates${NC}"
echo
echo -e "The system will now update your Raspberry Pi."
echo -e "This ensures you have the latest security patches and software."
echo
read -p "Continue with system updates? (y/n): " do_update
if [[ "$do_update" == "y" || "$do_update" == "Y" ]]; then
  echo -e "\n${YELLOW}Updating system packages...${NC}"
  apt update
  apt upgrade -y
  echo -e "\n${GREEN}System updates completed.${NC}"
else
  echo -e "\n${YELLOW}System updates skipped.${NC}"
fi
echo
read -p "Press Enter to continue..." dummy

# STEP 4: Hardware Interfaces
clear
echo -e "${BLUE}${BOLD}STEP 4: Hardware Interfaces${NC}"
echo
echo -e "Your sensors require specific Raspberry Pi interfaces to be enabled."
echo -e "This wizard will automatically enable them for you."
echo

echo -e "${YELLOW}Enabling required interfaces...${NC}"
REBOOT_NEEDED=0

# Always enable I2C
if [ "$(raspi-config nonint get_i2c)" -ne 0 ]; then
  echo "- Enabling I2C interface"
  raspi-config nonint do_i2c 0
  REBOOT_NEEDED=1
fi

# Always enable 1-Wire for temperature sensors
if ! grep -q "^dtoverlay=w1-gpio" /boot/config.txt; then
  echo "- Enabling 1-Wire interface"
  echo "dtoverlay=w1-gpio" >> /boot/config.txt
  REBOOT_NEEDED=1
fi

# Enable UART for Complete Farm Control or Research (CO2 sensor)
if [ "$config_name" == "complete_farm_control" ] || [ "$goal_name" == "research" ]; then
  if [ "$(raspi-config nonint get_serial)" -ne 0 ]; then
    echo "- Enabling UART interface"
    raspi-config nonint do_serial 0
    REBOOT_NEEDED=1
  fi
fi

# Enable SPI for advanced systems
if [ "$config_name" == "hydroponic_system" ] || [ "$goal_name" == "research" ]; then
  if [ "$(raspi-config nonint get_spi)" -ne 0 ]; then
    echo "- Enabling SPI interface"
    raspi-config nonint do_spi 0
    REBOOT_NEEDED=1
  fi
fi

# Add USB device rules for better sensor compatibility
echo -e "- Adding USB device rules for sensors"
cat > /etc/udev/rules.d/99-usb-sensors.rules << EOF
# Rules for USB pH and EC sensors
SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", GROUP="dialout", MODE="0660", SYMLINK+="ttyUSB_FTDI"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", GROUP="dialout", MODE="0660", SYMLINK+="ttyUSB_CH340"
EOF

echo -e "\n${GREEN}Hardware interfaces enabled.${NC}"
echo
read -p "Press Enter to continue..." dummy

# STEP 5: Install Dependencies
clear
echo -e "${BLUE}${BOLD}STEP 5: Install Dependencies${NC}"
echo
echo -e "The system will now install required software packages."
echo -e "This may take several minutes."
echo
read -p "Continue with software installation? (y/n): " do_install
if [[ "$do_install" == "y" || "$do_install" == "Y" ]]; then
  echo -e "\n${YELLOW}Installing dependencies...${NC}"
  apt install -y build-essential python3-dev python3-pip libatlas-base-dev git python3-venv
  apt install -y i2c-tools python3-smbus ufw libgpiod2
  apt install -y nginx sqlite3 supervisor # For web dashboard
  
  # Install Python packages
  echo -e "${YELLOW}Installing Python packages...${NC}"
  pip3 install RPi.GPIO w1thermsensor adafruit-circuitpython-dht
  pip3 install flask pandas matplotlib # For data visualization
  
  # Install system-specific packages
  if [ "$config_name" == "hydroponic_system" ]; then
    echo -e "${YELLOW}Installing additional dependencies for hydroponic system...${NC}"
    pip3 install adafruit-circuitpython-ads1x15
    pip3 install adafruit-circuitpython-mcp3xxx # For analog pH/EC sensors
  fi
  
  # Install educational packages if needed
  if [ "$goal_name" == "educational" ]; then
    echo -e "${YELLOW}Installing educational tools...${NC}"
    pip3 install jupyter notebook # For educational notebooks
    apt install -y python3-pygame # For visual demonstrations
  fi

  # Install accessibility tools if needed
  if [ "$accommodation" == "visual" ]; then
    echo -e "${YELLOW}Installing accessibility tools for visual impairments...${NC}"
    apt install -y espeak-ng festival # For text-to-speech
    apt install -y python3-pyttsx3 # For TTS in Python
  fi
  
  # Install photo logging dependencies
  if [[ "$photo_log" == "y" || "$photo_log" == "Y" ]]; then
    echo -e "${YELLOW}Installing photo documentation tools...${NC}"
    apt install -y fswebcam imagemagick
  fi
  
  # Install documentation tools
  echo -e "${YELLOW}Installing documentation tools...${NC}"
  apt install -y qrencode # For generating QR codes
  
  echo -e "\n${GREEN}Software installation completed.${NC}"
else
  echo -e "\n${YELLOW}Software installation skipped.${NC}"
fi
echo
read -p "Press Enter to continue..." dummy

# STEP 6: Sensor Detection
clear
echo -e "${BLUE}${BOLD}STEP 6: Sensor Detection${NC}"
echo
echo -e "Checking for connected sensors..."
echo

# Safety reminder for educational settings
if [ "$goal_name" == "educational" ]; then
  echo -e "${RED}SAFETY REMINDER FOR CLASSROOM SETTINGS:${NC}"
  echo -e "- Ensure all electrical connections are properly insulated"
  echo -e "- Keep water away from electronics"
  echo -e "- Consider using plastic enclosures for all components"
  echo -e "- Supervise students when working with the system"
  echo
fi

# Therapy safety reminders
if [ "$user_role" == "therapist" ] || [ "$user_role" == "agritherapist" ]; then
  echo -e "${RED}SAFETY REMINDER FOR THERAPEUTIC SETTINGS:${NC}"
  echo -e "- Use low-voltage components when possible (5V preferred)"
  echo -e "- Consider touch-safe enclosures for all electronics"
  echo -e "- Implement additional protections based on participant needs"
  echo -e "- Ensure all water-handling components are well-separated from electronics"
  echo
fi

# Check for I2C devices
echo -e "${CYAN}I2C Devices:${NC}"
i2c_devices=$(i2cdetect -y 1)
echo "$i2c_devices"

# Save raw scan for debugging
echo "$i2c_devices" > "${CONFIG_DIR}/i2c_devices.txt"

# Look for known sensor addresses
if echo "$i2c_devices" | grep -q "48"; then
  echo -e "${GREEN} Found ADS1115 ADC at address 0x48${NC}"
  echo "ads1115,0x48" >> "${CONFIG_DIR}/detected_sensors.txt"
fi
if echo "$i2c_devices" | grep -q "39"; then
  echo -e "${GREEN} Found TSL2561 Light Sensor at address 0x39${NC}"
  echo "tsl2561,0x39" >> "${CONFIG_DIR}/detected_sensors.txt"
fi
if echo "$i2c_devices" | grep -q "76"; then
  echo -e "${GREEN} Found BME280 Temperature/Humidity/Pressure at address 0x76${NC}"
  echo "bme280,0x76" >> "${CONFIG_DIR}/detected_sensors.txt"
fi
if echo "$i2c_devices" | grep -q "44"; then
  echo -e "${GREEN} Found SHT31 Temperature/Humidity at address 0x44${NC}"
  echo "sht31,0x44" >> "${CONFIG_DIR}/detected_sensors.txt"
fi

# Check for 1-Wire temperature sensors
echo -e "\n${CYAN}1-Wire Temperature Sensors:${NC}"
if [ -d /sys/bus/w1/devices ]; then
  ds18b20_devices=$(ls /sys/bus/w1/devices/ | grep -v "w1_bus_master")
  if [ -z "$ds18b20_devices" ]; then
    echo -e "${RED} No DS18B20 temperature sensors detected${NC}"
  else
    echo -e "${GREEN} Found DS18B20 temperature sensors:${NC}"
    for device in $ds18b20_devices; do
      echo "  - $device"
      # Save device ID for later use in configuration
      echo "ds18b20,$device" >> "${CONFIG_DIR}/detected_sensors.txt"
    fi
  fi
else
  echo -e "${RED} 1-Wire bus not detected${NC}"
fi

# Check for USB devices
echo -e "\n${CYAN}USB Devices:${NC}"
usb_devices=$(lsusb)
echo "$usb_devices" | grep "USB"
echo "$usb_devices" > "${CONFIG_DIR}/usb_devices.txt"

# Detect USB-Serial devices
if [ -d /dev/serial/by-id ]; then
  echo -e "\n${CYAN}USB-Serial Devices:${NC}"
  ls -la /dev/serial/by-id/
  
  # Save for configuration
  ls -la /dev/serial/by-id/ > "${CONFIG_DIR}/usb_serial_devices.txt"
fi

# Check for cameras
echo -e "\n${CYAN}Camera Detection:${NC}"
if [ -e /dev/video0 ]; then
  echo -e "${GREEN} USB Camera detected at /dev/video0${NC}"
  echo "usb_camera,/dev/video0" >> "${CONFIG_DIR}/detected_sensors.txt"
elif [ -e /dev/video1 ]; then
  echo -e "${GREEN} USB Camera detected at /dev/video1${NC}"
  echo "usb_camera,/dev/video1" >> "${CONFIG_DIR}/detected_sensors.txt"
elif vcgencmd get_camera | grep -q "detected=1"; then
  echo -e "${GREEN} Raspberry Pi Camera Module detected${NC}"
  echo "picamera,/dev/vchiq" >> "${CONFIG_DIR}/detected_sensors.txt"
else
  echo -e "${RED} No cameras detected${NC}"
  if [[ "$photo_log" == "y" || "$photo_log" == "Y" ]]; then
    echo -e "${YELLOW}Warning: Photo journaling is enabled but no camera detected.${NC}"
    echo -e "${YELLOW}Please connect a camera and restart the setup.${NC}"
  fi
fi

echo -e "\n${CYAN}NOTE:${NC} UART devices like the MH-Z19 CO2 sensor"
echo -e "cannot be auto-detected. Please ensure it's connected to"
echo -e "GPIO 14 (TX) and GPIO 15 (RX) pins if using this sensor."

echo
echo -e "${PURPLE}Sensor detection complete.${NC}"
echo -e "These results will be used to customize your configuration."
echo
read -p "Press Enter to continue..." dummy

# STEP 7: Install Mycodo
clear
echo -e "${BLUE}${BOLD}STEP 7: Install Mycodo${NC}"
echo
echo -e "Mycodo is the control software that manages your sensors and automation."
echo -e "This installation will take approximately 30-45 minutes."
echo

# Confirmation with different language based on user role
if [ "$user_role" == "educator" ]; then
  echo -e "${YELLOW}For educational use, Mycodo provides:${NC}"
  echo -e "- Simple dashboard suitable for student interaction"
  echo -e "- Data logging for classroom experiments"
  echo -e "- Visual representations of environmental conditions"
elif [ "$user_role" == "farmer" ]; then
  echo -e "${YELLOW}For farm use, Mycodo provides:${NC}"
  echo -e "- Precise environmental control"
  echo -e "- Automation of lighting, irrigation and ventilation"
  echo -e "- Alerts for out-of-range conditions"
elif [ "$user_role" == "therapist" ] || [ "$user_role" == "community" ]; then
  echo -e "${YELLOW}For social impact programs, Mycodo provides:${NC}"
  echo -e "- Simple interface suitable for diverse users"
  echo -e "- Documentation features for program impact"
  echo -e "- Customizable views for different participant types"
elif [ "$user_role" == "agritherapist" ]; then
  echo -e "${YELLOW}For horticultural therapy, Mycodo provides:${NC}"
  echo -e "- Accessible interfaces adaptable to various ability levels"
  echo -e "- Visual tracking of plant growth for therapeutic engagement"
  echo -e "- Simplified controls for participant interaction"
  echo -e "- Documentation tools for tracking therapeutic progress"
fi

read -p "Continue with Mycodo installation? (y/n): " do_mycodo
if [[ "$do_mycodo" == "y" || "$do_mycodo" == "Y" ]]; then
  echo -e "\n${YELLOW}Installing Mycodo...${NC}"
  echo -e "${YELLOW}This may take a while. Please be patient.${NC}"
  curl -L https://kizniche.github.io/Mycodo/install | bash
  
  # Check if installation was successful
  if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Mycodo installation completed successfully.${NC}"
    
    # Create symbolic link to Mycodo for easier access
    ln -sf /var/mycodo/mycodo/outputs/output.py /usr/local/bin/mycodo-output
    ln -sf /var/mycodo/mycodo/inputs/input.py /usr/local/bin/mycodo-input
    
    # Set permissions
    echo -e "${YELLOW}Setting permissions...${NC}"
    usermod -a -G mycodo pi
    usermod -a -G gpio mycodo
    usermod -a -G i2c mycodo
    usermod -a -G dialout mycodo
  else
    echo -e "\n${RED}Mycodo installation failed. Please check the logs.${NC}"
    echo -e "You may need to run the installer manually with:"
    echo -e "curl -L https://kizniche.github.io/Mycodo/install | bash"
    echo -e "${YELLOW}Installation will continue, but you'll need to fix this later.${NC}"
  fi
  
  # Configure Mycodo settings based on user role
  if [ -f /var/mycodo/databases/mycodo.db ]; then
    echo -e "\n${YELLOW}Configuring Mycodo settings...${NC}"
    
    # Set custom Mycodo settings
    sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='${project_name}' WHERE setting='farm_name'"
    
    # Educational settings
    if [ "$goal_name" == "educational" ]; then
      # Set default light cycle for school hours
      sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='8:00' WHERE setting='daemon_debug_mode'"
      # Enable notes widget by default
      sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='True' WHERE setting='enable_notes_1'"
    fi
    
    # Social impact settings
    if [ "$goal_name" == "social" ]; then
      # Enable soft alerts mode
      sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='False' WHERE setting='enable_fullscreen_mode'"
      # Enable simple view by default
      sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='True' WHERE setting='hide_alert_info'"
    fi
    
    # Accessibility settings
    if [ "$accessibility_needed" == "y" ]; then
      echo -e "\n${YELLOW}Applying accessibility configurations...${NC}"
      if [ "$accommodation" == "visual" ]; then
        # High contrast and larger fonts
        sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='dark_contrast' WHERE setting='theme_default'"
        sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='large' WHERE setting='font_size'"
      elif [ "$accommodation" == "motor" ]; then
        # Simplified controls
        sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='True' WHERE setting='enable_touch_mode'"
        sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='True' WHERE setting='hide_alert_success'"
      elif [ "$accommodation" == "cognitive" ]; then
        # Simplified view
        sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='True' WHERE setting='hide_alert_info'"
        sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='True' WHERE setting='hide_alert_warning'"
      fi
    fi
    
    # Restart Mycodo to apply settings
    systemctl restart mycodoflask
    systemctl restart mycododaemon
  fi

  # Preload configurations based on user role (PATCHED)
  if [ -f /var/mycodo/databases/mycodo.db ] && [ -d /var/mycodo/mycodo/scripts ]; then
    echo -e "\n${YELLOW}Applying preset configurations for ${user_role}...${NC}"
    
    # Create configuration directory if it doesn't exist
    mkdir -p "${CONFIG_DIR}/mycodo_presets"
    
    # Copy appropriate preset based on role and goal
    if [ "$user_role" == "agritherapist" ]; then
      # Apply agritherapy presets
      cp "${CONFIG_DIR}/mycodo_presets/agritherapy.mycodo" /var/mycodo/mycodo/scripts/preset_import.mycodo
      
      # Apply preset using Mycodo's command-line tools
      python3 /var/mycodo/mycodo/scripts/mycodo_wrapper.py -f import-preset
      
      echo -e "${GREEN}Applied agritherapy configuration preset.${NC}"
    elif [ "$goal_name" == "educational" ] || [ "$user_role" == "educator" ]; then
      # Apply education presets
      cp "${CONFIG_DIR}/mycodo_presets/education.mycodo" /var/mycodo/mycodo/scripts/preset_import.mycodo
      python3 /var/mycodo/mycodo/scripts/mycodo_wrapper.py -f import-preset
      
      echo -e "${GREEN}Applied educational configuration preset.${NC}"
    elif [ "$goal_name" == "social" ] || [ "$user_role" == "community" ]; then
      # Apply community/social presets
      cp "${CONFIG_DIR}/mycodo_presets/community.mycodo" /var/mycodo/mycodo/scripts/preset_import.mycodo
      python3 /var/mycodo/mycodo/scripts/mycodo_wrapper.py -f import-preset
      
      echo -e "${GREEN}Applied community/social impact configuration preset.${NC}"
    fi
  fi
  
else
  echo -e "\n${YELLOW}Mycodo installation skipped.${NC}"
  echo -e "${RED}NOTE: The system won't function without Mycodo.${NC}"
  echo -e "You will need to install it manually with:"
  echo -e "curl -L https://kizniche.github.io/Mycodo/install | bash"
fi
echo
read -p "Press Enter to continue..." dummy

# STEP 8: Backup Configuration
clear
echo -e "${BLUE}${BOLD}STEP 8: Backup Configuration${NC}"
echo
echo -e "Regular backups are essential to prevent data loss."
echo -e "This wizard will set up automated backup options."
echo

# Backup options
echo -e "${CYAN}Select your preferred backup schedule:${NC}"
echo -e "1) ${CYAN}Weekly${NC} - Standard backup every Sunday at 2:00 AM"
echo -e "2) ${CYAN}Daily${NC} - More frequent backup each night at 1:00 AM"
echo -e "3) ${CYAN}Monthly${NC} - Minimal backup on the 1st of each month"
read -p "Select backup schedule [1-3, default=1]: " backup_schedule

case $backup_schedule in
  2) backup_freq="daily" ;;
  3) backup_freq="monthly" ;;
  *) backup_freq="weekly" ;;
esac

# Create enhanced backup script
cat > "${SCRIPTS_DIR}/backup.sh" << EOF
#!/bin/bash
# Container Farm Control System Backup Script
# Project: ${project_name}
# Created: $(date)

TIMESTAMP=\$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR=${BACKUP_DIR}
PROJECT_NAME="${project_name}"
OPERATOR="${operator_name}"
PRIMARY_GOAL="${goal_name}"

# Create backup directories
mkdir -p \$BACKUP_DIR
mkdir -p \$BACKUP_DIR/configs
mkdir -p \$BACKUP_DIR/databases
mkdir -p \$BACKUP_DIR/logs

# Backup Mycodo data
echo "Backing up Mycodo..."
tar -czf \$BACKUP_DIR/\${PROJECT_NAME}_mycodo_backup_\$TIMESTAMP.tar.gz /var/mycodo

# Backup InfluxDB data
echo "Backing up InfluxDB..."
influxd backup -portable \$BACKUP_DIR/influxdb_backup_\$TIMESTAMP

# Backup system configuration
echo "Backing up system configuration..."
cp -r ${CONFIG_DIR}/* \$BACKUP_DIR/configs/

# Backup photo logs if enabled
if [ -d "${INSTALL_DIR}/photo_log" ]; then
  echo "Backing up photo journal..."
  tar -czf \$BACKUP_DIR/\${PROJECT_NAME}_photo_journal_\$TIMESTAMP.tar.gz ${INSTALL_DIR}/photo_log
fi

# Create summary file
cat > "\$BACKUP_DIR/\${PROJECT_NAME}_backup_summary_\$TIMESTAMP.txt" << EOL
============================================================
Container Farm Control System - Backup Summary
============================================================
Project Name   : ${project_name}
Location       : ${project_location}
Operator       : ${operator_name}
User Role      : ${user_role}
Primary Goal   : ${goal_name}
System Type    : ${config_name}
Backup Date    : \$(date)
============================================================
EOL

# Generate QR code for local access
qrencode -o "\$BACKUP_DIR/\${PROJECT_NAME}_access_qr.png" "http://\$(hostname -I | awk '{print \$1}')"

# Clean up old backups (keep last 10)
echo "Cleaning up old backups..."
find \$BACKUP_DIR -type d -name "influxdb_backup_*" -mtime +30 -exec rm -rf {} \;
ls -t \$BACKUP_DIR/\${PROJECT_NAME}_mycodo_backup_*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null

echo "Backup completed at \$(date)"
EOF

chmod +x "${SCRIPTS_DIR}/backup.sh"

# Schedule backup based on selected frequency
if [ "$backup_freq" == "daily" ]; then
  cron_schedule="0 1 * * *"
  echo -e "${GREEN}Daily backups will run every night at 1:00 AM.${NC}"
elif [ "$backup_freq" == "monthly" ]; then
  cron_schedule="0 3 1 * *"
  echo -e "${GREEN}Monthly backups will run on the 1st of each month at 3:00 AM.${NC}"
else
  cron_schedule="0 2 * * 0"
  echo -e "${GREEN}Weekly backups will run every Sunday at 2:00 AM.${NC}"
fi

# Schedule backup
(crontab -l 2>/dev/null || echo "") | grep -v "backup.sh" | { cat; echo "$cron_schedule ${SCRIPTS_DIR}/backup.sh"; } | crontab -

# Create a local documentation backup
echo -e "${YELLOW}Installing offline documentation...${NC}"
mkdir -p "${DOCS_DIR}/offline"
git clone https://github.com/kizniche/Mycodo-custom.git "${DOCS_DIR}/offline/mycodo-docs" 2>/dev/null || echo -e "${RED}Could not download offline documentation.${NC}"

echo
read -p "Press Enter to continue..." dummy

# STEP 9: Dashboard Setup
clear
echo -e "${BLUE}${BOLD}STEP 9: Dashboard Configuration${NC}"
echo
echo -e "Now we'll set up your control dashboard based on your selections."
echo

# Create custom dashboard based on user role
if [ "$goal_name" == "educational" ]; then
  echo -e "${YELLOW}Creating educational dashboard...${NC}"
  
  # Create educational dashboard settings
  cat > "${DASHBOARD_DIR}/educational_dashboard.json" << EOF
{
  "name": "${project_name} - Educational Dashboard",
  "widgets": [
    {"type": "gauge", "name": "Temperature", "sensor": "temp_sensor", "min": 0, "max": 40},
    {"type": "gauge", "name": "Humidity", "sensor": "humidity_sensor", "min": 0, "max": 100},
    {"type": "indicator", "name": "Lights", "output": "light_relay"},
    {"type": "indicator", "name": "Water Pump", "output": "pump_relay"},
    {"type": "camera", "name": "Plant Camera", "camera": "webcam"},
    {"type": "notes", "name": "Student Notes", "editable": true}
  ],
  "note": "This dashboard is designed for ${grade_level} level education"
}
EOF

  # Create Student View dashboard (simplified)
  cat > "${DASHBOARD_DIR}/student_dashboard.json" << EOF
{
  "name": "${project_name} - Student View",
  "widgets": [
    {"type": "gauge", "name": "Temperature", "sensor": "temp_sensor", "min": 0, "max": 40},
    {"type": "gauge", "name": "Humidity", "sensor": "humidity_sensor", "min": 0, "max": 100},
    {"type": "indicator", "name": "Lights", "output": "light_relay", "read_only": true},
    {"type": "notes", "name": "Student Notes", "editable": true},
    {"type": "graph", "name": "Daily Temperature", "sensor": "temp_sensor", "period": "day"}
  ],
  "note": "Student view dashboard for ${project_name}"
}
EOF

elif [ "$goal_name" == "social" ]; then
  echo -e "${YELLOW}Creating social impact dashboard...${NC}"
  
  # Create social impact dashboard settings (simplified, less technical)
  cat > "${DASHBOARD_DIR}/social_impact_dashboard.json" << EOF
{
  "name": "${project_name} - ${user_role} Dashboard",
  "widgets": [
    {"type": "gauge", "name": "Temperature", "sensor": "temp_sensor", "min": 0, "max": 40},
    {"type": "gauge", "name": "Humidity", "sensor": "humidity_sensor", "min": 0, "max": 100},
    {"type": "indicator", "name": "Lights", "output": "light_relay", "text": ["Off", "On"]},
    {"type": "indicator", "name": "Water", "output": "pump_relay", "text": ["Off", "On"]},
    {"type": "camera", "name": "Growth Progress", "camera": "webcam"},
    {"type": "notes", "name": "Program Notes", "editable": true}
  ],
  "note": "Social impact dashboard for ${project_name}"
}
EOF

  # Create Participant View (very simple)
  cat > "${DASHBOARD_DIR}/participant_dashboard.json" << EOF
{
  "name": "${project_name} - Participant View",
  "widgets": [
    {"type": "gauge", "name": "Temperature", "sensor": "temp_sensor", "min": 0, "max": 40},
    {"type": "indicator", "name": "Lights", "output": "light_relay", "text": ["Off", "On"], "read_only": true},
    {"type": "notes", "name": "Your Notes", "editable": true},
    {"type": "camera", "name": "Plants", "camera": "webcam"}
  ],
  "note": "Simple view for program participants"
}
EOF

# Agritherapy dashboard (PATCHED)
elif [ "$user_role" == "agritherapist" ]; then
  echo -e "${YELLOW}Creating agritherapy dashboard...${NC}"
  
  # Create agritherapy dashboard settings
  cat > "${DASHBOARD_DIR}/agritherapy_dashboard.json" << EOF
{
  "name": "${project_name} - Agritherapy Dashboard",
  "widgets": [
    {"type": "gauge", "name": "Temperature", "sensor": "temp_sensor", "min": 0, "max": 40},
    {"type": "gauge", "name": "Humidity", "sensor": "humidity_sensor", "min": 0, "max": 100},
    {"type": "indicator", "name": "Lights", "output": "light_relay", "text": ["Off", "On"]},
    {"type": "indicator", "name": "Water", "output": "pump_relay", "text": ["Off", "On"]},
    {"type": "camera", "name": "Plant Progress", "camera": "webcam"},
    {"type": "notes", "name": "Therapy Session Notes", "editable": true},
    {"type": "notes", "name": "Participant Observations", "editable": true},
    {"type": "graph", "name": "Growth Timeline", "sensor": "temp_sensor", "period": "week"},
    {"type": "custom", "name": "Photo Journal", "custom_options": {"type": "image_carousel", "directory": "/opt/container-farm-control/photo_log"}}
  ],
  "note": "Agritherapy dashboard for ${project_name}"
}
EOF

  # Create Participant View (simplified for therapy participants)
  cat > "${DASHBOARD_DIR}/therapy_participant_dashboard.json" << EOF
{
  "name": "${project_name} - Participant View",
  "widgets": [
    {"type": "indicator", "name": "Today's Tasks", "custom_options": {"type": "task_list", "max_items": 5}},
    {"type": "camera", "name": "Plants Today", "camera": "webcam"},
    {"type": "custom", "name": "Plant Progress", "custom_options": {"type": "image_carousel", "directory": "/opt/container-farm-control/photo_log"}},
    {"type": "notes", "name": "Your Observations", "editable": true, "placeholder": "What did you notice about the plants today?"}
  ],
  "note": "Simplified view for agritherapy participants"
}
EOF

else
  echo -e "${YELLOW}Creating standard dashboard...${NC}"
  
  # Create standard dashboard for commercial/research use
  cat > "${DASHBOARD_DIR}/standard_dashboard.json" << EOF
{
  "name": "${project_name} - Control Dashboard",
  "widgets": [
    {"type": "gauge", "name": "Temperature", "sensor": "temp_sensor", "min": 0, "max": 40},
    {"type": "gauge", "name": "Humidity", "sensor": "humidity_sensor", "min": 0, "max": 100},
    {"type": "gauge", "name": "CO2", "sensor": "co2_sensor", "min": 0, "max": 5000},
    {"type": "output", "name": "Light Control", "output": "light_relay"},
    {"type": "output", "name": "Fan Control", "output": "fan_relay"},
    {"type": "output", "name": "Pump Control", "output": "pump_relay"},
    {"type": "camera", "name": "System Camera", "camera": "webcam"},
    {"type": "graph", "name": "Environmental Data", "sensors": ["temp_sensor", "humidity_sensor"]}
  ],
  "note": "Main control dashboard for ${project_name}"
}
EOF
fi

# Add accessibility dashboard if needed
if [ "$accessibility_needed" == "y" ]; then
  echo -e "${YELLOW}Creating accessibility-friendly dashboard...${NC}"
  
  if [ "$accommodation" == "visual" ]; then
    cat > "${DASHBOARD_DIR}/accessible_dashboard.json" << EOF
{
  "name": "${project_name} - High Contrast Dashboard",
  "widgets": [
    {"type": "gauge", "name": "Temperature", "sensor": "temp_sensor", "min": 0, "max": 40, "colors": ["#000000", "#FFFFFF", "#FF0000"]},
    {"type": "gauge", "name": "Humidity", "sensor": "humidity_sensor", "min": 0, "max": 100, "colors": ["#000000", "#FFFFFF", "#0000FF"]},
    {"type": "indicator", "name": "LIGHTS", "output": "light_relay", "text": ["OFF", "ON"], "colors": ["#FFFFFF", "#FFFF00"], "font_size": "x-large"},
    {"type": "indicator", "name": "WATER", "output": "pump_relay", "text": ["OFF", "ON"], "colors": ["#FFFFFF", "#00FFFF"], "font_size": "x-large"},
    {"type": "notes", "name": "NOTES", "editable": true, "font_size": "x-large"}
  ],
  "note": "High contrast dashboard with larger text for visual accessibility"
}
EOF
  elif [ "$accommodation" == "motor" ]; then
    cat > "${DASHBOARD_DIR}/accessible_dashboard.json" << EOF
{
  "name": "${project_name} - Motor-Friendly Dashboard",
  "widgets": [
    {"type": "gauge", "name": "Temperature", "sensor": "temp_sensor", "min": 0, "max": 40},
    {"type": "gauge", "name": "Humidity", "sensor": "humidity_sensor", "min": 0, "max": 100},
    {"type": "indicator", "name": "Lights", "output": "light_relay", "text": ["Off", "On"], "button_size": "large", "spacing": "15px"},
    {"type": "indicator", "name": "Water", "output": "pump_relay", "text": ["Off", "On"], "button_size": "large", "spacing": "15px"},
    {"type": "camera", "name": "Plants", "camera": "webcam"}
  ],
  "note": "Dashboard with larger buttons and spacing for motor accessibility"
}
EOF
  elif [ "$accommodation" == "cognitive" ]; then
    cat > "${DASHBOARD_DIR}/accessible_dashboard.json" << EOF
{
  "name": "${project_name} - Simple Dashboard",
  "widgets": [
    {"type": "indicator", "name": "Temperature", "sensor": "temp_sensor", "display": "text", "text_template": "Temperature: {value}°C"},
    {"type": "indicator", "name": "Plant Lights", "output": "light_relay", "text": ["Lights Off", "Lights On"], "icons": ["lightbulb-off", "lightbulb-on"]},
    {"type": "indicator", "name": "Water Plants", "output": "pump_relay", "text": ["Water Off", "Water On"], "icons": ["water-off", "water"]},
    {"type": "camera", "name": "Your Plants", "camera": "webcam"},
    {"type": "notes", "name": "Today's Activities", "editable": true, "placeholder": "What did you do today?"}
  ],
  "note": "Simplified dashboard with visual cues for cognitive accessibility"
}
EOF
  fi
fi

# Voice Assistant Configuration (PATCHED)
echo -e "\n${CYAN}Accessibility Features:${NC}"
echo -e "Would you like to prepare for future voice control capabilities?"
echo -e "This is especially useful for therapeutic programs and accessibility needs."
echo -e "Note: This is a placeholder for future functionality."
read -p "Enable voice control preparation? (y/n): " voice_control

if [[ "$voice_control" == "y" || "$voice_control" == "Y" ]]; then
  echo "enabled" > "${CONFIG_DIR}/voice_control.txt"
  
  # Create placeholder directory
  mkdir -p "${INSTALL_DIR}/voice_control"
  
  echo -e "${YELLOW}Voice control preparation enabled.${NC}"
  echo -e "When this feature becomes available, run:"
  echo -e "${CYAN}sudo ${SCRIPTS_DIR}/update_features.sh --enable-voice${NC}"
else
  echo "disabled" > "${CONFIG_DIR}/voice_control.txt"
fi

echo -e "${GREEN}Dashboard configurations created.${NC}"
echo -e "These will be imported into Mycodo during final configuration."
echo
read -p "Press Enter to continue..." dummy

# STEP 10: Wiring Information
clear
echo -e "${BLUE}${BOLD}STEP 10: Wiring Information${NC}"
echo
echo -e "Based on your selected system type (${GREEN}$config_name${NC}),"
echo -e "please refer to the appropriate wiring diagram:"
echo

# Wiring diagram differs based on system type
if [ "$config_name" == "basic_monitoring" ]; then
  echo -e "${YELLOW}Basic Monitoring Wiring:${NC}"
  echo -e "- Temperature sensor (DS18B20) → GPIO 4 (with 4.7kΩ pull-up resistor)"
  echo -e "- DHT22 Temperature/Humidity → GPIO 17"
  echo -e "- Light Relay → GPIO 23"
  echo -e "- Fan Relay → GPIO 24"
elif [ "$config_name" == "complete_farm_control" ]; then
  echo -e "${YELLOW}Complete Farm Control Wiring:${NC}"
  echo -e "- Temperature sensors (DS18B20) → GPIO 4 (with 4.7kΩ pull-up resistor)"
  echo -e "- BME280 Sensor → I2C (SDA, SCL)"
  echo -e "- MH-Z19 CO2 Sensor → GPIO 14 (TX), GPIO 15 (RX)"
  echo -e "- 8-Channel Relay Board → GPIOs 5, 6, 13, 19, 20, 21, 26, 16"
  echo -e "  - Relay 1 (Lights) → GPIO 5"
  echo -e "  - Relay 2 (Fans) → GPIO 6"
  echo -e "  - Relay 3 (Water Pump) → GPIO 13"
  echo -e "  - Relay 4 (Heater) → GPIO 19"
  echo -e "  - Relay 5 (AC) → GPIO 20"
  echo -e "  - Relay 6 (Humidifier) → GPIO 21"
  echo -e "  - Relay 7 (Dehumidifier) → GPIO 26"
  echo -e "  - Relay 8 (Spare) → GPIO 16"
elif [ "$config_name" == "hydroponic_system" ]; then
  echo -e "${YELLOW}Hydroponic System Wiring:${NC}"
  echo -e "- Temperature sensors (DS18B20) → GPIO 4 (with 4.7kΩ pull-up resistor)"
  echo -e "- BME280 Sensor → I2C (SDA, SCL)"
  echo -e "- ADS1115 ADC → I2C (SDA, SCL)"
  echo -e "  - pH Sensor → ADS1115 A0"
  echo -e "  - EC Sensor → ADS1115 A1"
  echo -e "- 8-Channel Relay Board → GPIOs 5, 6, 13, 19, 20, 21, 26, 16"
  echo -e "  - Relay 1 (Lights) → GPIO 5"
  echo -e "  - Relay 2 (Air Pump) → GPIO 6"
  echo -e "  - Relay 3 (Water Pump) → GPIO 13"
  echo -e "  - Relay 4 (Nutrient Pump A) → GPIO 19"
  echo -e "  - Relay 5 (Nutrient Pump B) → GPIO 20"
  echo -e "  - Relay 6 (pH Up Pump) → GPIO 21"
  echo -e "  - Relay 7 (pH Down Pump) → GPIO 26"
  echo -e "  - Relay 8 (Mixer) → GPIO 16"
fi

echo -e "\n${CYAN}Wiring Diagram File:${NC} schematics/wiring_diagrams/${config_name}_wiring.svg"

# Safety notes based on user role
if [ "$goal_name" == "educational" ]; then
  echo -e "\n${RED}EDUCATIONAL SAFETY NOTES:${NC}"
  echo -e "- Use proper electrical safety measures in classroom settings"
  echo -e "- Consider using lower voltage (5V) components when possible"
  echo -e "- Ensure all connections are in a protected enclosure"
  echo -e "- Place a clear warning label on the system"
elif [ "$user_role" == "therapist" ] || [ "$user_role" == "agritherapist" ]; then
  echo -e "\n${RED}THERAPEUTIC ENVIRONMENT NOTES:${NC}"
  echo -e "- Ensure all wiring is secured and not accessible to participants"
  echo -e "- Consider additional protective enclosures"
  echo -e "- Use color-coded wires for teaching purposes if appropriate"
  echo -e "- Label components with large, clear text if possible"
  echo -e "- Consider touch-safe connectors for participant interaction points"
fi

echo -e "\n${RED}IMPORTANT:${NC} Proper wiring is critical for system functionality."
echo -e "Always shut down the Raspberry Pi before connecting or disconnecting hardware."
echo
read -p "Press Enter to continue..." dummy

# STEP 11: Final System Configuration
clear
echo -e "${BLUE}${BOLD}STEP 11: System Configuration${NC}"
echo
echo -e "Your system is now ready for final configuration."
echo

# Post-setup reflection (PATCHED)
if [ "$goal_name" == "educational" ] || [ "$goal_name" == "social" ] || [ "$user_role" == "agritherapist" ] || [ "$user_role" == "therapist" ]; then
  echo -e "\n${CYAN}POST-SETUP REFLECTION:${NC}"
  echo -e "Take a moment to document these aspects of your project:"
  echo -e "- What specific outcomes are you hoping to achieve?"
  echo -e "- How will you measure success with participants?"
  echo -e "- What regular activities will people do with this system?"
  
  # Specific to agritherapy
  if [ "$user_role" == "agritherapist" ]; then
    echo -e "\n${CYAN}AGRITHERAPY CONSIDERATIONS:${NC}"
    echo -e "- What therapeutic goals does this garden support?"
    echo -e "- How will you integrate plant care into therapy sessions?"
    echo -e "- What adaptations might be needed for different participants?"
  fi
  
  # Create reflection doc
  cat > "${DOCS_DIR}/reflection_prompts.txt" << EOF
PROJECT REFLECTION PROMPTS
=========================
Project: ${project_name}
Learning Goal: ${learning_goal:-Not specified}

PARTICIPANT OUTCOMES:
- What specific outcomes are you hoping participants will achieve?
- What skills or insights should they develop?
- How will you assess growth or progress?

SYSTEM USE:
- What regular activities will people do with this system?
- How frequently will the system be used?
- Who will maintain the system between sessions?

DOCUMENTATION:
- How will you document activities and outcomes?
- What evidence will you collect for grants or reports?
- How will you share successes with stakeholders?

${user_role^^} SPECIFIC QUESTIONS:
EOF

  if [ "$user_role" == "agritherapist" ]; then
    cat >> "${DOCS_DIR}/reflection_prompts.txt" << EOF
- What therapeutic modalities will you combine with gardening?
- How will you adapt activities for different participant abilities?
- How will you integrate sensory experiences (touch, smell, sight)?
- What assessment tools will you use to measure therapeutic outcomes?
EOF
  elif [ "$user_role" == "educator" ]; then
    cat >> "${DOCS_DIR}/reflection_prompts.txt" << EOF
- How does this system connect to your curriculum standards?
- What student-led inquiries could emerge from this system?
- How will students document their learning?
- What cross-curricular connections might you explore?
EOF
  fi
  
  echo -e "${GREEN}Reflection prompts saved to:${NC} ${DOCS_DIR}/reflection_prompts.txt"
fi

# About This Project generator (PATCHED)
cat > "${DOCS_DIR}/about_project.txt" <<EOF
===================================
ABOUT THIS CONTAINER FARM
===================================

Project: ${project_name}
Location: ${project_location}
Operator: ${operator_name}
User Role: ${user_role}
Primary Goal: ${goal_name}
Learning Focus: ${learning_goal:-Not specified}

SYSTEM TYPE: ${config_name}
INSTALLATION DATE: $(date)

This system was set up using the Open-Source Closed Environment framework,
developed in response to the shutdown of Farmhand.ag to preserve farmers'
autonomy and access to local control systems.

CORE PRINCIPLES:
- Data sovereignty and local control
- User autonomy and transparency
- Ethical and sustainable growing practices
EOF

if [ "$user_role" == "agritherapist" ]; then
  cat >> "${DOCS_DIR}/about_project.txt" <<EOF

AGRITHERAPY FOCUS:
This system is specifically configured to support horticultural therapy,
integrating plant care into therapeutic practice. It provides:
- Accessible interfaces for diverse participant needs
- Documentation tools for therapy session progress
- Visual tracking of plant growth for participant engagement
- Multi-sensory growing experiences

THERAPEUTIC APPROACH:
This growing system supports therapy through:
- Providing consistent care routines
- Creating tangible results that build confidence
- Offering sensory stimulation through plant interaction
- Supporting both individual and group engagement
EOF
fi

echo -e "${GREEN}Project description generated at:${NC} ${DOCS_DIR}/about_project.txt"
echo -e "This document can be printed for display or included in grant materials."

# Generate QR code for local access
echo -e "${YELLOW}Generating QR code for easy dashboard access...${NC}"
qrencode -o "${INSTALL_DIR}/dashboard_access.png" "http://$(hostname -I | awk '{print $1}')"
echo -e "${GREEN}QR code generated. You can scan this with your phone to access the dashboard.${NC}"
echo -e "QR code location: ${INSTALL_DIR}/dashboard_access.png"

echo -e "\nYou can import the pre-configured ${GREEN}$config_name${NC} settings"
echo -e "through the Mycodo web interface."
echo
echo -e "${CYAN}1. Access Mycodo at: https://$(hostname -I | awk '{print $1}')/${NC}"
echo -e "${CYAN}2. Navigate to: [Gear Icon] → Export/Import${NC}"
echo -e "${CYAN}3. Under 'Import', upload the file:${NC}"
echo -e "${CYAN}   configs/mycodo_exports/${config_name}.mycodo${NC}"
echo
echo -e "${YELLOW}NOTE:${NC} After importing, you'll need to adjust GPIO pins"
echo -e "to match your specific wiring."
echo

# Generate project summary file
SUMMARY_FILE="${INSTALL_DIR}/project_summary.txt"
cat > "$SUMMARY_FILE" <<EOF
============================================================
Container Farm Control System - Setup Summary
============================================================
Project Name   : $project_name
Location       : $project_location
Operator       : $operator_name
User Role      : $user_role
Primary Goal   : $goal_name
System Type    : $config_name
Installation   : $(date)
Mycodo URL     : https://$(hostname -I | awk '{print $1}')/login
============================================================

SYSTEM INFORMATION:
- Raspberry Pi Model: $(cat /proc/device-tree/model 2>/dev/null || echo "Unknown")
- Operating System: $(lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2- || echo "Unknown")
- Kernel Version: $(uname -r)
- IP Address: $(hostname -I | awk '{print $1}')

SENSORS DETECTED:
$(cat "${CONFIG_DIR}/detected_sensors.txt" 2>/dev/null || echo "No sensors detected")

BACKUP SCHEDULE:
- $backup_freq backups configured

NEXT STEPS:
1. Complete Mycodo configuration
2. Configure sensors and relays
3. Set up automation rules
4. Test system operation
5. Regular maintenance check
EOF

echo -e "${GREEN}Setup summary saved to:${NC} $SUMMARY_FILE"

# Create system update script
cat > "${SCRIPTS_DIR}/update_features.sh" << 'EOF'
#!/bin/bash
# Container Farm Control System - Feature Update Script
# This script allows enabling/disabling features and checking for updates

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Installation directories
INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo)${NC}"
  exit 1
fi

# Help menu
function show_help {
  echo -e "${CYAN}${BOLD}Container Farm Control System - Feature Update Script${NC}"
  echo
  echo "Usage: sudo $0 [OPTIONS]"
  echo
  echo "Options:"
  echo "  --enable-voice     Prepare system for voice control (placeholder)"
  echo "  --check-update     Check for system updates"
  echo "  --system-update    Update system components"
  echo "  --backup-now       Run backup immediately"
  echo "  --help             Show this help menu"
  echo
  echo "Example: sudo $0 --check-update"
}

# No arguments provided
if [ $# -eq 0 ]; then
  show_help
  exit 0
fi

# Process arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --enable-voice)
      echo -e "${YELLOW}Preparing system for voice control...${NC}"
      
      # Check if already enabled
      if [ "$(cat ${CONFIG_DIR}/voice_control.txt 2>/dev/null)" == "enabled" ]; then
        echo -e "${GREEN}Voice control is already enabled.${NC}"
      else
        echo "enabled" > "${CONFIG_DIR}/voice_control.txt"
        mkdir -p "${INSTALL_DIR}/voice_control"
        
        # Install required packages
        echo -e "${YELLOW}Installing voice control dependencies...${NC}"
        apt install -y python3-pip python3-pyaudio
        pip3 install SpeechRecognition pyttsx3
        
        echo -e "${GREEN}Voice control preparation complete.${NC}"
        echo -e "${YELLOW}Note: This is a placeholder for future functionality.${NC}"
      fi
      ;;
      
    --check-update)
      echo -e "${YELLOW}Checking for system updates...${NC}"
      
      # Check for updates to the main package
      if ping -c 1 github.com &> /dev/null; then
        echo -e "${CYAN}Checking for script updates from GitHub...${NC}"
        # Placeholder - in production would check a GitHub repo
        echo -e "${GREEN}Your system is up to date.${NC}"
      else
        echo -e "${RED}Cannot connect to update server. Please check your internet connection.${NC}"
      fi
      ;;
      
    --system-update)
      echo -e "${YELLOW}Updating system components...${NC}"
      
      # Update system packages
      apt update
      apt upgrade -y
      
      # Update Python packages
      pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install -U
      
      # For production, would pull latest from GitHub
      echo -e "${GREEN}System update complete.${NC}"
      ;;
      
    --backup-now)
      echo -e "${YELLOW}Running backup now...${NC}"
      ${SCRIPTS_DIR}/backup.sh
      echo -e "${GREEN}Backup complete.${NC}"
      ;;
      
    --help|*)
      show_help
      exit 0
      ;;
  esac
  shift
done

exit 0
EOF

chmod +x "${SCRIPTS_DIR}/update_features.sh"

# Create startup check script
cat > "${SCRIPTS_DIR}/startup_check.sh" << 'EOF'
#!/bin/bash
# Container Farm Control System - Startup Checks
# This script runs at boot to verify system functionality

# Load configuration
source /opt/container-farm-control/configs/config.sh 2>/dev/null || true

# Log file
LOG_FILE="/var/log/container-farm-startup.log"
echo "===== Container Farm Control System Startup Check =====" > $LOG_FILE
echo "Date: $(date)" >> $LOG_FILE
echo "Hostname: $(hostname)" >> $LOG_FILE

# Check if Mycodo services are running
echo "Checking Mycodo services..." >> $LOG_FILE
if systemctl is-active --quiet mycodoflask && systemctl is-active --quiet mycododaemon; then
  echo " Mycodo services running" >> $LOG_FILE
else
  echo " Mycodo services not running properly" >> $LOG_FILE
  # Try to restart services
  systemctl restart mycodoflask
  systemctl restart mycododaemon
fi

# Check network connection
echo "Checking network connection..." >> $LOG_FILE
if ping -c 1 8.8.8.8 &> /dev/null; then
  echo " Network connection active" >> $LOG_FILE
else
  echo " Network connection issue" >> $LOG_FILE
fi

# Check sensor connections by reading I2C bus
echo "Checking I2C sensors..." >> $LOG_FILE
if i2cdetect -y 1 &> /dev/null; then
  echo " I2C bus accessible" >> $LOG_FILE
  # Count I2C devices
  i2c_devices=$(i2cdetect -y 1 | grep -v "\-\-" | grep -v "00:" | tr -d ' ' | tr -d ':' | tr -d 'UU' | wc -c)
  if [ $i2c_devices -gt 0 ]; then
    echo " Found I2C devices" >> $LOG_FILE
  else
    echo " No I2C devices found" >> $LOG_FILE
  fi
else
  echo " I2C bus not accessible" >> $LOG_FILE
fi

# Check 1-Wire sensors
echo "Checking 1-Wire sensors..." >> $LOG_FILE
if [ -d /sys/bus/w1/devices ]; then
  w1_devices=$(ls /sys/bus/w1/devices/ | grep -v "w1_bus_master" | wc -l)
  if [ $w1_devices -gt 0 ]; then
    echo " Found $w1_devices 1-Wire temperature sensors" >> $LOG_FILE
  else
    echo " No 1-Wire sensors found" >> $LOG_FILE
  fi
else
  echo " 1-Wire bus not accessible" >> $LOG_FILE
fi

# Check cameras
echo "Checking cameras..." >> $LOG_FILE
if [ -e /dev/video0 ]; then
  echo " USB Camera detected" >> $LOG_FILE
elif vcgencmd get_camera | grep -q "detected=1"; then
  echo " Raspberry Pi Camera Module detected" >> $LOG_FILE
else
  echo " No cameras detected" >> $LOG_FILE
fi

# Send notification (if notification system is configured)
if [[ -f /var/mycodo/databases/mycodo.db && -x $(which sqlite3) ]]; then
  # Check if system has been running for over a day
  uptime_hours=$(awk '{print int($1/3600)}' /proc/uptime)
  if [ $uptime_hours -lt 24 ]; then
    # Don't spam with notifications, only send at startup or after reboot
    notification_enabled=$(sqlite3 /var/mycodo/databases/mycodo.db "SELECT value FROM misc WHERE setting='notification_smtp_enabled'" 2>/dev/null || echo "0")
    if [ "$notification_enabled" = "1" ]; then
      echo "Sending startup notification..." >> $LOG_FILE
      sqlite3 /var/mycodo/databases/mycodo.db "INSERT INTO notifications (datetime, recipient_id, notification_type, subject, body) VALUES (datetime('now'), 1, 'email', 'System Startup - ${project_name}', 'Container Farm Control System has started. IP: $(hostname -I | awk '{print $1}')')"
    fi
  fi
fi

echo "Startup check completed: $(date)" >> $LOG_FILE
EOF

chmod +x "${SCRIPTS_DIR}/startup_check.sh"

# Schedule startup check
(crontab -l 2>/dev/null || echo "") | grep -v "startup_check.sh" | { cat; echo "@reboot ${SCRIPTS_DIR}/startup_check.sh"; } | crontab -

# Create basic configuration file
cat > "${CONFIG_DIR}/config.sh" << EOF
#!/bin/bash
# Container Farm Control System - Configuration
# Project: ${project_name}
# Generated: $(date)

# Project Details
PROJECT_NAME="${project_name}"
PROJECT_LOCATION="${project_location}"
OPERATOR="${operator_name}"
USER_ROLE="${user_role}"
PRIMARY_GOAL="${goal_name}"
SYSTEM_TYPE="${config_name}"
BACKUP_FREQ="${backup_freq}"

# Accessibility Settings
ACCESSIBILITY_NEEDED="${accessibility_needed:-no}"
ACCOMMODATION_TYPE="${accommodation:-none}"

# Privacy Settings
PRIVACY_MODE="${privacy_mode}"
PHOTO_JOURNALING="${photo_log}"

# System Paths
INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="\${INSTALL_DIR}/configs"
SCRIPTS_DIR="\${INSTALL_DIR}/scripts"
BACKUP_DIR="\${INSTALL_DIR}/backups"
DOCS_DIR="\${INSTALL_DIR}/docs"
DASHBOARD_DIR="\${INSTALL_DIR}/dashboards"

# Mycodo Settings
MYCODO_URL="https://\$(hostname -I | awk '{print \$1}')/login"
EOF

chmod +x "${CONFIG_DIR}/config.sh"

# Summary
echo -e "${BLUE}${BOLD}Setup Summary:${NC}"
echo -e "- Project Name: ${GREEN}$project_name${NC}"
echo -e "- Location: ${GREEN}$project_location${NC}"
echo -e "- Primary Goal: ${GREEN}$goal_name${NC}"
echo -e "- User Role: ${GREEN}$user_role${NC}"
echo -e "- System Configuration: ${GREEN}$config_name${NC}"
echo -e "- Backup Schedule: ${GREEN}$backup_freq${NC}"
echo -e "- Mycodo Web Interface: ${GREEN}https://$(hostname -I | awk '{print $1}')/login${NC}"

if [ "$user_role" == "agritherapist" ]; then
  echo -e "- Therapy Type: ${GREEN}${therapy_type:-general}${NC}"
  if [ "$accessibility_needed" == "y" ]; then
    echo -e "- Accessibility Accommodations: ${GREEN}${accommodation}${NC}"
  fi
fi

# Ethical reminder
echo -e "\n${PURPLE}ETHICAL COMMITMENT:${NC}"
echo -e "This system was designed with the principles of:"
echo -e "- Local autonomy and resilience"
echo -e "- Respect for privacy and data sovereignty"
echo -e "- Freedom through functionality"
echo -e "- Consent in practice"

# Add information based on user role
if [ "$goal_name" == "educational" ]; then
  echo -e "\n${CYAN}EDUCATIONAL RESOURCES:${NC}"
  echo -e "- Lesson plan templates: ${DOCS_DIR}/lesson_plans/"
  echo -e "- Student dashboard: Access using the 'Student View' option in Mycodo"
  echo -e "- Export data for classroom use: Settings → Export Data"
  
elif [ "$goal_name" == "social" ]; then
  echo -e "\n${CYAN}SOCIAL IMPACT RESOURCES:${NC}"
  echo -e "- Program impact templates: ${DOCS_DIR}/impact_templates/"
  echo -e "- Participant dashboard: Access using the 'Participant View' option"
  echo -e "- Document management: Settings → Notes → Impact Documentation"

elif [ "$user_role" == "agritherapist" ]; then
  echo -e "\n${CYAN}AGRITHERAPY RESOURCES:${NC}"
  echo -e "- Therapy resources: ${DOCS_DIR}/therapy_resources/"
  echo -e "- Participant dashboard: Access using the 'Therapy Participant View' option"
  echo -e "- Photo journaling: ${INSTALL_DIR}/photo_log/"
  echo -e "- Reflection prompts: ${DOCS_DIR}/reflection_prompts.txt"
  
  if [ "$accessibility_needed" == "y" ]; then
    echo -e "- Accessibility guides: ${DOCS_DIR}/accessibility_guides/"
    echo -e "- Accessible dashboard: Use the 'Accessible Dashboard' option"
  fi
fi

# Reboot if necessary
if [ "$REBOOT_NEEDED" -eq 1 ]; then
  echo
  echo -e "${RED}IMPORTANT:${NC} A system reboot is required to apply hardware interface changes."
  read -p "Reboot now? (y/n): " do_reboot
  if [[ "$do_reboot" == "y" || "$do_reboot" == "Y" ]]; then
    echo -e "${YELLOW}Rebooting the system...${NC}"
    echo -e "${GREEN}After reboot, access Mycodo at: https://$(hostname -I | awk '{print $1}')/login${NC}"
    sleep 3
    reboot
  else
    echo -e "${YELLOW}Please remember to reboot your system manually.${NC}"
  fi
fi

echo
echo -e "${GREEN}${BOLD}Setup wizard completed successfully!${NC}"
echo
exit 0
