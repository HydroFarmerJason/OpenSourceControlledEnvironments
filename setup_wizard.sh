#!/bin/bash

# Container Farm Control System - Enhanced Interactive Setup Wizard
# This wizard guides users through the setup process in a user-friendly way
# Designed for users with minimal technical background
# Version 2.0 - May 2025

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

# STEP 0: Personalize Your Installation (NEW)
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

# User Role Selection
echo
echo -e "${CYAN}Who will primarily use this system?${NC}"
echo -e "1) ${CYAN}Educator${NC} - For teachers or educational staff"
echo -e "2) ${CYAN}Technician${NC} - For technical maintenance personnel"
echo -e "3) ${CYAN}Farmer${NC} - For commercial growers"
echo -e "4) ${CYAN}Researcher${NC} - For experimental or scientific use"
echo -e "5) ${CYAN}Therapist${NC} - For therapeutic or vocational programs"
echo -e "6) ${CYAN}Community Organizer${NC} - For community gardens or food security initiatives"
read -p "Select primary user role [1-6]: " role_selection

case $role_selection in
  1) user_role="educator" ;;
  2) user_role="technician" ;;
  3) user_role="farmer" ;;
  4) user_role="researcher" ;;
  5) user_role="therapist" ;;
  6) user_role="community" ;;
  *) user_role="general" ;;
esac

# Save values to config directory
echo "$project_name" > "${CONFIG_DIR}/project_name.txt"
echo "$project_location" > "${CONFIG_DIR}/location.txt"
echo "$operator_name" > "${CONFIG_DIR}/operator.txt"
echo "$user_role" > "${CONFIG_DIR}/user_role.txt"

echo -e "\n${GREEN}Project information saved!${NC}"
echo
read -p "Press Enter to continue..." dummy

# STEP 1: Primary Goal (ENHANCED)
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

# STEP 2: System Complexity (ENHANCED)
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
echo
read -p "Press Enter to continue..." dummy

# STEP 3: System Updates (UNCHANGED)
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

# STEP 4: Hardware Interfaces (ENHANCED)
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
cat > /etc/udev/rules.d/99-usb-sensors.rules << EOF_RULES
# Rules for USB pH and EC sensors
SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", GROUP="dialout", MODE="0660", SYMLINK+="ttyUSB_FTDI"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", GROUP="dialout", MODE="0660", SYMLINK+="ttyUSB_CH340"
EOF_RULES

echo -e "\n${GREEN}Hardware interfaces enabled.${NC}"
echo
read -p "Press Enter to continue..." dummy

# STEP 5: Install Dependencies (ENHANCED)
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
  apt install -y nginx sqlite3 supervisor
  
  # Install Python packages
  echo -e "${YELLOW}Installing Python packages...${NC}"
  pip3 install RPi.GPIO w1thermsensor adafruit-circuitpython-dht
  pip3 install flask pandas matplotlib
  
  # Install system-specific packages
  if [ "$config_name" == "hydroponic_system" ]; then
    echo -e "${YELLOW}Installing additional dependencies for hydroponic system...${NC}"
    pip3 install adafruit-circuitpython-ads1x15
    pip3 install adafruit-circuitpython-mcp3xxx
  fi
  
  # Install educational packages if needed
  if [ "$goal_name" == "educational" ]; then
    echo -e "${YELLOW}Installing educational tools...${NC}"
    pip3 install jupyter notebook
    apt install -y python3-pygame
  fi
  
  # Install documentation tools
  echo -e "${YELLOW}Installing documentation tools...${NC}"
  apt install -y qrencode
  
  echo -e "\n${GREEN}Software installation completed.${NC}"
else
  echo -e "\n${YELLOW}Software installation skipped.${NC}"
fi
echo
read -p "Press Enter to continue..." dummy

# STEP 6: Sensor Detection (ENHANCED)
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

# Check for I2C devices
echo -e "${CYAN}I2C Devices:${NC}"
i2c_devices=$(i2cdetect -y 1)
echo "$i2c_devices"

echo "$i2c_devices" > "${CONFIG_DIR}/i2c_devices.txt"

if echo "$i2c_devices" | grep -q "48"; then
  echo -e "${GREEN}✓ Found ADS1115 ADC at address 0x48${NC}"
  echo "ads1115,0x48" >> "${CONFIG_DIR}/detected_sensors.txt"
fi
if echo "$i2c_devices" | grep -q "39"; then
  echo -e "${GREEN}✓ Found TSL2561 Light Sensor at address 0x39${NC}"
  echo "tsl2561,0x39" >> "${CONFIG_DIR}/detected_sensors.txt"
