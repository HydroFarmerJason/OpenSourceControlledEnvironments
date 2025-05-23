# quickstart.py - Your First OSCE Setup in 5 Minutes
"""
This is what using OSCE should feel like - dead simple!
No complex configuration, no manual hardware setup, just works.
"""

from osce import ControlledEnvironment, Recipe

# === Example 1: Absolute Simplest Setup ===
# Just monitor temperature and humidity
env = ControlledEnvironment()
env.start()
# That's it! Dashboard available at http://your-pi:8080

# === Example 2: Basic Greenhouse ===
greenhouse = ControlledEnvironment("My Greenhouse")

# Add sensors (auto-detects type from common pins)
greenhouse.add_sensor("temp", pin=4)      # Auto-detects as DHT22
greenhouse.add_sensor("soil", pin=17)     # Auto-detects as moisture sensor

# Add actuators
greenhouse.add_relay("lights", pin=22)
greenhouse.add_relay("pump", pin=27)

# Simple automation rules (readable by anyone!)
greenhouse.automate(
    when="time is 6:00",
    then="turn lights on"
)

greenhouse.automate(
    when="time is 18:00",
    then="turn lights off"
)

greenhouse.automate(
    when="soil moisture < 40%",
    then="turn pump on for 30 seconds"
)

greenhouse.automate(
    when="temperature > 30°C",
    then="send alert: Too hot!"
)

# Start monitoring
greenhouse.start()

# === Example 3: Using a Recipe (Pre-configured Setup) ===
# Recipes are community-shared configurations
tomatoes = Recipe.load("indoor-tomatoes")

# Recipe automatically configures:
# - 16 hours of light (6am-10pm)
# - Temperature range: 18-26°C
# - Humidity range: 60-70%
# - Watering schedule based on moisture

env = ControlledEnvironment.from_recipe(tomatoes)
env.start()

# === Example 4: The WordPress Way - Everything is a Plugin ===
env = ControlledEnvironment()

# Install plugins with one line
env.install_plugin("weather-forecast")
env.install_plugin("plant-camera")
env.install_plugin("mobile-app")
env.install_plugin("alexa-control")

# Plugins automatically add their features
# No configuration needed for basic use

env.start()

# === Example 5: Multi-Zone Setup ===
farm = ControlledEnvironment("Urban Farm")

# Define zones
farm.add_zone("seedlings", pins={"temp": 4, "humid": 5, "light": 22})
farm.add_zone("vegetables", pins={"temp": 6, "humid": 7, "light": 23})
farm.add_zone("herbs", pins={"temp": 8, "humid": 9, "light": 24})

# Each zone can have different settings
farm.zone("seedlings").set_schedule({
    "lights": "on from 6:00 to 20:00",
    "temperature": "maintain 22-24°C",
    "humidity": "maintain 70-80%"
})

farm.zone("herbs").set_schedule({
    "lights": "on from 5:00 to 21:00",
    "temperature": "maintain 18-22°C",
    "humidity": "maintain 50-60%"
})

farm.start()

# === What Happens Behind the Scenes ===
"""
When you call env.start(), OSCE automatically:

1. Detects your hardware (Raspberry Pi model, GPIO version)
2. Initializes sensors with smart defaults
3. Creates a local database
4. Starts the web dashboard
5. Begins logging data
6. Activates any automation rules
7. Starts the API server
8. Enables mobile access via QR code

All the complexity is hidden but accessible if needed.
"""

# === The Dashboard Shows ===
"""
┌─────────────────────────────────────┐
│ My Greenhouse        [Settings] [+] │
├─────────────────────────────────────┤
│ Temperature  23.5°C  [──────●────]  │
│ Humidity     65%     [───────●───]  │
│ Soil         45%     [────●──────]  │
│                                     │
│ Lights      🟢 ON   (6:00 - 18:00) │
│ Pump        ⭘ OFF   (Auto)         │
├─────────────────────────────────────┤
│ [📊 Charts] [📅 Schedule] [🔌 Plugins]│
└─────────────────────────────────────┘
"""

# === For Advanced Users ===
# Everything is still accessible
env = ControlledEnvironment()

# Direct hardware access
temp = env.sensors.temp_1.read_raw()

# Custom automation with Python
@env.automation_rule
def complex_logic(sensors, actuators):
    if sensors.temp > 25 and sensors.humid < 50:
        actuators.misting_system.activate(duration=30)
        
# Raw SQL access
data = env.database.query("SELECT * FROM readings WHERE timestamp > ?")

# Custom API endpoints
@env.api_route("/custom/endpoint")
def my_endpoint():
    return {"status": "custom"}

# But none of this is required for basic use!