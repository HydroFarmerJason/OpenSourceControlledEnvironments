#!/bin/bash
# OSCE Debug Script - Helps diagnose installation issues
# Usage: curl -sSL https://raw.githubusercontent.com/HydroFarmerJason/OpenSourceControlledEnvironments/main/debug.sh | bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== OSCE Debug Information ===${NC}"
echo "Generated: $(date)"
echo ""

# System Information
echo -e "${YELLOW}System Information:${NC}"
echo "Hostname: $(hostname)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "Kernel: $(uname -r)"
echo "Architecture: $(uname -m)"

# Hardware Detection
echo -e "\n${YELLOW}Hardware Platform:${NC}"
if [ -f /proc/device-tree/model ]; then
    echo "Device: $(cat /proc/device-tree/model)"
else
    echo "Device: Generic Linux"
fi

# Memory Info
echo -e "\n${YELLOW}Memory:${NC}"
free -h | grep -E "^Mem|^Swap"

# Disk Space
echo -e "\n${YELLOW}Disk Space:${NC}"
df -h | grep -E "^/dev/root|^/dev/mmcblk|^/dev/sda"

# Python Check
echo -e "\n${YELLOW}Python Environment:${NC}"
if command -v python3 &> /dev/null; then
    echo "Python Version: $(python3 --version)"
    echo "Pip Version: $(python3 -m pip --version 2>/dev/null || echo 'pip not installed')"
else
    echo -e "${RED}Python 3 not found!${NC}"
fi

# OSCE Installation Check
echo -e "\n${YELLOW}OSCE Installation:${NC}"
INSTALL_DIR="$HOME/osce"

if [ -d "$INSTALL_DIR" ]; then
    echo -e "${GREEN}${NC} OSCE directory found: $INSTALL_DIR"
    
    # Check core files
    for file in "core.py" "start.sh" "venv"; do
        if [ -e "$INSTALL_DIR/$file" ]; then
            echo -e "${GREEN}${NC} $file exists"
        else
            echo -e "${RED}${NC} $file missing"
        fi
    done
    
    # Check if running
    if pgrep -f "python.*core.py" > /dev/null; then
        echo -e "${GREEN}${NC} OSCE is running (PID: $(pgrep -f 'python.*core.py'))"
    else
        echo -e "${RED}${NC} OSCE is not running"
    fi
    
    # Check install info
    if [ -f "$INSTALL_DIR/install_info.json" ]; then
        echo -e "\nInstall Info:"
        cat "$INSTALL_DIR/install_info.json" | python3 -m json.tool 2>/dev/null || cat "$INSTALL_DIR/install_info.json"
    fi
else
    echo -e "${RED}${NC} OSCE not installed at $INSTALL_DIR"
fi

# Network Check
echo -e "\n${YELLOW}Network:${NC}"
# Get IP addresses
echo "IP Addresses:"
ip -4 addr show | grep inet | grep -v 127.0.0.1 | awk '{print "  " $2}'

# Check if port 8080 is in use
echo -e "\nPort 8080 Status:"
if netstat -tuln 2>/dev/null | grep -q ":8080"; then
    echo -e "${GREEN}${NC} Port 8080 is in use (good if OSCE is running)"
    netstat -tuln | grep ":8080"
else
    echo -e "${YELLOW}!${NC} Port 8080 is not in use"
fi

# GPIO/Hardware Checks (Pi only)
if [[ -d /sys/class/gpio ]]; then
    echo -e "\n${YELLOW}GPIO Status:${NC}"
    
    # Check GPIO access
    if groups | grep -q gpio; then
        echo -e "${GREEN}${NC} User is in gpio group"
    else
        echo -e "${YELLOW}!${NC} User not in gpio group (run: sudo usermod -a -G gpio $USER)"
    fi
    
    # Check I2C
    if [ -e /dev/i2c-1 ]; then
        echo -e "${GREEN}${NC} I2C enabled (/dev/i2c-1 exists)"
        if command -v i2cdetect &> /dev/null; then
            echo "I2C devices detected:"
            i2cdetect -y 1 2>/dev/null || echo "  (requires sudo to scan)"
        fi
    else
        echo -e "${YELLOW}!${NC} I2C not enabled (enable with: sudo raspi-config)"
    fi
    
    # Check 1-Wire
    if [ -d /sys/bus/w1/devices ]; then
        echo -e "${GREEN}${NC} 1-Wire enabled"
        ONE_WIRE_COUNT=$(ls /sys/bus/w1/devices/ | grep -c "28-" || echo 0)
        echo "  DS18B20 sensors found: $ONE_WIRE_COUNT"
    else
        echo -e "${YELLOW}!${NC} 1-Wire not enabled"
    fi
