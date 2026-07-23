import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, Zap, Wind, Target, ArrowRight, ChevronLeft } from 'lucide-react'

const EEG_STATES = [
  {
    key: 'stress',
    label: 'Stress',
    sub: 'Bêta élevé · alpha réduit',
    desc: "Activation du système nerveux sympathique. Le système recommandera des médias calmants : audio nature, images vertes/cyan, exercices de respiration 4-6.",
    color: 'text-red-400',
    border: 'border-red-500/40',
    bg: 'bg-red-500/10',
    ring: 'ring-red-500/30',
    Icon: Zap,
  },
  {
    key: 'concentration',
    label: 'Concentration',
    sub: 'Engagement cognitif élevé',
    desc: "Bêta frontal actif, engagement index > 0.6. Le système recommandera des jeux cognitifs, illusions optiques actives et images stimulantes (bleu/violet).",
    color: 'text-emerald-400',
    border: 'border-emerald-500/40',
    bg: 'bg-emerald-500/10',
    ring: 'ring-emerald-500/30',
    Icon: Target,
  },
  {
    key: 'neutral',
    label: 'Neutre / Transition',
    sub: 'Équilibre alpha-bêta',
    desc: "État de base ou de transition. Le système recommandera des contenus doux — puzzles, vidéos lentes, illusions légères — pour préparer l'engagement progressif.",
    color: 'text-blue-400',
    border: 'border-blue-500/40',
    bg: 'bg-blue-500/10',
    ring: 'ring-blue-500/30',
    Icon: Wind,
  },
]

const CONFIDENCE_OPTIONS = [
  { value: 0.60, label: 'Approximatif', sub: '60 %' },
  { value: 0.80, label: 'Modéré',       sub: '80 %' },
  { value: 1.00, label: 'Certain',      sub: '100 %' },
]

export default function EEGManualInput() {
  const navigate = useNavigate()
  const [selectedState, setSelectedState] = useState(null)
  const [confidence, setConfidence] = useState(0.80)

  function handleStart() {
    if (!selectedState) return
    navigate('/eeg-feedback', {
      state: {
        source:     'manual',
        eegState:   selectedState,
        confidence,
        features:   null,
      },
    })
  }

  return (
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-12 space-y-8">

      {/* ── En-tête ── */}
      <div>
        <button
          onClick={() => navigate('/eeg')}
          className="flex items-center gap-2 text-nc-muted text-sm hover:text-nc-text transition-colors mb-6"
        >
          <ChevronLeft className="w-4 h-4" />
          Retour au choix EEG
        </button>
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-amber-500/15 flex items-center justify-center shrink-0">
            <Brain className="w-7 h-7 text-amber-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-nc-text">Saisie manuelle de l'état EEG</h1>
            <p className="text-sm text-nc-muted mt-0.5">
              Sans casque — explorez le système de recommandation adaptatif
            </p>
          </div>
        </div>
      </div>

      {/* ── Étape 1 : état EEG ── */}
      <div className="space-y-3">
        <p className="text-sm font-semibold text-nc-text">
          1. Quel est votre état cognitif actuel ?
        </p>
        <div className="space-y-3">
          {EEG_STATES.map(({ key, label, sub, desc, color, border, bg, ring, Icon }) => {
            const active = selectedState === key
            return (
              <button
                key={key}
                onClick={() => setSelectedState(key)}
                className={`w-full card p-5 text-start transition-all duration-200 border-2
                  ${active ? `${border} ${bg}` : 'border-nc-border hover:border-nc-accent/30'}`}
              >
                <div className="flex items-start gap-4">
                  <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0
                    ${active ? bg : 'bg-nc-surface2'}`}>
                    <Icon className={`w-5 h-5 ${active ? color : 'text-nc-muted'}`} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className={`font-semibold text-sm ${active ? color : 'text-nc-text'}`}>{label}</span>
                      <span className="text-[11px] text-nc-muted">{sub}</span>
                    </div>
                    <p className="text-xs text-nc-muted mt-1.5 leading-relaxed">{desc}</p>
                  </div>
                  <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 mt-0.5 transition-all
                    ${active ? `${border.replace('border-', 'bg-').replace('/40', '/80')} ${border}` : 'border-nc-border'}`}>
                    {active && (
                      <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* ── Étape 2 : confiance ── */}
      <div className="space-y-3">
        <p className="text-sm font-semibold text-nc-text">
          2. Niveau de certitude sur votre état
        </p>
        <div className="grid grid-cols-3 gap-3">
          {CONFIDENCE_OPTIONS.map(({ value, label, sub }) => {
            const active = confidence === value
            return (
              <button
                key={value}
                onClick={() => setConfidence(value)}
                className={`card p-4 text-center transition-all duration-200 border-2
                  ${active ? 'border-nc-accent/50 bg-nc-accent/8' : 'border-nc-border hover:border-nc-accent/30'}`}
              >
                <p className={`text-sm font-semibold ${active ? 'text-nc-accent' : 'text-nc-text'}`}>{label}</p>
                <p className={`text-lg font-bold font-mono mt-0.5 ${active ? 'text-nc-accent' : 'text-nc-muted'}`}>{sub}</p>
              </button>
            )
          })}
        </div>
      </div>

      {/* ── Note mode exploration ── */}
      <div className="card p-4 border-amber-500/20 bg-amber-500/5">
        <p className="text-xs text-amber-300/80 leading-relaxed">
          <strong className="text-amber-300">Mode exploration</strong> — Ce mode ne nécessite pas de casque EEG.
          Le système de recommandation neurophysiologique s'activera comme si l'état avait été détecté automatiquement
          par LightGBM. Utile pour explorer les contenus (audio, images, illusions optiques, jeux) ou tester la plateforme.
        </p>
      </div>

      {/* ── CTA ── */}
      <div className="space-y-3">
        <button
          onClick={handleStart}
          disabled={!selectedState}
          className="w-full btn-primary flex items-center justify-center gap-3 py-4 rounded-2xl text-base font-semibold
                     disabled:opacity-40 disabled:cursor-not-allowed transition-all"
        >
          <Brain className="w-5 h-5" />
          Démarrer le feedback adaptatif
          <ArrowRight className="w-5 h-5" />
        </button>
        {!selectedState && (
          <p className="text-xs text-nc-muted text-center">
            Sélectionnez votre état EEG pour continuer.
          </p>
        )}
      </div>
    </div>
  )
}
