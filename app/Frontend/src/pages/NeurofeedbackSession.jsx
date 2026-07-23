import { useState, useEffect } from 'react'
import { useNavigate, useLocation, useSearchParams } from 'react-router-dom'
import { Brain, Eye, Wind, Zap, ChevronRight, BookOpen } from 'lucide-react'

import FixationStep    from '../components/neurofeedback/FixationStep'
import BreathingStep   from '../components/neurofeedback/BreathingStep'
import CalibrationStep from '../components/neurofeedback/CalibrationStep'
import ElectrodeGuide  from './ElectrodeGuide'

/* ── Step definitions ──────────────────────────────────────── */
const STEPS = [
  { id: 'guide',       label: 'Guide',       icon: BookOpen },
  { id: 'fixation',    label: 'Fixation',    icon: Eye      },
  { id: 'breathing',   label: 'Respiration', icon: Wind     },
  { id: 'calibration', label: 'Calibration', icon: Brain    },
  { id: 'session',     label: 'Session EEG', icon: Zap      },
]

/* ── Stepper header ────────────────────────────────────────── */
function StepHeader({ currentStep, mode }) {
  // File/manual mode: guide, breathing, calibration are hardware-only steps — remove them
  const noHardware = mode === 'file' || mode === 'manual'
  const steps = noHardware
    ? STEPS.filter(s => s.id !== 'guide' && s.id !== 'breathing' && s.id !== 'calibration')
    : STEPS

  // Map raw step index to visible index for no-hardware modes
  // raw: 1=fixation, 4+=session  →  visible: 0, 1
  const visibleStep = noHardware
    ? currentStep <= 1 ? 0 : 1
    : currentStep

  return (
    <div className="flex items-center justify-center gap-2 py-6">
      {steps.map((s, i) => {
        const Icon    = s.icon
        const done    = i < visibleStep
        const active  = i === visibleStep
        const pending = i > visibleStep
        return (
          <div key={s.id} className="flex items-center gap-2">
            <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold
                             transition-all border
              ${done    ? 'bg-emerald-500/12 border-emerald-500/25 text-emerald-400' : ''}
              ${active  ? 'bg-nc-accent/15  border-nc-accent/35  text-nc-accent'    : ''}
              ${pending ? 'bg-nc-surface2   border-nc-border     text-nc-muted/50'  : ''}`}>
              <Icon className="w-3 h-3" />
              {s.label}
            </div>
            {i < steps.length - 1 && (
              <ChevronRight className={`w-3 h-3 ${done ? 'text-emerald-400/50' : 'text-nc-muted/20'}`} />
            )}
          </div>
        )
      })}
    </div>
  )
}

/* ── Launching screen before /feedback/session ─────────────── */
function LaunchingScreen() {
  return (
    <div className="flex flex-col items-center justify-center h-[60vh] gap-6 animate-fade-in">
      <div className="w-14 h-14 rounded-3xl bg-nc-accent/15 flex items-center justify-center">
        <Brain className="w-7 h-7 text-nc-accent" />
      </div>
      <div className="text-center space-y-2">
        <h2 className="text-xl font-bold text-nc-text">Démarrage de la session…</h2>
        <p className="text-sm text-nc-muted">Chargement du neurofeedback adaptatif</p>
      </div>
      <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════
   NeurofeedbackSession — stepper page (/neurofeedback)
════════════════════════════════════════════════════════════ */
export default function NeurofeedbackSession() {
  const navigate         = useNavigate()
  const location         = useLocation()
  const [searchParams]   = useSearchParams()

  const mode    = searchParams.get('mode') || 'live'
  const eegData = location.state || {}

  // Manual and file modes skip step 0 (ElectrodeGuide — only needed with a physical headset).
  const [step, setStep] = useState(mode === 'manual' || mode === 'file' ? 1 : 0)

  const advance = () => setStep(s => {
    const next = s + 1
    // File/manual: no breathing (2) and no calibration (3) — jump straight to session (4)
    if ((mode === 'file' || mode === 'manual') && next >= 2) return 4
    return next
  })

  // When we reach step 4 (session), navigate to FeedbackSession
  useEffect(() => {
    if (step < 4) return
    navigate('/feedback/session', {
      replace: true,
      state: {
        mode,
        eeg_state:                 eegData.eeg_state                 ?? 'neutral',
        classification_confidence: eegData.classification_confidence ?? 0,
        features_snapshot:         eegData.features_snapshot         ?? null,
      },
    })
  }, [step])

  return (
    <div className="max-w-3xl mx-auto">
      {/* Show header for non-full-screen steps (Fixation/Breathing are fixed inset-0) */}
      {step !== 1 && step !== 2 && <StepHeader currentStep={step} mode={mode} />}

      {step === 0 && (
        <ElectrodeGuide
          onComplete={advance}
          onSkip={advance}
        />
      )}

      {step === 1 && (
        <FixationStep
          onComplete={advance}
          onSkip={advance}
        />
      )}

      {step === 2 && (
        <BreathingStep
          onComplete={advance}
          onSkip={advance}
        />
      )}

      {step === 3 && (
        <CalibrationStep
          onComplete={advance}
          onSkip={advance}
        />
      )}

      {step >= 4 && <LaunchingScreen />}
    </div>
  )
}
