from functools import wraps
from flask import request, abort
import os

API_KEY = os.environ.get("API_KEY")

def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if API_KEY:
            provided = request.headers.get("X-API-Key")
            if not provided or provided != API_KEY:
                abort(401)
        return func(*args, **kwargs)
    return wrapper
