import { useRef, useEffect, useState } from 'react'

const BUF_SIZE = 1000   // 4 secondes à 250 Hz
const COLORS   = { raw: '#1e3a5e', filtered: '#00e5b0' }

/**
 * SignalCanvas — oscilloscope EEG temps réel.
 * Reçoit { uv, filtered } via prop wsData.
 * Bascule RAW / FILTRÉ via bouton.
 * Centrage automatique sur la médiane (suppression DC offset).
 */
export default function SignalCanvas({ wsData, electrodeOk }) {
  const canvasRef       = useRef(null)
  const rawBuf          = useRef(new Float32Array(BUF_SIZE))
  const filtBuf         = useRef(new Float32Array(BUF_SIZE))
  const headRef         = useRef(0)
  const countRef        = useRef(0)
  const rafRef          = useRef(null)
  const [mode, setMode] = useState('filtered')  // 'raw' | 'filtered'
  const modeRef         = useRef('filtered')
  const electrodeOkRef  = useRef(electrodeOk)

  // Sync refs pour closures stables dans RAF
  useEffect(() => { modeRef.current = mode }, [mode])
  useEffect(() => { electrodeOkRef.current = electrodeOk }, [electrodeOk])

  // Remplir les buffers à chaque sample reçu
  useEffect(() => {
    if (!wsData) return
    const i = headRef.current % BUF_SIZE
    rawBuf.current[i]  = wsData.uv       ?? 0
    filtBuf.current[i] = wsData.filtered ?? 0
    headRef.current++
    countRef.current = Math.min(countRef.current + 1, BUF_SIZE)
  }, [wsData])

  // Boucle RAF pour le dessin
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

      // Électrodes déconnectées → message et sortie anticipée
      if (!electrodeOkRef.current) {
        ctx.fillStyle   = '#ff4d6d'
        ctx.font        = "12px 'Space Mono', monospace"
        ctx.textAlign   = 'center'
        ctx.fillText('Électrodes déconnectées', W / 2, H / 2)
        ctx.textAlign   = 'left'
        return
      }

      // Grille horizontale
      ctx.strokeStyle = 'rgba(255,255,255,.04)'
      ctx.lineWidth = 1
      for (let g = 1; g < 5; g++) {
        const y = H * g / 5
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
      }
      // Ligne centrale
      ctx.strokeStyle = 'rgba(255,255,255,.08)'
      ctx.beginPath(); ctx.moveTo(0, H/2); ctx.lineTo(W, H/2); ctx.stroke()

      // Grille verticale (4s)
      ctx.strokeStyle = 'rgba(255,255,255,.04)'
      for (let g = 1; g < 4; g++) {
        const x = W * g / 4
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke()
      }

      const n = countRef.current
      if (n < 2) return

      const buf = modeRef.current === 'raw' ? rawBuf.current : filtBuf.current
      const head = headRef.current

      // Extraire les données dans l'ordre temporel
      const data = new Float32Array(n)
      for (let i = 0; i < n; i++) {
        data[i] = buf[(head - n + i + BUF_SIZE) % BUF_SIZE]
      }

      // Centrage DC par médiane robuste
      const sorted = Float32Array.from(data).sort()
      const median = sorted[Math.floor(n / 2)]
      for (let i = 0; i < n; i++) data[i] -= median

      // Échelle adaptative ±3 écart-types
      let sum2 = 0
      for (let i = 0; i < n; i++) sum2 += data[i] * data[i]
      const rms = Math.sqrt(sum2 / n)
      const scale = rms > 0.1 ? Math.max(rms * 4, 5) : 50  // µV → pixels

      // Tracé signal
      ctx.beginPath()
      ctx.strokeStyle = modeRef.current === 'raw' ? COLORS.raw : COLORS.filtered
      ctx.lineWidth   = modeRef.current === 'raw' ? 1 : 1.5
      ctx.shadowBlur  = modeRef.current === 'filtered' ? 6 : 0
      ctx.shadowColor = COLORS.filtered

      for (let i = 0; i < n; i++) {
        const x = (i / (BUF_SIZE - 1)) * W
        const y = H / 2 - (data[i] / scale) * (H / 2.2)
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
      }
      ctx.stroke()
      ctx.shadowBlur = 0

      // Labels
      ctx.fillStyle = 'rgba(255,255,255,.25)'
      ctx.font      = `10px 'Space Mono', monospace`
      ctx.fillText(`±${Math.round(scale)} µV`, 6, 14)
      ctx.fillText('4s', W - 22, 14)
    }

    draw()
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [])

  return (
    <div style={{ position:'relative', width:'100%', height:'100%' }}>
      <canvas
        ref={canvasRef}
        width={1200}
        height={260}
        style={{ width:'100%', height:'100%', borderRadius:8, display:'block' }}
      />
      {/* Boutons RAW / FILTRÉ */}
      <div style={{
        position:'absolute', top:8, right:8,
        display:'flex', gap:4,
      }}>
        {['raw','filtered'].map(m => (
          <button key={m} onClick={() => setMode(m)} style={{
            padding:'3px 10px', borderRadius:5, fontSize:9,
            fontFamily:"'Space Mono',monospace", letterSpacing:.5,
            border:'1px solid',
            background: mode === m ? (m === 'filtered' ? 'rgba(0,229,176,.15)' : 'rgba(77,102,142,.15)') : 'transparent',
            borderColor: mode === m ? (m === 'filtered' ? 'rgba(0,229,176,.5)' : 'rgba(77,102,142,.5)') : 'rgba(255,255,255,.08)',
            color: mode === m ? (m === 'filtered' ? '#00e5b0' : '#6a8aae') : '#3a4a5e',
            cursor:'pointer',
          }}>
            {m === 'raw' ? 'RAW' : 'FILTRÉ'}
          </button>
        ))}
      </div>
    </div>
  )
}
