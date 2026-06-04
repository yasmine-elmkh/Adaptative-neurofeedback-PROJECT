import { useRef, useEffect, useState } from 'react'

// ── Constantes ────────────────────────────────────────────────────────────────
const BUF_SIZE      = 1000   // 4 s à 250 Hz
const MARGIN_LEFT   = 54     // zone axe Y (labels µV)
const MARGIN_BOTTOM = 22     // zone axe X (labels temps)
const MARGIN_TOP    = 8      // marge haut
const MARGIN_RIGHT  = 10     // marge droite

const Y_LEVELS = [1, 0.5, 0, -0.5, -1]

const STATE_COLOR = {
  focused:  '#00ffcc',
  stressed: '#ff4444',
  relaxed:  '#4488ff',
  neutral:  '#88aacc',
  invalid:  '#445566',
}
const GLOW_COLOR = {
  focused:  'rgba(0,255,204,.30)',
  stressed: 'rgba(255,68,68,.30)',
  relaxed:  'rgba(68,136,255,.30)',
  neutral:  'rgba(136,170,204,.12)',
  invalid:  'rgba(68,85,102,.08)',
}

// ── Calcul d'échelle robuste (percentile 5–95 %) ─────────────────────────────
function robustScale(data, n) {
  if (n < 4) return 80
  const sorted = Float32Array.from(data).sort()
  const p5  = sorted[Math.floor(n * 0.05)]
  const p95 = sorted[Math.floor(n * 0.95)]
  const halfRange = (p95 - p5) / 2
  // Pas de cap supérieur : le signal peut être en µV amplifiés (gain AD8232).
  // Le plancher de 15 µV évite une division par zéro sur signal plat.
  return Math.max(15, halfRange > 0 ? halfRange * 1.4 : 80)
}

function fmtUv(v) {
  if (Math.abs(v) >= 100) return `${Math.round(v)}`
  if (Math.abs(v) >= 10)  return v.toFixed(0)
  return v.toFixed(1)
}

// ── Pipeline appliqué (affiché dans le badge) ────────────────────────────────
const PIPELINE_LABEL = 'EMA DC · Notch 50/100 Hz · BP 1–45 Hz'

