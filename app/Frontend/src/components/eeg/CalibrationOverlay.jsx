import { useState, useEffect, useRef, useCallback } from 'react'
import { Brain, Eye, EyeOff, Calculator, Wind, CheckCircle2, X, Send } from 'lucide-react'
import { protocol as protocolApi } from '../../utils/api'

/* ── Phases de calibration EEG ─────────────────────────────────────── */
const PHASES = [
  {
    id: 'C1', label: 'Repos yeux fermés', icon: EyeOff,
    duration: 120, color: 'text-indigo-400', bg: 'bg-indigo-500/10', border: 'border-indigo-500/25',
    instruction: 'Fermez les yeux, respirez normalement, restez immobile.',
    detail: 'Mesure de la puissance alpha de référence (P_alpha_ref) et de l\'IAPF.',
    content: null,
  },
  {
    id: 'C2', label: 'Repos yeux ouverts', icon: Eye,
    duration: 120, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/25',
    instruction: 'Fixez le point blanc au centre de l\'écran sans cligner excessivement.',
    detail: 'Mesure du blocage alpha (ERD) et de la réactivité visuelle.',
    content: 'dot',
  },
  {
    id: 'C3', label: 'Tâche cognitive', icon: Calculator,
    duration: 120, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/25',
    instruction: 'Résolvez mentalement les opérations affichées.',
    detail: 'Mesure de l\'activation bêta en situation de charge cognitive.',
    content: 'math',
  },
  {
    id: 'C4', label: 'Relaxation guidée', icon: Wind,
    duration: 120, color: 'text-cyan-400', bg: 'bg-cyan-500/10', border: 'border-cyan-500/25',
    instruction: 'Inspirez 4 secondes — expirez 4 secondes, suivez le guide.',
    detail: 'Mesure de la réponse alpha à la relaxation.',
    content: 'breath',
  },
]

const MATH_OPS = ['37 + 48', '82 − 29', '6 × 13', '91 + 37', '143 − 56', '7 × 12', '64 + 78', '112 − 47', '8 × 15', '53 + 69']

/* ── Breathing Guide ────────────────────────────────────────────────── */
function BreathBall({ elapsed }) {
  const cycle = 8
  const t = elapsed % cycle
  const scale = t < 4 ? 1 + (t / 4) * 0.5 : 1.5 - ((t - 4) / 4) * 0.5
  const label = t < 4 ? 'Inspirez…' : 'Expirez…'
  return (
    <div className="flex flex-col items-center gap-4">
      <div
        className="w-24 h-24 rounded-full bg-cyan-500/30 border-2 border-cyan-400/50 transition-all duration-500 flex items-center justify-center"
        style={{ transform: `scale(${scale})` }}
      >
        <div className="w-10 h-10 rounded-full bg-cyan-400/40" />
      </div>
      <p className="text-sm text-cyan-300 font-medium">{label}</p>
    </div>
  )
}

/* ── Countdown ring ─────────────────────────────────────────────────── */
function CountRing({ elapsed, total, color }) {
  const r = 42, cx = 48, cy = 48
  const circ = 2 * Math.PI * r
  const pct = Math.min(elapsed / total, 1)
  const rem = total - elapsed
  return (
    <svg width={96} height={96} className="mx-auto">
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={6} />
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="currentColor" strokeWidth={6}
        strokeDasharray={circ} strokeDashoffset={circ * (1 - pct)}
        strokeLinecap="round" transform={`rotate(-90 ${cx} ${cy})`}
        className={color} style={{ transition: 'stroke-dashoffset 0.9s linear' }}
      />
      <text x={cx} y={cy + 6} textAnchor="middle" fontSize={15} fontWeight={700} fill="currentColor" className={color}>
        {Math.floor(rem / 60)}:{String(rem % 60).padStart(2, '0')}
      </text>
    </svg>
  )
}

