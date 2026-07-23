import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Brain, CheckCircle2, Eye, EyeOff, Calculator,
  Wind, Volume2, FileQuestion, ArrowLeft, Clock, Radio, WifiOff,
  Activity, Zap, Wifi, Download, Mail,
} from 'lucide-react'
import BreathingGuide       from '../components/feedback/BreathingGuide'
import SignalCanvas          from '../components/eeg/SignalCanvas'
import BandBars              from '../components/eeg/BandBars'
import WifiSetupCard         from '../components/eeg/WifiSetupCard'
import { useEEGWebSocket }   from '../hooks/useEEGWebSocket'
import { eeg as eegApi }     from '../utils/api'
import { exportCalibrationPDF } from '../utils/exportPDF'

const API = (path, opts = {}) => fetch(`/api${path}`, {
  headers: {
    Authorization: `Bearer ${localStorage.getItem('neurocap_token')}`,
    'Content-Type': 'application/json',
  },
  ...opts,
}).then(r => r.json())

/* ── Étapes de calibration ─────────────────────────────────────────────── */
const STEPS = [
  {
    id: 'C1', label: 'Repos yeux fermés', icon: EyeOff,
    duration: 300, color: 'text-indigo-400', bg: 'bg-indigo-500/10',
    desc: 'Fermez les yeux, respirez normalement, restez immobile.',
    detail: 'Mesure de la puissance alpha de référence (P_alpha_ref) et de l\'IAPF.',
    auto: true,
  },
  {
    id: 'C2', label: 'Repos yeux ouverts', icon: Eye,
    duration: 300, color: 'text-blue-400', bg: 'bg-blue-500/10',
    desc: 'Fixez le point au centre de l\'écran sans cligner excessivement.',
    detail: 'Mesure du blocage alpha (ERD) et de la réactivité visuelle.',
    auto: true,
  },
  {
    id: 'C3', label: 'Tâche cognitive', icon: Calculator,
    duration: 300, color: 'text-emerald-400', bg: 'bg-emerald-500/10',
    desc: 'Résolvez mentalement les opérations affichées.',
    detail: 'Mesure de l\'activation bêta en situation de charge cognitive.',
    auto: true,
  },
  {
    id: 'C4', label: 'Relaxation guidée', icon: Wind,
    duration: 300, color: 'text-cyan-400', bg: 'bg-cyan-500/10',
    desc: 'Suivez le guide de respiration : 4s inspirez, 4s expirez.',
    detail: 'Mesure de la réponse alpha à la relaxation.',
    auto: true,
  },
  {
    id: 'C5', label: 'Préférences sonores', icon: Volume2,
    duration: 300, color: 'text-purple-400', bg: 'bg-purple-500/10',
    desc: 'Évaluez chaque son et indiquez vos préférences (1–5).',
    detail: 'Personnalisation du feedback auditif pour les séances suivantes.',
    auto: false,
  },
  {
    id: 'C6', label: 'Questionnaire cognitif', icon: FileQuestion,
    duration: 300, color: 'text-amber-400', bg: 'bg-amber-500/10',
    desc: 'Répondez aux questions sur votre profil habituel.',
    detail: 'Classification du profil cognitif (A / B / C).',
    auto: false,
  },
]

const MATH_OPS = [
  '37 + 48', '82 - 29', '6 × 13', '91 + 37',
  '143 - 56', '7 × 12', '64 + 78', '112 - 47',
  '8 × 15',  '53 + 69',
]

/* ── Anneau countdown ─────────────────────────────────────────────────── */
function CountdownRing({ elapsed, total, color }) {
  const pct  = Math.min(elapsed / total, 1)
  const r    = 54, cx = 60, cy = 60
  const circ = 2 * Math.PI * r
  return (
    <svg width={120} height={120} className="block mx-auto">
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={8} />
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="currentColor" strokeWidth={8}
        strokeDasharray={circ} strokeDashoffset={circ * (1 - pct)}
        strokeLinecap="round" transform={`rotate(-90 ${cx} ${cy})`}
        className={color} style={{ transition: 'stroke-dashoffset 0.9s linear' }}
      />
      <text x={cx} y={cy + 5} textAnchor="middle" fontSize={18} fontWeight={700}
        fill="currentColor" className={color}>
        {Math.floor((total - elapsed) / 60)}:{String((total - elapsed) % 60).padStart(2, '0')}
      </text>
    </svg>
  )
}

