# osce/hardware/mock_adapter.py
"""
Mock Hardware Adapter for OSCE
Enables testing, development, and education without physical hardware
Simulates realistic sensor readings and hardware behavior
"""

import random
import math
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
import json
import threading

from osce.hardware.hal import (
    HardwareAdapter, PinMode, SensorInfo, PlatformCapabilities
)


@dataclass
class MockSensor:
    """Simulated sensor with realistic behavior"""
    sensor_type: str
    base_value: float
    variation: float = 0.1
    trend: float = 0.0
    noise: float = 0.02
    response_time: float = 0.1
    failure_rate: float = 0.0
    
    def read(self) -> float:
        """Generate realistic sensor reading"""
        if random.random() < self.failure_rate:
            raise Exception(f"Mock sensor {self.sensor_type} failure")
            
        # Simulate response time
        time.sleep(self.response_time)
        
        # Calculate value with variations
        time_factor = math.sin(time.time() / 3600) * self.variation  # Hourly variation
        trend_factor = self.trend * (time.time() % 3600) / 3600
        noise_factor = random.gauss(0, self.noise)
        
        return self.base_value + time_factor + trend_factor + noise_factor


@dataclass 
class MockActuator:
    """Simulated actuator with state tracking"""
    actuator_type: str
    state: bool = False
    pwm_value: float = 0.0
    response_time: float = 0.05
    power_consumption: float = 0.0  # Watts when on
    
    def set_state(self, state: bool):
        """Set actuator state with delay"""
        time.sleep(self.response_time)
        self.state = state
        
    def set_pwm(self, value: float):
        """Set PWM value"""
        time.sleep(self.response_time)
        self.pwm_value = max(0.0, min(1.0, value))


class MockEnvironment:
    """Simulates a complete growing environment"""
    
    def __init__(self, scenario: str = "greenhouse"):
        self.scenario = scenario
        self.start_time = datetime.now()
        self.environment_state = self._initialize_scenario(scenario)
        self.running = True
        
        # Start environment simulation thread
        self.sim_thread = threading.Thread(target=self._simulate_environment)
        self.sim_thread.daemon = True
        self.sim_thread.start()
        
    def _initialize_scenario(self, scenario: str) -> Dict[str, Any]:
        """Initialize environment based on scenario"""
        scenarios = {
            "greenhouse": {
                "temperature": 22.0,
                "humidity": 65.0,
                "co2": 400.0,
                "light_level": 0.0,
                "soil_moisture": 45.0,
                "ph": 6.5,
                "ec": 1.2,
                "water_level": 80.0
            },
            "hydroponics": {
                "temperature": 24.0,
                "humidity": 70.0,
                "co2": 450.0,
                "light_level": 0.0,
                "ph": 5.8,
                "ec": 2.0,
                "water_temp": 20.0,
                "dissolved_oxygen": 8.0
            },
            "mushroom": {
                "temperature": 18.0,
                "humidity": 85.0,
                "co2": 800.0,
                "light_level": 0.0
            },
            "classroom": {
                "temperature": 21.0,
                "humidity": 50.0,
                "co2": 450.0,
                "light_level": 0.0,
                "soil_moisture": 40.0
            }
        }
        
        return scenarios.get(scenario, scenarios["greenhouse"]).copy()
        
    def _simulate_environment(self):
        """Continuously update environment state"""
        while self.running:
            current_hour = datetime.now().hour
            
            # Simulate day/night cycle for light
            if 6 <= current_hour < 18:  # Day time
                target_light = 800.0  # lux
            else:
                target_light = 0.0
                
            # Gradually adjust light level
            current_light = self.environment_state.get("light_level", 0)
            light_diff = target_light - current_light
            self.environment_state["light_level"] = current_light + (light_diff * 0.1)
            
            # Temperature follows light with delay
            if self.environment_state["light_level"] > 400:
                target_temp = 26.0
            else:
                target_temp = 20.0
                
            current_temp = self.environment_state.get("temperature", 22)
            temp_diff = target_temp - current_temp
            self.environment_state["temperature"] = current_temp + (temp_diff * 0.05)
            
            # Humidity inversely related to temperature
            target_humidity = 80 - (self.environment_state["temperature"] - 20) * 3
            current_humidity = self.environment_state.get("humidity", 65)
            humidity_diff = target_humidity - current_humidity
            self.environment_state["humidity"] = current_humidity + (humidity_diff * 0.05)
            
            # CO2 consumption during photosynthesis
            if self.environment_state["light_level"] > 200:
                self.environment_state["co2"] = max(350, self.environment_state.get("co2", 400) - 0.5)
            else:
                self.environment_state["co2"] = min(600, self.environment_state.get("co2", 400) + 0.2)
            
            # Soil moisture decreases over time
            if "soil_moisture" in self.environment_state:
                self.environment_state["soil_moisture"] = max(20, 
                    self.environment_state["soil_moisture"] - 0.1)
            
            time.sleep(1)  # Update every second
            
    def get_value(self, sensor_type: str) -> float:
        """Get current environment value"""
        return self.environment_state.get(sensor_type, 0.0)
        
    def apply_actuator_effect(self, actuator_type: str, state: Any):
        """Apply actuator effects to environment"""
        if actuator_type == "pump" and state:
            if "soil_moisture" in self.environment_state:
                self.environment_state["soil_moisture"] = min(80, 
                    self.environment_state["soil_moisture"] + 5)
        elif actuator_type == "fan" and state:
            # Fan reduces temperature and humidity
            self.environment_state["temperature"] *= 0.98
            self.environment_state["humidity"] *= 0.95
        elif actuator_type == "heater" and state:
            self.environment_state["temperature"] += 0.5
        elif actuator_type == "humidifier" and state:
            self.environment_state["humidity"] = min(95, 
                self.environment_state["humidity"] + 2)
                
    def stop(self):
        """Stop environment simulation"""
        self.running = False