fi

# Log Check
echo -e "\n${YELLOW}Recent OSCE Logs:${NC}"
LOG_FILE="$INSTALL_DIR/logs/osce.log"
if [ -f "$LOG_FILE" ]; then
    echo "Last 20 lines of $LOG_FILE:"
    tail -20 "$LOG_FILE" | sed 's/^/  /'
else
    echo "No log file found at $LOG_FILE"
fi

# Connection Test
echo -e "\n${YELLOW}Connection Test:${NC}"
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo -e "${GREEN}${NC} OSCE API responding on localhost:8080"
    echo "API Response:"
    curl -s http://localhost:8080/health | python3 -m json.tool 2>/dev/null | sed 's/^/  /'
else
    echo -e "${RED}${NC} Cannot connect to OSCE on localhost:8080"
fi

# Troubleshooting Suggestions
echo -e "\n${YELLOW}Troubleshooting Suggestions:${NC}"

if ! command -v python3 &> /dev/null; then
    echo "- Install Python 3: sudo apt-get install python3 python3-pip python3-venv"
fi

if [ ! -d "$INSTALL_DIR" ]; then
    echo "- OSCE not installed. Run the installer:"
    echo "  curl -sSL https://raw.githubusercontent.com/HydroFarmerJason/OpenSourceControlledEnvironments/main/install.sh | bash"
fi

if [ -d "$INSTALL_DIR" ] && ! pgrep -f "python.*core.py" > /dev/null; then
    echo "- OSCE not running. Start it with:"
    echo "  cd $INSTALL_DIR && ./start.sh"
fi

if ! netstat -tuln 2>/dev/null | grep -q ":8080"; then
    echo "- Port 8080 not active. Check if another process is using it or OSCE failed to start"
fi

# Generate Support Bundle
echo -e "\n${YELLOW}Creating Support Bundle:${NC}"
BUNDLE_DIR="/tmp/osce-debug-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BUNDLE_DIR"

# Collect info
{
    echo "=== OSCE Debug Report ==="
    echo "Date: $(date)"
    echo ""
    echo "=== System ==="
    uname -a
    cat /etc/os-release
    echo ""
    echo "=== Hardware ==="
    [ -f /proc/device-tree/model ] && cat /proc/device-tree/model
    echo ""
    echo "=== Memory ==="
    free -h
    echo ""
    echo "=== Disk ==="
    df -h
    echo ""
    echo "=== Python ==="
    python3 --version 2>&1
    python3 -m pip list 2>&1 | head -20
    echo ""
    echo "=== OSCE Status ==="
    [ -f "$INSTALL_DIR/install_info.json" ] && cat "$INSTALL_DIR/install_info.json"
    echo ""
    echo "=== Processes ==="
    ps aux | grep -E "python|osce" | grep -v grep
    echo ""
    echo "=== Network ==="
    ip addr
    netstat -tuln | grep 8080
    echo ""
    echo "=== Recent Logs ==="
    [ -f "$LOG_FILE" ] && tail -50 "$LOG_FILE"
} > "$BUNDLE_DIR/debug-report.txt"

# Create tarball
tar -czf "$BUNDLE_DIR.tar.gz" -C /tmp "$(basename "$BUNDLE_DIR")"
rm -rf "$BUNDLE_DIR"

echo -e "${GREEN}${NC} Support bundle created: ${BLUE}$BUNDLE_DIR.tar.gz${NC}"
echo ""
echo "If you need help:"
echo "1. Share the output above in a GitHub issue"
echo "2. Or attach the support bundle: $BUNDLE_DIR.tar.gz"
echo ""
echo "Get help at: https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/issues"