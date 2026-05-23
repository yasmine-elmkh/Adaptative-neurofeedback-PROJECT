/**
 * LiveFeedbackTab.jsx — Panel neurofeedback intégré au dashboard live
 * Reçoit eegState + features en temps réel depuis le WebSocket (App.jsx).
 * Gère son propre cycle session : idle → active → ended.
 */
import { useState, useCallback, useRef, useEffect } from 'react'
import { useFeedbackEngine }   from '../hooks/useFeedbackEngine'
import AudioFeedback           from './feedback/AudioFeedback'
import ImageFeedback           from './feedback/ImageFeedback'
import VideoFeedback           from './feedback/VideoFeedback'
import GameFeedback            from './feedback/GameFeedback'
import FeedbackSelector        from './feedback/FeedbackSelector'
import FeedbackJustification   from './feedback/FeedbackJustification'

const C = {
  card:   'rgba(255,255,255,0.03)',
  border: 'rgba(255,255,255,0.07)',
  text:   '#c9d8e8',
  muted:  '#4a5a6e',
  accent: '#00e5b0',
  purple: '#B87B9E',
}

const STATE_META = {
  stress:     { label: 'STRESS',        color: '#E87B9E', icon: '😰', desc: 'Médias apaisants sélectionnés' },
  focus:      { label: 'CONCENTRATION', color: '#7BA8C4', icon: '🎯', desc: 'Stimuli cognitifs actifs' },
  relax:      { label: 'RELAX',         color: '#7BC4A0', icon: '🌿', desc: 'Mode relaxation profonde' },
  distracted: { label: 'DISTRAIT',      color: '#C4A87B', icon: '😶', desc: 'Rétablissement du focus' },
  neutral:    { label: 'NEUTRE',        color: '#9A8BAE', icon: '😌', desc: 'État équilibré' },
}

const TYPE_OPTS = [
  { value: null,    icon: '🔀', label: 'Auto'  },
  { value: 'audio', icon: '🎵', label: 'Audio' },
  { value: 'image', icon: '🖼️', label: 'Image' },
  { value: 'video', icon: '🎬', label: 'Vidéo' },
  { value: 'game',  icon: '🎮', label: 'Jeu'   },
]

const OBJECTIVES = [
  { value: 'stress_reduction',  label: '🧘 Réduction du stress'    },
  { value: 'focus_enhancement', label: '🎯 Amélioration du focus'   },
  { value: 'relaxation',        label: '🌊 Relaxation profonde'     },
]

// ── Helpers UI ─────────────────────────────────────────────────────────────────
function Pill({ children, active, color, onClick }) {
  return (
    <button onClick={onClick} style={{
      padding: '4px 11px', borderRadius: 20, fontSize: 10, fontWeight: 600,
      border: `1px solid ${active ? (color || C.purple) : 'rgba(255,255,255,0.1)'}`,
      background: active ? `${color || C.purple}22` : 'transparent',
      color: active ? (color || C.purple) : C.muted,
      cursor: 'pointer', transition: 'all .12s',
    }}>{children}</button>
  )
}

function ActionBtn({ children, onClick, disabled, bg, color }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{
      padding: '7px 16px', borderRadius: 14, fontSize: 11, fontWeight: 600,
      border: '1px solid rgba(255,255,255,0.08)',
      background: disabled ? 'rgba(255,255,255,0.03)' : (bg || 'rgba(255,255,255,0.06)'),
      color: disabled ? C.muted : (color || C.text),
      cursor: disabled ? 'not-allowed' : 'pointer', transition: 'all .12s',
    }}>{children}</button>
  )
}

