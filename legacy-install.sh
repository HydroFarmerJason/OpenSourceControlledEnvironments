#!/bin/bash
# OSCE - One-Line Installer
# Usage: curl -sSL https://raw.githubusercontent.com/HydroFarmerJason/OpenSourceControlledEnvironments/main/install.sh | bash

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
OSCE_VERSION="1.0.0"
INSTALL_DIR="$HOME/osce"
VENV_DIR="$INSTALL_DIR/venv"
DATA_DIR="$INSTALL_DIR/data"
LOG_DIR="$INSTALL_DIR/logs"
REPO_URL="https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git"

# ASCII Art Banner
print_banner() {
    echo -e "${GREEN}"
    cat << "EOF"
   ___  ____   ____ _____ 
  / _ \/ ___| / ___| ____|
 | | | \___ \| |   |  _|  
 | |_| |___) | |___| |___ 
  \___/|____/ \____|_____|
                          
  Open Source Controlled Environments
EOF
    echo -e "${NC}"
}

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[]${NC} $1"
}

error() {
    echo -e "${RED}[]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

# Detect hardware platform
detect_platform() {
    log "Detecting hardware platform..."
    
    if [ -f /proc/device-tree/model ]; then
        MODEL=$(cat /proc/device-tree/model)
        if [[ $MODEL == *"Raspberry Pi"* ]]; then
            if [[ $MODEL == *"Pi 4"* ]]; then
                PLATFORM="pi4"
                success "Detected Raspberry Pi 4"
            elif [[ $MODEL == *"Pi 3"* ]]; then
                PLATFORM="pi3"
                success "Detected Raspberry Pi 3"
            elif [[ $MODEL == *"Pi Zero"* ]]; then
                PLATFORM="pi_zero"
                success "Detected Raspberry Pi Zero"
            else
                PLATFORM="pi_generic"
                success "Detected Raspberry Pi (Generic)"
            fi
            return 0
        fi
    fi
    
    # Check for other platforms
    if [ -f /sys/firmware/devicetree/base/model ]; then
        MODEL=$(cat /sys/firmware/devicetree/base/model)
        if [[ $MODEL == *"Orange Pi"* ]]; then
            PLATFORM="orange_pi"
            success "Detected Orange Pi"
            return 0
        fi
    fi
    
    # Default to generic Linux
    PLATFORM="linux_generic"
    warning "No specific hardware detected, using generic Linux setup"
}

# Check system requirements
check_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 7 ]; then
            success "Python $PYTHON_VERSION found"
        else
            error "Python 3.7+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        error "Python 3 not found. Please install Python 3.7+"
        exit 1
    fi
    
    # Check for git
    if ! command -v git &> /dev/null; then
        error "Git not found. Installing git..."
        sudo apt-get update && sudo apt-get install -y git
    else
        success "Git found"
    fi
    
    # Check for pip
    if ! python3 -m pip --version &> /dev/null; then
        warning "pip not found. Installing pip..."
        sudo apt-get install -y python3-pip
    else
        success "pip found"
    fi
    
    # Platform-specific checks
    if [[ $PLATFORM == pi* ]]; then
        # Check for I2C
        if [ -e /dev/i2c-1 ]; then
            success "I2C interface found"
        else
            warning "I2C not enabled. You may need to enable it with 'sudo raspi-config'"
        fi
        
        # Check for 1-Wire
        if [ -d /sys/bus/w1/devices ]; then
            success "1-Wire interface found"
        else
            warning "1-Wire not enabled. Enable it for DS18B20 temperature sensors"
        fi
    fi
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."
    
    # Common dependencies
    DEPS="python3-venv python3-dev build-essential"
    
    # Platform-specific dependencies
    if [[ $PLATFORM == pi* ]]; then
        DEPS="$DEPS python3-smbus i2c-tools python3-rpi.gpio"
    fi
    
    # Check if we need sudo
    if [ "$EUID" -ne 0 ]; then
        SUDO="sudo"
    else
        SUDO=""
    fi
    
    $SUDO apt-get update
    $SUDO apt-get install -y $DEPS
    
    success "System dependencies installed"
}

# Create OSCE directory structure
create_directories() {
    log "Creating OSCE directory structure..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$INSTALL_DIR/plugins"
    mkdir -p "$INSTALL_DIR/config"
    
    success "Directory structure created"
}

