/**
 * FeedbackSetup.jsx — ÉCRAN 1 : Configuration de la séance neurofeedback
 * Affiche l'état EEG détecté, permet de choisir l'objectif, puis démarre.
 */

import { useState } from 'react'
import { useFeedbackEngine } from '../hooks/useFeedbackEngine'

// ── Palette Bleu Mauve ────────────────────────────────────────────────────────
const C = {
  bg: '#C5D3E8', card: 'rgba(247,243,250,0.45)',
  border: 'rgba(255,255,255,0.4)', border2: 'rgba(255,255,255,0.6)',
  text: '#2B2A4A', muted: '#9A8BAE', sub: '#2B2A4A',
  conc: '#7BC4A0', stress: '#E87B9E', uncert: '#C4A87B', purple: '#B87B9E',
  accent2: '#9A6B8E', shadow: 'rgba(180,169,196,0.45)',
}

const STATE_META = {
  stress:     { label: 'Stress',        icon: '😰', color: '#E87B9E', bg: 'rgba(232,123,158,0.12)',  border: 'rgba(232,123,158,0.35)', objDefault: 'stress_reduction' },
  focus:      { label: 'Concentration', icon: '🎯', color: '#7BA8C4', bg: 'rgba(123,168,196,0.12)',  border: 'rgba(123,168,196,0.35)', objDefault: 'focus_enhancement' },
  relax:      { label: 'Relax',         icon: '🌿', color: '#7BC4A0', bg: 'rgba(123,196,160,0.12)',  border: 'rgba(123,196,160,0.35)', objDefault: 'relaxation' },
  distracted: { label: 'Distrait',      icon: '😶', color: '#C4A87B', bg: 'rgba(196,168,123,0.12)',  border: 'rgba(196,168,123,0.35)', objDefault: 'stress_reduction' },
  neutral:    { label: 'Neutre',        icon: '😌', color: '#9A8BAE', bg: 'rgba(154,139,174,0.12)', border: 'rgba(154,139,174,0.30)', objDefault: 'stress_reduction' },
}

const OBJECTIVES = [
  { value: 'stress_reduction',  label: '🧘 Réduction du stress',             desc: 'Médias apaisants pour réduire le cortisol et activer l\'alpha' },
  { value: 'focus_enhancement', label: '🎯 Amélioration de la concentration', desc: 'Stimuli cognitifs pour renforcer le beta frontal' },
  { value: 'relaxation',        label: '🌊 Relaxation profonde',              desc: 'Entraînement theta/alpha pour atteindre un état de flow' },
]

const MEDIA_TYPES = [
  { value: 'audio', label: '🎵 Audio',    desc: 'Musique thérapeutique' },
  { value: 'image', label: '🖼️ Image',    desc: 'Stimulus visuel statique' },
  { value: 'video', label: '🎬 Vidéo',    desc: 'Saillance visuelle adaptative' },
  { value: 'game',  label: '🎮 Jeu',      desc: 'Activité cognitive adaptative' },
]

