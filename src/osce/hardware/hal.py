# osce/hardware/hal.py
"""
Hardware Abstraction Layer (HAL) for OSCE
Enables OSCE to run on any hardware platform through adapters
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import importlib
import json
import logging

logger = logging.getLogger(__name__)


class PinMode(Enum):
    """Pin configuration modes"""
    INPUT = "input"
    OUTPUT = "output"
    PWM = "pwm"
    ANALOG = "analog"
    I2C = "i2c"
    SPI = "spi"
    UART = "uart"


@dataclass
class SensorInfo:
    """Information about a detected sensor"""
    sensor_type: str
    name: str
    pins: Dict[str, int]
    protocol: str
    address: Optional[int] = None


@dataclass
class PlatformCapabilities:
    """What a hardware platform can do"""
    name: str
    digital_pins: List[int]
    analog_pins: List[int]
    pwm_pins: List[int]
    i2c_support: bool
    spi_support: bool
    uart_support: bool
    wifi_support: bool
    bluetooth_support: bool


class HardwareAdapter(ABC):
    """Base adapter for all hardware platforms"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the hardware platform"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Cleanup resources"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> PlatformCapabilities:
        """Get platform capabilities"""
        pass
    
    @abstractmethod
    def setup_pin(self, pin: int, mode: PinMode) -> bool:
        """Configure a pin"""
        pass
    
    @abstractmethod
    def digital_read(self, pin: int) -> bool:
        """Read digital pin state"""
        pass
    
    @abstractmethod
    def digital_write(self, pin: int, value: bool):
        """Write digital pin state"""
        pass
    
    @abstractmethod
    def analog_read(self, pin: int) -> float:
        """Read analog value (0.0-1.0)"""
        pass
    
    @abstractmethod
    def pwm_write(self, pin: int, duty_cycle: float):
        """Write PWM duty cycle (0.0-1.0)"""
        pass
    
    @abstractmethod
    def i2c_scan(self) -> List[int]:
        """Scan for I2C devices, return addresses"""
        pass
    
    @abstractmethod
    def discover_sensors(self) -> List[SensorInfo]:
        """Auto-discover connected sensors"""
        pass


