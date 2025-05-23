import importlib.util
import json
import os
from types import ModuleType
from .base import OSCEPlugin


class PluginManager:
    """Simple plugin loader and manager."""

    def __init__(self, app, plugin_dir):
        self.app = app
        self.plugin_dir = plugin_dir
        self.plugins = {}

    def load_plugins(self):
        if not os.path.isdir(self.plugin_dir):
            return

        for name in os.listdir(self.plugin_dir):
            path = os.path.join(self.plugin_dir, name)
            plugin_file = os.path.join(path, 'plugin.py')
            if not os.path.isfile(plugin_file):
                continue

            module = self._load_module(name, plugin_file)
            plugin_class = self._find_plugin_class(module)
            if plugin_class is None:
                continue

            plugin = plugin_class(self.app)
            manifest_path = os.path.join(path, 'plugin.json')
            if os.path.isfile(manifest_path):
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    plugin.manifest = json.load(f)
            plugin.activate()
            self.plugins[name] = plugin

    def _load_module(self, name: str, path: str) -> ModuleType:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def _find_plugin_class(self, module: ModuleType):
        for attr in dir(module):
            obj = getattr(module, attr)
            if isinstance(obj, type) and issubclass(obj, OSCEPlugin) and obj is not OSCEPlugin:
                return obj
        return None
