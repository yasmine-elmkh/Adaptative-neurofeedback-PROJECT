// FeedbackReport.jsx (composant) — Palette Bleu Mauve
const P = {
  text: '#2B2A4A', text2: '#9A8BAE',
  accent: '#B87B9E', green: '#7BC4A0', red: '#E87B9E', blue: '#7BA8C4',
  glass: 'rgba(247,243,250,0.45)',
  shadow: 'rgba(180,169,196,0.45)',
}

export default function FeedbackReport({ report, onClose }) {
  if (!report) return null

  const history     = report.history      ?? []
  const duration    = report.duration_min ?? 0
  const liked       = report.liked_count  ?? history.filter(h => h.liked === true).length
  const disliked    = report.disliked_count ?? history.filter(h => h.liked === false).length
  const noteConc    = report.avg_note_concentration ?? '—'
  const noteStress  = report.avg_note_stress ?? '—'

  const stats = [
    { label: 'Durée',           value: `${duration} min`, color: P.blue },
    { label: '👍 Utiles',       value: liked,             color: P.green },
    { label: '👎 Non utiles',   value: disliked,          color: P.red },
    { label: 'Concentration /5', value: noteConc,          color: P.accent },
    { label: 'Stress réduit /5', value: noteStress,        color: P.green },
    { label: 'Stimuli joués',   value: report.items_played ?? history.length, color: P.text },
  ]

  return (
    <div style={{
      padding: '20px', borderRadius: 18,
      background: P.glass, border: '1px solid rgba(255,255,255,0.6)',
      backdropFilter: 'blur(10px)', boxShadow: `0 4px 20px ${P.shadow}`,
    }}>
      <div style={{ fontSize: 9, fontWeight: 700, color: P.text2, letterSpacing: 2.5, textTransform: 'uppercase', fontFamily: "'DM Mono',monospace", marginBottom: 16 }}>
        Rapport de session
      </div>

      {/* Stats grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 20 }}>
        {stats.map(s => (
          <div key={s.label} style={{
            background: 'rgba(255,255,255,0.35)', border: '1px solid rgba(255,255,255,0.5)',
            borderRadius: 12, padding: 14, textAlign: 'center',
          }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: s.color, fontFamily: "'DM Mono',monospace" }}>
              {s.value}
            </div>
            <div style={{ fontSize: 10, color: P.text2, marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Bouton fermer */}
      <button
        onClick={onClose}
        style={{
          width: '100%', padding: 13, borderRadius: 18, border: 'none',
          background: `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
          color: 'white', fontSize: 14, fontWeight: 600, cursor: 'pointer',
          boxShadow: '0 4px 16px rgba(184,123,158,0.4)',
        }}
      >
        ← Nouvelle session
      </button>
    </div>
  )
}