class RaspberryPiAdapter(HardwareAdapter):
    """Adapter for Raspberry Pi"""
    
    def __init__(self):
        self.GPIO = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize Raspberry Pi GPIO"""
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BCM)
            self.GPIO.setwarnings(False)
            self.initialized = True
            logger.info("Raspberry Pi GPIO initialized")
            return True
        except ImportError:
            logger.error("RPi.GPIO not available")
            return False
    
    def cleanup(self):
        """Cleanup GPIO resources"""
        if self.GPIO and self.initialized:
            self.GPIO.cleanup()
            
    def get_capabilities(self) -> PlatformCapabilities:
        """Get Raspberry Pi capabilities"""
        return PlatformCapabilities(
            name="Raspberry Pi",
            digital_pins=list(range(2, 28)),  # GPIO 2-27
            analog_pins=[],  # No built-in analog
            pwm_pins=[12, 13, 18, 19],  # Hardware PWM pins
            i2c_support=True,
            spi_support=True,
            uart_support=True,
            wifi_support=True,  # Pi 3/4/Zero W
            bluetooth_support=True
        )
    
    def setup_pin(self, pin: int, mode: PinMode) -> bool:
        """Configure a GPIO pin"""
        if not self.initialized:
            return False
            
        try:
            if mode == PinMode.INPUT:
                self.GPIO.setup(pin, self.GPIO.IN, pull_up_down=self.GPIO.PUD_DOWN)
            elif mode == PinMode.OUTPUT:
                self.GPIO.setup(pin, self.GPIO.OUT)
            elif mode == PinMode.PWM:
                self.GPIO.setup(pin, self.GPIO.OUT)
                # PWM setup handled in pwm_write
            return True
        except Exception as e:
            logger.error(f"Failed to setup pin {pin}: {e}")
            return False
    
    def digital_read(self, pin: int) -> bool:
        """Read digital pin state"""
        if not self.initialized:
            return False
        return bool(self.GPIO.input(pin))
    
    def digital_write(self, pin: int, value: bool):
        """Write digital pin state"""
        if not self.initialized:
            return
        self.GPIO.output(pin, self.GPIO.HIGH if value else self.GPIO.LOW)
    
    def analog_read(self, pin: int) -> float:
        """Raspberry Pi doesn't have built-in analog"""
        raise NotImplementedError("Use external ADC for analog input")
    
    def pwm_write(self, pin: int, duty_cycle: float):
        """Write PWM duty cycle"""
        if not self.initialized:
            return
        # Create PWM instance if not exists
        if not hasattr(self, f'_pwm_{pin}'):
            pwm = self.GPIO.PWM(pin, 1000)  # 1kHz
            pwm.start(0)
            setattr(self, f'_pwm_{pin}', pwm)
        
        pwm = getattr(self, f'_pwm_{pin}')
        pwm.ChangeDutyCycle(duty_cycle * 100)
    
    def i2c_scan(self) -> List[int]:
        """Scan for I2C devices"""
        devices = []
        try:
            import smbus
            bus = smbus.SMBus(1)  # I2C bus 1
            
            for address in range(0x03, 0x78):
                try:
                    bus.read_byte(address)
                    devices.append(address)
                except:
                    pass
                    
            logger.info(f"Found I2C devices at: {[hex(d) for d in devices]}")
        except Exception as e:
            logger.error(f"I2C scan failed: {e}")
            
        return devices
    
    def discover_sensors(self) -> List[SensorInfo]:
        """Auto-discover connected sensors"""
        sensors = []
        
        # Check 1-Wire for DS18B20 temperature sensors
        try:
            import glob
            w1_devices = glob.glob('/sys/bus/w1/devices/28-*')
            for device in w1_devices:
                sensor_id = device.split('/')[-1]
                sensors.append(SensorInfo(
                    sensor_type='DS18B20',
                    name=f'Temperature-{sensor_id[-4:]}',
                    pins={'data': 4},  # Default 1-Wire pin
                    protocol='1-wire'
                ))
        except:
            pass
        
        # Check I2C devices
        i2c_devices = self.i2c_scan()
        
        # Common I2C sensor addresses
        i2c_sensors = {
            0x76: ('BME280', 'Temp/Humidity/Pressure'),
            0x77: ('BMP280', 'Temp/Pressure'),
            0x23: ('BH1750', 'Light Sensor'),
            0x40: ('HTU21D', 'Temp/Humidity'),
            0x5A: ('MLX90614', 'IR Temperature'),
            0x68: ('MPU6050', 'Accelerometer/Gyro'),
        }
        
        for addr in i2c_devices:
            if addr in i2c_sensors:
                sensor_type, name = i2c_sensors[addr]
                sensors.append(SensorInfo(
                    sensor_type=sensor_type,
                    name=name,
                    pins={'sda': 2, 'scl': 3},
                    protocol='i2c',
                    address=addr
                ))
        
        return sensors


