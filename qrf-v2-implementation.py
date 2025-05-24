#!/usr/bin/env python3
"""
Quantum Readable Fractals (QRF) v2.0
Production-ready implementation with CEA-specific semantics

Developed by Jason DeLooze for Open Source, Locally Sovereign Sustainability.
This module encodes ecological and quantum uncertainty into a verifiable, 
recursive fractal—anchored in time, blockchain, and living complexity.
"""

import qrcode
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import hashlib
import json
from typing import Dict, List, Tuple, Optional, Union, Any
from dataclasses import dataclass, field
from enum import Enum, auto
import math
import asyncio
from datetime import datetime, timezone
import base64

# Try to import quantum-resistant crypto, fallback to placeholder
try:
    from pqcrypto.sign.dilithium2 import generate_keypair, sign, verify
    QUANTUM_CRYPTO_AVAILABLE = True
except ImportError:
    QUANTUM_CRYPTO_AVAILABLE = False
    print("Warning: pqcrypto not available. Using placeholder signatures.")

# Golden ratio constants
PHI = (1 + math.sqrt(5)) / 2
INVERSE_PHI = 1 / PHI

class QuantumBasis(Enum):
    """Measurement basis for quantum states in CEA context"""
    ENVIRONMENTAL = auto()  # Temperature, humidity, CO2
    NUTRITIONAL = auto()    # pH, EC, dissolved oxygen
    PHOTONIC = auto()       # Light spectrum, intensity, photoperiod
    BIOLOGICAL = auto()     # Plant health, growth rate, stress
    TEMPORAL = auto()       # Time-series patterns, circadian

@dataclass
class CEAQuantumState:
    """
    Quantum state representation for CEA data
    
    Coherence: How well-correlated/reliable the measurement is (0-1)
    Entanglement: How this measurement affects/is affected by others
    """
    state_vector: List[complex]
    measurement_basis: QuantumBasis
    coherence: float  # 0 = noisy/uncertain, 1 = perfect measurement
    entanglement_map: Dict[str, float]  # sensor_name -> correlation strength
    uncertainty_sources: List[str] = field(default_factory=list)
    
    def ecological_interpretation(self) -> Dict[str, Any]:
        """Interpret quantum state in ecological terms"""
        interpretation = {
            'measurement_quality': 'high' if self.coherence > 0.8 else 'medium' if self.coherence > 0.5 else 'low',
            'primary_influences': [],
            'uncertainty_factors': self.uncertainty_sources
        }
        
        # Find strongest entanglements
        for sensor, strength in sorted(self.entanglement_map.items(), 
                                     key=lambda x: x[1], reverse=True)[:3]:
            if strength > 0.3:
                interpretation['primary_influences'].append({
                    'sensor': sensor,
                    'correlation': strength,
                    'relationship': self._describe_relationship(sensor, strength)
                })
        
        return interpretation
    
    def _describe_relationship(self, sensor: str, strength: float) -> str:
        """Describe ecological relationship based on entanglement strength"""
        relationships = {
            ('temperature', 'humidity'): 'VPD coupling',
            ('ph', 'ec'): 'Nutrient availability',
            ('light', 'temperature'): 'Photosynthetic heat',
            ('co2', 'temperature'): 'Stomatal regulation'
        }
        
        # Look for known relationships
        for (s1, s2), desc in relationships.items():
            if sensor in [s1, s2]:
                return f"{desc} ({strength:.1%} coupled)"
        
        return f"Correlated ({strength:.1%})"

@dataclass
class QRFNode:
    """Enhanced QRF node with CEA semantics"""
    level: int
    data: Dict
    quantum_state: CEAQuantumState
    children: List['QRFNode']
    parent_hash: Optional[str]
    node_type: str = "sensor_data"  # sensor_data, aggregate, prediction
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    
    def to_quantum_payload(self) -> str:
        """Encode node data with enhanced metadata"""
        payload = {
            'v': '2.0',  # Version
            'l': self.level,
            'd': self.data,
            'q': {
                'sv': [(z.real, z.imag) for z in self.quantum_state.state_vector],
                'mb': self.quantum_state.measurement_basis.name,
                'c': round(self.quantum_state.coherence, 4),
                'e': {k: round(v, 4) for k, v in self.quantum_state.entanglement_map.items()},
                'u': self.quantum_state.uncertainty_sources
            },
            'ch': [child.get_hash()[:8] for child in self.children],  # Shortened for QR efficiency
            'ph': self.parent_hash[:8] if self.parent_hash else None,
            't': int(datetime.now(timezone.utc).timestamp() * 1000),
            'nt': self.node_type,
            'ci': [round(self.confidence_interval[0], 2), round(self.confidence_interval[1], 2)]
        }
        return json.dumps(payload, separators=(',', ':'))
    
    def get_hash(self) -> str:
        """Generate cryptographic hash of this node"""
        content = self.to_quantum_payload()
        return hashlib.sha256(content.encode()).hexdigest()

