#!/bin/bash
# Container Farm Control System - Hardware Kit Integration Module
# This script enables rapid deployment of pre-configured hardware kits
# Supports QR code scanning for setup and automatic GPIO pin mapping

INSTALL_DIR="/opt/container-farm-control"
CONFIG_DIR="${INSTALL_DIR}/configs"
SCRIPTS_DIR="${INSTALL_DIR}/scripts"
KIT_DIR="${INSTALL_DIR}/hardware_kits"

# Colors for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Create directories
mkdir -p "${KIT_DIR}"
mkdir -p "${KIT_DIR}/pin_maps"
mkdir -p "${KIT_DIR}/qr_codes"

# Hardware kit definitions - these would be expanded with more kits
cat > "${KIT_DIR}/kit_definitions.json" << 'EOF'
{
  "kits": [
    {
      "id": "basic_educational_kit",
      "name": "Educational Starter Kit",
      "description": "Basic kit with temperature, humidity sensors and simple relay controls",
      "manufacturer": "GrowLab Industries",
      "components": [
        "Raspberry Pi 4",
        "DHT22 Temperature/Humidity Sensor",
        "DS18B20 Temperature Sensor",
        "2-Channel Relay Module",
        "Water Pump Module",
        "Light Strip"
      ],
      "pin_map": {
        "dht22_data": 17,
        "ds18b20_data": 4,
        "light_relay": 23,
        "pump_relay": 24
      }
    },
    {
      "id": "hydroponic_research_kit",
      "name": "Hydroponic Research Kit",
      "description": "Advanced kit with pH, EC sensors and multi-channel control",
      "manufacturer": "AgroTech Systems",
      "components": [
        "Raspberry Pi 4",
        "BME280 Temperature/Humidity/Pressure Sensor",
        "Atlas Scientific pH Sensor",
        "Atlas Scientific EC Sensor",
        "8-Channel Relay Module",
        "Peristaltic Pump Array",
        "LED Growth Light Array"
      ],
      "pin_map": {
        "bme280_i2c": "0x76",
        "i2c_sda": 2,
        "i2c_scl": 3,
        "ph_tx": 14,
        "ph_rx": 15,
        "ec_tx": 14,
        "ec_rx": 15,
        "light_relay": 5,
        "fan_relay": 6,
        "pump_relay": 13,
        "nutrient_a_relay": 19,
        "nutrient_b_relay": 20,
        "ph_up_relay": 21,
        "ph_down_relay": 26,
        "mixer_relay": 16
      }
    },
    {
      "id": "therapy_accessibility_kit",
      "name": "Therapeutic Horticulture Kit",
      "description": "Specialized kit with accessibility features for therapeutic programs",
      "manufacturer": "Healing Gardens Tech",
      "components": [
        "Raspberry Pi 4",
        "DHT22 Temperature/Humidity Sensor",
        "Soil Moisture Sensors (3)",
        "4-Channel Relay Module with LED Indicators",
        "Accessible Water Pump Control",
        "Large Button Interface",
        "RGB Status Lights"
      ],
      "pin_map": {
        "dht22_data": 17,
        "soil_moisture_1": 27,
        "soil_moisture_2": 22,
        "soil_moisture_3": 10,
        "light_relay": 5,
        "water_relay": 6,
        "fan_relay": 13,
        "aux_relay": 19,
        "button_1": 20,
        "button_2": 21,
        "rgb_red": 12,
        "rgb_green": 16,
        "rgb_blue": 26
      }
    },
    {
      "id": "community_garden_kit",
      "name": "Community Garden Control System",
      "description": "Robust kit designed for community garden applications with weather resistance",
      "manufacturer": "Urban Farm Solutions",
      "components": [
        "Raspberry Pi 4 with Weather-Resistant Enclosure",
        "BME280 Temperature/Humidity/Pressure Sensor",
        "Soil Moisture Array (6 sensors)",
        "Light Sensor",
        "Rain Sensor",
        "8-Channel Outdoor Relay Module",
        "Irrigation Control System"
      ],
      "pin_map": {
        "bme280_i2c": "0x76",
        "i2c_sda": 2,
        "i2c_scl": 3,
        "light_sensor_analog": 0,
        "rain_sensor_digital": 25,
        "soil_1": 4,
        "soil_2": 17,
        "soil_3": 27,
        "soil_4": 22,
        "soil_5": 10,
        "soil_6": 9,
        "zone_1_relay": 5,
        "zone_2_relay": 6,
        "zone_3_relay": 13,
        "zone_4_relay": 19,
        "pump_relay": 20,
        "light_relay": 21,
        "auxiliary_1": 16,
        "auxiliary_2": 26
      }
    }
  ]
}
EOF

