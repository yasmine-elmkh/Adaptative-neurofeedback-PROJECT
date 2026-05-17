/**
 * NeuroCap – TopoMap2D Component
 * Canvas 2D topographic heatmap with IDW (Inverse Distance Weighting).
 * Simulated 10-20 electrode positions for single-channel display.
 */
import React, { useRef, useEffect, useMemo } from 'react'

// 10-20 electrode positions (normalized 0-1, centered at 0.5)
const ELECTRODES = [
  { name: 'Fp1', x: 0.35, y: 0.15 },
  { name: 'Fp2', x: 0.65, y: 0.15 },
  { name: 'F7',  x: 0.15, y: 0.30 },
  { name: 'F3',  x: 0.35, y: 0.30 },
  { name: 'Fz',  x: 0.50, y: 0.28 },
  { name: 'F4',  x: 0.65, y: 0.30 },
  { name: 'F8',  x: 0.85, y: 0.30 },
  { name: 'T3',  x: 0.10, y: 0.50 },
  { name: 'C3',  x: 0.30, y: 0.50 },
  { name: 'Cz',  x: 0.50, y: 0.50 },
  { name: 'C4',  x: 0.70, y: 0.50 },
  { name: 'T4',  x: 0.90, y: 0.50 },
  { name: 'P3',  x: 0.35, y: 0.70 },
  { name: 'Pz',  x: 0.50, y: 0.72 },
  { name: 'P4',  x: 0.65, y: 0.70 },
  { name: 'O1',  x: 0.40, y: 0.88 },
  { name: 'O2',  x: 0.60, y: 0.88 },
]

// Color interpolation: blue → green → yellow → red
function valueToColor(v) {
  v = Math.max(0, Math.min(1, v))
  let r, g, b
  if (v < 0.25) {
    const t = v / 0.25
    r = 0; g = Math.floor(t * 100); b = Math.floor(150 + t * 105)
  } else if (v < 0.5) {
    const t = (v - 0.25) / 0.25
    r = 0; g = Math.floor(100 + t * 155); b = Math.floor(255 - t * 155)
  } else if (v < 0.75) {
    const t = (v - 0.5) / 0.25
    r = Math.floor(t * 255); g = 255; b = 0
  } else {
    const t = (v - 0.75) / 0.25
    r = 255; g = Math.floor(255 - t * 200); b = 0
  }
  return [r, g, b]
}

export default function TopoMap2D({
  concentration = 0.5,
  features = {},
  size = 220,
}) {
  const canvasRef = useRef(null)

  // Generate simulated electrode values based on concentration + features
  const electrodeValues = useMemo(() => {
    const alpha = features.alpha ?? concentration * 15
    const tbr = features.theta_beta_ratio ?? 1.0

    return ELECTRODES.map((e) => {
      // Higher activation in frontal regions when concentrated
      const frontalBias = e.y < 0.4 ? concentration * 0.3 : 0
      // Spread from Fz
      const distFromFz = Math.sqrt((e.x - 0.5) ** 2 + (e.y - 0.28) ** 2)
      const fzSpread = Math.max(0, 1 - distFromFz * 2) * concentration * 0.4

      const baseVal = 0.2 + Math.random() * 0.1
      return {
        ...e,
        value: Math.min(1, baseVal + frontalBias + fzSpread),
      }
    })
  }, [concentration, features.alpha, features.theta_beta_ratio])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const w = canvas.width
    const h = canvas.height
    const cx = w / 2
    const cy = h / 2
    const radius = w * 0.42

    // Clear
    ctx.clearRect(0, 0, w, h)

    // Create head-shaped clipping path
    ctx.save()
    ctx.beginPath()
    ctx.arc(cx, cy, radius, 0, Math.PI * 2)
    ctx.clip()

    // IDW interpolation for each pixel
    const imageData = ctx.createImageData(w, h)
    const data = imageData.data
    const power = 2.5 // IDW exponent

    for (let py = 0; py < h; py++) {
      for (let px = 0; px < w; px++) {
        // Check if inside head circle
        const dx = px - cx
        const dy = py - cy
        if (dx * dx + dy * dy > radius * radius) continue

        // Normalized position
        const nx = px / w
        const ny = py / h

        let sumWeights = 0
        let sumValues = 0

        for (const el of electrodeValues) {
          const d = Math.sqrt((nx - el.x) ** 2 + (ny - el.y) ** 2)
          const weight = d < 0.001 ? 1e6 : 1 / Math.pow(d, power)
          sumWeights += weight
          sumValues += weight * el.value
        }

        const v = sumValues / sumWeights
        const [r, g, b] = valueToColor(v)
        const idx = (py * w + px) * 4
        data[idx] = r
        data[idx + 1] = g
        data[idx + 2] = b
        data[idx + 3] = 180 // semi-transparent
      }
    }

    ctx.putImageData(imageData, 0, 0)
    ctx.restore()

    // Draw head outline
    ctx.strokeStyle = '#2a3654'
    ctx.lineWidth = 2
    ctx.beginPath()
    ctx.arc(cx, cy, radius, 0, Math.PI * 2)
    ctx.stroke()

    // Draw nose indicator
    ctx.beginPath()
    ctx.moveTo(cx - 10, cy - radius + 2)
    ctx.lineTo(cx, cy - radius - 12)
    ctx.lineTo(cx + 10, cy - radius + 2)
    ctx.strokeStyle = '#64748b'
    ctx.lineWidth = 1.5
    ctx.stroke()

    // Draw electrode positions
    for (const el of electrodeValues) {
      const ex = el.x * w
      const ey = el.y * h
      const edx = ex - cx
      const edy = ey - cy
      if (edx * edx + edy * edy > radius * radius) continue

      // Dot
      ctx.beginPath()
      ctx.arc(ex, ey, 3, 0, Math.PI * 2)
      ctx.fillStyle = '#e2e8f0'
      ctx.fill()
      ctx.strokeStyle = '#0a0e1a'
      ctx.lineWidth = 1
      ctx.stroke()

      // Label
      ctx.fillStyle = '#94a3b8'
      ctx.font = '8px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText(el.name, ex, ey - 7)
    }

    // Draw ears
    ctx.strokeStyle = '#2a3654'
    ctx.lineWidth = 1.5
    // Left ear
    ctx.beginPath()
    ctx.ellipse(cx - radius - 5, cy, 5, 12, 0, -Math.PI * 0.4, Math.PI * 0.4)
    ctx.stroke()
    // Right ear
    ctx.beginPath()
    ctx.ellipse(cx + radius + 5, cy, 5, 12, 0, Math.PI * 0.6, Math.PI * 1.4)
    ctx.stroke()

  }, [electrodeValues])

  return (
    <div className="flex flex-col items-center gap-2">
      <canvas
        ref={canvasRef}
        width={size}
        height={size}
        className="rounded-full"
      />
      {/* Color legend */}
      <div className="flex items-center gap-2 text-[10px] text-neuro-muted">
        <span>Faible</span>
        <div className="w-24 h-2 rounded-full" style={{
          background: 'linear-gradient(to right, #0066ff, #00ff66, #ffff00, #ff3300)'
        }} />
        <span>Élevé</span>
      </div>
    </div>
  )
}