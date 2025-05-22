import time
from functools import wraps
from flask import request, abort

# Simple in-memory rate limiting
REQUEST_LIMIT = 60  # requests
WINDOW_SIZE = 60  # seconds

# Dictionary to store request counters per IP
_request_log = {}


def rate_limit(func):
    """Limit the number of requests per IP address."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        ip = request.remote_addr or 'anonymous'
        now = time.time()
        entry = _request_log.get(ip)
        if entry:
            count, first_ts = entry
            if now - first_ts <= WINDOW_SIZE:
                if count >= REQUEST_LIMIT:
                    abort(429)
                _request_log[ip] = (count + 1, first_ts)
            else:
                _request_log[ip] = (1, now)
        else:
            _request_log[ip] = (1, now)
        return func(*args, **kwargs)

    return wrapper
