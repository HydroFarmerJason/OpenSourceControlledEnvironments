# plugins/temperature-alert/plugin.py
"""
OSCE Temperature Alert Plugin
Sends notifications when temperature goes outside acceptable range
"""

from osce.plugin import OSCEPlugin, widget, api_endpoint
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta


class TemperatureAlertPlugin(OSCEPlugin):
    """Simple plugin demonstrating OSCE plugin architecture"""
    
    def __init__(self):
        super().__init__()
        self.name = "Temperature Alert"
        self.version = "1.0.0"
        self.author = "OSCE Community"
        self.description = "Get alerts when temperature is out of range"
        
        # Plugin settings (shown in admin panel)
        self.settings = {
            'min_temp': {
                'type': 'number',
                'default': 18,
                'label': 'Minimum Temperature (°C)',
                'description': 'Alert when temperature falls below this'
            },
            'max_temp': {
                'type': 'number', 
                'default': 28,
                'label': 'Maximum Temperature (°C)',
                'description': 'Alert when temperature rises above this'
            },
            'email': {
                'type': 'email',
                'label': 'Alert Email',
                'description': 'Where to send alerts'
            },
            'check_interval': {
                'type': 'select',
                'default': '5',
                'options': {'1': '1 minute', '5': '5 minutes', '15': '15 minutes'},
                'label': 'Check Interval'
            }
        }
        
        self.last_alert = {}
        
    def activate(self):
        """Called when plugin is activated"""
        # Register our check function to run on schedule
        interval = int(self.get_setting('check_interval'))
        self.schedule_task(self.check_temperature, minutes=interval)
        
        # Add our widget to the dashboard
        self.register_widget('temperature_alert_status')
        
        # Register API endpoint
        self.register_api('/api/plugins/temp-alert/status', self.get_status)
        
    def deactivate(self):
        """Called when plugin is deactivated"""
        self.unschedule_task(self.check_temperature)
        
    def check_temperature(self):
        """Main plugin logic - check temperature and send alerts"""
        min_temp = float(self.get_setting('min_temp'))
        max_temp = float(self.get_setting('max_temp'))
        email = self.get_setting('email')
        
        if not email:
            return
            
        # Get all temperature sensors
        temp_sensors = self.env.get_sensors(type='temperature')
        
        for sensor in temp_sensors:
            sensor_id = sensor['id']
            current_temp = sensor['value']
            
            # Check if we need to send alert
            alert_needed = False
            alert_type = None
            
            if current_temp < min_temp:
                alert_needed = True
                alert_type = 'low'
            elif current_temp > max_temp:
                alert_needed = True
                alert_type = 'high'
                
            if alert_needed:
                # Check if we already sent alert recently (avoid spam)
                last = self.last_alert.get(f"{sensor_id}_{alert_type}")
                if last and (datetime.now() - last) < timedelta(hours=1):
                    continue
                    
                # Send alert
                self.send_alert(sensor, current_temp, alert_type, email)
                self.last_alert[f"{sensor_id}_{alert_type}"] = datetime.now()
                
    def send_alert(self, sensor, temp, alert_type, email):
        """Send email alert"""
        subject = f"Temperature Alert: {sensor['name']}"
        
        if alert_type == 'low':
            message = f"Temperature is too low!\n\n"
            message += f"Sensor: {sensor['name']}\n"
            message += f"Current: {temp}°C\n"
            message += f"Minimum: {self.get_setting('min_temp')}°C\n"
        else:
            message = f"Temperature is too high!\n\n"
            message += f"Sensor: {sensor['name']}\n" 
            message += f"Current: {temp}°C\n"
            message += f"Maximum: {self.get_setting('max_temp')}°C\n"
            
        message += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # In real implementation, use proper email configuration
        self.log(f"Alert sent: {subject}")
        
        # Store alert in database
        self.store_data('alerts', {
            'sensor_id': sensor['id'],
            'type': alert_type,
            'temperature': temp,
            'timestamp': datetime.now()
        })
        
    @widget
    def temperature_alert_status(self):
        """Dashboard widget showing alert status"""
        recent_alerts = self.get_data('alerts', limit=5)
        
        return {
            'title': 'Temperature Alerts',
            'type': 'list',
            'content': [{
                'text': f"{alert['sensor_id']}: {alert['temperature']}°C ({alert['type']})",
                'time': alert['timestamp'],
                'icon': 'warning' if alert['type'] == 'high' else 'error'
            } for alert in recent_alerts],
            'footer': f"Monitoring {len(self.env.get_sensors(type='temperature'))} sensors"
        }
        
    @api_endpoint
    def get_status(self):
        """API endpoint for getting alert status"""
        return {
            'active': True,
            'settings': {
                'min_temp': self.get_setting('min_temp'),
                'max_temp': self.get_setting('max_temp'),
                'email': self.get_setting('email')
            },
            'recent_alerts': self.get_data('alerts', limit=10),
            'sensors_monitored': len(self.env.get_sensors(type='temperature'))
        }


# Plugin manifest (plugin.json)
plugin_manifest = {
    "id": "temperature-alert",
    "name": "Temperature Alert",
    "version": "1.0.0",
    "description": "Get email alerts when temperature goes out of range",
    "author": "OSCE Community",
    "homepage": "https://github.com/osce-plugins/temperature-alert",
    "requirements": {
        "osce": ">=1.0.0",
        "python": ">=3.7"
    },
    "tags": ["alerts", "notifications", "temperature", "email"],
    "screenshots": [
        "https://example.com/screenshot1.png",
        "https://example.com/screenshot2.png"
    ],
    "category": "Monitoring",
    "license": "MIT"
}


# === How to install this plugin ===
"""
1. From OSCE Dashboard:
   - Go to Plugins > Add New
   - Search "temperature alert"
   - Click "Install Now"
   - Activate and configure

2. From Command Line:
   osce install temperature-alert
   
3. From GitHub:
   cd /home/pi/osce/plugins
   git clone https://github.com/osce-plugins/temperature-alert
   osce activate temperature-alert
"""

# === Plugin Structure ===
"""
temperature-alert/
├── plugin.py          # Main plugin code
├── plugin.json        # Plugin manifest
├── readme.md          # Documentation
├── assets/           
│   ├── icon.png      # Plugin icon
│   └── banner.jpg    # Plugin banner
├── templates/        
│   └── widget.html   # Custom widget templates
├── static/
│   ├── style.css     # Plugin styles
│   └── script.js     # Plugin JavaScript
└── tests/
    └── test_plugin.py # Plugin tests
"""