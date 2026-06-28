import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Wifi, WifiOff, Activity, Download, Pause, Play, Square, Circle,
  CheckCircle2, Radio, RefreshCw, ChevronRight, Brain, BarChart3,
  List, FileText, ArrowLeft, Send, Sparkles, X,
} from 'lucide-react'
import SignalCanvas        from '../components/eeg/SignalCanvas'
import BandBars            from '../components/eeg/BandBars'
import FeaturesPanel       from '../components/eeg/FeaturesPanel'
import CalibrationOverlay  from '../components/eeg/CalibrationOverlay'
import WifiSetupCard       from '../components/eeg/WifiSetupCard'
import { useEEGWebSocket } from '../hooks/useEEGWebSocket'
import { useRecording }    from '../hooks/useRecording'
import { eeg as eegApi } from '../utils/api'

/* ── Métadonnées états cognitifs ──────────────────────────────────────────────── */
const STATE_META = {
  focused:       { label: 'Concentré',       color: 'text-emerald-400', bg: 'bg-emerald-500/15', dot: 'bg-emerald-400' },
  relaxed:       { label: 'Détendu',         color: 'text-blue-400',    bg: 'bg-blue-500/15',    dot: 'bg-blue-400'    },
  stressed:      { label: 'Stressé',         color: 'text-red-400',     bg: 'bg-red-500/15',     dot: 'bg-red-400'     },
  neutral:       { label: 'Neutre',          color: 'text-nc-muted',    bg: 'bg-nc-surface2',    dot: 'bg-nc-muted'    },
  invalid:       { label: 'Signal invalide', color: 'text-nc-muted/50', bg: 'bg-nc-surface2/50', dot: 'bg-nc-muted/40' },
}

/* ── Raisons de rejet (mapping court) ── */
const REJECT_REASON = {
  electrode_off:  'Électrode déconnectée',
  flat_line:      'Ligne plate',
  extreme_peak:   'Pic extrême',
  eyeblink:       'Clignement (EOG)',
  high_rms:       'RMS trop élevé',
  emg:            'Artefact EMG',
  too_short:      'Signal trop court',
  emg_broadband:  'EMG large bande',
}

