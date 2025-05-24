import structlog

def get_logger(name: str):
    """Return a structlog logger."""
    return structlog.get_logger(name)
