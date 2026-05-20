import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Wifi, WifiOff, Activity, Download, Pause, Play, Square, Circle,
  CheckCircle2, Radio, RefreshCw, ChevronRight, Brain, BarChart3,
  List, FileText, ArrowLeft, Send,
} from 'lucide-react'
import SignalCanvas      from '../components/eeg/SignalCanvas'
import BandBars          from '../components/eeg/BandBars'
import { useEEGWebSocket } from '../hooks/useEEGWebSocket'
import { useRecording }    from '../hooks/useRecording'
import { eeg as eegApi }   from '../utils/api'

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

/* ── Carte ML Classifier (LightGBM) ──────────────────────────────────────────── */
function MLClassifierCard({ prediction }) {
  if (!prediction) {
    return (
      <div className="card p-5 flex flex-col items-center justify-center gap-3 text-center min-h-[160px]">
        <Brain className="w-8 h-8 text-nc-muted/30" />
        <div>
          <p className="text-xs text-nc-muted">En attente de la première époque…</p>
          <p className="text-[10px] text-nc-muted/50 mt-0.5">63 features FeatEng · LightGBM LOSO</p>
        </div>
      </div>
    )
  }

  const isUncertain = prediction.uncertain
  const state   = isUncertain ? 'uncertain' : prediction.state
  const conf    = Math.round((prediction.confidence    ?? 0) * 100)
  const concPct = Math.round((prediction.concentration ?? 0) * 100)
  const stPct   = Math.round((prediction.stress        ?? 0) * 100)

  const STYLES = {
    concentration: { label: '🎯 CONCENTRATION', color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', bar: 'bg-emerald-500' },
    stress:        { label: '⚡ STRESS',          color: 'text-red-400',     bg: 'bg-red-500/10',     border: 'border-red-500/25',     bar: 'bg-red-500'     },
    uncertain:     { label: '⚠ INCERTAIN',        color: 'text-yellow-400',  bg: 'bg-yellow-500/10',  border: 'border-yellow-500/25',  bar: 'bg-yellow-500'  },
  }
  const st = STYLES[state] ?? STYLES.uncertain

  return (
    <div className={`card p-5 space-y-4 border ${st.border} ${st.bg}`}>
      <div className="flex items-center justify-between">
        <p className="text-[10px] font-semibold uppercase tracking-wider text-nc-muted">LightGBM · FeatEng</p>
        <span className="text-[10px] font-mono text-nc-muted">63 features</span>
      </div>

      <div className="flex items-center justify-between">
        <span className={`text-sm font-bold ${st.color}`}>{st.label}</span>
        <span className={`font-mono font-bold text-2xl ${st.color}`}>{conf}%</span>
      </div>

      {/* Barres probabilité */}
      <div className="space-y-2">
        {[
          { label: 'Concentration', pct: concPct, bar: 'bg-emerald-500' },
          { label: 'Stress',        pct: stPct,   bar: 'bg-red-500'     },
        ].map(({ label, pct, bar }) => (
          <div key={label}>
            <div className="flex justify-between text-[10px] mb-0.5">
              <span className="text-nc-muted">{label}</span>
              <span className="font-mono font-semibold text-nc-text">{pct}%</span>
            </div>
            <div className="h-1.5 rounded-full bg-nc-surface2 overflow-hidden">
              <div className={`h-full rounded-full ${bar} transition-all duration-500`} style={{ width: `${pct}%` }} />
            </div>
          </div>
        ))}
      </div>

      {isUncertain && (
        <div className="p-2 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-[10px] text-yellow-300">
          ⚠ Confiance {conf}% {'<'} 60% — époque incertaine (CdC §2.5.1)
        </div>
      )}
    </div>
  )
}

/* ── Panneau WiFi (inline collapsible) ───────────────────────────────────────── */
function WifiSetupCard({ status, onClose }) {
  const [networks, setNetworks] = useState([])
  const [ssid,     setSsid]     = useState('')
  const [password, setPassword] = useState('')
  const [phase,    setPhase]    = useState('idle') // idle | confirming | waiting | done | error
  const [errMsg,   setErrMsg]   = useState('')
  const [pending,  setPending]  = useState('')
  const pollRef = useRef(null)

  useEffect(() => {
    eegApi.wifiNetworks().then(d => setNetworks(d.networks || [])).catch(() => {})
  }, [])

  function startPolling() {
    clearInterval(pollRef.current)
    let tries = 0
    pollRef.current = setInterval(async () => {
      tries++
      if (tries > 90) { clearInterval(pollRef.current); setPhase('error'); setErrMsg('Timeout 90s — vérifiez SSID et mot de passe'); return }
      try {
        const s = await eegApi.status()
        if (s.wifi_result?.success)          { clearInterval(pollRef.current); setPhase('done') }
        else if (s.wifi_result?.success === false) { clearInterval(pollRef.current); setPhase('error'); setErrMsg(`Échec : ${s.wifi_result.reason ?? 'réseau introuvable'}`) }
      } catch {}
    }, 1000)
  }

  async function doConnect() {
    setPhase('waiting'); setErrMsg('')
    try {
      if (networks.includes(pending) && !password) await eegApi.wifiUseSaved(pending)
      else await eegApi.wifiConfigure(pending || ssid, password)
      startPolling()
    } catch (e) { setPhase('error'); setErrMsg(e?.response?.data?.error || e.message) }
  }

  function submitNew(e) {
    e.preventDefault()
    if (!ssid.trim()) return
    setPending(ssid.trim())
    setPhase('confirming')
  }

  useEffect(() => () => clearInterval(pollRef.current), [])

  if (phase === 'done') return (
    <div className="card p-8 text-center space-y-4">
      <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
      <p className="font-semibold text-nc-text">WiFi configuré !</p>
      <p className="text-xs text-nc-muted">ESP32 connecté. Reconnectez votre PC à votre réseau WiFi domestique si nécessaire.</p>
      <button onClick={onClose} className="btn-primary px-6 py-2.5 rounded-xl text-sm font-semibold">
        Voir le signal EEG →
      </button>
    </div>
  )

  if (phase === 'confirming') return (
    <div className="card p-6 space-y-4">
      <p className="text-sm font-semibold text-nc-text">Confirmer la connexion</p>
      <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-sm text-nc-text">
        Réseau : <strong>{pending}</strong>
      </div>
      <div className="space-y-1">
        <label className="text-xs text-nc-muted">Mot de passe {networks.includes(pending) ? '(optionnel si mémorisé)' : ''}</label>
        <input type="password" className="input w-full" value={password}
          onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
      </div>
      <div className="flex gap-3">
        <button onClick={doConnect} className="btn-primary flex-1 py-2.5 rounded-xl text-sm font-semibold">Confirmer</button>
        <button onClick={() => setPhase('idle')} className="btn-ghost flex-1 py-2.5 rounded-xl text-sm">Annuler</button>
      </div>
    </div>
  )

  if (phase === 'waiting') return (
    <div className="card p-8 text-center space-y-4">
      <div className="w-10 h-10 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin mx-auto" />
      <p className="text-sm text-nc-text">Connexion de l'ESP32 à <strong>{pending}</strong>…</p>
      <p className="text-xs text-nc-muted">Attente de confirmation (jusqu'à 90 s)</p>
    </div>
  )

  return (
    <div className="card p-6 space-y-5">
      <div className="flex items-center gap-2">
        <Wifi className="w-5 h-5 text-nc-accent" />
        <h3 className="font-semibold text-nc-text text-sm">Configuration WiFi ESP32</h3>
      </div>

      <div className="p-3 rounded-xl bg-blue-500/8 border border-blue-500/20 text-xs text-blue-300 leading-relaxed">
        <strong>Procédure :</strong> Connectez d'abord votre PC au hotspot{' '}
        <code className="bg-black/30 px-1 rounded">NeuroCap-XXXX</code> affiché sur l'ESP32,
        puis entrez les identifiants de votre réseau WiFi domestique (2,4 GHz uniquement).
      </div>

      {errMsg && (
        <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-300">{errMsg}</div>
      )}
      {status?.esp32_ap_detected && (
        <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300">
          📡 ESP32 détecté : <strong>{status.esp32_ap_ssid}</strong>
        </div>
      )}

      {networks.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold text-nc-muted uppercase tracking-wide mb-2">Réseaux mémorisés</p>
          <div className="space-y-1">
            {networks.map(net => (
              <button key={net} onClick={() => { setPending(net); setPhase('confirming') }}
                className="w-full flex items-center justify-between px-3 py-2 rounded-xl
                           bg-blue-500/5 border border-blue-500/15 hover:bg-blue-500/10 text-sm text-nc-text transition-colors">
                <span className="flex items-center gap-2">
                  <Wifi className="w-3.5 h-3.5 text-nc-accent" />{net}
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-nc-muted" />
              </button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={submitNew} className="space-y-3">
        <p className="text-[10px] font-semibold text-nc-muted uppercase tracking-wide">Nouveau réseau</p>
        <div className="space-y-1">
          <label className="text-xs text-nc-muted">SSID (2,4 GHz uniquement)</label>
          <input type="text" className="input w-full" value={ssid}
            onChange={e => setSsid(e.target.value)} placeholder="MonWiFi_2.4G" autoComplete="off" />
        </div>
        <div className="space-y-1">
          <label className="text-xs text-nc-muted">Mot de passe</label>
          <input type="password" className="input w-full" value={password}
            onChange={e => setPassword(e.target.value)} placeholder="••••••••" autoComplete="off" />
        </div>
        <button type="submit" disabled={!ssid.trim()}
          className="btn-primary w-full py-2.5 rounded-xl text-sm font-semibold disabled:opacity-40">
          📡 Configurer l'ESP32
        </button>
      </form>

      <button onClick={() => eegApi.wifiReset().catch(() => {})}
        className="text-xs text-nc-danger hover:underline w-full text-center">
        Effacer les réseaux mémorisés (reset)
      </button>
    </div>
  )
}

/* ════════════════════════════════════════════════════════════════════════════════
   Page EEGLive
═══════════════════════════════════════════════════════════════════════════════ */
export default function EEGLive() {
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

  /* ── Dérivés WebSocket ── */
  const esp32Connected = esp32Status?.connected ?? initFrame?.esp32_connected ?? false
  const wifiConfigured = initFrame?.wifi_configured ?? false
  const cognitiveState = epochFrame?.state ?? 'neutral'
  const electrodeOk   = eegFrame?.electrode_ok ?? initFrame?.electrode_ok ?? true
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
    setEpochHistory(prev => [{
      ...epochFrame, _accepted: true, _ts: Date.now(),
    }, ...prev].slice(0, 80))
    setSessionStats(prev => {
      const states = { ...prev.states }
      const st = epochFrame.state ?? 'neutral'
      states[st] = (states[st] ?? 0) + 1
      return { ...prev, n_accepted: prev.n_accepted + 1, states }
    })
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

  const sm = STATE_META[cognitiveState] ?? STATE_META.neutral

  const TABS = [
    { key: 'signal',   Icon: Activity,  label: 'Signal'    },
    { key: 'features', Icon: BarChart3, label: 'Features'  },
    { key: 'history',  Icon: List,      label: 'Historique' },
    { key: 'report',   Icon: FileText,  label: 'Rapport'   },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 space-y-5">

      {/* ══ En-tête ══════════════════════════════════════════════════════════════ */}
      <div className="flex items-center gap-3 flex-wrap">
        <button onClick={() => navigate('/eeg')}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="w-10 h-10 rounded-2xl flex items-center justify-center bg-cyan-500/15">
          <Activity className="w-5 h-5 text-nc-accent" />
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-nc-text">EEG Live</h1>
          <p className="text-sm text-nc-muted">Signal temps réel — Fp2 · 250 Hz · AD8232 + ESP32</p>
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
              ? <span className="text-emerald-400"> · Fp2 OK</span>
              : <span className="text-red-400"> · Fp2 KO</span>}
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
            <div className="lg:col-span-2 card overflow-hidden p-2" style={{ height: 260 }}>
              <SignalCanvas wsData={eegFrame} electrodeOk={electrodeOk} cognitiveState={cognitiveState} />
            </div>
            <MLClassifierCard prediction={mlPrediction} />
          </div>

          {/* Métriques rapides */}
          {eegFrame && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {[
                { label: 'Amplitude brute', value: `${Math.round(eegFrame.uv ?? 0)} µV` },
                { label: 'Filtré',          value: `${(eegFrame.filtered ?? 0).toFixed(1)} µV` },
                { label: 'Batterie ESP32',  value: `${(eegFrame.batt_V ?? 0).toFixed(2)} V` },
                { label: 'Époques OK',      value: sessionStats.n_accepted },
              ].map(({ label, value }) => (
                <div key={label} className="card p-3 text-center">
                  <p className="text-base font-bold font-mono text-nc-text">{value}</p>
                  <p className="text-[10px] text-nc-muted mt-0.5">{label}</p>
                </div>
              ))}
            </div>
          )}

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
          <div className="grid md:grid-cols-2 gap-4">

            {/* Puissances relatives */}
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-nc-text mb-4">Puissances spectrales relatives</h3>
              <BandBars bands={bands} />
            </div>

            {/* Ratios cognitifs */}
            <div className="card p-5 space-y-3">
              <h3 className="text-sm font-semibold text-nc-text">Ratios cognitifs</h3>
              {epochFrame?.features ? (
                [
                  ['Engagement (β / θ+α)',     epochFrame.features.engagement,      true  ],
                  ['Stress idx (β / α)',        epochFrame.features.stress_idx,      false ],
                  ['Alpha / Beta',              epochFrame.features.alpha_beta,      false ],
                  ['TBR — θ / β',              epochFrame.features.theta_beta,      false ],
                ].map(([label, val, isPct]) => val !== undefined && (
                  <div key={label} className="flex items-center justify-between border-b border-nc-border/30 pb-1.5 last:border-0 last:pb-0">
                    <span className="text-xs text-nc-muted">{label}</span>
                    <span className="text-xs font-mono font-semibold text-nc-text">
                      {typeof val === 'number' ? (isPct ? `${Math.round(val * 100)}%` : val.toFixed(3)) : '—'}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-nc-muted text-center py-6">En attente de la première époque (4 s)…</p>
              )}
            </div>

            {/* Hjorth + Spectral */}
            <div className="card p-5 space-y-3">
              <h3 className="text-sm font-semibold text-nc-text">Hjorth + Spectral</h3>
              {epochFrame?.features ? (
                [
                  ['Activité (RMS²)',       epochFrame.features.activity,         ''],
                  ['Mobilité',              epochFrame.features.mobility,         ''],
                  ['Complexité',            epochFrame.features.complexity,       ''],
                  ['Entropie spectrale',    epochFrame.features.spectral_entropy, ''],
                  ['SEF95',                 epochFrame.features.sef95,            'Hz'],
                  ['Pic α individuel',      epochFrame.features.alpha_peak,       'Hz'],
                ].map(([label, val, unit]) => val !== undefined && (
                  <div key={label} className="flex items-center justify-between border-b border-nc-border/30 pb-1.5 last:border-0 last:pb-0">
                    <span className="text-xs text-nc-muted">{label}</span>
                    <span className="text-xs font-mono font-semibold text-nc-text">
                      {typeof val === 'number' ? `${val.toFixed(3)}${unit ? ' ' + unit : ''}` : '—'}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-nc-muted text-center py-6">En attente de la première époque (4 s)…</p>
              )}
            </div>

            {/* Fractal + Distribution */}
            <div className="card p-5 space-y-3">
              <h3 className="text-sm font-semibold text-nc-text">Fractal & Distribution</h3>
              {epochFrame?.features ? (
                [
                  ['Higuchi FD',       epochFrame.features.higuchi_fd,   '' ],
                  ['Skewness',         epochFrame.features.skewness,     '' ],
                  ['Kurtosis',         epochFrame.features.kurtosis,     '' ],
                  ['ZCR',              epochFrame.features.zcr,          '' ],
                  ['RMS signal',       epochFrame.features.rms,          'µV'],
                  ['EMG ratio',        epochFrame.features.emg_ratio,    '%' ],
                ].map(([label, val, unit]) => val !== undefined && (
                  <div key={label} className="flex items-center justify-between border-b border-nc-border/30 pb-1.5 last:border-0 last:pb-0">
                    <span className="text-xs text-nc-muted">{label}</span>
                    <span className="text-xs font-mono font-semibold text-nc-text">
                      {typeof val === 'number'
                        ? (unit === '%' ? `${(val * 100).toFixed(1)}%` : `${val.toFixed(3)}${unit ? ' ' + unit : ''}`)
                        : '—'}
                    </span>
                  </div>
                ))
              ) : (
                <p className="text-xs text-nc-muted text-center py-6">En attente de la première époque (4 s)…</p>
              )}
            </div>
          </div>

          {/* Artefacts */}
          {epochFrame?.artifacts && (
            <div className="card p-4 flex flex-wrap items-center gap-4 text-xs">
              <span className="text-nc-muted font-semibold">Artefacts :</span>
              <span className={epochFrame.artifacts.eog_detected ? 'text-yellow-400 font-semibold' : 'text-emerald-400'}>
                {epochFrame.artifacts.eog_detected ? '⚠ EOG détecté' : '✓ EOG OK'}
              </span>
              <span className={epochFrame.artifacts.emg_suspect ? 'text-orange-400 font-semibold' : 'text-emerald-400'}>
                {epochFrame.artifacts.emg_suspect ? '⚠ EMG suspect' : '✓ EMG OK'}
              </span>
              {epochFrame.features?.emg_ratio !== undefined && (
                <span className="text-nc-muted font-mono">
                  EMG : {((epochFrame.features.emg_ratio ?? 0) * 100).toFixed(1)}%
                </span>
              )}
            </div>
          )}

          {/* ML card dans features */}
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-nc-text mb-4">Classification LightGBM</h3>
            <MLClassifierCard prediction={mlPrediction} />
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
              ['Électrode Fp2',      electrodeOk ? 'OK' : 'KO',           electrodeOk ? 'text-emerald-400' : 'text-red-400'],
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
              <h3 className="text-sm font-semibold text-nc-text mb-4">Dernière classification LightGBM</h3>
              <MLClassifierCard prediction={mlPrediction} />
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
