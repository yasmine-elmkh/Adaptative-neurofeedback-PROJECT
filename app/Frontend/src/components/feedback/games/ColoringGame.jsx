import { useState } from 'react'

const PALETTE = [
  '#818cf8', // indigo
  '#34d399', // emerald
  '#f87171', // red
  '#fbbf24', // amber
  '#60a5fa', // blue
  '#a78bfa', // violet
  '#f472b6', // pink
  '#2dd4bf', // teal
]

const BG = '#0f0e1a'

// 8 pétales intermédiaires (r=22) + 8 pétales extérieurs (r=14) + centre
function buildZones() {
  const zones = []
  for (let i = 0; i < 8; i++) {
    const angle = (i * 45 * Math.PI) / 180
    zones.push({
      id: `mid-${i}`,
      cx: 100 + 44 * Math.cos(angle),
      cy: 100 + 44 * Math.sin(angle),
      r: 20,
    })
  }
  for (let i = 0; i < 8; i++) {
    const angle = ((i * 45 + 22.5) * Math.PI) / 180
    zones.push({
      id: `out-${i}`,
      cx: 100 + 76 * Math.cos(angle),
      cy: 100 + 76 * Math.sin(angle),
      r: 13,
    })
  }
  return zones
}

const ZONES = buildZones()

export default function ColoringGame() {
  const [colors,        setColors]        = useState({})
  const [selectedColor, setSelectedColor] = useState(PALETTE[0])

  const fill = (id) => setColors(c => ({ ...c, [id]: selectedColor }))
  const reset = () => setColors({})

  return (
    <div className="flex flex-col items-center gap-5 py-4">
      <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide">Coloriage Mandala</p>

      {/* SVG mandala */}
      <svg width={210} height={210} viewBox="0 0 200 200" className="drop-shadow-lg">
        {/* Fond */}
        <circle cx={100} cy={100} r={98} fill={BG} stroke="#818cf8" strokeWidth={0.5} opacity={0.4} />

        {/* Zones colorables extérieures */}
        {ZONES.filter(z => z.id.startsWith('out')).map(z => (
          <circle
            key={z.id}
            cx={z.cx} cy={z.cy} r={z.r}
            fill={colors[z.id] ?? BG}
            stroke="#818cf8" strokeWidth={0.8} opacity={0.85}
            className="cursor-pointer transition-opacity hover:opacity-70"
            onClick={() => fill(z.id)}
          />
        ))}

        {/* Zones colorables intermédiaires */}
        {ZONES.filter(z => z.id.startsWith('mid')).map(z => (
          <circle
            key={z.id}
            cx={z.cx} cy={z.cy} r={z.r}
            fill={colors[z.id] ?? BG}
            stroke="#818cf8" strokeWidth={0.8}
            className="cursor-pointer transition-opacity hover:opacity-70"
            onClick={() => fill(z.id)}
          />
        ))}

        {/* Centre */}
        <circle
          cx={100} cy={100} r={18}
          fill={colors['center'] ?? BG}
          stroke="#818cf8" strokeWidth={1}
          className="cursor-pointer transition-opacity hover:opacity-70"
          onClick={() => fill('center')}
        />

        {/* Point centre décoratif */}
        <circle cx={100} cy={100} r={4} fill="#818cf8" opacity={0.6} style={{ pointerEvents: 'none' }} />
      </svg>

      {/* Palette couleurs */}
      <div className="flex gap-2 flex-wrap justify-center">
        {PALETTE.map(color => (
          <button
            key={color}
            title={color}
            onClick={() => setSelectedColor(color)}
            className="w-7 h-7 rounded-full border-2 transition-transform hover:scale-110 focus:outline-none"
            style={{
              background: color,
              borderColor: selectedColor === color ? '#fff' : 'transparent',
              transform:   selectedColor === color ? 'scale(1.15)' : undefined,
            }}
          />
        ))}
        {/* Gomme */}
        <button
          title="Effacer"
          onClick={() => setSelectedColor(BG)}
          className={`w-7 h-7 rounded-full border-2 flex items-center justify-center text-[10px] font-bold
                      bg-nc-surface2 hover:scale-110 transition-transform focus:outline-none
                      ${selectedColor === BG ? 'border-white' : 'border-nc-border'}`}
        >
          ✕
        </button>
      </div>

      <div className="flex items-center gap-4">
        <p className="text-xs text-nc-muted">Clic sur une zone pour colorier</p>
        <button
          onClick={reset}
          className="text-xs text-nc-muted hover:text-nc-text underline"
        >
          Effacer tout
        </button>
      </div>
    </div>
  )
}
