# modules/quantum_mesh/qkd_network_v3.py
"""
OSCE Quantum-Secured Mesh Network v3 - Production HAL Integration
Advanced cryptographic security with hardware performance optimization

Key v3 Enhancements:
- HAL-managed quantum hardware interfaces
- Performance-aware key distribution
- Multi-adapter security mesh
- Hardware health-based trust scoring
"""

import asyncio
import secrets
import hashlib
from typing import Dict, List, Optional, Tuple, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import numpy as np

from osce.core.base import OSCEModule
from osce.network.mesh import MeshNetwork
from osce.utils.logging import get_logger
from osce_hal_enhanced import (
    HardwareManager, HardwareAdapter, SensorInfo,
    HardwareHealth, NetworkHardwareAdapter, ESP32Adapter
)

logger = get_logger(__name__)

class SecurityLevel(Enum):
    """Network security levels"""
    STANDARD = "standard"  # AES-256
    ENHANCED = "enhanced"  # Post-quantum algorithms
    QUANTUM = "quantum"    # Quantum key distribution
    EXPERIMENTAL = "experimental"  # Full quantum protocols

@dataclass
class QuantumKeyV3:
    """Enhanced quantum key with hardware metrics"""
    key_id: str
    key_material: bytes
    creation_time: datetime
    protocol: QuantumProtocol
    error_rate: float
    consumed_bits: int = 0
    total_bits: int = 0
    hardware_health: float = 1.0  # Health at creation
    generation_latency_ms: float = 0.0
    
    def consume_bits(self, bits: int):
        """Mark key bits as used"""
        self.consumed_bits += bits
        if self.consumed_bits > self.total_bits:
            raise ValueError("Insufficient key material")
            
    def get_quality_score(self) -> float:
        """Calculate key quality based on multiple factors"""
        # Factor in error rate, hardware health, and age
        age_factor = 1.0 - min((datetime.utcnow() - self.creation_time).days / 30, 1.0)
        usage_factor = 1.0 - (self.consumed_bits / self.total_bits)
        
        return (
            (1.0 - self.error_rate) * 0.4 +
            self.hardware_health * 0.3 +
            age_factor * 0.2 +
            usage_factor * 0.1
        )

@dataclass
class NodeSecurityProfile:
    """Security profile for mesh nodes"""
    node_id: str
    adapter_name: str
    capabilities: Set[str]
    trust_score: float
    last_seen: datetime
    quantum_capable: bool
    hardware_health: float
    established_channels: List[str]

