"""
PulseROS Integration Module for Robotics Hardware Control
Version: 1.0
Description: Integrates PulseMesh with ROS for distributed robotic control,
             implementing redundancy, power management, care-based task scheduling,
             and specialized gardening functionality.
"""

import os
import time
import json
import logging
import uuid
import asyncio
import numpy as np
import threading
import queue
from enum import Enum, auto
from typing import Dict, List, Tuple, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
import hashlib
import base64
import socket
import math
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import traceback

# Import from PulseMesh Integration Module
from PulseMesh import (
    CommunicationLayer, MessageIntent, TransmissionPriority, EmotionalVector,
    PulseMeshMessage, NodeState, FoldMemory, WifiMeshLayer, BLEProximityLayer,
    SyncthingMemoryLayer, PulseMeshFederatedNode, ScaleLevel, FoldPattern
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pulse_ros_integration")

# ==== 1. EXTENDED MESSAGE TYPES FOR ROBOTICS ====

class RoboticsMessageIntent(Enum):
    """Extended intent types for robotics messages."""
    TASK_ASSIGNMENT = auto()       # Assign task to a node
    TASK_STATUS = auto()           # Report task status
    MOTION_COMMAND = auto()        # Command robot movement
    SENSOR_DATA = auto()           # Share sensor data
    ACTUATOR_COMMAND = auto()      # Command an actuator
    POWER_STATUS = auto()          # Report power status
    FAILOVER_REQUEST = auto()      # Request node failover
    CARE_SCHEDULE = auto()         # Share care scheduling
    GARDEN_UPDATE = auto()         # Update on garden state
    PLANT_DATA = auto()            # Plant-specific data
    ENVIRONMENT_DATA = auto()      # Environmental data
    HARDWARE_STATUS = auto()       # Report hardware status
    USER_INTERACTION = auto()      # User interaction event


class TaskPriority(Enum):
    """Priority levels for robotic tasks."""
    CRITICAL = 0        # Health and safety critical
    CARE = 1            # Care-based tasks (watering plants, etc.)
    SCHEDULED = 2       # Regular scheduled tasks
    USER_REQUESTED = 3  # Tasks requested by users
    MAINTENANCE = 4     # System maintenance
    LEARNING = 5        # Learning and exploration
    IDLE = 6            # Background/idle tasks


class TaskStatus(Enum):
    """Status of a robotic task."""
    PENDING = auto()    # Awaiting execution
    ASSIGNED = auto()   # Assigned to a node
    EXECUTING = auto()  # Currently executing
    PAUSED = auto()     # Temporarily paused
    COMPLETED = auto()  # Successfully completed
    FAILED = auto()     # Failed to complete
    CANCELLED = auto()  # Cancelled before completion


class PowerMode(Enum):
    """Power consumption modes for the system."""
    FULL = auto()        # Full power utilization
    BALANCED = auto()    # Balanced power usage
    ECO = auto()         # Power-saving mode
    MINIMAL = auto()     # Minimal functionality
    EMERGENCY = auto()   # Emergency power only


class NodeRole(Enum):
    """Roles a node can have in the system."""
    COORDINATOR = auto()  # System coordination
    PERCEPTION = auto()   # Sensing and perception
    MOTION = auto()       # Motion control
    MANIPULATION = auto() # Physical manipulation
    INTERACTION = auto()  # User interaction
    COMPUTATION = auto()  # Computational tasks
    MEMORY = auto()       # Data storage and recall
    POWER = auto()        # Power management
    REDUNDANCY = auto()   # Backup/redundancy


@dataclass
class RoboticTask:
    """Task information for robotic operations."""
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: str = ""  # gardening, mobility, social, etc.
    priority: TaskPriority = TaskPriority.SCHEDULED
    status: TaskStatus = TaskStatus.PENDING
    assigned_node: Optional[str] = None
    parent_task: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: float = 300.0  # seconds
    estimated_power: float = 1.0  # normalized
    creation_time: float = field(default_factory=time.time)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    schedule_time: Optional[float] = None
    expiration_time: Optional[float] = None
    progress: float = 0.0  # 0.0 to 1.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "task_id": self.task_id,
            "name": self.name,
            "description": self.description,
            "task_type": self.task_type,
            "priority": self.priority.name,
            "status": self.status.name,
            "assigned_node": self.assigned_node,
            "parent_task": self.parent_task,
            "subtasks": self.subtasks,
            "dependencies": self.dependencies,
            "estimated_duration": self.estimated_duration,
            "estimated_power": self.estimated_power,
            "creation_time": self.creation_time,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "schedule_time": self.schedule_time,
            "expiration_time": self.expiration_time,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
            "tags": self.tags,
            "metadata": self.metadata
        }
        
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'RoboticTask':
        """Create from JSON string."""
        data = json.loads(json_str)
        
        # Convert enum values from string
        priority = TaskPriority[data.get("priority", "SCHEDULED")]
        status = TaskStatus[data.get("status", "PENDING")]
        
        # Create task
        task = cls(
            task_id=data.get("task_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            description=data.get("description", ""),
            task_type=data.get("task_type", ""),
            priority=priority,
            status=status,
            assigned_node=data.get("assigned_node"),
            parent_task=data.get("parent_task"),
            subtasks=data.get("subtasks", []),
            dependencies=data.get("dependencies", []),
            estimated_duration=data.get("estimated_duration", 300.0),
            estimated_power=data.get("estimated_power", 1.0),
            creation_time=data.get("creation_time", time.time()),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            schedule_time=data.get("schedule_time"),
            expiration_time=data.get("expiration_time"),
            progress=data.get("progress", 0.0),
            result=data.get("result"),
            error=data.get("error"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {})
        )
        
        return task
    
    def update_status(self, status: TaskStatus, progress: Optional[float] = None, 
                     result: Optional[Dict[str, Any]] = None, 
                     error: Optional[str] = None) -> None:
        """
        Update task status, progress, and results.
        
        Args:
            status: New task status
            progress: Optional progress update (0.0-1.0)
            result: Optional task result
            error: Optional error message
        """
        self.status = status
        
        if progress is not None:
            self.progress = min(1.0, max(0.0, progress))
            
        if result is not None:
            self.result = result
            
        if error is not None:
            self.error = error
            
        # Update timestamps
        if status == TaskStatus.EXECUTING and self.start_time is None:
            self.start_time = time.time()
            
        elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED] and self.end_time is None:
            self.end_time = time.time()
    
    def is_critical(self) -> bool:
        """Check if task is critical."""
        return self.priority == TaskPriority.CRITICAL or self.priority == TaskPriority.CARE
    
    def is_care_task(self) -> bool:
        """Check if task is care-related."""
        return self.priority == TaskPriority.CARE or "care" in self.tags
    
    def is_expired(self) -> bool:
        """Check if task is expired."""
        return self.expiration_time is not None and time.time() > self.expiration_time
    
    def can_execute(self) -> bool:
        """Check if task can be executed (dependencies met)."""
        # TODO: Verify dependencies
        return True
    
    def estimated_completion_time(self) -> float:
        """Estimate completion time based on progress."""
        if self.start_time is None:
            return 0.0
            
        elapsed = time.time() - self.start_time
        
        if self.progress <= 0.01:
            # Just started, use full estimate
            return self.start_time + self.estimated_duration
            
        # Estimate based on current progress
        total_estimated = elapsed / self.progress
        return self.start_time + total_estimated


@dataclass
class SensorData:
    """Sensor data container."""
    sensor_id: str
    sensor_type: str  # temperature, humidity, moisture, etc.
    value: float
    unit: str
    timestamp: float = field(default_factory=time.time)
    location: Optional[str] = None
    valid: bool = True
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.__dict__)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SensorData':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class ActuatorCommand:
    """Command for an actuator."""
    actuator_id: str
    command: str  # on, off, move, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    priority: TransmissionPriority = TransmissionPriority.NORMAL
    expiration: Optional[float] = None
    requester_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "actuator_id": self.actuator_id,
            "command": self.command,
            "parameters": self.parameters,
            "timestamp": self.timestamp,
            "priority": self.priority.name,
            "expiration": self.expiration,
            "requester_id": self.requester_id,
            "metadata": self.metadata
        }
        
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ActuatorCommand':
        """Create from JSON string."""
        data = json.loads(json_str)
        
        # Convert enum value from string
        priority = TransmissionPriority[data.get("priority", "NORMAL")]
        
        # Create command
        command = cls(
            actuator_id=data.get("actuator_id", ""),
            command=data.get("command", ""),
            parameters=data.get("parameters", {}),
            timestamp=data.get("timestamp", time.time()),
            priority=priority,
            expiration=data.get("expiration"),
            requester_id=data.get("requester_id"),
            metadata=data.get("metadata", {})
        )
        
        return command
    
    def is_expired(self) -> bool:
        """Check if command is expired."""
        return self.expiration is not None and time.time() > self.expiration


@dataclass
class PlantData:
    """Plant information for gardening tasks."""
    plant_id: str
    name: str
    scientific_name: Optional[str] = None
    type: str = "unknown"  # vegetable, herb, flower, etc.
    location: Optional[str] = None
    planted_date: Optional[float] = None
    last_watered: Optional[float] = None
    last_fertilized: Optional[float] = None
    moisture_target: Tuple[float, float] = (0.4, 0.7)  # min, max
    light_target: Tuple[float, float] = (0.3, 0.8)  # min, max
    temperature_target: Tuple[float, float] = (15.0, 30.0)  # min, max Celsius
    humidity_target: Tuple[float, float] = (0.3, 0.7)  # min, max
    watering_frequency: int = 86400  # seconds (default: daily)
    fertilizing_frequency: int = 2592000  # seconds (default: monthly)
    growth_stage: str = "seedling"  # seedling, growing, mature, flowering, fruiting
    health_status: str = "good"  # good, needs_attention, stressed, diseased
    notes: List[str] = field(default_factory=list)
    care_history: List[Dict[str, Any]] = field(default_factory=list)
    image_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        data = {
            "plant_id": self.plant_id,
            "name": self.name,
            "scientific_name": self.scientific_name,
            "type": self.type,
            "location": self.location,
            "planted_date": self.planted_date,
            "last_watered": self.last_watered,
            "last_fertilized": self.last_fertilized,
            "moisture_target": self.moisture_target,
            "light_target": self.light_target,
            "temperature_target": self.temperature_target,
            "humidity_target": self.humidity_target,
            "watering_frequency": self.watering_frequency,
            "fertilizing_frequency": self.fertilizing_frequency,
            "growth_stage": self.growth_stage,
            "health_status": self.health_status,
            "notes": self.notes,
            "care_history": self.care_history,
            "image_path": self.image_path,
            "metadata": self.metadata
        }
        
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'PlantData':
        """Create from JSON string."""
        data = json.loads(json_str)
        
        # Convert tuples from lists if necessary
        moisture_target = tuple(data.get("moisture_target", (0.4, 0.7)))
        light_target = tuple(data.get("light_target", (0.3, 0.8)))
        temperature_target = tuple(data.get("temperature_target", (15.0, 30.0)))
        humidity_target = tuple(data.get("humidity_target", (0.3, 0.7)))
        
        # Create plant data
        plant = cls(
            plant_id=data.get("plant_id", ""),
            name=data.get("name", ""),
            scientific_name=data.get("scientific_name"),
            type=data.get("type", "unknown"),
            location=data.get("location"),
            planted_date=data.get("planted_date"),
            last_watered=data.get("last_watered"),
            last_fertilized=data.get("last_fertilized"),
            moisture_target=moisture_target,
            light_target=light_target,
            temperature_target=temperature_target,
            humidity_target=humidity_target,
            watering_frequency=data.get("watering_frequency", 86400),
            fertilizing_frequency=data.get("fertilizing_frequency", 2592000),
            growth_stage=data.get("growth_stage", "seedling"),
            health_status=data.get("health_status", "good"),
            notes=data.get("notes", []),
            care_history=data.get("care_history", []),
            image_path=data.get("image_path"),
            metadata=data.get("metadata", {})
        )
        
        return plant
    
    def needs_water(self) -> bool:
        """Check if plant needs water based on last watering."""
        if self.last_watered is None:
            return True
            
        time_since_watering = time.time() - self.last_watered
        return time_since_watering >= self.watering_frequency
    
    def needs_fertilizer(self) -> bool:
        """Check if plant needs fertilizer based on last application."""
        if self.last_fertilized is None:
            return True
            
        time_since_fertilizing = time.time() - self.last_fertilized
        return time_since_fertilizing >= self.fertilizing_frequency
    
    def record_watering(self, amount: float = 0.0, notes: Optional[str] = None) -> None:
        """Record a watering event."""
        self.last_watered = time.time()
        
        # Add to care history
        self.care_history.append({
            "type": "watering",
            "timestamp": self.last_watered,
            "amount": amount,
            "notes": notes
        })
    
    def record_fertilizing(self, type: str = "general", amount: float = 0.0, 
                         notes: Optional[str] = None) -> None:
        """Record a fertilizing event."""
        self.last_fertilized = time.time()
        
        # Add to care history
        self.care_history.append({
            "type": "fertilizing",
            "fertilizer_type": type,
            "timestamp": self.last_fertilized,
            "amount": amount,
            "notes": notes
        })
    
    def update_health(self, status: str, notes: Optional[str] = None) -> None:
        """Update plant health status."""
        self.health_status = status
        
        # Add to care history
        self.care_history.append({
            "type": "health_update",
            "timestamp": time.time(),
            "status": status,
            "notes": notes
        })
        
        if notes:
            self.notes.append(notes)


# ==== 2. ROS BRIDGE IMPLEMENTATION ====

