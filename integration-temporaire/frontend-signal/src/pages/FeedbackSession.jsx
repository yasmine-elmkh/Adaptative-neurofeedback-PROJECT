/**
 * FeedbackSession.jsx — Session neurofeedback temps réel
 * Fixes : next/submit, forced_type, fallback Supabase
 * Ajouts : signal EEG waveform, sélecteur type média, bouton reload, guide IA dynamique
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import { useFeedbackEngine }  from '../hooks/useFeedbackEngine'
import BrainStateIndicator    from '../components/feedback/BrainStateIndicator'
import AudioFeedback          from '../components/feedback/AudioFeedback'
import ImageFeedback          from '../components/feedback/ImageFeedback'
import VideoFeedback          from '../components/feedback/VideoFeedback'
import GameFeedback           from '../components/feedback/GameFeedback'
import FeedbackSelector       from '../components/feedback/FeedbackSelector'
import FeedbackJustification  from '../components/feedback/FeedbackJustification'
import MiniSignalWidget       from '../components/feedback/MiniSignalWidget'

// ── Palette ───────────────────────────────────────────────────────────────────
const C = {
  bg: '#C5D3E8', card: 'rgba(247,243,250,0.45)',
  border: 'rgba(255,255,255,0.4)', border2: 'rgba(255,255,255,0.6)',
  text: '#2B2A4A', muted: '#9A8BAE',
  conc: '#7BC4A0', stress: '#E87B9E', uncert: '#C4A87B', purple: '#B87B9E',
  shadow: 'rgba(180,169,196,0.45)',
}

const STATE_COLOR = {
  stress: '#E87B9E', focus: '#7BA8C4', relax: '#7BC4A0',
  distracted: '#C4A87B', neutral: '#9A8BAE',
}

const MEDIA_CFG = {
  audio: { icon: '🎵', label: 'Audio thérapeutique',    color: C.conc   },
  image: { icon: '🖼️', label: 'Image apaisante',        color: C.purple },
  video: { icon: '🎬', label: 'Vidéo relaxante',        color: '#4da6ff' },
  game:  { icon: '🎮', label: 'Jeu cognitif adaptatif', color: C.uncert },
}

const TYPE_OPTIONS = [
  { value: null,    icon: '🔀', label: 'Auto'   },
  { value: 'audio', icon: '🎵', label: 'Audio'  },
  { value: 'image', icon: '🖼️', label: 'Image'  },
  { value: 'video', icon: '🎬', label: 'Vidéo'  },
  { value: 'game',  icon: '🎮', label: 'Jeu'    },
]

function fmtTime(s) {
  const m = Math.floor(s / 60)
  return `${m}:${String(s % 60).padStart(2, '0')}`
}

// ── Signal EEG synthétique animé ─────────────────────────────────────────────
function EEGWaveform({ features }) {
  const canvasRef = useRef(null)
  const animRef   = useRef(null)
  const featRef   = useRef(features)
  useEffect(() => { featRef.current = features }, [features])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const W = canvas.width, H = canvas.height
    const mid = H / 2
    let t = 0

    const draw = () => {
      t += 0.055
      const f  = featRef.current || {}
      const d  = f.rel_delta ?? 0.20
      const th = f.rel_theta ?? 0.15
      const a  = f.rel_alpha ?? 0.30
      const b  = f.rel_beta  ?? 0.25
      const g  = f.rel_gamma ?? 0.10

      ctx.clearRect(0, 0, W, H)

      // Grille légère
      ctx.strokeStyle = 'rgba(184,123,158,0.08)'
      ctx.lineWidth = 0.5
      for (let y = 0; y < H; y += 14) {
        ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke()
      }

      // Ligne de base
      ctx.strokeStyle = 'rgba(123,196,160,0.2)'
      ctx.lineWidth = 0.5
      ctx.beginPath(); ctx.moveTo(0, mid); ctx.lineTo(W, mid); ctx.stroke()

      // Onde composite colorée
      const grad = ctx.createLinearGradient(0, 0, W, 0)
      grad.addColorStop(0,   '#7BC4A0')
      grad.addColorStop(0.5, '#B87B9E')
      grad.addColorStop(1,   '#7BA8C4')
      ctx.strokeStyle = grad
      ctx.lineWidth = 1.8
      ctx.beginPath()

      for (let x = 0; x < W; x++) {
        const tx = t - x * 0.045
        const y  = mid
          + d  * 16 * Math.sin(0.28 * tx)
          + th * 11 * Math.sin(0.75 * tx)
          + a  * 20 * Math.sin(2.00 * tx)
          + b  * 10 * Math.sin(4.80 * tx)
          + g  *  5 * Math.sin(9.50 * tx)
        x === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)
      }
      ctx.stroke()
      animRef.current = requestAnimationFrame(draw)
    }
    draw()
    return () => cancelAnimationFrame(animRef.current)
  }, []) // tourne en continu, featRef mis à jour par-dessus

  return (
    <canvas
      ref={canvasRef}
      width={210} height={56}
      style={{
        width: '100%', height: 56, borderRadius: 8, display: 'block',
        background: 'rgba(43,42,74,0.05)', border: '1px solid rgba(255,255,255,0.3)',
      }}
    />
  )
}

// ── Stimuli intégrés ──────────────────────────────────────────────────────────
function BreathingGuide({ color }) {
  const phases = ['Inspirez', 'Retenez', 'Expirez', 'Retenez']
  const times  = [4000, 2000, 6000, 2000]
  const [idx, setIdx] = useState(0)
  const col = color || C.conc
  useEffect(() => {
    const t = setTimeout(() => setIdx(i => (i + 1) % phases.length), times[idx])
    return () => clearTimeout(t)
  }, [idx]) // eslint-disable-line
  const isExpand = idx === 0 || idx === 1
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:'100%', gap:32, userSelect:'none' }}>
      <style>{`@keyframes b-in{to{transform:scale(1.5);opacity:1}} @keyframes b-out{to{transform:scale(1);opacity:.6}}`}</style>
      <div style={{
        width:160, height:160, borderRadius:'50%',
        border:`2px solid ${col}40`, background:`${col}10`,
        display:'flex', alignItems:'center', justifyContent:'center',
        animation: isExpand ? `b-in ${times[idx]}ms ease-in-out forwards` : `b-out ${times[idx]}ms ease-in-out forwards`,
      }}>
        <div style={{ width:70, height:70, borderRadius:'50%', background:`${col}30` }} />
      </div>
      <div style={{ textAlign:'center' }}>
        <div style={{ fontSize:22, fontWeight:300, color:`${col}cc`, letterSpacing:1, marginBottom:8 }}>{phases[idx]}</div>
        <div style={{ fontSize:11, color:C.muted }}>Cohérence cardiaque · Réduction du stress</div>
      </div>
    </div>
  )
}

function FixationPoint({ color }) {
  const col = color || C.conc
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:'100%', gap:28, userSelect:'none' }}>
      <div style={{ position:'relative', display:'flex', alignItems:'center', justifyContent:'center' }}>
        <div style={{ width:12, height:12, borderRadius:'50%', background:col, boxShadow:`0 0 20px ${col}60` }} />
        <div style={{ position:'absolute', width:30, height:30, borderRadius:'50%', border:`1px solid ${col}30` }} />
        <div style={{ position:'absolute', width:60, height:60, borderRadius:'50%', border:`1px solid ${col}15` }} />
        <div style={{ position:'absolute', width:0, height:50, border:`1px solid ${col}15` }} />
        <div style={{ position:'absolute', width:50, height:0, border:`1px solid ${col}15` }} />
      </div>
      <div style={{ textAlign:'center' }}>
        <div style={{ fontSize:20, fontWeight:300, color:`${col}cc`, marginBottom:8 }}>Fixez ce point</div>
        <div style={{ fontSize:11, color:C.muted }}>Relâchez les tensions oculaires · Respirez normalement</div>
      </div>
    </div>
  )
}

function NeutralWaiting() {
  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', height:'100%', gap:20, userSelect:'none' }}>
      <style>{`@keyframes pulse-ring{0%{transform:scale(1);opacity:.6}100%{transform:scale(1.4);opacity:0}}`}</style>
      <div style={{ position:'relative', display:'flex', alignItems:'center', justifyContent:'center' }}>
        <div style={{ width:56, height:56, borderRadius:'50%', background:'rgba(255,255,255,.04)', border:`1px solid ${C.border2}`, display:'flex', alignItems:'center', justifyContent:'center', fontSize:26 }}>🧠</div>
        <div style={{ position:'absolute', width:80, height:80, borderRadius:'50%', border:`1px solid ${C.purple}30`, animation:'pulse-ring 2s ease-out infinite' }} />
      </div>
      <div style={{ textAlign:'center' }}>
        <div style={{ fontSize:16, color:C.muted, fontWeight:300 }}>Chargement du stimulus…</div>
        <div style={{ fontSize:11, color:'#2a3a4e', marginTop:6 }}>Thompson Sampling sélectionne le média optimal</div>
      </div>
    </div>
  )
}

// ── Informations sur les bandes EEG (ce que ça veut dire pour l'utilisateur) ──
const BAND_INFO = {
  rel_delta: { label:'δ Delta · 0.5–4 Hz',  color:'#818cf8', emoji:'😴', short:'Sommeil / fatigue', desc:'Ondes lentes dominantes pendant le sommeil profond. Un delta élevé en état d\'éveil signale souvent de la fatigue ou du bruit de signal.' },
  rel_theta: { label:'θ Theta · 4–8 Hz',    color:'#f59e0b', emoji:'💭', short:'Mémoire / rêverie',  desc:'Associé à la créativité, la méditation et l\'apprentissage. Élevé lors de la distraction ou d\'un état de demi-sommeil. Cible du neurofeedback TDAH.' },
  rel_alpha: { label:'α Alpha · 8–13 Hz',   color:'#10b981', emoji:'🧘', short:'Relaxation alerte',  desc:'Le marqueur clé du protocole NeuroCap. Alpha élevé (> 30 %) = état de relaxation alerte, idéal pour l\'apprentissage. C\'est ce que vous entraînez.' },
  rel_beta:  { label:'β Beta · 13–30 Hz',   color:'#3b82f6', emoji:'🧠', short:'Cognition / stress',  desc:'Attention et traitement cognitif actif. Beta très élevé (> 40 %) est associé au stress et à l\'anxiété. L\'indice stress = β/α.' },
  rel_gamma: { label:'γ Gamma · 30–40 Hz',  color:'#ef4444', emoji:'⚡', short:'Traitement haut niv.', desc:'Intégration sensorielle et conscience. Très sensible aux artefacts musculaires (EMG) — un pic isolé peut être un artéfact de clignement.' },
}

// Explications des 15 features originales
const FEATURES_15 = [
  { name: 'rel_delta / theta / alpha / beta / gamma', cat: 'Puissances relatives', desc: 'Proportion de chaque bande sur la puissance totale (PSD Welch). Invariantes au gain ADC.' },
  { name: 'engagement = β/(α+θ)', cat: 'Ratio cognitif', desc: 'Indice d\'implication mentale (Pope 1995). > 1.5 = forte concentration active.' },
  { name: 'stress_idx = β/α', cat: 'Ratio cognitif', desc: 'Rapport bêta/alpha. > 2 = stress actif. Seuil NeuroCap > 0.5 → déclenche la respiration guidée.' },
  { name: 'theta_alpha = θ/α', cat: 'Ratio cognitif', desc: 'Indicateur de somnolence et distraction. Discriminant p<0.001 entre concentration et stress (Salam 2026).' },
  { name: 'alpha_beta = α/β', cat: 'Ratio cognitif', desc: 'Rapport calme/activation. Élevé = état paisible, bas = alerte ou stress.' },
  { name: 'hjorth_activity', cat: 'Hjorth (1970)', desc: 'Variance du signal — énergie instantanée en µV². Correspond à la puissance brute.' },
  { name: 'hjorth_mobility', cat: 'Hjorth (1970)', desc: 'Fréquence caractéristique estimée. Racine du rapport des variances des dérivées.' },
  { name: 'hjorth_complexity', cat: 'Hjorth (1970)', desc: 'Irrégularité fréquentielle. Élevé = signal complexe (stress), bas = régulier (concentration).' },
  { name: 'spectral_entropy', cat: 'Complexité', desc: 'Entropie de Shannon sur le PSD normalisé. Signal sinusoïdal = 0, bruit blanc = 1. Bas en concentration.' },
  { name: 'sef95', cat: 'Complexité', desc: 'Fréquence sous laquelle se trouve 95 % de l\'énergie. Baisse quand alpha/theta dominent (relaxation).' },
  { name: 'rms_uv', cat: 'Amplitude', desc: 'Valeur RMS du signal en µV. Indicateur d\'amplitude globale. Normale Fp2 éveillé : 5–50 µV.' },
]

function BandsPanel({ features }) {
  const [activeBand, setActiveBand]   = useState(null)
  const [showGlossary, setShowGlossary] = useState(false)

  return (
    <div style={{ marginBottom:16 }}>
      <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8 }}>
        <Label>BANDES SPECTRALES</Label>
        <button
          onClick={() => setShowGlossary(g => !g)}
          style={{ fontSize:9, color:C.muted, background:'none', border:'none', cursor:'pointer', fontFamily:"'DM Mono',monospace", padding:0 }}
        >
          {showGlossary ? '▲ Fermer' : '? Aide'}
        </button>
      </div>

      {Object.entries(BAND_INFO).map(([key, info]) => {
        const pct = Math.round((features[key] ?? 0) * 100)
        const isActive = activeBand === key
        return (
          <div key={key} style={{ marginBottom:7, cursor:'pointer' }} onClick={() => setActiveBand(isActive ? null : key)}>
            <div style={{ display:'flex', justifyContent:'space-between', marginBottom:3, alignItems:'center' }}>
              <span style={{ fontSize:9, fontFamily:"'DM Mono',monospace", color:info.color, letterSpacing:1, textTransform:'uppercase' }}>
                {info.emoji} {key.replace('rel_','')} <span style={{ color:C.muted, fontSize:8, fontStyle:'italic', fontFamily:'sans-serif', textTransform:'none' }}>{info.short}</span>
              </span>
              <span style={{ fontSize:9, fontFamily:"'DM Mono',monospace", fontWeight:700, color:info.color }}>{pct}%</span>
            </div>
            <div style={{ height:5, background:'rgba(255,255,255,0.4)', borderRadius:3, overflow:'hidden' }}>
              <div style={{ width:`${Math.min(pct,100)}%`, height:'100%', background:info.color, borderRadius:3, transition:'width .4s' }} />
            </div>
            {isActive && (
              <div style={{ marginTop:5, padding:'6px 8px', borderRadius:7, background:`${info.color}14`, border:`1px solid ${info.color}35`, fontSize:10, color:C.text, lineHeight:1.55 }}>
                <b style={{ color:info.color }}>{info.label}</b><br />{info.desc}
              </div>
            )}
          </div>
        )
      })}

      {showGlossary && (
        <div style={{ marginTop:8, padding:'8px 10px', borderRadius:10, background:'rgba(43,42,74,0.06)', border:'1px solid rgba(255,255,255,0.3)' }}>
          <div style={{ fontSize:9, color:C.muted, fontFamily:"'DM Mono',monospace", letterSpacing:1, marginBottom:6 }}>15 FEATURES EEG (pipeline v7)</div>
          {FEATURES_15.map((f, i) => (
            <div key={i} style={{ padding:'5px 0', borderBottom:'1px solid rgba(255,255,255,0.2)', fontSize:9, color:C.text, lineHeight:1.5 }}>
              <b style={{ color:C.purple }}>{f.name}</b>
              <span style={{ color:C.muted }}> · {f.cat}</span><br />
              {f.desc}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// ── Composant principal ───────────────────────────────────────────────────────
export default function FeedbackSession({ sessionId, eegState, features, onEnd, onBack }) {
  const [currentMedia, setCurrentMedia] = useState(null)
  const [phase,        setPhase]        = useState('loading')
  const [history,      setHistory]      = useState([])
  const [duration,     setDuration]     = useState(0)
  const [ending,       setEnding]       = useState(false)
  const [error,        setError]        = useState(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [forcedType,   setForcedType]   = useState(null) // type de média forcé par l'utilisateur

  const timerRef   = useRef(null)
  const mountedRef = useRef(true)

  const { recommend, submitFeedback, nextItem, skipItem, endSession } = useFeedbackEngine()

  const stateColor = STATE_COLOR[eegState] ?? C.muted
  const cfg = currentMedia ? (MEDIA_CFG[currentMedia.type] ?? MEDIA_CFG.audio) : null

  // Timer
  useEffect(() => {
    timerRef.current = setInterval(() => setDuration(d => d + 1), 1000)
    return () => clearInterval(timerRef.current)
  }, [])

  // Première recommandation
  useEffect(() => {
    mountedRef.current = true
    loadFirst(forcedType)
    return () => { mountedRef.current = false }
  }, []) // eslint-disable-line

  const loadFirst = useCallback(async (type = null) => {
    setPhase('loading'); setError(null)
    try {
      const media = await recommend(sessionId, eegState, features, type)
      if (!mountedRef.current) return
      if (media) {
        setCurrentMedia(media); setPhase('playing')
      } else {
        setError('Aucun média disponible pour cet état EEG.'); setPhase('playing')
      }
    } catch (e) {
      if (!mountedRef.current) return
      setError(e.message); setPhase('playing')
    }
  }, [sessionId, eegState, features, recommend])

  // Recharger une autre recommandation du même type
  const handleReload = useCallback(() => {
    loadFirst(forcedType)
  }, [loadFirst, forcedType])

  // Changer le type de média forcé
  const handleTypeChange = useCallback((type) => {
    setForcedType(type)
    loadFirst(type)
  }, [loadFirst])

  const handleFeedback = useCallback(async (liked, ressenti, noteConc, noteStress) => {
    setShowFeedback(false)
    try {
      // BUG FIX: on passe currentMedia (objet complet) et non pas mediaId (string)
      await submitFeedback(sessionId, currentMedia, liked, ressenti, noteConc, noteStress)
      setHistory(h => [...h, { ...currentMedia, liked, skipped: false }])
      setPhase('loading')
      // BUG FIX: on passe eegState et forcedType à nextItem
      const next = await nextItem(sessionId, eegState, forcedType)
      if (!mountedRef.current) return
      // BUG FIX: on vérifie !!next et non next?.action === 'play'
      if (next) {
        setCurrentMedia(next); setPhase('playing')
      } else {
        // Fallback : relancer une recommandation via recommend
        await loadFirst(forcedType)
      }
    } catch (e) {
      if (!mountedRef.current) return
      setError(e.message); setPhase('playing')
    }
  }, [sessionId, currentMedia, eegState, forcedType, submitFeedback, nextItem, loadFirst])

  const handleSkip = useCallback(async () => {
    setHistory(h => currentMedia ? [...h, { ...currentMedia, skipped: true }] : h)
    setShowFeedback(false)
    setPhase('loading')
    try {
      // BUG FIX: on passe eegState et forcedType
      const next = await skipItem(sessionId, eegState, forcedType)
      if (!mountedRef.current) return
      if (next) {
        setCurrentMedia(next); setPhase('playing')
      } else {
        await loadFirst(forcedType)
      }
    } catch (e) {
      if (!mountedRef.current) return
      setError(e.message); setPhase('playing')
    }
  }, [sessionId, currentMedia, eegState, forcedType, skipItem, loadFirst])

  const handleEnd = useCallback(async () => {
    setEnding(true)
    clearInterval(timerRef.current)
    const lastHistory = currentMedia ? [...history, { ...currentMedia, ended: true }] : history
    try {
      const report = await endSession(sessionId)
      onEnd({ ...(report || {}), history: lastHistory, duration_min: Math.round(duration / 60) })
    } catch {
      onEnd({ history: lastHistory, duration_min: Math.round(duration / 60), items_played: lastHistory.length })
    }
  }, [sessionId, currentMedia, history, duration, endSession, onEnd])

  return (
    <div style={{
      minHeight: '100vh', background: C.bg,
      fontFamily: "'DM Sans', system-ui, sans-serif",
      display: 'flex', flexDirection: 'column',
    }}>

      {/* ── Header ── */}
      <div style={{
        background: 'rgba(197,211,232,0.85)', borderBottom: '1px solid rgba(255,255,255,0.4)',
        padding: '0 24px', height: 57,
        display: 'flex', alignItems: 'center', gap: 14,
        position: 'sticky', top: 0, zIndex: 100, flexShrink: 0,
        backdropFilter: 'blur(20px)', boxShadow: `0 2px 20px ${C.shadow}`,
      }}>
        <div style={{ display:'flex', alignItems:'center', gap:10 }}>
          <div style={{
            width:28, height:28, borderRadius:'50%',
            background:`linear-gradient(135deg, ${C.purple}, #7BA8C4)`,
            display:'flex', alignItems:'center', justifyContent:'center', fontSize:14, color:'white',
          }}>🧠</div>
          <span style={{ fontSize:15, fontWeight:700, color:C.text }}>NeuroCap</span>
        </div>

        <div style={{ display:'flex', alignItems:'center', gap:6 }}>
          <div style={{
            width:7, height:7, borderRadius:'50%',
            background: ending ? C.stress : C.conc,
            boxShadow: `0 0 8px ${ending ? C.stress : C.conc}80`,
          }} />
          <span style={{ fontSize:10, color:C.muted, fontFamily:"'DM Mono',monospace" }}>
            {ending ? 'Fin de séance…' : 'Séance active'}
          </span>
        </div>

        <div style={{
          fontSize:13, fontFamily:"'DM Mono',monospace", color:C.muted,
          padding:'4px 12px', borderRadius:20, background:'rgba(255,255,255,0.35)',
          border:`1px solid ${C.border}`, letterSpacing:1,
        }}>
          {fmtTime(duration)}
        </div>

        <div style={{ fontSize:11, color:C.muted, fontFamily:"'DM Mono',monospace" }}>
          {history.length} stimulus{history.length !== 1 ? 's' : ''}
        </div>

        <div style={{ flex:1 }} />

        <button
          onClick={handleEnd} disabled={ending}
          style={{
            padding:'7px 16px', borderRadius:20,
            background: ending ? 'rgba(255,255,255,0.2)' : 'rgba(232,123,158,0.15)',
            border:`1.5px solid ${ending ? C.border : 'rgba(232,123,158,0.4)'}`,
            color: ending ? C.muted : '#8c4a6a',
            fontSize:12, fontWeight:700, cursor: ending ? 'not-allowed' : 'pointer',
          }}
        >
          {ending ? '■ Fin en cours…' : '⏹ Terminer la séance'}
        </button>
      </div>

      {/* ── Corps ── */}
      <div style={{ display:'flex', flex:1, overflow:'hidden' }}>

        {/* ── Sidebar EEG ── */}
        <aside style={{
          width:242, flexShrink:0,
          borderRight:`1px solid rgba(255,255,255,0.4)`,
          padding:'20px 14px', overflowY:'auto',
          background:'rgba(197,211,232,0.3)',
        }}>

          {/* État EEG */}
          <div style={{ marginBottom:14 }}>
            <Label>ÉTAT EEG TEMPS RÉEL</Label>
            <BrainStateIndicator state={eegState} />
          </div>

          {/* Signal EEG temps réel — WebSocket direct, latence < 50 ms */}
          <div style={{ marginBottom:16 }}>
            <Label>SIGNAL EEG · TEMPS RÉEL</Label>
            <MiniSignalWidget wsUrl="ws://localhost:8765/ws" />
          </div>

          {/* Bandes spectrales + explications utilisateur */}
          {features && Object.keys(features).some(k => k.startsWith('rel_')) && (
            <BandsPanel features={features} />
          )}

          {/* Métriques */}
          {features?.stress_idx != null && (
            <div style={{ marginBottom:16 }}>
              <Label>MÉTRIQUES</Label>
              {[
                { label:'Stress index', value: features.stress_idx?.toFixed(2) },
                { label:'Engagement',   value: features.engagement?.toFixed(2) },
                { label:'α/β ratio',    value: features.alpha_beta?.toFixed(2) },
              ].map(({ label, value }) => (
                <div key={label} style={{ display:'flex', justifyContent:'space-between', padding:'4px 0', borderBottom:`1px solid rgba(255,255,255,0.3)`, fontSize:10 }}>
                  <span style={{ color:C.muted }}>{label}</span>
                  <span style={{ fontFamily:"'DM Mono',monospace", color:C.text, fontWeight:600 }}>{value ?? '—'}</span>
                </div>
              ))}
            </div>
          )}

          {/* Historique */}
          {history.length > 0 && (
            <div>
              <Label>HISTORIQUE</Label>
              <div style={{ display:'flex', flexDirection:'column', gap:5 }}>
                {history.slice(-5).map((h, i) => {
                  const hcfg = MEDIA_CFG[h.type] ?? MEDIA_CFG.audio
                  return (
                    <div key={i} style={{
                      display:'flex', alignItems:'center', gap:7,
                      padding:'5px 9px', borderRadius:9,
                      background:'rgba(255,255,255,0.35)', border:'1px solid rgba(255,255,255,0.4)',
                      opacity: h.skipped ? 0.55 : 1,
                    }}>
                      <span style={{ fontSize:13 }}>{hcfg.icon}</span>
                      <span style={{ fontSize:9, color:C.text, flex:1, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', fontFamily:"'DM Mono',monospace" }}>
                        {h.filename?.slice(0, 14) ?? h.type}
                      </span>
                      <span style={{ fontSize:12, color: h.skipped ? C.muted : h.liked ? C.conc : C.stress }}>
                        {h.skipped ? '⏭' : h.liked === true ? '👍' : '👎'}
                      </span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </aside>

        {/* ── Zone stimulus principale ── */}
        <main style={{ flex:1, display:'flex', flexDirection:'column', overflow:'hidden' }}>

          {/* Sélecteur de type de média */}
          <div style={{
            display:'flex', alignItems:'center', gap:6, padding:'10px 20px 0',
            flexShrink:0,
          }}>
            <span style={{ fontSize:10, color:C.muted, fontFamily:"'DM Mono',monospace", letterSpacing:1, marginRight:4 }}>TYPE :</span>
            {TYPE_OPTIONS.map(opt => (
              <button
                key={String(opt.value)}
                onClick={() => handleTypeChange(opt.value)}
                disabled={phase === 'loading'}
                style={{
                  padding:'4px 10px', borderRadius:20, fontSize:11, fontWeight:600,
                  border:`1.5px solid ${forcedType === opt.value ? C.purple : 'rgba(255,255,255,0.5)'}`,
                  background: forcedType === opt.value ? `rgba(184,123,158,0.2)` : 'rgba(255,255,255,0.3)',
                  color: forcedType === opt.value ? C.purple : C.muted,
                  cursor: phase === 'loading' ? 'not-allowed' : 'pointer',
                  transition:'all .15s',
                }}
              >
                {opt.icon} {opt.label}
              </button>
            ))}
          </div>

          {/* Stimulus */}
          <div style={{ flex:1, display:'flex', alignItems:'center', justifyContent:'center', padding:'16px 24px', overflow:'hidden' }}>
            {phase === 'loading' ? (
              <NeutralWaiting />
            ) : phase === 'ended' ? (
              <div style={{ textAlign:'center' }}>
                <div style={{ fontSize:48, marginBottom:16 }}>✅</div>
                <div style={{ fontSize:18, fontWeight:700, color:C.text }}>Séance terminée</div>
                <div style={{ fontSize:12, color:C.muted, marginTop:8 }}>Génération du rapport en cours…</div>
              </div>
            ) : !currentMedia ? (
              eegState === 'stress'
                ? <BreathingGuide color={stateColor} />
                : <FixationPoint color={stateColor} />
            ) : (
              <div style={{ width:'100%', maxWidth:660, maxHeight:'62vh' }}>
                {currentMedia.type === 'audio' && (
                  <AudioFeedback
                    src={currentMedia.cloudinary_url || currentMedia.url_cloudinary}
                    filename={currentMedia.filename}
                  />
                )}
                {currentMedia.type === 'image' && (
                  <ImageFeedback
                    src={currentMedia.cloudinary_url || currentMedia.url_cloudinary}
                    alt={currentMedia.filename}
                  />
                )}
                {currentMedia.type === 'video' && (
                  <VideoFeedback
                    src={currentMedia.cloudinary_url || currentMedia.url_cloudinary}
                    title={currentMedia.filename}
                  />
                )}
                {currentMedia.type === 'game' && (
                  <GameFeedback game={currentMedia} eegState={eegState} onWin={(r) => console.log('[Game] win', r)} />
                )}
              </div>
            )}
          </div>

          {/* Guide IA dynamique */}
          {currentMedia && !showFeedback && (
            <div style={{ padding:'0 20px 8px', flexShrink:0 }}>
              <FeedbackJustification
                mediaId={currentMedia?.id}
                type={currentMedia.type}
                state={eegState}
                userId="anonymous"
              />
            </div>
          )}

          {/* Barre de contrôle */}
          <div style={{
            borderTop:'1px solid rgba(255,255,255,0.4)', flexShrink:0,
            padding:'10px 20px', background:'rgba(197,211,232,0.6)',
            backdropFilter:'blur(10px)',
          }}>
            {error && (
              <div style={{ marginBottom:8, padding:'7px 12px', background:'rgba(232,123,158,0.15)', border:'1px solid rgba(232,123,158,0.4)', borderRadius:12, fontSize:11, color:'#8c4a6a', fontFamily:"'DM Mono',monospace" }}>
                ⚠ {error}
              </div>
            )}

            {showFeedback ? (
              <FeedbackSelector
                onSubmit={handleFeedback}
                onSkip={() => { setShowFeedback(false); handleSkip() }}
              />
            ) : (
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:10 }}>
                {/* Info média */}
                {cfg && currentMedia && (
                  <div style={{ display:'flex', alignItems:'center', gap:8, flex:1, overflow:'hidden' }}>
                    <span style={{ fontSize:18, flexShrink:0 }}>{cfg.icon}</span>
                    <div style={{ overflow:'hidden' }}>
                      <div style={{ fontSize:10, color:cfg.color, fontFamily:"'Space Mono',monospace", letterSpacing:.5 }}>
                        {cfg.label.toUpperCase()}
                      </div>
                      <div style={{ fontSize:11, color:C.muted, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>
                        {currentMedia.filename ?? '—'}
                      </div>
                    </div>
                  </div>
                )}

                {/* Boutons */}
                <div style={{ display:'flex', gap:7, flexShrink:0 }}>
                  {/* Recharger une autre recommandation */}
                  <button
                    onClick={handleReload}
                    disabled={phase === 'loading'}
                    title="Obtenir une autre recommandation"
                    style={btnStyle('rgba(123,168,196,.12)', 'rgba(123,168,196,.4)', '#4da6ff', phase === 'loading')}
                  >
                    🔄 Autre
                  </button>
                  <button
                    onClick={() => setShowFeedback(true)}
                    disabled={phase === 'loading' || !currentMedia}
                    style={btnStyle('rgba(0,229,176,.1)', 'rgba(0,229,176,.3)', C.conc, phase === 'loading')}
                  >
                    👍 Ça m'aide
                  </button>
                  <button
                    onClick={() => handleFeedback(false, 'pas_bien', 2, 4)}
                    disabled={phase === 'loading' || !currentMedia}
                    style={btnStyle('rgba(255,77,109,.08)', 'rgba(255,77,109,.25)', C.stress, phase === 'loading')}
                  >
                    👎 Pas adapté
                  </button>
                  <button
                    onClick={handleSkip}
                    disabled={phase === 'loading'}
                    title="Passer ce stimulus"
                    style={btnStyle('rgba(255,255,255,.04)', C.border2, C.muted, phase === 'loading')}
                  >
                    ⏭
                  </button>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

// ── Helpers UI ────────────────────────────────────────────────────────────────
function Label({ children }) {
  return (
    <div style={{
      fontSize:9, fontWeight:700, letterSpacing:2.5, marginBottom:9,
      color:C.muted, fontFamily:"'DM Mono',monospace", textTransform:'uppercase',
    }}>
      {children}
    </div>
  )
}

function btnStyle(bg, border, color, disabled) {
  return {
    padding:'8px 14px', borderRadius:20,
    background: disabled ? 'rgba(255,255,255,0.2)' : bg,
    border:`1.5px solid ${disabled ? 'rgba(255,255,255,0.3)' : border}`,
    color: disabled ? C.muted : color,
    fontSize:12, fontWeight:700,
    cursor: disabled ? 'not-allowed' : 'pointer',
    transition:'all .15s',
  }
}
