class OSCEPlugin:
    """Base class for OSCE plugins."""

    def __init__(self, app):
        self.app = app
        self.name = getattr(self, 'name', self.__class__.__name__)
        self.version = getattr(self, 'version', '0.1.0')
        self.active = False

    def activate(self):
        """Called when plugin is activated."""
        self.active = True

    def deactivate(self):
        """Called when plugin is deactivated."""
        self.active = False

    def register_api(self, route, view_func, methods=('GET',)):
        """Register a Flask route provided by the plugin."""
        self.app.add_url_rule(route, view_func.__name__, view_func, methods=methods)

    def register_widget(self, widget_id, render_func):
        """Placeholder for registering dashboard widgets."""
        if not hasattr(self.app, 'widgets'):
            self.app.widgets = {}
        self.app.widgets[widget_id] = render_func

