// ProtocolSession.jsx — Runner Protocole Neurofeedback 15 séances (Mou et al., 2024)
// Fonctionne en mode LIVE (features prop) et mode CSV (analysisData prop).
import { useState, useEffect, useRef, useCallback } from 'react'
import axios from 'axios'

const API = '/api/protocol'

// ── Constantes (mirroir backend) ────────────────────────────────────────────
const N_BLOCS          = 5
const BLOC_S           = 180   // 3 min
const BASELINE_S       = 120   // 2 min
const IAPF_S           = 60    // 1 min
const INTERBLOC_S      = 20
const REST_FINAL_S     = 180   // 3 min
const PALIER_LABELS    = { P1:'Palier 1 (85-90%)', P2:'Palier 2 (95-110%)', P3:'Palier 3 (110-125%)', P4:'Palier 4 (125-140%)' }

// Questionnaire
const PRE_Q  = [
  { key:'mood',    label:'Humeur générale',    opts:['Très bonne','Bonne','Neutre','Mauvaise','Très mauvaise'] },
  { key:'energy',  label:'Niveau d\'énergie',  opts:['Très élevé','Élevé','Moyen','Bas','Très bas'] },
  { key:'sleep',   label:'Qualité du sommeil', opts:['Excellente','Bonne','Moyenne','Mauvaise','Très mauvaise'] },
  { key:'anxiety', label:'Niveau d\'anxiété',  opts:['Nul','Faible','Modéré','Élevé','Très élevé'] },
]
const POST_Q = [
  { key:'experience', label:'Ressenti général de la séance', opts:['Très positif','Positif','Neutre','Négatif','Très négatif'] },
  { key:'fatigue',    label:'Fatigue ressentie',              opts:['Aucune','Légère','Modérée','Élevée','Épuisante'] },
  { key:'focus_q',   label:'Facilité à se concentrer',       opts:['Très facile','Facile','Moyen','Difficile','Impossible'] },
]

// ── Palette sombre ────────────────────────────────────────────────────────────
const C = {
  bg:     '#07090f',
  card:   '#0b0f1a',
  border: 'rgba(255,255,255,.06)',
  text:   '#c9d8e8',
  muted:  '#4a5a6e',
  accent: '#00e5b0',
  warn:   '#f5a623',
  danger: '#ff4d6d',
  alpha:  '#a78bfa',  // violet pour alpha
}

function fmt(s) {
  const m = Math.floor(s / 60), sec = s % 60
  return `${String(m).padStart(2,'0')}:${String(sec).padStart(2,'0')}`
}

// ── Barre de progression alpha ────────────────────────────────────────────────
function AlphaBar({ value, threshold, label }) {
  const pct   = Math.min(100, (value / Math.max(threshold * 1.5, 0.01)) * 100)
  const above = value >= threshold
  return (
    <div>
      <div style={{ display:'flex', justifyContent:'space-between', marginBottom:4 }}>
        <span style={{ fontSize:10, color:C.muted }}>{label}</span>
        <span style={{ fontSize:10, fontFamily:'monospace', color: above ? C.accent : C.warn }}>
          {value.toFixed(3)} {above ? '▲ SUCCÈS' : '▼ sous seuil'}
        </span>
      </div>
      <div style={{ height:8, borderRadius:4, background:'rgba(255,255,255,.06)', position:'relative', overflow:'hidden' }}>
        <div style={{ width:`${pct}%`, height:'100%', borderRadius:4, transition:'width .3s',
                      background: above
                        ? 'linear-gradient(90deg,#00e5b0,#7bffdf)'
                        : 'linear-gradient(90deg,#f5a623,#ffcc44)' }} />
        {/* Marqueur seuil */}
        <div style={{
          position:'absolute', top:0, bottom:0, left:`${(threshold / Math.max(threshold*1.5,0.01))*100}%`,
          width:2, background:'rgba(167,139,250,.8)',
        }} />
      </div>
      <div style={{ fontSize:9, color:C.alpha, marginTop:2 }}>Seuil : {threshold.toFixed(3)}</div>
    </div>
  )
}