class MockHardwareAdapter(HardwareAdapter):
    """Mock adapter for testing and education"""
    
    def __init__(self, platform: str = "mock_pi", scenario: str = "greenhouse", 
                 failure_mode: bool = False):
        self.platform = platform
        self.scenario = scenario
        self.failure_mode = failure_mode
        self.initialized = False
        
        # Pin configurations
        self.pin_modes: Dict[int, PinMode] = {}
        self.pin_values: Dict[int, Any] = {}
        self.pwm_instances: Dict[int, float] = {}
        
        # Simulated sensors and actuators
        self.sensors: Dict[int, MockSensor] = {}
        self.actuators: Dict[int, MockActuator] = {}
        self.i2c_devices: Dict[int, SensorInfo] = {}
        
        # Environment simulation
        self.environment: Optional[MockEnvironment] = None
        
        # Educational mode features
        self.log_actions = True
        self.action_log: List[str] = []
        
    def initialize(self) -> bool:
        """Initialize mock hardware"""
        try:
            # Start environment simulation
            self.environment = MockEnvironment(self.scenario)
            
            # Pre-configure common sensors based on scenario
            self._setup_default_sensors()
            
            self.initialized = True
            self._log(f"Mock {self.platform} initialized with {self.scenario} scenario")
            return True
            
        except Exception as e:
            self._log(f"Failed to initialize: {e}")
            return False
            
    def _setup_default_sensors(self):
        """Setup default sensors for scenario"""
        if self.scenario == "greenhouse":
            # Temperature/Humidity sensor (DHT22 on pin 4)
            self.sensors[4] = MockSensor("dht22_temp", 22.0, variation=2.0)
            
            # Soil moisture sensor (analog on pin A0 - use 100)
            self.sensors[100] = MockSensor("soil_moisture", 45.0, variation=5.0, trend=-0.5)
            
            # Light sensor (I2C at 0x23)
            self.i2c_devices[0x23] = SensorInfo(
                sensor_type="BH1750",
                name="Light Sensor",
                pins={"sda": 2, "scl": 3},
                protocol="i2c",
                address=0x23
            )
            
            # CO2 sensor (I2C at 0x68)
            self.i2c_devices[0x68] = SensorInfo(
                sensor_type="SCD30",
                name="CO2 Sensor", 
                pins={"sda": 2, "scl": 3},
                protocol="i2c",
                address=0x68
            )
            
    def cleanup(self):
        """Cleanup mock resources"""
        if self.environment:
            self.environment.stop()
        self._log("Mock hardware cleaned up")
        
    def get_capabilities(self) -> PlatformCapabilities:
        """Return mock platform capabilities"""
        capabilities_map = {
            "mock_pi": PlatformCapabilities(
                name="Mock Raspberry Pi",
                digital_pins=list(range(2, 28)),
                analog_pins=[],  # Pi has no analog
                pwm_pins=[12, 13, 18, 19],
                i2c_support=True,
                spi_support=True,
                uart_support=True,
                wifi_support=True,
                bluetooth_support=True
            ),
            "mock_arduino": PlatformCapabilities(
                name="Mock Arduino Uno",
                digital_pins=list(range(2, 14)),
                analog_pins=list(range(100, 106)),  # A0-A5 as 100-105
                pwm_pins=[3, 5, 6, 9, 10, 11],
                i2c_support=True,
                spi_support=True,
                uart_support=True,
                wifi_support=False,
                bluetooth_support=False
            ),
            "mock_esp32": PlatformCapabilities(
                name="Mock ESP32",
                digital_pins=list(range(0, 34)),
                analog_pins=[32, 33, 34, 35, 36, 39],
                pwm_pins=list(range(0, 34)),
                i2c_support=True,
                spi_support=True,
                uart_support=True,
                wifi_support=True,
                bluetooth_support=True
            )
        }
        
        return capabilities_map.get(self.platform, capabilities_map["mock_pi"])
        
    def setup_pin(self, pin: int, mode: PinMode) -> bool:
        """Configure a pin"""
        if self.failure_mode and random.random() < 0.1:
            self._log(f"SIMULATED FAILURE: Pin {pin} setup failed")
            return False
            
        self.pin_modes[pin] = mode
        
        # Initialize pin value based on mode
        if mode == PinMode.INPUT:
            self.pin_values[pin] = False
        elif mode == PinMode.OUTPUT:
            self.pin_values[pin] = False
        elif mode == PinMode.ANALOG:
            self.pin_values[pin] = 0.5
            
        self._log(f"Pin {pin} configured as {mode.value}")
        return True
        
    def digital_read(self, pin: int) -> bool:
        """Read digital pin"""
        if pin in self.sensors:
            # Sensor pin - return based on threshold
            value = self.sensors[pin].read()
            return value > 0.5
        else:
            # Regular digital pin
            return self.pin_values.get(pin, False)
            
    def digital_write(self, pin: int, value: bool):
        """Write digital pin"""
        self.pin_values[pin] = value
        self._log(f"Digital write pin {pin}: {value}")
        
        # Check if this controls an actuator
        if pin in self.actuators:
            self.actuators[pin].set_state(value)
            if self.environment:
                actuator_type = self.actuators[pin].actuator_type
                self.environment.apply_actuator_effect(actuator_type, value)
                
    def analog_read(self, pin: int) -> float:
        """Read analog value"""
        if pin in self.sensors:
            # Simulated sensor reading
            sensor = self.sensors[pin]
            
            # Map environment values to sensor readings
            if sensor.sensor_type == "soil_moisture":
                value = self.environment.get_value("soil_moisture") / 100.0
            elif sensor.sensor_type == "light":
                value = self.environment.get_value("light_level") / 1000.0
            else:
                value = sensor.read() / sensor.base_value
                
            return max(0.0, min(1.0, value))
        else:
            # Random analog value
            return self.pin_values.get(pin, random.random())
            
    def pwm_write(self, pin: int, duty_cycle: float):
        """Write PWM value"""
        self.pwm_instances[pin] = duty_cycle
        self._log(f"PWM write pin {pin}: {duty_cycle:.2%}")
        
        if pin in self.actuators:
            self.actuators[pin].set_pwm(duty_cycle)
            
    def i2c_scan(self) -> List[int]:
        """Return mock I2C devices"""
        devices = list(self.i2c_devices.keys())
        self._log(f"I2C scan found devices: {[hex(d) for d in devices]}")
        return devices
        
    def discover_sensors(self) -> List[SensorInfo]:
        """Discover mock sensors"""
        discovered = []
        
        # Add configured I2C sensors
        discovered.extend(self.i2c_devices.values())
        
        # Add some 1-Wire temperature sensors
        for i in range(2):
            discovered.append(SensorInfo(
                sensor_type="DS18B20",
                name=f"Temperature-{1000+i}",
                pins={"data": 4},
                protocol="1-wire"
            ))
            
        self._log(f"Discovered {len(discovered)} sensors")
        return discovered
        
    def _log(self, message: str):
        """Log actions for educational purposes"""
        if self.log_actions:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            log_entry = f"[{timestamp}] {message}"
            self.action_log.append(log_entry)
            print(f"MOCK: {log_entry}")
            
    def get_action_log(self) -> List[str]:
        """Get log of all hardware actions"""
        return self.action_log.copy()
        
    def inject_failure(self, component: str, failure_type: str):
        """Inject a failure for testing"""
        self._log(f"INJECTED FAILURE: {component} - {failure_type}")
        
        if component == "sensor" and failure_type == "timeout":
            # Make next sensor read timeout
            for sensor in self.sensors.values():
                sensor.response_time = 5.0
        elif component == "i2c" and failure_type == "bus_error":
            # Clear I2C devices
            self.i2c_devices.clear()
            
    def set_environment_value(self, parameter: str, value: float):
        """Manually set environment parameter for testing"""
        if self.environment:
            self.environment.environment_state[parameter] = value
            self._log(f"Environment {parameter} set to {value}")
            
    def create_learning_scenario(self, lesson: str):
        """Create specific scenarios for education"""
        scenarios = {
            "sensor_failure": lambda: self.inject_failure("sensor", "timeout"),
            "overheating": lambda: self.set_environment_value("temperature", 35),
            "drought": lambda: self.set_environment_value("soil_moisture", 15),
            "power_outage": lambda: self.initialized == False,
            "network_loss": lambda: self._log("SIMULATED: Network connection lost")
        }
        
        if lesson in scenarios:
            scenarios[lesson]()
            self._log(f"Learning scenario '{lesson}' activated")


