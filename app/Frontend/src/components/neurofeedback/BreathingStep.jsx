import { useState, useEffect, useRef } from 'react'

// Box Breathing: 4s inspire / 4s hold / 6s expire = 14s cycle
const INSPIRE  = 4
const HOLD     = 4
const EXPIRE   = 6
const CYCLE    = INSPIRE + HOLD + EXPIRE   // 14s
const MIN_CYCLES = 3

export default function BreathingStep({ onComplete, onSkip }) {
  const [phase,    setPhase]    = useState('inspire')
  const [progress, setProgress] = useState(0)   // 0‒1 within current phase
  const [cycles,   setCycles]   = useState(0)
  const startRef  = useRef(Date.now())
  const rafRef    = useRef(null)
  const lastCycle = useRef(-1)

  useEffect(() => {
    startRef.current = Date.now()
    lastCycle.current = -1

    const tick = () => {
      const elapsed     = (Date.now() - startRef.current) / 1000
      const cycleNum    = Math.floor(elapsed / CYCLE)
      const posInCycle  = elapsed % CYCLE

      if (cycleNum !== lastCycle.current) {
        lastCycle.current = cycleNum
        setCycles(cycleNum)
      }

      if (posInCycle < INSPIRE) {
        setPhase('inspire')
        setProgress(posInCycle / INSPIRE)
      } else if (posInCycle < INSPIRE + HOLD) {
        setPhase('hold')
        setProgress((posInCycle - INSPIRE) / HOLD)
      } else {
        setPhase('expire')
        setProgress((posInCycle - INSPIRE - HOLD) / EXPIRE)
      }

      rafRef.current = requestAnimationFrame(tick)
    }

    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [])

  const canAdvance = cycles >= MIN_CYCLES

  // Circle radius: grows on inspire / stays at max during hold / shrinks on expire
  const circleSize = (() => {
    if (phase === 'inspire') return 80 + progress * 80    // 80 → 160
    if (phase === 'hold')    return 160
    return 160 - progress * 80                            // 160 → 80
  })()

  const PHASE_GRADIENT = {
    inspire: 'radial-gradient(circle, rgba(96,165,250,0.65), rgba(99,102,241,0.3))',
    hold:    'radial-gradient(circle, rgba(167,139,250,0.75), rgba(99,102,241,0.4))',
    expire:  'radial-gradient(circle, rgba(96,165,250,0.3),  rgba(99,102,241,0.12))',
  }[phase]

  const PHASE_LABEL = {
    inspire: 'Inspirez…',
    hold:    'Retenez…',
    expire:  'Expirez…',
  }[phase]

  const PHASE_SECONDS = { inspire: INSPIRE, hold: HOLD, expire: EXPIRE }[phase]

  return (
    <div className="fixed inset-0 z-50 bg-slate-900 flex flex-col items-center justify-center gap-10">

      {/* Cycle dots — top left */}
      <div className="absolute top-6 left-6 flex items-center gap-2">
        {Array.from({ length: MIN_CYCLES }).map((_, i) => (
          <div
            key={i}
            className={`w-2 h-2 rounded-full transition-all duration-500
              ${i < cycles ? 'bg-blue-400' : 'bg-white/12'}`}
          />
        ))}
        <span className="text-white/30 text-xs ml-1">
          {Math.min(cycles, MIN_CYCLES)}/{MIN_CYCLES} cycles
        </span>
      </div>

      {/* Skip — top right */}
      <button
        onClick={onSkip}
        className="absolute top-6 right-6 px-4 py-2 rounded-xl text-sm font-medium
                   text-white/35 hover:text-white/65 border border-white/8 hover:bg-white/5 transition-all"
      >
        Passer cette étape
      </button>

      {/* Breathing circle */}
      <div className="relative flex items-center justify-center" style={{ width: 220, height: 220 }}>
        {[200, 170, 140].map((sz, i) => (
          <div
            key={i}
            className="absolute rounded-full border border-blue-400/8"
            style={{ width: sz, height: sz }}
          />
        ))}
        <div
          className="rounded-full"
          style={{
            width:      circleSize,
            height:     circleSize,
            background: PHASE_GRADIENT,
            boxShadow:  `0 0 ${24 + circleSize * 0.15}px rgba(99,102,241,${0.15 + progress * 0.15})`,
            transition: 'width 100ms linear, height 100ms linear',
          }}
        />
      </div>

      {/* Phase text */}
      <div className="text-center space-y-1.5">
        <p className="text-2xl font-semibold text-blue-300 tracking-wide">{PHASE_LABEL}</p>
        <p className="text-sm text-white/25">{PHASE_SECONDS}s</p>
      </div>

      {/* Progress bar for current phase */}
      <div className="w-48 h-1 rounded-full bg-white/8 overflow-hidden">
        <div
          className="h-full rounded-full bg-blue-400"
          style={{ width: `${progress * 100}%`, transition: 'width 100ms linear' }}
        />
      </div>

      {/* Advance / waiting */}
      {canAdvance ? (
        <button
          onClick={onComplete}
          className="px-8 py-3 rounded-2xl text-sm font-semibold
                     bg-blue-500/18 border border-blue-400/30 text-blue-300
                     hover:bg-blue-500/28 transition-all"
        >
          Continuer →
        </button>
      ) : (
        <p className="text-white/18 text-xs">
          {MIN_CYCLES - cycles} cycle{MIN_CYCLES - cycles > 1 ? 's' : ''} restant{MIN_CYCLES - cycles > 1 ? 's' : ''}
        </p>
      )}
    </div>
  )
}
