#!/bin/bash
# Container Farm Control System - Multilingual Support Framework
# This script sets up the foundation for multilingual support
# Install in SCRIPTS_DIR

INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
LANG_DIR="${INSTALL_DIR}/i18n"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"

# Create i18n directory
mkdir -p "${LANG_DIR}"

# Default to English
echo "en" > "${CONFIG_DIR}/language.txt"

# Create a list of supported languages
cat > "${CONFIG_DIR}/supported_languages.json" << EOF
{
  "languages": [
    {
      "code": "en",
      "name": "English",
      "native_name": "English",
      "default": true
    },
    {
      "code": "es",
      "name": "Spanish",
      "native_name": "Español",
      "default": false
    },
    {
      "code": "fr",
      "name": "French",
      "native_name": "Français",
      "default": false
    }
  ]
}
EOF

# Create the translation function for bash scripts
cat > "${SCRIPTS_DIR}/translate.sh" << 'EOF'
#!/bin/bash
# Translation utility for bash scripts

INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
LANG_DIR="${INSTALL_DIR}/i18n"

# Get the current language
CURRENT_LANG=$(cat "${CONFIG_DIR}/language.txt" 2>/dev/null || echo "en")

# Function to get translated text
# Usage: translate "key" "default_text"
translate() {
    local key="$1"
    local default="$2"
    
    # If language file exists, try to get the translation
    if [ -f "${LANG_DIR}/${CURRENT_LANG}.json" ]; then
        # Try to extract the translation using jq if available
        if command -v jq >/dev/null 2>&1; then
            translation=$(jq -r ".$key // \"\"" "${LANG_DIR}/${CURRENT_LANG}.json" 2>/dev/null)
            if [ -n "$translation" ] && [ "$translation" != "null" ]; then
                echo "$translation"
                return
            fi
        else
            # Fallback to grep/sed if jq is not available
            translation=$(grep "\"$key\":" "${LANG_DIR}/${CURRENT_LANG}.json" | sed -E 's/.*"'"$key"'"\s*:\s*"(.*)".*/\1/')
            if [ -n "$translation" ]; then
                echo "$translation"
                return
            fi
        fi
    fi
    
    # Return default text if no translation found
    echo "$default"
}

# Export the function if this script is sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    export -f translate
fi

# If run directly, translate the provided key
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -lt 1 ]; then
        echo "Usage: translate.sh <key> [default_text]"
        exit 1
    fi
    
    key="$1"
    default="${2:-$key}"
    
    translate "$key" "$default"
fi
EOF

chmod +x "${SCRIPTS_DIR}/translate.sh"

# Create Python translation module
cat > "${SCRIPTS_DIR}/translate.py" << 'EOF'
#!/usr/bin/env python3
"""
Translation utility for Python scripts in the Container Farm Control System
"""

import os
import json
import sys

INSTALL_DIR = "/opt/container-farm-control"
CONFIG_DIR = os.path.join(INSTALL_DIR, "configs")
LANG_DIR = os.path.join(INSTALL_DIR, "i18n")

def get_current_language():
    """Get the current language code from config"""
    try:
        with open(os.path.join(CONFIG_DIR, "language.txt"), "r") as f:
            return f.read().strip()
    except:
        return "en"  # Default to English