# Create PIN Map Writer for pre-wired kits
cat > "${SCRIPTS_DIR}/apply_pin_map.py" << 'EOF'
#!/usr/bin/env python3
"""
Container Farm Control System - PIN Map Application Tool
Maps hardware kit PIN definitions to Mycodo configuration
"""

import os
import sys
import json
import argparse
import sqlite3
import subprocess
import glob
import re

# Base directories
INSTALL_DIR = "/opt/container-farm-control"
CONFIG_DIR = os.path.join(INSTALL_DIR, "configs")
KIT_DIR = os.path.join(INSTALL_DIR, "hardware_kits")

def load_kit_definitions():
    """Load the hardware kit definitions"""
    try:
        with open(os.path.join(KIT_DIR, "kit_definitions.json"), 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading kit definitions: {e}")
        return {"kits": []}

def get_kit_by_id(kit_id):
    """Get a specific kit definition by ID"""
    kits = load_kit_definitions()
    for kit in kits.get("kits", []):
        if kit.get("id") == kit_id:
            return kit
    return None

def list_available_kits():
    """List all available hardware kits"""
    kits = load_kit_definitions()
    
    if not kits.get("kits"):
        print("No hardware kits defined.")
        return
    
    print("\nAvailable Hardware Kits:")
    print("=" * 60)
    
    for i, kit in enumerate(kits.get("kits", []), 1):
        print(f"{i}. {kit.get('name')} [{kit.get('id')}]")
        print(f"   Description: {kit.get('description')}")
        print(f"   Manufacturer: {kit.get('manufacturer')}")
        print(f"   Components: {', '.join(kit.get('components', []))[:60]}...")
        print()

def apply_pin_map_to_mycodo(kit_id):
    """Apply a kit's PIN map to Mycodo configuration"""
    kit = get_kit_by_id(kit_id)
    
    if not kit:
        print(f"Error: Kit with ID '{kit_id}' not found.")
        return False
    
    pin_map = kit.get("pin_map", {})
    
    if not pin_map:
        print("Error: No PIN map defined for this kit.")
        return False
    
    print(f"Applying PIN map for {kit.get('name')}...")
    
    # Check if Mycodo is installed
    mycodo_db = "/var/mycodo/databases/mycodo.db"
    if not os.path.exists(mycodo_db):
        print("Error: Mycodo database not found. Is Mycodo installed?")
        return False
    
    try:
        # Connect to Mycodo database
        conn = sqlite3.connect(mycodo_db)
        cursor = conn.cursor()
        
        # Update input pins
        for input_name, pin in pin_map.items():
            if input_name.endswith(("_data", "_analog", "_digital", "_i2c", "_tx", "_rx", "_sda", "_scl")):
                # Find inputs with matching name pattern
                cursor.execute(
                    "SELECT id, device, name FROM input WHERE name LIKE ?", 
                    (f"%{input_name.split('_')[0]}%",)
                )
                inputs = cursor.fetchall()
                
                if inputs:
                    for input_id, device, name in inputs:
                        print(f"Updating input '{name}' to use pin {pin}")
                        
                        # Update custom_options field - this is a JSON field in Mycodo
                        cursor.execute("SELECT custom_options FROM input WHERE id = ?", (input_id,))
                        options_json = cursor.fetchone()[0]
                        
                        if options_json:
                            try:
                                options = json.loads(options_json)
                                
                                # Determine which field to update based on input type
                                if "pin" in options:
                                    options["pin"] = pin
                                elif "pin_clock" in options and input_name.endswith("_scl"):
                                    options["pin_clock"] = pin
                                elif "pin_data" in options and input_name.endswith("_sda"):
                                    options["pin_data"] = pin
                                elif "gpio" in options:
                                    options["gpio"] = pin
                                
                                # Update the database
                                cursor.execute(
                                    "UPDATE input SET custom_options = ? WHERE id = ?", 
                                    (json.dumps(options), input_id)
                                )
                            except json.JSONDecodeError:
                                print(f"Error: Could not parse custom_options for input {name}")
        
        # Update output pins (relays)
        for output_name, pin in pin_map.items():
            if any(relay_type in output_name for relay_type in ["relay", "light", "pump", "fan", "heater", "zone"]):
                # Find outputs with matching name pattern
                search_term = output_name.replace("_relay", "")
                cursor.execute(
                    "SELECT id, name FROM output WHERE name LIKE ?", 
                    (f"%{search_term}%",)
                )
                outputs = cursor.fetchall()
                
                if outputs:
                    for output_id, name in outputs:
                        print(f"Updating output '{name}' to use pin {pin}")
                        
                        # Update pin field directly
                        cursor.execute(
                            "UPDATE output SET pin = ? WHERE id = ?", 
                            (pin, output_id)
                        )
        
        # Commit changes
        conn.commit()
        
        # Close connection
        conn.close()
        
        print(f"Successfully applied PIN map for {kit.get('name')}.")
        print("Restarting Mycodo services...")
        
        # Restart Mycodo services to apply changes
        try:
            subprocess.run(["systemctl", "restart", "mycodoflask"])
            subprocess.run(["systemctl", "restart", "mycododaemon"])
            print("Mycodo services restarted.")
        except Exception as e:
            print(f"Error restarting Mycodo services: {e}")
        
        return True
        
    except Exception as e:
        print(f"Error applying PIN map: {e}")
        return False

def save_kit_to_config(kit_id):
    """Save the selected kit to the system configuration"""
    kit = get_kit_by_id(kit_id)
    
    if not kit:
        print(f"Error: Kit with ID '{kit_id}' not found.")
        return False
    
    # Save kit information to config
    try:
        with open(os.path.join(CONFIG_DIR, "hardware_kit.txt"), 'w') as f:
            f.write(kit_id)
        
        # Save detailed kit info for reference
        with open(os.path.join(CONFIG_DIR, "hardware_kit_info.json"), 'w') as f:
            json.dump(kit, f, indent=2)
        
        # Update config.sh if it exists
        config_sh = os.path.join(CONFIG_DIR, "config.sh")
        if os.path.exists(config_sh):
            with open(config_sh, 'r') as f:
                config_text = f.read()
                
            # Check if HARDWARE_KIT is already defined
            if "HARDWARE_KIT=" in config_text:
                # Replace existing definition
                config_text = re.sub(
                    r'HARDWARE_KIT="[^"]*"', 
                    f'HARDWARE_KIT="{kit_id}"', 
                    config_text
                )
            else:
                # Add new definition
                config_text += f'\nHARDWARE_KIT="{kit_id}"\n'
            
            with open(config_sh, 'w') as f:
                f.write(config_text)
        
        print(f"Hardware kit '{kit.get('name')}' set as system configuration.")
        return True
        
    except Exception as e:
        print(f"Error saving kit configuration: {e}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Container Farm Hardware Kit Tool")
    parser.add_argument("--list", action="store_true", help="List available hardware kits")
    parser.add_argument("--apply", help="Apply PIN map for specified kit ID")
    parser.add_argument("--set", dest="set_kit", help="Set specified kit ID as system configuration")
    
    args = parser.parse_args()
    
    if args.list:
        list_available_kits()
    elif args.apply:
        apply_pin_map_to_mycodo(args.apply)
    elif args.set_kit:
        save_kit_to_config(args.set_kit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
EOF

chmod +x "${SCRIPTS_DIR}/apply_pin_map.py"

# Create QR code generator script
cat > "${SCRIPTS_DIR}/generate_kit_qr.py" << 'EOF'
#!/usr/bin/env python3
"""
Container Farm Control System - Hardware Kit QR Code Generator
Creates QR codes for kit identification and rapid setup
"""

import os
import sys
import json
import argparse
import qrcode
import base64
import io
from PIL import Image, ImageDraw, ImageFont

# Base directories
INSTALL_DIR = "/opt/container-farm-control"
CONFIG_DIR = os.path.join(INSTALL_DIR, "configs")
KIT_DIR = os.path.join(INSTALL_DIR, "hardware_kits")
QR_DIR = os.path.join(KIT_DIR, "qr_codes")

def load_kit_definitions():
    """Load the hardware kit definitions"""
    try:
        with open(os.path.join(KIT_DIR, "kit_definitions.json"), 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading kit definitions: {e}")
        return {"kits": []}

def get_kit_by_id(kit_id):
    """Get a specific kit definition by ID"""
    kits = load_kit_definitions()
    for kit in kits.get("kits", []):
        if kit.get("id") == kit_id:
            return kit
    return None

def generate_qr_code(kit_id):
    """Generate a QR code for the specified kit"""
    kit = get_kit_by_id(kit_id)
    
    if not kit:
        print(f"Error: Kit with ID '{kit_id}' not found.")
        return False
    
    # Ensure output directory exists
    os.makedirs(QR_DIR, exist_ok=True)
    
    try:
        # Create QR code data
        qr_data = {
            "type": "container_farm_kit",
            "id": kit.get("id"),
            "name": kit.get("name"),
            "manufacturer": kit.get("manufacturer"),
            "pin_map": True,  # Indicates pin map is available
            "version": "1.0"
        }
        
        # Convert to JSON string
        qr_json = json.dumps(qr_data, separators=(',', ':'))
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_json)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Create a larger image with room for text
        width, height = qr_image.size
        new_img = Image.new('RGB', (width, height + 60), color='white')
        new_img.paste(qr_image, (0, 0))
        
        # Add text
        draw = ImageDraw.Draw(new_img)
        
        # Try to use a nice font, fall back to default if not available
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 16)
        except IOError:
            font = ImageFont.load_default()
        
        # Draw text
        draw.text((10, height + 10), f"Kit: {kit.get('name')}", fill='black', font=font)
        draw.text((10, height + 35), f"ID: {kit.get('id')}", fill='black', font=font)
        
        # Save image
        qr_path = os.path.join(QR_DIR, f"{kit_id}_qr.png")
        new_img.save(qr_path)
        
        print(f"QR code generated for {kit.get('name')}")
        print(f"Saved to: {qr_path}")
        
        return qr_path
        
    except Exception as e:
        print(f"Error generating QR code: {e}")
        return False

def generate_all_qr_codes():
    """Generate QR codes for all defined kits"""
    kits = load_kit_definitions()
    
    if not kits.get("kits"):
        print("No hardware kits defined.")
        return False
    
    print("Generating QR codes for all kits...")
    
    success_count = 0
    for kit in kits.get("kits", []):
        kit_id = kit.get("id")
        if generate_qr_code(kit_id):
            success_count += 1
    
    print(f"Generated {success_count} of {len(kits.get('kits', []))} QR codes.")
    return success_count > 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Container Farm Hardware Kit QR Code Generator")
    parser.add_argument("--generate", help="Generate QR code for specified kit ID")
    parser.add_argument("--all", action="store_true", help="Generate QR codes for all kits")
    
    args = parser.parse_args()
    
    if args.generate:
        generate_qr_code(args.generate)
    elif args.all:
        generate_all_qr_codes()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
EOF

chmod +x "${SCRIPTS_DIR}/generate_kit_qr.py"

# Create QR code scanner script
cat > "${SCRIPTS_DIR}/scan_kit_qr.py" << 'EOF'
#!/usr/bin/env python3
"""
Container Farm Control System - Hardware Kit QR Code Scanner
Scans QR codes from webcam for rapid kit setup
"""

import os
import sys
import json
import argparse
import subprocess
import time
import threading
import re

try:
    import cv2
    from pyzbar.pyzbar import decode
    SCANNER_AVAILABLE = True
except ImportError:
    SCANNER_AVAILABLE = False

# Base directories
INSTALL_DIR = "/opt/container-farm-control"
CONFIG_DIR = os.path.join(INSTALL_DIR, "configs")
SCRIPTS_DIR = os.path.join(INSTALL_DIR, "scripts")
KIT_DIR = os.path.join(INSTALL_DIR, "hardware_kits")

def install_dependencies():
    """Install required dependencies for QR scanning"""
    print("Installing required dependencies for QR code scanning...")
    
    try:
        # Update package list
        subprocess.run(["apt", "update"], check=True)
        
        # Install packages
        subprocess.run(["apt", "install", "-y", "python3-opencv", "python3-pip", "libzbar0"], check=True)
        
        # Install Python packages
        subprocess.run(["pip3", "install", "pyzbar", "qrcode", "pillow"], check=True)
        
        print("Dependencies installed successfully.")
        print("Please restart this script to use the QR scanner.")
        return True
        
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        return False

def apply_kit_from_qr(qr_data):
    """Apply kit configuration from QR code data"""
    try:
        # Parse QR data
        qr_json = json.loads(qr_data)
        
        # Verify this is a container farm kit QR code
        if qr_json.get("type") != "container_farm_kit":
            print("Error: Not a valid Container Farm kit QR code.")
            return False
        
        kit_id = qr_json.get("id")
        kit_name = qr_json.get("name")
        
        if not kit_id:
            print("Error: No kit ID found in QR code.")
            return False
        
        print(f"Detected kit: {kit_name} [{kit_id}]")
        
        # Set kit in configuration
        set_cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "apply_pin_map.py"), "--set", kit_id]
        subprocess.run(set_cmd, check=True)
        
        # Apply PIN map
        apply_cmd = [sys.executable, os.path.join(SCRIPTS_DIR, "apply_pin_map.py"), "--apply", kit_id]
        subprocess.run(apply_cmd, check=True)
        
        print(f"Successfully configured system for {kit_name}.")
        return True
        
    except json.JSONDecodeError:
        print("Error: Could not parse QR code data.")
        return False
    except Exception as e:
        print(f"Error applying kit configuration: {e}")
        return False

