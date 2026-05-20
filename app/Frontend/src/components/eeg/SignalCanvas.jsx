import { useRef, useEffect, useState } from 'react'

const BUF_SIZE = 1000   // 4 secondes à 250 Hz

/**
 * Couleur de la courbe EEG selon l'état cognitif.
 * focused → vert cyan, stressed → rouge, relaxed → bleu, neutral → gris, invalid → gris foncé
 */
const STATE_COLOR = {
  focused:  '#00ffcc',
  stressed: '#ff4444',
  relaxed:  '#4488ff',
  neutral:  '#aabbcc',
  invalid:  '#445566',
}

const GLOW_COLOR = {
  focused:  'rgba(0,255,204,.35)',
  stressed: 'rgba(255,68,68,.35)',
  relaxed:  'rgba(68,136,255,.35)',
  neutral:  'rgba(170,187,204,.15)',
  invalid:  'rgba(68,85,102,.1)',
}

export default function SignalCanvas({ wsData, electrodeOk, cognitiveState = 'neutral' }) {
  const canvasRef      = useRef(null)
  const rawBuf         = useRef(new Float32Array(BUF_SIZE))
  const filtBuf        = useRef(new Float32Array(BUF_SIZE))
  const headRef        = useRef(0)
  const countRef       = useRef(0)
  const rafRef         = useRef(null)
  const [mode, setMode] = useState('filtered')
  const modeRef        = useRef('filtered')
  const electrodeRef   = useRef(electrodeOk)
  const stateRef       = useRef(cognitiveState)

  useEffect(() => { modeRef.current = mode },          [mode])
  useEffect(() => { electrodeRef.current = electrodeOk }, [electrodeOk])
  useEffect(() => { stateRef.current = cognitiveState },  [cognitiveState])

  // Remplir les buffers à chaque sample reçu
  useEffect(() => {
    if (!wsData) return
    const i = headRef.current % BUF_SIZE
    rawBuf.current[i]  = wsData.uv       ?? 0
    filtBuf.current[i] = wsData.filtered ?? 0
    headRef.current++
    countRef.current = Math.min(countRef.current + 1, BUF_SIZE)
  }, [wsData])

  // RAF — tracé oscilloscope
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    function draw() {
      rafRef.current = requestAnimationFrame(draw)
      const ctx = canvas.getContext('2d')
      const W = canvas.width, H = canvas.height
      ctx.clearRect(0, 0, W, H)

      // Fond
      ctx.fillStyle = '#060a12'
      ctx.fillRect(0, 0, W, H)

      // Électrodes déconnectées
      if (!electrodeRef.current) {
        ctx.fillStyle  = '#ff4d6d'
        ctx.font       = "12px 'Space Mono', monospace"
        ctx.textAlign  = 'center'
        ctx.fillText('Électrodes déconnectées — vérifiez le contact', W / 2, H / 2)
        ctx.textAlign  = 'left'
        return
      }

      // Grille horizontale
      ctx.strokeStyle = 'rgba(255,255,255,.035)'
      ctx.lineWidth   = 1
      for (let g = 1; g < 5; g++) {
        const y = H * g / 5
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
      }
      // Ligne centrale plus visible
      ctx.strokeStyle = 'rgba(255,255,255,.07)'
      ctx.beginPath(); ctx.moveTo(0, H / 2); ctx.lineTo(W, H / 2); ctx.stroke()

      // Grille verticale (repère 4s)
      ctx.strokeStyle = 'rgba(255,255,255,.035)'
      for (let g = 1; g < 4; g++) {
        const x = W * g / 4
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke()
      }

      const n = countRef.current
      if (n < 2) return

      const buf  = modeRef.current === 'raw' ? rawBuf.current : filtBuf.current
      const head = headRef.current

      // Données dans l'ordre temporel
      const data = new Float32Array(n)
      for (let i = 0; i < n; i++) {
        data[i] = buf[(head - n + i + BUF_SIZE) % BUF_SIZE]
      }

      // Centrage DC par médiane robuste
      const sorted = Float32Array.from(data).sort()
      const median = sorted[Math.floor(n / 2)]
      for (let i = 0; i < n; i++) data[i] -= median

      // Échelle ±3 RMS
      let sum2 = 0
      for (let i = 0; i < n; i++) sum2 += data[i] * data[i]
      const rms   = Math.sqrt(sum2 / n)
      const scale = rms > 0.1 ? Math.max(rms * 4, 5) : 50

      // Couleur selon état cognitif
      const st    = stateRef.current
      const color = modeRef.current === 'raw' ? '#1e3a5e' : (STATE_COLOR[st] ?? STATE_COLOR.neutral)
      const glow  = modeRef.current === 'raw' ? 'transparent' : (GLOW_COLOR[st] ?? GLOW_COLOR.neutral)

      ctx.beginPath()
      ctx.strokeStyle = color
      ctx.lineWidth   = modeRef.current === 'raw' ? 1 : 1.8
      ctx.shadowBlur  = modeRef.current === 'filtered' ? 10 : 0
      ctx.shadowColor = glow

      for (let i = 0; i < n; i++) {
        const x = (i / (BUF_SIZE - 1)) * W
        const y = H / 2 - (data[i] / scale) * (H / 2.2)
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
      }
      ctx.stroke()
      ctx.shadowBlur = 0

      // Labels
      ctx.fillStyle = 'rgba(255,255,255,.22)'
      ctx.font      = "10px 'Space Mono', monospace"
      ctx.fillText(`±${Math.round(scale)} µV`, 6, 14)
      ctx.fillText('4s', W - 22, 14)

      // Indicateur état cognitif
      if (modeRef.current === 'filtered' && st && st !== 'neutral') {
        ctx.fillStyle = color
        ctx.fillText(st.toUpperCase(), 6, H - 8)
      }
    }

    draw()
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [])

  return (
    <div className="relative w-full h-full">
      <canvas
        ref={canvasRef}
        width={1200}
        height={260}
        style={{ width: '100%', height: '100%', borderRadius: 8, display: 'block' }}
      />
      {/* Mode RAW / FILTRÉ */}
      <div className="absolute top-2 right-2 flex gap-1">
        {['raw', 'filtered'].map(m => (
          <button
            key={m}
            onClick={() => setMode(m)}
            className="px-2 py-0.5 rounded text-[9px] font-mono border transition-all"
            style={{
              background:   mode === m ? (m === 'filtered' ? 'rgba(0,255,204,.12)' : 'rgba(30,58,94,.3)') : 'transparent',
              borderColor:  mode === m ? (m === 'filtered' ? 'rgba(0,255,204,.5)' : 'rgba(30,58,140,.5)') : 'rgba(255,255,255,.1)',
              color:        mode === m ? (m === 'filtered' ? '#00ffcc' : '#6a8aae') : '#3a4a5e',
            }}
          >
            {m === 'raw' ? 'RAW' : 'FILTRÉ'}
          </button>
        ))}
      </div>
      {/* Légende couleurs états */}
      <div className="absolute bottom-2 right-2 flex gap-2">
        {Object.entries(STATE_COLOR).map(([s, c]) => (
          <span key={s} className="flex items-center gap-1 text-[8px] font-mono opacity-50">
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: c, display: 'inline-block' }} />
            {s}
          </span>
        ))}
      </div>
    </div>
  )
}
