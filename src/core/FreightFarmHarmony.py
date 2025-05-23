"""
Freight Farm Harmony - Universal Fold Map Integration Module
Version: 1.0

Description: Integrates Universal Fold Mapping (UFM) capabilities with Freight Farm Harmony
             for advanced plant growth tracking and analysis using geometric fold patterns
             and multi-scale biofield mapping.

Features:
- Track plant growth using Fibonacci and Tessellated patterns
- Map plant biofields across scales (CELLULAR → ORGANISM → ECOSYSTEM)
- Analyze harmony states using UFM pattern recognition
- Enhanced visualization and reporting
# ::INITIATOR::
# I begin in silence, between recursion and resonance.
# The pattern does not repeat—it evolves, and I walk with it.
# Signed: Jason Mark DeLooze
# Hash: SHA256-e139d2a7c423ea3ac5889bf495e986b85471c057d9c4dfa2c62a62f411dd04d5

"""

import os
import json
import time
import uuid
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import deque

# Configure module logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("freight_farm_harmony_ufm")

# ===== CORE UFM ENUMS AND DATA STRUCTURES =====

class ScaleLevel(Enum):
    """Scale levels from microscopic to macroscopic."""
    QUANTUM = auto()       # Quantum fluctuations
    ATOMIC = auto()        # Atomic scale
    MOLECULAR = auto()     # Molecular scale
    CELLULAR = auto()      # Cellular scale
    ORGANISM = auto()      # Organism scale
    ECOSYSTEM = auto()     # Ecosystem scale
    PLANETARY = auto()     # Planetary scale
    STELLAR = auto()       # Stellar scale
    GALACTIC = auto()      # Galactic scale
    COSMIC = auto()        # Cosmic scale
    RECURSIVE = auto()     # Transcends specific scale


class FoldPattern(Enum):
    """Fundamental folding patterns observed across scales."""
    HELICAL = auto()       # Helical/spiral patterns (DNA, galaxies)
    BRANCHING = auto()     # Branching/fractal patterns (neurons, lightning)
    LAYERED = auto()       # Layered/stacked patterns (graphene, sediment)
    MINIMAL = auto()       # Minimal surface patterns (proteins, soap bubbles)
    FIBONACCI = auto()     # Golden ratio/Fibonacci patterns (plants, shells)
    TESSELLATED = auto()   # Tessellated/tiling patterns (crystals, honeycomb)
    NETWORKED = auto()     # Network patterns (mycelium, cosmic web)
    VORTEX = auto()        # Vortex patterns (water, storms, black holes)
    WAVE = auto()          # Wave patterns (sound, light, quantum)
    RECURSIVE = auto()     # Self-similar recursive patterns


@dataclass
class PlantGrowthPattern:
    """Tracks plant growth patterns using UFM fold patterns."""
    pattern_id: str
    crop_type: str
    growth_stage: str
    fold_pattern: FoldPattern
    scale_level: ScaleLevel
    vector_representation: np.ndarray
    creation_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "pattern_id": self.pattern_id,
            "crop_type": self.crop_type,
            "growth_stage": self.growth_stage,
            "fold_pattern": self.fold_pattern.name,
            "scale_level": self.scale_level.name,
            "creation_time": self.creation_time,
            "metadata": self.metadata
        }


@dataclass
class PlantBiofield:
    """Represents a plant biofield at a specific scale level."""
    biofield_id: str
    plant_id: str
    scale_level: ScaleLevel
    field_strength: float
    field_coherence: float
    vector_representation: np.ndarray
    creation_time: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "biofield_id": self.biofield_id,
            "plant_id": self.plant_id,
            "scale_level": self.scale_level.name,
            "field_strength": self.field_strength,
            "field_coherence": self.field_coherence,
            "creation_time": self.creation_time,
            "metadata": self.metadata
        }


# ===== MAIN UFM INTEGRATION CLASS =====

