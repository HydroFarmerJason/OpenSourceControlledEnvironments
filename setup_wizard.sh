#!/bin/bash
# Enhanced Container Farm Control System Setup Wizard
# Simplified implementation based on user-provided script

# Colors
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
  echo -e "${RED}Please run as root (sudo)${NC}"
  exit 1
fi

clear
cat <<BANNER
${BLUE}${BOLD}
============================================================
     Container Farm Control System - Interactive Setup
============================================================
${NC}
BANNER

echo "This wizard will guide you through configuration and installation."
echo -e "${YELLOW}No technical background is required!${NC}"

echo -e "${CYAN}This system was developed to preserve farmers' autonomy and local control.${NC}"
read -p "Press Enter to continue..." dummy

# Step 0 - project metadata
clear
printf "${BLUE}${BOLD}STEP 0: Personalize Your Installation${NC}\n\n"
read -p "Enter a project name: " project_name
read -p "Enter your location: " project_location
read -p "Enter operator name: " operator_name

echo -e "\nUser roles:\n 1) Educator\n 2) Technician\n 3) Farmer\n 4) Researcher\n 5) Therapist\n 6) Community Organizer"
read -p "Select primary user role [1-6]: " role_selection
case $role_selection in
 1) user_role="educator";;
 2) user_role="technician";;
 3) user_role="farmer";;
 4) user_role="researcher";;
 5) user_role="therapist";;
 6) user_role="community";;
 *) user_role="general";;
esac

echo "$project_name" > "$CONFIG_DIR/project_name.txt"
echo "$project_location" > "$CONFIG_DIR/location.txt"
echo "$operator_name" > "$CONFIG_DIR/operator.txt"
echo "$user_role" > "$CONFIG_DIR/user_role.txt"

echo -e "\n${GREEN}Project information saved!${NC}"
read -p "Press Enter to continue..." dummy

# Step 1 - primary goal
clear
printf "${BLUE}${BOLD}STEP 1: Primary Goal${NC}\n\n"
echo "1) Commercial Production"
echo "2) Educational"
echo "3) Social Impact"
echo "4) Research"
read -p "Select goal [1-4]: " primary_goal
case $primary_goal in
 1) goal_name="commercial";;
 2) goal_name="educational";;
 3) goal_name="social";;
 4) goal_name="research";;
 *) goal_name="general";;
esac

echo "$goal_name" > "$CONFIG_DIR/primary_goal.txt"

read -p "Do you have prior Linux experience? (y/n): " linux_exp
technical_level="beginner"
[[ "$linux_exp" =~ [Yy] ]] && technical_level="experienced"
read -p "Press Enter to continue..." dummy

# Step 2 - system complexity
clear
printf "${BLUE}${BOLD}STEP 2: Choose your system complexity${NC}\n\n"
echo "1) Basic Monitoring"
echo "2) Complete Farm Control"
echo "3) Hydroponic System"
read -p "Select type [1-3]: " system_type
case $system_type in
 1) config_name="basic_monitoring";;
 2) config_name="complete_farm_control";;
 3) config_name="hydroponic_system";;
 *) config_name="basic_monitoring";;
esac

echo "$config_name" > "$CONFIG_DIR/selected_config.txt"

echo -e "${CYAN}Data Privacy Settings:${NC}\n1) Local Only\n2) Backup Ready\n3) Research Sharing"
read -p "Select privacy preference [1-3, default=1]: " privacy_option
case $privacy_option in
 2) privacy_mode="backup";;
 3) privacy_mode="research";;
 *) privacy_mode="local";;
esac

echo "$privacy_mode" > "$CONFIG_DIR/privacy_mode.txt"
read -p "Press Enter to continue..." dummy

# Step 3 - updates
clear
printf "${BLUE}${BOLD}STEP 3: System Updates${NC}\n\n"
read -p "Continue with system updates? (y/n): " do_update
if [[ "$do_update" =~ [Yy] ]]; then
  apt update && apt upgrade -y
fi
read -p "Press Enter to continue..." dummy

# Step 4 - enable interfaces (simplified)
clear
printf "${BLUE}${BOLD}STEP 4: Hardware Interfaces${NC}\n\n"
REBOOT_NEEDED=0
if [ "$(raspi-config nonint get_i2c)" -ne 0 ]; then
  raspi-config nonint do_i2c 0
  REBOOT_NEEDED=1
fi
if ! grep -q '^dtoverlay=w1-gpio' /boot/config.txt; then
  echo 'dtoverlay=w1-gpio' >> /boot/config.txt
  REBOOT_NEEDED=1
fi
read -p "Press Enter to continue..." dummy

# Remaining steps omitted for brevity in this repository example
# Refer to the full script in project documentation for advanced features

if [ "$REBOOT_NEEDED" -eq 1 ]; then
  echo -e "${YELLOW}A reboot is required to apply changes.${NC}"
fi

echo -e "${GREEN}${BOLD}Setup wizard completed!${NC}"
