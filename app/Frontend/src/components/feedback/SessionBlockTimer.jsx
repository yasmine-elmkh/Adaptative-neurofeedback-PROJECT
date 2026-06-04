import { useEffect, useRef, useState } from 'react'

export default function SessionBlockTimer({
  blockIndex,          // 0-based (0 = bloc 1)
  totalBlocks = 6,
  blockDurationSec = 180,
  onBlockEnd,          // () => void appelé quand le bloc est fini
  paused = false,
}) {
  const [remaining, setRemaining] = useState(blockDurationSec)
  const intervalRef = useRef(null)

  // Reset quand le bloc change
  useEffect(() => {
    setRemaining(blockDurationSec)
  }, [blockIndex, blockDurationSec])

  useEffect(() => {
    if (paused) {
      clearInterval(intervalRef.current)
      return
    }
    intervalRef.current = setInterval(() => {
      setRemaining(r => {
        if (r <= 1) {
          clearInterval(intervalRef.current)
          onBlockEnd?.()
          return 0
        }
        return r - 1
      })
    }, 1000)
    return () => clearInterval(intervalRef.current)
  }, [blockIndex, paused, onBlockEnd])

  const progress = (blockDurationSec - remaining) / blockDurationSec
  const mm = String(Math.floor(remaining / 60)).padStart(2, '0')
  const ss = String(remaining % 60).padStart(2, '0')

  return (
    <div className="flex items-center gap-3">
      {/* Bloc actuel */}
      <div className="flex items-center gap-1.5">
        {Array.from({ length: totalBlocks }).map((_, i) => (
          <div
            key={i}
            className={`h-2 rounded-full transition-all ${
              i < blockIndex   ? 'w-4 bg-emerald-500' :
              i === blockIndex ? 'w-6 bg-nc-accent animate-pulse' :
                                 'w-4 bg-nc-surface2'
            }`}
          />
        ))}
      </div>

      {/* Timer */}
      <span className="text-sm font-mono font-bold text-nc-text">
        Bloc {blockIndex + 1}/{totalBlocks} — {mm}:{ss}
      </span>

      {/* Barre progression */}
      <div className="flex-1 h-1.5 rounded-full bg-nc-surface2 overflow-hidden">
        <div
          className="h-full rounded-full bg-nc-accent transition-all duration-1000"
          style={{ width: `${progress * 100}%` }}
        />
      </div>
    </div>
  )
}
