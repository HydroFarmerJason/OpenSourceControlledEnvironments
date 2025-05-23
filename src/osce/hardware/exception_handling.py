# osce/hardware/exceptions.py
"""
Robust exception handling for hardware operations
Provides graceful degradation when hardware fails
"""

import time
import logging
from typing import Optional, Callable, Any, Dict, List
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
import traceback

logger = logging.getLogger(__name__)


class HardwareErrorSeverity(Enum):
    """Severity levels for hardware errors"""
    INFO = "info"          # Recoverable, no impact
    WARNING = "warning"    # Recoverable, degraded performance
    ERROR = "error"        # Recoverable, feature disabled  
    CRITICAL = "critical"  # Not recoverable, system impact


class HardwareException(Exception):
    """Base exception for all hardware errors"""
    
    def __init__(self, 
                 message: str,
                 severity: HardwareErrorSeverity = HardwareErrorSeverity.ERROR,
                 hardware_id: Optional[str] = None,
                 recoverable: bool = True,
                 retry_after: Optional[int] = None):
        super().__init__(message)
        self.severity = severity
        self.hardware_id = hardware_id
        self.recoverable = recoverable
        self.retry_after = retry_after
        self.timestamp = datetime.now()


class SensorException(HardwareException):
    """Sensor-specific exceptions"""
    pass


class ActuatorException(HardwareException):
    """Actuator-specific exceptions"""
    pass


class CommunicationException(HardwareException):
    """Communication/network exceptions"""
    pass


class HardwareNotAvailableException(HardwareException):
    """Hardware not detected or available"""
    
    def __init__(self, hardware_type: str, **kwargs):
        message = f"{hardware_type} hardware not available"
        super().__init__(message, severity=HardwareErrorSeverity.WARNING, **kwargs)


@dataclass
class ErrorContext:
    """Context information for error handling"""
    operation: str
    hardware_id: str
    attempt: int = 1
    max_attempts: int = 3
    last_error: Optional[Exception] = None
    start_time: datetime = None
    
    def __post_init__(self):
        if self.start_time is None:
            self.start_time = datetime.now()


class HardwareErrorHandler:
    """Centralized hardware error handling with recovery strategies"""
    
    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.blacklisted_hardware: Dict[str, datetime] = {}
        self.recovery_strategies: Dict[type, Callable] = {}
        self.fallback_providers: Dict[str, List[Callable]] = {}
        
    def register_recovery_strategy(self, 
                                 exception_type: type,
                                 strategy: Callable[[Exception, ErrorContext], bool]):
        """Register a recovery strategy for an exception type"""
        self.recovery_strategies[exception_type] = strategy
        
    def register_fallback(self, hardware_id: str, fallback: Callable):
        """Register fallback provider for hardware"""
        if hardware_id not in self.fallback_providers:
            self.fallback_providers[hardware_id] = []
        self.fallback_providers[hardware_id].append(fallback)
        
    def handle_error(self, error: Exception, context: ErrorContext) -> Any:
        """Handle hardware error with recovery attempts"""
        
        # Log error
        self._log_error(error, context)
        
        # Update error counts
        self._update_error_counts(context.hardware_id)
        
        # Check if hardware should be blacklisted
        if self._should_blacklist(context.hardware_id):
            self._blacklist_hardware(context.hardware_id)
            raise HardwareNotAvailableException(
                context.hardware_id,
                recoverable=False
            )
        
        # Try recovery strategy
        if type(error) in self.recovery_strategies:
            strategy = self.recovery_strategies[type(error)]
            if strategy(error, context):
                logger.info(f"Recovery successful for {context.hardware_id}")
                return True
                
        # Try fallback providers
        if context.hardware_id in self.fallback_providers:
            for fallback in self.fallback_providers[context.hardware_id]:
                try:
                    result = fallback()
                    logger.info(f"Fallback successful for {context.hardware_id}")
                    return result
                except Exception as e:
                    logger.warning(f"Fallback failed: {e}")
                    
        # No recovery possible
        return None
        
    def _log_error(self, error: Exception, context: ErrorContext):
        """Log error with context"""
        if isinstance(error, HardwareException):
            level = getattr(logging, error.severity.value.upper())
        else:
            level = logging.ERROR
            
        logger.log(
            level,
            f"Hardware error in {context.operation} on {context.hardware_id}: {error}",
            extra={
                'hardware_id': context.hardware_id,
                'operation': context.operation,
                'attempt': context.attempt,
                'error_type': type(error).__name__
            }
        )
        
    def _update_error_counts(self, hardware_id: str):
        """Track error frequency"""
        if hardware_id not in self.error_counts:
            self.error_counts[hardware_id] = 0
        self.error_counts[hardware_id] += 1
        
    def _should_blacklist(self, hardware_id: str) -> bool:
        """Determine if hardware should be temporarily disabled"""
        error_count = self.error_counts.get(hardware_id, 0)
        return error_count > 10  # Threshold for blacklisting
        
    def _blacklist_hardware(self, hardware_id: str, duration: int = 300):
        """Temporarily disable problematic hardware"""
        self.blacklisted_hardware[hardware_id] = datetime.now() + timedelta(seconds=duration)
        logger.warning(f"Hardware {hardware_id} blacklisted for {duration} seconds")
        
    def is_blacklisted(self, hardware_id: str) -> bool:
        """Check if hardware is currently blacklisted"""
        if hardware_id in self.blacklisted_hardware:
            if datetime.now() < self.blacklisted_hardware[hardware_id]:
                return True
            else:
                # Remove from blacklist
                del self.blacklisted_hardware[hardware_id]
                self.error_counts[hardware_id] = 0
        return False


