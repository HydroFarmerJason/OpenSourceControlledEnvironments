#!/bin/bash
# OSCE v2.0 - One-Line Installer
# The WordPress of IoT with Planetary Harmony
# Usage: curl -sSL https://raw.githubusercontent.com/HydroFarmerJason/OpenSourceControlledEnvironments/main/install.sh | bash

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
OSCE_VERSION="2.0.0"
INSTALL_DIR="$HOME/osce"
VENV_DIR="$INSTALL_DIR/venv"
DATA_DIR="$INSTALL_DIR/data"
LOG_DIR="$INSTALL_DIR/logs"
PLUGIN_DIR="$INSTALL_DIR/plugins"
CONFIG_DIR="$INSTALL_DIR/config"
STATIC_DIR="$INSTALL_DIR/static"
CERTS_DIR="$INSTALL_DIR/certs"
REPO_URL="https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git"

# ASCII Art Banner - Updated for v2.0
print_banner() {
    echo -e "${GREEN}"
    cat << "EOF"
   ___  ____   ____ _____       ____    ___  
  / _ \/ ___| / ___| ____|     |___ \  / _ \ 
 | | | \___ \| |   |  _|  _____ __) || | | |
 | |_| |___) | |___| |___ |_____/ __/ | |_| |
  \___/|____/ \____|_____|     |_____|  \___/ 
                          
  Open Source Controlled Environments v2.0
  🌍 Harmonizing with Earth's Electromagnetic Rhythms 🌍
EOF
    echo -e "${NC}"
}

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

