from farm.plugins import OSCEPlugin
from datetime import datetime, timedelta

class TemperatureAlertPlugin(OSCEPlugin):
    """Send alerts when temperature goes out of range."""

    name = "Temperature Alert"
    version = "1.0.0"
    description = "Get alerts when temperature is out of range"

    def __init__(self, app):
        super().__init__(app)
        self.last_alert = {}

    def activate(self):
        super().activate()
        # register example API endpoint
        self.register_api('/api/plugins/temp-alert/status', self.get_status)

    def get_status(self):
        return {
            'active': self.active,
            'time': datetime.now().isoformat()
        }