export default function SignalCanvas({ wsData, electrodeOk, cognitiveState = 'neutral' }) {
  const canvasRef    = useRef(null)
  // Un seul buffer : signal filtré uniquement (wsData.filtered)
  const filtBuf      = useRef(new Float32Array(BUF_SIZE))
  const headRef      = useRef(0)
  const countRef     = useRef(0)
  const rafRef       = useRef(null)

  const electrodeRef = useRef(electrodeOk)
  const stateRef     = useRef(cognitiveState)
  const [currentScale, setScale] = useState(50)

  useEffect(() => { stateRef.current = cognitiveState }, [cognitiveState])

  useEffect(() => {
    electrodeRef.current = electrodeOk
    if (!electrodeOk) {
      filtBuf.current.fill(0)
      headRef.current  = 0
      countRef.current = 0
    }
  }, [electrodeOk])

  // ── Alimentation buffer — signal filtré UNIQUEMENT ──────────────────────────
  // wsData.filtered = sortie de filter_sample() côté backend :
  //   EMA DC removal → Notch 50 Hz → Notch 100 Hz → BP Butterworth 1-45 Hz
  // Le backend envoie 0.0 pendant le warm-up (500 premiers samples).
  useEffect(() => {
    if (!wsData || !electrodeRef.current) return
    // Clamp à ±500 000 µV : protège contre les valeurs infinies ou NaN
    // sans clipper un signal amplifié par AD8232 (gain ×100–×1000).
    const val = Math.max(-500000, Math.min(500000, wsData.filtered ?? 0))
    const i = headRef.current % BUF_SIZE
    filtBuf.current[i] = val
    headRef.current++
    countRef.current = Math.min(countRef.current + 1, BUF_SIZE)
  }, [wsData])

  // ── Boucle RAF — oscilloscope filtré ─────────────────────────────────────
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    // Démarrer large pour éviter le clipping pendant l'adaptation initiale.
    // α=0.08 → convergence à ~63 % en ~13 frames (~220 ms à 60fps) au lieu de ~550 ms.
    let scaleSmooth = 200

    function draw() {
      rafRef.current = requestAnimationFrame(draw)

      const ctx = canvas.getContext('2d')
      const W   = canvas.width
      const H   = canvas.height
      const px  = MARGIN_LEFT
      const py  = MARGIN_TOP
      const pw  = W - MARGIN_LEFT - MARGIN_RIGHT
      const ph  = H - MARGIN_TOP  - MARGIN_BOTTOM
      const cy  = py + ph / 2

      ctx.clearRect(0, 0, W, H)

      ctx.fillStyle = '#060a12'
      ctx.fillRect(0, 0, W, H)
      ctx.fillStyle = '#080d18'
      ctx.fillRect(px, py, pw, ph)

      // ── Électrode déconnectée ─────────────────────────────────────────────
      if (!electrodeRef.current) {
        ctx.fillStyle = '#ff4d6d'
        ctx.font      = "11px 'Space Mono', monospace"
        ctx.textAlign = 'center'
        ctx.fillText('Électrodes déconnectées', px + pw / 2, py + ph / 2 - 8)
        ctx.fillStyle = '#7a2030'
        ctx.font      = "9px 'Space Mono', monospace"
        ctx.fillText('Vérifiez le contact électrode', px + pw / 2, py + ph / 2 + 10)
        ctx.textAlign = 'left'
        _drawAxes(ctx, W, H, px, py, pw, ph, cy, 50)
        return
      }

      const n = countRef.current
      if (n < 2) {
        _drawAxes(ctx, W, H, px, py, pw, ph, cy, scaleSmooth)
        _drawWaiting(ctx, px, py, pw, ph)
        return
      }

      // ── Lecture buffer filtré ─────────────────────────────────────────────
      const head = headRef.current
      const data = new Float32Array(n)
      for (let i = 0; i < n; i++) {
        data[i] = filtBuf.current[(head - n + i + BUF_SIZE) % BUF_SIZE]
      }

      // ── Suppression résiduelle DC côté affichage (médiane robuste) ────────
      const sorted = Float32Array.from(data).sort()
      const median = sorted[Math.floor(n / 2)]
      for (let i = 0; i < n; i++) data[i] -= median

      // ── Échelle robuste ───────────────────────────────────────────────────
      const targetScale = robustScale(data, n)
      // α=0.08 : converge à 63 % en ~13 frames (220 ms) — évite le clipping initial
      scaleSmooth = scaleSmooth * 0.92 + targetScale * 0.08
      const scale = scaleSmooth
      setScale(Math.round(scale))

      _drawAxes(ctx, W, H, px, py, pw, ph, cy, scale)

      // ── Tracé signal — couleur selon état cognitif ────────────────────────
      const st    = stateRef.current
      const color = STATE_COLOR[st] ?? STATE_COLOR.neutral
      const glow  = GLOW_COLOR[st]  ?? GLOW_COLOR.neutral

      ctx.save()
      ctx.beginPath()
      ctx.rect(px, py, pw, ph)
      ctx.clip()

      ctx.beginPath()
      ctx.strokeStyle = color
      ctx.lineWidth   = 1.6
      ctx.shadowBlur  = 8
      ctx.shadowColor = glow

      for (let i = 0; i < n; i++) {
        const x     = px + (i / (n - 1)) * pw
        const raw_y = cy - (data[i] / scale) * (ph / 2)
        const y     = Math.max(py, Math.min(py + ph, raw_y))
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
      }
      ctx.stroke()
      ctx.shadowBlur = 0

      // ── Label état cognitif (coin bas gauche) ────────────────────────────
      if (st && st !== 'neutral' && st !== 'invalid') {
        ctx.fillStyle = color + 'cc'
        ctx.font      = "bold 9px 'Space Mono', monospace"
        ctx.textAlign = 'left'
        ctx.fillText(st.toUpperCase(), px + 6, py + ph - 6)
      }

      ctx.restore()
    }

    draw()
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [])   // eslint-disable-line

  // ── Rendu ─────────────────────────────────────────────────────────────────
  return (
    <div className="relative w-full h-full flex flex-col">

      {/* Canvas */}
      <div className="relative flex-1">
        <canvas
          ref={canvasRef}
          width={1200}
          height={280}
          style={{ width: '100%', height: '100%', display: 'block', borderRadius: 8 }}
        />

        {/* Badge pipeline — signal filtré uniquement, pas de brut */}
        <div className="absolute top-2 right-3 flex items-center gap-1.5
                        px-2 py-0.5 rounded text-[9px] font-mono
                        bg-emerald-500/10 border border-emerald-500/30 text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          FILTRÉ
        </div>

        {/* Scale courante — coin haut gauche (dans la zone du canvas, après la marge) */}
        <div className="absolute top-2 left-14 text-[9px] font-mono text-nc-muted/50">
          ±{currentScale} µV
        </div>
      </div>

      {/* Légende pipeline (sous le canvas) */}
      <div className="flex items-center justify-between px-1 pt-0.5 pb-0.5"
           style={{ marginLeft: MARGIN_LEFT }}>
        <span className="text-[8px] font-mono text-nc-muted/40">{PIPELINE_LABEL}</span>

        {/* Légende états cognitifs */}
        <div className="flex gap-3">
          {Object.entries(STATE_COLOR).map(([s, c]) => (
            <span
              key={s}
              className="flex items-center gap-1 text-[8px] font-mono"
              style={{ color: cognitiveState === s ? c : '#2a3a4e' }}
            >
              <span style={{
                width: 5, height: 5, borderRadius: '50%',
                background: c, display: 'inline-block',
                opacity: cognitiveState === s ? 1 : 0.3,
              }} />
              {s}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Helpers de dessin ─────────────────────────────────────────────────────────

function _drawAxes(ctx, W, H, px, py, pw, ph, cy, scale) {
  const font = "9px 'Space Mono', monospace"
  ctx.font   = font

  ctx.strokeStyle = 'rgba(255,255,255,.10)'
  ctx.lineWidth   = 1
  ctx.strokeRect(px, py, pw, ph)

  Y_LEVELS.forEach(frac => {
    const y   = cy - frac * (ph / 2)
    const val = frac * scale

    ctx.strokeStyle = frac === 0 ? 'rgba(255,255,255,.10)' : 'rgba(255,255,255,.04)'
    ctx.lineWidth   = frac === 0 ? 1 : 0.7
    ctx.beginPath(); ctx.moveTo(px, y); ctx.lineTo(px + pw, y); ctx.stroke()

    ctx.strokeStyle = 'rgba(255,255,255,.18)'
    ctx.lineWidth   = 1
    ctx.beginPath(); ctx.moveTo(px - 4, y); ctx.lineTo(px, y); ctx.stroke()

    const label = frac === 0 ? '0' : `${fmtUv(val)}`
    ctx.fillStyle = frac === 0 ? 'rgba(255,255,255,.35)' : 'rgba(255,255,255,.22)'
    ctx.textAlign = 'right'
    ctx.fillText(label, px - 7, y + 3)
  })

  ctx.save()
  ctx.translate(11, py + ph / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.textAlign  = 'center'
  ctx.fillStyle  = 'rgba(255,255,255,.18)'
  ctx.font       = "8px 'Space Mono', monospace"
  ctx.fillText('µV', 0, 0)
  ctx.restore()

  ctx.strokeStyle = 'rgba(255,255,255,.12)'
  ctx.lineWidth   = 1
  ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px, py + ph); ctx.stroke()

  const nDiv = 4
  for (let g = 0; g <= nDiv; g++) {
    const x = px + g * (pw / nDiv)
    if (g > 0 && g < nDiv) {
      ctx.strokeStyle = 'rgba(255,255,255,.04)'
      ctx.lineWidth   = 0.7
      ctx.beginPath(); ctx.moveTo(x, py); ctx.lineTo(x, py + ph); ctx.stroke()
    }
    ctx.strokeStyle = 'rgba(255,255,255,.18)'
    ctx.lineWidth   = 1
    ctx.beginPath(); ctx.moveTo(x, py + ph); ctx.lineTo(x, py + ph + 4); ctx.stroke()
    ctx.fillStyle  = 'rgba(255,255,255,.22)'
    ctx.textAlign  = g === 0 ? 'left' : g === nDiv ? 'right' : 'center'
    ctx.font       = "8px 'Space Mono', monospace"
    ctx.fillText(`${g}s`, x, H - 4)
  }
  ctx.textAlign = 'left'
}

function _drawWaiting(ctx, px, py, pw, ph) {
  ctx.fillStyle = 'rgba(255,255,255,.15)'
  ctx.font      = "11px 'Space Mono', monospace"
  ctx.textAlign = 'center'
  ctx.fillText('En attente du signal…', px + pw / 2, py + ph / 2)
  ctx.textAlign = 'left'
}
