#!/usr/bin/env python3
"""
HiveMindFFT v2.0 - Decision Adapter Interface for PHAL Integration
Enables FFT-based consensus for hardware resource conflicts

Created by Jason DeLooze for Locally Sovereign Sustainability (Open Source)
Repository: https://github.com/HydroFarmerJason/OpenSourceControlledEnvironments
Year: 2025

This module extends the original HiveMindFFT with clean interfaces for
PHAL integration, enabling plugins to participate in frequency-domain
consensus decisions.

License: MIT
Copyright (c) 2025 Jason DeLooze
"""

import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json
from scipy.fft import fft, ifft
from collections import deque

from osce.utils.logging import get_logger

logger = get_logger(__name__)

@dataclass
class AgentSignal:
    """Agent's frequency-domain voting signal"""
    agent_id: str
    signal: np.ndarray  # Frequency domain representation
    confidence: float   # 0-1, strength of opinion
    metadata: Dict[str, Any] = None

@dataclass
class DecisionResult:
    """Result of collective decision making"""
    consensus_frequency: float  # Dominant decision frequency
    coherence: float           # 0-1, how aligned agents are
    dominant_frequency: float   # Actual dominant frequency in spectrum
    participant_count: int
    decision_spectrum: np.ndarray
    metadata: Dict[str, Any] = None

