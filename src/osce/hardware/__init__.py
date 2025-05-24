from .hal import (
    HardwareAdapter,
    RaspberryPiAdapter,
    ESP32Adapter,
    ArduinoAdapter,
    PlatformCapabilities,
    SensorInfo,
    PinMode,
)
from .mock_adapter import MockHardwareAdapter, MockEnvironment
from .exception_handling import (
    HardwareErrorSeverity,
    HardwareException,
    SensorException,
    ActuatorException,
    CommunicationException,
    HardwareNotAvailableException,
    hardware_retry,
    log_and_raise,
)

__all__ = [
    'HardwareAdapter',
    'RaspberryPiAdapter',
    'ESP32Adapter',
    'ArduinoAdapter',
    'PlatformCapabilities',
    'SensorInfo',
    'PinMode',
    'MockHardwareAdapter',
    'MockEnvironment',
    'HardwareErrorSeverity',
    'HardwareException',
    'SensorException',
    'ActuatorException',
    'CommunicationException',
    'HardwareNotAvailableException',
    'hardware_retry',
    'log_and_raise',
]