/* ══════════════════════════════════════════════════════════════════════
   CalibrationOverlay — rendu par-dessus EEGLive
══════════════════════════════════════════════════════════════════════ */
export default function CalibrationOverlay({ epochFrame, onClose, onComplete }) {
  const [phaseIdx,    setPhaseIdx]    = useState(0)       // index dans PHASES
  const [stage,       setStage]       = useState('intro') // intro | running | done | questionnaire | submitting | result
  const [elapsed,     setElapsed]     = useState(0)
  const [mathIdx,     setMathIdx]     = useState(0)
  const [collected,   setCollected]   = useState({ C1: [], C2: [], C3: [], C4: [] })
  const [questionnaire, setQ]         = useState({ concentration: 5, stress: 5, motivation: 7 })
  const [result,      setResult]      = useState(null)
  const [emailSent,   setEmailSent]   = useState(false)
  const [error,       setError]       = useState('')

  const timerRef    = useRef(null)
  const phase       = PHASES[phaseIdx]
  const PhaseIcon   = phase?.icon

  /* ── Collecter les features EEG de l'époque courante ── */
  useEffect(() => {
    if (stage !== 'running' || !epochFrame?.features || !phase) return
    setCollected(prev => ({
      ...prev,
      [phase.id]: [...prev[phase.id], { ...epochFrame.features }],
    }))
  }, [epochFrame, stage, phase?.id])

  /* ── Démarrer le timer ── */
  const startTimer = useCallback(() => {
    setElapsed(0)
    clearInterval(timerRef.current)
    timerRef.current = setInterval(() => {
      setElapsed(e => {
        const next = e + 1
        if (next >= PHASES[phaseIdx]?.duration) {
          clearInterval(timerRef.current)
          setStage('done')
        }
        return next
      })
    }, 1000)
  }, [phaseIdx])

  useEffect(() => () => clearInterval(timerRef.current), [])

  const handleStart = () => { setStage('running'); startTimer() }

  const handleNext = () => {
    if (phaseIdx < PHASES.length - 1) {
      setPhaseIdx(i => i + 1)
      setStage('intro')
      setElapsed(0)
      setMathIdx(0)
    } else {
      setStage('questionnaire')
    }
  }

  const handleSubmit = async () => {
    setStage('submitting')
    setError('')
    try {
      const res = await protocolApi.calibrationComplete({
        epochs_c1:     collected.C1,
        epochs_c2:     collected.C2,
        epochs_c3:     collected.C3,
        epochs_c4:     collected.C4,
        questionnaire,
      })
      setResult(res.profile ?? res)
      setEmailSent(res.email_sent ?? false)
      setStage('result')
      onComplete?.()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Erreur lors de la soumission')
      setStage('questionnaire')
    }
  }

  /* ── Époque collectée count ── */
  const totalEpochs = Object.values(collected).reduce((s, arr) => s + arr.length, 0)

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4"
         style={{ background: 'rgba(0,0,0,0.80)', backdropFilter: 'blur(8px)' }}>
      <div className="w-full max-w-lg bg-nc-surface rounded-3xl border border-nc-border shadow-2xl overflow-hidden">

        {/* ── Header ── */}
        <div className="flex items-center gap-3 px-6 py-4 border-b border-nc-border bg-nc-surface2/40">
          <Brain className="w-5 h-5 text-nc-accent shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-bold text-nc-text">Calibration EEG automatisée</p>
            <p className="text-[10px] text-nc-muted">
              {totalEpochs} époques collectées · Signal temps réel
            </p>
          </div>
          {/* Barre de progression phases */}
          <div className="flex gap-1">
            {PHASES.map((p, i) => (
              <div key={p.id} className={`h-1.5 w-8 rounded-full transition-all ${
                i < phaseIdx ? 'bg-emerald-500' :
                i === phaseIdx ? 'bg-nc-accent' : 'bg-nc-surface2'
              }`} />
            ))}
          </div>
          {stage !== 'submitting' && (
            <button onClick={onClose} className="p-1.5 rounded-xl text-nc-muted hover:bg-nc-surface2 transition-colors ml-1">
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        <div className="p-6 space-y-5">

          {/* ══ RESULT ══════════════════════════════════════════════════ */}
          {stage === 'result' && result && (
            <div className="space-y-4 text-center">
              <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
              <h2 className="text-lg font-bold text-nc-text">Calibration réussie !</h2>
              <p className="text-xs text-nc-muted">Votre profil EEG individuel est établi.</p>

              <div className="text-left space-y-1.5 bg-nc-surface2/40 rounded-2xl p-4">
                {[
                  ['Profil cognitif',  `Type ${result.profile_type ?? '—'}`],
                  ['IAPF',             result.iapf ? `${result.iapf} Hz` : '—'],
                  ['P_alpha_ref',      result.p_alpha_ref?.toFixed(4) ?? '—'],
                  ['ERD alpha',        result.erd_pct != null ? `${result.erd_pct}%` : '—'],
                  ['Palier initial',   result.palier_initial ?? '—'],
                  ['Époques collectées', totalEpochs],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between text-xs py-1 border-b border-nc-border/20 last:border-0">
                    <span className="text-nc-muted">{k}</span>
                    <span className="font-mono font-semibold text-nc-text">{v}</span>
                  </div>
                ))}
              </div>

              {emailSent && (
                <div className="flex items-center justify-center gap-2 text-xs text-emerald-400">
                  <Send className="w-3.5 h-3.5" />
                  Résultats envoyés par email
                </div>
              )}

              <button onClick={onClose} className="w-full btn-primary py-3 rounded-xl text-sm font-semibold">
                Fermer et voir le protocole →
              </button>
            </div>
          )}

          {/* ══ SUBMITTING ═══════════════════════════════════════════════ */}
          {stage === 'submitting' && (
            <div className="text-center space-y-4 py-8">
              <div className="w-10 h-10 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin mx-auto" />
              <p className="text-sm text-nc-muted">Calcul du profil EEG…</p>
            </div>
          )}

          {/* ══ QUESTIONNAIRE ════════════════════════════════════════════ */}
          {stage === 'questionnaire' && (
            <div className="space-y-4">
              <div className="text-center">
                <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
                <h3 className="text-sm font-bold text-nc-text">Enregistrement terminé</h3>
                <p className="text-xs text-nc-muted mt-0.5">{totalEpochs} époques collectées</p>
              </div>

              <div className="space-y-3">
                {[
                  { key: 'concentration', label: 'Concentration habituelle', left: 'Faible', right: 'Élevée' },
                  { key: 'stress',        label: 'Niveau de stress quotidien', left: 'Calme', right: 'Stressé' },
                  { key: 'motivation',    label: 'Motivation pour le programme', left: 'Faible', right: 'Forte' },
                ].map(({ key, label, left, right }) => (
                  <div key={key} className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="text-nc-muted">{label}</span>
                      <span className="font-mono font-bold text-nc-accent">{questionnaire[key]}/10</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] text-nc-muted/60 w-10 text-right shrink-0">{left}</span>
                      <input type="range" min={1} max={10} value={questionnaire[key]}
                        onChange={e => setQ(q => ({ ...q, [key]: +e.target.value }))}
                        className="flex-1 accent-nc-accent" />
                      <span className="text-[10px] text-nc-muted/60 w-10 shrink-0">{right}</span>
                    </div>
                  </div>
                ))}
              </div>

              {error && (
                <div className="p-2 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-300">{error}</div>
              )}

              <button onClick={handleSubmit} className="w-full btn-primary py-3 rounded-xl text-sm font-semibold">
                Calculer mon profil et envoyer par email →
              </button>
            </div>
          )}

          {/* ══ PHASES C1–C4 ═════════════════════════════════════════════ */}
          {stage !== 'result' && stage !== 'submitting' && stage !== 'questionnaire' && phase && (
            <div className={`rounded-2xl border p-5 space-y-4 ${phase.bg} ${phase.border}`}>

              {/* Phase header */}
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl ${phase.bg} border ${phase.border} flex items-center justify-center`}>
                  <PhaseIcon className={`w-5 h-5 ${phase.color}`} />
                </div>
                <div className="flex-1">
                  <p className={`text-[10px] font-bold uppercase tracking-wider ${phase.color}`}>{phase.id}</p>
                  <h3 className="text-sm font-bold text-nc-text">{phase.label}</h3>
                </div>
                {/* Époque counter live */}
                {stage === 'running' && (
                  <span className={`text-[10px] font-mono px-2 py-1 rounded-lg ${phase.bg} border ${phase.border} ${phase.color}`}>
                    {collected[phase.id]?.length ?? 0} épo.
                  </span>
                )}
              </div>

              <p className="text-sm text-nc-text">{phase.instruction}</p>
              <p className="text-[10px] text-nc-muted">{phase.detail}</p>

              {/* INTRO */}
              {stage === 'intro' && (
                <button onClick={handleStart} className="w-full btn-primary py-2.5 rounded-xl text-sm font-semibold">
                  Démarrer {phase.label} →
                </button>
              )}

              {/* RUNNING */}
              {stage === 'running' && (
                <div className="space-y-4">
                  <CountRing elapsed={elapsed} total={phase.duration} color={phase.color} />

                  {phase.content === 'dot' && (
                    <div className="flex items-center justify-center" style={{ height: 80 }}>
                      <div className="w-5 h-5 rounded-full bg-white/90 shadow-lg shadow-white/30" />
                    </div>
                  )}
                  {phase.content === 'math' && (
                    <div className="text-center space-y-3">
                      <p className="text-2xl font-bold font-mono text-nc-text">{MATH_OPS[mathIdx % MATH_OPS.length]}</p>
                      <button onClick={() => setMathIdx(i => i + 1)}
                        className="px-4 py-1.5 rounded-xl border border-nc-border text-xs text-nc-muted hover:bg-nc-surface2 transition-colors">
                        Opération suivante
                      </button>
                    </div>
                  )}
                  {phase.content === 'breath' && <BreathBall elapsed={elapsed} />}
                  {phase.content === null && (
                    <div className="text-center">
                      <p className="text-4xl">😌</p>
                    </div>
                  )}
                </div>
              )}

              {/* DONE */}
              {stage === 'done' && (
                <div className="space-y-3 text-center">
                  <CheckCircle2 className={`w-8 h-8 mx-auto ${phase.color}`} />
                  <p className="text-xs font-semibold text-nc-muted">
                    {collected[phase.id]?.length ?? 0} époques EEG enregistrées
                  </p>
                  <button onClick={handleNext} className="w-full btn-primary py-2.5 rounded-xl text-sm font-semibold">
                    {phaseIdx < PHASES.length - 1
                      ? `Étape suivante : ${PHASES[phaseIdx + 1].label} →`
                      : 'Questionnaire final →'}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ── Liste des phases restantes ── */}
          {stage !== 'result' && stage !== 'submitting' && stage !== 'questionnaire' && (
            <div className="grid grid-cols-4 gap-2">
              {PHASES.map((p, i) => {
                const PIcon = p.icon
                const done = i < phaseIdx
                const active = i === phaseIdx
                return (
                  <div key={p.id} className={`rounded-xl p-2 text-center border transition-all ${
                    done   ? 'border-emerald-500/20 bg-emerald-500/5' :
                    active ? `${p.border} ${p.bg}` :
                    'border-nc-border bg-nc-surface2/20 opacity-40'
                  }`}>
                    <PIcon className={`w-4 h-4 mx-auto mb-1 ${done ? 'text-emerald-400' : active ? p.color : 'text-nc-muted'}`} />
                    <p className={`text-[9px] font-semibold ${done ? 'text-emerald-400' : active ? p.color : 'text-nc-muted'}`}>{p.id}</p>
                    <p className="text-[8px] text-nc-muted/60">{Math.floor(p.duration / 60)} min</p>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