def scan_qr_from_webcam():
    """Scan QR code from webcam"""
    if not SCANNER_AVAILABLE:
        print("Error: OpenCV and pyzbar are required for QR scanning.")
        print("Would you like to install the required dependencies? (y/n)")
        choice = input().lower()
        
        if choice == 'y':
            if install_dependencies():
                sys.exit(0)
            else:
                sys.exit(1)
        else:
            print("Exiting. Dependencies not installed.")
            sys.exit(1)
    
    print("Starting QR code scanner...")
    print("Point a Container Farm kit QR code at your webcam.")
    print("Press 'q' to quit.")
    
    # Initialize camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)
    
    # Create processing thread to avoid blocking the camera
    result_queue = []
    processing_complete = threading.Event()
    
    def process_qr(qr_data):
        """Process QR data in a separate thread"""
        success = apply_kit_from_qr(qr_data)
        result_queue.append(success)
        processing_complete.set()
    
    # Main scanning loop
    scanned = False
    while not scanned:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Could not read frame from webcam.")
            break
        
        # Decode QR codes in frame
        decoded_objects = decode(frame)
        
        # Draw rectangle around QR code
        for obj in decoded_objects:
            # Draw outline
            points = obj.polygon
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points]))
                cv2.polylines(frame, [hull], True, (0, 255, 0), 3)
            else:
                cv2.polylines(frame, [np.array(points)], True, (0, 255, 0), 3)
            
            # Get QR code data
            qr_data = obj.data.decode("utf-8")
            
            # Process in separate thread
            if not scanned:
                processing_thread = threading.Thread(target=process_qr, args=(qr_data,))
                processing_thread.start()
                scanned = True
        
        # Display the frame
        cv2.imshow("Container Farm QR Scanner", frame)
        
        # Check for 'q' key press to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
        # If QR processed, wait for result
        if scanned and processing_complete.is_set():
            success = result_queue[0] if result_queue else False
            
            if success:
                print("QR code processed successfully.")
                time.sleep(2)  # Give user time to read message
                break
            else:
                print("Error processing QR code. Please try again.")
                scanned = False
                processing_complete.clear()
                result_queue.clear()
    
    # Release camera and close windows
    cap.release()
    cv2.destroyAllWindows()
    
    return scanned

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Container Farm Hardware Kit QR Scanner")
    parser.add_argument("--scan", action="store_true", help="Scan QR code from webcam")
    parser.add_argument("--manual", help="Manually apply kit ID from text (no scanning)")
    
    args = parser.parse_args()
    
    if args.scan:
        scan_qr_from_webcam()
    elif args.manual:
        kit_id = args.manual
        apply_kit_from_qr(json.dumps({
            "type": "container_farm_kit",
            "id": kit_id,
            "name": kit_id
        }))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
