#!/usr/bin/env python3
"""
Container Farm Control System - Voice Interface Placeholder
This script simulates voice control capabilities for future implementation
It provides a sandbox for testing voice commands with the farm system

Usage:
    python3 voice_interface.py                  # Interactive mode
    python3 voice_interface.py --text "command" # Direct command mode
    python3 voice_interface.py --listen         # Microphone listening mode (if supported)
"""

import os
import sys
import time
import json
import argparse
import subprocess
import random
import re
from datetime import datetime

# Base directories
INSTALL_DIR = "/opt/container-farm-control"
CONFIG_DIR = os.path.join(INSTALL_DIR, "configs")
SCRIPTS_DIR = os.path.join(INSTALL_DIR, "scripts")
VOICE_DIR = os.path.join(INSTALL_DIR, "voice_control")

# Ensure voice control directory exists
os.makedirs(VOICE_DIR, exist_ok=True)

# Voice command log file
COMMAND_LOG = os.path.join(VOICE_DIR, "voice_commands.log")

# Load Mycodo command functions (these are just simulations)
def get_mycodo_status():
    """Get status of Mycodo services (simulated)"""
    return {
        "services": {
            "mycodoflask": "active",
            "mycododaemon": "active"
        },
        "sensors": {
            "temperature": random.uniform(20.0, 25.0),
            "humidity": random.uniform(40.0, 60.0),
            "moisture": random.uniform(30.0, 70.0),
            "light": random.uniform(200.0, 800.0)
        },
        "relays": {
            "lights": random.choice([True, False]),
            "water_pump": random.choice([True, False]),
            "fan": random.choice([True, False]),
            "heater": False
        },
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def toggle_output(output_name, state=None):
    """
    Toggle a Mycodo output (simulated)
    
    Args:
        output_name: Name of the output to toggle (lights, water_pump, fan, heater)
        state: True for on, False for off, None to toggle
    
    Returns:
        dict: Status of the operation
    """
    valid_outputs = ["lights", "water_pump", "fan", "heater"]
    
    if output_name not in valid_outputs:
        return {"success": False, "message": f"Unknown output: {output_name}"}
    
    # Get current state (simulated)
    current_state = get_mycodo_status()["relays"][output_name]
    
    # Determine new state
    if state is None:
        new_state = not current_state
    else:
        new_state = state
    
    # Log the action
    log_command(f"Toggle {output_name} to {'ON' if new_state else 'OFF'}")
    
    return {
        "success": True, 
        "output": output_name,
        "state": new_state,
        "message": f"{output_name.replace('_', ' ').title()} turned {'ON' if new_state else 'OFF'}"
    }

def get_sensor_reading(sensor_name):
    """
    Get reading from a Mycodo sensor (simulated)
    
    Args:
        sensor_name: Name of sensor (temperature, humidity, moisture, light)
    
    Returns:
        dict: Sensor reading data
    """
    valid_sensors = ["temperature", "humidity", "moisture", "light"]
    
    if sensor_name not in valid_sensors:
        return {"success": False, "message": f"Unknown sensor: {sensor_name}"}
    
    # Get simulated reading
    status = get_mycodo_status()
    reading = status["sensors"].get(sensor_name)
    
    # Format reading nicely
    units = {"temperature": "°C", "humidity": "%", "moisture": "%", "light": "lux"}
    formatted_reading = f"{reading:.1f} {units.get(sensor_name, '')}"
    
    log_command(f"Read {sensor_name} sensor: {formatted_reading}")
    
    return {
        "success": True,
        "sensor": sensor_name,
        "value": reading,
        "formatted": formatted_reading,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def take_snapshot():
    """Take a camera snapshot (simulated)"""
    log_command("Take camera snapshot")
    
    # Simulate taking a photo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"snapshot_{timestamp}.jpg"
    
    return {
        "success": True,
        "message": f"Snapshot taken: {filename}",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def log_command(command_text):
    """Log voice commands to a file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(COMMAND_LOG, "a") as log_file:
        log_file.write(f"{timestamp} - {command_text}\n")

def get_system_summary():
    """Get a summary of system status (simulated)"""
    status = get_mycodo_status()
    
    summary = {
        "temperature": f"{status['sensors']['temperature']:.1f}°C",
        "humidity": f"{status['sensors']['humidity']:.1f}%",
        "light_status": "ON" if status["relays"]["lights"] else "OFF",
        "water_pump_status": "ON" if status["relays"]["water_pump"] else "OFF",
        "fan_status": "ON" if status["relays"]["fan"] else "OFF",
        "system_status": "Healthy" if all(status["services"].values()) else "Warning",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    log_command("Get system summary")
    
    return summary

# Command patterns
COMMANDS = {
    # Lights control
    r"(turn|switch) (on|off) (?:the )?lights": lambda m: toggle_output("lights", m.group(2).lower() == "on"),
    r"lights (on|off)": lambda m: toggle_output("lights", m.group(1).lower() == "on"),
    
    # Water pump control
    r"(turn|switch) (on|off) (?:the )?(?:water )?pump": lambda m: toggle_output("water_pump", m.group(2).lower() == "on"),
    r"water (?:the )?plants": lambda m: toggle_output("water_pump", True),
    r"stop watering": lambda m: toggle_output("water_pump", False),
    
    # Fan control
    r"(turn|switch) (on|off) (?:the )?fans?": lambda m: toggle_output("fan", m.group(2).lower() == "on"),
    r"fans? (on|off)": lambda m: toggle_output("fan", m.group(1).lower() == "on"),
    
    # Temperature control
    r"(turn|switch) (on|off) (?:the )?heater": lambda m: toggle_output("heater", m.group(2).lower() == "on"),
    
    # Sensor readings
    r"(?:what'?s|what is|read|check) (?:the )?temperature": lambda m: get_sensor_reading("temperature"),
    r"(?:what'?s|what is|read|check) (?:the )?humidity": lambda m: get_sensor_reading("humidity"),
    r"(?:what'?s|what is|read|check) (?:the )?moisture": lambda m: get_sensor_reading("moisture"),
    r"(?:what'?s|what is|read|check) (?:the )?light (?:level|intensity)": lambda m: get_sensor_reading("light"),
    
    # Camera functions
    r"take (?:a )?(?:picture|photo|snapshot|image)": lambda m: take_snapshot(),
    
    # System status
    r"(?:what'?s|what is|read|check) (?:the )?system status": lambda m: get_system_summary(),
    r"(?:give me a )?system (?:summary|report|status)": lambda m: get_system_summary(),
    r"how (?:are|is) (?:the )?plants?": lambda m: get_system_summary(),
    r"how'?s (?:the )?farm": lambda m: get_system_summary()
}

def process_command(command_text):
    """
    Process a voice command
    
    Args:
        command_text: The text of the command to process
        
    Returns:
        dict: The result of the command
    """
    command_text = command_text.lower().strip()
    
    # Handle help command
    if command_text in ["help", "commands", "what can you do"]:
        return show_help()
    
    # Handle exit command
    if command_text in ["exit", "quit", "goodbye"]:
        return {"success": True, "message": "Goodbye!"}
    
    # Process against command patterns
    for pattern, handler in COMMANDS.items():
        match = re.match(pattern, command_text, re.IGNORECASE)
        if match:
            return handler(match)
    
    # No match found
    return {
        "success": False,
        "message": "I didn't understand that command. Try 'help' to see available commands."
    }

def show_help():
    """Show help information about available commands"""
    help_text = """
Available voice commands:

LIGHTS:
  - "Turn on the lights"
  - "Turn off the lights"
  - "Lights on"
  - "Lights off"

WATER:
  - "Turn on the water pump"
  - "Turn off the water pump"
  - "Water the plants"
  - "Stop watering"

FANS:
  - "Turn on the fans"
  - "Turn off the fans"
  - "Fan on"
  - "Fan off"

TEMPERATURE:
  - "Turn on the heater"
  - "Turn off the heater"

SENSORS:
  - "What's the temperature?"
  - "Check the humidity"
  - "Read moisture"
  - "What's the light level?"

CAMERA:
  - "Take a picture"
  - "Take a snapshot"

SYSTEM:
  - "System status"
  - "How are the plants?"
  - "System summary"

OTHER:
  - "help" - Show this help message
  - "exit" - Exit interactive mode
"""
    
    log_command("Show help")
    
    return {
        "success": True,
        "message": help_text
    }

def simulate_voice_activation(text_input=None):
    """
    Simulate voice activation with text input
    
    Args:
        text_input: Optional text input, if None will prompt user
    
    Returns:
        None
    """
    print("\n  Container Farm Voice Control Simulator ")
    print("=" * 50)
    print("This is a placeholder for future voice control capabilities.")
    print("You can test how voice commands will work in the future.")
    print("Type 'help' to see available commands, 'exit' to quit.")
    print("=" * 50)
    
    # Single command mode
    if text_input:
        result = process_command(text_input)
        if result.get("success", False):
            if "message" in result:
                print(f"\n {result['message']}")
            
            # Print any additional details
            for key, value in result.items():
                if key not in ["success", "message"]:
                    print(f"  {key}: {value}")
        else:
            print(f"\n {result.get('message', 'Command failed')}")
        
        return
    
    # Interactive mode
    while True:
        try:
            command = input("\n Say a command: ")
            
            if not command.strip():
                continue
                
            result = process_command(command)
            
            if command.lower() in ["exit", "quit", "goodbye"]:
                print("Voice control deactivated. Goodbye!")
                break
                
            if result.get("success", False):
                if "message" in result:
                    print(f"\n {result['message']}")
                
                # Print any additional details
                for key, value in result.items():
                    if key not in ["success", "message"]:
                        print(f"  {key}: {value}")
            else:
                print(f"\n {result.get('message', 'Command failed')}")
                
        except KeyboardInterrupt:
            print("\nVoice control deactivated. Goodbye!")
            break
        except Exception as e:
            print(f"\n Error: {str(e)}")

def try_listen():
    """
    Try to listen for voice commands using speech_recognition
    This is experimental and requires additional dependencies
    """
    try:
        import speech_recognition as sr
        
        # Check if we have a working microphone
        r = sr.Recognizer()
        
        with sr.Microphone() as source:
            print("\n  Container Farm Voice Control - Listening Mode ")
            print("=" * 50)
            print("Adjusting for ambient noise... please wait")
            r.adjust_for_ambient_noise(source, duration=1)
            print("Ready! Say something to control your farm (or 'exit' to quit)")
            print("=" * 50)
            
            while True:
                try:
                    print("\nListening...")
                    audio = r.listen(source, timeout=5, phrase_time_limit=5)
                    
                    print("Processing...")
                    text = r.recognize_google(audio)
                    print(f"I heard: {text}")
                    
                    result = process_command(text)
                    
                    if text.lower() in ["exit", "quit", "goodbye"]:
                        print("Voice control deactivated. Goodbye!")
                        break
                    
                    if result.get("success", False):
                        if "message" in result:
                            print(f"\n {result['message']}")
                        
                        # Print any additional details
                        for key, value in result.items():
                            if key not in ["success", "message"]:
                                print(f"  {key}: {value}")
                    else:
                        print(f"\n {result.get('message', 'Command failed')}")
                        
                except sr.WaitTimeoutError:
                    print("\nNo speech detected. Listening again...")
                except sr.UnknownValueError:
                    print("\nCould not understand audio. Please try again.")
                except sr.RequestError as e:
                    print(f"\n Speech recognition service error: {e}")
                    break
                except KeyboardInterrupt:
                    print("\nVoice control deactivated. Goodbye!")
                    break
                except Exception as e:
                    print(f"\n Error: {str(e)}")
                    
    except ImportError:
        print("\n Speech recognition module not installed.")
        print("To enable listening mode, install the required dependencies:")
        print("  pip3 install SpeechRecognition pyaudio")
        print("\nUsing text input mode instead.")
        simulate_voice_activation()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Container Farm Voice Control Simulator")
    parser.add_argument("--text", help="Process a single text command")
    parser.add_argument("--listen", action="store_true", help="Try to listen for voice commands (experimental)")
    
    args = parser.parse_args()
    
    if args.text:
        simulate_voice_activation(args.text)
    elif args.listen:
        try_listen()
    else:
        simulate_voice_activation()
