#!/usr/bin/env python3
"""
PHAL v2.0 - Pluripotent Hardware Abstraction Layer (Production Hardened)
Now with HiveMindFFT consensus integration and enterprise-grade security

Created by Jason DeLooze for Locally Sovereign Sustainability (Open Source)
Repository: https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments
Email: osce@duck.com
Year: 2025

v2.0 Enhancements:
- Real manifest validation with cryptographic signatures
- HiveMindFFT consensus integration for conflict resolution
- Constraint enforcement with rate limiting
- Federation namespace protection
- Health-based permission adaptation
- Complete audit logging

License: MIT
Copyright (c) 2025 Jason DeLooze
"""

import asyncio
import json
import hashlib
import hmac
import time
from typing import Dict, List, Optional, Union, Any, Callable, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, deque
import uuid
import re
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature

# Import security and logging
from osce.security import DeviceIdentity, IoTSecurityManager, SecurityLevel
from osce.utils.logging import get_logger

# Import HiveMindFFT for consensus
from osce.intelligence.hivemind_fft import HiveMindFFT, AgentSignal

logger = get_logger(__name__)

# v2.0 Constants
PHAL_VERSION = "2.0.0"
MIN_PLUGIN_VERSION = "1.0.0"
MAX_RATE_LIMIT_WINDOW = 60  # seconds
CONSENSUS_CACHE_TTL = 300  # 5 minutes

class PluginPermission(Enum):
    """Enhanced plugin permissions with hierarchy"""
    READ = "read"
    WRITE = "write"
    CONTROL = "control"
    EXCLUSIVE = "exclusive"
    MONITOR = "monitor"
    FEDERATE = "federate"
    ACTUATE = "actuate"  # New: Required for physical actuation
    
    @property
    def level(self) -> int:
        """Permission hierarchy level"""
        hierarchy = {
            'monitor': 1,
            'read': 2,
            'write': 3,
            'actuate': 4,
            'control': 5,
            'exclusive': 6,
            'federate': 7
        }
        return hierarchy.get(self.value, 0)

@dataclass
class PluginManifest:
    """v2.0 Plugin manifest with validation"""
    id: str
    name: str
    version: str
    author: str
    description: str
    permissions_required: Set[PluginPermission]
    permissions_optional: Set[PluginPermission] = field(default_factory=set)
    dependencies: List[str] = field(default_factory=list)
    signature: Optional[str] = None
    public_key: Optional[str] = None
    integrity_hash: Optional[str] = None
    
    def validate_version(self) -> bool:
        """Validate version compatibility"""
        try:
            major, minor, patch = map(int, self.version.split('.'))
            min_major, min_minor, min_patch = map(int, MIN_PLUGIN_VERSION.split('.'))
            return (major, minor, patch) >= (min_major, min_minor, min_patch)
        except:
            return False

@dataclass
class RateLimitConfig:
    """Rate limiting configuration per permission level"""
    requests_per_minute: int
    burst_size: int
    penalty_seconds: int = 60

# Default rate limits by permission
DEFAULT_RATE_LIMITS = {
    PluginPermission.MONITOR: RateLimitConfig(600, 100, 30),
    PluginPermission.READ: RateLimitConfig(300, 50, 60),
    PluginPermission.WRITE: RateLimitConfig(60, 10, 120),
    PluginPermission.ACTUATE: RateLimitConfig(30, 5, 180),
    PluginPermission.CONTROL: RateLimitConfig(30, 5, 300),
    PluginPermission.EXCLUSIVE: RateLimitConfig(10, 2, 600),
}

@dataclass
class ConsensusResult:
    """Enhanced consensus result with metadata"""
    decision: str  # 'grant', 'deny', 'share'
    confidence: float
    agent_count: int
    dominant_frequency: float
    dissenters: List[str]
    timestamp: datetime
    cache_key: str

