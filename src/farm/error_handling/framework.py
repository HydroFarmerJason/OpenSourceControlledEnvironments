# error_handling/framework.py
"""
Production-ready error handling framework for OpenSourceControlledEnvironments
Provides centralized error management, logging, and recovery mechanisms
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Callable, List
from enum import Enum
from functools import wraps
import json

from flask import Flask, jsonify, request


class ErrorSeverity(Enum):
    """Error severity levels"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better organization"""
    SENSOR = "sensor"
    ACTUATOR = "actuator"
    DATABASE = "database"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    CONFIGURATION = "configuration"
    HARDWARE = "hardware"
    USER_INPUT = "user_input"
    SYSTEM = "system"


class FarmSystemError(Exception):
    """Base exception class for all farm system errors"""
    
    def __init__(self, 
                 message: str,
                 category: ErrorCategory = ErrorCategory.SYSTEM,
                 severity: ErrorSeverity = ErrorSeverity.ERROR,
                 error_code: Optional[str] = None,
                 details: Optional[Dict[str, Any]] = None,
                 recovery_action: Optional[str] = None):
        self.message = message
        self.category = category
        self.severity = severity
        self.error_code = error_code or f"{category.value.upper()}_ERROR"
        self.details = details or {}
        self.recovery_action = recovery_action
        self.timestamp = datetime.utcnow()
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for logging/API responses"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'category': self.category.value,
            'severity': self.severity.value,
            'details': self.details,
            'recovery_action': self.recovery_action,
            'timestamp': self.timestamp.isoformat()
        }


# Specific error types
class SensorError(FarmSystemError):
    """Sensor-specific errors"""
    def __init__(self, sensor_id: str, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.SENSOR,
            details={'sensor_id': sensor_id},
            **kwargs
        )


class ActuatorError(FarmSystemError):
    """Actuator-specific errors"""
    def __init__(self, actuator_id: str, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.ACTUATOR,
            details={'actuator_id': actuator_id},
            **kwargs
        )


class DatabaseError(FarmSystemError):
    """Database-specific errors"""
    def __init__(self, message: str, query: Optional[str] = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.DATABASE,
            details={'query': query} if query else {},
            **kwargs
        )


class HardwareError(FarmSystemError):
    """Hardware-specific errors"""
    def __init__(self, component: str, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.HARDWARE,
            details={'component': component},
            **kwargs
        )


class ConfigurationError(FarmSystemError):
    """Configuration-specific errors"""
    def __init__(self, config_item: str, message: str, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            details={'config_item': config_item},
            **kwargs
        )


class ErrorHandler:
    """Central error handling and logging system"""
    
    def __init__(self, app: Flask = None, log_file: str = 'farm_system.log'):
        self.app = app
        self.error_log = []
        self.recovery_strategies = {}
        self.error_callbacks = {}
        
        # Configure logging
        self.logger = self._setup_logging(log_file)
        
        if app:
            self.init_app(app)
    
    def _setup_logging(self, log_file: str) -> logging.Logger:
        """Configure logging system"""
        logger = logging.getLogger('FarmSystem')
        logger.setLevel(logging.DEBUG)
        
        # File handler with rotation
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def init_app(self, app: Flask):
        """Initialize error handling for Flask app"""
        self.app = app
        
        # Register error handlers
        app.register_error_handler(FarmSystemError, self._handle_farm_error)
        app.register_error_handler(404, self._handle_404)
        app.register_error_handler(500, self._handle_500)
        app.register_error_handler(Exception, self._handle_generic_error)
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context"""
        error_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': type(error).__name__,
            'message': str(error),
            'context': context or {}
        }
        
        if isinstance(error, FarmSystemError):
            error_data.update(error.to_dict())
            log_level = getattr(logging, error.severity.value.upper())
        else:
            error_data['traceback'] = traceback.format_exc()
            log_level = logging.ERROR
        
        # Log to file
        self.logger.log(log_level, json.dumps(error_data))
        
        # Keep in memory for recent errors
        self.error_log.append(error_data)
        if len(self.error_log) > 1000:
            self.error_log.pop(0)
        
        # Execute callbacks
        self._execute_error_callbacks(error, error_data)
        
        return error_data
    
    def register_recovery_strategy(self, error_type: type, strategy: Callable):
        """Register automatic recovery strategy for error type"""
        self.recovery_strategies[error_type.__name__] = strategy
    
    def register_error_callback(self, category: ErrorCategory, callback: Callable):
        """Register callback for specific error category"""
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)
    
    def _execute_error_callbacks(self, error: Exception, error_data: Dict[str, Any]):
        """Execute registered callbacks for error"""
        if isinstance(error, FarmSystemError):
            callbacks = self.error_callbacks.get(error.category, [])
            for callback in callbacks:
                try:
                    callback(error, error_data)
                except Exception as e:
                    self.logger.error(f"Error callback failed: {e}")
    
    def attempt_recovery(self, error: Exception) -> bool:
        """Attempt automatic recovery for error"""
        error_type = type(error).__name__
        if error_type in self.recovery_strategies:
            try:
                strategy = self.recovery_strategies[error_type]
                strategy(error)
                self.logger.info(f"Successfully recovered from {error_type}")
                return True
            except Exception as e:
                self.logger.error(f"Recovery failed for {error_type}: {e}")
        return False
    
    def _handle_farm_error(self, error: FarmSystemError):
        """Handle FarmSystemError in Flask"""
        error_data = self.log_error(error, {'request_path': request.path})
        
        # Attempt recovery
        if error.recovery_action:
            self.attempt_recovery(error)
        
        return jsonify({
            'error': error_data,
            'success': False
        }), self._get_status_code(error.severity)
    
    def _handle_404(self, error):
        """Handle 404 errors"""
        return jsonify({
            'error': {
                'code': 'NOT_FOUND',
                'message': 'Resource not found',
                'path': request.path
            },
            'success': False
        }), 404
    
    def _handle_500(self, error):
        """Handle 500 errors"""
        error_data = self.log_error(error, {'request_path': request.path})
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred',
                'reference': error_data['timestamp']
            },
            'success': False
        }), 500
    
    def _handle_generic_error(self, error):
        """Handle generic exceptions"""
        error_data = self.log_error(error, {
            'request_path': request.path,
            'request_method': request.method
        })
        return jsonify({
            'error': {
                'code': 'SYSTEM_ERROR',
                'message': 'An unexpected error occurred',
                'reference': error_data['timestamp']
            },
            'success': False
        }), 500
    
    def _get_status_code(self, severity: ErrorSeverity) -> int:
        """Map error severity to HTTP status code"""
        mapping = {
            ErrorSeverity.WARNING: 200,
            ErrorSeverity.ERROR: 400,
            ErrorSeverity.CRITICAL: 500
        }
        return mapping.get(severity, 500)
    
    def get_recent_errors(self, 
                         category: Optional[ErrorCategory] = None,
                         severity: Optional[ErrorSeverity] = None,
                         limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent errors with optional filtering"""
        errors = self.error_log[-limit:]
        
        if category:
            errors = [e for e in errors if e.get('category') == category.value]
        
        if severity:
            errors = [e for e in errors if e.get('severity') == severity.value]
        
        return errors


