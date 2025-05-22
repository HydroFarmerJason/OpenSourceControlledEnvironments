#!/bin/bash
# Container Farm Control System - Enhanced Setup Wizard
# Simplified reimplementation with key features

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"
BACKUP_DIR="${INSTALL_DIR}/backups"
DOCS_DIR="${INSTALL_DIR}/docs"
DASHBOARD_DIR="${INSTALL_DIR}/dashboards"

mkdir -p "$INSTALL_DIR" "$CONFIG_DIR" "$SCRIPTS_DIR" "$BACKUP_DIR" "$DOCS_DIR" "$DASHBOARD_DIR"

if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root${NC}"
  exit 1
fi

clear
echo -e "${BLUE}${BOLD}Container Farm Control System - Setup Wizard${NC}"
echo -e "This wizard will guide you through installing and configuring the system."
echo -e "${YELLOW}No technical experience required.${NC}\n"
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 0 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 0: Personalize Your Installation${NC}"
read -p "Project name: " project_name
read -p "Location: " project_location
read -p "Operator name: " operator_name

cat > "$CONFIG_DIR/project_name.txt" <<< "$project_name"
cat > "$CONFIG_DIR/location.txt" <<< "$project_location"
cat > "$CONFIG_DIR/operator.txt" <<< "$operator_name"

echo -e "\n${CYAN}Select user role${NC}"
echo "1) Educator"
echo "2) Technician"
echo "3) Farmer"
echo "4) Researcher"
echo "5) Therapist"
echo "6) Community Organizer"
read -p "Role [1-6]: " role
case $role in
 1) user_role=educator;;
 2) user_role=technician;;
 3) user_role=farmer;;
 4) user_role=researcher;;
 5) user_role=therapist;;
 6) user_role=community;;
 *) user_role=general;;
esac
cat > "$CONFIG_DIR/user_role.txt" <<< "$user_role"

echo -e "${GREEN}Project information saved.${NC}"
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 1 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 1: Primary Goal${NC}"
echo "1) Commercial Production"
echo "2) Educational"
echo "3) Social Impact"
echo "4) Research"
read -p "Goal [1-4]: " primary_goal
case $primary_goal in
 1) goal_name=commercial;;
 2) goal_name=educational;;
 3) goal_name=social;;
 4) goal_name=research;;
 *) goal_name=general;;
esac
cat > "$CONFIG_DIR/primary_goal.txt" <<< "$goal_name"

if [ "$goal_name" = "educational" ]; then
  read -p "Student involvement (y/n): " student_involvement
  read -p "Grade level: " grade_level
  echo "$student_involvement" > "$CONFIG_DIR/student_involvement.txt"
  echo "$grade_level" > "$CONFIG_DIR/grade_level.txt"
  mkdir -p "$DOCS_DIR/lesson_plans"
fi

if [ "$goal_name" = "social" ]; then
  read -p "Therapeutic program (y/n): " therapeutic
  echo "$therapeutic" > "$CONFIG_DIR/therapeutic.txt"
  mkdir -p "$DOCS_DIR/impact_templates"
fi

read -p "Experience with Linux or Raspberry Pi (y/n): " linux_exp
technical_level="beginner"
[[ "$linux_exp" =~ [Yy] ]] && technical_level="experienced"
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 2 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 2: System Complexity${NC}"
echo "1) Basic Monitoring"
echo "2) Complete Farm Control"
echo "3) Hydroponic System"
read -p "Configuration [1-3]: " system_type
case $system_type in
 1) config_name=basic_monitoring;;
 2) config_name=complete_farm_control;;
 3) config_name=hydroponic_system;;
 *) config_name=basic_monitoring;;
esac
cat > "$CONFIG_DIR/selected_config.txt" <<< "$config_name"

echo -e "${CYAN}Data privacy mode${NC}"
echo "1) Local Only"
echo "2) Backup Ready"
echo "3) Research Sharing"
read -p "Mode [1-3]: " privacy_mode
case $privacy_mode in
 2) privacy_mode=backup;;
 3) privacy_mode=research;;
 *) privacy_mode=local;;
esac
cat > "$CONFIG_DIR/privacy_mode.txt" <<< "$privacy_mode"
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 3 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 3: System Updates${NC}"
read -p "Run system updates? (y/n): " do_update
if [[ "$do_update" =~ [Yy] ]]; then
  apt update && apt upgrade -y
fi
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 4 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 4: Hardware Interfaces${NC}"
REBOOT_NEEDED=0
if [ "$(raspi-config nonint get_i2c)" -ne 0 ]; then
  raspi-config nonint do_i2c 0
  REBOOT_NEEDED=1
fi
if ! grep -q '^dtoverlay=w1-gpio' /boot/config.txt; then
  echo 'dtoverlay=w1-gpio' >> /boot/config.txt
  REBOOT_NEEDED=1
fi
if [ "$config_name" = "complete_farm_control" ] || [ "$goal_name" = "research" ]; then
  raspi-config nonint do_serial 0
  REBOOT_NEEDED=1
