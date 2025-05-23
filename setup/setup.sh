#!/bin/bash

set -e  # Exit immediately on error

echo "==== Consentnet/OpenSourceControlledEnvironments SETUP SCRIPT ===="

# Update system
echo "Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install general dependencies
echo "Installing core utilities..."
sudo apt-get install -y python3 python3-pip python3-venv git curl wget build-essential

# Install numpy (and any other Python dependencies)
echo "Installing Python dependencies via pip..."
pip3 install --upgrade pip
pip3 install numpy

# ==================== ROS 2 Installation ====================
# Default to ROS 2 Foxy for Raspberry Pi OS (Debian-based)
echo "Installing ROS 2 (Foxy)..."

# Add ROS 2 apt repository and keys
sudo apt-get install -y locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8

sudo apt-get install -y software-properties-common
sudo add-apt-repository universe
sudo apt-get update

sudo apt-get install -y curl gnupg2 lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key | sudo apt-key add -

# For Raspberry Pi OS, add correct ROS 2 repo (adjust for Ubuntu if needed)
sudo sh -c 'echo "deb [arch=armhf,arm64,amd64 signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2-latest.list'

sudo apt-get update

# Install ROS 2 core packages
sudo apt-get install -y ros-foxy-desktop python3-argcomplete

# Source ROS 2 setup in bashrc (so Python scripts find rclpy, etc.)
echo "source /opt/ros/foxy/setup.bash" >> ~/.bashrc
source /opt/ros/foxy/setup.bash

# Install additional ROS 2 packages for common messages
sudo apt-get install -y ros-foxy-std-msgs ros-foxy-geometry-msgs ros-foxy-sensor-msgs

# ==================== Project-specific setup ====================
# Clone PulseMesh or any custom modules if required (uncomment if repo is elsewhere)
# git clone https://github.com/YourOrg/PulseMesh.git

echo "Setup complete! Please restart your terminal or source ~/.bashrc for ROS 2 access."
