# modules/abil/plant_consciousness_interface_v3.py
"""
OSCE ABIL v3 - Autonomous Biological Intelligence Layer
Production-ready bioelectric monitoring with HAL integration

Key v3 Enhancements:
- HAL-managed bioelectric sensor arrays
- Distributed signal processing
- Hardware health-aware interpretation
- Multi-zone democratic coordination
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from scipy import signal
from collections import deque

from osce.core.base import OSCEModule
from osce.ml.signal_processing import BioSignalProcessor
from osce.utils.logging import get_logger
from osce_hal_enhanced import (
    HardwareManager, HardwareAdapter, SensorInfo,
    HardwareHealth, PinMode, NetworkHardwareAdapter
)

logger = get_logger(__name__)

class SignalType(Enum):
    """Types of bioelectric signals"""
    ACTION_POTENTIAL = "action_potential"
    VARIATION_POTENTIAL = "variation_potential"
    SYSTEM_POTENTIAL = "system_potential"
    LOCAL_ELECTRIC_POTENTIAL = "local_electric_potential"
    WOUND_SIGNAL = "wound_signal"
    NETWORK_OSCILLATION = "network_oscillation"  # New v3

class PlantState(Enum):
    """Interpreted plant states"""
    OPTIMAL = "optimal"
    WATER_STRESS = "water_stress"
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"
    LIGHT_STRESS = "light_stress"
    TEMPERATURE_STRESS = "temperature_stress"
    PATHOGEN_ATTACK = "pathogen_attack"
    MECHANICAL_STRESS = "mechanical_stress"
    COMMUNICATING = "communicating"  # New v3

@dataclass
class BioelectricReadingV3:
    """Enhanced bioelectric measurement with hardware metadata"""
    timestamp: datetime
    electrode_id: str
    voltage_mv: float
    frequency_hz: float
    signal_type: Optional[SignalType] = None
    confidence: float = 0.0
    hardware_health: float = 1.0
    noise_level: float = 0.0
    adapter_latency_ms: float = 0.0

@dataclass
class ElectrodeArray:
    """HAL-managed electrode array"""
    array_id: str
    plant_id: str
    adapter_name: str
    electrodes: List[Dict[str, Any]]
    sampling_rate_hz: int
    buffer_size: int
    last_calibration: datetime
    signal_quality: float = 1.0

@dataclass
class PlantVoteV3:
    """Enhanced plant vote with signal strength"""
    plant_id: str
    temperature_c: float
    humidity_percent: float
    light_ppfd: float
    co2_ppm: float
    vote_weight: float
    signal_strength: float  # New - based on bioelectric clarity
    consensus_confidence: float  # New - how sure the plant is
    reasoning: str

class PlantConsciousnessInterfaceV3(OSCEModule):
    """
    v3: Production bioelectric monitoring with HAL integration
    
    New Features:
    - Multi-adapter electrode arrays
    - Hardware-accelerated signal processing
    - Distributed plant democracy
    - Real-time network visualization
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Configuration
        self.enabled = config.get('bioelectric_monitoring', False)
        self.sampling_rate = config.get('sampling_rate_hz', 1000)
        self.min_electrodes_per_plant = config.get('min_electrodes_per_plant', 4)
        
        # HAL integration
        self.hw_manager: Optional[HardwareManager] = None
        self.electrode_arrays: Dict[str, ElectrodeArray] = {}
        self.signal_adapters = {}  # Adapters with DSP capabilities
        
        # Signal processing
        self.signal_processor = BioSignalProcessor()
        self.signal_buffers: Dict[str, deque] = {}
        self.buffer_duration = config.get('buffer_seconds', 60)
        
        # Distributed processing
        self.processing_nodes = {}  # Network nodes for distributed processing
        self.signal_aggregator = SignalAggregator()
        
        # Plant models
        self.plant_models = {}
        self.baseline_signals = {}
        self.model_confidence = {}
        
        # Democracy settings
        self.democracy_enabled = config.get('plant_democracy', False)
        self.voting_interval = config.get('voting_interval_hours', 6)
        self.min_voters = config.get('min_voters_for_consensus', 5)
        self.signal_threshold = config.get('min_signal_strength', 0.7)
        
        # Multi-zone coordination
        self.zone_coordinators = {}
        self.cross_zone_communication = config.get('enable_cross_zone', True)
        
        # Performance monitoring
        self.processing_metrics = []
        self.interpretation_cache = {}
        
        # Communication history
        self.communication_log = deque(maxlen=10000)  # Larger for v3
        self.plant_states = {}
        self.network_state = NetworkState()
        
    async def initialize(self):
        """Initialize with HAL electrode discovery"""
        if not self.enabled:
            logger.info("Plant consciousness interface disabled")
            return
            
        # Get hardware manager
        self.hw_manager = self.env.hal
        
        if not self.hw_manager:
            logger.error("HAL required for bioelectric monitoring")
            return
            
        # Discover bioelectric sensors
        await self._discover_electrode_arrays()
        
        # Discover signal processing hardware
        await self._discover_signal_processors()
        
        # Setup distributed processing if available
        await self._setup_distributed_processing()
        
        # Register for hardware events
        self.hw_manager.on_event('adapter_added', self._handle_new_hardware)
        self.hw_manager.on_event('adapter_failed', self._handle_hardware_failure)
        
        # Load signal interpretation models
        await self._load_models()
        
        # Initialize zone coordinators
        await self._initialize_zone_coordinators()
        
        # Start monitoring
        asyncio.create_task(self._signal_monitoring_loop_v3())
        
        # Start interpretation
        asyncio.create_task(self._interpretation_loop_v3())
        
        # Start plant democracy if enabled
        if self.democracy_enabled:
            asyncio.create_task(self._democracy_loop_v3())
            
        # Start network state monitoring
        asyncio.create_task(self._network_monitoring_loop())
        
        logger.info(f"Plant consciousness v3 initialized with {len(self.electrode_arrays)} arrays")
        
    async def _discover_electrode_arrays(self):
        """Discover bioelectric sensors through HAL"""
        all_sensors = await self.hw_manager.get_all_sensors()
        
        # Electrode sensor types
        electrode_types = [
            'bioelectric', 'electrode', 'eeg', 'ecg', 
            'voltage_probe', 'differential_amplifier'
        ]
        
        # Group electrodes by plant
        plant_electrodes = {}
        
        for adapter_name, sensors in all_sensors.items():
            adapter = self.hw_manager.get_adapter(adapter_name)
            
            if not adapter:
                continue
                
            for sensor in sensors:
                # Check if it's an electrode
                if any(e_type in sensor.sensor_type.lower() for e_type in electrode_types):
                    # Extract plant ID from sensor name
                    plant_id = self._extract_plant_id_from_sensor(sensor)
                    
                    if plant_id not in plant_electrodes:
                        plant_electrodes[plant_id] = []
                        
                    plant_electrodes[plant_id].append({
                        'sensor': sensor,
                        'adapter_name': adapter_name,
                        'adapter': adapter,
                        'position': self._get_electrode_position(sensor)
                    })
                    
        # Create electrode arrays
        for plant_id, electrodes in plant_electrodes.items():
            if len(electrodes) >= self.min_electrodes_per_plant:
                array = ElectrodeArray(
                    array_id=f"array_{plant_id}",
                    plant_id=plant_id,
                    adapter_name=electrodes[0]['adapter_name'],  # Primary adapter
                    electrodes=electrodes,
                    sampling_rate_hz=self.sampling_rate,
                    buffer_size=self.sampling_rate * self.buffer_duration,
                    last_calibration=datetime.utcnow()
                )
                
                self.electrode_arrays[array.array_id] = array
                
                # Initialize signal buffer
                self.signal_buffers[plant_id] = deque(
                    maxlen=array.buffer_size
                )
                
                logger.info(f"Created electrode array for {plant_id} with {len(electrodes)} electrodes")
                
    async def _discover_signal_processors(self):
        """Find adapters with signal processing capabilities"""
        dsp_features = {'dsp', 'fft', 'signal_processing', 'neural_engine'}
        
        for adapter_name, adapter in self.hw_manager.adapters.items():
            capabilities = adapter.get_capabilities()
            
            if capabilities.features & dsp_features:
                self.signal_adapters[adapter_name] = {
                    'adapter': adapter,
                    'features': list(capabilities.features & dsp_features),
                    'performance': await self._benchmark_dsp_performance(adapter)
                }
                
                logger.info(f"Found DSP adapter: {adapter_name}")
                
    async def _benchmark_dsp_performance(self, adapter: HardwareAdapter) -> Dict[str, float]:
        """Benchmark signal processing performance"""
        performance = {}
        
        # Test data - 1 second of signal at 1kHz
        test_signal = np.random.randn(1000)
        
        # FFT benchmark
        try:
            start = datetime.utcnow()
            
            if hasattr(adapter, 'dsp_fft'):
                await adapter.secure_operation(
                    adapter.dsp_fft,
                    test_signal
                )
            else:
                np.fft.fft(test_signal)
                
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            performance['fft_1k_ms'] = elapsed
            
        except:
            performance['fft_1k_ms'] = float('inf')
            
        return performance
        
    async def _setup_distributed_processing(self):
        """Setup distributed signal processing across network nodes"""
        # Find network-connected processing nodes
        for adapter_name, adapter in self.hw_manager.adapters.items():
            if isinstance(adapter, NetworkHardwareAdapter):
                # Check if it supports signal processing
                try:
                    capabilities = await adapter._api_call('GET', '/capabilities')
                    
                    if capabilities and 'signal_processing' in capabilities.get('features', []):
                        self.processing_nodes[adapter_name] = {
                            'adapter': adapter,
                            'capabilities': capabilities,
                            'load': 0.0
                        }
                        
                        logger.info(f"Added distributed processing node: {adapter_name}")
                        
                except:
                    pass
                    
    async def _signal_monitoring_loop_v3(self):
        """Enhanced monitoring with hardware coordination"""
        sample_interval = 1.0 / self.sampling_rate
        
        while True:
            try:
                start_time = datetime.utcnow()
                
                # Collect readings from all arrays in parallel
                reading_tasks = []
                
                for array_id, array in self.electrode_arrays.items():
                    task = self._collect_array_readings_v3(array)
                    reading_tasks.append(task)
                    
                # Gather all readings
                all_readings = await asyncio.gather(*reading_tasks, return_exceptions=True)
                
                # Process readings
                for readings in all_readings:
                    if isinstance(readings, list):
                        # Buffer signals by plant
                        for reading in readings:
                            plant_id = self._get_plant_from_electrode(reading.electrode_id)
                            if plant_id:
                                self.signal_buffers[plant_id].append(reading)
                                
                        # Detect events
                        events = await self._detect_signal_events_v3(readings)
                        
                        for event in events:
                            await self._handle_signal_event_v3(event)
                            
                # Calculate actual interval
                elapsed = (datetime.utcnow() - start_time).total_seconds()
                sleep_time = max(0, sample_interval - elapsed)
                
                # Record performance
                self.processing_metrics.append({
                    'timestamp': start_time,
                    'readings_collected': sum(len(r) for r in all_readings if isinstance(r, list)),
                    'processing_time_ms': elapsed * 1000,
                    'efficiency': 1.0 - (elapsed / sample_interval)
                })
                
                await asyncio.sleep(sleep_time)
                
            except Exception as e:
                logger.error(f"Signal monitoring error: {e}")
                await asyncio.sleep(sample_interval)
                
    async def _collect_array_readings_v3(self, array: ElectrodeArray) -> List[BioelectricReadingV3]:
        """Collect readings from electrode array with quality metrics"""
        readings = []
        
        # Check adapter health
        adapter = self.hw_manager.get_adapter(array.adapter_name)
        
        if not adapter:
            logger.error(f"Adapter not found for array {array.array_id}")
            return readings
            
        health = await adapter.health_check()
        
        if health not in [HardwareHealth.EXCELLENT, HardwareHealth.GOOD]:
            logger.warning(f"Adapter health degraded for {array.array_id}: {health}")
            
        # Collect from each electrode
        for electrode_info in array.electrodes:
            try:
                start = datetime.utcnow()
                
                # Read voltage through HAL
                voltage = await adapter.secure_operation(
                    self._read_bioelectric_voltage,
                    electrode_info['sensor']
                )
                
                latency = (datetime.utcnow() - start).total_seconds() * 1000
                
                # Estimate frequency from recent buffer
                frequency = 0.0
                if array.plant_id in self.signal_buffers:
                    recent = list(self.signal_buffers[array.plant_id])[-100:]
                    if len(recent) > 10:
                        frequency = self._estimate_dominant_frequency(recent)
                        
                # Calculate noise level
                noise = await self._estimate_noise_level(adapter, electrode_info['sensor'])
                
                reading = BioelectricReadingV3(
                    timestamp=datetime.utcnow(),
                    electrode_id=electrode_info['sensor'].name,
                    voltage_mv=voltage * 1000,  # Convert to mV
                    frequency_hz=frequency,
                    hardware_health=adapter.health_score,
                    noise_level=noise,
                    adapter_latency_ms=latency
                )
                
                readings.append(reading)
                
            except Exception as e:
                logger.error(f"Failed to read electrode {electrode_info['sensor'].name}: {e}")
                
        # Update array signal quality
        if readings:
            signal_strengths = [1.0 - r.noise_level for r in readings]
            array.signal_quality = np.mean(signal_strengths)
            
        return readings
        
    async def _read_bioelectric_voltage(self, sensor: SensorInfo) -> float:
        """Read voltage from bioelectric sensor"""
        # This would interface with actual sensor
        # For now, simulate bioelectric signal
        
        # Base signal (resting potential)
        base_voltage = -0.07  # -70mV resting potential
        
        # Add realistic bioelectric activity
        # Action potential spikes
        if np.random.random() < 0.01:  # 1% chance of action potential
            return base_voltage + 0.1 * np.random.random()  # Depolarization
            
        # Slow variations
        slow_wave = 0.01 * np.sin(2 * np.pi * 0.1 * datetime.utcnow().timestamp())
        
        # Noise
        noise = 0.001 * np.random.randn()
        
        return base_voltage + slow_wave + noise
        
    async def _estimate_noise_level(self, adapter: HardwareAdapter, sensor: SensorInfo) -> float:
        """Estimate noise level in signal"""
        # Take rapid samples
        samples = []
        
        for _ in range(10):
            voltage = await self._read_bioelectric_voltage(sensor)
            samples.append(voltage)
            
        if len(samples) < 2:
            return 1.0
            
        # Calculate noise as coefficient of variation
        std_dev = np.std(samples)
        mean = np.mean(samples)
        
        if abs(mean) > 0.001:
            noise = std_dev / abs(mean)
        else:
            noise = std_dev
            
        return min(1.0, noise)
        
    def _estimate_dominant_frequency(self, readings: List[BioelectricReadingV3]) -> float:
        """Estimate dominant frequency using FFT"""
        if len(readings) < 32:
            return 0.0
            
        # Extract voltages
        voltages = [r.voltage_mv for r in readings]
        
        # Remove DC component
        voltages = voltages - np.mean(voltages)
        
        # Apply window
        window = signal.windows.hann(len(voltages))
        voltages = voltages * window
        
        # FFT
        fft_vals = np.abs(np.fft.rfft(voltages))
        
        # Find dominant frequency
        peak_idx = np.argmax(fft_vals[1:]) + 1  # Skip DC
        
        # Convert to Hz
        freq_hz = peak_idx * self.sampling_rate / len(voltages)
        
        return freq_hz
        
    async def _detect_signal_events_v3(self, readings: List[BioelectricReadingV3]) -> List[Dict]:
        """Enhanced event detection with pattern recognition"""
        events = []
        
        # Group by plant for coordinated detection
        plant_readings = {}
        for reading in readings:
            plant_id = self._get_plant_from_electrode(reading.electrode_id)
            if plant_id:
                if plant_id not in plant_readings:
                    plant_readings[plant_id] = []
                plant_readings[plant_id].append(reading)
                
        # Detect events per plant
        for plant_id, plant_signals in plant_readings.items():
            # Check for action potentials
            for reading in plant_signals:
                if reading.voltage_mv > 50 and reading.hardware_health > 0.8:
                    events.append({
                        'type': SignalType.ACTION_POTENTIAL,
                        'plant_id': plant_id,
                        'timestamp': reading.timestamp,
                        'magnitude': reading.voltage_mv,
                        'electrode': reading.electrode_id,
                        'confidence': reading.hardware_health * (1 - reading.noise_level)
                    })
                    
            # Check for network oscillations (plant communication)
            if len(plant_signals) >= 3:
                # Calculate phase coherence across electrodes
                coherence = await self._calculate_electrode_coherence(plant_signals)
                
                if coherence > 0.8:
                    events.append({
                        'type': SignalType.NETWORK_OSCILLATION,
                        'plant_id': plant_id,
                        'timestamp': datetime.utcnow(),
                        'coherence': coherence,
                        'participating_electrodes': len(plant_signals)
                    })
                    
        return events
        
    async def _interpretation_loop_v3(self):
        """Enhanced interpretation with distributed processing"""
        while True:
            try:
                interpretation_tasks = []
                
                for plant_id, signal_buffer in self.signal_buffers.items():
                    if len(signal_buffer) < self.sampling_rate * 5:  # Need 5 seconds
                        continue
                        
                    # Check cache
                    cache_key = f"{plant_id}_{len(signal_buffer)}"
                    if cache_key in self.interpretation_cache:
                        cached = self.interpretation_cache[cache_key]
                        if (datetime.utcnow() - cached['timestamp']).seconds < 30:
                            continue
                            
                    # Distribute processing if available
                    if self.processing_nodes:
                        task = self._distributed_interpretation(plant_id, signal_buffer)
                    else:
                        task = self._local_interpretation(plant_id, signal_buffer)
                        
                    interpretation_tasks.append(task)
                    
                # Process interpretations in parallel
                interpretations = await asyncio.gather(*interpretation_tasks, return_exceptions=True)
                
                for interpretation in interpretations:
                    if isinstance(interpretation, PlantCommunication):
                        # Update plant state
                        self.plant_states[interpretation.plant_id] = interpretation
                        
                        # Log communication
                        self.communication_log.append(interpretation)
                        
                        # Update network state
                        await self._update_network_state(interpretation)
                        
                        # Take action if needed
                        await self._respond_to_plant_needs_v3(interpretation)
                        
                        # Cache result
                        self.interpretation_cache[f"{interpretation.plant_id}_{len(signal_buffer)}"] = {
                            'interpretation': interpretation,
                            'timestamp': datetime.utcnow()
                        }
                        
            except Exception as e:
                logger.error(f"Interpretation error: {e}")
                
            await asyncio.sleep(5)  # Interpret every 5 seconds
            
    async def _distributed_interpretation(self, plant_id: str, 
                                        signal_buffer: deque) -> Optional[PlantCommunication]:
        """Distribute interpretation across processing nodes"""
        # Select least loaded node
        best_node = None
        min_load = float('inf')
        
        for node_name, node_info in self.processing_nodes.items():
            if node_info['load'] < min_load:
                min_load = node_info['load']
                best_node = (node_name, node_info)
                
        if not best_node:
            return await self._local_interpretation(plant_id, signal_buffer)
            
        node_name, node_info = best_node
        adapter = node_info['adapter']
        
        try:
            # Update load
            node_info['load'] += 0.1
            
            # Prepare signal data
            signal_data = {
                'plant_id': plant_id,
                'signals': [
                    {
                        'timestamp': r.timestamp.isoformat(),
                        'voltage_mv': r.voltage_mv,
                        'frequency_hz': r.frequency_hz,
                        'electrode_id': r.electrode_id
                    }
                    for r in list(signal_buffer)[-1000:]  # Last 1000 samples
                ],
                'species': await self.env.get_plant_info(plant_id).get('species', 'unknown')
            }
            
            # Send for processing
            result = await adapter._api_call('POST', '/bioelectric/interpret', signal_data)
            
            if result:
                # Convert to PlantCommunication
                return self._parse_remote_interpretation(plant_id, result)
                
        except Exception as e:
            logger.error(f"Distributed interpretation failed: {e}")
            
        finally:
            # Update load
            node_info['load'] = max(0, node_info['load'] - 0.1)
            
        return await self._local_interpretation(plant_id, signal_buffer)
        
    async def _local_interpretation(self, plant_id: str, 
                                   signal_buffer: deque) -> Optional[PlantCommunication]:
        """Local interpretation with HAL acceleration"""
        buffer = list(signal_buffer)
        
        if not buffer:
            return None
            
        # Get plant species for model selection
        plant_info = await self.env.get_plant_info(plant_id)
        species = plant_info.get('species', 'generic')
        
        # Select appropriate model
        model = self.plant_models.get(species)
        if not model:
            logger.warning(f"No model for {species}, using generic")
            model = self.plant_models.get('generic')
            
        if not model:
            return None
            
        # Extract features
        features = await self._extract_signal_features_v3(buffer)
        
        # Use DSP acceleration if available
        if self.signal_adapters:
            features = await self._accelerate_feature_extraction(features)
            
        # Run interpretation model
        prediction = await model.predict(features)
        
        # Create enhanced communication object
        return self._create_plant_communication_v3(plant_id, prediction, buffer)
        
    async def _democracy_loop_v3(self):
        """Enhanced plant democracy with signal validation"""
        while True:
            try:
                # Check if enough plants are communicating clearly
                clear_plants = [
                    (plant_id, state) for plant_id, state in self.plant_states.items()
                    if state.confidence > self.signal_threshold and
                    state.stress_level < 0.5
                ]
                
                if len(clear_plants) >= self.min_voters:
                    # Collect votes
                    votes = await self._collect_plant_votes_v3(clear_plants)
                    
                    # Validate votes based on signal strength
                    valid_votes = [v for v in votes if v.signal_strength > 0.7]
                    
                    if len(valid_votes) >= self.min_voters:
                        # Calculate consensus
                        consensus = await self._calculate_consensus_v3(valid_votes)
                        
                        # Apply with zone coordination
                        await self._apply_democratic_consensus_v3(consensus)
                        
                        logger.info(f"Plant democracy enacted with {len(valid_votes)} voters "
                                  f"(signal strength: {np.mean([v.signal_strength for v in valid_votes]):.2f})")
                        
            except Exception as e:
                logger.error(f"Democracy loop error: {e}")
                
            await asyncio.sleep(self.voting_interval * 3600)
            
    async def _collect_plant_votes_v3(self, clear_plants: List[Tuple[str, PlantCommunication]]) -> List[PlantVoteV3]:
        """Collect votes with signal strength validation"""
        votes = []
        
        for plant_id, state in clear_plants:
            # Get array signal quality
            array = next((a for a in self.electrode_arrays.values() if a.plant_id == plant_id), None)
            
            if not array:
                continue
                
            # Determine preferences
            preferences = await self._determine_plant_preferences(plant_id)
            
            # Calculate vote weight with hardware factors
            base_weight = await self._calculate_vote_weight(plant_id)
            hw_factor = array.signal_quality * np.mean([e['adapter'].health_score 
                                                       for e in array.electrodes 
                                                       if 'adapter' in e])
            
            vote = PlantVoteV3(
                plant_id=plant_id,
                temperature_c=preferences['temperature'],
                humidity_percent=preferences['humidity'],
                light_ppfd=preferences['light'],
                co2_ppm=preferences['co2'],
                vote_weight=base_weight * hw_factor,
                signal_strength=array.signal_quality,
                consensus_confidence=state.confidence,
                reasoning=self._explain_vote_v3(state, preferences, array)
            )
            
            votes.append(vote)
            
        return votes
        
    async def _calculate_consensus_v3(self, votes: List[PlantVoteV3]) -> Dict[str, float]:
        """Calculate consensus with signal-weighted voting"""
        # Weight by both vote weight and signal strength
        total_weight = sum(v.vote_weight * v.signal_strength for v in votes)
        
        if total_weight == 0:
            return {}
            
        consensus = {
            'temperature': sum(v.temperature_c * v.vote_weight * v.signal_strength for v in votes) / total_weight,
            'humidity': sum(v.humidity_percent * v.vote_weight * v.signal_strength for v in votes) / total_weight,
            'light': sum(v.light_ppfd * v.vote_weight * v.signal_strength for v in votes) / total_weight,
            'co2': sum(v.co2_ppm * v.vote_weight * v.signal_strength for v in votes) / total_weight,
            'confidence': sum(v.consensus_confidence * v.signal_strength for v in votes) / len(votes)
        }
        
        # Log detailed voting results
        logger.info("Plant democracy details:")
        for vote in sorted(votes, key=lambda v: v.vote_weight * v.signal_strength, reverse=True)[:5]:
            logger.info(f"  {vote.plant_id}: weight={vote.vote_weight:.2f}, "
                       f"signal={vote.signal_strength:.2f}, {vote.reasoning}")
                       
        return consensus
        
    async def _apply_democratic_consensus_v3(self, consensus: Dict[str, float]):
        """Apply consensus with zone coordination"""
        if consensus.get('confidence', 0) < 0.7:
            logger.warning("Consensus confidence too low, not applying")
            return
            
        # Coordinate across zones
        if self.zone_coordinators:
            # Each zone applies consensus with local adjustments
            for zone_id, coordinator in self.zone_coordinators.items():
                zone_consensus = await coordinator.adapt_consensus_to_zone(consensus)
                await self.env.set_zone_conditions(zone_id, zone_consensus)
        else:
            # Single zone application
            await self.env.set_conditions(consensus)
            
        # Log the democratic decision
        await self.env.log_event(
            'plant_democracy_enacted_v3',
            consensus=consensus,
            zones=list(self.zone_coordinators.keys()),
            hardware_health=await self._get_democracy_hardware_health()
        )
        
    async def _handle_hardware_failure(self, event_data: Dict):
        """Handle bioelectric hardware failures"""
        failed_adapter = event_data['name']
        
        # Find affected electrode arrays
        affected_arrays = []
        for array in self.electrode_arrays.values():
            if array.adapter_name == failed_adapter:
                affected_arrays.append(array)
            else:
                # Check individual electrodes
                for electrode in array.electrodes:
                    if electrode.get('adapter_name') == failed_adapter:
                        affected_arrays.append(array)
                        break
                        
        logger.warning(f"Bioelectric hardware failure affects {len(affected_arrays)} arrays")
        
        # Try to reassign to backup adapters
        for array in affected_arrays:
            backup_adapter = await self._find_backup_adapter(array)
            
            if backup_adapter:
                array.adapter_name = backup_adapter
                logger.info(f"Reassigned array {array.array_id} to {backup_adapter}")
            else:
                # Mark array as degraded
                array.signal_quality *= 0.5
                logger.warning(f"No backup for array {array.array_id}")
                
    async def get_consciousness_metrics_v3(self) -> Dict[str, Any]:
        """Get comprehensive consciousness interface metrics"""
        total_plants = len(self.plant_states)
        communicating_plants = sum(1 for s in self.plant_states.values() 
                                 if s.primary_state == PlantState.COMMUNICATING)
        
        # Hardware metrics
        total_electrodes = sum(len(a.electrodes) for a in self.electrode_arrays.values())
        healthy_electrodes = sum(
            sum(1 for e in a.electrodes 
                if self.hw_manager.get_adapter(e.get('adapter_name', '')).health_score > 0.8)
            for a in self.electrode_arrays.values()
        )
        
        # Signal quality
        avg_signal_quality = np.mean([a.signal_quality for a in self.electrode_arrays.values()]) \
                           if self.electrode_arrays else 0
                           
        # Processing performance
        recent_metrics = self.processing_metrics[-100:] if self.processing_metrics else []
        avg_processing_time = np.mean([m['processing_time_ms'] for m in recent_metrics]) \
                            if recent_metrics else 0
                            
        return {
            'total_monitored_plants': total_plants,
            'communicating_plants': communicating_plants,
            'total_electrodes': total_electrodes,
            'healthy_electrodes': healthy_electrodes,
            'electrode_arrays': len(self.electrode_arrays),
            'average_signal_quality': float(avg_signal_quality),
            'average_stress_level': np.mean([s.stress_level for s in self.plant_states.values()]) if self.plant_states else 0,
            'recent_communications': len([c for c in self.communication_log if (datetime.utcnow() - c.timestamp).seconds < 3600]),
            'democracy_active': self.democracy_enabled,
            'distributed_nodes': len(self.processing_nodes),
            'avg_processing_time_ms': float(avg_processing_time),
            'network_coherence': self.network_state.coherence if hasattr(self, 'network_state') else 0
        }
        
    def _explain_vote_v3(self, state: PlantCommunication, preferences: Dict, 
                        array: ElectrodeArray) -> str:
        """Generate detailed vote explanation"""
        if state.primary_state == PlantState.OPTIMAL:
            return f"Optimal (signal: {array.signal_quality:.0%})"
        else:
            return f"{state.primary_state.value} - requesting adjustment (signal: {array.signal_quality:.0%})"


class SignalAggregator:
    """Aggregate signals across distributed systems"""
    
    async def aggregate_plant_signals(self, plant_id: str, 
                                    signal_sources: List[Dict]) -> Dict:
        """Combine signals from multiple sources"""
        # Implementation would merge distributed signals
        return {}


class NetworkState:
    """Track overall plant network state"""
    
    def __init__(self):
        self.coherence = 0.0
        self.communication_events = deque(maxlen=1000)
        self.network_graph = {}  # Plant-to-plant communications