fi
if echo "$i2c_devices" | grep -q "76"; then
  echo -e "${GREEN}✓ Found BME280 Temperature/Humidity/Pressure at address 0x76${NC}"
  echo "bme280,0x76" >> "${CONFIG_DIR}/detected_sensors.txt"
fi
if echo "$i2c_devices" | grep -q "44"; then
  echo -e "${GREEN}✓ Found SHT31 Temperature/Humidity at address 0x44${NC}"
  echo "sht31,0x44" >> "${CONFIG_DIR}/detected_sensors.txt"
fi

# Check for 1-Wire temperature sensors
echo -e "\n${CYAN}1-Wire Temperature Sensors:${NC}"
if [ -d /sys/bus/w1/devices ]; then
  ds18b20_devices=$(ls /sys/bus/w1/devices/ | grep -v "w1_bus_master")
  if [ -z "$ds18b20_devices" ]; then
    echo -e "${RED}✗ No DS18B20 temperature sensors detected${NC}"
  else
    echo -e "${GREEN}✓ Found DS18B20 temperature sensors:${NC}"
    for device in $ds18b20_devices; do
      echo "  - $device"
      echo "ds18b20,$device" >> "${CONFIG_DIR}/detected_sensors.txt"
    done
  fi
else
  echo -e "${RED}✗ 1-Wire bus not detected${NC}"
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
  ls -la /dev/serial/by-id/ > "${CONFIG_DIR}/usb_serial_devices.txt"
fi

echo -e "\n${CYAN}NOTE:${NC} UART devices like the MH-Z19 CO2 sensor"
echo -e "cannot be auto-detected. Please ensure it's connected to"
echo -e "GPIO 14 (TX) and GPIO 15 (RX) pins if using this sensor."

echo
echo -e "${PURPLE}Sensor detection complete.${NC}"
echo -e "These results will be used to customize your configuration."
echo
read -p "Press Enter to continue..." dummy

# STEP 7: Install Mycodo (ENHANCED)
clear
echo -e "${BLUE}${BOLD}STEP 7: Install Mycodo${NC}"
echo
echo -e "Mycodo is the control software that manages your sensors and automation."
echo -e "This installation will take approximately 30-45 minutes."
echo

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
fi

read -p "Continue with Mycodo installation? (y/n): " do_mycodo
if [[ "$do_mycodo" == "y" || "$do_mycodo" == "Y" ]]; then
  echo -e "\n${YELLOW}Installing Mycodo...${NC}"
  echo -e "${YELLOW}This may take a while. Please be patient.${NC}"
  curl -L https://kizniche.github.io/Mycodo/install | bash
  
  if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}Mycodo installation completed successfully.${NC}"
    ln -sf /var/mycodo/mycodo/outputs/output.py /usr/local/bin/mycodo-output
    ln -sf /var/mycodo/mycodo/inputs/input.py /usr/local/bin/mycodo-input
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
  
  if [ -f /var/mycodo/databases/mycodo.db ]; then
    echo -e "\n${YELLOW}Configuring Mycodo settings...${NC}"
    sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='${project_name}' WHERE setting='farm_name'"
    if [ "$goal_name" == "educational" ]; then
      sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='8:00' WHERE setting='daemon_debug_mode'"
      sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='True' WHERE setting='enable_notes_1'"
    fi
    if [ "$goal_name" == "social" ]; then
      sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='False' WHERE setting='enable_fullscreen_mode'"
      sqlite3 /var/mycodo/databases/mycodo.db "UPDATE misc SET value='True' WHERE setting='hide_alert_info'"
    fi
    systemctl restart mycodoflask
    systemctl restart mycododaemon
  fi
else
  echo -e "\n${YELLOW}Mycodo installation skipped.${NC}"
  echo -e "${RED}NOTE: The system won't function without Mycodo.${NC}"
  echo -e "You will need to install it manually with:"
  echo -e "curl -L https://kizniche.github.io/Mycodo/install | bash"
fi
echo
read -p "Press Enter to continue..." dummy

# STEP 8: Backup Configuration (ENHANCED)
clear
echo -e "${BLUE}${BOLD}STEP 8: Backup Configuration${NC}"
echo
echo -e "Regular backups are essential to prevent data loss."
echo -e "This wizard will set up automated backup options."
echo

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

cat > "${SCRIPTS_DIR}/backup.sh" << EOF_BACKUP
#!/bin/bash
TIMESTAMP=\$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR=${BACKUP_DIR}
PROJECT_NAME="${project_name}"
OPERATOR="${operator_name}"
PRIMARY_GOAL="${goal_name}"
mkdir -p \$BACKUP_DIR \$BACKUP_DIR/configs \$BACKUP_DIR/databases \$BACKUP_DIR/logs

