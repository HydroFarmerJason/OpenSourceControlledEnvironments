# Educational Classroom Setup

A complete growing system designed specifically for K-12 education, emphasizing safety, learning outcomes, and curriculum integration.

## Learning Objectives

Students will:
- **Science**: Understand plant biology, photosynthesis, and environmental factors
- **Math**: Collect and analyze data, create graphs, calculate growth rates
- **Technology**: Use sensors, programming concepts, and data visualization
- **Engineering**: Problem-solve system issues and optimize growing conditions

## What You'll Build

A classroom-safe system that:
- Monitors temperature, humidity, and light levels
- Controls LED grow lights on a timer
- Waters plants automatically
- Logs data for student analysis
- Provides student-friendly web interface
- Includes safety lockouts and teacher overrides

## Parts List ($180-250)

| Item | Quantity | Price | Supplier | Educational Notes |
|------|----------|-------|----------|------------------|
| Raspberry Pi 4B (4GB) | 1 | $55 | Official distributors | 4GB for multiple student access |
| MicroSD Card (64GB) | 1 | $15 | Educational suppliers | Larger storage for student data |
| Educational Enclosure | 1 | $25 | Custom/3D printed | Clear cover for visibility |
| BME280 Environmental Sensor | 1 | $20 | Adafruit #2652 | All-in-one sensor |
| DS18B20 Temperature Sensors | 3 | $30 | Adafruit #381 | Multiple zones for comparison |
| Light Sensor (TSL2591) | 1 | $15 | Adafruit #1980 | Measure light intensity |
| 4-Channel Relay Board | 1 | $12 | Amazon | Educational safe (12V max) |
| LED Grow Light Strips (12V) | 2 | $30 | Amazon | Student-safe voltage |
| Water Pump (12V) | 1 | $15 | Amazon | Small, quiet pump |
| Water Level Sensor | 1 | $10 | Amazon | Float switch type |
| Breadboard & Jumper Wires | 1 set | $15 | Educational suppliers | For student experiments |
| Power Supply (12V/5V) | 1 | $25 | Amazon | Dual output, enclosed |
| Safety Emergency Stop | 1 | $8 | Amazon | Large red button |

**Total: $200-275**

## Safety Features

### Electrical Safety
- **Low voltage only** (12V maximum for student-accessible components)
- **GFCI protection** required for all AC power
- **Emergency stop button** easily accessible
- **Enclosed power supplies** - no exposed high voltage
- **Strain relief** on all cables

### Student Safety
- **Locked teacher controls** for system settings
- **Read-only student access** to most functions
- **Water safety**: Overflow protection and GFCI
- **Chemical restrictions**: pH solutions only with teacher supervision

## Wiring Diagram

```
Educational Classroom Setup Wiring:

┌─────────────────────────────────────────────────────────────┐
│                    TEACHER CONTROL SECTION                  │
│  ┌──────────────┐    ┌─────────────────────────────────┐   │
│  │ Raspberry Pi │    │         Power Supply            │   │
│  │   (Locked)   │    │  120V AC → 5V DC & 12V DC      │   │
│  │              │    │        (Enclosed)               │   │
│  └──────────────┘    └─────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   STUDENT OBSERVATION AREA                  │
│                                                             │
│  Environmental Sensors (Student Accessible):               │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────┐    │
│  │  BME280    │  │ Light Sensor │  │ Temperature     │    │
│  │Temp/Humid  │  │   (TSL2591)  │  │ Probes (3x)     │    │
│  │   (I2C)    │  │    (I2C)     │  │   (1-Wire)      │    │
│  └────────────┘  └──────────────┘  └─────────────────┘    │
│                                                             │
│  Growing Area:                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ LED Grow Lights (12V) - Timer Controlled           │   │
│  │ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │   │
│  │ │Plant│ │Plant│ │Plant│ │Plant│ │Plant│ │Plant│   │   │
│  │ │  1  │ │  2  │ │  3  │ │  4  │ │  5  │ │  6  │   │   │
│  │ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘   │   │
│  │                                                     │   │
│  │ Water Reservoir with Level Sensor & Pump           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────┐                                       │
│  │ EMERGENCY STOP  │ ← Large, accessible to all students   │
│  │   (Red Button)  │                                       │
│  └─────────────────┘                                       │
└─────────────────────────────────────────────────────────────┘

Connection Details:
BME280:     VIN→3.3V, GND→GND, SCL→GPIO3, SDA→GPIO2
TSL2591:    VIN→3.3V, GND→GND, SCL→GPIO3, SDA→GPIO2  
DS18B20s:   VDD→3.3V, GND→GND, DQ→GPIO4 (all 3 sensors on same bus)
Relays:     VCC→5V, GND→GND, IN1→GPIO5, IN2→GPIO6, IN3→GPIO13, IN4→GPIO19
E-Stop:     NC→GPIO21 (normally closed, opens on press)
```

