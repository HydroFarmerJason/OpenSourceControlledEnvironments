---
layout: default
title: Installation Guide
---

# Installation Guide

This guide provides detailed instructions for setting up the Raspberry Pi and Mycodo system for container farm control.

## Automated Installation

For a complete automated setup, you can use our master setup script:

```bash
# Download the script
wget https://raw.githubusercontent.com/example-user/container-farm-control-system/main/scripts/master_setup.sh

# Make it executable
chmod +x master_setup.sh

# Run the script as root
sudo ./master_setup.sh
```

The script will guide you through the entire installation process, including system updates, enabling interfaces, Mycodo installation, sensor detection, and more.

## Manual Installation

If you prefer to install components manually, follow these steps:

### Operating System Setup

1. Download the 64-bit version of Raspberry Pi OS (recommended) from the official website:
```
https://www.raspberrypi.org/software/operating-systems/
```

2. Flash the OS to your microSD card (32GB+ recommended) using the Raspberry Pi Imager tool:
   - Select Raspberry Pi OS (64-bit) as the operating system
   - Select your microSD card as the storage
   - Click on the gear icon to configure:
     - Set hostname (e.g., `container-farm-control`)
     - Enable SSH
     - Configure WiFi (if not using Ethernet)
     - Set username and password

3. Update your system:
```bash
sudo apt update
sudo apt upgrade -y
```

4. Configure your system for optimal operation:
```bash
# Enable I2C interface (for many sensors)
sudo raspi-config nonint do_i2c 0

# Enable 1-Wire interface (for temperature sensors)
sudo raspi-config nonint do_onewire 0

# Enable UART (for serial devices)
sudo raspi-config nonint do_serial 0
```

### Mycodo Installation

1. Install required packages:
```bash
sudo apt install -y build-essential python3-dev python3-pip libatlas-base-dev
```

2. Run the Mycodo installation command:
```bash
curl -L https://kizniche.github.io/Mycodo/install | bash
```

3. After installation completes, access the Mycodo web interface at:
```
https://YOUR_PI_IP_ADDRESS/
```

4. Create an administrator account when prompted during first access.

### InfluxDB Database Setup

Mycodo installs InfluxDB automatically, but you may want to set up regular backups:

```bash
# Create backup directory
mkdir -p ~/backups

# Create backup script
cat << 'EOF' > ~/backup_influxdb.sh
#!/bin/bash
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR
influxd backup -portable $BACKUP_DIR/influxdb_backup_$TIMESTAMP
find $BACKUP_DIR -type d -name "influxdb_backup_*" -mtime +7 -exec rm -rf {} \;
EOF

# Make the script executable
chmod +x ~/backup_influxdb.sh

# Add weekly backup to crontab
(crontab -l 2>/dev/null; echo "0 2 * * 0 ~/backup_influxdb.sh") | crontab -
```

## Firewall Configuration

For better security, configure a firewall:

```bash
# Install UFW if not already installed
sudo apt install -y ufw

# Configure firewall rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable
```

## Next Steps

After completing this installation guide, proceed to the [Hardware Setup](hardware-setup.html) instructions to connect your sensors and relays to the Raspberry Pi.