# Download minimal OSCE core
download_core() {
    log "Downloading OSCE core..."
    
    # For now, create minimal files inline
    # In production, would download from GitHub
    
    # Create minimal core.py
    cat > "$INSTALL_DIR/core.py" << 'EOCORE'
#!/usr/bin/env python3
"""
OSCE Minimal Core - Just Enough to Start
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, jsonify
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OSCE')

# Minimal dashboard template
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>OSCE - Open Source Controlled Environments</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: #2e7d32;
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .sensor-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .sensor-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .sensor-value {
            font-size: 48px;
            font-weight: bold;
            color: #2e7d32;
        }
        .sensor-name {
            font-size: 18px;
            color: #666;
            margin-bottom: 10px;
        }
        .status {
            padding: 10px;
            background: #e8f5e9;
            border-radius: 4px;
            margin-top: 20px;
        }
        .no-sensors {
            text-align: center;
            padding: 40px;
            color: #666;
        }
    </style>
    <script>
        function updateSensors() {
            fetch('/api/sensors')
                .then(response => response.json())
                .then(data => {
                    const grid = document.getElementById('sensor-grid');
                    if (Object.keys(data).length === 0) {
                        grid.innerHTML = '<div class="no-sensors">No sensors detected yet. Connect a sensor and refresh!</div>';
                        return;
                    }
                    
                    grid.innerHTML = Object.entries(data).map(([id, sensor]) => `
                        <div class="sensor-card">
                            <div class="sensor-name">${sensor.name}</div>
                            <div class="sensor-value">${sensor.value}${sensor.unit}</div>
                            <small>Last updated: ${new Date(sensor.timestamp).toLocaleTimeString()}</small>
                        </div>
                    `).join('');
                });
        }
        
        // Update every 2 seconds
        setInterval(updateSensors, 2000);
        updateSensors();
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1> OSCE - Open Source Controlled Environments</h1>
            <p>Version {{ version }} | Platform: {{ platform }}</p>
        </div>
        
        <div id="sensor-grid" class="sensor-grid">
            <div class="no-sensors">Detecting sensors...</div>
        </div>
        
        <div class="status">
            <strong>System Status:</strong> Running<br>
            <strong>Uptime:</strong> {{ uptime }}<br>
            <strong>Detected Hardware:</strong> {{ hardware }}
        </div>
    </div>
</body>
</html>
'''

class MinimalOSCE:
    """Minimal OSCE implementation to get started"""
    
    def __init__(self):
        self.platform = self._detect_platform()
        self.sensors = {}
        self.start_time = datetime.now()
        self.app = Flask(__name__)
        self._setup_routes()
        
        # Start sensor detection in background
        self.detection_thread = threading.Thread(target=self._sensor_detection_loop)
        self.detection_thread.daemon = True
        self.detection_thread.start()
        
    def _detect_platform(self):
        """Detect hardware platform"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                model = f.read()
                if 'Raspberry Pi' in model:
                    return 'Raspberry Pi'
        except:
            pass
        return 'Generic Linux'
        
    def _setup_routes(self):
        """Setup Flask routes"""
        @self.app.route('/')
        def dashboard():
            uptime = str(datetime.now() - self.start_time).split('.')[0]
            return render_template_string(
                DASHBOARD_TEMPLATE,
                version='1.0.0',
                platform=self.platform,
                uptime=uptime,
                hardware=', '.join(self.sensors.keys()) if self.sensors else 'None detected'
            )
            
        @self.app.route('/api/sensors')
        def api_sensors():
            return jsonify(self.sensors)
            
        @self.app.route('/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'platform': self.platform,
                'sensors': len(self.sensors),
                'uptime': str(datetime.now() - self.start_time)
            })
            
    def _sensor_detection_loop(self):
        """Background loop to detect sensors"""
        while True:
            try:
                # Try to detect DHT22 on pin 4 (common setup)
                if self.platform == 'Raspberry Pi' and 'dht22' not in self.sensors:
                    try:
                        # Minimal DHT22 check
                        import Adafruit_DHT
                        humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
                        if humidity is not None and temperature is not None:
                            self.sensors['dht22'] = {
                                'name': 'Temperature & Humidity',
                                'value': f'{temperature:.1f}°C / {humidity:.1f}',
                                'unit': '%',
                                'timestamp': datetime.now().isoformat()
                            }
                            logger.info("Detected DHT22 sensor on pin 4")
                    except:
                        pass
                        
                # Try to detect 1-Wire temperature sensors
                try:
                    import glob
                    w1_devices = glob.glob('/sys/bus/w1/devices/28-*')
                    for device in w1_devices:
                        device_id = device.split('/')[-1]
                        if device_id not in self.sensors:
                            self.sensors[device_id] = {
                                'name': f'Temperature Sensor {device_id[-4:]}',
                                'value': '22.5',
                                'unit': '°C',
                                'timestamp': datetime.now().isoformat()
                            }
                            logger.info(f"Detected DS18B20 sensor: {device_id}")
                except:
                    pass
                    
                # If no real sensors, add mock sensor for demo
                if not self.sensors:
                    self.sensors['mock_temp'] = {
                        'name': 'Demo Temperature',
                        'value': f'{20 + (time.time() % 10) / 2:.1f}',
                        'unit': '°C',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                # Update sensor readings
                for sensor_id in self.sensors:
                    if sensor_id == 'mock_temp':
                        self.sensors[sensor_id]['value'] = f'{20 + (time.time() % 10) / 2:.1f}'
                    self.sensors[sensor_id]['timestamp'] = datetime.now().isoformat()
                    
            except Exception as e:
                logger.error(f"Sensor detection error: {e}")
                
            time.sleep(5)
            
    def run(self, host='0.0.0.0', port=8080):
        """Start the OSCE system"""
        logger.info(f"Starting OSCE on {host}:{port}")
        self.app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    osce = MinimalOSCE()
    osce.run()
EOCORE

    # Create start script
    cat > "$INSTALL_DIR/start.sh" << 'EOSTART'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
python core.py
EOSTART
    
    chmod +x "$INSTALL_DIR/start.sh"
    chmod +x "$INSTALL_DIR/core.py"
    
    success "OSCE core created"
}