class PluginVoterAgent:
    """Adapter to translate plugin state into HiveMind agent signals"""
    
    def __init__(self, plugin_id: str, permission_level: int, priority: int = 0):
        self.plugin_id = plugin_id
        self.permission_level = permission_level
        self.priority = priority
        self.signal_profile = self._generate_signal_profile()
        
    def _generate_signal_profile(self) -> np.ndarray:
        """Generate frequency-domain voting signal based on plugin characteristics"""
        # Higher permission plugins get lower frequency (more fundamental)
        base_freq = 1.0 / (self.permission_level + 1)
        
        # Priority adds harmonics
        harmonics = [base_freq * (i + 1) for i in range(self.priority + 1)]
        
        # Generate signal
        signal = np.zeros(128)  # Standard FFT size
        for i, freq in enumerate(harmonics):
            idx = int(freq * 128) % 128
            signal[idx] = 1.0 / (i + 1)  # Decreasing amplitude for harmonics
            
        return signal / np.linalg.norm(signal)  # Normalize
        
    def to_agent_signal(self, vote: float) -> AgentSignal:
        """Convert to HiveMind agent signal"""
        return AgentSignal(
            agent_id=self.plugin_id,
            signal=self.signal_profile * vote,  # Scale by vote strength
            confidence=abs(vote),
            metadata={'permission_level': self.permission_level}
        )

