# === src/farm/__init__.py ===
"""
OpenSource Controlled Environments
Production-ready controlled environment agriculture system
"""

__version__ = "1.0.0"
__author__ = "HydroFarmerJason"

# === src/farm/app.py ===
"""
Main application factory and configuration
"""

import os
import logging
import platform
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from farm.database import db, migrate
from farm.security.config import create_secure_app, AuthenticationManager
from farm.error_handling.framework import ErrorHandler
from farm.api import api_bp
from farm.monitoring import init_monitoring


def create_app(config_name='production'):
    """Create and configure Flask application"""
    
    # Create secure app with authentication
    app = create_secure_app()
    
    # Load configuration
    app.config.from_object(f'farm.config.{config_name}')
    
    # Initialize extensions
    CORS(app, origins=app.config.get('CORS_ORIGINS', ['*']))
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Initialize error handling
    error_handler = ErrorHandler(app)
    app.error_handler = error_handler
    
    # Initialize monitoring
    init_monitoring(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """System health check endpoint"""
        try:
            # Check database
            db.session.execute('SELECT 1')
            db_status = 'healthy'
        except Exception as e:
            db_status = f'unhealthy: {str(e)}'
        
        # Get system health from error monitor
        system_health = app.error_handler.error_monitor.get_system_health()
        
        return jsonify({
            'status': system_health['status'],
            'version': __version__,
            'database': db_status,
            'health_score': system_health['health_score'],
            'components': {
                'api': 'healthy',
                'database': db_status,
                'sensors': 'healthy',  # In production, check actual sensors
                'actuators': 'healthy'  # In production, check actual actuators
            }
        })
    
    # Version endpoint
    @app.route('/version')
    def version():
        return jsonify({
            'version': __version__,
            'api_version': 'v1',
            'python_version': platform.python_version()
        })
    
    return app


# === src/farm/config.py ===
"""
Application configuration
"""

import os
from datetime import timedelta


class Config:
    """Base configuration"""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///farm_data.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
    
    # Celery
    CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Hardware
    GPIO_MODE = os.getenv('GPIO_MODE', 'BCM')
    MOCK_HARDWARE = os.getenv('MOCK_HARDWARE', 'False').lower() == 'true'
    
    # Monitoring
    PROMETHEUS_PORT = int(os.getenv('PROMETHEUS_PORT', '9090'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/var/log/farm/app.log')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    MOCK_HARDWARE = True


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    MOCK_HARDWARE = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Stricter security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'


# === src/farm/api/__init__.py ===
"""
API Blueprint and routes
"""

from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from flask_restx import Api, Resource, fields, Namespace

from farm.security.config import require_auth, require_role
from farm.sensors import sensor_manager
from farm.actuators import actuator_manager
from farm.controllers import automation_controller

# Create blueprint
api_bp = Blueprint('api', __name__)

# Create API with documentation
api = Api(
    api_bp,
    version='1.0',
    title='OpenSource Controlled Environments API',
    description='Control and monitor your growing environment',
    doc='/docs'
)

# Namespaces
sensors_ns = api.namespace('sensors', description='Sensor operations')
actuators_ns = api.namespace('actuators', description='Actuator operations')
automation_ns = api.namespace('automation', description='Automation control')
system_ns = api.namespace('system', description='System operations')

# Models
sensor_model = api.model('Sensor', {
    'id': fields.String(required=True, description='Sensor ID'),
    'type': fields.String(required=True, description='Sensor type'),
    'value': fields.Float(required=True, description='Current value'),
    'unit': fields.String(required=True, description='Measurement unit'),
    'timestamp': fields.DateTime(required=True, description='Reading timestamp'),
    'status': fields.String(description='Sensor status')
})

actuator_model = api.model('Actuator', {
    'id': fields.String(required=True, description='Actuator ID'),
    'type': fields.String(required=True, description='Actuator type'),
    'state': fields.String(required=True, description='Current state'),
    'value': fields.Float(description='Current value (if applicable)'),
    'timestamp': fields.DateTime(required=True, description='Last update timestamp')
})

# Sensor endpoints
@sensors_ns.route('/')
class SensorList(Resource):
    @require_auth
    @api.doc('list_sensors')
    @api.marshal_list_with(sensor_model)
    def get(self):
        """List all sensors"""
        return sensor_manager.get_all_sensors()


@sensors_ns.route('/<string:sensor_id>')
@api.param('sensor_id', 'The sensor identifier')
class Sensor(Resource):
    @require_auth
    @api.doc('get_sensor')
    @api.marshal_with(sensor_model)
    def get(self, sensor_id):
        """Get sensor reading"""
        sensor_data = sensor_manager.get_sensor_reading(sensor_id)
        if not sensor_data:
            api.abort(404, f"Sensor {sensor_id} not found")
        return sensor_data


@sensors_ns.route('/<string:sensor_id>/history')
@api.param('sensor_id', 'The sensor identifier')
class SensorHistory(Resource):
    @require_auth
    @api.doc('get_sensor_history')
    def get(self, sensor_id):
        """Get sensor history"""
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        limit = request.args.get('limit', 100, type=int)
        
        history = sensor_manager.get_sensor_history(
            sensor_id, start_time, end_time, limit
        )
        return jsonify(history)


# Actuator endpoints
@actuators_ns.route('/')
class ActuatorList(Resource):
    @require_auth
    @api.doc('list_actuators')
    @api.marshal_list_with(actuator_model)
    def get(self):
        """List all actuators"""
        return actuator_manager.get_all_actuators()


@actuators_ns.route('/<string:actuator_id>')
@api.param('actuator_id', 'The actuator identifier')
class Actuator(Resource):
    @require_auth
    @api.doc('get_actuator')
    @api.marshal_with(actuator_model)
    def get(self, actuator_id):
        """Get actuator state"""
        actuator_data = actuator_manager.get_actuator_state(actuator_id)
        if not actuator_data:
            api.abort(404, f"Actuator {actuator_id} not found")
        return actuator_data
    
    @require_auth
    @api.doc('control_actuator')
    def post(self, actuator_id):
        """Control actuator"""
        data = request.get_json()
        action = data.get('action')  # 'on', 'off', 'set'
        value = data.get('value')
        
        result = actuator_manager.control_actuator(actuator_id, action, value)
        if not result:
            api.abort(400, "Failed to control actuator")
        
        return jsonify(result)


# Automation endpoints
@automation_ns.route('/rules')
class AutomationRules(Resource):
    @require_auth
    @api.doc('list_automation_rules')
    def get(self):
        """List automation rules"""
        return jsonify(automation_controller.get_rules())
    
    @require_role('admin')
    @api.doc('create_automation_rule')
    def post(self):
        """Create automation rule"""
        data = request.get_json()
        rule = automation_controller.create_rule(data)
        return jsonify(rule), 201


@automation_ns.route('/rules/<string:rule_id>')
@api.param('rule_id', 'The rule identifier')
class AutomationRule(Resource):
    @require_auth
    @api.doc('get_automation_rule')
    def get(self, rule_id):
        """Get automation rule"""
        rule = automation_controller.get_rule(rule_id)
        if not rule:
            api.abort(404, f"Rule {rule_id} not found")
        return jsonify(rule)
    
    @require_role('admin')
    @api.doc('update_automation_rule')
    def put(self, rule_id):
        """Update automation rule"""
        data = request.get_json()
        rule = automation_controller.update_rule(rule_id, data)
        if not rule:
            api.abort(404, f"Rule {rule_id} not found")
        return jsonify(rule)
    
    @require_role('admin')
    @api.doc('delete_automation_rule')
    def delete(self, rule_id):
        """Delete automation rule"""
        if automation_controller.delete_rule(rule_id):
            return '', 204
        api.abort(404, f"Rule {rule_id} not found")


# System endpoints
@system_ns.route('/status')
class SystemStatus(Resource):
    @require_auth
    @api.doc('get_system_status')
    def get(self):
        """Get system status"""
        return jsonify({
            'sensors': sensor_manager.get_status(),
            'actuators': actuator_manager.get_status(),
            'automation': automation_controller.get_status(),
            'timestamp': datetime.utcnow().isoformat()
        })


@system_ns.route('/logs')
class SystemLogs(Resource):
    @require_role('admin')
    @api.doc('get_system_logs')
    def get(self):
        """Get recent system logs"""
        limit = request.args.get('limit', 100, type=int)
        category = request.args.get('category')
        severity = request.args.get('severity')
        
        logs = current_app.error_handler.get_recent_errors(
            category=category,
            severity=severity,
            limit=limit
        )
        return jsonify(logs)


@system_ns.route('/backup')
class SystemBackup(Resource):
    @require_role('admin')
    @api.doc('trigger_backup')
    def post(self):
        """Trigger system backup"""
        backup_type = request.get_json().get('type', 'manual')
        # In production, this would trigger the backup script
        return jsonify({
            'message': 'Backup initiated',
            'type': backup_type,
            'timestamp': datetime.utcnow().isoformat()
        }), 202


# === src/farm/cli.py ===
"""
Command-line interface for farm management
"""

import click
import sys
from flask.cli import FlaskGroup

from farm.app import create_app
from farm.database import db


def create_cli_app():
    """Create app for CLI"""
    return create_app('development')


cli = FlaskGroup(create_app=create_cli_app)


@cli.command()
def init_db():
    """Initialize the database"""
    click.echo('Initializing database...')
    db.create_all()
    click.echo('Database initialized.')


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
def run_api(host, port):
    """Run the API server"""
    app = create_app()
    app.run(host=host, port=port)


@cli.command()
def test():
    """Run tests"""
    import pytest
    
    click.echo('Running tests...')
    result = pytest.main(['-v', 'tests/'])
    sys.exit(result)


@cli.command()
def check_health():
    """Check system health"""
    app = create_app()
    with app.app_context():
        # Check database
        try:
            db.session.execute('SELECT 1')
            click.echo('✓ Database connection: OK')
        except Exception as e:
            click.echo(f'✗ Database connection: {e}', err=True)
        
        # Check sensors
        from farm.sensors import sensor_manager
        sensor_status = sensor_manager.check_all_sensors()
        for sensor_id, status in sensor_status.items():
            if status['healthy']:
                click.echo(f'✓ Sensor {sensor_id}: OK')
            else:
                click.echo(f'✗ Sensor {sensor_id}: {status["error"]}', err=True)


if __name__ == '__main__':
    cli()


# === run.py ===
"""
Entry point for running the application
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from farm.app import create_app

# Create application
app = create_app(os.getenv('FARM_ENV', 'production'))

if __name__ == '__main__':
    # Run with production server in production
    if app.config['DEBUG']:
        app.run(
            host=os.getenv('API_HOST', '0.0.0.0'),
            port=int(os.getenv('API_PORT', 5000)),
            debug=True
        )
    else:
        # Use gunicorn in production
        import multiprocessing
        
        bind = f"{os.getenv('API_HOST', '0.0.0.0')}:{os.getenv('API_PORT', '5000')}"
        workers = multiprocessing.cpu_count() * 2 + 1
        
        os.system(f"gunicorn -b {bind} -w {workers} 'farm.app:create_app()'")