## Code

### File: `examples/classroom_setup/educational_controller.py`

```python
#!/usr/bin/env python3
"""
Educational Classroom Growing System Controller
Designed for K-12 education with safety and learning focus
"""

import time
import json
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict
import RPi.GPIO as GPIO
from w1thermsensor import W1ThermSensor
try:
    import board
    import busio
    import adafruit_bme280
    import adafruit_tsl2591
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False
    print(" I2C libraries not available - running in simulation mode")

@dataclass
class SensorReading:
    timestamp: datetime
    sensor_type: str
    value: float
    unit: str
    location: str = "main"

class EducationalGrowController:
    def __init__(self):
        self.config = self.load_config()
        self.setup_gpio()
        self.setup_sensors()
        self.setup_database()
        
        # Safety state
        self.emergency_stop_active = False
        self.teacher_override = False
        
        # System state
        self.lights_on = False
        self.pump_running = False
        self.last_watering = None
        
        print(" Educational Growing System Initialized")
        print(" Safety systems active")
        
    def load_config(self):
        """Load educational configuration"""
        return {
            "safety": {
                "max_voltage": 12,
                "emergency_stop_gpio": 21,
                "teacher_override_gpio": 20,
                "max_pump_runtime": 30,  # seconds
                "min_pump_interval": 300  # 5 minutes between waterings
            },
            "schedule": {
                "lights_on": "08:00",
                "lights_off": "16:00",  # School hours
                "watering_times": ["09:00", "13:00"],
                "data_collection_interval": 300  # 5 minutes for education
            },
            "thresholds": {
                "temperature": {"min": 18, "max": 26, "target": 22},
                "humidity": {"min": 40, "max": 80, "target": 60},
                "soil_moisture": {"water_threshold": 30}  # Percent
            },
            "student_access": {
                "can_view_data": True,
                "can_control_lights": False,
                "can_control_pump": False,
                "can_emergency_stop": True
            }
        }
    
    def setup_gpio(self):
        """Setup GPIO pins with safety considerations"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Safety inputs (with pull-up resistors)
        GPIO.setup(self.config["safety"]["emergency_stop_gpio"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.config["safety"]["teacher_override_gpio"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Control outputs (start in safe state - OFF)
        self.relay_pins = {
            "lights": 5,
            "pump": 6,
            "fan": 13,
            "spare": 19
        }
        
        for name, pin in self.relay_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Safe state - OFF
        
        print(" GPIO configured for educational safety")
    
    def setup_sensors(self):
        """Initialize sensors with error handling"""
        self.sensors = {}
        
        # Temperature sensors (1-Wire)
        try:
            self.temperature_sensors = W1ThermSensor.get_available_sensors()
            if self.temperature_sensors:
                print(f" Found {len(self.temperature_sensors)} temperature sensors")
                # Label sensors by location
                locations = ["ambient", "canopy", "root_zone"]
                for i, sensor in enumerate(self.temperature_sensors):
                    location = locations[i] if i < len(locations) else f"sensor_{i+1}"
                    self.sensors[f"temp_{location}"] = sensor
            else:
                print(" No temperature sensors found")
        except Exception as e:
            print(f" Temperature sensor setup failed: {e}")
        
        # I2C sensors
        if I2C_AVAILABLE:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                
                # Environmental sensor (BME280)
                try:
                    self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
                    self.bme280.sea_level_pressure = 1013.25
                    self.sensors["environment"] = self.bme280
                    print(" BME280 environmental sensor ready")
                except Exception as e:
                    print(f" BME280 setup failed: {e}")
                
                # Light sensor (TSL2591)
                try:
                    self.light_sensor = adafruit_tsl2591.TSL2591(i2c)
                    self.sensors["light"] = self.light_sensor
                    print(" TSL2591 light sensor ready")
                except Exception as e:
                    print(f" TSL2591 setup failed: {e}")
                    
            except Exception as e:
                print(f" I2C setup failed: {e}")
        
    def setup_database(self):
        """Create educational database with student-friendly structure"""
        self.db_path = "classroom_data.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Main sensor data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                experiment_day INTEGER,
                sensor_type TEXT,
                sensor_location TEXT,
                value REAL,
                unit TEXT,
                student_notes TEXT
            )
        ''')
        
        # Plant growth tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plant_observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                experiment_day INTEGER,
                plant_id INTEGER,
                height_cm REAL,
                leaf_count INTEGER,
                health_score INTEGER,
                student_observer TEXT,
                notes TEXT,
                photo_filename TEXT
            )
        ''')
        
        # System events for learning
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                event_type TEXT,
                description TEXT,
                triggered_by TEXT,
                student_visible BOOLEAN
            )
        ''')
        
        # Experiments and lessons
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date DATE,
                experiment_name TEXT,
                hypothesis TEXT,
                variables TEXT,
                expected_outcome TEXT,
                class_section TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(" Educational database initialized")
    
    def check_safety_systems(self):
        """Check emergency stop and safety systems"""
        # Check emergency stop button
        if GPIO.input(self.config["safety"]["emergency_stop_gpio"]) == GPIO.LOW:
            if not self.emergency_stop_active:
                self.emergency_stop_active = True
                self.safe_shutdown()
                self.log_event("emergency_stop", "Emergency stop activated", "physical_button")
                print(" EMERGENCY STOP ACTIVATED")
            return False
        else:
            if self.emergency_stop_active:
                self.emergency_stop_active = False
                self.log_event("emergency_stop_reset", "Emergency stop reset", "physical_button")
                print(" Emergency stop reset")
        
        # Check teacher override
        self.teacher_override = GPIO.input(self.config["safety"]["teacher_override_gpio"]) == GPIO.LOW
        
        return not self.emergency_stop_active
    
    def safe_shutdown(self):
        """Safely shut down all systems"""
        for pin in self.relay_pins.values():
            GPIO.output(pin, GPIO.LOW)
        
        self.lights_on = False
        self.pump_running = False
        print(" All systems safely shut down")
    
    def read_sensors(self) -> List[SensorReading]:
        """Read all sensors and return educational data"""
        readings = []
        current_time = datetime.now()
        
        # Temperature sensors
        for name, sensor in self.sensors.items():
            if name.startswith("temp_"):
                try:
                    temp = sensor.get_temperature()
                    location = name.replace("temp_", "")
                    readings.append(SensorReading(
                        timestamp=current_time,
                        sensor_type="temperature",
                        value=round(temp, 1),
                        unit="°C",
                        location=location
                    ))
                except Exception as e:
                    print(f" Error reading {name}: {e}")
        
        # Environmental sensor (BME280)
        if "environment" in self.sensors:
            try:
                bme = self.sensors["environment"]
                readings.extend([
                    SensorReading(current_time, "temperature", round(bme.temperature, 1), "°C", "environment"),
                    SensorReading(current_time, "humidity", round(bme.relative_humidity, 1), "%", "environment"),
                    SensorReading(current_time, "pressure", round(bme.pressure, 1), "hPa", "environment")
                ])
            except Exception as e:
                print(f" Error reading BME280: {e}")
        
        # Light sensor
        if "light" in self.sensors:
            try:
                light = self.sensors["light"]
                lux = light.lux
                if lux is not None:
                    readings.append(SensorReading(
                        timestamp=current_time,
                        sensor_type="light",
                        value=round(lux, 1),
                        unit="lux",
                        location="canopy"
                    ))
            except Exception as e:
                print(f" Error reading light sensor: {e}")
        
        return readings
    
    def control_lights(self, turn_on: bool):
        """Control grow lights with safety checks"""
        if not self.check_safety_systems():
            return False
        
        if turn_on != self.lights_on:
            GPIO.output(self.relay_pins["lights"], GPIO.HIGH if turn_on else GPIO.LOW)
            self.lights_on = turn_on
            action = "on" if turn_on else "off"
            self.log_event("lights", f"Grow lights turned {action}", "automatic")
            print(f" Grow lights: {action}")
        
        return True
    
    def control_pump(self, duration_seconds: int = 10):
        """Control water pump with safety limits"""
        if not self.check_safety_systems():
            return False
        
        # Safety checks
        max_runtime = self.config["safety"]["max_pump_runtime"]
        min_interval = self.config["safety"]["min_pump_interval"]
        
        if duration_seconds > max_runtime:
            print(f" Pump duration limited to {max_runtime} seconds for safety")
            duration_seconds = max_runtime
        
        if self.last_watering:
            time_since_last = (datetime.now() - self.last_watering).total_seconds()
            if time_since_last < min_interval:
                print(f" Pump interval too short. Wait {min_interval - time_since_last:.0f} more seconds")
                return False
        
        # Run pump
        print(f" Watering plants for {duration_seconds} seconds")
        GPIO.output(self.relay_pins["pump"], GPIO.HIGH)
        self.pump_running = True
        
        time.sleep(duration_seconds)
        
        GPIO.output(self.relay_pins["pump"], GPIO.LOW)
        self.pump_running = False
        self.last_watering = datetime.now()
        
        self.log_event("watering", f"Plants watered for {duration_seconds}s", "automatic")
        return True
    
    def log_data(self, readings: List[SensorReading]):
        """Log sensor data to educational database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate experiment day (days since first reading)
        cursor.execute("SELECT MIN(timestamp) FROM sensor_readings")
        first_reading = cursor.fetchone()[0]
        
        if first_reading:
            experiment_day = (datetime.now() - datetime.fromisoformat(first_reading)).days + 1
        else:
            experiment_day = 1
        
        # Insert readings
        for reading in readings:
            cursor.execute('''
                INSERT INTO sensor_readings 
                (timestamp, experiment_day, sensor_type, sensor_location, value, unit)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (reading.timestamp, experiment_day, reading.sensor_type, 
                  reading.location, reading.value, reading.unit))
        
        conn.commit()
        conn.close()
    
    def log_event(self, event_type: str, description: str, triggered_by: str):
        """Log system events for educational analysis"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO system_events (timestamp, event_type, description, triggered_by, student_visible)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now(), event_type, description, triggered_by, True))
        conn.commit()
        conn.close()
    
    def check_schedule(self):
        """Check if scheduled actions should occur"""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Light schedule (school hours)
        lights_on_time = self.config["schedule"]["lights_on"]
        lights_off_time = self.config["schedule"]["lights_off"]
        
        if current_time == lights_on_time and not self.lights_on:
            self.control_lights(True)
        elif current_time == lights_off_time and self.lights_on:
            self.control_lights(False)
        
        # Watering schedule
        if current_time in self.config["schedule"]["watering_times"]:
            if not self.last_watering or \
               (now - self.last_watering).total_seconds() > 3600:  # Not watered in last hour
                self.control_pump(15)  # 15 second watering
    
    def run_educational_cycle(self):
        """Main educational monitoring loop"""
        print(" Starting educational growing cycle")
        print(" Data collection optimized for student learning")
        print(" Safety systems active - Emergency stop available")
        print("Press Ctrl+C to stop\n")
        
        interval = self.config["schedule"]["data_collection_interval"]
        
        try:
            while True:
                # Safety check first
                if not self.check_safety_systems():
                    print(" Safety systems activated - monitoring paused")
                    time.sleep(10)
                    continue
                
                # Read sensors
                readings = self.read_sensors()
                
                if readings:
                    # Log data
                    self.log_data(readings)
                    
                    # Display educational summary
                    print(f"\n {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    for reading in readings:
                        print(f"   {reading.sensor_type} ({reading.location}): "
                              f"{reading.value}{reading.unit}")
                    
                    print(f" Lights: {'ON' if self.lights_on else 'OFF'}")
                    print(f" Last watering: {self.last_watering.strftime('%H:%M') if self.last_watering else 'None'}")
                    
                    # Check for teachable moments
                    self.check_educational_alerts(readings)
                
                # Check schedule
                self.check_schedule()
                
                # Wait for next reading
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n Educational session ended")
            self.safe_shutdown()
            GPIO.cleanup()
    
    def check_educational_alerts(self, readings: List[SensorReading]):
        """Check for educational learning opportunities"""
        for reading in readings:
            if reading.sensor_type == "temperature":
                temp = reading.value
                target = self.config["thresholds"]["temperature"]["target"]
                
                if abs(temp - target) > 3:
                    print(f" LEARNING OPPORTUNITY: Temperature is {temp}°C "
                          f"(target: {target}°C) - Why might this happen?")
            
            elif reading.sensor_type == "humidity":
                humidity = reading.value
                if humidity > 80:
                    print(f" LEARNING OPPORTUNITY: High humidity ({humidity}%) "
                          f"- What problems could this cause for plants?")
                elif humidity < 40:
                    print(f" LEARNING OPPORTUNITY: Low humidity ({humidity}%) "
                          f"- How do plants respond to dry air?")

if __name__ == "__main__":
    controller = EducationalGrowController()
    controller.run_educational_cycle()
```