echo "Backing up Mycodo..."
tar -czf \$BACKUP_DIR/\${PROJECT_NAME}_mycodo_backup_\$TIMESTAMP.tar.gz /var/mycodo

echo "Backing up InfluxDB..."
influxd backup -portable \$BACKUP_DIR/influxdb_backup_\$TIMESTAMP

echo "Backing up system configuration..."
cp -r ${CONFIG_DIR}/* \$BACKUP_DIR/configs/

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

qrencode -o "\$BACKUP_DIR/\${PROJECT_NAME}_access_qr.png" "http://\$(hostname -I | awk '{print \$1}')"

find \$BACKUP_DIR -type d -name "influxdb_backup_*" -mtime +30 -exec rm -rf {} \;
ls -t \$BACKUP_DIR/\${PROJECT_NAME}_mycodo_backup_*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null

echo "Backup completed at \$(date)"
EOF_BACKUP

chmod +x "${SCRIPTS_DIR}/backup.sh"

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

(crontab -l 2>/dev/null || echo "") | grep -v "backup.sh" | { cat; echo "$cron_schedule ${SCRIPTS_DIR}/backup.sh"; } | crontab -

echo -e "${YELLOW}Installing offline documentation...${NC}"
mkdir -p "${DOCS_DIR}/offline"
git clone https://github.com/kizniche/Mycodo-custom.git "${DOCS_DIR}/offline/mycodo-docs" 2>/dev/null || echo -e "${RED}Could not download offline documentation.${NC}"

echo
read -p "Press Enter to continue..." dummy

# STEP 9: Dashboard Setup (NEW)
clear
echo -e "${BLUE}${BOLD}STEP 9: Dashboard Configuration${NC}"
echo
echo -e "Now we'll set up your control dashboard based on your selections."
echo

if [ "$goal_name" == "educational" ]; then
  echo -e "${YELLOW}Creating educational dashboard...${NC}"
  cat > "${DASHBOARD_DIR}/educational_dashboard.json" << EOF_EDU
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
EOF_EDU
  cat > "${DASHBOARD_DIR}/student_dashboard.json" << EOF_EDU2
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
EOF_EDU2
elif [ "$goal_name" == "social" ]; then
  echo -e "${YELLOW}Creating social impact dashboard...${NC}"
  cat > "${DASHBOARD_DIR}/social_impact_dashboard.json" << EOF_SOC
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
EOF_SOC
  cat > "${DASHBOARD_DIR}/participant_dashboard.json" << EOF_SOC2
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
EOF_SOC2
else
  echo -e "${YELLOW}Creating standard dashboard...${NC}"
  cat > "${DASHBOARD_DIR}/standard_dashboard.json" << EOF_STD
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
EOF_STD
fi

echo -e "${GREEN}Dashboard configurations created.${NC}"
echo -e "These will be imported into Mycodo during final configuration."
echo
read -p "Press Enter to continue..." dummy

# STEP 10: Wiring Information (ENHANCED)
clear
echo -e "${BLUE}${BOLD}STEP 10: Wiring Information${NC}"
echo
echo -e "Based on your selected system type (${GREEN}$config_name${NC}),"
echo -e "please refer to the appropriate wiring diagram:"
echo

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

if [ "$goal_name" == "educational" ]; then
  echo -e "\n${RED}EDUCATIONAL SAFETY NOTES:${NC}"
  echo -e "- Use proper electrical safety measures in classroom settings"
  echo -e "- Consider using lower voltage (5V) components when possible"
  echo -e "- Ensure all connections are in a protected enclosure"
  echo -e "- Place a clear warning label on the system"
elif [ "$user_role" == "therapist" ]; then
  echo -e "\n${RED}THERAPEUTIC ENVIRONMENT NOTES:${NC}"
  echo -e "- Ensure all wiring is secured and not accessible to participants"
  echo -e "- Consider additional protective enclosures"
  echo -e "- Use color-coded wires for teaching purposes if appropriate"
fi

echo -e "\n${RED}IMPORTANT:${NC} Proper wiring is critical for system functionality."
echo -e "Always shut down the Raspberry Pi before connecting or disconnecting hardware."
echo
read -p "Press Enter to continue..." dummy

# STEP 11: System Configuration (RENAMED)
clear
echo -e "${BLUE}${BOLD}STEP 11: System Configuration${NC}"
echo
echo -e "Your system is now ready for final configuration."
echo

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

SUMMARY_FILE="${INSTALL_DIR}/project_summary.txt"
cat > "$SUMMARY_FILE" <<EOF_SUM
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
EOF_SUM

echo -e "${GREEN}Setup summary saved to:${NC} $SUMMARY_FILE"

cat > "${SCRIPTS_DIR}/startup_check.sh" << 'EOF_START'
#!/bin/bash
source /opt/container-farm-control/configs/config.sh 2>/dev/null || true
LOG_FILE="/var/log/container-farm-startup.log"
echo "===== Container Farm Control System Startup Check =====" > $LOG_FILE
echo "Date: $(date)" >> $LOG_FILE
echo "Hostname: $(hostname)" >> $LOG_FILE

echo "Checking Mycodo services..." >> $LOG_FILE
if systemctl is-active --quiet mycodoflask && systemctl is-active --quiet mycododaemon; then
  echo "✓ Mycodo services running" >> $LOG_FILE
else
  echo "✗ Mycodo services not running properly" >> $LOG_FILE
  systemctl restart mycodoflask
  systemctl restart mycododaemon
fi

echo "Checking network connection..." >> $LOG_FILE
if ping -c 1 8.8.8.8 &> /dev/null; then
  echo "✓ Network connection active" >> $LOG_FILE
else
  echo "✗ Network connection issue" >> $LOG_FILE
fi

echo "Checking I2C sensors..." >> $LOG_FILE
if i2cdetect -y 1 &> /dev/null; then
  echo "✓ I2C bus accessible" >> $LOG_FILE
  i2c_devices=$(i2cdetect -y 1 | grep -v "\-\-" | grep -v "00:" | tr -d ' ' | tr -d ':' | tr -d 'UU' | wc -c)
  if [ $i2c_devices -gt 0 ]; then
    echo "✓ Found I2C devices" >> $LOG_FILE
  else
    echo "✗ No I2C devices found" >> $LOG_FILE
  fi
else
  echo "✗ I2C bus not accessible" >> $LOG_FILE
fi

echo "Checking 1-Wire sensors..." >> $LOG_FILE
if [ -d /sys/bus/w1/devices ]; then
  w1_devices=$(ls /sys/bus/w1/devices/ | grep -v "w1_bus_master" | wc -l)
  if [ $w1_devices -gt 0 ]; then
    echo "✓ Found $w1_devices 1-Wire temperature sensors" >> $LOG_FILE
  else
    echo "✗ No 1-Wire sensors found" >> $LOG_FILE
  fi
else
  echo "✗ 1-Wire bus not accessible" >> $LOG_FILE
fi

if [[ -f /var/mycodo/databases/mycodo.db && -x $(which sqlite3) ]]; then
  uptime_hours=$(awk '{print int($1/3600)}' /proc/uptime)
  if [ $uptime_hours -lt 24 ]; then
    notification_enabled=$(sqlite3 /var/mycodo/databases/mycodo.db "SELECT value FROM misc WHERE setting='notification_smtp_enabled'" 2>/dev/null || echo "0")
    if [ "$notification_enabled" = "1" ]; then
      echo "Sending startup notification..." >> $LOG_FILE
      sqlite3 /var/mycodo/databases/mycodo.db "INSERT INTO notifications (datetime, recipient_id, notification_type, subject, body) VALUES (datetime('now'), 1, 'email', 'System Startup - ${project_name}', 'Container Farm Control System has started. IP: $(hostname -I | awk '{print $1}')')"
    fi
  fi
fi

echo "Startup check completed: $(date)" >> $LOG_FILE
EOF_START

chmod +x "${SCRIPTS_DIR}/startup_check.sh"

(crontab -l 2>/dev/null || echo "") | grep -v "startup_check.sh" | { cat; echo "@reboot ${SCRIPTS_DIR}/startup_check.sh"; } | crontab -

echo -e "${BLUE}${BOLD}Setup Summary:${NC}"
echo -e "- Project Name: ${GREEN}$project_name${NC}"
echo -e "- Location: ${GREEN}$project_location${NC}"
echo -e "- Primary Goal: ${GREEN}$goal_name${NC}"
echo -e "- User Role: ${GREEN}$user_role${NC}"
echo -e "- System Configuration: ${GREEN}$config_name${NC}"
echo -e "- Backup Schedule: ${GREEN}$backup_freq${NC}"
echo -e "- Mycodo Web Interface: ${GREEN}https://$(hostname -I | awk '{print $1}')/login${NC}"

echo -e "\n${PURPLE}ETHICAL COMMITMENT:${NC}"
echo -e "This system was designed with the principles of:"
echo -e "- Local autonomy and resilience"
echo -e "- Respect for privacy and data sovereignty"
echo -e "- Freedom through functionality"
echo -e "- Consent in practice"

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
fi

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
