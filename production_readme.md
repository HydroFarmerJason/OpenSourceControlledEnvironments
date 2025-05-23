# OpenSource Controlled Environments - Production Deployment Guide

## 🚀 Quick Start Production Deployment

This guide covers deploying the production-ready components for OpenSourceControlledEnvironments.

### Prerequisites

- Raspberry Pi 4 (4GB+ RAM recommended) or compatible Linux system
- Python 3.9+
- Docker & Docker Compose (for containerized deployment)
- 16GB+ SD card or storage
- Internet connection for initial setup

## 📦 What's Included

### Security & Authentication
- **JWT-based authentication** with refresh tokens
- **API key management** for automated systems
- **Role-based access control** (RBAC)
- **Rate limiting** to prevent abuse
- **Security headers** and HTTPS support
- **Password policy enforcement**

### Error Handling & Monitoring
- **Centralized error handling** with recovery strategies
- **Structured logging** with rotation
- **Health monitoring** endpoints
- **Prometheus metrics** integration
- **Grafana dashboards** for visualization

### Backup & Recovery
- **Automated daily/weekly/monthly backups**
- **Remote backup support** (SSH/rsync)
- **Point-in-time recovery**
- **Backup verification** and integrity checks
- **Disaster recovery procedures**

### Deployment Options
- **Docker containerization** with multi-architecture support
- **Docker Compose** orchestration
- **Kubernetes-ready** configurations
- **Automated dependency management**
- **CI/CD pipeline** integration

## 🛠️ Installation

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git
cd OpenSourceControlledEnvironments

# Copy environment template
cp .env.example .env

# Edit configuration
nano .env  # Update with your settings

# Deploy with Docker
./scripts/docker-deploy.sh deploy

# Access the application
# API: http://localhost:5000
# Grafana: http://localhost:3000 (admin/admin)
```

### Option 2: Manual Installation

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip python3-venv \
    build-essential libssl-dev libffi-dev redis-server \
    python3-smbus i2c-tools

# Run automated installer
python3 install_dependencies.py

# Activate virtual environment
source venv/bin/activate

# Initialize database
alembic upgrade head

# Create admin user
python -m farm.cli create-admin

# Start the application
python run.py
```

## 🔐 Security Configuration

### Initial Setup

1. **Generate secure keys**:
```bash
# Generate secret keys
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

2. **Update .env file** with generated keys

3. **Create admin user**:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecurePassword123!",
    "role": "admin"
  }'
```

### API Authentication

**JWT Token**:
```bash
# Login to get token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "SecurePassword123!"}'

# Use token in requests
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:5000/api/v1/sensors
```

**API Key**:
```bash
# Generate API key
curl -X POST http://localhost:5000/api/auth/api-key \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Automation System"}'

# Use API key
curl -H "X-API-Key: osce_YOUR_API_KEY" \
  http://localhost:5000/api/v1/sensors
```

## 🔧 Configuration

### Hardware Configuration

Edit `config/hardware.yml`:
```yaml
sensors:
  temperature:
    - id: temp_1
      type: DS18B20
      pin: 4
      name: "Air Temperature"
  
  humidity:
    - id: humid_1
      type: DHT22
      pin: 17
      name: "Air Humidity"

actuators:
  lights:
    - id: light_1
      type: relay
      pin: 22
      name: "Grow Light"
  
  pumps:
    - id: pump_1
      type: relay
      pin: 27
      name: "Water Pump"
```

### Automation Rules

Create automation rules via API:
```json
{
  "name": "Temperature Control",
  "enabled": true,
  "conditions": [
    {
      "sensor": "temp_1",
      "operator": ">",
      "value": 28
    }
  ],
  "actions": [
    {
      "actuator": "fan_1",
      "action": "on"
    }
  ]
}
```

## 📊 Monitoring

### Prometheus Metrics

Available at: `http://localhost:9090/metrics`

