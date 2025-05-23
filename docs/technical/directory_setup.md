# Directory Structure Setup & Basic Configurations

## Create Directory Structure (Run this script)

```bash
#!/bin/bash
# create_structure.sh - Creates basic directory structure

# Create main directories
mkdir -p .github/{ISSUE_TEMPLATE,PULL_REQUEST_TEMPLATE,workflows}
mkdir -p setup/{hardware_tests,configuration_wizard,dependencies}
mkdir -p src/{core,sensors,actuators,web,database,utils}
mkdir -p hardware/{compatibility,wiring_diagrams,3d_models,safety}
mkdir -p config/{profiles,crops,systems,environments,templates}
mkdir -p examples/{basic_monitoring,hydroponic_system,classroom_setup,therapy_garden}
mkdir -p docs/{user_guides,technical,educational,therapeutic,community}
mkdir -p tests/{unit,integration,hardware,fixtures}
mkdir -p tools/{development,deployment,maintenance}
mkdir -p assets/{images,videos,presentations}
mkdir -p community/{contributions,showcase,events}

echo "Directory structure created successfully!"
```

## File: `config/profiles/educator.json`

```json
{
  "profile_name": "educator",
  "display_name": "Educational Environment",
  "description": "Configuration optimized for classroom use",
  "safety_level": "high",
  "complexity_level": "simplified",
  "features": {
    "student_tracking": true,
    "simplified_interface": true,
    "safety_interlocks": true,
    "data_logging": true,
    "photo_journaling": true,
    "assessment_tools": true
  },
  "dashboard": {
    "theme": "educational",
    "widgets": [
      "temperature_gauge",
      "humidity_gauge", 
      "growth_photos",
      "daily_activities",
      "safety_status"
    ],
    "student_access": {
      "view_data": true,
      "control_lights": false,
      "control_pumps": false,
      "emergency_stop": true
    }
  },
  "alerts": {
    "temperature_range": {"min": 18, "max": 26},
    "humidity_range": {"min": 40, "max": 70},
    "notification_methods": ["dashboard", "email"],
    "emergency_contacts": ["teacher@school.edu"]
  },
  "data_retention": {
    "student_data": "1_semester",
    "sensor_data": "1_year",
    "photos": "1_year"
  },
  "safety": {
    "voltage_limit": "12V",
    "chemical_restrictions": ["ph_solutions_diluted_only"],
    "supervision_required": true,
    "age_restrictions": "6+"
  }
}
```

## File: `config/crops/leafy_greens.json`

```json
{
  "crop_category": "leafy_greens",
  "display_name": "Leafy Greens (Lettuce, Spinach, Kale)",
  "crops": ["lettuce", "spinach", "kale", "arugula", "swiss_chard"],
  "growth_stages": {
    "germination": {
      "duration_days": "3-7",
      "temperature": {"day": 22, "night": 18},
      "humidity": {"min": 60, "max": 80},
      "light_hours": 16,
      "ph_range": {"min": 5.5, "max": 6.5},
      "ec_range": {"min": 0.8, "max": 1.2}
    },
    "seedling": {
      "duration_days": "7-14", 
      "temperature": {"day": 20, "night": 16},
      "humidity": {"min": 50, "max": 70},
      "light_hours": 14,
      "ph_range": {"min": 5.8, "max": 6.2},
      "ec_range": {"min": 1.0, "max": 1.6}
    },
    "vegetative": {
      "duration_days": "14-30",
      "temperature": {"day": 18, "night": 14},
      "humidity": {"min": 45, "max": 65},
      "light_hours": 12,
      "ph_range": {"min": 5.8, "max": 6.2},
      "ec_range": {"min": 1.2, "max": 2.0}
    },
    "harvest": {
      "duration_days": "30-45",
      "indicators": ["leaf_size_mature", "color_vibrant"],
      "harvest_method": "cut_and_come_again"
    }
  },
  "nutrients": {
    "primary": "balanced_leafy_green",
    "n_p_k_ratio": "3-1-2",
    "supplements": ["calcium", "magnesium"],
    "deficiency_symptoms": {
      "nitrogen": "yellowing_lower_leaves",
      "phosphorus": "purple_leaf_edges",
      "potassium": "brown_leaf_tips"
    }
  },
  "common_issues": {
    "tip_burn": "reduce_ec_increase_airflow",
    "bolting": "reduce_temperature_increase_light",
    "slow_growth": "check_ph_increase_nutrients"
  }
}
```

