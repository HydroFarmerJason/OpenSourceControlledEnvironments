#!/bin/bash
# Container Farm Control System - Micro Monitoring Setup
# Simplified installer for temperature and humidity monitoring only.

set -e

CONFIG_FILE="basic_monitoring.json"
INSTALL_DIR="/opt/container-farm-control"

if [[ $EUID -ne 0 ]]; then
  echo "Please run as root (sudo)." >&2
  exit 1
fi

# Create install directory
mkdir -p "$INSTALL_DIR"
cp "$CONFIG_FILE" "$INSTALL_DIR/"

echo "Installing required packages..."
apt-get update
apt-get install -y git python3 python3-pip

# Install Mycodo (minimal)
if ! command -v mycodo-client >/dev/null; then
  curl -L https://kizniche.github.io/mycodo-installer/install | bash
fi

# Import configuration
if [ -f /var/mycodo/databases/mycodo.db ]; then
  echo "Importing basic monitoring configuration..."
  mycodo-client --import "$INSTALL_DIR/$CONFIG_FILE"
  systemctl restart mycododaemon
fi

echo "Micro monitoring setup complete. Access the dashboard at http://<pi-ip>:8080"

