import { useParams, useNavigate } from 'react-router-dom'
import { ArrowLeft, Activity, Upload, Shuffle, ArrowRight, Brain, Wifi } from 'lucide-react'

const EEG_STATES = [
  { value: 'stress',     label: 'Stress',    emoji: '😰', color: 'text-red-400',     desc: 'Stimuli apaisants recommandés' },
  { value: 'focus',      label: 'Focus',     emoji: '🎯', color: 'text-emerald-400', desc: 'Stimuli cognitifs pour maintenir le flow' },
  { value: 'distracted', label: 'Distrait',  emoji: '😶', color: 'text-yellow-400',  desc: 'Jeux de focalisation pour réentraîner l\'attention' },
  { value: 'neutral',    label: 'Neutre',    emoji: '😌', color: 'text-nc-muted',    desc: 'Contenus variés pour explorer vos préférences' },
  { value: 'relax',      label: 'Relaxé',    emoji: '🌿', color: 'text-blue-400',    desc: 'Contenus immersifs légers pour consolider la relaxation' },
]

export default function SessionEntry() {
  const { n }    = useParams()
  const navigate = useNavigate()
  const sessionN = parseInt(n)

  const goEEG = () =>
    navigate('/eeg', { state: { fromProtocol: true, sessionN } })

  const goRandom = () =>
    navigate('/feedback', { state: { fromProtocol: true, sessionN } })

  return (
    <div className="max-w-2xl mx-auto px-4 py-8 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/protocol')}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="w-10 h-10 rounded-2xl bg-nc-accent/15 flex items-center justify-center">
          <Brain className="w-5 h-5 text-nc-accent" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-nc-text">Séance {sessionN}</h1>
          <p className="text-xs text-nc-muted">Choisissez comment démarrer votre neurofeedback</p>
        </div>
      </div>

      {/* Separator */}
      <div className="h-px bg-nc-border" />

      {/* Info banner */}
      <div className="card p-4 border border-nc-accent/20 bg-nc-accent/5">
        <p className="text-xs text-nc-muted leading-relaxed">
          Le neurofeedback s'adapte à votre état cérébral en temps réel.
          Pour un feedback précis, utilisez votre casque EEG.
          Sinon, choisissez manuellement votre état du moment.
        </p>
      </div>

      {/* Two options */}
      <div className="grid sm:grid-cols-2 gap-4">

        {/* Option A — EEG */}
        <button
          onClick={goEEG}
          className="group card p-6 text-left space-y-4 border-2 border-transparent
                     hover:border-nc-accent/40 hover:shadow-lg transition-all duration-200
                     active:scale-[0.98]"
        >
          <div className="flex items-start justify-between">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/15 flex items-center justify-center">
              <Wifi className="w-6 h-6 text-emerald-400" />
            </div>
            <ArrowRight className="w-5 h-5 text-nc-muted group-hover:text-nc-accent group-hover:translate-x-1 transition-all" />
          </div>

          <div>
            <p className="text-base font-bold text-nc-text">EEG Réel ou Téléversement</p>
            <p className="text-xs text-nc-muted mt-1 leading-relaxed">
              Connectez votre casque EEG pour une analyse en temps réel,
              ou téléversez un fichier CSV pour une classification hors-ligne.
            </p>
          </div>

          <div className="flex gap-2 pt-1">
            <span className="flex items-center gap-1 text-[10px] font-semibold px-2 py-1 rounded-lg
                             bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Activity className="w-3 h-3" /> EEG Temps Réel
            </span>
            <span className="flex items-center gap-1 text-[10px] font-semibold px-2 py-1 rounded-lg
                             bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Upload className="w-3 h-3" /> Fichier CSV
            </span>
          </div>

          <div className="pt-1">
            <div className="w-full py-2.5 rounded-xl bg-emerald-500/15 text-emerald-400
                            text-xs font-semibold text-center group-hover:bg-emerald-500/25 transition-colors">
              Aller vers l'interface EEG →
            </div>
          </div>
        </button>

        {/* Option B — Random / Manual */}
        <div className="card p-6 text-left space-y-4 border-2 border-transparent flex flex-col">
          <button
            onClick={goRandom}
            className="group flex flex-col space-y-4 flex-1 text-left active:scale-[0.98] transition-all"
          >
            <div className="flex items-start justify-between">
              <div className="w-12 h-12 rounded-2xl bg-purple-500/15 flex items-center justify-center">
                <Shuffle className="w-6 h-6 text-purple-400" />
              </div>
              <ArrowRight className="w-5 h-5 text-nc-muted group-hover:text-nc-accent group-hover:translate-x-1 transition-all" />
            </div>

            <div>
              <p className="text-base font-bold text-nc-text">Neurofeedback au Choix</p>
              <p className="text-xs text-nc-muted mt-1 leading-relaxed">
                Décrivez votre état actuel (stressé, distrait, concentré…)
                et recevez un feedback adaptatif immédiat sans casque.
              </p>
            </div>

            <div className="flex flex-wrap gap-1.5 pt-1">
              {EEG_STATES.map(s => (
                <span key={s.value}
                  className="text-[9px] font-semibold px-1.5 py-0.5 rounded-md bg-nc-surface2 text-nc-muted border border-nc-border">
                  {s.emoji} {s.label}
                </span>
              ))}
            </div>

            <div className="pt-1">
              <div className="w-full py-2.5 rounded-xl bg-purple-500/15 text-purple-400
                              text-xs font-semibold text-center group-hover:bg-purple-500/25 transition-colors">
                Choisir mon état →
              </div>
            </div>
          </button>

          {/* Passer directement — intégré dans la carte */}
          <div className="h-px bg-nc-border" />
          <button
            onClick={() => navigate(`/protocol/session/${sessionN}`)}
            className="text-xs text-nc-muted hover:text-nc-text transition-colors text-center py-1 rounded-lg hover:bg-nc-surface2 w-full"
          >
            Passer directement à la séance →
          </button>
        </div>
      </div>

      <p className="text-center text-[10px] text-nc-muted/50 pb-4">
        Recommandé : utiliser le casque EEG pour un feedback personnalisé optimal
      </p>
    </div>
  )
}
