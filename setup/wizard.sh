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
  echo "4) Researcher"
  echo "5) Therapist"
  echo "6) Agritherapist"
  echo "7) Community Organizer"
  read -p "Choice [1-7]: " ans
  case $ans in
    1) ROLE="educator" ;;
    2) ROLE="technician" ;;
    3) ROLE="farmer" ;;
    4) ROLE="researcher" ;;
    5) ROLE="therapist" ;;
    6) ROLE="agritherapist" ;;
    7) ROLE="community" ;;
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

choose_learning_goal() {
  if [ "$ROLE" = "educator" ] || [ "$ROLE" = "therapist" ] || [ "$ROLE" = "agritherapist" ]; then
    read -p "Learning or therapy goal (optional): " LEARNING_GOAL
  fi
}

choose_therapy_options() {
  if [ "$ROLE" = "agritherapist" ] || [ "$ROLE" = "therapist" ]; then
    read -p "Therapy type (group/individual): " THERAPY_TYPE
    read -p "Accessibility accommodations needed? (y/n): " ACCESS_NEEDED
    if [[ "$ACCESS_NEEDED" =~ ^[yY]$ ]]; then
      echo "1) Visual impairments"
      echo "2) Motor limitations"
      echo "3) Cognitive"
      echo "4) Multiple"
      read -p "Select accommodation [1-4]: " acc
      case $acc in
        1) ACCOMMODATION="visual" ;;
        2) ACCOMMODATION="motor" ;;
        3) ACCOMMODATION="cognitive" ;;
        4) ACCOMMODATION="multiple" ;;
        *) ACCOMMODATION="general" ;;
      esac
    fi
  fi
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

choose_photo_journaling() {
  read -p "Enable daily photo journaling? (y/n): " PHOTO_JOURNAL
}

consent_reminder() {
  if [[ "$PRIVACY" != "local" || "$PHOTO_JOURNAL" =~ ^[yY]$ ]]; then
    echo "Data collection features selected." 
    read -p "Confirm all participants are informed (y/n): " CONSENT_CONFIRMED
  fi
}

save_config() {
  mkdir -p "$(dirname "$CONFIG_LOG")"
  cat > "$CONFIG_LOG" <<EOC
{
  "user_role": "$ROLE",
  "primary_goal": "$GOAL",
  "system_type": "$HARDWARE",
  "privacy_mode": "$PRIVACY",
  "learning_goal": "$LEARNING_GOAL",
  "therapy_type": "$THERAPY_TYPE",
  "accommodation": "$ACCOMMODATION",
  "photo_journaling": "$PHOTO_JOURNAL",
  "consent_confirmed": "$CONSENT_CONFIRMED"
}
EOC
  echo "Configuration saved to $CONFIG_LOG"
}

main() {
  choose_role
  choose_goal
  choose_learning_goal
  choose_therapy_options
  choose_hardware
  choose_privacy
  choose_photo_journaling
  consent_reminder
  save_config
}

main "$@"
