/**
 * EpochHistory — historique scrollable des 60 dernières époques.
 * Acceptée = vert, Rejetée = rouge avec reason.
 * Bouton Replay pour revenir dans FeaturesPanel.
 */

const REASONS = {
  electrode_off: 'Électrode déconnectée',
  flat_line:     'Signal plat (circuit ouvert ?)',
  extreme_peak:  'Pic extrême (saturation)',
  eyeblink:      'Clignement oculaire (Fp2)',
  high_rms:      'Amplitude trop élevée',
  emg:           'Artefact musculaire (EMG)',
  too_short:     'Buffer trop court',
  emg_broadband: 'Bruit large bande',
}

function fmt(ts) {
  try { return new Date(ts).toLocaleTimeString('fr-FR') } catch { return '—' }
}

export default function EpochHistory({ epochs, onReplay }) {
  if (epochs.length === 0) return (
    <div style={{
      background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)',
      borderRadius:14, padding:'48px 24px', textAlign:'center',
      color:'#3a4a5e', fontSize:13, lineHeight:1.9,
    }}>
      <div style={{ fontSize:32, marginBottom:12 }}>📊</div>
      Aucune époque enregistrée.<br/>
      <span style={{ fontSize:11 }}>Signal actif + électrodes connectées = 4s minimum</span>
    </div>
  )

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:8, animation:'fadeIn .3s ease' }}>
      <div style={{ fontFamily:"'Space Mono',monospace", fontSize:10, color:'#3a4a5e',
                    marginBottom:4 }}>
        {epochs.length} époque(s) · Fenêtre 4s · Overlap 75%
      </div>
      {[...epochs].reverse().map((ep, i) => (
        <div key={i} style={{
          display:'flex', alignItems:'center', justifyContent:'space-between',
          background:'#0a0e18',
          border:`1px solid ${ep.rejected ? 'rgba(255,77,109,.12)' : 'rgba(0,229,176,.1)'}`,
          borderRadius:10, padding:'10px 14px',
          animation:'fadeIn .2s ease',
        }}>
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>
            {/* Badge #idx */}
            <div style={{
              fontFamily:"'Space Mono',monospace", fontSize:10, fontWeight:700,
              color: ep.rejected ? '#ff4d6d' : '#00e5b0',
              minWidth:36,
            }}>
              #{ep.idx}
            </div>
            {/* Heure */}
            <div style={{ fontSize:11, color:'#4a5a6e', minWidth:65 }}>{fmt(ep.timestamp)}</div>
            {/* Statut */}
            {ep.rejected ? (
              <div style={{ fontSize:11, color:'#ff4d6d' }}>
                ✕ {REASONS[ep.reason] || ep.reason}
              </div>
            ) : (
              <div style={{ display:'flex', gap:10, fontSize:11, color:'#6a7a8e' }}>
                <span>Eng. <span style={{color:'#4da6ff'}}>{ep.features?.engagement?.toFixed(3) ?? '—'}</span></span>
                <span>α <span style={{color:'#10b981'}}>{ep.features?.rel_alpha?.toFixed(3) ?? '—'}</span></span>
                <span>β <span style={{color:'#3b82f6'}}>{ep.features?.rel_beta?.toFixed(3) ?? '—'}</span></span>
              </div>
            )}
          </div>
          {/* Bouton Replay */}
          {!ep.rejected && (
            <button onClick={() => onReplay?.(ep)} style={{
              padding:'3px 12px', borderRadius:5,
              background:'rgba(77,166,255,.08)', border:'1px solid rgba(77,166,255,.2)',
              color:'#4da6ff', fontSize:10, cursor:'pointer',
              fontFamily:"'Space Mono',monospace",
            }}>
              REPLAY
            </button>
          )}
        </div>
      ))}
    </div>
  )
}