# Decorators for common patterns

def with_retry(max_attempts: int = 3, 
               delay: float = 1.0,
               backoff: float = 2.0,
               exceptions: tuple = (Exception,)):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise
                        
                    logger.warning(
                        f"{func.__name__} failed (attempt {attempt}/{max_attempts}): {e}"
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
                    attempt += 1
                    
            return None
        return wrapper
    return decorator


def with_timeout(timeout: float):
    """Timeout decorator for hardware operations"""
    import signal
    
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {timeout} seconds")
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Set alarm
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(timeout))
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)  # Cancel alarm
                return result
            except TimeoutError:
                raise HardwareException(
                    f"{func.__name__} timed out",
                    severity=HardwareErrorSeverity.ERROR,
                    recoverable=True,
                    retry_after=5
                )
            finally:
                signal.alarm(0)  # Ensure alarm is cancelled
                
        return wrapper
    return decorator


def with_fallback(fallback_value: Any = None, fallback_func: Optional[Callable] = None):
    """Provide fallback value on error"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"{func.__name__} failed, using fallback: {e}")
                
                if fallback_func:
                    try:
                        return fallback_func(*args, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {fallback_error}")
                        
                return fallback_value
        return wrapper
    return decorator


def validate_hardware(hardware_id: str):
    """Decorator to check if hardware is available before operation"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Check blacklist
            if hasattr(self, 'error_handler') and self.error_handler.is_blacklisted(hardware_id):
                raise HardwareNotAvailableException(
                    hardware_id,
                    recoverable=True,
                    retry_after=60
                )
                
            # Check if hardware exists
            if hasattr(self, 'hardware_manager'):
                if not self.hardware_manager.get_adapter(hardware_id):
                    raise HardwareNotAvailableException(hardware_id)
                    
            return func(self, *args, **kwargs)
        return wrapper
    return decorator


# Recovery strategies

class RecoveryStrategies:
    """Common recovery strategies for hardware errors"""
    
    @staticmethod
    def sensor_reconnect(error: Exception, context: ErrorContext) -> bool:
        """Try to reconnect sensor"""
        logger.info(f"Attempting sensor reconnect for {context.hardware_id}")
        
        # Simulate reconnection attempt
        time.sleep(2)
        
        # In real implementation, would reset sensor
        return context.attempt < 3
        
    @staticmethod
    def actuator_reset(error: Exception, context: ErrorContext) -> bool:
        """Reset actuator to safe state"""
        logger.info(f"Resetting actuator {context.hardware_id} to safe state")
        
        # In real implementation, would set actuator to OFF
        return True
        
    @staticmethod
    def network_retry(error: Exception, context: ErrorContext) -> bool:
        """Retry network operation with backoff"""
        wait_time = min(60, 2 ** context.attempt)
        logger.info(f"Network retry for {context.hardware_id} in {wait_time}s")
        time.sleep(wait_time)
        return context.attempt < 5


# Example usage with robust hardware operations

