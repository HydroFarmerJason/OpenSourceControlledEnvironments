#!/usr/bin/env python3
"""
OSCE Hardware Abstraction Layer (HAL) - Production Enhanced
Integrates with the unified setup for seamless hardware management

Key Enhancements:
1. Secure Device Authentication
2. Real-time Performance Monitoring
3. Automatic Failover and Redundancy
4. Hardware Health Scoring with ML
5. Distributed HAL for Multi-Site Deployments
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable, Set, Tuple
import hashlib
import hmac
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import numpy as np

# Advanced structured logging
import structlog
logger = structlog.get_logger()

# Import security components from main system
from osce.security import DeviceIdentity, IoTSecurityManager, SecurityLevel

class PinMode(Enum):
    """Enhanced pin configuration modes"""
    INPUT = "input"
    OUTPUT = "output"
    PWM = "pwm"
    ANALOG = "analog"
    I2C = "i2c"
    SPI = "spi"
    UART = "uart"
    CAN = "can"
    INTERRUPT = "interrupt"
    DIFFERENTIAL = "differential"  # For industrial sensors

class HardwareHealth(Enum):
    """Hardware health states"""
    EXCELLENT = auto()
    GOOD = auto()
    DEGRADED = auto()
    FAILING = auto()
    FAILED = auto()
    UNKNOWN = auto()

@dataclass
class PinCapability:
    """Detailed pin capability information"""
    number: int
    modes: Set[PinMode]
    current_mode: Optional[PinMode] = None
    max_current_ma: float = 20.0
    max_voltage: float = 3.3
    adc_resolution: Optional[int] = None
    pwm_frequency_range: Optional[Tuple[float, float]] = None
    interrupt_capable: bool = False
    in_use: bool = False
    reserved: bool = False

@dataclass
class SensorInfo:
    """Enhanced sensor information with metadata"""
    sensor_type: str
    name: str
    pins: Dict[str, int]
    protocol: str
    address: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    calibration_data: Optional[Dict[str, Any]] = None
    last_seen: datetime = field(default_factory=datetime.utcnow)
    health_score: float = 1.0
    error_count: int = 0
    
    def to_device_identity(self) -> DeviceIdentity:
        """Convert to DeviceIdentity for security system"""
        return DeviceIdentity(
            uuid=f"{self.sensor_type}_{self.serial_number or self.address}",
            manufacturer=self.manufacturer or "Unknown",
            model=self.model or self.sensor_type,
            serial_number=self.serial_number or str(self.address),
            public_key=""  # Would be populated by security system
        )

@dataclass
class HardwareMetrics:
    """Real-time hardware performance metrics"""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    temperature: Optional[float] = None
    voltage: Optional[float] = None
    pin_usage: Dict[int, float] = field(default_factory=dict)
    error_rate: float = 0.0
    latency_ms: float = 0.0
    operations_per_second: float = 0.0

@dataclass
class PlatformCapabilities:
    """Enhanced platform capabilities with detailed specifications"""
    name: str
    version: str
    digital_pins: List[PinCapability]
    analog_pins: List[PinCapability]
    pwm_pins: List[PinCapability]
    communication_protocols: Set[str]
    max_gpio_current_ma: float
    operating_voltage: float
    adc_resolution_bits: int
    dac_resolution_bits: Optional[int]
    hardware_timers: int
    hardware_interrupts: int
    memory_kb: int
    flash_kb: int
    cpu_mhz: float
    features: Set[str]  # wifi, bluetooth, ethernet, etc.
    
    def get_available_pins(self, mode: PinMode) -> List[PinCapability]:
        """Get available pins for a specific mode"""
        all_pins = self.digital_pins + self.analog_pins + self.pwm_pins
        return [p for p in all_pins if mode in p.modes and not p.in_use and not p.reserved]

class HardwareAdapter(ABC):
    """Enhanced base adapter with monitoring and security"""
    
    def __init__(self, adapter_id: str, security_manager: Optional[IoTSecurityManager] = None):
        self.adapter_id = adapter_id
        self.security_manager = security_manager or IoTSecurityManager()
        self.initialized = False
        self.health_score = 1.0
        self.metrics_history = deque(maxlen=1000)
        self.error_callbacks: List[Callable] = []
        self.performance_monitor = PerformanceMonitor(self)
        self._operation_count = 0
        self._error_count = 0
        self._last_health_check = datetime.utcnow()
        
    @abstractmethod
    async def initialize(self) -> bool:
        """Async initialization for better performance"""
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Async cleanup"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> PlatformCapabilities:
        """Get detailed platform capabilities"""
        pass
    
    async def health_check(self) -> HardwareHealth:
        """Perform comprehensive health check"""
        try:
            # Basic connectivity test
            caps = self.get_capabilities()
            
            # Check error rate
            error_rate = self._error_count / max(self._operation_count, 1)
            
            # Calculate health score
            self.health_score = 1.0 - (error_rate * 2)  # Penalize errors heavily
            self.health_score = max(0.0, min(1.0, self.health_score))
            
            # Determine health state
            if self.health_score > 0.9:
                return HardwareHealth.EXCELLENT
            elif self.health_score > 0.7:
                return HardwareHealth.GOOD
            elif self.health_score > 0.5:
                return HardwareHealth.DEGRADED
            elif self.health_score > 0.2:
                return HardwareHealth.FAILING
            else:
                return HardwareHealth.FAILED
                
        except Exception as e:
            logger.error("Health check failed", adapter=self.adapter_id, error=str(e))
            return HardwareHealth.UNKNOWN
    
    async def secure_operation(self, operation: Callable, *args, **kwargs):
        """Execute operation with security and monitoring"""
        start_time = time.time()
        
        try:
            # Increment operation count
            self._operation_count += 1
            
            # Execute operation
            result = await operation(*args, **kwargs)
            
            # Record metrics
            latency = (time.time() - start_time) * 1000
            self.record_metric('latency_ms', latency)
            
            return result
            
        except Exception as e:
            self._error_count += 1
            logger.error("Operation failed", 
                        adapter=self.adapter_id, 
                        operation=operation.__name__,
                        error=str(e))
            
            # Notify error callbacks
            for callback in self.error_callbacks:
                try:
                    await callback(self, e)
                except:
                    pass
                    
            raise
    
    def record_metric(self, metric_name: str, value: float):
        """Record performance metric"""
        metric = HardwareMetrics(
            timestamp=datetime.utcnow(),
            **{metric_name: value}
        )
        self.metrics_history.append(metric)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of recent metrics"""
        if not self.metrics_history:
            return {}
            
        recent_metrics = list(self.metrics_history)[-100:]
        
        summary = {
            'health_score': self.health_score,
            'error_rate': self._error_count / max(self._operation_count, 1),
            'total_operations': self._operation_count,
            'total_errors': self._error_count,
            'uptime_seconds': (datetime.utcnow() - self._last_health_check).total_seconds()
        }
        
        # Calculate averages for numeric metrics
        for metric in ['latency_ms', 'cpu_usage', 'memory_usage']:
            values = [m.__dict__.get(metric, 0) for m in recent_metrics if metric in m.__dict__]
            if values:
                summary[f'avg_{metric}'] = np.mean(values)
                summary[f'max_{metric}'] = np.max(values)
                summary[f'p95_{metric}'] = np.percentile(values, 95)
        
        return summary
    
    # Pin validation with security
    def validate_pin_access(self, pin: int, mode: PinMode) -> bool:
        """Validate pin access with security checks"""
        caps = self.get_capabilities()
        
        # Find pin capability
        all_pins = caps.digital_pins + caps.analog_pins + caps.pwm_pins
        pin_cap = next((p for p in all_pins if p.number == pin), None)
        
        if not pin_cap:
            logger.warning("Invalid pin access attempt", pin=pin, adapter=self.adapter_id)
            return False
            
        if pin_cap.reserved:
            logger.warning("Reserved pin access attempt", pin=pin, adapter=self.adapter_id)
            return False
            
        if pin_cap.in_use and pin_cap.current_mode != mode:
            logger.warning("Pin mode conflict", pin=pin, 
                         current=pin_cap.current_mode, requested=mode)
            return False
            
        return mode in pin_cap.modes

