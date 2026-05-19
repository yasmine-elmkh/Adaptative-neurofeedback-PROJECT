/**
 * BatteryIndicator — jauge batterie 18650 (3.0–4.2V)
 * Conforme firmware v4.x : gBattV mesuré via diviseur 0.5×
 */
export default function BatteryIndicator({ voltage }) {
  const v    = voltage || 0
  const pct  = Math.max(0, Math.min(100, ((v - 3.0) / (4.2 - 3.0)) * 100))
  const color = pct > 50 ? '#00e5b0' : pct > 20 ? '#f5a623' : '#ff4d6d'

  return (
    <div style={{ display:'flex', alignItems:'center', gap:8 }}>
      {/* Icône batterie */}
      <div style={{ display:'flex', alignItems:'center', gap:3 }}>
        <div style={{
          width:28, height:13, borderRadius:3,
          border:`1px solid ${color}44`,
          padding:2, display:'flex', alignItems:'center',
          position:'relative',
        }}>
          <div style={{
            height:'100%', borderRadius:2,
            width:`${pct}%`,
            background: color,
            transition:'width .5s ease, background .5s ease',
            boxShadow:`0 0 4px ${color}66`,
          }} />
          {/* Borne positive */}
          <div style={{
            position:'absolute', right:-4, top:'50%', transform:'translateY(-50%)',
            width:3, height:6, borderRadius:'0 2px 2px 0',
            background:`${color}88`,
          }} />
        </div>
      </div>
      {/* Tension + % */}
      <div>
        <div style={{ fontFamily:"'Space Mono',monospace", fontSize:11, color, lineHeight:1 }}>
          {v > 0 ? `${v.toFixed(2)}V` : '—'}
        </div>
        <div style={{ fontSize:9, color:'#3a4a5e', lineHeight:1, marginTop:1 }}>
          {v > 0 ? `${Math.round(pct)}%` : 'N/A'}
        </div>
      </div>
    </div>
  )
}
