import { useNavigate } from 'react-router-dom'
import {
  Radio, FileText, ArrowRight, Zap, Brain, BarChart3, Clock,
  BookOpen, Wifi,
} from 'lucide-react'

export default function EEGSelector() {
  const navigate = useNavigate()

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 space-y-10">

      {/* ── En-tête ── */}
      <div className="text-center space-y-3">
        <div className="w-16 h-16 rounded-3xl bg-nc-accent/15 flex items-center justify-center mx-auto">
          <Brain className="w-8 h-8 text-nc-accent" />
        </div>
        <h1 className="text-3xl font-bold text-nc-text">Analyse EEG</h1>
        <p className="text-base text-nc-muted max-w-lg mx-auto">
          Choisissez votre mode d'analyse : signal temps réel avec le casque NeuroCap,
          ou classification d'un fichier EEG existant.
        </p>
      </div>

      {/* ── Cartes de choix ── */}
      <div className="grid md:grid-cols-2 gap-6">

        {/* Carte 1 — Live Hardware */}
        <button
          onClick={() => navigate('/eeg-live')}
          className="card p-8 text-start space-y-5 border-nc-border hover:border-nc-accent/40
                     hover:bg-nc-accent/5 transition-all duration-200 group cursor-pointer"
        >
          <div className="w-14 h-14 rounded-2xl bg-nc-accent/15 flex items-center justify-center
                          group-hover:scale-110 transition-transform duration-200">
            <Radio className="w-7 h-7 text-nc-accent" />
          </div>

          <div>
            <h2 className="text-xl font-bold text-nc-text">EEG Temps Réel</h2>
            <p className="text-sm text-nc-muted mt-1">Casque NeuroCap · ESP32 · AD8232</p>
          </div>

          <ul className="space-y-2.5">
            {[
              [Zap,      'Signal en direct à 250 Hz'],
              [Wifi,     'Configuration WiFi ESP32 intégrée'],
              [Brain,    'Classification cognitif automatique'],
              [BarChart3,'63 features FeatEng + DSP v8.0'],
              [Clock,    'Enregistrement CSV session'],
            ].map(([Icon, text]) => (
              <li key={text} className="flex items-center gap-2 text-sm text-nc-muted">
                <Icon className="w-4 h-4 text-nc-accent shrink-0" />
                {text}
              </li>
            ))}
          </ul>

          <div className="flex items-center gap-2 text-nc-accent font-semibold text-sm pt-1">
            Démarrer la session
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </button>

        {/* Carte 2 — Analyse fichier */}
        <button
          onClick={() => navigate('/eeg-file')}
          className="card p-8 text-start space-y-5 border-nc-border hover:border-purple-400/40
                     hover:bg-purple-500/5 transition-all duration-200 group cursor-pointer"
        >
          <div className="w-14 h-14 rounded-2xl bg-purple-500/15 flex items-center justify-center
                          group-hover:scale-110 transition-transform duration-200">
            <FileText className="w-7 h-7 text-purple-400" />
          </div>

          <div>
            <h2 className="text-xl font-bold text-nc-text">Analyser un fichier</h2>
            <p className="text-sm text-nc-muted mt-1">EDF · CSV · TXT — analyse hors ligne</p>
          </div>

          <ul className="space-y-2.5">
            {[
              [FileText,  'Formats EDF, CSV et TXT'],
              [Brain,     'Classification LightGBM epoch par epoch'],
              [BarChart3, 'Résumé de session complet'],
              [Zap,       'Rééchantillonnage automatique à 250 Hz'],
              [Clock,     'Résultats instantanés sans matériel'],
            ].map(([Icon, text]) => (
              <li key={text} className="flex items-center gap-2 text-sm text-nc-muted">
                <Icon className="w-4 h-4 text-purple-400 shrink-0" />
                {text}
              </li>
            ))}
          </ul>

          <div className="flex items-center gap-2 text-purple-400 font-semibold text-sm pt-1">
            Choisir un fichier
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </button>
      </div>

      {/* ── Hint bas de page ── */}
      <div className="card p-4 flex items-center gap-3">
        <BookOpen className="w-5 h-5 text-nc-muted shrink-0" />
        <p className="text-xs text-nc-muted">
          <strong className="text-nc-text">Première utilisation ?</strong>{' '}
          Consultez le{' '}
          <button
            className="text-nc-accent underline hover:no-underline"
            onClick={() => navigate('/electrode-guide')}
          >
            guide de pose des électrodes
          </button>{' '}
          avant de démarrer votre session temps réel.
        </p>
      </div>

      {/* ── Specs techniques ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Fréquence',    value: '250 Hz',     sub: 'Fp2 canal unique'   },
          { label: 'Époque',       value: '4 s',        sub: 'Overlap 75%'        },
          { label: 'Features',     value: '63',         sub: 'FeatEng LightGBM'   },
          { label: 'Classificateur', value: 'LGBM',    sub: 'LOSO validé'        },
        ].map(({ label, value, sub }) => (
          <div key={label} className="card p-4 text-center">
            <p className="text-lg font-bold font-mono text-nc-accent">{value}</p>
            <p className="text-xs text-nc-text font-medium mt-0.5">{label}</p>
            <p className="text-[10px] text-nc-muted">{sub}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
