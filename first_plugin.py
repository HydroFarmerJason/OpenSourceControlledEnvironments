# plugins/led-blink/plugin.py
"""
LED Blink Plugin for OSCE
Simple plugin to demonstrate the plugin system
Blinks an LED on GPIO pin 23 (physical pin 16)
"""

import time
import threading
from datetime import datetime

class LEDBinkPlugin:
    """Simple LED control plugin"""
    
    def __init__(self, env):
        self.env = env
        self.name = "LED Blink"
        self.version = "1.0.0"
        self.author = "OSCE Team"
        self.description = "Control an LED for visual notifications"
        
        # Configuration
        self.led_pin = 23  # GPIO 23 (physical pin 16)
        self.enabled = False
        self.blink_thread = None
        self.running = False
        
        # Try to import GPIO
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.gpio_available = True
        except:
            self.gpio_available = False
            print(f"[{self.name}] GPIO not available - running in mock mode")
    
    def activate(self):
        """Called when plugin is activated"""
        print(f"[{self.name}] Activating plugin v{self.version}")
        
        if self.gpio_available:
            # Setup GPIO
            self.GPIO.setmode(self.GPIO.BCM)
            self.GPIO.setup(self.led_pin, self.GPIO.OUT)
            self.GPIO.output(self.led_pin, self.GPIO.LOW)
        
        # Add dashboard widget
        self.env.add_widget({
            'id': 'led_control',
            'name': 'LED Control',
            'html': self._get_widget_html(),
            'refresh': 5
        })
        
        # Add API endpoint
        self.env.add_api_route('/api/plugins/led/toggle', self.toggle_led)
        self.env.add_api_route('/api/plugins/led/blink', self.start_blink)
        self.env.add_api_route('/api/plugins/led/stop', self.stop_blink)
        
        self.enabled = True
        print(f"[{self.name}] Plugin activated!")
    
    def deactivate(self):
        """Called when plugin is deactivated"""
        print(f"[{self.name}] Deactivating plugin")
        
        # Stop any blinking
        self.stop_blink()
        
        # Turn off LED
        if self.gpio_available:
            self.GPIO.output(self.led_pin, self.GPIO.LOW)
            self.GPIO.cleanup(self.led_pin)
        
        self.enabled = False
    
    def toggle_led(self):
        """Toggle LED on/off"""
        if not self.gpio_available:
            return {'status': 'error', 'message': 'GPIO not available'}
        
        current_state = self.GPIO.input(self.led_pin)
        new_state = not current_state
        self.GPIO.output(self.led_pin, new_state)
        
        return {
            'status': 'success',
            'led_state': 'on' if new_state else 'off',
            'timestamp': datetime.now().isoformat()
        }
    
    def start_blink(self):
        """Start blinking the LED"""
        if self.running:
            return {'status': 'already_running'}
        
        self.running = True
        self.blink_thread = threading.Thread(target=self._blink_loop)
        self.blink_thread.daemon = True
        self.blink_thread.start()
        
        return {
            'status': 'started',
            'timestamp': datetime.now().isoformat()
        }
    
    def stop_blink(self):
        """Stop blinking the LED"""
        self.running = False
        if self.blink_thread:
            self.blink_thread.join(timeout=2)
        
        # Turn off LED
        if self.gpio_available:
            self.GPIO.output(self.led_pin, self.GPIO.LOW)
        
        return {
            'status': 'stopped',
            'timestamp': datetime.now().isoformat()
        }
    
    def _blink_loop(self):
        """Background thread for blinking"""
        while self.running:
            if self.gpio_available:
                # Turn on
                self.GPIO.output(self.led_pin, self.GPIO.HIGH)
                time.sleep(0.5)
                
                # Turn off
                self.GPIO.output(self.led_pin, self.GPIO.LOW)
                time.sleep(0.5)
            else:
                # Mock mode - just print
                print(f"[{self.name}] LED: ON")
                time.sleep(0.5)
                print(f"[{self.name}] LED: OFF")
                time.sleep(0.5)
    
    def _get_widget_html(self):
        """Generate dashboard widget HTML"""
        return '''
        <div class="plugin-widget" id="led-control-widget">
            <style>
                .led-indicator {
                    width: 30px;
                    height: 30px;
                    border-radius: 50%;
                    display: inline-block;
                    margin: 10px;
                    transition: all 0.3s;
                }
                .led-off {
                    background: #333;
                    box-shadow: 0 0 5px rgba(0,0,0,0.5);
                }
                .led-on {
                    background: #ff3333;
                    box-shadow: 0 0 20px #ff3333;
                }
                .led-controls button {
                    margin: 5px;
                    padding: 8px 16px;
                    background: #2e7d32;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    cursor: pointer;
                }
                .led-controls button:hover {
                    background: #1b5e20;
                }
            </style>
            
            <h3> LED Control</h3>
            <div class="led-indicator led-off" id="led-indicator"></div>
            
            <div class="led-controls">
                <button onclick="toggleLED()">Toggle</button>
                <button onclick="startBlink()">Start Blink</button>
                <button onclick="stopBlink()">Stop Blink</button>
            </div>
            
            <script>
                let blinking = false;
                
                function toggleLED() {
                    fetch('/api/plugins/led/toggle')
                        .then(r => r.json())
                        .then(data => {
                            if (data.led_state === 'on') {
                                document.getElementById('led-indicator').className = 'led-indicator led-on';
                            } else {
                                document.getElementById('led-indicator').className = 'led-indicator led-off';
                            }
                        });
                }
                
                function startBlink() {
                    fetch('/api/plugins/led/blink')
                        .then(r => r.json())
                        .then(data => {
                            if (data.status === 'started') {
                                blinking = true;
                                animateBlink();
                            }
                        });
                }
                
                function stopBlink() {
                    fetch('/api/plugins/led/stop')
                        .then(r => r.json())
                        .then(data => {
                            blinking = false;
                            document.getElementById('led-indicator').className = 'led-indicator led-off';
                        });
                }
                
                function animateBlink() {
                    if (!blinking) return;
                    
                    const indicator = document.getElementById('led-indicator');
                    if (indicator.className.includes('led-on')) {
                        indicator.className = 'led-indicator led-off';
                    } else {
                        indicator.className = 'led-indicator led-on';
                    }
                    
                    setTimeout(animateBlink, 500);
                }
            </script>
        </div>
        '''

