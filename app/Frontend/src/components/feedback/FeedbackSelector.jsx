import { useState } from 'react'

const RESSENTIS = [
  { value: 'tres_bien', emoji: '😄', label: 'Très bien' },
  { value: 'bien',      emoji: '🙂', label: 'Bien' },
  { value: 'neutre',    emoji: '😐', label: 'Neutre' },
  { value: 'pas_bien',  emoji: '😕', label: 'Pas bien' },
  { value: 'tres_mal',  emoji: '😣', label: 'Très mal' },
]

function StarRow({ value, onChange }) {
  return (
    <div style={{ display: 'flex', gap: 4 }}>
      {[1,2,3,4,5].map(n => (
        <button
          key={n}
          onClick={() => onChange(n)}
          style={{
            flex: 1, height: 24, borderRadius: 4, border: 'none', cursor: 'pointer',
            background: n <= value ? '#B87B9E' : 'rgba(255,255,255,0.4)',
            transition: 'background 0.15s',
          }}
        />
      ))}
    </div>
  )
}

export default function FeedbackSelector({ onSubmit, onSkip }) {
  const [liked,      setLiked]      = useState(null)
  const [ressenti,   setRessenti]   = useState('')
  const [noteConc,   setNoteConc]   = useState(0)
  const [noteStress, setNoteStress] = useState(0)

  const canSubmit = liked !== null

  return (
    <div style={{
      padding: '16px', borderRadius: 18,
      background: 'rgba(247,243,250,0.45)',
      border: '1px solid rgba(255,255,255,0.6)',
      backdropFilter: 'blur(10px)',
      boxShadow: '0 4px 20px rgba(180,169,196,0.45)',
    }}>
      <div style={{ fontSize: 9, fontWeight: 700, color: '#9A8BAE', letterSpacing: 2.5, textTransform: 'uppercase', fontFamily: 'monospace', marginBottom: 12 }}>
        Votre ressenti
      </div>

      {/* Like / Dislike */}
      <div style={{ display: 'flex', gap: 10, marginBottom: 14 }}>
        <button
          onClick={() => setLiked(true)}
          style={{
            flex: 1, padding: 14, borderRadius: 18, fontSize: 20,
            border: `2px solid ${liked === true ? '#7BC4A0' : 'rgba(255,255,255,0.5)'}`,
            background: liked === true ? 'rgba(123,196,160,0.25)' : 'rgba(255,255,255,0.3)',
            cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            transition: 'all 0.2s',
            boxShadow: liked === true ? '0 4px 16px rgba(123,196,160,0.3)' : 'none',
          }}
        >
          👍 <span style={{ fontSize: 12, fontWeight: 600, color: '#2B2A4A' }}>Ce média m'a aidé</span>
        </button>
        <button
          onClick={() => setLiked(false)}
          style={{
            flex: 1, padding: 14, borderRadius: 18, fontSize: 20,
            border: `2px solid ${liked === false ? '#E87B9E' : 'rgba(255,255,255,0.5)'}`,
            background: liked === false ? 'rgba(232,123,158,0.2)' : 'rgba(255,255,255,0.3)',
            cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            transition: 'all 0.2s',
            boxShadow: liked === false ? '0 4px 16px rgba(232,123,158,0.3)' : 'none',
          }}
        >
          👎 <span style={{ fontSize: 12, fontWeight: 600, color: '#2B2A4A' }}>Pas adapté</span>
        </button>
      </div>

      {/* Ressenti emojis */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 14 }}>
        {RESSENTIS.map(r => (
          <button
            key={r.value}
            onClick={() => setRessenti(r.value)}
            style={{
              flex: 1, padding: '8px 4px', borderRadius: 12, textAlign: 'center',
              border: `1px solid ${ressenti === r.value ? '#B87B9E' : 'rgba(255,255,255,0.5)'}`,
              background: ressenti === r.value ? 'rgba(255,255,255,0.6)' : 'rgba(255,255,255,0.3)',
              cursor: 'pointer', transition: 'all 0.2s',
            }}
          >
            <div style={{ fontSize: 20, marginBottom: 3 }}>{r.emoji}</div>
            <div style={{ fontSize: 9, color: '#9A8BAE' }}>{r.label}</div>
          </button>
        ))}
      </div>

      {/* Notes étoiles */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10, marginBottom: 14 }}>
        <div style={{ background: 'rgba(255,255,255,0.3)', border: '1px solid rgba(255,255,255,0.5)', borderRadius: 12, padding: '10px 12px' }}>
          <div style={{ fontSize: 10, color: '#9A8BAE', marginBottom: 8 }}>Concentration améliorée</div>
          <StarRow value={noteConc} onChange={setNoteConc} />
        </div>
        <div style={{ background: 'rgba(255,255,255,0.3)', border: '1px solid rgba(255,255,255,0.5)', borderRadius: 12, padding: '10px 12px' }}>
          <div style={{ fontSize: 10, color: '#9A8BAE', marginBottom: 8 }}>Stress diminué</div>
          <StarRow value={noteStress} onChange={setNoteStress} />
        </div>
      </div>

      {/* Boutons */}
      <div style={{ display: 'flex', gap: 8 }}>
        <button
          onClick={() => canSubmit && onSubmit(liked, ressenti, noteConc, noteStress)}
          disabled={!canSubmit}
          style={{
            flex: 2, padding: 13, borderRadius: 18, border: 'none',
            cursor: canSubmit ? 'pointer' : 'not-allowed',
            background: canSubmit ? 'linear-gradient(135deg, #B87B9E, #9A6B8E)' : 'rgba(255,255,255,0.3)',
            color: canSubmit ? 'white' : '#9A8BAE',
            fontSize: 14, fontWeight: 600,
            boxShadow: canSubmit ? '0 4px 16px rgba(184,123,158,0.4)' : 'none',
            transition: 'all 0.25s',
          }}
        >
          Enregistrer le feedback
        </button>
        <button
          onClick={onSkip}
          style={{
            flex: 1, padding: 13, borderRadius: 18,
            background: 'rgba(255,255,255,0.3)', border: '1px solid rgba(255,255,255,0.5)',
            color: '#9A8BAE', fontSize: 13, fontWeight: 500, cursor: 'pointer',
          }}
        >
          Passer →
        </button>
      </div>
    </div>
  )
}
