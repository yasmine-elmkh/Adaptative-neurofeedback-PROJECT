import { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import { useAuthStore } from '../stores'
import { useFeedbackEngine } from '../hooks/useFeedbackEngine'

import BrainStateIndicator  from '../components/feedback/BrainStateIndicator'
import FeedbackSelector     from '../components/feedback/FeedbackSelector'
import FeedbackReport       from '../components/feedback/FeedbackReport'
import FeedbackJustification from '../components/feedback/FeedbackJustification'
import AudioFeedback        from '../components/feedback/AudioFeedback'
import ImageFeedback        from '../components/feedback/ImageFeedback'
import VideoFeedback        from '../components/feedback/VideoFeedback'
import GameFeedback         from '../components/feedback/GameFeedback'

// ── Palette bleu-mauve cohérente avec l'app ──────────────────────────────────
const P = {
  bg:      '#C5D3E8',
  card:    'rgba(247,243,250,0.55)',
  accent:  '#B87B9E',
  accent2: '#9A6B8E',
  text:    '#2B2A4A',
  text2:   '#9A8BAE',
  shadow:  'rgba(180,169,196,0.45)',
}

const STATE_OPTIONS = [
  { value: 'stress',     label: '😰 Stress',   color: '#E87B9E' },
  { value: 'focus',      label: '🎯 Focus',    color: '#7BA8C4' },
  { value: 'relax',      label: '🌿 Relax',    color: '#7BC4A0' },
  { value: 'distracted', label: '😶 Distrait', color: '#C4A87B' },
  { value: 'neutral',    label: '😌 Neutre',   color: '#9A8BAE' },
]

// ── Phase : Sélection de l'état EEG ─────────────────────────────────────────
function SetupPhase({ initialState, onStart }) {
  const [selected, setSelected] = useState(initialState || 'neutral')
  const [loading, setLoading] = useState(false)

  const handleStart = async () => {
    setLoading(true)
    await onStart(selected)
    setLoading(false)
  }

  return (
    <div style={{ minHeight: '70vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem', fontFamily: "'Outfit',sans-serif" }}>
      <div style={{ width: '100%', maxWidth: 480, background: P.card, borderRadius: 24, padding: '40px', border: '1px solid rgba(255,255,255,0.6)', backdropFilter: 'blur(20px)', boxShadow: `0 20px 60px ${P.shadow}` }}>

        {/* Logo zone */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ fontSize: 44, marginBottom: 8 }}>🧠</div>
          <div style={{ fontSize: 22, fontWeight: 800, background: `linear-gradient(135deg, ${P.text}, ${P.accent})`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Session Neurofeedback
          </div>
          <div style={{ fontSize: 12, color: P.text2, marginTop: 6, lineHeight: 1.5 }}>
            Régulation cognitive adaptative — NeuroCap<br/>
            <span style={{ fontSize: 10, fontFamily: 'monospace' }}>Concentration · Relaxation · Réduction du stress</span>
          </div>
        </div>

        {/* Sélection état EEG */}
        <div style={{ marginBottom: 24 }}>
          <label style={{ display: 'block', fontSize: 10, color: P.text2, fontFamily: 'monospace', letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 10 }}>
            État EEG de départ
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {STATE_OPTIONS.map(opt => (
              <button
                key={opt.value}
                onClick={() => setSelected(opt.value)}
                style={{
                  padding: '12px 16px', borderRadius: 14, border: `1.5px solid ${selected === opt.value ? opt.color : 'rgba(255,255,255,0.5)'}`,
                  background: selected === opt.value ? `${opt.color}18` : 'rgba(255,255,255,0.3)',
                  color: selected === opt.value ? opt.color : P.text2,
                  fontWeight: selected === opt.value ? 700 : 500, fontSize: 14,
                  cursor: 'pointer', textAlign: 'left', transition: 'all 0.2s',
                  boxShadow: selected === opt.value ? `0 4px 16px ${opt.color}30` : 'none',
                }}
              >
                {opt.label}
                {selected === opt.value && (
                  <span style={{ float: 'right', fontSize: 10, fontFamily: 'monospace', opacity: 0.7 }}>sélectionné</span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Description de l'état sélectionné */}
        <div style={{
          padding: '12px 16px', borderRadius: 12,
          background: 'rgba(184,123,158,0.08)', border: '1px solid rgba(184,123,158,0.2)',
          marginBottom: 24, fontSize: 12, color: P.text2, lineHeight: 1.6,
        }}>
          {selected === 'stress'     && '→ Stimuli apaisants recommandés : sons doux, images de nature, jeux légers de coloriage pour réduire le cortisol.'}
          {selected === 'focus'      && '→ Stimuli cognitifs recommandés : jeux de logique, calcul mental, énigmes pour maintenir le cerveau en zone de flow.'}
          {selected === 'relax'      && '→ Stimuli de maintien : contenus immersifs légers pour consolider l\'état de relaxation.'}
          {selected === 'distracted' && '→ Stimuli de focalisation recommandés : jeux de mémoire, sudoku pour réentraîner l\'attention.'}
          {selected === 'neutral'    && '→ Stimuli de transition : contenus variés pour explorer vos préférences et calibrer le système.'}
        </div>

        <button
          onClick={handleStart}
          disabled={loading}
          style={{
            width: '100%', padding: 16, borderRadius: 18, border: 'none',
            background: `linear-gradient(135deg, ${P.accent}, ${P.accent2})`,
            color: 'white', fontSize: 15, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
            boxShadow: '0 6px 24px rgba(184,123,158,0.45)', opacity: loading ? 0.7 : 1,
          }}
        >
          {loading ? 'Démarrage…' : '→ Démarrer la session'}
        </button>
      </div>
    </div>
  )
}

// ── Phase : Rapport final ────────────────────────────────────────────────────
function RapportPhase({ rapport, onRestart }) {
  return (
    <div style={{ maxWidth: 640, margin: '2rem auto', padding: '0 1rem', fontFamily: "'Outfit',sans-serif" }}>
      <FeedbackReport report={rapport} onClose={onRestart} />
    </div>
  )
}

const MEDIA_FILTERS = [
  { key: null,    label: 'Tous',   icon: '🎯' },
  { key: 'image', label: 'Images', icon: '🖼️' },
  { key: 'audio', label: 'Audio',  icon: '🎵' },
  { key: 'video', label: 'Vidéo',  icon: '🎬' },
  { key: 'game',  label: 'Jeux',   icon: '🎮' },
]

// ── Phase : Session principale ───────────────────────────────────────────────
function SessionPhase({ sessionId, eegState, confidence, features, user, onEnd, onChangeState }) {
  const { recommend, submitFeedback, endSession } = useFeedbackEngine()
  const [currentMedia,     setCurrentMedia]     = useState(null)
  const [loadingMedia,     setLoadingMedia]     = useState(false)
  const [showForm,         setShowForm]         = useState(false)
  const [itemCount,        setItemCount]        = useState(0)
  const [mediaTypeFilter,  setMediaTypeFilter]  = useState(null)

  // Charge le premier média au montage
  useEffect(() => {
    loadRecommendation(mediaTypeFilter)
  }, [sessionId])

  const loadRecommendation = async (typeFilter = mediaTypeFilter) => {
    setLoadingMedia(true)
    setShowForm(false)
    try {
      const media = await recommend(sessionId, eegState, features || {}, typeFilter)
      setCurrentMedia(media)
      setItemCount(c => c + 1)
    } catch (e) {
      console.error('[FeedbackPage] recommend error:', e)
    } finally {
      setLoadingMedia(false)
    }
  }

  const handleFilterChange = (key) => {
    setMediaTypeFilter(key)
    loadRecommendation(key)
  }

  const handleFeedback = async (liked, ressenti, noteC, noteS) => {
    if (currentMedia) {
      await submitFeedback(sessionId, currentMedia, liked, ressenti, noteC, noteS)
    }
    setShowForm(false)
    loadRecommendation()
  }

  const handleEnd = async () => {
    const report = await endSession(sessionId)
    onEnd(report)
  }

  return (
    <div style={{ maxWidth: 640, margin: '0 auto', padding: '1rem', fontFamily: "'Outfit',sans-serif" }}>

      {/* Barre de filtre type de média */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
        {MEDIA_FILTERS.map(f => (
          <button
            key={String(f.key)}
            onClick={() => handleFilterChange(f.key)}
            style={{
              padding: '6px 12px', borderRadius: 12, fontSize: 12, cursor: 'pointer',
              background: mediaTypeFilter === f.key ? `${P.accent}22` : 'rgba(255,255,255,0.08)',
              border: `1.5px solid ${mediaTypeFilter === f.key ? P.accent : 'rgba(255,255,255,0.15)'}`,
              color: mediaTypeFilter === f.key ? P.accent : P.text2,
              fontWeight: mediaTypeFilter === f.key ? 700 : 400,
            }}
          >{f.icon} {f.label}</button>
        ))}
      </div>

      {/* En-tête de session */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
        <BrainStateIndicator state={eegState} confidence={confidence} />
        <div style={{ display: 'flex', gap: 8 }}>
          <span style={{ fontSize: 10, color: P.text2, fontFamily: 'monospace', alignSelf: 'center' }}>
            #{itemCount} stimulus
          </span>
          <button
            onClick={handleEnd}
            style={{
              padding: '7px 14px', borderRadius: 12, fontSize: 12, fontWeight: 600, cursor: 'pointer',
              background: 'rgba(232,123,158,0.12)', border: '1.5px solid rgba(232,123,158,0.35)',
              color: '#8c4a6a',
            }}
          >
            ⏹ Terminer
          </button>
        </div>
      </div>

      {/* Chargement */}
      {loadingMedia && (
        <div style={{ textAlign: 'center', padding: '2rem', color: P.text2 }}>
          <div style={{ fontSize: 28, marginBottom: 8, animation: 'nc-blink-dot 1s ease-in-out infinite' }}>🧠</div>
          <div style={{ fontSize: 12 }}>Sélection du stimulus optimal…</div>
        </div>
      )}

      {/* Média courant */}
      {!loadingMedia && currentMedia && (
        <div style={{ background: P.card, borderRadius: 18, padding: '1rem', border: '1px solid rgba(255,255,255,0.6)', backdropFilter: 'blur(10px)', boxShadow: `0 4px 20px ${P.shadow}` }}>

          {/* Badge type */}
          <div style={{ marginBottom: 12 }}>
            <span style={{ fontSize: 10, fontWeight: 700, color: P.text2, fontFamily: 'monospace', letterSpacing: 1, textTransform: 'uppercase',
              background: 'rgba(184,123,158,0.12)', border: '1px solid rgba(184,123,158,0.2)', borderRadius: 20, padding: '3px 10px' }}>
              {currentMedia.type === 'audio' ? '🎵 Audio'
               : currentMedia.type === 'image' ? '🖼️ Image'
               : currentMedia.type === 'video' ? '🎬 Vidéo'
               : '🎮 Jeu'}
            </span>
          </div>

          {/* Rendu du média */}
          {currentMedia.type === 'audio' && (
            <AudioFeedback src={currentMedia.url_cloudinary || currentMedia.url} />
          )}
          {currentMedia.type === 'image' && (
            <ImageFeedback src={currentMedia.url_cloudinary || currentMedia.url} alt="" />
          )}
          {currentMedia.type === 'video' && (
            <VideoFeedback src={currentMedia.url_cloudinary || currentMedia.url} />
          )}
          {currentMedia.type === 'game' && (
            <GameFeedback game={currentMedia} eegState={eegState} onWin={(r) => console.log('[Game] win', r)} />
          )}

          {/* Justification IA */}
          <div style={{ marginTop: 12 }}>
            <FeedbackJustification
              mediaId={currentMedia.id}
              type={currentMedia.type}
              state={eegState}
              userId={user?.id}
            />
          </div>

          {/* Bouton évaluer / Formulaire feedback */}
          <div style={{ marginTop: 12 }}>
            {!showForm ? (
              <button
                onClick={() => setShowForm(true)}
                style={{
                  width: '100%', padding: 12, borderRadius: 18, border: 'none',
                  background: `linear-gradient(135deg, ${P.accent}, ${P.accent2})`,
                  color: 'white', fontSize: 14, fontWeight: 600, cursor: 'pointer',
                  boxShadow: '0 4px 16px rgba(184,123,158,0.35)',
                }}
              >
                Évaluer ce stimulus
              </button>
            ) : (
              <FeedbackSelector onSubmit={handleFeedback} onSkip={loadRecommendation} />
            )}
          </div>
        </div>
      )}

      {/* Pas de média disponible */}
      {!loadingMedia && !currentMedia && (
        <div style={{
          textAlign: 'center', padding: '2rem',
          background: P.card, borderRadius: 18,
          border: '1px solid rgba(255,255,255,0.6)',
        }}>
          <div style={{ fontSize: 28, marginBottom: 8 }}>🔌</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: P.text, marginBottom: 8 }}>
            Aucun média disponible
          </div>
          <div style={{ fontSize: 12, color: P.text2, marginBottom: 16 }}>
            Le backend de recommandation n'est pas accessible ou la base de médias est vide.
          </div>
          <button
            onClick={loadRecommendation}
            style={{ padding: '10px 20px', borderRadius: 12, border: 'none', background: `linear-gradient(135deg, ${P.accent}, ${P.accent2})`, color: 'white', fontWeight: 600, cursor: 'pointer' }}
          >
            Réessayer
          </button>
        </div>
      )}
    </div>
  )
}

// ── Page principale ──────────────────────────────────────────────────────────
export default function FeedbackPage() {
  const location = useLocation()
  const navigate = useNavigate()

  // Peut recevoir un état EEG initial ou un contexte protocole via location.state
  const { eegState: initState, features, confidence, fromProtocol, sessionN } = location.state || {}

  const handleStart = (selectedState) => {
    navigate('/feedback/session', {
      state: {
        eeg_state:                 selectedState,
        classification_confidence:  confidence ?? 0,
        features_snapshot:          features ?? null,
        fromProtocol:               fromProtocol ?? false,
        sessionN:                   sessionN ?? null,
      },
    })
  }

  return (
    <div
      className="min-h-screen"
      style={{ background: 'linear-gradient(160deg, #C5D3E8 0%, #D9C9E5 50%, #C5D3E8 100%)', minHeight: '100vh' }}
    >
      <div style={{
        borderBottom: '1px solid rgba(255,255,255,0.4)',
        background: 'rgba(247,243,250,0.5)',
        backdropFilter: 'blur(12px)',
        padding: '14px 24px',
        display: 'flex',
        alignItems: 'center',
        gap: 12,
      }}>
        <button
          onClick={() => navigate(-1)}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '6px 12px', borderRadius: 10, border: '1.5px solid rgba(184,123,158,0.3)',
            background: 'rgba(255,255,255,0.4)', color: P.text2,
            fontSize: 12, fontWeight: 600, cursor: 'pointer',
            backdropFilter: 'blur(6px)', transition: 'all 0.2s',
          }}
          onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.65)'}
          onMouseLeave={e => e.currentTarget.style.background = 'rgba(255,255,255,0.4)'}
        >
          <ArrowLeft size={14} />
          Retour
        </button>

        <span style={{ fontSize: 20 }}>🧠</span>
        <div>
          <div style={{ fontWeight: 700, fontSize: 16, color: P.text }}>Neurofeedback au choix</div>
          <div style={{ fontSize: 11, color: P.text2 }}>Sélectionnez votre état EEG actuel</div>
        </div>
      </div>

      <SetupPhase initialState={initState} onStart={handleStart} />
    </div>
  )
}
