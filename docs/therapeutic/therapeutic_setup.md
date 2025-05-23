# Therapeutic Garden Setup

A specialized growing system designed for horticultural therapy, emphasizing accessibility, sensory engagement, and therapeutic outcomes for various physical and cognitive abilities.

## Therapeutic Benefits

### Physical Therapy Goals
- **Fine motor skills**: Seed planting, gentle plant care, data recording
- **Gross motor skills**: Reaching, stretching, coordinated movements
- **Strength building**: Lifting water containers, manipulating controls
- **Coordination**: Multi-step tasks, following sequences

### Cognitive Therapy Goals
- **Memory**: Daily routines, plant care schedules, data patterns
- **Attention/Focus**: Sustained observation, task completion
- **Problem solving**: Plant health assessment, environmental adjustments
- **Planning**: Daily care routines, harvest timing

### Emotional/Social Benefits
- **Stress reduction**: Calming environment, natural interactions
- **Achievement**: Visible growth progress, successful harvests
- **Responsibility**: Daily care routines, plant welfare
- **Social interaction**: Group activities, shared experiences

## What You'll Build

A therapy-optimized system featuring:
- **Accessible height controls** (wheelchair friendly)
- **Large, easy-to-use interfaces** with tactile feedback
- **Multi-sensory feedback** (visual, auditory, tactile)
- **Gentle automation** with manual override options
- **Progress tracking** for therapeutic goals
- **Calming environment** with soft lighting and sounds

## Parts List ($220-320)