# Plugin manifest
plugin_manifest = {
    "id": "led-blink",
    "name": "LED Blink",
    "version": "1.0.0",
    "description": "Control an LED for visual notifications",
    "author": "OSCE Team",
    "category": "Hardware Control",
    "hardware_required": ["GPIO"],
    "tags": ["led", "notification", "visual", "example"],
    "readme": """
# LED Blink Plugin

This plugin demonstrates basic hardware control in OSCE.

## Hardware Setup

1. Connect an LED to GPIO 23 (physical pin 16)
2. Use a 330Ω resistor in series
3. Connect the other end to GND

```
GPIO 23 (Pin 16) ---[330Ω]---[LED]--- GND (Pin 14)
```

## Features

- Toggle LED on/off
- Blink LED continuously
- Dashboard widget for control
- Works without GPIO (mock mode)

## API Endpoints

- `/api/plugins/led/toggle` - Toggle LED state
- `/api/plugins/led/blink` - Start blinking
- `/api/plugins/led/stop` - Stop blinking

Perfect for notifications or status indicators!
""",
    "install_notes": "Remember to connect an LED to GPIO 23 with a resistor!"
}

# Installation instructions to add to the main OSCE system
INSTALL_SNIPPET = """
# To install this plugin after OSCE is running:

# 1. Create plugin directory
mkdir -p ~/osce/plugins/led-blink

# 2. Download plugin
curl -o ~/osce/plugins/led-blink/plugin.py https://raw.githubusercontent.com/HydroFarmerJason/OpenSourceControlledEnvironments/main/plugins/led-blink/plugin.py

# 3. The plugin will auto-load, or restart OSCE
"""