### File: `examples/classroom_setup/student_web_interface.py`

```python
#!/usr/bin/env python3
"""
Student-friendly web interface for classroom growing system
Simplified controls with educational focus
"""

from flask import Flask, render_template, jsonify, request
import sqlite3
import json
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "educational_growing_2024"

DATABASE_PATH = "classroom_data.db"

@app.route('/')
def student_dashboard():
    """Student-friendly dashboard"""
    return render_template('student_dashboard.html')

@app.route('/teacher')
def teacher_dashboard():
    """Teacher control dashboard"""
    return render_template('teacher_dashboard.html')

@app.route('/api/current_data')
def current_data():
    """Get current sensor readings for students"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get latest readings of each type
    cursor.execute('''
        SELECT sensor_type, sensor_location, value, unit, timestamp,
               MAX(timestamp) as latest
        FROM sensor_readings 
        GROUP BY sensor_type, sensor_location
        ORDER BY latest DESC
    ''')
    
    readings = cursor.fetchall()
    conn.close()
    
    # Format for student display
    data = {
        "timestamp": datetime.now().isoformat(),
        "sensors": {}
    }
    
    for reading in readings:
        sensor_type, location, value, unit, timestamp, _ = reading
        key = f"{sensor_type}_{location}"
        data["sensors"][key] = {
            "type": sensor_type,
            "location": location,
            "value": value,
            "unit": unit,
            "timestamp": timestamp,
            "student_friendly_name": get_student_friendly_name(sensor_type, location)
        }
    
    return jsonify(data)

@app.route('/api/experiment_data')
def experiment_data():
    """Get data formatted for student experiments"""
    days = request.args.get('days', 7, type=int)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get data for the last N days
    cursor.execute('''
        SELECT experiment_day, sensor_type, sensor_location, 
               AVG(value) as avg_value, MIN(value) as min_value, 
               MAX(value) as max_value, unit
        FROM sensor_readings 
        WHERE timestamp > datetime('now', '-{} days')
        GROUP BY experiment_day, sensor_type, sensor_location
        ORDER BY experiment_day, sensor_type
    '''.format(days))
    
    results = cursor.fetchall()
    conn.close()
    
    # Format for student charts
    chart_data = {}
    for row in results:
        day, sensor_type, location, avg_val, min_val, max_val, unit = row
        key = f"{sensor_type}_{location}"
        
        if key not in chart_data:
            chart_data[key] = {
                "name": get_student_friendly_name(sensor_type, location),
                "unit": unit,
                "data": []
            }
        
        chart_data[key]["data"].append({
            "day": day,
            "average": round(avg_val, 1),
            "minimum": round(min_val, 1),
            "maximum": round(max_val, 1)
        })
    
    return jsonify(chart_data)

@app.route('/api/plant_observations')
def plant_observations():
    """Get plant growth observations for student analysis"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT experiment_day, plant_id, height_cm, leaf_count, 
               health_score, student_observer, notes, timestamp
        FROM plant_observations
        ORDER BY experiment_day, plant_id
    ''')
    
    observations = cursor.fetchall()
    conn.close()
    
    # Format for student display
    data = []
    for obs in observations:
        day, plant_id, height, leaves, health, observer, notes, timestamp = obs
        data.append({
            "experiment_day": day,
            "plant_id": plant_id,
            "height_cm": height,
            "leaf_count": leaves,
            "health_score": health,
            "observer": observer,
            "notes": notes,
            "date": timestamp
        })
    
    return jsonify(data)

@app.route('/api/add_observation', methods=['POST'])
def add_observation():
    """Allow students to add plant observations"""
    data = request.json
    
    # Validate student input
    required_fields = ['plant_id', 'height_cm', 'leaf_count', 'health_score', 'student_name']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get current experiment day
    cursor.execute("SELECT MAX(experiment_day) FROM sensor_readings")
    current_day = cursor.fetchone()[0] or 1
    
    # Insert observation
    cursor.execute('''
        INSERT INTO plant_observations 
        (timestamp, experiment_day, plant_id, height_cm, leaf_count, 
         health_score, student_observer, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now(),
        current_day,
        data['plant_id'],
        data['height_cm'],
        data['leaf_count'],
        data['health_score'],
        data['student_name'],
        data.get('notes', '')
    ))
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "message": "Observation recorded!"})

def get_student_friendly_name(sensor_type, location):
    """Convert technical names to student-friendly names"""
    names = {
        "temperature_ambient": "Room Temperature",
        "temperature_canopy": "Plant Area Temperature", 
        "temperature_root_zone": "Root Zone Temperature",
        "temperature_environment": "Growing Area Temperature",
        "humidity_environment": "Air Moisture",
        "pressure_environment": "Air Pressure",
        "light_canopy": "Light Level Above Plants"
    }
    
    key = f"{sensor_type}_{location}"
    return names.get(key, f"{sensor_type.title()} ({location})")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

## Installation Guide for Teachers

### 1. Pre-Installation Classroom Preparation

**Safety Setup:**
1. Ensure GFCI outlet near growing area
2. Install emergency stop button in accessible location
3. Prepare enclosed area for Raspberry Pi (locked from students)
4. Set up growing area with good visibility for all students

**Materials Preparation:**
1. Order all components 2 weeks before lesson
2. Pre-wire sensors to terminal blocks for easy student connection
3. Create laminated wiring diagrams for student reference
4. Prepare safety checklist and emergency procedures

### 2. Teacher Installation (1 hour setup)

```bash
# 1. Setup Raspberry Pi
sudo apt update && sudo apt upgrade -y
git clone https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments.git
cd OpenSourceControlledEnvironments
sudo ./setup/educational_setup.sh