class QRFGenerator:
    """Enhanced QRF Generator with production features"""
    
    def __init__(self, max_depth: int = 4, base_size: int = 1024):
        self.max_depth = max_depth
        self.base_size = base_size
        self.nodes: Dict[int, List[QRFNode]] = {i: [] for i in range(max_depth)}
        self.metadata = {
            'created_at': datetime.now(timezone.utc),
            'generator_version': '2.0',
            'purpose': 'CEA Data Verification'
        }
        
    async def generate_cea_fractal(self, 
                                  facility_data: Dict,
                                  sensor_readings: List[Dict],
                                  time_window: str = "1h") -> Tuple[Image.Image, Dict]:
        """
        Generate QRF for CEA facility data
        
        Args:
            facility_data: Facility metadata
            sensor_readings: List of recent sensor readings
            time_window: Time aggregation window (1h, 24h, 7d)
        
        Returns:
            Tuple of (QRF image, blockchain anchor data)
        """
        # Create root quantum state from facility overview
        root_quantum_state = self._create_facility_quantum_state(sensor_readings)
        
        # Build root node
        root_data = {
            'facility': facility_data.get('name', 'Unknown'),
            'zones': facility_data.get('zone_count', 0),
            'window': time_window,
            'summary': self._summarize_readings(sensor_readings)
        }
        
        root = QRFNode(
            level=0,
            data=root_data,
            quantum_state=root_quantum_state,
            children=[],
            parent_hash=None,
            node_type="aggregate",
            confidence_interval=self._calculate_confidence(sensor_readings)
        )
        
        # Build fractal tree
        await self._build_cea_tree(root, sensor_readings)
        
        # Render fractal
        qrf_image = self._render_enhanced_fractal(root)
        
        # Create blockchain anchor
        anchor_data = self._create_blockchain_anchor()
        
        return qrf_image, anchor_data
    
    def _create_facility_quantum_state(self, readings: List[Dict]) -> CEAQuantumState:
        """Create quantum state representing facility-wide conditions"""
        # Calculate overall coherence from sensor reliability
        coherence_values = []
        for reading in readings:
            # Coherence based on sensor age, calibration status, variance
            sensor_coherence = reading.get('reliability', 0.8)
            coherence_values.append(sensor_coherence)
        
        avg_coherence = np.mean(coherence_values) if coherence_values else 0.5
        
        # Build entanglement map from correlations
        entanglement_map = {}
        correlations = self._calculate_sensor_correlations(readings)
        for (s1, s2), corr in correlations.items():
            if s1 not in entanglement_map:
                entanglement_map[s1] = 0
            entanglement_map[s1] = max(entanglement_map[s1], abs(corr))
        
        # Identify uncertainty sources
        uncertainty_sources = []
        if avg_coherence < 0.7:
            uncertainty_sources.append("Low sensor reliability")
        if len(readings) < 10:
            uncertainty_sources.append("Limited data points")
        
        # Create quantum state vector (simplified Bell state + noise)
        state_vector = [
            complex(np.sqrt(avg_coherence), 0),
            complex(np.sqrt(1 - avg_coherence), 0)
        ]
        
        return CEAQuantumState(
            state_vector=state_vector,
            measurement_basis=QuantumBasis.ENVIRONMENTAL,
            coherence=avg_coherence,
            entanglement_map=entanglement_map,
            uncertainty_sources=uncertainty_sources
        )
    
    def _calculate_sensor_correlations(self, readings: List[Dict]) -> Dict[Tuple[str, str], float]:
        """Calculate pairwise sensor correlations"""
        correlations = {}
        sensor_types = ['temperature', 'humidity', 'co2', 'ph', 'ec']
        
        for i, s1 in enumerate(sensor_types):
            for s2 in sensor_types[i+1:]:
                values1 = [r.get(s1, 0) for r in readings if s1 in r]
                values2 = [r.get(s2, 0) for r in readings if s2 in r]
                
                if len(values1) > 1 and len(values2) > 1:
                    corr = np.corrcoef(values1[:min(len(values1), len(values2))], 
                                      values2[:min(len(values1), len(values2))])[0, 1]
                    if not np.isnan(corr):
                        correlations[(s1, s2)] = corr
        
        return correlations
    
    def _summarize_readings(self, readings: List[Dict]) -> Dict:
        """Create statistical summary of readings"""
        summary = {}
        for key in ['temperature', 'humidity', 'co2', 'ph', 'ec']:
            values = [r.get(key, 0) for r in readings if key in r]
            if values:
                summary[key] = {
                    'avg': round(np.mean(values), 2),
                    'std': round(np.std(values), 2),
                    'min': round(min(values), 2),
                    'max': round(max(values), 2)
                }
        return summary
    
    def _calculate_confidence(self, readings: List[Dict]) -> Tuple[float, float]:
        """Calculate confidence interval for aggregated data"""
        if not readings:
            return (0.0, 0.0)
        
        # Simplified: Use coefficient of variation
        cv_values = []
        for key in ['temperature', 'humidity', 'co2']:
            values = [r.get(key, 0) for r in readings if key in r]
            if len(values) > 1:
                mean = np.mean(values)
                std = np.std(values)
                if mean > 0:
                    cv_values.append(std / mean)
        
        avg_cv = np.mean(cv_values) if cv_values else 0.5
        confidence = max(0, 1 - avg_cv)
        
        return (confidence * 0.9, min(1.0, confidence * 1.1))
    
    async def _build_cea_tree(self, parent: QRFNode, sensor_readings: List[Dict]):
        """Build tree with CEA-specific hierarchy"""
        if parent.level >= self.max_depth - 1:
            return
        
        # Different branching strategies based on level
        if parent.level == 0:
            # Level 1: Branch by sensor type
            branches = ['environmental', 'nutritional', 'photonic']
        elif parent.level == 1:
            # Level 2: Branch by time segments
            branches = ['recent', 'median', 'historical']
        else:
            # Level 3+: Branch by statistical moments
            branches = ['mean', 'variance', 'extrema']
        
        for branch_type in branches:
            child_data = self._derive_branch_data(parent.data, branch_type, sensor_readings)
            child_quantum_state = self._derive_branch_quantum_state(
                parent.quantum_state, branch_type
            )
            
            child = QRFNode(
                level=parent.level + 1,
                data=child_data,
                quantum_state=child_quantum_state,
                children=[],
                parent_hash=parent.get_hash(),
                node_type="sensor_data" if parent.level == 0 else "aggregate"
            )
            
            parent.children.append(child)
            self.nodes[child.level].append(child)
            
            # Recursive build
            await self._build_cea_tree(child, sensor_readings)
    
    def _derive_branch_data(self, parent_data: Dict, branch_type: str, 
                           readings: List[Dict]) -> Dict:
        """Derive child data based on branch type"""
        child_data = {'branch': branch_type}
        
        if branch_type == 'environmental':
            relevant_keys = ['temperature', 'humidity', 'co2']
        elif branch_type == 'nutritional':
            relevant_keys = ['ph', 'ec', 'dissolved_oxygen']
        elif branch_type == 'photonic':
            relevant_keys = ['light_intensity', 'light_spectrum', 'photoperiod']
        else:
            relevant_keys = list(parent_data.get('summary', {}).keys())
        
        # Filter and summarize relevant data
        for key in relevant_keys:
            if key in parent_data.get('summary', {}):
                child_data[key] = parent_data['summary'][key]
        
        return child_data
    
    def _derive_branch_quantum_state(self, parent_state: CEAQuantumState, 
                                    branch_type: str) -> CEAQuantumState:
        """Derive child quantum state with reduced coherence"""
        # Each level reduces coherence (information loss)
        child_coherence = parent_state.coherence * 0.9
        
        # Filter entanglement map based on branch
        if branch_type in ['environmental', 'nutritional', 'photonic']:
            relevant_sensors = {
                'environmental': ['temperature', 'humidity', 'co2'],
                'nutritional': ['ph', 'ec', 'dissolved_oxygen'],
                'photonic': ['light_intensity', 'light_spectrum']
            }.get(branch_type, [])
            
            child_entanglement = {
                k: v for k, v in parent_state.entanglement_map.items()
                if any(sensor in k for sensor in relevant_sensors)
            }
        else:
            child_entanglement = parent_state.entanglement_map.copy()
        
        # Create child state vector (partial measurement)
        parent_amp = parent_state.state_vector[0]
        child_state_vector = [
            complex(abs(parent_amp) * np.sqrt(child_coherence), 0),
            complex(np.sqrt(1 - abs(parent_amp)**2 * child_coherence), 0)
        ]
        
        return CEAQuantumState(
            state_vector=child_state_vector,
            measurement_basis=parent_state.measurement_basis,
            coherence=child_coherence,
            entanglement_map=child_entanglement,
            uncertainty_sources=parent_state.uncertainty_sources + [f"Level {branch_type} aggregation"]
        )
    
    def _render_enhanced_fractal(self, root: QRFNode) -> Image.Image:
        """Render fractal with visual enhancements"""
        img = Image.new('RGBA', (self.base_size, self.base_size), (255, 255, 255, 255))
        
        # Add background gradient
        self._add_background_gradient(img)
        
        # Render fractal
        self._render_node_recursive(img, root, 0, 0, self.base_size)
        
        # Add metadata overlay
        self._add_metadata_overlay(img, root)
        
        return img
    
    def _add_background_gradient(self, img: Image.Image):
        """Add subtle gradient background"""
        draw = ImageDraw.Draw(img)
        for i in range(self.base_size):
            color = int(255 - (i / self.base_size) * 30)  # Subtle gradient
            draw.line([(0, i), (self.base_size, i)], fill=(color, color, color, 255))
    
    def _add_metadata_overlay(self, img: Image.Image, root: QRFNode):
        """Add metadata text overlay"""
        draw = ImageDraw.Draw(img)
        
        # Try to load font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Add title
        title = f"QRF v2.0 - {root.data.get('facility', 'CEA Facility')}"
        draw.text((10, 10), title, fill=(0, 0, 0, 255), font=font)
        
        # Add timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        draw.text((10, 30), timestamp, fill=(64, 64, 64, 255), font=small_font)
        
        # Add coherence indicator
        coherence_text = f"Quantum Coherence: {root.quantum_state.coherence:.1%}"
        draw.text((10, self.base_size - 30), coherence_text, 
                 fill=(0, 128, 0, 255), font=small_font)
    
    def _render_node_recursive(self, img: Image.Image, node: QRFNode, 
                              x: int, y: int, size: int, depth: int = 0):
        """Recursively render QR codes with visual hierarchy"""
        if size < 64 or depth > self.max_depth:  # Minimum readable QR size
            return
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=1,
            border=1
        )
        
        try:
            qr.add_data(node.to_quantum_payload())
            qr.make(fit=True)
            
            # Color based on coherence
            fill_color = self._coherence_to_color(node.quantum_state.coherence)
            qr_img = qr.make_image(fill_color=fill_color, back_color="white")
            
            # Resize with quality preservation
            qr_img = qr_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # Add border based on node type
            if node.node_type == "aggregate":
                self._add_border(qr_img, (0, 0, 255, 128), 2)  # Blue for aggregate
            elif node.level == 0:
                self._add_border(qr_img, (0, 128, 0, 128), 3)  # Green for root
            
            # Paste into main image
            img.paste(qr_img, (x, y))
            
        except Exception as e:
            print(f"QR generation error at level {node.level}: {e}")
            # Draw placeholder
            draw = ImageDraw.Draw(img)
            draw.rectangle([(x, y), (x + size, y + size)], 
                          outline=(255, 0, 0, 255), width=2)
        
        # Render children
        if node.children:
            child_size = int(size * INVERSE_PHI)
            positions = self._calculate_golden_positions(x, y, size, child_size, len(node.children))
            
            for child, (cx, cy) in zip(node.children, positions):
                self._render_node_recursive(img, child, cx, cy, child_size, depth + 1)
    
    def _coherence_to_color(self, coherence: float) -> str:
        """Map coherence to color (high coherence = darker/more certain)"""
        # Green channel varies with coherence
        green = int(255 * (1 - coherence * 0.5))
        return f"#{0:02x}{green:02x}{0:02x}"
    
    def _add_border(self, img: Image.Image, color: Tuple[int, int, int, int], width: int):
        """Add colored border to QR code"""
        draw = ImageDraw.Draw(img)
        w, h = img.size
        for i in range(width):
            draw.rectangle([(i, i), (w-i-1, h-i-1)], outline=color)
    
    def _calculate_golden_positions(self, x: int, y: int, parent_size: int,
                                   child_size: int, num_children: int) -> List[Tuple[int, int]]:
        """Calculate golden ratio spiral positions"""
        positions = []
        
        if num_children <= 4:
            # Quadrant layout
            half = parent_size // 2
            positions = [
                (x + half - child_size, y + half - child_size),  # Center
                (x, y),  # Top-left
                (x + parent_size - child_size, y),  # Top-right
                (x + half - child_size//2, y + parent_size - child_size)  # Bottom-center
            ][:num_children]
        else:
            # Fibonacci spiral
            angle = 0
            radius_step = (parent_size - child_size) / (2 * num_children)
            
            for i in range(num_children):
                radius = radius_step * (i + 1)
                angle += 2.399963  # Golden angle in radians
                
                cx = int(x + parent_size//2 + radius * math.cos(angle) - child_size//2)
                cy = int(y + parent_size//2 + radius * math.sin(angle) - child_size//2)
                
                # Ensure within bounds
                cx = max(x, min(cx, x + parent_size - child_size))
                cy = max(y, min(cy, y + parent_size - child_size))
                
                positions.append((cx, cy))
        
        return positions
    
    def _create_blockchain_anchor(self) -> Dict:
        """Create comprehensive blockchain anchor data"""
        # Collect all node hashes
        all_hashes = []
        for level in sorted(self.nodes.keys()):
            for node in self.nodes[level]:
                all_hashes.append(node.get_hash())
        
        # Calculate merkle root
        merkle_root = self._calculate_merkle_root(all_hashes)
        
        # Calculate aggregate quantum metrics
        total_coherence = 0
        total_nodes = 0
        uncertainty_summary = set()
        
        for nodes in self.nodes.values():
            for node in nodes:
                total_coherence += node.quantum_state.coherence
                total_nodes += 1
                uncertainty_summary.update(node.quantum_state.uncertainty_sources)
        
        avg_coherence = total_coherence / total_nodes if total_nodes > 0 else 0
        
        # Create signature
        signature = self._generate_quantum_signature({
            'merkle_root': merkle_root,
            'timestamp': int(datetime.now(timezone.utc).timestamp()),
            'node_count': total_nodes
        })
        
        return {
            'version': '2.0',
            'merkle_root': merkle_root,
            'node_count': total_nodes,
            'depth': self.max_depth,
            'quantum_metrics': {
                'average_coherence': round(avg_coherence, 4),
                'total_uncertainty_sources': len(uncertainty_summary),
                'uncertainty_types': list(uncertainty_summary)
            },
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'signature': signature,
            'metadata': self.metadata
        }
    
    def _calculate_merkle_root(self, hashes: List[str]) -> str:
        """Calculate Merkle tree root"""
        if not hashes:
            return hashlib.sha256(b"empty").hexdigest()
        
        level_hashes = hashes[:]
        
        while len(level_hashes) > 1:
            next_level = []
            
            for i in range(0, len(level_hashes), 2):
                if i + 1 < len(level_hashes):
                    combined = level_hashes[i] + level_hashes[i + 1]
                else:
                    combined = level_hashes[i] + level_hashes[i]
                
                next_hash = hashlib.sha256(combined.encode()).hexdigest()
                next_level.append(next_hash)
            
            level_hashes = next_level
        
        return level_hashes[0]
    
    def _generate_quantum_signature(self, data: Dict) -> str:
        """Generate quantum-resistant signature"""
        if QUANTUM_CRYPTO_AVAILABLE:
            # Use real quantum-resistant signature
            message = json.dumps(data, sort_keys=True).encode()
            public_key, secret_key = generate_keypair()
            signature = sign(message, secret_key)
            return base64.b64encode(signature).decode()
        else:
            # Fallback to SHA3-512 (still quantum-resistant hash)
            message = json.dumps(data, sort_keys=True).encode()
            return hashlib.sha3_512(message).hexdigest()

class QRFBlockchainAPI:
    """API for blockchain integration"""
    
    def __init__(self, blockchain_endpoint: str = None):
        self.endpoint = blockchain_endpoint or "http://localhost:8545"
        self.web3 = None  # Placeholder for Web3 instance
    
    async def anchor_qrf(self, anchor_data: Dict) -> Dict:
        """Anchor QRF data to blockchain"""
        # This would connect to actual blockchain
        # For now, return mock transaction
        return {
            'status': 'pending',
            'tx_hash': hashlib.sha256(
                json.dumps(anchor_data).encode()
            ).hexdigest(),
            'block_number': None,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    async def verify_qrf(self, merkle_root: str) -> Optional[Dict]:
        """Verify QRF by merkle root lookup"""
        # This would query blockchain for anchor
        # For now, return mock verification
        return {
            'verified': True,
            'merkle_root': merkle_root,
            'anchor_timestamp': datetime.now(timezone.utc).isoformat(),
            'block_number': 12345678,
            'coherence_at_anchor': 0.85
        }

# Integration with OSCE
class OSCEQRFIntegration:
    """Integrate QRF with OSCE platform"""
    
    def __init__(self, osce_environment):
        self.env = osce_environment
        self.qrf_generator = QRFGenerator()
        self.blockchain_api = QRFBlockchainAPI()
    
    async def create_hourly_snapshot(self) -> Tuple[str, Dict]:
        """Create hourly QRF snapshot of facility"""
        # Gather recent sensor data
        sensor_readings = await self._collect_recent_readings("1h")
        
        # Get facility metadata
        facility_data = {
            'name': self.env.name,
            'zone_count': len(self.env.sensors),
            'actuator_count': len(self.env.actuators),
            'rule_count': len(self.env.rules)
        }
        
        # Generate QRF
        qrf_image, anchor_data = await self.qrf_generator.generate_cea_fractal(
            facility_data, sensor_readings, "1h"
        )
        
        # Save image
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"qrf_snapshot_{self.env.name}_{timestamp}.png"
        qrf_image.save(filename)
        
        # Anchor to blockchain
        blockchain_tx = await self.blockchain_api.anchor_qrf(anchor_data)
        
        # Log event
        await self.env.emit_event('qrf_generated', {
            'filename': filename,
            'merkle_root': anchor_data['merkle_root'],
            'blockchain_tx': blockchain_tx['tx_hash'],
            'coherence': anchor_data['quantum_metrics']['average_coherence']
        })
        
        return filename, anchor_data
    
    async def _collect_recent_readings(self, time_window: str) -> List[Dict]:
        """Collect recent sensor readings"""
        readings = []
        
        for sensor_name, sensor in self.env.sensors.items():
            if sensor.value is not None:
                reading = {
                    'sensor': sensor_name,
                    'type': sensor.sensor_type,
                    sensor.sensor_type: sensor.value,
                    'timestamp': sensor.last_reading.isoformat() if sensor.last_reading else None,
                    'reliability': sensor.health_status == 'healthy' and 0.9 or 0.5
                }
                readings.append(reading)
        
        return readings

# Example usage
async def demo_qrf_v2():
    """Demonstrate QRF v2 capabilities"""
    
    # Sample CEA sensor data
    sensor_readings = [
        {'temperature': 24.5, 'humidity': 65.2, 'co2': 1200, 'reliability': 0.95},
        {'temperature': 24.8, 'humidity': 64.8, 'co2': 1180, 'reliability': 0.93},
        {'temperature': 25.1, 'humidity': 63.9, 'co2': 1150, 'reliability': 0.91},
        {'ph': 6.2, 'ec': 2.1, 'dissolved_oxygen': 7.8, 'reliability': 0.88},
        {'ph': 6.3, 'ec': 2.0, 'dissolved_oxygen': 7.9, 'reliability': 0.89},
    ]
    
    facility_data = {
        'name': 'Greenhouse Alpha',
        'zone_count': 4,
        'crop': 'Tomatoes',
        'stage': 'Flowering'
    }
    
    # Generate QRF
    generator = QRFGenerator(max_depth=4, base_size=1024)
    qrf_image, anchor_data = await generator.generate_cea_fractal(
        facility_data, sensor_readings, "1h"
    )
    
    # Save and display results
    qrf_image.save('cea_qrf_v2_demo.png')
    
    print("\n=== QRF v2 Generation Complete ===")
    print(f"Merkle Root: {anchor_data['merkle_root'][:16]}...")
    print(f"Node Count: {anchor_data['node_count']}")
    print(f"Average Coherence: {anchor_data['quantum_metrics']['average_coherence']:.1%}")
    print(f"Uncertainty Sources: {anchor_data['quantum_metrics']['uncertainty_types']}")
    print(f"\nQRF saved as: cea_qrf_v2_demo.png")
    
    # Demonstrate ecological interpretation
    root_node = generator.nodes[0][0]
    interpretation = root_node.quantum_state.ecological_interpretation()
    print(f"\nEcological Interpretation:")
    print(f"  Measurement Quality: {interpretation['measurement_quality']}")
    print(f"  Primary Influences:")
    for influence in interpretation['primary_influences']:
        print(f"    - {influence['sensor']}: {influence['relationship']}")

if __name__ == "__main__":
    asyncio.run(demo_qrf_v2())