// ── Carte de phase (timer + consigne) ─────────────────────────────────────────
function PhaseCard({ phase, countdown, children }) {
  const phaseConfig = {
    baseline:   { label:'BASELINE', color:'#7ba8c4', icon:'👁‍🗨', consigne:'Fermez les yeux et respirez normalement.' },
    iapf:       { label:'IAPF',    color:'#7bc4a0', icon:'👀', consigne:'Ouvrez les yeux, fixez un point devant vous.' },
    bloc:       { label:'BLOC',    color:C.accent,  icon:'🧠', consigne:'Essayez d\'augmenter votre activité alpha.' },
    interbloc:  { label:'PAUSE',   color:C.warn,    icon:'⏸',  consigne:'Reposez-vous, détendez-vous.' },
    rest_final: { label:'REPOS',   color:'#7ba8c4', icon:'🌿', consigne:'Yeux fermés. Repos complet.' },
  }
  const cfg = phaseConfig[phase] || { label: phase.toUpperCase(), color:C.muted, icon:'•', consigne:'' }

  return (
    <div style={{
      background: C.card, border: `1px solid ${cfg.color}30`,
      borderRadius:16, padding:'20px 24px', textAlign:'center',
    }}>
      <div style={{ fontSize:32, marginBottom:8 }}>{cfg.icon}</div>
      <div style={{ fontSize:10, fontWeight:700, letterSpacing:2, color:cfg.color,
                    textTransform:'uppercase', marginBottom:6 }}>{cfg.label}</div>
      <div style={{ fontFamily:'monospace', fontSize:48, fontWeight:700,
                    color:cfg.color, letterSpacing:4, marginBottom:10 }}>
        {fmt(countdown)}
      </div>
      <div style={{ fontSize:12, color:C.muted, marginBottom:12 }}>{cfg.consigne}</div>
      {children}
    </div>
  )
}

// ── Questionnaire ─────────────────────────────────────────────────────────────
function Questionnaire({ questions, onSubmit, title }) {
  const [answers, setAnswers] = useState({})
  const set = (k, v) => setAnswers(p => ({ ...p, [k]: v }))
  const done = questions.every(q => answers[q.key] !== undefined)

  return (
    <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:16, padding:'24px 28px' }}>
      <div style={{ fontSize:13, fontWeight:700, color:C.text, marginBottom:18 }}>{title}</div>
      {questions.map(q => (
        <div key={q.key} style={{ marginBottom:16 }}>
          <div style={{ fontSize:11, color:C.muted, marginBottom:6 }}>{q.label}</div>
          <div style={{ display:'flex', gap:6, flexWrap:'wrap' }}>
            {q.opts.map((o, i) => (
              <button key={o} onClick={() => set(q.key, i)}
                style={{
                  padding:'6px 12px', borderRadius:8, fontSize:11, cursor:'pointer',
                  background: answers[q.key]===i ? 'rgba(0,229,176,.15)' : 'rgba(255,255,255,.03)',
                  border: `1px solid ${answers[q.key]===i ? 'rgba(0,229,176,.4)' : C.border}`,
                  color: answers[q.key]===i ? C.accent : C.muted,
                }}>
                {o}
              </button>
            ))}
          </div>
        </div>
      ))}
      <button
        disabled={!done}
        onClick={() => onSubmit(answers)}
        style={{
          marginTop:12, width:'100%', padding:12, borderRadius:12,
          background: done ? C.accent : 'rgba(255,255,255,.05)',
          border:'none', color: done ? '#000' : C.muted,
          fontWeight:700, fontSize:13, cursor: done ? 'pointer' : 'not-allowed',
        }}>
        Valider →
      </button>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// COMPOSANT PRINCIPAL
