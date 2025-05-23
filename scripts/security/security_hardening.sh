#!/bin/bash
# security_hardening.sh

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable

# SSL/TLS Configuration
sudo certbot --nginx -d your-farm.local

# Fail2ban configuration
sudo apt-get install fail2ban
sudo cp config/fail2ban/jail.local /etc/fail2ban/

# Network isolation for IoT devices
sudo ip link add name iot0 type bridge
sudo ip addr add 192.168.100.1/24 dev iot0
