// FeedbackSetup.jsx (composant) — Palette Bleu Mauve
import { useState } from "react"

const P = {
  accent: '#B87B9E', accent2: '#9A6B8E',
  text: '#2B2A4A', text2: '#9A8BAE',
  glass: 'rgba(247,243,250,0.45)',
  shadow: 'rgba(180,169,196,0.45)',
}

export default function FeedbackSetup({ onStart }) {
  const [objective, setObjective] = useState("stress_reduction")

  return (
    <div style={{
      padding: '32px', maxWidth: 480, margin: '0 auto',
      background: P.glass, border: '1px solid rgba(255,255,255,0.6)',
      borderRadius: 24, backdropFilter: 'blur(20px)',
      boxShadow: `0 20px 60px ${P.shadow}`,
    }}>
      <div style={{ fontSize: 9, fontWeight: 700, color: P.text2, letterSpacing: 2.5, textTransform: 'uppercase', fontFamily: "'DM Mono',monospace", marginBottom: 16 }}>
        Configuration de la séance
      </div>

      <label style={{ display: 'block', marginBottom: 6, fontSize: 11, color: P.text2, fontFamily: "'DM Mono',monospace", letterSpacing: 1.5, textTransform: 'uppercase' }}>
        Objectif
      </label>
      <select
        value={objective}
        onChange={e => setObjective(e.target.value)}
        style={{
          width: '100%', padding: '12px 16px', borderRadius: 12, fontSize: 14,
          border: '1.5px solid rgba(255,255,255,0.5)', background: 'rgba(255,255,255,0.4)',
          color: P.text, fontFamily: "'Outfit',sans-serif", outline: 'none', marginBottom: 20,
        }}
      >
        <option value="stress_reduction">🧘 Réduction du stress</option>
        <option value="focus_improvement">🎯 Amélioration de la concentration</option>
        <option value="relaxation">🌊 Relaxation profonde</option>
      </select>

      <button
        onClick={() => onStart(objective)}
        style={{
          width: '100%', padding: 16, borderRadius: 18, border: 'none',
          background: `linear-gradient(135deg, ${P.accent}, ${P.accent2})`,
          color: 'white', fontSize: 15, fontWeight: 700, cursor: 'pointer',
          boxShadow: '0 6px 24px rgba(184,123,158,0.45)', transition: 'all 0.25s',
        }}
      >
        → Démarrer
      </button>
    </div>
  )
}