EOF

chmod +x "${SCRIPTS_DIR}/scan_kit_qr.py"

# Create wizard extension for kit setup
cat > "${SCRIPTS_DIR}/kit_setup_wizard.sh" << 'EOF'
#!/bin/bash
# Container Farm Control System - Hardware Kit Setup Wizard
# This wizard guides users through setting up pre-configured hardware kits

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
KIT_DIR="${INSTALL_DIR}/hardware_kits"

# Display welcome banner
clear
echo -e "${BLUE}${BOLD}"
echo "============================================================"
echo "     Container Farm Hardware Kit Setup Wizard              "
echo "============================================================"
echo -e "${NC}"
echo -e "This wizard will guide you through setting up your hardware kit."
echo -e "You can use a QR code or select your kit from a list."
echo
echo -e "${YELLOW}All kits include pre-configured PIN mappings for easier setup.${NC}"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}Please run as root (sudo)${NC}"
  exit 1
fi

# Check if setup_wizard has run first
if [ ! -f "${CONFIG_DIR}/project_name.txt" ]; then
  echo -e "${RED}Error: Please run the main setup wizard first:${NC}"
  echo -e "sudo ${SCRIPTS_DIR}/setup_wizard.sh"
  exit 1
fi

# Hardware Kit Selection
echo -e "${CYAN}How would you like to identify your hardware kit?${NC}"
echo -e "1) ${CYAN}Scan QR Code${NC} - Use webcam to scan kit QR code"
echo -e "2) ${CYAN}Select from List${NC} - Choose from list of supported kits"
echo -e "3) ${CYAN}Custom Setup${NC} - Manual PIN mapping (for custom hardware)"
echo
read -p "Please select an option [1-3]: " kit_option