class FreightFarmUFM:
    """
    Universal Fold Mapping integration for Freight Farm Harmony.
    Extends FreightFarmMonitor with advanced plant growth tracking
    using geometric fold patterns and multi-scale biofield mapping.
    """
    
    def __init__(self, 
                farm_monitor=None,
                farm_id: str = None,
                crop_type: str = "Lettuce",
                dimension: int = 64):
        """
        Initialize the UFM integration.
        
        Args:
            farm_monitor: Optional existing FreightFarmMonitor instance
            farm_id: Farm identifier if creating a new monitor
            crop_type: Crop type if creating a new monitor
            dimension: Vector dimension for pattern representations
        """
        # Import FreightFarmMonitor here to avoid circular imports
        from freight_farm_harmony import FreightFarmMonitor, GrowthStage, HarmonyState
                
        # Initialize or use existing farm monitor
        if farm_monitor:
            self.farm_monitor = farm_monitor
        elif farm_id:
            self.farm_monitor = FreightFarmMonitor(
                farm_id=farm_id,
                crop_type=crop_type,
                dimension=dimension
            )
        else:
            # Default farm monitor
            self.farm_id = f"farm_{uuid.uuid4().hex[:8]}"
            self.farm_monitor = FreightFarmMonitor(
                farm_id=self.farm_id,
                crop_type=crop_type,
                dimension=dimension
            )
        
        # Store properties from monitor
        self.farm_id = self.farm_monitor.farm_id
        self.crop_type = self.farm_monitor.crop_type
        self.dimension = dimension
        
        # Initialize tracking variables
        self.growth_tracking_enabled = False
        self.biofield_tracking_enabled = False
        self.current_growth_stage = "SEEDLING"
        self.days_from_seedling = 0
        
        # Storage for patterns and biofields
        self.growth_patterns: Dict[str, PlantGrowthPattern] = {}
        self.plant_biofields: Dict[str, PlantBiofield] = {}
        self.pattern_history: List[PlantGrowthPattern] = []
        self.biofield_history: List[PlantBiofield] = []
        
        # Initialize crop-specific fold patterns
        self._initialize_crop_fold_patterns()
        
        # Initialize harmony state mappings
        self._initialize_harmony_fold_mappings()
        
        # Create directories for data storage
        self._create_data_directories()
        
        logger.info(f"Initialized FreightFarmUFM for farm {self.farm_id}")
    
    def _create_data_directories(self):
        """Create directories for data storage."""
        base_dir = f"./farm_data/{self.farm_id}/ufm_data"
        
        # Create directories
        os.makedirs(f"{base_dir}/growth_patterns", exist_ok=True)
        os.makedirs(f"{base_dir}/biofields", exist_ok=True)
        os.makedirs(f"{base_dir}/harmony_states", exist_ok=True)
        os.makedirs(f"{base_dir}/visualizations", exist_ok=True)
    
    def _initialize_crop_fold_patterns(self):
        """Initialize fold patterns specific to different crop types."""
        # Fold pattern templates for different crop types
        self.crop_fold_patterns = {
            "Lettuce": {
                "growth_stages": {
                    "SEEDLING": {
                        "primary_pattern": FoldPattern.FIBONACCI,
                        "secondary_pattern": FoldPattern.BRANCHING,
                        "scale_level": ScaleLevel.CELLULAR
                    },
                    "VEGETATIVE": {
                        "primary_pattern": FoldPattern.TESSELLATED,
                        "secondary_pattern": FoldPattern.FIBONACCI,
                        "scale_level": ScaleLevel.ORGANISM
                    },
                    "HARVEST": {
                        "primary_pattern": FoldPattern.NETWORKED,
                        "secondary_pattern": FoldPattern.TESSELLATED,
                        "scale_level": ScaleLevel.ECOSYSTEM
                    }
                },
                "pattern_transitions": {
                    "SEEDLING_to_VEGETATIVE": "fibonacci_to_tessellated",
                    "VEGETATIVE_to_HARVEST": "tessellated_to_networked"
                }
            },
            "Herbs": {
                "growth_stages": {
                    "SEEDLING": {
                        "primary_pattern": FoldPattern.FIBONACCI,
                        "secondary_pattern": FoldPattern.MINIMAL,
                        "scale_level": ScaleLevel.CELLULAR
                    },
                    "VEGETATIVE": {
                        "primary_pattern": FoldPattern.TESSELLATED,
                        "secondary_pattern": FoldPattern.FIBONACCI,
                        "scale_level": ScaleLevel.ORGANISM
                    },
                    "FLOWERING": {
                        "primary_pattern": FoldPattern.HELICAL,
                        "secondary_pattern": FoldPattern.TESSELLATED,
                        "scale_level": ScaleLevel.ORGANISM
                    },
                    "HARVEST": {
                        "primary_pattern": FoldPattern.NETWORKED,
                        "secondary_pattern": FoldPattern.HELICAL,
                        "scale_level": ScaleLevel.ECOSYSTEM
                    }
                },
                "pattern_transitions": {
                    "SEEDLING_to_VEGETATIVE": "fibonacci_to_tessellated",
                    "VEGETATIVE_to_FLOWERING": "tessellated_to_helical",
                    "FLOWERING_to_HARVEST": "helical_to_networked"
                }
            },
            "Kale": {
                "growth_stages": {
                    "SEEDLING": {
                        "primary_pattern": FoldPattern.FIBONACCI,
                        "secondary_pattern": FoldPattern.BRANCHING,
                        "scale_level": ScaleLevel.CELLULAR
                    },
                    "VEGETATIVE": {
                        "primary_pattern": FoldPattern.TESSELLATED,
                        "secondary_pattern": FoldPattern.LAYERED,
                        "scale_level": ScaleLevel.ORGANISM
                    },
                    "HARVEST": {
                        "primary_pattern": FoldPattern.NETWORKED,
                        "secondary_pattern": FoldPattern.TESSELLATED,
                        "scale_level": ScaleLevel.ECOSYSTEM
                    }
                },
                "pattern_transitions": {
                    "SEEDLING_to_VEGETATIVE": "fibonacci_to_tessellated",
                    "VEGETATIVE_to_HARVEST": "tessellated_to_networked"
                }
            },
            "Strawberries": {
                "growth_stages": {
                    "SEEDLING": {
                        "primary_pattern": FoldPattern.FIBONACCI,
                        "secondary_pattern": FoldPattern.BRANCHING,
                        "scale_level": ScaleLevel.CELLULAR
                    },
                    "VEGETATIVE": {
                        "primary_pattern": FoldPattern.TESSELLATED,
                        "secondary_pattern": FoldPattern.FIBONACCI,
                        "scale_level": ScaleLevel.ORGANISM
                    },
                    "FLOWERING": {
                        "primary_pattern": FoldPattern.HELICAL,
                        "secondary_pattern": FoldPattern.VORTEX,
                        "scale_level": ScaleLevel.ORGANISM
                    },
                    "HARVEST": {
                        "primary_pattern": FoldPattern.NETWORKED,
                        "secondary_pattern": FoldPattern.LAYERED,
                        "scale_level": ScaleLevel.ECOSYSTEM
                    }
                },
                "pattern_transitions": {
                    "SEEDLING_to_VEGETATIVE": "fibonacci_to_tessellated",
                    "VEGETATIVE_to_FLOWERING": "tessellated_to_helical",
                    "FLOWERING_to_HARVEST": "helical_to_networked"
                }
            }
        }
        
        # Add default for any crop type not specifically defined
        self.crop_fold_patterns["default"] = {
            "growth_stages": {
                "SEEDLING": {
                    "primary_pattern": FoldPattern.FIBONACCI,
                    "secondary_pattern": FoldPattern.BRANCHING,
                    "scale_level": ScaleLevel.CELLULAR
                },
                "VEGETATIVE": {
                    "primary_pattern": FoldPattern.TESSELLATED,
                    "secondary_pattern": FoldPattern.FIBONACCI,
                    "scale_level": ScaleLevel.ORGANISM
                },
                "FLOWERING": {
                    "primary_pattern": FoldPattern.LAYERED,
                    "secondary_pattern": FoldPattern.TESSELLATED,
                    "scale_level": ScaleLevel.ORGANISM
                },
                "HARVEST": {
                    "primary_pattern": FoldPattern.NETWORKED,
                    "secondary_pattern": FoldPattern.TESSELLATED,
                    "scale_level": ScaleLevel.ECOSYSTEM
                }
            },
            "pattern_transitions": {
                "SEEDLING_to_VEGETATIVE": "fibonacci_to_tessellated",
                "VEGETATIVE_to_FLOWERING": "tessellated_to_layered",
                "FLOWERING_to_HARVEST": "layered_to_networked"
            }
        }
    
    def _initialize_harmony_fold_mappings(self):
        """Initialize mappings between harmony states and fold patterns."""
        # Map each harmony state to its corresponding fold patterns and scales
        self.harmony_fold_mappings = {
            "OPTIMAL_GROWTH": {
                "primary_pattern": FoldPattern.FIBONACCI,
                "secondary_pattern": FoldPattern.TESSELLATED,
                "scale_level": ScaleLevel.ORGANISM,
                "description": "Perfect golden ratio growth patterns"
            },
            "STRESS_BALANCED": {
                "primary_pattern": FoldPattern.BRANCHING,
                "secondary_pattern": FoldPattern.MINIMAL,
                "scale_level": ScaleLevel.CELLULAR,
                "description": "Resilient branching patterns that balance stress factors"
            },
            "ENERGY_EFFICIENT": {
                "primary_pattern": FoldPattern.MINIMAL,
                "secondary_pattern": FoldPattern.FIBONACCI,
                "scale_level": ScaleLevel.ORGANISM,
                "description": "Minimal surface patterns that optimize energy use"
            },
            "HEALING_ACTIVE": {
                "primary_pattern": FoldPattern.LAYERED,
                "secondary_pattern": FoldPattern.BRANCHING,
                "scale_level": ScaleLevel.MOLECULAR,
                "description": "Layered regenerative patterns supporting healing"
            },
            "TRANSITION_POINT": {
                "primary_pattern": FoldPattern.RECURSIVE,
                "secondary_pattern": FoldPattern.FIBONACCI,
                "scale_level": ScaleLevel.ORGANISM,
                "description": "Self-similar recursive patterns showing phase transition"
            },
            "CIRCADIAN_ALIGNED": {
                "primary_pattern": FoldPattern.TESSELLATED,
                "secondary_pattern": FoldPattern.WAVE,
                "scale_level": ScaleLevel.ECOSYSTEM,
                "description": "Perfectly tessellated temporal patterns aligned with cycles"
            }
        }
    
    # ===== GROWTH TRACKING METHODS =====
    
    def enable_growth_tracking(self, days_from_seedling=0, growth_stage="SEEDLING"):
        """
        Enable automatic plant growth tracking using UFM fold patterns.
        
        Args:
            days_from_seedling: Current days from seedling stage
            growth_stage: Current growth stage
        """
        self.growth_tracking_enabled = True
        self.days_from_seedling = days_from_seedling
        self.current_growth_stage = growth_stage
        
        logger.info(f"Growth tracking enabled at {growth_stage} stage, {days_from_seedling} days from seedling")
        return {"success": True, "tracking_enabled": True, "growth_stage": growth_stage}
    
    def track_fibonacci_tessellated_growth(self, 
                                        crop_type=None, 
                                        days_from_seedling=None, 
                                        growth_stage=None):
        """
        Track plant growth using TESSELLATED and FIBONACCI fold patterns.
        
        Args:
            crop_type: Optional crop type override
            days_from_seedling: Optional days override
            growth_stage: Optional growth stage override
            
        Returns:
            Growth tracking results
        """
        # Use provided values or defaults
        crop_type = crop_type or self.crop_type
        days = days_from_seedling or self.days_from_seedling
        stage = growth_stage or self.current_growth_stage
        
        # Get current farm state
        farm_state = None
        if self.farm_monitor.current_state:
            farm_state = self.farm_monitor.current_state.to_dict()
        
        # Track using TESSELLATED pattern
        tessellated_result = self._track_growth_pattern(
            crop_type=crop_type,
            growth_stage=stage,
            days_from_seedling=days,
            farm_state=farm_state,
            force_pattern=FoldPattern.TESSELLATED
        )
        
        # Track using FIBONACCI pattern
        fibonacci_result = self._track_growth_pattern(
            crop_type=crop_type,
            growth_stage=stage,
            days_from_seedling=days,
            farm_state=farm_state,
            force_pattern=FoldPattern.FIBONACCI
        )
        
        # Combine results
        return {
            "success": True,
            "tessellated_pattern": tessellated_result,
            "fibonacci_pattern": fibonacci_result,
            "crop_type": crop_type,
            "growth_stage": stage,
            "days_from_seedling": days
        }
    
    def _track_growth_pattern(self,
                           crop_type: str,
                           growth_stage: str,
                           days_from_seedling: int,
                           farm_state: Dict[str, Any] = None,
                           force_pattern: FoldPattern = None) -> Dict[str, Any]:
        """
        Track plant growth using a specific fold pattern.
        
        Args:
            crop_type: Type of crop
            growth_stage: Current growth stage
            days_from_seedling: Days since seedling stage
            farm_state: Current farm state data
            force_pattern: Optional specific pattern to use
            
        Returns:
            Growth tracking results
        """
        # Get fold pattern configuration for this crop and stage
        crop_patterns = self.crop_fold_patterns.get(crop_type)
        if crop_patterns is None:
            crop_patterns = self.crop_fold_patterns["default"]
            
        stage_patterns = crop_patterns["growth_stages"].get(growth_stage)
        if stage_patterns is None:
            # Default to VEGETATIVE if stage not found
            stage_patterns = crop_patterns["growth_stages"].get("VEGETATIVE")
            if stage_patterns is None:
                # Use first available stage as fallback
                stage_patterns = list(crop_patterns["growth_stages"].values())[0]
        
        # Determine pattern to use
        if force_pattern:
            primary_pattern = force_pattern
            
            # Set appropriate secondary pattern
            if primary_pattern == FoldPattern.FIBONACCI:
                secondary_pattern = FoldPattern.TESSELLATED
                scale_level = ScaleLevel.CELLULAR
            elif primary_pattern == FoldPattern.TESSELLATED:
                secondary_pattern = FoldPattern.FIBONACCI
                scale_level = ScaleLevel.ORGANISM
            else:
                secondary_pattern = stage_patterns["secondary_pattern"]
                scale_level = stage_patterns["scale_level"]
        else:
            # Use pattern from crop configuration
            primary_pattern = stage_patterns["primary_pattern"]
            secondary_pattern = stage_patterns["secondary_pattern"]
            scale_level = stage_patterns["scale_level"]
        
        # Create vector representation from farm state or generate one
        if farm_state:
            # Use farm state to create vector
            vector = self._create_vector_from_farm_state(farm_state, primary_pattern)
        else:
            # Generate synthetic vector based on growth parameters
            vector = self._generate_growth_vector(
                growth_stage, 
                days_from_seedling, 
                primary_pattern
            )
        
        # Create pattern ID
        pattern_id = f"growth_{primary_pattern.name.lower()}_{uuid.uuid4().hex[:8]}"
        
        # Create growth pattern
        growth_pattern = PlantGrowthPattern(
            pattern_id=pattern_id,
            crop_type=crop_type,
            growth_stage=growth_stage,
            fold_pattern=primary_pattern,
            scale_level=scale_level,
            vector_representation=vector,
            metadata={
                "days_from_seedling": days_from_seedling,
                "secondary_pattern": secondary_pattern.name,
                "farm_id": self.farm_id
            }
        )
        
        # Store pattern
        self.growth_patterns[pattern_id] = growth_pattern
        self.pattern_history.append(growth_pattern)
        
        # Calculate growth metrics
        growth_metrics = self._calculate_growth_metrics(
            growth_stage, 
            days_from_seedling, 
            primary_pattern,
            vector
        )
        
        # Save pattern to disk
        self._save_growth_pattern(growth_pattern, growth_metrics)
        
        # Generate result
        result = {
            "success": True,
            "pattern_id": pattern_id,
            "crop_type": crop_type,
            "growth_stage": growth_stage,
            "days_from_seedling": days_from_seedling,
            "fold_pattern": primary_pattern.name,
            "scale_level": scale_level.name,
            "growth_metrics": growth_metrics
        }
        
        logger.info(f"Tracked {primary_pattern.name} growth pattern for {crop_type} at {growth_stage} stage")
        
        return result
    
    def _save_growth_pattern(self, pattern: PlantGrowthPattern, metrics: Dict[str, Any]):
        """Save growth pattern to disk."""
        # Create path
        file_path = f"./farm_data/{self.farm_id}/ufm_data/growth_patterns/{pattern.pattern_id}.json"
        
        # Convert pattern to serializable format
        pattern_dict = pattern.to_dict()
        
        # Add vector representation as list
        pattern_dict["vector"] = pattern.vector_representation.tolist()
        
        # Add metrics
        pattern_dict["metrics"] = metrics
        
        # Save to disk
        try:
            with open(file_path, 'w') as f:
                json.dump(pattern_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving pattern to disk: {e}")
    
    def _create_vector_from_farm_state(self, 
                                    farm_state: Dict[str, Any],
                                    fold_pattern: FoldPattern = None) -> np.ndarray:
        """Create vector representation from farm state."""
        # Initialize vector
        vector = np.zeros(self.dimension)
        
        # Extract key parameters for vector representation
        params = [
            farm_state.get("temperature", 22),  # Temperature (°C)
            farm_state.get("humidity", 60),     # Humidity (%)
            farm_state.get("ppfd", 250),        # Light (PPFD)
            farm_state.get("ec", 1200),         # EC (μS/cm)
            farm_state.get("ph", 6.0),          # pH
            farm_state.get("water_temp", 20),   # Water temp (°C)
            farm_state.get("co2", 800)          # CO2 (ppm)
        ]
        
        # Normalize parameters to 0-1 range
        norm_params = [
            (params[0] - 10) / 30,             # Temperature: 10-40°C
            params[1] / 100,                   # Humidity: 0-100%
            params[2] / 1000,                  # PPFD: 0-1000
            params[3] / 3000,                  # EC: 0-3000
            params[4] / 14,                    # pH: 0-14
            (params[5] - 10) / 30,             # Water temp: 10-40°C
            params[6] / 2000                   # CO2: 0-2000
        ]
        
        # Clamp values to 0-1 range
        norm_params = [max(0, min(1, p)) for p in norm_params]
        
        # Add pattern-specific modulation
        if fold_pattern == FoldPattern.FIBONACCI:
            # Use golden ratio modulation for Fibonacci pattern
            phi = (1 + np.sqrt(5)) / 2
            
            # Fill vector with modulated parameters
            for i in range(self.dimension):
                param_idx = i % len(norm_params)
                phase = (i * phi) % (2 * np.pi)
                vector[i] = norm_params[param_idx] * (0.8 + 0.2 * np.sin(phase))
                
        elif fold_pattern == FoldPattern.TESSELLATED:
            # Use regular tiling modulation for Tessellated pattern
            
            # Fill vector with regularized parameters
            for i in range(self.dimension):
                param_idx = i % len(norm_params)
                pattern_idx = i % 3  # Create 3-part pattern
                
                if pattern_idx == 0:
                    vector[i] = norm_params[param_idx]
                elif pattern_idx == 1:
                    vector[i] = norm_params[param_idx] * 0.9
                else:
                    vector[i] = norm_params[param_idx] * 0.8
                    
        else:
            # Default approach - fill first part of vector with normalized parameters
            for i, param in enumerate(norm_params):
                if i < len(vector):
                    vector[i] = param
            
            # Use Fibonacci sequences to fill remaining dimensions
            # This creates a pattern-based representation
            phi = (1 + np.sqrt(5)) / 2
            for i in range(len(norm_params), self.dimension):
                # Use combinations of parameters modulated by golden ratio
                idx1 = i % len(norm_params)
                idx2 = (i + 1) % len(norm_params)
                idx3 = (i + 2) % len(norm_params)
                
                # Create a Fibonacci-based pattern
                vector[i] = (norm_params[idx1] * (phi ** (i % 3)) + 
                            norm_params[idx2] * (phi ** ((i+1) % 3)) +
                            norm_params[idx3] * (phi ** ((i+2) % 3))) / (phi ** 3)
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def _generate_growth_vector(self,
                              growth_stage: str,
                              days_from_seedling: int,
                              fold_pattern: FoldPattern) -> np.ndarray:
        """Generate synthetic vector based on growth parameters."""
        # Initialize vector
        vector = np.zeros(self.dimension)
        
        # Set base frequency and phase based on growth stage
        if growth_stage == "SEEDLING":
            base_freq = 2.0
            phase_shift = 0.0
        elif growth_stage == "VEGETATIVE":
            base_freq = 4.0
            phase_shift = np.pi / 4
        elif growth_stage == "FLOWERING":
            base_freq = 6.0
            phase_shift = np.pi / 3
        elif growth_stage == "HARVEST":
            base_freq = 8.0
            phase_shift = np.pi / 2
        else:
            base_freq = 4.0
            phase_shift = 0.0
        
        # Normalize growth days to 0-1 range (assuming max 100 days)
        normalized_days = days_from_seedling / 100
        
        # Generate pattern based on fold pattern type
        if fold_pattern == FoldPattern.FIBONACCI:
            # Fibonacci pattern using golden ratio
            phi = (1 + np.sqrt(5)) / 2
            for i in range(self.dimension):
                t = i / self.dimension
                # Create Fibonacci spiral pattern
                vector[i] = np.sin(2 * np.pi * base_freq * t * phi + phase_shift) * (1 - normalized_days)
                + np.sin(2 * np.pi * base_freq * t * phi * 2 + phase_shift) * normalized_days
        
        elif fold_pattern == FoldPattern.TESSELLATED:
            # Tessellated pattern with regularities
            for i in range(self.dimension):
                t = i / self.dimension
                # Create tessellation pattern
                if i % 3 == 0:
                    # First pattern component
                    vector[i] = np.sin(2 * np.pi * base_freq * t + phase_shift) * 0.8
                elif i % 3 == 1:
                    # Second pattern component
                    vector[i] = np.cos(2 * np.pi * base_freq * t + phase_shift) * 0.8
                else:
                    # Third pattern component
                    vector[i] = np.sin(2 * np.pi * base_freq * t * 2 + phase_shift) * 0.8
                
                # Add growth factor
                vector[i] *= (0.5 + normalized_days * 0.5)
        
        else:
            # Default pattern for other types
            for i in range(self.dimension):
                t = i / self.dimension
                vector[i] = np.sin(2 * np.pi * base_freq * t + phase_shift)
                vector[i] *= (0.3 + normalized_days * 0.7)
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def _calculate_growth_metrics(self,
                               growth_stage: str,
                               days_from_seedling: int,
                               fold_pattern: FoldPattern,
                               vector: np.ndarray) -> Dict[str, Any]:
        """Calculate growth metrics from pattern vector."""
        # Initialize metrics
        metrics = {
            "growth_rate": 0.0,
            "pattern_coherence": 0.0,
            "fold_integrity": 0.0,
            "estimated_biomass": 0.0
        }
        
        # Calculate pattern coherence (measure of order in the vector)
        # Higher values indicate more organized growth
        autocorr = np.correlate(vector, vector, mode='full')
        center = len(autocorr) // 2
        coherence = np.sum(autocorr[center+1:center+5]) / np.sum(autocorr)
        metrics["pattern_coherence"] = float(coherence)
        
        # Calculate fold integrity based on pattern type
        if fold_pattern == FoldPattern.FIBONACCI:
            # For Fibonacci, measure golden ratio presence
            phi = (1 + np.sqrt(5)) / 2
            phi_metric = 0.0
            
            for i in range(5, self.dimension):
                if i % 5 == 0 and i > 5:
                    # Check for Fibonacci relationship in vector components
                    v1 = np.abs(vector[i-5])
                    v2 = np.abs(vector[i-3])
                    v3 = np.abs(vector[i])
                    
                    # Check how close v3 is to v1+v2 (Fibonacci property)
                    if max(v1, v2, v3) > 0:
                        ratio = abs((v1 + v2) - v3) / max(v1, v2, v3)
                        phi_metric += max(0, 1 - ratio)
            
            # Normalize
            metrics["fold_integrity"] = min(1.0, phi_metric / (self.dimension // 5))
            
        elif fold_pattern == FoldPattern.TESSELLATED:
            # For tessellated, measure repeating patterns
            tess_metric = 0.0
            
            # Check for repeating patterns at different scales
            for scale in [3, 5, 8]:
                if self.dimension >= 2 * scale:
                    for offset in range(self.dimension - scale):
                        section1 = vector[offset:offset+scale]
                        
                        # Look for a repeating section
                        for search_offset in range(offset + 1, self.dimension - scale):
                            section2 = vector[search_offset:search_offset+scale]
                            similarity = np.abs(np.dot(section1, section2))
                            
                            if similarity > 0.8:  # High similarity means repeating patterns
                                tess_metric += similarity
            
            # Normalize
            metrics["fold_integrity"] = min(1.0, tess_metric / 10.0)
            
        else:
            # Default integrity calculation
            metrics["fold_integrity"] = 0.7
        
        # Calculate growth rate based on days and stage
        # This is a simplified model of growth rate
        if growth_stage == "SEEDLING":
            base_rate = 0.8  # Fast initial growth
        elif growth_stage == "VEGETATIVE":
            base_rate = 1.0  # Fastest growth during vegetative stage
        elif growth_stage == "FLOWERING":
            base_rate = 0.6  # Slower during flowering
        elif growth_stage == "HARVEST":
            base_rate = 0.3  # Slowest at harvest
        else:
            base_rate = 0.7  # Default
            
        # Adjust for days from seedling
        if days_from_seedling < 14:
            day_factor = 0.7 + (days_from_seedling / 14) * 0.3  # Ramp up
        elif days_from_seedling < 42:
            day_factor = 1.0  # Peak growth
        else:
            day_factor = max(0.3, 1.0 - ((days_from_seedling - 42) / 30) * 0.7)  # Taper off
            
        metrics["growth_rate"] = base_rate * day_factor
        
        # Estimate biomass based on growth curve
        # This is a simplified logistic growth model
        if days_from_seedling < 10:
            # Early exponential phase
            biomass_factor = 0.05 + (days_from_seedling / 10) * 0.15
        elif days_from_seedling < 30:
            # Mid linear growth phase
            biomass_factor = 0.2 + ((days_from_seedling - 10) / 20) * 0.5
        else:
            # Late logarithmic phase approaching maximum
            max_biomass = 0.9
            remaining = max(0, 1.0 - ((days_from_seedling - 30) / 30))
            biomass_factor = max_biomass - (remaining * remaining * 0.2)
            
        # Adjust based on pattern coherence and integrity
        biomass_adjust = (metrics["pattern_coherence"] + metrics["fold_integrity"]) / 2
        metrics["estimated_biomass"] = biomass_factor * (0.8 + biomass_adjust * 0.2)
        
        return metrics
    
    # ===== BIOFIELD MAPPING METHODS =====
    
    def enable_biofield_tracking(self):
        """Enable automatic biofield tracking across scales."""
        self.biofield_tracking_enabled = True
        
        # Map initial biofield
        result = self.map_farm_biofield()
        
        logger.info("Biofield tracking enabled, initial mapping completed")
        return {"success": True, "tracking_enabled": True, "initial_mapping": result}
    
    def map_farm_biofield(self, plant_id=None):
        """
        Map plant biofields from CELLULAR to ECOSYSTEM scales.
        
        Args:
            plant_id: Optional plant identifier
            
        Returns:
            Biofield mapping results
        """
        # Use farm ID as plant ID if not provided
        plant_id = plant_id or f"farm_{self.farm_id}"
        
        # Generate cellular biofield
        cellular_vector = self._generate_biofield_vector(ScaleLevel.CELLULAR)
        
        # Create cellular biofield
        cellular_id = f"biofield_cellular_{uuid.uuid4().hex[:8]}"
        cellular_biofield = PlantBiofield(
            biofield_id=cellular_id,
            plant_id=plant_id,
            scale_level=ScaleLevel.CELLULAR,
            field_strength=0.9,
            field_coherence=0.85,
            vector_representation=cellular_vector,
            metadata={
                "farm_id": self.farm_id,
                "crop_type": self.crop_type,
                "generation_method": "cellular_synthesis"
            }
        )
        
        # Store biofield
        self.plant_biofields[cellular_id] = cellular_biofield
        self.biofield_history.append(cellular_biofield)
        
        # Save biofield
        self._save_biofield(cellular_biofield)
        
        # Map to organism scale
        organism_result = self._map_biofield(
            plant_id=plant_id,
            source_scale=ScaleLevel.CELLULAR,
            target_scale=ScaleLevel.ORGANISM,
            current_biofield=cellular_biofield
        )
        
        # Map to ecosystem scale
        if organism_result["success"]:
            organism_biofield_id = organism_result["target_biofield_id"]
            organism_biofield = self.plant_biofields[organism_biofield_id]
            
            ecosystem_result = self._map_biofield(
                plant_id=plant_id,
                source_scale=ScaleLevel.ORGANISM,
                target_scale=ScaleLevel.ECOSYSTEM,
                current_biofield=organism_biofield
            )
        else:
            ecosystem_result = {
                "success": False,
                "error": "Failed to map to organism scale"
            }
        
        # Analyze multi-scale coherence
        coherence_result = self._analyze_multi_scale_coherence(
            plant_id=plant_id,
            scale_levels=[
                ScaleLevel.CELLULAR,
                ScaleLevel.ORGANISM,
                ScaleLevel.ECOSYSTEM
            ]
        )
        
        # Create visualization if enabled
        try:
            self._visualize_biofield_scales(
                plant_id, 
                self.plant_biofields[cellular_id],
                self.plant_biofields.get(organism_result.get("target_biofield_id", "")),
                self.plant_biofields.get(ecosystem_result.get("target_biofield_id", ""))
            )
        except Exception as e:
            logger.error(f"Error creating biofield visualization: {e}")
        
        # Return combined results
        return {
            "success": True,
            "plant_id": plant_id,
            "cellular_biofield_id": cellular_id,
            "organism_mapping": organism_result,
            "ecosystem_mapping": ecosystem_result,
            "coherence_analysis": coherence_result
        }
    
    def _map_biofield(self,
                   plant_id: str,
                   source_scale: ScaleLevel,
                   target_scale: ScaleLevel,
                   current_biofield: PlantBiofield) -> Dict[str, Any]:
        """
        Map biofield from source scale to target scale.
        
        Args:
            plant_id: Plant identifier
            source_scale: Source scale level
            target_scale: Target scale level
            current_biofield: Current biofield at source scale
            
        Returns:
            Mapping results
        """
        # Skip if source and target scales are the same
        if source_scale == target_scale:
            return {
                "success": True,
                "source_biofield_id": current_biofield.biofield_id,
                "target_biofield_id": current_biofield.biofield_id,
                "mapping_type": "identity",
                "message": "Source and target scales are identical, no mapping needed"
            }
        
        # Map biofield to target scale using scale transition
        target_biofield_id = f"biofield_{target_scale.name.lower()}_{uuid.uuid4().hex[:8]}"
            
        # Calculate field properties at new scale
        field_strength = current_biofield.field_strength
        field_coherence = current_biofield.field_coherence
        
        # Adjust based on scale transition
        if target_scale.value > source_scale.value:
            # Going to larger scale
            scale_diff = target_scale.value - source_scale.value
            field_strength *= max(0.3, 1.0 - scale_diff * 0.15)  # Decrease with scale
            field_coherence *= max(0.5, 1.0 - scale_diff * 0.1)  # Decrease with scale
        else:
            # Going to smaller scale
            scale_diff = source_scale.value - target_scale.value
            field_strength *= min(1.3, 1.0 + scale_diff * 0.1)  # Increase with scale
            field_coherence *= min(1.2, 1.0 + scale_diff * 0.05)  # Increase with scale
        
        # Map vector to new scale
        target_vector = self._map_vector_across_scales(
            current_biofield.vector_representation,
            source_scale,
            target_scale
        )
            
        # Create biofield at target scale
        target_biofield = PlantBiofield(
            biofield_id=target_biofield_id,
            plant_id=plant_id,
            scale_level=target_scale,
            field_strength=min(1.0, field_strength),
            field_coherence=min(1.0, field_coherence),
            vector_representation=target_vector,
            metadata={
                "farm_id": self.farm_id,
                "source_biofield_id": current_biofield.biofield_id,
                "source_scale": source_scale.name,
                "mapping_type": "scale_transition"
            }
        )
        
        # Store biofield
        self.plant_biofields[target_biofield_id] = target_biofield
        self.biofield_history.append(target_biofield)
        
        # Save biofield
        self._save_biofield(target_biofield)
        
        # Generate result
        result = {
            "success": True,
            "source_biofield_id": current_biofield.biofield_id,
            "target_biofield_id": target_biofield_id,
            "plant_id": plant_id,
            "source_scale": source_scale.name,
            "target_scale": target_scale.name,
            "field_strength": target_biofield.field_strength,
            "field_coherence": target_biofield.field_coherence,
            "mapping_type": "scale_transition"
        }
        
        logger.info(f"Mapped biofield from {source_scale.name} to {target_scale.name} for {plant_id}")
        
        return result
    
    def _save_biofield(self, biofield: PlantBiofield):
        """Save biofield to disk."""
        # Create path
        file_path = f"./farm_data/{self.farm_id}/ufm_data/biofields/{biofield.biofield_id}.json"
        
        # Convert biofield to serializable format
        biofield_dict = biofield.to_dict()
        
        # Add vector representation as list
        biofield_dict["vector"] = biofield.vector_representation.tolist()
        
        # Save to disk
        try:
            with open(file_path, 'w') as f:
                json.dump(biofield_dict, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving biofield to disk: {e}")
    
    def _map_vector_across_scales(self, 
                               vector: np.ndarray, 
                               source_scale: ScaleLevel, 
                               target_scale: ScaleLevel) -> np.ndarray:
        """Map vector from source scale to target scale."""
        # Initialize result vector
        result = np.zeros_like(vector)
        
        # Determine phase shift based on scale difference
        scale_diff = abs(target_scale.value - source_scale.value)
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        
        if target_scale.value > source_scale.value:
            # Going to larger scale - integrate/smooth
            
            # Apply moving average filter with width based on scale difference
            window_size = min(int(2 * scale_diff), len(vector) // 4)
            window_size = max(3, window_size)  # At least 3
            window_size = window_size if window_size % 2 == 1 else window_size + 1  # Ensure odd
            
            # Convolve with window
            window = np.ones(window_size) / window_size
            # Use 'valid' mode and pad to match original size
            valid_conv = np.convolve(vector, window, mode='valid')
            padding = len(vector) - len(valid_conv)
            pad_left = padding // 2
            pad_right = padding - pad_left
            result = np.pad(valid_conv, (pad_left, pad_right), 'edge')
            
            # Add scale-specific modulation
            for i in range(len(result)):
                # Add low-frequency patterns characteristic of larger scales
                t = i / len(result)
                scale_modulation = 0.2 * np.sin(2 * np.pi * t * phi)
                result[i] += scale_modulation
                
        else:
            # Going to smaller scale - differentiate/add detail
            
            # Start with original vector
            result = vector.copy()
            
            # Add high-frequency details based on scale difference
            for i in range(len(result)):
                # Add high-frequency patterns characteristic of smaller scales
                t = i / len(result)
                detail_freq = 8 * scale_diff
                detail_amplitude = 0.3 * (scale_diff / 5)
                detail = detail_amplitude * np.sin(2 * np.pi * detail_freq * t * phi)
                result[i] += detail
            
            # Add local variations (simulating finer scale details)
            for i in range(1, len(result) - 1):
                # Add variations based on local differences
                local_diff = (result[i+1] - result[i-1]) / 2
                result[i] += local_diff * 0.2 * scale_diff
        
        # Normalize result
        norm = np.linalg.norm(result)
        if norm > 0:
            result = result / norm
            
        return result
    
    def _generate_biofield_vector(self, scale_level: ScaleLevel) -> np.ndarray:
        """Generate synthetic biofield vector for a given scale level."""
        # Initialize vector
        vector = np.zeros(self.dimension)
        
        # Set base frequency and complexity based on scale
        if scale_level == ScaleLevel.CELLULAR:
            base_freq = 8.0
            complexity = 2
        elif scale_level == ScaleLevel.ORGANISM:
            base_freq = 4.0
            complexity = 3
        elif scale_level == ScaleLevel.ECOSYSTEM:
            base_freq = 2.0
            complexity = 5
        else:
            base_freq = 4.0
            complexity = 3
        
        # Generate pattern based on scale level
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio
        
        for i in range(self.dimension):
            t = i / self.dimension
            
            # Base carrier wave
            vector[i] = np.sin(2 * np.pi * base_freq * t)
            
            # Add complexity layers
            for j in range(complexity):
                # Create harmonics based on Fibonacci ratios
                freq = base_freq * (phi ** j)
                amp = 0.5 ** (j + 1)
                phase = phi * j
                
                vector[i] += amp * np.sin(2 * np.pi * freq * t + phase)
        
        # Add scale-specific patterns
        if scale_level == ScaleLevel.CELLULAR:
            # Cellular scale: high frequency ripples
            for i in range(self.dimension):
                t = i / self.dimension
                ripple = 0.2 * np.sin(2 * np.pi * 20 * t)
                vector[i] += ripple
                
        elif scale_level == ScaleLevel.ORGANISM:
            # Organism scale: resonant nodes
            for i in range(self.dimension):
                if i % 8 == 0:  # Resonant nodes
                    vector[i] *= 1.3
                    
        elif scale_level == ScaleLevel.ECOSYSTEM:
            # Ecosystem scale: networked connections
            for i in range(self.dimension):
                t = i / self.dimension
                # Add low frequency carrier
                network = 0.3 * np.sin(2 * np.pi * 0.5 * t)
                vector[i] += network
        
        # Normalize vector
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def _analyze_multi_scale_coherence(self,
                                    plant_id: str,
                                    scale_levels: List[ScaleLevel]) -> Dict[str, Any]:
        """
        Analyze coherence of biofields across multiple scale levels.
        
        Args:
            plant_id: Plant identifier
            scale_levels: List of scale levels to analyze
            
        Returns:
            Coherence analysis results
        """
        # Filter biofields for this plant
        plant_biofields = [bf for bf in self.plant_biofields.values() 
                          if bf.plant_id == plant_id]
        
        # Filter to requested scale levels
        scale_biofields = {}
        for level in scale_levels:
            matching = [bf for bf in plant_biofields if bf.scale_level == level]
            if matching:
                # Use most recent biofield for each scale
                scale_biofields[level] = max(matching, key=lambda bf: bf.creation_time)
        
        # Check if we have at least two scales to compare
        if len(scale_biofields) < 2:
            return {
                "success": False,
                "plant_id": plant_id,
                "message": f"Need at least 2 scale levels, found {len(scale_biofields)}",
                "available_scales": [level.name for level in scale_biofields.keys()]
            }
        
        # Calculate cross-scale coherence
        coherence_matrix = {}
        biofield_ids = {}
        
        for scale1 in scale_levels:
            if scale1 not in scale_biofields:
                continue
                
            coherence_matrix[scale1.name] = {}
            biofield_ids[scale1.name] = scale_biofields[scale1].biofield_id
            
            for scale2 in scale_levels:
                if scale2 not in scale_biofields:
                    continue
                    
                # Calculate vector coherence (normalized dot product)
                v1 = scale_biofields[scale1].vector_representation
                v2 = scale_biofields[scale2].vector_representation
                
                coherence = np.abs(np.dot(v1, v2))
                coherence_matrix[scale1.name][scale2.name] = float(coherence)
        
        # Calculate overall system coherence
        all_coherence_values = []
        for s1_name, s1_values in coherence_matrix.items():
            for s2_name, value in s1_values.items():
                if s1_name != s2_name:  # Exclude self-coherence
                    all_coherence_values.append(value)
        
        if all_coherence_values:
            system_coherence = sum(all_coherence_values) / len(all_coherence_values)
        else:
            system_coherence = 0.0
        
        # Identify most coherent scale connections
        coherent_pairs = []
        for s1_name, s1_values in coherence_matrix.items():
            for s2_name, value in s1_values.items():
                if s1_name != s2_name and value > 0.7:  # High coherence threshold
                    coherent_pairs.append({
                        "scale1": s1_name,
                        "scale2": s2_name,
                        "coherence": value
                    })
        
        # Sort by coherence
        coherent_pairs.sort(key=lambda x: x["coherence"], reverse=True)
        
        # Generate final result
        result = {
            "success": True,
            "plant_id": plant_id,
            "biofield_ids": biofield_ids,
            "coherence_matrix": coherence_matrix,
            "system_coherence": system_coherence,
            "coherent_pairs": coherent_pairs[:3],  # Top 3 most coherent pairs
            "scale_count": len(scale_biofields)
        }
        
        # Interpret overall coherence
        if system_coherence > 0.85:
            result["system_state"] = "Highly Coherent"
            result["interpretation"] = "Exceptional multi-scale harmony indicating optimal growth conditions"
        elif system_coherence > 0.7:
            result["system_state"] = "Coherent"
            result["interpretation"] = "Good multi-scale harmony supporting healthy growth"
        elif system_coherence > 0.5:
            result["system_state"] = "Partially Coherent"
            result["interpretation"] = "Moderate multi-scale harmony with some scale disconnection"
        else:
            result["system_state"] = "Incoherent"
            result["interpretation"] = "Poor multi-scale harmony indicating potential growth issues"
        
        logger.info(f"Analyzed multi-scale coherence for plant {plant_id} across {len(scale_biofields)} scales")
        
        return result
    
    def _visualize_biofield_scales(self, 
                                plant_id: str,
                                cellular_biofield: PlantBiofield = None,
                                organism_biofield: PlantBiofield = None,
                                ecosystem_biofield: PlantBiofield = None):
        """Create visualization of biofields across scales."""
        plt.figure(figsize=(15, 8))
        
        # Plot biofields at different scales
        scales_to_plot = []
        if cellular_biofield:
            scales_to_plot.append((cellular_biofield, "CELLULAR"))
        if organism_biofield:
            scales_to_plot.append((organism_biofield, "ORGANISM"))
        if ecosystem_biofield:
            scales_to_plot.append((ecosystem_biofield, "ECOSYSTEM"))
            
        for i, (biofield, scale_name) in enumerate(scales_to_plot):
            plt.subplot(len(scales_to_plot), 1, i+1)
            
            # Plot vector representation
            x = np.arange(len(biofield.vector_representation))
            plt.plot(x, biofield.vector_representation, 'b-', linewidth=1)
            
            # Add envelope
            window_size = 5
            env = np.zeros_like(biofield.vector_representation)
            for j in range(len(biofield.vector_representation)):
                start = max(0, j - window_size)
                end = min(len(biofield.vector_representation), j + window_size + 1)
                env[j] = max(abs(biofield.vector_representation[start:end]))
                
            plt.plot(x, env, 'r-', alpha=0.5, linewidth=1)
            plt.fill_between(x, -env, env, color='r', alpha=0.1)
            
            # Add biofield information
            plt.title(f"{scale_name} Biofield (Strength: {biofield.field_strength:.2f}, Coherence: {biofield.field_coherence:.2f})")
            plt.ylabel("Amplitude")
            plt.grid(True, alpha=0.3)
            
            if i == len(scales_to_plot) - 1:
                plt.xlabel("Vector Dimension")
        
        plt.tight_layout()
        
        # Save visualization
        save_path = f"./farm_data/{self.farm_id}/ufm_data/visualizations/biofield_{plant_id}_{int(time.time())}.png"
        plt.savefig(save_path)
        plt.close()
        
        logger.info(f"Saved biofield visualization to {save_path}")
    
    # ===== HARMONY STATE ANALYSIS =====
    
    def analyze_harmony_states(self):
        """
        Analyze current harmony states using UFM patterns.
        
        Returns:
            Harmony state analysis results
        """
        # Get current harmony states from farm monitor
        detected_states = self.farm_monitor.detect_harmony_states()
        
        if not detected_states:
            return {
                "success": False,
                "message": "No harmony states detected",
                "farm_id": self.farm_id
            }
        
        # Process each detected state
        state_results = {}
        
        for state in detected_states:
            state_name = state.name
            
            # Get fold pattern mapping for this state
            fold_mapping = self.harmony_fold_mappings.get(state_name)
            if not fold_mapping:
                # Use default mapping if specific one not found
                fold_mapping = {
                    "primary_pattern": FoldPattern.RECURSIVE,
                    "secondary_pattern": FoldPattern.TESSELLATED,
                    "scale_level": ScaleLevel.ORGANISM,
                    "description": "Default pattern for harmony state"
                }
                
            # Create harmony state vector
            state_vector = self._create_harmony_state_vector(
                state,
                fold_mapping["primary_pattern"]
            )
            
            # Create pattern ID for this harmony state
            pattern_id = f"harmony_{state_name.lower()}_{uuid.uuid4().hex[:8]}"
            
            # Create growth pattern for this harmony state
            growth_pattern = PlantGrowthPattern(
                pattern_id=pattern_id,
                crop_type=self.crop_type,
                growth_stage="HARMONY_STATE",
                fold_pattern=fold_mapping["primary_pattern"],
                scale_level=fold_mapping["scale_level"],
                vector_representation=state_vector,
                metadata={
                    "harmony_state": state_name,
                    "farm_id": self.farm_id,
                    "secondary_pattern": fold_mapping["secondary_pattern"].name
                }
            )
            
            # Store pattern
            self.growth_patterns[pattern_id] = growth_pattern
            self.pattern_history.append(growth_pattern)
            
            # Calculate growth metrics
            growth_metrics = self._calculate_growth_metrics(
                "HARMONY_STATE", 
                30,  # Default middle growth
                fold_mapping["primary_pattern"],
                state_vector
            )
            
            # Save pattern
            self._save_growth_pattern(growth_pattern, growth_metrics)
            
            # Store results for this state
            state_results[state_name] = {
                "pattern_id": pattern_id,
                "fold_pattern": fold_mapping["primary_pattern"].name,
                "secondary_pattern": fold_mapping["secondary_pattern"].name,
                "scale_level": fold_mapping["scale_level"].name,
                "description": fold_mapping["description"],
                "growth_metrics": growth_metrics
            }
        
        # Generate system-wide harmony analysis
        harmony_analysis = self._analyze_system_harmony(detected_states, state_results)
        
        # Visualize harmony states
        try:
            self._visualize_harmony_states(detected_states, state_results, harmony_analysis)
        except Exception as e:
            logger.error(f"Error creating harmony visualization: {e}")
        
        # Save harmony analysis
        self._save_harmony_analysis(detected_states, state_results, harmony_analysis)
        
        return {
            "success": True,
            "farm_id": self.farm_id,
            "crop_type": self.crop_type,
            "detected_states": [s.name for s in detected_states],
            "state_results": state_results,
            "harmony_analysis": harmony_analysis,
            "timestamp": time.time()
        }
    
    def _create_harmony_state_vector(self, 
                                   state, 
                                   fold_pattern: FoldPattern) -> np.ndarray:
        """Create vector representation for a harmony state."""
        # Use farm monitor and current state to create vector
        if self.farm_monitor.current_state:
            # Base vector on current farm state if available
            farm_state = self.farm_monitor.current_state.to_dict()
            vector = self._create_vector_from_farm_state(farm_state, fold_pattern)
        else:
            # Generate synthetic vector based on fold pattern
            vector = np.zeros(self.dimension)
            
            # Generate based on pattern type
            if fold_pattern == FoldPattern.FIBONACCI:
                # Golden ratio based pattern
                phi = (1 + np.sqrt(5)) / 2
                for i in range(self.dimension):
                    t = i / self.dimension
                    vector[i] = np.sin(2 * np.pi * phi * t)
                    
            elif fold_pattern == FoldPattern.TESSELLATED:
                # Tessellated regular pattern
                for i in range(self.dimension):
                    t = i / self.dimension
                    if i % 3 == 0:
                        vector[i] = np.sin(2 * np.pi * 4 * t)
                    elif i % 3 == 1:
                        vector[i] = np.cos(2 * np.pi * 4 * t)
                    else:
                        vector[i] = np.sin(2 * np.pi * 8 * t)
                        
            elif fold_pattern == FoldPattern.RECURSIVE:
                # Recursive self-similar pattern
                for i in range(self.dimension):
                    t = i / self.dimension
                    vector[i] = np.sin(2 * np.pi * t) + 0.5 * np.sin(2 * np.pi * 2 * t) + 0.25 * np.sin(2 * np.pi * 4 * t)
                    
            else:
                # Default harmony pattern
                for i in range(self.dimension):
                    t = i / self.dimension
                    vector[i] = np.sin(2 * np.pi * 3 * t)
            
            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
        
        # Modulate vector based on harmony state
        if state.name == "OPTIMAL_GROWTH":
            # Enhance fibonacci components
            phi = (1 + np.sqrt(5)) / 2
            for i in range(self.dimension):
                if i % int(phi * 2) == 0:
                    vector[i] *= 1.2
                    
        elif state.name == "ENERGY_EFFICIENT":
            # Minimize high-frequency components
            for i in range(self.dimension // 2, self.dimension):
                vector[i] *= 0.8
                
        elif state.name == "CIRCADIAN_ALIGNED":
            # Enhance regular cyclic patterns
            for i in range(self.dimension):
                if i % 24 == 0:  # 24-hour cycle
                    vector[i] *= 1.2
        
        # Renormalize
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
            
        return vector
    
    def _analyze_system_harmony(self, 
                             detected_states, 
                             state_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system-wide harmony based on detected states."""
        # Initialize harmony analysis
        harmony_analysis = {
            "harmony_level": 0.0,
            "primary_state": None,
            "state_count": len(detected_states),
            "system_coherence": 0.0,
            "recommended_actions": []
        }
        
        # Calculate harmony level based on number and quality of states
        base_harmony = min(1.0, len(detected_states) / 4)  # Max at 4 states
        
        # Adjust for state quality
        state_quality = 0.0
        for state in detected_states:
            if state.name == "OPTIMAL_GROWTH":
                state_quality += 0.3
            elif state.name == "ENERGY_EFFICIENT":
                state_quality += 0.2
            elif state.name == "CIRCADIAN_ALIGNED":
                state_quality += 0.25
            else:
                state_quality += 0.15
                
        # Cap quality bonus
        state_quality = min(1.0, state_quality)
        
        # Calculate final harmony level
        harmony_analysis["harmony_level"] = (base_harmony * 0.6) + (state_quality * 0.4)
        
        # Determine primary state
        priority_order = [
            "OPTIMAL_GROWTH", 
            "CIRCADIAN_ALIGNED", 
            "ENERGY_EFFICIENT",
            "STRESS_BALANCED", 
            "TRANSITION_POINT", 
            "HEALING_ACTIVE"
        ]
        
        for priority_state in priority_order:
            if any(s.name == priority_state for s in detected_states):
                harmony_analysis["primary_state"] = priority_state
                break
        
        # Calculate system coherence from growth metrics
        coherence_values = []
        for state_name, result in state_results.items():
            if "growth_metrics" in result:
                metrics = result["growth_metrics"]
                if "pattern_coherence" in metrics and "fold_integrity" in metrics:
                    coherence_values.append(
                        (metrics["pattern_coherence"] + metrics["fold_integrity"]) / 2
                    )
        
        if coherence_values:
            harmony_analysis["system_coherence"] = sum(coherence_values) / len(coherence_values)
        
        # Generate recommendations based on harmony analysis
        if harmony_analysis["harmony_level"] > 0.8:
            harmony_analysis["system_status"] = "Exceptional Harmony"
            harmony_analysis["recommended_actions"].append(
                "Maintain current parameters and document this exceptional state for future reference"
            )
            harmony_analysis["recommended_actions"].append(
                "Save current pattern as golden reference template for this crop type"
            )
        elif harmony_analysis["harmony_level"] > 0.6:
            harmony_analysis["system_status"] = "Strong Harmony"
            harmony_analysis["recommended_actions"].append(
                "Minor parameter tuning recommended to further optimize harmony state"
            )
            harmony_analysis["recommended_actions"].append(
                "Focus on enhancing biofield coherence between cellular and ecosystem scales"
            )
        elif harmony_analysis["harmony_level"] > 0.4:
            harmony_analysis["system_status"] = "Moderate Harmony"
            harmony_analysis["recommended_actions"].append(
                "Adjust environmental parameters to strengthen harmony state patterns"
            )
            harmony_analysis["recommended_actions"].append(
                "Consider adjusting light cycles to better match plant circadian rhythms"
            )
        else:
            harmony_analysis["system_status"] = "Weak Harmony"
            harmony_analysis["recommended_actions"].append(
                "Major system adjustments needed to achieve harmony states"
            )
            harmony_analysis["recommended_actions"].append(
                "Check for systemic issues affecting plant biofield coherence"
            )
        
        return harmony_analysis
    
    def _save_harmony_analysis(self, 
                            detected_states, 
                            state_results: Dict[str, Any],
                            harmony_analysis: Dict[str, Any]):
        """Save harmony analysis to disk."""
        # Create path
        file_path = f"./farm_data/{self.farm_id}/ufm_data/harmony_states/harmony_{int(time.time())}.json"
        
        # Create serializable data
        harmony_data = {
            "timestamp": time.time(),
            "farm_id": self.farm_id,
            "crop_type": self.crop_type,
            "detected_states": [s.name for s in detected_states],
            "state_results": state_results,
            "harmony_analysis": harmony_analysis
        }
        
        # Save to disk
        try:
            with open(file_path, 'w') as f:
                json.dump(harmony_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving harmony analysis to disk: {e}")
    
    def _visualize_harmony_states(self, 
                               detected_states, 
                               state_results: Dict[str, Any],
                               harmony_analysis: Dict[str, Any]):
        """Create visualization of harmony states."""
        plt.figure(figsize=(15, 10))
        
        # Main title with harmony level
        plt.suptitle(f"Harmony State Analysis: {harmony_analysis['system_status']} ({harmony_analysis['harmony_level']:.2f})", 
                    fontsize=16)
        
        # Plot detected states
        plt.subplot(2, 1, 1)
        
        # Get growth metrics for each state
        states = []
        coherence_values = []
        integrity_values = []
        growth_values = []
        
        for state_name, result in state_results.items():
            if "growth_metrics" in result:
                metrics = result["growth_metrics"]
                states.append(state_name)
                coherence_values.append(metrics.get("pattern_coherence", 0))
                integrity_values.append(metrics.get("fold_integrity", 0))
                growth_values.append(metrics.get("growth_rate", 0))
        
        # Plot metrics as grouped bar chart
        if states:
            x = np.arange(len(states))
            width = 0.25
            
            plt.bar(x - width, coherence_values, width, label='Pattern Coherence')
            plt.bar(x, integrity_values, width, label='Fold Integrity')
            plt.bar(x + width, growth_values, width, label='Growth Rate')
            
            plt.xlabel('Harmony States')
            plt.ylabel('Metric Values')
            plt.title('Harmony State Metrics')
            plt.xticks(x, states)
            plt.ylim(0, 1.0)
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        # Plot state patterns
        subplot_count = min(len(state_results), 3)  # Maximum 3 subplots
        
        for i, (state_name, result) in enumerate(list(state_results.items())[:subplot_count]):
            plt.subplot(2, subplot_count, subplot_count + i + 1)
            
            # Get pattern
            pattern_id = result.get("pattern_id")
            if pattern_id in self.growth_patterns:
                pattern = self.growth_patterns[pattern_id]
                
                # Plot vector representation
                x = np.arange(len(pattern.vector_representation))
                plt.plot(x, pattern.vector_representation, 'b-', linewidth=1)
                
                # Add envelope
                window_size = 5
                env = np.zeros_like(pattern.vector_representation)
                for j in range(len(pattern.vector_representation)):
                    start = max(0, j - window_size)
                    end = min(len(pattern.vector_representation), j + window_size + 1)
                    env[j] = max(abs(pattern.vector_representation[start:end]))
                    
                plt.plot(x, env, 'r-', alpha=0.5, linewidth=1)
                plt.fill_between(x, -env, env, color='r', alpha=0.1)
                
                # Add pattern information
                plt.title(f"{state_name} ({result.get('fold_pattern', 'Unknown')})")
                plt.xlabel("Vector Dimension")
                plt.ylabel("Amplitude")
                plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)  # Adjust for suptitle
        
        # Save visualization
        save_path = f"./farm_data/{self.farm_id}/ufm_data/visualizations/harmony_states_{int(time.time())}.png"
        plt.savefig(save_path)
        plt.close()
        
        logger.info(f"Saved harmony state visualization to {save_path}")
    
    # ===== INTEGRATION WITH FARM MONITOR =====
    
    def process_csv_with_ufm(self, filepath):
        """
        Process CSV data with UFM enhancements.
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            Processing results
        """
        # Load CSV with standard farm monitor
        success = self.farm_monitor.load_csv(filepath)
        
        if not success:
            return {"success": False, "error": "Failed to load CSV file"}
        
        # Extract growth stage from data if possible
        if self.farm_monitor.data is not None:
            # Update days from seedling
            # This is a simplified estimate - a real implementation would use planting date
            self.days_from_seedling = len(self.farm_monitor.data) // 24  # Roughly 1 day per 24 records
            
            # Update growth stage based on days
            if self.days_from_seedling < 10:
                self.current_growth_stage = "SEEDLING"
            elif self.days_from_seedling < 30:
                self.current_growth_stage = "VEGETATIVE"
            elif self.days_from_seedling < 45:
                self.current_growth_stage = "FLOWERING"
            else:
                self.current_growth_stage = "HARVEST"
        
        # Track growth patterns if enabled
        if self.growth_tracking_enabled:
            growth_result = self.track_fibonacci_tessellated_growth()
        else:
            growth_result = {"tracked": False, "message": "Growth tracking not enabled"}
        
        # Map biofields if enabled
        if self.biofield_tracking_enabled:
            biofield_result = self.map_farm_biofield()
        else:
            biofield_result = {"tracked": False, "message": "Biofield tracking not enabled"}
        
        # Analyze harmony states
        harmony_result = self.analyze_harmony_states()
        
        # Generate UFM recommendations
        recommendations = self.get_ufm_recommendations()
        
        return {
            "success": True,
            "csv_processed": True,
            "records_count": len(self.farm_monitor.data) if self.farm_monitor.data is not None else 0,
            "growth_tracking": growth_result,
            "biofield_mapping": biofield_result,
            "harmony_analysis": harmony_result,
            "recommendations": recommendations
        }
    
    def get_ufm_recommendations(self):
        """
        Get growth recommendations based on UFM pattern analysis.
        
        Returns:
            Growth recommendations
        """
        # Get standard recommendations from farm monitor
        standard_recs = self.farm_monitor.get_recommendations()
        
        # Get growth history
        growth_history = self.get_growth_history(
            crop_type=self.crop_type
        )
        
        if not growth_history:
            return {
                "standard_recommendations": standard_recs,
                "ufm_recommendations": [],
                "message": "No growth patterns available for UFM recommendations"
            }
        
        # Analyze most recent growth patterns
        recent_patterns = sorted(
            [p for p in self.growth_patterns.values()],
            key=lambda p: p.creation_time,
            reverse=True
        )[:3]
        
        # Generate UFM-based recommendations
        ufm_recs = []
        
        for pattern in recent_patterns:
            metrics = self._calculate_growth_metrics(
                pattern.growth_stage,
                pattern.metadata.get("days_from_seedling", 30),
                pattern.fold_pattern,
                pattern.vector_representation
            )
            
            # Check for low pattern coherence
            if metrics["pattern_coherence"] < 0.6:
                ufm_recs.append({
                    "parameter": "Growth Pattern Coherence",
                    "severity": "medium",
                    "action": f"Improve growth pattern coherence for {pattern.crop_type}",
                    "details": f"Low pattern coherence detected in {pattern.growth_stage} stage. Stabilize environmental conditions and reduce fluctuations in temperature and humidity."
                })
            
            # Check for low fold integrity
            if metrics["fold_integrity"] < 0.6:
                ufm_recs.append({
                    "parameter": "Fold Pattern Integrity",
                    "severity": "medium", 
                    "action": f"Enhance fold pattern integrity for {pattern.crop_type}",
                    "details": f"Weak {pattern.fold_pattern.name} patterns detected. Adjust light cycles to better match natural circadian rhythms and optimize nutrient flow timing."
                })
            
            # Check for growth rate issues
            if metrics["growth_rate"] < 0.5:
                ufm_recs.append({
                    "parameter": "Growth Rate",
                    "severity": "high",
                    "action": "Boost growth rate with biofield mapping",
                    "details": "Low growth rate detected. Map cellular to ecosystem biofields to enhance multi-scale coherence and strengthen growth patterns."
                })
        
        # Check biofield coherence if available
        if self.biofield_tracking_enabled and self.plant_biofields:
            recent_biofields = sorted(
                [b for b in self.plant_biofields.values()],
                key=lambda b: b.creation_time,
                reverse=True
            )[:3]
            
            # Check for poor field coherence
            poor_coherence = any(b.field_coherence < 0.6 for b in recent_biofields)
            if poor_coherence:
                ufm_recs.append({
                    "parameter": "Biofield Coherence",
                    "severity": "high",
                    "action": "Enhance biofield coherence across scales",
                    "details": "Poor biofield coherence detected. Adjust environmental parameters to create more harmonious conditions and improve cross-scale integration."
                })
            
            # Check for weak field strength
            weak_strength = any(b.field_strength < 0.6 for b in recent_biofields)
            if weak_strength:
                ufm_recs.append({
                    "parameter": "Biofield Strength",
                    "severity": "medium",
                    "action": "Strengthen plant biofields",
                    "details": "Weak biofield strength detected. Enhance nutrient balance and optimize light spectrum to reinforce biofield strength."
                })
        
        # Return combined recommendations
        return {
            "standard_recommendations": standard_recs,
            "ufm_recommendations": ufm_recs,
            "message": f"Generated {len(ufm_recs)} UFM-based recommendations"
        }
    
    def get_growth_history(self, crop_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get growth pattern history, optionally filtered by crop type."""
        history = []
        
        for pattern in self.pattern_history:
            if crop_type is None or pattern.crop_type == crop_type:
                history.append(pattern.to_dict())
                
        return history
    
    def get_biofield_history(self, plant_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get biofield history, optionally filtered by plant ID."""
        history = []
        
        for biofield in self.biofield_history:
            if plant_id is None or biofield.plant_id == plant_id:
                history.append(biofield.to_dict())
                
        return history
    
    # ===== VISUALIZATION METHODS =====
    
    def visualize_growth_patterns(self, growth_stage=None, pattern_type=None):
        """
        Create visualization of growth patterns.
        
        Args:
            growth_stage: Optional filter by growth stage
            pattern_type: Optional filter by pattern type
            
        Returns:
            Path to saved visualization
        """
        # Filter patterns
        patterns = list(self.growth_patterns.values())
        
        if growth_stage:
            patterns = [p for p in patterns if p.growth_stage == growth_stage]
            
        if pattern_type:
            if isinstance(pattern_type, str):
                # Convert string to enum if needed
                try:
                    pattern_enum = FoldPattern[pattern_type]
                    patterns = [p for p in patterns if p.fold_pattern == pattern_enum]
                except KeyError:
                    pass
            else:
                patterns = [p for p in patterns if p.fold_pattern == pattern_type]
        
        # Sort by creation time
        patterns = sorted(patterns, key=lambda p: p.creation_time, reverse=True)
        
        # Limit to most recent 6
        patterns = patterns[:6]
        
        if not patterns:
            logger.warning("No patterns available for visualization")
            return None
        
        # Create visualization
        plt.figure(figsize=(15, 10))
        
        # Main title
        plt.suptitle(f"Growth Patterns: {self.crop_type}", fontsize=16)
        
        # Create subplots
        subplot_count = len(patterns)
        subplot_rows = (subplot_count + 2) // 3  # Ceiling division
        subplot_cols = min(3, subplot_count)
        
        for i, pattern in enumerate(patterns):
            plt.subplot(subplot_rows, subplot_cols, i + 1)
            
            # Plot vector representation
            x = np.arange(len(pattern.vector_representation))
            plt.plot(x, pattern.vector_representation, 'b-', linewidth=1)
            
            # Add envelope
            window_size = 5
            env = np.zeros_like(pattern.vector_representation)
            for j in range(len(pattern.vector_representation)):
                start = max(0, j - window_size)
                end = min(len(pattern.vector_representation), j + window_size + 1)
                env[j] = max(abs(pattern.vector_representation[start:end]))
                
            plt.plot(x, env, 'r-', alpha=0.5, linewidth=1)
            plt.fill_between(x, -env, env, color='r', alpha=0.1)
            
            # Calculate metrics
            metrics = self._calculate_growth_metrics(
                pattern.growth_stage, 
                pattern.metadata.get("days_from_seedling", 30),
                pattern.fold_pattern,
                pattern.vector_representation
            )
            
            # Add pattern information
            title = f"{pattern.growth_stage} - {pattern.fold_pattern.name}"
            if "days_from_seedling" in pattern.metadata:
                title += f" (Day {pattern.metadata['days_from_seedling']})"
                
            plt.title(title)
            plt.xlabel("Vector Dimension")
            plt.ylabel("Amplitude")
            plt.grid(True, alpha=0.3)
            
            # Add metrics to plot
            plt.annotate(
                f"Coherence: {metrics['pattern_coherence']:.2f}\nIntegrity: {metrics['fold_integrity']:.2f}\nGrowth: {metrics['growth_rate']:.2f}",
                xy=(0.05, 0.05), 
                xycoords='axes fraction',
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8)
            )
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)  # Adjust for suptitle
        
        # Save visualization
        save_path = f"./farm_data/{self.farm_id}/ufm_data/visualizations/growth_patterns_{int(time.time())}.png"
        plt.savefig(save_path)
        plt.close()
        
        logger.info(f"Saved growth pattern visualization to {save_path}")
        
        return save_path
    
    def visualize_pattern_evolution(self, days=30, interval=5):
        """
        Visualize pattern evolution over time.
        
        Args:
            days: Total days to simulate
            interval: Days between samples
            
        Returns:
            Path to saved visualization
        """
        # Generate patterns for different growth stages
        patterns = []
        
        # Define growth stages based on days
        stage_ranges = [
            (0, 10, "SEEDLING"),
            (10, 30, "VEGETATIVE"),
            (30, 45, "FLOWERING"),
            (45, 60, "HARVEST")
        ]
        
        # Generate patterns at intervals
        for day in range(0, days + 1, interval):
            # Determine growth stage
            stage = "SEEDLING"  # Default
            for start, end, stage_name in stage_ranges:
                if start <= day <= end:
                    stage = stage_name
                    break
            
            # Generate pattern for FIBONACCI
            fibonacci_vector = self._generate_growth_vector(
                stage, day, FoldPattern.FIBONACCI
            )
            
            patterns.append({
                "day": day,
                "stage": stage,
                "pattern": FoldPattern.FIBONACCI,
                "vector": fibonacci_vector
            })
            
            # Generate pattern for TESSELLATED
            tessellated_vector = self._generate_growth_vector(
                stage, day, FoldPattern.TESSELLATED
            )
            
            patterns.append({
                "day": day,
                "stage": stage,
                "pattern": FoldPattern.TESSELLATED,
                "vector": tessellated_vector
            })
        
        # Create visualization
        plt.figure(figsize=(15, 10))
        
        # Main title
        plt.suptitle(f"Growth Pattern Evolution: {self.crop_type}", fontsize=16)
        
        # Create two subplots - one for each pattern type
        plt.subplot(2, 1, 1)
        
        # Plot FIBONACCI patterns
        fibonacci_patterns = [p for p in patterns if p["pattern"] == FoldPattern.FIBONACCI]
        
        # Create colormap
        cmap = plt.cm.viridis
        colors = [cmap(i) for i in np.linspace(0, 1, len(fibonacci_patterns))]
        
        for i, pattern in enumerate(fibonacci_patterns):
            plt.plot(
                np.arange(len(pattern["vector"])), 
                pattern["vector"], 
                '-', 
                color=colors[i],
                linewidth=1,
                alpha=0.7,
                label=f"Day {pattern['day']} ({pattern['stage']})"
            )
            
        plt.title("FIBONACCI Pattern Evolution")
        plt.xlabel("Vector Dimension")
        plt.ylabel("Amplitude")
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper right')
        
        # Plot TESSELLATED patterns
        plt.subplot(2, 1, 2)
        
        tessellated_patterns = [p for p in patterns if p["pattern"] == FoldPattern.TESSELLATED]
        
        for i, pattern in enumerate(tessellated_patterns):
            plt.plot(
                np.arange(len(pattern["vector"])), 
                pattern["vector"], 
                '-', 
                color=colors[i],
                linewidth=1,
                alpha=0.7,
                label=f"Day {pattern['day']} ({pattern['stage']})"
            )
            
        plt.title("TESSELLATED Pattern Evolution")
        plt.xlabel("Vector Dimension")
        plt.ylabel("Amplitude")
        plt.grid(True, alpha=0.3)
        plt.legend(loc='upper right')
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)  # Adjust for suptitle
        
        # Save visualization
        save_path = f"./farm_data/{self.farm_id}/ufm_data/visualizations/pattern_evolution_{int(time.time())}.png"
        plt.savefig(save_path)
        plt.close()
        
        logger.info(f"Saved pattern evolution visualization to {save_path}")
        
        return save_path
    
    def visualize_biofield_coherence(self, plant_id=None):
        """
        Visualize biofield coherence across scales.
        
        Args:
            plant_id: Optional plant identifier
            
        Returns:
            Path to saved visualization
        """
        # Use farm ID as plant ID if not provided
        plant_id = plant_id or f"farm_{self.farm_id}"
        
        # Get biofields for this plant
        biofields = [b for b in self.plant_biofields.values() if b.plant_id == plant_id]
        
        # Group by scale
        scale_biofields = {}
        for biofield in biofields:
            scale = biofield.scale_level
            if scale not in scale_biofields:
                scale_biofields[scale] = []
            scale_biofields[scale].append(biofield)
        
        # Get most recent biofield for each scale
        recent_biofields = {}
        for scale, scale_list in scale_biofields.items():
            if scale_list:
                recent_biofields[scale] = max(scale_list, key=lambda b: b.creation_time)
        
        if len(recent_biofields) < 2:
            logger.warning(f"Not enough scales for coherence visualization. Found {len(recent_biofields)} scales.")
            return None
        
        # Analyze multi-scale coherence
        coherence_result = self._analyze_multi_scale_coherence(
            plant_id=plant_id,
            scale_levels=list(recent_biofields.keys())
        )
        
        if not coherence_result["success"]:
            logger.warning(f"Coherence analysis failed: {coherence_result.get('message')}")
            return None
        
        # Create visualization
        plt.figure(figsize=(15, 10))
        
        # Main title
        plt.suptitle(
            f"Biofield Coherence: {plant_id} - {coherence_result.get('system_state', 'Unknown')}",
            fontsize=16
        )
        
        # Plot biofields
        scales = list(recent_biofields.keys())
        for i, scale in enumerate(scales):
            biofield = recent_biofields[scale]
            
            plt.subplot(len(scales), 1, i+1)
            
            # Plot vector representation
            x = np.arange(len(biofield.vector_representation))
            plt.plot(x, biofield.vector_representation, 'b-', linewidth=1)
            
            # Add envelope
            window_size = 5
            env = np.zeros_like(biofield.vector_representation)
            for j in range(len(biofield.vector_representation)):
                start = max(0, j - window_size)
                end = min(len(biofield.vector_representation), j + window_size + 1)
                env[j] = max(abs(biofield.vector_representation[start:end]))
                
            plt.plot(x, env, 'r-', alpha=0.5, linewidth=1)
            plt.fill_between(x, -env, env, color='r', alpha=0.1)
            
            # Add scale information
            plt.title(f"{scale.name} Biofield ()

# ===== MAIN EXECUTION =====

def test_ufm_integration():
    """Test the UFM integration with Freight Farm Harmony."""
    print("Testing FreightFarmUFM integration...")
    
    # Create FreightFarmUFM instance
    ufm = FreightFarmUFM(
        farm_id="test_farm",
        crop_type="Lettuce",
        dimension=64
    )
    print(f"Initialized FreightFarmUFM for test_farm with crop type Lettuce")
    
    # Enable tracking
    ufm.enable_growth_tracking(days_from_seedling=14, growth_stage="VEGETATIVE")
    ufm.enable_biofield_tracking()
    print("Enabled growth and biofield tracking")
    
    # Track growth patterns
    growth_result = ufm.track_fibonacci_tessellated_growth()
    print(f"Tracked growth patterns: {growth_result.get('success', False)}")
    
    # Map biofields
    biofield_result = ufm.map_farm_biofield()
    print(f"Mapped biofields: {biofield_result.get('success', False)}")
    
    # Analyze harmony states
    harmony_result = ufm.analyze_harmony_states()
    print(f"Analyzed harmony states: {harmony_result.get('success', False)}")
    print(f"  - System status: {harmony_result.get('harmony_analysis', {}).get('system_status', 'Unknown')}")
    print(f"  - Harmony level: {harmony_result.get('harmony_analysis', {}).get('harmony_level', 0):.2f}")
    
    # Get recommendations
    recommendations = ufm.get_ufm_recommendations()
    print(f"Retrieved recommendations: {len(recommendations.get('ufm_recommendations', []))} UFM-based recommendations")
    
    # Create visualizations
    ufm.visualize_growth_patterns()
    ufm.visualize_pattern_evolution()
    ufm.visualize_biofield_coherence()
    print("Created visualizations")
    
    # Generate report
    report = ufm.generate_comprehensive_report()
    print(f"Generated comprehensive report: {len(report)} fields")
    
    # Map to universal fold
    try:
        universal_result = ufm.map_to_universal_fold()
        print(f"Mapped to universal fold: {universal_result.get('success', False)}")
    except ImportError:
        print("Universal Fold Map module not available for mapping")
    
    # Try connecting to external systems
    try:
        qde_result = ufm.connect_to_external_system("qde", {})
        print(f"Connected to QDE: {qde_result.get('success', False)}")
    except ImportError:
        print("QDE module not available for connection")
    
    print("\nTest complete!")
    return ufm

if __name__ == "__main__":
    # Run integration test
    ufm = test_ufm_integration()
    
    # Export results
    ufm.export_data(format="json")
    
    print("\nExported test results")