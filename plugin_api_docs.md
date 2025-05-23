# OSCE Plugin API Documentation

## Creating Your First Plugin

OSCE plugins extend functionality without modifying core. This guide shows you how to build plugins that integrate seamlessly with the platform.

## Plugin Structure

```
my-awesome-plugin/
├── plugin.json         # Plugin manifest (required)
├── plugin.py          # Main plugin code (required)
├── requirements.txt   # Python dependencies
├── README.md         # Documentation
├── LICENSE           # License file
├── assets/          
│   ├── icon.png     # 64x64 icon
│   └── banner.jpg   # 1200x400 banner
├── templates/       
│   └── widget.html  # Custom dashboard widgets
├── static/
│   ├── style.css    # Plugin styles
│   └── script.js    # Plugin JavaScript
└── tests/
    └── test_plugin.py # Plugin tests
```

## Plugin Manifest (plugin.json)

```json
{
  "id": "my-awesome-plugin",
  "name": "My Awesome Plugin",
  "version": "1.0.0",
  "description": "Does awesome things for your grow",
  "author": {
    "name": "Your Name",
    "email": "you@example.com",
    "url": "https://yoursite.com"
  },
  "osce": {
    "minimum": "1.0.0",
    "maximum": "2.0.0"
  },
  "homepage": "https://github.com/yourusername/my-awesome-plugin",
  "license": "MIT",
  "keywords": ["sensors", "automation", "monitoring"],
  "category": "Automation",
  "screenshots": [
    "https://example.com/screenshot1.png",
    "https://example.com/screenshot2.png"
  ],
  "dependencies": {
    "python": ["requests>=2.25.0", "numpy>=1.19.0"],
    "plugins": ["osce-mqtt", "osce-database"]
  },
  "permissions": [
    "sensors:read",
    "actuators:write",
    "database:write",
    "network:external"
  ]
}
```

## Plugin Base Class

```python
from osce.plugin import Plugin, hook, api_endpoint, widget, scheduled_task

class MyAwesomePlugin(Plugin):
    """Your plugin must inherit from Plugin base class"""
    
    def __init__(self):
        super().__init__()
        # Plugin initialization
        
    def activate(self):
        """Called when plugin is activated"""
        self.log("Plugin activated!")
        
    def deactivate(self):
        """Called when plugin is deactivated"""
        self.log("Plugin deactivated!")
```

## Core Plugin Hooks

### Lifecycle Hooks

```python
@hook('osce.init')
def on_system_init(self):
    """Called when OSCE starts"""
    pass

@hook('osce.shutdown')
def on_system_shutdown(self):
    """Called when OSCE stops"""
    pass

@hook('plugin.install')
def on_install(self):
    """Called once when plugin is first installed"""
    # Create database tables, etc.
    pass

@hook('plugin.uninstall')
def on_uninstall(self):
    """Called when plugin is being removed"""
    # Cleanup data, etc.
    pass

@hook('plugin.update')
def on_update(self, old_version, new_version):
    """Called when plugin is updated"""
    # Migrate data, etc.
    pass
```

### Sensor Hooks

```python
@hook('sensor.reading')
def on_sensor_reading(self, sensor_id: str, value: float, unit: str):
    """Called whenever any sensor is read"""
    if sensor_id == 'temperature' and value > 30:
        self.send_alert("High temperature detected!")

@hook('sensor.added')
def on_sensor_added(self, sensor_info: dict):
    """Called when a new sensor is added"""
    self.log(f"New sensor: {sensor_info['name']}")

@hook('sensor.error')
def on_sensor_error(self, sensor_id: str, error: Exception):
    """Called when sensor reading fails"""
    self.log_error(f"Sensor {sensor_id} failed: {error}")
```

### Actuator Hooks

```python
@hook('actuator.state_changed')
def on_actuator_change(self, actuator_id: str, new_state: str, old_state: str):
    """Called when actuator state changes"""
    if actuator_id == 'pump' and new_state == 'on':
        self.schedule_task(self.stop_pump, minutes=5)

@hook('actuator.command')
def before_actuator_command(self, actuator_id: str, command: str) -> bool:
    """Called before actuator command executes. Return False to cancel."""
    if self.is_maintenance_mode():
        self.log("Actuator command blocked during maintenance")
        return False
    return True
```

