# Basic Temperature Monitoring Example

This is a complete, working example that you can build for under $100. Perfect for getting started or classroom demonstrations.

## What You'll Build

A simple system that:
- Monitors temperature with a DS18B20 sensor
- Controls a grow light based on temperature
- Logs data to a local database
- Provides a web interface to view current status

## Parts List ($75-100)

| Item | Quantity | Price | Supplier | Notes |
|------|----------|-------|----------|-------|
| Raspberry Pi 4B (2GB) | 1 | $35 | Official stores | 4GB recommended for classroom use |
| MicroSD Card (32GB) | 1 | $12 | Amazon/Best Buy | Class 10 or better |
| DS18B20 Temperature Sensor | 1 | $10 | Adafruit #381 | Waterproof version |
| 4.7kΩ Resistor | 1 | $0.25 | Any electronics store | For pullup |
| 2-Channel Relay Board | 1 | $8 | Amazon | 5V coil voltage |
| Breadboard Jumper Wires | 1 pack | $5 | Any electronics store | Male-to-female |
| LED Grow Light (12V) | 1 | $15-25 | Amazon | Or any 12V device |
| 12V Power Supply | 1 | $10 | Amazon | 2A minimum |

**Total: $85-105**

## Wiring Diagram

```
DS18B20 Temperature Sensor:
┌─────────────┐    ┌─────────────────┐
│ DS18B20     │    │ Raspberry Pi    │
│             │    │                 │
│ VDD (Red)   ├────┤ 3.3V (Pin 1)    │
│ DQ (Yellow) ├────┤ GPIO 4 (Pin 7)  │ (+ 4.7kΩ to 3.3V)
│ GND (Black) ├────┤ Ground (Pin 6)  │
└─────────────┘    └─────────────────┘

2-Channel Relay Board:
┌─────────────┐    ┌─────────────────┐
│ Relay Board │    │ Raspberry Pi    │
│             │    │                 │
│ VCC         ├────┤ 5V (Pin 2)      │
│ GND         ├────┤ Ground (Pin 9)  │
│ IN1         ├────┤ GPIO 23 (Pin 16)│
│ IN2         ├────┤ GPIO 24 (Pin 18)│
└─────────────┘    └─────────────────┘

Connect your 12V grow light to relay 1 (IN1)
```

## Code

### File: `examples/basic_monitoring/temperature_monitor.py`

```python
#!/usr/bin/env python3
"""
Basic Temperature Monitoring System
Monitors temperature and controls a grow light
"""

import time
import sqlite3
from datetime import datetime
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor

# Configuration
TEMP_TARGET = 22.0  # Target temperature in Celsius
TEMP_TOLERANCE = 2.0  # Temperature tolerance
LIGHT_GPIO = 23  # GPIO pin for grow light relay
DATABASE_PATH = 'temperature_data.db'

class TemperatureController:
    def __init__(self):
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LIGHT_GPIO, GPIO.OUT)
        GPIO.output(LIGHT_GPIO, GPIO.LOW)  # Start with light off
        
        # Setup temperature sensor
        try:
            self.sensor = W1ThermSensor()
            print(f"✓ Temperature sensor found: {self.sensor.id}")
        except:
            print("✗ No temperature sensor found!")
            print("Check wiring and ensure 1-Wire is enabled")
            exit(1)
        
        # Setup database
        self.setup_database()
        
        # State tracking
        self.light_on = False
        
    def setup_database(self):
        """Create database table if it doesn't exist"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS temperature_readings (
                timestamp DATETIME,
                temperature REAL,
                light_status INTEGER
            )
        ''')
        conn.commit()
        conn.close()
        print("✓ Database initialized")
    
    def read_temperature(self):
        """Read temperature from sensor"""
        try:
            temp = self.sensor.get_temperature()
            return temp
        except Exception as e:
            print(f"Error reading temperature: {e}")
            return None
    
    def control_light(self, temperature):
        """Control grow light based on temperature"""
        should_heat = temperature < (TEMP_TARGET - TEMP_TOLERANCE)
        
        if should_heat and not self.light_on:
            GPIO.output(LIGHT_GPIO, GPIO.HIGH)
            self.light_on = True
            print(f"🔥 Light ON - Temperature: {temperature:.1f}°C")
        elif not should_heat and self.light_on:
            GPIO.output(LIGHT_GPIO, GPIO.LOW)
            self.light_on = False
            print(f"❄️  Light OFF - Temperature: {temperature:.1f}°C")
    
    def log_data(self, temperature):
        """Log data to database"""
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO temperature_readings (timestamp, temperature, light_status)
            VALUES (?, ?, ?)
        ''', (datetime.now(), temperature, int(self.light_on)))
        conn.commit()
        conn.close()
    
    def run(self):
        """Main control loop"""
        print("🌱 Container Farm Temperature Controller Started")
        print(f"📊 Target: {TEMP_TARGET}°C ± {TEMP_TOLERANCE}°C")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Read temperature
                temperature = self.read_temperature()
                
                if temperature is not None:
                    # Control light based on temperature
                    self.control_light(temperature)
                    
                    # Log data
                    self.log_data(temperature)
                    
                    # Display status
                    status = "ON" if self.light_on else "OFF"
                    print(f"{datetime.now().strftime('%H:%M:%S')} - "
                          f"Temp: {temperature:.1f}°C, Light: {status}")
                
                # Wait 30 seconds before next reading
                time.sleep(30)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            GPIO.output(LIGHT_GPIO, GPIO.LOW)
            GPIO.cleanup()
            print("✓ Cleanup complete")

if __name__ == "__main__":
    controller = TemperatureController()
    controller.run()
```

