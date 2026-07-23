/**
 * EEGFeedbackMode — Page de feedback adaptatif déclenchée depuis EEG live ou offline.
 * Distincte de FeedbackSession (protocole 15 séances) — aucun appel à /api/feedback/*.
 * Reçoit en location.state : { source, eegState, confidence, features }
 */
import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  ArrowLeft, Brain, Zap, HelpCircle, Gamepad2, Image, Video,
  Music, Wind, ThumbsUp, ThumbsDown, SkipForward, RefreshCw,
} from 'lucide-react'

import { recommendFeedback, stateGuideText } from '../utils/feedbackRecommender'
import { media as mediaApi, feedback as fbApi } from '../utils/api'
import { supabase } from '../lib/supabase'
import { useEEGWebSocket } from '../hooks/useEEGWebSocket'
import MiniEEGOscilloscope from '../components/feedback/MiniEEGOscilloscope'

import BreathingGuide   from '../components/feedback/BreathingGuide'
import FocusPoint       from '../components/feedback/FocusPoint'
import AudioFeedback    from '../components/feedback/AudioFeedback'
import CalibrationStep  from '../components/neurofeedback/CalibrationStep'
import ImageFeedback  from '../components/feedback/ImageFeedback'
import VideoFeedback  from '../components/feedback/VideoFeedback'
import MemoryGame     from '../components/feedback/games/MemoryGame'
import PuzzleGame     from '../components/feedback/games/PuzzleGame'
import SudokuGame     from '../components/feedback/games/SudokuGame'
import CalculGame     from '../components/feedback/games/CalculGame'
import EnigmeGame     from '../components/feedback/games/EnigmeGame'
import ColoringGame   from '../components/feedback/games/ColoringGame'

// ── Constantes protocole paliers ─────────────────────────────────────────────

// Types de feedback autorisés selon le palier (Protocole NeuroCap v1.0)
const PALIER_ALLOWED_TYPES = {
  1: ['breathing', 'audio'],                         // P1 Initiation : son seul + respiration
  2: ['breathing', 'audio', 'image', 'video'],       // P2 Apprentissage : + visuel
  3: ['breathing', 'audio', 'image', 'video', 'game'], // P3 Maîtrise : tout
  4: ['breathing', 'audio', 'image'],                // P4 Autonomie : feedback réduit, pas de jeu
}

const PALIER_INFO = {
  1: { label: 'P1 · Initiation',    color: 'text-purple-400', bg: 'bg-purple-500/10',  note: 'Respiration & audio uniquement'              },
  2: { label: 'P2 · Apprentissage', color: 'text-blue-400',   bg: 'bg-blue-500/10',    note: 'Sonore + visuel activés'                      },
  3: { label: 'P3 · Maîtrise',      color: 'text-emerald-400',bg: 'bg-emerald-500/10', note: 'Feedback complet + jeux disponibles'           },
  4: { label: 'P4 · Autonomie',     color: 'text-amber-400',  bg: 'bg-amber-500/10',   note: 'Feedback réduit — jeux désactivés (transfert)' },
}

const SESSION_PHASE_LABELS = {
  phase1: { label: 'Phase 1 · Découverte',    color: 'text-purple-400', bg: 'bg-purple-500/10'  },
  phase2: { label: 'Phase 2 · Apprentissage', color: 'text-blue-400',   bg: 'bg-blue-500/10'    },
  phase3: { label: 'Phase 3 · Consolidation', color: 'text-emerald-400',bg: 'bg-emerald-500/10' },
}

// ── Constantes ────────────────────────────────────────────────────────────────

const GAME_LIST = [
  { key: 'memory',   label: 'Mémoire',   desc: 'Mémoriser des paires' },
  { key: 'puzzle',   label: 'Puzzle',    desc: 'Reconstituer une image' },
  { key: 'sudoku',   label: 'Sudoku',    desc: 'Grille logique' },
  { key: 'calcul',   label: 'Calcul',    desc: 'Opérations mentales' },
  { key: 'enigme',   label: 'Énigme',    desc: 'Devinettes' },
  { key: 'coloring', label: 'Coloriage', desc: 'Mandala relaxant' },
]

const BREATH_RHYTHMS = [
  { key: '4-4', label: '4 — 4', desc: 'Cohérence cardiaque' },
  { key: '4-6', label: '4 — 6', desc: 'Activation parasympathique' },
  { key: '5-5', label: '5 — 5', desc: 'Relaxation profonde' },
]

const FEEDBACK_TYPES = [
  { key: 'game',      Icon: Gamepad2, label: 'Jeux'      },
  { key: 'image',     Icon: Image,    label: 'Images'    },
  { key: 'video',     Icon: Video,    label: 'Vidéos'    },
  { key: 'audio',     Icon: Music,    label: 'Audio'     },
  { key: 'breathing', Icon: Wind,     label: 'Respiration' },
]

