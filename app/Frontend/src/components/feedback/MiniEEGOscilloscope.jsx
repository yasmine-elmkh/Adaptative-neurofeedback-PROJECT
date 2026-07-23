import { useEffect, useRef } from 'react'

const HISTORY_LEN = 200
const COLORS = {
  concentration: '#34d399',
  stress:        '#f87171',
  neutral:       '#94a3b8',
  uncertain:     '#fbbf24',
}

export default function MiniEEGOscilloscope({ wsData, eegState, mlPrediction, features, compact = false, canvasHeight = 90, hideLabel = false }) {
  const canvasRef  = useRef(null)
  const bufferRef  = useRef([])

  // Alimenter le buffer à partir des trames WebSocket
  useEffect(() => {
    if (wsData?.filtered != null) {
      bufferRef.current.push(wsData.filtered)
      if (bufferRef.current.length > HISTORY_LEN) bufferRef.current.shift()
    }
  }, [wsData])

  // Dessin canvas
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const W = canvas.width
    const H = canvas.height
    const buf = bufferRef.current

    ctx.clearRect(0, 0, W, H)

    // Fond
    ctx.clearRect(0, 0, W, H)
    ctx.fillStyle = 'rgba(6,14,24,0.85)'
    ctx.fillRect(0, 0, W, H)

    if (buf.length < 2) return

    // Ligne médiane
    ctx.strokeStyle = 'rgba(148,163,184,0.1)'
    ctx.lineWidth = 0.5
    ctx.beginPath()
    ctx.moveTo(0, H / 2)
    ctx.lineTo(W, H / 2)
    ctx.stroke()

    // Normalisation
    const min = Math.min(...buf)
    const max = Math.max(...buf)
    const range = max - min || 1

    const color = COLORS[mlPrediction?.state] ?? COLORS.neutral
    ctx.strokeStyle = color
    ctx.lineWidth = 1.5
    ctx.shadowColor = color
    ctx.shadowBlur = 4
    ctx.beginPath()

    buf.forEach((v, i) => {
      const x = (i / (HISTORY_LEN - 1)) * W
      const y = H - ((v - min) / range) * H * 0.85 - H * 0.075
      if (i === 0) ctx.moveTo(x, y)
      else ctx.lineTo(x, y)
    })
    ctx.stroke()
  })

  const conf   = mlPrediction ? Math.round((mlPrediction.confidence ?? 0) * 100) : null
  const alpha  = features?.rel_alpha  != null ? (features.rel_alpha  * 100).toFixed(1) : '—'
  const beta   = features?.rel_beta   != null ? (features.rel_beta   * 100).toFixed(1) : '—'
  const tbr    = features?.theta_beta != null ? features.theta_beta.toFixed(2)          : '—'

  const STATE_LABEL = {
    concentration: { label: 'CONCENTRATION', color: 'text-emerald-400' },
    stress:        { label: 'STRESS',         color: 'text-red-400'     },
    neutral:       { label: 'NEUTRE',         color: 'text-nc-muted'    },
    uncertain:     { label: 'INCERTAIN',      color: 'text-yellow-400'  },
  }
  const stl = STATE_LABEL[mlPrediction?.state] ?? STATE_LABEL.neutral

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        <span className={`text-[10px] font-bold ${stl.color} shrink-0`}>{stl.label}</span>
        <canvas
          ref={canvasRef}
          width={300} height={44}
          className="flex-1 rounded-lg border border-nc-border/30"
          style={{ imageRendering: 'pixelated', height: 44 }}
        />
        {conf != null && (
          <span className="text-[10px] font-mono text-nc-muted shrink-0">{conf}%</span>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-2">
      {/* État actuel */}
      {!hideLabel && (
        <div className="flex items-center justify-between">
          <span className={`text-xs font-bold ${stl.color}`}>{stl.label}</span>
          {conf != null && <span className="text-xs font-mono text-nc-muted">{conf}%</span>}
        </div>
      )}

      {/* Oscilloscope */}
      <canvas
        ref={canvasRef}
        width={200} height={canvasHeight}
        className="w-full rounded-xl border border-nc-border/30"
        style={{ imageRendering: 'pixelated', height: canvasHeight }}
      />

      {/* Features clés */}
      <div className="space-y-1.5 text-[10px]">
        {[
          { k: 'Alpha', v: alpha, raw: features?.rel_alpha  ?? 0, color: '#22d3ee', glow: 'rgba(34,211,238,0.6)'  },
          { k: 'Beta',  v: beta,  raw: features?.rel_beta   ?? 0, color: '#fb923c', glow: 'rgba(251,146,60,0.6)'  },
          { k: 'TBR',   v: tbr,   raw: Math.min((features?.theta_beta ?? 0) / 4, 1), color: '#a78bfa', glow: 'rgba(167,139,250,0.6)' },
        ].map(({ k, v, raw, color, glow }) => (
          <div key={k} className="space-y-0.5">
            <div className="flex justify-between items-center">
              <span className="font-semibold" style={{ color }}>{k}</span>
              <span className="font-mono font-bold" style={{ color, textShadow: `0 0 8px ${glow}` }}>{v}</span>
            </div>
            <div className="h-1 rounded-full overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
              <div className="h-full rounded-full transition-all duration-700"
                style={{
                  width: `${Math.min(raw * 100, 100)}%`,
                  background: `linear-gradient(90deg, ${color}aa, ${color})`,
                  boxShadow: `0 0 6px ${glow}`,
                }} />
            </div>
          </div>
        ))}
      </div>

      {/* Jauge "temps en zone cible" */}
      {mlPrediction && (
        <div>
          <div className="flex justify-between text-[9px] mb-0.5">
            <span className="text-nc-muted">Conf. IA</span>
            <span className={`font-mono font-bold ${stl.color}`}>{conf}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-nc-surface2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                mlPrediction.state === 'concentration' ? 'bg-emerald-500' :
                mlPrediction.state === 'stress'        ? 'bg-red-500' : 'bg-nc-muted'
              }`}
              style={{ width: `${conf}%` }}
            />
          </div>
        </div>
      )}
    </div>
  )
}
