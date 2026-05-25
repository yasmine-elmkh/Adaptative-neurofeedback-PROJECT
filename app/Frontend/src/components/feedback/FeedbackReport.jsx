export default function FeedbackReport({ report, onClose }) {
  if (!report) return null

  const history    = report.history      ?? []
  const duration   = report.duration_min ?? 0
  const liked      = report.liked_count  ?? history.filter(h => h.liked === true).length
  const disliked   = report.disliked_count ?? history.filter(h => h.liked === false).length
  const noteConc   = report.avg_note_concentration ?? '—'
  const noteStress = report.avg_note_stress ?? '—'

  const stats = [
    { label: 'Durée',             value: `${duration} min`, color: '#7BA8C4' },
    { label: '👍 Utiles',         value: liked,              color: '#7BC4A0' },
    { label: '👎 Non utiles',     value: disliked,           color: '#E87B9E' },
    { label: 'Concentration /5',  value: noteConc,           color: '#B87B9E' },
    { label: 'Stress réduit /5',  value: noteStress,         color: '#7BC4A0' },
    { label: 'Stimuli joués',     value: report.items_played ?? history.length, color: '#2B2A4A' },
  ]

  return (
    <div style={{
      padding: '20px', borderRadius: 18,
      background: 'rgba(247,243,250,0.45)',
      border: '1px solid rgba(255,255,255,0.6)',
      backdropFilter: 'blur(10px)',
      boxShadow: '0 4px 20px rgba(180,169,196,0.45)',
    }}>
      <div style={{ fontSize: 9, fontWeight: 700, color: '#9A8BAE', letterSpacing: 2.5, textTransform: 'uppercase', fontFamily: 'monospace', marginBottom: 16 }}>
        Rapport de session
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 10, marginBottom: 20 }}>
        {stats.map(s => (
          <div key={s.label} style={{
            background: 'rgba(255,255,255,0.35)', border: '1px solid rgba(255,255,255,0.5)',
            borderRadius: 12, padding: 14, textAlign: 'center',
          }}>
            <div style={{ fontSize: 22, fontWeight: 700, color: s.color, fontFamily: 'monospace' }}>{s.value}</div>
            <div style={{ fontSize: 10, color: '#9A8BAE', marginTop: 4 }}>{s.label}</div>
          </div>
        ))}
      </div>

      {report.rapport_claude && (
        <div style={{
          background: 'rgba(123,168,196,0.08)', border: '1px solid rgba(123,168,196,0.25)',
          borderRadius: 12, padding: '12px 16px', marginBottom: 16,
        }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: '#7BA8C4', letterSpacing: 1.5, textTransform: 'uppercase', fontFamily: 'monospace', marginBottom: 8 }}>
            ✦ Rapport IA
          </div>
          <p style={{ fontSize: 12, color: '#2B2A4A', lineHeight: 1.65, margin: 0 }}>{report.rapport_claude}</p>
        </div>
      )}

      <button
        onClick={onClose}
        style={{
          width: '100%', padding: 13, borderRadius: 18, border: 'none',
          background: 'linear-gradient(135deg, #B87B9E, #9A6B8E)',
          color: 'white', fontSize: 14, fontWeight: 600, cursor: 'pointer',
          boxShadow: '0 4px 16px rgba(184,123,158,0.4)',
        }}
      >
        ← Nouvelle session
      </button>
    </div>
  )
}