def load_language_file(lang_code):
    """Load the language JSON file for the given language code"""
    lang_file = os.path.join(LANG_DIR, f"{lang_code}.json")
    if os.path.exists(lang_file):
        try:
            with open(lang_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

class Translator:
    """Translation handler class"""
    
    def __init__(self, lang_code=None):
        """Initialize with optional language code, otherwise use system default"""
        self.lang_code = lang_code or get_current_language()
        self.translations = load_language_file(self.lang_code)
        
        # Load English as fallback for missing translations
        if self.lang_code != "en":
            self.fallback = load_language_file("en")
        else:
            self.fallback = {}
    
    def translate(self, key, default=None):
        """
        Translate a key to the current language
        
        Args:
            key: The translation key
            default: Default text if no translation found (if None, uses key)
            
        Returns:
            Translated text
        """
        # If default is None, use key as default
        if default is None:
            default = key
            
        # Check for translation in current language
        if key in self.translations:
            return self.translations[key]
            
        # Check fallback language
        if key in self.fallback:
            return self.fallback[key]
            
        # Return default text
        return default
    
    # Shorthand method
    def t(self, key, default=None):
        """Shorthand for translate()"""
        return self.translate(key, default)

# Create singleton instance
_translator = Translator()

# Expose translate and t as module-level functions
def translate(key, default=None):
    """Translate using the default translator"""
    return _translator.translate(key, default)

def t(key, default=None):
    """Shorthand for translate()"""
    return translate(key, default)

# Command-line interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: translate.py <key> [default_text]")
        sys.exit(1)
    
    key = sys.argv[1]
    default = sys.argv[2] if len(sys.argv) > 2 else key
    
    print(translate(key, default))
EOF

chmod +x "${SCRIPTS_DIR}/translate.py"

# Create empty language files with sample translations
mkdir -p "${LANG_DIR}"

# English (base language)
cat > "${LANG_DIR}/en.json" << EOF
{
  "welcome_message": "Welcome to your Container Farm Control System!",
  "setup_complete": "Setup complete. Your farm system is ready.",
  "sensor_error": "Sensor error detected. Please check connections.",
  "water_level_low": "Water level is low. Please refill the reservoir.",
  "optimal_conditions": "Plants are growing in optimal conditions.",
  "light_on": "Lights turned ON",
  "light_off": "Lights turned OFF",
  "pump_on": "Water pump turned ON",
  "pump_off": "Water pump turned OFF",
  "next": "Next",
  "back": "Back",
  "save": "Save",
  "cancel": "Cancel",
  "settings": "Settings",
  "dashboard": "Dashboard",
  "reports": "Reports",
  "alerts": "Alerts",
  "temperature": "Temperature",
  "humidity": "Humidity",
  "water_level": "Water Level",
  "light_intensity": "Light Intensity"
}
EOF

# Spanish (example translation)
cat > "${LANG_DIR}/es.json" << EOF
{
  "welcome_message": "¡Bienvenido a su Sistema de Control de Cultivo en Contenedor!",
  "setup_complete": "Configuración completa. Su sistema de cultivo está listo.",
  "sensor_error": "Error de sensor detectado. Por favor, verifique las conexiones.",
  "water_level_low": "El nivel de agua es bajo. Por favor, rellene el depósito.",
  "optimal_conditions": "Las plantas están creciendo en condiciones óptimas.",
  "light_on": "Luces ENCENDIDAS",
  "light_off": "Luces APAGADAS",
  "pump_on": "Bomba de agua ENCENDIDA",
  "pump_off": "Bomba de agua APAGADA",
  "next": "Siguiente",
  "back": "Atrás",
  "save": "Guardar",
  "cancel": "Cancelar",
  "settings": "Configuración",
  "dashboard": "Panel de control",
  "reports": "Informes",
  "alerts": "Alertas",
  "temperature": "Temperatura",
  "humidity": "Humedad",
  "water_level": "Nivel de agua",
  "light_intensity": "Intensidad de luz"
}
EOF

# French (example translation)
cat > "${LANG_DIR}/fr.json" << EOF
{
  "welcome_message": "Bienvenue dans votre Système de Contrôle de Culture en Conteneur !",
  "setup_complete": "Configuration terminée. Votre système de culture est prêt.",
  "sensor_error": "Erreur de capteur détectée. Veuillez vérifier les connexions.",
  "water_level_low": "Le niveau d'eau est bas. Veuillez remplir le réservoir.",
  "optimal_conditions": "Les plantes poussent dans des conditions optimales.",
  "light_on": "Lumières ALLUMÉES",
  "light_off": "Lumières ÉTEINTES",
  "pump_on": "Pompe à eau ALLUMÉE",
  "pump_off": "Pompe à eau ÉTEINTE",
  "next": "Suivant",
  "back": "Retour",
  "save": "Enregistrer",
  "cancel": "Annuler",
  "settings": "Paramètres",
  "dashboard": "Tableau de bord",
  "reports": "Rapports",
  "alerts": "Alertes",
  "temperature": "Température",
  "humidity": "Humidité",
  "water_level": "Niveau d'eau",
  "light_intensity": "Intensité lumineuse"
}
EOF

# Create a language switcher script
cat > "${SCRIPTS_DIR}/switch_language.sh" << 'EOF'
#!/bin/bash
# Language switcher utility

INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
LANG_DIR="${INSTALL_DIR}/i18n"

# List available languages
list_languages() {
    echo "Available languages:"
    echo "------------------"
    
    # Try to parse using jq if available
    if command -v jq >/dev/null 2>&1; then
        jq -r '.languages[] | "\(.code) - \(.name) (\(.native_name))"' "${CONFIG_DIR}/supported_languages.json" 2>/dev/null
    else
        # Simple grep fallback if jq isn't available
        grep -E '"code": "|"name": "|"native_name": "' "${CONFIG_DIR}/supported_languages.json" | 
            sed 's/.*"code": "\([^"]*\)".*/\1/g;s/.*"name": "\([^"]*\)".*/\1/g;s/.*"native_name": "\([^"]*\)".*/\1/g' | 
            paste -d ' ' - - - | 
            sed 's/\([^ ]*\) \([^ ]*\) \(.*\)/\1 - \2 (\3)/'
    fi
}

# Switch to a different language
switch_language() {
    local lang_code="$1"
    
    # Validate that the language exists
    if [ ! -f "${LANG_DIR}/${lang_code}.json" ]; then
        echo "Error: Language '${lang_code}' is not supported."
        echo "Please choose from these language codes:"
        list_languages | grep -o "^[^ ]*" | sort
        return 1
    fi
    
    # Update the language setting
    echo "${lang_code}" > "${CONFIG_DIR}/language.txt"
    echo "Language switched to: ${lang_code}"
    
    # Restart services if Mycodo is installed
    if systemctl is-active --quiet mycodoflask; then
        echo "Restarting services to apply language change..."
        systemctl restart mycodoflask
    fi
    
    return 0
}

# Main CLI logic
if [ $# -lt 1 ]; then
    echo "Current language: $(cat "${CONFIG_DIR}/language.txt" 2>/dev/null || echo "en")"
    echo
    list_languages
    echo
    echo "Usage: switch_language.sh <language_code>"
    exit 0
fi

switch_language "$1"
EOF

chmod +x "${SCRIPTS_DIR}/switch_language.sh"

# Create sample usage instructions
cat > "${DOCS_DIR}/multilingual_support.md" << 'EOF'
# Multilingual Support for Container Farm Control System

The system now has a foundation for supporting multiple languages. Currently, English, Spanish, and French are included with basic translations.

## How to Use Translations

### In Bash Scripts

Load the translation function at the beginning of your script:

```bash
source /opt/container-farm-control/scripts/translate.sh

# Now you can use the translate function
echo "$(translate "welcome_message" "Welcome to your farm!")"
```

### In Python Scripts

```python
from translate import translate, t

# Use either the full or short version
print(translate("welcome_message", "Welcome to your farm!"))
print(t("sensor_error"))  # Short version
```

## Switching Languages

To switch the system language:

```bash
sudo /opt/container-farm-control/scripts/switch_language.sh es  # Switch to Spanish
sudo /opt/container-farm-control/scripts/switch_language.sh en  # Switch to English
sudo /opt/container-farm-control/scripts/switch_language.sh fr  # Switch to French
```

## Adding New Languages

1. Create a new JSON file in the `/opt/container-farm-control/i18n/` directory
2. Name it with the language code (e.g., `de.json` for German)
3. Copy the structure from en.json and translate the values
4. Add the language to supported_languages.json

Example:

```json
{
  "welcome_message": "Willkommen bei Ihrem Container-Farm-Kontrollsystem!",
  "setup_complete": "Einrichtung abgeschlossen. Ihr Farmsystem ist bereit."
}
```

## Recommended Translation Workflow

When developing new features:

1. Always add new strings to `en.json` first
2. Use descriptive keys that indicate context
3. Run a translation update script to identify missing translations in other languages
4. Avoid concatenating strings - use placeholders instead

## Technical Notes

Translations are stored as JSON files with straightforward key-value pairs. The system will first try to find a translation in the selected language, then fall back to English if not found, and finally use the provided default text if neither is available.
EOF

echo "Multilingual support framework installed!"
echo "Currently supported languages: English (en), Spanish (es), French (fr)"
echo "Switch language with: sudo ${SCRIPTS_DIR}/switch_language.sh <lang_code>"
echo "See ${DOCS_DIR}/multilingual_support.md for usage instructions"