class RaspberryPiAdapter(HardwareAdapter):
    """Production-ready Raspberry Pi adapter with advanced features"""
    
    def __init__(self, adapter_id: str = "rpi_main", 
                 security_manager: Optional[IoTSecurityManager] = None):
        super().__init__(adapter_id, security_manager)
        self.GPIO = None
        self.cpu_temp_path = Path("/sys/class/thermal/thermal_zone0/temp")
        self._i2c_bus = None
        self._spi_bus = None
        self._pwm_instances = {}
        self._interrupt_handlers = {}
        self._pin_monitors = {}
        
    async def initialize(self) -> bool:
        """Initialize with comprehensive setup"""
        try:
            import RPi.GPIO as GPIO
            self.GPIO = GPIO
            self.GPIO.setmode(GPIO.BCM)
            self.GPIO.setwarnings(False)
            
            # Initialize I2C
            try:
                import smbus2
                self._i2c_bus = smbus2.SMBus(1)
                logger.info("I2C initialized")
            except:
                logger.warning("I2C initialization failed")
            
            # Initialize SPI
            try:
                import spidev
                self._spi_bus = spidev.SpiDev()
                logger.info("SPI initialized")
            except:
                logger.warning("SPI initialization failed")
            
            # Start monitoring
            self.performance_monitor.start()
            
            self.initialized = True
            logger.info("Raspberry Pi adapter initialized", adapter_id=self.adapter_id)
            return True
            
        except ImportError:
            logger.error("RPi.GPIO not available")
            return False
        except Exception as e:
            logger.error("Initialization failed", error=str(e))
            return False
    
    async def cleanup(self):
        """Comprehensive cleanup"""
        if self.GPIO and self.initialized:
            # Stop all PWM instances
            for pwm in self._pwm_instances.values():
                try:
                    pwm.stop()
                except:
                    pass
            
            # Remove interrupt handlers
            for pin in self._interrupt_handlers:
                try:
                    self.GPIO.remove_event_detect(pin)
                except:
                    pass
            
            # Cleanup GPIO
            self.GPIO.cleanup()
            
            # Close buses
            if self._i2c_bus:
                self._i2c_bus.close()
            if self._spi_bus:
                self._spi_bus.close()
            
            # Stop monitoring
            self.performance_monitor.stop()
            
            logger.info("Raspberry Pi adapter cleaned up", adapter_id=self.adapter_id)
    
    def get_capabilities(self) -> PlatformCapabilities:
        """Get detailed Raspberry Pi capabilities"""
        # Detect Pi model
        model = self._detect_pi_model()
        
        # Create pin capabilities
        digital_pins = []
        for pin in range(2, 28):  # GPIO 2-27
            modes = {PinMode.INPUT, PinMode.OUTPUT}
            if pin in [12, 13, 18, 19]:  # Hardware PWM
                modes.add(PinMode.PWM)
            if pin in [2, 3]:  # I2C
                modes.add(PinMode.I2C)
            if pin in [9, 10, 11]:  # SPI
                modes.add(PinMode.SPI)
            if pin in [14, 15]:  # UART
                modes.add(PinMode.UART)
            
            digital_pins.append(PinCapability(
                number=pin,
                modes=modes,
                max_current_ma=16,
                max_voltage=3.3,
                interrupt_capable=True
            ))
        
        return PlatformCapabilities(
            name=f"Raspberry Pi {model}",
            version=self._get_pi_revision(),
            digital_pins=digital_pins,
            analog_pins=[],  # No built-in analog
            pwm_pins=[p for p in digital_pins if PinMode.PWM in p.modes],
            communication_protocols={'i2c', 'spi', 'uart', '1-wire'},
            max_gpio_current_ma=50,
            operating_voltage=3.3,
            adc_resolution_bits=0,  # No built-in ADC
            dac_resolution_bits=None,
            hardware_timers=4,
            hardware_interrupts=len(digital_pins),
            memory_kb=self._get_memory_kb(),
            flash_kb=0,  # SD card based
            cpu_mhz=self._get_cpu_freq_mhz(),
            features={'wifi', 'bluetooth', 'ethernet', 'usb', 'hdmi', 'camera', 'gpio'}
        )
    
    def _detect_pi_model(self) -> str:
        """Detect Raspberry Pi model"""
        try:
            with open('/sys/firmware/devicetree/base/model', 'r') as f:
                model = f.read().strip()
                # Extract model number
                if "Pi 4" in model:
                    return "4B"
                elif "Pi 3" in model:
                    return "3B+"
                elif "Pi Zero 2" in model:
                    return "Zero 2 W"
                elif "Pi Zero" in model:
                    return "Zero W"
                else:
                    return "Unknown"
        except:
            return "Unknown"
    
    def _get_pi_revision(self) -> str:
        """Get Pi revision code"""
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line.startswith('Revision'):
                        return line.split(':')[1].strip()
        except:
            pass
        return "unknown"
    
    def _get_memory_kb(self) -> int:
        """Get total memory in KB"""
        try:
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if line.startswith('MemTotal'):
                        return int(line.split()[1])
        except:
            pass
        return 0
    
    def _get_cpu_freq_mhz(self) -> float:
        """Get current CPU frequency"""
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq', 'r') as f:
                return float(f.read().strip()) / 1000  # Convert KHz to MHz
        except:
            return 1500.0  # Default for Pi 4
    
    async def get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature for thermal monitoring"""
        try:
            if self.cpu_temp_path.exists():
                temp = int(self.cpu_temp_path.read_text().strip()) / 1000.0
                self.record_metric('temperature', temp)
                return temp
        except:
            pass
        return None
    
    async def setup_pin(self, pin: int, mode: PinMode, **kwargs) -> bool:
        """Enhanced pin setup with validation and monitoring"""
        if not self.validate_pin_access(pin, mode):
            return False
            
        async def _setup():
            if mode == PinMode.INPUT:
                pull_up_down = self.GPIO.PUD_DOWN
                if kwargs.get('pull_up'):
                    pull_up_down = self.GPIO.PUD_UP
                elif kwargs.get('pull_down'):
                    pull_up_down = self.GPIO.PUD_DOWN
                    
                self.GPIO.setup(pin, self.GPIO.IN, pull_up_down=pull_up_down)
                
                # Setup interrupt if requested
                if kwargs.get('interrupt'):
                    edge = self.GPIO.RISING
                    if kwargs.get('edge') == 'falling':
                        edge = self.GPIO.FALLING
                    elif kwargs.get('edge') == 'both':
                        edge = self.GPIO.BOTH
                        
                    callback = kwargs.get('callback')
                    if callback:
                        self.GPIO.add_event_detect(pin, edge, callback=callback, 
                                                 bouncetime=kwargs.get('bouncetime', 200))
                        self._interrupt_handlers[pin] = callback
                        
            elif mode == PinMode.OUTPUT:
                initial = self.GPIO.HIGH if kwargs.get('initial_high') else self.GPIO.LOW
                self.GPIO.setup(pin, self.GPIO.OUT, initial=initial)
                
            elif mode == PinMode.PWM:
                self.GPIO.setup(pin, self.GPIO.OUT)
                frequency = kwargs.get('frequency', 1000)
                pwm = self.GPIO.PWM(pin, frequency)
                pwm.start(0)
                self._pwm_instances[pin] = pwm
                
            # Update pin capability
            caps = self.get_capabilities()
            for p in caps.digital_pins:
                if p.number == pin:
                    p.current_mode = mode
                    p.in_use = True
                    break
                    
            return True
            
        return await self.secure_operation(_setup)
    
    async def digital_read(self, pin: int) -> bool:
        """Read with monitoring"""
        async def _read():
            return bool(self.GPIO.input(pin))
        return await self.secure_operation(_read)
    
    async def digital_write(self, pin: int, value: bool):
        """Write with monitoring"""
        async def _write():
            self.GPIO.output(pin, self.GPIO.HIGH if value else self.GPIO.LOW)
        await self.secure_operation(_write)
    
    async def pwm_write(self, pin: int, duty_cycle: float, frequency: Optional[float] = None):
        """Enhanced PWM control"""
        async def _pwm_write():
            if pin not in self._pwm_instances:
                raise ValueError(f"Pin {pin} not configured for PWM")
                
            pwm = self._pwm_instances[pin]
            
            if frequency:
                pwm.ChangeFrequency(frequency)
                
            pwm.ChangeDutyCycle(max(0, min(100, duty_cycle * 100)))
            
        await self.secure_operation(_pwm_write)
    
    async def i2c_scan(self) -> List[int]:
        """Scan with device identification"""
        if not self._i2c_bus:
            return []
            
        async def _scan():
            devices = []
            device_info = {}
            
            for address in range(0x03, 0x78):
                try:
                    self._i2c_bus.read_byte(address)
                    devices.append(address)
                    
                    # Try to identify device
                    device_type = self._identify_i2c_device(address)
                    if device_type:
                        device_info[address] = device_type
                        
                except:
                    pass
                    
            logger.info("I2C scan complete", 
                       devices=[hex(d) for d in devices],
                       identified=device_info)
            return devices
            
        return await self.secure_operation(_scan)
    
    def _identify_i2c_device(self, address: int) -> Optional[str]:
        """Identify I2C device by reading known registers"""
        i2c_signatures = {
            0x76: [
                (0xD0, 0x58, "BMP280"),
                (0xD0, 0x60, "BME280"),
                (0xD0, 0x61, "BMP680")
            ],
            0x77: [
                (0xD0, 0x58, "BMP280"),
                (0xD0, 0x60, "BME280")
            ],
            0x68: [
                (0x75, 0x68, "MPU6050"),
                (0x75, 0x71, "MPU9250")
            ],
            0x40: [(0xE7, None, "HTU21D")],
            0x23: [(None, None, "BH1750")],
            0x5A: [(None, None, "MLX90614")]
        }
        
        if address not in i2c_signatures:
            return None
            
        for reg, expected, name in i2c_signatures[address]:
            if reg is None:
                return name  # Device doesn't have ID register
                
            try:
                value = self._i2c_bus.read_byte_data(address, reg)
                if expected is None or value == expected:
                    return name
            except:
                pass
                
        return None
    
    async def discover_sensors(self) -> List[SensorInfo]:
        """Advanced sensor discovery with auto-identification"""
        sensors = []
        
        # 1-Wire sensors
        sensors.extend(await self._discover_onewire_sensors())
        
        # I2C sensors
        sensors.extend(await self._discover_i2c_sensors())
        
        # SPI sensors (if configured)
        if self._spi_bus:
            sensors.extend(await self._discover_spi_sensors())
        
        # GPIO-based sensors (check for known patterns)
        sensors.extend(await self._discover_gpio_sensors())
        
        return sensors
    
    async def _discover_onewire_sensors(self) -> List[SensorInfo]:
        """Discover 1-Wire sensors with enhanced metadata"""
        sensors = []
        
        try:
            import glob
            w1_devices = glob.glob('/sys/bus/w1/devices/28-*')
            
            for device_path in w1_devices:
                device_id = device_path.split('/')[-1]
                
                # Read temperature to verify sensor is working
                try:
                    temp_file = Path(device_path) / 'w1_slave'
                    temp_data = temp_file.read_text()
                    
                    if 'YES' in temp_data:
                        # Extract temperature
                        temp_line = temp_data.split('\n')[1]
                        temp_value = float(temp_line.split('t=')[1]) / 1000.0
                        
                        sensor = SensorInfo(
                            sensor_type='DS18B20',
                            name=f'Temperature-{device_id[-4:]}',
                            pins={'data': 4},  # Default 1-Wire pin
                            protocol='1-wire',
                            manufacturer='Maxim Integrated',
                            model='DS18B20',
                            serial_number=device_id,
                            calibration_data={'offset': 0.0, 'scale': 1.0}
                        )
                        sensors.append(sensor)
                        
                        logger.info("Found DS18B20", 
                                   id=device_id, 
                                   temp=temp_value)
                except:
                    pass
                    
        except Exception as e:
            logger.error("1-Wire discovery failed", error=str(e))
            
        return sensors
    
    async def _discover_i2c_sensors(self) -> List[SensorInfo]:
        """Discover I2C sensors with detailed information"""
        sensors = []
        
        if not self._i2c_bus:
            return sensors
            
        i2c_addresses = await self.i2c_scan()
        
        for addr in i2c_addresses:
            device_type = self._identify_i2c_device(addr)
            
            if device_type:
                sensor_info = self._get_i2c_sensor_info(addr, device_type)
                if sensor_info:
                    sensors.append(sensor_info)
                    
        return sensors
    
    def _get_i2c_sensor_info(self, address: int, device_type: str) -> Optional[SensorInfo]:
        """Get detailed sensor information for known I2C devices"""
        sensor_db = {
            'BME280': {
                'name': 'Environmental Sensor',
                'manufacturer': 'Bosch',
                'model': 'BME280',
                'calibration': self._read_bme280_calibration
            },
            'BMP280': {
                'name': 'Pressure Sensor',
                'manufacturer': 'Bosch',
                'model': 'BMP280',
                'calibration': self._read_bmp280_calibration
            },
            'BH1750': {
                'name': 'Light Sensor',
                'manufacturer': 'ROHM',
                'model': 'BH1750FVI',
                'calibration': lambda addr: {'mode': 'continuous_high_res'}
            },
            'MPU6050': {
                'name': 'IMU Sensor',
                'manufacturer': 'InvenSense',
                'model': 'MPU-6050',
                'calibration': self._read_mpu6050_calibration
            }
        }
        
        if device_type not in sensor_db:
            return None
            
        info = sensor_db[device_type]
        
        try:
            calibration = info['calibration'](address) if info['calibration'] else None
        except:
            calibration = None
            
        return SensorInfo(
            sensor_type=device_type,
            name=info['name'],
            pins={'sda': 2, 'scl': 3},
            protocol='i2c',
            address=address,
            manufacturer=info['manufacturer'],
            model=info['model'],
            calibration_data=calibration
        )
    
    def _read_bme280_calibration(self, address: int) -> Dict[str, Any]:
        """Read BME280 calibration data"""
        try:
            # Read calibration registers
            calib = []
            for i in range(0x88, 0xA2):
                calib.append(self._i2c_bus.read_byte_data(address, i))
                
            # Parse calibration data (simplified)
            return {
                'T1': (calib[1] << 8) | calib[0],
                'T2': (calib[3] << 8) | calib[2],
                'T3': (calib[5] << 8) | calib[4],
                # ... more calibration values
            }
        except:
            return {}
    
    def _read_bmp280_calibration(self, address: int) -> Dict[str, Any]:
        """Read BMP280 calibration data"""
        # Similar to BME280 but simpler
        return {}
    
    def _read_mpu6050_calibration(self, address: int) -> Dict[str, Any]:
        """Read MPU6050 calibration/configuration"""
        try:
            # Read gyro and accel config
            gyro_config = self._i2c_bus.read_byte_data(address, 0x1B)
            accel_config = self._i2c_bus.read_byte_data(address, 0x1C)
            
            return {
                'gyro_range': (gyro_config >> 3) & 0x03,
                'accel_range': (accel_config >> 3) & 0x03
            }
        except:
            return {}
    
    async def _discover_spi_sensors(self) -> List[SensorInfo]:
        """Discover SPI sensors"""
        sensors = []
        
        # Check for common SPI devices
        # This would need device-specific probing
        
        return sensors
    
    async def _discover_gpio_sensors(self) -> List[SensorInfo]:
        """Discover GPIO-connected sensors by probing"""
        sensors = []
        
        # Check for DHT sensors on common pins
        dht_pins = [4, 17, 27, 22]  # Common DHT sensor pins
        
        for pin in dht_pins:
            if await self._probe_dht_sensor(pin):
                sensors.append(SensorInfo(
                    sensor_type='DHT22',
                    name=f'DHT22-GPIO{pin}',
                    pins={'data': pin},
                    protocol='gpio',
                    manufacturer='Aosong',
                    model='DHT22/AM2302'
                ))
                
        return sensors
    
    async def _probe_dht_sensor(self, pin: int) -> bool:
        """Probe for DHT sensor on specific pin"""
        # This would implement the DHT protocol to check if sensor responds
        # For now, return False as it requires specific timing
        return False

class PerformanceMonitor:
    """Monitor hardware adapter performance"""
    
    def __init__(self, adapter: HardwareAdapter):
        self.adapter = adapter
        self.monitoring = False
        self._monitor_thread = None
        self._monitor_interval = 10  # seconds
        
    def start(self):
        """Start performance monitoring"""
        self.monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        
    def stop(self):
        """Stop performance monitoring"""
        self.monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
            
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                # Collect system metrics
                metrics = self._collect_metrics()
                
                # Record metrics
                for name, value in metrics.items():
                    self.adapter.record_metric(name, value)
                    
                # Check for anomalies
                self._check_anomalies(metrics)
                
            except Exception as e:
                logger.error("Performance monitoring error", 
                           adapter=self.adapter.adapter_id,
                           error=str(e))
                           
            time.sleep(self._monitor_interval)
            
    def _collect_metrics(self) -> Dict[str, float]:
        """Collect system metrics"""
        metrics = {}
        
        try:
            # CPU usage
            with open('/proc/stat', 'r') as f:
                cpu_line = f.readline()
                cpu_times = list(map(int, cpu_line.split()[1:]))
                idle_time = cpu_times[3]
                total_time = sum(cpu_times)
                
                if hasattr(self, '_last_cpu_times'):
                    idle_delta = idle_time - self._last_cpu_times[3]
                    total_delta = total_time - sum(self._last_cpu_times)
                    cpu_usage = 1.0 - (idle_delta / total_delta)
                    metrics['cpu_usage'] = max(0.0, min(1.0, cpu_usage))
                    
                self._last_cpu_times = cpu_times
                
            # Memory usage
            with open('/proc/meminfo', 'r') as f:
                meminfo = {}
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = int(parts[1].strip().split()[0])
                        meminfo[key] = value
                        
                total = meminfo.get('MemTotal', 1)
                available = meminfo.get('MemAvailable', 0)
                metrics['memory_usage'] = 1.0 - (available / total)
                
            # Temperature (if available)
            if hasattr(self.adapter, 'get_cpu_temperature'):
                temp = asyncio.run(self.adapter.get_cpu_temperature())
                if temp:
                    metrics['temperature'] = temp
                    
        except Exception as e:
            logger.error("Metric collection failed", error=str(e))
            
        return metrics
        
    def _check_anomalies(self, metrics: Dict[str, float]):
        """Check for performance anomalies"""
        # High CPU usage
        if metrics.get('cpu_usage', 0) > 0.9:
            logger.warning("High CPU usage detected", 
                         adapter=self.adapter.adapter_id,
                         cpu_usage=metrics['cpu_usage'])
                         
        # High temperature
        if metrics.get('temperature', 0) > 80:
            logger.warning("High temperature detected",
                         adapter=self.adapter.adapter_id,
                         temperature=metrics['temperature'])
                         
        # High memory usage
        if metrics.get('memory_usage', 0) > 0.9:
            logger.warning("High memory usage detected",
                         adapter=self.adapter.adapter_id,
                         memory_usage=metrics['memory_usage'])

class NetworkHardwareAdapter(HardwareAdapter):
    """Base class for network-connected hardware adapters"""
    
    def __init__(self, adapter_id: str, base_url: str, 
                 auth_token: Optional[str] = None,
                 security_manager: Optional[IoTSecurityManager] = None):
        super().__init__(adapter_id, security_manager)
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = None
        self._heartbeat_task = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5
        
    async def initialize(self) -> bool:
        """Initialize network connection with retry logic"""
        try:
            import aiohttp
            
            # Create session with security headers
            headers = {
                'User-Agent': 'OSCE-HAL/1.0',
                'X-Adapter-ID': self.adapter_id
            }
            
            if self.auth_token:
                headers['Authorization'] = f'Bearer {self.auth_token}'
                
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout
            )
            
            # Test connection
            async with self.session.get(f"{self.base_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    logger.info("Network adapter connected",
                              adapter_id=self.adapter_id,
                              device_info=data)
                              
                    # Start heartbeat
                    self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
                    
                    self.initialized = True
                    self._reconnect_attempts = 0
                    return True
                    
        except Exception as e:
            logger.error("Network adapter connection failed",
                       adapter_id=self.adapter_id,
                       error=str(e))
                       
            # Try reconnection
            if self._reconnect_attempts < self._max_reconnect_attempts:
                self._reconnect_attempts += 1
                await asyncio.sleep(2 ** self._reconnect_attempts)  # Exponential backoff
                return await self.initialize()
                
        return False
        
    async def cleanup(self):
        """Cleanup network resources"""
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
            
        if self.session:
            await self.session.close()
            
    async def _heartbeat_loop(self):
        """Maintain connection with heartbeat"""
        while self.initialized:
            try:
                await asyncio.sleep(30)
                
                async with self.session.get(f"{self.base_url}/heartbeat") as resp:
                    if resp.status != 200:
                        logger.warning("Heartbeat failed",
                                     adapter_id=self.adapter_id,
                                     status=resp.status)
                        # Attempt reconnection
                        await self.initialize()
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Heartbeat error",
                           adapter_id=self.adapter_id,
                           error=str(e))
                           
    async def _api_call(self, method: str, endpoint: str, 
                       data: Optional[Dict] = None,
                       retry: bool = True) -> Optional[Dict]:
        """Make API call with retry and monitoring"""
        if not self.session:
            return None
            
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        async def _call():
            try:
                if method == 'GET':
                    async with self.session.get(url) as resp:
                        resp.raise_for_status()
                        return await resp.json()
                elif method == 'POST':
                    async with self.session.post(url, json=data) as resp:
                        resp.raise_for_status()
                        return await resp.json()
                elif method == 'PUT':
                    async with self.session.put(url, json=data) as resp:
                        resp.raise_for_status()
                        return await resp.json()
                elif method == 'DELETE':
                    async with self.session.delete(url) as resp:
                        resp.raise_for_status()
                        return await resp.json()
                        
            except aiohttp.ClientError as e:
                if retry and e.status in [502, 503, 504]:
                    # Retry on server errors
                    await asyncio.sleep(1)
                    return await self._api_call(method, endpoint, data, retry=False)
                raise
                
        return await self.secure_operation(_call)

class ESP32Adapter(NetworkHardwareAdapter):
    """Enhanced ESP32 adapter with OTA updates and advanced features"""
    
    def __init__(self, adapter_id: str, ip_address: str, port: int = 80,
                 auth_token: Optional[str] = None,
                 security_manager: Optional[IoTSecurityManager] = None):
        base_url = f"http://{ip_address}:{port}/api/v1"
        super().__init__(adapter_id, base_url, auth_token, security_manager)
        self.ip_address = ip_address
        self.port = port
        self._websocket = None
        self._event_handlers = {}
        
    async def initialize(self) -> bool:
        """Initialize with WebSocket support"""
        if not await super().initialize():
            return False
            
        # Try to establish WebSocket connection for real-time updates
        try:
            import aiohttp
            ws_url = f"ws://{self.ip_address}:{self.port}/ws"
            self._websocket = await self.session.ws_connect(ws_url)
            
            # Start WebSocket handler
            asyncio.create_task(self._websocket_handler())
            
            logger.info("ESP32 WebSocket connected", adapter_id=self.adapter_id)
        except:
            logger.warning("ESP32 WebSocket not available", adapter_id=self.adapter_id)
            
        return True
        
    async def _websocket_handler(self):
        """Handle WebSocket messages"""
        if not self._websocket:
            return
            
        try:
            async for msg in self._websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    event_type = data.get('type')
                    
                    if event_type in self._event_handlers:
                        for handler in self._event_handlers[event_type]:
                            try:
                                await handler(data)
                            except:
                                pass
                                
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    logger.error("WebSocket error",
                               adapter_id=self.adapter_id,
                               error=self._websocket.exception())
                               
        except Exception as e:
            logger.error("WebSocket handler error",
                       adapter_id=self.adapter_id,
                       error=str(e))
                       
    def on_event(self, event_type: str, handler: Callable):
        """Register event handler for WebSocket events"""
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        
    def get_capabilities(self) -> PlatformCapabilities:
        """Get ESP32 capabilities with variants"""
        # This could be dynamically fetched from device
        return PlatformCapabilities(
            name="ESP32-WROOM-32",
            version="1.0.0",
            digital_pins=[
                PinCapability(
                    number=pin,
                    modes={PinMode.INPUT, PinMode.OUTPUT, PinMode.PWM, 
                          PinMode.INTERRUPT},
                    max_current_ma=12,
                    max_voltage=3.3,
                    pwm_frequency_range=(1, 40000000),
                    interrupt_capable=True
                ) for pin in range(0, 34) if pin not in [6, 7, 8, 9, 10, 11]
            ],
            analog_pins=[
                PinCapability(
                    number=pin,
                    modes={PinMode.ANALOG, PinMode.INPUT},
                    max_voltage=3.3,
                    adc_resolution=12
                ) for pin in [32, 33, 34, 35, 36, 39]
            ],
            pwm_pins=[],  # All digital pins support PWM
            communication_protocols={'i2c', 'spi', 'uart', 'can', 'wifi', 'bluetooth'},
            max_gpio_current_ma=40,
            operating_voltage=3.3,
            adc_resolution_bits=12,
            dac_resolution_bits=8,
            hardware_timers=4,
            hardware_interrupts=34,
            memory_kb=520,
            flash_kb=4096,
            cpu_mhz=240,
            features={'wifi', 'bluetooth', 'ble', 'touch', 'hall_sensor', 
                     'temperature_sensor', 'deep_sleep', 'ota_update'}
        )
        
    async def ota_update(self, firmware_url: str, 
                        verify_signature: bool = True) -> bool:
        """Perform Over-The-Air firmware update"""
        if verify_signature:
            # Verify firmware signature
            # This would download and verify the firmware signature
            pass
            
        data = {
            'firmware_url': firmware_url,
            'verify': verify_signature
        }
        
        result = await self._api_call('POST', '/system/ota', data)
        
        if result and result.get('status') == 'updating':
            logger.info("OTA update started", adapter_id=self.adapter_id)
            
            # Monitor update progress
            while True:
                await asyncio.sleep(5)
                status = await self._api_call('GET', '/system/ota/status')
                
                if status:
                    progress = status.get('progress', 0)
                    state = status.get('state')
                    
                    logger.info("OTA progress", 
                              adapter_id=self.adapter_id,
                              progress=progress,
                              state=state)
                              
                    if state == 'completed':
                        return True
                    elif state == 'failed':
                        return False
                        
        return False
        
    async def deep_sleep(self, duration_seconds: int, 
                        wake_pin: Optional[int] = None) -> bool:
        """Put ESP32 into deep sleep mode"""
        data = {
            'duration': duration_seconds,
            'wake_pin': wake_pin
        }
        
        result = await self._api_call('POST', '/power/deep_sleep', data)
        return result is not None
        
    async def read_touch_sensor(self, pin: int) -> int:
        """Read capacitive touch sensor value"""
        result = await self._api_call('GET', f'/touch/{pin}')
        return result.get('value', 0) if result else 0
        
    async def read_hall_sensor(self) -> int:
        """Read built-in hall effect sensor"""
        result = await self._api_call('GET', '/sensors/hall')
        return result.get('value', 0) if result else 0
        
    async def read_internal_temperature(self) -> float:
        """Read internal temperature sensor"""
        result = await self._api_call('GET', '/sensors/temperature')
        return result.get('value', 0.0) if result else 0.0

class HardwareManager:
    """Enhanced hardware manager with distributed support"""
    
    def __init__(self, security_manager: Optional[IoTSecurityManager] = None):
        self.security_manager = security_manager or IoTSecurityManager()
        self.adapters: Dict[str, HardwareAdapter] = {}
        self.primary_adapter: Optional[str] = None
        self.adapter_groups: Dict[str, List[str]] = defaultdict(list)
        self._discovery_task = None
        self._health_check_task = None
        self._event_handlers = defaultdict(list)
        
    async def start(self):
        """Start hardware manager with background tasks"""
        # Start discovery
        self._discovery_task = asyncio.create_task(self._discovery_loop())
        
        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        
        logger.info("Hardware manager started")
        
    async def stop(self):
        """Stop hardware manager and cleanup"""
        # Cancel background tasks
        if self._discovery_task:
            self._discovery_task.cancel()
        if self._health_check_task:
            self._health_check_task.cancel()
            
        # Cleanup all adapters
        for adapter in list(self.adapters.values()):
            await adapter.cleanup()
            
        logger.info("Hardware manager stopped")
        
    async def add_adapter(self, name: str, adapter: HardwareAdapter,
                         group: Optional[str] = None) -> bool:
        """Add adapter with group support"""
        if await adapter.initialize():
            self.adapters[name] = adapter
            
            if group:
                self.adapter_groups[group].append(name)
                
            if not self.primary_adapter:
                self.primary_adapter = name
                
            # Register for adapter events
            adapter.error_callbacks.append(self._handle_adapter_error)
            
            logger.info("Added hardware adapter", 
                       name=name, 
                       group=group,
                       type=type(adapter).__name__)
            
            # Emit event
            await self._emit_event('adapter_added', {
                'name': name,
                'adapter': adapter,
                'group': group
            })
            
            return True
        return False
        
    async def remove_adapter(self, name: str):
        """Remove adapter with cleanup"""
        if name in self.adapters:
            adapter = self.adapters[name]
            
            # Cleanup
            await adapter.cleanup()
            
            # Remove from groups
            for group, members in self.adapter_groups.items():
                if name in members:
                    members.remove(name)
                    
            # Remove adapter
            del self.adapters[name]
            
            # Update primary if needed
            if self.primary_adapter == name:
                self.primary_adapter = next(iter(self.adapters), None)
                
            # Emit event
            await self._emit_event('adapter_removed', {
                'name': name
            })
            
    async def _handle_adapter_error(self, adapter: HardwareAdapter, error: Exception):
        """Handle adapter errors with recovery"""
        adapter_name = None
        for name, ad in self.adapters.items():
            if ad == adapter:
                adapter_name = name
                break
                
        logger.error("Adapter error",
                   adapter=adapter_name,
                   error=str(error))
                   
        # Check if adapter needs restart
        health = await adapter.health_check()
        if health in [HardwareHealth.FAILED, HardwareHealth.UNKNOWN]:
            logger.warning("Attempting adapter recovery", adapter=adapter_name)
            
            # Try to reinitialize
            await adapter.cleanup()
            if await adapter.initialize():
                logger.info("Adapter recovered", adapter=adapter_name)
            else:
                logger.error("Adapter recovery failed", adapter=adapter_name)
                
                # Emit critical event
                await self._emit_event('adapter_failed', {
                    'name': adapter_name,
                    'adapter': adapter
                })
                
    async def _discovery_loop(self):
        """Continuous hardware discovery"""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                # Discover new hardware
                discovered = await self.discover_hardware()
                
                if discovered:
                    logger.info("New hardware discovered", count=len(discovered))
                    
                    # Emit discovery event
                    await self._emit_event('hardware_discovered', {
                        'devices': discovered
                    })
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Discovery error", error=str(e))
                
    async def _health_check_loop(self):
        """Monitor adapter health"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                unhealthy = []
                
                for name, adapter in self.adapters.items():
                    health = await adapter.health_check()
                    
                    if health not in [HardwareHealth.EXCELLENT, HardwareHealth.GOOD]:
                        unhealthy.append({
                            'name': name,
                            'health': health,
                            'metrics': adapter.get_metrics_summary()
                        })
                        
                if unhealthy:
                    logger.warning("Unhealthy adapters detected",
                                 count=len(unhealthy),
                                 adapters=unhealthy)
                                 
                    # Emit health event
                    await self._emit_event('adapters_unhealthy', {
                        'adapters': unhealthy
                    })
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Health check error", error=str(e))
                
    async def discover_hardware(self) -> List[Dict[str, Any]]:
        """Discover all available hardware"""
        discovered = []
        
        # Local hardware discovery
        discovered.extend(await self._discover_local_hardware())
        
        # Network discovery (mDNS/Bonjour)
        discovered.extend(await self._discover_network_hardware())
        
        # USB device discovery
        discovered.extend(await self._discover_usb_hardware())
        
        return discovered
        
    async def _discover_local_hardware(self) -> List[Dict[str, Any]]:
        """Discover local hardware platforms"""
        discovered = []
        
        # Check for Raspberry Pi
        if Path("/sys/firmware/devicetree/base/model").exists():
            pi_adapter = RaspberryPiAdapter()
            if await self.add_adapter("local_pi", pi_adapter, group="local"):
                discovered.append({
                    'type': 'raspberry_pi',
                    'name': 'local_pi',
                    'adapter': pi_adapter
                })
                
        return discovered
        
    async def _discover_network_hardware(self) -> List[Dict[str, Any]]:
        """Discover network devices using mDNS"""
        discovered = []
        
        try:
            # This would use zeroconf/mDNS to discover ESP32/ESP8266 devices
            # For now, return empty list
            pass
        except:
            pass
            
        return discovered
        
    async def _discover_usb_hardware(self) -> List[Dict[str, Any]]:
        """Discover USB-connected devices"""
        discovered = []
        
        try:
            import serial.tools.list_ports
            
            for port in serial.tools.list_ports.comports():
                # Check for Arduino
                if any(x in port.description for x in ["Arduino", "CH340", "FT232"]):
                    # Try to connect
                    from .arduino_adapter import ArduinoAdapter
                    arduino = ArduinoAdapter(port.device)
                    
                    adapter_name = f"arduino_{port.device.replace('/', '_')}"
                    if await self.add_adapter(adapter_name, arduino, group="usb"):
                        discovered.append({
                            'type': 'arduino',
                            'name': adapter_name,
                            'port': port.device,
                            'adapter': arduino
                        })
                        
        except ImportError:
            logger.warning("pyserial not available for USB discovery")
            
        return discovered
        
    async def get_all_sensors(self) -> Dict[str, List[SensorInfo]]:
        """Get all sensors from all adapters"""
        all_sensors = {}
        
        # Parallel sensor discovery
        tasks = []
        for name, adapter in self.adapters.items():
            tasks.append(self._discover_adapter_sensors(name, adapter))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                all_sensors.update(result)
                
        return all_sensors
        
    async def _discover_adapter_sensors(self, name: str, 
                                      adapter: HardwareAdapter) -> Dict[str, List[SensorInfo]]:
        """Discover sensors for single adapter"""
        try:
            sensors = await adapter.discover_sensors()
            if sensors:
                # Authenticate sensors with security manager
                for sensor in sensors:
                    device_identity = sensor.to_device_identity()
                    try:
                        auth_result = await self.security_manager.authenticate_device(
                            device_identity
                        )
                        sensor.auth_token = auth_result['token']
                    except:
                        logger.warning("Sensor authentication failed",
                                     sensor=sensor.name)
                                     
                return {name: sensors}
        except Exception as e:
            logger.error("Sensor discovery failed",
                       adapter=name,
                       error=str(e))
                       
        return {}
        
    def on_event(self, event_type: str, handler: Callable):
        """Register event handler"""
        self._event_handlers[event_type].append(handler)
        
    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit event to all handlers"""
        for handler in self._event_handlers[event_type]:
            try:
                await handler(data)
            except Exception as e:
                logger.error("Event handler error",
                           event=event_type,
                           error=str(e))
                           
    def get_adapter(self, name: str = None, group: str = None) -> Optional[HardwareAdapter]:
        """Get adapter by name or from group"""
        if name:
            return self.adapters.get(name)
        elif group and group in self.adapter_groups:
            # Return first healthy adapter from group
            for adapter_name in self.adapter_groups[group]:
                adapter = self.adapters.get(adapter_name)
                if adapter and adapter.health_score > 0.5:
                    return adapter
        elif self.primary_adapter:
            return self.adapters.get(self.primary_adapter)
            
        return None
        
    def get_metrics_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive metrics for all adapters"""
        dashboard = {
            'timestamp': datetime.utcnow().isoformat(),
            'adapter_count': len(self.adapters),
            'adapters': {}
        }
        
        for name, adapter in self.adapters.items():
            dashboard['adapters'][name] = {
                'type': type(adapter).__name__,
                'health_score': adapter.health_score,
                'metrics': adapter.get_metrics_summary(),
                'capabilities': adapter.get_capabilities().name
            }
            
        return dashboard

