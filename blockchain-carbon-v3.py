# modules/carbon_credits/blockchain_carbon_v3.py
"""
OSCE Carbon Credit Engine v3 - Production HAL Integration
Automated carbon measurement and trading with hardware verification

Key v3 Enhancements:
- HAL-verified sensor measurements
- Hardware health-weighted carbon calculations
- Multi-site carbon aggregation
- Performance-optimized verification
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from decimal import Decimal
from dataclasses import dataclass
from enum import Enum
import hashlib

from osce.core.base import OSCEModule
from osce.ml.predictions import CarbonPricePredictor
from osce.utils.logging import get_logger
from osce_hal_enhanced import (
    HardwareManager, HardwareAdapter, SensorInfo,
    HardwareHealth, NetworkHardwareAdapter
)

logger = get_logger(__name__)

class CarbonProtocol(Enum):
    """Supported carbon credit protocols"""
    VERRA_VCS = "verra_vcs"
    GOLD_STANDARD = "gold_standard"
    CAR = "climate_action_reserve"
    OSCE_PROTOCOL = "osce_v3"  # Enhanced v3 protocol

@dataclass
class CarbonMeasurementV3:
    """Enhanced carbon measurement with hardware validation"""
    timestamp: datetime
    plant_sequestration: float
    soil_sequestration: float
    emissions_avoided: float
    energy_emissions: float
    net_sequestration: float
    confidence: float
    measurement_hash: str
    hardware_health: Dict[str, float]  # Sensor health scores
    sensor_coverage: float  # Percentage of area monitored
    measurement_quality: str  # 'verified', 'estimated', 'interpolated'

class CarbonCreditEngineV3(OSCEModule):
    """
    v3: Production-ready with HAL sensor verification
    
    New Features:
    - Multi-sensor carbon verification
    - Hardware health-weighted measurements
    - Distributed site aggregation
    - Real-time blockchain integration
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Configuration
        self.enabled = config.get('carbon_credits_enabled', False)
        self.protocol = CarbonProtocol(config.get('protocol', 'osce_v3'))
        self.trading_enabled = config.get('trading_enabled', False)
        
        # HAL integration
        self.hw_manager: Optional[HardwareManager] = None
        self.co2_sensor_groups = {}
        self.soil_sensor_groups = {}
        self.energy_monitors = {}
        
        # Measurement configuration
        self.measurement_interval = config.get('measurement_interval', 3600)
        self.min_sensor_coverage = config.get('min_sensor_coverage', 0.8)
        self.sensor_redundancy = config.get('sensor_redundancy', 3)
        
        # Verification
        self.verification_service = config.get('verification_service')
        self.min_confidence = config.get('min_confidence', 0.90)
        self.min_hardware_health = config.get('min_hardware_health', 0.85)
        
        # Trading
        self.trading_strategy = TradingStrategy(
            config.get('trading_strategy', 'hold')
        )
        self.min_price = Decimal(config.get('min_price', '20.00'))
        self.price_predictor = None
        
        # Multi-site support
        self.sites = config.get('sites', [])
        self.site_measurements = {}
        
        # Storage
        self.measurements = []
        self.credits = []
        self.pending_verifications = []
        
    async def initialize(self):
        """Initialize with HAL sensor discovery"""
        if not self.enabled:
            logger.info("Carbon credit engine disabled")
            return
            
        # Get hardware manager
        self.hw_manager = self.env.hal
        
        if not self.hw_manager:
            logger.error("HAL required for carbon measurements")
            return
            
        # Discover and group CO2 sensors
        await self._initialize_co2_sensors()
        
        # Initialize soil carbon analyzers
        await self._initialize_soil_sensors()
        
        # Setup energy monitoring
        await self._initialize_energy_monitors()
        
        # Register for hardware events
        self.hw_manager.on_event('adapter_failed', self._handle_sensor_failure)
        self.hw_manager.on_event('hardware_discovered', self._handle_new_sensors)
        
        # Initialize price predictor if trading
        if self.trading_enabled:
            self.price_predictor = CarbonPricePredictor()
            await self.price_predictor.load_model()
            
        # Start measurement loop
        asyncio.create_task(self._continuous_measurement_v3())
        
        # Start verification loop
        asyncio.create_task(self._verification_loop())
        
        logger.info(f"Carbon credit engine v3 initialized with {self.protocol.value}")
        
    async def _initialize_co2_sensors(self):
        """Group CO2 sensors by location/zone"""
        all_sensors = await self.hw_manager.get_all_sensors()
        
        co2_types = ['MH-Z19', 'SCD30', 'SCD41', 'K30', 'T6713']
        
        for adapter_name, sensors in all_sensors.items():
            for sensor in sensors:
                if any(co2_type in sensor.sensor_type for co2_type in co2_types):
                    # Determine zone from sensor name or location
                    zone = self._extract_zone_from_sensor(sensor)
                    
                    if zone not in self.co2_sensor_groups:
                        self.co2_sensor_groups[zone] = []
                        
                    self.co2_sensor_groups[zone].append({
                        'sensor': sensor,
                        'adapter_name': adapter_name,
                        'last_reading': None,
                        'error_count': 0,
                        'calibration': sensor.calibration_data or {}
                    })
                    
        logger.info(f"Initialized {sum(len(g) for g in self.co2_sensor_groups.values())} CO2 sensors in {len(self.co2_sensor_groups)} zones")
        
    async def _initialize_soil_sensors(self):
        """Initialize soil carbon monitoring sensors"""
        all_sensors = await self.hw_manager.get_all_sensors()
        
        # Soil sensor types that can indicate carbon
        soil_types = ['soil_carbon', 'soil_ec', 'soil_organic_matter', 'nirs']
        
        for adapter_name, sensors in all_sensors.items():
            for sensor in sensors:
                if any(soil_type in sensor.sensor_type.lower() for soil_type in soil_types):
                    zone = self._extract_zone_from_sensor(sensor)
                    
                    if zone not in self.soil_sensor_groups:
                        self.soil_sensor_groups[zone] = []
                        
                    self.soil_sensor_groups[zone].append({
                        'sensor': sensor,
                        'adapter_name': adapter_name,
                        'measurement_type': self._classify_soil_sensor(sensor),
                        'last_sample': None
                    })
                    
    async def _initialize_energy_monitors(self):
        """Setup energy consumption monitoring"""
        all_sensors = await self.hw_manager.get_all_sensors()
        
        energy_types = ['power_meter', 'current_sensor', 'energy_monitor', 'smart_plug']
        
        for adapter_name, sensors in all_sensors.items():
            for sensor in sensors:
                if any(energy_type in sensor.sensor_type.lower() for energy_type in energy_types):
                    circuit = sensor.name.split('_')[0] if '_' in sensor.name else 'main'
                    
                    if circuit not in self.energy_monitors:
                        self.energy_monitors[circuit] = []
                        
                    self.energy_monitors[circuit].append({
                        'sensor': sensor,
                        'adapter_name': adapter_name,
                        'scale_factor': sensor.calibration_data.get('scale', 1.0) if sensor.calibration_data else 1.0
                    })
                    
    async def _continuous_measurement_v3(self):
        """Enhanced measurement with hardware validation"""
        while True:
            try:
                # Check overall hardware health
                hw_health = await self._assess_measurement_hardware_health()
                
                if hw_health < self.min_hardware_health:
                    logger.warning(f"Hardware health below threshold: {hw_health}")
                    # Still measure but mark as lower quality
                    
                # Measure carbon with multi-sensor verification
                measurement = await self._measure_carbon_flux_v3()
                
                # Store measurement
                self.measurements.append(measurement)
                
                # If multi-site, aggregate measurements
                if self.sites:
                    await self._aggregate_site_measurements(measurement)
                    
                # Check if ready for verification
                if await self._sufficient_data_for_credit():
                    await self._prepare_verification_batch()
                    
            except Exception as e:
                logger.error(f"Measurement error: {e}")
                
            await asyncio.sleep(self.measurement_interval)
            
    async def _measure_carbon_flux_v3(self) -> CarbonMeasurementV3:
        """Measure carbon with hardware validation"""
        start_time = datetime.utcnow()
        hardware_health = {}
        
        # CO2 measurements from multiple sensors
        co2_absorbed = 0.0
        co2_measurements = []
        total_zones = len(self.co2_sensor_groups)
        measured_zones = 0
        
        for zone, sensors in self.co2_sensor_groups.items():
            zone_measurements = []
            
            # Read from multiple sensors for verification
            for sensor_info in sensors:
                adapter = self.hw_manager.get_adapter(sensor_info['adapter_name'])
                
                if adapter and adapter.health_score > 0.7:
                    try:
                        # Read CO2 through HAL
                        co2_reading = await adapter.secure_operation(
                            self._read_co2_sensor,
                            sensor_info['sensor']
                        )
                        
                        zone_measurements.append(co2_reading)
                        hardware_health[sensor_info['sensor'].name] = adapter.health_score
                        
                    except Exception as e:
                        sensor_info['error_count'] += 1
                        logger.warning(f"CO2 sensor read failed: {e}")
                        
            if zone_measurements:
                # Use median for robustness
                zone_co2 = np.median(zone_measurements)
                co2_measurements.append(zone_co2)
                measured_zones += 1
                
        # Calculate plant sequestration
        if co2_measurements:
            # Get plant biomass data through HAL cameras/sensors
            biomass_data = await self._get_biomass_data_hal()
            plant_sequestration = await self._calculate_plant_sequestration_v3(
                co2_measurements, biomass_data
            )
        else:
            plant_sequestration = 0.0
            
        # Soil carbon measurements
        soil_sequestration = await self._measure_soil_carbon_hal()
        
        # Calculate avoided emissions
        emissions_avoided = await self._calculate_avoided_emissions_hal()
        
        # Measure energy consumption
        energy_emissions = await self._calculate_energy_emissions_hal()
        
        # Net calculation
        net_sequestration = (
            plant_sequestration + 
            soil_sequestration + 
            emissions_avoided - 
            energy_emissions
        )
        
        # Calculate confidence based on sensor coverage and health
        sensor_coverage = measured_zones / max(total_zones, 1)
        avg_hw_health = sum(hardware_health.values()) / len(hardware_health) if hardware_health else 0
        confidence = sensor_coverage * avg_hw_health
        
        # Determine measurement quality
        if confidence > 0.9 and sensor_coverage > 0.8:
            quality = 'verified'
        elif confidence > 0.7:
            quality = 'estimated'
        else:
            quality = 'interpolated'
            
        measurement = CarbonMeasurementV3(
            timestamp=datetime.utcnow(),
            plant_sequestration=plant_sequestration,
            soil_sequestration=soil_sequestration,
            emissions_avoided=emissions_avoided,
            energy_emissions=energy_emissions,
            net_sequestration=net_sequestration,
            confidence=confidence,
            measurement_hash=self._hash_measurement(net_sequestration),
            hardware_health=hardware_health,
            sensor_coverage=sensor_coverage,
            measurement_quality=quality
        )
        
        logger.debug(f"Carbon measurement: {net_sequestration:.2f} kg CO2 "
                    f"(quality: {quality}, coverage: {sensor_coverage:.0%})")
                    
        return measurement
        
    async def _calculate_plant_sequestration_v3(self, co2_readings: List[float], 
                                              biomass_data: Dict) -> float:
        """Enhanced calculation with multiple verification methods"""
        if not co2_readings or not biomass_data:
            return 0.0
            
        # Method 1: Direct CO2 flux measurement
        avg_co2_reduction = sum(co2_readings) / len(co2_readings)
        
        # Method 2: Biomass-based calculation
        total_leaf_area = biomass_data.get('total_leaf_area', 0)
        avg_light_intensity = biomass_data.get('light_intensity', 0)
        
        # Photosynthesis rate with hardware-verified parameters
        photosynthesis_rate = min(avg_light_intensity / 50, 15)  # μmol/m²/s
        
        # CO2 absorbed calculation
        co2_absorbed_biomass = (
            photosynthesis_rate *
            total_leaf_area *
            3600 *  # seconds per hour
            44.01 *  # molecular weight of CO2
            1e-9     # μmol to kg
        )
        
        # Method 3: Environmental chamber mass balance
        chamber_volume = biomass_data.get('chamber_volume', 0)  # m³
        co2_absorbed_chamber = (
            avg_co2_reduction * 1e-6 *  # ppm to fraction
            chamber_volume *
            1.977  # kg CO2 per m³ at STP
        )
        
        # Weighted average of methods based on sensor quality
        weights = {
            'flux': 0.4 if len(co2_readings) >= self.sensor_redundancy else 0.2,
            'biomass': 0.4 if biomass_data.get('confidence', 0) > 0.8 else 0.2,
            'chamber': 0.2
        }
        
        total_weight = sum(weights.values())
        
        co2_absorbed = (
            weights['flux'] * co2_absorbed_chamber +
            weights['biomass'] * co2_absorbed_biomass +
            weights['chamber'] * co2_absorbed_chamber
        ) / total_weight
        
        return max(0, co2_absorbed)
        
    async def _measure_soil_carbon_hal(self) -> float:
        """Measure soil carbon using HAL sensors"""
        if not self.soil_sensor_groups:
            return 0.0
            
        soil_measurements = []
        
        for zone, sensors in self.soil_sensor_groups.items():
            for sensor_info in sensors:
                adapter = self.hw_manager.get_adapter(sensor_info['adapter_name'])
                
                if adapter and adapter.health_score > 0.8:
                    try:
                        if sensor_info['measurement_type'] == 'direct':
                            # Direct soil carbon sensor
                            carbon_percent = await adapter.secure_operation(
                                self._read_soil_carbon_sensor,
                                sensor_info['sensor']
                            )
                            soil_measurements.append(carbon_percent)
                            
                        elif sensor_info['measurement_type'] == 'ec_proxy':
                            # Estimate from electrical conductivity
                            ec = await adapter.secure_operation(
                                self._read_ec_sensor,
                                sensor_info['sensor']
                            )
                            # Convert EC to estimated carbon
                            carbon_estimate = self._ec_to_carbon(ec)
                            soil_measurements.append(carbon_estimate)
                            
                    except Exception as e:
                        logger.error(f"Soil sensor read failed: {e}")
                        
        if not soil_measurements:
            return 0.0
            
        # Compare with baseline
        current_carbon = np.median(soil_measurements)
        baseline_carbon = self.config.get('baseline_soil_carbon', 2.0)  # %
        
        # Calculate change
        carbon_change_percent = current_carbon - baseline_carbon
        
        # Convert to kg CO2
        soil_volume = await self.env.get_soil_volume()  # m³
        soil_density = 1300  # kg/m³
        
        carbon_change_kg = (
            carbon_change_percent / 100 *
            soil_volume *
            soil_density
        )
        
        # Convert C to CO2
        co2_change = carbon_change_kg * 3.67
        
        return max(0, co2_change)
        
    async def _calculate_energy_emissions_hal(self) -> float:
        """Calculate emissions using HAL energy monitors"""
        total_energy_kwh = 0.0
        
        for circuit, monitors in self.energy_monitors.items():
            circuit_energy = 0.0
            
            for monitor_info in monitors:
                adapter = self.hw_manager.get_adapter(monitor_info['adapter_name'])
                
                if adapter:
                    try:
                        # Read power consumption
                        power_w = await adapter.secure_operation(
                            self._read_power_sensor,
                            monitor_info['sensor']
                        )
                        
                        # Apply calibration
                        power_w *= monitor_info['scale_factor']
                        
                        # Convert to kWh (assuming hourly measurements)
                        circuit_energy += power_w / 1000
                        
                    except Exception as e:
                        logger.error(f"Energy monitor read failed: {e}")
                        
            total_energy_kwh += circuit_energy
            
        # Get energy source mix from config or smart meter
        energy_mix = await self._get_energy_mix_hal()
        
        # Calculate emissions
        emission_factors = {
            'solar': 0.05,
            'wind': 0.01,
            'grid': 0.5,
            'natural_gas': 0.4,
            'diesel': 0.7
        }
        
        total_emissions = 0
        for source, fraction in energy_mix.items():
            emissions = total_energy_kwh * fraction * emission_factors.get(source, 0.5)
            total_emissions += emissions
            
        return total_emissions
        
    async def _handle_sensor_failure(self, event_data: Dict):
        """Handle sensor failures gracefully"""
        failed_adapter = event_data['name']
        
        # Mark affected sensors
        affected_co2 = 0
        for zone, sensors in self.co2_sensor_groups.items():
            for sensor_info in sensors:
                if sensor_info['adapter_name'] == failed_adapter:
                    sensor_info['error_count'] = 999  # Mark as failed
                    affected_co2 += 1
                    
        # Check if we still have minimum coverage
        total_co2_sensors = sum(len(s) for s in self.co2_sensor_groups.values())
        working_sensors = total_co2_sensors - affected_co2
        
        coverage = working_sensors / total_co2_sensors if total_co2_sensors > 0 else 0
        
        if coverage < self.min_sensor_coverage:
            logger.critical(f"Carbon sensor coverage below minimum: {coverage:.0%}")
            # Pause high-confidence measurements
            self.min_confidence = 0.99  # Increase threshold
            
    async def _prepare_verification_batch(self):
        """Prepare batch with hardware quality metrics"""
        # Get measurements with sufficient quality
        quality_measurements = [
            m for m in self.measurements
            if m.measurement_quality in ['verified', 'estimated'] and
            m.confidence >= self.min_confidence
        ]
        
        if len(quality_measurements) < 30:  # Need 30 days
            return
            
        # Calculate totals with quality weighting
        total_sequestration = 0.0
        total_weight = 0.0
        
        for m in quality_measurements:
            weight = m.confidence * (1.0 if m.measurement_quality == 'verified' else 0.8)
            total_sequestration += m.net_sequestration * weight
            total_weight += weight
            
        weighted_sequestration = total_sequestration / total_weight if total_weight > 0 else 0
        
        # Create verification request
        verification_request = {
            'protocol': self.protocol.value,
            'period_start': quality_measurements[0].timestamp.isoformat(),
            'period_end': quality_measurements[-1].timestamp.isoformat(),
            'total_sequestration_kg': weighted_sequestration,
            'measurement_count': len(quality_measurements),
            'avg_confidence': sum(m.confidence for m in quality_measurements) / len(quality_measurements),
            'avg_sensor_coverage': sum(m.sensor_coverage for m in quality_measurements) / len(quality_measurements),
            'hardware_health_summary': self._summarize_hardware_health(quality_measurements),
            'measurements': [self._serialize_measurement_v3(m) for m in quality_measurements],
            'facility_data': await self._get_facility_data(),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        self.pending_verifications.append(verification_request)
        
        logger.info(f"Prepared verification batch: {weighted_sequestration:.2f} kg CO2 "
                   f"({len(quality_measurements)} measurements)")
                   
    def _serialize_measurement_v3(self, measurement: CarbonMeasurementV3) -> Dict:
        """Serialize measurement with hardware data"""
        return {
            'timestamp': measurement.timestamp.isoformat(),
            'plant_sequestration': measurement.plant_sequestration,
            'soil_sequestration': measurement.soil_sequestration,
            'emissions_avoided': measurement.emissions_avoided,
            'energy_emissions': measurement.energy_emissions,
            'net_sequestration': measurement.net_sequestration,
            'confidence': measurement.confidence,
            'measurement_hash': measurement.measurement_hash,
            'hardware_health': measurement.hardware_health,
            'sensor_coverage': measurement.sensor_coverage,
            'measurement_quality': measurement.measurement_quality
        }
        
    async def get_carbon_summary_v3(self) -> Dict:
        """Enhanced summary with hardware metrics"""
        total_sequestered = sum(m.net_sequestration for m in self.measurements) / 1000
        quality_measurements = [m for m in self.measurements if m.measurement_quality == 'verified']
        verified_sequestration = sum(m.net_sequestration for m in quality_measurements) / 1000
        
        # Hardware metrics
        current_hw_health = await self._assess_measurement_hardware_health()
        sensor_summary = {
            'co2_sensors': sum(len(s) for s in self.co2_sensor_groups.values()),
            'soil_sensors': sum(len(s) for s in self.soil_sensor_groups.values()),
            'energy_monitors': sum(len(m) for m in self.energy_monitors.values())
        }
        
        return {
            'total_sequestered_tonnes': float(total_sequestered),
            'verified_sequestration_tonnes': float(verified_sequestration),
            'total_credits_issued': sum(c.amount_tonnes for c in self.credits),
            'credits_available': len([c for c in self.credits if c.status == 'active']),
            'pending_verifications': len(self.pending_verifications),
            'measurement_count': len(self.measurements),
            'verified_measurement_count': len(quality_measurements),
            'current_hardware_health': current_hw_health,
            'sensor_summary': sensor_summary,
            'average_sensor_coverage': np.mean([m.sensor_coverage for m in self.measurements[-100:]]) if self.measurements else 0,
            'last_measurement': self.measurements[-1].timestamp if self.measurements else None
        }