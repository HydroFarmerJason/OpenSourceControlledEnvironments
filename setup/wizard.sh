#!/bin/bash
# Container Setup Wizard v0.1
# This modular script guides non-technical users through basic configuration
# for the controlled environment project. Each section is wrapped in a
# function for easier maintenance and translation.

CONFIG_LOG="$(dirname "$0")/../config/user_choices.json"

choose_role() {
  echo "Select your user role:"
  echo "1) Educator"
  echo "2) Technician"
  echo "3) Farmer"
  read -p "Choice [1-3]: " ans
  case $ans in
    1) ROLE="educator" ;;
    2) ROLE="technician" ;;
    3) ROLE="farmer" ;;
    *) ROLE="general" ;;
  esac
}

choose_goal() {
  echo "What is your primary goal?"
  echo "1) Education"
  echo "2) Production"
  echo "3) Research"
  read -p "Choice [1-3]: " ans
  case $ans in
    1) GOAL="education" ;;
    2) GOAL="production" ;;
    3) GOAL="research" ;;
    *) GOAL="demo" ;;
  esac
}

choose_hardware() {
  echo "Select hardware complexity:"
  echo "1) Basic Monitoring"
  echo "2) Complete Farm Control"
  read -p "Choice [1-2]: " ans
  case $ans in
    2) HARDWARE="complete_farm_control" ;;
    *) HARDWARE="basic_monitoring" ;;
  esac
}

choose_privacy() {
  echo "Choose privacy level:"
  echo "1) Local only"
  echo "2) Local with backups"
  read -p "Choice [1-2]: " ans
  case $ans in
    2) PRIVACY="backup" ;;
    *) PRIVACY="local" ;;
  esac
}

save_config() {
  mkdir -p "$(dirname "$CONFIG_LOG")"
  cat > "$CONFIG_LOG" <<EOC
{
  "user_role": "$ROLE",
  "primary_goal": "$GOAL",
  "system_type": "$HARDWARE",
  "privacy_mode": "$PRIVACY"
}
EOC
  echo "Configuration saved to $CONFIG_LOG"
}

main() {
  choose_role
  choose_goal
  choose_hardware
  choose_privacy
  save_config
}

main "$@"