class ESP32Adapter(HardwareAdapter):
    """Adapter for ESP32 via network API"""
    
    def __init__(self, ip_address: str, port: int = 80):
        self.base_url = f"http://{ip_address}:{port}/api"
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize ESP32 connection"""
        try:
            import requests
            response = requests.get(f"{self.base_url}/status", timeout=5)
            if response.status_code == 200:
                self.initialized = True
                logger.info(f"ESP32 connected at {self.base_url}")
                return True
        except Exception as e:
            logger.error(f"Failed to connect to ESP32: {e}")
        return False
    
    def cleanup(self):
        """No cleanup needed for network adapter"""
        pass
    
    def get_capabilities(self) -> PlatformCapabilities:
        """Get ESP32 capabilities"""
        return PlatformCapabilities(
            name="ESP32",
            digital_pins=list(range(0, 34)),
            analog_pins=[32, 33, 34, 35, 36, 39],  # ADC1 pins
            pwm_pins=list(range(0, 34)),  # All pins support PWM
            i2c_support=True,
            spi_support=True,
            uart_support=True,
            wifi_support=True,
            bluetooth_support=True
        )
    
    def _api_call(self, endpoint: str, method: str = 'GET', data: dict = None):
        """Make API call to ESP32"""
        import requests
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url)
            elif method == 'POST':
                response = requests.post(url, json=data)
            
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.error(f"API call failed: {e}")
        return None
    
    def setup_pin(self, pin: int, mode: PinMode) -> bool:
        """Configure pin via API"""
        result = self._api_call('pin/setup', 'POST', {
            'pin': pin,
            'mode': mode.value
        })
        return result is not None
    
    def digital_read(self, pin: int) -> bool:
        """Read digital pin via API"""
        result = self._api_call(f'pin/{pin}/digital')
        return result.get('value', False) if result else False
    
    def digital_write(self, pin: int, value: bool):
        """Write digital pin via API"""
        self._api_call('pin/digital', 'POST', {
            'pin': pin,
            'value': value
        })
    
    def analog_read(self, pin: int) -> float:
        """Read analog value via API"""
        result = self._api_call(f'pin/{pin}/analog')
        return result.get('value', 0.0) if result else 0.0
    
    def pwm_write(self, pin: int, duty_cycle: float):
        """Write PWM via API"""
        self._api_call('pin/pwm', 'POST', {
            'pin': pin,
            'duty_cycle': duty_cycle
        })
    
    def i2c_scan(self) -> List[int]:
        """Scan I2C devices via API"""
        result = self._api_call('i2c/scan')
        return result.get('devices', []) if result else []
    
    def discover_sensors(self) -> List[SensorInfo]:
        """Discover sensors via API"""
        result = self._api_call('sensors/discover')
        sensors = []
        
        if result and 'sensors' in result:
            for sensor_data in result['sensors']:
                sensors.append(SensorInfo(**sensor_data))
        
        return sensors


class ArduinoAdapter(HardwareAdapter):
    """Adapter for Arduino via serial communication"""
    
    def __init__(self, port: str, baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial = None
        self.initialized = False
        
    def initialize(self) -> bool:
        """Initialize Arduino connection"""
        try:
            import serial
            self.serial = serial.Serial(self.port, self.baudrate, timeout=1)
            # Wait for Arduino to reset
            import time
            time.sleep(2)
            
            # Send handshake
            self._send_command("HELLO")
            response = self._read_response()
            
            if response and response.get('status') == 'ready':
                self.initialized = True
                logger.info(f"Arduino connected on {self.port}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to connect to Arduino: {e}")
        return False
    
    def cleanup(self):
        """Close serial connection"""
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def get_capabilities(self) -> PlatformCapabilities:
        """Get Arduino capabilities (Uno example)"""
        return PlatformCapabilities(
            name="Arduino Uno",
            digital_pins=list(range(2, 14)),
            analog_pins=[0, 1, 2, 3, 4, 5],  # A0-A5
            pwm_pins=[3, 5, 6, 9, 10, 11],
            i2c_support=True,
            spi_support=True,
            uart_support=True,
            wifi_support=False,
            bluetooth_support=False
        )
    
    def _send_command(self, cmd: str, params: dict = None):
        """Send command to Arduino"""
        if not self.serial or not self.serial.is_open:
            return
            
        command = {'cmd': cmd}
        if params:
            command.update(params)
            
        self.serial.write((json.dumps(command) + '\n').encode())
    
    def _read_response(self) -> dict:
        """Read response from Arduino"""
        if not self.serial or not self.serial.is_open:
            return None
            
        try:
            line = self.serial.readline().decode().strip()
            if line:
                return json.loads(line)
        except Exception as e:
            logger.error(f"Failed to read response: {e}")
        return None
    
    # Implement remaining methods similar to ESP32...
    def setup_pin(self, pin: int, mode: PinMode) -> bool:
        self._send_command("SETUP_PIN", {'pin': pin, 'mode': mode.value})
        response = self._read_response()
        return response and response.get('status') == 'ok'
    
    def digital_read(self, pin: int) -> bool:
        self._send_command("DIGITAL_READ", {'pin': pin})
        response = self._read_response()
        return response.get('value', False) if response else False
    
    def digital_write(self, pin: int, value: bool):
        self._send_command("DIGITAL_WRITE", {'pin': pin, 'value': value})
    
    def analog_read(self, pin: int) -> float:
        self._send_command("ANALOG_READ", {'pin': pin})
        response = self._read_response()
        if response and 'value' in response:
            # Convert 10-bit ADC to 0.0-1.0
            return response['value'] / 1023.0
        return 0.0
    
    def pwm_write(self, pin: int, duty_cycle: float):
        # Convert 0.0-1.0 to 0-255
        value = int(duty_cycle * 255)
        self._send_command("PWM_WRITE", {'pin': pin, 'value': value})
    
    def i2c_scan(self) -> List[int]:
        self._send_command("I2C_SCAN")
        response = self._read_response()
        return response.get('devices', []) if response else []
    
    def discover_sensors(self) -> List[SensorInfo]:
        self._send_command("DISCOVER_SENSORS")
        response = self._read_response()
        sensors = []
        
        if response and 'sensors' in response:
            for sensor_data in response['sensors']:
                sensors.append(SensorInfo(**sensor_data))
        
        return sensors


class HardwareManager:
    """Manages multiple hardware adapters"""
    
    def __init__(self):
        self.adapters: Dict[str, HardwareAdapter] = {}
        self.primary_adapter: Optional[str] = None
        
    def add_adapter(self, name: str, adapter: HardwareAdapter) -> bool:
        """Add a hardware adapter"""
        if adapter.initialize():
            self.adapters[name] = adapter
            if not self.primary_adapter:
                self.primary_adapter = name
            logger.info(f"Added hardware adapter: {name}")
            return True
        return False
    
    def remove_adapter(self, name: str):
        """Remove and cleanup adapter"""
        if name in self.adapters:
            self.adapters[name].cleanup()
            del self.adapters[name]
            if self.primary_adapter == name:
                self.primary_adapter = next(iter(self.adapters), None)
    
    def get_adapter(self, name: str = None) -> Optional[HardwareAdapter]:
        """Get adapter by name or primary adapter"""
        if name:
            return self.adapters.get(name)
        elif self.primary_adapter:
            return self.adapters.get(self.primary_adapter)
        return None
    
    def discover_all_sensors(self) -> Dict[str, List[SensorInfo]]:
        """Discover sensors on all adapters"""
        all_sensors = {}
        for name, adapter in self.adapters.items():
            sensors = adapter.discover_sensors()
            if sensors:
                all_sensors[name] = sensors
        return all_sensors
    
    def auto_detect_hardware(self) -> List[str]:
        """Auto-detect available hardware platforms"""
        detected = []
        
        # Try Raspberry Pi
        try:
            pi = RaspberryPiAdapter()
            if self.add_adapter("raspberry_pi", pi):
                detected.append("raspberry_pi")
        except:
            pass
        
        # Try local Arduino ports
        try:
            import serial.tools.list_ports
            for port in serial.tools.list_ports.comports():
                if "Arduino" in port.description or "CH340" in port.description:
                    arduino = ArduinoAdapter(port.device)
                    if self.add_adapter(f"arduino_{port.device}", arduino):
                        detected.append(f"arduino_{port.device}")
        except:
            pass
        
        # Try ESP32 on local network (mDNS)
        # This would scan for ESP32 devices advertising themselves
        
        return detected


# Example usage:
if __name__ == "__main__":
    # Create hardware manager
    hw_manager = HardwareManager()
    
    # Auto-detect available hardware
    detected = hw_manager.auto_detect_hardware()
    print(f"Detected hardware: {detected}")
    
    # Add ESP32 node manually
    esp32 = ESP32Adapter("192.168.1.100")
    hw_manager.add_adapter("greenhouse_esp32", esp32)
    
    # Discover all sensors
    all_sensors = hw_manager.discover_all_sensors()
    for adapter_name, sensors in all_sensors.items():
        print(f"\nSensors on {adapter_name}:")
        for sensor in sensors:
            print(f"  - {sensor.name} ({sensor.sensor_type}) on pins {sensor.pins}")
    
    # Use sensors from any adapter
    pi_adapter = hw_manager.get_adapter("raspberry_pi")
    if pi_adapter:
        pi_adapter.setup_pin(22, PinMode.OUTPUT)
        pi_adapter.digital_write(22, True)  # Turn on relay
    
    esp_adapter = hw_manager.get_adapter("greenhouse_esp32")
    if esp_adapter:
        temp = esp_adapter.analog_read(34)  # Read analog sensor
        print(f"ESP32 temperature: {temp}")