// ═══════════════════════════════════════════════════════════════════════════════
export default function ProtocolSession({ features, bands, eegState, analysisData }) {
  // features = objet features EEG live (époque)
  // bands    = { alpha, beta, ... } puissances relatives live
  // analysisData = résultat d'une analyse CSV (mode offline)

  const [phase,       setPhase]      = useState('setup')    // setup|pre_q|baseline|iapf|bloc|interbloc|rest_final|post_q|report
  const [userId,      setUserId]     = useState('neurocap_user')
  const [sessionN,    setSessionN]   = useState(1)
  const [program,     setProgram]    = useState(null)
  const [countdown,   setCountdown]  = useState(0)
  const [blocN,       setBlocN]      = useState(1)
  const [seuil,       setSeuil]      = useState(0)
  const [seuilInitial,setSeuilInitial] = useState(0)

  // Buffers de collecte
  const alphaBaselineRef  = useRef([])  // valeurs alpha pendant baseline
  const blocSamplesRef    = useRef({ above:0, total:0, alphas:[] })
  const blocResultsRef    = useRef([])
  const timerRef          = useRef(null)
  const preAnswersRef     = useRef({})
  const postAnswersRef    = useRef({})
  const [loadingApi, setLoadingApi] = useState(false)
  const [apiError,   setApiError]   = useState('')
  const [report,     setReport]     = useState(null)

  // Alpha live : priorité features.rel_alpha, sinon bands.alpha
  const liveAlpha = features?.rel_alpha ?? bands?.alpha ?? 0

  // ── Sync alpha dans les blocs ──
  useEffect(() => {
    if (phase === 'baseline') {
      alphaBaselineRef.current.push(liveAlpha)
    } else if (phase === 'bloc') {
      blocSamplesRef.current.total++
      if (liveAlpha >= seuil) blocSamplesRef.current.above++
      blocSamplesRef.current.alphas.push(liveAlpha)
    }
  }, [features, liveAlpha, phase, seuil])

  // ── Chargement programme utilisateur ──
  const loadProgram = useCallback(async (uid) => {
    try {
      const { data } = await axios.get(`${API}/user/${uid}`)
      setProgram(data)
      setSessionN(data.next_session <= 15 ? data.next_session : 15)
    } catch {
      setProgram(null)
    }
  }, [])

  // ── Timer countdown ──────────────────────────────────────────────────────────
  const startTimer = useCallback((seconds, onEnd) => {
    setCountdown(seconds)
    clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(timerRef.current)
          onEnd()
          return 0
        }
        return prev - 1
      })
    }, 1000)
  }, [])

  useEffect(() => () => clearInterval(timerRef.current), [])

  // ── Transitions de phase ──────────────────────────────────────────────────────
  const goSetup        = ()   => { clearInterval(timerRef.current); setPhase('setup') }
  const goPreQ         = ()   => setPhase('pre_q')
  const goBaseline     = ()   => {
    alphaBaselineRef.current = []
    setPhase('baseline')
    startTimer(BASELINE_S, goIapf)
  }
  const goIapf         = ()   => {
    setPhase('iapf')
    startTimer(IAPF_S, startProtocol)
  }
  const startProtocol  = useCallback(async () => {
    // Calcul seuil depuis baseline
    const arr = alphaBaselineRef.current
    const meanBaseline = arr.length > 0 ? arr.reduce((a,b)=>a+b,0)/arr.length : 0.2
    setLoadingApi(true); setApiError('')
    try {
      const { data } = await axios.post(`${API}/session/baseline`, {
        user_id: userId,
        session_n: sessionN,
        p_alpha_baseline: meanBaseline,
        iapf_hz: null,
      })
      const s = data.seuil_initial
      setSeuil(s); setSeuilInitial(s)
      blocResultsRef.current = []
      setBlocN(1)
      setPhase('bloc')
      blocSamplesRef.current = { above:0, total:0, alphas:[] }
      startTimer(BLOC_S, () => endBloc(1, s))
    } catch(e) {
      setApiError(e.response?.data?.detail || e.message)
    } finally { setLoadingApi(false) }
  }, [userId, sessionN, startTimer])

  const endBloc = useCallback(async (bn, currentSeuil) => {
    const { above, total, alphas } = blocSamplesRef.current
    const meanAlpha = alphas.length > 0 ? alphas.reduce((a,b)=>a+b,0)/alphas.length : null
    setLoadingApi(true)
    try {
      const { data } = await axios.post(`${API}/bloc/end`, {
        user_id:        userId,
        session_n:      sessionN,
        bloc_n:         bn,
        samples_above:  above,
        total_samples:  total,
        current_seuil:  currentSeuil,
        mean_alpha:     meanAlpha,
      })
      blocResultsRef.current.push({ ...data, bloc_n: bn })
      const nextSeuil = data.seuil_next
      setSeuil(nextSeuil)

      if (data.is_last_bloc) {
        setPhase('rest_final')
        startTimer(REST_FINAL_S, goPostQ)
      } else {
        const nextBn = bn + 1
        setBlocN(nextBn)
        setPhase('interbloc')
        blocSamplesRef.current = { above:0, total:0, alphas:[] }
        startTimer(INTERBLOC_S, () => {
          setPhase('bloc')
          startTimer(BLOC_S, () => endBloc(nextBn, nextSeuil))
        })
      }
    } catch(e) {
      setApiError(e.response?.data?.detail || e.message)
    } finally { setLoadingApi(false) }
  }, [userId, sessionN, startTimer])

  const goPostQ  = () => setPhase('post_q')

  const endSession = useCallback(async (postAnswers) => {
    postAnswersRef.current = postAnswers
    setLoadingApi(true); setApiError('')
    try {
      const { data } = await axios.post(`${API}/session/end`, {
        user_id:   userId,
        session_n: sessionN,
        notes:     JSON.stringify({ pre: preAnswersRef.current, post: postAnswers }),
      })
      setReport(data)
      setPhase('report')
    } catch(e) {
      setApiError(e.response?.data?.detail || e.message)
    } finally { setLoadingApi(false) }
  }, [userId, sessionN])

  // ── RENDER ────────────────────────────────────────────────────────────────────

  // ── Setup ─────────────────────────────────────────────────────────────────────
  if (phase === 'setup') {
    return (
      <div style={{ fontFamily:"'Outfit',sans-serif", color:C.text, padding:8 }}>
        <div style={{ maxWidth:520, margin:'0 auto' }}>
          <div style={{ textAlign:'center', marginBottom:28 }}>
            <div style={{ fontSize:22, fontWeight:700, color:C.accent, marginBottom:6 }}>
              Protocole 15 Séances
            </div>
            <div style={{ fontSize:11, color:C.muted, lineHeight:1.7 }}>
              Neurofeedback adaptatif alpha — Mou et al. (2024)<br/>
              5 blocs × 3 min · Seuil adaptatif inter-blocs
            </div>
          </div>

          {/* Info paliers */}
          <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:14, padding:'16px 20px', marginBottom:20 }}>
            <div style={{ fontSize:9, fontWeight:700, letterSpacing:2, color:C.muted, textTransform:'uppercase', marginBottom:12 }}>
              Structure du protocole
            </div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8 }}>
              {[
                ['P1 · S1-3', '85-90% · Δ ±1.0 µV', '#7ba8c4'],
                ['P2 · S4-7', '95-110% · Δ ±0.5 µV', '#7bc4a0'],
                ['P3 · S8-12', '110-125% · Δ ±0.3 µV', C.warn],
                ['P4 · S13-15', '125-140% · Δ ±0.2 µV', C.accent],
              ].map(([label, desc, color]) => (
                <div key={label} style={{ padding:'10px 12px', borderRadius:10, background:'rgba(255,255,255,.02)', border:`1px solid ${color}20` }}>
                  <div style={{ fontSize:11, fontWeight:700, color }}>{label}</div>
                  <div style={{ fontSize:10, color:C.muted, marginTop:2 }}>{desc}</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop:12, fontSize:10, color:C.muted, lineHeight:1.6 }}>
              Séance (~35 min) : 2 min baseline (yeux fermés) → 1 min IAPF (yeux ouverts) → {N_BLOCS} blocs × 3 min → 3 min repos final
            </div>
          </div>

          {/* Saisie utilisateur */}
          <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:14, padding:'16px 20px', marginBottom:20 }}>
            <div style={{ marginBottom:14 }}>
              <label style={{ fontSize:11, color:C.muted, display:'block', marginBottom:6 }}>Identifiant participant</label>
              <input
                value={userId}
                onChange={e => setUserId(e.target.value)}
                onBlur={() => userId && loadProgram(userId)}
                style={{
                  width:'100%', padding:'8px 12px', borderRadius:8,
                  background:'rgba(255,255,255,.04)', border:`1px solid ${C.border}`,
                  color:C.text, fontSize:12, outline:'none', boxSizing:'border-box',
                }}
              />
            </div>
            <div>
              <label style={{ fontSize:11, color:C.muted, display:'block', marginBottom:6 }}>Numéro de séance (1-15)</label>
              <input
                type="number" min={1} max={15} value={sessionN}
                onChange={e => setSessionN(parseInt(e.target.value) || 1)}
                style={{
                  width:80, padding:'8px 12px', borderRadius:8,
                  background:'rgba(255,255,255,.04)', border:`1px solid ${C.border}`,
                  color:C.text, fontSize:12, outline:'none',
                }}
              />
              {program && (
                <span style={{ marginLeft:12, fontSize:10, color:C.accent }}>
                  Progression : {program.sessions_done}/15 séances terminées
                </span>
              )}
            </div>
          </div>

          {/* Mode CSV info */}
          {analysisData && (
            <div style={{ background:'rgba(0,229,176,.06)', border:`1px solid rgba(0,229,176,.2)`, borderRadius:12, padding:'10px 14px', marginBottom:16, fontSize:11, color:C.accent }}>
              Mode CSV — Fichier : {analysisData.filename || 'analyse'}<br/>
              <span style={{ color:C.muted }}>Les données EEG seront extraites de l'analyse.</span>
            </div>
          )}

          {apiError && (
            <div style={{ marginBottom:12, padding:'10px 14px', borderRadius:10, background:'rgba(255,77,109,.08)', border:`1px solid rgba(255,77,109,.2)`, fontSize:11, color:C.danger }}>
              {apiError}
            </div>
          )}

          <button
            onClick={() => { loadProgram(userId); goPreQ() }}
            disabled={!userId}
            style={{
              width:'100%', padding:14, borderRadius:14,
              background: `linear-gradient(135deg, rgba(0,229,176,.9), rgba(0,200,140,.9))`,
              border:'none', color:'#000', fontWeight:800, fontSize:14,
              cursor: userId ? 'pointer' : 'not-allowed', letterSpacing:.5,
            }}>
            Démarrer la séance {sessionN} →
          </button>
        </div>
      </div>
    )
  }

  // ── Pré-questionnaire ──────────────────────────────────────────────────────────
  if (phase === 'pre_q') {
    return (
      <div style={{ fontFamily:"'Outfit',sans-serif", color:C.text, maxWidth:520, margin:'0 auto', padding:8 }}>
        <div style={{ fontSize:13, fontWeight:700, color:C.muted, marginBottom:14 }}>
          Séance {sessionN} — {program ? PALIER_LABELS[program.palier] : ''}
        </div>
        <Questionnaire
          title="Évaluation pré-séance"
          questions={PRE_Q}
          onSubmit={(ans) => { preAnswersRef.current = ans; goBaseline() }}
        />
      </div>
    )
  }

  // ── Phases chronométrées ───────────────────────────────────────────────────────
  if (['baseline', 'iapf', 'bloc', 'interbloc', 'rest_final'].includes(phase)) {
    const taux = blocSamplesRef.current.total > 0
      ? blocSamplesRef.current.above / blocSamplesRef.current.total
      : 0

    return (
      <div style={{ fontFamily:"'Outfit',sans-serif", color:C.text, maxWidth:560, margin:'0 auto', padding:8 }}>

        {/* Barre de progression globale */}
        <div style={{ display:'flex', gap:6, marginBottom:16, alignItems:'center' }}>
          {['baseline','iapf',...Array.from({length:N_BLOCS},(_,i)=>`b${i+1}`),'rest_final'].map((s,i) => {
            const done = i < (['baseline','iapf',...Array.from({length:N_BLOCS-1},(_,j)=>`b${j+1}`)].indexOf(phase) +
              (phase==='bloc' ? blocN : 0) + (phase==='interbloc' ? blocN : 0) + (phase==='rest_final' ? N_BLOCS+2:0))
            const curr = s === phase || (s===`b${blocN}` && (phase==='bloc'||phase==='interbloc'))
            return (
              <div key={s} style={{ flex:1, height:4, borderRadius:2,
                background: curr ? C.accent : done ? 'rgba(0,229,176,.4)' : 'rgba(255,255,255,.06)' }} />
            )
          })}
        </div>

        <PhaseCard phase={phase} countdown={countdown}>
          {/* Alpha bar visible pendant baseline et blocs */}
          {(phase === 'baseline' || phase === 'iapf' || phase === 'bloc') && (
            <div style={{ marginTop:12 }}>
              {phase === 'bloc' ? (
                <AlphaBar value={liveAlpha} threshold={seuil} label="Puissance alpha relative" />
              ) : (
                <div style={{ fontSize:11, color:C.muted }}>
                  Alpha live : <span style={{ color:C.alpha, fontFamily:'monospace' }}>{liveAlpha.toFixed(3)}</span>
                  {phase==='baseline' && <span style={{ color:C.muted }}> · Collecte en cours ({alphaBaselineRef.current.length} points)</span>}
                </div>
              )}
            </div>
          )}
        </PhaseCard>

        {/* Stats du bloc courant */}
        {phase === 'bloc' && (
          <div style={{ marginTop:14, background:C.card, border:`1px solid ${C.border}`, borderRadius:14, padding:'14px 18px' }}>
            <div style={{ display:'flex', justifyContent:'space-between', marginBottom:10 }}>
              <span style={{ fontSize:9, fontWeight:700, letterSpacing:2, color:C.muted, textTransform:'uppercase' }}>
                Bloc {blocN}/{N_BLOCS}
              </span>
              <span style={{ fontSize:10, fontFamily:'monospace', color: taux>0.6?C.accent:taux<0.4?C.danger:C.warn }}>
                Succès : {(taux*100).toFixed(0)}%
              </span>
            </div>
            <div style={{ display:'flex', gap:3 }}>
              {blocResultsRef.current.map(b => (
                <div key={b.bloc_n} style={{ flex:1, padding:'6px 4px', borderRadius:6, textAlign:'center',
                                             background: b.taux_succes>0.6?'rgba(0,229,176,.12)':b.taux_succes<0.4?'rgba(255,77,109,.08)':'rgba(245,166,35,.08)',
                                             border:`1px solid ${b.taux_succes>0.6?'rgba(0,229,176,.3)':b.taux_succes<0.4?'rgba(255,77,109,.2)':'rgba(245,166,35,.2)'}` }}>
                  <div style={{ fontSize:9, color:C.muted }}>B{b.bloc_n}</div>
                  <div style={{ fontSize:11, fontFamily:'monospace', fontWeight:700,
                                color:b.taux_succes>0.6?C.accent:b.taux_succes<0.4?C.danger:C.warn }}>
                    {(b.taux_succes*100).toFixed(0)}%
                  </div>
                  <div style={{ fontSize:8, color:C.muted }}>{b.direction==='up'?'↑':b.direction==='down'?'↓':'—'}</div>
                </div>
              ))}
              {/* Bloc courant */}
              <div style={{ flex:1, padding:'6px 4px', borderRadius:6, textAlign:'center',
                            background:'rgba(167,139,250,.1)', border:'1px solid rgba(167,139,250,.3)' }}>
                <div style={{ fontSize:9, color:C.alpha }}>B{blocN}</div>
                <div style={{ fontSize:11, fontFamily:'monospace', fontWeight:700, color:C.alpha }}>
                  {(taux*100).toFixed(0)}%
                </div>
                <div style={{ fontSize:8, color:C.muted }}>•</div>
              </div>
              {/* Blocs futurs */}
              {Array.from({length:N_BLOCS-blocN-blocResultsRef.current.length+blocN}).map((_,i) => (
                <div key={`f${i}`} style={{ flex:1, padding:'6px 4px', borderRadius:6, textAlign:'center',
                                            background:'rgba(255,255,255,.02)', border:`1px solid ${C.border}` }}>
                  <div style={{ fontSize:9, color:'rgba(255,255,255,.15)' }}>B{blocN+i+1}</div>
                  <div style={{ fontSize:11, color:'rgba(255,255,255,.1)' }}>—</div>
                </div>
              ))}
            </div>
            <div style={{ marginTop:8, fontSize:10, color:C.muted }}>
              Seuil initial : <span style={{ color:C.alpha, fontFamily:'monospace' }}>{seuilInitial.toFixed(3)}</span>
              {' · '}Seuil actuel : <span style={{ color:C.accent, fontFamily:'monospace' }}>{seuil.toFixed(3)}</span>
            </div>
          </div>
        )}

        {phase === 'interbloc' && (
          <div style={{ marginTop:14, background:C.card, border:`1px solid ${C.border}`, borderRadius:14, padding:'14px 18px' }}>
            {blocResultsRef.current.slice(-1).map(b => (
              <div key={b.bloc_n}>
                <div style={{ fontSize:12, color:C.text, marginBottom:6 }}>
                  Résultat bloc {b.bloc_n} : <span style={{ color: b.taux_succes>0.6?C.accent:b.taux_succes<0.4?C.danger:C.warn, fontWeight:700 }}>
                    {(b.taux_succes*100).toFixed(0)}% de succès
                  </span>
                </div>
                <div style={{ fontSize:11, color:C.muted }}>{b.feedback_msg}</div>
                <div style={{ marginTop:8, fontSize:10, color:C.alpha }}>
                  Seuil suivant : {b.seuil_next?.toFixed(3)} ({b.direction==='up'?'↑ augmenté':b.direction==='down'?'↓ réduit':'maintenu'})
                </div>
              </div>
            ))}
          </div>
        )}

        {loadingApi && (
          <div style={{ marginTop:10, textAlign:'center', fontSize:11, color:C.muted }}>
            Synchronisation avec le serveur…
          </div>
        )}
        {apiError && (
          <div style={{ marginTop:10, padding:'8px 12px', borderRadius:8, background:'rgba(255,77,109,.08)', fontSize:11, color:C.danger }}>
            {apiError}
          </div>
        )}
      </div>
    )
  }

  // ── Post-questionnaire ────────────────────────────────────────────────────────
  if (phase === 'post_q') {
    return (
      <div style={{ fontFamily:"'Outfit',sans-serif", color:C.text, maxWidth:520, margin:'0 auto', padding:8 }}>
        <Questionnaire
          title="Évaluation post-séance"
          questions={POST_Q}
          onSubmit={endSession}
        />
      </div>
    )
  }

  // ── Rapport final ─────────────────────────────────────────────────────────────
  if (phase === 'report' && report) {
    const { taux_succes_global, bilan } = report
    const blocs = blocResultsRef.current

    return (
      <div style={{ fontFamily:"'Outfit',sans-serif", color:C.text, maxWidth:560, margin:'0 auto', padding:8 }}>

        {/* En-tête succès */}
        <div style={{
          background: taux_succes_global>0.6 ? 'rgba(0,229,176,.08)' : taux_succes_global>0.4 ? 'rgba(245,166,35,.08)' : 'rgba(255,77,109,.08)',
          border: `1px solid ${taux_succes_global>0.6?'rgba(0,229,176,.3)':taux_succes_global>0.4?'rgba(245,166,35,.3)':'rgba(255,77,109,.3)'}`,
          borderRadius:16, padding:'20px 24px', textAlign:'center', marginBottom:16,
        }}>
          <div style={{ fontSize:32, marginBottom:8 }}>
            {taux_succes_global>0.6?'🎉':taux_succes_global>0.4?'👍':'💪'}
          </div>
          <div style={{ fontSize:20, fontWeight:800, color:C.accent, marginBottom:4 }}>
            Séance {sessionN} terminée
          </div>
          <div style={{ fontSize:28, fontFamily:'monospace', fontWeight:700,
                        color:taux_succes_global>0.6?C.accent:taux_succes_global>0.4?C.warn:C.danger }}>
            {(taux_succes_global*100).toFixed(0)}% de succès
          </div>
          <div style={{ fontSize:11, color:C.muted, marginTop:6 }}>Taux global sur les 5 blocs</div>
        </div>

        {/* Résultats par bloc */}
        <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:14, padding:'16px 18px', marginBottom:14 }}>
          <div style={{ fontSize:9, fontWeight:700, letterSpacing:2, color:C.muted, textTransform:'uppercase', marginBottom:12 }}>Détail par bloc</div>
          <div style={{ display:'flex', gap:6 }}>
            {blocs.map(b => (
              <div key={b.bloc_n} style={{ flex:1, padding:'10px 6px', borderRadius:10, textAlign:'center',
                                           background: b.taux_succes>0.6?'rgba(0,229,176,.1)':b.taux_succes<0.4?'rgba(255,77,109,.08)':'rgba(245,166,35,.08)' }}>
                <div style={{ fontSize:9, color:C.muted, marginBottom:4 }}>BLOC {b.bloc_n}</div>
                <div style={{ fontSize:16, fontWeight:800, color:b.taux_succes>0.6?C.accent:b.taux_succes<0.4?C.danger:C.warn }}>
                  {(b.taux_succes*100).toFixed(0)}%
                </div>
                <div style={{ fontSize:9, color:C.muted, marginTop:4 }}>
                  {b.direction==='up'?'↑ +seuil':b.direction==='down'?'↓ -seuil':'→ stable'}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bilan programme */}
        {bilan && (
          <div style={{ background:C.card, border:`1px solid ${C.border}`, borderRadius:14, padding:'16px 18px', marginBottom:14 }}>
            <div style={{ fontSize:9, fontWeight:700, letterSpacing:2, color:C.muted, textTransform:'uppercase', marginBottom:12 }}>Bilan du programme</div>
            <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10, marginBottom:12 }}>
              {[
                ['Séances terminées', `${bilan.sessions_done}/15`],
                ['Séances restantes', bilan.sessions_left],
                ['Palier actuel', bilan.current_palier],
                ['Succès moyen', bilan.avg_taux_succes!=null ? `${(bilan.avg_taux_succes*100).toFixed(0)}%` : '—'],
              ].map(([l,v]) => (
                <div key={l} style={{ padding:'8px 12px', borderRadius:8, background:'rgba(255,255,255,.02)' }}>
                  <div style={{ fontSize:9, color:C.muted }}>{l}</div>
                  <div style={{ fontSize:13, fontWeight:700, color:C.text, marginTop:2 }}>{v}</div>
                </div>
              ))}
            </div>
            {bilan.message && (
              <div style={{ fontSize:11, color:C.muted, lineHeight:1.6, padding:'10px 12px',
                            background:'rgba(255,255,255,.02)', borderRadius:8 }}>
                {bilan.message}
              </div>
            )}
          </div>
        )}

        {/* Évolution trend */}
        {bilan?.trend && (
          <div style={{ marginBottom:14, padding:'10px 14px', borderRadius:10,
                        background: bilan.trend==='improving'?'rgba(0,229,176,.06)':bilan.trend==='declining'?'rgba(255,77,109,.06)':'rgba(255,255,255,.03)',
                        border:`1px solid ${bilan.trend==='improving'?'rgba(0,229,176,.2)':bilan.trend==='declining'?'rgba(255,77,109,.2)':C.border}`,
                        fontSize:11,
                        color:bilan.trend==='improving'?C.accent:bilan.trend==='declining'?C.danger:C.muted }}>
            {bilan.trend==='improving'?'📈 Progression croissante détectée sur les 3 dernières séances.':
             bilan.trend==='declining'?'📉 Légère baisse — envisagez un repos ou réduisez la difficulté.':
             '📊 Progression stable.'}
          </div>
        )}

        <div style={{ display:'flex', gap:10 }}>
          <button
            onClick={goSetup}
            style={{
              flex:1, padding:12, borderRadius:12,
              background:'rgba(255,255,255,.05)', border:`1px solid ${C.border}`,
              color:C.text, fontWeight:600, fontSize:12, cursor:'pointer',
            }}>
            ← Nouvelle séance
          </button>
          {bilan?.sessions_left > 0 && (
            <button
              onClick={() => { setSessionN(s=>Math.min(15,s+1)); goSetup() }}
              style={{
                flex:2, padding:12, borderRadius:12,
                background:'linear-gradient(135deg, rgba(0,229,176,.9), rgba(0,200,140,.9))',
                border:'none', color:'#000', fontWeight:800, fontSize:12, cursor:'pointer',
              }}>
              Séance {Math.min(15,sessionN+1)} → Prochaine session
            </button>
          )}
        </div>
      </div>
    )
  }

  return null
}