### File: `examples/basic_monitoring/web_interface.py`

```python
#!/usr/bin/env python3
"""
Simple web interface for temperature monitoring
"""

from flask import Flask, render_template, jsonify
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
DATABASE_PATH = 'temperature_data.db'

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/current')
def current_status():
    """Get current temperature and light status"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT temperature, light_status, timestamp 
        FROM temperature_readings 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''')
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'temperature': result[0],
            'light_on': bool(result[1]),
            'timestamp': result[2]
        })
    else:
        return jsonify({'error': 'No data available'})

@app.route('/api/history')
def temperature_history():
    """Get last 24 hours of temperature data"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get data from last 24 hours
    yesterday = datetime.now() - timedelta(hours=24)
    cursor.execute('''
        SELECT timestamp, temperature, light_status 
        FROM temperature_readings 
        WHERE timestamp > ?
        ORDER BY timestamp
    ''', (yesterday,))
    
    results = cursor.fetchall()
    conn.close()
    
    data = []
    for row in results:
        data.append({
            'timestamp': row[0],
            'temperature': row[1],
            'light_status': row[2]
        })
    
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### File: `examples/basic_monitoring/templates/dashboard.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Container Farm - Basic Monitoring</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .status-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        .status-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .temperature {
            font-size: 2.5em;
            font-weight: bold;
            color: #2196F3;
        }
        .light-status {
            font-size: 1.5em;
            font-weight: bold;
        }
        .light-on { color: #4CAF50; }
        .light-off { color: #9E9E9E; }
        .timestamp {
            color: #666;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .error {
            color: #f44336;
            text-align: center;
            padding: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌱 Container Farm Monitor</h1>
            <p>Basic Temperature Monitoring System</p>
        </div>
        
        <div id="status" class="status-grid">
            <div class="status-card">
                <h3>Temperature</h3>
                <div id="temperature" class="temperature">--°C</div>
            </div>
            
            <div class="status-card">
                <h3>Grow Light</h3>
                <div id="light-status" class="light-status">--</div>
            </div>
        </div>
        
        <div id="timestamp" class="timestamp">Last updated: --</div>
        
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <script>
        function updateStatus() {
            fetch('/api/current')
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        document.getElementById('error').style.display = 'block';
                        document.getElementById('error').textContent = data.error;
                        document.getElementById('status').style.display = 'none';
                    } else {
                        document.getElementById('error').style.display = 'none';
                        document.getElementById('status').style.display = 'grid';
                        
                        // Update temperature
                        document.getElementById('temperature').textContent = 
                            data.temperature.toFixed(1) + '°C';
                        
                        // Update light status
                        const lightElement = document.getElementById('light-status');
                        if (data.light_on) {
                            lightElement.textContent = '🔥 ON';
                            lightElement.className = 'light-status light-on';
                        } else {
                            lightElement.textContent = '❄️ OFF';
                            lightElement.className = 'light-status light-off';
                        }
                        
                        // Update timestamp
                        document.getElementById('timestamp').textContent = 
                            'Last updated: ' + new Date(data.timestamp).toLocaleString();
                    }
                })
                .catch(error => {
                    document.getElementById('error').style.display = 'block';
                    document.getElementById('error').textContent = 
                        'Unable to connect to sensor system';
                    document.getElementById('status').style.display = 'none';
                });
        }

        // Update every 10 seconds
        updateStatus();
        setInterval(updateStatus, 10000);
    </script>
</body>
</html>
```

## Installation Instructions

### 1. Hardware Setup
1. **Connect DS18B20 sensor** according to wiring diagram
2. **Connect relay board** to GPIO pins
3. **Connect grow light** to relay output

### 2. Software Setup
```bash
# Enable 1-Wire interface
sudo raspi-config
# Go to Interface Options → 1-Wire → Enable

# Install Python dependencies
pip install w1thermsensor flask RPi.GPIO

# Create project directory
mkdir -p examples/basic_monitoring/templates
cd examples/basic_monitoring

# Copy the Python files and HTML template (from above)
# Make executable
chmod +x temperature_monitor.py web_interface.py
```

### 3. Testing
```bash
# Test temperature sensor
python3 -c "from w1thermsensor import W1ThermSensor; print(f'Temperature: {W1ThermSensor().get_temperature():.1f}°C')"

# Run the monitoring system
python3 temperature_monitor.py
```

### 4. Access Web Interface
```bash
# In another terminal, start web interface
python3 web_interface.py

# Open browser to: http://your-pi-ip:5000
```

## Expected Results

- **Temperature monitoring** every 30 seconds
- **Automatic light control** when temperature drops below target
- **Data logging** to local SQLite database
- **Web dashboard** showing current status
- **Console output** with real-time status

## Troubleshooting

### "No temperature sensor found"
1. Check wiring connections
2. Ensure 1-Wire is enabled: `sudo raspi-config`
3. Check if sensor detected: `ls /sys/bus/w1/devices/`

### "Relay not switching"
1. Verify GPIO connections
2. Check relay board power (needs 5V)
3. Test GPIO manually: `gpio -g write 23 1`

### "Web interface won't load"
1. Check if Flask is running: `ps aux | grep python`
2. Verify port 5000 is available: `netstat -ln | grep 5000`
3. Try accessing locally: `curl http://localhost:5000`

## Next Steps

Once this basic example works:
1. **Add humidity sensor** (DHT22)
2. **Add pH monitoring** (requires ADC)
3. **Add irrigation control** (water pumps)
4. **Implement scheduling** (day/night cycles)

This example provides a solid foundation that can be expanded into a complete growing system!