class HiveMindFFT:
    """
    FFT-based collective intelligence for distributed decision making
    
    v2.0 Features:
    - Clean decision interface for PHAL
    - Plugin signal registration
    - Weighted voting by role
    - Decision history and learning
    """
    
    def __init__(self, fft_size: int = 128):
        self.fft_size = fft_size
        self.decision_history = deque(maxlen=1000)
        self.agent_profiles = {}
        self.role_weights = {
            'control': 1.0,
            'actuate': 0.8,
            'write': 0.6,
            'read': 0.4,
            'monitor': 0.2
        }
        self.coherence_threshold = 0.6
        self.initialized = False
        
    async def initialize(self):
        """Initialize HiveMind systems"""
        logger.info("Initializing HiveMindFFT v2.0")
        
        # Start background tasks
        asyncio.create_task(self._coherence_monitor())
        asyncio.create_task(self._decision_learner())
        
        self.initialized = True
        logger.info("HiveMindFFT ready for consensus operations")
        
    async def get_decision(self, issue: Dict[str, Any], 
                          agents: List[AgentSignal]) -> Dict[str, Any]:
        """
        Primary interface for PHAL - get collective decision on an issue
        
        Args:
            issue: Dictionary describing the decision needed
            agents: List of agent signals (votes)
            
        Returns:
            Dictionary with decision data including consensus
        """
        if not self.initialized:
            await self.initialize()
            
        logger.debug(f"Processing decision for {len(agents)} agents")
        
        # Normalize and weight signals
        weighted_signals = self._apply_role_weights(agents, issue)
        
        # Combine signals
        combined_spectrum = self._combine_signals(weighted_signals)
        
        # Analyze for consensus
        result = self._analyze_consensus(combined_spectrum, agents)
        
        # Record decision
        self._record_decision(issue, agents, result)
        
        # Format for PHAL
        return {
            'consensus_frequency': result.consensus_frequency,
            'coherence': result.coherence,
            'dominant_frequency': result.dominant_frequency,
            'participant_count': result.participant_count,
            'decision': self._interpret_consensus(result),
            'confidence': result.coherence,
            'timestamp': datetime.utcnow().isoformat()
        }
        
    def _apply_role_weights(self, agents: List[AgentSignal], 
                           issue: Dict[str, Any]) -> List[Tuple[AgentSignal, float]]:
        """Apply role-based weights to agent signals"""
        weighted = []
        
        for agent in agents:
            # Get weight from metadata or issue context
            weight = 1.0
            
            if agent.metadata and 'permission_level' in agent.metadata:
                # Map permission level to role
                level = agent.metadata['permission_level']
                role_map = {7: 'control', 5: 'actuate', 3: 'write', 2: 'read', 1: 'monitor'}
                role = role_map.get(level, 'monitor')
                weight = self.role_weights.get(role, 0.5)
                
            # Adjust for issue type
            if issue.get('type') == 'resource_conflict':
                # Current holder gets slight advantage
                if agent.agent_id == issue.get('current_holder', {}).get('plugin_id'):
                    weight *= 1.2
                    
            weighted.append((agent, weight))
            
        return weighted
        
    def _combine_signals(self, weighted_signals: List[Tuple[AgentSignal, float]]) -> np.ndarray:
        """Combine weighted signals into collective spectrum"""
        combined = np.zeros(self.fft_size, dtype=complex)
        total_weight = 0
        
        for agent, weight in weighted_signals:
            # Apply confidence and role weight
            signal_weight = weight * agent.confidence
            combined += agent.signal * signal_weight
            total_weight += signal_weight
            
        # Normalize
        if total_weight > 0:
            combined /= total_weight
            
        return combined
        
    def _analyze_consensus(self, spectrum: np.ndarray, 
                          agents: List[AgentSignal]) -> DecisionResult:
        """Analyze frequency spectrum for consensus"""
        # Find dominant frequency
        magnitude = np.abs(spectrum)
        dominant_idx = np.argmax(magnitude)
        dominant_freq = dominant_idx / self.fft_size
        
        # Calculate coherence (how concentrated energy is around dominant)
        total_energy = np.sum(magnitude ** 2)
        if total_energy > 0:
            # Energy in dominant frequency and neighbors
            window = 3  # Check neighboring frequencies
            start = max(0, dominant_idx - window)
            end = min(self.fft_size, dominant_idx + window + 1)
            dominant_energy = np.sum(magnitude[start:end] ** 2)
            coherence = dominant_energy / total_energy
        else:
            coherence = 0
            
        # Interpret consensus frequency
        # Map frequency to decision space (-1 to 1)
        consensus_value = (dominant_freq - 0.5) * 2
        
        return DecisionResult(
            consensus_frequency=consensus_value,
            coherence=coherence,
            dominant_frequency=dominant_freq,
            participant_count=len(agents),
            decision_spectrum=spectrum,
            metadata={
                'energy_distribution': self._analyze_energy_distribution(magnitude)
            }
        )
        
    def _analyze_energy_distribution(self, magnitude: np.ndarray) -> Dict[str, float]:
        """Analyze how energy is distributed in spectrum"""
        total = np.sum(magnitude)
        if total == 0:
            return {'low': 0, 'mid': 0, 'high': 0}
            
        third = self.fft_size // 3
        
        return {
            'low': np.sum(magnitude[:third]) / total,
            'mid': np.sum(magnitude[third:2*third]) / total,
            'high': np.sum(magnitude[2*third:]) / total
        }
        
    def _interpret_consensus(self, result: DecisionResult) -> str:
        """Interpret consensus result as decision"""
        if result.coherence < self.coherence_threshold:
            return 'no_consensus'  # Agents too divided
            
        if result.consensus_frequency > 0.3:
            return 'grant'
        elif result.consensus_frequency > -0.3:
            return 'share'
        else:
            return 'deny'
            
    def _record_decision(self, issue: Dict[str, Any], 
                        agents: List[AgentSignal],
                        result: DecisionResult):
        """Record decision for learning"""
        record = {
            'timestamp': datetime.utcnow(),
            'issue_type': issue.get('type'),
            'agent_count': len(agents),
            'coherence': result.coherence,
            'consensus': result.consensus_frequency,
            'decision': self._interpret_consensus(result)
        }
        
        self.decision_history.append(record)
        
    async def register_plugin_profile(self, plugin_id: str, 
                                    profile: Dict[str, Any]):
        """Register a plugin's signal profile for consistent voting"""
        self.agent_profiles[plugin_id] = {
            'base_frequency': profile.get('base_frequency', 0.1),
            'harmonics': profile.get('harmonics', 3),
            'phase_offset': profile.get('phase_offset', 0),
            'registered': datetime.utcnow()
        }
        
        logger.info(f"Registered plugin profile: {plugin_id}")
        
    def create_agent_signal(self, plugin_id: str, vote: float,
                           confidence: float = 1.0) -> AgentSignal:
        """Create an agent signal for a plugin's vote"""
        # Get or create profile
        if plugin_id in self.agent_profiles:
            profile = self.agent_profiles[plugin_id]
        else:
            # Auto-generate profile
            profile = {
                'base_frequency': hash(plugin_id) % 20 / 100 + 0.1,
                'harmonics': 3,
                'phase_offset': 0
            }
            
        # Generate frequency domain signal
        signal = np.zeros(self.fft_size, dtype=complex)
        
        # Add base frequency and harmonics
        base_freq = profile['base_frequency']
        for h in range(profile['harmonics']):
            freq_idx = int((base_freq * (h + 1) * self.fft_size)) % self.fft_size
            amplitude = vote / (h + 1)  # Decreasing amplitude for harmonics
            phase = profile['phase_offset'] + (h * np.pi / 4)
            signal[freq_idx] = amplitude * np.exp(1j * phase)
            
        return AgentSignal(
            agent_id=plugin_id,
            signal=signal,
            confidence=confidence,
            metadata={'profile': profile}
        )
        
    async def _coherence_monitor(self):
        """Monitor decision coherence patterns"""
        while True:
            try:
                if len(self.decision_history) > 10:
                    recent = list(self.decision_history)[-100:]
                    avg_coherence = np.mean([d['coherence'] for d in recent])
                    
                    if avg_coherence < 0.5:
                        logger.warning(f"Low average coherence: {avg_coherence:.2f}")
                        
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Coherence monitor error: {e}")
                await asyncio.sleep(60)
                
    async def _decision_learner(self):
        """Learn from decision patterns to improve future consensus"""
        while True:
            try:
                if len(self.decision_history) > 100:
                    # Analyze patterns
                    patterns = self._analyze_decision_patterns()
                    
                    # Adjust weights based on success patterns
                    self._update_role_weights(patterns)
                    
                await asyncio.sleep(3600)  # Learn every hour
                
            except Exception as e:
                logger.error(f"Decision learner error: {e}")
                await asyncio.sleep(300)
                
    def _analyze_decision_patterns(self) -> Dict[str, Any]:
        """Analyze historical decision patterns"""
        recent = list(self.decision_history)[-500:]
        
        patterns = {
            'avg_coherence_by_type': {},
            'decision_distribution': {'grant': 0, 'deny': 0, 'share': 0, 'no_consensus': 0},
            'high_coherence_decisions': []
        }
        
        # Group by issue type
        by_type = {}
        for record in recent:
            issue_type = record.get('issue_type', 'unknown')
            if issue_type not in by_type:
                by_type[issue_type] = []
            by_type[issue_type].append(record)
            
            # Count decisions
            decision = record.get('decision', 'unknown')
            if decision in patterns['decision_distribution']:
                patterns['decision_distribution'][decision] += 1
                
            # Track high coherence
            if record['coherence'] > 0.8:
                patterns['high_coherence_decisions'].append(record)
                
        # Calculate averages
        for issue_type, records in by_type.items():
            patterns['avg_coherence_by_type'][issue_type] = np.mean([r['coherence'] for r in records])
            
        return patterns
        
    def _update_role_weights(self, patterns: Dict[str, Any]):
        """Update role weights based on learned patterns"""
        # This is where ML could optimize weights
        # For now, just log insights
        
        high_coherence_ratio = len(patterns['high_coherence_decisions']) / 500
        if high_coherence_ratio > 0.3:
            logger.info("System achieving good consensus rates")
        else:
            logger.info("Consider adjusting role weights for better consensus")
            
    def get_decision_metrics(self) -> Dict[str, Any]:
        """Get metrics about decision making performance"""
        if not self.decision_history:
            return {'status': 'no_data'}
            
        recent = list(self.decision_history)[-100:]
        
        return {
            'total_decisions': len(self.decision_history),
            'recent_coherence': np.mean([d['coherence'] for d in recent]),
            'consensus_rate': sum(1 for d in recent if d['decision'] != 'no_consensus') / len(recent),
            'decision_distribution': {
                'grant': sum(1 for d in recent if d['decision'] == 'grant') / len(recent),
                'deny': sum(1 for d in recent if d['decision'] == 'deny') / len(recent),
                'share': sum(1 for d in recent if d['decision'] == 'share') / len(recent),
            },
            'avg_participants': np.mean([d['agent_count'] for d in recent])
        }
        
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down HiveMindFFT")
        
        # Save decision history
        try:
            with open('hivemind_decisions.json', 'w') as f:
                # Convert to serializable format
                history = []
                for record in self.decision_history:
                    rec = dict(record)
                    rec['timestamp'] = rec['timestamp'].isoformat()
                    history.append(rec)
                    
                json.dump(history, f)
                logger.info(f"Saved {len(history)} decision records")
                
        except Exception as e:
            logger.error(f"Failed to save decision history: {e}")

# Example usage for testing
if __name__ == "__main__":
    async def test_consensus():
        hive = HiveMindFFT()
        await hive.initialize()
        
        # Create test issue
        issue = {
            'type': 'resource_conflict',
            'resource': 'main:temperature_sensor',
            'current_holder': {'plugin_id': 'climate_control', 'permission_level': 5},
            'requester': {'plugin_id': 'ml_optimizer', 'permission_level': 3}
        }
        
        # Create agent signals
        agents = [
            hive.create_agent_signal('climate_control', vote=-0.8, confidence=0.9),
            hive.create_agent_signal('ml_optimizer', vote=0.7, confidence=0.8),
            hive.create_agent_signal('monitor_dashboard', vote=0.3, confidence=0.5),
        ]
        
        # Get decision
        decision = await hive.get_decision(issue, agents)
        
        print(f"Decision: {decision['decision']}")
        print(f"Coherence: {decision['coherence']:.2f}")
        print(f"Consensus: {decision['consensus_frequency']:.2f}")
        
        # Get metrics
        metrics = hive.get_decision_metrics()
        print(f"\nMetrics: {json.dumps(metrics, indent=2)}")
        
        await hive.shutdown()
        
    asyncio.run(test_consensus())
