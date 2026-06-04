import { useState, useEffect, useRef } from 'react'

const CYCLE = 8  // secondes totales (4 inspire + 4 expire)

export default function BreathingGuide({ active = true }) {
  const [phase,    setPhase]    = useState('inspire')   // 'inspire' | 'expire'
  const [progress, setProgress] = useState(0)           // 0–1 dans la demi-phase
  const startRef = useRef(Date.now())
  const rafRef   = useRef(null)

  useEffect(() => {
    if (!active) return
    startRef.current = Date.now()

    const tick = () => {
      const elapsed = (Date.now() - startRef.current) / 1000
      const posInCycle = elapsed % CYCLE
      if (posInCycle < CYCLE / 2) {
        setPhase('inspire')
        setProgress(posInCycle / (CYCLE / 2))
      } else {
        setPhase('expire')
        setProgress((posInCycle - CYCLE / 2) / (CYCLE / 2))
      }
      rafRef.current = requestAnimationFrame(tick)
    }

    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [active])

  if (!active) return null

  // Taille du cercle : expand lors de l'inspiration
  const size = phase === 'inspire'
    ? 60 + progress * 40   // 60px → 100px
    : 100 - progress * 40  // 100px → 60px

  return (
    <div className="flex flex-col items-center gap-4 py-4">
      {/* Cercle pulsant SVG */}
      <div className="relative flex items-center justify-center" style={{ width: 120, height: 120 }}>
        {/* Anneaux de fond */}
        {[1, 0.6, 0.3].map((op, i) => (
          <div
            key={i}
            className="absolute rounded-full border border-blue-400/30"
            style={{ width: 80 + i * 20, height: 80 + i * 20, opacity: op * 0.4 }}
          />
        ))}
        {/* Cercle principal */}
        <div
          className="rounded-full transition-none flex items-center justify-center"
          style={{
            width: size,
            height: size,
            background: phase === 'inspire'
              ? 'radial-gradient(circle, rgba(59,130,246,0.6), rgba(99,102,241,0.3))'
              : 'radial-gradient(circle, rgba(99,102,241,0.4), rgba(59,130,246,0.15))',
            boxShadow: `0 0 ${20 + size * 0.3}px rgba(99,102,241,${0.3 + progress * 0.2})`,
            transition: 'width 100ms linear, height 100ms linear',
          }}
        >
          <span className="text-white text-[10px] font-semibold opacity-70">
            {phase === 'inspire' ? '▲' : '▼'}
          </span>
        </div>
      </div>

      {/* Texte synchronisé */}
      <div className="text-center">
        <p className="text-base font-semibold text-blue-300">
          {phase === 'inspire' ? 'Inspirez…' : 'Expirez…'}
        </p>
        <p className="text-xs text-nc-muted mt-1">4 secondes</p>
      </div>

      {/* Barre de progression */}
      <div className="w-32 h-1 rounded-full bg-nc-surface2 overflow-hidden">
        <div
          className="h-full rounded-full bg-blue-400 transition-none"
          style={{ width: `${progress * 100}%`, transition: 'width 100ms linear' }}
        />
      </div>

      <p className="text-[10px] text-nc-muted opacity-60">
        Respirez lentement et régulièrement
      </p>
    </div>
  )
}