const STATE_STYLE = {
  concentration: { label: 'Concentration', color: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/25' },
  focused:       { label: 'Concentration', color: 'text-emerald-400', bg: 'bg-emerald-500/15', border: 'border-emerald-500/25' },
  stress:        { label: 'Stress',         color: 'text-red-400',     bg: 'bg-red-500/15',     border: 'border-red-500/25'     },
  stressed:      { label: 'Stress',         color: 'text-red-400',     bg: 'bg-red-500/15',     border: 'border-red-500/25'     },
  uncertain:     { label: 'Incertain',      color: 'text-yellow-400',  bg: 'bg-yellow-500/15',  border: 'border-yellow-500/25'  },
  neutral:       { label: 'Neutre',         color: 'text-nc-muted',    bg: 'bg-nc-surface2',    border: 'border-nc-border'      },
}

// ── Breathing paramétrable (extension locale, n'altère pas BreathingGuide) ───

function BreathingVariant({ rhythm = '4-4' }) {
  // Parse rythme "inspire-expire"
  const [inS, outS] = rhythm.split('-').map(Number)
  const cycle = inS + outS

  const [phase,    setPhase]    = useState('inspire')
  const [progress, setProgress] = useState(0)
  const startRef = useRef(Date.now())
  const rafRef   = useRef(null)

  useEffect(() => {
    startRef.current = Date.now()
    const tick = () => {
      const elapsed = (Date.now() - startRef.current) / 1000
      const pos = elapsed % cycle
      if (pos < inS) {
        setPhase('inspire')
        setProgress(pos / inS)
      } else {
        setPhase('expire')
        setProgress((pos - inS) / outS)
      }
      rafRef.current = requestAnimationFrame(tick)
    }
    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [rhythm])

  const size = phase === 'inspire' ? 60 + progress * 40 : 100 - progress * 40

  return (
    <div className="flex flex-col items-center gap-4 py-4">
      <p className="text-[10px] font-semibold text-nc-muted uppercase tracking-wide">
        Rythme {rhythm.replace('-', ' — ')} secondes
      </p>
      <div className="relative flex items-center justify-center" style={{ width: 120, height: 120 }}>
        {[1, 0.6, 0.3].map((op, i) => (
          <div key={i} className="absolute rounded-full border border-blue-400/30"
            style={{ width: 80 + i * 20, height: 80 + i * 20, opacity: op * 0.4 }} />
        ))}
        <div className="rounded-full flex items-center justify-center" style={{
          width: size, height: size,
          background: phase === 'inspire'
            ? 'radial-gradient(circle, rgba(59,130,246,0.6), rgba(99,102,241,0.3))'
            : 'radial-gradient(circle, rgba(99,102,241,0.4), rgba(59,130,246,0.15))',
          boxShadow: `0 0 ${20 + size * 0.3}px rgba(99,102,241,${0.3 + progress * 0.2})`,
          transition: 'width 100ms linear, height 100ms linear',
        }}>
          <span className="text-white text-[10px] font-semibold opacity-70">
            {phase === 'inspire' ? '▲' : '▼'}
          </span>
        </div>
      </div>
      <div className="text-center">
        <p className="text-base font-semibold text-blue-300">
          {phase === 'inspire' ? 'Inspirez…' : 'Expirez…'}
        </p>
        <p className="text-xs text-nc-muted mt-1">
          {phase === 'inspire' ? inS : outS} secondes
        </p>
      </div>
      <div className="w-32 h-1 rounded-full bg-nc-surface2 overflow-hidden">
        <div className="h-full rounded-full bg-blue-400"
          style={{ width: `${progress * 100}%`, transition: 'width 100ms linear' }} />
      </div>
    </div>
  )
}

// ── Panneau gauche — contexte EEG ─────────────────────────────────────────────

function EEGContextPanel({ eegState, confidence, features, recommendation }) {
  const st      = STATE_STYLE[eegState] ?? STATE_STYLE.neutral
  const confPct = Math.round((confidence ?? 0) * 100)

  const featureRows = features ? [
    ['Alpha',      `${((features.rel_alpha  ?? features.alpha_power ?? 0) * 100).toFixed(1)}%`],
    ['Beta',       `${((features.rel_beta   ?? features.beta_power  ?? 0) * 100).toFixed(1)}%`],
    ['Theta',      `${((features.rel_theta  ?? features.theta_power ?? 0) * 100).toFixed(1)}%`],
    ['TBR',        (features.theta_beta ?? features.tbr ?? 0).toFixed(2)],
    ['EI',         (features.engagement ?? features.ei  ?? 0).toFixed(2)],
  ] : []

  return (
    <div className="space-y-4">
      {/* Badge état EEG */}
      <div className={`card p-4 border ${st.border} ${st.bg} space-y-2`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className={`w-4 h-4 ${st.color}`} />
            <span className={`text-sm font-bold ${st.color}`}>{st.label}</span>
          </div>
          <span className={`font-mono font-bold text-xl ${st.color}`}>{confPct}%</span>
        </div>
        {/* Barre confiance */}
        <div>
          <div className="flex justify-between text-[10px] text-nc-muted mb-0.5">
            <span>Confiance classifieur</span>
            <span>{confPct}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-nc-surface2 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${confPct >= 75 ? 'bg-emerald-500' : confPct >= 55 ? 'bg-yellow-500' : 'bg-red-500'}`}
              style={{ width: `${confPct}%` }}
            />
          </div>
        </div>
      </div>

      {/* Features clés */}
      {featureRows.length > 0 && (
        <div className="card p-4 space-y-2">
          <p className="text-[10px] font-semibold text-nc-muted uppercase tracking-wide">Features EEG</p>
          {featureRows.map(([k, v]) => (
            <div key={k} className="flex items-center gap-2">
              <span className="text-xs text-nc-muted w-20 shrink-0">{k}</span>
              <div className="flex-1 h-1 rounded-full bg-nc-surface2 overflow-hidden">
                <div className="h-full rounded-full bg-nc-accent/50"
                  style={{ width: `${Math.min(parseFloat(v) * (k === 'TBR' || k === 'EI' ? 33 : 1), 100)}%` }} />
              </div>
              <span className="text-xs font-mono font-semibold text-nc-text w-14 text-right">{v}</span>
            </div>
          ))}
        </div>
      )}

      {/* Pourquoi ce feedback */}
      {recommendation && (
        <div className="card p-4 space-y-2 border border-nc-accent/20">
          <div className="flex items-center gap-1.5">
            <HelpCircle className="w-3.5 h-3.5 text-nc-accent" />
            <p className="text-[10px] font-semibold text-nc-accent uppercase tracking-wide">Pourquoi ce feedback ?</p>
          </div>
          <p className="text-xs text-nc-muted leading-relaxed">{recommendation.reason}</p>
        </div>
      )}

      {/* Guide utilisateur */}
      <div className="card p-4 space-y-1.5 bg-nc-surface2/30">
        <p className="text-[10px] font-semibold text-nc-muted uppercase tracking-wide">Guide</p>
        <p className="text-xs text-nc-muted leading-relaxed">
          {recommendation?.guide ?? stateGuideText(eegState)}
        </p>
      </div>
    </div>
  )
}

// ── Zone d'évaluation utilisateur ─────────────────────────────────────────────

function EvalBar({ onSubmit }) {
  const [sam,   setSam]   = useState(null)
  const [liked, setLiked] = useState(null)
  const [sent,  setSent]  = useState(false)

  const submit = () => {
    onSubmit({ sam_score: sam, liked })
    setSent(true)
    setTimeout(() => setSent(false), 3000)
  }

  if (sent) {
    return (
      <div className="card p-4 flex items-center justify-center gap-2 text-sm text-emerald-400">
        <span>✓</span> Évaluation enregistrée
      </div>
    )
  }

  return (
    <div className="card p-4 space-y-3">
      <p className="text-xs font-semibold text-nc-muted">Comment tu te sens ?</p>

      {/* SAM 1-5 */}
      <div className="flex items-center gap-2">
        <span className="text-[10px] text-red-400 font-medium shrink-0">Stress</span>
        <div className="flex gap-1.5 flex-1 justify-center">
          {[1, 2, 3, 4, 5].map(v => (
            <button key={v}
              onClick={() => setSam(v)}
              className={`w-8 h-8 rounded-full text-xs font-bold border transition-all
                ${sam === v
                  ? 'bg-nc-accent border-nc-accent text-white scale-110'
                  : 'border-nc-border text-nc-muted hover:border-nc-accent hover:text-nc-accent'}`}
            >
              {v}
            </button>
          ))}
        </div>
        <span className="text-[10px] text-emerald-400 font-medium shrink-0">Concentr.</span>
      </div>

      {/* Boutons */}
      <div className="flex gap-2">
        <button
          onClick={() => setLiked(true)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border flex-1 justify-center transition-all
            ${liked === true ? 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400' : 'border-nc-border text-nc-muted hover:border-emerald-500/30 hover:text-emerald-400'}`}
        >
          <ThumbsUp className="w-3.5 h-3.5" /> Ce feedback m'aide
        </button>
        <button
          onClick={() => setLiked(false)}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border flex-1 justify-center transition-all
            ${liked === false ? 'bg-red-500/20 border-red-500/40 text-red-400' : 'border-nc-border text-nc-muted hover:border-red-500/30 hover:text-red-400'}`}
        >
          <ThumbsDown className="w-3.5 h-3.5" /> Pas pour moi
        </button>
        <button
          onClick={submit}
          disabled={sam === null && liked === null}
          className="px-3 py-1.5 rounded-xl text-xs font-semibold btn-primary disabled:opacity-40 shrink-0"
        >
          Valider
        </button>
      </div>
    </div>
  )
}

// ═══════════════════════════════════════════════════════════════════════════════
// Page principale
// ═══════════════════════════════════════════════════════════════════════════════

export default function EEGFeedbackMode() {
  const navigate = useNavigate()
  const location = useLocation()

  const {
    source       = 'live',
    eegState: rawEegState = 'neutral',
    confidence   = 0,
    features     = null,
    fromProtocol = false,
    sessionN     = null,
  } = location.state ?? {}

  // Normaliser l'état EEG vers les valeurs attendues par l'API backend (stress | focus | neutral)
  const eegState = (rawEegState === 'focused' || rawEegState === 'concentration') ? 'focus'
    : (rawEegState === 'stressed') ? 'stress'
    : (rawEegState === 'relaxed')  ? 'neutral'
    : rawEegState

  // ── Statut protocole (palier, phase, séance) ──
  const [protocolStatus, setProtocolStatus] = useState({ session_number: null, phase: 'phase1', palier: 2, completed: 0, remaining: 15 })
  useEffect(() => {
    fbApi.status().then(d => setProtocolStatus(d)).catch(() => {})
  }, [])

  const palier       = protocolStatus.palier ?? 2
  // Hors protocole : tous les types disponibles sans restriction de palier
  const allowedTypes = fromProtocol
    ? (PALIER_ALLOWED_TYPES[palier] ?? PALIER_ALLOWED_TYPES[2])
    : ['breathing', 'audio', 'image', 'video', 'game']

  // ── Recommendation initiale (prend en compte le palier) ──
  const recommendation = recommendFeedback(eegState, features ?? {}, confidence, palier)

  // ── State — respiration toujours en premier, puis switch vers la recommandation ──
  // Si breathing non autorisé par palier, démarrer directement sur le type recommandé autorisé
  const initialType = allowedTypes.includes('breathing') ? 'breathing'
    : allowedTypes.includes(recommendation.type) ? recommendation.type
    : allowedTypes[0] ?? 'audio'

  const [feedbackType,   setFeedbackType]   = useState(initialType)
  const [selectedGame,   setSelectedGame]   = useState(recommendation.subtype ?? 'memory')
  const [breathRhythm,   setBreathRhythm]   = useState(
    recommendation.type === 'breathing' ? (recommendation.subtype ?? '4-4') : '5-5'
  )
  const [medias,         setMedias]         = useState([])
  const [mediasLoading,  setMediasLoading]  = useState(false)
  const [selectedMedia,  setSelectedMedia]  = useState(null)
  const [evalLog,        setEvalLog]        = useState([])  // local only
  const [illusions,      setIllusions]      = useState([])
  const [illusionsLoading, setIllusionsLoading] = useState(false)
  const [selectedIllusion, setSelectedIllusion] = useState(null)
  const [illusionGuide,  setIllusionGuide]  = useState(false)
  const [imageSubTab,    setImageSubTab]    = useState('images')  // 'images' | 'illusions'
  const sessionStartRef = useRef(Date.now())

  // ── Phase calibration → session ──
  // Calibration uniquement dans le flux protocole — accès libre passe directement en session
  const [sessionPhase, setSessionPhase] = useState('calibration')
  const enterSession = () => setSessionPhase('session')

  // ── Signal EEG temps réel (seulement si source === 'live') ──
  const liveEEG = useEEGWebSocket()

  // ── Détection électrode déconnectée ──
  const [electrodeOff, setElectrodeOff] = useState(false)
  useEffect(() => {
    if (liveEEG.rejectedFrame?.reason === 'electrode_off') setElectrodeOff(true)
  }, [liveEEG.rejectedFrame])
  useEffect(() => {
    if (liveEEG.epochFrame?.features) setElectrodeOff(false)
  }, [liveEEG.epochFrame])

  // ── Charger les illusions optiques HTML internes (Feedback_METADATA/illusions/) ──
  useEffect(() => {
    if (feedbackType !== 'image') return
    setIllusionsLoading(true)
    fetch(`/api/media/illusions/internal?eeg_state=${encodeURIComponent(eegState)}`)
      .then(r => r.ok ? r.json() : [])
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          // Ajouter l'URL backend pour chaque illusion
          setIllusions(data.map(ill => ({
            ...ill,
            url: `/api/media/illusions/html/${encodeURIComponent(ill.filename)}`,
          })))
        } else {
          setIllusions([])
        }
      })
      .catch(() => setIllusions([]))
      .finally(() => setIllusionsLoading(false))
  }, [feedbackType, eegState])

  // ── Chargement médias quand type change ──
  useEffect(() => {
    if (feedbackType === 'game' || feedbackType === 'breathing') return
    setMediasLoading(true)
    setSelectedMedia(null)
    mediaApi.list(feedbackType, fromProtocol ? eegState : null)
      .then(data => {
        const list = Array.isArray(data) ? data : (data.medias ?? data.items ?? [])
        setMedias(list)
        if (list.length > 0) setSelectedMedia(list[0])
      })
      .catch(() => setMedias([]))
      .finally(() => setMediasLoading(false))
  }, [feedbackType, eegState])

  const handleTypeChange = useCallback((type) => {
    setFeedbackType(type)
    if (type === 'game') setSelectedGame(recommendation.subtype ?? 'memory')
    if (type === 'breathing') setBreathRhythm(recommendation.subtype ?? '4-4')
  }, [recommendation])

  const handleEval = useCallback((vals) => {
    setEvalLog(prev => [...prev, {
      ...vals,
      feedbackType,
      selectedGame:  feedbackType === 'game'      ? selectedGame  : undefined,
      mediaId:       selectedMedia?.id,
      t: Date.now(),
    }])
    // Log non-bloquant vers backend (optionnel)
    const duration = Math.round((Date.now() - sessionStartRef.current) / 1000)
    fetch('/api/eeg-feedback/log', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json',
                 Authorization: `Bearer ${localStorage.getItem('neurocap_token')}` },
      body: JSON.stringify({
        source,
        eeg_state:        eegState,
        confidence,
        feedback_type:    feedbackType,
        feedback_subtype: feedbackType === 'game' ? selectedGame : (feedbackType === 'breathing' ? breathRhythm : null),
        user_sam_score:   vals.sam_score ?? null,
        liked:            vals.liked ?? null,
        duration_seconds: duration,
      }),
    }).catch(() => {})
  }, [source, eegState, confidence, feedbackType, selectedGame, breathRhythm, selectedMedia])

  // ── Rafraîchissement — propose un autre feedback au hasard ──────────────────
  const handleRefreshMedia = useCallback(() => {
    if (feedbackType === 'game') {
      const allowed  = GAME_LIST.filter(g => g.key !== selectedGame)
      const pick     = allowed.length > 0
        ? allowed[Math.floor(Math.random() * allowed.length)]
        : GAME_LIST[Math.floor(Math.random() * GAME_LIST.length)]
      setSelectedGame(pick.key)
    } else if (feedbackType === 'breathing') {
      const allowed  = BREATH_RHYTHMS.filter(r => r.key !== breathRhythm)
      const pick     = allowed[Math.floor(Math.random() * allowed.length)]
      if (pick) setBreathRhythm(pick.key)
    } else {
      // image / video / audio : pick aléatoire différent du courant
      if (medias.length > 1) {
        const others = medias.filter(m => m.id !== selectedMedia?.id)
        const pick   = others[Math.floor(Math.random() * others.length)]
        if (pick) setSelectedMedia(pick)
      } else if (medias.length === 1) {
        // Un seul média → recharger la liste (nouvel appel API)
        setMediasLoading(true)
        mediaApi.list(feedbackType, fromProtocol ? eegState : null)
          .then(data => {
            const list = Array.isArray(data) ? data : (data.medias ?? data.items ?? [])
            setMedias(list)
            if (list.length > 0) setSelectedMedia(list[0])
          })
          .catch(() => {})
          .finally(() => setMediasLoading(false))
      }
    }
  }, [feedbackType, selectedGame, breathRhythm, medias, selectedMedia, eegState])

  const st = STATE_STYLE[eegState] ?? STATE_STYLE.neutral

  // ── Rendu médias standard (image / vidéo / audio depuis API) ────────────────

  function renderStandardMedia() {
    if (mediasLoading) {
      return (
        <div className="card flex items-center justify-center h-48">
          <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
        </div>
      )
    }

    if (medias.length === 0) {
      return (
        <div className="card flex flex-col items-center justify-center h-48 gap-3 text-nc-muted">
          <p className="text-sm">Aucun média disponible pour ce type</p>
          <p className="text-xs text-nc-muted/60 text-center max-w-xs">
            Ajoutez des fichiers dans Supabase Storage → bucket <code className="text-nc-accent">neurofeedback-media</code>, puis exécutez le seed SQL.
          </p>
          <button onClick={() => handleTypeChange('game')}
            className="text-xs underline text-nc-accent">
            Passer aux jeux →
          </button>
        </div>
      )
    }

    const currentIdx = medias.findIndex(m => m.id === selectedMedia?.id)
    const displayIdx = currentIdx >= 0 ? currentIdx : 0

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide">
            {feedbackType === 'image' ? 'Image' : feedbackType === 'video' ? 'Vidéo' : 'Audio'}
          </p>
          <button
            onClick={handleRefreshMedia}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold
                       border border-nc-accent/30 text-nc-accent hover:bg-nc-accent/10
                       transition-all active:scale-95"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Autre feedback
          </button>
        </div>

        {selectedMedia && (
          <div className="card overflow-hidden">
            {feedbackType === 'image' && <ImageFeedback src={selectedMedia.url_cloudinary || selectedMedia.url} initialPreset="Naturel" />}
            {feedbackType === 'video' && <VideoFeedback src={selectedMedia.url_cloudinary || selectedMedia.url} />}
            {feedbackType === 'audio' && (
              <div className="p-6"><AudioFeedback src={selectedMedia.url_cloudinary || selectedMedia.url} /></div>
            )}
          </div>
        )}

        {medias.length > 1 && (
          <div className="flex gap-2">
            <button
              onClick={() => setSelectedMedia(medias[(displayIdx - 1 + medias.length) % medias.length])}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl
                         text-xs text-nc-muted hover:text-nc-text border border-nc-border hover:bg-nc-surface2 transition-colors"
            >
              ← Précédent
            </button>
            <button
              onClick={() => setSelectedMedia(medias[(displayIdx + 1) % medias.length])}
              className="flex-1 flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-xl
                         text-xs text-nc-muted hover:text-nc-text border border-nc-border hover:bg-nc-surface2 transition-colors"
            >
              <SkipForward className="w-3.5 h-3.5" /> Suivant
            </button>
          </div>
        )}
      </div>
    )
  }

  // ── Rendu zone feedback droite ──────────────────────────────────────────────

  function renderFeedbackContent() {
    if (feedbackType === 'breathing') {
      return (
        <div className="card p-6 space-y-5">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide">Rythme respiratoire</p>
            <button
              onClick={handleRefreshMedia}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold
                         border border-nc-accent/30 text-nc-accent hover:bg-nc-accent/10 transition-colors"
              title="Essayer un autre rythme"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Autre rythme
            </button>
          </div>
          <div className="flex gap-2 flex-wrap">
            {BREATH_RHYTHMS.map(r => (
              <button key={r.key}
                onClick={() => setBreathRhythm(r.key)}
                className={`flex-1 min-w-[90px] px-3 py-2.5 rounded-xl border text-xs font-semibold transition-all text-center
                  ${breathRhythm === r.key ? 'bg-blue-500/20 border-blue-500/40 text-blue-300' : 'border-nc-border text-nc-muted hover:border-blue-500/30'}`}
              >
                <span className="block font-mono text-sm">{r.label}</span>
                <span className="text-[10px] opacity-70">{r.desc}</span>
              </button>
            ))}
          </div>
          <BreathingVariant rhythm={breathRhythm} />
          {(eegState === 'concentration' || eegState === 'focused') && <FocusPoint active />}
        </div>
      )
    }

    if (feedbackType === 'game') {
      return (
        <div className="space-y-4">
          {/* Header jeu + bouton refresh */}
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide">Jeu cognitif</p>
            <button
              onClick={handleRefreshMedia}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold
                         border border-nc-accent/30 text-nc-accent hover:bg-nc-accent/10 transition-colors"
              title="Proposer un autre jeu"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Autre jeu
            </button>
          </div>

          {/* Grille sélection jeu */}
          <div className="grid grid-cols-3 sm:grid-cols-6 gap-2">
            {GAME_LIST.map(g => (
              <button key={g.key}
                onClick={() => setSelectedGame(g.key)}
                className={`p-3 rounded-xl border text-center transition-all
                  ${selectedGame === g.key
                    ? 'bg-nc-accent/20 border-nc-accent text-nc-accent'
                    : 'border-nc-border text-nc-muted hover:border-nc-accent/40 hover:text-nc-text'}`}
              >
                <p className="text-xs font-semibold">{g.label}</p>
                <p className="text-[9px] text-nc-muted/70 mt-0.5 hidden sm:block">{g.desc}</p>
                {g.key === recommendation.subtype && selectedGame !== g.key && (
                  <span className="text-[8px] text-nc-accent mt-0.5 block">★ recommandé</span>
                )}
              </button>
            ))}
          </div>

          {/* Jeu sélectionné */}
          <div className="card p-2 min-h-[300px]">
            {selectedGame === 'memory'   && <MemoryGame />}
            {selectedGame === 'puzzle'   && <PuzzleGame />}
            {selectedGame === 'sudoku'   && <SudokuGame />}
            {selectedGame === 'calcul'   && <CalculGame />}
            {selectedGame === 'enigme'   && <EnigmeGame />}
            {selectedGame === 'coloring' && <ColoringGame />}
          </div>
        </div>
      )
    }

    // ── Sous-onglets image / illusions optiques ───────────────────────────────
    if (feedbackType === 'image') {
      return (
        <div className="space-y-4">
          {/* Sous-onglets */}
          <div className="flex gap-2">
            <button
              onClick={() => setImageSubTab('images')}
              className={`flex-1 py-2 rounded-xl text-xs font-semibold border transition-all
                ${imageSubTab === 'images'
                  ? 'bg-nc-accent/20 border-nc-accent text-nc-accent'
                  : 'border-nc-border text-nc-muted hover:border-nc-accent/30'}`}
            >
              🖼️ Images
            </button>
            <button
              onClick={() => setImageSubTab('illusions')}
              className={`flex-1 py-2 rounded-xl text-xs font-semibold border transition-all
                ${imageSubTab === 'illusions'
                  ? 'bg-purple-500/20 border-purple-500/40 text-purple-400'
                  : 'border-nc-border text-nc-muted hover:border-purple-500/30'}`}
            >
              🌀 Illusions Optiques Interactives
            </button>
          </div>

          {/* Sous-onglet images standard */}
          {imageSubTab === 'images' && renderStandardMedia()}

          {/* Sous-onglet illusions optiques HTML */}
          {imageSubTab === 'illusions' && (
            <div className="space-y-4">
              {/* Guide utilisateur */}
              <div className="card p-4 border border-purple-500/20 bg-purple-500/5 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-base">🌀</span>
                    <p className="text-xs font-semibold text-purple-400">Guide — Illusions Optiques Interactives</p>
                  </div>
                  <button
                    onClick={() => setIllusionGuide(v => !v)}
                    className="text-[10px] text-nc-muted hover:text-nc-text transition-colors"
                  >
                    {illusionGuide ? 'Masquer ▲' : 'Voir le guide ▼'}
                  </button>
                </div>
                {illusionGuide && (
                  <div className="space-y-1.5 text-xs text-nc-muted leading-relaxed">
                    <p>• <strong className="text-nc-text">Fixez le centre</strong> de l'illusion pendant 20–30 secondes pour activer les zones visuelles corticales.</p>
                    <p>• <strong className="text-nc-text">Déplacez lentement le regard</strong> autour de l'image pour observer les distorsions perceptuelles.</p>
                    <p>• Pour les illusions <em>interactives</em> : survolez ou cliquez les zones colorées selon les instructions affichées.</p>
                    <p>• Effet neurofeedback : les illusions optiques stimulent le cortex visuel V1/V2 et favorisent la synchronisation des ondes alpha (8–12 Hz).</p>
                    <p>• Si vous ressentez une gêne visuelle, fermez les yeux 10 secondes puis revenez à la séance.</p>
                  </div>
                )}
              </div>

              {/* Liste des illusions */}
              {illusionsLoading ? (
                <div className="card flex items-center justify-center h-32">
                  <div className="w-6 h-6 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin" />
                </div>
              ) : illusions.length === 0 ? (
                <div className="card flex flex-col items-center justify-center h-32 gap-2 text-nc-muted">
                  <span className="text-2xl">🌀</span>
                  <p className="text-xs">Aucune illusion disponible pour cet état EEG</p>
                  <p className="text-[10px] text-nc-muted/60">Backend : /api/media/illusions/internal</p>
                </div>
              ) : (
                <div className="space-y-3">
                  <p className="text-[10px] text-nc-muted font-semibold uppercase tracking-wide">
                    {illusions.length} illusion{illusions.length > 1 ? 's' : ''} disponible{illusions.length > 1 ? 's' : ''}
                  </p>
                  <div className="flex gap-1.5 flex-wrap max-h-24 overflow-y-auto pr-1">
                    {illusions.map((ill, i) => (
                      <button key={ill.id ?? i}
                        onClick={() => setSelectedIllusion(ill)}
                        className={`px-2.5 py-1 rounded-lg text-[10px] font-medium border transition-all shrink-0
                          ${selectedIllusion?.id === ill.id
                            ? 'bg-purple-500/20 border-purple-500/40 text-purple-400'
                            : 'border-nc-border text-nc-muted hover:border-purple-400/40 hover:text-nc-text'}`}
                        title={ill.titre ?? ill.filename}
                      >
                        🌀 {(ill.titre ?? ill.filename ?? `Illusion ${i + 1}`).slice(0, 22)}
                      </button>
                    ))}
                  </div>

                  {selectedIllusion && (
                    <div className="card overflow-hidden space-y-2">
                      <div className="px-3 pt-3 flex items-center gap-3 justify-between flex-wrap">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="text-xs font-semibold text-purple-400 truncate">
                            {selectedIllusion.titre ?? selectedIllusion.filename?.replace(/\.[^.]+$/, '') ?? 'Illusion optique'}
                          </p>
                          {selectedIllusion.badge_eeg && (
                            <span className="text-[9px] px-2 py-0.5 rounded-full bg-purple-500/15 border border-purple-500/30 text-purple-300 font-semibold">
                              ⚡ {selectedIllusion.badge_eeg}
                            </span>
                          )}
                          {selectedIllusion.effet_cognitif && (
                            <span className="text-[9px] px-2 py-0.5 rounded-full bg-nc-surface2 border border-nc-border text-nc-muted">
                              {selectedIllusion.effet_cognitif.replace('_', ' ')}
                            </span>
                          )}
                        </div>
                        <button
                          onClick={() => setSelectedIllusion(null)}
                          className="text-[10px] text-nc-muted hover:text-nc-text transition-colors"
                        >
                          ✕ Fermer
                        </button>
                      </div>
                      <iframe
                        key={selectedIllusion.filename}
                        src={selectedIllusion.url}
                        title={selectedIllusion.titre ?? selectedIllusion.filename}
                        className="w-full border-0"
                        style={{ height: 480 }}
                        sandbox="allow-scripts allow-same-origin"
                      />
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )
    }

    // ── video / audio — depuis Supabase Storage ───────────────────────────────
    return renderStandardMedia()
  }

  // ── Phase calibration ───────────────────────────────────────────────────────

  if (sessionPhase === 'calibration') {
    return (
      <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">

        {/* En-tête avec état EEG classifié */}
        <div className="flex items-center gap-3">
          <button onClick={() => navigate('/eeg')}
            className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="flex-1">
            <h1 className="text-lg font-bold text-nc-text">Calibration avant séance</h1>
            <p className="text-xs text-nc-muted mt-0.5">
              État EEG classifié :&nbsp;
              <span className={`font-semibold ${(STATE_STYLE[eegState] ?? STATE_STYLE.neutral).color}`}>
                {(STATE_STYLE[eegState] ?? STATE_STYLE.neutral).label}
              </span>
              {confidence > 0 && (
                <span className="text-nc-muted/60 ml-2">· {Math.round(confidence * 100)}% confiance</span>
              )}
            </p>
          </div>
        </div>

        {/* Composant calibration (skippable) */}
        <CalibrationStep
          onComplete={enterSession}
          onSkip={enterSession}
        />
      </div>
    )
  }

  // ── Layout ──────────────────────────────────────────────────────────────────

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 space-y-4">

      {/* ── En-tête ── */}
      <div className="flex items-center gap-3 flex-wrap">
        <button onClick={() => navigate('/eeg')}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="w-10 h-10 rounded-2xl bg-nc-accent/15 flex items-center justify-center">
          <Brain className="w-5 h-5 text-nc-accent" />
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-nc-text">Feedback Adaptatif EEG</h1>
          <p className="text-xs text-nc-muted">
            Source : {source === 'live' ? 'signal temps réel' : source === 'manual' ? 'saisie manuelle' : 'fichier hors-ligne'}
            {' · '}
            <span className={st.color}>{st.label}</span>
            {' · '}
            {Math.round((confidence ?? 0) * 100)}% de confiance
          </p>
        </div>
        {source === 'live' && (
          <button
            onClick={() => navigate('/eeg/live')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border
                       border-nc-accent/30 text-nc-accent hover:bg-nc-accent/10 transition-colors"
          >
            <Zap className="w-3.5 h-3.5" /> Retour EEG live
          </button>
        )}
      </div>


      {/* ── Badge mode manuel ── */}
      {source === 'manual' && (
        <div className="card p-3 flex items-center gap-3 border border-amber-500/20 bg-amber-500/5">
          <Brain className="w-4 h-4 text-amber-400 shrink-0" />
          <div className="flex-1">
            <span className="text-[10px] font-semibold text-amber-400 uppercase tracking-wide">
              Mode Exploration Manuelle
            </span>
            <span className="text-[10px] text-nc-muted ml-3">
              État saisi manuellement · Aucun casque EEG requis · Les recommandations sont identiques au mode live
            </span>
          </div>
          <button
            onClick={() => navigate('/eeg-manual')}
            className="text-[10px] text-amber-400 border border-amber-500/30 px-2.5 py-1 rounded-lg
                       hover:bg-amber-500/10 transition-colors shrink-0"
          >
            Changer d'état
          </button>
        </div>
      )}

      {/* ── Retour protocole si fromProtocol ── */}
      {fromProtocol && sessionN && (
        <div className="card p-3 flex items-center gap-3 border border-nc-accent/20 bg-nc-accent/5">
          <Brain className="w-4 h-4 text-nc-accent shrink-0" />
          <p className="text-xs text-nc-muted flex-1">
            Session dans le cadre du protocole — Séance {sessionN}
          </p>
          <button
            onClick={() => navigate(`/protocol/session/${sessionN}`, {
              state: { eegState, confidence, features, source }
            })}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold
                       bg-nc-accent/15 text-nc-accent border border-nc-accent/30 hover:bg-nc-accent/25 transition-colors"
          >
            Continuer vers la séance →
          </button>
        </div>
      )}

      {/* ── Bannière protocole ── */}
      {(() => {
        const phInfo = SESSION_PHASE_LABELS[protocolStatus.phase] ?? SESSION_PHASE_LABELS.phase1
        const palInfo = PALIER_INFO[palier] ?? PALIER_INFO[2]
        const completed  = protocolStatus.completed ?? 0
        const remaining  = protocolStatus.remaining ?? 15
        const sessionNum = protocolStatus.session_number
        const progress   = Math.round((completed / 15) * 100)

        return (
          <div className="card p-3 flex items-center gap-3 flex-wrap text-xs">
            {/* Progression */}
            <div className="flex items-center gap-2 shrink-0">
<div className="w-24 h-1.5 rounded-full bg-nc-surface2 overflow-hidden">
                <div className="h-full rounded-full bg-gradient-to-r from-purple-500 via-blue-500 to-emerald-500"
                     style={{ width: `${progress}%` }} />
              </div>
              <span className="text-nc-muted font-mono">{completed}/15</span>
            </div>

            <span className="text-nc-border">|</span>

            {/* Phase */}
            <span className={`px-2 py-0.5 rounded-full font-semibold ${phInfo.bg} ${phInfo.color}`}>
              {phInfo.label}
            </span>

            {/* Palier */}
            <span className={`px-2 py-0.5 rounded-full font-semibold ${palInfo.bg} ${palInfo.color}`}>
              {palInfo.label}
            </span>

            {/* Note palier */}
            <span className="text-nc-muted hidden sm:inline">{palInfo.note}</span>

            {/* Séances restantes */}
            <span className="ms-auto font-semibold text-nc-muted">
              {remaining} séance{remaining !== 1 ? 's' : ''} restante{remaining !== 1 ? 's' : ''}
            </span>
          </div>
        )
      })()}

      {/* ── Layout deux colonnes ── */}
      <div className="grid lg:grid-cols-4 gap-4">

        {/* ── Colonne gauche — carte EEG holo + contexte ── */}
        <div className="lg:col-span-1 space-y-4">

          {/* Carte holographique EEG live */}
          {source === 'live' && (
            <div className="relative overflow-hidden rounded-2xl border border-emerald-400/25
                            bg-[#060e18] shadow-[0_0_32px_rgba(52,211,153,0.12),inset_0_0_24px_rgba(52,211,153,0.04)]">

              {/* Scan lines */}
              <div className="absolute inset-0 pointer-events-none"
                style={{ background: 'repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(52,211,153,0.025) 3px,rgba(52,211,153,0.025) 4px)' }} />

              {/* Grille holographique */}
              <div className="absolute inset-0 pointer-events-none opacity-40"
                style={{ background: 'linear-gradient(rgba(52,211,153,0.04) 1px,transparent 1px),linear-gradient(90deg,rgba(52,211,153,0.04) 1px,transparent 1px)', backgroundSize: '18px 18px' }} />

              {/* Coins déco */}
              <div className="absolute top-2.5 left-2.5 w-5 h-5 border-t-2 border-l-2 border-emerald-400/60" />
              <div className="absolute top-2.5 right-2.5 w-5 h-5 border-t-2 border-r-2 border-emerald-400/60" />
              <div className="absolute bottom-2.5 left-2.5 w-5 h-5 border-b-2 border-l-2 border-emerald-400/60" />
              <div className="absolute bottom-2.5 right-2.5 w-5 h-5 border-b-2 border-r-2 border-emerald-400/60" />

              {/* Ligne de balayage animée */}
              <div className="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-emerald-400/40 to-transparent pointer-events-none animate-[scanline_3s_linear_infinite]"
                style={{ animation: 'scanline 3s linear infinite' }} />

              <div className="relative p-4 space-y-3">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"
                      style={{ boxShadow: '0 0 8px rgba(52,211,153,0.9)' }} />
                    <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-[0.2em] font-mono">
                      EEG Live
                    </span>
                  </div>
                  <span className="text-[9px] font-mono text-emerald-400/50 tracking-wide">Fp2</span>
                  {electrodeOff && (
                    <span className="text-[9px] font-bold text-red-400 px-1.5 py-0.5 rounded bg-red-500/10 border border-red-500/30 animate-pulse">
                      ⚠ Élec.
                    </span>
                  )}
                </div>

                {/* Oscilloscope holographique */}
                <div className="rounded-xl overflow-hidden border border-emerald-400/15"
                  style={{ boxShadow: 'inset 0 0 16px rgba(52,211,153,0.06)' }}>
                  <MiniEEGOscilloscope
                    wsData={liveEEG.eegFrame}
                    eegState={eegState}
                    mlPrediction={liveEEG.mlPrediction}
                    features={liveEEG.epochFrame?.features ?? features}
                    canvasHeight={130}
                    hideLabel
                  />
                </div>
              </div>
            </div>
          )}

          <EEGContextPanel
            eegState={eegState}
            confidence={confidence}
            features={features}
            recommendation={recommendation}
          />
        </div>

        {/* ── Colonne droite — zone feedback ── */}
        <div className="lg:col-span-3 space-y-4">

          {/* Sélecteur type de feedback — filtré selon le palier */}
          <div className="card p-3 space-y-2">
            {feedbackType === 'breathing' && recommendation.type !== 'breathing' && allowedTypes.includes(recommendation.type) && (
              <p className="text-[10px] text-nc-muted text-center">
                Commencez par 2–3 minutes de respiration, puis choisissez votre feedback
                <span className="text-nc-accent ml-1">
                  {FEEDBACK_TYPES.find(t => t.key === recommendation.type)?.label ?? ''} recommandé ★
                </span>
              </p>
            )}
            <div className="flex gap-1.5 flex-wrap">
              {FEEDBACK_TYPES.filter(t => allowedTypes.includes(t.key)).map(({ key, Icon, label }) => (
                <button key={key}
                  onClick={() => handleTypeChange(key)}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-semibold
                               border transition-all flex-1 min-w-[80px] justify-center
                    ${feedbackType === key
                      ? 'bg-nc-accent/20 border-nc-accent text-nc-accent'
                      : 'border-nc-border text-nc-muted hover:border-nc-accent/30 hover:text-nc-text'}`}
                >
                  <Icon className="w-3.5 h-3.5 shrink-0" />
                  <span className="hidden sm:inline">{label}</span>
                  {key === recommendation.type && feedbackType !== key && (
                    <span className="w-1.5 h-1.5 rounded-full bg-nc-accent animate-pulse ml-0.5" />
                  )}
                </button>
              ))}
            </div>
            {/* Indication types verrouillés */}
            {FEEDBACK_TYPES.filter(t => !allowedTypes.includes(t.key)).length > 0 && (
              <p className="text-[9px] text-nc-muted/60 text-center">
                {FEEDBACK_TYPES.filter(t => !allowedTypes.includes(t.key)).map(t => t.label).join(', ')} — disponible à partir de {
                  palier === 1 ? 'P2' : palier === 4 ? 'P3 (terminé)' : 'P3'
                }
              </p>
            )}
          </div>

          {/* Contenu feedback */}
          {renderFeedbackContent()}

          {/* Barre évaluation */}
          <EvalBar onSubmit={handleEval} />

          {/* Historique évaluations locales (mini) */}
          {evalLog.length > 0 && (
            <div className="card p-3 flex items-center gap-3 text-xs text-nc-muted">
              <span>{evalLog.length} évaluation{evalLog.length > 1 ? 's' : ''} enregistrée{evalLog.length > 1 ? 's' : ''}</span>
              <span>·</span>
              <span className="text-emerald-400">
                {evalLog.filter(e => e.liked === true).length} utiles
              </span>
              {evalLog.filter(e => e.sam_score !== null).length > 0 && (
                <>
                  <span>·</span>
                  <span>SAM moy. {(
                    evalLog.filter(e => e.sam_score !== null)
                      .reduce((acc, e) => acc + e.sam_score, 0) /
                    evalLog.filter(e => e.sam_score !== null).length
                  ).toFixed(1)}</span>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
