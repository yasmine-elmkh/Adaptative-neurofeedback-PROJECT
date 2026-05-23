/**
 * FeedbackReport.jsx — ÉCRAN 3 : Rapport de séance neurofeedback
 * Résumé : durée, efficacité, delta EEG, historique, rapport IA
 */

// ── Palette Bleu Mauve ────────────────────────────────────────────────────────
const C = {
  bg: '#C5D3E8', card: 'rgba(247,243,250,0.45)',
  border: 'rgba(255,255,255,0.4)', border2: 'rgba(255,255,255,0.6)',
  text: '#2B2A4A', muted: '#9A8BAE', sub: '#2B2A4A',
  conc: '#7BC4A0', stress: '#E87B9E', uncert: '#C4A87B', purple: '#B87B9E',
  shadow: 'rgba(180,169,196,0.45)',
}

const MEDIA_ICON = { audio: '🎵', image: '🖼️', video: '🎬', game: '🎮' }

function StatCard({ label, value, color, sub }) {
  return (
    <div style={{
      background: C.card, border: `1px solid ${C.border2}`,
      borderRadius: 14, padding: '16px 18px', textAlign: 'center',
      backdropFilter: 'blur(10px)', boxShadow: `0 4px 14px ${C.shadow}`,
    }}>
      <div style={{ fontSize: 9, color: C.muted, letterSpacing: 2, marginBottom: 6, fontFamily: "'DM Mono',monospace", textTransform: 'uppercase' }}>
        {label}
      </div>
      <div style={{ fontSize: 24, fontWeight: 700, color: color ?? C.text, fontFamily: "'DM Mono',monospace" }}>{value}</div>
      {sub && <div style={{ fontSize: 9, color: C.muted, marginTop: 4 }}>{sub}</div>}
    </div>
  )
}