### Data Hooks

```python
@hook('database.write')
def on_data_write(self, table: str, data: dict):
    """Called when data is written to database"""
    if table == 'sensor_readings':
        self.update_statistics(data)

@hook('database.query')
def on_data_query(self, query: str, results: list):
    """Called after database query"""
    # Can modify results before returning to caller
    return results
```

## Plugin APIs

### Accessing Environment

```python
class MyPlugin(Plugin):
    def get_current_state(self):
        # Access sensors
        temp = self.env.sensors.get('temperature').read()
        
        # Access actuators  
        self.env.actuators.get('pump').turn_on()
        
        # Access other plugins
        mqtt = self.env.plugins.get('osce-mqtt')
        if mqtt:
            mqtt.publish('greenhouse/temp', temp)
```

### Data Storage

```python
# Store plugin data
self.store_data('my_table', {
    'timestamp': datetime.now(),
    'value': 42,
    'notes': 'Sensor calibration'
})

# Query plugin data
recent_data = self.query_data(
    'my_table',
    where={'timestamp': {'$gt': datetime.now() - timedelta(hours=1)}},
    order_by='timestamp DESC',
    limit=10
)

# Key-value storage for settings
self.set_setting('alert_email', 'user@example.com')
email = self.get_setting('alert_email', default='admin@localhost')
```

### Dashboard Widgets

```python
@widget
def status_widget(self):
    """Define a dashboard widget"""
    return {
        'id': 'my_plugin_status',
        'title': 'My Plugin Status',
        'size': 'medium',  # small, medium, large, full
        'position': 'top',  # top, middle, bottom
        'refresh': 30,  # seconds
        'template': 'status.html',  # in templates/ folder
        'data': {
            'active': True,
            'last_run': self.last_run,
            'sensor_count': len(self.monitored_sensors)
        }
    }

@widget
def chart_widget(self):
    """Chart widget with live data"""
    return {
        'id': 'my_plugin_chart',
        'title': 'Sensor Trends',
        'type': 'chart',
        'chart_type': 'line',
        'data_source': '/api/plugins/my-plugin/chart-data',
        'refresh': 60
    }
```

### API Endpoints

```python
@api_endpoint('/api/plugins/my-plugin/status', methods=['GET'])
def get_status(self, request):
    """Expose plugin data via API"""
    return {
        'active': self.is_active,
        'version': self.version,
        'stats': self.get_statistics()
    }

@api_endpoint('/api/plugins/my-plugin/config', methods=['POST'])
@require_auth
def update_config(self, request):
    """Update plugin configuration"""
    data = request.json
    self.set_setting('threshold', data.get('threshold', 25))
    return {'success': True}
```

### Scheduled Tasks

```python
@scheduled_task(minutes=5)
def regular_check(self):
    """Run every 5 minutes"""
    self.check_sensor_health()

@scheduled_task(hours=1)
def hourly_report(self):
    """Run every hour"""
    self.generate_report()

@scheduled_task(cron='0 6 * * *')
def daily_maintenance(self):
    """Run daily at 6 AM using cron syntax"""
    self.run_maintenance()

# Dynamic scheduling
def some_method(self):
    # Schedule a one-time task
    self.schedule_task(self.delayed_action, seconds=30)
    
    # Schedule repeating task
    task_id = self.schedule_repeating_task(
        self.monitor_something,
        minutes=10,
        max_runs=6  # Stop after 1 hour
    )
    
    # Cancel task
    self.cancel_task(task_id)
```

### Events and Notifications

```python
# Emit custom events
self.emit_event('my_plugin.alert', {
    'level': 'warning',
    'message': 'Temperature approaching threshold',
    'value': 28.5
})

# Listen to custom events
@hook('another_plugin.data_ready')
def on_external_data(self, data):
    """React to events from other plugins"""
    self.process_external_data(data)

# Send notifications
self.send_notification(
    level='warning',  # info, warning, error, critical
    title='High Temperature Alert',
    message=f'Temperature is {temp}°C',
    actions=[
        {'label': 'View Dashboard', 'url': '/dashboard'},
        {'label': 'Disable Alert', 'callback': self.disable_alerts}
    ]
)
```