// ── Composant principal ────────────────────────────────────────────────────────
export default function LiveFeedbackTab({ eegState = 'neutral', features = {} }) {
  const [phase,       setPhase]       = useState('idle')   // idle | active | ended
  const [sessionId,   setSessionId]   = useState(null)
  const [media,       setMedia]       = useState(null)
  const [loading,     setLoading]     = useState(false)
  const [showFeed,    setShowFeed]    = useState(false)
  const [history,     setHistory]     = useState([])
  const [report,      setReport]      = useState(null)
  const [forcedType,  setForcedType]  = useState(null)
  const [objective,   setObjective]   = useState('stress_reduction')
  const [error,       setError]       = useState(null)

  const mountedRef   = useRef(true)
  const sessionIdRef = useRef(null)   // ref pour les closures async
  const eegStateRef  = useRef(eegState)
  const featuresRef  = useRef(features)

  useEffect(() => { eegStateRef.current = eegState }, [eegState])
  useEffect(() => { featuresRef.current = features }, [features])
  useEffect(() => () => { mountedRef.current = false }, [])

  const { startSession, recommend, submitFeedback, nextItem, skipItem, endSession } = useFeedbackEngine()

  const meta = STATE_META[eegState] ?? STATE_META.neutral

  // ── Charger un média ─────────────────────────────────────────────────────────
  const loadMedia = useCallback(async (sid, type) => {
    setLoading(true); setError(null)
    try {
      const m = await recommend(
        sid ?? sessionIdRef.current,
        eegStateRef.current,
        featuresRef.current,
        type ?? forcedType,
      )
      if (!mountedRef.current) return
      setMedia(m)
      if (!m) setError('Aucun média disponible pour cet état EEG.')
    } catch (e) {
      if (mountedRef.current) setError(e.message)
    } finally {
      if (mountedRef.current) setLoading(false)
    }
  }, [recommend, forcedType])

  // ── Démarrer la session ──────────────────────────────────────────────────────
  const handleStart = async () => {
    setLoading(true); setError(null)
    try {
      const sid = await startSession('neurocap_live', objective)
      sessionIdRef.current = sid
      setSessionId(sid)
      setHistory([])
      setPhase('active')
      await loadMedia(sid, forcedType)
    } catch (e) {
      if (mountedRef.current) { setError(e.message || 'Impossible de démarrer'); setLoading(false) }
    }
  }

  // ── Feedback utilisateur ─────────────────────────────────────────────────────
  const handleFeedback = useCallback(async (liked, ressenti, noteC, noteS) => {
    setShowFeed(false)
    if (media) {
      try { await submitFeedback(sessionIdRef.current, media, liked, ressenti, noteC, noteS) } catch {}
      setHistory(h => [...h, { ...media, liked }])
    }
    const next = await nextItem(sessionIdRef.current, eegStateRef.current, forcedType)
    if (mountedRef.current) {
      if (next) setMedia(next)
      else await loadMedia(null, forcedType)
    }
  }, [media, forcedType, submitFeedback, nextItem, loadMedia])

  // ── Skip ─────────────────────────────────────────────────────────────────────
  const handleSkip = useCallback(async () => {
    setShowFeed(false)
    if (media) setHistory(h => [...h, { ...media, skipped: true }])
    const next = await skipItem(sessionIdRef.current, eegStateRef.current, forcedType)
    if (mountedRef.current) {
      if (next) setMedia(next)
      else await loadMedia(null, forcedType)
    }
  }, [media, forcedType, skipItem, loadMedia])

  // ── Terminer ─────────────────────────────────────────────────────────────────
  const handleEnd = async () => {
    try {
      const rep = await endSession(sessionIdRef.current)
      if (mountedRef.current) { setReport(rep); setPhase('ended') }
    } catch {
      if (mountedRef.current) setPhase('ended')
    }
  }

  // ── Changer type forcé ───────────────────────────────────────────────────────
  const handleTypeChange = (type) => {
    setForcedType(type)
    if (phase === 'active') loadMedia(null, type)
  }

  // ════════════════════════════════════════════════════════════════════════════
  // IDLE
  // ════════════════════════════════════════════════════════════════════════════
  if (phase === 'idle') return (
    <div style={{
      height: '100%', display: 'flex', alignItems: 'center',
      justifyContent: 'center', padding: '20px',
    }}>
      <div style={{
        maxWidth: 440, width: '100%',
        background: C.card, border: `1px solid ${C.border}`,
        borderRadius: 20, padding: '36px 32px',
      }}>
        {/* Titre */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>🧠</div>
          <div style={{ fontSize: 17, fontWeight: 700, color: C.text, marginBottom: 6 }}>
            Neurofeedback adaptatif
          </div>
          <div style={{ fontSize: 11, color: C.muted, lineHeight: 1.7 }}>
            Thompson Sampling sélectionne en temps réel le stimulus<br/>optimal selon ton état EEG actuel.
          </div>
        </div>

        {/* État EEG live */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px',
          borderRadius: 14, marginBottom: 20,
          background: `${meta.color}10`, border: `1px solid ${meta.color}35`,
        }}>
          <span style={{ fontSize: 22 }}>{meta.icon}</span>
          <div>
            <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1.5 }}>ÉTAT EEG TEMPS RÉEL</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: meta.color }}>{meta.label}</div>
            <div style={{ fontSize: 10, color: C.muted }}>{meta.desc}</div>
          </div>
          <div style={{
            marginLeft: 'auto', width: 8, height: 8, borderRadius: '50%',
            background: meta.color, boxShadow: `0 0 8px ${meta.color}80`,
            animation: 'nf-pulse 2s ease-in-out infinite',
          }} />
        </div>

        {/* Objectif */}
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1.5, marginBottom: 8, textTransform: 'uppercase' }}>
            Objectif
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {OBJECTIVES.map(o => (
              <button key={o.value} onClick={() => setObjective(o.value)} style={{
                padding: '10px 14px', borderRadius: 12, textAlign: 'left', fontSize: 12, fontWeight: 500,
                border: `1.5px solid ${objective === o.value ? C.purple + '80' : 'rgba(255,255,255,0.08)'}`,
                background: objective === o.value ? 'rgba(184,123,158,0.12)' : 'transparent',
                color: objective === o.value ? '#d9b8d0' : C.muted, cursor: 'pointer',
              }}>{o.label}</button>
            ))}
          </div>
        </div>

        {/* Type de média */}
        <div style={{ marginBottom: 24 }}>
          <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1.5, marginBottom: 8, textTransform: 'uppercase' }}>
            Type de stimulus
          </div>
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
            {TYPE_OPTS.map(opt => (
              <Pill
                key={String(opt.value)}
                active={forcedType === opt.value}
                onClick={() => setForcedType(opt.value)}
              >
                {opt.icon} {opt.label}
              </Pill>
            ))}
          </div>
        </div>

        {error && (
          <div style={{
            marginBottom: 14, padding: '10px 14px', borderRadius: 12, fontSize: 11,
            background: 'rgba(232,123,158,0.12)', border: '1px solid rgba(232,123,158,0.3)',
            color: '#E87B9E',
          }}>⚠ {error}</div>
        )}

        <button onClick={handleStart} disabled={loading} style={{
          width: '100%', padding: '14px', borderRadius: 16, border: 'none',
          background: loading
            ? 'rgba(255,255,255,0.05)'
            : 'linear-gradient(135deg, #B87B9E, #9A6B8E)',
          color: loading ? C.muted : 'white',
          fontSize: 14, fontWeight: 700,
          cursor: loading ? 'not-allowed' : 'pointer',
          boxShadow: loading ? 'none' : '0 6px 24px rgba(184,123,158,0.35)',
          transition: 'all .2s',
        }}>
          {loading ? '⏳ Démarrage…' : '→ Démarrer la session'}
        </button>
        <style>{`@keyframes nf-pulse{0%,100%{opacity:1}50%{opacity:.3}}`}</style>
      </div>
    </div>
  )

  // ════════════════════════════════════════════════════════════════════════════
  // ENDED
  // ════════════════════════════════════════════════════════════════════════════
  if (phase === 'ended') return (
    <div style={{
      height: '100%', display: 'flex', alignItems: 'center',
      justifyContent: 'center', padding: '20px',
    }}>
      <div style={{
        maxWidth: 460, width: '100%',
        background: C.card, border: `1px solid ${C.border}`,
        borderRadius: 20, padding: '32px 28px',
      }}>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>✅</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: C.text, marginBottom: 6 }}>
            Session terminée
          </div>
          <div style={{ fontSize: 12, color: C.muted }}>
            {history.length} stimulus · {history.filter(h => h.liked).length} appréciés ·{' '}
            {history.filter(h => h.skipped).length} passés
          </div>
        </div>

        {report?.rapport_ia && (
          <div style={{
            background: 'rgba(0,229,176,0.04)', border: '1px solid rgba(0,229,176,0.15)',
            borderRadius: 14, padding: '16px', fontSize: 12, color: '#8ab8a8',
            lineHeight: 1.8, marginBottom: 20,
          }}>
            {report.rapport_ia}
          </div>
        )}

        {/* Mini-historique */}
        {history.length > 0 && (
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1.5, marginBottom: 8, textTransform: 'uppercase' }}>
              Historique
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 160, overflowY: 'auto' }}>
              {history.map((h, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  padding: '5px 10px', borderRadius: 9,
                  background: 'rgba(255,255,255,0.02)', border: `1px solid ${C.border}`,
                  fontSize: 10, color: C.muted, opacity: h.skipped ? 0.5 : 1,
                }}>
                  <span style={{ fontSize: 12 }}>
                    {h.type === 'audio' ? '🎵' : h.type === 'image' ? '🖼️' : h.type === 'video' ? '🎬' : '🎮'}
                  </span>
                  <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {h.filename?.slice(0, 28) ?? h.type}
                  </span>
                  <span>{h.skipped ? '⏭' : h.liked ? '👍' : '👎'}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <button onClick={() => {
          setPhase('idle'); setHistory([]); setMedia(null)
          setReport(null); setError(null)
        }} style={{
          width: '100%', padding: '12px', borderRadius: 14,
          border: `1px solid ${C.border}`, background: 'transparent',
          color: C.text, fontSize: 13, fontWeight: 600, cursor: 'pointer',
        }}>
          ↺ Nouvelle session
        </button>
      </div>
    </div>
  )

  // ════════════════════════════════════════════════════════════════════════════
  // ACTIVE
  // ════════════════════════════════════════════════════════════════════════════
  return (
    <div style={{ display: 'flex', height: '100%', gap: 14, overflow: 'hidden' }}>

      {/* ── Zone stimulus ── */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0, overflow: 'hidden' }}>

        {/* Barre de contrôle */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0,
          marginBottom: 12, flexWrap: 'wrap',
        }}>
          {/* État EEG live (mis à jour à chaque epoch) */}
          <div style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '4px 12px', borderRadius: 20,
            background: `${meta.color}12`, border: `1px solid ${meta.color}30`,
          }}>
            <span style={{ fontSize: 13 }}>{meta.icon}</span>
            <span style={{ fontSize: 10, fontWeight: 700, color: meta.color, letterSpacing: 1 }}>
              {meta.label}
            </span>
            <div style={{
              width: 6, height: 6, borderRadius: '50%',
              background: meta.color, boxShadow: `0 0 6px ${meta.color}80`,
              animation: 'nf-pulse 2s ease-in-out infinite',
            }} />
          </div>

          {/* Sélecteur type */}
          {TYPE_OPTS.map(opt => (
            <Pill
              key={String(opt.value)}
              active={forcedType === opt.value}
              onClick={() => handleTypeChange(opt.value)}
            >
              {opt.icon}
            </Pill>
          ))}

          <div style={{ marginLeft: 'auto', display: 'flex', gap: 6, alignItems: 'center' }}>
            <span style={{ fontSize: 10, color: C.muted, fontFamily: "'Space Mono',monospace" }}>
              {history.length} stimulus
            </span>
            <ActionBtn
              onClick={handleEnd}
              bg="rgba(232,123,158,0.1)"
              color="#E87B9E"
            >⏹ Fin</ActionBtn>
          </div>
        </div>

        {/* Contenu */}
        <div style={{ flex: 1, overflowY: 'auto', minHeight: 0 }}>
          {loading ? (
            <div style={{
              height: '100%', display: 'flex', alignItems: 'center',
              justifyContent: 'center', color: C.muted, gap: 10,
            }}>
              <span style={{ fontSize: 18, animation: 'nf-pulse 1s infinite' }}>⏳</span>
              Chargement du stimulus…
            </div>
          ) : error ? (
            <div style={{
              margin: '20px', padding: '16px', borderRadius: 14, fontSize: 12,
              background: 'rgba(232,123,158,0.1)', border: '1px solid rgba(232,123,158,0.25)',
              color: '#E87B9E', textAlign: 'center',
            }}>
              ⚠ {error}
              <br />
              <button onClick={() => loadMedia(null, forcedType)} style={{
                marginTop: 10, padding: '6px 16px', borderRadius: 10, border: 'none',
                background: 'rgba(184,123,158,0.2)', color: C.purple, fontSize: 11,
                cursor: 'pointer', fontWeight: 600,
              }}>Réessayer</button>
            </div>
          ) : !media ? null : (
            <div>
              {/* Nom du fichier */}
              <div style={{
                fontSize: 9, color: C.muted, fontFamily: "'Space Mono',monospace",
                marginBottom: 10, letterSpacing: .5,
              }}>
                {media.type?.toUpperCase()} · {media.filename?.slice(0, 50)}
              </div>

              {media.type === 'audio' && (
                <AudioFeedback
                  src={media.cloudinary_url || media.url_cloudinary}
                  filename={media.filename}
                />
              )}
              {media.type === 'image' && (
                <ImageFeedback
                  src={media.cloudinary_url || media.url_cloudinary}
                  alt={media.filename}
                />
              )}
              {media.type === 'video' && (
                <VideoFeedback
                  src={media.cloudinary_url || media.url_cloudinary}
                  title={media.filename}
                />
              )}
              {media.type === 'game' && (
                <GameFeedback
                  game={media}
                  eegState={eegState}
                  onWin={r => console.log('[LiveNF] game win', r)}
                />
              )}

              {/* Justification IA */}
              <div style={{ marginTop: 10 }}>
                <FeedbackJustification
                  mediaId={media?.id}
                  type={media.type}
                  state={eegState}
                  userId="neurocap_live"
                />
              </div>
            </div>
          )}
        </div>

        {/* Contrôles feedback */}
        {!loading && media && (
          <div style={{
            flexShrink: 0, borderTop: '1px solid rgba(255,255,255,0.05)',
            paddingTop: 10, marginTop: 8,
          }}>
            {showFeed ? (
              <FeedbackSelector
                onSubmit={handleFeedback}
                onSkip={() => { setShowFeed(false); handleSkip() }}
              />
            ) : (
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                <ActionBtn onClick={() => loadMedia(null, forcedType)} bg="rgba(123,168,196,0.1)" color="#7BA8C4">
                  🔄 Autre
                </ActionBtn>
                <ActionBtn onClick={() => setShowFeed(true)} bg="rgba(0,229,176,0.1)" color="#00e5b0">
                  👍 Ça m'aide
                </ActionBtn>
                <ActionBtn onClick={() => handleFeedback(false, 'pas_bien', 2, 4)} bg="rgba(232,123,158,0.1)" color="#E87B9E">
                  👎 Pas adapté
                </ActionBtn>
                <ActionBtn onClick={handleSkip}>⏭</ActionBtn>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Mini-sidebar : historique session ── */}
      <div style={{
        width: 170, flexShrink: 0, display: 'flex', flexDirection: 'column',
        borderLeft: '1px solid rgba(255,255,255,0.05)', paddingLeft: 14,
        overflow: 'hidden',
      }}>
        <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1.5, marginBottom: 10, textTransform: 'uppercase' }}>
          Historique
        </div>
        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 5 }}>
          {history.length === 0 && (
            <div style={{ fontSize: 10, color: C.muted, fontStyle: 'italic' }}>Aucun stimulus</div>
          )}
          {[...history].reverse().map((h, i) => (
            <div key={i} style={{
              padding: '6px 8px', borderRadius: 9,
              background: 'rgba(255,255,255,0.02)', border: `1px solid ${C.border}`,
              opacity: h.skipped ? 0.5 : 1,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
                <span style={{ fontSize: 11 }}>
                  {h.type === 'audio' ? '🎵' : h.type === 'image' ? '🖼️' : h.type === 'video' ? '🎬' : '🎮'}
                </span>
                <span style={{ fontSize: 12 }}>
                  {h.skipped ? '⏭' : h.liked ? '👍' : '👎'}
                </span>
              </div>
              <div style={{
                fontSize: 9, color: C.muted, marginTop: 3,
                overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
              }}>
                {h.filename?.slice(0, 18) ?? h.type}
              </div>
            </div>
          ))}
        </div>

        {/* Bandes EEG live */}
        {Object.keys(features).some(k => k.startsWith('rel_')) && (
          <div style={{ marginTop: 14, borderTop: '1px solid rgba(255,255,255,0.05)', paddingTop: 12 }}>
            <div style={{ fontSize: 9, color: C.muted, letterSpacing: 1.5, marginBottom: 8, textTransform: 'uppercase' }}>
              EEG live
            </div>
            {[
              { key: 'rel_delta', label: 'δ', color: '#818cf8' },
              { key: 'rel_theta', label: 'θ', color: '#f59e0b' },
              { key: 'rel_alpha', label: 'α', color: '#10b981' },
              { key: 'rel_beta',  label: 'β', color: '#3b82f6' },
              { key: 'rel_gamma', label: 'γ', color: '#ef4444' },
            ].map(({ key, label, color }) => {
              const pct = Math.round((features[key] ?? 0) * 100)
              return (
                <div key={key} style={{ marginBottom: 5 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                    <span style={{ fontSize: 9, color, fontWeight: 700 }}>{label}</span>
                    <span style={{ fontSize: 9, color, fontFamily: "'Space Mono',monospace" }}>{pct}%</span>
                  </div>
                  <div style={{ height: 4, background: 'rgba(255,255,255,0.06)', borderRadius: 2, overflow: 'hidden' }}>
                    <div style={{
                      width: `${Math.min(pct, 100)}%`, height: '100%',
                      background: color, borderRadius: 2, transition: 'width .5s',
                    }} />
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      <style>{`@keyframes nf-pulse{0%,100%{opacity:1}50%{opacity:.3}}`}</style>
    </div>
  )
}
