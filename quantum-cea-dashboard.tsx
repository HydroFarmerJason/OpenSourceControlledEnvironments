// Created by Jason DeLooze for Locally Sovereign Sustainability (Open Source) osce@duck.com
import React, { useState, useEffect } from 'react';
import { Heart, Brain, Leaf, Activity, Users, AlertCircle, TrendingUp } from 'lucide-react';

const LivingQuantumDashboard = () => {
  const [systemData, setSystemData] = useState({
    health: 0.87,
    phase: 'baseline',
    coherenceEvents: 3,
    daysMonitoring: 42,
    communityReviewers: 7,
    lastUpdate: new Date().toISOString()
  });

  const [healthHistory, setHealthHistory] = useState([
    { time: '00:00', value: 0.85 },
    { time: '04:00', value: 0.86 },
    { time: '08:00', value: 0.87 },
    { time: '12:00', value: 0.88 },
    { time: '16:00', value: 0.87 },
    { time: '20:00', value: 0.87 }
  ]);

  const [bioelectricData, setBioelectricData] = useState([
    { plant: 'Tomato-01', signal: 0.3, sync: 0.7 },
    { plant: 'Lettuce-03', signal: 0.4, sync: 0.65 },
    { plant: 'Basil-02', signal: 0.35, sync: 0.72 },
    { plant: 'Pepper-01', signal: 0.38, sync: 0.68 }
  ]);

  const [ethicalStatus, setEthicalStatus] = useState({
    consent: true,
    transparency: 0.95,
    communityApproval: true,
    lastReview: '2024-11-20'
  });

  const phases = {
    baseline: { name: 'Listening', color: 'bg-blue-500', description: 'Establishing baseline patterns' },
    coherence: { name: 'Harmonizing', color: 'bg-green-500', description: 'Optimizing natural coherence' },
    correlation: { name: 'Conversing', color: 'bg-purple-500', description: 'Finding communication patterns' },
    experimental: { name: 'Computing', color: 'bg-orange-500', description: 'Exploring quantum behaviors' }
  };

  const currentPhase = phases[systemData.phase];

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Living Quantum CEA Monitor</h1>
          <p className="text-gray-600">Real-time transparency for ecosystem-based quantum research</p>
          <div className="mt-4 flex items-center gap-4 text-sm text-gray-500">
            <span>Last updated: {new Date(systemData.lastUpdate).toLocaleString()}</span>
            <span className="flex items-center gap-1">
              <Users className="w-4 h-4" />
              {systemData.communityReviewers} community reviewers
            </span>
          </div>
        </div>

        {/* Health Priority Alert */}
        {systemData.health < 0.8 && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600" />
            <div>
              <p className="font-semibold text-red-800">System Health Below Threshold</p>
              <p className="text-red-600 text-sm">All experiments paused. Focus on ecosystem recovery.</p>
            </div>
          </div>
        )}

        {/* Main Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <Heart className="w-8 h-8 text-red-500" />
              <span className={`text-2xl font-bold ${systemData.health >= 0.8 ? 'text-green-600' : 'text-red-600'}`}>
                {(systemData.health * 100).toFixed(0)}%
              </span>
            </div>
            <h3 className="font-semibold text-gray-700">Ecosystem Health</h3>
            <p className="text-sm text-gray-500 mt-1">Primary metric - all else depends on this</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <Brain className="w-8 h-8 text-purple-500" />
              <span className="text-2xl font-bold text-gray-800">{systemData.coherenceEvents}</span>
            </div>
            <h3 className="font-semibold text-gray-700">Natural Coherence</h3>
            <p className="text-sm text-gray-500 mt-1">Synchronization events observed</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <Activity className="w-8 h-8 text-blue-500" />
              <span className="text-2xl font-bold text-gray-800">{systemData.daysMonitoring}</span>
            </div>
            <h3 className="font-semibold text-gray-700">Days Monitoring</h3>
            <p className="text-sm text-gray-500 mt-1">Continuous observation period</p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-2">
              <div className={`w-8 h-8 rounded-full ${currentPhase.color}`}></div>
              <Leaf className="w-6 h-6 text-gray-600" />
            </div>
            <h3 className="font-semibold text-gray-700">{currentPhase.name} Phase</h3>
            <p className="text-sm text-gray-500 mt-1">{currentPhase.description}</p>
          </div>
        </div>

        {/* Health Timeline */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">24-Hour Health Trend</h2>
          <div className="h-64 flex items-end justify-between gap-2">
            {healthHistory.map((point, i) => (
              <div key={i} className="flex-1 flex flex-col items-center">
                <div 
                  className={`w-full ${point.value >= 0.8 ? 'bg-green-400' : 'bg-yellow-400'} rounded-t`}
                  style={{ height: `${point.value * 100}%` }}
                ></div>
                <span className="text-xs text-gray-500 mt-2">{point.time}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Bioelectric Coherence */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Plant Bioelectric Signals</h2>
            <div className="space-y-3">
              {bioelectricData.map((plant, i) => (
                <div key={i} className="flex items-center justify-between">
                  <span className="font-medium text-gray-700">{plant.plant}</span>
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Signal:</span>
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${plant.signal * 100}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-gray-500">Sync:</span>
                      <div className="w-24 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-500 h-2 rounded-full"
                          style={{ width: `${plant.sync * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-sm text-gray-500 mt-4">
              Natural synchronization between plants - no intervention applied
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Ethical Compliance</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-700">Living System Consent</span>
                <span className={`px-3 py-1 rounded-full text-sm ${ethicalStatus.consent ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                  {ethicalStatus.consent ? 'Maintained' : 'Review Needed'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-700">Data Transparency</span>
                <span className="text-gray-600">{(ethicalStatus.transparency * 100).toFixed(0)}%</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-700">Community Approval</span>
                <span className={`px-3 py-1 rounded-full text-sm ${ethicalStatus.communityApproval ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'}`}>
                  {ethicalStatus.communityApproval ? 'Active' : 'Pending'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="font-medium text-gray-700">Last Ethics Review</span>
                <span className="text-gray-600">{ethicalStatus.lastReview}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Philosophy Quote */}
        <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 mb-6">
          <blockquote className="text-lg text-gray-700 italic">
            "We are not building a quantum computer. We are learning to recognize and collaborate 
            with the quantum computation that life already performs."
          </blockquote>
          <p className="text-sm text-gray-600 mt-2">— Living Quantum CEA Philosophy</p>
        </div>

        {/* Community Engagement */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Get Involved</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <h3 className="font-semibold text-gray-700 mb-1">View Raw Data</h3>
              <p className="text-sm text-gray-500">Access all sensor readings and analysis</p>
            </button>
            <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <h3 className="font-semibold text-gray-700 mb-1">Join Review Board</h3>
              <p className="text-sm text-gray-500">Help guide ethical decisions</p>
            </button>
            <button className="p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <h3 className="font-semibold text-gray-700 mb-1">Visit the Garden</h3>
              <p className="text-sm text-gray-500">Experience the living system yourself</p>
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500 mt-8">
          <p>Developed by Jason DeLooze for Open Source, Locally Sovereign Sustainability</p>
          <p className="mt-1">All data CC-BY-SA 4.0 • Code MIT Licensed • Methods Open Source</p>
        </div>
      </div>
    </div>
  );
};

export default LivingQuantumDashboard;