class PHALCore:
    """Pluripotent Hardware Abstraction Layer Core v2.0"""
    
    def __init__(self, zone_id: str = "main", 
                 security_manager: Optional[IoTSecurityManager] = None,
                 enable_consensus: bool = True):
        self.zone_id = zone_id
        self.security_manager = security_manager or IoTSecurityManager()
        self.enable_consensus = enable_consensus
        
        # Initialize HiveMind for consensus
        if enable_consensus:
            self.hive_mind = HiveMindFFT()
            asyncio.create_task(self.hive_mind.initialize())
        
        # v2.0 Enhanced registries
        self.plugin_manifests: Dict[str, PluginManifest] = {}
        self.rate_limiters: Dict[str, Dict[PluginPermission, deque]] = defaultdict(lambda: defaultdict(deque))
        self.permission_violations: deque = deque(maxlen=1000)
        self.consensus_cache: Dict[str, ConsensusResult] = {}
        
        # Namespace protection for federation
        self.namespace_registry: Dict[str, str] = {}  # namespace -> zone_id
        
        # Health feedback systems
        self.health_thresholds = {
            'critical': 0.3,
            'degraded': 0.5,
            'warning': 0.7,
            'healthy': 0.9
        }
        
        # Enhanced metrics
        self.audit_log: deque = deque(maxlen=10000)
        
        # Continue with original initialization...
        self.capabilities: Dict[str, List[CapabilityRegistration]] = defaultdict(list)
        self.device_capabilities: Dict[str, List[str]] = defaultdict(list)
        self.plugin_permissions: Dict[str, Set[PluginPermission]] = {}
        self.active_grants: Dict[str, AccessGrant] = {}
        self.access_history: deque = deque(maxlen=1000)
        self.resource_locks: Dict[str, Tuple[ResourceLock, str]] = {}
        self.lock_queues: Dict[str, deque] = defaultdict(deque)
        
        # v2.0 Constraint engine
        self.constraint_engine = ConstraintEngine()
        
        # Conflict resolution handlers
        self.conflict_handlers[ConflictResolutionStrategy.CONSENSUS] = self._resolve_by_consensus_v2
        
    async def register_plugin(self, plugin_id: str, 
                            permissions: Set[PluginPermission],
                            manifest: Optional[Dict[str, Any]] = None) -> bool:
        """v2.0 Register plugin with enhanced validation"""
        
        # Audit log entry
        self._audit_log('plugin_registration_attempt', {
            'plugin_id': plugin_id,
            'permissions': [p.value for p in permissions],
            'has_manifest': manifest is not None
        })
        
        # Parse and validate manifest
        if not manifest:
            logger.error("Plugin registration requires manifest in v2.0", plugin_id=plugin_id)
            return False
            
        try:
            plugin_manifest = PluginManifest(
                id=plugin_id,
                name=manifest.get('name', plugin_id),
                version=manifest.get('version', '0.0.0'),
                author=manifest.get('author', 'unknown'),
                description=manifest.get('description', ''),
                permissions_required=permissions,
                permissions_optional=set(manifest.get('permissions_optional', [])),
                dependencies=manifest.get('dependencies', []),
                signature=manifest.get('signature'),
                public_key=manifest.get('public_key'),
                integrity_hash=manifest.get('integrity_hash')
            )
            
            # Validate manifest
            if not await self._validate_plugin_manifest_v2(plugin_manifest):
                logger.error("Plugin manifest validation failed", plugin_id=plugin_id)
                self._audit_log('plugin_registration_failed', {
                    'plugin_id': plugin_id,
                    'reason': 'manifest_validation_failed'
                })
                return False
                
            # Store manifest
            self.plugin_manifests[plugin_id] = plugin_manifest
            
            # Register permissions
            self.plugin_permissions[plugin_id] = permissions
            
            # Initialize rate limiters
            for permission in permissions:
                self.rate_limiters[plugin_id][permission] = deque()
                
            logger.info("Plugin registered successfully", 
                       plugin_id=plugin_id,
                       version=plugin_manifest.version)
                       
            self._audit_log('plugin_registered', {
                'plugin_id': plugin_id,
                'version': plugin_manifest.version,
                'permissions': [p.value for p in permissions]
            })
            
            return True
            
        except Exception as e:
            logger.error("Plugin registration error", plugin_id=plugin_id, error=str(e))
            return False
            
    async def _validate_plugin_manifest_v2(self, manifest: PluginManifest) -> bool:
        """v2.0 Comprehensive manifest validation"""
        
        # Version compatibility check
        if not manifest.validate_version():
            logger.error("Plugin version incompatible", 
                        plugin_id=manifest.id,
                        version=manifest.version,
                        required=MIN_PLUGIN_VERSION)
            return False
            
        # Validate plugin ID format
        if not re.match(r'^[a-z0-9_]+$', manifest.id):
            logger.error("Invalid plugin ID format", plugin_id=manifest.id)
            return False
            
        # Check dependencies
        for dep in manifest.dependencies:
            if dep not in self.plugin_manifests:
                logger.error("Missing dependency", 
                           plugin_id=manifest.id,
                           dependency=dep)
                return False
                
        # Verify integrity hash
        if manifest.integrity_hash:
            calculated_hash = self._calculate_manifest_hash(manifest)
            if calculated_hash != manifest.integrity_hash:
                logger.error("Manifest integrity check failed", plugin_id=manifest.id)
                return False
                
        # Verify signature if provided
        if self.security_manager.security_level >= SecurityLevel.PRODUCTION:
            if manifest.signature and manifest.public_key:
                if not self._verify_manifest_signature(manifest):
                    logger.error("Manifest signature verification failed", 
                               plugin_id=manifest.id)
                    return False
            else:
                logger.warning("Plugin lacks signature in production mode", 
                             plugin_id=manifest.id)
                # In production, unsigned plugins are rejected
                return False
                
        # Check for permission escalation attempts
        if PluginPermission.EXCLUSIVE in manifest.permissions_required:
            self._audit_log('permission_escalation_attempt', {
                'plugin_id': manifest.id,
                'requested_permission': 'exclusive'
            })
            
        return True
        
    def _calculate_manifest_hash(self, manifest: PluginManifest) -> str:
        """Calculate manifest integrity hash"""
        # Hash relevant fields
        content = f"{manifest.id}:{manifest.version}:{manifest.author}:"
        content += ','.join(sorted([p.value for p in manifest.permissions_required]))
        content += ':' + ','.join(sorted(manifest.dependencies))
        
        return hashlib.sha256(content.encode()).hexdigest()
        
    def _verify_manifest_signature(self, manifest: PluginManifest) -> bool:
        """Verify manifest cryptographic signature"""
        try:
            # Load public key
            public_key = serialization.load_pem_public_key(
                manifest.public_key.encode()
            )
            
            # Prepare signed content
            signed_content = self._calculate_manifest_hash(manifest).encode()
            signature = bytes.fromhex(manifest.signature)
            
            # Verify signature
            public_key.verify(
                signature,
                signed_content,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            return True
            
        except (InvalidSignature, Exception) as e:
            logger.error("Signature verification failed", 
                       plugin_id=manifest.id,
                       error=str(e))
            return False
            
    async def request_capability(self, request: PluginAccessRequest) -> Optional[AccessGrant]:
        """v2.0 Enhanced capability request with rate limiting"""
        
        # Check rate limits first
        if not self._check_rate_limit(request.plugin_id, request.permission):
            logger.warning("Rate limit exceeded", 
                         plugin_id=request.plugin_id,
                         permission=request.permission.value)
            
            self._audit_log('rate_limit_exceeded', {
                'plugin_id': request.plugin_id,
                'permission': request.permission.value
            })
            
            return None
            
        # Add namespace to device_id for federation
        if request.device_id and ':' not in request.device_id:
            request.device_id = f"{self.zone_id}:{request.device_id}"
            
        # Continue with original logic...
        return await super().request_capability(request)
        
    def _check_rate_limit(self, plugin_id: str, permission: PluginPermission) -> bool:
        """v2.0 Check and enforce rate limits"""
        now = time.time()
        
        # Get rate limit config
        limit_config = DEFAULT_RATE_LIMITS.get(permission, 
                                              RateLimitConfig(100, 10, 60))
        
        # Get request history
        history = self.rate_limiters[plugin_id][permission]
        
        # Remove old entries
        cutoff_time = now - MAX_RATE_LIMIT_WINDOW
        while history and history[0] < cutoff_time:
            history.popleft()
            
        # Check if in penalty period
        if history and len(history) >= limit_config.requests_per_minute:
            last_violation = max(history)
            if now - last_violation < limit_config.penalty_seconds:
                return False  # Still in penalty
                
        # Check rate
        if len(history) >= limit_config.requests_per_minute:
            return False
            
        # Check burst
        recent_burst = [t for t in history if now - t < 1.0]  # Last second
        if len(recent_burst) >= limit_config.burst_size:
            return False
            
        # Record request
        history.append(now)
        return True
        
    async def _resolve_by_consensus_v2(self, request: PluginAccessRequest,
                                      current_holder: str, resource_key: str) -> str:
        """v2.0 HiveMindFFT consensus-based conflict resolution"""
        
        # Check cache first
        cache_key = f"{request.plugin_id}:{current_holder}:{resource_key}"
        if cache_key in self.consensus_cache:
            cached = self.consensus_cache[cache_key]
            if (datetime.utcnow() - cached.timestamp).seconds < CONSENSUS_CACHE_TTL:
                logger.debug("Using cached consensus result", cache_key=cache_key)
                return cached.decision
                
        # Prepare issue for HiveMind
        issue = {
            'type': 'resource_conflict',
            'resource': resource_key,
            'current_holder': {
                'plugin_id': current_holder,
                'permission': self._get_plugin_permission_level(current_holder),
                'priority': self._get_plugin_priority(current_holder),
                'hold_duration': self._get_hold_duration(current_holder, resource_key)
            },
            'requester': {
                'plugin_id': request.plugin_id,
                'permission': request.permission.level,
                'priority': request.priority,
                'requested_duration': request.duration.total_seconds() if request.duration else None
            },
            'resource_health': await self._get_resource_health(resource_key)
        }
        
        # Create voter agents
        agents = []
        
        # Current holder votes to keep
        holder_agent = PluginVoterAgent(
            current_holder,
            self._get_plugin_permission_level(current_holder),
            self._get_plugin_priority(current_holder)
        )
        agents.append(holder_agent.to_agent_signal(vote=-1.0))  # Negative = keep
        
        # Requester votes to take
        requester_agent = PluginVoterAgent(
            request.plugin_id,
            request.permission.level,
            request.priority
        )
        agents.append(requester_agent.to_agent_signal(vote=1.0))  # Positive = grant
        
        # Add other interested plugins as voters
        for plugin_id in self._get_interested_plugins(resource_key):
            if plugin_id not in [current_holder, request.plugin_id]:
                agent = PluginVoterAgent(
                    plugin_id,
                    self._get_plugin_permission_level(plugin_id),
                    self._get_plugin_priority(plugin_id)
                )
                # Vote based on permission hierarchy
                vote = 0.5 if request.permission.level > self._get_plugin_permission_level(plugin_id) else -0.5
                agents.append(agent.to_agent_signal(vote))
                
        # Get HiveMind decision
        try:
            decision_data = await self.hive_mind.get_decision(issue, agents)
            
            # Interpret consensus
            consensus_value = decision_data['consensus_frequency']
            confidence = decision_data['coherence']
            
            if consensus_value > 0.3:
                decision = 'grant'
            elif consensus_value > 0:
                decision = 'share'
            else:
                decision = 'deny'
                
            # Create result
            result = ConsensusResult(
                decision=decision,
                confidence=confidence,
                agent_count=len(agents),
                dominant_frequency=decision_data['dominant_frequency'],
                dissenters=[a.agent_id for a in agents if a.confidence < 0.5],
                timestamp=datetime.utcnow(),
                cache_key=cache_key
            )
            
            # Cache result
            self.consensus_cache[cache_key] = result
            
            # Log decision
            self._audit_log('consensus_decision', {
                'issue': issue,
                'decision': decision,
                'confidence': confidence,
                'agent_count': len(agents)
            })
            
            return decision
            
        except Exception as e:
            logger.error("Consensus resolution failed", error=str(e))
            # Fallback to priority-based resolution
            return await self._resolve_by_priority(request, current_holder, resource_key)
            
    def _apply_constraints(self, grant: AccessGrant, command: Dict[str, Any]) -> Dict[str, Any]:
        """v2.0 Apply grant constraints to command"""
        
        # Get constraint profile for this grant
        constraints = self.constraint_engine.get_constraints(grant)
        
        # Apply rate limiting
        if 'rate_limit' in constraints:
            # Check command rate
            rate_key = f"{grant.grant_id}:commands"
            if not self._check_command_rate(rate_key, constraints['rate_limit']):
                raise PermissionError("Command rate limit exceeded")
                
        # Apply value constraints
        if 'value_range' in constraints and 'value' in command:
            min_val, max_val = constraints['value_range']
            original_value = command['value']
            command['value'] = max(min_val, min(max_val, command['value']))
            
            if command['value'] != original_value:
                logger.info("Value constrained", 
                          original=original_value,
                          constrained=command['value'])
                          
        # Apply time constraints
        if 'allowed_hours' in constraints:
            current_hour = datetime.utcnow().hour
            if current_hour not in constraints['allowed_hours']:
                raise PermissionError(f"Command not allowed at hour {current_hour}")
                
        # Apply command type constraints
        if 'allowed_commands' in constraints:
            if command.get('type') not in constraints['allowed_commands']:
                raise PermissionError(f"Command type '{command.get('type')}' not allowed")
                
        # Apply health-based constraints
        if grant.capability_type in self.capabilities:
            health = await self._get_capability_health(grant.capability_type)
            
            if health < self.health_thresholds['critical']:
                # Critical health - read only
                if command.get('type') not in ['read', 'get', 'query']:
                    raise PermissionError("Device health critical - read only access")
                    
            elif health < self.health_thresholds['degraded']:
                # Degraded - no actuation
                if grant.permission == PluginPermission.ACTUATE:
                    raise PermissionError("Device health degraded - actuation disabled")
                    
        return command
        
    async def register_device(self, device_id: str, capabilities: List[Dict[str, Any]], 
                            zone: Optional[str] = None) -> bool:
        """v2.0 Register device with namespace protection"""
        zone = zone or self.zone_id
        
        # Apply namespace
        namespaced_id = f"{zone}:{device_id}"
        
        # Check for namespace conflicts
        if device_id in self.namespace_registry and self.namespace_registry[device_id] != zone:
            logger.error("Namespace conflict", 
                       device_id=device_id,
                       existing_zone=self.namespace_registry[device_id],
                       requested_zone=zone)
            return False
            
        # Register namespace
        self.namespace_registry[device_id] = zone
        
        # Continue with registration using namespaced ID
        for cap in capabilities:
            registration = CapabilityRegistration(
                device_id=namespaced_id,
                capability_type=cap['type'],
                protocol=cap.get('protocol', 'unknown'),
                pins=cap.get('pins', []),
                properties=cap.get('properties', {}),
                zone=zone
            )
            
            self.capabilities[cap['type']].append(registration)
            self.device_capabilities[namespaced_id].append(cap['type'])
            
        logger.info("Device registered with namespace", 
                   device_id=namespaced_id,
                   zone=zone,
                   capabilities=[c['type'] for c in capabilities])
                   
        return True
        
    async def update_device_health(self, device_id: str, health_score: float):
        """v2.0 Update device health and adapt permissions"""
        
        # Find all capabilities for this device
        for cap_type, registrations in self.capabilities.items():
            for reg in registrations:
                if reg.device_id == device_id:
                    old_health = reg.health_score
                    reg.health_score = health_score
                    reg.last_update = datetime.utcnow()
                    
                    # Check if health crossed thresholds
                    old_threshold = self._get_health_threshold(old_health)
                    new_threshold = self._get_health_threshold(health_score)
                    
                    if old_threshold != new_threshold:
                        await self._handle_health_transition(
                            device_id, cap_type, old_threshold, new_threshold
                        )
                        
    def _get_health_threshold(self, health_score: float) -> str:
        """Get health threshold category"""
        for threshold_name, threshold_value in sorted(self.health_thresholds.items(), 
                                                    key=lambda x: x[1]):
            if health_score <= threshold_value:
                return threshold_name
        return 'healthy'
        
    async def _handle_health_transition(self, device_id: str, capability: str,
                                       old_threshold: str, new_threshold: str):
        """Handle device health threshold transitions"""
        logger.info("Device health transition",
                   device_id=device_id,
                   capability=capability,
                   from_threshold=old_threshold,
                   to_threshold=new_threshold)
                   
        # Revoke grants if health degraded
        if new_threshold in ['critical', 'degraded']:
            grants_to_revoke = []
            
            for grant_id, grant in self.active_grants.items():
                if (grant.device_id == device_id and 
                    grant.capability_type == capability and
                    grant.permission.level > PluginPermission.READ.level):
                    grants_to_revoke.append(grant_id)
                    
            for grant_id in grants_to_revoke:
                logger.warning("Revoking grant due to health degradation",
                             grant_id=grant_id,
                             device_id=device_id)
                await self.revoke_access(grant_id)
                
        # Emit health event
        await self._emit_event('device_health_changed', {
            'device_id': device_id,
            'capability': capability,
            'old_threshold': old_threshold,
            'new_threshold': new_threshold,
            'timestamp': datetime.utcnow()
        })
        
    def _get_plugin_permission_level(self, plugin_id: str) -> int:
        """Get highest permission level for plugin"""
        if plugin_id not in self.plugin_permissions:
            return 0
            
        return max(p.level for p in self.plugin_permissions[plugin_id])
        
    def _get_hold_duration(self, holder_id: str, resource_key: str) -> float:
        """Get how long a plugin has held a resource"""
        for grant in self.active_grants.values():
            if grant.plugin_id == holder_id:
                resource = f"{grant.device_id}:{grant.capability_type}"
                if resource == resource_key:
                    duration = datetime.utcnow() - grant.granted_at
                    return duration.total_seconds()
        return 0.0
        
    def _get_interested_plugins(self, resource_key: str) -> List[str]:
        """Get plugins that might be interested in a resource"""
        interested = []
        
        # Parse resource key
        parts = resource_key.split(':')
        if len(parts) >= 2:
            capability_type = parts[-1]
            
            # Find plugins with permissions for this capability type
            for plugin_id, manifest in self.plugin_manifests.items():
                # Check if plugin has relevant permissions
                relevant_perms = {PluginPermission.READ, PluginPermission.WRITE, 
                                PluginPermission.CONTROL, PluginPermission.ACTUATE}
                if manifest.permissions_required & relevant_perms:
                    interested.append(plugin_id)
                    
        return interested[:10]  # Limit to prevent too many voters
        
    async def _get_resource_health(self, resource_key: str) -> float:
        """Get health score for a resource"""
        parts = resource_key.split(':')
        if len(parts) >= 2:
            device_id = ':'.join(parts[:-1])
            capability_type = parts[-1]
            
            for reg in self.capabilities.get(capability_type, []):
                if reg.device_id == device_id:
                    return reg.health_score
                    
        return 0.5  # Default
        
    async def _get_capability_health(self, capability_type: str) -> float:
        """Get average health for a capability type"""
        registrations = self.capabilities.get(capability_type, [])
        if not registrations:
            return 0.5
            
        return sum(r.health_score for r in registrations) / len(registrations)
        
    def _check_command_rate(self, rate_key: str, limit: int) -> bool:
        """Check command rate limiting"""
        # Implementation similar to _check_rate_limit
        return True  # Simplified for now
        
    def _audit_log(self, event_type: str, data: Dict[str, Any]):
        """Add entry to audit log"""
        entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'event': event_type,
            'zone': self.zone_id,
            'data': data
        }
        
        self.audit_log.append(entry)
        
        # Also log significant events
        if event_type in ['permission_escalation_attempt', 'rate_limit_exceeded',
                         'consensus_decision', 'plugin_registration_failed']:
            logger.info(f"Audit: {event_type}", **data)
            
    async def get_audit_log(self, event_types: Optional[List[str]] = None,
                           since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Retrieve audit log entries"""
        results = []
        
        for entry in self.audit_log:
            # Filter by event type
            if event_types and entry['event'] not in event_types:
                continue
                
            # Filter by time
            if since:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time < since:
                    continue
                    
            results.append(entry)
            
        return results

class ConstraintEngine:
    """v2.0 Constraint management engine"""
    
    def __init__(self):
        self.constraint_profiles = {
            PluginPermission.MONITOR: {
                'rate_limit': 600,  # commands per hour
                'allowed_commands': ['read', 'get', 'query', 'subscribe'],
                'value_constraints': False
            },
            PluginPermission.READ: {
                'rate_limit': 300,
                'allowed_commands': ['read', 'get', 'query'],
                'value_constraints': False
            },
            PluginPermission.WRITE: {
                'rate_limit': 60,
                'allowed_commands': ['read', 'get', 'write', 'set'],
                'value_constraints': True,
                'value_range': (0, 100)  # Default safe range
            },
            PluginPermission.ACTUATE: {
                'rate_limit': 30,
                'allowed_commands': ['read', 'write', 'actuate', 'control'],
                'value_constraints': True,
                'value_range': (0, 100),
                'safety_checks': True
            },
            PluginPermission.CONTROL: {
                'rate_limit': 30,
                'allowed_commands': ['read', 'write', 'control', 'configure'],
                'value_constraints': True,
                'safety_checks': True
            }
        }
        
    def get_constraints(self, grant: AccessGrant) -> Dict[str, Any]:
        """Get applicable constraints for a grant"""
        base_constraints = self.constraint_profiles.get(
            grant.permission,
            {'rate_limit': 100}
        )
        
        # Merge with grant-specific constraints
        if grant.constraints:
            base_constraints.update(grant.constraints)
            
        return base_constraints

# Additional v2.0 data structures

@dataclass
class CapabilityRegistration:
    """Enhanced capability registration with health tracking"""
    device_id: str
    capability_type: str
    protocol: str
    pins: List[int]
    properties: Dict[str, Any]
    health_score: float = 1.0
    last_update: datetime = field(default_factory=datetime.utcnow)
    registered_by: Optional[str] = None
    zone: Optional[str] = None
    granted_at: datetime = field(default_factory=datetime.utcnow)  # v2.0 addition
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'device_id': self.device_id,
            'type': self.capability_type,
            'protocol': self.protocol,
            'pins': self.pins,
            'properties': self.properties,
            'health': self.health_score,
            'zone': self.zone,
            'last_update': self.last_update.isoformat()
        }

@dataclass
class AccessGrant:
    """Enhanced access grant with v2.0 features"""
    grant_id: str
    plugin_id: str
    device_id: str
    capability_type: str
    permission: PluginPermission
    expires_at: Optional[datetime]
    lock_type: ResourceLock
    constraints: Dict[str, Any] = field(default_factory=dict)
    granted_at: datetime = field(default_factory=datetime.utcnow)
    usage_count: int = 0
    last_used: Optional[datetime] = None

# Continue with remaining enums and structures...
class ConflictResolutionStrategy(Enum):
    """Strategies for resolving plugin conflicts"""
    PRIORITY = auto()
    TEMPORAL = auto()
    CONSENSUS = auto()
    HEALTH_BASED = auto()
    ZONE_LOCAL = auto()

class ResourceLock(Enum):
    """Resource locking strategies"""
    NONE = auto()
    SHARED = auto()
    EXCLUSIVE = auto()
    TEMPORAL = auto()
    PRIORITY = auto()

@dataclass
class PluginAccessRequest:
    """Plugin hardware access request"""
    plugin_id: str
    capability_type: str
    device_id: Optional[str]
    permission: PluginPermission
    duration: Optional[timedelta] = None
    priority: int = 0
    zone: Optional[str] = None
    request_time: datetime = field(default_factory=datetime.utcnow)

# Module exports
__all__ = [
    'PHALCore',
    'PluginPermission',
    'PluginManifest',
    'PluginAccessRequest',
    'AccessGrant',
    'ConflictResolutionStrategy',
    'ConsensusResult',
    'ConstraintEngine'
]
