/**
 * NeuroCap — Indicateur de qualité du signal EEG
 *
 * Props :
 *   quality   : float 0–1  (0 = très mauvais, 1 = parfait)
 *   connected : bool        (false = pas de connexion WebSocket)
 */
import { Wifi, WifiOff } from 'lucide-react'

const LEVELS = [
  { min: 0.75, label: 'Excellent', color: 'text-nc-success',  barColor: 'bg-nc-success'  },
  { min: 0.50, label: 'Bon',       color: 'text-nc-accent',   barColor: 'bg-nc-accent'   },
  { min: 0.25, label: 'Faible',    color: 'text-nc-warning',  barColor: 'bg-nc-warning'  },
  { min: 0,    label: 'Mauvais',   color: 'text-nc-danger',   barColor: 'bg-nc-danger'   },
]

function getLevel(quality) {
  return LEVELS.find(l => quality >= l.min) ?? LEVELS[LEVELS.length - 1]
}

export default function SignalQuality({ quality = 0, connected = false }) {
  if (!connected) {
    return (
      <div className="flex items-center gap-1.5 text-nc-muted text-xs">
        <WifiOff className="w-4 h-4" />
        <span>Déconnecté</span>
      </div>
    )
  }

  const level = getLevel(quality)
  const pct   = Math.round(quality * 100)

  return (
    <div className="flex items-center gap-2">
      {/* Icône wifi colorée selon le niveau */}
      <Wifi className={`w-4 h-4 ${level.color}`} />

      {/* Barres empilées (style signal mobile) */}
      <div className="flex items-end gap-0.5 h-4">
        {[0.25, 0.50, 0.75, 1.0].map((threshold, i) => (
          <div
            key={i}
            className={`w-1 rounded-sm transition-colors duration-300 ${
              quality >= threshold ? level.barColor : 'bg-nc-border'
            }`}
            style={{ height: `${40 + i * 20}%` }}
          />
        ))}
      </div>

      {/* Label + pourcentage */}
      <span className={`text-xs font-medium ${level.color}`}>
        {level.label} <span className="opacity-70">({pct}%)</span>
      </span>
    </div>
  )
}
