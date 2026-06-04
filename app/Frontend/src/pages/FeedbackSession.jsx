import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { ArrowLeft, Brain, ChevronRight, Target, Gauge, BarChart3, CheckCircle2, RefreshCw, Music } from 'lucide-react'

import { useEEGWebSocket }    from '../hooks/useEEGWebSocket'
import { useFeedbackSocket }  from '../hooks/useFeedbackSocket'
import { feedback as fbApi }  from '../utils/api'
import { useAuthStore }       from '../stores'

import MiniEEGOscilloscope       from '../components/feedback/MiniEEGOscilloscope'
import BreathingGuide            from '../components/feedback/BreathingGuide'
import FocusPoint                from '../components/feedback/FocusPoint'
import MediaZone                 from '../components/feedback/MediaZone'
import UserFeedbackBar           from '../components/feedback/UserFeedbackBar'
import SessionBlockTimer         from '../components/feedback/SessionBlockTimer'
import FeedbackReport            from '../components/feedback/FeedbackReport'
import MediaNeuroscienceGuide    from '../components/feedback/MediaNeuroscienceGuide'

// ── Constantes protocole (Mou et al., 2024 ; Wu et al., 2022) ─────────────────
const TOTAL_BLOCKS          = 6
const BLOCK_DURATION        = 180    // 3 min en secondes
const PAUSE_DURATION        = 20     // 20 s entre blocs
const EWMA_ALPHA            = 0.3    // Lissage exponentiel intra-bloc
const THRESHOLD_INIT_RATIO  = 0.95   // Seuil initial = 95 % de la baseline
const THRESHOLD_STEP        = 0.005  // ±0.5 % puissance relative par bloc
const THRESHOLD_MIN_RATIO   = 0.70   // Minimum absolu = 70 % de la baseline
const SUCCESS_HIGH          = 0.60   // Seuil succès → augmenter difficulté
const SUCCESS_LOW           = 0.40   // Seuil échec  → réduire difficulté

const PHASES = {
  PRE_QUESTIONNAIRE:  'pre_questionnaire',
  PRE_SESSION:        'pre_session',
  BASELINE_CLOSED:    'baseline_closed',
  FEEDBACK_BLOCK:     'feedback_block',
  INTER_BLOCK_PAUSE:  'inter_block_pause',
  GUIDED_REST:        'guided_rest',
  POST_QUESTIONNAIRE: 'post_questionnaire',
  POST_SESSION:       'post_session',
}

const PHASE_LABELS = {
  phase1: { label: 'Phase 1 · Découverte',     color: 'text-purple-400',  bg: 'bg-purple-500/10' },
  phase2: { label: 'Phase 2 · Apprentissage',  color: 'text-blue-400',    bg: 'bg-blue-500/10'   },
  phase3: { label: 'Phase 3 · Consolidation',  color: 'text-emerald-400', bg: 'bg-emerald-500/10'},
}

const PALIER_LABELS = {
  1: { label: 'P1 · Initiation',   color: 'text-purple-400' },
  2: { label: 'P2 · Apprentissage', color: 'text-blue-400'  },
  3: { label: 'P3 · Maîtrise',     color: 'text-emerald-400'},
  4: { label: 'P4 · Autonomie',    color: 'text-amber-400'  },
}

