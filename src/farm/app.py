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
from farm.plugins import PluginManager


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

    # Initialize plugins
    plugin_dir = app.config.get('PLUGIN_DIR', os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plugins'))
    app.plugin_manager = PluginManager(app, plugin_dir)
    app.plugin_manager.load_plugins()
    
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