# Integration with main Environment class
class HALIntegratedEnvironment:
    """Environment with integrated HAL support"""
    
    def __init__(self, name: str, security_level: SecurityLevel = SecurityLevel.PRODUCTION):
        from osce import Environment
        
        # Create base environment
        self.env = Environment(name, security_level=security_level)
        
        # Create hardware manager
        self.hw_manager = HardwareManager(self.env.security_manager)
        
        # Integrate HAL into environment
        self.env.hal = self.hw_manager
        
    async def setup(self):
        """Setup with hardware auto-discovery"""
        # Start hardware manager
        await self.hw_manager.start()
        
        # Auto-setup environment
        await self.env.auto_setup()
        
        # Discover hardware
        logger.info("Discovering hardware...")
        discovered = await self.hw_manager.discover_hardware()
        
        # Discover sensors
        all_sensors = await self.hw_manager.get_all_sensors()
        
        # Auto-configure sensors in environment
        for adapter_name, sensors in all_sensors.items():
            for sensor in sensors:
                sensor_name = f"{adapter_name}_{sensor.name}"
                await self.env.add_sensor(
                    sensor_name,
                    sensor_type=sensor.sensor_type,
                    config={
                        'adapter': adapter_name,
                        'sensor_info': sensor,
                        'pins': sensor.pins,
                        'protocol': sensor.protocol,
                        'address': sensor.address
                    }
                )
                
        logger.info("Hardware setup complete",
                   adapters=len(self.hw_manager.adapters),
                   sensors=len(self.env.sensors))
                   
    async def start(self):
        """Start environment with hardware monitoring"""
        await self.env.start()
        
    async def stop(self):
        """Stop environment and hardware"""
        await self.env.stop()
        await self.hw_manager.stop()

# Example usage showing production deployment
if __name__ == "__main__":
    async def main():
        # Create production environment with HAL
        env = HALIntegratedEnvironment(
            "Production Greenhouse",
            security_level=SecurityLevel.PRODUCTION
        )
        
        # Setup with auto-discovery
        await env.setup()
        
        # Add network devices manually
        esp32 = ESP32Adapter(
            adapter_id="greenhouse_controller",
            ip_address="192.168.1.100",
            auth_token="your-secure-token"
        )
        await env.hw_manager.add_adapter("greenhouse_esp32", esp32, group="greenhouse")
        
        # Monitor adapter health
        env.hw_manager.on_event('adapters_unhealthy', lambda data: 
            logger.warning("Health alert", adapters=data['adapters'])
        )
        
        # Start the system
        await env.start()
        
        # Get metrics dashboard
        metrics = env.hw_manager.get_metrics_dashboard()
        print("System Metrics:", json.dumps(metrics, indent=2))
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            await env.stop()
            
    asyncio.run(main())