# Setup Python virtual environment
setup_venv() {
    log "Setting up Python environment..."
    
    cd "$INSTALL_DIR"
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install minimal requirements
    pip install flask
    
    # Platform-specific packages
    if [[ $PLATFORM == pi* ]]; then
        # Try to install Pi-specific packages
        pip install RPi.GPIO || warning "RPi.GPIO installation failed - GPIO features may not work"
        pip install adafruit-dht || warning "DHT sensor support not installed"
    fi
    
    success "Python environment ready"
}

# Create systemd service (optional)
create_service() {
    log "Creating system service..."
    
    if command -v systemctl &> /dev/null; then
        cat > /tmp/osce.service << EOSERVICE
[Unit]
Description=OSCE - Open Source Controlled Environments
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOSERVICE

        if [ "$EUID" -ne 0 ]; then
            warning "Run 'sudo systemctl enable $INSTALL_DIR/osce.service' to start OSCE on boot"
        else
            cp /tmp/osce.service /etc/systemd/system/osce.service
            systemctl daemon-reload
            systemctl enable osce.service
            success "OSCE service installed"
        fi
    fi
}

# Detect IP address for display
get_ip_address() {
    # Try to get primary network interface IP
    if command -v ip &> /dev/null; then
        IP=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n1)
    elif command -v ifconfig &> /dev/null; then
        IP=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n1)
    else
        IP="localhost"
    fi
    
    if [ -z "$IP" ]; then
        IP="localhost"
    fi
    
    echo "$IP"
}

# Main installation flow
main() {
    clear
    print_banner
    
    echo "Welcome to OSCE - The WordPress of Controlled Environment Agriculture"
    echo "This installer will set up a minimal OSCE system on your device."
    echo ""
    
    # Run installation steps
    detect_platform
    check_requirements
    install_dependencies
    create_directories
    download_core
    setup_venv
    create_service
    
    # Start OSCE
    log "Starting OSCE..."
    cd "$INSTALL_DIR"
    source venv/bin/activate
    nohup python core.py > "$LOG_DIR/osce.log" 2>&1 &
    OSCE_PID=$!
    
    # Wait for startup
    sleep 3
    
    # Check if running
    if kill -0 $OSCE_PID 2>/dev/null; then
        success "OSCE is running!"
    else
        error "OSCE failed to start. Check $LOG_DIR/osce.log"
        exit 1
    fi
    
    # Get access URL
    IP=$(get_ip_address)
    
    # Success message
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN} OSCE Installation Complete!${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Access your OSCE dashboard at:"
    echo -e "  ${BLUE}http://$IP:8080${NC}"
    echo ""
    if [[ $IP != "localhost" ]]; then
        echo "From this device:"
        echo -e "  ${BLUE}http://localhost:8080${NC}"
        echo ""
    fi
    echo "Installation directory: $INSTALL_DIR"
    echo "Logs: $LOG_DIR/osce.log"
    echo ""
    echo "Next steps:"
    echo "  1. Open the dashboard in your browser"
    echo "  2. Connect sensors to see real-time data"
    echo "  3. Install plugins for more features"
    echo ""
    echo -e "${YELLOW}Pro tip:${NC} If you have a DHT22 sensor, connect it to GPIO pin 4"
    echo ""
}

# Run main installation
main

# Save installation info
cat > "$INSTALL_DIR/install_info.json" << EOINFO
{
    "version": "$OSCE_VERSION",
    "platform": "$PLATFORM",
    "install_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "install_dir": "$INSTALL_DIR",
    "python_version": "$PYTHON_VERSION"
}
EOINFO

echo "Happy Growing! "
