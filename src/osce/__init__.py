"""Minimal OSCE core package."""

from . import hardware
from .hardware import *
from .core import LivingQuantumMonitor, PlanetaryOptimizerV3

class Node:
    """Simple representation of a hardware node."""

    def __init__(self, name: str):
        self.name = name
        self.sensors = []
        self.actuators = []

    def add_sensor(self, name: str, **kwargs):
        self.sensors.append({'name': name, **kwargs})

    def add_actuator(self, name: str, **kwargs):
        self.actuators.append({'name': name, **kwargs})


class Environment:
    """Simplified environment manager used in examples."""

    def __init__(self, name: str = "OSCE Environment"):
        self.name = name
        self.nodes = {}
        self.plugins = []

    def auto_setup(self):
        # Placeholder for auto-detection logic
        print("[OSCE] Auto setup complete")

    def start(self):
        print(f"[OSCE] Environment '{self.name}' started")

    def add_sensor(self, name: str, **kwargs):
        node = self.nodes.setdefault('local', Node('local'))
        node.add_sensor(name, **kwargs)

    def add_actuator(self, name: str, **kwargs):
        node = self.nodes.setdefault('local', Node('local'))
        node.add_actuator(name, **kwargs)

    def add_remote_node(self, name: str, type: str, address: str = "") -> Node:
        node = Node(name)
        self.nodes[name] = node
        return node

    def add_plugin(self, plugin_name: str):
        self.plugins.append(plugin_name)

    install_plugin = add_plugin  # alias used in example

    def enable_redundancy(self):
        print("[OSCE] Redundancy enabled")

    def enable_data_backup(self):
        print("[OSCE] Data backup enabled")

    def get_summary(self) -> dict:
        return {
            'nodes': list(self.nodes.keys()),
            'plugins': self.plugins,
        }

__all__ = [
    'Environment',
    'Node',
    'LivingQuantumMonitor',
    'PlanetaryOptimizerV3',
] + hardware.__all__
