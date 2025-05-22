#!/usr/bin/env python3
"""
Container Farm Control System - REST API
This lightweight API exposes sensor readings and simple
control commands from the local system. It is intended
as a foundation for mobile apps or third party services.
"""

from flask import Flask, jsonify, request
import json
import os
from middleware.auth import require_api_key

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), '..', 'config', 'user_choices.json')


def load_data():
    """Load sensor data from a JSON file (placeholder)."""
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


@app.route('/api/status', methods=['GET'])
@require_api_key
def status():
    """Return basic system status."""
    data = load_data()
    return jsonify({
        'status': 'ok',
        'data': data
    })


@app.route('/api/control/<string:output>', methods=['POST'])
@require_api_key
def control(output):
    """Placeholder route to toggle an output."""
    action = request.json.get('action', 'toggle')
    # This is only a placeholder; real implementation would
    # interface with Mycodo or GPIO to control hardware.
    return jsonify({
        'output': output,
        'action': action,
        'success': True
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

