import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Radio, Upload, Brain, ChevronRight, ArrowLeft, AlertTriangle, CheckCircle2, PenLine } from 'lucide-react'

const MODES = [
  {
    key:   'live',
    icon:  Radio,
    color: 'text-emerald-400',
    bg:    'bg-emerald-500/12',
    border:'border-emerald-500/25',
    title: 'EEG en direct',
    desc:  'Casque ESP32 connecté — acquisition 250 Hz, classification LightGBM temps réel. Pointera vers la page EEG live.',
    path:  '/eeg/live',
  },
  {
    key:   'file',
    icon:  Upload,
    color: 'text-purple-400',
    bg:    'bg-purple-500/12',
    border:'border-purple-500/25',
    title: 'Fichier EEG (offline)',
    desc:  'Téléverser un fichier CSV / EDF — classification offline puis neurofeedback adaptatif.',
    path:  '/eeg/upload',
  },
  {
    key:   'manual',
    icon:  PenLine,
    color: 'text-nc-accent',
    bg:    'bg-nc-accent/12',
    border:'border-nc-accent/25',
    title: 'Sans EEG — saisie manuelle',
    desc:  'Pas de casque requis. Vous décrivez vous-même votre état (stress, concentration…) via le questionnaire intégré.',
    path:  '/neurofeedback?mode=manual',
  },
]

export default function SessionSetup() {
  const navigate = useNavigate()
  const [backendOk, setBackendOk] = useState(null) // null = checking, true/false

  useEffect(() => {
    fetch('/api/health', { signal: AbortSignal.timeout(3000) })
      .then(r => setBackendOk(r.ok))
      .catch(() => setBackendOk(false))
  }, [])

  const handleSelect = (mode) => {
    if (mode.key === 'manual') {
      navigate('/feedback/session', {
        state: { mode: 'manual', eeg_state: 'neutral', classification_confidence: 0, features_snapshot: null },
      })
    } else {
      navigate(mode.path)
    }
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-10 space-y-8 animate-fade-in">

      {/* ── Header ── */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/dashboard')}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-nc-text">Démarrer une séance</h1>
          <p className="text-sm text-nc-muted mt-0.5">Choisissez votre mode d'acquisition EEG</p>
        </div>
      </div>

      {/* ── Backend status ── */}
      {backendOk === false && (
        <div className="card p-4 flex items-start gap-3 border-amber-500/25 bg-amber-500/5">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-400">Backend inaccessible</p>
            <p className="text-xs text-nc-muted mt-0.5">
              Vérifiez que le serveur FastAPI tourne sur le port 8000. Le mode démo reste disponible.
            </p>
          </div>
        </div>
      )}
      {backendOk === true && (
        <div className="flex items-center gap-2 text-xs text-emerald-400">
          <CheckCircle2 className="w-3.5 h-3.5" />
          Backend connecté
        </div>
      )}

      {/* ── Mode cards ── */}
      <div className="space-y-4">
        {MODES.map((mode) => {
          const Icon = mode.icon
          const disabled = mode.key !== 'demo' && backendOk === false
          return (
            <button
              key={mode.key}
              onClick={() => !disabled && handleSelect(mode)}
              disabled={disabled}
              className={`w-full card p-5 flex items-center gap-5 text-start group
                          transition-all hover:shadow-md border
                          ${disabled
                            ? 'opacity-40 cursor-not-allowed'
                            : `hover:border-nc-accent/30 cursor-pointer`}`}
            >
              <div className={`w-12 h-12 rounded-2xl ${mode.bg} border ${mode.border}
                               flex items-center justify-center shrink-0`}>
                <Icon className={`w-6 h-6 ${mode.color}`} />
              </div>

              <div className="flex-1 min-w-0">
                <p className="font-semibold text-nc-text text-base">{mode.title}</p>
                <p className="text-sm text-nc-muted leading-relaxed mt-0.5">{mode.desc}</p>
                {mode.key !== 'manual' && backendOk === false && (
                  <p className="text-xs text-amber-400 mt-1">⚠ Requiert le backend</p>
                )}
              </div>

              <ChevronRight className={`w-5 h-5 shrink-0 transition-colors
                ${disabled ? 'text-nc-muted/30' : 'text-nc-muted group-hover:text-nc-accent'}`} />
            </button>
          )
        })}
      </div>

      {/* ── Footer note ── */}
      <p className="text-xs text-nc-muted text-center">
        Chaque session inclut une phase de préparation (fixation + respiration) avant le neurofeedback actif.
      </p>
    </div>
  )
}