/* ── Questionnaire C6 ─────────────────────────────────────────────────── */
function QuestionnaireC6({ onSubmit }) {
  const [vals, setVals] = useState({
    concentration_habituelle: 5,
    stress_quotidien: 5,
    motivation: 7,
    meditation_exp: 'jamais',
    audio_preference: 'nature',
    audio_volume_pref: 3,
  })
  const set = (k, v) => setVals(p => ({ ...p, [k]: v }))

  return (
    <div className="space-y-5 max-w-md mx-auto">
      {[
        { key: 'concentration_habituelle', label: 'Concentration habituelle' },
        { key: 'stress_quotidien',         label: 'Niveau de stress quotidien' },
        { key: 'motivation',               label: 'Motivation pour le programme' },
      ].map(({ key, label }) => (
        <div key={key}>
          <div className="flex justify-between text-xs text-nc-muted mb-1.5">
            <span>{label}</span><span className="font-mono font-bold text-nc-text">{vals[key]}/10</span>
          </div>
          <input type="range" min={1} max={10} value={vals[key]}
            onChange={e => set(key, parseInt(e.target.value))}
            className="w-full accent-nc-accent" />
        </div>
      ))}

      <div>
        <p className="text-xs text-nc-muted mb-2">Expérience de méditation</p>
        <div className="flex gap-2">
          {['jamais','parfois','régulièrement'].map(opt => (
            <button key={opt} onClick={() => set('meditation_exp', opt)}
              className={`flex-1 py-1.5 rounded-xl text-xs font-medium border transition-all
                ${vals.meditation_exp === opt
                  ? 'bg-nc-accent/15 border-nc-accent/40 text-nc-accent'
                  : 'border-nc-border text-nc-muted hover:bg-nc-surface2'}`}>
              {opt}
            </button>
          ))}
        </div>
      </div>

      <div>
        <p className="text-xs text-nc-muted mb-2">Préférence sonore</p>
        <div className="flex gap-2">
          {[['bip','🔔'],['nature','🌿'],['musique','🎵']].map(([opt, icon]) => (
            <button key={opt} onClick={() => set('audio_preference', opt)}
              className={`flex-1 py-2 rounded-xl text-xs font-medium border transition-all
                ${vals.audio_preference === opt
                  ? 'bg-nc-accent/15 border-nc-accent/40 text-nc-accent'
                  : 'border-nc-border text-nc-muted hover:bg-nc-surface2'}`}>
              {icon} {opt}
            </button>
          ))}
        </div>
      </div>

      <div>
        <div className="flex justify-between text-xs text-nc-muted mb-1.5">
          <span>Volume préféré</span>
          <span className="font-mono font-bold text-nc-text">{vals.audio_volume_pref}/5</span>
        </div>
        <input type="range" min={1} max={5} value={vals.audio_volume_pref}
          onChange={e => set('audio_volume_pref', parseInt(e.target.value))}
          className="w-full accent-nc-accent" />
      </div>

      <button onClick={() => onSubmit(vals)}
        className="w-full btn-primary py-3 rounded-xl text-sm font-semibold">
        Valider le questionnaire →
      </button>
    </div>
  )
}

/* ── Évaluation sons C5 ────────────────────────────────────────────────── */
const SOUNDS = [
  { id: 'bip',     label: '🔔 Bip régulier'    },
  { id: 'nature',  label: '🌿 Sons de la nature' },
  { id: 'musique', label: '🎵 Musique douce'      },
]