// ── Guide IA contextuel par état EEG × type de média ─────────────────────────
//
// Sources scientifiques (ANALYSE.md) :
//   Audio  : Thaut 1999 (tempo 60-75 BPM → alpha ↑), Sammler 2007 (harmonicité → relaxation)
//   Image  : Valdez & Mehrabian 1994 (luminosité → valence), Berman 2014 (complexité → arousal)
//   Video  : Grill-Spector & Malach 2001 (habituation), optical flow faible → relaxation
//   Game   : Vygotsky 1978 (ZPD niveaux adaptatifs), Clément 2015 (coloriage thérapeutique)
//
// Features CSV déterminantes :
//   Audio  : tempo_bpm, harm_perc_ratio, spectral_stationarity, rms_mean
//   Image  : brightness_global, glcm_homogeneity, contrast_rms, edge_density
//   Video  : optical_flow_mean, motion_regularity, scene_change_rate
//   Game   : type (coloriage/sudoku/mémoire/puzzle) selon état EEG
//
const AI_GUIDES = {
  // ── AUDIO ────────────────────────────────────────────────────────────────────
  stress_audio: {
    icon: '🎵', title: 'Audio anti-stress actif',
    color: 'text-blue-400', bg: 'bg-blue-500/8', border: 'border-blue-500/20',
    tip: 'Sons sélectionnés : tempo 60-75 BPM, graves dominants, ratio harmonique élevé. Ce profil acoustique induit une montée des ondes alpha et réduit le cortisol (Thaut 1999, Sammler 2007).',
    steps: [
      'Fermez partiellement les yeux — focalisez sur les sons graves',
      'Laissez votre respiration se synchroniser au tempo naturellement',
      'Ne cherchez pas à analyser la mélodie — laissez venir',
      'Si une émotion monte, c\'est normal : évaluez avec les étoiles',
    ],
    science: 'RMS faible · Tempo 60-75 BPM · harm_perc_ratio > 0.8',
  },
  concentration_audio: {
    icon: '🎯', title: 'Audio de concentration',
    color: 'text-emerald-400', bg: 'bg-emerald-500/8', border: 'border-emerald-500/20',
    tip: 'Sons à tempo stable ~120 BPM et centroïde spectral moyen. Ce profil anchor l\'attention et synchronise les oscillations beta frontales.',
    steps: [
      'Gardez les yeux ouverts, regard neutre vers l\'écran',
      'Laissez le rythme ancrer votre attention — pensez au tempo',
      'Si une pensée parasite arrive, revenez au rythme sonore',
      'Utilisez "Passer" si le son devient distrayant',
    ],
    science: 'Tempo ~120 BPM · Centroïde spectral moyen · Stationnarité > 0.4',
  },
  neutral_audio: {
    icon: '🧠', title: 'Exploration sonore',
    color: 'text-purple-400', bg: 'bg-purple-500/8', border: 'border-purple-500/20',
    tip: 'Le système mesure votre réponse EEG à ce profil acoustique pour affiner votre vecteur de préférences neurophysiologiques.',
    steps: [
      'Écoutez attentivement les différentes textures sonores',
      'Notez ce qui vous attire ou vous dérange (étoiles)',
      'Respirez normalement, ne forcez aucun état',
      'Chaque évaluation améliore la prochaine sélection',
    ],
    science: 'Calibration Thompson Sampling — prior informé features statiques',
  },

  // ── IMAGE ────────────────────────────────────────────────────────────────────
  stress_image: {
    icon: '🌿', title: 'Image thérapeutique anti-stress',
    color: 'text-blue-400', bg: 'bg-blue-500/8', border: 'border-blue-500/20',
    tip: 'Image à luminosité élevée (>0.7), faible contraste, homogénéité GLCM haute. Ce profil visuel diminue l\'arousal et favorise la valence positive (Valdez & Mehrabian 1994, Berman 2014).',
    steps: [
      'Balayez l\'image lentement — pas de fixation forcée',
      'Laissez votre regard se poser sur les zones lumineuses',
      'Évitez les saccades oculaires rapides, restez fluide',
      'Respirez 4 s / 4 s / 6 s pendant que vous regardez',
    ],
    science: 'brightness > 0.7 · glcm_homogeneity > 0.8 · contrast_rms < 0.2',
  },
  concentration_image: {
    icon: '🔍', title: 'Image de focalisation',
    color: 'text-emerald-400', bg: 'bg-emerald-500/8', border: 'border-emerald-500/20',
    tip: 'Image à contraste moyen et densité de bords élevée. Engage l\'attention fovéale et active les oscillations gamma (Berman 2014).',
    steps: [
      'Choisissez un détail précis et fixez-le 5 secondes',
      'Cherchez les lignes directrices ou patterns de l\'image',
      'Comptez mentalement les éléments si possible',
      'Évaluez si l\'image soutient votre concentration',
    ],
    science: 'edge_density > 0.4 · contrast_rms ~0.55 · saturation moyenne',
  },
  neutral_image: {
    icon: '🧠', title: 'Exploration visuelle',
    color: 'text-purple-400', bg: 'bg-purple-500/8', border: 'border-purple-500/20',
    tip: 'Exploration pour cartographier vos préférences visuelles. Le score de cosine similarity sera mis à jour avec votre évaluation.',
    steps: [
      'Observez l\'ensemble de l\'image pendant 10 secondes',
      'Explorez ensuite les détails qui attirent votre regard',
      'Notez 3 éléments marquants dans votre tête',
      'Donnez votre ressenti honnête avec les étoiles',
    ],
    science: 'Initialisation CBF cosine · prior uniforme Thompson Sampling',
  },

  // ── VIDEO ────────────────────────────────────────────────────────────────────
  stress_video: {
    icon: '🌊', title: 'Vidéo apaisante active',
    color: 'text-blue-400', bg: 'bg-blue-500/8', border: 'border-blue-500/20',
    tip: 'Vidéo à flux optique quasi-statique (<0.1), mouvement régulier (>0.85) et rares changements de scène (<5%). Ce profil induit une synchronisation visuo-respiratoire (Grill-Spector 2001).',
    steps: [
      'Laissez vos yeux suivre le mouvement sans effort actif',
      'Respirez au rythme visuel perçu — lent et régulier',
      'Évitez de cligner excessivement, gardez le regard doux',
      'Si votre esprit s\'emballe, revenez au mouvement à l\'écran',
    ],
    science: 'optical_flow < 0.1 · motion_regularity > 0.85 · scene_change_rate < 0.05',
  },
  concentration_video: {
    icon: '🎬', title: 'Vidéo de stimulation cognitive',
    color: 'text-emerald-400', bg: 'bg-emerald-500/8', border: 'border-emerald-500/20',
    tip: 'Vidéo à flux optique modéré et changements de scène contrôlés. Engage l\'attention soutenue et les circuits frontaux de concentration.',
    steps: [
      'Suivez activement chaque changement de scène',
      'Anticipez le prochain mouvement ou transition',
      'Restez en mode "observateur actif" — pensée analytique',
      'Évaluez si la vidéo soutient votre flux de concentration',
    ],
    science: 'optical_flow ~0.5 · scene_change_rate ~0.35 · motion_regularity ~0.55',
  },
  neutral_video: {
    icon: '🧠', title: 'Exploration vidéo',
    color: 'text-purple-400', bg: 'bg-purple-500/8', border: 'border-purple-500/20',
    tip: 'Calibration de votre réponse EEG aux stimuli vidéo. Données utilisées pour optimiser le Thompson Sampling.',
    steps: [
      'Regardez naturellement, sans effort de concentration',
      'Notez si le contenu vous calme, vous stimule, ou est neutre',
      'Votre évaluation entraîne le moteur adaptatif en temps réel',
      'Utilisez "Passer" librement — le skip est une donnée utile',
    ],
    science: 'EEG delta (32s) · Habituation threshold vidéo = 2 séquences',
  },

  // ── GAME ────────────────────────────────────────────────────────────────────
  stress_game: {
    icon: '🎨', title: 'Coloriage thérapeutique',
    color: 'text-blue-400', bg: 'bg-blue-500/8', border: 'border-blue-500/20',
    tip: 'Sélectionné selon votre indice de stress EEG. Le coloriage de mandalas ou motifs géométriques réduit l\'activation corticale et ancre l\'attention dans le présent (Clément 2015, VPD Vygotsky 1978).',
    steps: [
      'Remplissez chaque zone lentement — sans viser la perfection',
      'Focalisez sur le mouvement de coloration, pas le résultat',
      'Choisissez les couleurs instinctivement',
      'Si une erreur arrive, continuez — le process est thérapeutique',
    ],
    science: 'Coloriage mandala/nature sélectionné via stress_idx + historique · Niveau adaptatif VPD',
  },
  concentration_game: {
    icon: '🧩', title: 'Jeu de concentration active',
    color: 'text-emerald-400', bg: 'bg-emerald-500/8', border: 'border-emerald-500/20',
    tip: 'Sudoku, mémoire ou calcul sélectionné selon votre delta_alpha EEG. Le niveau s\'adapte : monte si error_rate < 20% et delta_beta > 0.05, descend si error_rate > 60%.',
    steps: [
      'Résolvez méthodiquement, une étape à la fois',
      'Ne passez à la suivante qu\'après avoir stabilisé votre réponse',
      'Si bloqué, respirez et re-visualisez le problème',
      'Le niveau s\'adapte automatiquement — faites confiance au système',
    ],
    science: 'Delta_alpha Thompson · Niveau ZPD : error_rate + delta_beta · Focus/mémoire/calcul',
  },
  neutral_game: {
    icon: '🔲', title: 'Puzzle de transition',
    color: 'text-purple-400', bg: 'bg-purple-500/8', border: 'border-purple-500/20',
    tip: 'Type de puzzle sélectionné selon votre ratio α/β. L\'assemblage spatial engage simultanément les circuits visuels et frontaux pour rééquilibrer vos ondes.',
    steps: [
      'Commencez par identifier les bords et les coins',
      'Cherchez ensuite les patterns et textures similaires',
      'Progressez metho­diquement sans vous précipiter',
      'L\'engagement visuo-spatial équilibre alpha et beta',
    ],
    science: 'Sliding/jigsaw/tangram selon ratio α/β · Habituation threshold = 1 partie',
  },
}

