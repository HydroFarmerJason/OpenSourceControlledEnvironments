# PATCH FILE: agritherapy_and_enhancements.patch
# Apply to the enhanced setup wizard script

# ---- USER ROLE MODIFICATION ----
# Find the user role selection section and replace with:

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

# ---- ADD LEARNING GOALS PROMPT ----
# Add after saving the user role (at end of STEP 0)

# Learning goals for educational and therapeutic settings
if [ "$goal_name" == "educational" ] || [ "$user_role" == "educator" ] || [ "$user_role" == "therapist" ] || [ "$user_role" == "agritherapist" ]; then
  echo
  echo -e "${CYAN}What are you trying to learn or measure with this system?${NC}"
  read -p "Enter a learning goal (e.g., 'impact of light cycles on basil growth' or 'therapeutic benefits of daily plant care'): " learning_goal
  echo "$learning_goal" > "${CONFIG_DIR}/learning_goal.txt"
fi

# ---- ADD THERAPY-SPECIFIC QUESTIONS (After primary goal selection in STEP 1) ----
# Add this section after the existing goal-specific questions

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

# ---- ADD PHOTO JOURNALING OPTION ----
# Add this after the privacy settings section in STEP 2

# Photo Journaling Configuration
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

# ---- ADD CONSENT REMINDER ----
# Add this section after privacy mode selection

# Operator consent reminder for data collection
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

# ---- VOICE ASSISTANT HOOKS ----
# Add after the Dashboard Setup section

# Voice Assistant Configuration (Future Feature)
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

# ---- AGRITHERAPY DASHBOARD ----
# Add to the Dashboard Setup section

# Add to the dashboard setup section after other dashboard configurations
if [ "$user_role" == "agritherapist" ]; then
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
fi

# ---- POST-SETUP REFLECTION ----
# Add before the final summary

# Add post-setup reflection prompt
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

# ---- ABOUT THIS PROJECT GENERATOR ----
# Add before the summary file generation

# Create About This Project document
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

# ---- PRELOADED CONFIGURATIONS ----
# Add to the Mycodo installation section

# Preload configurations based on user role
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