class PulseROSBridge:
    """Bridge between PulseMesh and ROS for hardware control."""
    
    def __init__(self, 
                node_id: str,
                node_name: str,
                mesh_node: PulseMeshFederatedNode,
                ros_node_name: str = "pulse_ros_bridge",
                device_type: str = "primary",  # primary, backup, etc.
                roles: List[NodeRole] = None,
                capabilities: List[str] = None):
        """
        Initialize ROS bridge.
        
        Args:
            node_id: Unique identifier for this node
            node_name: Human-readable name
            mesh_node: PulseMesh node to connect to
            ros_node_name: ROS node name
            device_type: Type of device (primary, backup)
            roles: Roles this node can fulfill
            capabilities: List of capabilities this node provides
        """
        self.node_id = node_id
        self.node_name = node_name
        self.mesh_node = mesh_node
        self.ros_node_name = ros_node_name
        self.device_type = device_type
        self.roles = roles or [NodeRole.MOTION]
        self.capabilities = capabilities or ["base_control"]
        
        # ROS components
        self.node = None
        self.publishers = {}
        self.subscribers = {}
        self.services = {}
        self.action_clients = {}
        self.action_servers = {}
        self.tf_broadcaster = None
        self.tf_listener = None
        
        # Hardware control components
        self.motors = {}
        self.servos = {}
        self.sensors = {}
        self.cameras = {}
        
        # Parameters
        self.parameters = {}
        
        # Status tracking
        self.is_active = False
        self.is_primary = (device_type == "primary")
        self.battery_level = 1.0
        self.system_temperature = 25.0
        
        # Task management
        self.task_queue = asyncio.PriorityQueue()
        self.current_task = None
        self.task_processor = None
        self.completed_tasks = []
        
        # Message handlers
        self.message_handlers = {}
        
        # Function maps
        self.actuator_functions = {}
        self.sensor_functions = {}
        self.motion_functions = {}
        
        # Heartbeat
        self.heartbeat_task = None
        self.heartbeat_interval = 1.0  # seconds
        
        # Import ROS if available
        self.ros_available = False
        try:
            import rclpy
            from rclpy.node import Node
            self.rclpy = rclpy
            self.Node = Node
            self.ros_available = True
        except ImportError:
            logger.warning("ROS 2 (rclpy) not available, using simulation mode")
            
            # Create simulation environment
            self.simulation_data = {
                "position": (0.0, 0.0, 0.0),
                "orientation": (0.0, 0.0, 0.0, 1.0),
                "velocity": (0.0, 0.0, 0.0),
                "sensors": {},
                "actuators": {},
                "battery": 1.0,
                "temperature": 25.0
            }
    
    async def initialize(self) -> bool:
        """
        Initialize ROS bridge.
        
        Returns:
            Success status
        """
        try:
            # Set up ROS
            if self.ros_available:
                # Initialize ROS
                self.rclpy.init()
                
                # Create node
                self.node = self.Node(self.ros_node_name)
                
                # Set up publishers
                self.publishers["status"] = self.node.create_publisher(
                    self.get_ros_msg_type("String"), f"{self.ros_node_name}/status", 10)
                    
                # Set up subscribers
                self.subscribers["command"] = self.node.create_subscription(
                    self.get_ros_msg_type("String"), f"{self.ros_node_name}/command",
                    self.ros_command_callback, 10)
                
                # Create executor in separate thread
                self.ros_executor = self.rclpy.executors.SingleThreadedExecutor()
                self.ros_executor.add_node(self.node)
                self.ros_thread = threading.Thread(target=self.ros_spin)
                self.ros_thread.daemon = True
                self.ros_thread.start()
            else:
                # Simulated initialization
                logger.info("Initializing simulated ROS environment")
                
            # Register message handlers
            self._register_message_handlers()
            
            # Start heartbeat
            self.heartbeat_task = asyncio.create_task(self._send_heartbeat())
            
            # Start task processor
            self.task_processor = asyncio.create_task(self._process_tasks())
            
            # Mark as active
            self.is_active = True
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing ROS bridge: {e}")
            traceback.print_exc()
            return False
    
    async def shutdown(self) -> bool:
        """
        Shutdown ROS bridge.
        
        Returns:
            Success status
        """
        try:
            # Stop heartbeat
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass
                    
            # Stop task processor
            if self.task_processor:
                self.task_processor.cancel()
                try:
                    await self.task_processor
                except asyncio.CancelledError:
                    pass
                    
            # Shutdown ROS
            if self.ros_available and self.node:
                self.node.destroy_node()
                self.rclpy.shutdown()
                
                # Wait for thread to end
                if hasattr(self, 'ros_thread') and self.ros_thread.is_alive():
                    self.ros_thread.join(timeout=2.0)
                    
            # Mark as inactive
            self.is_active = False
            
            return True
            
        except Exception as e:
            logger.error(f"Error shutting down ROS bridge: {e}")
            return False
    
    def get_ros_msg_type(self, type_name: str):
        """
        Get ROS message type.
        
        Args:
            type_name: Name of message type
            
        Returns:
            ROS message type
        """
        if not self.ros_available:
            return None
            
        # Import standard message types
        if type_name == "String":
            from std_msgs.msg import String
            return String
        elif type_name == "Bool":
            from std_msgs.msg import Bool
            return Bool
        elif type_name == "Int32":
            from std_msgs.msg import Int32
            return Int32
        elif type_name == "Float32":
            from std_msgs.msg import Float32
            return Float32
        elif type_name == "Twist":
            from geometry_msgs.msg import Twist
            return Twist
        elif type_name == "PoseStamped":
            from geometry_msgs.msg import PoseStamped
            return PoseStamped
        elif type_name == "LaserScan":
            from sensor_msgs.msg import LaserScan
            return LaserScan
        elif type_name == "Image":
            from sensor_msgs.msg import Image
            return Image
        elif type_name == "JointState":
            from sensor_msgs.msg import JointState
            return JointState
        elif type_name == "BatteryState":
            from sensor_msgs.msg import BatteryState
            return BatteryState
        elif type_name == "Temperature":
            from sensor_msgs.msg import Temperature
            return Temperature
        elif type_name == "RelativeHumidity":
            from sensor_msgs.msg import RelativeHumidity
            return RelativeHumidity
        else:
            logger.warning(f"Unknown ROS message type: {type_name}")
            return None
    
    def ros_spin(self):
        """ROS spin function for thread."""
        try:
            while self.ros_available and self.is_active and self.rclpy.ok():
                self.ros_executor.spin_once(timeout_sec=0.1)
                time.sleep(0.01)
        except Exception as e:
            logger.error(f"Error in ROS spin thread: {e}")
    
    def ros_command_callback(self, msg):
        """
        ROS command callback.
        
        Args:
            msg: ROS message
        """
        try:
            # Parse command
            command_str = msg.data
            command_data = json.loads(command_str)
            
            # Extract command info
            command_type = command_data.get("type", "unknown")
            command_params = command_data.get("params", {})
            
            logger.info(f"Received ROS command: {command_type}")
            
            # Handle different command types
            if command_type == "move":
                # Extract movement parameters
                linear = command_params.get("linear", {"x": 0.0, "y": 0.0, "z": 0.0})
                angular = command_params.get("angular", {"x": 0.0, "y": 0.0, "z": 0.0})
                
                # Send move command
                asyncio.run(self.move_robot(
                    linear_x=linear.get("x", 0.0),
                    linear_y=linear.get("y", 0.0),
                    linear_z=linear.get("z", 0.0),
                    angular_x=angular.get("x", 0.0),
                    angular_y=angular.get("y", 0.0),
                    angular_z=angular.get("z", 0.0)
                ))
                
            elif command_type == "actuator":
                # Extract actuator parameters
                actuator_id = command_params.get("id", "")
                action = command_params.get("action", "")
                params = command_params.get("params", {})
                
                # Send actuator command
                asyncio.run(self.control_actuator(
                    actuator_id=actuator_id,
                    command=action,
                    parameters=params
                ))
                
            elif command_type == "task":
                # Extract task parameters
                task_name = command_params.get("name", "")
                task_type = command_params.get("task_type", "")
                priority = command_params.get("priority", "SCHEDULED")
                
                # Create task
                task = RoboticTask(
                    name=task_name,
                    task_type=task_type,
                    priority=TaskPriority[priority],
                    description=command_params.get("description", ""),
                    estimated_duration=command_params.get("duration", 300.0)
                )
                
                # Add task
                asyncio.run(self.add_task(task))
                
            else:
                logger.warning(f"Unknown command type: {command_type}")
                
        except Exception as e:
            logger.error(f"Error handling ROS command: {e}")
    
    async def move_robot(self, linear_x: float = 0.0, linear_y: float = 0.0, linear_z: float = 0.0,
                      angular_x: float = 0.0, angular_y: float = 0.0, angular_z: float = 0.0,
                      frame_id: str = "base_link", duration: float = 0.0) -> bool:
        """
        Send movement command to the robot.
        
        Args:
            linear_x: Linear velocity in x (forward/backward)
            linear_y: Linear velocity in y (left/right)
            linear_z: Linear velocity in z (up/down)
            angular_x: Angular velocity around x
            angular_y: Angular velocity around y
            angular_z: Angular velocity around z (rotation)
            frame_id: Reference frame
            duration: Movement duration (0.0 = indefinite)
            
        Returns:
            Success status
        """
        try:
            # Create movement command
            if self.ros_available:
                # Create ROS Twist message
                from geometry_msgs.msg import Twist
                
                twist = Twist()
                twist.linear.x = float(linear_x)
                twist.linear.y = float(linear_y)
                twist.linear.z = float(linear_z)
                twist.angular.x = float(angular_x)
                twist.angular.y = float(angular_y)
                twist.angular.z = float(angular_z)
                
                # Find cmd_vel publisher or create one
                if "cmd_vel" not in self.publishers:
                    self.publishers["cmd_vel"] = self.node.create_publisher(
                        Twist, "cmd_vel", 10)
                    
                # Publish command
                self.publishers["cmd_vel"].publish(twist)
                
                # If duration specified, schedule stop
                if duration > 0.0:
                    asyncio.create_task(self._timed_stop(duration))
                    
            else:
                # Simulated movement
                logger.info(f"Simulated movement: linear=({linear_x}, {linear_y}, {linear_z}), "
                          f"angular=({angular_x}, {angular_y}, {angular_z})")
                
                # Update simulation state
                self.simulation_data["velocity"] = (linear_x, linear_y, linear_z)
                
                # If duration specified, schedule stop
                if duration > 0.0:
                    asyncio.create_task(self._timed_stop(duration))
            
            # Create and send PulseMesh message
            message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=MessageIntent.STATE_BROADCAST,
                priority=TransmissionPriority.NORMAL,
                content=f"Robot moving: linear=({linear_x}, {linear_y}, {linear_z}), "
                       f"angular=({angular_x}, {angular_y}, {angular_z})",
                metadata={
                    "movement": {
                        "linear": {"x": linear_x, "y": linear_y, "z": linear_z},
                        "angular": {"x": angular_x, "y": angular_y, "z": angular_z},
                        "frame_id": frame_id,
                        "duration": duration
                    },
                    "timestamp": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending move command: {e}")
            return False
    
    async def _timed_stop(self, duration: float) -> None:
        """
        Stop robot after specified duration.
        
        Args:
            duration: Duration in seconds
        """
        await asyncio.sleep(duration)
        await self.move_robot(0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    
    async def control_actuator(self, actuator_id: str, command: str, 
                            parameters: Dict[str, Any] = None) -> bool:
        """
        Control a robot actuator.
        
        Args:
            actuator_id: Identifier for the actuator
            command: Command to send
            parameters: Command parameters
            
        Returns:
            Success status
        """
        try:
            # Get parameters
            params = parameters or {}
            
            # Create actuator command
            actuator_command = ActuatorCommand(
                actuator_id=actuator_id,
                command=command,
                parameters=params,
                requester_id=self.node_id
            )
            
            # Check if we have a function for this actuator
            if actuator_id in self.actuator_functions:
                # Call function
                function = self.actuator_functions[actuator_id]
                success = await function(command, params)
                
                if not success:
                    logger.warning(f"Actuator function failed: {actuator_id}/{command}")
                    return False
                    
            elif self.ros_available:
                # Use ROS to control actuator
                # Implementation depends on actuator type
                if actuator_id.startswith("joint_"):
                    # Joint control
                    joint_name = actuator_id[6:]  # Remove "joint_" prefix
                    position = params.get("position", 0.0)
                    velocity = params.get("velocity", 0.0)
                    effort = params.get("effort", 0.0)
                    
                    # Find joint publisher or create one
                    topic = f"joint_cmd/{joint_name}"
                    if topic not in self.publishers:
                        from std_msgs.msg import Float64
                        self.publishers[topic] = self.node.create_publisher(
                            Float64, topic, 10)
                        
                    # Publish command
                    from std_msgs.msg import Float64
                    msg = Float64()
                    
                    if command == "position":
                        msg.data = float(position)
                    elif command == "velocity":
                        msg.data = float(velocity)
                    else:
                        msg.data = float(params.get("value", 0.0))
                        
                    self.publishers[topic].publish(msg)
                    
                elif actuator_id.startswith("gpio_"):
                    # GPIO control
                    pin = actuator_id[5:]  # Remove "gpio_" prefix
                    value = params.get("value", 0)
                    
                    # Find GPIO publisher or create one
                    topic = f"gpio/{pin}"
                    if topic not in self.publishers:
                        from std_msgs.msg import Bool
                        self.publishers[topic] = self.node.create_publisher(
                            Bool, topic, 10)
                        
                    # Publish command
                    from std_msgs.msg import Bool
                    msg = Bool()
                    msg.data = bool(value)
                    self.publishers[topic].publish(msg)
                    
                else:
                    # Generic actuator
                    # Create service client if needed
                    service_name = f"actuator/{actuator_id}"
                    
                    logger.warning(f"No implementation for actuator: {actuator_id}")
                    return False
                    
            else:
                # Simulated actuator
                logger.info(f"Simulated actuator command: {actuator_id}/{command} - {params}")
                
                # Update simulation state
                if "actuators" not in self.simulation_data:
                    self.simulation_data["actuators"] = {}
                    
                self.simulation_data["actuators"][actuator_id] = {
                    "command": command,
                    "parameters": params,
                    "timestamp": time.time()
                }
            
            # Create and send PulseMesh message
            message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=RoboticsMessageIntent.ACTUATOR_COMMAND,
                priority=TransmissionPriority.NORMAL,
                content=f"Actuator command: {actuator_id}/{command}",
                metadata={
                    "actuator_command": actuator_command.__dict__,
                    "timestamp": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error controlling actuator: {e}")
            return False
    
    async def read_sensor(self, sensor_id: str, parameters: Dict[str, Any] = None) -> Optional[SensorData]:
        """
        Read data from a sensor.
        
        Args:
            sensor_id: Identifier for the sensor
            parameters: Read parameters
            
        Returns:
            Sensor data or None if failed
        """
        try:
            # Get parameters
            params = parameters or {}
            
            # Check if we have a function for this sensor
            if sensor_id in self.sensor_functions:
                # Call function
                function = self.sensor_functions[sensor_id]
                return await function(params)
                
            elif self.ros_available:
                # Use ROS to read sensor
                # Implementation depends on sensor type
                if sensor_id.startswith("camera_"):
                    # Not implemented - would use image subscription
                    logger.warning(f"Camera sensor not implemented: {sensor_id}")
                    return None
                    
                else:
                    # Generic sensor - try to find topic
                    topic = f"sensor/{sensor_id}"
                    
                    # Check if we have recent data
                    if hasattr(self, 'sensor_data') and sensor_id in self.sensor_data:
                        sensor_data = self.sensor_data[sensor_id]
                        
                        # Check if data is recent enough
                        if time.time() - sensor_data.timestamp < 5.0:
                            return sensor_data
                            
                    logger.warning(f"No recent data for sensor: {sensor_id}")
                    return None
                    
            else:
                # Simulated sensor
                logger.info(f"Simulated sensor read: {sensor_id} - {params}")
                
                # Generate simulated data
                if sensor_id.startswith("temperature_"):
                    # Temperature sensor
                    location = sensor_id.split("_")[1] if "_" in sensor_id else "ambient"
                    base_temp = 22.0  # Room temperature
                    
                    # Add variation based on timestamp
                    variation = math.sin(time.time() / 3600.0) * 2.0  # +/- 2 degrees over an hour
                    
                    # Different base temperatures for different locations
                    if location == "soil":
                        base_temp = 18.0
                    elif location == "water":
                        base_temp = 20.0
                    elif location == "outdoor":
                        base_temp = 25.0
                        variation = math.sin(time.time() / 3600.0) * 5.0  # +/- 5 degrees outdoors
                        
                    temperature = base_temp + variation
                    
                    return SensorData(
                        sensor_id=sensor_id,
                        sensor_type="temperature",
                        value=temperature,
                        unit="celsius"
                    )
                    
                elif sensor_id.startswith("humidity_"):
                    # Humidity sensor
                    location = sensor_id.split("_")[1] if "_" in sensor_id else "ambient"
                    base_humidity = 0.5  # 50%
                    
                    # Add variation based on timestamp
                    variation = math.sin(time.time() / 7200.0) * 0.1  # +/- 10% over two hours
                    
                    # Different base humidity for different locations
                    if location == "soil":
                        base_humidity = 0.6
                    elif location == "greenhouse":
                        base_humidity = 0.7
                    elif location == "outdoor":
                        base_humidity = 0.4
                        
                    humidity = base_humidity + variation
                    
                    return SensorData(
                        sensor_id=sensor_id,
                        sensor_type="humidity",
                        value=humidity,
                        unit="relative"
                    )
                    
                elif sensor_id.startswith("moisture_"):
                    # Soil moisture sensor
                    plant_id = sensor_id.split("_")[1] if "_" in sensor_id else "generic"
                    
                    # Base moisture depends on when plant was last watered
                    # Here we simulate a plant that gradually dries out over 24 hours
                    # and is watered at random intervals
                    
                    # Generate a consistent pseudo-random timestamp for last watering
                    # based on plant_id so it's consistent between calls
                    watering_seed = sum(ord(c) for c in plant_id)
                    last_watered = time.time() - (watering_seed % 86400)  # Within last 24 hours
                    
                    # Calculate moisture based on time since watering
                    # Starts at 0.8 (80%) and drops to 0.2 (20%) over 24 hours
                    time_since_watering = time.time() - last_watered
                    moisture = max(0.2, 0.8 - (time_since_watering / 86400.0) * 0.6)
                    
                    return SensorData(
                        sensor_id=sensor_id,
                        sensor_type="moisture",
                        value=moisture,
                        unit="relative"
                    )
                    
                elif sensor_id.startswith("light_"):
                    # Light sensor
                    location = sensor_id.split("_")[1] if "_" in sensor_id else "ambient"
                    
                    # Simulate day/night cycle - assuming 24 hour cycle starting at midnight
                    current_time = datetime.now()
                    hour = current_time.hour + current_time.minute / 60.0
                    
                    # Peak light at noon, dark at night (0-1 scale)
                    if hour < 6 or hour > 18:  # Night time (6 PM to 6 AM)
                        light = 0.0
                    else:
                        # Parabolic curve peaking at noon
                        normalized_hour = (hour - 6) / 12.0  # 0 to 1 from 6 AM to 6 PM
                        light = math.sin(normalized_hour * math.pi) * 0.9 + 0.1  # 0.1 to 1.0
                        
                    # Adjust for location
                    if location == "indoor":
                        light *= 0.6  # Reduced indoor light
                    elif location == "shade":
                        light *= 0.3  # Heavily reduced in shade
                        
                    return SensorData(
                        sensor_id=sensor_id,
                        sensor_type="light",
                        value=light,
                        unit="relative"
                    )
                    
                elif sensor_id == "battery":
                    # Battery sensor
                    return SensorData(
                        sensor_id=sensor_id,
                        sensor_type="battery",
                        value=self.battery_level,
                        unit="percentage"
                    )
                    
                else:
                    # Unknown sensor type - return random value
                    return SensorData(
                        sensor_id=sensor_id,
                        sensor_type="unknown",
                        value=random.random(),
                        unit="unitless",
                        confidence=0.5
                    )
            
            return None
            
        except Exception as e:
            logger.error(f"Error reading sensor: {e}")
            return None
    
    async def capture_image(self, camera_id: str = "main", 
                         parameters: Dict[str, Any] = None) -> Optional[str]:
        """
        Capture an image from a camera.
        
        Args:
            camera_id: Identifier for the camera
            parameters: Capture parameters
            
        Returns:
            Path to image file or None if failed
        """
        try:
            # Get parameters
            params = parameters or {}
            resolution = params.get("resolution", (640, 480))
            format = params.get("format", "jpg")
            save_path = params.get("save_path", f"/tmp/pulse_image_{int(time.time())}.{format}")
            
            if self.ros_available:
                # Use ROS to capture image
                # This would typically subscribe to a camera topic
                # and save the image when received
                logger.warning("ROS image capture not implemented")
                return None
                
            else:
                # Simulated image capture
                logger.info(f"Simulated image capture: {camera_id} - {resolution}")
                
                # Pretend we saved an image
                return save_path
                
            return None
            
        except Exception as e:
            logger.error(f"Error capturing image: {e}")
            return None
    
    async def add_task(self, task: RoboticTask) -> bool:
        """
        Add a task to the queue.
        
        Args:
            task: Task to add
            
        Returns:
            Success status
        """
        try:
            # Make sure task has an ID
            if not task.task_id:
                task.task_id = str(uuid.uuid4())
                
            # Set initial status if not set
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.ASSIGNED
                task.assigned_node = self.node_id
                
            # Add to queue with priority
            await self.task_queue.put((task.priority.value, time.time(), task))
            
            # Notify about new task
            message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=RoboticsMessageIntent.TASK_ASSIGNMENT,
                priority=TransmissionPriority.NORMAL,
                content=f"Task assigned: {task.name}",
                metadata={
                    "task_id": task.task_id,
                    "task_name": task.name,
                    "task_type": task.task_type,
                    "priority": task.priority.name,
                    "assigned_node": task.assigned_node
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding task: {e}")
            return False
    
    async def _process_tasks(self) -> None:
        """Process tasks from the queue."""
        while self.is_active:
            try:
                # Skip if currently executing a task
                if self.current_task is not None:
                    # Check if current task is complete
                    if self.current_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                        # Add to completed tasks
                        self.completed_tasks.append(self.current_task)
                        
                        # Trim completed tasks if too many
                        if len(self.completed_tasks) > 100:
                            self.completed_tasks = self.completed_tasks[-100:]
                            
                        # Clear current task
                        self.current_task = None
                    else:
                        # Still executing
                        await asyncio.sleep(0.1)
                        continue
                        
                # Get next task
                try:
                    _, _, task = await asyncio.wait_for(self.task_queue.get(), timeout=0.5)
                except asyncio.TimeoutError:
                    # No task available
                    await asyncio.sleep(0.1)
                    continue
                    
                # Set as current task
                self.current_task = task
                
                # Update status
                task.update_status(TaskStatus.EXECUTING)
                
                # Create task execution task
                asyncio.create_task(self._execute_task(task))
                
                # Mark as done
                self.task_queue.task_done()
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error processing tasks: {e}")
                await asyncio.sleep(1.0)
    
    async def _execute_task(self, task: RoboticTask) -> None:
        """
        Execute a specific task.
        
        Args:
            task: Task to execute
        """
        try:
            # Notify about task start
            message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=RoboticsMessageIntent.TASK_STATUS,
                priority=TransmissionPriority.NORMAL,
                content=f"Task started: {task.name}",
                metadata={
                    "task_id": task.task_id,
                    "task_name": task.name,
                    "task_type": task.task_type,
                    "status": TaskStatus.EXECUTING.name,
                    "start_time": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(message)
            
            # Execute based on task type
            success = False
            result = {}
            
            if task.task_type == "move_to":
                # Movement task
                x = task.metadata.get("x", 0.0)
                y = task.metadata.get("y", 0.0)
                theta = task.metadata.get("theta", 0.0)
                
                # Simple movement - in a real system, would use navigation
                success = await self.move_robot(
                    linear_x=0.2 if x > 0 else -0.2 if x < 0 else 0.0,
                    linear_y=0.2 if y > 0 else -0.2 if y < 0 else 0.0,
                    angular_z=0.2 if theta > 0 else -0.2 if theta < 0 else 0.0,
                    duration=5.0
                )
                
                result = {"moved": success}
                
            elif task.task_type == "water_plant":
                # Plant watering task
                plant_id = task.metadata.get("plant_id", "")
                amount = task.metadata.get("amount", 100.0)  # ml
                
                # Execute watering sequence
                if plant_id:
                    # 1. Move to plant
                    await self.move_robot(linear_x=0.2, duration=2.0)
                    
                    # 2. Activate water pump
                    await self.control_actuator(
                        actuator_id="water_pump",
                        command="on",
                        parameters={"duration": amount / 50.0}  # 50 ml/s
                    )
                    
                    # 3. Wait for completion
                    await asyncio.sleep(amount / 50.0 + 1.0)
                    
                    # 4. Update plant record
                    # In a real system, would update plant database
                    success = True
                    result = {"watered": True, "amount": amount}
                else:
                    success = False
                    result = {"error": "Missing plant ID"}
                    
            elif task.task_type == "scan_plants":
                # Plant scanning task
                # 1. Move to scanning position
                await self.move_robot(linear_x=0.2, duration=2.0)
                
                # 2. Capture image if camera available
                image_path = await self.capture_image()
                
                # 3. Read environmental sensors
                temp_data = await self.read_sensor("temperature_ambient")
                humidity_data = await self.read_sensor("humidity_ambient")
                light_data = await self.read_sensor("light_ambient")
                
                # Package results
                sensor_data = {}
                if temp_data:
                    sensor_data["temperature"] = temp_data.value
                if humidity_data:
                    sensor_data["humidity"] = humidity_data.value
                if light_data:
                    sensor_data["light"] = light_data.value
                    
                success = True
                result = {
                    "image_path": image_path,
                    "sensor_data": sensor_data,
                    "timestamp": time.time()
                }
                
            else:
                # Unknown task type
                logger.warning(f"Unknown task type: {task.task_type}")
                success = False
                result = {"error": f"Unknown task type: {task.task_type}"}
                
            # Update task status
            if success:
                task.update_status(TaskStatus.COMPLETED, 1.0, result)
            else:
                task.update_status(TaskStatus.FAILED, task.progress, result, 
                                 f"Failed to execute task: {task.task_type}")
                
            # Notify about task completion
            message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=RoboticsMessageIntent.TASK_STATUS,
                priority=TransmissionPriority.NORMAL,
                content=f"Task {'completed' if success else 'failed'}: {task.name}",
                metadata={
                    "task_id": task.task_id,
                    "task_name": task.name,
                    "task_type": task.task_type,
                    "status": task.status.name,
                    "result": result,
                    "end_time": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(message)
            
        except Exception as e:
            logger.error(f"Error executing task {task.task_id}: {e}")
            
            # Update task status
            task.update_status(TaskStatus.FAILED, task.progress, {}, str(e))
            
            # Notify about failure
            message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=RoboticsMessageIntent.TASK_STATUS,
                priority=TransmissionPriority.NORMAL,
                content=f"Task failed: {task.name}",
                metadata={
                    "task_id": task.task_id,
                    "task_name": task.name,
                    "task_type": task.task_type,
                    "status": TaskStatus.FAILED.name,
                    "error": str(e),
                    "end_time": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(message)
    
    async def _send_heartbeat(self) -> None:
        """Send periodic heartbeat."""
        while self.is_active:
            try:
                # Update battery and temperature
                if not self.ros_available:
                    # Simulate battery discharge (very slow)
                    self.battery_level = max(0.0, self.battery_level - 0.0001)
                    
                    # Simulate temperature variations
                    self.system_temperature = 25.0 + math.sin(time.time() / 600.0) * 2.0
                    
                # Create heartbeat message
                message = PulseMeshMessage(
                    sender_id=self.node_id,
                    sender_name=self.node_name,
                    layer=CommunicationLayer.WIFI_MESH,
                    intent=RoboticsMessageIntent.HARDWARE_STATUS,
                    priority=TransmissionPriority.NORMAL,
                    content=f"Hardware status: {self.device_type}",
                    metadata={
                        "device_type": self.device_type,
                        "roles": [role.name for role in self.roles],
                        "capabilities": self.capabilities,
                        "is_active": self.is_active,
                        "is_primary": self.is_primary,
                        "battery_level": self.battery_level,
                        "system_temperature": self.system_temperature,
                        "current_task": self.current_task.task_id if self.current_task else None,
                        "task_queue_size": self.task_queue.qsize(),
                        "timestamp": time.time()
                    }
                )
                
                await self.mesh_node.wifi_layer.send_message(message)
                
                # Wait for next heartbeat
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error sending heartbeat: {e}")
                await asyncio.sleep(1.0)
    
    def _register_message_handlers(self) -> None:
        """Register message handlers."""
        # Register ROS-specific handlers
        if hasattr(self.mesh_node, 'wifi_layer'):
            self.mesh_node.wifi_layer.register_handler(
                RoboticsMessageIntent.TASK_ASSIGNMENT, self._handle_task_assignment)
            self.mesh_node.wifi_layer.register_handler(
                RoboticsMessageIntent.MOTION_COMMAND, self._handle_motion_command)
            self.mesh_node.wifi_layer.register_handler(
                RoboticsMessageIntent.ACTUATOR_COMMAND, self._handle_actuator_command)
            self.mesh_node.wifi_layer.register_handler(
                RoboticsMessageIntent.FAILOVER_REQUEST, self._handle_failover_request)
    
    def _handle_task_assignment(self, message: PulseMeshMessage) -> None:
        """
        Handle task assignment message.
        
        Args:
            message: Task assignment message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract task info
        task_id = message.metadata.get("task_id")
        assigned_node = message.metadata.get("assigned_node")
        
        # Skip if not assigned to us
        if assigned_node != self.node_id:
            return
            
        # Extract task details
        task_name = message.metadata.get("task_name", "")
        task_type = message.metadata.get("task_type", "")
        priority_name = message.metadata.get("priority", "SCHEDULED")
        
        try:
            # Convert priority string to enum
            priority = TaskPriority[priority_name]
        except KeyError:
            priority = TaskPriority.SCHEDULED
            
        # Create task
        task = RoboticTask(
            task_id=task_id,
            name=task_name,
            task_type=task_type,
            priority=priority,
            status=TaskStatus.ASSIGNED,
            assigned_node=self.node_id
        )
        
        # Add to queue
        asyncio.create_task(self.add_task(task))
    
    def _handle_motion_command(self, message: PulseMeshMessage) -> None:
        """
        Handle motion command message.
        
        Args:
            message: Motion command message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract movement info
        movement = message.metadata.get("movement", {})
        linear = movement.get("linear", {})
        angular = movement.get("angular", {})
        duration = movement.get("duration", 0.0)
        
        # Execute movement
        asyncio.create_task(self.move_robot(
            linear_x=linear.get("x", 0.0),
            linear_y=linear.get("y", 0.0),
            linear_z=linear.get("z", 0.0),
            angular_x=angular.get("x", 0.0),
            angular_y=angular.get("y", 0.0),
            angular_z=angular.get("z", 0.0),
            duration=duration
        ))
    
    def _handle_actuator_command(self, message: PulseMeshMessage) -> None:
        """
        Handle actuator command message.
        
        Args:
            message: Actuator command message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract actuator command
        actuator_data = message.metadata.get("actuator_command", {})
        actuator_id = actuator_data.get("actuator_id", "")
        command = actuator_data.get("command", "")
        parameters = actuator_data.get("parameters", {})
        
        # Execute command
        asyncio.create_task(self.control_actuator(
            actuator_id=actuator_id,
            command=command,
            parameters=parameters
        ))
    
    def _handle_failover_request(self, message: PulseMeshMessage) -> None:
        """
        Handle failover request message.
        
        Args:
            message: Failover request message
        """
        # Skip own messages or if not a backup
        if message.sender_id == self.node_id or self.device_type != "backup":
            return
            
        # Extract failover info
        failed_node = message.metadata.get("failed_node", "")
        capabilities = message.metadata.get("capabilities", [])
        
        # Check if we have matching capabilities
        if not any(cap in self.capabilities for cap in capabilities):
            return
            
        # Activate as primary
        self.is_primary = True
        
        logger.info(f"Activating as primary due to failover from {failed_node}")
        
        # Acknowledge failover
        asyncio.create_task(self._send_failover_acknowledgement(
            message.sender_id, failed_node))
    
    async def _send_failover_acknowledgement(self, requester_id: str, failed_node: str) -> None:
        """
        Send failover acknowledgement.
        
        Args:
            requester_id: ID of node that requested failover
            failed_node: ID of failed node
        """
        # Create acknowledgement message
        message = PulseMeshMessage(
            sender_id=self.node_id,
            sender_name=self.node_name,
            receiver_id=requester_id,
            layer=CommunicationLayer.WIFI_MESH,
            intent=RoboticsMessageIntent.HARDWARE_STATUS,
            priority=TransmissionPriority.HIGH,
            content=f"Failover activated: {self.node_name} taking over for {failed_node}",
            metadata={
                "failover_acknowledged": True,
                "failed_node": failed_node,
                "activated_node": self.node_id,
                "device_type": "primary",  # Now primary
                "roles": [role.name for role in self.roles],
                "capabilities": self.capabilities,
                "timestamp": time.time()
            }
        )
        
        await self.mesh_node.wifi_layer.send_message(message)


# ==== 3. HARDWARE REDUNDANCY SYSTEM ====

class PulseRedundancyManager:
    """Manages redundancy and failover between multiple hardware nodes."""
    
    def __init__(self, 
                node_id: str,
                node_name: str,
                mesh_node: PulseMeshFederatedNode,
                primary_nodes: Dict[str, Dict[str, Any]] = None,
                backup_nodes: Dict[str, Dict[str, Any]] = None,
                heartbeat_interval: float = 5.0):
        """
        Initialize redundancy manager.
        
        Args:
            node_id: Unique identifier for this manager
            node_name: Human-readable name
            mesh_node: PulseMesh node for communication
            primary_nodes: Dictionary of primary nodes by capability
            backup_nodes: Dictionary of backup nodes by capability
            heartbeat_interval: Interval for heartbeat checks
        """
        self.node_id = node_id
        self.node_name = node_name
        self.mesh_node = mesh_node
        self.primary_nodes = primary_nodes or {}
        self.backup_nodes = backup_nodes or {}
        self.heartbeat_interval = heartbeat_interval
        
        # Status tracking
        self.node_status = {}
        self.active_nodes = {}
        self.capability_map = {}
        
        # Initialize capability map
        for capability, nodes in self.primary_nodes.items():
            self.capability_map[capability] = {
                "primary": nodes,
                "backup": self.backup_nodes.get(capability, {})
            }
            
        # Failover handlers
        self.failover_handlers = {}
        
        # Task migration queue
        self.migration_queue = asyncio.Queue()
        
        # Internal state
        self.is_active = False
        self.monitor_task = None
        self.migration_task = None
    
    async def start(self) -> bool:
        """
        Start redundancy manager.
        
        Returns:
            Success status
        """
        try:
            # Register message handlers
            if hasattr(self.mesh_node, 'wifi_layer'):
                self.mesh_node.wifi_layer.register_handler(
                    RoboticsMessageIntent.HARDWARE_STATUS, self._handle_hardware_status)
                self.mesh_node.wifi_layer.register_handler(
                    RoboticsMessageIntent.TASK_STATUS, self._handle_task_status)
                
            # Start monitoring task
            self.monitor_task = asyncio.create_task(self._monitor_heartbeats())
            
            # Start migration task
            self.migration_task = asyncio.create_task(self._process_migrations())
            
            # Set active
            self.is_active = True
            
            logger.info(f"Redundancy manager started: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting redundancy manager: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop redundancy manager.
        
        Returns:
            Success status
        """
        try:
            # Set inactive
            self.is_active = False
            
            # Cancel tasks
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
                    
            if self.migration_task:
                self.migration_task.cancel()
                try:
                    await self.migration_task
                except asyncio.CancelledError:
                    pass
                    
            logger.info(f"Redundancy manager stopped: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping redundancy manager: {e}")
            return False
    
    async def register_node(self, node_id: str, node_info: Dict[str, Any]) -> bool:
        """
        Register a node with the redundancy manager.
        
        Args:
            node_id: Node identifier
            node_info: Node information
            
        Returns:
            Success status
        """
        try:
            # Extract node info
            device_type = node_info.get("device_type", "unknown")
            capabilities = node_info.get("capabilities", [])
            roles = node_info.get("roles", [])
            
            # Store in appropriate map
            if device_type == "primary":
                # Primary node
                for capability in capabilities:
                    if capability not in self.primary_nodes:
                        self.primary_nodes[capability] = {}
                        
                    self.primary_nodes[capability][node_id] = node_info
                    
                    # Update capability map
                    if capability not in self.capability_map:
                        self.capability_map[capability] = {"primary": {}, "backup": {}}
                        
                    self.capability_map[capability]["primary"][node_id] = node_info
                    
            elif device_type == "backup":
                # Backup node
                for capability in capabilities:
                    if capability not in self.backup_nodes:
                        self.backup_nodes[capability] = {}
                        
                    self.backup_nodes[capability][node_id] = node_info
                    
                    # Update capability map
                    if capability not in self.capability_map:
                        self.capability_map[capability] = {"primary": {}, "backup": {}}
                        
                    self.capability_map[capability]["backup"][node_id] = node_info
                    
            # Store in node status
            self.node_status[node_id] = {
                "device_type": device_type,
                "capabilities": capabilities,
                "roles": roles,
                "is_active": node_info.get("is_active", True),
                "last_seen": time.time(),
                "battery_level": node_info.get("battery_level", 1.0),
                "system_temperature": node_info.get("system_temperature", 25.0)
            }
            
            # Add to active nodes
            self.active_nodes[node_id] = True
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering node: {e}")
            return False
    
    async def _monitor_heartbeats(self) -> None:
        """Monitor heartbeats from all nodes."""
        while self.is_active:
            try:
                # Check each node's status
                current_time = time.time()
                for node_id, status in self.node_status.items():
                    last_seen = status.get("last_seen", 0)
                    
                    # If node hasn't been seen in 3 heartbeat intervals, consider it down
                    if current_time - last_seen > self.heartbeat_interval * 3:
                        # Check if already marked inactive
                        if node_id in self.active_nodes and self.active_nodes[node_id]:
                            # Mark as inactive
                            self.active_nodes[node_id] = False
                            
                            # Node is down, initiate failover
                            await self._handle_node_failure(node_id)
                    
                # Wait for next check
                await asyncio.sleep(self.heartbeat_interval)
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error in heartbeat monitoring: {e}")
                await asyncio.sleep(1.0)  # Brief delay before retry
    
    async def _handle_node_failure(self, failed_node_id: str) -> None:
        """
        Handle failure of a node by activating backups.
        
        Args:
            failed_node_id: ID of failed node
        """
        # Get node information
        failed_node = self.node_status.get(failed_node_id, {})
        capabilities = failed_node.get("capabilities", [])
        device_type = failed_node.get("device_type", "unknown")
        
        logger.warning(f"Node failure detected: {failed_node_id} ({device_type})")
        
        # Skip if not a primary
        if device_type != "primary":
            logger.info(f"Ignoring non-primary node failure: {failed_node_id}")
            return
            
        # For each capability, find a backup
        activated_backups = []
        
        for capability in capabilities:
            # Find backup for this capability
            backup_nodes = self.capability_map.get(capability, {}).get("backup", {})
            
            if not backup_nodes:
                logger.error(f"No backup available for capability: {capability}")
                continue
                
            # Find first available backup
            for backup_id, backup_info in backup_nodes.items():
                # Skip if backup is also down
                if backup_id not in self.active_nodes or not self.active_nodes[backup_id]:
                    continue
                    
                # Activate this backup
                await self._activate_backup(backup_id, capability, failed_node_id)
                activated_backups.append(backup_id)
                break
        
        if not activated_backups:
            logger.error(f"Could not find any active backups for {failed_node_id}")
            
            # Send alert message
            alert_message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=MessageIntent.STATE_BROADCAST,
                priority=TransmissionPriority.EMERGENCY,
                content=f"ALERT: No backup available for failed node {failed_node_id}",
                metadata={
                    "alert_type": "redundancy_failure",
                    "failed_node": failed_node_id,
                    "capabilities": capabilities,
                    "timestamp": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(alert_message)
    
    async def _activate_backup(self, backup_id: str, capability: str, failed_node_id: str) -> None:
        """
        Activate a backup node for a specific capability.
        
        Args:
            backup_id: ID of backup node
            capability: Capability to activate
            failed_node_id: ID of failed node
        """
        logger.info(f"Activating backup {backup_id} for capability {capability}")
        
        # Create failover request message
        message = PulseMeshMessage(
            sender_id=self.node_id,
            sender_name=self.node_name,
            receiver_id=backup_id,
            layer=CommunicationLayer.WIFI_MESH,
            intent=RoboticsMessageIntent.FAILOVER_REQUEST,
            priority=TransmissionPriority.HIGH,
            content=f"Failover request: {capability}",
            metadata={
                "failed_node": failed_node_id,
                "capability": capability,
                "capabilities": [capability],
                "timestamp": time.time()
            }
        )
        
        await self.mesh_node.wifi_layer.send_message(message)
        
        # Update capability map
        if capability in self.capability_map:
            # Move backup to primary
            backup_info = self.capability_map[capability]["backup"].pop(backup_id, None)
            
            if backup_info:
                # Update to primary role
                backup_info["device_type"] = "primary"
                
                # Add to primary
                self.capability_map[capability]["primary"][backup_id] = backup_info
                
                # Update in primary_nodes map
                if capability not in self.primary_nodes:
                    self.primary_nodes[capability] = {}
                    
                self.primary_nodes[capability][backup_id] = backup_info
                
                # Remove from backup_nodes map
                if capability in self.backup_nodes:
                    self.backup_nodes[capability].pop(backup_id, None)
    
    async def _process_migrations(self) -> None:
        """Process task migrations."""
        while self.is_active:
            try:
                # Get next migration
                migration = await self.migration_queue.get()
                
                # Process migration
                task_id = migration.get("task_id")
                source_node = migration.get("source_node")
                target_node = migration.get("target_node")
                task_data = migration.get("task_data")
                
                logger.info(f"Migrating task {task_id} from {source_node} to {target_node}")
                
                # Create task migration message
                message = PulseMeshMessage(
                    sender_id=self.node_id,
                    sender_name=self.node_name,
                    receiver_id=target_node,
                    layer=CommunicationLayer.WIFI_MESH,
                    intent=RoboticsMessageIntent.TASK_ASSIGNMENT,
                    priority=TransmissionPriority.HIGH,
                    content=f"Task migration: {task_data.get('name', '')}",
                    metadata={
                        "task_id": task_id,
                        "task_name": task_data.get("name", ""),
                        "task_type": task_data.get("task_type", ""),
                        "priority": task_data.get("priority", "SCHEDULED"),
                        "source_node": source_node,
                        "assigned_node": target_node,
                        "task_data": task_data,
                        "is_migration": True,
                        "timestamp": time.time()
                    }
                )
                
                await self.mesh_node.wifi_layer.send_message(message)
                
                # Mark as done
                self.migration_queue.task_done()
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error processing migrations: {e}")
                await asyncio.sleep(1.0)
    
    def _handle_hardware_status(self, message: PulseMeshMessage) -> None:
        """
        Handle hardware status message.
        
        Args:
            message: Hardware status message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract status info
        node_id = message.sender_id
        device_type = message.metadata.get("device_type", "unknown")
        roles = message.metadata.get("roles", [])
        capabilities = message.metadata.get("capabilities", [])
        is_active = message.metadata.get("is_active", True)
        battery_level = message.metadata.get("battery_level", 1.0)
        system_temperature = message.metadata.get("system_temperature", 25.0)
        
        # Update node status
        self.node_status[node_id] = {
            "device_type": device_type,
            "roles": roles,
            "capabilities": capabilities,
            "is_active": is_active,
            "last_seen": time.time(),
            "battery_level": battery_level,
            "system_temperature": system_temperature
        }
        
        # Update active nodes
        self.active_nodes[node_id] = is_active
        
        # Check for failover acknowledgement
        if message.metadata.get("failover_acknowledged"):
            # Update capability map with new primary
            failed_node = message.metadata.get("failed_node")
            activated_node = message.metadata.get("activated_node")
            
            logger.info(f"Failover activated: {activated_node} taking over for {failed_node}")
    
    def _handle_task_status(self, message: PulseMeshMessage) -> None:
        """
        Handle task status message.
        
        Args:
            message: Task status message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract task info
        task_id = message.metadata.get("task_id")
        node_id = message.sender_id
        status = message.metadata.get("status", "EXECUTING")
        
        # Only care about failed tasks
        if status != "FAILED":
            return
            
        # Check if node is still active
        if node_id not in self.active_nodes or not self.active_nodes[node_id]:
            # Node is down, may need to migrate failed task
            task_name = message.metadata.get("task_name", "")
            task_type = message.metadata.get("task_type", "")
            
            logger.warning(f"Task {task_name} failed on inactive node {node_id}")
            
            # In a real system, would determine whether to retry on another node


# ==== 4. POWER MANAGEMENT SYSTEM ====

class PulsePowerManager:
    """Manages power consumption and allocation across nodes."""
    
    def __init__(self, 
                node_id: str,
                node_name: str,
                mesh_node: PulseMeshFederatedNode,
                min_operating_power: float = 0.2,  # 20% battery
                critical_tasks: List[str] = None):
        """
        Initialize power manager.
        
        Args:
            node_id: Unique identifier for this manager
            node_name: Human-readable name
            mesh_node: PulseMesh node for communication
            min_operating_power: Minimum power level for operation
            critical_tasks: List of critical tasks that must continue
        """
        self.node_id = node_id
        self.node_name = node_name
        self.mesh_node = mesh_node
        self.min_operating_power = min_operating_power
        self.critical_tasks = critical_tasks or ["plant_watering", "emergency_response"]
        
        # Power status
        self.current_power = 1.0
        self.solar_input = 0.0
        self.power_consumption = {}
        self.power_modes = {
            "full": 1.0,
            "balanced": 0.7,
            "eco": 0.4,
            "minimal": 0.2,
            "emergency": 0.1
        }
        self.current_mode = "full"
        
        # Device power management
        self.device_power = {}
        
        # Connected devices
        self.connected_devices = {}
        
        # Internal state
        self.is_active = False
        self.monitor_task = None
    
    async def start(self) -> bool:
        """
        Start power manager.
        
        Returns:
            Success status
        """
        try:
            # Register message handlers
            if hasattr(self.mesh_node, 'wifi_layer'):
                self.mesh_node.wifi_layer.register_handler(
                    RoboticsMessageIntent.POWER_STATUS, self._handle_power_status)
                self.mesh_node.wifi_layer.register_handler(
                    RoboticsMessageIntent.HARDWARE_STATUS, self._handle_hardware_status)
                
            # Start monitor task
            self.monitor_task = asyncio.create_task(self.manage_power_modes())
            
            # Set active
            self.is_active = True
            
            logger.info(f"Power manager started: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting power manager: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop power manager.
        
        Returns:
            Success status
        """
        try:
            # Set inactive
            self.is_active = False
            
            # Cancel tasks
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
                    
            logger.info(f"Power manager stopped: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping power manager: {e}")
            return False
    
    async def update_power_status(self, battery_level: float, solar_input: float = 0.0) -> None:
        """
        Update power status.
        
        Args:
            battery_level: Current battery level (0.0 - 1.0)
            solar_input: Current solar input (watts)
        """
        # Update status
        self.current_power = battery_level
        self.solar_input = solar_input
        
        # Create status message
        message = PulseMeshMessage(
            sender_id=self.node_id,
            sender_name=self.node_name,
            layer=CommunicationLayer.WIFI_MESH,
            intent=RoboticsMessageIntent.POWER_STATUS,
            priority=TransmissionPriority.NORMAL,
            content=f"Power status update: {battery_level:.1%}",
            metadata={
                "battery_level": battery_level,
                "solar_input": solar_input,
                "power_mode": self.current_mode,
                "timestamp": time.time()
            }
        )
        
        await self.mesh_node.wifi_layer.send_message(message)
    
    def register_device(self, device_id: str, power_profile: Dict[str, float]) -> None:
        """
        Register a device with power profiles.
        
        Args:
            device_id: Device identifier
            power_profile: Power consumption for different modes
        """
        self.device_power[device_id] = power_profile
        
        # Initialize consumption tracking
        self.power_consumption[device_id] = power_profile.get(self.current_mode, 
                                                         power_profile.get("full", 1.0))
        
        # Add to connected devices
        self.connected_devices[device_id] = {
            "power_profile": power_profile,
            "current_consumption": self.power_consumption[device_id],
            "last_update": time.time()
        }
    
    def unregister_device(self, device_id: str) -> None:
        """
        Unregister a device.
        
        Args:
            device_id: Device identifier
        """
        # Remove from tracking
        if device_id in self.device_power:
            del self.device_power[device_id]
            
        if device_id in self.power_consumption:
            del self.power_consumption[device_id]
            
        if device_id in self.connected_devices:
            del self.connected_devices[device_id]
    
    async def manage_power_modes(self) -> None:
        """Adjust system power modes based on available power."""
        while self.is_active:
            try:
                # Calculate power trend (charging or discharging)
                power_consumption = sum(self.power_consumption.values())
                power_trend = self.solar_input - power_consumption
                
                # Determine appropriate power mode
                if self.current_power < self.min_operating_power:
                    # Critical power level
                    new_mode = "emergency"
                elif self.current_power < 0.3:
                    # Low power
                    new_mode = "minimal"
                elif self.current_power < 0.5:
                    # Moderate power
                    new_mode = "eco"
                elif self.current_power < 0.8:
                    # Good power
                    new_mode = "balanced"
                else:
                    # Full power
                    new_mode = "full"
                    
                # Adjust if power is decreasing rapidly
                if power_trend < -0.05 and new_mode != "emergency":
                    # Step down one level for safety
                    modes = ["full", "balanced", "eco", "minimal", "emergency"]
                    current_index = modes.index(new_mode)
                    new_mode = modes[min(current_index + 1, len(modes) - 1)]
                    
                # Apply mode change if needed
                if new_mode != self.current_mode:
                    await self._change_power_mode(new_mode)
                    
                # Wait for next check
                await asyncio.sleep(60.0)  # Check every minute
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error in power management: {e}")
                await asyncio.sleep(30.0)  # Longer delay if error
    
    async def _change_power_mode(self, new_mode: str) -> None:
        """
        Change system power mode.
        
        Args:
            new_mode: New power mode
        """
        logger.info(f"Changing power mode: {self.current_mode} -> {new_mode}")
        
        # Get power allocation for new mode
        power_allocation = self.power_modes.get(new_mode, 1.0)
        
        # Update device power consumption
        for device_id, profile in self.device_power.items():
            # Get consumption for new mode, fallback to default
            consumption = profile.get(new_mode, profile.get("full", 1.0) * power_allocation)
            
            # Update tracking
            self.power_consumption[device_id] = consumption
            
            if device_id in self.connected_devices:
                self.connected_devices[device_id]["current_consumption"] = consumption
        
        # Notify all nodes of power mode change
        message = PulseMeshMessage(
            sender_id=self.node_id,
            sender_name=self.node_name,
            layer=CommunicationLayer.WIFI_MESH,
            intent=RoboticsMessageIntent.POWER_STATUS,
            priority=TransmissionPriority.HIGH,
            content=f"Power mode change: {self.current_mode} -> {new_mode}",
            metadata={
                "power_mode": new_mode,
                "previous_mode": self.current_mode,
                "power_allocation": power_allocation,
                "current_power": self.current_power,
                "solar_input": self.solar_input,
                "critical_only": new_mode in ["minimal", "emergency"],
                "timestamp": time.time()
            }
        )
        
        await self.mesh_node.wifi_layer.send_message(message)
        
        # Update current mode
        self.current_mode = new_mode
    
    async def _suspend_non_critical_tasks(self) -> None:
        """Suspend non-critical tasks to save power."""
        # Create task suspension message
        message = PulseMeshMessage(
            sender_id=self.node_id,
            sender_name=self.node_name,
            layer=CommunicationLayer.WIFI_MESH,
            intent=RoboticsMessageIntent.TASK_STATUS,
            priority=TransmissionPriority.HIGH,
            content="Suspending non-critical tasks due to low power",
            metadata={
                "action": "suspend_non_critical",
                "critical_tasks": self.critical_tasks,
                "power_mode": self.current_mode,
                "timestamp": time.time()
            }
        )
        
        await self.mesh_node.wifi_layer.send_message(message)
    
    def _handle_power_status(self, message: PulseMeshMessage) -> None:
        """
        Handle power status message.
        
        Args:
            message: Power status message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract status info
        device_id = message.sender_id
        battery_level = message.metadata.get("battery_level", 1.0)
        solar_input = message.metadata.get("solar_input", 0.0)
        power_mode = message.metadata.get("power_mode", "full")
        
        # Update device tracking
        if device_id in self.connected_devices:
            self.connected_devices[device_id].update({
                "battery_level": battery_level,
                "solar_input": solar_input,
                "power_mode": power_mode,
                "last_update": time.time()
            })
            
        # Check for power mode change
        if message.metadata.get("power_mode") and device_id != self.node_id:
            new_mode = message.metadata.get("power_mode")
            
            # Align with coordinating power manager if needed
            if new_mode != self.current_mode:
                # Only follow if our battery is in similar state
                if ((new_mode == "emergency" and self.current_power < 0.3) or
                    (new_mode == "minimal" and self.current_power < 0.4) or
                    (new_mode == "eco" and self.current_power < 0.6) or
                    (new_mode == "balanced" and self.current_power < 0.9)):
                    asyncio.create_task(self._change_power_mode(new_mode))
    
    def _handle_hardware_status(self, message: PulseMeshMessage) -> None:
        """
        Handle hardware status message.
        
        Args:
            message: Hardware status message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract status info
        device_id = message.sender_id
        battery_level = message.metadata.get("battery_level", 1.0)
        
        # Update device tracking
        if device_id not in self.connected_devices:
            # New device
            self.connected_devices[device_id] = {
                "battery_level": battery_level,
                "last_update": time.time()
            }
        else:
            # Update existing device
            self.connected_devices[device_id].update({
                "battery_level": battery_level,
                "last_update": time.time()
            })


# ==== 5. CARE TASK SCHEDULER ====

class PulseCareTaskScheduler:
    """Specialized scheduler for care-focused tasks."""
    
    def __init__(self, 
                node_id: str,
                node_name: str,
                mesh_node: PulseMeshFederatedNode,
                care_categories: Dict[str, Dict[str, Any]] = None):
        """
        Initialize care task scheduler.
        
        Args:
            node_id: Unique identifier for this scheduler
            node_name: Human-readable name
            mesh_node: PulseMesh node for communication
            care_categories: Dictionary of care categories and their priorities
        """
        self.node_id = node_id
        self.node_name = node_name
        self.mesh_node = mesh_node
        
        # Default care categories if none provided
        self.care_categories = care_categories or {
            "plant_care": {
                "priority": 1,
                "tasks": ["watering", "monitoring", "pruning"],
                "schedule_type": "needs_based"
            },
            "social_interaction": {
                "priority": 2,
                "tasks": ["conversation", "play", "support"],
                "schedule_type": "time_based"
            },
            "ecological_restoration": {
                "priority": 3,
                "tasks": ["cleanup", "planting", "monitoring"],
                "schedule_type": "project_based"
            }
        }
        
        # Task queues by category
        self.task_queues = {}
        for category in self.care_categories:
            self.task_queues[category] = asyncio.PriorityQueue()
            
        # Current tasks
        self.active_tasks = {}
        
        # Scheduling history for learning
        self.task_history = []
        
        # Plant and environment data
        self.plants = {}
        self.garden_zones = {}
        self.environment_data = {}
        
        # Internal state
        self.is_active = False
        self.scheduler_task = None
        self.environment_monitor_task = None
        
        # Connected ROS bridges
        self.ros_bridges = {}
        
        # Task templates
        self.task_templates = {
            "watering": {
                "name": "Water Plant",
                "task_type": "water_plant",
                "priority": TaskPriority.CARE,
                "estimated_duration": 180.0,
                "estimated_power": 0.3
            },
            "monitoring": {
                "name": "Monitor Plant Health",
                "task_type": "scan_plants",
                "priority": TaskPriority.SCHEDULED,
                "estimated_duration": 120.0,
                "estimated_power": 0.2
            },
            "pruning": {
                "name": "Prune Plant",
                "task_type": "prune_plant",
                "priority": TaskPriority.SCHEDULED,
                "estimated_duration": 300.0,
                "estimated_power": 0.4
            },
            "conversation": {
                "name": "Social Interaction",
                "task_type": "social_interaction",
                "priority": TaskPriority.USER_REQUESTED,
                "estimated_duration": 600.0,
                "estimated_power": 0.3
            },
            "ecological_survey": {
                "name": "Ecological Survey",
                "task_type": "ecological_survey",
                "priority": TaskPriority.SCHEDULED,
                "estimated_duration": 1800.0,
                "estimated_power": 0.5
            }
        }
    
    async def start(self) -> bool:
        """
        Start care task scheduler.
        
        Returns:
            Success status
        """
        try:
            # Register message handlers
            if hasattr(self.mesh_node, 'wifi_layer'):
                self.mesh_node.wifi_layer.register_handler(
                    RoboticsMessageIntent.TASK_STATUS, self._handle_task_status)
                self.mesh_node.wifi_layer.register_handler(
                    RoboticsMessageIntent.GARDEN_UPDATE, self._handle_garden_update)
                self.mesh_node.wifi_layer.register_handler(
                    RoboticsMessageIntent.PLANT_DATA, self._handle_plant_data)
                
            # Start scheduler task
            self.scheduler_task = asyncio.create_task(self._run_scheduler())
            
            # Start environment monitor
            self.environment_monitor_task = asyncio.create_task(self._monitor_environment())
            
            # Set active
            self.is_active = True
            
            logger.info(f"Care task scheduler started: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting care task scheduler: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop care task scheduler.
        
        Returns:
            Success status
        """
        try:
            # Set inactive
            self.is_active = False
            
            # Cancel tasks
            if self.scheduler_task:
                self.scheduler_task.cancel()
                try:
                    await self.scheduler_task
                except asyncio.CancelledError:
                    pass
                    
            if self.environment_monitor_task:
                self.environment_monitor_task.cancel()
                try:
                    await self.environment_monitor_task
                except asyncio.CancelledError:
                    pass
                    
            logger.info(f"Care task scheduler stopped: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping care task scheduler: {e}")
            return False
    
    def register_ros_bridge(self, node_id: str, bridge: PulseROSBridge) -> None:
        """
        Register a ROS bridge for task execution.
        
        Args:
            node_id: Node identifier
            bridge: ROS bridge instance
        """
        self.ros_bridges[node_id] = bridge
    
    async def add_plant(self, plant: PlantData) -> bool:
        """
        Add a plant to the garden database.
        
        Args:
            plant: Plant data
            
        Returns:
            Success status
        """
        try:
            # Store plant data
            self.plants[plant.plant_id] = plant
            
            # Create database record
            plant_message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=RoboticsMessageIntent.PLANT_DATA,
                priority=TransmissionPriority.NORMAL,
                content=f"Plant added: {plant.name}",
                metadata={
                    "plant_id": plant.plant_id,
                    "plant_name": plant.name,
                    "action": "add",
                    "plant_data": json.loads(plant.to_json()),
                    "timestamp": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(plant_message)
            
            # Schedule initial monitoring
            await self._schedule_plant_care(plant.plant_id)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding plant: {e}")
            return False
    
    async def update_plant(self, plant_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update plant information.
        
        Args:
            plant_id: Plant identifier
            updates: Fields to update
            
        Returns:
            Success status
        """
        try:
            # Check if plant exists
            if plant_id not in self.plants:
                logger.warning(f"Plant not found: {plant_id}")
                return False
                
            # Get plant
            plant = self.plants[plant_id]
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(plant, key):
                    setattr(plant, key, value)
                elif key in plant.metadata:
                    plant.metadata[key] = value
                else:
                    plant.metadata[key] = value
                    
            # Create update message
            plant_message = PulseMeshMessage(
                sender_id=self.node_id,
                sender_name=self.node_name,
                layer=CommunicationLayer.WIFI_MESH,
                intent=RoboticsMessageIntent.PLANT_DATA,
                priority=TransmissionPriority.NORMAL,
                content=f"Plant updated: {plant.name}",
                metadata={
                    "plant_id": plant.plant_id,
                    "plant_name": plant.name,
                    "action": "update",
                    "updates": updates,
                    "timestamp": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(plant_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating plant: {e}")
            return False
    
    async def add_care_task(self, 
                          task_type: str,
                          priority: TaskPriority = TaskPriority.SCHEDULED,
                          category: str = "plant_care",
                          target_id: Optional[str] = None,
                          parameters: Dict[str, Any] = None,
                          schedule_time: Optional[float] = None) -> Optional[str]:
        """
        Add a care task to the schedule.
        
        Args:
            task_type: Type of task
            priority: Task priority
            category: Care category
            target_id: Target identifier (plant, zone, etc.)
            parameters: Task parameters
            schedule_time: When to execute task
            
        Returns:
            Task ID if successful, None otherwise
        """
        try:
            # Check if category exists
            if category not in self.care_categories:
                logger.warning(f"Unknown care category: {category}")
                return None
                
            # Get template
            template = self.task_templates.get(task_type)
            
            if not template:
                logger.warning(f"Unknown task type: {task_type}")
                return None
                
            # Create task
            task = RoboticTask(
                name=template["name"],
                task_type=template["task_type"],
                priority=priority,
                estimated_duration=template["estimated_duration"],
                estimated_power=template["estimated_power"],
                tags=[category, task_type],
                schedule_time=schedule_time,
                metadata=parameters or {}
            )
            
            # Add target to metadata
            if target_id:
                task.metadata["target_id"] = target_id
                
                # If plant task, add plant name
                if category == "plant_care" and target_id in self.plants:
                    plant = self.plants[target_id]
                    task.name = f"{template['name']}: {plant.name}"
                    task.metadata["plant_name"] = plant.name
            
            # Add to queue
            if category in self.task_queues:
                # Use schedule time as priority if available
                priority_time = schedule_time or time.time()
                await self.task_queues[category].put((priority.value, priority_time, task))
                
                # Add to active tasks
                self.active_tasks[task.task_id] = {
                    "task": task,
                    "category": category,
                    "added_time": time.time()
                }
                
                # Create task message
                task_message = PulseMeshMessage(
                    sender_id=self.node_id,
                    sender_name=self.node_name,
                    layer=CommunicationLayer.WIFI_MESH,
                    intent=RoboticsMessageIntent.CARE_SCHEDULE,
                    priority=TransmissionPriority.NORMAL,
                    content=f"Care task scheduled: {task.name}",
                    metadata={
                        "task_id": task.task_id,
                        "task_name": task.name,
                        "task_type": task.task_type,
                        "category": category,
                        "priority": priority.name,
                        "target_id": target_id,
                        "schedule_time": schedule_time,
                        "timestamp": time.time()
                    }
                )
                
                await self.mesh_node.wifi_layer.send_message(task_message)
                
                return task.task_id
                
            else:
                logger.warning(f"No queue for category: {category}")
                return None
                
        except Exception as e:
            logger.error(f"Error adding care task: {e}")
            return None
    
    async def _run_scheduler(self) -> None:
        """Main scheduler loop for care tasks."""
        while self.is_active:
            try:
                # Check for available executors
                available_executors = [
                    node_id for node_id, bridge in self.ros_bridges.items()
                    if bridge.is_active and not bridge.current_task
                ]
                
                if not available_executors:
                    # No available executors
                    await asyncio.sleep(1.0)
                    continue
                    
                # Find highest priority task across all categories
                next_tasks = {}
                for category, queue in self.task_queues.items():
                    if not queue.empty():
                        try:
                            # Peek at next task
                            priority, schedule_time, task = queue._queue[0]
                            next_tasks[category] = (priority, schedule_time, task)
                        except (IndexError, AttributeError):
                            # Queue empty or no peek available
                            pass
                
                if not next_tasks:
                    # Check if any ROS bridge has the default gardening behavior enabled
                    # and no active tasks
                    ros_bridge = self.ros_bridges.get(available_executors[0])
                    if ros_bridge and not ros_bridge.current_task:
                        # Check if any plants need attention
                        plant_task = await self._check_for_plant_needs()
                        if plant_task:
                            # Send plant task to bridge
                            await ros_bridge.add_task(plant_task)
                        else:
                            # Check for default ecological task
                            eco_task = await self._create_default_ecological_task()
                            if eco_task:
                                await ros_bridge.add_task(eco_task)
                    
                    # Wait before checking again
                    await asyncio.sleep(5.0)
                    continue
                    
                # Find highest priority task
                selected_category = min(next_tasks.keys(), 
                                       key=lambda cat: (next_tasks[cat][0], next_tasks[cat][1]))
                
                priority, schedule_time, task = next_tasks[selected_category]
                
                # Check if task is ready to execute
                current_time = time.time()
                
                if task.schedule_time and task.schedule_time > current_time:
                    # Not ready yet
                    wait_time = min(task.schedule_time - current_time, 5.0)
                    await asyncio.sleep(wait_time)
                    continue
                    
                # Get task from queue
                _, _, task = await self.task_queues[selected_category].get()
                
                # Select executor
                executor_id = available_executors[0]
                ros_bridge = self.ros_bridges[executor_id]
                
                # Assign task
                task.assigned_node = executor_id
                await ros_bridge.add_task(task)
                
                # Update task status
                if task.task_id in self.active_tasks:
                    self.active_tasks[task.task_id]["status"] = "assigned"
                    self.active_tasks[task.task_id]["assigned_node"] = executor_id
                    self.active_tasks[task.task_id]["assigned_time"] = current_time
                    
                # Mark queue task as done
                self.task_queues[selected_category].task_done()
                
                # Brief pause before next cycle
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error in care scheduler: {e}")
                await asyncio.sleep(1.0)
    
    async def _monitor_environment(self) -> None:
        """Monitor environment and update care needs."""
        while self.is_active:
            try:
                # Check plants for care needs
                for plant_id, plant in self.plants.items():
                    # Check if watering needed
                    if plant.needs_water():
                        # Check if task already scheduled
                        already_scheduled = False
                        for task_id, task_info in self.active_tasks.items():
                            task = task_info["task"]
                            if (task.task_type == "water_plant" and 
                                task.metadata.get("target_id") == plant_id and
                                task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.EXECUTING]):
                                already_scheduled = True
                                break
                                
                        if not already_scheduled:
                            # Schedule watering task
                            await self.add_care_task(
                                task_type="watering",
                                priority=TaskPriority.CARE,
                                category="plant_care",
                                target_id=plant_id,
                                parameters={
                                    "plant_id": plant_id,
                                    "amount": 100.0  # Default amount in ml
                                }
                            )
                            
                    # Check if monitoring needed
                    last_monitored = plant.metadata.get("last_monitored", 0)
                    if time.time() - last_monitored > 86400:  # Daily
                        # Check if task already scheduled
                        already_scheduled = False
                        for task_id, task_info in self.active_tasks.items():
                            task = task_info["task"]
                            if (task.task_type == "scan_plants" and 
                                task.metadata.get("target_id") == plant_id and
                                task.status in [TaskStatus.PENDING, TaskStatus.ASSIGNED, TaskStatus.EXECUTING]):
                                already_scheduled = True
                                break
                                
                        if not already_scheduled:
                            # Schedule monitoring task
                            await self.add_care_task(
                                task_type="monitoring",
                                priority=TaskPriority.SCHEDULED,
                                category="plant_care",
                                target_id=plant_id,
                                parameters={
                                    "plant_id": plant_id
                                }
                            )
                
                # Wait before next check
                await asyncio.sleep(300.0)  # Check every 5 minutes
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error monitoring environment: {e}")
                await asyncio.sleep(60.0)
    
    async def _schedule_plant_care(self, plant_id: str) -> None:
        """
        Schedule care for a specific plant.
        
        Args:
            plant_id: Plant identifier
        """
        if plant_id not in self.plants:
            return
            
        plant = self.plants[plant_id]
        
        # Schedule monitoring
        await self.add_care_task(
            task_type="monitoring",
            priority=TaskPriority.SCHEDULED,
            category="plant_care",
            target_id=plant_id,
            parameters={
                "plant_id": plant_id
            }
        )
        
        # Schedule watering if needed
        if plant.needs_water():
            await self.add_care_task(
                task_type="watering",
                priority=TaskPriority.CARE,
                category="plant_care",
                target_id=plant_id,
                parameters={
                    "plant_id": plant_id,
                    "amount": 100.0  # Default amount in ml
                }
            )
    
    async def _check_for_plant_needs(self) -> Optional[RoboticTask]:
        """
        Check for any immediate plant care needs.
        
        Returns:
            Task for immediate execution or None
        """
        # Find plants that need water
        for plant_id, plant in self.plants.items():
            if plant.needs_water():
                # Create watering task
                task = RoboticTask(
                    name=f"Water Plant: {plant.name}",
                    task_type="water_plant",
                    priority=TaskPriority.CARE,
                    estimated_duration=180.0,
                    tags=["plant_care", "watering"],
                    metadata={
                        "plant_id": plant_id,
                        "plant_name": plant.name,
                        "amount": 100.0  # Default amount in ml
                    }
                )
                
                return task
                
        # Find plants that need monitoring
        for plant_id, plant in self.plants.items():
            last_monitored = plant.metadata.get("last_monitored", 0)
            if time.time() - last_monitored > 86400:  # Daily
                # Create monitoring task
                task = RoboticTask(
                    name=f"Monitor Plant: {plant.name}",
                    task_type="scan_plants",
                    priority=TaskPriority.SCHEDULED,
                    estimated_duration=120.0,
                    tags=["plant_care", "monitoring"],
                    metadata={
                        "plant_id": plant_id,
                        "plant_name": plant.name
                    }
                )
                
                return task
                
        return None
    
    async def _create_default_ecological_task(self) -> Optional[RoboticTask]:
        """
        Create a default ecological task when no other tasks are available.
        
        Returns:
            Default ecological task or None
        """
        # Create a survey task
        task = RoboticTask(
            name="Garden Ecological Survey",
            task_type="ecological_survey",
            priority=TaskPriority.IDLE,
            estimated_duration=900.0,
            tags=["ecological_restoration", "monitoring"],
            metadata={
                "survey_type": "routine",
                "survey_parameters": {
                    "light_levels": True,
                    "temperature": True,
                    "humidity": True,
                    "plant_health": True,
                    "soil_conditions": True
                }
            }
        )
        
        return task
    
    def _handle_task_status(self, message: PulseMeshMessage) -> None:
        """
        Handle task status message.
        
        Args:
            message: Task status message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract task info
        task_id = message.metadata.get("task_id")
        status = message.metadata.get("status")
        
        if not task_id or not status or task_id not in self.active_tasks:
            return
            
        # Update task status
        task_info = self.active_tasks[task_id]
        task_info["status"] = status
        
        # Handle completed tasks
        if status == "COMPLETED":
            # Get result
            result = message.metadata.get("result", {})
            
            # Update task info
            task_info["result"] = result
            task_info["completed_time"] = time.time()
            
            # Handle specific task types
            task = task_info["task"]
            
            if task.task_type == "water_plant":
                # Update plant watering record
                plant_id = task.metadata.get("plant_id")
                
                if plant_id in self.plants:
                    plant = self.plants[plant_id]
                    amount = task.metadata.get("amount", 100.0)
                    
                    # Record watering
                    plant.record_watering(amount, f"Automatic watering by {message.sender_name}")
                    
                    # Update plant
                    asyncio.create_task(self.update_plant(plant_id, 
                                                      {"last_watered": time.time()}))
                    
            elif task.task_type == "scan_plants":
                # Update plant monitoring record
                plant_id = task.metadata.get("plant_id")
                
                if plant_id in self.plants:
                    # Update monitoring timestamp
                    asyncio.create_task(self.update_plant(plant_id, 
                                                      {"last_monitored": time.time()}))
                    
                    # Parse sensor data if available
                    if "sensor_data" in result:
                        sensor_data = result["sensor_data"]
                        updates = {"metadata": {}}
                        
                        if "temperature" in sensor_data:
                            updates["metadata"]["last_temperature"] = sensor_data["temperature"]
                            
                        if "humidity" in sensor_data:
                            updates["metadata"]["last_humidity"] = sensor_data["humidity"]
                            
                        if "light" in sensor_data:
                            updates["metadata"]["last_light"] = sensor_data["light"]
                            
                        if "moisture" in sensor_data:
                            updates["metadata"]["last_soil_moisture"] = sensor_data["moisture"]
                            
                        # Update plant with sensor data
                        asyncio.create_task(self.update_plant(plant_id, updates))
            
            # Add to history and remove from active
            self.task_history.append(task_info)
            del self.active_tasks[task_id]
            
            # Trim history if too long
            if len(self.task_history) > 100:
                self.task_history = self.task_history[-100:]
                
        elif status == "FAILED":
            # Get error
            error = message.metadata.get("error", "Unknown error")
            
            # Update task info
            task_info["error"] = error
            task_info["failed_time"] = time.time()
            
            # Add to history and remove from active
            self.task_history.append(task_info)
            del self.active_tasks[task_id]
            
            # Trim history if too long
            if len(self.task_history) > 100:
                self.task_history = self.task_history[-100:]
    
    def _handle_garden_update(self, message: PulseMeshMessage) -> None:
        """
        Handle garden update message.
        
        Args:
            message: Garden update message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract update info
        update_type = message.metadata.get("update_type")
        
        if update_type == "environment":
            # Environmental data update
            environment_data = message.metadata.get("environment_data", {})
            
            # Update environment tracking
            self.environment_data.update(environment_data)
            
        elif update_type == "zone":
            # Garden zone update
            zone_id = message.metadata.get("zone_id")
            zone_data = message.metadata.get("zone_data", {})
            
            if zone_id:
                self.garden_zones[zone_id] = zone_data
    
    def _handle_plant_data(self, message: PulseMeshMessage) -> None:
        """
        Handle plant data message.
        
        Args:
            message: Plant data message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract plant info
        plant_id = message.metadata.get("plant_id")
        action = message.metadata.get("action")
        
        if not plant_id or not action:
            return
            
        if action == "add":
            # New plant
            plant_data = message.metadata.get("plant_data")
            
            if plant_data:
                # Create plant
                try:
                    plant = PlantData(**plant_data)
                    
                    # Add to database
                    self.plants[plant_id] = plant
                    
                    # Schedule care
                    asyncio.create_task(self._schedule_plant_care(plant_id))
                except Exception as e:
                    logger.error(f"Error parsing plant data: {e}")
                    
        elif action == "update":
            # Update existing plant
            updates = message.metadata.get("updates", {})
            
            if plant_id in self.plants and updates:
                plant = self.plants[plant_id]
                
                # Apply updates
                for key, value in updates.items():
                    if hasattr(plant, key):
                        setattr(plant, key, value)
                    elif key == "metadata":
                        # Update metadata dict
                        plant.metadata.update(value)
                        
        elif action == "delete":
            # Remove plant
            if plant_id in self.plants:
                del self.plants[plant_id]


# ==== 6. GARDENING ACTIONS ====

class PulseGardeningActions:
    """Implements gardening and plant care actions."""
    
    def __init__(self, 
                node_id: str,
                node_name: str,
                ros_bridge: PulseROSBridge,
                mesh_node: PulseMeshFederatedNode,
                gardening_config: Dict[str, Any] = None):
        """
        Initialize gardening actions.
        
        Args:
            node_id: Unique identifier for this node
            node_name: Human-readable name
            ros_bridge: ROS bridge for hardware control
            mesh_node: PulseMesh node for communication
            gardening_config: Configuration for gardening tasks
        """
        self.node_id = node_id
        self.node_name = node_name
        self.ros_bridge = ros_bridge
        self.mesh_node = mesh_node
        self.gardening_config = gardening_config or {}
        
        # Plant database
        self.plants = {}
        
        # Tool management
        self.tools = {
            "watering_system": None,
            "manipulator": None,
            "soil_sensor": None
        }
        
        # Action sequences
        self.action_sequences = {
            "water_plant": [
                "approach_plant",
                "check_soil_moisture",
                "prepare_watering_tool",
                "dispense_water",
                "verify_watering",
                "log_watering"
            ],
            "prune_plant": [
                "approach_plant",
                "analyze_plant_structure",
                "identify_pruning_points",
                "prepare_pruning_tool",
                "execute_pruning",
                "collect_cuttings",
                "verify_pruning",
                "log_pruning"
            ],
            "monitor_plant": [
                "approach_plant",
                "capture_plant_image",
                "measure_environmental_conditions",
                "analyze_plant_health",
                "log_monitoring_data"
            ],
            "collect_data": [
                "move_to_location",
                "setup_sensors",
                "collect_measurements",
                "log_data"
            ]
        }
        
        # Register action handlers
        if ros_bridge:
            self._register_action_handlers()
        
        # Internal state
        self.is_active = False
        self.current_action = None
        
        # Plant locations (in robot's coordinate system)
        self.plant_locations = {}
        
        # Sensor configuration
        self.sensors = {
            "moisture_sensor": {
                "id": "moisture_sensor",
                "type": "soil_moisture",
                "actuator_id": "manipulator_arm",
                "action": "extend",
                "parameters": {"position": "soil"}
            },
            "temperature_sensor": {
                "id": "temperature_ambient",
                "type": "temperature"
            },
            "humidity_sensor": {
                "id": "humidity_ambient",
                "type": "humidity"
            },
            "light_sensor": {
                "id": "light_ambient",
                "type": "light"
            }
        }
        
        # Actuator configuration
        self.actuators = {
            "water_pump": {
                "id": "water_pump",
                "type": "pump",
                "commands": ["on", "off"],
                "flow_rate": 50.0  # ml/s
            },
            "manipulator_arm": {
                "id": "manipulator_arm",
                "type": "arm",
                "commands": ["extend", "retract", "position"],
                "positions": {
                    "home": [0.0, 0.0, 0.0],
                    "soil": [0.3, 0.0, -0.2],
                    "water": [0.3, 0.0, 0.1],
                    "prune": [0.3, 0.0, 0.0]
                }
            }
        }
    
    async def start(self) -> bool:
        """
        Start gardening actions module.
        
        Returns:
            Success status
        """
        try:
            # Set active
            self.is_active = True
            
            logger.info(f"Gardening actions started: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting gardening actions: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop gardening actions module.
        
        Returns:
            Success status
        """
        try:
            # Set inactive
            self.is_active = False
            
            logger.info(f"Gardening actions stopped: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping gardening actions: {e}")
            return False
    
    def _register_action_handlers(self) -> None:
        """Register action handlers with ROS bridge."""
        if not self.ros_bridge:
            return
            
        # Register gardening task handlers
        for task_type, handler in [
            ("water_plant", self.execute_watering),
            ("prune_plant", self.execute_pruning),
            ("scan_plants", self.execute_plant_scan),
            ("ecological_survey", self.execute_ecological_survey)
        ]:
            # Register handler
            if hasattr(self.ros_bridge, "task_handler"):
                self.ros_bridge.task_handler[task_type] = handler
    
    async def execute_watering(self, task: RoboticTask) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute a plant watering task.
        
        Args:
            task: Watering task
            
        Returns:
            Success status and result data
        """
        try:
            # Get task parameters
            plant_id = task.metadata.get("plant_id")
            amount = task.metadata.get("amount", 100.0)  # ml
            
            if not plant_id:
                return False, {"error": "Missing plant ID"}
                
            # Get plant location
            location = self.plant_locations.get(plant_id)
            
            if not location:
                # Default location
                location = {"x": 0.5, "y": 0.0, "theta": 0.0}
                
            # Execute watering sequence
            
            # 1. Approach plant
            logger.info(f"Approaching plant: {plant_id}")
            
            success = await self.ros_bridge.move_robot(
                linear_x=0.2,
                duration=2.0
            )
            
            if not success:
                return False, {"error": "Failed to approach plant"}
                
            # Update task progress
            task.update_status(task.status, 0.2)
            
            # 2. Check soil moisture
            logger.info(f"Checking soil moisture")
            
            moisture_data = await self.ros_bridge.read_sensor(
                "moisture_" + plant_id if plant_id else "moisture_sensor"
            )
            
            current_moisture = 0.0
            if moisture_data:
                current_moisture = moisture_data.value
                
            # 3. Position manipulator for watering
            logger.info(f"Positioning manipulator for watering")
            
            success = await self.ros_bridge.control_actuator(
                actuator_id="manipulator_arm",
                command="position",
                parameters={"position": "water"}
            )
            
            if not success:
                return False, {"error": "Failed to position manipulator"}
                
            # Update task progress
            task.update_status(task.status, 0.4)
            
            # 4. Activate water pump
            logger.info(f"Dispensing water: {amount} ml")
            
            # Calculate duration based on flow rate
            flow_rate = 50.0  # ml/s
            if "water_pump" in self.actuators:
                flow_rate = self.actuators["water_pump"].get("flow_rate", 50.0)
                
            duration = amount / flow_rate
            
            success = await self.ros_bridge.control_actuator(
                actuator_id="water_pump",
                command="on",
                parameters={"duration": duration}
            )
            
            if not success:
                return False, {"error": "Failed to activate water pump"}
                
            # Wait for watering to complete
            await asyncio.sleep(duration + 1.0)
            
            # Update task progress
            task.update_status(task.status, 0.7)
            
            # 5. Return manipulator to home position
            logger.info(f"Returning manipulator to home position")
            
            success = await self.ros_bridge.control_actuator(
                actuator_id="manipulator_arm",
                command="position",
                parameters={"position": "home"}
            )
            
            # 6. Back away from plant
            logger.info(f"Backing away from plant")
            
            success = await self.ros_bridge.move_robot(
                linear_x=-0.2,
                duration=1.0
            )
            
            # 7. Update plant record
            logger.info(f"Watering completed: {plant_id}")
            
            # Return success
            return True, {
                "watered": True,
                "plant_id": plant_id,
                "amount": amount,
                "moisture_before": current_moisture,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error executing watering task: {e}")
            return False, {"error": str(e)}
    
    async def execute_pruning(self, task: RoboticTask) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute a plant pruning task.
        
        Args:
            task: Pruning task
            
        Returns:
            Success status and result data
        """
        try:
            # Get task parameters
            plant_id = task.metadata.get("plant_id")
            
            if not plant_id:
                return False, {"error": "Missing plant ID"}
                
            # Get plant location
            location = self.plant_locations.get(plant_id)
            
            if not location:
                # Default location
                location = {"x": 0.5, "y": 0.0, "theta": 0.0}
                
            # Execute pruning sequence - simplified for simulation
            logger.info(f"Executing simulated pruning for plant: {plant_id}")
            
            # 1. Approach plant
            success = await self.ros_bridge.move_robot(
                linear_x=0.2,
                duration=2.0
            )
            
            # Update task progress
            task.update_status(task.status, 0.3)
            
            # 2. Position manipulator
            success = await self.ros_bridge.control_actuator(
                actuator_id="manipulator_arm",
                command="position",
                parameters={"position": "prune"}
            )
            
            # Update task progress
            task.update_status(task.status, 0.5)
            
            # 3. Simulate pruning
            await asyncio.sleep(3.0)
            
            # 4. Return manipulator to home
            success = await self.ros_bridge.control_actuator(
                actuator_id="manipulator_arm",
                command="position",
                parameters={"position": "home"}
            )
            
            # Update task progress
            task.update_status(task.status, 0.8)
            
            # 5. Back away from plant
            success = await self.ros_bridge.move_robot(
                linear_x=-0.2,
                duration=1.0
            )
            
            # Return success
            return True, {
                "pruned": True,
                "plant_id": plant_id,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error executing pruning task: {e}")
            return False, {"error": str(e)}
    
    async def execute_plant_scan(self, task: RoboticTask) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute a plant scanning/monitoring task.
        
        Args:
            task: Scanning task
            
        Returns:
            Success status and result data
        """
        try:
            # Get task parameters
            plant_id = task.metadata.get("plant_id")
            
            if not plant_id:
                return False, {"error": "Missing plant ID"}
                
            # Get plant location
            location = self.plant_locations.get(plant_id)
            
            if not location:
                # Default location
                location = {"x": 0.5, "y": 0.0, "theta": 0.0}
                
            # Execute monitoring sequence
            logger.info(f"Scanning plant: {plant_id}")
            
            # 1. Approach plant
            success = await self.ros_bridge.move_robot(
                linear_x=0.2,
                duration=2.0
            )
            
            # Update task progress
            task.update_status(task.status, 0.2)
            
            # 2. Capture image
            image_path = await self.ros_bridge.capture_image(
                camera_id="main_camera",
                parameters={"format": "jpg"}
            )
            
            # Update task progress
            task.update_status(task.status, 0.4)
            
            # 3. Measure environmental conditions
            temp_data = await self.ros_bridge.read_sensor("temperature_ambient")
            humid_data = await self.ros_bridge.read_sensor("humidity_ambient")
            light_data = await self.ros_bridge.read_sensor("light_ambient")
            
            # Update task progress
            task.update_status(task.status, 0.6)
            
            # 4. Measure soil moisture
            # First position manipulator
            success = await self.ros_bridge.control_actuator(
                actuator_id="manipulator_arm",
                command="position",
                parameters={"position": "soil"}
            )
            
            moisture_data = await self.ros_bridge.read_sensor(
                "moisture_" + plant_id if plant_id else "moisture_sensor"
            )
            
            # Return manipulator to home
            success = await self.ros_bridge.control_actuator(
                actuator_id="manipulator_arm",
                command="position",
                parameters={"position": "home"}
            )
            
            # Update task progress
            task.update_status(task.status, 0.8)
            
            # 5. Back away from plant
            success = await self.ros_bridge.move_robot(
                linear_x=-0.2,
                duration=1.0
            )
            
            # Process sensor data
            sensor_data = {}
            
            if temp_data:
                sensor_data["temperature"] = temp_data.value
                
            if humid_data:
                sensor_data["humidity"] = humid_data.value
                
            if light_data:
                sensor_data["light"] = light_data.value
                
            if moisture_data:
                sensor_data["moisture"] = moisture_data.value
                
            # Return success
            return True, {
                "scanned": True,
                "plant_id": plant_id,
                "image_path": image_path,
                "sensor_data": sensor_data,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error executing plant scan task: {e}")
            return False, {"error": str(e)}
    
    async def execute_ecological_survey(self, task: RoboticTask) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute an ecological survey task.
        
        Args:
            task: Survey task
            
        Returns:
            Success status and result data
        """
        try:
            # Get task parameters
            survey_type = task.metadata.get("survey_type", "routine")
            params = task.metadata.get("survey_parameters", {})
            
            # Execute survey sequence
            logger.info(f"Performing ecological survey: {survey_type}")
            
            # 1. Move around garden
            patrol_points = [
                {"x": 1.0, "y": 0.0, "theta": 0.0},  # Forward
                {"x": 1.0, "y": 1.0, "theta": 1.57},  # Right
                {"x": 0.0, "y": 1.0, "theta": 3.14},  # Back
                {"x": 0.0, "y": 0.0, "theta": 4.71}   # Left/Home
            ]
            
            survey_data = {
                "temperature": [],
                "humidity": [],
                "light": [],
                "images": []
            }
            
            for i, point in enumerate(patrol_points):
                # Move to point
                logger.info(f"Moving to survey point {i+1}")
                
                success = await self.ros_bridge.move_robot(
                    linear_x=0.2 if point["x"] > 0 else -0.2,
                    linear_y=0.2 if point["y"] > 0 else -0.2,
                    duration=3.0
                )
                
                # Update task progress
                progress = 0.2 + ((i+1) / len(patrol_points)) * 0.6
                task.update_status(task.status, progress)
                
                # Collect data
                if params.get("temperature", True):
                    temp_data = await self.ros_bridge.read_sensor("temperature_ambient")
                    if temp_data:
                        survey_data["temperature"].append({
                            "value": temp_data.value,
                            "position": point,
                            "timestamp": time.time()
                        })
                        
                if params.get("humidity", True):
                    humid_data = await self.ros_bridge.read_sensor("humidity_ambient")
                    if humid_data:
                        survey_data["humidity"].append({
                            "value": humid_data.value,
                            "position": point,
                            "timestamp": time.time()
                        })
                        
                if params.get("light_levels", True):
                    light_data = await self.ros_bridge.read_sensor("light_ambient")
                    if light_data:
                        survey_data["light"].append({
                            "value": light_data.value,
                            "position": point,
                            "timestamp": time.time()
                        })
                        
                # Capture image
                image_path = await self.ros_bridge.capture_image(
                    camera_id="main_camera",
                    parameters={"format": "jpg"}
                )
                
                if image_path:
                    survey_data["images"].append({
                        "path": image_path,
                        "position": point,
                        "timestamp": time.time()
                    })
            
            # Return to home position
            success = await self.ros_bridge.move_robot(
                linear_x=-0.2,
                duration=2.0
            )
            
            # Generate survey summary
            summary = self._generate_survey_summary(survey_data)
            
            # Return success
            return True, {
                "survey_completed": True,
                "survey_type": survey_type,
                "summary": summary,
                "data": survey_data,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error executing ecological survey: {e}")
            return False, {"error": str(e)}
    
    def _generate_survey_summary(self, survey_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a summary of ecological survey data.
        
        Args:
            survey_data: Raw survey data
            
        Returns:
            Survey summary
        """
        summary = {}
        
        # Process temperature data
        if survey_data.get("temperature"):
            temp_values = [item["value"] for item in survey_data["temperature"]]
            summary["temperature"] = {
                "average": sum(temp_values) / len(temp_values),
                "min": min(temp_values),
                "max": max(temp_values),
                "variance": sum((x - (sum(temp_values) / len(temp_values))) ** 2 for x in temp_values) / len(temp_values)
            }
            
        # Process humidity data
        if survey_data.get("humidity"):
            humid_values = [item["value"] for item in survey_data["humidity"]]
            summary["humidity"] = {
                "average": sum(humid_values) / len(humid_values),
                "min": min(humid_values),
                "max": max(humid_values),
                "variance": sum((x - (sum(humid_values) / len(humid_values))) ** 2 for x in humid_values) / len(humid_values)
            }
            
        # Process light data
        if survey_data.get("light"):
            light_values = [item["value"] for item in survey_data["light"]]
            summary["light"] = {
                "average": sum(light_values) / len(light_values),
                "min": min(light_values),
                "max": max(light_values),
                "variance": sum((x - (sum(light_values) / len(light_values))) ** 2 for x in light_values) / len(light_values)
            }
            
        # Count images
        if survey_data.get("images"):
            summary["images"] = {
                "count": len(survey_data["images"])
            }
            
        return summary


# ==== 7. DEFAULT BEHAVIOR SYSTEM ====

class PulseDefaultBehaviorManager:
    """Manages default behaviors when no other tasks are present."""
    
    def __init__(self, 
                node_id: str,
                node_name: str,
                mesh_node: PulseMeshFederatedNode,
                ros_bridge: PulseROSBridge,
                care_scheduler: PulseCareTaskScheduler = None,
                gardening_actions: PulseGardeningActions = None,
                default_config: Dict[str, Any] = None):
        """
        Initialize default behavior manager.
        
        Args:
            node_id: Unique identifier for this manager
            node_name: Human-readable name
            mesh_node: PulseMesh node for communication
            ros_bridge: ROS bridge for hardware control
            care_scheduler: Care task scheduler
            gardening_actions: Gardening actions module
            default_config: Default behavior configuration
        """
        self.node_id = node_id
        self.node_name = node_name
        self.mesh_node = mesh_node
        self.ros_bridge = ros_bridge
        self.care_scheduler = care_scheduler
        self.gardening_actions = gardening_actions
        self.default_config = default_config or {}
        
        # Default behavior settings
        self.default_behavior = self.default_config.get("default_behavior", "gardening")
        self.behavior_priorities = self.default_config.get("behavior_priorities", {
            "human_interaction": 1,
            "gardening": 2,
            "ecological_restoration": 3,
            "exploration": 4,
            "rest": 5
        })
        
        # Behavior durations (seconds)
        self.behavior_durations = self.default_config.get("behavior_durations", {
            "gardening": 1800,  # 30 minutes
            "ecological_restoration": 1200,  # 20 minutes
            "exploration": 900,  # 15 minutes
            "rest": 600  # 10 minutes
        })
        
        # Behavior active flags
        self.active_behaviors = {
            "gardening": False,
            "ecological_restoration": False,
            "exploration": False,
            "human_interaction": False,
            "rest": False
        }
        
        # Human interaction tracking
        self.last_human_interaction = 0
        self.human_present = False
        
        # Default task ID
        self.default_task_id = None
        
        # Consent tracking
        self.has_consent = self.default_config.get("has_consent", True)
        
        # Internal state
        self.is_active = False
        self.monitor_task = None
    
    async def start(self) -> bool:
        """
        Start default behavior manager.
        
        Returns:
            Success status
        """
        try:
            # Register message handlers
            if hasattr(self.mesh_node, 'wifi_layer'):
                self.mesh_node.wifi_layer.register_handler(
                    RoboticsMessageIntent.USER_INTERACTION, self._handle_user_interaction)
                
            # Start monitor task
            self.monitor_task = asyncio.create_task(self._monitor_behavior())
            
            # Set active
            self.is_active = True
            
            logger.info(f"Default behavior manager started: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting default behavior manager: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop default behavior manager.
        
        Returns:
            Success status
        """
        try:
            # Set inactive
            self.is_active = False
            
            # Cancel tasks
            if self.monitor_task:
                self.monitor_task.cancel()
                try:
                    await self.monitor_task
                except asyncio.CancelledError:
                    pass
                    
            logger.info(f"Default behavior manager stopped: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping default behavior manager: {e}")
            return False
    
    async def set_consent(self, has_consent: bool) -> None:
        """
        Set consent status.
        
        Args:
            has_consent: Whether system has consent for autonomous behavior
        """
        self.has_consent = has_consent
        
        # Notify about consent change
        message = PulseMeshMessage(
            sender_id=self.node_id,
            sender_name=self.node_name,
            layer=CommunicationLayer.WIFI_MESH,
            intent=MessageIntent.CONSENT_VERIFICATION,
            priority=TransmissionPriority.HIGH,
            content=f"Consent status updated: {has_consent}",
            consent_verified=has_consent,
            metadata={
                "consent_status": has_consent,
                "consent_type": "default_behavior",
                "timestamp": time.time()
            }
        )
        
        await self.mesh_node.wifi_layer.send_message(message)
        
        # If consent withdrawn, stop any active behaviors
        if not has_consent:
            await self._stop_all_behaviors()
    
    async def set_human_presence(self, is_present: bool) -> None:
        """
        Set human presence status.
        
        Args:
            is_present: Whether humans are present
        """
        previous_state = self.human_present
        self.human_present = is_present
        
        # Update interaction time if newly present
        if is_present and not previous_state:
            self.last_human_interaction = time.time()
            
            # Transition to human interaction behavior if not already active
            if not self.active_behaviors["human_interaction"]:
                await self._transition_to_behavior("human_interaction")
        
        # If human leaves, check what behavior to transition to
        if not is_present and previous_state:
            # Wait a bit before transitioning away from human interaction
            # to avoid rapid switching if human briefly steps away
            asyncio.create_task(self._delayed_behavior_transition())
    
    async def _delayed_behavior_transition(self, delay: float = 30.0) -> None:
        """
        Delayed transition away from human interaction.
        
        Args:
            delay: Delay in seconds
        """
        await asyncio.sleep(delay)
        
        # If human still not present, transition to default behavior
        if not self.human_present and self.active_behaviors["human_interaction"]:
            await self._transition_to_behavior(self.default_behavior)
    
    async def _monitor_behavior(self) -> None:
        """Monitor and update default behaviors."""
        while self.is_active:
            try:
                # Skip if no consent
                if not self.has_consent:
                    await asyncio.sleep(5.0)
                    continue
                    
                # Check if ROS bridge is active and has no assigned task
                if (self.ros_bridge and self.ros_bridge.is_active and 
                    not self.ros_bridge.current_task):
                    
                    # Check for human presence
                    if self.human_present:
                        # Prioritize human interaction
                        if not self.active_behaviors["human_interaction"]:
                            await self._transition_to_behavior("human_interaction")
                    else:
                        # No humans, check for plant care needs first
                        if self.care_scheduler:
                            plant_task = await self.care_scheduler._check_for_plant_needs()
                            
                            if plant_task:
                                # Execute plant care task
                                await self.ros_bridge.add_task(plant_task)
                                continue
                                
                        # No immediate care needs, use default behavior
                        if not any(self.active_behaviors.values()):
                            await self._transition_to_behavior(self.default_behavior)
                            
                # Check if behavior has been active for too long
                for behavior, is_active in self.active_behaviors.items():
                    if is_active and hasattr(self, f"{behavior}_start_time"):
                        start_time = getattr(self, f"{behavior}_start_time")
                        duration = self.behavior_durations.get(behavior, 1800)
                        
                        if time.time() - start_time > duration:
                            # Behavior has been active long enough, transition
                            next_behavior = self._get_next_behavior(behavior)
                            await self._transition_to_behavior(next_behavior)
                
                # Wait before next check
                await asyncio.sleep(5.0)
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error in behavior monitoring: {e}")
                await asyncio.sleep(30.0)
    
    async def _transition_to_behavior(self, behavior: str) -> None:
        """
        Transition to a new behavior.
        
        Args:
            behavior: New behavior to activate
        """
        # Skip if already in this behavior
        if self.active_behaviors.get(behavior, False):
            return
            
        logger.info(f"Transitioning to behavior: {behavior}")
        
        # Stop all current behaviors
        await self._stop_all_behaviors()
        
        # Start new behavior
        if behavior == "gardening":
            await self._start_gardening_behavior()
        elif behavior == "ecological_restoration":
            await self._start_ecological_behavior()
        elif behavior == "exploration":
            await self._start_exploration_behavior()
        elif behavior == "human_interaction":
            await self._start_human_interaction_behavior()
        elif behavior == "rest":
            await self._start_rest_behavior()
            
        # Record start time
        setattr(self, f"{behavior}_start_time", time.time())
        
        # Update active flag
        self.active_behaviors[behavior] = True
        
        # Create behavior transition message
        message = PulseMeshMessage(
            sender_id=self.node_id,
            sender_name=self.node_name,
            layer=CommunicationLayer.WIFI_MESH,
            intent=MessageIntent.STATE_BROADCAST,
            priority=TransmissionPriority.NORMAL,
            content=f"Behavior transition: {behavior}",
            metadata={
                "behavior": behavior,
                "start_time": time.time(),
                "duration": self.behavior_durations.get(behavior, 1800),
                "human_present": self.human_present,
                "timestamp": time.time()
            }
        )
        
        await self.mesh_node.wifi_layer.send_message(message)
    
    async def _stop_all_behaviors(self) -> None:
        """Stop all active behaviors."""
        # Stop all behavior flags
        for behavior in self.active_behaviors:
            self.active_behaviors[behavior] = False
            
        # If a default task is running, cancel it
        if self.default_task_id and self.ros_bridge and self.ros_bridge.current_task:
            if self.ros_bridge.current_task.task_id == self.default_task_id:
                # Cancel task
                self.ros_bridge.current_task.update_status(
                    TaskStatus.CANCELLED, 
                    self.ros_bridge.current_task.progress,
                    {"cancelled_reason": "behavior_transition"}
                )
                
                # Clear current task
                self.ros_bridge.current_task = None
                
                # Clear ID
                self.default_task_id = None
    
    def _get_next_behavior(self, current_behavior: str) -> str:
        """
        Get next behavior in rotation.
        
        Args:
            current_behavior: Current active behavior
            
        Returns:
            Next behavior to activate
        """
        # If human present, always go to human interaction
        if self.human_present:
            return "human_interaction"
            
        # Create ordered list of behaviors
        behaviors = sorted(
            ["gardening", "ecological_restoration", "exploration", "rest"],
            key=lambda b: self.behavior_priorities.get(b, 99)
        )
        
        # Find current index
        try:
            current_index = behaviors.index(current_behavior)
            # Return next in rotation
            return behaviors[(current_index + 1) % len(behaviors)]
        except ValueError:
            # Current behavior not in list, return default
            return self.default_behavior
    
    async def _start_gardening_behavior(self) -> None:
        """Start gardening behavior."""
        logger.info("Starting gardening behavior")
        
        # Create gardening task if care scheduler available
        if self.care_scheduler:
            # Try to find a plant that needs care
            plant_task = await self.care_scheduler._check_for_plant_needs()
            
            if plant_task:
                # Start task
                if self.ros_bridge:
                    self.default_task_id = plant_task.task_id
                    await self.ros_bridge.add_task(plant_task)
                    return
                    
        # No specific plant needs or no care scheduler, create general garden task
        if self.ros_bridge:
            task = RoboticTask(
                name="Garden Survey",
                task_type="ecological_survey",
                priority=TaskPriority.SCHEDULED,
                estimated_duration=900.0,
                tags=["gardening", "default_behavior"],
                metadata={
                    "survey_type": "garden",
                    "survey_parameters": {
                        "light_levels": True,
                        "temperature": True,
                        "humidity": True,
                        "plant_health": True,
                        "soil_conditions": True
                    },
                    "behavior": "gardening"
                }
            )
            
            self.default_task_id = task.task_id
            await self.ros_bridge.add_task(task)
    
    async def _start_ecological_behavior(self) -> None:
        """Start ecological restoration behavior."""
        logger.info("Starting ecological restoration behavior")
        
        # Create ecological task
        if self.ros_bridge:
            task = RoboticTask(
                name="Ecological Survey",
                task_type="ecological_survey",
                priority=TaskPriority.SCHEDULED,
                estimated_duration=1200.0,
                tags=["ecological_restoration", "default_behavior"],
                metadata={
                    "survey_type": "ecological",
                    "survey_parameters": {
                        "wildlife": True,
                        "ecosystem_health": True,
                        "invasive_species": True,
                        "biodiversity": True,
                        "environmental_conditions": True
                    },
                    "behavior": "ecological_restoration"
                }
            )
            
            self.default_task_id = task.task_id
            await self.ros_bridge.add_task(task)
    
    async def _start_exploration_behavior(self) -> None:
        """Start exploration behavior."""
        logger.info("Starting exploration behavior")
        
        # Create exploration task
        if self.ros_bridge:
            task = RoboticTask(
                name="Area Exploration",
                task_type="explore",
                priority=TaskPriority.SCHEDULED,
                estimated_duration=900.0,
                tags=["exploration", "default_behavior"],
                metadata={
                    "exploration_type": "frontier",
                    "coverage": "spiral",
                    "data_collection": {
                        "images": True,
                        "environmental": True,
                        "mapping": True
                    },
                    "behavior": "exploration"
                }
            )
            
            self.default_task_id = task.task_id
            await self.ros_bridge.add_task(task)
    
    async def _start_human_interaction_behavior(self) -> None:
        """Start human interaction behavior."""
        logger.info("Starting human interaction behavior")
        
        # Create interaction task
        if self.ros_bridge:
            task = RoboticTask(
                name="Human Interaction",
                task_type="social_interaction",
                priority=TaskPriority.USER_REQUESTED,
                estimated_duration=600.0,
                tags=["human_interaction", "default_behavior"],
                metadata={
                    "interaction_type": "passive",
                    "interaction_mode": "reactive",
                    "behavior": "human_interaction"
                }
            )
            
            self.default_task_id = task.task_id
            await self.ros_bridge.add_task(task)
    
    async def _start_rest_behavior(self) -> None:
        """Start rest/idle behavior."""
        logger.info("Starting rest behavior")
        
        # Create rest task
        if self.ros_bridge:
            task = RoboticTask(
                name="System Rest",
                task_type="idle",
                priority=TaskPriority.IDLE,
                estimated_duration=600.0,
                tags=["rest", "default_behavior"],
                metadata={
                    "rest_type": "power_saving",
                    "monitoring": True,
                    "behavior": "rest"
                }
            )
            
            self.default_task_id = task.task_id
            await self.ros_bridge.add_task(task)
    
    def _handle_user_interaction(self, message: PulseMeshMessage) -> None:
        """
        Handle user interaction message.
        
        Args:
            message: User interaction message
        """
        # Skip own messages
        if message.sender_id == self.node_id:
            return
            
        # Extract interaction info
        interaction_type = message.metadata.get("interaction_type", "presence")
        
        if interaction_type == "presence":
            # Human presence detected
            is_present = message.metadata.get("is_present", True)
            asyncio.create_task(self.set_human_presence(is_present))
            
        elif interaction_type == "consent":
            # Consent update
            has_consent = message.metadata.get("has_consent", True)
            asyncio.create_task(self.set_consent(has_consent))


# ==== 8. MAIN INTEGRATION CLASS ====

class PulseROSIntegration:
    """Main integration class for PulseROS system."""
    
    def __init__(self, 
                node_id: str,
                node_name: str,
                mesh_node: PulseMeshFederatedNode,
                config: Dict[str, Any] = None):
        """
        Initialize PulseROS integration.
        
        Args:
            node_id: Unique identifier for this integrator
            node_name: Human-readable name
            mesh_node: PulseMesh node for communication
            config: Configuration options
        """
        self.node_id = node_id
        self.node_name = node_name
        self.mesh_node = mesh_node
        self.config = config or {}
        
        # Components
        self.ros_bridge = None
        self.redundancy_manager = None
        self.power_manager = None
        self.care_scheduler = None
        self.gardening_actions = None
        self.default_behavior_manager = None
        
        # Component configuration
        self.ros_config = self.config.get("ros", {})
        self.redundancy_config = self.config.get("redundancy", {})
        self.power_config = self.config.get("power", {})
        self.care_config = self.config.get("care", {})
        self.gardening_config = self.config.get("gardening", {})
        self.behavior_config = self.config.get("behavior", {})
        
        # Device role
        self.device_type = self.config.get("device_type", "primary")
        self.roles = [NodeRole[role] for role in self.config.get("roles", ["MOTION"])]
        
        # Internal state
        self.is_active = False
        self.startup_complete = False
    
    async def initialize(self) -> bool:
        """
        Initialize PulseROS integration.
        
        Returns:
            Success status
        """
        try:
            # Create ROS bridge
            self.ros_bridge = PulseROSBridge(
                node_id=f"{self.node_id}_ros",
                node_name=f"{self.node_name} ROS",
                mesh_node=self.mesh_node,
                ros_node_name=self.ros_config.get("node_name", "pulse_ros"),
                device_type=self.device_type,
                roles=self.roles
            )
            
            # Initialize ROS bridge
            ros_init = await self.ros_bridge.initialize()
            
            if not ros_init:
                logger.error("Failed to initialize ROS bridge")
                return False
                
            # Create redundancy manager
            self.redundancy_manager = PulseRedundancyManager(
                node_id=f"{self.node_id}_redundancy",
                node_name=f"{self.node_name} Redundancy",
                mesh_node=self.mesh_node,
                primary_nodes=self.redundancy_config.get("primary_nodes", {}),
                backup_nodes=self.redundancy_config.get("backup_nodes", {})
            )
            
            # Create power manager
            self.power_manager = PulsePowerManager(
                node_id=f"{self.node_id}_power",
                node_name=f"{self.node_name} Power",
                mesh_node=self.mesh_node,
                min_operating_power=self.power_config.get("min_operating_power", 0.2),
                critical_tasks=self.power_config.get("critical_tasks", ["plant_watering"])
            )
            
            # Create care scheduler
            self.care_scheduler = PulseCareTaskScheduler(
                node_id=f"{self.node_id}_care",
                node_name=f"{self.node_name} Care",
                mesh_node=self.mesh_node,
                care_categories=self.care_config.get("care_categories")
            )
            
            # Create gardening actions
            self.gardening_actions = PulseGardeningActions(
                node_id=f"{self.node_id}_gardening",
                node_name=f"{self.node_name} Gardening",
                ros_bridge=self.ros_bridge,
                mesh_node=self.mesh_node,
                gardening_config=self.gardening_config
            )
            
            # Create default behavior manager
            self.default_behavior_manager = PulseDefaultBehaviorManager(
                node_id=f"{self.node_id}_behavior",
                node_name=f"{self.node_name} Behavior",
                mesh_node=self.mesh_node,
                ros_bridge=self.ros_bridge,
                care_scheduler=self.care_scheduler,
                gardening_actions=self.gardening_actions,
                default_config=self.behavior_config
            )
            
            # Register ROS bridge with care scheduler
            self.care_scheduler.register_ros_bridge(self.ros_bridge.node_id, self.ros_bridge)
            
            logger.info(f"PulseROS integration initialized: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing PulseROS integration: {e}")
            traceback.print_exc()
            return False
    
    async def start(self) -> bool:
        """
        Start PulseROS integration.
        
        Returns:
            Success status
        """
        try:
            # Start components
            if self.redundancy_manager:
                await self.redundancy_manager.start()
                
            if self.power_manager:
                await self.power_manager.start()
                
            if self.care_scheduler:
                await self.care_scheduler.start()
                
            if self.gardening_actions:
                await self.gardening_actions.start()
                
            if self.default_behavior_manager:
                await self.default_behavior_manager.start()
                
            # Register with redundancy manager
            if self.redundancy_manager and self.ros_bridge:
                node_info = {
                    "device_type": self.device_type,
                    "roles": [role.name for role in self.roles],
                    "capabilities": self.ros_bridge.capabilities,
                    "is_active": True
                }
                
                await self.redundancy_manager.register_node(
                    self.ros_bridge.node_id, node_info)
                    
            # Register with power manager
            if self.power_manager and self.ros_bridge:
                power_profile = {
                    "full": 1.0,
                    "balanced": 0.7,
                    "eco": 0.4,
                    "minimal": 0.2,
                    "emergency": 0.1
                }
                
                self.power_manager.register_device(
                    self.ros_bridge.node_id, power_profile)
                    
            # Set as active
            self.is_active = True
            self.startup_complete = True
            
            logger.info(f"PulseROS integration started: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error starting PulseROS integration: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop PulseROS integration.
        
        Returns:
            Success status
        """
        try:
            # Stop components in reverse order
            if self.default_behavior_manager:
                await self.default_behavior_manager.stop()
                
            if self.gardening_actions:
                await self.gardening_actions.stop()
                
            if self.care_scheduler:
                await self.care_scheduler.stop()
                
            if self.power_manager:
                await self.power_manager.stop()
                
            if self.redundancy_manager:
                await self.redundancy_manager.stop()
                
            if self.ros_bridge:
                await self.ros_bridge.shutdown()
                
            # Set as inactive
            self.is_active = False
            
            logger.info(f"PulseROS integration stopped: {self.node_name}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping PulseROS integration: {e}")
            return False
    
    async def add_plant(self, plant_data: Dict[str, Any]) -> Optional[str]:
        """
        Add a plant to the care system.
        
        Args:
            plant_data: Plant information
            
        Returns:
            Plant ID if successful, None otherwise
        """
        try:
            # Create plant
            plant = PlantData(
                plant_id=plant_data.get("plant_id", str(uuid.uuid4())),
                name=plant_data.get("name", "Unknown Plant"),
                scientific_name=plant_data.get("scientific_name"),
                type=plant_data.get("type", "unknown"),
                location=plant_data.get("location"),
                moisture_target=plant_data.get("moisture_target", (0.4, 0.7)),
                light_target=plant_data.get("light_target", (0.3, 0.8)),
                temperature_target=plant_data.get("temperature_target", (15.0, 30.0)),
                watering_frequency=plant_data.get("watering_frequency", 86400),
                growth_stage=plant_data.get("growth_stage", "seedling"),
                health_status=plant_data.get("health_status", "good")
            )
            
            # Add to care scheduler
            if self.care_scheduler:
                success = await self.care_scheduler.add_plant(plant)
                
                if success:
                    return plant.plant_id
                    
            return None
            
        except Exception as e:
            logger.error(f"Error adding plant: {e}")
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get status of PulseROS integration.
        
        Returns:
            Status information
        """
        status = {
            "node_id": self.node_id,
            "node_name": self.node_name,
            "is_active": self.is_active,
            "startup_complete": self.startup_complete,
            "device_type": self.device_type,
            "roles": [role.name for role in self.roles],
            "components": {}
        }
        
        # Add component status
        if self.ros_bridge:
            status["components"]["ros_bridge"] = {
                "is_active": self.ros_bridge.is_active,
                "current_task": (self.ros_bridge.current_task.task_id 
                               if self.ros_bridge.current_task else None),
                "battery_level": self.ros_bridge.battery_level
            }
            
        if self.redundancy_manager:
            status["components"]["redundancy_manager"] = {
                "is_active": self.redundancy_manager.is_active,
                "active_nodes": len([n for n, v in self.redundancy_manager.active_nodes.items() if v])
            }
            
        if self.power_manager:
            status["components"]["power_manager"] = {
                "is_active": self.power_manager.is_active,
                "power_mode": self.power_manager.current_mode,
                "current_power": self.power_manager.current_power
            }
            
        if self.care_scheduler:
            status["components"]["care_scheduler"] = {
                "is_active": self.care_scheduler.is_active,
                "plant_count": len(self.care_scheduler.plants),
                "active_tasks": len(self.care_scheduler.active_tasks)
            }
            
        if self.default_behavior_manager:
            active_behavior = None
            for behavior, is_active in self.default_behavior_manager.active_behaviors.items():
                if is_active:
                    active_behavior = behavior
                    break
                    
            status["components"]["default_behavior_manager"] = {
                "is_active": self.default_behavior_manager.is_active,
                "has_consent": self.default_behavior_manager.has_consent,
                "human_present": self.default_behavior_manager.human_present,
                "active_behavior": active_behavior,
                "default_behavior": self.default_behavior_manager.default_behavior
            }
            
        return status


# ==== 9. HELPER FUNCTIONS ====

async def create_pulse_ros_system(
    node_id: Optional[str] = None,
    node_name: str = "PulseROS",
    mesh_node: Optional[PulseMeshFederatedNode] = None,
    config: Optional[Dict[str, Any]] = None
) -> PulseROSIntegration:
    """
    Create a complete PulseROS system.
    
    Args:
        node_id: Unique identifier (auto-generated if None)
        node_name: Human-readable name
        mesh_node: Existing PulseMesh node
        config: Configuration options
        
    Returns:
        PulseROS integration instance
    """
    # Generate node ID if not provided
    if not node_id:
        node_id = f"pulse_ros_{uuid.uuid4().hex[:8]}"
        
    # Use default config if not provided
    if not config:
        config = {
            "device_type": "primary",
            "roles": ["COORDINATOR", "MOTION", "PERCEPTION"],
            "ros": {
                "node_name": f"{node_name.lower()}_ros"
            },
            "power": {
                "min_operating_power": 0.2,
                "critical_tasks": ["plant_watering", "emergency_response"]
            },
            "behavior": {
                "default_behavior": "gardening",
                "has_consent": True
            }
        }
        
    # Create PulseMesh node if not provided
    if not mesh_node:
        from PulseMesh import create_pulsemesh_node
        
        mesh_node = create_pulsemesh_node(
            node_id=f"{node_id}_mesh",
            node_name=f"{node_name} Mesh"
        )
        
        # Initialize and start mesh node
        await mesh_node.initialize()
        await mesh_node.start()
        
    # Create PulseROS integration
    integration = PulseROSIntegration(
        node_id=node_id,
        node_name=node_name,
        mesh_node=mesh_node,
        config=config
    )
    
    # Initialize and start
    await integration.initialize()
    await integration.start()
    
    return integration


async def create_redundant_ros_system(
    primary_config: Dict[str, Any],
    backup_config: Optional[Dict[str, Any]] = None,
    mesh_node: Optional[PulseMeshFederatedNode] = None
) -> Tuple[PulseROSIntegration, Optional[PulseROSIntegration]]:
    """
    Create a redundant PulseROS system with primary and backup.
    
    Args:
        primary_config: Configuration for primary system
        backup_config: Configuration for backup system
        mesh_node: Existing PulseMesh node
        
    Returns:
        Tuple of (primary integration, backup integration)
    """
    # Create PulseMesh node if not provided
    if not mesh_node:
        from PulseMesh import create_pulsemesh_node
        
        mesh_node = create_pulsemesh_node(
            node_id=f"pulse_ros_mesh_{uuid.uuid4().hex[:8]}",
            node_name="PulseROS Mesh"
        )
        
        # Initialize and start mesh node
        await mesh_node.initialize()
        await mesh_node.start()
        
    # Ensure primary config has correct device type
    if not primary_config.get("device_type"):
        primary_config["device_type"] = "primary"
        
    # Create primary system
    primary = await create_pulse_ros_system(
        node_id=primary_config.get("node_id"),
        node_name=primary_config.get("node_name", "PulseROS Primary"),
        mesh_node=mesh_node,
        config=primary_config
    )
    
    # Create backup system if config provided
    backup = None
    if backup_config:
        # Ensure backup config has correct device type
        if not backup_config.get("device_type"):
            backup_config["device_type"] = "backup"
            
        backup = await create_pulse_ros_system(
            node_id=backup_config.get("node_id"),
            node_name=backup_config.get("node_name", "PulseROS Backup"),
            mesh_node=mesh_node,
            config=backup_config
        )
    
    return primary, backup


async def example_garden_bot():
    """Example usage of PulseROS for a garden robot."""
    # Create PulseROS system
    system = await create_pulse_ros_system(
        node_name="GardenBot",
        config={
            "device_type": "primary",
            "roles": ["COORDINATOR", "MOTION", "PERCEPTION"],
            "behavior": {
                "default_behavior": "gardening",
                "has_consent": True
            }
        }
    )
    
    # Add sample plants
    tomato = await system.add_plant({
        "name": "Tomato Plant",
        "scientific_name": "Solanum lycopersicum",
        "type": "vegetable",
        "location": "garden_bed_1",
        "moisture_target": (0.5, 0.7),
        "light_target": (0.6, 0.9),
        "temperature_target": (18.0, 32.0),
        "watering_frequency": 43200  # Twice daily
    })
    
    basil = await system.add_plant({
        "name": "Basil",
        "scientific_name": "Ocimum basilicum",
        "type": "herb",
        "location": "garden_bed_2",
        "moisture_target": (0.4, 0.6),
        "light_target": (0.5, 0.8),
        "temperature_target": (20.0, 30.0),
        "watering_frequency": 86400  # Daily
    })
    
    # Run system for a while
    try:
        # Simulate operation
        logger.info("GardenBot started, running for 60 seconds...")
        await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        logger.info("Example interrupted")
        
    finally:
        # Stop system
        await system.stop()
        
    return system


if __name__ == "__main__":
    # Run example
    asyncio.run(example_garden_bot())