### Hardware Access

```python
# Access hardware through HAL
def read_custom_sensor(self):
    # Get hardware adapter
    hw = self.env.hardware.get_adapter('raspberry_pi')
    
    # Read from pins
    value = hw.analog_read(0)  # Read analog pin 0
    state = hw.digital_read(22)  # Read digital pin 22
    
    # Control outputs
    hw.digital_write(23, True)  # Set pin 23 HIGH
    hw.pwm_write(18, 0.75)  # 75% duty cycle on pin 18

# Register custom sensor type
self.register_sensor_type('my_sensor', {
    'name': 'My Custom Sensor',
    'pins': {'data': 'required', 'power': 'optional'},
    'protocols': ['i2c', 'spi'],
    'driver': MySensorDriver
})
```

### Internationalization

```python
# In plugin.py
from osce.i18n import translate as _

class MyPlugin(Plugin):
    def get_message(self):
        return _('my_plugin.greeting', name=self.user_name)

# In locales/en.json
{
    "my_plugin.greeting": "Hello, {name}!",
    "my_plugin.high_temp": "Temperature too high: {temp}°C"
}

# In locales/es.json
{
    "my_plugin.greeting": "¡Hola, {name}!",
    "my_plugin.high_temp": "Temperatura demasiado alta: {temp}°C"
}
```

## Plugin Best Practices

### 1. Namespace Everything
```python
# Good: Prefixed with plugin ID
self.store_data('my_plugin_readings', data)
self.set_setting('my_plugin.threshold', 25)

# Bad: Generic names
self.store_data('readings', data)  # Conflicts with other plugins!
```

### 2. Handle Errors Gracefully
```python
def read_sensor(self):
    try:
        return self.sensor.read()
    except Exception as e:
        self.log_error(f"Sensor read failed: {e}")
        # Return safe default or None
        return None
```

### 3. Respect User Settings
```python
def send_alert(self, message):
    if self.get_setting('alerts_enabled', True):
        # Check user notification preferences
        if self.env.user_prefers('email'):
            self.send_email(message)
        elif self.env.user_prefers('sms'):
            self.send_sms(message)
```

### 4. Provide Migration Path
```python
def on_update(self, old_version, new_version):
    if old_version < '2.0.0':
        # Migrate old data format
        old_data = self.query_data('old_table')
        for row in old_data:
            self.store_data('new_table', transform_data(row))
```

### 5. Clean Up Resources
```python
def deactivate(self):
    # Cancel all scheduled tasks
    self.cancel_all_tasks()
    
    # Close connections
    if self.mqtt_client:
        self.mqtt_client.disconnect()
    
    # Save state
    self.set_setting('last_state', self.current_state)
```

## Testing Your Plugin

```python
# tests/test_plugin.py
import pytest
from osce.testing import PluginTestCase

class TestMyPlugin(PluginTestCase):
    plugin_class = MyAwesomePlugin
    
    def test_activation(self):
        """Test plugin activates correctly"""
        self.activate_plugin()
        assert self.plugin.is_active
        
    def test_sensor_threshold(self):
        """Test threshold detection"""
        self.simulate_sensor_reading('temperature', 35)
        assert self.plugin.alerts_sent == 1
        
    def test_api_endpoint(self):
        """Test API endpoint"""
        response = self.client.get('/api/plugins/my-plugin/status')
        assert response.status_code == 200
        assert response.json['active'] == True
```

## Publishing Your Plugin

1. **Test Thoroughly**
   ```bash
   osce test-plugin .
   ```

2. **Package Plugin**
   ```bash
   osce package-plugin .
   ```

3. **Publish to Marketplace**
   ```bash
   osce publish-plugin my-awesome-plugin-1.0.0.zip
   ```

4. **Or Share on GitHub**
   - Users can install directly:
   ```bash
   osce install https://github.com/you/my-awesome-plugin
   ```

## Example: Complete Temperature Alert Plugin

