import { useEffect, useRef } from 'react'

const HISTORY_LEN = 200
const COLORS = {
  concentration: '#34d399',
  stress:        '#f87171',
  neutral:       '#94a3b8',
  uncertain:     '#fbbf24',
}

export default function MiniEEGOscilloscope({ wsData, eegState, mlPrediction, features }) {
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
    ctx.fillStyle = 'rgba(15,17,23,0.6)'
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

  return (
    <div className="space-y-2">
      {/* État actuel */}
      <div className="flex items-center justify-between">
        <span className={`text-xs font-bold ${stl.color}`}>{stl.label}</span>
        {conf != null && <span className="text-xs font-mono text-nc-muted">{conf}%</span>}
      </div>

      {/* Oscilloscope */}
      <canvas
        ref={canvasRef}
        width={200} height={90}
        className="w-full rounded-xl border border-nc-border/30"
        style={{ imageRendering: 'pixelated' }}
      />

      {/* Features clés */}
      <div className="space-y-1 text-[10px]">
        {[
          ['Alpha', `${alpha}%`],
          ['Beta',  `${beta}%`],
          ['TBR',   tbr],
        ].map(([k, v]) => (
          <div key={k} className="flex justify-between">
            <span className="text-nc-muted">{k}</span>
            <span className="font-mono font-semibold text-nc-text">{v}</span>
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
