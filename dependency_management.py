# Requirements and setup files for production deployment

# === requirements.in ===
# Core dependencies with pinned versions for production stability
# Use pip-compile to generate requirements.txt with hashes

# Core Framework
Flask==2.3.3
flask-cors==4.0.0
flask-limiter==3.5.0
flask-bcrypt==1.0.1
flask-restx==1.2.0

# Authentication & Security
PyJWT==2.8.0
python-dotenv==1.0.0
cryptography==41.0.4

# Database
SQLAlchemy==2.0.21
alembic==1.12.0
redis==5.0.0

# Hardware Interface (Raspberry Pi)
RPi.GPIO==0.7.1
adafruit-circuitpython-dht==4.0.2
w1thermsensor==2.0.0
smbus2==0.4.3

# Monitoring & Logging
prometheus-client==0.17.1
python-json-logger==2.0.7

# Task Queue
celery==5.3.4
celery[redis]==5.3.4

# Data Processing
pandas==2.1.1
numpy==1.25.2

# Testing
pytest==7.4.2
pytest-cov==4.1.0
pytest-mock==3.11.1
factory-boy==3.3.0

# Development
black==23.9.1
flake8==6.1.0
mypy==1.5.1
pre-commit==3.4.0

# === setup.py ===
"""
Setup configuration for OpenSourceControlledEnvironments
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="opensourcecontrolledenvironments",
    version="1.0.0",
    author="HydroFarmerJason",
    author_email="",
    description="Open source controlled environment agriculture system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.9",
    install_requires=[
        # List core requirements here
        # Full list in requirements.txt
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.2",
            "black>=23.9.1",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "farm-controller=farm.cli:main",
            "farm-api=farm.api:run_server",
        ],
    },
)

# === pyproject.toml ===
"""
Modern Python project configuration
"""

[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "opensourcecontrolledenvironments"
version = "1.0.0"
description = "Open source controlled environment agriculture system"
readme = "README.md"
requires-python = ">=3.9"
license = {text = "MIT"}
authors = [
    {name = "HydroFarmerJason"},
]
maintainers = [
    {name = "HydroFarmerJason"},
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
]

[project.urls]
Homepage = "https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments"
Documentation = "https://hydrofarmerjason.github.io/OpenSourceControlledEnvironments"
Repository = "https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments"
"Bug Tracker" = "https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/issues"

[tool.black]
line-length = 100
target-version = ['py39', 'py310', 'py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
line_length = 100
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_return_any = true
strict_equality = true

[tool.pytest.ini_options]
minversion = "7.0"
addopts = [
    "-ra",
    "--strict-markers",
    "--cov=src",
    "--cov-branch",
    "--cov-report=term-missing:skip-covered",
    "--cov-report=html",
    "--cov-report=xml",
]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if __name__ == .__main__.:",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if False:",
]

# === .env.example ===
"""
Environment configuration template
Copy to .env and update with your values
"""

# Security
SECRET_KEY=change_this_to_random_secret_key
JWT_SECRET_KEY=change_this_to_different_random_secret
SESSION_COOKIE_SECURE=True

# Database
DATABASE_URL=sqlite:///farm_data.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/farmdb

# Redis (for caching and Celery)
REDIS_URL=redis://localhost:6379/0

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_DEBUG=False

# Rate Limiting
RATE_LIMIT_DEFAULT=100 per hour
RATE_LIMIT_LOGIN=5 per minute

# Hardware Configuration
GPIO_MODE=BCM
TEMPERATURE_SENSOR_PIN=4
HUMIDITY_SENSOR_PIN=17
LIGHT_SENSOR_I2C_ADDRESS=0x23

# Monitoring
PROMETHEUS_PORT=9090
LOG_LEVEL=INFO
LOG_FILE=/var/log/farm/app.log

# Backup Configuration
BACKUP_DIR=/home/pi/backups
REMOTE_BACKUP_HOST=
REMOTE_BACKUP_USER=
REMOTE_BACKUP_DIR=

# External Services (optional)
WEATHER_API_KEY=
MQTT_BROKER=
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=

# Email Notifications (optional)
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
NOTIFICATION_EMAIL=

# === install_dependencies.py ===
"""
Automated dependency installation and verification
"""

import subprocess
import sys
import os
import platform
from pathlib import Path

class DependencyInstaller:
    """Handle dependency installation and verification"""
    
    def __init__(self):
        self.python_version = sys.version_info
        self.is_raspberry_pi = self._detect_raspberry_pi()
        self.venv_path = Path("venv")
    
    def _detect_raspberry_pi(self) -> bool:
        """Detect if running on Raspberry Pi"""
        try:
            with open('/proc/device-tree/model', 'r') as f:
                return 'Raspberry Pi' in f.read()
        except:
            return False
    
    def check_python_version(self):
        """Verify Python version meets requirements"""
        if self.python_version < (3, 9):
            print(f"Error: Python 3.9+ required, found {self.python_version.major}.{self.python_version.minor}")
            sys.exit(1)
        print(f"✓ Python {self.python_version.major}.{self.python_version.minor} detected")
    
    def install_system_dependencies(self):
        """Install system-level dependencies"""
        print("\nInstalling system dependencies...")
        
        system_packages = [
            "python3-dev",
            "python3-pip",
            "python3-venv",
            "build-essential",
            "libssl-dev",
            "libffi-dev",
            "git",
            "redis-server",
        ]
        
        if self.is_raspberry_pi:
            system_packages.extend([
                "python3-smbus",
                "i2c-tools",
                "python3-rpi.gpio",
            ])
        
        try:
            # Update package list
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            
            # Install packages
            subprocess.run(
                ["sudo", "apt-get", "install", "-y"] + system_packages,
                check=True
            )
            print("✓ System dependencies installed")
        except subprocess.CalledProcessError as e:
            print(f"Error installing system dependencies: {e}")
            sys.exit(1)
    
    def create_virtual_environment(self):
        """Create Python virtual environment"""
        if not self.venv_path.exists():
            print("\nCreating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
            print("✓ Virtual environment created")
        else:
            print("✓ Virtual environment already exists")
    
    def activate_virtual_environment(self):
        """Get activation command for virtual environment"""
        if platform.system() == "Windows":
            return str(self.venv_path / "Scripts" / "activate")
        else:
            return f"source {self.venv_path / 'bin' / 'activate'}"
    
    def install_python_dependencies(self):
        """Install Python package dependencies"""
        print("\nInstalling Python dependencies...")
        
        pip_executable = str(self.venv_path / "bin" / "pip")
        
        # Upgrade pip
        subprocess.run([pip_executable, "install", "--upgrade", "pip"], check=True)
        
        # Install pip-tools
        subprocess.run([pip_executable, "install", "pip-tools"], check=True)
        
        # Compile requirements with hashes
        if Path("requirements.in").exists():
            print("Compiling requirements with hashes...")
            subprocess.run([
                str(self.venv_path / "bin" / "pip-compile"),
                "requirements.in",
                "--generate-hashes",
                "--resolver=backtracking"
            ], check=True)
        
        # Install from requirements.txt
        if Path("requirements.txt").exists():
            subprocess.run([
                pip_executable,
                "install",
                "-r", "requirements.txt",
                "--require-hashes"
            ], check=True)
            print("✓ Python dependencies installed")
        else:
            print("Warning: requirements.txt not found")
    
    def setup_raspberry_pi(self):
        """Additional setup for Raspberry Pi"""
        if not self.is_raspberry_pi:
            return
        
        print("\nConfiguring Raspberry Pi...")
        
        # Enable I2C
        subprocess.run(["sudo", "raspi-config", "nonint", "do_i2c", "0"], check=True)
        
        # Add user to gpio group
        subprocess.run(["sudo", "usermod", "-a", "-G", "gpio", os.environ.get("USER", "pi")], check=True)
        
        print("✓ Raspberry Pi configured")
        print("Note: You may need to reboot for I2C changes to take effect")
    
    def create_directory_structure(self):
        """Create required directory structure"""
        print("\nCreating directory structure...")
        
        directories = [
            "src/farm",
            "src/farm/api",
            "src/farm/sensors",
            "src/farm/actuators",
            "src/farm/controllers",
            "src/farm/database",
            "src/farm/utils",
            "tests",
            "logs",
            "data",
            "config",
            "docs",
            "scripts",
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        
        print("✓ Directory structure created")
    
    def create_env_file(self):
        """Create .env file from template"""
        if not Path(".env").exists() and Path(".env.example").exists():
            print("\nCreating .env file...")
            import shutil
            shutil.copy(".env.example", ".env")
            print("✓ .env file created")
            print("Important: Update .env with your configuration values")
    
    def run_initial_tests(self):
        """Run basic tests to verify installation"""
        print("\nRunning installation tests...")
        
        pip_executable = str(self.venv_path / "bin" / "python")
        
        # Test imports
        test_script = """