# 2. Install educational components
cd examples/classroom_setup
pip install -r requirements.txt

# 3. Setup hardware (following wiring diagram)
# 4. Test all systems before student access

# 5. Start educational system
python3 educational_controller.py
```

### 3. Student Activities & Curriculum Integration

**Week 1: System Setup & Hypothesis**
- Students help connect sensors (low voltage only)
- Form hypothesis about plant growth
- Set up experiment variables
- Begin daily data collection

**Week 2-4: Daily Monitoring**
- Record plant observations
- Analyze daily sensor data
- Identify patterns and correlations
- Adjust growing conditions (teacher supervised)

**Week 5-6: Data Analysis**
- Create graphs from collected data
- Compare hypothesis to actual results
- Calculate growth rates and averages
- Prepare presentations of findings

**Assessment Rubric:**
- Data collection accuracy (25%)
- Scientific reasoning (25%) 
- Problem-solving (25%)
- Collaboration and safety (25%)

### 4. Safety Protocols

**Daily Classroom Checklist:**
- [ ] Emergency stop button accessible
- [ ] All electrical connections secure
- [ ] Water levels safe (no overflow risk)
- [ ] Students briefed on safety rules
- [ ] Teacher override key secured

**Student Safety Rules:**
1. Never touch electrical connections
2. Always wash hands before/after plant contact
3. Report any unusual smells or sounds immediately
4. Use emergency stop if anything seems wrong
5. No running or rough play near growing system

**Emergency Procedures:**
- **Power issues**: Hit emergency stop, call maintenance
- **Water spill**: Turn off system, clean immediately, check GFCI
- **Plant problems**: Document symptoms, research solutions
- **Student injury**: Follow school emergency protocols

## Expected Learning Outcomes

**Scientific Skills:**
- Data collection and analysis
- Hypothesis formation and testing
- Understanding of plant biology
- Environmental monitoring concepts

**Technology Skills:**
- Sensor operation and calibration
- Data visualization and interpretation
- Basic programming concepts (optional advanced activities)
- Digital measurement and precision

**Math Skills:**
- Graphing and chart creation
- Statistical analysis (averages, ranges)
- Measurement and unit conversion
- Pattern recognition in data

This educational setup provides a complete, safe, and engaging introduction to modern agriculture technology while meeting curriculum standards for science, technology, and mathematics education.