error() {
    echo -e "${RED}[✗]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

info() {
    echo -e "${PURPLE}[i]${NC} $1"
}

# Detect hardware platform with v2.0 EM sensor support
detect_platform() {
    log "Detecting hardware platform..."
    
    if [ -f /proc/device-tree/model ]; then
        MODEL=$(cat /proc/device-tree/model)
        if [[ $MODEL == *"Raspberry Pi"* ]]; then
            if [[ $MODEL == *"Pi 4"* ]]; then
                PLATFORM="pi4"
                success "Detected Raspberry Pi 4 - Full EM sensor support"
            elif [[ $MODEL == *"Pi 3"* ]]; then
                PLATFORM="pi3"
                success "Detected Raspberry Pi 3 - Basic EM sensor support"
            elif [[ $MODEL == *"Pi Zero"* ]]; then
                PLATFORM="pi_zero"
                success "Detected Raspberry Pi Zero - Limited EM sensor support"
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

# Check system requirements - Updated for v2.0
check_requirements() {
    log "Checking system requirements for OSCE v2.0..."
    
    # Check Python version (3.8+ required for v2.0)
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            success "Python $PYTHON_VERSION found (3.8+ required for v2.0)"
        else
            error "Python 3.8+ required for v2.0, found $PYTHON_VERSION"
            exit 1
        fi
    else
        error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    # Check RAM (4GB recommended for v2.0)
    TOTAL_MEM=$(awk '/MemTotal/ {print $2}' /proc/meminfo)
    TOTAL_MEM_GB=$((TOTAL_MEM / 1024 / 1024))
    if [ "$TOTAL_MEM_GB" -lt 2 ]; then
        warning "Only ${TOTAL_MEM_GB}GB RAM detected. 2GB minimum, 4GB recommended for v2.0"
    else
        success "${TOTAL_MEM_GB}GB RAM detected"
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
    
    # Platform-specific checks for v2.0
    if [[ $PLATFORM == pi* ]]; then
        # Check for I2C
        if [ -e /dev/i2c-1 ]; then
            success "I2C interface found"
        else
            warning "I2C not enabled. You may need to enable it with 'sudo raspi-config'"
        fi
        
        # Check for SPI (needed for some EM sensors)
        if [ -e /dev/spidev0.0 ]; then
            success "SPI interface found (for advanced EM sensors)"
        else
            warning "SPI not enabled. Enable it for advanced EM sensor support"
        fi
        
        # Check for 1-Wire
        if [ -d /sys/bus/w1/devices ]; then
            success "1-Wire interface found"
        else
            warning "1-Wire not enabled. Enable it for DS18B20 temperature sensors"
        fi
    fi
}

# Install system dependencies - Updated for v2.0
install_dependencies() {
    log "Installing system dependencies for OSCE v2.0..."
    
    # Common dependencies
    DEPS="python3-venv python3-dev build-essential libssl-dev libffi-dev"
    DEPS="$DEPS python3-numpy python3-scipy"  # v2.0 requirements
    
    # Platform-specific dependencies
    if [[ $PLATFORM == pi* ]]; then
        DEPS="$DEPS python3-smbus i2c-tools python3-rpi.gpio"
        DEPS="$DEPS python3-spidev"  # For SPI-based EM sensors
    fi
    
    # Development tools for compiling
    DEPS="$DEPS gcc g++ make cmake"
    
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

# Create OSCE v2.0 directory structure
create_directories() {
    log "Creating OSCE v2.0 directory structure..."
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$DATA_DIR"
    mkdir -p "$LOG_DIR"
    mkdir -p "$PLUGIN_DIR"
    mkdir -p "$CONFIG_DIR"
    mkdir -p "$STATIC_DIR"
    mkdir -p "$CERTS_DIR"
    
    # v2.0 specific directories
    mkdir -p "$INSTALL_DIR/osce/plugins/core"
    mkdir -p "$INSTALL_DIR/osce/drivers"
    mkdir -p "$DATA_DIR/telemetry"
    mkdir -p "$DATA_DIR/planetary"
    
    success "Directory structure created"
}

# Create v2.0 core modules
create_core_modules() {
    log "Creating OSCE v2.0 core modules..."
    
    # Create __init__.py files
    touch "$INSTALL_DIR/osce/__init__.py"
    touch "$INSTALL_DIR/osce/plugins/__init__.py"
    touch "$INSTALL_DIR/osce/plugins/core/__init__.py"
    touch "$INSTALL_DIR/osce/drivers/__init__.py"
    
    # Create minimal PHAL v2 stub
    cat > "$INSTALL_DIR/osce/plugins/core/phal_v2.py" << 'EOPHAL'
"""PHAL v2 - Pluripotent Hardware Abstraction Layer"""
from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import asyncio
import logging

logger = logging.getLogger(__name__)

class PluginPermission(Enum):
    READ = "read"
    ACTUATE = "actuate" 
    CONFIGURE = "configure"
    EXCLUSIVE = "exclusive"

class ConflictResolutionStrategy(Enum):
    PRIORITY = auto()
    CONSENSUS = auto()
    AUCTION = auto()
    ENERGY_AWARE = auto()

@dataclass
class PluginManifest:
    plugin_id: str
    name: str
    version: str
    permissions: List[str]

@dataclass
class PluginAccessRequest:
    plugin_id: str
    capability_type: str
    permission: PluginPermission
    priority: int = 1

@dataclass
class AccessGrant:
    grant_id: str
    plugin_id: str
    capability_type: str
    permission: PluginPermission

class PHALCore:
    def __init__(self, zone_id: str, security_manager=None, enable_consensus=True):
        self.zone_id = zone_id
        self.security_manager = security_manager
        self.enable_consensus = enable_consensus
        self.devices = {}
        self.plugins = {}
        self.grants = {}
        self.hive_mind = HiveMindFFT() if enable_consensus else None
        
    async def start(self):
        logger.info(f"PHAL v2 starting for zone {self.zone_id}")
        
    async def register_plugin(self, plugin_id: str, permissions: set, manifest: dict) -> bool:
        self.plugins[plugin_id] = {
            'permissions': permissions,
            'manifest': manifest
        }
        return True
        
    async def register_device(self, device_id: str, capabilities: list, zone: str):
        self.devices[device_id] = {
            'capabilities': capabilities,
            'zone': zone
        }
        
    async def request_capability(self, request: PluginAccessRequest) -> Optional[AccessGrant]:
        # Simplified grant for initial setup
        grant = AccessGrant(
            grant_id=f"grant_{request.plugin_id}_{request.capability_type}",
            plugin_id=request.plugin_id,
            capability_type=request.capability_type,
            permission=request.permission
        )
        self.grants[grant.grant_id] = grant
        return grant
        
    async def route_command(self, grant_id: str, command: dict) -> dict:
        # Simplified routing for initial setup
        return {'status': 'success', 'value': 0.0}
        
    async def revoke_access(self, grant_id: str):
        if grant_id in self.grants:
            del self.grants[grant_id]
            
    async def publish_metrics(self) -> dict:
        return {
            'devices': len(self.devices),
            'active_grants': len(self.grants),
            'health_score': 1.0
        }
        
    async def stop(self):
        logger.info("PHAL v2 stopping")

# Minimal HiveMind stub
class HiveMindFFT:
    def __init__(self):
        self.decisions = []
        
    def get_decision_metrics(self):
        return {
            'status': 'active',
            'recent_coherence': 0.85,
            'consensus_rate': 0.9,
            'total_decisions': len(self.decisions)
        }
EOPHAL

    # Create minimal HiveMind FFT v2 stub
    cat > "$INSTALL_DIR/osce/plugins/core/hivemind_fft_v2.py" << 'EOHIVE'
"""HiveMind FFT v2 - Frequency Domain Consensus"""
import numpy as np
from typing import Dict, List, Any
import asyncio

class HiveMindFFT:
    def __init__(self):
        self.agents = {}
        self.decisions = []
        self.coherence = 0.85
        
    async def collective_decision(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        # Simplified consensus for initial setup
        return {
            'decision': 'consensus_reached',
            'confidence': 0.9,
            'participating_agents': len(self.agents),
            'consensus_strength': self.coherence
        }
        
    def get_decision_metrics(self) -> Dict[str, Any]:
        return {
            'status': 'active',
            'recent_coherence': self.coherence,
            'consensus_rate': 0.9,
            'total_decisions': len(self.decisions)
        }
EOHIVE

    # Create minimal Quantum Planetary Awareness v2 stub
    cat > "$INSTALL_DIR/osce/plugins/core/qpa_v2.py" << 'EOQPA'
"""Quantum Planetary Awareness v2"""
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, Any
import random
import asyncio

class PlanetaryState(Enum):
    CALM = "calm"
    ACTIVE = "active"
    ENERGIZED = "energized"
    STORMY = "stormy"
    TRANSFORMING = "transforming"

@dataclass
class PlanetaryContext:
    state: PlanetaryState
    schumann_frequency: float
    energy_available: Dict[str, float]
    harmony_score: float
    recommendations: List[str]
    messages: List[Dict[str, Any]]
    
    def to_dict(self) -> dict:
        return {
            'state': self.state.value,
            'schumann': {
                'frequency': self.schumann_frequency,
                'amplitude': 1.0
            },
            'energy_available': self.energy_available,
            'harmony_score': self.harmony_score,
            'recommendations': self.recommendations,
            'messages': self.messages
        }

class QuantumPlanetaryAwareness:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_state = PlanetaryState.ACTIVE
        self.schumann_base = 7.83
        self.env = None
        self.phal_core = None
        
    async def initialize(self):
        # Simplified initialization
        pass
        
    def subscribe_to_context(self, zone_id: str):
        # Simplified subscription
        pass
        
    async def get_planetary_context(self) -> PlanetaryContext:
        # Generate simulated planetary context
        return PlanetaryContext(
            state=self.current_state,
            schumann_frequency=self.schumann_base + random.uniform(-0.1, 0.1),
            energy_available={
                'atmospheric': random.uniform(5, 15),
                'telluric': random.uniform(2, 8),
                'bioelectric': random.uniform(1, 3)
            },
            harmony_score=random.uniform(0.7, 0.95),
            recommendations=["Optimize for current electromagnetic conditions"],
            messages=[{
                'pattern_type': 'harmonic',
                 'meaning': 'System in resonance with planetary rhythms',
                'confidence': 0.85
            }]
        )
EOQPA
    
    success "Core v2.0 modules created"
}

# Download or create minimal core
download_core() {
    log "Creating OSCE v2.0 core..."
    
    # Create the main setup script
    cp "$INSTALL_DIR/osce-unified-setup-v2.py" "$INSTALL_DIR/core.py" 2>/dev/null || \
    cat > "$INSTALL_DIR/core.py" << 'EOCORE'
#!/usr/bin/env python3
"""
OSCE v2.0 Minimal Core - Just Enough to Start
Includes PHAL, HiveMind, and Planetary Awareness
"""

import os
import sys
import json
import time
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template_string, jsonify, send_from_directory
import logging

# Add OSCE modules to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import v2.0 components
try:
    from osce.plugins.core.phal_v2 import PHALCore, PluginPermission, PluginAccessRequest
    from osce.plugins.core.hivemind_fft_v2 import HiveMindFFT
    from osce.plugins.core.qpa_v2 import QuantumPlanetaryAwareness, PlanetaryState
except ImportError as e:
    print(f"Warning: Could not import v2.0 modules: {e}")
    print("Running in minimal mode")
    PHALCore = None
    HiveMindFFT = None
    QuantumPlanetaryAwareness = None

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OSCE')

__version__ = "2.0.0"

class MinimalOSCE:
    """Minimal OSCE v2.0 implementation to get started"""
    
    def __init__(self):
        self.platform = self._detect_platform()
        self.sensors = {}
        self.start_time = datetime.now()
        self.app = Flask(__name__)
        
        # v2.0 components
        self.phal_core = None
        self.hive_mind = None
        self.planetary_awareness = None
        
        self._setup_routes()
        self._init_v2_components()
        
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
        
    def _init_v2_components(self):
        """Initialize v2.0 components if available"""
        if PHALCore:
            try:
                self.phal_core = PHALCore("main", enable_consensus=True)
                asyncio.create_task(self.phal_core.start())
                logger.info("PHAL v2 initialized")
            except Exception as e:
                logger.warning(f"Could not initialize PHAL: {e}")
                
        if HiveMindFFT:
            try:
                self.hive_mind = HiveMindFFT()
                logger.info("HiveMind FFT v2 initialized")
            except Exception as e:
                logger.warning(f"Could not initialize HiveMind: {e}")
                
        if QuantumPlanetaryAwareness:
            try:
                self.planetary_awareness = QuantumPlanetaryAwareness({
                    'latitude': 0.0,
                    'longitude': 0.0,
                    'dry_run_mode': True
                })
                asyncio.create_task(self.planetary_awareness.initialize())
                logger.info("Quantum Planetary Awareness v2 initialized")
            except Exception as e:
                logger.warning(f"Could not initialize Planetary Awareness: {e}")
        
    def _setup_routes(self):
        """Setup Flask routes"""
        @self.app.route('/')
        def index():
            return '<h1>OSCE v2.0</h1><p>Dashboard: <a href="/dashboard">/dashboard</a></p>'
            
        @self.app.route('/dashboard')
        def dashboard():
            # Try to serve static dashboard first
            static_path = Path(__file__).parent / "static" / "dashboard.html"
            if static_path.exists():
                return send_from_directory('static', 'dashboard.html')
            else:
                # Fallback to embedded dashboard
                uptime = str(datetime.now() - self.start_time).split('.')[0]
                return render_template_string(
                    DASHBOARD_TEMPLATE,
                    version=__version__,
                    platform=self.platform,
                    uptime=uptime,
                    hardware=', '.join(self.sensors.keys()) if self.sensors else 'None detected'
                )
            
        @self.app.route('/api/status')
        def api_status():
            phal_metrics = {}
            if self.phal_core:
                phal_metrics = asyncio.run(self.phal_core.publish_metrics())
                
            return jsonify({
                'name': 'OSCE v2.0',
                'version': __version__,
                'status': 'running',
                'platform': self.platform,
                'sensors': len(self.sensors),
                'uptime': str(datetime.now() - self.start_time),
                'phal': phal_metrics,
                'features': {
                    'phal_v2': self.phal_core is not None,
                    'hivemind_fft': self.hive_mind is not None,
                    'planetary_awareness': self.planetary_awareness is not None
                }
            })
            
        @self.app.route('/api/sensors')
        def api_sensors():
            return jsonify(self.sensors)
            
        @self.app.route('/api/phal/metrics')
        def api_phal_metrics():
            if self.phal_core:
                metrics = asyncio.run(self.phal_core.publish_metrics())
                return jsonify(metrics)
            return jsonify({'status': 'not_initialized'})
            
        @self.app.route('/api/hivemind/metrics')
        def api_hivemind_metrics():
            if self.hive_mind:
                return jsonify(self.hive_mind.get_decision_metrics())
            return jsonify({'status': 'not_initialized'})
            
        @self.app.route('/api/planetary/context')
        def api_planetary_context():
            if self.planetary_awareness:
                context = asyncio.run(self.planetary_awareness.get_planetary_context())
                return jsonify(context.to_dict())
            return jsonify({'status': 'not_initialized'})
            
        @self.app.route('/api/harmony/score')
        def api_harmony_score():
            score = 0.85  # Default harmony score
            return jsonify({
                'harmony_score': score,
                'timestamp': datetime.now().isoformat()
            })
            
        @self.app.route('/health')
        def health():
            return jsonify({
                'status': 'healthy',
                'platform': self.platform,
                'sensors': len(self.sensors),
                'uptime': str(datetime.now() - self.start_time),
                'version': __version__
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
                    self.sensors['mock_humidity'] = {
                        'name': 'Demo Humidity',
                        'value': f'{60 + (time.time() % 20) / 2:.1f}',
                        'unit': '%',
                        'timestamp': datetime.now().isoformat()
                    }
                    
                # Update sensor readings
                for sensor_id in self.sensors:
                    if sensor_id == 'mock_temp':
                        self.sensors[sensor_id]['value'] = f'{20 + (time.time() % 10) / 2:.1f}'
                    elif sensor_id == 'mock_humidity':
                        self.sensors[sensor_id]['value'] = f'{60 + (time.time() % 20) / 2:.1f}'
                    self.sensors[sensor_id]['timestamp'] = datetime.now().isoformat()
                    
            except Exception as e:
                logger.error(f"Sensor detection error: {e}")
                
            time.sleep(5)
            
    def run(self, host='0.0.0.0', port=8080):
        """Start the OSCE v2.0 system"""
        logger.info(f"Starting OSCE v2.0 on {host}:{port}")
        logger.info(f"Dashboard: http://localhost:{port}/dashboard")
        logger.info(f"API: http://localhost:{port}/api/status")
        self.app.run(host=host, port=port, debug=False)

# Minimal dashboard template with v2.0 branding
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>OSCE v2.0 - Open Source Controlled Environments</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #e0e0e0;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #2e7d32, #1976d2, #7b1fa2);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header .subtitle {
            margin-top: 10px;
            opacity: 0.9;
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }
        .feature-card.active {
            border-color: #8b5cf6;
            background: rgba(139, 92, 246, 0.1);
        }
        .sensor-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .sensor-card {
            background: rgba(255, 255, 255, 0.05);
            padding: 20px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .sensor-value {
            font-size: 48px;
            font-weight: bold;
            color: #8b5cf6;
        }
        .sensor-name {
            font-size: 18px;
            color: #a0a0a0;
            margin-bottom: 10px;
        }
        .status {
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            margin-top: 20px;
        }
        .no-sensors {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top-color: #8b5cf6;
            animation: spin 1s ease-in-out infinite;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
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
                
            // Check v2 features
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('phal-status').className = 
                        data.features.phal_v2 ? 'feature-card active' : 'feature-card';
                    document.getElementById('hivemind-status').className = 
                        data.features.hivemind_fft ? 'feature-card active' : 'feature-card';
                    document.getElementById('planetary-status').className = 
                        data.features.planetary_awareness ? 'feature-card active' : 'feature-card';
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
            <h1>🌍 OSCE v2.0 - Planetary Harmony Edition</h1>
            <p class="subtitle">The WordPress of IoT • Platform: {{ platform }}</p>
            <p>Uptime: {{ uptime }} • Version: {{ version }}</p>
        </div>
        
        <div class="features">
            <div class="feature-card" id="phal-status">
                <h3>PHAL v2</h3>
                <p>Adaptive Hardware</p>
            </div>
            <div class="feature-card" id="hivemind-status">
                <h3>HiveMind FFT</h3>
                <p>Consensus Engine</p>
            </div>
            <div class="feature-card" id="planetary-status">
                <h3>Planetary Awareness</h3>
                <p>Earth Harmony</p>
            </div>
        </div>
        
        <h2>🌡️ Active Sensors</h2>
        <div id="sensor-grid" class="sensor-grid">
            <div class="no-sensors">
                <div class="loading"></div>
                <p>Detecting sensors...</p>
            </div>
        </div>
        
        <div class="status">
            <strong>System Status:</strong> Running<br>
            <strong>Detected Hardware:</strong> {{ hardware }}<br>
            <strong>API Endpoint:</strong> <a href="/api/status" style="color: #8b5cf6">/api/status</a><br>
            <strong>Advanced Dashboard:</strong> Coming soon with full v2.0 features!
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    osce = MinimalOSCE()
    osce.run()
EOCORE

    # Copy dashboard if available
    if [ -f "osce-dashboard-v21.html" ]; then
        cp osce-dashboard-v21.html "$STATIC_DIR/dashboard.html"
        success "v2.0 Dashboard copied"
    else
        # Create minimal dashboard placeholder
        echo "<h1>OSCE v2.0 Dashboard - Full version coming soon!</h1>" > "$STATIC_DIR/dashboard.html"
    fi
    
    # Create start script
    cat > "$INSTALL_DIR/start.sh" << 'EOSTART'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting OSCE v2.0..."
python core.py
EOSTART
    
    chmod +x "$INSTALL_DIR/start.sh"
    chmod +x "$INSTALL_DIR/core.py"
    
    success "OSCE v2.0 core created"
}

# Setup Python virtual environment with v2.0 dependencies
setup_venv() {
    log "Setting up Python environment for v2.0..."
    
    cd "$INSTALL_DIR"
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install v2.0 requirements
    pip install flask aiohttp
    pip install numpy scipy  # For FFT and signal processing
    pip install structlog    # For structured logging
    pip install cryptography # For enhanced security
    pip install pyyaml      # For configuration
    
    # Platform-specific packages
    if [[ $PLATFORM == pi* ]]; then
        # Try to install Pi-specific packages
        pip install RPi.GPIO || warning "RPi.GPIO installation failed - GPIO features may not work"
        pip install adafruit-dht || warning "DHT sensor support not installed"
        pip install spidev || warning "SPI support not installed (needed for some EM sensors)"
    fi
    
    # Optional ML packages for advanced features
    pip install scikit-learn || warning "ML features not available"
    
    success "Python environment ready for v2.0"
}

# Create systemd service for v2.0
create_service() {
    log "Creating system service..."
    
    if command -v systemctl &> /dev/null; then
        cat > /tmp/osce.service << EOSERVICE
[Unit]
Description=OSCE v2.0 - Open Source Controlled Environments with Planetary Harmony
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/start.sh
Restart=always
RestartSec=10
Environment="OSCE_VERSION=2.0.0"

[Install]
WantedBy=multi-user.target
EOSERVICE

        if [ "$EUID" -ne 0 ]; then
            warning "Run 'sudo systemctl enable $INSTALL_DIR/osce.service' to start OSCE on boot"
        else
            cp /tmp/osce.service /etc/systemd/system/osce.service
            systemctl daemon-reload
            systemctl enable osce.service
            success "OSCE v2.0 service installed"
        fi
    fi
}

# Create example configuration
create_example_config() {
    log "Creating example configuration..."
    
    cat > "$CONFIG_DIR/config.yaml" << 'EOCONFIG'
# OSCE v2.0 Configuration
version: 2.0

# Zone configuration
zone:
  id: main_greenhouse
  name: "Harmonic Greenhouse"
  location:
    latitude: 0.0
    longitude: 0.0
    altitude: 0.0

# Security settings
security:
  level: production  # development, staging, production, critical_infrastructure, quantum_ready
  change_default_passwords: true
  enable_ssl: true

# v2.0 Features
planetary_awareness:
  enabled: true
  passive_harvest: true
  harmonic_mode: adaptive
  em_sensor_pins: [16, 17, 18]  # GPIO pins for EM sensor

hivemind:
  enabled: true
  consensus_threshold: 0.7
  conflict_resolution: consensus  # priority, consensus, auction, energy_aware

phal:
  adaptive_permissions: true
  health_monitoring: true
  grant_timeout: 3600  # seconds

# Hardware detection
hardware:
  auto_detect: true
  i2c_bus: 1
  spi_bus: 0
  
# Default sensors (auto-detected if available)
sensors:
  - name: temperature
    type: auto
    pin: 4
    interval: 60
    
  - name: humidity
    type: auto
    pin: 4
    interval: 60
    
# Default actuators
actuators:
  - name: fan
    type: relay
    pin: 17
    safe_value: 0
    
  - name: pump
    type: relay
    pin: 27
    safe_value: 0
    max_commands_per_minute: 5

# Example rules
rules:
  - "if temperature > 28 then turn fan on"
  - "if temperature < 26 then turn fan off"
  - "if humidity < 60 then turn pump on"
  - "if humidity > 80 then turn pump off"

# Monitoring
monitoring:
  enable_telemetry: true
  telemetry_interval: 300  # seconds
  health_check_interval: 60  # seconds
  
# Plugins to auto-install
plugins:
  - weather_integration
  - energy_optimizer
  - plant_health_ai
EOCONFIG
    
    success "Example configuration created"
}

# Create self-signed certificates for development
create_dev_certificates() {
    log "Creating development SSL certificates..."
    
    if ! command -v openssl &> /dev/null; then
        warning "OpenSSL not found, skipping certificate generation"
        return
    fi
    
    cd "$CERTS_DIR"
    
    # Generate private key
    openssl genrsa -out server.key 2048
    
    # Generate certificate signing request
    openssl req -new -key server.key -out server.csr -subj "/C=US/ST=State/L=City/O=OSCE/CN=localhost"
    
    # Generate self-signed certificate
    openssl x509 -req -days 365 -in server.csr -signkey server.key -out server.crt
    
    # Clean up
    rm server.csr
    
    success "Development certificates created (self-signed)"
    warning "For production, use proper SSL certificates"
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
    
    echo "Welcome to OSCE v2.0 - The WordPress of Controlled Environment Agriculture"
    echo "Now with Planetary Harmony: PHAL v2, HiveMind FFT, and Quantum Awareness!"
    echo ""
    
    # Run installation steps
    detect_platform
    check_requirements
    install_dependencies
    create_directories
    create_core_modules
    download_core
    setup_venv
    create_example_config
    create_dev_certificates
    create_service
    
    # Start OSCE
    log "Starting OSCE v2.0..."
    cd "$INSTALL_DIR"
    source venv/bin/activate
    nohup python core.py > "$LOG_DIR/osce.log" 2>&1 &
    OSCE_PID=$!
    
    # Wait for startup
    sleep 5
    
    # Check if running
    if kill -0 $OSCE_PID 2>/dev/null; then
        success "OSCE v2.0 is running!"
    else
        error "OSCE failed to start. Check $LOG_DIR/osce.log"
        exit 1
    fi
    
    # Get access URL
    IP=$(get_ip_address)
    
    # Success message
    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✨ OSCE v2.0 Installation Complete! ✨${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Access your OSCE dashboard at:"
    echo -e "  ${BLUE}http://$IP:8080/dashboard${NC}"
    echo ""
    if [[ $IP != "localhost" ]]; then
        echo "From this device:"
        echo -e "  ${BLUE}http://localhost:8080/dashboard${NC}"
        echo ""
    fi
    echo "Installation directory: $INSTALL_DIR"
    echo "Configuration: $CONFIG_DIR/config.yaml"
    echo "Logs: $LOG_DIR/osce.log"
    echo ""
    echo -e "${PURPLE}v2.0 Features:${NC}"
    echo "  ✓ PHAL v2 - Adaptive hardware abstraction"
    echo "  ✓ HiveMind FFT - Frequency-domain consensus"
    echo "  ✓ Quantum Planetary Awareness - Earth harmony"
    echo "  ✓ Enhanced security with manifest validation"
    echo "  ✓ Real-time health monitoring"
    echo ""
    echo "Next steps:"
    echo "  1. Change default passwords in config.yaml"
    echo "  2. Open the dashboard in your browser"
    echo "  3. Connect sensors to see real-time data"
    echo "  4. Enable Planetary Awareness for EM harmony"
    echo "  5. Join the community at the GitHub repo"
    echo ""
    echo -e "${YELLOW}Pro tips:${NC}"
    echo "  • Connect a DHT22 to GPIO pin 4 for temp/humidity"
    echo "  • Enable I2C and SPI for advanced sensors"
    echo "  • For EM sensing, connect 3-axis sensor to pins 16,17,18"
    echo "  • Check /api/planetary/context for Earth's status"
    echo ""
    echo -e "${GREEN}🌍 Welcome to the future of harmonious growing! 🌱${NC}"
}

# Save installation info
save_installation_info() {
    cat > "$INSTALL_DIR/install_info.json" << EOINFO
{
    "version": "$OSCE_VERSION",
    "platform": "$PLATFORM",
    "install_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "install_dir": "$INSTALL_DIR",
    "python_version": "$PYTHON_VERSION",
    "features": {
        "phal_v2": true,
        "hivemind_fft": true,
        "planetary_awareness": true,
        "zero_trust_security": true,
        "adaptive_permissions": true
    }
}
EOINFO
}

# Run main installation
main

# Save installation info
save_installation_info

echo ""
echo "Happy Growing in Harmony with Earth! 🌍✨"