import sys
import flask
import jwt
import RPi.GPIO as GPIO if 'RPi' in sys.modules else None
print("✓ All imports successful")
"""
        
        result = subprocess.run(
            [pip_executable, "-c", test_script],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Warning: Some imports failed (this is normal on non-Pi systems)")
    
    def print_next_steps(self):
        """Print next steps for user"""
        print("\n" + "="*50)
        print("Installation Complete!")
        print("="*50)
        print("\nNext steps:")
        print(f"1. Activate virtual environment: {self.activate_virtual_environment()}")
        print("2. Update configuration in .env file")
        print("3. Run database migrations: alembic upgrade head")
        print("4. Start the application: python -m farm.api")
        print("\nFor development:")
        print("- Run tests: pytest")
        print("- Format code: black src/ tests/")
        print("- Type checking: mypy src/")

def main():
    """Main installation process"""
    installer = DependencyInstaller()
    
    print("OpenSource Controlled Environments - Dependency Installation")
    print("="*60)
    
    # Run installation steps
    installer.check_python_version()
    installer.install_system_dependencies()
    installer.create_virtual_environment()
    installer.install_python_dependencies()
    installer.setup_raspberry_pi()
    installer.create_directory_structure()
    installer.create_env_file()
    installer.run_initial_tests()
    installer.print_next_steps()

if __name__ == "__main__":
    main()