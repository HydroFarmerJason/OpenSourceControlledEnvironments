import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, date
import seaborn as sns
import os
import json
import requests
import time
import uuid
import hashlib
import logging
import threading
import cv2
from typing import Dict, List, Tuple, Optional, Any, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict, deque
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from scipy import optimize
from scipy.signal import find_peaks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("freight_farm_integration")

# =====1. CORE ENUMS AND DATA STRUCTURES=====

class GrowthStage(Enum):
    """Plant growth stages."""
    GERMINATION = auto()    # Initial sprouting
    SEEDLING = auto()       # First true leaves
    VEGETATIVE = auto()     # Leaf and stem growth
    FLOWERING = auto()      # Flowering/fruiting
    HARVEST = auto()        # Ready for harvest


class SensorType(Enum):
    """Types of sensors in the farm system."""
    TEMPERATURE = auto()     # Temperature sensors
    HUMIDITY = auto()        # Humidity sensors
    CO2 = auto()             # CO2 sensors
    LIGHT = auto()           # Light intensity sensors (PPFD)
    EC = auto()              # Electrical conductivity
    PH = auto()              # pH sensors
    WATER_TEMP = auto()      # Water temperature
    WATER_LEVEL = auto()     # Water level
    NUTRIENT_A = auto()      # Nutrient A level
    NUTRIENT_B = auto()      # Nutrient B level
    CAMERA = auto()          # Visual cameras
    THERMAL = auto()         # Thermal cameras
    FLOW = auto()            # Water flow sensors
    PRESSURE = auto()        # Pressure sensors
    POWER = auto()           # Power consumption monitors


class AlertLevel(Enum):
    """Alert levels for system notifications."""
    INFO = auto()           # Informational
    WARNING = auto()        # Warning, needs attention
    CRITICAL = auto()       # Critical, immediate action required
    SUCCESS = auto()        # Positive outcome


# ===== HARMONY STATE TRIGGERS =====

class HarmonyState(Enum):
    """Harmonious states that can trigger actions."""
    OPTIMAL_GROWTH = auto()      # All parameters in optimal range
    STRESS_BALANCED = auto()     # Balanced state after stress
    ENERGY_EFFICIENT = auto()    # Energy efficiency with good growth
    HEALING_ACTIVE = auto()      # State conducive to plant recovery
    TRANSITION_POINT = auto()    # Unique transition between growth phases
    CIRCADIAN_ALIGNED = auto()   # Perfect day/night cycle alignment


@dataclass
class HarmonyPattern:
    """Pattern representing a harmonious state."""
    pattern_id: str
    pattern_name: str
    state_type: HarmonyState
    parameter_relationships: Dict[Tuple[str, str], float]  # Param pairs and their ideal correlation
    parameter_ratios: Dict[str, float]  # Param values and their ideal ratios
    vector_representation: np.ndarray
    confidence_threshold: float = 0.75
    duration_required: float = 0  # Seconds required to maintain this pattern


@dataclass
class HarmonyTrigger:
    """Trigger that activates when a harmony state is detected."""
    trigger_id: str
    harmony_state: HarmonyState
    actions: List[str]  # List of actions to perform
    cooldown_period: float = 3600  # Seconds before this trigger can fire again
    last_triggered: Optional[float] = None
    notification_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FarmState:
    """Current state of the farm system."""
    # Core properties
    farm_id: str
    timestamp: datetime
    
    # Environmental parameters
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    co2: Optional[float] = None
    ppfd: Optional[float] = None
    ec: Optional[float] = None
    ph: Optional[float] = None
    water_temp: Optional[float] = None
    water_level: Optional[float] = None
    nutrient_a: Optional[float] = None
    nutrient_b: Optional[float] = None
    fan_speed: Optional[float] = None
    
    # System states
    light_status: Optional[str] = None
    pump_status: Optional[str] = None
    
    # Vector representation
    state_vector: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert farm state to dictionary."""
        return {
            "farm_id": self.farm_id,
            "timestamp": self.timestamp.isoformat(),
            "temperature": self.temperature,
            "humidity": self.humidity,
            "co2": self.co2,
            "ppfd": self.ppfd,
            "ec": self.ec,
            "ph": self.ph,
            "water_temp": self.water_temp,
            "water_level": self.water_level,
            "nutrient_a": self.nutrient_a,
            "nutrient_b": self.nutrient_b,
            "fan_speed": self.fan_speed,
            "light_status": self.light_status,
            "pump_status": self.pump_status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FarmState':
        """Create FarmState from dictionary."""
        # Parse timestamp
        timestamp = datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"]
        
        return cls(
            farm_id=data.get("farm_id", ""),
            timestamp=timestamp,
            temperature=data.get("temperature"),
            humidity=data.get("humidity"),
            co2=data.get("co2"),
            ppfd=data.get("ppfd"),
            ec=data.get("ec"),
            ph=data.get("ph"),
            water_temp=data.get("water_temp"),
            water_level=data.get("water_level"),
            nutrient_a=data.get("nutrient_a"),
            nutrient_b=data.get("nutrient_b"),
            fan_speed=data.get("fan_speed"),
            light_status=data.get("light_status"),
            pump_status=data.get("pump_status")
        )


@dataclass
class CropProfile:
    """Profile for a specific crop type."""
    # Core properties
    crop_id: str
    crop_name: str
    
    # Growth parameters
    growth_duration: int  # Days from seedling to harvest
    growth_stages: Dict[GrowthStage, Tuple[int, int]]  # Stage: (start_day, end_day)
    
    # Optimal growing parameters per growth stage
    optimal_ranges: Dict[GrowthStage, Dict[str, Dict[str, float]]]
    
    # Vector representation of ideal growth
    ideal_vectors: Dict[GrowthStage, np.ndarray] = field(default_factory=dict)
    
    # Additional metadata
    planting_density: Optional[float] = None  # Plants per square meter
    expected_yield: Optional[float] = None  # kg per square meter
    nutrient_requirements: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert crop profile to dictionary."""
        return {
            "crop_id": self.crop_id,
            "crop_name": self.crop_name,
            "growth_duration": self.growth_duration,
            "growth_stages": {stage.name: days for stage, days in self.growth_stages.items()},
            "planting_density": self.planting_density,
            "expected_yield": self.expected_yield,
            "nutrient_requirements": self.nutrient_requirements
        }
    
    def get_optimal_range(self, parameter: str, days_from_seedling: int) -> Tuple[float, float]:
        """Get optimal parameter range based on days from seedling."""
        # Determine current growth stage
        current_stage = None
        for stage, (start, end) in self.growth_stages.items():
            if start <= days_from_seedling <= end:
                current_stage = stage
                break
        
        if current_stage is None or parameter not in self.optimal_ranges.get(current_stage, {}):
            # Default fallback to VEGETATIVE stage if stage not found
            current_stage = GrowthStage.VEGETATIVE
        
        # Get optimal range for parameter at current stage
        param_range = self.optimal_ranges.get(current_stage, {}).get(parameter, {})
        return param_range.get("min", 0), param_range.get("max", 0)


@dataclass
class Alert:
    """Alert notification from the system."""
    # Core properties
    alert_id: str
    timestamp: datetime
    alert_level: AlertLevel
    
    # Alert content
    title: str
    message: str
    parameter: Optional[str] = None
    value: Optional[float] = None
    optimal_range: Optional[Tuple[float, float]] = None
    
    # Action information
    action_required: bool = False
    recommended_action: Optional[str] = None
    
    # Alert status
    acknowledged: bool = False
    resolved: bool = False
    resolution_timestamp: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            "alert_id": self.alert_id,
            "timestamp": self.timestamp.isoformat(),
            "alert_level": self.alert_level.name,
            "title": self.title,
            "message": self.message,
            "parameter": self.parameter,
            "value": self.value,
            "optimal_range": self.optimal_range,
            "action_required": self.action_required,
            "recommended_action": self.recommended_action,
            "acknowledged": self.acknowledged,
            "resolved": self.resolved,
            "resolution_timestamp": self.resolution_timestamp.isoformat() if self.resolution_timestamp else None,
            "resolution_notes": self.resolution_notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Alert':
        """Create Alert from dictionary."""
        return cls(
            alert_id=data.get("alert_id", str(uuid.uuid4())),
            timestamp=datetime.fromisoformat(data["timestamp"]) if isinstance(data["timestamp"], str) else data["timestamp"],
            alert_level=AlertLevel[data["alert_level"]] if isinstance(data["alert_level"], str) else data["alert_level"],
            title=data["title"],
            message=data["message"],
            parameter=data.get("parameter"),
            value=data.get("value"),
            optimal_range=data.get("optimal_range"),
            action_required=data.get("action_required", False),
            recommended_action=data.get("recommended_action"),
            acknowledged=data.get("acknowledged", False),
            resolved=data.get("resolved", False),
            resolution_timestamp=datetime.fromisoformat(data["resolution_timestamp"]) if data.get("resolution_timestamp") else None,
            resolution_notes=data.get("resolution_notes")
        )


# =====2. CORE FARM MONITOR SYSTEM=====