fi
if [ "$config_name" = "hydroponic_system" ]; then
  raspi-config nonint do_spi 0
  REBOOT_NEEDED=1
fi
cat > /etc/udev/rules.d/99-usb-sensors.rules <<'RULES'
SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", GROUP="dialout", MODE="0660", SYMLINK+="ttyUSB_FTDI"
SUBSYSTEM=="usb", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", GROUP="dialout", MODE="0660", SYMLINK+="ttyUSB_CH340"
RULES
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 5 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 5: Install Dependencies${NC}"
read -p "Install required packages? (y/n): " do_install
if [[ "$do_install" =~ [Yy] ]]; then
  apt install -y build-essential python3-dev python3-pip git python3-venv
  apt install -y i2c-tools python3-smbus ufw libgpiod2
  apt install -y nginx sqlite3 supervisor qrencode
  pip3 install RPi.GPIO w1thermsensor adafruit-circuitpython-dht flask pandas matplotlib
  [[ "$config_name" = "hydroponic_system" ]] && pip3 install adafruit-circuitpython-ads1x15 adafruit-circuitpython-mcp3xxx
  [[ "$goal_name" = "educational" ]] && pip3 install jupyter notebook
fi
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 6 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 6: Sensor Detection${NC}"
i2c_devices=$(i2cdetect -y 1)
echo "$i2c_devices" > "$CONFIG_DIR/i2c_devices.txt"
if echo "$i2c_devices" | grep -q "76"; then
  echo "BME280 detected" >> "$CONFIG_DIR/detected_sensors.txt"
fi
if [ -d /sys/bus/w1/devices ]; then
  ls /sys/bus/w1/devices/ | grep -v w1_bus_master > "$CONFIG_DIR/1wire.txt"
fi
lsusb > "$CONFIG_DIR/usb_devices.txt"
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 7 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 7: Install Mycodo${NC}"
read -p "Install Mycodo? (y/n): " do_mycodo
if [[ "$do_mycodo" =~ [Yy] ]]; then
  curl -L https://kizniche.github.io/Mycodo/install | bash
  usermod -a -G mycodo pi
fi
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 8 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 8: Backup Configuration${NC}"
echo "1) Weekly"
echo "2) Daily"
echo "3) Monthly"
read -p "Schedule [1-3]: " backup_schedule
case $backup_schedule in
 2) cron_schedule="0 1 * * *";;
 3) cron_schedule="0 3 1 * *";;
 *) cron_schedule="0 2 * * 0";;
esac
cat > "$SCRIPTS_DIR/backup.sh" <<'BKSCRIPT'
#!/bin/bash
BACKUP_DIR=/opt/container-farm-control/backups
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/mycodo_$TIMESTAMP.tar.gz" /var/mycodo
BKSCRIPT
chmod +x "$SCRIPTS_DIR/backup.sh"
(crontab -l 2>/dev/null; echo "$cron_schedule $SCRIPTS_DIR/backup.sh") | crontab -
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 9 ----------------------------
clear
echo -e "${BLUE}${BOLD}STEP 9: Dashboard Configuration${NC}"
case $goal_name in
 educational)
  cat > "$DASHBOARD_DIR/educational.json" <<'EDU'
{"name":"Educational Dashboard"}
EDU
  ;;
 social)
  cat > "$DASHBOARD_DIR/social.json" <<'SOC'
{"name":"Social Dashboard"}
SOC
  ;;
 *)
  cat > "$DASHBOARD_DIR/standard.json" <<'STD'
{"name":"Standard Dashboard"}
STD
  ;;
esac
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 10 ---------------------------
clear
echo -e "${BLUE}${BOLD}STEP 10: Wiring Information${NC}"
# (Display wiring info simplified)
echo "Refer to schematics for wiring: schematics/wiring_diagrams/${config_name}_wiring.svg"
read -p "Press Enter to continue..." dummy

# ------------------------- STEP 11 ---------------------------
clear
echo -e "${BLUE}${BOLD}STEP 11: Final Configuration${NC}"
qrencode -o "$INSTALL_DIR/dashboard_qr.png" "http://$(hostname -I | awk '{print $1}')"
cat > "$INSTALL_DIR/project_summary.txt" <<EOF_SUM
Project: $project_name
Location: $project_location
Role: $user_role
Goal: $goal_name
Configuration: $config_name
EOF_SUM

cat > "$SCRIPTS_DIR/startup_check.sh" <<'CHECK'
#!/bin/bash
LOG=/var/log/container-farm-startup.log
if systemctl is-active --quiet mycododaemon; then
  echo "Mycodo running" > $LOG
else
  echo "Mycodo NOT running" > $LOG
fi
CHECK
chmod +x "$SCRIPTS_DIR/startup_check.sh"
(crontab -l 2>/dev/null; echo "@reboot $SCRIPTS_DIR/startup_check.sh") | crontab -

if [ $REBOOT_NEEDED -eq 1 ]; then
  echo -e "${YELLOW}Reboot required to apply interface changes.${NC}"
fi

echo -e "${GREEN}${BOLD}Setup wizard completed!${NC}"