class RobustSensorReader:
    """Example of sensor reading with comprehensive error handling"""
    
    def __init__(self, sensor_id: str, hardware_adapter):
        self.sensor_id = sensor_id
        self.hardware_adapter = hardware_adapter
        self.error_handler = HardwareErrorHandler()
        self.last_good_value = None
        self.last_read_time = None
        
        # Register recovery strategies
        self.error_handler.register_recovery_strategy(
            SensorException,
            RecoveryStrategies.sensor_reconnect
        )
        
        # Register fallback
        self.error_handler.register_fallback(
            sensor_id,
            self._use_predicted_value
        )
        
    @with_retry(max_attempts=3, exceptions=(SensorException,))
    @with_timeout(5.0)
    @with_fallback(fallback_value={'value': None, 'source': 'fallback'})
    def read_sensor(self) -> Dict[str, Any]:
        """Read sensor with full error handling"""
        context = ErrorContext(
            operation='read_sensor',
            hardware_id=self.sensor_id
        )
        
        try:
            # Attempt to read sensor
            value = self.hardware_adapter.analog_read(self.sensor_id)
            
            # Validate reading
            if not self._validate_reading(value):
                raise SensorException(
                    f"Invalid reading from {self.sensor_id}: {value}",
                    severity=HardwareErrorSeverity.WARNING
                )
                
            # Update cache
            self.last_good_value = value
            self.last_read_time = datetime.now()
            
            return {
                'value': value,
                'timestamp': self.last_read_time,
                'source': 'sensor',
                'quality': 'good'
            }
            
        except Exception as e:
            # Let error handler try recovery
            result = self.error_handler.handle_error(e, context)
            
            if result is not None:
                return result
            else:
                # Use cached value if available
                if self.last_good_value is not None:
                    age = (datetime.now() - self.last_read_time).seconds
                    if age < 300:  # Use cache if less than 5 minutes old
                        return {
                            'value': self.last_good_value,
                            'timestamp': self.last_read_time,
                            'source': 'cache',
                            'quality': 'stale',
                            'age': age
                        }
                        
                raise  # Re-raise if no recovery possible
                
    def _validate_reading(self, value: float) -> bool:
        """Validate sensor reading is reasonable"""
        # Example validation - customize per sensor type
        return 0 <= value <= 1.0
        
    def _use_predicted_value(self) -> Dict[str, Any]:
        """Fallback: predict value based on history"""
        # Simple prediction - in reality would use proper algorithm
        if self.last_good_value is not None:
            predicted = self.last_good_value + random.uniform(-0.05, 0.05)
            return {
                'value': max(0, min(1, predicted)),
                'timestamp': datetime.now(),
                'source': 'predicted',
                'quality': 'estimated'
            }
        return None


# Integration with main Environment class

class RobustEnvironment:
    """Environment with comprehensive error handling"""
    
    def __init__(self):
        self.error_handler = HardwareErrorHandler()
        self.sensors = {}
        self.health_status = {}
        
    def add_sensor(self, sensor_id: str, **kwargs):
        """Add sensor with error handling"""
        try:
            sensor = RobustSensorReader(sensor_id, self.hardware_adapter)
            self.sensors[sensor_id] = sensor
            self.health_status[sensor_id] = 'healthy'
        except Exception as e:
            logger.error(f"Failed to add sensor {sensor_id}: {e}")
            self.health_status[sensor_id] = 'failed'
            
    def read_all_sensors(self) -> Dict[str, Any]:
        """Read all sensors with graceful degradation"""
        readings = {}
        
        for sensor_id, sensor in self.sensors.items():
            try:
                readings[sensor_id] = sensor.read_sensor()
            except Exception as e:
                logger.error(f"Failed to read {sensor_id}: {e}")
                self.health_status[sensor_id] = 'degraded'
                # Continue reading other sensors
                
        return readings
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        total_sensors = len(self.sensors)
        healthy = sum(1 for s in self.health_status.values() if s == 'healthy')
        degraded = sum(1 for s in self.health_status.values() if s == 'degraded')
        failed = sum(1 for s in self.health_status.values() if s == 'failed')
        
        if failed > total_sensors * 0.5:
            overall = 'critical'
        elif degraded > total_sensors * 0.3:
            overall = 'degraded'
        elif healthy == total_sensors:
            overall = 'healthy'
        else:
            overall = 'warning'
            
        return {
            'overall': overall,
            'total_sensors': total_sensors,
            'healthy': healthy,
            'degraded': degraded,
            'failed': failed,
            'details': self.health_status.copy()
        }


if __name__ == "__main__":
    # Example: Using robust error handling
    from osce.hardware.mock_adapter import MockHardwareAdapter
    
    # Create environment with error handling
    env = RobustEnvironment()
    
    # Add mock hardware
    mock = MockHardwareAdapter(failure_mode=True)  # Enable random failures
    env.hardware_adapter = mock
    
    # Add sensors
    env.add_sensor('temperature')
    env.add_sensor('humidity')
    
    # Read sensors multiple times
    for i in range(10):
        print(f"\n--- Reading {i+1} ---")
        readings = env.read_all_sensors()
        
        for sensor_id, data in readings.items():
            print(f"{sensor_id}: {data}")
            
        health = env.get_system_health()
        print(f"System health: {health['overall']}")
        
        time.sleep(2)
