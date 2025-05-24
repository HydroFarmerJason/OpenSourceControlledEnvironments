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
            click.echo(' Database connection: OK')
        except Exception as e:
            click.echo(f' Database connection: {e}', err=True)
        
        # Check sensors
        from farm.sensors import sensor_manager
        sensor_status = sensor_manager.check_all_sensors()
        for sensor_id, status in sensor_status.items():
            if status['healthy']:
                click.echo(f' Sensor {sensor_id}: OK')
            else:
                click.echo(f' Sensor {sensor_id}: {status["error"]}', err=True)


if __name__ == '__main__':
    cli()


