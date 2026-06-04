import { useState, useEffect } from 'react'

const TIMER_DURATION = 30

export default function FixationStep({ onComplete, onSkip }) {
  const [remaining, setRemaining] = useState(TIMER_DURATION)

  useEffect(() => {
    const interval = setInterval(() => {
      setRemaining(r => {
        if (r <= 1) {
          clearInterval(interval)
          onComplete?.()
          return 0
        }
        return r - 1
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [onComplete])

  return (
    <div className="fixed inset-0 z-50 bg-black flex flex-col items-center justify-center">
      {/* Timer — top left */}
      <div className="absolute top-6 left-6">
        <span className="text-white/25 font-mono text-sm tabular-nums">{remaining}s</span>
      </div>

      {/* Skip — top right */}
      <button
        onClick={onSkip}
        className="absolute top-6 right-6 px-4 py-2 rounded-xl text-sm font-medium
                   text-white/35 hover:text-white/65 border border-white/8 hover:bg-white/5
                   transition-all"
      >
        Passer →
      </button>

      {/* Concentric rings + fixation dot */}
      <div className="relative flex items-center justify-center">
        {[180, 120, 70].map((sz, i) => (
          <div
            key={i}
            className="absolute rounded-full border border-white/4"
            style={{ width: sz, height: sz }}
          />
        ))}
        <div
          className="w-2 h-2 rounded-full bg-white"
          style={{ boxShadow: '0 0 8px rgba(255,255,255,0.9), 0 0 24px rgba(255,255,255,0.25)' }}
        />
      </div>

      {/* Instruction — bottom */}
      <p className="absolute bottom-12 text-white/25 text-sm tracking-wide">
        Fixez le point central. Respirez normalement.
      </p>
    </div>
  )
}