## File: `config/systems/basic_monitoring.json`

```json
{
  "system_name": "basic_monitoring",
  "display_name": "Basic Environmental Monitoring",
  "description": "Simple temperature and humidity monitoring with basic controls",
  "complexity": "beginner",
  "estimated_cost": "$75-150",
  "hardware_requirements": {
    "raspberry_pi": "Pi 4B 2GB minimum",
    "sensors": [
      {
        "type": "temperature",
        "model": "DS18B20",
        "quantity": 1,
        "interface": "1-wire",
        "gpio": 4
      },
      {
        "type": "humidity", 
        "model": "DHT22",
        "quantity": 1,
        "interface": "digital",
        "gpio": 17
      }
    ],
    "actuators": [
      {
        "type": "relay",
        "model": "2-channel_relay_board",
        "quantity": 1,
        "controls": ["grow_light", "exhaust_fan"]
      }
    ]
  },
  "automation_rules": {
    "temperature_control": {
      "target": 22,
      "tolerance": 2,
      "heating_device": "grow_light",
      "cooling_device": "exhaust_fan"
    },
    "humidity_control": {
      "target": 60,
      "tolerance": 10,
      "action": "ventilation_adjustment"
    },
    "lighting_schedule": {
      "on_time": "06:00",
      "off_time": "22:00",
      "override": "manual_allowed"
    }
  },
  "data_logging": {
    "interval_minutes": 5,
    "retention_days": 30,
    "metrics": ["temperature", "humidity", "light_status", "fan_status"]
  }
}
```

## File: `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# Configuration with secrets
.env
config/secrets.json
config/local_config.json

# Hardware-specific
hardware/custom_configs/
calibration_data/

# Backup files
backups/
*.backup
*.bak

# Temporary files
tmp/
temp/
*.tmp

# Photo storage (keep structure, ignore content)
data/photos/*
!data/photos/.gitkeep

# User data
user_data/
student_records/
therapy_records/

# Compiled documentation
docs/_build/
docs/site/

# Test coverage
.coverage
htmlcov/

# Security
*.key
*.pem
*.crt
secrets/
```

## File: `requirements.txt`

```
# Core dependencies
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-WTF==1.1.1
WTForms==3.0.1

# Hardware interfaces
RPi.GPIO==0.7.1
gpiozero==1.6.2
spidev==3.6
smbus2==0.4.2
w1thermsensor==2.0.0

# Sensor libraries
adafruit-circuitpython-ads1x15==2.2.21
adafruit-circuitpython-bme280==2.6.15
adafruit-circuitpython-dht==3.7.8

# Data handling
pandas==2.0.3
numpy==1.24.4
influxdb-client==1.37.0
redis==4.6.0

# Web and API
requests==2.31.0
gunicorn==21.2.0
eventlet==0.33.3

# Automation and scheduling
APScheduler==3.10.4
celery==5.3.1

# Image processing
Pillow==10.0.0
opencv-python==4.8.0.76

# Communication protocols
pyserial==3.5
paho-mqtt==1.6.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3
psutil==5.9.5
configparser==6.0.0

# Development and testing
pytest==7.4.2
pytest-cov==4.1.0
black==23.7.0
flake8==6.0.0
```

## File: `Makefile`

```makefile
# Container Farm Control System Makefile

.PHONY: help install test clean setup-dev lint format

help:
	@echo "Container Farm Control System"
	@echo "Available commands:"
	@echo "  install    - Install system dependencies and setup"
	@echo "  test       - Run all tests"
	@echo "  setup-dev  - Setup development environment"
	@echo "  lint       - Run code linting"
	@echo "  format     - Format code"
	@echo "  clean      - Clean temporary files"

install:
	@echo "Installing Container Farm Control System..."
	sudo ./setup/setup.sh

test:
	@echo "Running tests..."
	python -m pytest tests/ -v

setup-dev:
	@echo "Setting up development environment..."
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	. venv/bin/activate && pip install -r setup/dependencies/dev_requirements.txt

lint:
	@echo "Running linting..."
	flake8 src/ tests/
	black --check src/ tests/

format:
	@echo "Formatting code..."
	black src/ tests/
	isort src/ tests/

clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf build/ dist/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
```
