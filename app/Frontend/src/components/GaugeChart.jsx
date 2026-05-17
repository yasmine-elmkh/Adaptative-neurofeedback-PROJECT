/**
 * =============================================================================
 * COMPOSANT JAUGE ANIMÉE - Affichage P(Concentration) et P(Stress)
 * =============================================================================
 * Utilise Chart.js avec plugin doughnut pour affichage circulaire
 * 
 * Features:
 * - Animation fluide des valeurs
 * - Couleurs dynamiques (gradient)
 * - Seuils visuels (zone verte/orange/rouge)
 * - Responsive design
 * 
 * Usage:
 * <GaugeChart value={75} label="Concentration" color="blue" />
 */

import { useState, useEffect } from 'react';
import { Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function GaugeChart({ value = 0, label = "Metric", color = "blue" }) {
  const [animatedValue, setAnimatedValue] = useState(0);

  // Animation: interpolation linéaire vers la valeur cible
  useEffect(() => {
    let animationFrame;
    let start = animatedValue;
    let diff = value - start;
    let duration = 500; // ms
    let startTime = Date.now();

    const animate = () => {
      let elapsed = Date.now() - startTime;
      let progress = Math.min(elapsed / duration, 1);
      setAnimatedValue(start + diff * progress);

      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };

    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [value]);

  // Déterminer la couleur en fonction de la valeur
  const getColor = () => {
    if (animatedValue >= 70) return '#10b981'; // vert
    if (animatedValue >= 50) return '#f59e0b'; // orange
    return '#ef4444'; // rouge
  };

  // Données pour le graphique doughnut
  const data = {
    labels: [label, 'Inactive'],
    datasets: [
      {
        data: [animatedValue, 100 - animatedValue],
        backgroundColor: [getColor(), 'rgba(255,255,255,0.1)'],
        borderColor: ['white', 'transparent'],
        borderWidth: 2,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        enabled: false,
      },
    },
    cutout: '75%', // Épaisseur du doughnut
  };

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative w-40 h-40">
        <Doughnut data={data} options={options} />
        
        {/* Texte au centre du doughnut */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-4xl font-bold text-white">
            {animatedValue.toFixed(0)}%
          </div>
          <div className="text-sm text-gray-300">{label}</div>
        </div>
      </div>

      {/* Indicateur de qualité */}
      <div className="mt-4 w-full">
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full transition-all duration-300"
            style={{
              width: `${animatedValue}%`,
              backgroundColor: getColor(),
            }}
          />
        </div>
      </div>
    </div>
  );
}