/* ── Carte Dual Classifier (EEGNet+LR · RF+feat78) ──────────────────────────── */
function DualClassifierCard({ prediction }) {
  if (!prediction) {
    return (
      <div className="card p-5 flex flex-col items-center justify-center gap-3 text-center min-h-[180px]">
        <Brain className="w-8 h-8 text-nc-muted/30" />
        <div>
          <p className="text-xs text-nc-muted">En attente de la première époque…</p>
          <p className="text-[10px] text-nc-muted/50 mt-1">EEGNet+LR/B (conc) · RF+feat78 (stress)</p>
        </div>
      </div>
    )
  }

  const conc   = prediction.concentration ?? {}
  const stress = prediction.stress        ?? {}
  const dominant = prediction.dominant ?? prediction.state ?? 'neutral'

  const concScore  = conc.score  ?? 0
  const stressScore = stress.score ?? 0
  const concPct    = Math.round((conc.pct  ?? concScore  * 10))
  const stressPct  = Math.round((stress.pct ?? stressScore * 10))

  const isConcActive   = concScore  >= 5.0
  const isStressActive = stressScore >= 5.0

  const DOMINANT_STYLES = {
    concentration: { label: '🎯 CONCENTRATION', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/25' },
    stress:        { label: '⚡ STRESS',          color: 'text-red-400',     bg: 'bg-red-500/10',     border: 'border-red-500/25'     },
    neutral:       { label: '😌 NEUTRE',           color: 'text-nc-muted',    bg: 'bg-nc-surface2',    border: 'border-nc-border'      },
  }
  const dom = DOMINANT_STYLES[dominant] ?? DOMINANT_STYLES.neutral

  const MetricBadge = ({ label, value }) => (
    <span className="text-[8px] font-mono text-nc-muted/60">{label}={value}</span>
  )

  const ScoreBar = ({ label, score, pct, active, color, model, metrics }) => (
    <div className={`rounded-xl p-3 border transition-all ${
      active
        ? color === 'emerald'
          ? 'bg-emerald-500/10 border-emerald-500/30'
          : 'bg-red-500/10 border-red-500/30'
        : 'bg-nc-surface2/50 border-nc-border'
    }`}>
      <div className="flex items-center justify-between mb-1.5">
        <div>
          <span className={`text-[10px] font-bold uppercase tracking-wide ${
            active
              ? color === 'emerald' ? 'text-emerald-400' : 'text-red-400'
              : 'text-nc-muted'
          }`}>{label}</span>
          <div className="flex gap-2 mt-0.5">
            <span className="text-[8px] font-mono text-nc-muted/50">{model}</span>
            {Object.entries(metrics).map(([k, v]) => (
              <MetricBadge key={k} label={k.toUpperCase()} value={v} />
            ))}
          </div>
        </div>
        <span className={`font-mono font-bold text-2xl ${
          active
            ? color === 'emerald' ? 'text-emerald-400' : 'text-red-400'
            : 'text-nc-muted'
        }`}>{Math.round(pct)}<span className="text-sm font-normal ml-0.5">%</span></span>
      </div>
      <div className="h-2.5 rounded-full bg-nc-surface overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            active
              ? color === 'emerald' ? 'bg-emerald-500' : 'bg-red-500'
              : 'bg-nc-muted/30'
          }`}
          style={{ width: `${Math.min(pct, 100)}%` }}
        />
      </div>
      <div className="flex justify-between mt-1">
        <span className="text-[8px] text-nc-muted/50">0%</span>
        <span className="text-[8px] text-nc-muted/50">⬆ seuil 50%</span>
        <span className="text-[8px] text-nc-muted/50">100%</span>
      </div>
    </div>
  )

  return (
    <div className={`card p-4 space-y-3 border ${dom.border} ${dom.bg}`}>
      {/* En-tête */}
      <div className="flex items-center justify-between">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-wider text-nc-muted">
            Dual IA · Fp2 monocanal
          </p>
          <p className="text-[8px] text-nc-muted/40 mt-0.5">LOSO inter-sujet · seuil 50 %</p>
        </div>
        <span className={`text-xs font-bold ${dom.color}`}>{dom.label}</span>
      </div>

      {/* Score Concentration — EEGNet+LR */}
      <ScoreBar
        label="Concentration"
        score={concScore}
        pct={concPct}
        active={isConcActive}
        color="emerald"
        model="EEGNet+LR/B"
        metrics={{ AUC: (conc.auc ?? 0.723).toFixed(3), "R²": (conc.r2 ?? 0.250).toFixed(3) }}
      />

      {/* Score Stress — RF feat78 */}
      <ScoreBar
        label="Stress"
        score={stressScore}
        pct={stressPct}
        active={isStressActive}
        color="red"
        model="RF+feat78"
        metrics={{
          AUC: (stress.auc ?? 0.668).toFixed(3),
          "R²":  (stress.r2  ?? 0.184).toFixed(3),
          MCC: (stress.mcc ?? 0.318).toFixed(3),
        }}
      />

      {prediction.uncertain && (
        <div className="p-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-[9px] text-yellow-300">
          ⚠ Un ou plusieurs modèles en erreur — résultat non fiable
        </div>
      )}
    </div>
  )
}

/* ── Popup "Passer au neurofeedback" ─────────────────────────────────────────── */
function FeedbackReadyPopup({ prediction, features, stableSeconds, onStart, onDismiss }) {
  const state    = prediction?.uncertain ? 'uncertain' : (prediction?.state ?? 'neutral')
  const conf     = Math.round((prediction?.confidence ?? 0) * 100)

  const LABEL = {
    concentration: { text: 'CONCENTRATION', color: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/30' },
    stress:        { text: 'STRESS',         color: 'text-red-400',     bg: 'bg-red-500/15',     border: 'border-red-500/30'     },
    neutral:       { text: 'NEUTRE',         color: 'text-nc-muted',    bg: 'bg-nc-surface2',    border: 'border-nc-border'      },
    uncertain:     { text: 'INCERTAIN',      color: 'text-yellow-400',  bg: 'bg-yellow-500/15',  border: 'border-yellow-500/30'  },
  }
  const lbl = LABEL[state] ?? LABEL.neutral

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
         style={{ background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(6px)' }}>
      <div className="card max-w-md w-full p-6 space-y-5 animate-fade-in">

        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-nc-accent/15 flex items-center justify-center">
              <Brain className="w-5 h-5 text-nc-accent" />
            </div>
            <div>
              <h2 className="text-base font-bold text-nc-text">Prêt pour le Neurofeedback</h2>
              <p className="text-xs text-nc-muted">Signal EEG analysé et stable</p>
            </div>
          </div>
          <button onClick={onDismiss} className="p-1.5 rounded-xl text-nc-muted hover:bg-nc-surface2 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* État EEG */}
        <div className={`p-3 rounded-xl border ${lbl.bg} ${lbl.border} space-y-2`}>
          <div className="flex items-center justify-between">
            <span className={`text-sm font-bold ${lbl.color}`}>
              🧠 {lbl.text}
            </span>
            <span className={`font-mono font-bold text-lg ${lbl.color}`}>{conf}%</span>
          </div>
          <p className="text-xs text-nc-muted">
            Stable depuis {stableSeconds}s · Signal qualifié sur les dernières époques
          </p>
        </div>

        {/* Features clés */}
        {features && (
          <div className="grid grid-cols-3 gap-2 text-xs">
            {[
              ['Alpha',     `${((features.rel_alpha  ?? 0) * 100).toFixed(1)}%`],
              ['Beta',      `${((features.rel_beta   ?? 0) * 100).toFixed(1)}%`],
              ['TBR',       (features.theta_beta ?? 0).toFixed(2)],
              ['EI',        (features.engagement ?? 0).toFixed(2)],
              ['Theta',     `${((features.rel_theta  ?? 0) * 100).toFixed(1)}%`],
              ['Confiance', `${conf}%`],
            ].map(([k, v]) => (
              <div key={k} className="card p-2 text-center">
                <p className="font-mono font-bold text-nc-text">{v}</p>
                <p className="text-nc-muted text-[9px] mt-0.5">{k}</p>
              </div>
            ))}
          </div>
        )}

        <p className="text-xs text-nc-muted leading-relaxed">
          Le système est prêt à démarrer une séance de feedback adaptée à votre profil neurophysiologique.
        </p>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={onStart}
            className="btn-primary flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl text-sm font-semibold"
          >
            <Sparkles className="w-4 h-4" />
            Démarrer le feedback →
          </button>
          <button
            onClick={onDismiss}
            className="btn-ghost px-4 py-2.5 rounded-xl text-sm text-nc-muted hover:text-nc-text border border-nc-border"
          >
            Continuer l'EEG
          </button>
        </div>
      </div>
    </div>
  )
}

/* ════════════════════════════════════════════════════════════════════════════════
   Page EEGLive
═══════════════════════════════════════════════════════════════════════════════ */
export default function EEGLive({ embedded = false }) {
  const navigate = useNavigate()

  const {
    connected, eegFrame, epochFrame, rejectedFrame, initFrame, esp32Status, send,
  } = useEEGWebSocket()

  const { rec, paused, recT, start: recStart, pause: recPause, resume: recResume, stop: recStop, fmt: recFmt } = useRecording()

  /* ── État local ── */
  const [status,        setStatus]        = useState(null)
  const [tab,           setTab]           = useState('signal')
  const [calProgress,   setCalProgress]   = useState(0)
  const [baselineOk,    setBaselineOk]    = useState(false)
  const [epochHistory,  setEpochHistory]  = useState([])
  const [showWifi,      setShowWifi]      = useState(false)
  const [mlPrediction,  setMlPrediction]  = useState(null)
  const [sessionStats,  setSessionStats]  = useState({ n_accepted: 0, n_rejected: 0, states: {} })
  const [sendRep,       setSendRep]       = useState({ loading: false, done: false, error: '' })

  const [showCalibration, setShowCalibration] = useState(false)

  /* ── Popup "Passer au feedback" ── */
  const [showFeedbackPopup,  setShowFeedbackPopup]  = useState(false)
  const [popupDismissed,     setPopupDismissed]     = useState(false)
  const classifiedCountRef  = useRef(0)      // total non-uncertain
  const consecutiveRef      = useRef(0)      // consécutives même label
  const lastLabelRef        = useRef(null)
  const stableSecondsRef    = useRef(0)
  const lastFeaturesRef     = useRef(null)

  /* ── Dérivés WebSocket ── */
  const esp32Connected = esp32Status?.connected ?? initFrame?.esp32_connected ?? false
  const wifiConfigured = initFrame?.wifi_configured ?? false
  const cognitiveState = epochFrame?.state ?? 'neutral'
  const electrodeOk   = eegFrame?.electrode_ok ?? initFrame?.electrode_ok ?? false
  const cqeScore      = epochFrame?.cqe_score ?? 0

  const bands = epochFrame?.features ? {
    delta:     epochFrame.features.rel_delta     ?? 0,
    theta:     epochFrame.features.rel_theta     ?? 0,
    alpha:     epochFrame.features.rel_alpha     ?? 0,
    beta:      epochFrame.features.rel_beta      ?? 0,
    beta_high: epochFrame.features.rel_beta_high ?? 0,
    gamma_low: epochFrame.features.rel_gamma_low ?? 0,
  } : {}

  /* ── Mises à jour depuis WS ── */
  useEffect(() => {
    if (eegFrame?.cal_progress !== undefined) setCalProgress(eegFrame.cal_progress)
  }, [eegFrame])

  useEffect(() => {
    if (!epochFrame) return
    if (epochFrame.ml_prediction) setMlPrediction(epochFrame.ml_prediction)
    if (epochFrame.features) lastFeaturesRef.current = epochFrame.features
    setEpochHistory(prev => [{
      ...epochFrame, _accepted: true, _ts: Date.now(),
    }, ...prev].slice(0, 80))
    setSessionStats(prev => {
      const states = { ...prev.states }
      const st = epochFrame.state ?? 'neutral'
      states[st] = (states[st] ?? 0) + 1
      return { ...prev, n_accepted: prev.n_accepted + 1, states }
    })

    // ── Logique popup feedback ──
    const ml = epochFrame.ml_prediction
    if (ml && !ml.uncertain && ml.state && ml.state !== 'uncertain') {
      classifiedCountRef.current += 1
      if (ml.state === lastLabelRef.current) {
        consecutiveRef.current += 1
        stableSecondsRef.current += 4
      } else {
        consecutiveRef.current = 1
        stableSecondsRef.current = 4
        lastLabelRef.current = ml.state
      }
      // Déclencher popup : 5 classifiées + 3 consécutives + baseline OK + pas encore dismissé
      if (
        classifiedCountRef.current >= 5 &&
        consecutiveRef.current >= 3 &&
        baselineOk &&
        !popupDismissed &&
        !showFeedbackPopup
      ) {
        setShowFeedbackPopup(true)
      }
    }
  }, [epochFrame])

  useEffect(() => {
    if (!rejectedFrame) return
    setEpochHistory(prev => [{
      ...rejectedFrame, _accepted: false, _ts: Date.now(),
    }, ...prev].slice(0, 80))
    setSessionStats(prev => ({ ...prev, n_rejected: prev.n_rejected + 1 }))
  }, [rejectedFrame])

  /* ── Statut initial — auto-ouvre WiFi si ESP32 non connecté ── */
  useEffect(() => {
    eegApi.status().then(s => {
      setStatus(s)
      setBaselineOk(s.baseline_ok)
      setCalProgress(s.cal_progress ?? 0)
      if (!s.esp32_connected) setShowWifi(true)
    }).catch(() => {})
  }, [])

  /* ── Envoi rapport au thérapeute ── */
  const handleSendReport = useCallback(async () => {
    setSendRep({ loading: true, done: false, error: '' })
    const total = Math.max(sessionStats.n_accepted, 1)
    const dominantEntry = Object.entries(sessionStats.states).sort(([, a], [, b]) => b - a)[0]
    try {
      await eegApi.sendReport({
        type:               'live',
        duration_s:         Math.round(sessionStats.n_accepted * 4),
        n_epochs_accepted:  sessionStats.n_accepted,
        n_epochs_rejected:  sessionStats.n_rejected,
        dominant_state:     dominantEntry?.[0] ?? 'neutral',
        concentration_pct:  Math.round(((sessionStats.states.focused ?? 0) / total) * 100),
        stress_pct:         Math.round(((sessionStats.states.stressed ?? 0) / total) * 100),
        uncertain_pct:      0,
        mean_confidence:    mlPrediction?.confidence ?? 0,
        states_json:        sessionStats.states,
      })
      setSendRep({ loading: false, done: true, error: '' })
      setTimeout(() => setSendRep(s => ({ ...s, done: false })), 5000)
    } catch (e) {
      setSendRep({ loading: false, done: false, error: e?.response?.data?.detail || e.message || 'Erreur' })
    }
  }, [sessionStats, mlPrediction])

  const handleFinaliseBaseline = async () => {
    try { const r = await eegApi.finaliseBaseline(); if (r.success) setBaselineOk(true) } catch {}
  }

  const handleStartFeedback = useCallback(() => {
    setShowFeedbackPopup(false)
    navigate('/neurofeedback?mode=live', {
      state: {
        eeg_state:                lastLabelRef.current ?? 'neutral',
        classification_confidence: mlPrediction?.confidence ?? 0,
        features_snapshot:         lastFeaturesRef.current,
      },
    })
  }, [navigate, mlPrediction])

  const handleDismissPopup = useCallback(() => {
    setShowFeedbackPopup(false)
    setPopupDismissed(true)
    // Réautoriser après 10 nouvelles époques
    setTimeout(() => setPopupDismissed(false), 40_000)
  }, [])

  const sm = STATE_META[cognitiveState] ?? STATE_META.neutral

  const TABS = [
    { key: 'signal',   Icon: Activity,  label: 'Signal'    },
    { key: 'features', Icon: BarChart3, label: 'Features'  },
    { key: 'history',  Icon: List,      label: 'Historique' },
    { key: 'report',   Icon: FileText,  label: 'Rapport'   },
  ]

  return (
    <div className={`max-w-7xl mx-auto px-4 sm:px-6 ${embedded ? 'py-4' : 'py-6'} space-y-5`}>

      {/* ══ Calibration Overlay ══════════════════════════════════════════════════ */}
      {showCalibration && (
        <CalibrationOverlay
          epochFrame={epochFrame}
          onClose={() => setShowCalibration(false)}
          onComplete={() => { setShowCalibration(false); setBaselineOk(true) }}
        />
      )}

      {/* ══ Popup Feedback ═══════════════════════════════════════════════════════ */}
      {showFeedbackPopup && (
        <FeedbackReadyPopup
          prediction={mlPrediction}
          features={lastFeaturesRef.current}
          stableSeconds={stableSecondsRef.current}
          onStart={handleStartFeedback}
          onDismiss={handleDismissPopup}
        />
      )}

      {/* ══ En-tête ══════════════════════════════════════════════════════════════ */}
      <div className="flex items-center gap-3 flex-wrap">
        {!embedded && (
          <button onClick={() => navigate('/eeg')}
            className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
        )}
        <div className="w-10 h-10 rounded-2xl flex items-center justify-center bg-cyan-500/15">
          <Activity className="w-5 h-5 text-nc-accent" />
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-nc-text">EEG Live</h1>
          <p className="text-sm text-nc-muted">Signal temps réel — 250 Hz · AD8232 + ESP32</p>
        </div>

        {/* Badges connexion */}
        <div className="flex items-center gap-2 flex-wrap">
          <span className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border
            ${connected
              ? 'bg-emerald-500/10 border-emerald-500/25 text-emerald-400'
              : 'bg-red-500/10 border-red-500/25 text-red-400'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
            {connected ? 'Backend OK' : 'Backend KO'}
          </span>

          <span className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border
            ${esp32Connected
              ? 'bg-blue-500/10 border-blue-500/25 text-blue-400'
              : 'bg-nc-surface2 border-nc-border text-nc-muted'}`}>
            {esp32Connected ? <Radio className="w-3.5 h-3.5" /> : <WifiOff className="w-3.5 h-3.5" />}
            {esp32Connected ? `ESP32 · ${initFrame?.esp32_ip ?? ''}` : 'ESP32 non connecté'}
          </span>

          {rec && (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                             border bg-red-500/10 border-red-500/25 text-red-400">
              <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
              REC {recFmt(recT)}
            </span>
          )}

          {/* ── Bouton Neurofeedback permanent ── */}
          <button
            onClick={() => navigate('/neurofeedback?mode=live', {
              state: {
                eeg_state:                mlPrediction?.state ?? 'neutral',
                classification_confidence: mlPrediction?.confidence ?? 0,
                features_snapshot:         lastFeaturesRef.current,
              },
            })}
            disabled={!mlPrediction}
            title={!mlPrediction ? 'Attendez la première classification ML' : 'Démarrer le neurofeedback adaptatif'}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all
              ${mlPrediction
                ? 'bg-nc-accent/12 border-nc-accent/35 text-nc-accent hover:bg-nc-accent/22'
                : 'border-nc-border/40 text-nc-muted/40 cursor-not-allowed'}`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            Neurofeedback
          </button>

          {/* ── Bouton Calibration EEG ── */}
          <button
            onClick={() => setShowCalibration(true)}
            disabled={!esp32Connected}
            title={!esp32Connected ? 'Connectez l\'ESP32 avant de démarrer la calibration' : 'Calibration EEG automatisée (8 min)'}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition-all
              ${esp32Connected
                ? 'bg-amber-500/12 border-amber-500/35 text-amber-400 hover:bg-amber-500/22'
                : 'border-nc-border/40 text-nc-muted/40 cursor-not-allowed'}`}
          >
            <Brain className="w-3.5 h-3.5" />
            Calibration
          </button>

          <button onClick={() => setShowWifi(v => !v)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                       border border-nc-border text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
            <Wifi className="w-3.5 h-3.5" /> Config WiFi
          </button>
        </div>
      </div>

      {/* ══ Panneau WiFi collapsible ═════════════════════════════════════════════ */}
      {showWifi && <WifiSetupCard status={status} onClose={() => setShowWifi(false)} />}

      {/* ══ Suggestion guide électrodes ═════════════════════════════════════════ */}
      {!esp32Connected && !showWifi && (
        <div className="card p-4 flex items-center gap-4 border-nc-accent/25">
          <div className="w-10 h-10 rounded-xl bg-nc-accent/10 flex items-center justify-center shrink-0">
            <Brain className="w-5 h-5 text-nc-accent" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-semibold text-nc-text">Pas encore configuré ?</p>
            <p className="text-xs text-nc-muted">Consultez le guide de pose des électrodes avant de commencer.</p>
          </div>
          <button onClick={() => navigate('/electrode-guide')}
            className="btn-ghost flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm
                       text-nc-accent border border-nc-accent/30 hover:bg-nc-accent/10 shrink-0">
            Guide électrodes <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* ══ Barre état cognitif ══════════════════════════════════════════════════ */}
      <div className={`card p-4 flex items-center gap-4 ${sm.bg}`}>
        <span className={`w-3 h-3 rounded-full ${sm.dot} ${cognitiveState === 'focused' ? 'animate-pulse' : ''}`} />
        <div className="flex-1 min-w-0">
          <p className={`font-semibold text-sm ${sm.color}`}>{sm.label}</p>
          <p className="text-xs text-nc-muted truncate">
            CQE {cqeScore}% · Cal. {Math.round(calProgress * 100)}%
            {baselineOk && ' · Baseline ✓'}
            {electrodeOk
              ? <span className="text-emerald-400"> · Électrode OK</span>
              : <span className="text-red-400"> · Électrode KO</span>}
          </p>
        </div>

        {/* Calibration action */}
        {!baselineOk && calProgress >= 0.5 && (
          <button onClick={handleFinaliseBaseline}
            className="btn-primary px-4 py-2 rounded-xl text-xs font-semibold shrink-0">
            Finaliser baseline
          </button>
        )}
        {!baselineOk && calProgress < 0.5 && (
          <div className="text-xs text-nc-muted shrink-0">
            {Math.round(calProgress * 100)}% — gardez l'électrode en place
          </div>
        )}
      </div>

      {/* ══ Onglets ══════════════════════════════════════════════════════════════ */}
      <div className="flex gap-0.5 border-b border-nc-border overflow-x-auto">
        {TABS.map(({ key, Icon, label }) => (
          <button key={key} onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-all -mb-px whitespace-nowrap
              ${tab === key
                ? 'border-nc-accent text-nc-accent'
                : 'border-transparent text-nc-muted hover:text-nc-text'}`}>
            <Icon className="w-4 h-4" />{label}
          </button>
        ))}
      </div>

      {/* ════════════════════════ SIGNAL ════════════════════════════════════════ */}
      {tab === 'signal' && (
        <div className="space-y-4">

          {/* Oscilloscope + ML Classifier */}
          <div className="grid lg:grid-cols-3 gap-4">
            <div className="lg:col-span-2 card overflow-hidden p-2" style={{ height: 310 }}>
              <SignalCanvas wsData={eegFrame} electrodeOk={electrodeOk} cognitiveState={cognitiveState} />
            </div>
            <DualClassifierCard prediction={mlPrediction} />
          </div>

          {/* ── Carte de lancement Neurofeedback ── */}
          {mlPrediction && !mlPrediction.uncertain && (
            <div className={`card p-4 flex items-center gap-4 flex-wrap border
              ${mlPrediction.state === 'concentration'
                ? 'border-emerald-500/25 bg-emerald-500/5'
                : mlPrediction.state === 'stress'
                ? 'border-red-500/25 bg-red-500/5'
                : 'border-nc-accent/20'}`}>
              <div className="w-10 h-10 rounded-2xl bg-nc-accent/15 flex items-center justify-center shrink-0">
                <Sparkles className="w-5 h-5 text-nc-accent" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-nc-text">Démarrer le neurofeedback adaptatif</p>
                <p className="text-xs text-nc-muted mt-0.5 leading-relaxed">
                  État classifié : <span className={sm.color}>{sm.label}</span>
                  {' · '}Confiance {Math.round((mlPrediction.confidence ?? 0) * 100)}%
                  {' · '}Feedback, justification et guide personnalisés selon vos features EEG
                </p>
              </div>
              <button
                onClick={() => navigate('/eeg-feedback', {
                  state: {
                    source:     'live',
                    eegState:   mlPrediction.state ?? 'neutral',
                    confidence: mlPrediction.confidence ?? 0,
                    features:   lastFeaturesRef.current,
                  },
                })}
                className="btn-primary flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold shrink-0"
              >
                <Sparkles className="w-4 h-4" />
                Lancer →
              </button>
            </div>
          )}

          {/* Métriques rapides */}
          {eegFrame && (() => {
            const settling = eegFrame.raw_metrics?.settling !== false
            // Affiche la valeur si dans la plage physiologique EEG, sinon masque
            const fmtUV = (v, maxPhysio = 500) => {
              if (!electrodeOk || settling) return '— cal —'
              const n = v ?? 0
              if (Math.abs(n) > maxPhysio) return '⚠ hors-plage'
              return `${n.toFixed(1)} µV`
            }
            // Batterie LiPo : 4.2 V = 100 %, 3.0 V = 0 %
            const battV   = eegFrame.batt_V ?? 0
            const battPct = Math.min(100, Math.max(0, Math.round(((battV - 3.0) / 1.2) * 100)))
            const battColor = battPct > 60 ? 'text-emerald-400'
                            : battPct > 20 ? 'text-yellow-400'
                            : 'text-red-400'
            const battBarColor = battPct > 60 ? 'bg-emerald-500'
                               : battPct > 20 ? 'bg-yellow-500'
                               : 'bg-red-500'

            return (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
                {[
                  { label: 'Signal filtré',   value: fmtUV(eegFrame.filtered, 300),
                    warn: !settling && electrodeOk && Math.abs(eegFrame.filtered ?? 0) > 150 },
                  { label: 'RMS signal',      value: fmtUV(eegFrame.raw_metrics?.rms_raw, 150),
                    warn: !settling && electrodeOk && (eegFrame.raw_metrics?.rms_raw ?? 0) > 80 },
                  { label: 'Pic (Peak)',      value: fmtUV(eegFrame.raw_metrics?.peak, 500),
                    warn: !settling && electrodeOk && (eegFrame.raw_metrics?.peak ?? 0) > 250 },
                  { label: 'Époques OK',      value: sessionStats.n_accepted },
                ].map(({ label, value, warn }) => (
                  <div key={label} className={`card p-3 text-center ${warn ? 'border border-yellow-500/30' : ''}`}>
                    <p className={`text-base font-bold font-mono ${warn ? 'text-yellow-400' : settling ? 'text-nc-muted/40' : 'text-nc-text'}`}>{value}</p>
                    <p className="text-[10px] text-nc-muted mt-0.5">{label}</p>
                  </div>
                ))}

                {/* Batterie ESP32 — affichage en pourcentage avec jauge */}
                <div className="card p-3 text-center space-y-1.5">
                  <p className={`text-base font-bold font-mono ${battColor}`}>
                    {battV > 0 ? `${battPct}%` : '—'}
                  </p>
                  {battV > 0 && (
                    <div className="flex items-center gap-1 px-1">
                      <div className="flex-1 h-1.5 rounded-full bg-nc-surface2 overflow-hidden">
                        <div
                          className={`h-full rounded-full transition-all duration-500 ${battBarColor}`}
                          style={{ width: `${battPct}%` }}
                        />
                      </div>
                      {/* Corps batterie */}
                      <div className="flex items-center shrink-0">
                        <div className={`w-5 h-3 rounded-sm border ${battColor.replace('text-', 'border-')}/60
                                        flex items-center px-0.5 gap-0.5`}>
                          {[0,1,2,3].map(i => (
                            <div key={i} className={`flex-1 h-1.5 rounded-sm
                              ${i < Math.ceil(battPct / 25) ? battBarColor : 'bg-nc-surface2'}`} />
                          ))}
                        </div>
                        <div className={`w-0.5 h-1.5 rounded-r ${battBarColor} opacity-70`} />
                      </div>
                    </div>
                  )}
                  <p className="text-[10px] text-nc-muted">
                    Batterie ESP32{battV > 0 ? ` · ${battV.toFixed(2)} V` : ''}
                  </p>
                </div>
              </div>
            )
          })()}

          {/* Bandes spectrales */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-nc-text mb-4">Bandes de fréquences</h3>
            <BandBars bands={bands} />
          </div>

          {/* Contrôles enregistrement */}
          <div className="flex flex-wrap gap-3 items-center">
            {!rec ? (
              <button onClick={recStart}
                className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold
                           bg-red-500/10 border border-red-500/25 text-red-400 hover:bg-red-500/15 transition-all">
                <Circle className="w-4 h-4" /> Démarrer REC
              </button>
            ) : (
              <>
                {paused ? (
                  <button onClick={recResume}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold
                               bg-emerald-500/10 border border-emerald-500/25 text-emerald-400">
                    <Play className="w-4 h-4" /> Reprendre
                  </button>
                ) : (
                  <button onClick={recPause}
                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold
                               bg-yellow-500/10 border border-yellow-500/25 text-yellow-400">
                    <Pause className="w-4 h-4" /> Pause
                  </button>
                )}
                <button onClick={recStop}
                  className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold
                             bg-nc-surface2 border border-nc-border text-nc-muted hover:text-nc-text">
                  <Square className="w-4 h-4" /> Arrêter
                </button>
              </>
            )}

            <a href="/api/eeg/recording/export"
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold
                         bg-nc-surface2 border border-nc-border text-nc-muted hover:text-nc-text transition-colors">
              <Download className="w-4 h-4" /> Export CSV
            </a>

            <button onClick={() => send('ANALYZE_NOW')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold
                         bg-nc-surface2 border border-nc-border text-nc-muted hover:text-nc-text">
              <RefreshCw className="w-4 h-4" /> Analyser
            </button>
          </div>
        </div>
      )}

      {/* ════════════════════════ FEATURES ══════════════════════════════════════ */}
      {tab === 'features' && (
        <div className="space-y-4">
          {/* Artefacts — bandeau rapide */}
          {epochFrame?.eog_detected !== undefined && (
            <div className="card p-3 flex flex-wrap items-center gap-4 text-xs">
              <span className="text-nc-muted font-semibold">Artefacts :</span>
              <span className={epochFrame.eog_detected ? 'text-yellow-400 font-semibold' : 'text-emerald-400'}>
                {epochFrame.eog_detected ? '⚠ EOG détecté' : '✓ EOG OK'}
              </span>
              <span className={epochFrame.emg_suspect ? 'text-orange-400 font-semibold' : 'text-emerald-400'}>
                {epochFrame.emg_suspect ? '⚠ EMG suspect' : '✓ EMG OK'}
              </span>
              {epochFrame.features?.emg_ratio !== undefined && (
                <span className="text-nc-muted font-mono">
                  EMG ratio : {((epochFrame.features.emg_ratio ?? 0) * 100).toFixed(1)}%
                </span>
              )}
            </div>
          )}

          {epochFrame?.features ? (
            <FeaturesPanel features={epochFrame.features} epochIdx={epochFrame.epoch_idx} />
          ) : (
            <div className="card p-12 text-center space-y-3">
              <p className="text-3xl">📊</p>
              <p className="text-sm text-nc-muted">En attente de la première époque (4 s de signal valide)…</p>
              <p className="text-xs text-nc-muted/60">Fenêtre 4 s · Overlap 75% · Welch PSD</p>
            </div>
          )}

          {/* ML card dans features */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-nc-text mb-4">Prédiction EEGNet (DL/TL)</h3>
            <DualClassifierCard prediction={mlPrediction} />
          </div>
        </div>
      )}

      {/* ════════════════════════ HISTORIQUE ════════════════════════════════════ */}
      {tab === 'history' && (
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-nc-border flex items-center justify-between flex-wrap gap-2">
            <h3 className="text-sm font-semibold text-nc-text">Époque par époque</h3>
            <div className="flex items-center gap-3 text-xs">
              <span className="text-emerald-400">{sessionStats.n_accepted} acceptées</span>
              <span className="text-red-400">{sessionStats.n_rejected} rejetées</span>
              <span className="text-nc-muted">{epochHistory.length} affichées</span>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-nc-border bg-nc-surface2/40">
                  {['#', 'Statut', 'État DSP', 'LightGBM', 'Conf.', 'Alpha', 'Beta', 'Theta', 'Artefact / Raison'].map(h => (
                    <th key={h} className="px-3 py-2 text-start text-nc-muted font-semibold uppercase tracking-wide text-[10px]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {epochHistory.map((ep, i) => {
                  const f   = ep.features ?? {}
                  const ml  = ep.ml_prediction
                  const stm = STATE_META[ep.state] ?? STATE_META.neutral
                  const mlState = ml ? (ml.uncertain ? 'uncertain' : ml.state) : null
                  const ML_STYLES = {
                    concentration: { label: '🎯 Concentr.', color: 'text-emerald-400' },
                    stress:        { label: '⚡ Stress',     color: 'text-red-400'     },
                    uncertain:     { label: '⚠ Incertain',  color: 'text-yellow-400'  },
                  }
                  const mlMeta = mlState ? ML_STYLES[mlState] : null

                  return (
                    <tr key={i} className={`border-b border-nc-border transition-colors
                      ${ep._accepted ? 'hover:bg-nc-surface2/40' : 'bg-red-500/3 hover:bg-red-500/8'}`}>
                      <td className="px-3 py-2 font-mono text-nc-muted">{ep.epoch_idx ?? i}</td>
                      <td className="px-3 py-2">
                        {ep._accepted
                          ? <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">✓ OK</span>
                          : <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-red-500/10 text-red-400 border border-red-500/20">✕ Rejeté</span>}
                      </td>
                      <td className="px-3 py-2">
                        {ep._accepted
                          ? <span className={`text-[10px] font-semibold ${stm.color}`}>{stm.label}</span>
                          : <span className="text-nc-muted text-[10px]">—</span>}
                      </td>
                      <td className="px-3 py-2">
                        {mlMeta
                          ? <span className={`text-[10px] font-semibold ${mlMeta.color}`}>{mlMeta.label}</span>
                          : <span className="text-nc-muted">—</span>}
                      </td>
                      <td className="px-3 py-2 font-mono">
                        {ml ? `${Math.round((ml.confidence ?? 0) * 100)}%` : '—'}
                      </td>
                      <td className="px-3 py-2 font-mono">
                        {f.rel_alpha != null ? `${(f.rel_alpha * 100).toFixed(1)}%` : '—'}
                      </td>
                      <td className="px-3 py-2 font-mono">
                        {f.rel_beta != null ? `${(f.rel_beta * 100).toFixed(1)}%` : '—'}
                      </td>
                      <td className="px-3 py-2 font-mono">
                        {f.rel_theta != null ? `${(f.rel_theta * 100).toFixed(1)}%` : '—'}
                      </td>
                      <td className="px-3 py-2 text-nc-muted">
                        {ep._accepted
                          ? (ep.artifacts?.eog_detected
                              ? <span className="text-yellow-400">EOG</span>
                              : ep.artifacts?.emg_suspect
                              ? <span className="text-orange-400">EMG</span>
                              : '—')
                          : <span className="text-red-400">
                              {REJECT_REASON[ep.reason] ?? ep.reason ?? 'Inconnu'}
                            </span>}
                      </td>
                    </tr>
                  )
                })}
                {epochHistory.length === 0 && (
                  <tr>
                    <td colSpan={9} className="px-4 py-10 text-center text-nc-muted">
                      Aucune époque — en attente de 4 s de signal valide…
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ════════════════════════ RAPPORT ═══════════════════════════════════════ */}
      {tab === 'report' && (
        <div className="space-y-5">

          {/* Stats session */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            {[
              { label: 'Époques acceptées', value: sessionStats.n_accepted, color: 'text-emerald-400' },
              { label: 'Époques rejetées',  value: sessionStats.n_rejected,  color: 'text-red-400'     },
              { label: 'Calibration',       value: `${Math.round(calProgress * 100)}%`, color: 'text-blue-400' },
              { label: 'Baseline',          value: baselineOk ? 'OK ✓' : 'En cours',   color: baselineOk ? 'text-emerald-400' : 'text-yellow-400' },
            ].map(({ label, value, color }) => (
              <div key={label} className="card p-4 text-center">
                <p className={`text-2xl font-bold font-mono ${color}`}>{value}</p>
                <p className="text-xs text-nc-muted mt-1">{label}</p>
              </div>
            ))}
          </div>

          {/* Distribution états cognitifs */}
          {Object.keys(sessionStats.states).length > 0 && (
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-nc-text mb-4">Distribution des états (Z-score DSP)</h3>
              <div className="space-y-3">
                {Object.entries(sessionStats.states)
                  .sort(([, a], [, b]) => b - a)
                  .map(([state, count]) => {
                    const stm = STATE_META[state] ?? STATE_META.neutral
                    const pct = sessionStats.n_accepted > 0
                      ? Math.round((count / sessionStats.n_accepted) * 100)
                      : 0
                    return (
                      <div key={state}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className={stm.color}>{stm.label}</span>
                          <span className="font-mono text-nc-text">{count} époques ({pct}%)</span>
                        </div>
                        <div className="h-2 rounded-full bg-nc-surface2 overflow-hidden">
                          <div className={`h-full rounded-full ${stm.dot} transition-all`}
                               style={{ width: `${pct}%` }} />
                        </div>
                      </div>
                    )
                  })}
              </div>
            </div>
          )}

          {/* Informations système */}
          <div className="card p-5 space-y-3">
            <h3 className="text-sm font-semibold text-nc-text">Informations système</h3>
            {[
              ['ESP32 connecté',     esp32Connected ? 'Oui' : 'Non',       esp32Connected ? 'text-emerald-400' : 'text-red-400'],
              ['IP ESP32',           initFrame?.esp32_ip ?? '—',           'text-nc-text'],
              ['WiFi configuré',     wifiConfigured ? 'Oui' : 'Non',       wifiConfigured ? 'text-emerald-400' : 'text-nc-muted'],
              ['Électrode',          electrodeOk ? 'OK' : 'KO',           electrodeOk ? 'text-emerald-400' : 'text-red-400'],
              ['CQE signal',         `${cqeScore}%`,                       cqeScore >= 60 ? 'text-emerald-400' : 'text-yellow-400'],
              ['Enregistrement',     rec ? `En cours ${recFmt(recT)}` : 'Arrêté', rec ? 'text-red-400' : 'text-nc-muted'],
            ].map(([label, value, color]) => (
              <div key={label} className="flex justify-between items-center text-xs py-1.5 border-b border-nc-border/30 last:border-0">
                <span className="text-nc-muted">{label}</span>
                <span className={`font-mono font-semibold ${color}`}>{value}</span>
              </div>
            ))}
          </div>

          {/* Dernière classification ML */}
          {mlPrediction && (
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-nc-text mb-4">Dernière prédiction EEGNet (DL/TL)</h3>
              <DualClassifierCard prediction={mlPrediction} />
            </div>
          )}

          {/* ── Envoyer au thérapeute ── */}
          <div className="card p-5 space-y-3">
            <h3 className="text-sm font-semibold text-nc-text">Partager avec le thérapeute</h3>
            <p className="text-xs text-nc-muted">
              Envoyez ce rapport de session ({sessionStats.n_accepted} époques acceptées) directement
              dans le dossier de votre thérapeute.
            </p>
            {sendRep.error && (
              <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-300">
                {sendRep.error}
              </div>
            )}
            <button
              onClick={handleSendReport}
              disabled={sendRep.loading || sendRep.done || sessionStats.n_accepted === 0}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all
                disabled:opacity-50
                ${sendRep.done
                  ? 'bg-emerald-500/15 border border-emerald-500/30 text-emerald-400'
                  : 'btn-primary'}`}
            >
              <Send className="w-4 h-4" />
              {sendRep.done
                ? '✓ Rapport envoyé au thérapeute'
                : sendRep.loading
                ? 'Envoi en cours…'
                : 'Envoyer au thérapeute'}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
