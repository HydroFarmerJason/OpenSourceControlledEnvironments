#!/bin/bash

# Container Farm Control System Setup Script
# For OpenSourceControlledEnvironments by HydroFarmerJason
# This script sets up all dependencies and system configuration

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Starting Container Farm Control System Setup..."

# Update system packages
print_status "Updating system packages..."
apt-get update -y
apt-get upgrade -y

# Install essential system packages
print_status "Installing essential system packages..."
apt-get install -y \
    curl \
    wget \
    git \
    unzip \
    build-essential \
    cmake \
    pkg-config \
    libjpeg-dev \
    libtiff5-dev \
    libpng-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libfontconfig1-dev \
    libcairo2-dev \
    libgdk-pixbuf2.0-dev \
    libpango1.0-dev \
    libgtk2.0-dev \
    libgtk-3-dev \
    libatlas-base-dev \
    gfortran \
    libhdf5-dev \
    libhdf5-serial-dev \
    libhdf5-103 \
    python3-pyqt5 \
    python3-dev \
    python3-pip \
    python3-venv

# Install Python 3 and pip
print_status "Setting up Python environment..."
apt-get install -y python3 python3-pip python3-dev python3-setuptools python3-wheel python3-venv

# Install system libraries for hardware communication
print_status "Installing hardware communication libraries..."
apt-get install -y \
    i2c-tools \
    libi2c-dev \
    python3-smbus \
    python3-rpi.gpio \
    gpsd \
    gpsd-clients \
    python3-gps \
    bluetooth \
    libbluetooth-dev

# Install database systems
print_status "Installing database systems..."
apt-get install -y \
    sqlite3 \
    libsqlite3-dev \
    influxdb \
    influxdb-client

# Install web server and related packages
print_status "Installing web server components..."
apt-get install -y \
    nginx \
    supervisor \
    redis-server

# Install additional Python packages via apt
print_status "Installing Python packages via apt..."
apt-get install -y \
    python3-numpy \
    python3-scipy \
    python3-pandas \
    python3-matplotlib \
    python3-opencv \
    python3-pil \
    python3-requests \
    python3-flask \
    python3-wtf \
    python3-sqlalchemy \
    python3-alembic \
    python3-marshmallow \
    python3-dateutil \
    python3-tz \
    python3-serial \
    python3-psutil \
    python3-configparser

# Upgrade pip and install Python dependencies
print_status "Installing Python packages via pip..."
python3 -m pip install --upgrade pip setuptools wheel

# Install core Python packages for the farm system
python3 -m pip install \
    mycodo \
    adafruit-circuitpython-ads1x15 \
    adafruit-circuitpython-bme280 \
    adafruit-circuitpython-dht \
    adafruit-circuitpython-mcp3xxx \
    w1thermsensor \
    pyserial \
    influxdb-client \
    redis \
    celery \
    apscheduler \
    paho-mqtt \
    pillow \
    opencv-python \
    imutils \
    rpicamera

# Install additional sensor and hardware libraries
python3 -m pip install \
    Adafruit-GPIO \
    Adafruit-PureIO \
    Adafruit-PlatformDetect \
    Adafruit-Blinka \
    RPi.GPIO \
    spidev \
    smbus2 \
    gpiozero \
    pigpio

# Install web framework and dashboard dependencies
python3 -m pip install \
    flask \
    flask-wtf \
    flask-login \
    flask-babel \
    flask-sqlalchemy \
    flask-migrate \
    flask-mail \
    flask-cors \
    wtforms \
    jinja2 \
    werkzeug \
    gunicorn \
    eventlet

# Install data processing and visualization libraries
python3 -m pip install \
    numpy \
    scipy \
    pandas \
    matplotlib \
    plotly \
    bokeh \
    seaborn

# Install image processing and computer vision
python3 -m pip install \
    opencv-python \
    opencv-contrib-python \
    scikit-image \
    imageio

# Install backup and file management utilities
apt-get install -y \
    rsync \
    zip \
    unzip \
    cron \
    logrotate

# Enable hardware interfaces (would normally need raspi-config on real Pi)
print_status "Configuring hardware interfaces..."

# Create config files for hardware interfaces
mkdir -p /boot/firmware/
cat > /boot/firmware/config.txt << 'EOF'
# Hardware interface configuration for Container Farm
dtparam=i2c_arm=on
dtparam=spi=on
dtparam=audio=on
enable_uart=1
dtoverlay=w1-gpio
dtoverlay=i2c-rtc,ds3231
gpu_mem=128

# Camera interface
start_x=1
EOF

# Enable I2C
if ! grep -q "i2c-dev" /etc/modules; then
    echo "i2c-dev" >> /etc/modules
fi
if ! grep -q "i2c-bcm2708" /etc/modules; then
    echo "i2c-bcm2708" >> /etc/modules
fi

# Enable 1-Wire
if ! grep -q "w1-gpio" /etc/modules; then
    echo "w1-gpio" >> /etc/modules
fi
if ! grep -q "w1-therm" /etc/modules; then
    echo "w1-therm" >> /etc/modules
fi