case $kit_option in
  1) 
    # QR Code scanning
    echo -e "\n${YELLOW}Preparing QR code scanner...${NC}"
    
    # Check if dependencies are installed
    if ! command -v python3 >/dev/null 2>&1; then
      echo -e "${RED}Python 3 is required for QR scanning.${NC}"
      echo -e "Installing Python 3..."
      apt install -y python3 python3-pip
    fi
    
    # Run QR scanner
    python3 "${SCRIPTS_DIR}/scan_kit_qr.py" --scan
    ;;
    
  2)
    # List selection
    echo -e "\n${YELLOW}Loading available hardware kits...${NC}"
    python3 "${SCRIPTS_DIR}/apply_pin_map.py" --list
    
    echo
    read -p "Enter the ID of your kit: " selected_kit
    
    # Apply kit configuration
    if [ -n "$selected_kit" ]; then
      echo -e "\n${YELLOW}Configuring system for selected kit...${NC}"
      python3 "${SCRIPTS_DIR}/apply_pin_map.py" --set "$selected_kit"
      python3 "${SCRIPTS_DIR}/apply_pin_map.py" --apply "$selected_kit"
    else
      echo -e "${RED}No kit selected. Exiting.${NC}"
      exit 1
    fi
    ;;
    
  3)
    # Custom setup
    echo -e "\n${YELLOW}Custom hardware setup selected.${NC}"
    echo -e "This option is for advanced users with custom hardware configurations."
    echo -e "You will need to manually configure your PIN mappings in Mycodo."
    
    # Set custom mode
    echo "custom" > "${CONFIG_DIR}/hardware_kit.txt"
    
    echo -e "\n${GREEN}System set to custom hardware mode.${NC}"
    echo -e "Please configure your sensors and relays manually in Mycodo:"
    echo -e "https://$(hostname -I | awk '{print $1}')/login"
    ;;
    
  *)
    echo -e "${RED}Invalid selection. Exiting.${NC}"
    exit 1
    ;;
