"""
PulseFarmBridge - Advanced Integration Module for PulseROS and FreightFarmUFM
Version: 2.0

Description: Enhanced bidirectional integration between PulseROS robotics control and 
             FreightFarmUFM fold pattern tracking for synchronized plant care in controlled
             agriculture environments, with support for multi-farm coordination, 
             environmental optimization, and adaptive growth pattern analysis.

Features:
- Translates FreightFarmUFM pattern recommendations into PulseROS care tasks
- Maps biofield data to optimize robotic movement patterns
- Coordinates multiple robots through UFM-enhanced federation
- Enables default gardening behaviors guided by fold pattern harmony states
- Facilitates spatial coordination in confined growing environments
- Implements advanced environmental optimization using fold pattern analysis
- Provides predictive growth modeling based on pattern evolution
- Supports multi-farm synchronization for distributed operations
"""

import os
import sys
import json
import time
import uuid
import logging
import asyncio
import threading
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union, Set, Callable
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta
import traceback
import hashlib
import math
import requests
from io import StringIO

# Import from existing modules
from PulseROS import (
    PulseROSIntegration, PulseROSBridge, PulseCareTaskScheduler, 
    PulseGardeningActions, PulseDefaultBehaviorManager,
    NodeRole, RoboticTask, TaskPriority, TaskStatus, PlantData,
    PulseMeshMessage, CommunicationLayer, RoboticsMessageIntent, 
    TransmissionPriority
)

from FreightFarmHarmony import (
    FreightFarmUFM, ScaleLevel, FoldPattern,
    PlantGrowthPattern, PlantBiofield
)

# Configure module logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pulse_farm_bridge")

# ===== EXTENDED ENUMS AND DATA STRUCTURES =====

class FarmSystemType(Enum):
    """Types of farm systems supported."""
    FREIGHT_FARM = auto()      # Standard Freight Farm container
    VERTICAL_FARM = auto()     # Vertical farming setup
    GREENHOUSE = auto()        # Controlled greenhouse
    AQUAPONICS = auto()        # Aquaponic system
    AEROPONICS = auto()        # Aeroponic system
    HYBRID = auto()            # Hybrid system


class GrowthPredictionModel(Enum):
    """Prediction models for plant growth analysis."""
    LINEAR = auto()           # Simple linear projection
    EXPONENTIAL = auto()      # Exponential growth model
    LOGISTIC = auto()         # Logistic (S-curve) growth model
    FOLD_PATTERN = auto()     # UFM fold pattern based prediction
    HARMONY_WEIGHTED = auto() # Harmony state weighted model
    ENSEMBLE = auto()         # Ensemble of multiple models


class EnvironmentOptimizationMode(Enum):
    """Modes for environmental parameter optimization."""
    ENERGY_SAVING = auto()      # Prioritize energy efficiency
    YIELD_MAXIMIZING = auto()   # Prioritize maximum yield
    QUALITY_FOCUSED = auto()    # Prioritize crop quality
    WATER_CONSERVING = auto()   # Prioritize water conservation
    BALANCED = auto()           # Balance all parameters
    PATTERN_GUIDED = auto()     # Use fold patterns to guide optimization


@dataclass
class EnvironmentalParameters:
    """Environmental parameters for growing zone."""
    temperature: float = 22.0  # Celsius
    humidity: float = 0.65     # Relative (0-1)
    co2_level: float = 800.0   # ppm
    light_intensity: float = 0.7  # Relative (0-1)
    light_spectrum: Dict[str, float] = field(default_factory=lambda: {
        "red": 0.6, "blue": 0.3, "green": 0.1
    })
    air_circulation: float = 0.5  # Relative (0-1)
    nutrient_ec: float = 1.8      # Electrical conductivity (mS/cm)
    nutrient_ph: float = 6.0      # pH
    day_length: float = 16.0      # Hours of light per day
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "temperature": self.temperature,
            "humidity": self.humidity,
            "co2_level": self.co2_level,
            "light_intensity": self.light_intensity,
            "light_spectrum": self.light_spectrum,
            "air_circulation": self.air_circulation,
            "nutrient_ec": self.nutrient_ec,
            "nutrient_ph": self.nutrient_ph,
            "day_length": self.day_length
        }


@dataclass
class GrowthPrediction:
    """Predicted growth based on fold pattern analysis."""
    plant_id: str
    current_stage: str
    predicted_stage: str
    days_to_next_stage: float
    predicted_yield: float  # Estimated yield in grams
    quality_score: float    # Predicted quality (0-1)
    confidence: float       # Prediction confidence (0-1)
    fold_integrity: float   # Pattern integrity measure (0-1)
    recommended_actions: List[Dict[str, Any]] = field(default_factory=list)
    creation_time: float = field(default_factory=time.time)
    model_type: GrowthPredictionModel = GrowthPredictionModel.FOLD_PATTERN
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "plant_id": self.plant_id,
            "current_stage": self.current_stage,
            "predicted_stage": self.predicted_stage,
            "days_to_next_stage": self.days_to_next_stage,
            "predicted_yield": self.predicted_yield,
            "quality_score": self.quality_score,
            "confidence": self.confidence,
            "fold_integrity": self.fold_integrity,
            "recommended_actions": self.recommended_actions,
            "creation_time": self.creation_time,
            "model_type": self.model_type.name,
            "metadata": self.metadata
        }


@dataclass
class ResourceUsage:
    """Resource consumption tracking."""
    water_usage_ml: float = 0.0     # Water used in milliliters
    energy_usage_kwh: float = 0.0   # Energy used in kilowatt-hours
    nutrient_usage_ml: float = 0.0  # Nutrient solution used in milliliters
    co2_usage_g: float = 0.0        # CO2 used in grams
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "water_usage_ml": self.water_usage_ml,
            "energy_usage_kwh": self.energy_usage_kwh,
            "nutrient_usage_ml": self.nutrient_usage_ml,
            "co2_usage_g": self.co2_usage_g,
            "start_time": self.start_time,
            "end_time": self.end_time
        }


@dataclass
class FarmPerformanceMetrics:
    """Performance metrics for a farm system."""
    farm_id: str
    yield_per_sqm: float = 0.0          # kg/m²
    energy_per_kg: float = 0.0          # kWh/kg
    water_per_kg: float = 0.0           # L/kg
    average_growth_time: float = 0.0    # days
    pattern_coherence: float = 0.0      # 0-1
    system_reliability: float = 0.0     # 0-1
    sustainability_score: float = 0.0   # 0-1
    creation_time: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "farm_id": self.farm_id,
            "yield_per_sqm": self.yield_per_sqm,
            "energy_per_kg": self.energy_per_kg,
            "water_per_kg": self.water_per_kg,
            "average_growth_time": self.average_growth_time,
            "pattern_coherence": self.pattern_coherence,
            "system_reliability": self.system_reliability,
            "sustainability_score": self.sustainability_score,
            "creation_time": self.creation_time
        }


@dataclass
class HarvestPlan:
    """Planned harvest based on fold pattern and growth predictions."""
    farm_id: str
    scheduled_date: float  # Timestamp for planned harvest
    zones: List[str]  # Zone IDs to harvest
    plant_ids: List[str]  # Specific plants to harvest
    estimated_yield: float  # Estimated yield in kg
    optimal_window_start: float  # Start of optimal harvest window
    optimal_window_end: float  # End of optimal harvest window
    priority: int = 1  # Harvest priority (1-5)
    notes: List[str] = field(default_factory=list)
    fold_pattern_basis: Optional[str] = None  # Related fold pattern
    creation_time: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "farm_id": self.farm_id,
            "scheduled_date": self.scheduled_date,
            "zones": self.zones,
            "plant_ids": self.plant_ids,
            "estimated_yield": self.estimated_yield,
            "optimal_window_start": self.optimal_window_start,
            "optimal_window_end": self.optimal_window_end,
            "priority": self.priority,
            "notes": self.notes,
            "fold_pattern_basis": self.fold_pattern_basis,
            "creation_time": self.creation_time
        }


# ===== ENHANCED FARM BRIDGE CLASS =====