class FreightFarmMonitor:
    """
    A comprehensive system for monitoring and optimizing Freight Farm hydroponic containers.
    Processes data from farmhand.ag exports and provides analytics and recommendations.
    """
    
    def __init__(self, 
               farm_id: str = "default_farm",
               crop_type: str = "Lettuce", 
               dimension: int = 32):
        """
        Initialize the FreightFarmMonitor system.
        
        Args:
            farm_id: Unique identifier for the farm
            crop_type: Type of crop being grown (determines optimal ranges)
            dimension: Dimension of vector representations
        """
        self.farm_id = farm_id
        self.crop_type = crop_type
        self.dimension = dimension
        self.data = None
        self.analysis_results = {}
        self.recommendations = []
        self.alerts = []
        
        # Initialize components
        self.farm_data_store = FarmDataStore(farm_id)
        self.pattern_engine = PatternRecognitionEngine(dimension)
        self.forecast_engine = ForecastEngine(dimension)
        
        # State tracking
        self.current_state = None
        self.last_update = None
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring = threading.Event()
        
        # Harmony state triggers
        self.harmony_triggers = {}
        
        # Define optimal growing conditions for different crops
        self.optimal_ranges = {
            'Lettuce': {
                'Temperature': {'min': 17, 'max': 24, 'unit': '°C'},
                'Humidity': {'min': 50, 'max': 70, 'unit': '%'},
                'CO2': {'min': 800, 'max': 1200, 'unit': 'ppm'},
                'PPFD': {'min': 200, 'max': 400, 'unit': 'μmol/m²/s'},
                'EC': {'min': 1000, 'max': 1400, 'unit': 'μS/cm'},
                'pH': {'min': 5.8, 'max': 6.2, 'unit': ''},
                'WaterTemp': {'min': 18, 'max': 22, 'unit': '°C'}
            },
            'Herbs': {
                'Temperature': {'min': 18, 'max': 26, 'unit': '°C'},
                'Humidity': {'min': 40, 'max': 60, 'unit': '%'},
                'CO2': {'min': 800, 'max': 1200, 'unit': 'ppm'},
                'PPFD': {'min': 300, 'max': 500, 'unit': 'μmol/m²/s'},
                'EC': {'min': 1200, 'max': 1800, 'unit': 'μS/cm'},
                'pH': {'min': 5.5, 'max': 6.5, 'unit': ''},
                'WaterTemp': {'min': 18, 'max': 23, 'unit': '°C'}
            },
            'Strawberries': {
                'Temperature': {'min': 18, 'max': 25, 'unit': '°C'},
                'Humidity': {'min': 65, 'max': 75, 'unit': '%'},
                'CO2': {'min': 800, 'max': 1200, 'unit': 'ppm'},
                'PPFD': {'min': 350, 'max': 600, 'unit': 'μmol/m²/s'},
                'EC': {'min': 1200, 'max': 1600, 'unit': 'μS/cm'},
                'pH': {'min': 5.5, 'max': 6.2, 'unit': ''},
                'WaterTemp': {'min': 18, 'max': 22, 'unit': '°C'}
            },
            'Kale': {
                'Temperature': {'min': 15, 'max': 24, 'unit': '°C'},
                'Humidity': {'min': 50, 'max': 70, 'unit': '%'},
                'CO2': {'min': 800, 'max': 1200, 'unit': 'ppm'},
                'PPFD': {'min': 250, 'max': 450, 'unit': 'μmol/m²/s'},
                'EC': {'min': 1200, 'max': 1500, 'unit': 'μS/cm'},
                'pH': {'min': 5.8, 'max': 6.3, 'unit': ''},
                'WaterTemp': {'min': 18, 'max': 21, 'unit': '°C'}
            }
        }
        
        # Map of field names to units and display names
        self.field_units = {
            'Temperature': {'unit': '°C', 'display': 'Air Temperature'},
            'Humidity': {'unit': '%', 'display': 'Humidity'},
            'CO2': {'unit': 'ppm', 'display': 'CO₂ Level'},
            'PPFD': {'unit': 'μmol/m²/s', 'display': 'Light Intensity (PPFD)'},
            'EC': {'unit': 'μS/cm', 'display': 'Electrical Conductivity (EC)'},
            'pH': {'unit': '', 'display': 'pH Level'},
            'WaterTemp': {'unit': '°C', 'display': 'Water Temperature'},
            'WaterLevel': {'unit': '%', 'display': 'Water Level'},
            'NutrientA': {'unit': '%', 'display': 'Nutrient A Level'},
            'NutrientB': {'unit': '%', 'display': 'Nutrient B Level'},
            'FanSpeed': {'unit': '%', 'display': 'Fan Speed'}
        }
        
        # Initialize crop profiles
        self._initialize_crop_profiles()

        # Initialize default harmony triggers
        self.create_default_harmony_triggers()
        
        logger.info(f"Initialized FreightFarmMonitor for farm {farm_id} with crop type {crop_type}")
    
    def add_crop_type(self, 
                    crop_name: str, 
                    temperature_range: Tuple[float, float],
                    humidity_range: Tuple[float, float],
                    co2_range: Tuple[float, float],
                    ppfd_range: Tuple[float, float],
                    ec_range: Tuple[float, float],
                    ph_range: Tuple[float, float],
                    water_temp_range: Tuple[float, float]) -> bool:
        """
        Add a new crop type with its optimal parameter ranges.
        
        Args:
            crop_name: Name of the crop type
            temperature_range: Optimal temperature range (min, max) in °C
            humidity_range: Optimal humidity range (min, max) in %
            co2_range: Optimal CO2 range (min, max) in ppm
            ppfd_range: Optimal PPFD range (min, max) in μmol/m²/s
            ec_range: Optimal EC range (min, max) in μS/cm
            ph_range: Optimal pH range (min, max)
            water_temp_range: Optimal water temperature range (min, max) in °C
            
        Returns:
            Success flag
        """
        if crop_name in self.optimal_ranges:
            logger.warning(f"Crop type '{crop_name}' already exists. Use update_crop_type to modify.")
            return False
        
        # Add to optimal ranges
        self.optimal_ranges[crop_name] = {
            'Temperature': {'min': temperature_range[0], 'max': temperature_range[1], 'unit': '°C'},
            'Humidity': {'min': humidity_range[0], 'max': humidity_range[1], 'unit': '%'},
            'CO2': {'min': co2_range[0], 'max': co2_range[1], 'unit': 'ppm'},
            'PPFD': {'min': ppfd_range[0], 'max': ppfd_range[1], 'unit': 'μmol/m²/s'},
            'EC': {'min': ec_range[0], 'max': ec_range[1], 'unit': 'μS/cm'},
            'pH': {'min': ph_range[0], 'max': ph_range[1], 'unit': ''},
            'WaterTemp': {'min': water_temp_range[0], 'max': water_temp_range[1], 'unit': '°C'}
        }
        
        # Create a basic crop profile
        crop_id = crop_name.lower().replace(' ', '_')
        
        crop_profile = CropProfile(
            crop_id=crop_id,
            crop_name=crop_name,
            growth_duration=60,  # Default growth duration
            growth_stages={
                GrowthStage.SEEDLING: (0, 10),      # Days 0-10
                GrowthStage.VEGETATIVE: (11, 40),   # Days 11-40
                GrowthStage.FLOWERING: (41, 50),    # Days 41-50
                GrowthStage.HARVEST: (51, 60)       # Days 51-60
            },
            optimal_ranges={
                GrowthStage.SEEDLING: {
                    'Temperature': {'min': temperature_range[0], 'max': temperature_range[1], 'unit': '°C'},
                    'Humidity': {'min': humidity_range[0], 'max': humidity_range[1], 'unit': '%'},
                    'PPFD': {'min': ppfd_range[0] * 0.8, 'max': ppfd_range[1] * 0.8, 'unit': 'μmol/m²/s'},
                    'EC': {'min': ec_range[0] * 0.8, 'max': ec_range[1] * 0.8, 'unit': 'μS/cm'},
                    'pH': {'min': ph_range[0], 'max': ph_range[1], 'unit': ''}
                },
                GrowthStage.VEGETATIVE: {
                    'Temperature': {'min': temperature_range[0], 'max': temperature_range[1], 'unit': '°C'},
                    'Humidity': {'min': humidity_range[0], 'max': humidity_range[1], 'unit': '%'},
                    'PPFD': {'min': ppfd_range[0], 'max': ppfd_range[1], 'unit': 'μmol/m²/s'},
                    'EC': {'min': ec_range[0], 'max': ec_range[1], 'unit': 'μS/cm'},
                    'pH': {'min': ph_range[0], 'max': ph_range[1], 'unit': ''}
                },
                GrowthStage.FLOWERING: {
                    'Temperature': {'min': temperature_range[0], 'max': temperature_range[1], 'unit': '°C'},
                    'Humidity': {'min': humidity_range[0] * 0.9, 'max': humidity_range[1] * 0.9, 'unit': '%'},
                    'PPFD': {'min': ppfd_range[0] * 1.1, 'max': ppfd_range[1] * 1.1, 'unit': 'μmol/m²/s'},
                    'EC': {'min': ec_range[0] * 1.1, 'max': ec_range[1] * 1.1, 'unit': 'μS/cm'},
                    'pH': {'min': ph_range[0], 'max': ph_range[1], 'unit': ''}
                },
                GrowthStage.HARVEST: {
                    'Temperature': {'min': temperature_range[0], 'max': temperature_range[1], 'unit': '°C'},
                    'Humidity': {'min': humidity_range[0] * 0.8, 'max': humidity_range[1] * 0.8, 'unit': '%'},
                    'PPFD': {'min': ppfd_range[0], 'max': ppfd_range[1], 'unit': 'μmol/m²/s'},
                    'EC': {'min': ec_range[0], 'max': ec_range[1], 'unit': 'μS/cm'},
                    'pH': {'min': ph_range[0], 'max': ph_range[1], 'unit': ''}
                }
            }
        )
        
        # Generate ideal vectors for each growth stage
        for stage in crop_profile.growth_stages.keys():
            # Create vector from optimal parameter ranges
            stage_vector = self._create_vector_from_optimal_ranges(crop_profile.optimal_ranges[stage])
            crop_profile.ideal_vectors[stage] = stage_vector
        
        # Add to crop profiles
        self.crop_profiles[crop_name] = crop_profile
        
        logger.info(f"Added new crop type: {crop_name}")
        return True
    
    def update_crop_type(self, 
                       crop_name: str, 
                       **parameter_ranges) -> bool:
        """
        Update parameter ranges for an existing crop type.
        
        Args:
            crop_name: Name of the crop type
            **parameter_ranges: Keyword arguments for parameter ranges to update
                Example: temperature_range=(18, 24), humidity_range=(60, 80)
            
        Returns:
            Success flag
        """
        if crop_name not in self.optimal_ranges:
            logger.warning(f"Crop type '{crop_name}' not found. Use add_crop_type to create it.")
            return False
        
        # Map parameter names to optimal_ranges keys
        param_map = {
            'temperature_range': 'Temperature',
            'humidity_range': 'Humidity',
            'co2_range': 'CO2',
            'ppfd_range': 'PPFD',
            'ec_range': 'EC',
            'ph_range': 'pH',
            'water_temp_range': 'WaterTemp'
        }
        
        # Update parameters
        for param_name, range_value in parameter_ranges.items():
            if param_name in param_map and isinstance(range_value, tuple) and len(range_value) == 2:
                param_key = param_map[param_name]
                self.optimal_ranges[crop_name][param_key]['min'] = range_value[0]
                self.optimal_ranges[crop_name][param_key]['max'] = range_value[1]
        
        # Update crop profile if it exists
        if crop_name in self.crop_profiles:
            # This is a simplified update - a full implementation would update
            # all growth stages and regenerate vectors
            for stage in self.crop_profiles[crop_name].growth_stages.keys():
                for param_name, range_value in parameter_ranges.items():
                    if param_name in param_map and isinstance(range_value, tuple) and len(range_value) == 2:
                        param_key = param_map[param_name]
                        
                        # Different modifications based on growth stage
                        if stage == GrowthStage.SEEDLING:
                            if param_key in ['PPFD', 'EC']:
                                # Seedlings need lower light and nutrients
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['min'] = range_value[0] * 0.8
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['max'] = range_value[1] * 0.8
                            else:
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['min'] = range_value[0]
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['max'] = range_value[1]
                        
                        elif stage == GrowthStage.FLOWERING:
                            if param_key == 'Humidity':
                                # Flowering stage typically needs lower humidity
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['min'] = range_value[0] * 0.9
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['max'] = range_value[1] * 0.9
                            elif param_key in ['PPFD', 'EC']:
                                # Flowering stage typically needs more light and nutrients
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['min'] = range_value[0] * 1.1
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['max'] = range_value[1] * 1.1
                            else:
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['min'] = range_value[0]
                                self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['max'] = range_value[1]
                        
                        else:
                            # VEGETATIVE and HARVEST stages use the base values
                            self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['min'] = range_value[0]
                            self.crop_profiles[crop_name].optimal_ranges[stage][param_key]['max'] = range_value[1]
                
                # Regenerate vector for this stage
                self.crop_profiles[crop_name].ideal_vectors[stage] = self._create_vector_from_optimal_ranges(
                    self.crop_profiles[crop_name].optimal_ranges[stage]
                )
        
        logger.info(f"Updated crop type: {crop_name}")
        return True
    
    def get_supported_crop_types(self) -> List[str]:
        """Get the list of supported crop types."""
        return list(self.optimal_ranges.keys())
    
    def _initialize_crop_profiles(self) -> None:
        """Initialize detailed crop profiles with growth stages."""
        self.crop_profiles = {}
        
        # Lettuce profile
        lettuce_profile = CropProfile(
            crop_id="lettuce_standard",
            crop_name="Lettuce",
            growth_duration=42,  # 6 weeks from seedling to harvest
            growth_stages={
                GrowthStage.SEEDLING: (0, 7),      # Days 0-7
                GrowthStage.VEGETATIVE: (8, 35),   # Days 8-35
                GrowthStage.HARVEST: (36, 42)      # Days 36-42
            },
            optimal_ranges={
                GrowthStage.SEEDLING: {
                    'Temperature': {'min': 18, 'max': 22, 'unit': '°C'},
                    'Humidity': {'min': 60, 'max': 80, 'unit': '%'},
                    'PPFD': {'min': 150, 'max': 250, 'unit': 'μmol/m²/s'},
                    'EC': {'min': 800, 'max': 1000, 'unit': 'μS/cm'},
                    'pH': {'min': 5.8, 'max': 6.2, 'unit': ''}
                },
                GrowthStage.VEGETATIVE: {
                    'Temperature': {'min': 17, 'max': 24, 'unit': '°C'},
                    'Humidity': {'min': 50, 'max': 70, 'unit': '%'},
                    'PPFD': {'min': 200, 'max': 400, 'unit': 'μmol/m²/s'},
                    'EC': {'min': 1000, 'max': 1400, 'unit': 'μS/cm'},
                    'pH': {'min': 5.8, 'max': 6.2, 'unit': ''}
                },
                GrowthStage.HARVEST: {
                    'Temperature': {'min': 16, 'max': 22, 'unit': '°C'},
                    'Humidity': {'min': 45, 'max': 65, 'unit': '%'},
                    'PPFD': {'min': 200, 'max': 350, 'unit': 'μmol/m²/s'},
                    'EC': {'min': 1100, 'max': 1300, 'unit': 'μS/cm'},
                    'pH': {'min': 5.8, 'max': 6.2, 'unit': ''}
                }
            },
            planting_density=24,  # plants per square meter
            expected_yield=2.5    # kg per square meter
        )
        
        # Generate ideal vectors for each growth stage
        for stage in lettuce_profile.growth_stages.keys():
            # Create vector from optimal parameter ranges
            stage_vector = self._create_vector_from_optimal_ranges(lettuce_profile.optimal_ranges[stage])
            lettuce_profile.ideal_vectors[stage] = stage_vector
            
        self.crop_profiles["Lettuce"] = lettuce_profile
        
        # Add other crop profiles similarly
        # This is simplified - in a full implementation, would add profiles for all supported crops
    
    def _create_vector_from_optimal_ranges(self, 
                                        optimal_ranges: Dict[str, Dict[str, float]]) -> np.ndarray:
        """Create a normalized vector representation from optimal parameter ranges."""
        # Initialize vector with zeros
        vector = np.zeros(self.dimension)
        
        # Extract key parameters and their midpoints in optimal range
        parameters = ['Temperature', 'Humidity', 'PPFD', 'EC', 'pH']
        values = []
        
        for i, param in enumerate(parameters):
            if param in optimal_ranges:
                # Use midpoint of optimal range
                min_val = optimal_ranges[param].get('min', 0)
                max_val = optimal_ranges[param].get('max', 0)
                mid_val = (min_val + max_val) / 2
                values.append(mid_val)
                
                # Map to vector positions based on parameter
                if i < self.dimension // 5:
                    vector[i] = mid_val
        
        # Use PCA-inspired encoding for remaining dimensions
        if values:
            for i in range(len(values), self.dimension):
                # Create synthetic combinations
                combo_idx = i % len(values)
                next_idx = (i + 1) % len(values)
                vector[i] = values[combo_idx] * 0.8 + values[next_idx] * 0.2
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def detect_harmony_states(self) -> List[HarmonyState]:
        """
        Detect harmony states across all parameters.
        
        Returns:
            List of detected harmony states
        """
        detected_states = []
        
        # Can't detect harmony states without data
        if self.data is None or self.current_state is None:
            return detected_states
        
        # Check for OPTIMAL_GROWTH state
        optimal_params_count = 0
        total_param_count = 0
        
        for param, range_values in self.optimal_ranges.get(self.crop_type, {}).items():
            if hasattr(self.current_state, param.lower()):
                total_param_count += 1
                value = getattr(self.current_state, param.lower())
                
                if value is not None and range_values['min'] <= value <= range_values['max']:
                    optimal_params_count += 1
        
        # If 80% of parameters are in optimal range
        if total_param_count > 0 and optimal_params_count / total_param_count >= 0.8:
            detected_states.append(HarmonyState.OPTIMAL_GROWTH)
        
        # Check for CIRCADIAN_ALIGNED state - perfect day/night cycle
        if 'day_night' in self.analysis_results:
            day_night = self.analysis_results['day_night']
            
            # Calculate metrics for determining alignment
            alignment_score = 0.0
            checks_passed = 0
            total_checks = 0
            
            # Check day/night temperature differential
            if 'Temperature' in day_night['differential']:
                total_checks += 1
                temp_diff = day_night['differential']['Temperature']['absolute_diff']
                # Ideal temperature drop at night is 3-5°C for most plants
                if 3 <= temp_diff <= 5:
                    checks_passed += 1
                    
            # Check day/night humidity balance
            if 'Humidity' in day_night['differential']:
                total_checks += 1
                humidity_diff = day_night['differential']['Humidity']['absolute_diff']
                # Humidity should be slightly higher at night (5-15%)
                if -15 <= humidity_diff <= -5:
                    checks_passed += 1
                    
            # Check if light hours are appropriate for the crop
            if self.crop_type == 'Lettuce' and 'light_hours' in day_night.get('patterns', {}):
                total_checks += 1
                light_hours = len(day_night['patterns'].get('light_hours', []))
                # Lettuce typically wants 14-16 hours of light
                if 14 <= light_hours <= 16:
                    checks_passed += 1
            
            # If 75% of circadian checks are good
            if total_checks > 0 and checks_passed / total_checks >= 0.75:
                detected_states.append(HarmonyState.CIRCADIAN_ALIGNED)
        
        # Check for ENERGY_EFFICIENT state
        if ('PPFD' in self.data.columns and 'CO2' in self.data.columns and 
            'Temperature' in self.data.columns):
            
            # Calculate efficiency metrics
            co2_utilization = 0.0
            light_efficiency = 0.0
            
            # Check CO2 and PPFD correlation during light hours
            light_data = self.data[self.data['LightStatus'] == 'On']
            if len(light_data) > 10:
                co2_ppfd_corr = light_data['CO2'].corr(light_data['PPFD'])
                
                # Strong positive correlation indicates good CO2 utilization
                if co2_ppfd_corr > 0.7:
                    co2_utilization = co2_ppfd_corr
                
                # Calculate light efficiency (PPFD vs Energy consumption)
                # In a real implementation, would need actual energy data
                # Here we'll use a placeholder calculation
                avg_ppfd = light_data['PPFD'].mean()
                if avg_ppfd > 0:
                    if 'Temperature' in light_data.columns:
                        # Higher temps with good PPFD can mean energy inefficiency
                        avg_temp = light_data['Temperature'].mean()
                        temp_efficiency = 1.0 - (max(0, avg_temp - 24) / 10)
                        light_efficiency = 0.8 * temp_efficiency
                    else:
                        light_efficiency = 0.7  # Default
            
            # If both metrics are good
            if co2_utilization > 0.7 and light_efficiency > 0.8:
                detected_states.append(HarmonyState.ENERGY_EFFICIENT)
        
        # Check for STRESS_BALANCED state - recovery from stress
        if 'forecasts' in self.analysis_results:
            forecasts = self.analysis_results['forecasts']
            
            stress_factors = 0
            improving_factors = 0
            
            # Check for stress indicators
            for param in ['Temperature', 'Humidity', 'CO2', 'EC', 'pH']:
                if param in forecasts:
                    # Get optimal range
                    optimal_min = self.optimal_ranges.get(self.crop_type, {}).get(param, {}).get('min', 0)
                    optimal_max = self.optimal_ranges.get(self.crop_type, {}).get(param, {}).get('max', 1000)
                    
                    current_value = forecasts[param].get('current_value')
                    forecast_value = forecasts[param].get('forecast_value')
                    
                    if current_value is not None and forecast_value is not None:
                        # Check if currently outside optimal range
                        if current_value < optimal_min or current_value > optimal_max:
                            stress_factors += 1
                            
                            # Check if forecast shows improvement toward optimal range
                            if ((current_value < optimal_min and forecast_value > current_value) or
                                (current_value > optimal_max and forecast_value < current_value)):
                                improving_factors += 1
            
            # If multiple stress factors are improving simultaneously
            if stress_factors >= 2 and improving_factors >= 2:
                detected_states.append(HarmonyState.STRESS_BALANCED)
        
        # Check for TRANSITION_POINT state
        # This would typically involve detecting when plants are transitioning
        # between growth phases, which would need more specialized plant monitoring
        # We'll use a simplified placeholder implementation
        if 'patterns' in self.analysis_results:
            patterns = self.analysis_results['patterns']
            
            # Check for pattern shifts in key parameters
            if 'daily_patterns' in patterns:
                daily_patterns = patterns['daily_patterns']
                
                pattern_shifts = 0
                for param, param_data in daily_patterns.items():
                    if 'peaks' in param_data and len(param_data['peaks']) == 1:
                        # Single peak patterns often indicate transition points
                        pattern_shifts += 1
                
                if pattern_shifts >= 2:
                    detected_states.append(HarmonyState.TRANSITION_POINT)
        
        return detected_states
    
    def register_harmony_trigger(self, 
                               harmony_state: HarmonyState,
                               actions: List[str],
                               notification_message: str = "",
                               cooldown_period: float = 3600) -> str:
        """
        Register a new trigger for a harmony state.
        
        Args:
            harmony_state: Harmony state to trigger on
            actions: List of actions to perform
            notification_message: Message to include with trigger
            cooldown_period: Seconds before trigger can fire again
            
        Returns:
            Trigger ID
        """
        trigger_id = f"harmony_trigger_{uuid.uuid4().hex[:8]}"
        
        # Create trigger
        trigger = HarmonyTrigger(
            trigger_id=trigger_id,
            harmony_state=harmony_state,
            actions=actions,
            cooldown_period=cooldown_period,
            notification_message=notification_message
        )
        
        # Store trigger
        self.harmony_triggers[trigger_id] = trigger
        
        logger.info(f"Registered harmony trigger {trigger_id} for {harmony_state.name}")
        
        return trigger_id
    
    def create_default_harmony_triggers(self) -> None:
        """Create default harmony triggers for common scenarios."""
        # OPTIMAL_GROWTH - Turn on data logging for research
        self.register_harmony_trigger(
            harmony_state=HarmonyState.OPTIMAL_GROWTH,
            actions=[
                "log_state",  # Log the optimal state for reference
                "notify_optimal"  # Send notification about optimal conditions
            ],
            notification_message="All parameters are in optimal ranges - perfect growing conditions!",
            cooldown_period=86400  # Once per day at most
        )
        
        # CIRCADIAN_ALIGNED - Reduce monitoring frequency to save energy
        self.register_harmony_trigger(
            harmony_state=HarmonyState.CIRCADIAN_ALIGNED,
            actions=[
                "reduce_monitoring",  # Reduce monitoring frequency
                "log_pattern"  # Log the pattern for future reference
            ],
            notification_message="Perfect day/night cycle established - reducing monitoring frequency.",
            cooldown_period=43200  # Twice per day at most
        )
        
        # ENERGY_EFFICIENT - Document the efficient settings
        self.register_harmony_trigger(
            harmony_state=HarmonyState.ENERGY_EFFICIENT,
            actions=[
                "capture_settings",  # Record current settings as reference
                "notify_efficiency"  # Alert about efficiency achievement
            ],
            notification_message="Energy efficient balance achieved - recording settings.",
            cooldown_period=86400  # Once per day at most
        )
        
        # STRESS_BALANCED - Document recovery pattern
        self.register_harmony_trigger(
            harmony_state=HarmonyState.STRESS_BALANCED,
            actions=[
                "log_recovery",  # Log the recovery pattern
                "increase_monitoring"  # Temporarily increase monitoring frequency
            ],
            notification_message="System recovering from stress factors - monitoring recovery.",
            cooldown_period=21600  # Four times per day at most
        )
        
        logger.info("Created default harmony triggers")
    
    def check_harmony_triggers(self) -> List[Dict[str, Any]]:
        """
        Check all harmony triggers against current state.
        
        Returns:
            List of triggered actions
        """
        # Get current harmony states
        current_harmony_states = self.detect_harmony_states()
        
        if not current_harmony_states:
            return []
        
        triggered_actions = []
        current_time = time.time()
        
        # Check each trigger
        for trigger_id, trigger in self.harmony_triggers.items():
            # Skip if on cooldown
            if (trigger.last_triggered is not None and 
                current_time - trigger.last_triggered < trigger.cooldown_period):
                continue
            
            # Check if trigger state is active
            if trigger.harmony_state in current_harmony_states:
                # Mark as triggered
                trigger.last_triggered = current_time
                
                # Log trigger
                logger.info(f"Harmony trigger {trigger_id} activated: {trigger.harmony_state.name}")
                
                # Process each action
                for action in trigger.actions:
                    # Execute action
                    action_result = self._execute_harmony_action(action, trigger)
                    
                    # Record triggered action
                    triggered_actions.append({
                        'trigger_id': trigger_id,
                        'harmony_state': trigger.harmony_state.name,
                        'action': action,
                        'timestamp': current_time,
                        'result': action_result
                    })
        
        return triggered_actions
    
    def _execute_harmony_action(self, action: str, trigger: HarmonyTrigger) -> Dict[str, Any]:
        """
        Execute a triggered harmony action.
        
        Args:
            action: Action to execute
            trigger: Trigger that activated this action
            
        Returns:
            Action result
        """
        result = {
            'action': action,
            'success': False,
            'message': ''
        }
        
        try:
            if action == "log_state":
                # Log the current state
                if self.current_state:
                    state_dict = self.current_state.to_dict()
                    
                    # Add to farm data store
                    log_id = f"harmony_state_{int(time.time())}"
                    log_path = f"./farm_data/{self.farm_id}/harmony_states/{log_id}.json"
                    
                    os.makedirs(os.path.dirname(log_path), exist_ok=True)
                    
                    with open(log_path, 'w') as f:
                        json.dump({
                            'harmony_state': trigger.harmony_state.name,
                            'timestamp': time.time(),
                            'farm_state': state_dict,
                            'trigger_id': trigger.trigger_id
                        }, f, indent=2)
                    
                    result['success'] = True
                    result['message'] = f"State logged to {log_path}"
                else:
                    result['message'] = "No current state to log"
            
            elif action == "notify_optimal":
                # Send notification about optimal conditions
                notification = f"HARMONY ALERT: {trigger.notification_message}"
                
                # In a real implementation, this would send an actual notification
                # via email, SMS, push notification, etc.
                logger.info(f"NOTIFICATION: {notification}")
                
                result['success'] = True
                result['message'] = f"Notification sent: {notification}"
            
            elif action == "reduce_monitoring":
                # Reduce monitoring frequency to save energy
                if self.monitoring_active:
                    # In a real implementation, this would adjust monitoring intervals
                    logger.info("Reducing monitoring frequency due to harmony state")
                    
                    result['success'] = True
                    result['message'] = "Monitoring frequency reduced"
                else:
                    result['message'] = "Monitoring not active"
            
            elif action == "increase_monitoring":
                # Increase monitoring frequency
                if self.monitoring_active:
                    # In a real implementation, this would adjust monitoring intervals
                    logger.info("Increasing monitoring frequency due to harmony state")
                    
                    result['success'] = True
                    result['message'] = "Monitoring frequency increased"
                else:
                    result['message'] = "Monitoring not active"
            
            elif action == "log_pattern":
                # Log the current pattern
                if 'patterns' in self.analysis_results:
                    pattern_data = self.analysis_results['patterns']
                    
                    # Add to farm data store
                    log_id = f"harmony_pattern_{int(time.time())}"
                    log_path = f"./farm_data/{self.farm_id}/harmony_patterns/{log_id}.json"
                    
                    os.makedirs(os.path.dirname(log_path), exist_ok=True)
                    
                    with open(log_path, 'w') as f:
                        json.dump({
                            'harmony_state': trigger.harmony_state.name,
                            'timestamp': time.time(),
                            'patterns': pattern_data,
                            'trigger_id': trigger.trigger_id
                        }, f, indent=2)
                    
                    result['success'] = True
                    result['message'] = f"Pattern logged to {log_path}"
                else:
                    result['message'] = "No pattern data available"
            
            elif action == "capture_settings":
                # Document current settings
                if self.current_state:
                    settings_dict = self.current_state.to_dict()
                    
                    # In a real implementation, this would also capture
                    # automation settings, light schedules, etc.
                    
                    # Add to farm data store
                    log_id = f"harmony_settings_{int(time.time())}"
                    log_path = f"./farm_data/{self.farm_id}/harmony_settings/{log_id}.json"
                    
                    os.makedirs(os.path.dirname(log_path), exist_ok=True)
                    
                    with open(log_path, 'w') as f:
                        json.dump({
                            'harmony_state': trigger.harmony_state.name,
                            'timestamp': time.time(),
                            'settings': settings_dict,
                            'trigger_id': trigger.trigger_id
                        }, f, indent=2)
                    
                    result['success'] = True
                    result['message'] = f"Settings captured to {log_path}"
                else:
                    result['message'] = "No current settings to capture"
            
            elif action == "log_recovery":
                # Document recovery pattern
                if 'forecasts' in self.analysis_results:
                    forecast_data = self.analysis_results['forecasts']
                    
                    # Add to farm data store
                    log_id = f"harmony_recovery_{int(time.time())}"
                    log_path = f"./farm_data/{self.farm_id}/harmony_recovery/{log_id}.json"
                    
                    os.makedirs(os.path.dirname(log_path), exist_ok=True)
                    
                    with open(log_path, 'w') as f:
                        json.dump({
                            'harmony_state': trigger.harmony_state.name,
                            'timestamp': time.time(),
                            'forecasts': forecast_data,
                            'trigger_id': trigger.trigger_id
                        }, f, indent=2)
                    
                    result['success'] = True
                    result['message'] = f"Recovery pattern logged to {log_path}"
                else:
                    result['message'] = "No forecast data available"
            
            elif action == "notify_efficiency":
                # Send notification about efficiency
                notification = f"HARMONY ALERT: {trigger.notification_message}"
                
                # In a real implementation, this would send an actual notification
                logger.info(f"NOTIFICATION: {notification}")
                
                result['success'] = True
                result['message'] = f"Notification sent: {notification}"
            
            else:
                result['message'] = f"Unknown action: {action}"
        
        except Exception as e:
            result['message'] = f"Error executing action: {str(e)}"
        
        return result
    
    def load_csv(self, filepath: str) -> bool:
        """
        Load and process a CSV file from farmhand.ag export.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            Success flag
        """
        try:
            logger.info(f"Loading CSV file: {filepath}")
            
            # Read CSV file
            self.data = pd.read_csv(filepath)
            
            # Convert timestamp to datetime
            if 'Timestamp' in self.data.columns:
                self.data['Timestamp'] = pd.to_datetime(self.data['Timestamp'])
            
            logger.info(f"Successfully loaded {len(self.data)} records from {filepath}")
            
            # Store in farm data store
            self.farm_data_store.store_dataframe(self.data, source="csv_import")
            
            # Update current state
            self._update_current_state_from_dataframe()
            
            # Run analysis
            self.analyze_data()
            
            # Check for harmony states
            self.check_harmony_triggers()
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading CSV file: {str(e)}")
            return False
    
    def _update_current_state_from_dataframe(self) -> None:
        """Update the current state based on the most recent data in the DataFrame."""
        if self.data is None or len(self.data) == 0:
            return
            
        # Sort by timestamp if available
        if 'Timestamp' in self.data.columns:
            latest_data = self.data.sort_values('Timestamp', ascending=False).iloc[0]
            timestamp = latest_data['Timestamp']
        else:
            latest_data = self.data.iloc[-1]
            timestamp = datetime.now()
            
        # Create farm state from the latest data
        current_state = FarmState(
            farm_id=self.farm_id,
            timestamp=timestamp
        )
        
        # Map dataframe columns to state properties
        mapping = {
            'Temperature': 'temperature',
            'Humidity': 'humidity',
            'CO2': 'co2',
            'PPFD': 'ppfd',
            'EC': 'ec',
            'pH': 'ph',
            'WaterTemp': 'water_temp',
            'WaterLevel': 'water_level',
            'NutrientA': 'nutrient_a',
            'NutrientB': 'nutrient_b',
            'FanSpeed': 'fan_speed',
            'LightStatus': 'light_status',
            'PumpStatus': 'pump_status'
        }
        
        # Update state properties from dataframe
        for df_col, state_prop in mapping.items():
            if df_col in latest_data and not pd.isna(latest_data[df_col]):
                setattr(current_state, state_prop, latest_data[df_col])
        
        # Create state vector
        state_vector = self._create_state_vector(current_state)
        current_state.state_vector = state_vector
        
        # Update current state
        self.current_state = current_state
        self.last_update = datetime.now()
    
    def _create_state_vector(self, state: FarmState) -> np.ndarray:
        """Create a normalized vector representation of the farm state."""
        # Initialize vector with zeros
        vector = np.zeros(self.dimension)
        
        # Map state properties to vector
        properties = [
            (state.temperature, 0, 40),      # Temperature range: 0-40°C
            (state.humidity, 0, 100),        # Humidity range: 0-100%
            (state.co2, 0, 2000),            # CO2 range: 0-2000ppm
            (state.ppfd, 0, 1000),           # PPFD range: 0-1000 μmol/m²/s
            (state.ec, 0, 3000),             # EC range: 0-3000 μS/cm
            (state.ph, 0, 14),               # pH range: 0-14
            (state.water_temp, 0, 40),       # Water temp range: 0-40°C
            (state.water_level, 0, 100)      # Water level range: 0-100%
        ]
        
        # Fill vector with normalized values
        for i, (value, min_val, max_val) in enumerate(properties):
            if value is not None and i < self.dimension:
                # Normalize to 0-1 range
                normalized = (value - min_val) / (max_val - min_val)
                normalized = max(0, min(1, normalized))  # Clamp to 0-1
                vector[i] = normalized
        
        # Add binary flags for system states
        if state.light_status == 'On' and self.dimension > 8:
            vector[8] = 1.0
        if state.pump_status == 'On' and self.dimension > 9:
            vector[9] = 1.0
            
        # Create synthetic combinations for remaining dimensions
        for i in range(10, self.dimension):
            idx1 = (i % 8)
            idx2 = ((i + 3) % 8)
            if properties[idx1][0] is not None and properties[idx2][0] is not None:
                vector[i] = (vector[idx1] * 0.7 + vector[idx2] * 0.3)
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def analyze_data(self) -> Dict[str, Any]:
        """
        Analyze the loaded farm data to extract insights.
        
        Returns:
            Analysis results
        """
        if self.data is None:
            logger.warning("No data available for analysis")
            return {}
            
        logger.info("Analyzing farm data...")
        
        # Environmental analysis
        self.analysis_results['environmental'] = self._analyze_environmental_data()
        
        # Day/night cycle analysis
        if 'LightStatus' in self.data.columns:
            self.analysis_results['day_night'] = self._analyze_day_night_cycles()
        
        # Optimal range check
        self.analysis_results['optimal_check'] = self._check_optimal_ranges()
        
        # Pattern analysis
        self.analysis_results['patterns'] = self._analyze_patterns()
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Pattern recognition
        if hasattr(self, 'pattern_engine'):
            pattern_results = self.pattern_engine.process_dataframe(self.data)
            self.analysis_results['pattern_recognition'] = pattern_results
        
        # Generate forecasts
        if hasattr(self, 'forecast_engine'):
            forecast_results = self.forecast_engine.generate_forecasts(self.data)
            self.analysis_results['forecasts'] = forecast_results
        
        logger.info("Analysis complete")
        
        return self.analysis_results
    
    def _analyze_environmental_data(self) -> Dict[str, Dict[str, Any]]:
        """Analyze environmental metrics."""
        metrics = {}
        
        # Define numeric fields to analyze
        numeric_fields = [
            'Temperature', 'Humidity', 'CO2', 'PPFD', 'EC', 
            'pH', 'WaterTemp', 'WaterLevel', 'NutrientA', 'NutrientB', 'FanSpeed'
        ]
        
        # Filter to include only columns that exist in the data
        numeric_fields = [field for field in numeric_fields if field in self.data.columns]
        
        for field in numeric_fields:
            # Skip fields with all NaN values
            if self.data[field].isna().all():
                continue
                
            values = self.data[field].dropna()
            
            if len(values) > 0:
                # Basic statistics
                min_val = values.min()
                max_val = values.max()
                avg_val = values.mean()
                std_val = values.std()
                
                # Detect trends using simple linear regression
                if 'Timestamp' in self.data.columns:
                    # Prepare timestamp data
                    timestamps = self.data['Timestamp'].dropna()
                    if len(timestamps) == len(values):
                        # Convert to seconds since first timestamp
                        t0 = timestamps.min()
                        t_seconds = [(t - t0).total_seconds() for t in timestamps]
                        
                        # Linear regression
                        if len(t_seconds) > 1:
                            slope, intercept = np.polyfit(t_seconds, values, 1)
                            
                            # Calculate R^2
                            y_pred = np.array(t_seconds) * slope + intercept
                            ss_tot = np.sum((values - values.mean())**2)
                            ss_res = np.sum((values - y_pred)**2)
                            r2 = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
                            
                            # Determine trend
                            if abs(slope) < 1e-5 or r2 < 0.1:
                                trend = "stable"
                            elif slope > 0:
                                trend = "increasing"
                            else:
                                trend = "decreasing"
                                
                            trend_data = {
                                "slope": slope,
                                "intercept": intercept,
                                "r2": r2,
                                "direction": trend
                            }
                        else:
                            trend_data = None
                    else:
                        trend_data = None
                else:
                    trend_data = None
                
                metrics[field] = {
                    'min': min_val,
                    'max': max_val,
                    'avg': avg_val,
                    'std': std_val,
                    'unit': self.field_units.get(field, {}).get('unit', ''),
                    'trend': trend_data
                }
        
        return metrics
    
    def _analyze_day_night_cycles(self) -> Dict[str, Dict[str, Any]]:
        """Analyze day/night cycle differences."""
        # Filter day and night records
        day_records = self.data[self.data['LightStatus'] == 'On']
        night_records = self.data[self.data['LightStatus'] == 'Off']
        
        # Analyze each set separately
        day_metrics = self._analyze_subset(day_records)
        night_metrics = self._analyze_subset(night_records)
        
        # Calculate day/night differential
        differential = {}
        for field in day_metrics:
            if field in night_metrics:
                day_avg = day_metrics[field].get('avg', 0)
                night_avg = night_metrics[field].get('avg', 0)
                
                # Calculate relative difference
                if night_avg != 0:
                    rel_diff = (day_avg - night_avg) / night_avg
                else:
                    rel_diff = 0 if day_avg == 0 else 1
                    
                differential[field] = {
                    'day_avg': day_avg,
                    'night_avg': night_avg,
                    'absolute_diff': day_avg - night_avg,
                    'relative_diff': rel_diff,
                    'unit': day_metrics[field].get('unit', '')
                }
        
        # Extract light hours pattern if timestamp available
        light_hours_pattern = []
        if 'Timestamp' in self.data.columns and len(day_records) > 0:
            # Group by hour of day 
            if 'Hour' not in day_records.columns:
                day_records['Hour'] = day_records['Timestamp'].dt.hour
            
            # Count records per hour to determine light hours
            light_counts = day_records.groupby('Hour').size()
            total_counts = self.data.groupby(self.data['Timestamp'].dt.hour).size()
            
            # Calculate percentage of time lights are on for each hour
            light_pct = light_counts / total_counts
            
            # Hours with lights on most of the time (>70%)
            light_hours = light_pct[light_pct > 0.7].index.tolist()
            light_hours_pattern = sorted(light_hours)
        
        return {
            'day': {
                'record_count': len(day_records),
                'metrics': day_metrics
            },
            'night': {
                'record_count': len(night_records),
                'metrics': night_metrics
            },
            'differential': differential,
            'patterns': {
                'light_hours': light_hours_pattern
            }
        }
    
    def _analyze_subset(self, subset: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
        """Analyze a subset of data."""
        metrics = {}
        
        # Define numeric fields to analyze
        numeric_fields = [
            'Temperature', 'Humidity', 'CO2', 'PPFD', 'EC', 
            'pH', 'WaterTemp', 'WaterLevel', 'NutrientA', 'NutrientB', 'FanSpeed'
        ]
        
        # Filter to include only columns that exist in the data
        numeric_fields = [field for field in numeric_fields if field in subset.columns]
        
        for field in numeric_fields:
            # Skip fields with all NaN values
            if subset[field].isna().all():
                continue
                
            values = subset[field].dropna()
            
            if len(values) > 0:
                min_val = values.min()
                max_val = values.max()
                avg_val = values.mean()
                std_val = values.std()
                
                metrics[field] = {
                    'min': min_val,
                    'max': max_val,
                    'avg': avg_val,
                    'std': std_val,
                    'unit': self.field_units.get(field, {}).get('unit', '')
                }
        
        return metrics
    
    def _check_optimal_ranges(self) -> Dict[str, Any]:
        """Check if parameters are within optimal ranges."""
        # Get optimal ranges for the current crop
        if self.crop_type not in self.optimal_ranges:
            logger.warning(f"No optimal ranges defined for crop type: {self.crop_type}")
            return {
                'crop_type': self.crop_type,
                'parameters': {}
            }
            
        optimal_range = self.optimal_ranges[self.crop_type]
        results = {}
        
        # Check each parameter against optimal ranges
        for param, range_values in optimal_range.items():
            if param in self.data.columns and not self.data[param].isna().all():
                values = self.data[param].dropna()
                avg = values.mean()
                std = values.std()
                
                # Calculate percentage of time within optimal range
                in_range_count = sum((values >= range_values['min']) & (values <= range_values['max']))
                pct_in_range = in_range_count / len(values) * 100 if len(values) > 0 else 0
                
                # Calculate percentage of time below/above range
                below_count = sum(values < range_values['min'])
                above_count = sum(values > range_values['max'])
                pct_below = below_count / len(values) * 100 if len(values) > 0 else 0
                pct_above = above_count / len(values) * 100 if len(values) > 0 else 0
                
                # Determine status
                status = 'optimal'
                if avg < range_values['min']:
                    status = 'below'
                elif avg > range_values['max']:
                    status = 'above'
                
                results[param] = {
                    'average': avg,
                    'std_dev': std,
                    'optimal_min': range_values['min'],
                    'optimal_max': range_values['max'],
                    'pct_in_range': pct_in_range,
                    'pct_below': pct_below,
                    'pct_above': pct_above,
                    'status': status,
                    'unit': range_values['unit']
                }
        
        return {
            'crop_type': self.crop_type,
            'parameters': results
        }
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Analyze patterns in the data."""
        if self.data is None or len(self.data) < 24:  # Need at least 24 hours of data
            return {}
            
        patterns = {}
        
        # Detect daily patterns if timestamp available
        if 'Timestamp' in self.data.columns:
            # Extract hour of day
            self.data['Hour'] = self.data['Timestamp'].dt.hour
            
            # Analyze key parameters by hour
            for param in ['Temperature', 'Humidity', 'CO2', 'PPFD']:
                if param in self.data.columns:
                    hourly_avg = self.data.groupby('Hour')[param].mean()
                    
                    # Find peaks and troughs
                    if len(hourly_avg) == 24:
                        hourly_values = hourly_avg.values
                        peaks, _ = find_peaks(hourly_values, distance=4)
                        troughs, _ = find_peaks(-hourly_values, distance=4)
                        
                        patterns[param] = {
                            'hourly_avg': hourly_avg.to_dict(),
                            'peaks': [(int(hour), float(hourly_values[hour])) for hour in peaks],
                            'troughs': [(int(hour), float(hourly_values[hour])) for hour in troughs]
                        }
        
        # Analyze parameter correlations
        correlations = {}
        numeric_fields = [
            'Temperature', 'Humidity', 'CO2', 'PPFD', 'EC', 
            'pH', 'WaterTemp', 'WaterLevel', 'NutrientA', 'NutrientB', 'FanSpeed'
        ]
        
        # Filter to include only columns that exist in the data
        numeric_fields = [field for field in numeric_fields if field in self.data.columns]
        
        if len(numeric_fields) > 1:
            # Calculate correlation matrix
            corr_matrix = self.data[numeric_fields].corr()
            
            # Find strong correlations
            for i, param1 in enumerate(numeric_fields):
                for j, param2 in enumerate(numeric_fields):
                    if i < j:  # Only look at upper triangle
                        corr_value = corr_matrix.loc[param1, param2]
                        if abs(corr_value) > 0.5:  # Only strong correlations
                            correlations[f"{param1}_{param2}"] = {
                                'correlation': corr_value,
                                'strength': 'strong' if abs(corr_value) > 0.7 else 'moderate'
                            }
        
        return {
            'daily_patterns': patterns,
            'correlations': correlations
        }
    
    def _generate_recommendations(self) -> None:
        """Generate recommendations based on the analysis."""
        self.recommendations = []
        
        # Check if optimal check results exist
        if 'optimal_check' not in self.analysis_results:
            return
            
        optimal_check = self.analysis_results['optimal_check']
        
        # Check each parameter
        for param, check in optimal_check.get('parameters', {}).items():
            param_display = self.field_units.get(param, {}).get('display', param)
            
            if check['status'] == 'below':
                if param == 'Temperature':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'high' if (check['optimal_min'] - check['average']) > 3 else 'medium',
                        'action': f"Increase temperature: Current avg is {check['average']:.1f}{check['unit']}, which is below optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': f"Consider increasing the temperature by {(check['optimal_min'] - check['average']):.1f}{check['unit']} to reach optimal range."
                    })
                elif param == 'Humidity':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'medium',
                        'action': f"Increase humidity: Current avg is {check['average']:.1f}{check['unit']}, which is below optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Reduce ventilation, use a humidifier, or mist plants to increase humidity."
                    })
                elif param == 'CO2':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'high',
                        'action': f"Increase CO2 levels: Current avg is {check['average']:.1f}{check['unit']}, which is below optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Check CO2 injection system or add supplemental CO2 during light hours."
                    })
                elif param == 'PPFD':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'high',
                        'action': f"Increase light intensity: Current avg is {check['average']:.1f}{check['unit']}, which is below optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Increase light intensity or duration, or check for light obstructions."
                    })
                elif param == 'EC':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'high',
                        'action': f"Increase nutrient concentration: Current avg is {check['average']:.1f}{check['unit']}, which is below optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Add more nutrients or verify dosing system is functioning correctly."
                    })
                elif param == 'pH':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'high',
                        'action': f"Increase pH: Current avg is {check['average']:.2f}, which is below optimal range ({check['optimal_min']}-{check['optimal_max']}).",
                        'details': "Add pH up solution and verify pH monitoring system is calibrated correctly."
                    })
                elif param == 'WaterTemp':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'medium',
                        'action': f"Increase water temperature: Current avg is {check['average']:.1f}{check['unit']}, which is below optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Check water heater setting or insulate reservoir to maintain higher temperature."
                    })
            
            elif check['status'] == 'above':
                if param == 'Temperature':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'high' if (check['average'] - check['optimal_max']) > 3 else 'medium',
                        'action': f"Decrease temperature: Current avg is {check['average']:.1f}{check['unit']}, which is above optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': f"Consider increasing ventilation or cooling to reduce temperature by {(check['average'] - check['optimal_max']):.1f}{check['unit']}."
                    })
                elif param == 'Humidity':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'medium',
                        'action': f"Decrease humidity: Current avg is {check['average']:.1f}{check['unit']}, which is above optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Increase ventilation or use dehumidifier to reduce humidity."
                    })
                elif param == 'CO2':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'low',
                        'action': f"Decrease CO2 levels: Current avg is {check['average']:.1f}{check['unit']}, which is above optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Reduce CO2 supplementation or increase ventilation."
                    })
                elif param == 'PPFD':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'medium',
                        'action': f"Decrease light intensity: Current avg is {check['average']:.1f}{check['unit']}, which is above optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Reduce light intensity or duration to prevent light stress."
                    })
                elif param == 'EC':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'high',
                        'action': f"Decrease nutrient concentration: Current avg is {check['average']:.1f}{check['unit']}, which is above optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Dilute the nutrient solution or verify dosing system is functioning correctly."
                    })
                elif param == 'pH':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'high',
                        'action': f"Decrease pH: Current avg is {check['average']:.2f}, which is above optimal range ({check['optimal_min']}-{check['optimal_max']}).",
                        'details': "Add pH down solution and verify pH monitoring system is calibrated correctly."
                    })
                elif param == 'WaterTemp':
                    self.recommendations.append({
                        'parameter': param_display,
                        'severity': 'medium',
                        'action': f"Decrease water temperature: Current avg is {check['average']:.1f}{check['unit']}, which is above optimal range ({check['optimal_min']}-{check['optimal_max']}{check['unit']}).",
                        'details': "Check cooling system or shade water reservoir to maintain lower temperature."
                    })
                    
        # Add recommendations from pattern analysis
        if 'patterns' in self.analysis_results:
            pattern_recommendations = self._generate_pattern_recommendations()
            self.recommendations.extend(pattern_recommendations)
            
        # Add forecasting-based recommendations
        if 'forecasts' in self.analysis_results:
            forecast_recommendations = self._generate_forecast_recommendations()
            self.recommendations.extend(forecast_recommendations)
    
    def _generate_pattern_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on pattern analysis."""
        recommendations = []
        patterns = self.analysis_results.get('patterns', {})
        
        # Check correlations
        correlations = patterns.get('correlations', {})
        for corr_key, corr_data in correlations.items():
            param1, param2 = corr_key.split('_')
            param1_display = self.field_units.get(param1, {}).get('display', param1)
            param2_display = self.field_units.get(param2, {}).get('display', param2)
            
            # Strong negative correlation between Temperature and Humidity
            if (param1 == 'Temperature' and param2 == 'Humidity' and 
                corr_data['correlation'] < -0.7):
                recommendations.append({
                    'parameter': f"{param1_display} & {param2_display}",
                    'severity': 'medium',
                    'action': f"Monitor temperature and humidity relationship: Strong negative correlation detected.",
                    'details': "Increases in temperature are strongly associated with decreases in humidity. Consider humidity control strategies when adjusting temperature."
                })
                
            # Strong positive correlation between CO2 and PPFD (good)
            if (param1 == 'CO2' and param2 == 'PPFD' and 
                corr_data['correlation'] > 0.7):
                recommendations.append({
                    'parameter': f"{param1_display} & {param2_display}",
                    'severity': 'low',
                    'action': f"Maintain CO2 and light synchronization: Strong positive correlation detected.",
                    'details': "CO2 levels and light intensity are well synchronized. Continue this pattern for optimal photosynthesis."
                })
                
            # Weak correlation between CO2 and PPFD (needs improvement)
            if (param1 == 'CO2' and param2 == 'PPFD' and 
                0.3 < corr_data['correlation'] < 0.7):
                recommendations.append({
                    'parameter': f"{param1_display} & {param2_display}",
                    'severity': 'medium',
                    'action': f"Improve CO2 and light synchronization: Moderate correlation detected.",
                    'details': "Increase CO2 levels during periods of high light intensity to optimize photosynthesis efficiency."
                })
                
        # Check daily patterns
        daily_patterns = patterns.get('daily_patterns', {})
        for param, pattern_data in daily_patterns.items():
            param_display = self.field_units.get(param, {}).get('display', param)
            
            # Check for extreme fluctuations in temperature
            if param == 'Temperature' and len(pattern_data.get('peaks', [])) > 0 and len(pattern_data.get('troughs', [])) > 0:
                peak_values = [p[1] for p in pattern_data['peaks']]
                trough_values = [t[1] for t in pattern_data['troughs']]
                
                max_peak = max(peak_values) if peak_values else 0
                min_trough = min(trough_values) if trough_values else 0
                
                if max_peak - min_trough > 5:  # More than 5°C daily swing
                    recommendations.append({
                        'parameter': param_display,
                        'severity': 'medium',
                        'action': f"Reduce daily temperature fluctuations: Daily variation of {max_peak - min_trough:.1f}°C detected.",
                        'details': "Large temperature swings can stress plants. Improve temperature control to maintain more consistent levels throughout the day."
                    })
        
        return recommendations
    
    def _generate_forecast_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on forecasts."""
        recommendations = []
        forecasts = self.analysis_results.get('forecasts', {})
        
        # Process temperature forecasts
        if 'Temperature' in forecasts:
            temp_forecast = forecasts['Temperature']
            
            # Get optimal range
            optimal_min = self.optimal_ranges.get(self.crop_type, {}).get('Temperature', {}).get('min', 17)
            optimal_max = self.optimal_ranges.get(self.crop_type, {}).get('Temperature', {}).get('max', 24)
            
            # Check for forecasted issues
            if temp_forecast.get('forecast_max', 0) > optimal_max + 2:
                recommendations.append({
                    'parameter': 'Temperature (Forecast)',
                    'severity': 'medium',
                    'action': f"Prepare for high temperatures: Forecast shows temperatures reaching {temp_forecast['forecast_max']:.1f}°C.",
                    'details': "Ensure cooling systems are operational and consider adjusting light intensity during peak temperature periods."
                })
                
            if temp_forecast.get('forecast_min', 30) < optimal_min - 2:
                recommendations.append({
                    'parameter': 'Temperature (Forecast)',
                    'severity': 'medium',
                    'action': f"Prepare for low temperatures: Forecast shows temperatures dropping to {temp_forecast['forecast_min']:.1f}°C.",
                    'details': "Ensure heating systems are operational and consider adjusting light schedules to increase heat during expected cold periods."
                })
        
        # Process humidity forecasts
        if 'Humidity' in forecasts:
            humidity_forecast = forecasts['Humidity']
            
            # Get optimal range
            optimal_min = self.optimal_ranges.get(self.crop_type, {}).get('Humidity', {}).get('min', 50)
            optimal_max = self.optimal_ranges.get(self.crop_type, {}).get('Humidity', {}).get('max', 70)
            
            if humidity_forecast.get('forecast_max', 0) > optimal_max + 10:
                recommendations.append({
                    'parameter': 'Humidity (Forecast)',
                    'severity': 'medium',
                    'action': f"Prepare for high humidity: Forecast shows humidity reaching {humidity_forecast['forecast_max']:.1f}%.",
                    'details': "Ensure dehumidifiers are operational and consider increasing ventilation during peak humidity periods."
                })
                
            if humidity_forecast.get('forecast_min', 100) < optimal_min - 10:
                recommendations.append({
                    'parameter': 'Humidity (Forecast)',
                    'severity': 'medium',
                    'action': f"Prepare for low humidity: Forecast shows humidity dropping to {humidity_forecast['forecast_min']:.1f}%.",
                    'details': "Consider using humidifiers or reducing ventilation to maintain proper humidity levels."
                })
        
        # Process CO2 forecasts
        if 'CO2' in forecasts:
            co2_forecast = forecasts['CO2']
            
            # Get optimal range
            optimal_min = self.optimal_ranges.get(self.crop_type, {}).get('CO2', {}).get('min', 800)
            optimal_max = self.optimal_ranges.get(self.crop_type, {}).get('CO2', {}).get('max', 1200)
            
            if co2_forecast.get('trend', '') == 'decreasing' and co2_forecast.get('forecast_value', 1000) < optimal_min:
                recommendations.append({
                    'parameter': 'CO2 (Forecast)',
                    'severity': 'medium',
                    'action': f"Prepare for CO2 deficiency: Forecast shows CO2 levels dropping below {optimal_min} ppm.",
                    'details': "Check CO2 injection system and ensure it's functioning properly. Consider increasing CO2 supplementation."
                })
        
        # Process EC forecasts for trend-based recommendations
        if 'EC' in forecasts:
            ec_forecast = forecasts['EC']
            
            if ec_forecast.get('trend', '') == 'increasing' and ec_forecast.get('trend_confidence', 0) > 0.7:
                recommendations.append({
                    'parameter': 'EC (Forecast)',
                    'severity': 'medium',
                    'action': f"Monitor increasing EC trend: EC is projected to reach {ec_forecast.get('forecast_value', 0):.0f}μS/cm.",
                    'details': "Prepare to adjust nutrient dosing to prevent EC from exceeding optimal range."
                })
                
            elif ec_forecast.get('trend', '') == 'decreasing' and ec_forecast.get('trend_confidence', 0) > 0.7:
                recommendations.append({
                    'parameter': 'EC (Forecast)',
                    'severity': 'medium',
                    'action': f"Monitor decreasing EC trend: EC is projected to drop to {ec_forecast.get('forecast_value', 0):.0f}μS/cm.",
                    'details': "Prepare to add nutrients to prevent EC from falling below optimal range."
                })
                
        # Process pH forecasts
        if 'pH' in forecasts:
            ph_forecast = forecasts['pH']
            
            # Get optimal range
            optimal_min = self.optimal_ranges.get(self.crop_type, {}).get('pH', {}).get('min', 5.8)
            optimal_max = self.optimal_ranges.get(self.crop_type, {}).get('pH', {}).get('max', 6.2)
            
            if ph_forecast.get('trend', '') == 'increasing' and ph_forecast.get('forecast_value', 7) > optimal_max:
                recommendations.append({
                    'parameter': 'pH (Forecast)',
                    'severity': 'high',
                    'action': f"Prepare for pH increase: pH is projected to rise above {optimal_max}.",
                    'details': "Be ready to add pH down solution to maintain optimal pH levels."
                })
                
            elif ph_forecast.get('trend', '') == 'decreasing' and ph_forecast.get('forecast_value', 7) < optimal_min:
                recommendations.append({
                    'parameter': 'pH (Forecast)',
                    'severity': 'high',
                    'action': f"Prepare for pH decrease: pH is projected to drop below {optimal_min}.",
                    'details': "Be ready to add pH up solution to maintain optimal pH levels."
                })
        
        return recommendations
    
    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Get the list of recommendations."""
        return self.recommendations
    
    def plot_daily_trends(self, parameter: str, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot daily trends for a specific parameter.
        
        Args:
            parameter: Parameter to plot
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        if self.data is None or parameter not in self.data.columns:
            logger.warning(f"Cannot plot {parameter}: data not available")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f"No data available for {parameter}", 
                   horizontalalignment='center', verticalalignment='center')
            return fig
        
        # Group by hour of day and calculate statistics
        if 'Timestamp' in self.data.columns:
            # Extract hour
            self.data['Hour'] = self.data['Timestamp'].dt.hour
            
            # Group by hour
            hourly_data = self.data.groupby('Hour')[parameter].agg(['mean', 'min', 'max'])
            
            # Create figure
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot mean with confidence band
            ax.plot(hourly_data.index, hourly_data['mean'], 'b-', label='Average')
            ax.fill_between(hourly_data.index, hourly_data['min'], hourly_data['max'], 
                           color='b', alpha=0.2, label='Min-Max Range')
            
            # Get display name and unit
            display_name = self.field_units.get(parameter, {}).get('display', parameter)
            unit = self.field_units.get(parameter, {}).get('unit', '')
            
            # Add optimal range if available
            if (self.crop_type in self.optimal_ranges and 
                parameter in self.optimal_ranges[self.crop_type]):
                
                opt_min = self.optimal_ranges[self.crop_type][parameter]['min']
                opt_max = self.optimal_ranges[self.crop_type][parameter]['max']
                
                ax.axhline(y=opt_min, color='g', linestyle='--', alpha=0.7, 
                          label=f'Optimal Min ({opt_min}{unit})')
                ax.axhline(y=opt_max, color='r', linestyle='--', alpha=0.7, 
                          label=f'Optimal Max ({opt_max}{unit})')
                
                # Fill optimal range
                ax.axhspan(opt_min, opt_max, color='g', alpha=0.1)
            
            # Customize plot
            ax.set_title(f'Daily Trend: {display_name}', fontsize=16)
            ax.set_xlabel('Hour of Day', fontsize=12)
            ax.set_ylabel(f'{display_name} ({unit})' if unit else display_name, fontsize=12)
            ax.set_xticks(range(0, 24, 2))
            ax.grid(True, alpha=0.3)
            ax.legend(loc='best')
            
            # Adjust layout
            plt.tight_layout()
            
            # Save if path provided
            if save_path:
                plt.savefig(save_path)
            
            return fig
        else:
            logger.warning("Cannot plot daily trends: Timestamp column not available")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, "No timestamp data available", 
                   horizontalalignment='center', verticalalignment='center')
            return fig
    
    def plot_parameter_correlation(self, param1: str, param2: str, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot correlation between two parameters.
        
        Args:
            param1: First parameter
            param2: Second parameter
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        if self.data is None or param1 not in self.data.columns or param2 not in self.data.columns:
            logger.warning(f"Cannot plot correlation: data not available")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f"No data available for correlation between {param1} and {param2}", 
                   horizontalalignment='center', verticalalignment='center')
            return fig
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create scatter plot with regression line
        sns.regplot(x=param1, y=param2, data=self.data, scatter_kws={'alpha':0.5}, ax=ax)
        
        # Get display names and units
        display_name1 = self.field_units.get(param1, {}).get('display', param1)
        unit1 = self.field_units.get(param1, {}).get('unit', '')
        display_name2 = self.field_units.get(param2, {}).get('display', param2)
        unit2 = self.field_units.get(param2, {}).get('unit', '')
        
        # Calculate correlation
        correlation = self.data[[param1, param2]].corr().iloc[0, 1]
        
        # Customize plot
        ax.set_title(f'Correlation between {display_name1} and {display_name2}\n(r = {correlation:.2f})', fontsize=16)
        ax.set_xlabel(f'{display_name1} ({unit1})' if unit1 else display_name1, fontsize=12)
        ax.set_ylabel(f'{display_name2} ({unit2})' if unit2 else display_name2, fontsize=12)
        ax.grid(True, alpha=0.3)
        
        # Add light/dark points if available
        if 'LightStatus' in self.data.columns:
            # Clear previous plot
            ax.clear()
            
            # Plot with color based on light status
            light_on = self.data[self.data['LightStatus'] == 'On']
            light_off = self.data[self.data['LightStatus'] == 'Off']
            
            ax.scatter(light_on[param1], light_on[param2], color='red', alpha=0.5, label='Lights On')
            ax.scatter(light_off[param1], light_off[param2], color='blue', alpha=0.5, label='Lights Off')
            
            # Add title, labels, etc. again
            ax.set_title(f'Correlation between {display_name1} and {display_name2}\n(r = {correlation:.2f})', fontsize=16)
            ax.set_xlabel(f'{display_name1} ({unit1})' if unit1 else display_name1, fontsize=12)
            ax.set_ylabel(f'{display_name2} ({unit2})' if unit2 else display_name2, fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def plot_parameter_over_time(self, parameter: str, days: int = 7, save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot a parameter over time.
        
        Args:
            parameter: Parameter to plot
            days: Number of days to plot (most recent)
            save_path: Optional path to save the plot
            
        Returns:
            Matplotlib figure
        """
        if self.data is None or parameter not in self.data.columns or 'Timestamp' not in self.data.columns:
            logger.warning(f"Cannot plot {parameter} over time: data not available")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f"No time-series data available for {parameter}", 
                   horizontalalignment='center', verticalalignment='center')
            return fig
        
        # Sort data by timestamp
        df = self.data.sort_values('Timestamp')
        
        # Filter to last X days
        if days > 0:
            last_date = df['Timestamp'].max()
            start_date = last_date - timedelta(days=days)
            df = df[df['Timestamp'] >= start_date]
        
        # Get display name and unit
        display_name = self.field_units.get(parameter, {}).get('display', parameter)
        unit = self.field_units.get(parameter, {}).get('unit', '')
        
        # Create figure
        fig, ax = plt.subplots(figsize=(15, 6))
        
        # Plot parameter over time
        ax.plot(df['Timestamp'], df[parameter], 'b-', linewidth=1)
        
        # Add moving average
        window_size = min(24, len(df) // 4)  # Appropriate window size based on data length
        if window_size > 1:
            df['MA'] = df[parameter].rolling(window=window_size).mean()
            ax.plot(df['Timestamp'], df['MA'], 'r-', linewidth=2, label=f'{window_size}-point Moving Avg')
        
        # Add optimal range if available
        if (self.crop_type in self.optimal_ranges and 
            parameter in self.optimal_ranges[self.crop_type]):
            
            opt_min = self.optimal_ranges[self.crop_type][parameter]['min']
            opt_max = self.optimal_ranges[self.crop_type][parameter]['max']
            
            ax.axhline(y=opt_min, color='g', linestyle='--', alpha=0.7, 
                      label=f'Optimal Min ({opt_min}{unit})')
            ax.axhline(y=opt_max, color='r', linestyle='--', alpha=0.7, 
                      label=f'Optimal Max ({opt_max}{unit})')
            
            # Fill optimal range
            ax.axhspan(opt_min, opt_max, color='g', alpha=0.1)
        
        # Customize plot
        title = f'{display_name} over Time'
        if days > 0:
            title += f' (Last {days} days)'
        ax.set_title(title, fontsize=16)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel(f'{display_name} ({unit})' if unit else display_name, fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Format x-axis date
        fig.autofmt_xdate()
        
        # Add forecasts if available
        if hasattr(self, 'forecast_engine') and 'forecasts' in self.analysis_results:
            forecasts = self.analysis_results.get('forecasts', {})
            if parameter in forecasts:
                param_forecast = forecasts[parameter]
                
                # Get forecast data points
                forecast_times = param_forecast.get('forecast_times', [])
                forecast_values = param_forecast.get('forecast_values', [])
                
                if forecast_times and forecast_values and len(forecast_times) == len(forecast_values):
                    # Plot forecast
                    ax.plot(forecast_times, forecast_values, 'g--', linewidth=2, label='Forecast')
                    
                    # Add confidence intervals if available
                    upper_bound = param_forecast.get('upper_bound', [])
                    lower_bound = param_forecast.get('lower_bound', [])
                    
                    if upper_bound and lower_bound and len(upper_bound) == len(forecast_times):
                        ax.fill_between(forecast_times, lower_bound, upper_bound, 
                                      color='g', alpha=0.2, label='Forecast Confidence')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path)
        
        return fig
    
    def generate_report(self, output_dir: str = "./reports") -> str:
        """
        Generate a complete analysis report.
        
        Args:
            output_dir: Directory to save the report
            
        Returns:
            Path to the report
        """
        if self.data is None:
            logger.warning("Cannot generate report: No data available")
            return ""
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = os.path.join(output_dir, f"report_{timestamp}")
        os.makedirs(report_dir, exist_ok=True)
        
        # Create plots directory
        plots_dir = os.path.join(report_dir, "plots")
        os.makedirs(plots_dir, exist_ok=True)
        
        # Generate plots for key parameters
        key_parameters = [
            'Temperature', 'Humidity', 'CO2', 'PPFD', 'EC', 'pH', 'WaterTemp'
        ]
        
        # Filter to include only columns that exist in the data
        key_parameters = [param for param in key_parameters if param in self.data.columns]
        
        # Generate daily trend plots
        for param in key_parameters:
            plot_path = os.path.join(plots_dir, f"{param}_daily_trend.png")
            self.plot_daily_trends(param, save_path=plot_path)
        
        # Generate time series plots
        for param in key_parameters:
            plot_path = os.path.join(plots_dir, f"{param}_time_series.png")
            self.plot_parameter_over_time(param, days=7, save_path=plot_path)
        
        # Generate correlation plots for important pairs
        correlation_pairs = [
            ('Temperature', 'Humidity'),
            ('PPFD', 'Temperature'),
            ('PPFD', 'CO2'),
            ('EC', 'pH')
        ]
        
        for param1, param2 in correlation_pairs:
            if param1 in self.data.columns and param2 in self.data.columns:
                plot_path = os.path.join(plots_dir, f"{param1}_{param2}_correlation.png")
                self.plot_parameter_correlation(param1, param2, save_path=plot_path)
        
        # Generate JSON report
        report_data = {
            'generated_at': datetime.now().isoformat(),
            'farm_id': self.farm_id,
            'crop_type': self.crop_type,
            'data_summary': {
                'record_count': len(self.data),
                'start_date': self.data['Timestamp'].min().isoformat() if 'Timestamp' in self.data.columns else None,
                'end_date': self.data['Timestamp'].max().isoformat() if 'Timestamp' in self.data.columns else None
            },
            'analysis': self.analysis_results,
            'recommendations': self.recommendations,
            'harmony_states': self.detect_harmony_states() if hasattr(self, 'detect_harmony_states') else []
        }
        
        report_path = os.path.join(report_dir, "report.json")
        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        # Generate HTML report
        html_report = self._generate_html_report(report_data, plots_dir)
        
        html_path = os.path.join(report_dir, "report.html")
        with open(html_path, 'w') as f:
            f.write(html_report)
        
        logger.info(f"Report generated at: {report_dir}")
        
        return report_dir
    
    def _generate_html_report(self, report_data: Dict[str, Any], plots_dir: str) -> str:
        """Generate HTML report from report data."""
        # Get relative paths to plot images
        plot_files = [f for f in os.listdir(plots_dir) if f.endswith('.png')]
        
        # Group plots by type
        daily_trend_plots = [f for f in plot_files if 'daily_trend' in f]
        time_series_plots = [f for f in plot_files if 'time_series' in f]
        correlation_plots = [f for f in plot_files if 'correlation' in f]
        
        # Create HTML content
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Freight Farm Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                h1, h2, h3 {{
                    color: #0d6efd;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                }}
                .header {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                }}
                .metric-card {{
                    background-color: #fff;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    padding: 15px;
                    margin-bottom: 15px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .metric-card h3 {{
                    margin-top: 0;
                }}
                .recommendations {{
                    background-color: #f0f8ff;
                    border-left: 4px solid #0d6efd;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .critical {{
                    background-color: #fff0f0;
                    border-left: 4px solid #dc3545;
                }}
                .warning {{
                    background-color: #fff8e6;
                    border-left: 4px solid #ffc107;
                }}
                .harmony-state {{
                    background-color: #f0fff0;
                    border-left: 4px solid #28a745;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .row {{
                    display: flex;
                    flex-wrap: wrap;
                    margin: 0 -10px;
                }}
                .col {{
                    flex: 1;
                    padding: 0 10px;
                    min-width: 300px;
                }}
                .plot-container {{
                    margin-bottom: 30px;
                }}
                .plot-container img {{
                    max-width: 100%;
                    height: auto;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                }}
                table, th, td {{
                    border: 1px solid #ddd;
                }}
                th, td {{
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Freight Farm Analysis Report</h1>
                    <p>Generated: {report_data['generated_at']}</p>
                    <p>Farm ID: {report_data['farm_id']}</p>
                    <p>Crop Type: {report_data['crop_type']}</p>
                    <p>Records: {report_data['data_summary']['record_count']}</p>
                    <p>Period: {report_data['data_summary']['start_date']} to {report_data['data_summary']['end_date']}</p>
                </div>
                
                <h2>Executive Summary</h2>
                <div class="row">
        """
        
        # Add summary metrics
        if 'environmental' in report_data['analysis']:
            env_data = report_data['analysis']['environmental']
            html += """
                    <div class="col">
                        <div class="metric-card">
                            <h3>Environmental Metrics</h3>
                            <table>
                                <tr>
                                    <th>Parameter</th>
                                    <th>Min</th>
                                    <th>Avg</th>
                                    <th>Max</th>
                                </tr>
            """
            
            for param, data in env_data.items():
                display_name = self.field_units.get(param, {}).get('display', param)
                unit = data.get('unit', '')
                html += f"""
                                <tr>
                                    <td>{display_name}</td>
                                    <td>{data['min']:.1f}{unit}</td>
                                    <td>{data['avg']:.1f}{unit}</td>
                                    <td>{data['max']:.1f}{unit}</td>
                                </tr>
                """
            
            html += """
                            </table>
                        </div>
                    </div>
            """
        
        # Add optimal range check
        if 'optimal_check' in report_data['analysis']:
            opt_data = report_data['analysis']['optimal_check']
            html += """
                    <div class="col">
                        <div class="metric-card">
                            <h3>Optimal Range Assessment</h3>
                            <table>
                                <tr>
                                    <th>Parameter</th>
                                    <th>Average</th>
                                    <th>Optimal Range</th>
                                    <th>Status</th>
                                </tr>
            """
            
            for param, data in opt_data.get('parameters', {}).items():
                display_name = self.field_units.get(param, {}).get('display', param)
                unit = data.get('unit', '')
                
                # Set status style
                status_class = ""
                if data['status'] == 'below':
                    status_class = "color: orange;"
                elif data['status'] == 'above':
                    status_class = "color: red;"
                else:
                    status_class = "color: green;"
                
                html += f"""
                                <tr>
                                    <td>{display_name}</td>
                                    <td>{data['average']:.1f}{unit}</td>
                                    <td>{data['optimal_min']}{unit} - {data['optimal_max']}{unit}</td>
                                    <td style="{status_class}">{data['status'].upper()}</td>
                                </tr>
                """
            
            html += """
                            </table>
                        </div>
                    </div>
            """
        
        html += """
                </div>
                
                <h2>Harmony States</h2>
        """
        
        # Add harmony states section
        if report_data.get('harmony_states'):
            for state in report_data['harmony_states']:
                html += f"""
                <div class="harmony-state">
                    <h3>{state}</h3>
                    <p>The system has detected this harmonious state where multiple parameters are working together optimally.</p>
                </div>
                """
        else:
            html += """
                <p>No harmony states detected in the current data.</p>
            """
        
        html += """
                <h2>Recommendations</h2>
        """
        
        # Add recommendations
        if report_data['recommendations']:
            for rec in report_data['recommendations']:
                severity_class = ""
                if rec['severity'] == 'high':
                    severity_class = "critical"
                elif rec['severity'] == 'medium':
                    severity_class = "warning"
                
                html += f"""
                <div class="recommendations {severity_class}">
                    <h3>{rec['parameter']}</h3>
                    <p><strong>{rec['action']}</strong></p>
                    <p>{rec['details']}</p>
                </div>
                """
        else:
            html += """
                <p>No recommendations at this time. All parameters appear to be within optimal ranges.</p>
            """
        
        # Add daily trend plots
        if daily_trend_plots:
            html += """
                <h2>Daily Trends</h2>
                <div class="row">
            """
            
            for plot_file in daily_trend_plots:
                param = plot_file.split('_daily')[0]
                display_name = self.field_units.get(param, {}).get('display', param)
                
                html += f"""
                    <div class="col">
                        <div class="plot-container">
                            <h3>{display_name} Daily Trend</h3>
                            <img src="plots/{plot_file}" alt="{display_name} Daily Trend">
                        </div>
                    </div>
                """
            
            html += """
                </div>
            """
        
        # Add time series plots
        if time_series_plots:
            html += """
                <h2>Time Series Analysis</h2>
                <div class="row">
            """
            
            for plot_file in time_series_plots:
                param = plot_file.split('_time')[0]
                display_name = self.field_units.get(param, {}).get('display', param)
                
                html += f"""
                    <div class="col">
                        <div class="plot-container">
                            <h3>{display_name} Over Time</h3>
                            <img src="plots/{plot_file}" alt="{display_name} Time Series">
                        </div>
                    </div>
                """
            
            html += """
                </div>
            """
        
        # Add correlation plots
        if correlation_plots:
            html += """
                <h2>Parameter Correlations</h2>
                <div class="row">
            """
            
            for plot_file in correlation_plots:
                params = plot_file.split('_correlation')[0]
                param1, param2 = params.split('_')
                display_name1 = self.field_units.get(param1, {}).get('display', param1)
                display_name2 = self.field_units.get(param2, {}).get('display', param2)
                
                html += f"""
                    <div class="col">
                        <div class="plot-container">
                            <h3>{display_name1} vs {display_name2}</h3>
                            <img src="plots/{plot_file}" alt="{display_name1} vs {display_name2} Correlation">
                        </div>
                    </div>
                """
            
            html += """
                </div>
            """
        
        # Add pattern analysis section if available
        if 'patterns' in report_data['analysis']:
            patterns = report_data['analysis']['patterns']
            if patterns.get('correlations'):
                html += """
                    <h2>Pattern Analysis</h2>
                    <div class="metric-card">
                        <h3>Parameter Correlations</h3>
                        <table>
                            <tr>
                                <th>Parameters</th>
                                <th>Correlation</th>
                                <th>Strength</th>
                            </tr>
                """
                
                for key, correlation in patterns.get('correlations', {}).items():
                    param1, param2 = key.split('_')
                    display_name1 = self.field_units.get(param1, {}).get('display', param1)
                    display_name2 = self.field_units.get(param2, {}).get('display', param2)
                    
                    html += f"""
                            <tr>
                                <td>{display_name1} & {display_name2}</td>
                                <td>{correlation.get('correlation', 0):.2f}</td>
                                <td>{correlation.get('strength', 'unknown')}</td>
                            </tr>
                    """
                
                html += """
                        </table>
                    </div>
                """
                
            # Add forecast section if available
            if 'forecasts' in report_data['analysis']:
                forecasts = report_data['analysis']['forecasts']
                if forecasts:
                    html += """
                        <h2>Forecasts</h2>
                        <div class="metric-card">
                            <h3>Parameter Forecasts</h3>
                            <table>
                                <tr>
                                    <th>Parameter</th>
                                    <th>Current</th>
                                    <th>Forecast</th>
                                    <th>Trend</th>
                                </tr>
                    """
                    
                    for param, forecast in forecasts.items():
                        display_name = self.field_units.get(param, {}).get('display', param)
                        unit = self.field_units.get(param, {}).get('unit', '')
                        
                        # Format values
                        current_val = forecast.get('current_value', 0)
                        forecast_val = forecast.get('forecast_value', 0)
                        trend = forecast.get('trend', 'stable')
                        
                        # Set trend style
                        trend_class = ""
                        if trend == 'increasing':
                            trend_class = "color: green;"
                        elif trend == 'decreasing':
                            trend_class = "color: red;"
                        
                        html += f"""
                                <tr>
                                    <td>{display_name}</td>
                                    <td>{current_val:.1f}{unit}</td>
                                    <td>{forecast_val:.1f}{unit}</td>
                                    <td style="{trend_class}">{trend}</td>
                                </tr>
                        """
                    
                    html += """
                            </table>
                        </div>
                    """
        
        # Close HTML
        html += """
            </div>
        </body>
        </html>
        """
        
        return html