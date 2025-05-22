from functools import wraps
from flask import request, abort

ALLOWED_ACTIONS = {'toggle', 'on', 'off'}


def require_json(func):
    """Ensure the request contains JSON."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        if not request.is_json:
            abort(400)
        return func(*args, **kwargs)

    return wrapper


def validate_control_action(func):
    """Validate action field for /api/control."""

    @wraps(func)
    def wrapper(output, *args, **kwargs):
        data = request.get_json() or {}
        action = data.get('action', 'toggle')
        if action not in ALLOWED_ACTIONS:
            abort(400)
        return func(output, *args, **kwargs)

    return wrapper