function DeltaBar({ label, value, targetGood }) {
  const good   = targetGood ? value > 0.05 : value < -0.05
  const neutral = Math.abs(value) < 0.01
  const color  = good ? C.conc : neutral ? C.muted : C.uncert
  const pct    = Math.min(Math.abs(value) * 600, 100)
  const sign   = value > 0 ? '+' : ''

  return (
    <div style={{ marginBottom: 14 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
        <span style={{ fontSize: 12, color: C.sub }}>{label}</span>
        <span style={{ fontSize: 12, fontFamily: "'Space Mono',monospace", fontWeight: 700, color }}>
          {sign}{value?.toFixed(4) ?? '0.0000'} {good ? '↑' : neutral ? '→' : '↓'}
        </span>
      </div>
      <div style={{ height: 6, background: 'rgba(255,255,255,.05)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: 3, transition: 'width .7s' }} />
      </div>
    </div>
  )
}

function HistoryItem({ item, idx }) {
  const icon  = MEDIA_ICON[item.type] ?? '◎'
  const da    = item.delta_alpha ?? 0
  const db    = item.delta_beta  ?? 0
  const statusColor = item.skipped ? C.muted : item.liked === true ? C.conc : item.liked === false ? C.stress : '#2a3a4e'
  const statusLabel = item.skipped ? '⏭ Ignoré' : item.liked === true ? '✓ Efficace' : item.liked === false ? '✗ Non adapté' : item.ended ? '■ Fin' : '—'

  return (
    <tr style={{ borderBottom: `1px solid rgba(255,255,255,.03)` }}>
      <td style={td}><span style={{ color: C.muted }}>{idx + 1}</span></td>
      <td style={td}>
        <span style={{ fontSize: 15 }}>{icon}</span>
        <span style={{ fontSize: 10, color: C.muted, marginLeft: 5, textTransform: 'capitalize' }}>{item.type}</span>
      </td>
      <td style={{ ...td, maxWidth: 160 }}>
        <span style={{ fontSize: 10, fontFamily: "'Space Mono',monospace", color: C.sub, display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {item.filename ? item.filename.replace(/^.*[\\/]/, '').slice(0, 24) : '—'}
        </span>
      </td>
      <td style={td}>
        <span style={{ fontSize: 10, fontFamily: "'Space Mono',monospace", color: da > 0.05 ? C.conc : C.muted }}>
          {da > 0 ? '+' : ''}{da.toFixed(3)}
        </span>
      </td>
      <td style={td}>
        <span style={{ fontSize: 10, fontFamily: "'Space Mono',monospace", color: db < -0.05 ? C.conc : C.muted }}>
          {db > 0 ? '+' : ''}{db.toFixed(3)}
        </span>
      </td>
      <td style={td}>
        <span style={{ fontSize: 10, fontWeight: 700, color: statusColor }}>{statusLabel}</span>
      </td>
    </tr>
  )
}

const td = { padding: '7px 10px', verticalAlign: 'middle', color: C.sub }

export default function FeedbackReport({ report, onClose, onNewSession }) {
  if (!report) {
    return (
      <div style={{ minHeight: '100vh', background: C.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'DM Sans', system-ui" }}>
        <div style={{ textAlign: 'center', color: C.muted }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>⚠</div>
          <div style={{ fontSize: 14 }}>Rapport non disponible</div>
          <button onClick={onClose} style={{ marginTop: 16, padding: '8px 18px', borderRadius: 8, background: 'rgba(255,255,255,.05)', border: `1px solid ${C.border2}`, color: C.sub, cursor: 'pointer', fontSize: 12 }}>
            ← Retour
          </button>
        </div>
      </div>
    )
  }

  const history      = report.history     ?? []
  const duration     = report.duration_min ?? 0
  const itemsPlayed  = report.items_played ?? history.length
  const efficaces    = report.items_efficaces ?? history.filter(h => h.efficace || h.liked === true).length
  const skipped      = report.skip_count  ?? history.filter(h => h.skipped).length
  const da           = report.delta_alpha_global ?? 0
  const db           = report.delta_beta_global  ?? 0
  const success      = report.session_success ?? (da > 0.05 && db < -0.05)
  const efficacyPct  = itemsPlayed > 0 ? Math.round(efficaces / itemsPlayed * 100) : 0

  return (
    <div style={{
      minHeight: '100vh', background: C.bg,
      fontFamily: "'DM Sans', system-ui, sans-serif",
    }}>

      {/* ── Header ── */}
      <div style={{
        background: 'rgba(197,211,232,0.85)', borderBottom: '1px solid rgba(255,255,255,0.4)',
        padding: '0 28px', height: 57,
        display: 'flex', alignItems: 'center', gap: 14,
        position: 'sticky', top: 0, zIndex: 100,
        backdropFilter: 'blur(20px)', boxShadow: `0 2px 20px ${C.shadow}`,
      }}>
        <button
          onClick={onClose}
          style={{ background: 'rgba(255,255,255,0.35)', border: `1px solid ${C.border2}`, borderRadius: 20, color: C.text, padding: '6px 14px', cursor: 'pointer', fontSize: 12, fontWeight: 500 }}
        >← Retour</button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28, height: 28, borderRadius: '50%',
            background: success ? `rgba(123,196,160,0.3)` : `linear-gradient(135deg,${C.purple},#7BA8C4)`,
            border: `1px solid ${success ? C.conc + '60' : 'rgba(255,255,255,0.5)'}`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, color: 'white',
          }}>{success ? '✅' : '🧠'}</div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: C.text }}>Rapport de séance</div>
            <div style={{ fontSize: 9, color: success ? C.conc : C.muted, fontFamily: "'DM Mono',monospace", letterSpacing: 1 }}>
              {success ? 'SÉANCE RÉUSSIE — Alpha ↑ Beta ↓' : 'DONNÉES ENREGISTRÉES'}
            </div>
          </div>
        </div>

        <div style={{ flex: 1 }} />

        <button
          onClick={onNewSession}
          style={{
            padding: '7px 16px', borderRadius: 20,
            background: 'rgba(184,123,158,0.15)', border: `1.5px solid rgba(184,123,158,0.4)`,
            color: C.purple, fontSize: 12, fontWeight: 700, cursor: 'pointer',
          }}
        >
          ↺ Nouvelle séance
        </button>
      </div>

      {/* ── Contenu ── */}
      <div style={{ maxWidth: 900, margin: '0 auto', padding: '28px 20px 60px' }}>

        {/* Stats grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: 12, marginBottom: 24 }}>
          <StatCard label="DURÉE"       value={`${duration} min`} color={C.text} />
          <StatCard label="STIMULI"     value={itemsPlayed}       color={C.text}   sub={`${efficaces} efficaces`} />
          <StatCard label="EFFICACITÉ"  value={`${efficacyPct}%`} color={efficacyPct >= 50 ? C.conc : C.muted} sub="stimuli → ∆α>0.05" />
          <StatCard label="IGNORÉS"     value={skipped}           color={C.muted}  sub="skip count" />
        </div>

        {/* Évolution EEG */}
        <div style={{
          background: C.card, border: `1px solid ${C.border2}`,
          borderRadius: 14, padding: '20px 22px', marginBottom: 20,
          backdropFilter: 'blur(10px)', boxShadow: `0 4px 20px ${C.shadow}`,
        }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: C.purple, letterSpacing: 2.5, marginBottom: 16, fontFamily: "'DM Mono',monospace", textTransform: 'uppercase' }}>
            📈 Évolution des bandes EEG
          </div>
          <DeltaBar label="Δ Alpha (cible > +0.050)" value={da} targetGood={true} />
          <DeltaBar label="Δ Beta  (cible < −0.050)" value={db} targetGood={false} />
          <div style={{ fontSize: 10, color: C.muted, marginTop: 8, lineHeight: 1.7, fontFamily: "'DM Mono',monospace" }}>
            Alpha ↑ = relaxation améliorée · Beta ↓ = arousal réduit
            (Thaut 1999 · Nozaradan 2011 · Birbaumer 1999)
          </div>
        </div>

        {/* Rapport IA */}
        {report.rapport_ia && (
          <div style={{
            background: C.card, border: `1px solid rgba(184,123,158,0.35)`,
            borderRadius: 14, padding: '20px 22px', marginBottom: 20,
            backdropFilter: 'blur(10px)', boxShadow: `0 4px 20px ${C.shadow}`,
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: C.purple, letterSpacing: 2.5, fontFamily: "'DM Mono',monospace", textTransform: 'uppercase' }}>
                🤖 Analyse IA de la séance
              </div>
              <span style={{
                fontSize: 9, padding: '3px 10px', borderRadius: 20,
                background: `rgba(184,123,158,0.15)`, border: `1px solid rgba(184,123,158,0.35)`, color: C.purple,
                fontFamily: "'DM Mono',monospace",
              }}>Claude Haiku</span>
            </div>
            <div style={{
              fontSize: 13, color: C.text, lineHeight: 1.8,
              padding: '14px 16px', borderRadius: 12,
              background: 'rgba(255,255,255,0.35)', border: `1px solid ${C.border}`,
              whiteSpace: 'pre-wrap',
            }}>
              {report.rapport_ia}
            </div>
          </div>
        )}

        {/* Historique */}
        {history.length > 0 && (
          <div style={{
            background: C.card, border: `1px solid ${C.border2}`,
            borderRadius: 14, overflow: 'hidden',
            backdropFilter: 'blur(10px)', boxShadow: `0 4px 20px ${C.shadow}`,
          }}>
            <div style={{
              padding: '14px 18px', borderBottom: `1px solid rgba(255,255,255,0.4)`,
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <div style={{ fontSize: 9, fontWeight: 700, color: C.muted, letterSpacing: 2.5, fontFamily: "'DM Mono',monospace", textTransform: 'uppercase' }}>
                Stimuli joués
              </div>
              <span style={{ fontSize: 10, color: C.muted, fontFamily: "'DM Mono',monospace" }}>{history.length} items</span>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
                <thead>
                  <tr>
                    {['#', 'Type', 'Fichier', 'Δ Alpha', 'Δ Beta', 'Résultat'].map(h => (
                      <th key={h} style={{
                        padding: '8px 10px', textAlign: 'left',
                        color: C.muted, fontSize: 9, fontWeight: 700, letterSpacing: 1.5,
                        borderBottom: `1px solid rgba(255,255,255,0.4)`, whiteSpace: 'nowrap',
                        fontFamily: "'DM Mono',monospace", textTransform: 'uppercase',
                      }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {history.map((item, i) => <HistoryItem key={i} item={item} idx={i} />)}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Actions bas de page */}
        <div style={{ display: 'flex', gap: 12, marginTop: 24, justifyContent: 'flex-end' }}>
          <button
            onClick={onClose}
            style={{ padding: '10px 20px', borderRadius: 20, background: 'rgba(255,255,255,0.35)', border: `1px solid ${C.border2}`, color: C.text, fontSize: 12, fontWeight: 600, cursor: 'pointer' }}
          >
            ← Retour à l'analyse
          </button>
          <button
            onClick={onNewSession}
            style={{ padding: '10px 20px', borderRadius: 20, background: 'rgba(184,123,158,0.15)', border: `1.5px solid rgba(184,123,158,0.4)`, color: C.purple, fontSize: 12, fontWeight: 700, cursor: 'pointer' }}
          >
            ↺ Nouvelle séance
          </button>
        </div>
      </div>
    </div>
  )
}
