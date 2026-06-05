/**
 * Page de session en direct
 * - Affiche P(Concentration) et P(Stress) en temps réel
 * - Streaming WebSocket toutes les 500ms
 * - Visualisations 3D, jauges, graphiques
 */

import { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuthStore } from '../stores';
import EEGVisualization from '../components/EEGVisualization';
import GaugeChart from '../components/GaugeChart';
import BiofeedbackGame from '../components/BiofeedbackGame';

export default function SessionPage() {
  const { sessionId } = useParams();
  const token = useAuthStore((s) => s.token);
  const [eegData, setEegData] = useState(null);
  const [sessionMetrics, setSessionMetrics] = useState({
    score: 0,
    avgTBR: 0,
    successRate: 0
  });
  const wsRef = useRef(null);

  useEffect(() => {
    // Connecter WebSocket pour streaming EEG
    const ws = new WebSocket(
      `/ws/session/${sessionId}?token=${token}`
    );

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEegData(data);
      
      // Mettre à jour les métriques
      setSessionMetrics(prev => ({
        ...prev,
        score: (data.p_concentration * 100).toFixed(1)
      }));
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current = ws;

    return () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.close();
      }
    };
  }, [sessionId, token]);

  if (!eegData) {
    return <div className="p-8">Loading session...</div>;
  }

  return (
    <div className="p-8 bg-gradient-to-br from-blue-900 to-purple-900 min-h-screen text-white">
      <h1 className="text-4xl font-bold mb-8">Session in Progress</h1>

      <div className="grid grid-cols-3 gap-8">
        {/* Colonne 1: Jauges P(Concentration) & P(Stress) */}
        <div className="bg-white/10 p-8 rounded-lg backdrop-blur">
          <GaugeChart 
            value={eegData.p_concentration * 100} 
            label="Concentration"
            color="blue"
          />
          <GaugeChart 
            value={eegData.p_stress * 100} 
            label="Stress"
            color="red"
          />
        </div>

        {/* Colonne 2: Visualisation EEG 3D */}
        <div className="bg-white/10 p-8 rounded-lg backdrop-blur">
          <EEGVisualization 
            data={eegData}
            iapf={eegData.iapf}
          />
        </div>

        {/* Colonne 3: Jeu de feedback */}
        <div className="bg-white/10 p-8 rounded-lg backdrop-blur">
          <BiofeedbackGame 
            concentration={eegData.p_concentration}
            stress={eegData.p_stress}
          />
        </div>
      </div>

      {/* Barre inférieure: Métriques en direct */}
      <div className="mt-8 grid grid-cols-4 gap-4">
        <div className="bg-blue-500/20 p-4 rounded">
          <p className="text-sm opacity-75">Score Session</p>
          <p className="text-3xl font-bold">{sessionMetrics.score}%</p>
        </div>
        <div className="bg-green-500/20 p-4 rounded">
          <p className="text-sm opacity-75">Avg TBR</p>
          <p className="text-3xl font-bold">{eegData.tbr?.toFixed(2)}</p>
        </div>
        <div className="bg-purple-500/20 p-4 rounded">
          <p className="text-sm opacity-75">Signal Quality</p>
          <p className="text-3xl font-bold">{(eegData.signal_quality * 100).toFixed(0)}%</p>
        </div>
        <div className="bg-orange-500/20 p-4 rounded">
          <p className="text-sm opacity-75">Model Latency</p>
          <p className="text-3xl font-bold">{eegData.model_latency_ms?.toFixed(1)}ms</p>
        </div>
      </div>
    </div>
  );
}