# Educational wrapper for interactive learning
class InteractiveMockAdapter(MockHardwareAdapter):
    """Interactive mock adapter for educational use"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student_predictions: Dict[str, Any] = {}
        self.quiz_mode = False
        
    def predict_reading(self, sensor_type: str, prediction: float):
        """Student predicts sensor reading"""
        self.student_predictions[sensor_type] = {
            "prediction": prediction,
            "timestamp": datetime.now()
        }
        
    def check_prediction(self, sensor_type: str) -> Dict[str, Any]:
        """Check student prediction against actual"""
        if sensor_type not in self.student_predictions:
            return {"error": "No prediction made"}
            
        actual = self.environment.get_value(sensor_type)
        predicted = self.student_predictions[sensor_type]["prediction"]
        error = abs(actual - predicted)
        
        return {
            "actual": actual,
            "predicted": predicted,
            "error": error,
            "accuracy": max(0, 100 - error),
            "feedback": self._generate_feedback(sensor_type, error)
        }
        
    def _generate_feedback(self, sensor_type: str, error: float) -> str:
        """Generate educational feedback"""
        if error < 1:
            return "Excellent! Very close prediction."
        elif error < 5:
            return "Good job! You understand the general range."
        elif error < 10:
            return "Not bad. Consider the environmental factors affecting this sensor."
        else:
            return f"Let's review how {sensor_type} sensors work and typical ranges."
            
    def start_quiz(self, topic: str):
        """Start an interactive quiz"""
        self.quiz_mode = True
        self._log(f"Starting quiz on topic: {topic}")
        
        # Create quiz scenarios
        if topic == "sensor_types":
            return {
                "question": "What sensor would you use to measure soil water content?",
                "options": ["DHT22", "Capacitive Moisture", "DS18B20", "BH1750"],
                "hint": "Think about what property changes with water content"
            }
            
    def visualize_data(self) -> str:
        """Generate ASCII visualization of current state"""
        temp = self.environment.get_value("temperature")
        humidity = self.environment.get_value("humidity")
        light = self.environment.get_value("light_level")
        
        viz = f"""
        === Current Environment ===
        Temperature: {'█' * int(temp/2)} {temp:.1f}°C
        Humidity:    {'█' * int(humidity/5)} {humidity:.1f}%
        Light:       {'█' * int(light/100)} {light:.0f} lux
        
        Actuators:
        """
        
        for pin, actuator in self.actuators.items():
            state = "ON " if actuator.state else "OFF"
            viz += f"  {actuator.actuator_type}: [{state}]\n"
            
        return viz


if __name__ == "__main__":
    # Example: Using mock adapter for testing
    mock = MockHardwareAdapter(platform="mock_pi", scenario="greenhouse")
    mock.initialize()
    
    # Setup a sensor pin
    mock.setup_pin(4, PinMode.INPUT)
    
    # Read temperature (will vary realistically)
    for i in range(5):
        temp = mock.analog_read(4) * 50  # Convert to celsius
        print(f"Temperature reading {i}: {temp:.2f}°C")
        time.sleep(1)
        
    # Control an actuator
    mock.actuators[22] = MockActuator("pump")
    mock.setup_pin(22, PinMode.OUTPUT)
    mock.digital_write(22, True)  # Turn on pump
    
    # Check soil moisture increased
    time.sleep(2)
    moisture = mock.environment.get_value("soil_moisture")
    print(f"Soil moisture after watering: {moisture:.1f}%")
    
    # Educational mode
    edu_mock = InteractiveMockAdapter(scenario="classroom")
    edu_mock.initialize()
    
    # Student/educator predicts temperature
    edu_mock.predict_reading("temperature", 23.5)
    result = edu_mock.check_prediction("temperature")
    print(f"Prediction result: {result}")
    
    # Show visualization
    print(edu_mock.visualize_data())