```python
# plugin.py
from osce.plugin import Plugin, hook, widget, scheduled_task, api_endpoint
from datetime import datetime, timedelta

class TemperatureAlertPlugin(Plugin):
    """Monitors temperature and sends alerts"""
    
    def __init__(self):
        super().__init__()
        self.alert_sent = {}
        
    def activate(self):
        """Initialize plugin"""
        self.log("Temperature Alert Plugin activated")
        
        # Set default settings
        if not self.get_setting('threshold_high'):
            self.set_setting('threshold_high', 30)
            self.set_setting('threshold_low', 15)
            self.set_setting('alert_cooldown', 3600)  # 1 hour
            
    @hook('sensor.reading')
    def check_temperature(self, sensor_id: str, value: float, unit: str):
        """Check each temperature reading"""
        if 'temp' not in sensor_id.lower():
            return
            
        high = self.get_setting('threshold_high')
        low = self.get_setting('threshold_low')
        
        if value > high:
            self.send_temp_alert(sensor_id, value, 'high')
        elif value < low:
            self.send_temp_alert(sensor_id, value, 'low')
            
    def send_temp_alert(self, sensor_id: str, value: float, alert_type: str):
        """Send temperature alert with cooldown"""
        key = f"{sensor_id}_{alert_type}"
        cooldown = self.get_setting('alert_cooldown')
        
        # Check cooldown
        last_alert = self.alert_sent.get(key)
        if last_alert and (datetime.now() - last_alert).seconds < cooldown:
            return
            
        # Send alert
        self.send_notification(
            level='warning',
            title=f'Temperature {alert_type.title()} Alert',
            message=f'{sensor_id}: {value}°C',
            actions=[{
                'label': 'View Dashboard',
                'url': '/dashboard'
            }]
        )
        
        self.alert_sent[key] = datetime.now()
        
        # Log to database
        self.store_data('temperature_alerts', {
            'timestamp': datetime.now(),
            'sensor_id': sensor_id,
            'value': value,
            'alert_type': alert_type
        })
        
    @widget
    def alert_status_widget(self):
        """Dashboard widget showing recent alerts"""
        recent_alerts = self.query_data(
            'temperature_alerts',
            where={'timestamp': {'$gt': datetime.now() - timedelta(hours=24)}},
            order_by='timestamp DESC',
            limit=5
        )
        
        return {
            'id': 'temp_alerts',
            'title': 'Temperature Alerts (24h)',
            'size': 'medium',
            'data': {
                'alerts': recent_alerts,
                'thresholds': {
                    'high': self.get_setting('threshold_high'),
                    'low': self.get_setting('threshold_low')
                }
            }
        }
        
    @api_endpoint('/api/plugins/temp-alert/config', methods=['GET', 'POST'])
    def config_endpoint(self, request):
        """Get or update configuration"""
        if request.method == 'GET':
            return {
                'threshold_high': self.get_setting('threshold_high'),
                'threshold_low': self.get_setting('threshold_low'),
                'alert_cooldown': self.get_setting('alert_cooldown')
            }
        else:
            data = request.json
            self.set_setting('threshold_high', data.get('threshold_high', 30))
            self.set_setting('threshold_low', data.get('threshold_low', 15))
            self.set_setting('alert_cooldown', data.get('alert_cooldown', 3600))
            return {'success': True}
            
    @scheduled_task(hours=24)
    def cleanup_old_alerts(self):
        """Clean up alerts older than 30 days"""
        cutoff = datetime.now() - timedelta(days=30)
        self.delete_data('temperature_alerts', where={'timestamp': {'$lt': cutoff}})
        self.log("Cleaned up old temperature alerts")
```

## Plugin Development Tips

1. **Start Simple**: Begin with one feature, test it, then expand
2. **Use Hooks Wisely**: Don't hook into everything - it impacts performance
3. **Cache When Possible**: Don't recalculate on every request
4. **Document Everything**: Users need to understand your plugin
5. **Version Carefully**: Follow semantic versioning
6. **Test Edge Cases**: What if sensors fail? Network drops? 
7. **Respect Privacy**: Only collect necessary data
8. **Be a Good Citizen**: Don't hog resources or break other plugins

## Need Help?

- **Documentation**: https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/wiki
- **Examples**: https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/tree/main/plugins
- **Community**: https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments/discussions
- **Plugin Ideas**: Check the issues labeled "plugin-idea"

Remember: The best plugins solve real problems for real growers. Talk to users, understand their needs, and build something that makes their lives easier.

Happy plugin development! 🌱