esac

# Update main configuration
if [ -f "${CONFIG_DIR}/config.sh" ]; then
  # Check if setup_mode is already defined
  if grep -q "SETUP_MODE=" "${CONFIG_DIR}/config.sh"; then
    # Update existing value
    sed -i 's/SETUP_MODE="[^"]*"/SETUP_MODE="kit"/' "${CONFIG_DIR}/config.sh"
  else
    # Add new value
    echo 'SETUP_MODE="kit"' >> "${CONFIG_DIR}/config.sh"
  fi
fi

# Success message
if [ "$kit_option" != "3" ]; then
  echo -e "\n${GREEN}${BOLD}Hardware kit setup completed successfully!${NC}"
  echo -e "Your Container Farm is now configured with the correct PIN mappings."
  echo -e "You can access the control panel at: https://$(hostname -I | awk '{print $1}')/login"
fi

echo
echo -e "${YELLOW}Would you like to restart the system to apply all changes?${NC}"
read -p "Restart now? (y/n): " do_restart

if [[ "$do_restart" == "y" || "$do_restart" == "Y" ]]; then
  echo -e "${YELLOW}Restarting system...${NC}"
  reboot
else
  echo -e "${YELLOW}Please remember to restart your system manually to apply all changes.${NC}"
fi

echo
exit 0
EOF

