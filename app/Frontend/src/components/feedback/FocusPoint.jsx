import { useEffect, useRef } from 'react'

export default function FocusPoint({ active = true }) {
  const dotRef = useRef(null)

  // Légère pulsation lente pour guider le regard sans distraire
  useEffect(() => {
    if (!active || !dotRef.current) return
    let t = 0
    const tick = () => {
      t += 0.02
      const scale = 1 + Math.sin(t) * 0.06
      if (dotRef.current) {
        dotRef.current.style.transform = `scale(${scale})`
      }
      animRef = requestAnimationFrame(tick)
    }
    let animRef = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(animRef)
  }, [active])

  if (!active) return null

  return (
    <div className="flex flex-col items-center gap-5 py-6"
         style={{ background: 'radial-gradient(ellipse at center, rgba(99,102,241,0.05) 0%, transparent 70%)' }}>

      {/* Point central */}
      <div className="relative flex items-center justify-center">
        {/* Anneaux concentriques légers */}
        {[80, 56, 36].map((sz, i) => (
          <div
            key={i}
            className="absolute rounded-full border border-indigo-400/10"
            style={{ width: sz, height: sz }}
          />
        ))}
        {/* Point principal */}
        <div
          ref={dotRef}
          className="w-5 h-5 rounded-full"
          style={{
            background: 'radial-gradient(circle, #818cf8, #4f46e5)',
            boxShadow: '0 0 20px rgba(99,102,241,0.5), 0 0 40px rgba(99,102,241,0.15)',
          }}
        />
      </div>

      {/* Instructions */}
      <div className="text-center space-y-1 max-w-xs">
        <p className="text-sm font-medium text-indigo-300">Fixez ce point</p>
        <p className="text-xs text-nc-muted leading-relaxed">
          Gardez votre regard sur le point central.<br />
          Laissez vos pensées s'apaiser naturellement.
        </p>
      </div>

      <p className="text-[10px] text-nc-muted/50 italic">
        Technique de focalisation attentionnelle
      </p>
    </div>
  )
}