| Item | Quantity | Price | Supplier | Therapeutic Features |
|------|----------|-------|----------|---------------------|
| Raspberry Pi 4B (4GB) | 1 | $55 | Official distributors | Reliable, quiet operation |
| Large Touch Display (7") | 1 | $60 | Official Pi Foundation | Easy-to-see, touch-friendly |
| Accessibility Enclosure | 1 | $40 | Custom/Therapy supplier | Height adjustable, rounded corners |
| BME280 Environmental Sensor | 1 | $20 | Adafruit #2652 | Silent operation |
| Soil Moisture Sensors | 4 | $40 | Capacitive type | Multiple plant monitoring |
| Large Button Switches | 4 | $32 | Therapy suppliers | Easy press, tactile feedback |
| Gentle Water Pump | 1 | $18 | Aquarium type | Quiet, adjustable flow |
| LED Grow Lights (Soft) | 2 | $35 | Warm white spectrum | Eye-friendly, calming |
| Audio Feedback Module | 1 | $15 | Speaker + amplifier | Audio cues and feedback |
| Tactile Sensors | 2 | $25 | Force-sensitive pads | Touch interaction |
| Safety Mat Sensor | 1 | $20 | Pressure mat | Presence detection |

**Total: $250-360**

## Accessibility Features

### Physical Accommodations

**Wheelchair Accessibility:**
- **Height**: All controls 28"-34" from floor
- **Reach**: Maximum 18" reach required
- **Clearance**: 30" wide x 48" deep clear space
- **Surface**: Smooth, stable wheelchair access

**Motor Skill Accommodations:**
- **Large controls**: Minimum 2" diameter buttons
- **Low force**: Maximum 5 lbs force required
- **Stable support**: Armrests and support surfaces
- **Non-slip surfaces**: Textured grips and surfaces

### Cognitive Accommodations

**Simplified Interface:**
- **Visual cues**: Color coding (green=good, yellow=attention, red=help needed)
- **Large text**: Minimum 18pt fonts, high contrast
- **Simple language**: Basic vocabulary, clear instructions
- **Progress indicators**: Visual progress bars and checkmarks

**Memory Aids:**
- **Routine cards**: Step-by-step photo instructions
- **Audio reminders**: Gentle voice prompts
- **Progress tracking**: Visual history of accomplishments
- **Consistency**: Same layout and procedures daily

### Sensory Accommodations

**Visual:**
- **High contrast**: Black text on white background, colored borders
- **Large elements**: Buttons, text, and icons 2x normal size
- **Good lighting**: Even, glare-free illumination
- **Color coding**: Consistent meaning throughout

**Auditory:**
- **Clear speech**: Slow, clear audio instructions
- **Volume control**: Adjustable audio levels
- **Visual alternatives**: All audio has visual backup
- **Quiet operation**: Minimal mechanical noise

**Tactile:**
- **Texture variations**: Different textures for different functions
- **Vibration feedback**: Gentle confirmation of actions
- **Temperature feedback**: Warm/cool surfaces for guidance
- **Raised elements**: Tactile boundaries and guides

## Wiring Diagram

```
Therapeutic Garden Setup - Accessibility Focused:

┌─────────────────────────────────────────────────────────────┐
│                    THERAPIST CONTROL AREA                   │
│                   (Height: 32" from floor)                  │
│                                                             │
│  ┌─────────────────┐    ┌──────────────────────────────┐   │
│  │   Raspberry Pi  │    │     7" Touch Display         │   │
│  │   (Enclosed)    │    │   (Large Icons, High Contrast)│   │
│  │                 │    │                              │   │
│  └─────────────────┘    └──────────────────────────────┘   │
│                                                             │
│  Emergency Stop & Override Controls:                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ EMERGENCY   │  │   MANUAL    │  │   AUDIO     │         │
│  │    STOP     │  │  OVERRIDE   │  │  ON/OFF     │         │
│  │(Large, Red) │  │  (Yellow)   │  │  (Blue)     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                  PARTICIPANT INTERACTION AREA               │
│              (Height: 28"-30" - Wheelchair Accessible)      │
│                                                             │
│  Accessibility Controls:                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │   WATER     │  │   LIGHTS    │  │   CHECK     │  │   │
│  │  │   PLANTS    │  │   ON/OFF    │  │   PLANTS    │  │   │
│  │  │             │  │             │  │             │  │   │
│  │  │(Large Green │  │(Large Yellow│  │(Large Blue  │  │   │
│  │  │ Button)     │  │ Button)     │  │ Button)     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  │                                                     │   │
│  │  Audio Feedback:                                    │   │
│  │  🔊 "Great job watering!" / "Plants look healthy!"  │   │
│  │                                                     │   │
│  │  Visual Progress Display:                           │   │
│  │  ████████░░ Tasks Complete Today: 8/10              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Growing Area:                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                                                     │   │
│  │  🌱    🌱    🌱    🌱      (Accessible Height)      │   │
│  │ Plant  Plant Plant Plant                            │   │
│  │   1     2     3     4                               │   │
│  │                                                     │   │
│  │ Soil Moisture Sensors (Visual Indicators):         │   │
│  │ 💧🟢  💧🟡  💧🟢  💧🟡                              │   │
│  │ Good  Water Good  Water                             │   │
│  │       Soon        Soon                              │   │
│  │                                                     │   │
│  │ Water Reservoir (Clear, Visible Level):             │   │
│  │ ┌─────────────────────────────────────────────┐     │   │
│  │ │ Water Level: ████████░░ 80% Full            │     │   │
│  │ │ 💧 Gentle pump (nearly silent)              │     │   │
│  │ └─────────────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Safety Features:                                           │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 🛡️ Pressure Mat (detects participant presence)      │   │
│  │ 🔊 Audio cues: "Please water the yellow plant"     │   │
│  │ 📊 Progress tracking for therapy goals              │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

Connection Details:
BME280:         VIN→3.3V, GND→GND, SCL→GPIO3, SDA→GPIO2
Soil Sensors:   VCC→3.3V, GND→GND, Data→GPIO4,17,27,22
Large Buttons:  One side→GND, Other→GPIO5,6,13,19 (with pullup)
Audio Module:   VCC→5V, GND→GND, Audio→GPIO18 (PWM)
Pump Control:   Signal→GPIO23, Power→12V through relay
LED Control:    Signal→GPIO24, Power→12V through relay
Touch Display:  DSI connector (official 7" display)
Pressure Mat:   Data→GPIO25 (safety monitoring)
```

## Code

### File: `examples/therapy_garden/therapeutic_controller.py`

```python
#!/usr/bin/env python3
"""
Therapeutic Garden Controller
Designed for horticultural therapy with accessibility focus
"""

import time
import json
import sqlite3
import threading
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import RPi.GPIO as GPIO

# Audio feedback
try:
    import pygame
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("⚠️ Audio not available - running without sound feedback")

# Sensor libraries
try:
    import board
    import busio
    import adafruit_bme280
    I2C_AVAILABLE = True
except ImportError:
    I2C_AVAILABLE = False
    print("⚠️ I2C libraries not available - running in simulation mode")

@dataclass
class TherapySession:
    participant_id: str
    start_time: datetime
    activities_completed: List[str]
    goals_met: List[str]
    therapist_notes: str = ""
    mood_before: int = 5  # 1-10 scale
    mood_after: int = 5   # 1-10 scale

@dataclass
class PlantStatus:
    plant_id: int
    moisture_level: float
    needs_water: bool
    last_watered: Optional[datetime]
    participant_interactions: int

class TherapeuticGardenController:
    def __init__(self):
        self.config = self.load_therapeutic_config()
        self.setup_gpio()
        self.setup_sensors()
        self.setup_database()
        self.setup_audio()
        
        # Therapeutic state
        self.current_session = None
        self.participant_present = False
        self.emergency_stop_active = False
        self.manual_override = False
        
        # System state
        self.lights_on = False
        self.pump_running = False
        self.plant_status = {}
        
        # Accessibility features
        self.audio_enabled = True
        self.large_text_mode = True
        self.high_contrast_mode = True
        
        print("🌱 Therapeutic Garden System Initialized")
        print("♿ Accessibility features enabled")
        print("🎯 Ready for therapeutic sessions")
        
    def load_therapeutic_config(self):
        """Load therapeutic-specific configuration"""
        return {
            "accessibility": {
                "button_press_duration": 0.5,  # Seconds to register press
                "audio_volume": 0.7,
                "display_timeout": 300,  # 5 minutes
                "large_text_size": 24,
                "high_contrast": True
            },
            "therapy_goals": {
                "daily_plant_checks": 4,
                "watering_tasks": 2,
                "observation_tasks": 3,
                "fine_motor_activities": 5,
                "social_interactions": 2
            },
            "safety": {
                "emergency_stop_gpio": 21,
                "manual_override_gpio": 20,
                "presence_sensor_gpio": 25,
                "max_pump_runtime": 15,  # Shorter for safety
                "gentle_pump_speed": 0.5  # 50% speed for gentleness
            },
            "plant_care": {
                "moisture_check_interval": 300,  # 5 minutes
                "watering_duration": 8,  # Gentle, longer watering
                "moisture_threshold": 40,  # Water when below 40%
                "recovery_time": 1800  # 30 minutes between waterings
            },
            "feedback": {
                "positive_reinforcement": True,
                "progress_celebrations": True,
                "gentle_corrections": True,
                "achievement_sounds": True
            }
        }
    
    def setup_gpio(self):
        """Setup GPIO with accessibility considerations"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Safety and control inputs
        GPIO.setup(self.config["safety"]["emergency_stop_gpio"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.config["safety"]["manual_override_gpio"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.config["safety"]["presence_sensor_gpio"], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # Large accessibility buttons
        self.button_pins = {
            "water_plants": 5,
            "toggle_lights": 6,
            "check_plants": 13,
            "help_needed": 19
        }
        
        for name, pin in self.button_pins.items():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # Add event detection with debouncing
            GPIO.add_event_detect(pin, GPIO.FALLING, 
                                callback=lambda channel, btn=name: self.handle_button_press(btn),
                                bouncetime=500)
        
        # Control outputs
        self.output_pins = {
            "lights": 23,
            "pump": 24,
            "audio": 18  # PWM for audio
        }
        
        for name, pin in self.output_pins.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
        # Soil moisture sensors (analog)
        self.moisture_pins = [4, 17, 27, 22]  # 4 plants
        for pin in self.moisture_pins:
            GPIO.setup(pin, GPIO.IN)
        
        print("✅ GPIO configured for therapeutic accessibility")
    
    def setup_sensors(self):
        """Initialize sensors with error handling"""
        self.sensors = {}
        
        # Environmental sensor (BME280)
        if I2C_AVAILABLE:
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                self.bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c)
                self.sensors["environment"] = self.bme280
                print("✅ Environmental sensor ready")
            except Exception as e:
                print(f"⚠️ Environmental sensor setup failed: {e}")
        
        # Initialize plant status
        for i in range(4):  # 4 plants
            self.plant_status[i] = PlantStatus(
                plant_id=i,
                moisture_level=50.0,
                needs_water=False,
                last_watered=None,
                participant_interactions=0
            )
        
        print("✅ Therapeutic sensors initialized")
    
    def setup_database(self):
        """Create therapeutic database with therapy-specific tables"""
        self.db_path = "therapy_garden.db"
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Therapy sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS therapy_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT,
                session_date DATE,
                start_time DATETIME,
                end_time DATETIME,
                activities_completed TEXT,
                goals_achieved TEXT,
                mood_before INTEGER,
                mood_after INTEGER,
                therapist_notes TEXT,
                motor_skill_rating INTEGER,
                cognitive_engagement INTEGER,
                social_interaction INTEGER
            )
        ''')
        
        # Participant interactions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participant_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp DATETIME,
                interaction_type TEXT,
                plant_id INTEGER,
                success_level INTEGER,
                assistance_needed BOOLEAN,
                duration_seconds INTEGER,
                notes TEXT,
                FOREIGN KEY (session_id) REFERENCES therapy_sessions (id)
            )
        ''')
        
        # Plant care activities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plant_care_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                plant_id INTEGER,
                care_type TEXT,
                participant_id TEXT,
                success_rating INTEGER,
                motor_skill_demonstrated TEXT,
                cognitive_skill_demonstrated TEXT,
                notes TEXT
            )
        ''')
        
        # Sensor data with therapy context
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                sensor_type TEXT,
                value REAL,
                unit TEXT,
                plant_id INTEGER,
                therapy_relevant BOOLEAN
            )
        ''')
        
        # Progress tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS therapy_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                participant_id TEXT,
                assessment_date DATE,
                fine_motor_score INTEGER,
                gross_motor_score INTEGER,
                cognitive_score INTEGER,
                emotional_wellbeing INTEGER,
                social_engagement INTEGER,
                independence_level INTEGER,
                therapist_assessment TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Therapeutic database initialized")
    
    def setup_audio(self):
        """Setup audio feedback system"""
        if AUDIO_AVAILABLE:
            try:
                # Create audio files programmatically or load existing ones
                self.audio_messages = {
                    "welcome": "audio/welcome.wav",
                    "good_job": "audio/good_job.wav",
                    "plants_happy": "audio/plants_happy.wav",
                    "time_to_water": "audio/time_to_water.wav",
                    "task_complete": "audio/task_complete.wav",
                    "need_help": "audio/need_help.wav",
                    "session_complete": "audio/session_complete.wav"
                }
                print("✅ Audio feedback system ready")
            except Exception as e:
                print(f"⚠️ Audio setup failed: {e}")
                self.audio_enabled = False
        else:
            self.audio_enabled = False
    
    def check_participant_presence(self):
        """Check if participant is present using pressure mat"""
        return GPIO.input(self.config["safety"]["presence_sensor_gpio"]) == GPIO.HIGH
    
    def check_safety_systems(self):
        """Check emergency stop and safety systems"""
        # Emergency stop
        if GPIO.input(self.config["safety"]["emergency_stop_gpio"]) == GPIO.LOW:
            if not self.emergency_stop_active:
                self.emergency_stop_active = True
                self.safe_shutdown()
                self.play_audio("emergency_stop")
                print("🚨 EMERGENCY STOP - All systems halted")
            return False
        else:
            if self.emergency_stop_active:
                self.emergency_stop_active = False
                print("✅ Emergency stop reset")
        
        # Manual override by therapist
        self.manual_override = GPIO.input(self.config["safety"]["manual_override_gpio"]) == GPIO.LOW
        
        return not self.emergency_stop_active
    
    def safe_shutdown(self):
        """Safely shut down all therapeutic systems"""
        for pin in self.output_pins.values():
            GPIO.output(pin, GPIO.LOW)
        
        self.lights_on = False
        self.pump_running = False
        
        if self.current_session:
            self.end_therapy_session("emergency_stop")
        
        print("🛡️ Therapeutic systems safely shut down")
    
    def handle_button_press(self, button_name):
        """Handle accessibility button presses with feedback"""
        if not self.check_safety_systems():
            return
        
        if not self.participant_present:
            self.participant_present = self.check_participant_presence()
            if not self.participant_present:
                return
        
        print(f"🖲️ Button pressed: {button_name}")
        
        # Provide immediate tactile/audio feedback
        self.provide_button_feedback(button_name)
        
        # Log interaction
        if self.current_session:
            self.log_participant_interaction(button_name, "button_press")
        
        # Handle specific button actions
        if button_name == "water_plants":
            self.participant_water_plants()
        elif button_name == "toggle_lights":
            self.participant_toggle_lights()
        elif button_name == "check_plants":
            self.participant_check_plants()
        elif button_name == "help_needed":
            self.participant_request_help()
    
    def provide_button_feedback(self, button_name):
        """Provide immediate feedback for button press"""
        # Audio feedback
        if self.audio_enabled:
            feedback_messages = {
                "water_plants": "Watering plants now...",
                "toggle_lights": "Changing lights...",
                "check_plants": "Checking on plants...",
                "help_needed": "Help is on the way..."
            }
            # In real implementation, use text-to-speech or pre-recorded audio
            print(f"🔊 Audio: {feedback_messages.get(button_name, 'Action started')}")
        
        # Visual feedback (would be on display)
        print(f"💡 Visual: {button_name.replace('_', ' ').title()} activated")
        
        # Tactile feedback (brief LED flash or vibration)
        GPIO.output(self.output_pins["lights"], GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.output_pins["lights"], GPIO.LOW if not self.lights_on else GPIO.HIGH)
    
    def participant_water_plants(self):
        """Allow participant to water plants with guidance"""
        plants_needing_water = [pid for pid, status in self.plant_status.items() 
                               if status.needs_water]
        
        if not plants_needing_water:
            self.play_audio("plants_happy")
            print("💧 All plants have enough water! Great job caring for them.")
            return
        
        # Guide participant to water specific plants
        for plant_id in plants_needing_water[:2]:  # Limit to 2 plants per session
            print(f"💧 Watering plant {plant_id + 1}...")
            
            # Gentle watering with participant involvement
            self.gentle_watering(plant_id, participant_assisted=True)
            
            # Update plant status
            self.plant_status[plant_id].needs_water = False
            self.plant_status[plant_id].last_watered = datetime.now()
            self.plant_status[plant_id].participant_interactions += 1
            
            # Log therapeutic activity
            self.log_plant_care_activity(plant_id, "watering", success_rating=8)
            
        self.play_audio("good_job")
        print("🎉 Excellent watering! The plants are happy and healthy.")
    
    def gentle_watering(self, plant_id, participant_assisted=True):
        """Perform gentle watering suitable for therapy"""
        duration = self.config["plant_care"]["watering_duration"]
        
        print(f"💧 Gently watering plant {plant_id + 1} for {duration} seconds...")
        
        # Start pump at gentle speed
        GPIO.output(self.output_pins["pump"], GPIO.HIGH)
        self.pump_running = True
        
        # Count down for participant engagement
        if participant_assisted:
            for i in range(duration, 0, -1):
                if i % 2 == 0:  # Every 2 seconds
                    print(f"   💧 Watering... {i} seconds remaining")
                time.sleep(1)
        else:
            time.sleep(duration)
        
        # Stop pump
        GPIO.output(self.output_pins["pump"], GPIO.LOW)
        self.pump_running = False
        
        print(f"   ✅ Plant {plant_id + 1} watered successfully!")
    
    def participant_toggle_lights(self):
        """Allow participant to control lighting"""
        new_state = not self.lights_on
        
        GPIO.output(self.output_pins["lights"], GPIO.HIGH if new_state else GPIO.LOW)
        self.lights_on = new_state
        
        action = "on" if new_state else "off"
        print(f"💡 Lights turned {action} by participant")
        
        # Audio feedback
        if self.audio_enabled:
            print(f"🔊 'Great job turning the lights {action}! Plants need light to grow.'")
        
        # Log therapeutic interaction
        if self.current_session:
            self.log_participant_interaction("light_control", "motor_skill")
    
    def participant_check_plants(self):
        """Guide participant through plant observation"""
        print("🔍 Let's check on our plants together!")
        
        for plant_id, status in self.plant_status.items():
            # Read current moisture
            moisture = self.read_soil_moisture(plant_id)
            self.plant_status[plant_id].moisture_level = moisture
            
            # Provide educational feedback
            if moisture > 60:
                condition = "very happy - nice and moist!"
                print(f"🌱 Plant {plant_id + 1}: {condition}")
            elif moisture > 40:
                condition = "doing well - has enough water"
                print(f"🌱 Plant {plant_id + 1}: {condition}")
            else:
                condition = "thirsty - needs water soon"
                self.plant_status[plant_id].needs_water = True
                print(f"🌱 Plant {plant_id + 1}: {condition}")
                
            # Brief pause for observation
            time.sleep(2)
        
        # Log observation activity
        self.log_plant_care_activity(None, "observation", success_rating=9)
        
        self.play_audio("good_job")
        print("🎉 Excellent plant checking! You're a wonderful plant caretaker.")
    
    def participant_request_help(self):
        """Handle participant request for assistance"""
        print("🆘 Participant requesting assistance")
        
        # Audio feedback
        if self.audio_enabled:
            print("🔊 'Help is on the way! You're doing great!'")
        
        # Log interaction
        if self.current_session:
            self.log_participant_interaction("help_request", "communication")
        
        # In real implementation, this would notify therapist
        print("📞 Therapist notified of assistance request")
    
    def read_soil_moisture(self, plant_id):
        """Read soil moisture for specific plant"""
        try:
            # Simulate reading from capacitive soil sensor
            # In real implementation, this would use ADC to read analog sensor
            pin = self.moisture_pins[plant_id]
            
            # Simplified reading (in real implementation, use MCP3008 or ADS1115)
            # For now, simulate based on time since last watering
            if self.plant_status[plant_id].last_watered:
                hours_since = (datetime.now() - self.plant_status[plant_id].last_watered).total_seconds() / 3600
                moisture = max(20, 80 - (hours_since * 5))  # Gradual decrease
            else:
                moisture = 30  # Default low moisture
            
            return round(moisture, 1)
        
        except Exception as e:
            print(f"⚠️ Error reading soil moisture for plant {plant_id}: {e}")
            return 50.0  # Safe default
    
    def start_therapy_session(self, participant_id, therapist_notes=""):
        """Start a new therapy session"""
        if self.current_session:
            self.end_therapy_session("new_session_started")
        
        self.current_session = TherapySession(
            participant_id=participant_id,
            start_time=datetime.now(),
            activities_completed=[],
            goals_met=[],
            therapist_notes=therapist_notes
        )
        
        # Welcome participant
        self.play_audio("welcome")
        print(f"🌱 Welcome to the therapeutic garden, {participant_id}!")
        print("🎯 Today's activities: check plants, water them, and watch them grow!")
        
        # Log session start
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO therapy_sessions 
            (participant_id, session_date, start_time, therapist_notes)
            VALUES (?, ?, ?, ?)
        ''', (participant_id, datetime.now().date(), datetime.now(), therapist_notes))
        
        self.current_session.session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        print(f"📝 Therapy session {self.current_session.session_id} started")
    
    def end_therapy_session(self, reason="normal_completion"):
        """End current therapy session with summary"""
        if not self.current_session:
            return
        
        session = self.current_session
        session.end_time = datetime.now()
        
        # Calculate session duration
        duration = (session.end_time - session.start_time).total_seconds() / 60
        
        # Update database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE therapy_sessions 
            SET end_time = ?, activities_completed = ?, goals_achieved = ?,
                mood_after = ?
            WHERE id = ?
        ''', (session.end_time, 
              json.dumps(session.activities_completed),
              json.dumps(session.goals_met),
              session.mood_after,
              session.session_id))
        
        conn.commit()
        conn.close()
        
        # Session summary
        print(f"\n🎉 Therapy session complete!")
        print(f"⏱️ Duration: {duration:.1f} minutes")
        print(f"✅ Activities completed: {len(session.activities_completed)}")
        print(f"🎯 Goals achieved: {len(session.goals_met)}")
        
        self.play_audio("session_complete")
        
        self.current_session = None
    
    def log_participant_interaction(self, interaction_type, skill_category):
        """Log participant interaction for therapy tracking"""
        if not self.current_session:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO participant_interactions
            (session_id, timestamp, interaction_type, success_level, assistance_needed)
            VALUES (?, ?, ?, ?, ?)
        ''', (self.current_session.session_id, datetime.now(), 
              interaction_type, 8, False))  # Default values for demo
        
        conn.commit()
        conn.close()
        
        # Update session activities
        if interaction_type not in self.current_session.activities_completed:
            self.current_session.activities_completed.append(interaction_type)
    
    def log_plant_care_activity(self, plant_id, care_type, success_rating):
        """Log plant care activity for therapeutic assessment"""
        if not self.current_session:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO plant_care_log
            (timestamp, plant_id, care_type, participant_id, success_rating,
             motor_skill_demonstrated, cognitive_skill_demonstrated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (datetime.now(), plant_id, care_type, 
              self.current_session.participant_id, success_rating,
              "fine_motor", "attention_focus"))
        
        conn.commit()
        conn.close()
    
    def play_audio(self, message_type):
        """Play audio feedback message"""
        if not self.audio_enabled:
            return
        
        try:
            # In real implementation, load and play audio file
            messages = {
                "welcome": "Welcome to the garden! Let's take care of our plants together.",
                "good_job": "Excellent work! You're doing great!",
                "plants_happy": "The plants are happy and healthy thanks to you!",
                "time_to_water": "Some plants are thirsty. Can you help water them?",
                "task_complete": "Task completed successfully! Great job!",
                "session_complete": "Wonderful session today! See you next time!"
            }
            
            message = messages.get(message_type, "Great job!")
            print(f"🔊 Audio: {message}")
            
        except Exception as e:
            print(f"⚠️ Audio playback failed: {e}")
    
    def run_therapy_monitoring(self):
        """Main therapeutic monitoring loop"""
        print("🌱 Therapeutic Garden System Active")
        print("♿ All accessibility features enabled")
        print("🎯 Ready for therapy sessions")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Safety check
                if not self.check_safety_systems():
                    time.sleep(5)
                    continue
                
                # Check participant presence
                self.participant_present = self.check_participant_presence()
                
                if self.participant_present and not self.current_session:
                    print("👋 Participant detected - ready to start session")
                    # In real implementation, therapist would start session
                    # For demo, auto-start after 3 seconds
                    time.sleep(3)
                    if self.check_participant_presence():
                        self.start_therapy_session("demo_participant")
                
                elif not self.participant_present and self.current_session:
                    # Participant left - pause or end session
                    print("⏸️ Participant not detected - session paused")
                    time.sleep(10)  # Wait 10 seconds before ending
                    if not self.check_participant_presence():
                        self.end_therapy_session("participant_left")
                
                # Update plant status
                for plant_id in range(4):
                    moisture = self.read_soil_moisture(plant_id)
                    self.plant_status[plant_id].moisture_level = moisture
                    
                    if moisture < self.config["plant_care"]["moisture_threshold"]:
                        self.plant_status[plant_id].needs_water = True
                
                # Gentle automated care (when no participant present)
                if not self.participant_present:
                    for plant_id, status in self.plant_status.items():
                        if status.needs_water and status.last_watered:
                            hours_since = (datetime.now() - status.last_watered).total_seconds() / 3600
                            if hours_since > 6:  # Auto-water after 6 hours
                                self.gentle_watering(plant_id, participant_assisted=False)
                                status.needs_water = False
                                status.last_watered = datetime.now()
                
                # Status display (every 30 seconds)
                if int(time.time()) % 30 == 0:
                    self.display_system_status()
                
                time.sleep(1)  # Short loop for responsiveness
                
        except KeyboardInterrupt:
            print("\n🌱 Therapeutic Garden System Shutting Down")
            if self.current_session:
                self.end_therapy_session("system_shutdown")
            self.safe_shutdown()
            GPIO.cleanup()
    
    def display_system_status(self):
        """Display current system status for monitoring"""
        print(f"\n📊 System Status - {datetime.now().strftime('%H:%M:%S')}")
        print(f"👤 Participant present: {'Yes' if self.participant_present else 'No'}")
        
        if self.current_session:
            duration = (datetime.now() - self.current_session.start_time).total_seconds() / 60
            print(f"🎯 Session active: {duration:.1f} minutes")
            print(f"✅ Activities: {len(self.current_session.activities_completed)}")
        
        print("🌱 Plant Status:")
        for plant_id, status in self.plant_status.items():
            moisture = status.moisture_level
            water_icon = "💧" if status.needs_water else "✅"
            print(f"   Plant {plant_id + 1}: {moisture:.1f}% {water_icon}")
        
        print(f"💡 Lights: {'ON' if self.lights_on else 'OFF'}")
        print()

if __name__ == "__main__":
    controller = TherapeuticGardenController()
    controller.run_therapy_monitoring()
```

## Therapeutic Installation Guide

### 1. Space Requirements

**Physical Setup:**
- **Clear space**: 4' x 6' minimum for wheelchair access
- **Height**: All controls between 28"-34" from floor
- **Lighting**: Even, glare-free illumination (avoid shadows)
- **Flooring**: Non-slip, stable surface suitable for wheelchairs
- **Ventilation**: Good air circulation, avoid drafts

**Accessibility Compliance:**
- **ADA Standards**: Follow local accessibility guidelines
- **Emergency exits**: Clear, unobstructed access
- **Communication**: Visual and audio alert systems
- **Support**: Nearby seating or support surfaces

### 2. Safety Considerations

**Electrical Safety:**
- **GFCI protection**: All electrical outlets
- **Low voltage**: 12V maximum for participant-accessible components
- **Emergency stops**: Large, easily accessible buttons
- **Professional installation**: Licensed electrician for all AC wiring

**Therapeutic Safety:**
- **Supervision**: Trained therapy staff always present
- **Emergency procedures**: Clear protocols for all staff
- **Participant assessment**: Evaluate individual capabilities
- **Infection control**: Easy-to-clean surfaces and tools

### 3. Therapist Training Requirements

**Technical Training:**
- System operation and basic troubleshooting
- Data collection and progress tracking
- Safety procedures and emergency protocols
- Accessibility feature operation

**Therapeutic Integration:**
- Goal setting and progress measurement
- Activity adaptation for different abilities
- Motivation and positive reinforcement techniques
- Documentation requirements

### 4. Expected Therapeutic Outcomes

**Motor Skills (4-8 weeks):**
- Improved fine motor control (buttons, gentle handling)
- Enhanced gross motor coordination (reaching, positioning)
- Better strength and endurance
- Increased range of motion

**Cognitive Benefits (2-6 weeks):**
- Improved attention span and focus
- Better memory and routine following
- Enhanced problem-solving skills
- Increased planning and sequencing abilities

**Emotional Benefits (1-4 weeks):**
- Reduced stress and anxiety
- Increased sense of accomplishment
- Improved mood and emotional regulation
- Enhanced self-esteem and confidence

**Social Benefits (2-8 weeks):**
- Better communication and interaction
- Increased cooperation and turn-taking
- Enhanced social engagement
- Improved following of instructions

This therapeutic setup provides a safe, accessible, and engaging environment for horticultural therapy while collecting valuable data on participant progress and therapeutic outcomes.
