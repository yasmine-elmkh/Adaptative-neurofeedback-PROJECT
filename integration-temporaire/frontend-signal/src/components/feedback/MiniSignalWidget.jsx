/**
 * MiniSignalWidget — oscilloscope EEG miniature pour la sidebar feedback
 *
 * Latence cible < 50 ms :
 *  - WebSocket direct (new WebSocket), aucun useState pour les samples
 *  - Buffer Float32Array dans un useRef — écriture directe à 250 Hz
 *  - Boucle requestAnimationFrame indépendante de React
 *  - setLatencyMs toutes les 25 trames seulement pour minimiser les re-renders
 */

import { useRef, useEffect, useState } from 'react'

const BUF = 500   // 2 secondes @ 250 Hz

export default function MiniSignalWidget({ wsUrl = 'ws://localhost:8765/ws' }) {
  const canvasRef     = useRef(null)
  const bufRef        = useRef(new Float32Array(BUF))
  const headRef       = useRef(0)
  const countRef      = useRef(0)
  const wsRef         = useRef(null)
  const rafRef        = useRef(null)
  const lastMsgRef    = useRef(0)

  const [connected, setConnected] = useState(false)
  const [latencyMs, setLatencyMs] = useState(null)

  // ── WebSocket direct — bypass complet de React state pour les samples ──
  useEffect(() => {
    let reconnectTimer = null

    function connect() {
      try {
        const ws = new WebSocket(wsUrl)
        wsRef.current = ws

        ws.onopen  = () => setConnected(true)
        ws.onerror = () => ws.close()
        ws.onclose = () => {
          setConnected(false)
          reconnectTimer = setTimeout(connect, 3000)
        }

        ws.onmessage = (ev) => {
          try {
            const d = JSON.parse(ev.data)
            if (d.type !== 'eeg') return

            const now = performance.now()
            // Calcul latence inter-message (≈ 4 ms @ 250 Hz si en direct)
            if (lastMsgRef.current > 0 && countRef.current % 25 === 0) {
              setLatencyMs(Math.round(now - lastMsgRef.current))
            }
            lastMsgRef.current = now

            // Écriture directe dans le buffer — pas de setState
            const val = d.filtered ?? d.uv ?? 0
            bufRef.current[headRef.current % BUF] = val
            headRef.current++
            countRef.current = Math.min(countRef.current + 1, BUF)
          } catch (_) { /* JSON invalide, ignoré */ }
        }
      } catch (_) {
        reconnectTimer = setTimeout(connect, 3000)
      }
    }

    connect()
    return () => {
      clearTimeout(reconnectTimer)
      wsRef.current?.close()
    }
  }, [wsUrl])

  // ── Boucle RAF — rendu canvas sans re-render React ──
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    function draw() {
      rafRef.current = requestAnimationFrame(draw)
      const ctx = canvas.getContext('2d')
      const W = canvas.width, H = canvas.height

      ctx.fillStyle = 'rgba(43,42,74,0.07)'
      ctx.fillRect(0, 0, W, H)

      // Ligne centrale
      ctx.strokeStyle = 'rgba(184,123,158,0.15)'
      ctx.lineWidth = 1
      ctx.beginPath(); ctx.moveTo(0, H / 2); ctx.lineTo(W, H / 2); ctx.stroke()

      const n = countRef.current
      if (n < 2) {
        ctx.fillStyle = '#9A8BAE'
        ctx.font = '8px monospace'
        ctx.textAlign = 'center'
        ctx.fillText('En attente du signal…', W / 2, H / 2 + 3)
        ctx.textAlign = 'left'
        return
      }

      // Extraction dans l'ordre temporel
      const data = new Float32Array(n)
      const head = headRef.current
      for (let i = 0; i < n; i++) {
        data[i] = bufRef.current[(head - n + i + BUF) % BUF]
      }

      // Suppression DC par moyenne
      let sum = 0
      for (let i = 0; i < n; i++) sum += data[i]
      const mean = sum / n
      let ss = 0
      for (let i = 0; i < n; i++) { data[i] -= mean; ss += data[i] * data[i] }
      const rms = Math.sqrt(ss / n)
      const scale = rms > 0.1 ? Math.max(rms * 4, 5) : 50

      // Tracé signal — gradient vert→mauve du vrai projet
      const grad = ctx.createLinearGradient(0, 0, W, 0)
      grad.addColorStop(0,   '#7BC4A0')
      grad.addColorStop(0.5, '#B87B9E')
      grad.addColorStop(1,   '#7BA8C4')
      ctx.beginPath()
      ctx.strokeStyle = grad
      ctx.lineWidth   = 1.5
      ctx.shadowBlur  = 4
      ctx.shadowColor = '#B87B9E'

      for (let i = 0; i < n; i++) {
        const x = (i / (BUF - 1)) * W
        const y = H / 2 - (data[i] / scale) * (H / 2.2)
        i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
      }
      ctx.stroke()
      ctx.shadowBlur = 0

      ctx.fillStyle = 'rgba(43,42,74,0.4)'
      ctx.font = '7px monospace'
      ctx.fillText(`±${Math.round(scale)}µV`, 3, 10)
    }

    draw()
    return () => { if (rafRef.current) cancelAnimationFrame(rafRef.current) }
  }, [])

  const latOk = latencyMs !== null && latencyMs < 50

  return (
    <div style={{
      background: 'rgba(43,42,74,0.06)',
      borderRadius: 8,
      padding: '6px 8px',
      border: `1px solid ${connected ? 'rgba(123,196,160,0.35)' : 'rgba(232,123,158,0.2)'}`,
      marginBottom: 12,
    }}>
      {/* En-tête */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
        <span style={{ fontSize: 8, fontFamily: "'DM Mono',monospace", letterSpacing: 1, color: '#9A8BAE', textTransform: 'uppercase' }}>
          Signal EEG · LIVE
        </span>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          {latencyMs !== null && (
            <span style={{ fontSize: 8, fontFamily: "'DM Mono',monospace", color: latOk ? '#7BC4A0' : '#C4A87B' }}>
              ~{latencyMs}ms
            </span>
          )}
          <div style={{
            width: 6, height: 6, borderRadius: '50%',
            background: connected ? '#7BC4A0' : '#E87B9E',
            animation: connected ? 'miniSigPulse 1.5s ease-in-out infinite' : 'none',
          }} />
        </div>
      </div>

      {/* Canvas oscilloscope */}
      <canvas
        ref={canvasRef}
        width={400} height={56}
        style={{ width: '100%', height: 56, borderRadius: 6, display: 'block', background: 'rgba(255,255,255,0.25)', border: '1px solid rgba(255,255,255,0.3)' }}
      />

      {/* Légende */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 3, fontSize: 7, fontFamily: "'DM Mono',monospace", color: '#9A8BAE' }}>
        <span>2s · 250 Hz · Fp2</span>
        <span>{connected ? 'FILTRÉ · TEMPS RÉEL' : 'DÉCONNECTÉ'}</span>
      </div>

      <style>{`
        @keyframes miniSigPulse {
          0%,100% { opacity:1; transform:scale(1) }
          50%      { opacity:.5; transform:scale(.75) }
        }
      `}</style>
    </div>
  )
}