class PulseFarmBridge:
    """
    Enhanced integration bridge between PulseROS and FreightFarmUFM systems.
    
    Enables smart robotic farm management guided by Universal Fold Mapping
    patterns and biofield analysis for optimal plant care, with advanced
    features for multi-farm coordination, environmental optimization,
    and predictive modeling.
    """
    
    def __init__(self, 
                bridge_id: Optional[str] = None,
                ros_integration: Optional[PulseROSIntegration] = None,
                farm_ufm: Optional[FreightFarmUFM] = None,
                farm_id: Optional[str] = None,
                farm_type: FarmSystemType = FarmSystemType.FREIGHT_FARM,
                mode: BridgeMode = BridgeMode.ADVISORY,
                config: Dict[str, Any] = None):
        """
        Initialize the PulseFarmBridge.
        
        Args:
            bridge_id: Unique identifier for this bridge
            ros_integration: PulseROSIntegration instance
            farm_ufm: FreightFarmUFM instance
            farm_id: Farm identifier if creating new instances
            farm_type: Type of farm system
            mode: Initial bridge operation mode
            config: Configuration options
        """
        # Set bridge ID
        self.bridge_id = bridge_id or f"farm_bridge_{uuid.uuid4().hex[:8]}"
        
        # Set configuration
        self.config = config or {}
        
        # Initialize or use existing ROS integration
        self.ros_integration = ros_integration
        self.ros_connected = ros_integration is not None
        
        # Initialize or use existing UFM instance
        self.farm_ufm = farm_ufm
        self.ufm_connected = farm_ufm is not None
        
        # Store farm ID and type
        self.farm_id = farm_id
        if self.farm_ufm:
            self.farm_id = self.farm_ufm.farm_id
        if not self.farm_id:
            self.farm_id = f"farm_{uuid.uuid4().hex[:8]}"
            
        self.farm_type = farm_type
        
        # Initialize bridge state
        self.state = BridgeState(
            bridge_id=self.bridge_id,
            mode=mode,
            farm_id=self.farm_id,
            ros_connected=self.ros_connected,
            ufm_connected=self.ufm_connected,
            robot_count=0
        )
        
        # Storage for care actions
        self.care_actions: Dict[str, PlantCareAction] = {}
        self.action_history: List[PlantCareAction] = []
        
        # Spatial model of the farm
        self.zones: Dict[str, SpatialZone] = {}
        self.plants: Dict[str, PlantData] = {}
        
        # Robot coordination mapping
        self.robot_locations: Dict[str, Tuple[float, float, float]] = {}
        self.robot_assignments: Dict[str, Dict[str, Any]] = {}
        
        # Task synchronization
        self.pending_tasks: List[RoboticTask] = []
        self.executing_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        
        # Pattern and biofield caches
        self.pattern_cache: Dict[str, PlantGrowthPattern] = {}
        self.biofield_cache: Dict[str, PlantBiofield] = {}
        
        # Reference to ROS components
        self.ros_bridge = None
        self.care_scheduler = None
        self.gardening_actions = None
        self.behavior_manager = None
        
        # Extract references from ROS integration if provided
        if self.ros_integration:
            self.ros_bridge = getattr(self.ros_integration, 'ros_bridge', None)
            self.care_scheduler = getattr(self.ros_integration, 'care_scheduler', None)
            self.gardening_actions = getattr(self.ros_integration, 'gardening_actions', None)
            self.behavior_manager = getattr(self.ros_integration, 'default_behavior_manager', None)
            
            # Count robots
            if self.ros_integration.is_active:
                self.state.robot_count = 1
        
        # Initialize FreightFarmUFM if needed
        if not self.farm_ufm and farm_id:
            self._initialize_farm_ufm()
        
        # Initialize PulseROSIntegration if needed
        if not self.ros_integration and not self.config.get("no_ros_init", False):
            self._initialize_ros_integration()
        
        # Internal state
        self.is_active = False
        self.sync_task = None
        self.action_task = None
        self.spatial_model_initialized = False
        
        # Create directories for data storage
        self._create_data_directories()
        
        # Initialize enhanced components
        self.environmental_parameters: Dict[str, EnvironmentalParameters] = {}
        self.growth_predictions: Dict[str, GrowthPrediction] = {}
        self.resource_usage = ResourceUsage()
        self.performance_metrics = FarmPerformanceMetrics(farm_id=self.farm_id)
        self.harvest_plans: List[HarvestPlan] = []
        
        # Enhanced task management
        self.prediction_task = None
        self.optimization_task = None
        self.resource_tracking_task = None
        
        # Multi-farm coordination
        self.connected_farms: Dict[str, Dict[str, Any]] = {}
        
        # Optimization settings
        self.optimization_mode = EnvironmentOptimizationMode.BALANCED
        self.prediction_model = GrowthPredictionModel.FOLD_PATTERN
        
        # Data analysis
        self.growth_data_buffer: List[Dict[str, Any]] = []
        self.environment_data_buffer: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized PulseFarmBridge (ID: {self.bridge_id}, Mode: {mode.name}, Type: {farm_type.name})")
    
    # ... [Keeping existing methods] ...
    
    # ===== NEW ENHANCED METHODS =====
    
    async def start_enhanced_features(self) -> Dict[str, Any]:
        """
        Start enhanced bridge features.
        
        Returns:
            Startup results
        """
        if not self.is_active:
            logger.warning("Bridge not active. Call start() before start_enhanced_features()")
            return {"success": False, "message": "Bridge not active"}
            
        try:
            # Start growth prediction task
            self.prediction_task = asyncio.create_task(self._run_growth_predictions())
            
            # Start environment optimization task
            self.optimization_task = asyncio.create_task(self._run_environment_optimization())
            
            # Start resource tracking task
            self.resource_tracking_task = asyncio.create_task(self._track_resource_usage())
            
            logger.info(f"Enhanced features started for bridge: {self.bridge_id}")
            
            return {
                "success": True,
                "message": "Enhanced features started",
                "bridge_id": self.bridge_id,
                "features": ["growth_prediction", "environment_optimization", "resource_tracking"]
            }
            
        except Exception as e:
            logger.error(f"Error starting enhanced features: {e}")
            traceback.print_exc()
            
            return {
                "success": False,
                "message": f"Error starting enhanced features: {str(e)}",
                "bridge_id": self.bridge_id
            }
    
    async def stop_enhanced_features(self) -> Dict[str, Any]:
        """
        Stop enhanced bridge features.
        
        Returns:
            Shutdown results
        """
        try:
            # Cancel prediction task
            if self.prediction_task:
                self.prediction_task.cancel()
                try:
                    await self.prediction_task
                except asyncio.CancelledError:
                    pass
                    
            # Cancel optimization task
            if self.optimization_task:
                self.optimization_task.cancel()
                try:
                    await self.optimization_task
                except asyncio.CancelledError:
                    pass
                    
            # Cancel resource tracking task
            if self.resource_tracking_task:
                self.resource_tracking_task.cancel()
                try:
                    await self.resource_tracking_task
                except asyncio.CancelledError:
                    pass
                    
            logger.info(f"Enhanced features stopped for bridge: {self.bridge_id}")
            
            return {
                "success": True,
                "message": "Enhanced features stopped",
                "bridge_id": self.bridge_id
            }
            
        except Exception as e:
            logger.error(f"Error stopping enhanced features: {e}")
            
            return {
                "success": False,
                "message": f"Error stopping enhanced features: {str(e)}",
                "bridge_id": self.bridge_id
            }
    
    async def set_environmental_parameters(self, zone_id: str, 
                                        parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set environmental parameters for a specific zone.
        
        Args:
            zone_id: Zone identifier
            parameters: Environmental parameters
            
        Returns:
            Result of the operation
        """
        try:
            # Check if zone exists
            if zone_id not in self.zones:
                return {"success": False, "error": f"Zone not found: {zone_id}"}
                
            # Create or update parameters
            if zone_id not in self.environmental_parameters:
                self.environmental_parameters[zone_id] = EnvironmentalParameters()
                
            params = self.environmental_parameters[zone_id]
            
            # Update parameters
            if "temperature" in parameters:
                params.temperature = float(parameters["temperature"])
            if "humidity" in parameters:
                params.humidity = float(parameters["humidity"])
            if "co2_level" in parameters:
                params.co2_level = float(parameters["co2_level"])
            if "light_intensity" in parameters:
                params.light_intensity = float(parameters["light_intensity"])
            if "light_spectrum" in parameters:
                params.light_spectrum.update(parameters["light_spectrum"])
            if "air_circulation" in parameters:
                params.air_circulation = float(parameters["air_circulation"])
            if "nutrient_ec" in parameters:
                params.nutrient_ec = float(parameters["nutrient_ec"])
            if "nutrient_ph" in parameters:
                params.nutrient_ph = float(parameters["nutrient_ph"])
            if "day_length" in parameters:
                params.day_length = float(parameters["day_length"])
                
            # Apply parameters to physical systems if in AUTONOMOUS mode
            if self.state.mode == BridgeMode.AUTONOMOUS:
                await self._apply_environmental_parameters(zone_id, params)
                
            # Record in data buffer
            self.environment_data_buffer.append({
                "timestamp": time.time(),
                "zone_id": zone_id,
                "parameters": params.to_dict(),
                "source": "manual_set"
            })
            
            # Create environment update message
            message = PulseMeshMessage(
                sender_id=self.bridge_id,
                sender_name=f"Farm Bridge {self.bridge_id[:6]}",
                layer=CommunicationLayer.WIFI_MESH,
                intent=RoboticsMessageIntent.ENVIRONMENT_DATA,
                priority=TransmissionPriority.NORMAL,
                content=f"Environmental parameters updated for zone {zone_id}",
                metadata={
                    "zone_id": zone_id,
                    "parameters": params.to_dict(),
                    "timestamp": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(message)
            
            return {
                "success": True, 
                "zone_id": zone_id,
                "parameters": params.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error setting environmental parameters: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_environmental_parameters(self, zone_id: str) -> Dict[str, Any]:
        """
        Get environmental parameters for a specific zone.
        
        Args:
            zone_id: Zone identifier
            
        Returns:
            Environmental parameters
        """
        try:
            # Check if zone exists
            if zone_id not in self.zones:
                return {"success": False, "error": f"Zone not found: {zone_id}"}
                
            # Check if parameters exist
            if zone_id not in self.environmental_parameters:
                # Create default parameters
                self.environmental_parameters[zone_id] = EnvironmentalParameters()
                
            params = self.environmental_parameters[zone_id]
            
            return {
                "success": True,
                "zone_id": zone_id,
                "parameters": params.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting environmental parameters: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_growth_prediction(self, plant_id: str, 
                                    model_type: GrowthPredictionModel = GrowthPredictionModel.FOLD_PATTERN) -> Dict[str, Any]:
        """
        Create a growth prediction for a specific plant.
        
        Args:
            plant_id: Plant identifier
            model_type: Type of prediction model to use
            
        Returns:
            Growth prediction
        """
        try:
            # Check if plant exists
            if plant_id not in self.plants:
                return {"success": False, "error": f"Plant not found: {plant_id}"}
                
            plant = self.plants[plant_id]
            
            # Get latest growth pattern if available
            pattern = None
            pattern_id = None
            
            for action_id, action in self.care_actions.items():
                if action.plant_id == plant_id and action.source_pattern_id:
                    if action.source_pattern_id in self.pattern_cache:
                        pattern = self.pattern_cache[action.source_pattern_id]
                        pattern_id = action.source_pattern_id
                        break
            
            # Generate prediction based on model type
            if model_type == GrowthPredictionModel.FOLD_PATTERN:
                prediction = self._generate_fold_pattern_prediction(plant, pattern)
            elif model_type == GrowthPredictionModel.LINEAR:
                prediction = self._generate_linear_prediction(plant)
            elif model_type == GrowthPredictionModel.EXPONENTIAL:
                prediction = self._generate_exponential_prediction(plant)
            elif model_type == GrowthPredictionModel.LOGISTIC:
                prediction = self._generate_logistic_prediction(plant)
            elif model_type == GrowthPredictionModel.HARMONY_WEIGHTED:
                prediction = self._generate_harmony_weighted_prediction(plant, pattern)
            elif model_type == GrowthPredictionModel.ENSEMBLE:
                prediction = self._generate_ensemble_prediction(plant, pattern)
            else:
                # Default to fold pattern prediction
                prediction = self._generate_fold_pattern_prediction(plant, pattern)
                
            # Set model type
            prediction.model_type = model_type
            
            # Store prediction
            self.growth_predictions[plant_id] = prediction
            
            # Record in data buffer
            self.growth_data_buffer.append({
                "timestamp": time.time(),
                "plant_id": plant_id,
                "prediction": prediction.to_dict(),
                "pattern_id": pattern_id,
                "source": "manual_prediction"
            })
            
            return {
                "success": True,
                "plant_id": plant_id,
                "prediction": prediction.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating growth prediction: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    def _generate_fold_pattern_prediction(self, plant: PlantData, 
                                       pattern: Optional[PlantGrowthPattern] = None) -> GrowthPrediction:
        """
        Generate growth prediction based on fold pattern analysis.
        
        Args:
            plant: Plant data
            pattern: Growth pattern if available
            
        Returns:
            Growth prediction
        """
        # Default values
        current_stage = plant.growth_stage
        confidence = 0.7  # Default confidence
        fold_integrity = 0.8  # Default integrity
        
        # Calculate better values if pattern available
        if pattern:
            fold_integrity = pattern.metadata.get("fold_integrity", 0.8)
            
            # Extract metrics if available
            if "growth_metrics" in pattern.metadata:
                metrics = pattern.metadata["growth_metrics"]
                if "pattern_coherence" in metrics:
                    confidence = metrics["pattern_coherence"]
        
        # Map current stage to next stage
        stage_progression = {
            "seedling": "vegetative",
            "vegetative": "flowering",
            "flowering": "fruiting",
            "fruiting": "harvest",
            "harvest": "complete"
        }
        
        # Determine next stage
        predicted_stage = stage_progression.get(current_stage, current_stage)
        
        # Calculate days to next stage based on current stage and fold integrity
        base_days = {
            "seedling": 14.0,
            "vegetative": 21.0,
            "flowering": 28.0,
            "fruiting": 21.0,
            "harvest": 7.0
        }
        
        # Adjust days based on fold integrity (better integrity = faster growth)
        base_time = base_days.get(current_stage, 14.0)
        days_to_next_stage = base_time * (1.5 - fold_integrity/2.0)
        
        # Calculate predicted yield based on pattern metrics
        base_yield = {
            "seedling": 0.0,
            "vegetative": 50.0,
            "flowering": 150.0,
            "fruiting": 350.0,
            "harvest": 500.0
        }
        
        # Adjust yield based on fold integrity
        base_yield_value = base_yield.get(predicted_stage, 100.0)
        predicted_yield = base_yield_value * fold_integrity
        
        # Calculate quality score based on pattern coherence
        quality_score = confidence * fold_integrity
        
        # Generate recommended actions
        recommended_actions = []
        
        if fold_integrity < 0.6:
            recommended_actions.append({
                "action": "adjust_nutrients",
                "urgency": "high",
                "details": "Low fold integrity detected. Adjust nutrient balance to improve pattern coherence."
            })
            
        if confidence < 0.7:
            recommended_actions.append({
                "action": "monitor_environment",
                "urgency": "medium",
                "details": "Pattern confidence below threshold. Monitor and stabilize environmental conditions."
            })
            
        # Create prediction
        prediction = GrowthPrediction(
            plant_id=plant.plant_id,
            current_stage=current_stage,
            predicted_stage=predicted_stage,
            days_to_next_stage=days_to_next_stage,
            predicted_yield=predicted_yield,
            quality_score=quality_score,
            confidence=confidence,
            fold_integrity=fold_integrity,
            recommended_actions=recommended_actions,
            model_type=GrowthPredictionModel.FOLD_PATTERN
        )
        
        return prediction
        
    def _generate_linear_prediction(self, plant: PlantData) -> GrowthPrediction:
        """Generate simple linear growth prediction."""
        # Simple implementation with placeholder logic
        current_stage = plant.growth_stage
        stage_progression = {
            "seedling": "vegetative",
            "vegetative": "flowering",
            "flowering": "fruiting",
            "fruiting": "harvest",
            "harvest": "complete"
        }
        predicted_stage = stage_progression.get(current_stage, current_stage)
        
        # Create prediction with simplified values
        prediction = GrowthPrediction(
            plant_id=plant.plant_id,
            current_stage=current_stage,
            predicted_stage=predicted_stage,
            days_to_next_stage=14.0,
            predicted_yield=100.0,
            quality_score=0.7,
            confidence=0.6,
            fold_integrity=0.7,
            model_type=GrowthPredictionModel.LINEAR
        )
        
        return prediction
        
    def _generate_exponential_prediction(self, plant: PlantData) -> GrowthPrediction:
        """Generate exponential growth prediction."""
        # Simple implementation with placeholder exponential logic
        prediction = self._generate_linear_prediction(plant)
        prediction.model_type = GrowthPredictionModel.EXPONENTIAL
        prediction.days_to_next_stage *= 0.8  # Faster than linear
        prediction.predicted_yield *= 1.2  # Higher yield
        prediction.confidence = 0.65  # Different confidence level
        
        return prediction
    
    def _generate_logistic_prediction(self, plant: PlantData) -> GrowthPrediction:
        """Generate logistic (S-curve) growth prediction."""
        # Simple implementation with placeholder logistic curve logic
        prediction = self._generate_linear_prediction(plant)
        prediction.model_type = GrowthPredictionModel.LOGISTIC
        
        # Adjust based on current growth stage (S-curve has faster middle growth)
        if plant.growth_stage in ["vegetative", "flowering"]:
            prediction.days_to_next_stage *= 0.75  # Faster in middle stages
        else:
            prediction.days_to_next_stage *= 1.1  # Slower at beginning/end
            
        prediction.confidence = 0.75  # Different confidence level
        
        return prediction
    
    def _generate_harmony_weighted_prediction(self, plant: PlantData, 
                                          pattern: Optional[PlantGrowthPattern] = None) -> GrowthPrediction:
        """Generate prediction weighted by harmony states."""
        # Start with fold pattern prediction
        prediction = self._generate_fold_pattern_prediction(plant, pattern)
        prediction.model_type = GrowthPredictionModel.HARMONY_WEIGHTED
        
        # Get harmony analysis
        harmony_result = None
        if self.farm_ufm and hasattr(self.farm_ufm, "analyze_harmony_states"):
            harmony_result = self.farm_ufm.analyze_harmony_states()
            
        if harmony_result and harmony_result.get("success", False):
            harmony_analysis = harmony_result.get("harmony_analysis", {})
            harmony_level = harmony_analysis.get("harmony_level", 0.5)
            primary_state = harmony_analysis.get("primary_state", "NEUTRAL")
            
            # Adjust prediction based on harmony state
            if primary_state == "OPTIMAL_GROWTH":
                prediction.days_to_next_stage *= 0.8  # Faster growth
                prediction.predicted_yield *= 1.2  # Better yield
                prediction.quality_score = min(1.0, prediction.quality_score * 1.2)  # Better quality
            elif primary_state == "STRESS_BALANCED":
                prediction.days_to_next_stage *= 1.1  # Slower growth
                prediction.quality_score *= 0.9  # Lower quality
            elif primary_state == "ENERGY_EFFICIENT":
                prediction.days_to_next_stage *= 1.05  # Slightly slower
                prediction.predicted_yield *= 0.95  # Slightly lower yield
            elif primary_state == "HEALING_ACTIVE":
                prediction.days_to_next_stage *= 1.2  # Much slower growth
                prediction.predicted_yield *= 0.8  # Lower yield
            
            # Adjust confidence based on harmony level
            prediction.confidence = (prediction.confidence + harmony_level) / 2
            
            # Add harmony-specific recommendations
            prediction.recommended_actions.append({
                "action": "maintain_harmony",
                "urgency": "medium",
                "details": f"Current harmony state: {primary_state}. Maintain optimal conditions for best growth."
            })
            
            # Add to metadata
            prediction.metadata["harmony_level"] = harmony_level
            prediction.metadata["primary_state"] = primary_state
        
        return prediction
    
    def _generate_ensemble_prediction(self, plant: PlantData, 
                                   pattern: Optional[PlantGrowthPattern] = None) -> GrowthPrediction:
        """Generate ensemble prediction combining multiple models."""
        # Generate predictions from all models
        fold_prediction = self._generate_fold_pattern_prediction(plant, pattern)
        linear_prediction = self._generate_linear_prediction(plant)
        exp_prediction = self._generate_exponential_prediction(plant)
        logistic_prediction = self._generate_logistic_prediction(plant)
        harmony_prediction = self._generate_harmony_weighted_prediction(plant, pattern)
        
        # Create ensemble prediction
        ensemble = GrowthPrediction(
            plant_id=plant.plant_id,
            current_stage=plant.growth_stage,
            predicted_stage=fold_prediction.predicted_stage,  # Use fold pattern for stage
            days_to_next_stage=0.0,  # Will calculate weighted average
            predicted_yield=0.0,  # Will calculate weighted average
            quality_score=0.0,  # Will calculate weighted average
            confidence=0.0,  # Will calculate weighted average
            fold_integrity=fold_prediction.fold_integrity,  # Use fold pattern value
            model_type=GrowthPredictionModel.ENSEMBLE
        )
        
        # Define weights for each model
        weights = {
            "fold": 0.4,
            "linear": 0.1,
            "exponential": 0.15,
            "logistic": 0.15,
            "harmony": 0.2
        }
        
        # Calculate weighted averages
        ensemble.days_to_next_stage = (
            fold_prediction.days_to_next_stage * weights["fold"] +
            linear_prediction.days_to_next_stage * weights["linear"] +
            exp_prediction.days_to_next_stage * weights["exponential"] +
            logistic_prediction.days_to_next_stage * weights["logistic"] +
            harmony_prediction.days_to_next_stage * weights["harmony"]
        )
        
        ensemble.predicted_yield = (
            fold_prediction.predicted_yield * weights["fold"] +
            linear_prediction.predicted_yield * weights["linear"] +
            exp_prediction.predicted_yield * weights["exponential"] +
            logistic_prediction.predicted_yield * weights["logistic"] +
            harmony_prediction.predicted_yield * weights["harmony"]
        )
        
        ensemble.quality_score = (
            fold_prediction.quality_score * weights["fold"] +
            linear_prediction.quality_score * weights["linear"] +
            exp_prediction.quality_score * weights["exponential"] +
            logistic_prediction.quality_score * weights["logistic"] +
            harmony_prediction.quality_score * weights["harmony"]
        )
        
        # For confidence, we want the highest among all models
        ensemble.confidence = max(
            fold_prediction.confidence * 0.9,  # Slight penalty to prevent overconfidence
            linear_prediction.confidence * 0.85,
            exp_prediction.confidence * 0.85,
            logistic_prediction.confidence * 0.85,
            harmony_prediction.confidence * 0.9
        )
        
        # Combine recommended actions
        seen_actions = set()
        for model_prediction in [fold_prediction, harmony_prediction]:  # Only use main models for actions
            for action in model_prediction.recommended_actions:
                action_key = f"{action['action']}_{action['urgency']}"
                if action_key not in seen_actions:
                    ensemble.recommended_actions.append(action)
                    seen_actions.add(action_key)
        
        # Add metadata showing component models
        ensemble.metadata["component_models"] = ["fold_pattern", "linear", "exponential", 
                                              "logistic", "harmony_weighted"]
        ensemble.metadata["weights"] = weights
        
        return ensemble
    
    async def create_harvest_plan(self, scheduled_date: float, 
                               zone_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a harvest plan for specified zones.
        
        Args:
            scheduled_date: Timestamp for planned harvest
            zone_ids: Specific zones to include (None for all harvest-ready zones)
            
        Returns:
            Created harvest plan
        """
        try:
            # Identify harvestable zones if none specified
            if not zone_ids:
                zone_ids = []
                for zone_id, zone in self.zones.items():
                    if zone.zone_type == "growing":
                        zone_ids.append(zone_id)
            
            # Verify zones exist
            for zone_id in zone_ids:
                if zone_id not in self.zones:
                    return {"success": False, "error": f"Zone not found: {zone_id}"}
            
            # Find plants in these zones that will be ready for harvest
            plant_ids = []
            estimated_yield = 0.0
            
            for plant_id, plant in self.plants.items():
                # Check if plant is in one of the target zones
                if plant.location in zone_ids:
                    # Check current stage or predictions
                    if plant.growth_stage == "harvest":
                        plant_ids.append(plant_id)
                        estimated_yield += 0.5  # Default estimate if no prediction
                    elif plant_id in self.growth_predictions:
                        prediction = self.growth_predictions[plant_id]
                        
                        # Calculate if plant will be ready by scheduled date
                        days_to_harvest = 0
                        current_stage = plant.growth_stage
                        
                        while current_stage != "harvest":
                            if current_stage == prediction.current_stage:
                                days_to_harvest += prediction.days_to_next_stage
                                current_stage = prediction.predicted_stage
                            else:
                                # Use default estimates for other stages
                                if current_stage == "seedling":
                                    days_to_harvest += 14
                                    current_stage = "vegetative"
                                elif current_stage == "vegetative":
                                    days_to_harvest += 21
                                    current_stage = "flowering"
                                elif current_stage == "flowering":
                                    days_to_harvest += 28
                                    current_stage = "fruiting"
                                elif current_stage == "fruiting":
                                    days_to_harvest += 21
                                    current_stage = "harvest"
                                else:
                                    break
                        
                        # Check if ready by scheduled date
                        days_until_scheduled = (scheduled_date - time.time()) / 86400  # Convert to days
                        
                        if days_until_scheduled >= days_to_harvest:
                            plant_ids.append(plant_id)
                            estimated_yield += prediction.predicted_yield / 1000  # Convert g to kg
            
            # Set optimal harvest window (3 days before and after scheduled date)
            optimal_window_start = scheduled_date - (3 * 86400)  # 3 days before
            optimal_window_end = scheduled_date + (3 * 86400)    # 3 days after
            
            # Create harvest plan
            harvest_plan = HarvestPlan(
                farm_id=self.farm_id,
                scheduled_date=scheduled_date,
                zones=zone_ids,
                plant_ids=plant_ids,
                estimated_yield=estimated_yield,
                optimal_window_start=optimal_window_start,
                optimal_window_end=optimal_window_end,
                priority=1,
                notes=["Generated based on growth predictions", 
                       f"Planned for {datetime.fromtimestamp(scheduled_date).strftime('%Y-%m-%d')}"]
            )
            
            # Look for a pattern to associate with plan
            if self.farm_ufm and hasattr(self.farm_ufm, "get_dominant_fold_pattern"):
                dominant_pattern = self.farm_ufm.get_dominant_fold_pattern()
                if dominant_pattern:
                    harvest_plan.fold_pattern_basis = dominant_pattern.pattern_id
            
            # Store harvest plan
            self.harvest_plans.append(harvest_plan)
            
            # Create task for harvest if in AUTONOMOUS mode
            if self.state.mode in [BridgeMode.AUTONOMOUS, BridgeMode.FEDERATED]:
                await self._schedule_harvest_task(harvest_plan)
            
            return {
                "success": True,
                "harvest_plan": harvest_plan.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error creating harvest plan: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _schedule_harvest_task(self, harvest_plan: HarvestPlan) -> None:
        """
        Schedule a harvest task based on the harvest plan.
        
        Args:
            harvest_plan: Harvest plan to schedule
        """
        # Check if care scheduler is available
        if not self.care_scheduler:
            return
            
        # Calculate when to schedule the task
        days_before_harvest = 1  # Schedule 1 day before optimal start
        schedule_time = harvest_plan.optimal_window_start - (days_before_harvest * 86400)
        
        # Don't schedule if it's in the past
        if schedule_time < time.time():
            schedule_time = time.time() + 3600  # Schedule 1 hour from now
        
        # Create parameters
        parameters = {
            "harvest_plan_id": str(hash(harvest_plan)),
            "zones": harvest_plan.zones,
            "plant_ids": harvest_plan.plant_ids,
            "estimated_yield": harvest_plan.estimated_yield,
            "scheduled_date": harvest_plan.scheduled_date,
            "notes": harvest_plan.notes
        }
        
        # Schedule harvest task
        await self.care_scheduler.add_care_task(
            task_type="harvesting",
            priority=TaskPriority.SCHEDULED,
            category="plant_care",
            parameters=parameters,
            schedule_time=schedule_time
        )
    
    async def connect_to_farm(self, farm_id: str, connection_url: str, 
                           api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Connect to another farm system for data sharing and coordination.
        
        Args:
            farm_id: Farm identifier
            connection_url: URL to connect to
            api_key: Optional API key for authentication
            
        Returns:
            Connection result
        """
        try:
            # Check if already connected
            if farm_id in self.connected_farms:
                return {
                    "success": True, 
                    "message": "Already connected to farm",
                    "farm_id": farm_id
                }
                
            # Attempt connection
            headers = {}
            if api_key:
                headers["X-API-Key"] = api_key
                
            # Make test request to verify connection
            try:
                response = requests.get(
                    f"{connection_url}/api/status",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Connection failed: HTTP {response.status_code}"
                    }
                    
                # Parse farm info
                farm_info = response.json()
                
            except requests.RequestException as e:
                return {
                    "success": False,
                    "error": f"Connection failed: {str(e)}"
                }
            
            # Store connection info
            self.connected_farms[farm_id] = {
                "farm_id": farm_id,
                "connection_url": connection_url,
                "api_key": api_key,
                "connected_at": time.time(),
                "farm_info": farm_info
            }
            
            # Create notification message
            message = PulseMeshMessage(
                sender_id=self.bridge_id,
                sender_name=f"Farm Bridge {self.bridge_id[:6]}",
                layer=CommunicationLayer.WIFI_MESH,
                intent=MessageIntent.STATE_BROADCAST,
                priority=TransmissionPriority.NORMAL,
                content=f"Connected to farm: {farm_id}",
                metadata={
                    "farm_id": farm_id,
                    "connection_type": "farm_bridge",
                    "timestamp": time.time()
                }
            )
            
            await self.mesh_node.wifi_layer.send_message(message)
            
            return {
                "success": True,
                "message": "Connected successfully",
                "farm_id": farm_id,
                "farm_info": farm_info
            }
            
        except Exception as e:
            logger.error(f"Error connecting to farm: {e}")
            return {"success": False, "error": str(e)}
    
    async def share_growth_data(self, farm_id: str, plant_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Share growth data with a connected farm.
        
        Args:
            farm_id: Farm identifier to share with
            plant_ids: Specific plants to share (None for all)
            
        Returns:
            Sharing result
        """
        try:
            # Check if farm is connected
            if farm_id not in self.connected_farms:
                return {
                    "success": False,
                    "error": f"Farm not connected: {farm_id}"
                }
                
            farm_connection = self.connected_farms[farm_id]
            
            # Collect growth data
            growth_data = []
            
            for plant_id, prediction in self.growth_predictions.items():
                # Skip if not in requested plants
                if plant_ids and plant_id not in plant_ids:
                    continue
                    
                # Get plant info
                plant = self.plants.get(plant_id)
                if not plant:
                    continue
                    
                # Add to growth data
                growth_data.append({
                    "plant_id": plant_id,
                    "plant_type": plant.type,
                    "growth_stage": plant.growth_stage,
                    "prediction": prediction.to_dict(),
                    "farm_id": self.farm_id,
                    "timestamp": time.time()
                })
            
            # No data to share
            if not growth_data:
                return {
                    "success": True,
                    "message": "No growth data to share",
                    "farm_id": farm_id
                }
                
            # Send data to connected farm
            try:
                headers = {}
                if farm_connection.get("api_key"):
                    headers["X-API-Key"] = farm_connection["api_key"]
                    
                response = requests.post(
                    f"{farm_connection['connection_url']}/api/growth-data",
                    headers=headers,
                    json={
                        "source_farm_id": self.farm_id,
                        "growth_data": growth_data
                    },
                    timeout=10
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"Data sharing failed: HTTP {response.status_code}"
                    }
                    
            except requests.RequestException as e:
                return {
                    "success": False,
                    "error": f"Data sharing failed: {str(e)}"
                }
            
            return {
                "success": True,
                "message": f"Shared {len(growth_data)} growth records with farm {farm_id}",
                "count": len(growth_data)
            }
            
        except Exception as e:
            logger.error(f"Error sharing growth data: {e}")
            return {"success": False, "error": str(e)}
    
    async def analyze_performance(self) -> Dict[str, Any]:
        """
        Analyze farm performance metrics.
        
        Returns:
            Performance analysis
        """
        try:
            # Calculate metrics
            
            # 1. Yield per square meter
            total_yield = 0.0  # kg
            total_growing_area = 0.0  # m²
            
            for zone_id, zone in self.zones.items():
                if zone.zone_type == "growing":
                    # Calculate area
                    width = abs(zone.coordinates[2] - zone.coordinates[0])
                    length = abs(zone.coordinates[3] - zone.coordinates[1])
                    area = width * length
                    total_growing_area += area
                    
                    # Estimate yield from plants in this zone
                    for plant_id in zone.plant_ids:
                        if plant_id in self.growth_predictions:
                            prediction = self.growth_predictions[plant_id]
                            total_yield += prediction.predicted_yield / 1000  # g to kg
            
            # Calculate yield per sqm
            if total_growing_area > 0:
                yield_per_sqm = total_yield / total_growing_area
            else:
                yield_per_sqm = 0.0
                
            # 2. Energy per kg
            if total_yield > 0 and self.resource_usage.energy_usage_kwh > 0:
                energy_per_kg = self.resource_usage.energy_usage_kwh / total_yield
            else:
                energy_per_kg = 0.0
                
            # 3. Water per kg
            if total_yield > 0 and self.resource_usage.water_usage_ml > 0:
                water_per_kg = self.resource_usage.water_usage_ml / 1000 / total_yield  # L/kg
            else:
                water_per_kg = 0.0
                
            # 4. Average growth time
            growth_times = []
            for plant_id, prediction in self.growth_predictions.items():
                if prediction.days_to_next_stage > 0:
                    growth_times.append(prediction.days_to_next_stage)
                    
            average_growth_time = sum(growth_times) / len(growth_times) if growth_times else 0.0
            
            # 5. Pattern coherence
            pattern_coherence_values = []
            
            for pattern_id, pattern in self.pattern_cache.items():
                if "growth_metrics" in pattern.metadata:
                    metrics = pattern.metadata["growth_metrics"]
                    if "pattern_coherence" in metrics:
                        pattern_coherence_values.append(metrics["pattern_coherence"])
                        
            pattern_coherence = sum(pattern_coherence_values) / len(pattern_coherence_values) if pattern_coherence_values else 0.0
            
            # 6. System reliability (based on completed vs. failed tasks)
            total_tasks = len(self.completed_tasks)
            failed_tasks = sum(1 for task in self.completed_tasks if task.get("status") == "FAILED")
            
            if total_tasks > 0:
                reliability = 1.0 - (failed_tasks / total_tasks)
            else:
                reliability = 1.0  # Default to perfect reliability with no data
                
            # 7. Sustainability score (simplified calculation)
            energy_score = 1.0 - min(1.0, energy_per_kg / 10.0) if energy_per_kg > 0 else 0.5
            water_score = 1.0 - min(1.0, water_per_kg / 20.0) if water_per_kg > 0 else 0.5
            
            sustainability_score = (energy_score + water_score) / 2
            
            # Update performance metrics
            self.performance_metrics = FarmPerformanceMetrics(
                farm_id=self.farm_id,
                yield_per_sqm=yield_per_sqm,
                energy_per_kg=energy_per_kg,
                water_per_kg=water_per_kg,
                average_growth_time=average_growth_time,
                pattern_coherence=pattern_coherence,
                system_reliability=reliability,
                sustainability_score=sustainability_score
            )
            
            return {
                "success": True,
                "metrics": self.performance_metrics.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def optimize_farm_layout(self) -> Dict[str, Any]:
        """
        Optimize farm layout based on fold pattern analysis.
        
        Returns:
            Optimization results
        """
        try:
            # Check if UFM is available
            if not self.farm_ufm:
                return {"success": False, "error": "FreightFarmUFM not available"}
                
            # Check if we have spatial model initialized
            if not self.spatial_model_initialized:
                self._initialize_spatial_model()
                
            # Get dominant patterns from UFM
            dominant_patterns = []
            if hasattr(self.farm_ufm, "get_dominant_fold_patterns"):
                dominant_patterns = self.farm_ufm.get_dominant_fold_patterns()
                
            # Get harmony analysis
            harmony_result = None
            if hasattr(self.farm_ufm, "analyze_harmony_states"):
                harmony_result = self.farm_ufm.analyze_harmony_states()
                
            # Generate optimization recommendations
            recommendations = []
            
            # 1. Zone pattern assignments
            if dominant_patterns:
                for i, pattern in enumerate(dominant_patterns[:len(self.zones)]):
                    # Assign patterns to zones based on compatibility
                    zone_ids = sorted(self.zones.keys())
                    if i < len(zone_ids):
                        zone_id = zone_ids[i]
                        zone = self.zones[zone_id]
                        
                        # Check if pattern is different from current
                        if zone.fold_pattern != pattern.fold_pattern:
                            recommendations.append({
                                "type": "zone_pattern",
                                "zone_id": zone_id,
                                "current_pattern": zone.fold_pattern.name if zone.fold_pattern else "None",
                                "recommended_pattern": pattern.fold_pattern.name,
                                "confidence": 0.8,
                                "reason": f"Zone {zone.name} would benefit from {pattern.fold_pattern.name} pattern"
                            })
            
            # 2. Zone type assignments
            zone_type_recommendations = []
            growing_zones = [z for z_id, z in self.zones.items() if z.zone_type == "growing"]
            seedling_zones = [z for z_id, z in self.zones.items() if z.zone_type == "seedling"]
            
            # Check if we need more growing zones
            if len(growing_zones) < 2 and len(seedling_zones) > 1:
                # Find a seedling zone to convert
                for zone_id, zone in self.zones.items():
                    if zone.zone_type == "seedling" and len(seedling_zones) > 1:
                        zone_type_recommendations.append({
                            "type": "zone_type",
                            "zone_id": zone_id,
                            "current_type": "seedling",
                            "recommended_type": "growing",
                            "confidence": 0.7,
                            "reason": "Farm needs more growing space based on pattern distribution"
                        })
                        break
            
            # 3. Plant relocation recommendations
            plant_recommendations = []
            
            for plant_id, plant in self.plants.items():
                if plant.location and plant.location in self.zones:
                    zone = self.zones[plant.location]
                    
                    # Find growth pattern if available
                    matching_pattern = None
                    for action_id, action in self.care_actions.items():
                        if action.plant_id == plant_id and action.source_pattern_id:
                            if action.source_pattern_id in self.pattern_cache:
                                matching_pattern = self.pattern_cache[action.source_pattern_id]
                                break
                    
                    # If we have a pattern mismatch, recommend relocation
                    if matching_pattern and zone.fold_pattern != matching_pattern.fold_pattern:
                        # Find better zone
                        target_zone_id = None
                        for z_id, z in self.zones.items():
                            if z.zone_type == "growing" and z.fold_pattern == matching_pattern.fold_pattern:
                                target_zone_id = z_id
                                break
                                
                        if target_zone_id:
                            plant_recommendations.append({
                                "type": "plant_relocation",
                                "plant_id": plant_id,
                                "current_zone": plant.location,
                                "recommended_zone": target_zone_id,
                                "confidence": 0.75,
                                "reason": f"Plant shows {matching_pattern.fold_pattern.name} pattern, better matching zone {target_zone_id}"
                            })
            
            # Combine all recommendations
            all_recommendations = recommendations + zone_type_recommendations + plant_recommendations
            
            # Apply recommendations if in AUTONOMOUS mode
            if self.state.mode == BridgeMode.AUTONOMOUS and all_recommendations:
                await self._apply_layout_recommendations(all_recommendations)
            
            return {
                "success": True,
                "recommendations": all_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error optimizing farm layout: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def _apply_layout_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """
        Apply layout optimization recommendations.
        
        Args:
            recommendations: List of recommendations to apply
        """
        # Schedule appropriate tasks for recommendations
        for rec in recommendations:
            if rec["type"] == "zone_pattern":
                # Update zone pattern
                zone_id = rec["zone_id"]
                if zone_id in self.zones:
                    new_pattern = FoldPattern[rec["recommended_pattern"]]
                    self.zones[zone_id].fold_pattern = new_pattern
                    
                    logger.info(f"Updated zone {zone_id} pattern to {new_pattern.name}")
                    
            elif rec["type"] == "plant_relocation":
                # Schedule plant relocation task
                if self.care_scheduler:
                    plant_id = rec["plant_id"]
                    target_zone = rec["recommended_zone"]
                    
                    # Create task parameters
                    params = {
                        "plant_id": plant_id,
                        "target_zone": target_zone,
                        "reason": rec["reason"]
                    }
                    
                    # Schedule task
                    await self.care_scheduler.add_care_task(
                        task_type="plant_relocation",
                        priority=TaskPriority.SCHEDULED,
                        category="plant_care",
                        target_id=plant_id,
                        parameters=params
                    )
                    
                    logger.info(f"Scheduled relocation of plant {plant_id} to zone {target_zone}")
    
    async def _apply_environmental_parameters(self, zone_id: str, 
                                          parameters: EnvironmentalParameters) -> bool:
        """
        Apply environmental parameters to physical systems.
        
        Args:
            zone_id: Zone identifier
            parameters: Environmental parameters to apply
            
        Returns:
            Success status
        """
        try:
            # Check if we have ROS bridge
            if not self.ros_bridge:
                return False
                
            # Apply temperature control
            if parameters.temperature > 0:
                await self.ros_bridge.control_actuator(
                    actuator_id=f"temperature_control_{zone_id}",
                    command="set",
                    parameters={"value": parameters.temperature}
                )
                
            # Apply humidity control
            if parameters.humidity > 0:
                await self.ros_bridge.control_actuator(
                    actuator_id=f"humidity_control_{zone_id}",
                    command="set",
                    parameters={"value": parameters.humidity * 100}  # Convert 0-1 to 0-100
                )
                
            # Apply CO2 control
            if parameters.co2_level > 0:
                await self.ros_bridge.control_actuator(
                    actuator_id=f"co2_control_{zone_id}",
                    command="set",
                    parameters={"value": parameters.co2_level}
                )
                
            # Apply lighting controls
            if parameters.light_intensity > 0:
                await self.ros_bridge.control_actuator(
                    actuator_id=f"light_intensity_{zone_id}",
                    command="set",
                    parameters={"value": parameters.light_intensity * 100}  # Convert 0-1 to 0-100
                )
                
                # Apply spectrum if available
                if parameters.light_spectrum:
                    await self.ros_bridge.control_actuator(
                        actuator_id=f"light_spectrum_{zone_id}",
                        command="set",
                        parameters={"spectrum": parameters.light_spectrum}
                    )
                    
            # Apply air circulation
            if parameters.air_circulation > 0:
                await self.ros_bridge.control_actuator(
                    actuator_id=f"air_circulation_{zone_id}",
                    command="set",
                    parameters={"value": parameters.air_circulation * 100}  # Convert 0-1 to 0-100
                )
                
            # Apply nutrient solution parameters
            if parameters.nutrient_ec > 0:
                await self.ros_bridge.control_actuator(
                    actuator_id=f"nutrient_ec_{zone_id}",
                    command="set",
                    parameters={"value": parameters.nutrient_ec}
                )
                
            if parameters.nutrient_ph > 0:
                await self.ros_bridge.control_actuator(
                    actuator_id=f"nutrient_ph_{zone_id}",
                    command="set",
                    parameters={"value": parameters.nutrient_ph}
                )
                
            # Apply day length - this might control lighting schedules
            if parameters.day_length > 0:
                await self.ros_bridge.control_actuator(
                    actuator_id=f"day_length_{zone_id}",
                    command="set",
                    parameters={"hours": parameters.day_length}
                )
                
            return True
            
        except Exception as e:
            logger.error(f"Error applying environmental parameters: {e}")
            return False
    
    async def _run_growth_predictions(self) -> None:
        """Periodically run growth predictions for all plants."""
        # Run every 6 hours by default
        prediction_interval = self.config.get("prediction_interval", 21600)  # 6 hours
        
        while self.is_active:
            try:
                update_count = 0
                current_time = time.time()
                
                # Skip if not enough plants or no UFM
                if len(self.plants) < 1 or not self.farm_ufm:
                    await asyncio.sleep(60)  # Check again in a minute
                    continue
                
                # Process each plant
                for plant_id, plant in self.plants.items():
                    # Skip if recently updated (within last 4 hours)
                    if (plant_id in self.growth_predictions and 
                        current_time - self.growth_predictions[plant_id].creation_time < 14400):
                        continue
                        
                    # Create prediction
                    prediction_result = await self.create_growth_prediction(
                        plant_id, model_type=self.prediction_model)
                        
                    if prediction_result["success"]:
                        update_count += 1
                
                # Update farm metrics after predictions
                if update_count > 0:
                    await self.analyze_performance()
                
                logger.info(f"Updated growth predictions for {update_count} plants")
                
                # Sleep until next update
                await asyncio.sleep(prediction_interval)
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error running growth predictions: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes
    
    async def _run_environment_optimization(self) -> None:
        """Periodically optimize environmental parameters based on fold patterns."""
        # Run every 4 hours by default
        optimization_interval = self.config.get("optimization_interval", 14400)  # 4 hours
        
        while self.is_active:
            try:
                # Skip if not in AUTONOMOUS mode
                if self.state.mode not in [BridgeMode.AUTONOMOUS, BridgeMode.FEDERATED]:
                    await asyncio.sleep(60)  # Check again in a minute
                    continue
                
                # Skip if no zones or no UFM
                if len(self.zones) < 1 or not self.farm_ufm:
                    await asyncio.sleep(60)  # Check again in a minute
                    continue
                
                # Optimize for each zone
                for zone_id, zone in self.zones.items():
                    # Skip non-growing zones
                    if zone.zone_type not in ["growing", "seedling"]:
                        continue
                        
                    # Get current parameters or create defaults
                    if zone_id not in self.environmental_parameters:
                        self.environmental_parameters[zone_id] = EnvironmentalParameters()
                        
                    # Optimize parameters based on fold pattern
                    await self._optimize_zone_parameters(zone_id, zone)
                
                logger.info(f"Completed environmental optimization cycle for {len(self.zones)} zones")
                
                # Sleep until next optimization
                await asyncio.sleep(optimization_interval)
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error running environment optimization: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes
    
    async def _optimize_zone_parameters(self, zone_id: str, zone: SpatialZone) -> None:
        """
        Optimize environmental parameters for a specific zone based on fold pattern.
        
        Args:
            zone_id: Zone identifier
            zone: Zone information
        """
        try:
            # Get current parameters
            params = self.environmental_parameters.get(zone_id, EnvironmentalParameters())
            
            # Use fold pattern to guide optimization
            if zone.fold_pattern:
                # Different patterns have different optimal environmental conditions
                if zone.fold_pattern == FoldPattern.FIBONACCI:
                    # Fibonacci patterns benefit from higher temperature and humidity
                    params.temperature = self._adjust_parameter(params.temperature, 24.0, 0.2)
                    params.humidity = self._adjust_parameter(params.humidity, 0.7, 0.2)
                    params.light_spectrum = {
                        "red": 0.7, "blue": 0.2, "green": 0.1
                    }
                    
                elif zone.fold_pattern == FoldPattern.TESSELLATED:
                    # Tessellated patterns prefer balanced conditions
                    params.temperature = self._adjust_parameter(params.temperature, 22.0, 0.2)
                    params.humidity = self._adjust_parameter(params.humidity, 0.65, 0.2)
                    params.light_spectrum = {
                        "red": 0.5, "blue": 0.4, "green": 0.1
                    }
                    
                elif zone.fold_pattern == FoldPattern.VORTEX:
                    # Vortex patterns benefit from air circulation
                    params.temperature = self._adjust_parameter(params.temperature, 21.0, 0.2)
                    params.humidity = self._adjust_parameter(params.humidity, 0.6, 0.2)
                    params.air_circulation = self._adjust_parameter(params.air_circulation, 0.7, 0.2)
                    
                elif zone.fold_pattern == FoldPattern.MINIMAL:
                    # Minimal patterns prefer lower resource use
                    params.temperature = self._adjust_parameter(params.temperature, 20.0, 0.2)
                    params.light_intensity = self._adjust_parameter(params.light_intensity, 0.6, 0.2)
                    params.co2_level = self._adjust_parameter(params.co2_level, 700.0, 50.0)
            
            # Consider scale level
            if zone.scale_level:
                if zone.scale_level == ScaleLevel.CELLULAR:
                    # Cellular focus needs more precise nutrient balance
                    params.nutrient_ec = self._adjust_parameter(params.nutrient_ec, 1.9, 0.1)
                    params.nutrient_ph = self._adjust_parameter(params.nutrient_ph, 5.8, 0.1)
                    
                elif zone.scale_level == ScaleLevel.ORGANISM:
                    # Organism focus needs balanced growth conditions
                    params.day_length = self._adjust_parameter(params.day_length, 16.0, 1.0)
                    
                elif zone.scale_level == ScaleLevel.ECOSYSTEM:
                    # Ecosystem focus benefits from diverse conditions
                    # No specific changes needed, use defaults
                    pass
            
            # Apply optimization mode adjustments
            if self.optimization_mode == EnvironmentOptimizationMode.ENERGY_SAVING:
                # Reduce energy intensive parameters
                params.temperature = self._adjust_parameter(params.temperature, params.temperature - 1.0, 0.2)
                params.light_intensity = self._adjust_parameter(params.light_intensity, params.light_intensity - 0.1, 0.1)
                params.day_length = self._adjust_parameter(params.day_length, params.day_length - 1.0, 0.5)
                
            elif self.optimization_mode == EnvironmentOptimizationMode.YIELD_MAXIMIZING:
                # Maximize parameters that increase yield
                params.co2_level = self._adjust_parameter(params.co2_level, 1000.0, 50.0)
                params.light_intensity = self._adjust_parameter(params.light_intensity, 0.9, 0.1)
                params.nutrient_ec = self._adjust_parameter(params.nutrient_ec, 2.0, 0.1)
                
            elif self.optimization_mode == EnvironmentOptimizationMode.QUALITY_FOCUSED:
                # Adjust for quality rather than yield
                params.temperature = self._adjust_parameter(params.temperature, params.temperature - 0.5, 0.2)
                params.day_length = self._adjust_parameter(params.day_length, 14.0, 0.5)
                params.light_spectrum = {
                    "red": 0.6, "blue": 0.35, "green": 0.05
                }
                
            elif self.optimization_mode == EnvironmentOptimizationMode.WATER_CONSERVING:
                # Reduce water usage
                params.humidity = self._adjust_parameter(params.humidity, params.humidity - 0.05, 0.05)
                
            # Save new parameters
            self.environmental_parameters[zone_id] = params
            
            # Apply to physical systems
            await self._apply_environmental_parameters(zone_id, params)
            
            # Record in data buffer
            self.environment_data_buffer.append({
                "timestamp": time.time(),
                "zone_id": zone_id,
                "parameters": params.to_dict(),
                "source": "auto_optimization",
                "fold_pattern": zone.fold_pattern.name if zone.fold_pattern else None,
                "scale_level": zone.scale_level.name if zone.scale_level else None,
            })
            
        except Exception as e:
            logger.error(f"Error optimizing zone parameters: {e}")
    
    def _adjust_parameter(self, current: float, target: float, max_change: float) -> float:
        """
        Gradually adjust a parameter towards a target value.
        
        Args:
            current: Current parameter value
            target: Target parameter value
            max_change: Maximum change to apply at once
            
        Returns:
            New parameter value
        """
        if current == target:
            return current
            
        # Determine direction and amount of change
        direction = 1 if target > current else -1
        change = min(abs(target - current), max_change) * direction
        
        # Apply change
        return current + change
    
    async def _track_resource_usage(self) -> None:
        """Periodically track resource usage across the farm."""
        # Run every hour by default
        tracking_interval = self.config.get("resource_tracking_interval", 3600)  # 1 hour
        
        while self.is_active:
            try:
                # Read power consumption if available
                energy_usage = 0.0
                if self.ros_bridge:
                    power_sensor = await self.ros_bridge.read_sensor("power_consumption")
                    if power_sensor:
                        # Assuming power reading is in watts, convert to kWh for the interval
                        energy_usage = power_sensor.value * (tracking_interval / 3600) / 1000
                        self.resource_usage.energy_usage_kwh += energy_usage
                
                # Read water usage if available
                water_usage = 0.0
                if self.ros_bridge:
                    water_sensor = await self.ros_bridge.read_sensor("water_consumption")
                    if water_sensor:
                        # Assuming water reading is in ml
                        water_usage = water_sensor.value
                        self.resource_usage.water_usage_ml += water_usage
                
                # Read nutrient usage if available
                nutrient_usage = 0.0
                if self.ros_bridge:
                    nutrient_sensor = await self.ros_bridge.read_sensor("nutrient_consumption")
                    if nutrient_sensor:
                        # Assuming nutrient reading is in ml
                        nutrient_usage = nutrient_sensor.value
                        self.resource_usage.nutrient_usage_ml += nutrient_usage
                
                # Read CO2 usage if available
                co2_usage = 0.0
                if self.ros_bridge:
                    co2_sensor = await self.ros_bridge.read_sensor("co2_consumption")
                    if co2_sensor:
                        # Assuming CO2 reading is in grams
                        co2_usage = co2_sensor.value
                        self.resource_usage.co2_usage_g += co2_usage
                
                # Log usage for this interval
                logger.info(f"Resource usage: Energy={energy_usage:.2f}kWh, Water={water_usage:.2f}ml, "
                          f"Nutrients={nutrient_usage:.2f}ml, CO2={co2_usage:.2f}g")
                
                # Sleep until next tracking interval
                await asyncio.sleep(tracking_interval)
                
            except asyncio.CancelledError:
                # Task cancelled
                break
                
            except Exception as e:
                logger.error(f"Error tracking resource usage: {e}")
                await asyncio.sleep(300)  # Retry in 5 minutes
    
    async def export_growth_data(self, start_time: Optional[float] = None, 
                              end_time: Optional[float] = None,
                              format: str = "csv") -> Dict[str, Any]:
        """
        Export growth data for analysis.
        
        Args:
            start_time: Start time for data export (None for all data)
            end_time: End time for data export (None for up to current time)
            format: Export format ("csv" or "json")
            
        Returns:
            Exported data
        """
        try:
            # Set default time range if not specified
            if not end_time:
                end_time = time.time()
                
            if not start_time:
                start_time = 0  # All data
            
            # Filter data buffer by time range
            filtered_data = [
                data for data in self.growth_data_buffer
                if start_time <= data["timestamp"] <= end_time
            ]
            
            # Check if we have data
            if not filtered_data:
                return {
                    "success": True,
                    "message": "No growth data found in specified time range",
                    "count": 0
                }
            
            # Export based on format
            if format.lower() == "csv":
                # Convert to CSV
                output = StringIO()
                
                # Create flattened data for CSV
                csv_data = []
                for data in filtered_data:
                    row = {
                        "timestamp": data["timestamp"],
                        "plant_id": data["plant_id"]
                    }
                    
                    # Add prediction data
                    if "prediction" in data:
                        prediction = data["prediction"]
                        row.update({
                            "current_stage": prediction.get("current_stage", ""),
                            "predicted_stage": prediction.get("predicted_stage", ""),
                            "days_to_next_stage": prediction.get("days_to_next_stage", 0),
                            "predicted_yield": prediction.get("predicted_yield", 0),
                            "quality_score": prediction.get("quality_score", 0),
                            "confidence": prediction.get("confidence", 0),
                            "fold_integrity": prediction.get("fold_integrity", 0),
                            "model_type": prediction.get("model_type", "")
                        })
                    
                    # Add source and pattern ID
                    row["source"] = data.get("source", "")
                    row["pattern_id"] = data.get("pattern_id", "")
                    
                    csv_data.append(row)
                
                # Write to CSV
                if csv_data:
                    df = pd.DataFrame(csv_data)
                    csv_string = df.to_csv(index=False)
                    
                    return {
                        "success": True,
                        "format": "csv",
                        "data": csv_string,
                        "count": len(csv_data)
                    }
                else:
                    return {
                        "success": True,
                        "message": "No data to export after processing",
                        "count": 0
                    }
                    
            elif format.lower() == "json":
                # Export as JSON
                return {
                    "success": True,
                    "format": "json",
                    "data": filtered_data,
                    "count": len(filtered_data)
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unsupported export format: {format}"
                }
                
        except Exception as e:
            logger.error(f"Error exporting growth data: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def export_environment_data(self, start_time: Optional[float] = None, 
                                   end_time: Optional[float] = None,
                                   format: str = "csv") -> Dict[str, Any]:
        """
        Export environment data for analysis.
        
        Args:
            start_time: Start time for data export (None for all data)
            end_time: End time for data export (None for up to current time)
            format: Export format ("csv" or "json")
            
        Returns:
            Exported data
        """
        try:
            # Set default time range if not specified
            if not end_time:
                end_time = time.time()
                
            if not start_time:
                start_time = 0  # All data
            
            # Filter data buffer by time range
            filtered_data = [
                data for data in self.environment_data_buffer
                if start_time <= data["timestamp"] <= end_time
            ]
            
            # Check if we have data
            if not filtered_data:
                return {
                    "success": True,
                    "message": "No environment data found in specified time range",
                    "count": 0
                }
            
            # Export based on format
            if format.lower() == "csv":
                # Convert to CSV
                output = StringIO()
                
                # Create flattened data for CSV
                csv_data = []
                for data in filtered_data:
                    row = {
                        "timestamp": data["timestamp"],
                        "zone_id": data["zone_id"],
                        "source": data.get("source", "")
                    }
                    
                    # Add parameters data
                    if "parameters" in data:
                        params = data["parameters"]
                        row.update({
                            "temperature": params.get("temperature", 0),
                            "humidity": params.get("humidity", 0),
                            "co2_level": params.get("co2_level", 0),
                            "light_intensity": params.get("light_intensity", 0),
                            "light_red": params.get("light_spectrum", {}).get("red", 0),
                            "light_blue": params.get("light_spectrum", {}).get("blue", 0),
                            "light_green": params.get("light_spectrum", {}).get("green", 0),
                            "air_circulation": params.get("air_circulation", 0),
                            "nutrient_ec": params.get("nutrient_ec", 0),
                            "nutrient_ph": params.get("nutrient_ph", 0),
                            "day_length": params.get("day_length", 0)
                        })
                    
                    # Add fold pattern and scale level
                    row["fold_pattern"] = data.get("fold_pattern", "")
                    row["scale_level"] = data.get("scale_level", "")
                    
                    csv_data.append(row)
                
                # Write to CSV
                if csv_data:
                    df = pd.DataFrame(csv_data)
                    csv_string = df.to_csv(index=False)
                    
                    return {
                        "success": True,
                        "format": "csv",
                        "data": csv_string,
                        "count": len(csv_data)
                    }
                else:
                    return {
                        "success": True,
                        "message": "No data to export after processing",
                        "count": 0
                    }
                    
            elif format.lower() == "json":
                # Export as JSON
                return {
                    "success": True,
                    "format": "json",
                    "data": filtered_data,
                    "count": len(filtered_data)
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Unsupported export format: {format}"
                }
                
        except Exception as e:
            logger.error(f"Error exporting environment data: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}


# ===== HELPER FUNCTIONS =====

async def create_enhanced_farm_bridge(
    ros_integration: Optional[PulseROSIntegration] = None,
    farm_ufm: Optional[FreightFarmUFM] = None,
    farm_id: Optional[str] = None,
    farm_type: FarmSystemType = FarmSystemType.FREIGHT_FARM,
    mode: BridgeMode = BridgeMode.ADVISORY,
    config: Dict[str, Any] = None,
    enable_enhanced_features: bool = True
) -> PulseFarmBridge:
    """
    Create an enhanced PulseFarmBridge instance.
    
    Args:
        ros_integration: PulseROSIntegration instance
        farm_ufm: FreightFarmUFM instance
        farm_id: Farm identifier if creating new instances
        farm_type: Type of farm system
        mode: Initial bridge operation mode
        config: Configuration options
        enable_enhanced_features: Whether to enable enhanced features
        
    Returns:
        PulseFarmBridge instance
    """
    # Create bridge
    bridge = PulseFarmBridge(
        ros_integration=ros_integration,
        farm_ufm=farm_ufm,
        farm_id=farm_id,
        farm_type=farm_type,
        mode=mode,
        config=config
    )
    
    # Start bridge
    await bridge.start()
    
    # Start enhanced features if requested
    if enable_enhanced_features:
        await bridge.start_enhanced_features()
    
    return bridge


async def create_multi_farm_system(
    farm_configs: List[Dict[str, Any]],
    federation_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a multi-farm system with coordinated bridges.
    
    Args:
        farm_configs: List of farm configurations
        federation_id: Federation identifier (auto-generated if None)
        
    Returns:
        Federation information
    """
    # Create federation ID if not provided
    if not federation_id:
        federation_id = f"farm_federation_{uuid.uuid4().hex[:8]}"
    
    # Create bridges for each farm
    bridges = []
    
    for config in farm_configs:
        # Extract configuration
        farm_id = config.get("farm_id")
        farm_type_name = config.get("farm_type", "FREIGHT_FARM")
        farm_type = FarmSystemType[farm_type_name] if farm_type_name in FarmSystemType.__members__ else FarmSystemType.FREIGHT_FARM
        mode = BridgeMode[config.get("mode", "FEDERATED")] if config.get("mode") in BridgeMode.__members__ else BridgeMode.FEDERATED
        
        # Create bridge
        bridge = await create_enhanced_farm_bridge(
            farm_id=farm_id,
            farm_type=farm_type,
            mode=mode,
            config=config.get("config", {}),
            enable_enhanced_features=config.get("enhanced_features", True)
        )
        
        bridges.append(bridge)
    
    # Register all bridges with federation
    for bridge in bridges:
        await bridge.register_with_federation(federation_id, {
            "farm_ids": [b.farm_id for b in bridges],
            "federation_id": federation_id,
            "creation_time": time.time()
        })
    
    # Connect bridges to each other
    for i, bridge1 in enumerate(bridges):
        for j, bridge2 in enumerate(bridges):
            if i != j:  # Don't connect to self
                # This would use the real API in production, but for demo we're simulating
                # await bridge1.connect_to_farm(bridge2.farm_id, f"http://farm-api/{bridge2.farm_id}")
                bridge1.connected_farms[bridge2.farm_id] = {
                    "farm_id": bridge2.farm_id,
                    "connection_url": f"http://farm-api/{bridge2.farm_id}",
                    "api_key": None,
                    "connected_at": time.time(),
                    "farm_info": {
                        "farm_id": bridge2.farm_id,
                        "farm_type": bridge2.farm_type.name,
                        "mode": bridge2.state.mode.name
                    }
                }
    
    return {
        "success": True,
        "federation_id": federation_id,
        "farm_count": len(bridges),
        "farm_ids": [bridge.farm_id for bridge in bridges]
    }


async def example_enhanced_farm_system():
    """Example usage of the enhanced PulseFarmBridge."""
    # Create bridge
    bridge = await create_enhanced_farm_bridge(
        farm_id="enhanced_demo_farm",
        farm_type=FarmSystemType.FREIGHT_FARM,
        mode=BridgeMode.AUTONOMOUS,
        config={
            "prediction_interval": 3600,  # Update predictions every hour
            "optimization_interval": 7200,  # Optimize environment every 2 hours
            "resource_tracking_interval": 1800  # Track resources every 30 minutes
        }
    )
    
    # Add some plants
    # In a real system, these would be populated from sensors or user input
    # Here we're creating sample plants for demonstration
    for i in range(5):
        plant_data = {
            "name": f"Lettuce Plant {i+1}",
            "type": "Lettuce",
            "location": "zone_growing_left" if i % 2 == 0 else "zone_growing_right",
            "growth_stage": "vegetative" if i < 3 else "seedling",
            "moisture_target": (0.4, 0.7),
            "light_target": (0.6, 0.9),
            "temperature_target": (18.0, 28.0),
            "watering_frequency": 43200  # 12 hours
        }
        
        await bridge.add_plant(plant_data)
    
    # Set up environmental parameters for zones
    for zone_id in bridge.zones:
        if zone_id.startswith("zone_growing"):
            await bridge.set_environmental_parameters(zone_id, {
                "temperature": 22.5,
                "humidity": 0.65,
                "light_intensity": 0.8,
                "co2_level": 850.0
            })
    
    # Run for a demo period
    try:
        print("Enhanced farm system running for demonstration...")
        print("Farm ID:", bridge.farm_id)
        print("Mode:", bridge.state.mode.name)
        print("Type:", bridge.farm_type.name)
        print("Zones:", len(bridge.zones))
        print("Plants:", len(bridge.plants))
        
        # Wait a bit to let the system run
        await asyncio.sleep(10)
        
        # Generate predictions for all plants
        for plant_id in bridge.plants:
            await bridge.create_growth_prediction(plant_id)
            
        # Create a harvest plan
        harvest_date = time.time() + (30 * 86400)  # 30 days from now
        await bridge.create_harvest_plan(harvest_date)
        
        # Get performance metrics
        performance = await bridge.analyze_performance()
        print("Performance metrics:", performance.get("metrics", {}))
        
        # Wait a bit more
        await asyncio.sleep(5)
        
    finally:
        # Stop enhanced features
        await bridge.stop_enhanced_features()
        
        # Stop bridge
        await bridge.stop()
    
    return bridge


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_enhanced_farm_system())