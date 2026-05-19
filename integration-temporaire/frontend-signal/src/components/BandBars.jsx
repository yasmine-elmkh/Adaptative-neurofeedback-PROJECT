const BAND_CFG = [
  { key:'delta', label:'δ', color:'#818cf8', range:'0.5–4 Hz' },
  { key:'theta', label:'θ', color:'#f59e0b', range:'4–8 Hz' },
  { key:'alpha', label:'α', color:'#10b981', range:'8–13 Hz' },
  { key:'beta',  label:'β', color:'#3b82f6', range:'13–30 Hz' },
  { key:'gamma', label:'γ', color:'#ef4444', range:'30–40 Hz' },
]

export default function BandBars({ bands = {} }) {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
      {BAND_CFG.map(({ key, label, color, range }) => {
        const pct = Math.round((bands[key] ?? 0.2) * 100)
        return (
          <div key={key}>
            <div style={{ display:'flex', justifyContent:'space-between', marginBottom:3 }}>
              <span style={{ fontFamily:"'Space Mono',monospace", fontSize:10, color }}>
                {label} <span style={{ fontSize:8, color:'#3a4a5e' }}>{range}</span>
              </span>
              <span style={{ fontFamily:"'Space Mono',monospace", fontSize:10, color }}>
                {pct}%
              </span>
            </div>
            <div style={{ height:5, background:'rgba(255,255,255,.05)', borderRadius:3, overflow:'hidden' }}>
              <div style={{
                height:'100%', borderRadius:3,
                width:`${Math.min(pct, 100)}%`,
                background:`linear-gradient(90deg, ${color}88, ${color})`,
                boxShadow:`0 0 6px ${color}44`,
                transition:'width .3s ease',
              }} />
            </div>
          </div>
        )
      })}
    </div>
  )
}
