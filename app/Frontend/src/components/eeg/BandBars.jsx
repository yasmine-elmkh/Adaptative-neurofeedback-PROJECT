const BANDS = [
  { key: 'delta',     label: 'δ Delta',     color: 'rgb(129,140,248)', range: '1–4 Hz'   },
  { key: 'theta',     label: 'θ Theta',     color: 'rgb(245,158,11)',  range: '6–8 Hz'   },
  { key: 'alpha',     label: 'α Alpha',     color: 'rgb(16,185,129)',  range: '8–13 Hz'  },
  { key: 'beta',      label: 'β Beta',      color: 'rgb(59,130,246)',  range: '13–30 Hz' },
  { key: 'beta_high', label: 'β↑ Beta Hi',  color: 'rgb(236,72,153)',  range: '20–30 Hz' },
  { key: 'gamma_low', label: 'γ Gamma',     color: 'rgb(239,68,68)',   range: '30–45 Hz' },
]

export default function BandBars({ bands = {}, compact = false }) {
  return (
    <div className="space-y-2">
      {BANDS.map(({ key, label, color, range }) => {
        const pct = Math.round((bands[key] ?? 0) * 100)
        return (
          <div key={key}>
            <div className="flex justify-between items-center mb-0.5">
              <span className="text-[10px] font-mono" style={{ color }}>
                {label}
                {!compact && (
                  <span className="text-nc-muted/50 ms-1 text-[8px]">{range}</span>
                )}
              </span>
              <span className="text-[10px] font-mono font-bold" style={{ color }}>
                {pct}%
              </span>
            </div>
            <div className="h-[5px] rounded-full overflow-hidden bg-white/5">
              <div
                className="h-full rounded-full transition-all duration-300"
                style={{
                  width:      `${Math.min(pct, 100)}%`,
                  background: `linear-gradient(90deg, ${color}55, ${color})`,
                  boxShadow:  `0 0 6px ${color}44`,
                }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