function SoundPrefs({ onSubmit }) {
  const [ratings, setRatings] = useState({ bip: 3, nature: 4, musique: 3 })
  return (
    <div className="space-y-4 max-w-sm mx-auto">
      {SOUNDS.map(s => (
        <div key={s.id} className="card p-4 space-y-2">
          <p className="text-sm font-medium text-nc-text">{s.label}</p>
          <div className="flex gap-2 justify-center">
            {[1,2,3,4,5].map(n => (
              <button key={n} onClick={() => setRatings(r => ({ ...r, [s.id]: n }))}
                className={`w-8 h-8 rounded-full text-sm font-bold border transition-all
                  ${ratings[s.id] >= n
                    ? 'bg-nc-accent/20 border-nc-accent/50 text-nc-accent'
                    : 'border-nc-border text-nc-muted hover:bg-nc-surface2'}`}>
                {n}
              </button>
            ))}
          </div>
        </div>
      ))}
      <button onClick={() => onSubmit(ratings)}
        className="w-full btn-primary py-2.5 rounded-xl text-sm font-semibold">
        Valider les préférences →
      </button>
    </div>
  )
}

/* ── Barre pipeline EEG (landing) ─────────────────────────────────────── */
function EEGPipelineBar() {
  const [eegStatus, setEegStatus] = useState(null)
  const pollRef = useRef(null)

  useEffect(() => {
    const poll = async () => {
      try { setEegStatus(await eegApi.status()) } catch { setEegStatus(null) }
    }
    poll()
    pollRef.current = setInterval(poll, 2000)
    return () => clearInterval(pollRef.current)
  }, [])

  const conn      = eegStatus?.connected
  const streaming = eegStatus?.streaming
  const srate     = eegStatus?.sample_rate
  const quality   = eegStatus?.signal_quality ?? eegStatus?.rms ?? null

  const PIPE = [
    { label: 'ESP32',      ok: conn,                              icon: Wifi      },
    { label: 'Streaming',  ok: conn && streaming,                 icon: Radio     },
    { label: 'Traitement', ok: conn && streaming,                 icon: Activity  },
    { label: 'Analyse',    ok: conn && streaming && quality != null, icon: Zap    },
  ]

  return (
    <div className="card p-4 border border-nc-accent/20 space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide">Pipeline EEG live</p>
        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
          conn ? 'bg-emerald-500/15 text-emerald-400' : 'bg-red-500/10 text-red-400'
        }`}>
          {conn ? `Connecté${srate ? ` · ${srate} Hz` : ''}` : 'Non connecté'}
        </span>
      </div>

      <div className="flex items-center gap-2">
        {PIPE.map((s, i) => {
          const Icon = s.icon
          return (
            <div key={s.label} className="flex items-center gap-1.5 flex-1 min-w-0">
              <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${s.ok ? 'bg-emerald-500/15' : 'bg-nc-surface2'}`}>
                <Icon className={`w-3.5 h-3.5 ${s.ok ? 'text-emerald-400' : 'text-nc-muted/30'}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className={`text-[9px] font-semibold truncate ${s.ok ? 'text-emerald-400' : 'text-nc-muted/40'}`}>{s.label}</p>
                <div className={`h-0.5 rounded-full mt-0.5 ${s.ok ? 'bg-emerald-500' : 'bg-nc-surface2'}`} />
              </div>
              {i < PIPE.length - 1 && (
                <div className={`w-3 h-0.5 rounded-full shrink-0 ${s.ok ? 'bg-emerald-500/50' : 'bg-nc-surface2'}`} />
              )}
            </div>
          )
        })}
      </div>

      {!conn && (
        <p className="text-[11px] text-nc-muted text-center">
          Branchez votre casque EEG et démarrez l'ESP32 pour une acquisition en direct.
        </p>
      )}
    </div>
  )
}

/* ════════════════════════════════════════════════════════
   Page principale CalibrationSession
════════════════════════════════════════════════════════ */
export default function CalibrationSession({ onComplete, onSkip } = {}) {
  const navigate = useNavigate()

  const [landing,      setLanding]      = useState(true)
  const [stepIdx,      setStepIdx]      = useState(0)
  const [elapsed,      setElapsed]      = useState(0)
  const [mathIdx,      setMathIdx]      = useState(0)
  const [soundPrefs,   setSoundPrefs]   = useState({})
  const [submitting,   setSubmitting]   = useState(false)
  const [result,       setResult]       = useState(null)
  const [emailSent,    setEmailSent]    = useState(false)
  const [autoAdvance,  setAutoAdvance]  = useState(false)
  const [showWifi,     setShowWifi]     = useState(false)
  const [eegStatus,    setEegStatus]    = useState(null)

  const timerRef    = useRef(null)
  const firedRef    = useRef(false)

  const step     = STEPS[stepIdx]
  const StepIcon = step?.icon

  /* ── Statut EEG initial — auto-ouvre WiFi si ESP32 non connecté ── */
  useEffect(() => {
    eegApi.status().then(s => {
      setEegStatus(s)
      if (!s.esp32_connected && !s.connected) setShowWifi(true)
    }).catch(() => {})
  }, [])

  /* ── WebSocket EEG ────────────────────────────────────────────────────── */
  const { connected, eegFrame, epochFrame, initFrame, esp32Status } = useEEGWebSocket()

  const esp32Connected = esp32Status?.connected ?? initFrame?.esp32_connected ?? false
  const electrodeOk    = eegFrame?.electrode_ok ?? initFrame?.electrode_ok ?? false

  const bands = epochFrame?.features ? {
    delta:     epochFrame.features.rel_delta     ?? 0,
    theta:     epochFrame.features.rel_theta     ?? 0,
    alpha:     epochFrame.features.rel_alpha     ?? 0,
    beta:      epochFrame.features.rel_beta      ?? 0,
    beta_high: epochFrame.features.rel_beta_high ?? 0,
    gamma_low: epochFrame.features.rel_gamma_low ?? 0,
  } : {}

  /* ── Auto-timer pour les étapes C1-C4 ────────────────────────────────── */
  useEffect(() => {
    if (landing || !step?.auto) return

    firedRef.current = false
    setElapsed(0)
    clearInterval(timerRef.current)

    timerRef.current = setInterval(() => {
      setElapsed(e => {
        if (e + 1 >= step.duration && !firedRef.current) {
          firedRef.current = true
          clearInterval(timerRef.current)
          setAutoAdvance(true)
        }
        return e + 1
      })
    }, 1000)

    return () => clearInterval(timerRef.current)
  }, [stepIdx, landing])

  useEffect(() => () => clearInterval(timerRef.current), [])

  /* ── Réaction à autoAdvance (evite la stale closure) ─────────────────── */
  useEffect(() => {
    if (!autoAdvance) return
    setAutoAdvance(false)
    setElapsed(0)
    setMathIdx(0)
    setStepIdx(prev => prev + 1)   // C1→C2→C3→C4→C5 (C5 n'a pas auto:true)
  }, [autoAdvance])

  /* ── Soumission finale (appelée depuis C6 avec valeurs fraîches) ──────── */
  const submitCalibration = async (questData, currentSoundPrefs) => {
    setSubmitting(true)
    try {
      const r = await API('/protocol/calibration/complete', {
        method: 'POST',
        body: JSON.stringify({
          epochs_c1: [],
          epochs_c2: [],
          epochs_c3: [],
          epochs_c4: [],
          questionnaire: { ...currentSoundPrefs, ...questData },
        }),
      })
      setResult(r.profile)
      setEmailSent(r.email_sent ?? false)
      // Auto-download PDF
      try { exportCalibrationPDF(r.profile) } catch {}
      if (onComplete) onComplete(r.profile)
    } catch (e) {
      alert('Erreur lors de la soumission : ' + e.message)
    } finally {
      setSubmitting(false)
    }
  }

  /* ══════════════════════════════════════════════════════════════
     Landing page
  ══════════════════════════════════════════════════════════════ */
  if (landing) return (
    <div className="max-w-lg mx-auto px-4 py-10 space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => onSkip ? onSkip() : navigate('/protocol')}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <h1 className="text-xl font-bold text-nc-text">Séance 1 — Calibration EEG</h1>
      </div>

      <div className="card p-6 space-y-4 border border-amber-500/30 bg-amber-500/5">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-amber-500/20 flex items-center justify-center shrink-0">
            <Brain className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <p className="text-sm font-bold text-amber-300">À quoi sert la calibration ?</p>
            <p className="text-[11px] text-amber-400/70">Obligatoire avant toute séance de neurofeedback</p>
          </div>
        </div>
        <div className="space-y-3">
          {[
            { icon: '🧠', title: 'Établit votre baseline EEG', desc: 'Mesure votre fréquence alpha individuelle (IAPF) et la puissance alpha de référence pendant le repos.' },
            { icon: '📊', title: 'Crée votre profil cognitif', desc: 'Détermine si vous êtes profil A (alpha dominant), B (équilibré) ou C (beta dominant) selon vos mesures neurophysiologiques.' },
            { icon: '⚙️', title: 'Adapte l\'expérience', desc: 'Fixe le seuil de feedback adaptatif, le palier de départ et personnalise les médias pour les 14 séances suivantes.' },
          ].map(({ icon, title, desc }) => (
            <div key={title} className="flex items-start gap-3">
              <span className="text-lg mt-0.5">{icon}</span>
              <div>
                <p className="text-sm font-semibold text-nc-text">{title}</p>
                <p className="text-xs text-nc-muted leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-4 gap-2 text-center pt-1">
          {[
            { step: 'C1', label: 'Yeux fermés',  icon: '😌' },
            { step: 'C2', label: 'Yeux ouverts', icon: '👁' },
            { step: 'C3', label: 'Calcul mental', icon: '🧮' },
            { step: 'C4', label: 'Relaxation',   icon: '🌬' },
          ].map(({ step: s, label, icon }) => (
            <div key={s} className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/15">
              <div className="text-lg mb-0.5">{icon}</div>
              <p className="text-[9px] font-bold text-amber-300">{label}</p>
              <p className="text-[9px] text-amber-400/60">5 min</p>
            </div>
          ))}
        </div>
      </div>

      {/* Pipeline EEG — toujours visible sur la landing */}
      <EEGPipelineBar />

      <button
        onClick={() => { setLanding(false) }}
        className="w-full btn-primary py-3 rounded-xl text-sm font-semibold"
      >
        Commencer la calibration →
      </button>

      {onSkip && (
        <button
          onClick={onSkip}
          className="w-full py-2.5 rounded-xl text-sm font-medium text-nc-muted
                     border border-nc-border hover:bg-nc-surface2 hover:text-nc-text transition-colors"
        >
          Passer cette étape →
        </button>
      )}
    </div>
  )

  /* ══════════════════════════════════════════════════════════════
     Écran de complétion
  ══════════════════════════════════════════════════════════════ */
  if (result) return (
    <div className="max-w-lg mx-auto px-4 py-10 space-y-6 text-center">
      <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 flex items-center justify-center mx-auto">
        <CheckCircle2 className="w-8 h-8 text-emerald-400" />
      </div>
      <h1 className="text-2xl font-bold text-nc-text">Calibration terminée !</h1>
      <p className="text-sm text-nc-muted">Votre profil EEG individuel est établi.</p>

      {/* Email auto-envoyé */}
      {emailSent && (
        <div className="flex items-center gap-2 px-4 py-2.5 rounded-xl
                        bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 text-sm font-medium justify-center">
          <Mail className="w-4 h-4" />
          Rapport envoyé automatiquement par email
        </div>
      )}

      {/* Profil EEG */}
      <div className="card p-5 text-left space-y-3">
        {[
          ['Profil cognitif', `Type ${result.profile_type}`],
          ['IAPF',            `${result.iapf} Hz`],
          ['Plage alpha',     `${result.alpha_band_lo} – ${result.alpha_band_hi} Hz`],
          ['P_alpha_ref',     result.p_alpha_ref?.toFixed(4)],
          ['ERD alpha',       `${result.erd_pct}%`],
          ['Palier initial',  result.palier_initial],
        ].map(([k, v]) => (
          <div key={k} className="flex justify-between text-sm py-1 border-b border-nc-border/30 last:border-0">
            <span className="text-nc-muted">{k}</span>
            <span className="font-mono font-semibold text-nc-text">{v ?? '—'}</span>
          </div>
        ))}
      </div>

      {/* Télécharger PDF */}
      <button
        onClick={() => exportCalibrationPDF(result)}
        className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold
                   border border-nc-accent/30 text-nc-accent hover:bg-nc-accent/10 transition-colors"
      >
        <Download className="w-4 h-4" />
        Télécharger le rapport PDF
      </button>

      {onComplete
        ? <button onClick={() => onComplete(result)} className="w-full btn-primary py-3 rounded-xl text-sm font-semibold">
            Continuer vers la session →
          </button>
        : <button onClick={() => navigate('/protocol')} className="w-full btn-primary py-3 rounded-xl text-sm font-semibold">
            Voir mon programme →
          </button>
      }
    </div>
  )

  /* ══════════════════════════════════════════════════════════════
     Vue principale — signal EEG + protocole de calibration
  ══════════════════════════════════════════════════════════════ */
  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">

      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => setLanding(true)}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-nc-text">Calibration EEG — Séance 1</h1>
          <p className="text-xs text-nc-muted">6 étapes · 30 minutes au total</p>
        </div>
        {onSkip && (
          <button onClick={onSkip}
            className="px-3 py-1.5 rounded-xl text-xs font-medium text-nc-muted
                       border border-nc-border hover:bg-nc-surface2 hover:text-nc-text transition-colors">
            Passer →
          </button>
        )}
      </div>

      {/* Barre de progression étapes */}
      <div className="flex gap-1.5">
        {STEPS.map((s, i) => (
          <div key={s.id} className="flex-1 space-y-1">
            <div className={`h-1.5 rounded-full transition-all ${
              i < stepIdx ? 'bg-emerald-500'
              : i === stepIdx ? 'bg-nc-accent animate-pulse'
              : 'bg-nc-surface2'
            }`} />
            <p className={`text-[8px] text-center font-semibold ${
              i < stepIdx ? 'text-emerald-400' : i === stepIdx ? 'text-nc-accent' : 'text-nc-muted/40'
            }`}>{s.id}</p>
          </div>
        ))}
      </div>

      {/* Statut connexion WiFi TCP */}
      <div className="card p-3 flex items-center gap-3 flex-wrap border border-nc-border/50">
        <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border
          ${connected
            ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400'
            : 'bg-red-500/10 border-red-500/25 text-red-400'}`}>
          <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
          {connected ? 'Backend OK' : 'Backend KO'}
        </span>

        <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border
          ${esp32Connected
            ? 'bg-blue-500/10 border-blue-500/25 text-blue-400'
            : 'bg-nc-surface2 border-nc-border text-nc-muted'}`}>
          {esp32Connected ? <Radio className="w-3 h-3" /> : <WifiOff className="w-3 h-3" />}
          {esp32Connected ? `ESP32 WiFi TCP${initFrame?.esp32_ip ? ` · ${initFrame.esp32_ip}` : ''}` : 'ESP32 non connecté'}
        </span>

        <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border
          ${electrodeOk
            ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400'
            : 'bg-nc-surface2 border-nc-border text-nc-muted'}`}>
          <Activity className="w-3 h-3" />
          {electrodeOk ? 'Électrode OK' : 'Électrode KO'}
        </span>

        {step?.auto && (
          <span className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium
                           bg-red-500/10 border border-red-500/25 text-red-400">
            <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
            EEG en cours
          </span>
        )}

        {/* Bouton Config WiFi */}
        <button
          onClick={() => setShowWifi(v => !v)}
          className="ml-auto flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium
                     border border-nc-border text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
          <Wifi className="w-3 h-3" /> Config WiFi
        </button>
      </div>

      {/* Panneau WiFi collapsible */}
      {showWifi && (
        <WifiSetupCard status={eegStatus} onClose={() => setShowWifi(false)} />
      )}

      {/* Oscilloscope EEG temps réel */}
      <div className="card overflow-hidden p-2" style={{ height: 220 }}>
        <SignalCanvas
          wsData={eegFrame}
          electrodeOk={electrodeOk}
          cognitiveState="neutral"
        />
      </div>

      {/* Bandes de fréquences */}
      <div className="card p-4">
        <p className="text-xs font-semibold text-nc-muted mb-3 uppercase tracking-wide">
          Bandes de fréquences — Fp2
        </p>
        <BandBars bands={bands} />
        {!epochFrame && (
          <p className="text-[11px] text-nc-muted/60 text-center mt-3">
            En attente de la première époque (4 s de signal)…
          </p>
        )}
      </div>

      {/* Carte étape courante */}
      <div className={`card p-6 space-y-5 border ${
        step.bg.replace('bg-', 'border-').replace('/10', '/25')
      }`}>
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-xl ${step.bg} flex items-center justify-center`}>
            {StepIcon && <StepIcon className={`w-5 h-5 ${step.color}`} />}
          </div>
          <div className="flex-1">
            <p className="text-xs font-semibold text-nc-muted">{step.id}</p>
            <h2 className="text-base font-bold text-nc-text">{step.label}</h2>
          </div>
          <div className="text-right">
            <span className="text-xs text-nc-muted flex items-center gap-1 justify-end">
              <Clock className="w-3.5 h-3.5" /> 5 min
            </span>
            {step.auto && (
              <p className="text-[10px] text-emerald-400/80 mt-0.5">Auto</p>
            )}
          </div>
        </div>

        <p className="text-sm text-nc-text">{step.desc}</p>
        <p className="text-xs text-nc-muted">{step.detail}</p>

        {/* ── C1–C4 : timer automatique ── */}
        {step.auto && (
          <div className="space-y-4">
            <CountdownRing elapsed={elapsed} total={step.duration} color={step.color} />

            {step.id === 'C1' && (
              <div className="text-center space-y-2">
                <p className="text-5xl">😌</p>
                <p className="text-sm text-nc-muted">Fermez les yeux — respirez naturellement</p>
                <p className="text-xs text-nc-muted/60">L'EEG s'enregistre automatiquement</p>
              </div>
            )}

            {step.id === 'C2' && (
              <div className="flex flex-col items-center gap-4">
                <div className="relative flex items-center justify-center" style={{ height: 100 }}>
                  {[100, 70, 40].map((sz, i) => (
                    <div key={i} className="absolute rounded-full border border-white/8"
                         style={{ width: sz, height: sz }} />
                  ))}
                  <div className="w-3 h-3 rounded-full bg-white"
                       style={{ boxShadow: '0 0 12px rgba(255,255,255,0.9)' }} />
                </div>
                <p className="text-sm text-nc-muted">Fixez le point central sans cligner</p>
              </div>
            )}

            {step.id === 'C3' && (
              <div className="text-center space-y-3">
                <p className="text-3xl font-bold font-mono text-nc-text">
                  {MATH_OPS[mathIdx % MATH_OPS.length]}
                </p>
                <p className="text-xs text-nc-muted">Résolvez mentalement</p>
                <button onClick={() => setMathIdx(i => i + 1)}
                  className="px-4 py-1.5 rounded-xl border border-nc-border text-xs text-nc-muted hover:bg-nc-surface2">
                  Opération suivante
                </button>
              </div>
            )}

            {step.id === 'C4' && (
              <div className="space-y-2">
                <BreathingGuide />
              </div>
            )}
          </div>
        )}

        {/* ── C5 : préférences sonores ── */}
        {step.id === 'C5' && (
          <SoundPrefs onSubmit={p => {
            setSoundPrefs(p)
            setStepIdx(5)
            setElapsed(0)
            setMathIdx(0)
          }} />
        )}

        {/* ── C6 : questionnaire ── */}
        {step.id === 'C6' && (
          <QuestionnaireC6 onSubmit={q => submitCalibration(q, soundPrefs)} />
        )}

        {submitting && (
          <div className="flex items-center justify-center gap-3 py-2">
            <div className="w-5 h-5 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
            <p className="text-sm text-nc-muted">Calcul du profil cognitif…</p>
          </div>
        )}
      </div>

      {/* Liste des autres étapes */}
      <div className="space-y-2">
        {STEPS.map((s, i) => {
          if (i === stepIdx) return null
          const SIcon = s.icon
          return (
            <div key={s.id} className={`flex items-center gap-3 p-3 rounded-xl border transition-all
              ${i < stepIdx
                ? 'border-emerald-500/20 bg-emerald-500/5'
                : 'border-nc-border bg-nc-surface2/20 opacity-40'}`}>
              {SIcon && <SIcon className={`w-4 h-4 ${i < stepIdx ? 'text-emerald-400' : s.color}`} />}
              <span className="text-xs font-medium text-nc-muted">{s.id} — {s.label}</span>
              {i < stepIdx && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 ml-auto" />}
              {i > stepIdx && s.auto && (
                <span className="ml-auto text-[9px] text-nc-muted/50">Auto · 5 min</span>
              )}
            </div>
          )
        })}
      </div>

    </div>
  )
}