# Decorators for error handling
def handle_errors(recovery_action: Optional[str] = None):
    """Decorator to handle errors in functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except FarmSystemError:
                raise  # Re-raise farm system errors
            except Exception as e:
                # Convert to FarmSystemError
                raise FarmSystemError(
                    message=f"Error in {func.__name__}: {str(e)}",
                    details={'function': func.__name__, 'original_error': str(e)},
                    recovery_action=recovery_action
                )
        return wrapper
    return decorator


def retry_on_error(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry function on error"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_error = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        raise
            
            raise last_error
        return wrapper
    return decorator


class ErrorMonitor:
    """Monitor system health based on errors"""
    
    def __init__(self, error_handler: ErrorHandler):
        self.error_handler = error_handler
        self.health_thresholds = {
            ErrorSeverity.WARNING: 50,
            ErrorSeverity.ERROR: 10,
            ErrorSeverity.CRITICAL: 1
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Calculate system health based on recent errors"""
        recent_errors = self.error_handler.get_recent_errors(limit=100)
        
        # Count errors by severity
        severity_counts = {}
        for error in recent_errors:
            severity = error.get('severity', 'unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Calculate health score
        health_score = 100
        for severity, threshold in self.health_thresholds.items():
            count = severity_counts.get(severity.value, 0)
            if count > threshold:
                health_score -= (count - threshold) * (10 if severity == ErrorSeverity.WARNING else 20)
        
        health_score = max(0, health_score)
        
        # Determine status
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        elif health_score >= 50:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'status': status,
            'health_score': health_score,
            'error_counts': severity_counts,
            'recent_errors': recent_errors[:10]
        }
    
    def check_component_health(self, category: ErrorCategory) -> Dict[str, Any]:
        """Check health of specific component"""
        recent_errors = self.error_handler.get_recent_errors(category=category, limit=50)
        
        error_rate = len(recent_errors)
        if error_rate == 0:
            status = "healthy"
        elif error_rate < 5:
            status = "warning"
        else:
            status = "critical"
        
        return {
            'component': category.value,
            'status': status,
            'error_count': error_rate,
            'last_error': recent_errors[0] if recent_errors else None
        }


# Example recovery strategies
class RecoveryStrategies:
    """Common recovery strategies for different error types"""
    
    @staticmethod
    def sensor_recovery(error: SensorError):
        """Recovery strategy for sensor errors"""
        sensor_id = error.details.get('sensor_id')
        
        # Log recovery attempt
        logging.info(f"Attempting recovery for sensor {sensor_id}")
        
        # Restart sensor
        # In real implementation, this would restart the actual sensor
        logging.info(f"Restarting sensor {sensor_id}")
        
        # Recalibrate if needed
        if "calibration" in error.message.lower():
            logging.info(f"Recalibrating sensor {sensor_id}")
    
    @staticmethod
    def network_recovery(error: FarmSystemError):
        """Recovery strategy for network errors"""
        import time
        
        # Wait and retry
        logging.info("Network error detected, waiting 30 seconds before retry")
        time.sleep(30)
        
        # In real implementation, would check network connectivity
        logging.info("Checking network connectivity")
    
    @staticmethod
    def database_recovery(error: DatabaseError):
        """Recovery strategy for database errors"""
        # In real implementation, would attempt to reconnect to database
        logging.info("Attempting database reconnection")


# Example usage
if __name__ == '__main__':
    app = Flask(__name__)
    error_handler = ErrorHandler(app)
    
    # Register recovery strategies
    error_handler.register_recovery_strategy(SensorError, RecoveryStrategies.sensor_recovery)
    error_handler.register_recovery_strategy(DatabaseError, RecoveryStrategies.database_recovery)
    
    # Example route with error handling
    @app.route('/api/sensor/<sensor_id>')
    @handle_errors(recovery_action="restart_sensor")
    def get_sensor_data(sensor_id):
        # Simulate sensor read
        if sensor_id == 'bad':
            raise SensorError(
                sensor_id=sensor_id,
                message="Sensor not responding",
                recovery_action="restart_sensor"
            )
        
        return jsonify({'sensor_id': sensor_id, 'value': 22.5})