export default function FeedbackSetup({ data, onStart, onBack, onStartProtocol }) {
  const detectedState = data?.eegState ?? 'neutral'
  const meta          = STATE_META[detectedState] ?? STATE_META.neutral

  const [objective,  setObjective]  = useState(meta.objDefault)
  const [mediaTypes, setMediaTypes] = useState(['audio', 'image', 'video', 'game'])
  const [loading,    setLoading]    = useState(false)
  const [error,      setError]      = useState(null)

  const { startSession } = useFeedbackEngine()

  const toggleMedia = (v) => {
    setMediaTypes(prev =>
      prev.includes(v)
        ? prev.length > 1 ? prev.filter(t => t !== v) : prev
        : [...prev, v]
    )
  }

  const start = async () => {
    setLoading(true); setError(null)
    try {
      const sessionId = await startSession('neurocap_user', objective)
      onStart(sessionId, detectedState, data?.features ?? {})
    } catch (e) {
      setError(e.message || 'Impossible de démarrer la séance')
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh', background: C.bg,
      fontFamily: "'Outfit', 'DM Sans', system-ui, sans-serif",
    }}>

      {/* ── Header ── */}
      <div style={{
        background: 'rgba(197,211,232,0.85)', borderBottom: '1px solid rgba(255,255,255,0.4)',
        padding: '0 28px', height: 57, position: 'sticky', top: 0, zIndex: 100,
        display: 'flex', alignItems: 'center', gap: 14,
        backdropFilter: 'blur(20px)', boxShadow: `0 2px 20px ${C.shadow}`,
      }}>
        <button
          onClick={onBack}
          style={{
            background: 'rgba(255,255,255,0.35)', border: `1px solid ${C.border2}`,
            borderRadius: 20, color: C.text, padding: '6px 14px',
            cursor: 'pointer', fontSize: 12, fontWeight: 500,
          }}
        >← Retour</button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28, height: 28, borderRadius: '50%',
            background: `linear-gradient(135deg,${C.purple},#7BA8C4)`,
            display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14, color: 'white',
          }}>🧠</div>
          <div>
            <div style={{ fontSize: 15, fontWeight: 700, color: C.text }}>NeuroCap EEG</div>
            <div style={{ fontSize: 9, color: C.muted, fontFamily: "'DM Mono',monospace", letterSpacing: 1 }}>NEUROFEEDBACK ADAPTATIF</div>
          </div>
        </div>

        <div style={{ flex: 1 }} />
        <div style={{
          fontSize: 9, color: C.muted, fontFamily: "'DM Mono',monospace",
          padding: '4px 10px', borderRadius: 20, background: 'rgba(255,255,255,0.35)',
          border: `1px solid ${C.border}`,
        }}>
          Thompson Sampling · 812 items
        </div>
      </div>

      {/* ── Contenu ── */}
      <div style={{ maxWidth: 520, margin: '0 auto', padding: '32px 20px 60px' }}>

        {/* Titre */}
        <div style={{ marginBottom: 28, textAlign: 'center' }}>
          <div style={{
            fontSize: 26, fontWeight: 700, marginBottom: 6,
            background: `linear-gradient(135deg, ${C.text}, ${C.purple})`,
            WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
          }}>
            Configuration de la séance
          </div>
          <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.7 }}>
            Le moteur adaptatif sélectionne des stimuli via Thompson Sampling (prior cosinus + feedback utilisateur).
          </div>
        </div>

        {/* ── État EEG détecté ── */}
        <Section label="ÉTAT EEG DÉTECTÉ">
          <div style={{
            display: 'flex', alignItems: 'center', gap: 16,
            padding: '18px 20px',
            background: meta.bg, border: `1.5px solid ${meta.border}`,
            borderRadius: 14, backdropFilter: 'blur(10px)',
          }}>
            <div style={{
              width: 52, height: 52, borderRadius: 12, flexShrink: 0,
              background: `${meta.color}15`, border: `1px solid ${meta.border}`,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 26,
            }}>
              {meta.icon}
            </div>
            <div>
              <div style={{ fontSize: 18, fontWeight: 800, color: meta.color }}>
                {meta.label}
              </div>
              {data?.filename && (
                <div style={{ fontSize: 11, color: C.muted, marginTop: 3 }}>
                  Fichier : {data.filename}
                  {data.confidence && ` · Confiance : ${(data.confidence * 100).toFixed(1)}%`}
                </div>
              )}
              {!data?.filename && (
                <div style={{ fontSize: 11, color: C.muted, marginTop: 3 }}>
                  Vous pouvez modifier l'état ci-dessous
                </div>
              )}
            </div>
            <div style={{ flex: 1 }} />
            <div style={{
              fontSize: 10, fontFamily: "'Space Mono',monospace",
              color: meta.color, letterSpacing: .5,
            }}>
              {data?.source === 'csv' ? '📂 FICHIER' : '🎧 LIVE'}
            </div>
          </div>
        </Section>

        {/* ── Objectif ── */}
        <Section label="OBJECTIF DE LA SÉANCE">
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {OBJECTIVES.map(obj => (
              <label key={obj.value} style={{
                display: 'flex', alignItems: 'flex-start', gap: 12,
                padding: '14px 16px',
                background: objective === obj.value ? `rgba(184,123,158,0.15)` : 'rgba(255,255,255,0.3)',
                border: `1.5px solid ${objective === obj.value ? C.purple + '80' : C.border}`,
                borderRadius: 14, cursor: 'pointer', transition: 'all .15s',
                backdropFilter: 'blur(8px)',
              }}>
                <input
                  type="radio" name="objective" value={obj.value}
                  checked={objective === obj.value}
                  onChange={() => setObjective(obj.value)}
                  style={{ marginTop: 2, accentColor: C.purple, flexShrink: 0 }}
                />
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: C.text }}>{obj.label}</div>
                  <div style={{ fontSize: 11, color: C.muted, marginTop: 2 }}>{obj.desc}</div>
                </div>
              </label>
            ))}
          </div>
        </Section>

        {/* ── Types de médias ── */}
        <Section label="TYPES DE MÉDIAS AUTORISÉS">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
            {MEDIA_TYPES.map(mt => {
              const active = mediaTypes.includes(mt.value)
              return (
                <button
                  key={mt.value}
                  onClick={() => toggleMedia(mt.value)}
                  style={{
                    padding: '12px 14px', textAlign: 'left',
                    background: active ? 'rgba(184,123,158,0.15)' : 'rgba(255,255,255,0.3)',
                    border: `1.5px solid ${active ? C.purple + '80' : C.border}`,
                    borderRadius: 14, cursor: 'pointer', transition: 'all .15s',
                  }}
                >
                  <div style={{ fontSize: 13, fontWeight: 600, color: active ? C.text : C.muted }}>
                    {mt.label}
                  </div>
                  <div style={{ fontSize: 10, color: C.muted, marginTop: 2 }}>{mt.desc}</div>
                </button>
              )
            })}
          </div>
          <div style={{ fontSize: 10, color: C.muted, marginTop: 8, fontFamily: "'DM Mono',monospace" }}>
            Habituation entre types respectée (Grill-Spector & Malach 2001).
          </div>
        </Section>

        {/* ── Erreur ── */}
        {error && (
          <div style={{
            marginBottom: 16, padding: '12px 16px',
            background: 'rgba(232,123,158,0.15)', border: '1px solid rgba(232,123,158,0.4)',
            borderRadius: 14, fontSize: 12, color: '#8c4a6a', fontFamily: "'DM Mono',monospace",
          }}>
            ❌ {error}
          </div>
        )}

        {/* ── Bouton démarrer ── */}
        <button
          onClick={start}
          disabled={loading || mediaTypes.length === 0}
          style={{
            width: '100%', padding: 16,
            background: loading
              ? 'rgba(255,255,255,0.3)'
              : `linear-gradient(135deg, ${C.purple}, ${C.accent2})`,
            border: 'none', borderRadius: 18,
            color: loading ? C.muted : '#fff',
            fontSize: 15, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
            letterSpacing: .4, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            boxShadow: loading ? 'none' : '0 6px 24px rgba(184,123,158,0.45)',
            transition: 'all .25s',
          }}
        >
          {loading ? (
            <>
              <Spinner color={C.purple} />
              Démarrage en cours…
            </>
          ) : (
            '→ Démarrer la séance de neurofeedback'
          )}
        </button>

        <div style={{ marginTop: 14, textAlign: 'center', fontSize: 11, color: C.muted }}>
          Objectif : <span style={{ color: C.purple, fontWeight: 600 }}>
            {OBJECTIVES.find(o => o.value === objective)?.label}
          </span>
          {' · '}Médias actifs : {mediaTypes.join(', ')}
        </div>

        {/* ── Option Protocole 15 séances ── */}
        {onStartProtocol && (
          <div style={{ marginTop: 28 }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12,
            }}>
              <div style={{ flex:1, height:1, background:'rgba(184,123,158,0.15)' }} />
              <span style={{ fontSize:10, color:C.muted, fontFamily:"'DM Mono',monospace", whiteSpace:'nowrap' }}>
                OU LANCER LE PROTOCOLE STRUCTURÉ
              </span>
              <div style={{ flex:1, height:1, background:'rgba(184,123,158,0.15)' }} />
            </div>

            <button
              onClick={() => onStartProtocol(detectedState, data?.features ?? {})}
              style={{
                width: '100%', padding: 14,
                background: 'rgba(184,123,158,0.1)',
                border: `1.5px solid ${C.purple}50`,
                borderRadius: 18,
                color: C.purple,
                fontSize: 14, fontWeight: 700, cursor: 'pointer',
                letterSpacing: .4, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                transition: 'all .25s',
              }}
            >
              🧠 Protocole 15 séances (Mou et al., 2024)
            </button>
            <div style={{ marginTop: 8, textAlign:'center', fontSize:10, color:C.muted }}>
              Neurofeedback adaptatif · 5 blocs × 3 min · Seuil alpha adaptatif · Questionnaires pré/post
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

// ── Helpers UI ────────────────────────────────────────────────────────────────

function Section({ label, children }) {
  return (
    <div style={{ marginBottom: 22 }}>
      <div style={{
        fontSize: 9, fontWeight: 700, letterSpacing: 2.5, marginBottom: 10,
        color: C.muted, fontFamily: "'DM Mono', monospace", textTransform: 'uppercase',
      }}>
        {label}
      </div>
      {children}
    </div>
  )
}

function Spinner({ color = '#B87B9E' }) {
  return (
    <span style={{
      display: 'inline-block', width: 14, height: 14, flexShrink: 0,
      border: `2px solid ${color}22`, borderTopColor: color,
      borderRadius: '50%', animation: 'spin .7s linear infinite',
    }}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </span>
  )
}