# Configure InfluxDB
print_status "Configuring InfluxDB..."
systemctl enable influxdb
systemctl start influxdb

# Wait for InfluxDB to start
sleep 5

# Create InfluxDB database for mycodo
influx -execute "CREATE DATABASE mycodo_db"
influx -execute "CREATE USER mycodo WITH PASSWORD 'mmdu77sj3nlqe928' WITH ALL PRIVILEGES"
influx -execute "GRANT ALL ON mycodo_db TO mycodo"

# Configure Redis
print_status "Configuring Redis..."
systemctl enable redis-server
systemctl start redis-server

# Configure Nginx
print_status "Configuring Nginx..."
systemctl enable nginx

# Create nginx configuration for the farm system
cat > /etc/nginx/sites-available/container-farm << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    location /static/ {
        alias /opt/Mycodo/mycodo/mycodo_flask/static/;
        expires 30d;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/container-farm /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Create directories for the farm system
print_status "Creating system directories..."
mkdir -p /opt/Mycodo
mkdir -p /var/log/mycodo
mkdir -p /var/mycodo-backups
mkdir -p /home/pi/container-farm/{config,dashboards,docs,logs,backups}

# Set up log rotation
cat > /etc/logrotate.d/mycodo << 'EOF'
/var/log/mycodo/*.log {
    weekly
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    copytruncate
}
EOF

# Install Mycodo (this would normally clone and install)
print_status "Preparing Mycodo installation directories..."
cd /opt/Mycodo
git clone --depth=1 https://github.com/kizniche/Mycodo.git . || print_warning "Mycodo clone may fail in container environment"

# Create systemd service files for the farm system
print_status "Creating systemd services..."

cat > /etc/systemd/system/mycodo.service << 'EOF'
[Unit]
Description=Mycodo
After=network.target influxdb.service redis.service

[Service]
Type=forking
User=root
ExecStart=/opt/Mycodo/mycodo/scripts/mycodo_wrapper.sh start
ExecStop=/opt/Mycodo/mycodo/scripts/mycodo_wrapper.sh stop
ExecReload=/opt/Mycodo/mycodo/scripts/mycodo_wrapper.sh restart
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

cat > /etc/systemd/system/container-farm.service << 'EOF'
[Unit]
Description=Container Farm Control System
After=network.target mycodo.service

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/container-farm
ExecStart=/usr/bin/python3 app.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/opt/Mycodo

[Install]
WantedBy=multi-user.target
EOF

# Create backup script
print_status "Creating backup system..."
cat > /usr/local/bin/farm-backup.sh << 'EOF'
#!/bin/bash
# Container Farm Backup Script

BACKUP_DIR="/var/mycodo-backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="farm_backup_${DATE}.tar.gz"

# Create backup
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    /opt/Mycodo/databases/ \
    /opt/Mycodo/mycodo/mycodo_flask/ssl_certs/ \
    /home/pi/container-farm/config/ \
    /var/log/mycodo/ \
    /etc/nginx/sites-available/container-farm

# Keep only last 10 backups
cd "${BACKUP_DIR}"
ls -t farm_backup_*.tar.gz | tail -n +11 | xargs -r rm

echo "Backup completed: ${BACKUP_FILE}"
EOF

chmod +x /usr/local/bin/farm-backup.sh

# Set up cron job for daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/farm-backup.sh") | crontab -

# Create default configuration files
print_status "Creating default configuration files..."

cat > /home/pi/container-farm/config/farm_config.py << 'EOF'
# Container Farm Configuration

# Database Configuration
INFLUXDB_HOST = 'localhost'
INFLUXDB_PORT = 8086
INFLUXDB_USER = 'mycodo'
INFLUXDB_PASSWORD = 'mmdu77sj3nldkje928'
INFLUXDB_DATABASE = 'mycodo_db'

# Hardware Configuration
I2C_BUS = 1
TEMP_SENSOR_PIN = 4
DHT_SENSOR_PIN = 17

# Default sensor addresses
BME280_ADDRESS = 0x76
ADS1115_ADDRESS = 0x48

# Relay GPIO pins
RELAY_PINS = {
    'light': 23,
    'fan': 24,
    'heater': 25,
    'pump': 18,
    'ph_up': 5,
    'ph_down': 6,
    'nutrient_a': 13,
    'nutrient_b': 19
}

# Alert thresholds
TEMP_MIN = 18.0
TEMP_MAX = 28.0
HUMIDITY_MIN = 40.0
HUMIDITY_MAX = 70.0
PH_MIN = 5.5
PH_MAX = 6.5
EOF

# Set permissions
chown -R pi:pi /home/pi/container-farm/
chmod -R 755 /home/pi/container-farm/

# Enable services
print_status "Enabling services..."
systemctl daemon-reload
systemctl enable influxdb
systemctl enable redis-server
systemctl enable nginx

# Create a simple test script to verify installation
cat > /home/pi/container-farm/test_sensors.py << 'EOF'
#!/usr/bin/env python3
"""
Simple sensor test script for Container Farm
"""

import sys
import time

def test_i2c():
    """Test I2C communication"""
    try:
        import smbus
        bus = smbus.SMBus(1)
        print("✓ I2C bus accessible")
        return True
    except Exception as e:
        print(f"✗ I2C test failed: {e}")
        return False

def test_gpio():
    """Test GPIO access"""
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        print("✓ GPIO accessible")
        GPIO.cleanup()
        return True
    except Exception as e:
        print(f"✗ GPIO test failed: {e}")
        return False

def test_1wire():
    """Test 1-Wire sensors"""
    try:
        import glob
        devices = glob.glob('/sys/bus/w1/devices/28*')
        if devices:
            print(f"✓ Found {len(devices)} 1-Wire temperature sensor(s)")
        else:
            print("○ No 1-Wire sensors detected (normal if not connected)")
        return True
    except Exception as e:
        print(f"✗ 1-Wire test failed: {e}")
        return False

def test_libraries():
    """Test required Python libraries"""
    libraries = [
        'numpy', 'pandas', 'flask', 'serial', 
        'influxdb_client', 'redis', 'PIL'
    ]
    
    success = True
    for lib in libraries:
        try:
            __import__(lib)
            print(f"✓ {lib} imported successfully")
        except ImportError as e:
            print(f"✗ {lib} import failed: {e}")
            success = False
    
    return success

if __name__ == "__main__":
    print("Container Farm System Test")
    print("=" * 30)
    
    tests = [
        ("I2C Communication", test_i2c),
        ("GPIO Access", test_gpio),
        ("1-Wire Sensors", test_1wire),
        ("Python Libraries", test_libraries)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        result = test_func()
        results.append(result)
    
    print("\n" + "=" * 30)
    print("Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! System ready.")
        sys.exit(0)
    else:
        print("⚠ Some tests failed. Check hardware connections.")
        sys.exit(1)
EOF

chmod +x /home/pi/container-farm/test_sensors.py

# Create a simple status checker
cat > /usr/local/bin/farm-status << 'EOF'
#!/bin/bash
# Container Farm Status Checker

echo "Container Farm Control System Status"
echo "===================================="

# Check services
services=("influxdb" "redis-server" "nginx")
for service in "${services[@]}"; do
    if systemctl is-active --quiet "$service"; then
        echo "✓ $service: Running"
    else
        echo "✗ $service: Stopped"
    fi
done

# Check database
if influx -execute "SHOW DATABASES" | grep -q "mycodo_db"; then
    echo "✓ InfluxDB: mycodo_db exists"
else
    echo "✗ InfluxDB: mycodo_db missing"
fi

# Check disk space
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 90 ]; then
    echo "✓ Disk space: ${disk_usage}% used"
else
    echo "⚠ Disk space: ${disk_usage}% used (WARNING)"
fi

# Check log files
if [ -d "/var/log/mycodo" ]; then
    log_count=$(find /var/log/mycodo -name "*.log" | wc -l)
    echo "✓ Log files: $log_count found"
else
    echo "⚠ Log directory not found"
fi

echo ""
echo "Last system backup:"
if [ -d "/var/mycodo-backups" ]; then
    latest_backup=$(ls -t /var/mycodo-backups/farm_backup_*.tar.gz 2>/dev/null | head -1)
    if [ -n "$latest_backup" ]; then
        echo "  $(basename "$latest_backup")"
        echo "  $(stat -c %y "$latest_backup" | cut -d. -f1)"
    else
        echo "  No backups found"
    fi
else
    echo "  Backup directory not found"
fi
EOF

chmod +x /usr/local/bin/farm-status

# Final setup steps
print_status "Final setup steps..."

# Add current user to relevant groups (for hardware access)
usermod -a -G i2c,spi,gpio,dialout pi 2>/dev/null || print_warning "User 'pi' may not exist yet"

# Create final installation marker
cat > /opt/container-farm-installed << 'EOF'
Container Farm Control System Installation Complete
Installation Date: $(date)
Version: 1.0.0

To get started:
1. Reboot the system: sudo reboot
2. Check system status: farm-status
3. Test sensors: cd /home/pi/container-farm && python3 test_sensors.py
4. Access web interface: http://your-pi-ip-address

For troubleshooting, check logs in /var/log/mycodo/
EOF

print_success "Setup completed successfully!"
print_status "Installation summary:"
echo "  ✓ System packages updated and installed"
echo "  ✓ Python environment configured with required libraries"
echo "  ✓ Hardware interfaces enabled (I2C, SPI, 1-Wire, UART)"
echo "  ✓ Database systems installed and configured (InfluxDB, Redis)"
echo "  ✓ Web server configured (Nginx)"
echo "  ✓ Backup system configured"
echo "  ✓ Test scripts created"
echo ""
print_status "Next steps:"
echo "  1. Reboot the system to enable hardware interfaces"
echo "  2. Run 'farm-status' to check system status"
echo "  3. Run 'python3 /home/pi/container-farm/test_sensors.py' to test hardware"
echo "  4. Connect your sensors according to the pinout in the config"
echo "  5. Access the web interface at http://localhost or your device IP"
echo ""
print_warning "Remember to configure your specific sensors and hardware in:"
echo "  /home/pi/container-farm/config/farm_config.py"

exit 0