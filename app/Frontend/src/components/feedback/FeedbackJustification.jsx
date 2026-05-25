import { useState, useEffect, useRef } from 'react'

const STATIC_GUIDE = {
  audio: {
    icon: '🎵',
    why: (s) => s === 'stress'
      ? 'Les sons doux réduisent le cortisol et activent le système parasympathique.'
      : s === 'focus'
      ? 'La musique à 40 Hz synchronise les ondes cérébrales et améliore la concentration.'
      : 'Un fond sonore apaisant stabilise les ondes alpha.',
    tips: [
      '🎧 Fermez les yeux si possible.',
      '🧘 Concentrez-vous sur votre respiration en écoutant.',
      '🌿 Laissez les vibrations vous imprégner progressivement.',
      '🎵 Observez les changements de tonalité et de rythme.',
    ],
  },
  image: {
    icon: '🖼️',
    why: (s) => s === 'stress'
      ? 'Les images de nature activent le cortex préfrontal et réduisent l\'activation de l\'amygdale.'
      : s === 'focus'
      ? 'Une image inspirante ancre l\'attention sans la surcharger.'
      : 'Le regard contemplatif synchronise les ondes alpha.',
    tips: [
      '👁️ Laissez votre regard se promener librement.',
      '🔆 Notez la luminosité générale — comment vous affecte-t-elle ?',
      '🎨 Identifiez les couleurs dominantes et leurs nuances.',
      '🔍 Explorez les détails fins en arrière-plan.',
      '🧘 Respirez doucement en observant sans forcer.',
    ],
  },
  video: {
    icon: '🎬',
    why: (s) => s === 'stress'
      ? 'Les vidéos de nature activent le système parasympathique 3x plus vite.'
      : s === 'focus'
      ? 'Un contenu vidéo court booste la dopamine et maintient l\'attention.'
      : 'Une vidéo immersive entraîne le cerveau dans un état de flow.',
    tips: [
      '🎬 Suivez le mouvement sans tension oculaire.',
      '🚶 Observez le rythme — lent ou dynamique ?',
      '👀 Notez les transitions de couleur et de lumière.',
      '💨 Laissez-vous porter par l\'ambiance sans analyser.',
      '🌊 Synchronisez votre respiration sur le mouvement de la scène.',
    ],
  },
  game: {
    icon: '🎮',
    why: (s) => s === 'stress'
      ? 'Un jeu simple de coloriage détourne l\'attention du stress.'
      : s === 'focus'
      ? 'Un jeu cognitif adapté maintient le cerveau en zone de flow.'
      : 'L\'interaction ludique stimule la neuroplasticité.',
    tips: [
      '🎮 Jouez à votre rythme, sans pression.',
      '🧠 Le jeu s\'adapte automatiquement à votre état EEG.',
      '⚖️ Ne cherchez pas la perfection — restez détendu(e).',
      '✨ L\'objectif est l\'engagement, pas le score.',
    ],
  },
}

export default function FeedbackJustification({ mediaId, type, state, userId }) {
  const [apiData, setApiData] = useState(null)
  const [tipIdx,  setTipIdx]  = useState(0)
  const [visible, setVisible] = useState(true)
  const [loading, setLoading] = useState(false)
  const prevMediaId = useRef(null)

  useEffect(() => {
    if (!mediaId || mediaId === prevMediaId.current) return
    prevMediaId.current = mediaId
    setApiData(null); setTipIdx(0); setLoading(true)

    fetch('/api/feedback/justify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ media_id: mediaId, user_id: userId || 'anonymous', eeg_state: state || 'neutral' }),
    })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d && !d.error) setApiData(d) })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [mediaId, state, userId])

  useEffect(() => { setTipIdx(0) }, [apiData, type])

  const meta = STATIC_GUIDE[type] || STATIC_GUIDE.audio
  const tips = apiData?.guide ?? meta.tips ?? []

  useEffect(() => {
    if (tips.length <= 1) return
    const interval = setInterval(() => {
      setVisible(false)
      setTimeout(() => { setTipIdx(i => (i + 1) % tips.length); setVisible(true) }, 350)
    }, 4500)
    return () => clearInterval(interval)
  }, [tips.length])

  const justText   = apiData?.justification || meta.why(state)
  const currentTip = tips[tipIdx] || ''

  return (
    <div style={{ padding: '12px 16px', borderRadius: 14, background: 'rgba(184,123,158,0.08)', border: '1px solid rgba(184,123,158,0.25)' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
        <span style={{ fontSize: 14 }}>{meta.icon}</span>
        <span style={{ fontSize: 11, fontWeight: 700, color: '#B87B9E', flex: 1 }}>
          Pourquoi ce {type} pour vous ?
        </span>
        {apiData ? (
          <span style={{ fontSize: 9, fontWeight: 700, letterSpacing: 0.8, color: '#7BA8C4', background: 'rgba(123,168,196,0.12)', border: '1px solid rgba(123,168,196,0.3)', borderRadius: 20, padding: '2px 7px' }}>
            ✦ IA
          </span>
        ) : loading ? (
          <span style={{ fontSize: 9, color: '#9A8BAE', fontStyle: 'italic' }}>analyse…</span>
        ) : null}
      </div>

      <div style={{ fontSize: 11.5, color: '#2B2A4A', lineHeight: 1.65, marginBottom: 10 }}>{justText}</div>

      {tips.length > 0 && (
        <div style={{ background: 'rgba(255,255,255,0.5)', borderRadius: 10, border: '1px solid rgba(184,123,158,0.2)', padding: '8px 12px', display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 3, flexShrink: 0 }}>
            {tips.map((_, i) => (
              <div key={i} style={{ width: 3, height: i === tipIdx ? 14 : 5, borderRadius: 2, background: i === tipIdx ? '#B87B9E' : 'rgba(184,123,158,0.25)', transition: 'all .4s' }} />
            ))}
          </div>
          <div style={{ fontSize: 12, color: '#2B2A4A', lineHeight: 1.55, flex: 1, opacity: visible ? 1 : 0, transition: 'opacity 0.35s ease' }}>
            {currentTip}
          </div>
          <button
            onClick={() => { setVisible(false); setTimeout(() => { setTipIdx(i => (i + 1) % tips.length); setVisible(true) }, 200) }}
            style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: 16, color: 'rgba(184,123,158,0.5)', padding: 4, flexShrink: 0 }}
          >›</button>
        </div>
      )}

      {tips.length > 1 && (
        <div style={{ display: 'flex', gap: 4, marginTop: 7, justifyContent: 'center' }}>
          {tips.map((_, i) => (
            <button
              key={i}
              onClick={() => { setTipIdx(i); setVisible(true) }}
              style={{ width: i === tipIdx ? 16 : 5, height: 5, borderRadius: 3, border: 'none', padding: 0, background: i === tipIdx ? '#B87B9E' : 'rgba(184,123,158,0.25)', cursor: 'pointer', transition: 'all .35s' }}
            />
          ))}
        </div>
      )}
    </div>
  )
}