// Sélection guide : {état}_{type} → fallback {état}_audio → fallback neutral_audio
function selectGuide(eegState, mediaType) {
  const type = mediaType ?? 'audio'
  return (
    AI_GUIDES[`${eegState}_${type}`] ??
    AI_GUIDES[`${eegState}_audio`]   ??
    AI_GUIDES['neutral_audio']
  )
}

function AIGuideCard({ eegState, mediaType, blockIndex }) {
  const g = selectGuide(eegState, mediaType)
  const blockLabel = blockIndex < 2 ? 'Découverte' : blockIndex < 4 ? 'Apprentissage' : 'Consolidation'
  const typeLabel  = { audio: 'Audio', image: 'Image', video: 'Vidéo', game: 'Jeu' }[mediaType] ?? '—'

  return (
    <div className={`card p-4 space-y-3 border ${g.border} ${g.bg}`}>
      <div className="flex items-center gap-2">
        <span className="text-base">{g.icon}</span>
        <p className={`text-xs font-bold ${g.color} flex-1`}>{g.title}</p>
        <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-nc-surface2 text-nc-muted/60 font-mono">
          IA Guide
        </span>
      </div>

      <p className="text-[11px] text-nc-muted leading-relaxed">{g.tip}</p>

      <div className="space-y-1.5">
        {g.steps.map((s, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className={`text-[10px] font-bold ${g.color} shrink-0 tabular-nums`}>{i + 1}.</span>
            <span className="text-[11px] text-nc-muted leading-tight">{s}</span>
          </div>
        ))}
      </div>

      {g.science && (
        <div className="p-2 rounded-lg bg-nc-surface2/40 border border-nc-border/30">
          <p className="text-[9px] text-nc-muted/50 font-mono leading-snug">{g.science}</p>
        </div>
      )}

      <div className="pt-1 border-t border-nc-border/30 flex items-center justify-between">
        <p className="text-[10px] text-nc-muted/60">
          Bloc {blockIndex + 1}/6 · {blockLabel} · {typeLabel}
        </p>
        <p className="text-[9px] text-nc-muted/40">Adaptatif · NeuroCap</p>
      </div>
    </div>
  )
}

// ── Dérivation état EEG ML → objectif feedback ───────────────────────────────
function eegStateToObjective(mlState) {
  if (mlState === 'concentration') return 'focus'
  if (mlState === 'stress')        return 'stress'
  return 'neutral'
}