Key metrics:
- `farm_sensor_reading{sensor_id, type}` - Sensor values
- `farm_actuator_state{actuator_id, type}` - Actuator states
- `farm_api_requests_total{method, endpoint, status}` - API requests
- `farm_errors_total{category, severity}` - System errors

### Grafana Dashboards

1. Access Grafana: `http://localhost:3000`
2. Default credentials: `admin/admin`
3. Pre-configured dashboards:
   - System Overview
   - Sensor Readings
   - Environmental Conditions
   - API Performance

## 🔄 Backup & Recovery

### Automated Backups

Configure in crontab:
```bash
# Edit crontab
crontab -e

# Add backup schedules
0 2 * * * /home/pi/OpenSourceControlledEnvironments/backup_system.sh daily
0 3 * * 0 /home/pi/OpenSourceControlledEnvironments/backup_system.sh weekly
0 4 1 * * /home/pi/OpenSourceControlledEnvironments/backup_system.sh monthly
```

### Manual Backup

```bash
# Create backup
./backup_system.sh daily

# List backups
./backup_system.sh list

# Restore from backup
./backup_system.sh restore /path/to/backup.tar.gz
```

### Remote Backup Setup

Edit `.env`:
```bash
REMOTE_BACKUP_HOST=backup.example.com
REMOTE_BACKUP_USER=farmbackup
REMOTE_BACKUP_DIR=/backups/farm
```

Setup SSH key:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/farm_backup
ssh-copy-id -i ~/.ssh/farm_backup farmbackup@backup.example.com
```

## 🐛 Troubleshooting

### Check System Health

```bash
# Using CLI
python -m farm.cli check_health

# Using API
curl http://localhost:5000/health

# Check logs
tail -f logs/farm_system.log
```

### Common Issues

**Sensor Not Responding**:
```bash
# Check I2C devices
sudo i2cdetect -y 1

# Restart sensor service
docker-compose restart farm-worker
```

**Database Connection Error**:
```bash
# Check PostgreSQL
docker-compose ps postgres
docker-compose logs postgres

# Rebuild database
docker-compose down -v
docker-compose up -d
```

**Permission Errors**:
```bash
# Fix GPIO permissions
sudo usermod -a -G gpio,i2c $USER
# Logout and login again
```

## 🚀 Production Best Practices

### 1. **Security**
- Change all default passwords
- Enable HTTPS with Let's Encrypt
- Regularly update dependencies
- Monitor security logs

### 2. **Performance**
- Enable Redis caching
- Use PostgreSQL for production
- Configure proper worker counts
- Monitor resource usage

### 3. **Reliability**
- Set up monitoring alerts
- Configure automatic restarts
- Test backup restoration
- Document procedures

### 4. **Maintenance**
- Schedule regular updates
- Monitor disk space
- Rotate logs properly
- Clean old backups

## 📚 API Documentation

### Interactive Documentation
Access Swagger UI at: `http://localhost:5000/api/v1/docs`

### Key Endpoints

**Sensors**:
- `GET /api/v1/sensors` - List all sensors
- `GET /api/v1/sensors/{id}` - Get sensor reading
- `GET /api/v1/sensors/{id}/history` - Get historical data

**Actuators**:
- `GET /api/v1/actuators` - List all actuators
- `POST /api/v1/actuators/{id}` - Control actuator

**Automation**:
- `GET /api/v1/automation/rules` - List rules
- `POST /api/v1/automation/rules` - Create rule

**System**:
- `GET /api/v1/system/status` - System status
- `GET /api/v1/system/logs` - System logs
- `POST /api/v1/system/backup` - Trigger backup

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🆘 Support

- Documentation: [https://hydrofarmerjason.github.io/OpenSourceControlledEnvironments](https://hydrofarmerjason.github.io/OpenSourceControlledEnvironments)
- Issues: [GitHub Issues](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/issues)
- Discussions: [GitHub Discussions](https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/discussions)

---

**Remember**: This is a living system. Regular maintenance, monitoring, and updates are essential for optimal performance and security.