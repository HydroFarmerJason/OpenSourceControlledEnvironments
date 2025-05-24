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
