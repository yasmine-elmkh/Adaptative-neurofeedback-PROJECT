import { useRef, useEffect, useState } from 'react'

const BUF_SIZE = 250   // 250 samples — fenêtre glissante affichée sur toute la largeur dès le 1er sample
const COLORS   = { raw: '#1e3a5e', filtered: '#00e5b0' }

/**
 * SignalCanvas — oscilloscope EEG temps réel.
 * Accepte SOIT signalQueue (ref vers tableau de {uv,filtered}) SOIT wsData (prop React legacy).
 * signalQueue est préféré : les samples sont drainés dans le RAF → aucune perte par batching React.
 */
export default function SignalCanvas({ wsData, signalQueue, electrodeOk }) {
  const canvasRef       = useRef(null)
  const rawBuf          = useRef(new Float32Array(BUF_SIZE))
  const filtBuf         = useRef(new Float32Array(BUF_SIZE))
  const headRef         = useRef(0)
  const countRef        = useRef(0)
  const rafRef          = useRef(null)
  const [mode, setMode] = useState('filtered')
  const modeRef         = useRef('filtered')
  const electrodeOkRef  = useRef(electrodeOk)

  useEffect(() => { modeRef.current = mode }, [mode])
  useEffect(() => { electrodeOkRef.current = electrodeOk }, [electrodeOk])

  // Fallback legacy : wsData prop (React state batched) — utilisé seulement si pas de signalQueue
  useEffect(() => {
    if (signalQueue) return   // signalQueue gère le push dans le RAF
    if (!wsData) return
    const i = headRef.current % BUF_SIZE
    rawBuf.current[i]  = wsData.uv       ?? 0
    filtBuf.current[i] = wsData.filtered ?? 0
    headRef.current++
    countRef.current = Math.min(countRef.current + 1, BUF_SIZE)
  }, [wsData, signalQueue])

  // Boucle RAF — drain la file ref à chaque frame si disponible
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    function push(uv, filtered) {
      const i = headRef.current % BUF_SIZE
      rawBuf.current[i]  = uv       ?? 0
      filtBuf.current[i] = filtered ?? 0
      headRef.current++
      countRef.current = Math.min(countRef.current + 1, BUF_SIZE)
    }

    function draw() {
      rafRef.current = requestAnimationFrame(draw)

      // ── Drain la file de samples (true real-time, aucune perte) ──────────────
      if (signalQueue?.current?.length) {
        const batch = signalQueue.current.splice(0)
        for (const s of batch) push(s.uv, s.filtered)
      }

      const ctx = canvas.getContext('2d')
      const W = canvas.width, H = canvas.height
      ctx.clearRect(0, 0, W, H)

      ctx.fillStyle = '#060a12'
      ctx.fillRect(0, 0, W, H)

      if (!electrodeOkRef.current) {
        ctx.fillStyle = '#ff4d6d'
        ctx.font = "12px 'Space Mono', monospace"
        ctx.textAlign = 'center'
        ctx.fillText('Électrodes déconnectées', W / 2, H / 2)
        ctx.textAlign = 'left'
        return
      }

      // Grille
      ctx.strokeStyle = 'rgba(255,255,255,.04)'
      ctx.lineWidth = 1
      for (let g = 1; g < 5; g++) {
        const y = H * g / 5
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
      }
      ctx.strokeStyle = 'rgba(255,255,255,.08)'
      ctx.beginPath(); ctx.moveTo(0, H/2); ctx.lineTo(W, H/2); ctx.stroke()
      ctx.strokeStyle = 'rgba(255,255,255,.04)'
      for (let g = 1; g < 4; g++) {
        const x = W * g / 4
        ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke()
      }

      const n = countRef.current
      if (n < 2) return

      const buf  = modeRef.current === 'raw' ? rawBuf.current : filtBuf.current
      const head = headRef.current

      const data = new Float32Array(n)
      for (let i = 0; i < n; i++) {
        data[i] = buf[(head - n + i + BUF_SIZE) % BUF_SIZE]
      }

      // Centrage DC par médiane
      const sorted = Float32Array.from(data).sort()
      const median = sorted[Math.floor(n / 2)]
      for (let i = 0; i < n; i++) data[i] -= median

      // Échelle ±3 RMS
      let sum2 = 0
      for (let i = 0; i < n; i++) sum2 += data[i] * data[i]
      const rms = Math.sqrt(sum2 / n)
      const scale = rms > 0.1 ? Math.max(rms * 4, 5) : 50

      ctx.beginPath()
      ctx.strokeStyle = modeRef.current === 'raw' ? COLORS.raw : COLORS.filtered
      ctx.lineWidth   = modeRef.current === 'raw' ? 1 : 1.5
      ctx.shadowBlur  = modeRef.current === 'filtered' ? 6 : 0
      ctx.shadowColor = COLORS.filtered

      // ── Tracé — les n points couvrent TOUJOURS toute la largeur (oscilloscope réel) ──
      for (let i = 0; i < n; i++) {
        const x = (i / (n - 1)) * W
        const y = H / 2 - (data[i] / scale) * (H / 2.2)
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
      }
      ctx.stroke()
      ctx.shadowBlur = 0

      // Ligne de tête (bord droit = échantillon le plus récent)
      ctx.strokeStyle = 'rgba(0,229,176,.25)'
      ctx.lineWidth = 1
      ctx.beginPath(); ctx.moveTo(W - 1, 0); ctx.lineTo(W - 1, H); ctx.stroke()

      // Labels
      const winSec = (n / 125).toFixed(1)   // ~125 Hz après throttle ×2
      ctx.fillStyle = 'rgba(255,255,255,.25)'
      ctx.font = `10px 'Space Mono', monospace`
      ctx.fillText(`±${Math.round(scale)} µV`, 6, 14)
      ctx.fillText(`${winSec}s`, W - 26, 14)
    }

    draw()
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [signalQueue])  // signalQueue est une ref stable → pas de restart du RAF

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%' }}>
      <canvas
        ref={canvasRef}
        width={1200}
        height={260}
        style={{ width: '100%', height: '100%', borderRadius: 8, display: 'block' }}
      />
      <div style={{ position: 'absolute', top: 8, right: 8, display: 'flex', gap: 4 }}>
        {['raw', 'filtered'].map(m => (
          <button key={m} onClick={() => setMode(m)} style={{
            padding: '3px 10px', borderRadius: 5, fontSize: 9,
            fontFamily: "'Space Mono',monospace", letterSpacing: .5,
            border: '1px solid',
            background: mode === m ? (m === 'filtered' ? 'rgba(0,229,176,.15)' : 'rgba(77,102,142,.15)') : 'transparent',
            borderColor: mode === m ? (m === 'filtered' ? 'rgba(0,229,176,.5)' : 'rgba(77,102,142,.5)') : 'rgba(255,255,255,.08)',
            color: mode === m ? (m === 'filtered' ? '#00e5b0' : '#6a8aae') : '#3a4a5e',
            cursor: 'pointer',
          }}>
            {m === 'raw' ? 'RAW' : 'FILTRÉ'}
          </button>
        ))}
      </div>
    </div>
  )
}
