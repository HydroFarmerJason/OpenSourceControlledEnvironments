# examples/unified_setup.py
"""
OSCE Unified Setup - Works on ANY Hardware
This demonstrates how HAL makes OSCE truly platform-agnostic
"""

from osce import Environment

# === Example 1: Auto-Detect Everything ===
# The simplest possible setup - OSCE figures it out
env = Environment("My Smart Garden")
env.auto_setup()  # Detects hardware, sensors, everything
env.start()
print(f"Dashboard: http://localhost:8080")
print(f"Detected: {env.get_summary()}")

# Output:
# Detected hardware: Raspberry Pi 4
# Found sensors:
#   - DHT22 Temperature/Humidity (Pin 4)
#   - DS18B20 Soil Temperature (Pin 7)
#   - BH1750 Light Sensor (I2C 0x23)
# Dashboard: http://localhost:8080

# === Example 2: Mixed Hardware Setup ===
# Raspberry Pi as main controller with ESP32 remote nodes
env = Environment("Distributed Greenhouse")

# Main controller (auto-detected as Raspberry Pi)
env.add_sensor("air_temp", pin=4)  # DHT22 on Pi
env.add_actuator("main_pump", pin=22)  # Relay on Pi

# Add ESP32 for remote monitoring
env.add_remote_node(
    name="south_wall",
    type="esp32",
    address="192.168.1.100"  # ESP32 running OSCE firmware
)

# Sensors on ESP32 are automatically available
env.south_wall.add_sensor("wall_temp", pin=34)
env.south_wall.add_sensor("wall_humidity", pin=35)

# Add Arduino for precise analog readings
env.add_remote_node(
    name="nutrient_monitor",
    type="arduino",
    port="/dev/ttyUSB0"
)

env.nutrient_monitor.add_sensor("ph", pin="A0")
env.nutrient_monitor.add_sensor("ec", pin="A1")

# Single dashboard shows everything
env.start()

# === Example 3: Platform-Specific Features ===
# Use each platform's strengths
env = Environment("Advanced Setup")

# Raspberry Pi: Complex logic and internet
env.add_plugin("weather-forecast")  # Needs internet
env.add_plugin("ai-plant-health")   # Needs processing power

# ESP32: Wireless sensors
esp_node = env.add_node("wireless_sensors", "esp32", "192.168.1.101")
esp_node.enable_deep_sleep(minutes=10)  # Battery saving
esp_node.add_sensor("remote_temp", pin=34)

# Arduino: Precise timing
arduino = env.add_node("dosing_system", "arduino", "/dev/ttyUSB0")
arduino.add_precision_pump("nutrients", pin=9)  # Microsecond accuracy

env.start()

# === Example 4: Progressive Enhancement ===
# Start simple, grow over time
env = Environment("Beginner Friendly")

# Day 1: Just monitoring
env.add_sensor("temperature", pin=4)
env.start()

# Week 2: Add automation
env.add_actuator("fan", pin=22)
env.add_rule("if temperature > 28 then turn fan on")

# Month 2: Add remote monitoring
env.install_plugin("mobile-app")
env.install_plugin("email-alerts")

# Month 6: Go distributed
env.add_node("greenhouse_2", "esp32", "greenhouse2.local")
env.install_plugin("multi-zone-climate")

# Year 2: Commercial scale
env.install_plugin("osce-commercial-suite")
env.enable_redundancy()
env.enable_data_backup()

# === Example 5: The WordPress Way ===
# Everything beyond basics is a plugin

# Minimal core
env = Environment()
env.start()  # Just data logging

# User installs only what they need:
env.install_plugin("tomato-recipes")     # Growing recipes
env.install_plugin("spanish-language")   # Localization  
env.install_plugin("hydroponic-dosing")  # Specialized feature
env.install_plugin("3d-plant-view")      # Fancy visualization

# === Example 6: Migration from Other Systems ===

# From Mycodo
env = Environment("Migrated from Mycodo")
env.install_plugin("mycodo-importer")
env.import_config("/home/pi/Mycodo/mycodo.db")
env.start()  # All settings preserved

# From Arduino sketch
env = Environment("Upgraded Arduino")
env.install_plugin("arduino-sketch-wrapper")
env.wrap_sketch("/home/user/greenhouse/greenhouse.ino")
env.add_web_dashboard()  # Arduino sketch now has web UI!
env.start()

# From custom Python script
env = Environment("Enhanced Custom Script")
env.install_plugin("python-script-adapter")

@env.sensor("custom_calculation")
def my_complex_sensor():
    """Your existing code becomes a sensor"""
    # ... existing calculation code ...
    return calculated_value

env.start()  # Custom code now integrated with OSCE

# === Platform Comparison ===
"""
Setup Time Comparison:

Traditional Arduino Project:
- Write sketch: 2-4 hours
- Add web server: 8-12 hours  
- Add data logging: 4-6 hours
- Add phone app: Give up
Total: Several days to weeks

Commercial System:
- Purchase: $800-3000
- Wait for shipping: 3-7 days
- Learn proprietary software: 2-4 hours
- Realize you need their sensors: +$500
Total: Week+ and $1000s

OSCE on Any Hardware:
- Install: 5 minutes
- Add sensors: 30 seconds each
- See data on phone: Immediate
- Add any feature: Install plugin
Total: 5 minutes to functional
"""

# === The Magic: Hardware Abstraction ===
# This same code works on:
# - Raspberry Pi (all models)
# - ESP32 (any variant)
# - ESP8266
# - Arduino (Uno, Mega, Nano)
# - Orange Pi
# - BeagleBone
# - Rock Pi
# - NVIDIA Jetson (for AI)
# - Your laptop (for testing)
# - Mixed combinations of all above!

# The user doesn't need to know or care about:
# - GPIO libraries
# - Communication protocols  
# - Driver installation
# - Pin mappings
# - Voltage levels
# - I2C addresses

# They just say what they want:
env = Environment("Just Works")
env.add_sensor("temperature")  # OSCE figures out the rest
env.add_actuator("light")       # OSCE handles the details
env.start()                     # It just works