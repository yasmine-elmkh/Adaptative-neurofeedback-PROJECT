import BandBars from './BandBars.jsx'

const STATE_CFG = {
  focused:  { label:'Focus',      color:'#4da6ff', icon:'🎯' },
  stressed: { label:'Stress',     color:'#ff4d6d', icon:'⚡' },
  relaxed:  { label:'Relaxation', color:'#00e5b0', icon:'🌿' },
  neutral:  { label:'Neutre',     color:'#6a7a8e', icon:'◯'  },
}

function Metric({ label, value, color }) {
  return (
    <div style={{
      display:'flex', justifyContent:'space-between', alignItems:'center',
      padding:'6px 0', borderBottom:'1px solid rgba(255,255,255,.04)',
    }}>
      <span style={{ fontSize:11, color:'#4a5a6e' }}>{label}</span>
      <span style={{ fontFamily:"'Space Mono',monospace", fontSize:11, color: color || '#c9d8e8' }}>
        {value}
      </span>
    </div>
  )
}

export default function Sidebar({
  state, focus, stress, bands,
  electrodeOk, fp2Connected, m2Connected,
  calProgress, rawMetrics, pipeActive,
  epochCount, rejectedCount,
}) {
  const sc = STATE_CFG[state] || STATE_CFG.neutral
  const f3 = v => typeof v === 'number' ? v.toFixed(3) : '—'
  const f1 = v => typeof v === 'number' ? v.toFixed(1) : '—'

  return (
    <aside style={{
      width: 220, flexShrink: 0,
      background: '#0a0e18',
      borderRight: '1px solid rgba(255,255,255,.05)',
      display: 'flex', flexDirection: 'column',
      overflowY: 'auto', padding: '14px 14px',
      gap: 16,
    }}>

      {/* ── État mental ── */}
      <div style={{
        background:'#0e1420', border:'1px solid rgba(255,255,255,.06)',
        borderRadius:10, padding:'14px 12px', textAlign:'center',
      }}>
        <div style={{ fontSize:28, marginBottom:6 }}>{sc.icon}</div>
        <div style={{ fontFamily:"'Space Mono',monospace", fontSize:12, fontWeight:700, color:sc.color }}>
          {sc.label.toUpperCase()}
        </div>
        <div style={{ fontSize:9, color:'#3a4a5e', marginTop:3 }}>État mental estimé</div>
        {/* Barre d'activité */}
        <div style={{ marginTop:10, height:3, background:'rgba(255,255,255,.05)', borderRadius:2 }}>
          <div style={{
            height:'100%', borderRadius:2,
            width: pipeActive ? '100%' : '0%',
            background:`linear-gradient(90deg, ${sc.color}44, ${sc.color})`,
            transition:'width 1s ease',
          }} />
        </div>
      </div>

      {/* ── Électrodes ── */}
      <div style={{
        background:'#0e1420', border:'1px solid rgba(255,255,255,.06)',
        borderRadius:10, padding:'12px',
      }}>
        <div style={{ fontSize:9, color:'#3a4a5e', letterSpacing:1, textTransform:'uppercase', marginBottom:10 }}>
          Électrodes
        </div>
        {[
          { id:'Fp2', ok:fp2Connected, desc:'IN+ (Signal)' },
          { id:'M2',  ok:m2Connected,  desc:'IN− (Référ.)' },
          { id:'M1',  ok:true,         desc:'REF (Masse)'  },
        ].map(({ id, ok, desc }) => (
          <div key={id} style={{
            display:'flex', alignItems:'center', justifyContent:'space-between',
            padding:'5px 0', borderBottom:'1px solid rgba(255,255,255,.03)',
          }}>
            <div>
              <span style={{ fontFamily:"'Space Mono',monospace", fontSize:11, color:'#c9d8e8' }}>{id}</span>
              <span style={{ fontSize:9, color:'#3a4a5e', marginLeft:6 }}>{desc}</span>
            </div>
            <span style={{
              fontSize:9, padding:'2px 7px', borderRadius:4,
              background: ok ? 'rgba(0,229,176,.08)' : 'rgba(255,77,109,.08)',
              color:       ok ? '#00e5b0' : '#ff4d6d',
              border:`1px solid ${ok ? 'rgba(0,229,176,.2)' : 'rgba(255,77,109,.2)'}`,
            }}>
              {ok ? '✓ OK' : '✕ KO'}
            </span>
          </div>
        ))}
        {/* Calibration */}
        <div style={{ marginTop:10 }}>
          <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
            <span style={{ fontSize:10, color:'#4a5a6e' }}>Calibration</span>
            <span style={{ fontFamily:"'Space Mono',monospace", fontSize:10, color: calProgress >= 100 ? '#00e5b0' : '#f5a623' }}>
              {Math.round(calProgress)}%
            </span>
          </div>
          <div style={{ height:3, background:'rgba(255,255,255,.05)', borderRadius:2 }}>
            <div style={{
              height:'100%', borderRadius:2, width:`${calProgress}%`,
              background: calProgress >= 100 ? '#00e5b0' : '#f5a623',
              transition:'width .5s ease',
            }} />
          </div>
        </div>
      </div>

      {/* ── Bandes spectrales ── */}
      <div style={{
        background:'#0e1420', border:'1px solid rgba(255,255,255,.06)',
        borderRadius:10, padding:'12px',
      }}>
        <div style={{ fontSize:9, color:'#3a4a5e', letterSpacing:1, textTransform:'uppercase', marginBottom:10 }}>
          Bandes EEG
        </div>
        <BandBars bands={bands} />
      </div>

      {/* ── Métriques rapides ── */}
      <div style={{
        background:'#0e1420', border:'1px solid rgba(255,255,255,.06)',
        borderRadius:10, padding:'12px',
      }}>
        <div style={{ fontSize:9, color:'#3a4a5e', letterSpacing:1, textTransform:'uppercase', marginBottom:8 }}>
          Métriques
        </div>
        <Metric label="RMS brut"   value={`${f1(rawMetrics?.rms_raw)} µV`} />
        <Metric label="Peak"       value={`${f1(rawMetrics?.peak)} µV`}     warn={rawMetrics?.peak > 300} />
        <Metric label="Focus β/θ+α" value={f3(focus)}  color="#4da6ff" />
        <Metric label="Stress β/α"  value={f3(stress)} color={stress > 2 ? '#ff4d6d' : '#c9d8e8'} />
        <Metric label="Époques ✓"  value={epochCount}       color="#00e5b0" />
        <Metric label="Époques ✕"  value={rejectedCount}    color={rejectedCount > 5 ? '#f5a623' : '#4a5a6e'} />
      </div>

    </aside>
  )
}