class QuantumSecuredMeshV3(OSCEModule):
    """
    v3: Production quantum security with HAL integration
    
    New Features:
    - Hardware-accelerated cryptography
    - Adaptive security based on hardware health
    - Multi-path key distribution
    - Performance-optimized protocols
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        # Security configuration
        self.security_level = SecurityLevel(
            config.get('security_level', 'enhanced')
        )
        self.quantum_enabled = config.get('quantum_hardware_available', False)
        
        # HAL integration
        self.hw_manager: Optional[HardwareManager] = None
        self.security_adapters = {}  # Adapters with security capabilities
        self.quantum_adapters = {}   # Quantum-capable adapters
        
        # Network topology
        self.mesh_network = MeshNetwork()
        self.node_profiles: Dict[str, NodeSecurityProfile] = {}
        self.secure_channels = {}
        
        # Key management
        self.key_pool = {}
        self.key_refresh_interval = config.get('key_refresh_hours', 24)
        self.min_key_quality = config.get('min_key_quality', 0.7)
        
        # Performance thresholds
        self.min_hardware_health = config.get('min_hardware_health', 0.75)
        self.max_key_latency_ms = config.get('max_key_latency_ms', 1000)
        
        # Intrusion detection
        self.ids_enabled = config.get('intrusion_detection', True)
        self.suspicious_activity = []
        self.anomaly_threshold = config.get('anomaly_threshold', 0.15)
        
        # Quantum simulation
        self.simulate_quantum = config.get('simulate_quantum', True)
        
    async def initialize(self):
        """Initialize with HAL security discovery"""
        logger.info(f"Initializing quantum mesh v3 at security level: {self.security_level.value}")
        
        # Get hardware manager
        self.hw_manager = self.env.hal
        
        if not self.hw_manager:
            logger.error("HAL required for quantum mesh operations")
            return
            
        # Discover security-capable hardware
        await self._discover_security_hardware()
        
        # Register for hardware events
        self.hw_manager.on_event('adapter_added', self._handle_new_adapter)
        self.hw_manager.on_event('adapter_failed', self._handle_adapter_failure)
        
        # Initialize security protocols
        await self._initialize_security()
        
        # Start key distribution
        asyncio.create_task(self._key_distribution_loop_v3())
        
        # Start intrusion detection
        if self.ids_enabled:
            asyncio.create_task(self._intrusion_detection_loop_v3())
            
        # Start performance monitoring
        asyncio.create_task(self._security_performance_monitoring())
        
        logger.info(f"Quantum mesh v3 initialized with {len(self.security_adapters)} security adapters")
        
    async def _discover_security_hardware(self):
        """Discover adapters with security capabilities"""
        for name, adapter in self.hw_manager.adapters.items():
            capabilities = adapter.get_capabilities()
            
            # Check for security features
            security_features = capabilities.features & {
                'aes', 'rsa', 'ecc', 'sha', 'rng', 'secure_element',
                'quantum', 'post_quantum', 'tpm', 'hsm'
            }
            
            if security_features:
                self.security_adapters[name] = {
                    'adapter': adapter,
                    'features': security_features,
                    'performance': await self._benchmark_crypto_performance(adapter)
                }
                
                # Create node profile
                profile = NodeSecurityProfile(
                    node_id=f"node_{name}",
                    adapter_name=name,
                    capabilities=security_features,
                    trust_score=0.5,  # Initial trust
                    last_seen=datetime.utcnow(),
                    quantum_capable='quantum' in security_features,
                    hardware_health=adapter.health_score,
                    established_channels=[]
                )
                
                self.node_profiles[profile.node_id] = profile
                
                # Track quantum-capable adapters
                if 'quantum' in security_features:
                    self.quantum_adapters[name] = adapter
                    
        logger.info(f"Discovered {len(self.security_adapters)} security adapters, "
                   f"{len(self.quantum_adapters)} quantum-capable")
                   
    async def _benchmark_crypto_performance(self, adapter: HardwareAdapter) -> Dict[str, float]:
        """Benchmark cryptographic performance"""
        performance = {}
        
        # Test data
        test_data = secrets.token_bytes(1024)  # 1KB
        
        # AES-256 benchmark
        try:
            start = datetime.utcnow()
            
            # Simulate AES operation through adapter
            if hasattr(adapter, 'crypto_aes'):
                await adapter.secure_operation(
                    adapter.crypto_aes,
                    test_data,
                    'encrypt'
                )
            else:
                # Software fallback
                key = secrets.token_bytes(32)
                iv = secrets.token_bytes(16)
                cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
                encryptor = cipher.encryptor()
                encryptor.update(test_data) + encryptor.finalize()
                
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            performance['aes_256_ms'] = elapsed
            
        except Exception as e:
            logger.warning(f"AES benchmark failed: {e}")
            performance['aes_256_ms'] = float('inf')
            
        # SHA-256 benchmark
        try:
            start = datetime.utcnow()
            
            if hasattr(adapter, 'crypto_sha256'):
                await adapter.secure_operation(
                    adapter.crypto_sha256,
                    test_data
                )
            else:
                hashlib.sha256(test_data).digest()
                
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            performance['sha_256_ms'] = elapsed
            
        except:
            performance['sha_256_ms'] = float('inf')
            
        # Random number generation
        try:
            start = datetime.utcnow()
            
            if hasattr(adapter, 'crypto_random'):
                await adapter.secure_operation(
                    adapter.crypto_random,
                    256  # bits
                )
            else:
                secrets.token_bytes(32)
                
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            performance['rng_256bit_ms'] = elapsed
            
        except:
            performance['rng_256bit_ms'] = float('inf')
            
        return performance
        
    async def _initialize_security(self):
        """Initialize security protocols based on available hardware"""
        if self.security_level in [SecurityLevel.QUANTUM, SecurityLevel.EXPERIMENTAL]:
            if self.quantum_adapters:
                await self._initialize_quantum_protocols_v3()
            elif self.simulate_quantum:
                logger.info("No quantum hardware found, using simulation")
                await self._initialize_quantum_protocols_v3()
            else:
                logger.warning("Quantum security requested but not available, falling back to enhanced")
                self.security_level = SecurityLevel.ENHANCED
                
        # Initialize post-quantum algorithms for enhanced mode
        if self.security_level == SecurityLevel.ENHANCED:
            await self._initialize_post_quantum()
            
    async def _initialize_quantum_protocols_v3(self):
        """Initialize quantum protocols with hardware optimization"""
        logger.info("Initializing quantum protocols v3")
        
        # Group nodes by capabilities
        quantum_nodes = [
            node_id for node_id, profile in self.node_profiles.items()
            if profile.quantum_capable
        ]
        
        # Establish quantum channels between capable nodes
        for i, node_a in enumerate(quantum_nodes):
            for node_b in quantum_nodes[i+1:]:
                # Select best adapters for channel
                adapter_a = self._select_best_adapter_for_node(node_a)
                adapter_b = self._select_best_adapter_for_node(node_b)
                
                if adapter_a and adapter_b:
                    await self._establish_quantum_channel_v3(
                        node_a, node_b, adapter_a, adapter_b
                    )
                    
    async def _establish_quantum_channel_v3(self, node_a: str, node_b: str,
                                          adapter_a: HardwareAdapter,
                                          adapter_b: HardwareAdapter) -> bool:
        """Establish quantum channel with hardware acceleration"""
        logger.debug(f"Establishing quantum channel: {node_a} <-> {node_b}")
        
        try:
            start_time = datetime.utcnow()
            
            # Check adapter health
            health_a = await adapter_a.health_check()
            health_b = await adapter_b.health_check()
            
            if health_a not in [HardwareHealth.EXCELLENT, HardwareHealth.GOOD] or \
               health_b not in [HardwareHealth.EXCELLENT, HardwareHealth.GOOD]:
                logger.warning("Adapter health insufficient for quantum channel")
                return False
                
            # Perform key distribution
            if self.quantum_enabled and hasattr(adapter_a, 'quantum_qkd'):
                # Hardware QKD
                key = await self._perform_hardware_qkd(adapter_a, adapter_b)
            else:
                # Simulated QKD
                key = await self._simulate_qkd_v3(node_a, node_b, adapter_a, adapter_b)
                
            if key and key.error_rate < self.anomaly_threshold:
                # Store key with quality metrics
                channel_id = self._get_channel_id(node_a, node_b)
                
                self.secure_channels[channel_id] = {
                    'key': key,
                    'established': datetime.utcnow(),
                    'protocol': key.protocol,
                    'usage_count': 0,
                    'adapter_a': adapter_a.adapter_id,
                    'adapter_b': adapter_b.adapter_id,
                    'performance': {
                        'establishment_ms': (datetime.utcnow() - start_time).total_seconds() * 1000,
                        'throughput_bps': key.total_bits / key.generation_latency_ms * 1000
                    }
                }
                
                # Update node profiles
                self.node_profiles[node_a].established_channels.append(channel_id)
                self.node_profiles[node_b].established_channels.append(channel_id)
                
                logger.info(f"Quantum channel established: {channel_id} "
                           f"(QBER: {key.error_rate:.3f}, latency: {key.generation_latency_ms:.1f}ms)")
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to establish quantum channel: {e}")
            
        return False
        
    async def _simulate_qkd_v3(self, node_a: str, node_b: str,
                             adapter_a: HardwareAdapter,
                             adapter_b: HardwareAdapter) -> QuantumKeyV3:
        """Enhanced QKD simulation with hardware metrics"""
        protocol = QuantumProtocol.BB84
        
        # Use hardware RNG if available
        key_length = 256  # bits
        
        if hasattr(adapter_a, 'crypto_random'):
            raw_key = await adapter_a.secure_operation(
                adapter_a.crypto_random,
                key_length // 8
            )
        else:
            raw_key = secrets.token_bytes(key_length // 8)
            
        # Simulate realistic QBER based on hardware health
        hw_health = (adapter_a.health_score + adapter_b.health_score) / 2
        base_qber = 0.02  # 2% base error rate
        
        # Add noise based on hardware condition
        noise_factor = (1.0 - hw_health) * 0.1
        qber = base_qber + noise_factor + np.random.uniform(-0.01, 0.01)
        qber = max(0.001, min(qber, 0.15))  # Clamp between 0.1% and 15%
        
        # Simulate latency
        base_latency = 50  # ms
        
        # Add network latency for remote adapters
        if isinstance(adapter_a, NetworkHardwareAdapter) or \
           isinstance(adapter_b, NetworkHardwareAdapter):
            base_latency += 100
            
        latency = base_latency + np.random.exponential(10)
        
        # Privacy amplification
        final_key = self._privacy_amplification(raw_key, qber)
        
        return QuantumKeyV3(
            key_id=f"qk_{node_a}_{node_b}_{datetime.utcnow().timestamp()}",
            key_material=final_key,
            creation_time=datetime.utcnow(),
            protocol=protocol,
            error_rate=qber,
            total_bits=len(final_key) * 8,
            hardware_health=hw_health,
            generation_latency_ms=latency
        )
        
    def _select_best_adapter_for_node(self, node_id: str) -> Optional[HardwareAdapter]:
        """Select best adapter for cryptographic operations"""
        profile = self.node_profiles.get(node_id)
        if not profile:
            return None
            
        adapter_info = self.security_adapters.get(profile.adapter_name)
        if not adapter_info:
            return None
            
        adapter = adapter_info['adapter']
        
        # Check health
        if adapter.health_score < self.min_hardware_health:
            # Try to find alternative
            for name, info in self.security_adapters.items():
                if info['adapter'].health_score > self.min_hardware_health:
                    return info['adapter']
                    
        return adapter
        
    async def send_secure_v3(self, from_node: str, to_node: str, 
                           data: bytes, priority: str = 'normal') -> bool:
        """Send data with hardware-optimized encryption"""
        channel_id = self._get_channel_id(from_node, to_node)
        
        # Find or establish channel
        if channel_id not in self.secure_channels:
            # Find best adapters
            adapter_from = self._select_best_adapter_for_node(from_node)
            adapter_to = self._select_best_adapter_for_node(to_node)
            
            if not adapter_from or not adapter_to:
                logger.error("No suitable adapters for secure channel")
                return False
                
            if not await self._establish_quantum_channel_v3(
                from_node, to_node, adapter_from, adapter_to
            ):
                logger.error(f"Failed to establish secure channel: {channel_id}")
                return False
                
        channel = self.secure_channels[channel_id]
        key = channel['key']
        
        # Check key quality
        if key.get_quality_score() < self.min_key_quality:
            logger.info("Key quality low, refreshing...")
            # Refresh key
            await self._refresh_channel_key(channel_id)
            key = self.secure_channels[channel_id]['key']
            
        try:
            # Select encryption based on priority and hardware
            if priority == 'critical' and self.security_level == SecurityLevel.QUANTUM:
                encrypted = await self._otp_encrypt_hw(data, key)
            else:
                encrypted = await self._encrypt_data_hw(data, key)
                
            # Send through mesh network
            success = await self.mesh_network.send(
                from_node=from_node,
                to_node=to_node,
                payload=encrypted,
                metadata={
                    'channel_id': channel_id,
                    'encrypted': True,
                    'encryption_type': 'otp' if priority == 'critical' else 'aes',
                    'key_id': key.key_id
                }
            )
            
            # Update usage
            channel['usage_count'] += 1
            
            # Record performance metrics
            self._record_transmission_metrics(channel_id, len(data), success)
            
            return success
            
        except Exception as e:
            logger.error(f"Secure send failed: {e}")
            return False
            
    async def _encrypt_data_hw(self, data: bytes, key: QuantumKeyV3) -> bytes:
        """Hardware-accelerated encryption"""
        # Try hardware acceleration first
        channel_info = next(
            (ch for ch in self.secure_channels.values() if ch['key'] == key),
            None
        )
        
        if channel_info:
            adapter_name = channel_info.get('adapter_a')
            adapter_info = self.security_adapters.get(adapter_name)
            
            if adapter_info and 'aes' in adapter_info['features']:
                adapter = adapter_info['adapter']
                
                # Use hardware AES if available
                if hasattr(adapter, 'crypto_aes'):
                    return await adapter.secure_operation(
                        adapter.crypto_aes,
                        data,
                        'encrypt',
                        key=key.key_material[:32]
                    )
                    
        # Software fallback
        iv = secrets.token_bytes(12)
        cipher = Cipher(
            algorithms.AES(key.key_material[:32]),
            modes.GCM(iv)
        )
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(data) + encryptor.finalize()
        
        return iv + ciphertext + encryptor.tag
        
    async def _intrusion_detection_loop_v3(self):
        """Enhanced IDS with hardware monitoring"""
        while True:
            try:
                # Check for anomalies
                anomalies = await self._detect_anomalies_v3()
                
                for anomaly in anomalies:
                    await self._handle_security_event(anomaly)
                    
                # Update trust scores based on behavior
                await self._update_trust_scores()
                
                # Check hardware security status
                await self._verify_hardware_security()
                
            except Exception as e:
                logger.error(f"IDS error: {e}")
                
            await asyncio.sleep(30)
            
    async def _detect_anomalies_v3(self) -> List[Dict]:
        """Detect anomalies including hardware-based attacks"""
        anomalies = []
        
        # Standard anomaly detection
        anomalies.extend(await self._check_traffic_anomalies())
        anomalies.extend(await self._check_auth_failures())
        
        # Quantum channel anomalies
        if self.security_level in [SecurityLevel.QUANTUM, SecurityLevel.EXPERIMENTAL]:
            anomalies.extend(await self._check_quantum_anomalies())
            
        # Hardware security anomalies
        anomalies.extend(await self._check_hardware_anomalies())
        
        return anomalies
        
    async def _check_hardware_anomalies(self) -> List[Dict]:
        """Check for hardware-based security issues"""
        anomalies = []
        
        # Check for sudden health degradation
        for name, adapter_info in self.security_adapters.items():
            adapter = adapter_info['adapter']
            current_health = adapter.health_score
            
            # Get historical health
            profile = next(
                (p for p in self.node_profiles.values() if p.adapter_name == name),
                None
            )
            
            if profile and profile.hardware_health - current_health > 0.3:
                anomalies.append({
                    'type': 'hardware_degradation',
                    'adapter': name,
                    'previous_health': profile.hardware_health,
                    'current_health': current_health,
                    'severity': 'warning',
                    'timestamp': datetime.utcnow()
                })
                
            # Update profile
            if profile:
                profile.hardware_health = current_health
                
        # Check for timing attacks
        for channel_id, channel in self.secure_channels.items():
            if 'performance' in channel:
                current_latency = channel['performance'].get('establishment_ms', 0)
                
                # Detect significant latency increases (possible side-channel attack)
                if current_latency > self.max_key_latency_ms * 2:
                    anomalies.append({
                        'type': 'timing_anomaly',
                        'channel': channel_id,
                        'latency_ms': current_latency,
                        'severity': 'warning',
                        'timestamp': datetime.utcnow()
                    })
                    
        return anomalies
        
    async def _handle_adapter_failure(self, event_data: Dict):
        """Handle security adapter failures"""
        failed_adapter = event_data['name']
        
        logger.critical(f"Security adapter failed: {failed_adapter}")
        
        # Find affected channels
        affected_channels = []
        for channel_id, channel in self.secure_channels.items():
            if channel.get('adapter_a') == failed_adapter or \
               channel.get('adapter_b') == failed_adapter:
                affected_channels.append(channel_id)
                
        # Invalidate affected channels
        for channel_id in affected_channels:
            logger.warning(f"Invalidating channel due to adapter failure: {channel_id}")
            del self.secure_channels[channel_id]
            
        # Try to re-establish with alternative adapters
        for channel_id in affected_channels:
            node_a, node_b = self._parse_channel_id(channel_id)
            
            # Find alternative adapters
            alt_adapter_a = self._find_alternative_adapter(node_a, failed_adapter)
            alt_adapter_b = self._find_alternative_adapter(node_b, failed_adapter)
            
            if alt_adapter_a and alt_adapter_b:
                asyncio.create_task(
                    self._establish_quantum_channel_v3(
                        node_a, node_b, alt_adapter_a, alt_adapter_b
                    )
                )
                
    def _find_alternative_adapter(self, node_id: str, 
                                 failed_adapter: str) -> Optional[HardwareAdapter]:
        """Find alternative security adapter"""
        profile = self.node_profiles.get(node_id)
        
        if not profile or profile.adapter_name == failed_adapter:
            # Need different adapter
            for name, adapter_info in self.security_adapters.items():
                if name != failed_adapter and \
                   adapter_info['adapter'].health_score > self.min_hardware_health:
                    return adapter_info['adapter']
                    
        return self._select_best_adapter_for_node(node_id)
        
    async def get_security_metrics_v3(self) -> Dict[str, Any]:
        """Get comprehensive security metrics"""
        # Calculate channel statistics
        total_channels = len(self.secure_channels)
        quantum_channels = sum(
            1 for ch in self.secure_channels.values()
            if ch['key'].protocol in [QuantumProtocol.BB84, QuantumProtocol.E91]
        )
        
        # Average key quality
        if self.secure_channels:
            avg_key_quality = sum(
                ch['key'].get_quality_score() 
                for ch in self.secure_channels.values()
            ) / len(self.secure_channels)
        else:
            avg_key_quality = 0
            
        # Hardware health
        security_hw_health = {}
        for name, adapter_info in self.security_adapters.items():
            security_hw_health[name] = {
                'health_score': adapter_info['adapter'].health_score,
                'features': list(adapter_info['features']),
                'performance': adapter_info['performance']
            }
            
        return {
            'security_level': self.security_level.value,
            'total_nodes': len(self.node_profiles),
            'quantum_capable_nodes': len(self.quantum_adapters),
            'active_channels': total_channels,
            'quantum_channels': quantum_channels,
            'average_key_quality': avg_key_quality,
            'intrusion_attempts': len(self.suspicious_activity),
            'hardware_health': security_hw_health,
            'average_qber': self._calculate_average_qber(),
            'last_key_refresh': max(
                (ch['established'] for ch in self.secure_channels.values()),
                default=datetime.utcnow()
            ).isoformat()
        }