chmod +x "${SCRIPTS_DIR}/kit_setup_wizard.sh"

# Create documentation
cat > "${KIT_DIR}/README.md" << 'EOF'
# Container Farm Control System - Hardware Kits

This directory contains configurations for pre-wired hardware kits that work with the Container Farm Control System. These kits make setup faster and more reliable by providing pre-configured PIN mappings.

## Supported Hardware Kits

The system currently supports the following hardware kits:

1. **Educational Starter Kit** - Basic kit with temperature, humidity sensors and simple relay controls
2. **Hydroponic Research Kit** - Advanced kit with pH, EC sensors and multi-channel control
3. **Therapeutic Horticulture Kit** - Specialized kit with accessibility features for therapeutic programs
4. **Community Garden Control System** - Robust kit for community garden applications with weather resistance

## Using Hardware Kits

There are three ways to configure your system for a hardware kit:

### 1. Using QR Codes

Each hardware kit includes a QR code that can be scanned to instantly configure your system:

```bash
sudo /opt/container-farm-control/scripts/kit_setup_wizard.sh
```

Choose the "Scan QR Code" option and follow the prompts.

### 2. Selecting from the List

If you don't have a QR code, you can select your kit from the list:

```bash
sudo /opt/container-farm-control/scripts/kit_setup_wizard.sh
```

Choose the "Select from List" option and enter your kit ID.

### 3. Manual Configuration

```bash
sudo python3 /opt/container-farm-control/scripts/apply_pin_map.py --list
sudo python3 /opt/container-farm-control/scripts/apply_pin_map.py --apply KIT_ID
```

Replace `KIT_ID` with the ID of your hardware kit.

## Creating QR Codes

If you need to generate QR codes for a hardware kit:

```bash
sudo python3 /opt/container-farm-control/scripts/generate_kit_qr.py --generate KIT_ID
```

This will create a QR code in the `/opt/container-farm-control/hardware_kits/qr_codes/` directory.

## Adding New Hardware Kits

To add support for a new hardware kit, edit the `/opt/container-farm-control/hardware_kits/kit_definitions.json` file and add your kit definition following the existing format.

## Troubleshooting

If you encounter issues with your hardware kit configuration:

1. Check that the PIN mappings in your kit definition match your actual hardware
2. Verify that the correct kit ID is being used
3. Try manually configuring the PINs in Mycodo
4. Restart the Mycodo services after making changes:
   ```bash
   sudo systemctl restart mycodoflask
   sudo systemctl restart mycododaemon
   ```

## Hardware Kit Development Guidelines

When creating new hardware kits, follow these guidelines:

1. Use standardized pin naming conventions
2. Provide clear documentation of all connections
3. Include a wiring diagram with your kit
4. Test all sensors and outputs before creating kit definition
5. Consider accessibility needs in your design

For more information, see the full documentation in the `/opt/container-farm-control/docs/` directory.
EOF

# Modify setup_wizard.sh to include hardware kit option
# This would insert code into the main setup wizard to handle kits
SETUP_WIZARD="${SCRIPTS_DIR}/setup_wizard.sh"

echo "Hardware Kit Integration module installed successfully!"
echo "To set up a pre-configured hardware kit, run:"
echo "sudo ${SCRIPTS_DIR}/kit_setup_wizard.sh"
echo
echo "To generate QR codes for all supported kits, run:"
echo "sudo python3 ${SCRIPTS_DIR}/generate_kit_qr.py --all"
echo
echo "Documentation available at: ${KIT_DIR}/README.md"
