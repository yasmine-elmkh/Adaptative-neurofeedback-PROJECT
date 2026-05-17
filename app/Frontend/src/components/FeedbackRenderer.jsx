/**
 * NeuroCap – Feedback Renderers
 * Visual (color/particles), Sound (Web Audio), Game (ball control)
 */
import React, { useRef, useEffect, useMemo } from 'react'

// ── Visual Feedback ──────────────────────────────────────────
export function VisualFeedback({ concentration, intensity, isSuccess }) {
  const hue = concentration * 120 // 0=red → 120=green
  const glow = intensity * 40
  const scale = 0.6 + intensity * 0.4

  return (
    <div className="flex items-center justify-center h-full">
      <div className="relative">
        {/* Outer glow */}
        <div
          className="absolute inset-0 rounded-full blur-[60px] transition-all duration-500"
          style={{
            background: `hsl(${hue}, 80%, 50%)`,
            opacity: intensity * 0.4,
            transform: `scale(${1.2 + intensity * 0.3})`,
          }}
        />
        {/* Main orb */}
        <div
          className="w-48 h-48 rounded-full transition-all duration-300 flex items-center justify-center relative"
          style={{
            background: `radial-gradient(circle at 40% 35%, hsl(${hue}, 90%, 65%), hsl(${hue}, 70%, 35%))`,
            transform: `scale(${scale})`,
            boxShadow: `0 0 ${glow}px ${glow / 2}px hsl(${hue}, 80%, 50%, 0.4)`,
          }}
        >
          <span className="text-white text-4xl font-bold opacity-90">
            {(concentration * 100).toFixed(0)}
          </span>
        </div>
        {/* Success indicator */}
        {isSuccess && (
          <div className="absolute -bottom-6 left-1/2 -translate-x-1/2">
            <span className="text-xs font-bold text-neuro-success uppercase tracking-wider animate-pulse">
              ✓ Au-dessus du seuil
            </span>
          </div>
        )}
      </div>
    </div>
  )
}


// ── Sound Feedback ──────────────────────────────────────────
export function SoundFeedback({ concentration, intensity, isPaused }) {
  const audioCtxRef = useRef(null)
  const oscRef = useRef(null)
  const gainRef = useRef(null)

  useEffect(() => {
    if (isPaused) {
      if (gainRef.current) gainRef.current.gain.setValueAtTime(0, audioCtxRef.current.currentTime)
      return
    }

    if (!audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)()
      oscRef.current = audioCtxRef.current.createOscillator()
      gainRef.current = audioCtxRef.current.createGain()
      oscRef.current.type = 'sine'
      oscRef.current.connect(gainRef.current)
      gainRef.current.connect(audioCtxRef.current.destination)
      oscRef.current.start()
    }

    const freq = 200 + 400 * concentration
    const vol = Math.max(0, Math.min(0.15, intensity * 0.15))
    const ctx = audioCtxRef.current
    oscRef.current.frequency.setTargetAtTime(freq, ctx.currentTime, 0.05)
    gainRef.current.gain.setTargetAtTime(vol, ctx.currentTime, 0.05)

    return () => {}
  }, [concentration, intensity, isPaused])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (oscRef.current) { try { oscRef.current.stop() } catch {} }
      if (audioCtxRef.current) { try { audioCtxRef.current.close() } catch {} }
    }
  }, [])

  const freq = (200 + 400 * concentration).toFixed(0)
  const barCount = 20

  return (
    <div className="flex flex-col items-center justify-center h-full gap-6">
      {/* Frequency bars visualization */}
      <div className="flex items-end gap-1 h-32">
        {Array.from({ length: barCount }).map((_, i) => {
          const h = Math.max(8, (Math.sin(i * 0.5 + concentration * 10) * 0.5 + 0.5) * intensity * 100)
          return (
            <div
              key={i}
              className="w-3 rounded-t transition-all duration-200"
              style={{
                height: `${h}%`,
                background: `linear-gradient(to top, hsl(${180 + i * 4}, 80%, 50%), hsl(${180 + i * 4}, 60%, 70%))`,
                opacity: isPaused ? 0.2 : 0.8,
              }}
            />
          )
        })}
      </div>
      <div className="text-center">
        <p className="text-2xl font-mono text-neuro-accent">{freq} Hz</p>
        <p className="text-xs text-neuro-muted mt-1">
          {isPaused ? 'Son en pause' : 'Fréquence proportionnelle à la concentration'}
        </p>
      </div>
    </div>
  )
}


// ── Game Feedback ────────────────────────────────────────────
export function GameFeedback({ concentration, threshold }) {
  const canvasRef = useRef(null)
  const ballY = useRef(0.5)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const w = canvas.width
    const h = canvas.height

    // Smooth ball position
    const target = 1 - concentration // invert: top = high concentration
    ballY.current += (target - ballY.current) * 0.1

    // Clear
    ctx.clearRect(0, 0, w, h)

    // Background gradient
    const grad = ctx.createLinearGradient(0, 0, 0, h)
    grad.addColorStop(0, '#0d2818')
    grad.addColorStop(1, '#1a0505')
    ctx.fillStyle = grad
    ctx.fillRect(0, 0, w, h)

    // Threshold line
    const threshY = (1 - threshold) * h
    ctx.strokeStyle = '#f59e0b'
    ctx.lineWidth = 2
    ctx.setLineDash([8, 4])
    ctx.beginPath()
    ctx.moveTo(0, threshY)
    ctx.lineTo(w, threshY)
    ctx.stroke()
    ctx.setLineDash([])

    // Label
    ctx.fillStyle = '#f59e0b'
    ctx.font = '11px sans-serif'
    ctx.fillText('Seuil', 8, threshY - 6)

    // Ball
    const by = ballY.current * h
    const bx = w / 2
    const radius = 18
    const isAbove = by < threshY

    // Ball glow
    const glowGrad = ctx.createRadialGradient(bx, by, 0, bx, by, radius * 3)
    glowGrad.addColorStop(0, isAbove ? 'rgba(34,197,94,0.3)' : 'rgba(239,68,68,0.3)')
    glowGrad.addColorStop(1, 'transparent')
    ctx.fillStyle = glowGrad
    ctx.fillRect(bx - radius * 3, by - radius * 3, radius * 6, radius * 6)

    // Ball body
    const ballGrad = ctx.createRadialGradient(bx - 4, by - 4, 2, bx, by, radius)
    ballGrad.addColorStop(0, isAbove ? '#4ade80' : '#f87171')
    ballGrad.addColorStop(1, isAbove ? '#16a34a' : '#dc2626')
    ctx.fillStyle = ballGrad
    ctx.beginPath()
    ctx.arc(bx, by, radius, 0, Math.PI * 2)
    ctx.fill()

    // Score text
    ctx.fillStyle = '#e2e8f0'
    ctx.font = 'bold 14px sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(`${(concentration * 100).toFixed(0)}%`, bx, by + 5)

  }, [concentration, threshold])

  return (
    <div className="flex items-center justify-center h-full">
      <div className="relative">
        <canvas ref={canvasRef} width={200} height={350} className="rounded-2xl border border-neuro-border" />
        <p className="text-center text-xs text-neuro-muted mt-3">
          Gardez la balle au-dessus du seuil
        </p>
      </div>
    </div>
  )
}