// ── Overlay Pause inter-bloc ──────────────────────────────────────────────────
function PauseOverlay({ remaining, blockNext, totalBlocks, successRate, newThreshold, baselineAlpha }) {
  const pct     = newThreshold && baselineAlpha ? Math.round((newThreshold / baselineAlpha) * 100) : null
  const srPct   = successRate !== null ? Math.round(successRate * 100) : null
  const srColor = srPct === null ? 'text-nc-muted'
    : srPct >= 60 ? 'text-emerald-400'
    : srPct >= 40 ? 'text-yellow-400'
    : 'text-red-400'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center"
         style={{ background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(10px)' }}>
      <div className="card p-10 text-center space-y-5 max-w-sm w-full mx-4">
        <p className="text-lg font-bold text-nc-text">Pause inter-bloc</p>
        <p className="text-5xl font-mono font-bold text-nc-accent">{remaining}s</p>
        <p className="text-sm text-nc-muted">
          {blockNext <= totalBlocks ? `Prochain : Bloc ${blockNext}/${totalBlocks}` : 'Repos guidé ensuite'}
        </p>

        {/* Résultat du bloc précédent */}
        {srPct !== null && (
          <div className={`p-3 rounded-xl border text-sm font-semibold ${
            srPct >= 60 ? 'bg-emerald-500/10 border-emerald-500/25' :
            srPct >= 40 ? 'bg-yellow-500/10 border-yellow-500/25'   :
                          'bg-red-500/10 border-red-500/25'
          }`}>
            <span className={srColor}>
              {srPct >= 60 ? '↑ Taux de succès élevé' : srPct >= 40 ? '↔ Niveau stable' : '↓ Taux de succès faible'}
            </span>
            <p className="text-xs text-nc-muted font-normal mt-0.5">
              {srPct}% du temps en zone cible
              {pct !== null && ` · Nouveau seuil : ${pct}% baseline`}
            </p>
          </div>
        )}

        <p className="text-xs text-nc-muted/60">Détendez-vous, respirez calmement</p>
      </div>
    </div>
  )
}

// ── Questionnaire pré-séance ──────────────────────────────────────────────────
function PreQuestionnaire({ onSubmit }) {
  const [values, setValues] = useState({ fatigue: 5, stress: 5, motivation: 5 })

  const items = [
    { key: 'fatigue',    label: 'Fatigue',    left: 'Reposé', right: 'Épuisé' },
    { key: 'stress',     label: 'Stress',     left: 'Calme',  right: 'Stressé' },
    { key: 'motivation', label: 'Motivation', left: 'Faible', right: 'Élevée' },
  ]

  return (
    <div className="max-w-xl mx-auto px-4 py-10 space-y-8 animate-fade-in">
      <div className="text-center space-y-2">
        <div className="w-14 h-14 rounded-3xl bg-nc-accent/15 flex items-center justify-center mx-auto">
          <Brain className="w-7 h-7 text-nc-accent" />
        </div>
        <h1 className="text-2xl font-bold text-nc-text">Avant la séance</h1>
        <p className="text-sm text-nc-muted">Comment vous sentez-vous en ce moment ? (échelle 1–10)</p>
      </div>

      <div className="space-y-6">
        {items.map(({ key, label, left, right }) => (
          <div key={key} className="card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-nc-text">{label}</span>
              <span className="font-mono font-bold text-nc-accent text-lg">{values[key]}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-nc-muted shrink-0 w-14 text-right">{left}</span>
              <input
                type="range" min={1} max={10} value={values[key]}
                onChange={e => setValues(v => ({ ...v, [key]: +e.target.value }))}
                className="flex-1 accent-nc-accent"
              />
              <span className="text-xs text-nc-muted shrink-0 w-14">{right}</span>
            </div>
            <div className="flex justify-between text-[9px] text-nc-muted/50 px-1">
              {[1,2,3,4,5,6,7,8,9,10].map(n => <span key={n}>{n}</span>)}
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={() => onSubmit(values)}
        className="btn-primary w-full py-3 text-sm font-semibold flex items-center justify-center gap-2"
      >
        Commencer la séance <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  )
}

// ── Questionnaire post-séance (NASA-TLX simplifié) ───────────────────────────
function PostQuestionnaire({ blockSuccessHistory, onSubmit }) {
  const [values, setValues] = useState({ focus: 5, calm: 5, fatigue_post: 5 })

  const avgSuccess = blockSuccessHistory.length > 0
    ? Math.round(blockSuccessHistory.reduce((a, b) => a + b, 0) / blockSuccessHistory.length)
    : null

  const items = [
    { key: 'focus',       label: 'Focus / Concentration',   left: 'Diffuse', right: 'Intense'     },
    { key: 'calm',        label: 'Calme intérieur',         left: 'Agité',   right: 'Très calme'  },
    { key: 'fatigue_post',label: 'Fatigue mentale ressentie',left: 'Aucune', right: 'Importante'  },
  ]

  return (
    <div className="max-w-xl mx-auto px-4 py-10 space-y-8 animate-fade-in">
      <div className="text-center space-y-2">
        <div className="w-14 h-14 rounded-3xl bg-emerald-500/15 flex items-center justify-center mx-auto">
          <CheckCircle2 className="w-7 h-7 text-emerald-400" />
        </div>
        <h1 className="text-2xl font-bold text-nc-text">Après la séance</h1>
        <p className="text-sm text-nc-muted">Évaluez votre ressenti post-séance (NASA-TLX simplifié)</p>
      </div>

      {/* Récapitulatif des blocs */}
      {blockSuccessHistory.length > 0 && (
        <div className="card p-4 space-y-2">
          <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide">Taux de succès par bloc</p>
          <div className="flex items-end gap-1.5 h-12">
            {blockSuccessHistory.map((rate, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className={`w-full rounded-t transition-all ${
                    rate >= 60 ? 'bg-emerald-500' : rate >= 40 ? 'bg-yellow-500' : 'bg-red-400'
                  }`}
                  style={{ height: `${Math.max(4, rate)}%` }}
                />
                <span className="text-[9px] text-nc-muted">B{i + 1}</span>
              </div>
            ))}
          </div>
          {avgSuccess !== null && (
            <p className="text-xs text-nc-muted text-center">
              Moyenne : <span className="text-nc-text font-semibold">{avgSuccess}%</span> en zone cible
            </p>
          )}
        </div>
      )}

      <div className="space-y-6">
        {items.map(({ key, label, left, right }) => (
          <div key={key} className="card p-5 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-nc-text">{label}</span>
              <span className="font-mono font-bold text-nc-accent text-lg">{values[key]}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-xs text-nc-muted shrink-0 w-14 text-right">{left}</span>
              <input
                type="range" min={1} max={10} value={values[key]}
                onChange={e => setValues(v => ({ ...v, [key]: +e.target.value }))}
                className="flex-1 accent-nc-accent"
              />
              <span className="text-xs text-nc-muted shrink-0 w-14">{right}</span>
            </div>
          </div>
        ))}
      </div>

      <button
        onClick={() => onSubmit(values)}
        className="btn-primary w-full py-3 text-sm font-semibold flex items-center justify-center gap-2"
      >
        Voir le rapport de séance <ChevronRight className="w-4 h-4" />
      </button>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
export default function FeedbackSession() {
  const navigate  = useNavigate()
  const location  = useLocation()
  const { user }  = useAuthStore()

  const {
    eeg_state: initialEegState = 'neutral',
    features_snapshot: initialFeatures = null,
    classification_confidence: initialConf = 0,
    mode: sessionMode = 'live',
  } = location.state || {}

  const isDemo = sessionMode === 'demo' || sessionMode === 'manual'

  // ── State session ──
  const [sessionId,    setSessionId]    = useState(null)
  const [sessionNum,   setSessionNum]   = useState(null)
  const [sessionPhase, setSessionPhase] = useState('phase1')
  const [sessionPalier,setSessionPalier]= useState(1)

  const [phase,        setPhase]        = useState(PHASES.PRE_QUESTIONNAIRE)
  const [blockIndex,   setBlockIndex]   = useState(0)
  const [pauseRemaining, setPauseRemaining] = useState(PAUSE_DURATION)
  const [currentMediaId, setCurrentMediaId] = useState(null)
  const [mediaPlayedLog, setMediaPlayedLog] = useState([])
  const [sessionReport,  setSessionReport]  = useState(null)
  const [sessionMetrics, setSessionMetrics] = useState(null)
  const [deltaAlpha,     setDeltaAlpha]     = useState(0)
  const [deltaBeta,      setDeltaBeta]      = useState(0)

  // Pre/Post questionnaire
  const [preData,  setPreData]  = useState(null)

  // ── Seuil adaptatif (refs pour performance intra-bloc) ──
  const baselineAlphaRef    = useRef([])    // Accumulés pendant BASELINE
  const alphaBaselineVal    = useRef(null)  // Moyenne baseline calculée
  const currentThreshold    = useRef(null)  // Seuil courant
  const ewmaAlphaRef        = useRef(null)  // EWMA lissé
  const blockSuccessRef     = useRef({ count: 0, total: 0 })

  // Display states pour les métriques d'adaptation
  const [thresholdDisplay,    setThresholdDisplay]    = useState(null)  // % de baseline
  const [blockSuccessRate,    setBlockSuccessRate]    = useState(null)  // % courant du bloc
  const [blockSuccessHistory, setBlockSuccessHistory] = useState([])    // par bloc

  // EEG accumulé pour delta
  const epochAlphaRef = useRef([])
  const epochBetaRef  = useRef([])

  // Features EEG en cours (live) — ref pour éviter de recréer le callback trop souvent
  const liveFeaturesRef = useRef(initialFeatures)

  // ── WebSockets ──
  const { eegFrame, epochFrame } = useEEGWebSocket()
  const { currentMedia, sessionReport: wsReport, send: fbSend } = useFeedbackSocket(sessionId)

  const [mlPrediction, setMlPrediction] = useState(
    isDemo
      ? { state: 'neutral', confidence: 0.75 }
      : (initialConf > 0 ? { state: initialEegState, confidence: initialConf } : null)
  )

  // Mise à jour état cognitif depuis le signal EEG (classificateur Z-score)
  // eegFrame.state = "concentration" | "neutral" | "stress" mis à jour à chaque époque
  useEffect(() => {
    if (!eegFrame?.state) return
    setMlPrediction(prev => {
      if (prev?.state === eegFrame.state) return prev
      const conf = epochFrame?.ml_prediction?.confidence ?? eegFrame.cqe_score ?? 0.6
      return { state: eegFrame.state, confidence: conf }
    })
  }, [eegFrame?.state])

  // Mode manuel : pas de WebSocket EEG — l'état est dérivé du questionnaire pré-séance.

  // ── Accumuler baseline alpha pendant BASELINE_CLOSED ──
  useEffect(() => {
    if (phase !== PHASES.BASELINE_CLOSED || !epochFrame?.features?.rel_alpha) return
    baselineAlphaRef.current.push(epochFrame.features.rel_alpha)
  }, [epochFrame, phase])

  // ── Mise à jour des features live en continu ──
  useEffect(() => {
    if (epochFrame?.features) liveFeaturesRef.current = epochFrame.features
  }, [epochFrame])

  // ── EWMA + tracking succès pendant FEEDBACK_BLOCK ──
  useEffect(() => {
    if (phase !== PHASES.FEEDBACK_BLOCK || !epochFrame?.features) return

    const alpha = epochFrame.features.rel_alpha ?? 0
    const beta  = epochFrame.features.rel_beta  ?? 0

    // EWMA (Wu et al., 2022 — α=0.3)
    ewmaAlphaRef.current = ewmaAlphaRef.current === null
      ? alpha
      : EWMA_ALPHA * alpha + (1 - EWMA_ALPHA) * ewmaAlphaRef.current

    // Tracking succès vs seuil adaptatif
    if (currentThreshold.current !== null) {
      blockSuccessRef.current.total++
      if (ewmaAlphaRef.current > currentThreshold.current) {
        blockSuccessRef.current.count++
      }
      const rate = blockSuccessRef.current.count / blockSuccessRef.current.total
      setBlockSuccessRate(Math.round(rate * 100))
    }

    // Accumuler pour delta global
    epochAlphaRef.current.push(alpha)
    epochBetaRef.current.push(beta)
  }, [epochFrame, phase])

  // Rapport WebSocket reçu
  useEffect(() => {
    if (wsReport) {
      setSessionReport(wsReport.report)
      setSessionMetrics(wsReport.metrics)
    }
  }, [wsReport])

  // Synchro média courant depuis WS feedback
  useEffect(() => {
    if (currentMedia) setCurrentMediaId(currentMedia.id)
  }, [currentMedia])

  // ── Démarrage session (au montage) ──
  useEffect(() => {
    const objective = initialEegState === 'stress' ? 'relaxation' : 'concentration'
    fbApi.startSession(objective, initialFeatures)
      .then(d => {
        setSessionId(d.session_id)
        setSessionNum(d.session_number ?? null)
        setSessionPhase(d.phase ?? 'phase1')
        setSessionPalier(d.palier ?? 1)
      })
      .catch(console.error)
  }, [])

  // ── Transitions automatiques de phases ──
  useEffect(() => {
    if (phase === PHASES.PRE_SESSION) {
      const t = setTimeout(() => setPhase(PHASES.BASELINE_CLOSED), 3000)
      return () => clearTimeout(t)
    }
    if (phase === PHASES.BASELINE_CLOSED) {
      const t = setTimeout(() => finalizeBaseline(), 120_000)
      return () => clearTimeout(t)
    }
  }, [phase])

  // ── Demande du premier média au début du premier bloc ──
  useEffect(() => {
    if (phase === PHASES.FEEDBACK_BLOCK && sessionId) {
      requestNextMedia()
    }
  }, [phase, sessionId])

  // ── Finalisation baseline → calcul seuil initial ──
  function finalizeBaseline() {
    const alphas = baselineAlphaRef.current
    if (alphas.length > 0) {
      const baseline = alphas.reduce((a, b) => a + b, 0) / alphas.length
      alphaBaselineVal.current   = baseline
      currentThreshold.current   = baseline * THRESHOLD_INIT_RATIO
      ewmaAlphaRef.current       = baseline
      setThresholdDisplay(Math.round((currentThreshold.current / baseline) * 100))
    }
    startBlock(0)
  }

  const requestNextMedia = useCallback(async () => {
    if (!sessionId) return
    try {
      const eegState    = eegStateToObjective(mlPrediction?.state)
      // En mode live/offline, on envoie les features et la confiance du classificateur
      // pour que le backend puisse affiner la sélection de médias.
      // En mode manuel, liveFeaturesRef.current = initialFeatures (snapshot du questionnaire)
      const features    = isDemo ? null : liveFeaturesRef.current
      const confidence  = mlPrediction?.confidence ?? null
      await fbApi.recommend(sessionId, eegState, null, features, confidence)
    } catch (e) {
      console.error('recommend error', e)
    }
  }, [sessionId, mlPrediction, isDemo])

  function startBlock(idx) {
    setBlockIndex(idx)
    setPhase(PHASES.FEEDBACK_BLOCK)
    epochAlphaRef.current = []
    epochBetaRef.current  = []
    blockSuccessRef.current = { count: 0, total: 0 }
    setBlockSuccessRate(null)
  }

  function handleBlockEnd() {
    // ── Calcul delta alpha/beta ──
    const alphas = epochAlphaRef.current
    const betas  = epochBetaRef.current
    if (alphas.length >= 2) {
      const half = Math.floor(alphas.length / 2)
      const da = alphas.slice(half).reduce((a, b) => a + b, 0) / half
             - alphas.slice(0, half).reduce((a, b) => a + b, 0) / half
      setDeltaAlpha(prev => prev + da)
    }
    if (betas.length >= 2) {
      const half = Math.floor(betas.length / 2)
      const db = betas.slice(half).reduce((a, b) => a + b, 0) / half
             - betas.slice(0, half).reduce((a, b) => a + b, 0) / half
      setDeltaBeta(prev => prev + db)
    }

    // ── Adaptation inter-blocs (Mou et al., 2024) ──
    const { count, total } = blockSuccessRef.current
    const successRate = total > 0 ? count / total : 0
    const successPct  = Math.round(successRate * 100)

    setBlockSuccessHistory(prev => [...prev, successPct])

    if (currentThreshold.current !== null && alphaBaselineVal.current !== null) {
      let newThreshold = currentThreshold.current
      if (successRate > SUCCESS_HIGH) newThreshold += THRESHOLD_STEP
      else if (successRate < SUCCESS_LOW) newThreshold -= THRESHOLD_STEP
      // Minimum = 70% de la baseline
      newThreshold = Math.max(newThreshold, alphaBaselineVal.current * THRESHOLD_MIN_RATIO)
      currentThreshold.current = newThreshold
      setThresholdDisplay(Math.round((newThreshold / alphaBaselineVal.current) * 100))
    }

    if (blockIndex < TOTAL_BLOCKS - 1) {
      setPhase(PHASES.INTER_BLOCK_PAUSE)
      setPauseRemaining(PAUSE_DURATION)
    } else {
      setPhase(PHASES.GUIDED_REST)
    }
  }

  // ── Compte à rebours pause inter-bloc ──
  useEffect(() => {
    if (phase !== PHASES.INTER_BLOCK_PAUSE) return
    const interval = setInterval(() => {
      setPauseRemaining(r => {
        if (r <= 1) {
          clearInterval(interval)
          startBlock(blockIndex + 1)
          return PAUSE_DURATION
        }
        return r - 1
      })
    }, 1000)
    return () => clearInterval(interval)
  }, [phase, blockIndex])

  const handleSkip = useCallback(async () => {
    if (!sessionId) return
    await fbApi.skip(sessionId, currentMediaId).catch(() => {})
    setMediaPlayedLog(prev => [...prev, { type: currentMedia?.type, filename: currentMedia?.filename, efficace: false }])
    await requestNextMedia()
  }, [sessionId, currentMediaId, currentMedia, requestNextMedia])

  const handleFeedbackSubmit = useCallback(async (vals) => {
    if (!sessionId) return
    const alphas = epochAlphaRef.current
    const betas  = epochBetaRef.current
    const half   = Math.floor(alphas.length / 2) || 1
    const da = alphas.length >= 2
      ? alphas.slice(half).reduce((a,b)=>a+b,0)/Math.max(half,1) - alphas.slice(0,half).reduce((a,b)=>a+b,0)/Math.max(half,1)
      : 0
    const db = betas.length >= 2
      ? betas.slice(half).reduce((a,b)=>a+b,0)/Math.max(half,1) - betas.slice(0,half).reduce((a,b)=>a+b,0)/Math.max(half,1)
      : 0

    await fbApi.submit({
      session_id: sessionId,
      media_id: currentMediaId,
      delta_alpha: da,
      delta_beta: db,
      ...vals,
    }).catch(() => {})

    const efficace = da > 0.05 && db < -0.05
    setMediaPlayedLog(prev => [...prev, {
      type: currentMedia?.type,
      filename: currentMedia?.filename,
      efficace,
    }])
    await requestNextMedia()
  }, [sessionId, currentMediaId, currentMedia, requestNextMedia])

  const handleEndSession = useCallback(async (postData = null) => {
    if (!sessionId) return
    const itemsEff = mediaPlayedLog.filter(m => m.efficace).length
    try {
      await fbApi.end({
        session_id: sessionId,
        items_played: mediaPlayedLog.length,
        items_efficaces: itemsEff,
        delta_alpha_global: deltaAlpha,
        delta_beta_global: deltaBeta,
        media_played: mediaPlayedLog,
      })
      // Le rapport arrive via WebSocket (wsReport)
      // Déclencher génération recommandations en arrière-plan
      const token = localStorage.getItem('neurocap_token')
      fetch(`/api/sessions/${sessionId}/media-recommendation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ eeg_state: 'neutral', top_n: 5 }),
      }).catch(() => {})
    } catch (e) {
      console.error('end session error', e)
    }
    setPhase(PHASES.POST_SESSION)
  }, [sessionId, mediaPlayedLog, deltaAlpha, deltaBeta])

  // ── Dérivés affichage ──────────────────────────────────────────────────────
  const eegState   = mlPrediction?.state ?? 'neutral'
  const showBreath = eegState === 'stress' && phase === PHASES.FEEDBACK_BLOCK
  const showFocus  = eegState === 'concentration' && phase === PHASES.FEEDBACK_BLOCK

  const phaseLabel = {
    [PHASES.PRE_QUESTIONNAIRE]:  'Questionnaire initial',
    [PHASES.PRE_SESSION]:        'Préparation',
    [PHASES.BASELINE_CLOSED]:    'Calibration — yeux fermés (2 min)',
    [PHASES.FEEDBACK_BLOCK]:     `Bloc actif ${blockIndex + 1}/${TOTAL_BLOCKS}`,
    [PHASES.INTER_BLOCK_PAUSE]:  'Pause',
    [PHASES.GUIDED_REST]:        'Repos guidé (3 min)',
    [PHASES.POST_QUESTIONNAIRE]: 'Évaluation post-séance',
    [PHASES.POST_SESSION]:       'Rapport de séance',
  }[phase] ?? ''

  const phaseInfo   = PHASE_LABELS[sessionPhase]  ?? PHASE_LABELS.phase1
  const palierInfo  = PALIER_LABELS[sessionPalier] ?? PALIER_LABELS[1]

  // ── Barre de protocole (header persistant) ──
  function ProtocolBar() {
    return (
      <div className="flex items-center gap-2 flex-wrap text-[10px]">
        {sessionNum && (
          <span className="font-bold text-nc-accent font-mono">S{sessionNum}/15</span>
        )}
        <span className={`px-2 py-0.5 rounded-full font-semibold ${phaseInfo.bg} ${phaseInfo.color}`}>
          {phaseInfo.label}
        </span>
        <span className={`font-semibold ${palierInfo.color}`}>{palierInfo.label}</span>
        {thresholdDisplay !== null && phase === PHASES.FEEDBACK_BLOCK && (
          <span className="text-nc-muted flex items-center gap-1">
            <Target className="w-3 h-3" /> Seuil : {thresholdDisplay}% baseline
          </span>
        )}
        {blockSuccessRate !== null && phase === PHASES.FEEDBACK_BLOCK && (
          <span className={`flex items-center gap-1 font-semibold ${
            blockSuccessRate >= 60 ? 'text-emerald-400' :
            blockSuccessRate >= 40 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            <Gauge className="w-3 h-3" /> {blockSuccessRate}% en zone
          </span>
        )}
      </div>
    )
  }

  // ── PRE_QUESTIONNAIRE ──────────────────────────────────────────────────────
  if (phase === PHASES.PRE_QUESTIONNAIRE) {
    return (
      <PreQuestionnaire
        onSubmit={data => {
          setPreData(data)
          // En mode sans EEG, dériver l'état cognitif depuis les réponses
          if (isDemo) {
            const derivedState = data.stress >= 7 ? 'stress'
              : (data.motivation >= 7 && data.fatigue <= 4) ? 'concentration'
              : 'neutral'
            setMlPrediction({ state: derivedState, confidence: 0.82 })
          }
          setPhase(PHASES.PRE_SESSION)
        }}
      />
    )
  }

  // ── PRE_SESSION ────────────────────────────────────────────────────────────
  if (phase === PHASES.PRE_SESSION) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center space-y-6">
        <div className="w-16 h-16 rounded-3xl bg-nc-accent/15 flex items-center justify-center mx-auto">
          <Brain className="w-8 h-8 text-nc-accent" />
        </div>
        <h1 className="text-2xl font-bold text-nc-text">Séance de Neurofeedback</h1>
        <ProtocolBar />
        {isDemo ? (
          <p className="text-sm px-4 py-2 rounded-xl bg-nc-accent/10 border border-nc-accent/25 text-nc-accent font-medium">
            Mode sans EEG — état issu du questionnaire, classification simulée
          </p>
        ) : (
          <p className="text-nc-muted">
            État EEG : <span className="text-nc-accent font-semibold capitalize">{initialEegState}</span>
          </p>
        )}
        <p className="text-sm text-nc-muted">Préparation de la session…</p>
        <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin mx-auto" />
      </div>
    )
  }

  // ── BASELINE ───────────────────────────────────────────────────────────────
  if (phase === PHASES.BASELINE_CLOSED) {
    const samplesCount = baselineAlphaRef.current.length
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center space-y-8">
        <ProtocolBar />
        <h1 className="text-xl font-bold text-nc-text">Calibration de référence</h1>
        <p className="text-nc-muted text-sm">
          Fermez les yeux et restez immobile pendant <strong>2 minutes</strong>.<br />
          Calcul de votre profil EEG individuel — IAPF et puissance alpha de référence.
        </p>
        {samplesCount > 0 && (
          <p className="text-xs text-nc-muted">{samplesCount} époques EEG enregistrées</p>
        )}
        <BreathingGuide active />
        <button
          onClick={finalizeBaseline}
          className="btn-primary px-8 py-3 rounded-xl text-sm font-semibold"
        >
          Passer la baseline →
        </button>
      </div>
    )
  }

  // ── POST_QUESTIONNAIRE ─────────────────────────────────────────────────────
  if (phase === PHASES.POST_QUESTIONNAIRE) {
    return (
      <PostQuestionnaire
        blockSuccessHistory={blockSuccessHistory}
        onSubmit={postData => handleEndSession(postData)}
      />
    )
  }

  // ── POST_SESSION (rapport) ─────────────────────────────────────────────────
  if (phase === PHASES.POST_SESSION) {
    return (
      <div className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-5">
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/feedback')}
            className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <h1 className="text-xl font-bold text-nc-text">Rapport de séance</h1>
          <div className="flex-1" />
          <ProtocolBar />
        </div>

        {/* Mini recap protocole */}
        {blockSuccessHistory.length > 0 && (
          <div className="card p-4 flex items-center gap-4 flex-wrap">
            <BarChart3 className="w-4 h-4 text-nc-accent shrink-0" />
            <div className="flex items-end gap-1 h-8">
              {blockSuccessHistory.map((rate, i) => (
                <div key={i} className="flex flex-col items-center gap-0.5">
                  <div
                    className={`w-5 rounded-sm ${rate >= 60 ? 'bg-emerald-500' : rate >= 40 ? 'bg-yellow-500' : 'bg-red-400'}`}
                    style={{ height: `${Math.max(3, rate * 0.28)}px` }}
                  />
                  <span className="text-[8px] text-nc-muted">B{i+1}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-nc-muted">
              Moy. <span className="font-semibold text-nc-text">
                {Math.round(blockSuccessHistory.reduce((a,b)=>a+b,0)/blockSuccessHistory.length)}%
              </span> en zone cible
            </p>
          </div>
        )}

        <FeedbackReport
          report={sessionReport}
          metrics={sessionMetrics}
          onClose={() => navigate('/dashboard')}
        />

        {/* Navigation post-séance */}
        <div className="flex gap-3 justify-end pt-1">
          <button
            onClick={() => navigate('/media-dashboard')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold border border-purple-500/30 bg-purple-500/10 text-purple-400 hover:bg-purple-500/20 transition-colors"
          >
            <Music className="w-4 h-4" />
            Médias recommandés
          </button>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary px-4 py-2 rounded-xl text-sm font-semibold"
          >
            Tableau de bord
          </button>
        </div>
      </div>
    )
  }

  // ── GUIDED REST ────────────────────────────────────────────────────────────
  if (phase === PHASES.GUIDED_REST) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-12 text-center space-y-8">
        <ProtocolBar />
        <h1 className="text-xl font-bold text-nc-text">Repos guidé</h1>
        <p className="text-nc-muted text-sm">
          Excellent travail ! Prenez <strong>3 minutes</strong> pour récupérer.
        </p>
        <BreathingGuide active />
        <button
          onClick={() => setPhase(PHASES.POST_QUESTIONNAIRE)}
          className="btn-primary px-8 py-3 rounded-xl text-sm font-semibold"
        >
          Continuer vers l'évaluation →
        </button>
      </div>
    )
  }

  // ── PAUSE INTER-BLOC ───────────────────────────────────────────────────────
  const showPause = phase === PHASES.INTER_BLOCK_PAUSE
  const lastBlockRate = blockSuccessHistory.length > 0
    ? blockSuccessHistory[blockSuccessHistory.length - 1] / 100
    : null

  // ── LAYOUT PRINCIPAL (FEEDBACK_BLOCK) ─────────────────────────────────────
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 space-y-4">
      {showPause && (
        <PauseOverlay
          remaining={pauseRemaining}
          blockNext={blockIndex + 2}
          totalBlocks={TOTAL_BLOCKS}
          successRate={lastBlockRate}
          newThreshold={currentThreshold.current}
          baselineAlpha={alphaBaselineVal.current}
        />
      )}

      {/* ── HEADER ── */}
      <div className="card p-3 space-y-2">
        <div className="flex items-center gap-4 flex-wrap">
          <button onClick={() => navigate('/feedback')}
            className="p-1.5 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
            <ArrowLeft className="w-4 h-4" />
          </button>

          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-nc-accent" />
            <span className="text-sm font-semibold text-nc-text">{phaseLabel}</span>
          </div>

          <div className="flex-1">
            <SessionBlockTimer
              blockIndex={blockIndex}
              totalBlocks={TOTAL_BLOCKS}
              blockDurationSec={BLOCK_DURATION}
              onBlockEnd={handleBlockEnd}
              paused={showPause}
            />
          </div>

          <button
            onClick={() => setPhase(PHASES.GUIDED_REST)}
            className="px-3 py-1.5 rounded-xl text-xs font-medium border border-red-500/25
                       text-red-400 hover:bg-red-500/10 transition-colors"
          >
            Terminer
          </button>
        </div>

        {/* Barre protocole */}
        <ProtocolBar />
      </div>

      {/* ── CONTENU PRINCIPAL ── */}
      <div className="grid lg:grid-cols-4 gap-4">

        {/* ── PANNEAU GAUCHE : mini EEG + guide IA + stats + adaptation ── */}
        <div className="lg:col-span-1 space-y-4">
          <div className="card p-4 space-y-3">
            <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide">Signal EEG</p>
            <MiniEEGOscilloscope
              wsData={eegFrame}
              eegState={eegState}
              mlPrediction={mlPrediction}
              features={epochFrame?.features}
            />
          </div>

          {/* Guide IA d'utilisation */}
          <AIGuideCard eegState={eegState} mediaType={currentMedia?.type} blockIndex={blockIndex} />

          {/* Guide Neuroscience détaillé */}
          <MediaNeuroscienceGuide
            mediaType={currentMedia?.type}
            eegState={eegState}
            mediaCategory={currentMedia?.category}
            eegBands={epochFrame?.features}
          />

          {/* Features clés */}
          {epochFrame?.features && (
            <div className="card p-4 space-y-2 text-xs">
              <p className="font-semibold text-nc-muted uppercase tracking-wide text-[10px]">Features EEG</p>
              {[
                ['Alpha',  `${((epochFrame.features.rel_alpha  ?? 0) * 100).toFixed(1)}%`],
                ['Beta',   `${((epochFrame.features.rel_beta   ?? 0) * 100).toFixed(1)}%`],
                ['Theta',  `${((epochFrame.features.rel_theta  ?? 0) * 100).toFixed(1)}%`],
                ['TBR',    (epochFrame.features.theta_beta ?? 0).toFixed(2)],
                ['EI',     (epochFrame.features.engagement ?? 0).toFixed(2)],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between">
                  <span className="text-nc-muted">{k}</span>
                  <span className="font-mono font-semibold text-nc-text">{v}</span>
                </div>
              ))}
            </div>
          )}

          {/* Métriques adaptation */}
          <div className="card p-4 space-y-3 text-xs">
            <p className="font-semibold text-nc-muted uppercase tracking-wide text-[10px]">Adaptation protocole</p>
            <div className="space-y-2">
              {thresholdDisplay !== null && (
                <div className="flex justify-between items-center">
                  <span className="text-nc-muted flex items-center gap-1">
                    <Target className="w-3 h-3" /> Seuil alpha
                  </span>
                  <span className="font-mono font-semibold text-nc-text">{thresholdDisplay}% base</span>
                </div>
              )}
              {blockSuccessRate !== null && (
                <div className="flex justify-between items-center">
                  <span className="text-nc-muted flex items-center gap-1">
                    <Gauge className="w-3 h-3" /> Succès bloc
                  </span>
                  <span className={`font-mono font-semibold ${
                    blockSuccessRate >= 60 ? 'text-emerald-400' :
                    blockSuccessRate >= 40 ? 'text-yellow-400' : 'text-red-400'
                  }`}>{blockSuccessRate}%</span>
                </div>
              )}
            </div>

            {/* Historique blocs précédents */}
            {blockSuccessHistory.length > 0 && (
              <div className="space-y-1">
                <p className="text-[9px] text-nc-muted/70 uppercase">Blocs précédents</p>
                <div className="flex gap-1 items-end h-6">
                  {blockSuccessHistory.map((rate, i) => (
                    <div key={i} className="flex flex-col items-center flex-1">
                      <div
                        className={`w-full rounded-sm ${rate >= 60 ? 'bg-emerald-500' : rate >= 40 ? 'bg-yellow-400' : 'bg-red-400'}`}
                        style={{ height: `${Math.max(2, rate * 0.22)}px` }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* ── ZONE PRINCIPALE ── */}
        <div className="lg:col-span-3 space-y-4">

          {/* Breathing / Focus guide */}
          {(showBreath || showFocus) && (
            <div className="card p-4">
              {showBreath && <BreathingGuide active />}
              {showFocus  && <FocusPoint active />}
            </div>
          )}

          {/* Zone média */}
          <div className="card p-4 space-y-3">
            {/* Bouton rafraîchir — propose un autre média via Thompson sampling */}
            <div className="flex items-center justify-between">
              <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide">
                Média en cours
              </p>
              <button
                onClick={requestNextMedia}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold
                           border border-nc-accent/30 text-nc-accent hover:bg-nc-accent/10
                           transition-all active:scale-95"
                title="Proposer automatiquement un autre feedback"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Autre feedback
              </button>
            </div>
            <MediaZone
              media={currentMedia}
              eegState={eegState}
              sessionId={sessionId}
              eegFeatures={epochFrame?.features ?? null}
              onSkip={handleSkip}
              onMediaEnd={requestNextMedia}
            />
          </div>

          {/* Barre feedback utilisateur */}
          <div className="card p-4">
            <UserFeedbackBar
              onSubmit={handleFeedbackSubmit}
              onSkip={handleSkip}
              canSkip
            />
          </div>
        </div>
      </div>
    </div>
  )
}
