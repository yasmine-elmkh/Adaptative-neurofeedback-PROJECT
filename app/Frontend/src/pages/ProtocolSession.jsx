import { useState, useEffect, useRef, useCallback } from 'react'
import { useNavigate, useParams, useLocation } from 'react-router-dom'
import {
  Brain, CheckCircle2, ArrowLeft, Clock, Zap, AlertCircle,
  ChevronRight, Activity, SkipForward, Info,
} from 'lucide-react'
import BreathingGuide    from '../components/feedback/BreathingGuide'
import FocusPoint        from '../components/feedback/FocusPoint'
import MediaZone         from '../components/feedback/MediaZone'
import SessionBlockTimer from '../components/feedback/SessionBlockTimer'
import { feedback as feedbackApi } from '../utils/api'

const API = (path, method = 'GET', body) => fetch(`/api/protocol${path}`, {
  method,
  headers: {
    Authorization: `Bearer ${localStorage.getItem('neurocap_token')}`,
    'Content-Type': 'application/json',
  },
  ...(body ? { body: JSON.stringify(body) } : {}),
}).then(r => r.json())

/* ── Phases de séance ── */
const SESSION_PHASES = [
  { id: 'pre',       label: 'Pré-séance',           duration: 300 },
  { id: 'rest_ec',   label: 'Repos yeux fermés',     duration: 120 },
  { id: 'rest_eo',   label: 'Repos yeux ouverts',    duration: 60  },
  { id: 'bloc1',     label: 'Bloc 1',                duration: 180 },
  { id: 'bloc2',     label: 'Bloc 2',                duration: 180 },
  { id: 'bloc3',     label: 'Bloc 3',                duration: 180 },
  { id: 'bloc4',     label: 'Bloc 4',                duration: 180 },
  { id: 'bloc5',     label: 'Bloc 5',                duration: 180 },
  { id: 'bloc6',     label: 'Bloc 6',                duration: 180 },
  { id: 'rest_fin',  label: 'Repos guidé final',     duration: 180 },
  { id: 'post',      label: 'Post-séance',           duration: 180 },
]

const BLOC_IDS = ['bloc1','bloc2','bloc3','bloc4','bloc5','bloc6']
const BLOC_NUM = (id) => parseInt(id.replace('bloc', ''))

const PHASE_UTILITY = {
  pre:      { label: 'Évaluation initiale',          desc: 'Mesure votre état de départ pour calibrer la séance et mesurer les progrès.', color: 'text-nc-muted',    bar: 'bg-nc-muted/40'    },
  rest_ec:  { label: 'Baseline alpha du jour',        desc: 'Établit votre référence alpha individuelle et améliore la précision du feedback adaptatif.', color: 'text-blue-400',   bar: 'bg-blue-500'       },
  rest_eo:  { label: 'Préparation à la concentration', desc: 'Active en douceur les zones de concentration (cortex frontal) avant les blocs de neurofeedback.', color: 'text-cyan-400',   bar: 'bg-cyan-500'       },
  bloc1:    { label: 'Bloc de neurofeedback 1/6',     desc: 'Renforce les circuits neuronaux cibles. Le feedback s\'adapte à votre performance en temps réel.', color: 'text-nc-accent',  bar: 'bg-nc-accent'      },
  bloc2:    { label: 'Bloc de neurofeedback 2/6',     desc: 'Continuez à maintenir l\'état cible. Le seuil s\'ajuste selon votre réussite du bloc précédent.', color: 'text-nc-accent',  bar: 'bg-nc-accent'      },
  bloc3:    { label: 'Bloc de neurofeedback 3/6',     desc: 'Mi-parcours — les effets commencent à se consolider. Restez focalisé sur le feedback.', color: 'text-nc-accent',  bar: 'bg-nc-accent'      },
  bloc4:    { label: 'Bloc de neurofeedback 4/6',     desc: 'Phase de consolidation. L\'entraînement cérébral devient plus profond à mesure que les blocs avancent.', color: 'text-emerald-400', bar: 'bg-emerald-500'    },
  bloc5:    { label: 'Bloc de neurofeedback 5/6',     desc: 'Avant-dernier bloc — maintenez la concentration même si la fatigue s\'installe.', color: 'text-emerald-400', bar: 'bg-emerald-500'    },
  bloc6:    { label: 'Bloc de neurofeedback 6/6',     desc: 'Dernier bloc — la pratique répétée installe durablement les nouvelles connexions cérébrales.', color: 'text-emerald-400', bar: 'bg-emerald-500'    },
  rest_fin: { label: 'Décompression guidée',          desc: 'Favorise la consolidation des apprentissages et réduit la fatigue mentale post-séance.', color: 'text-purple-400',  bar: 'bg-purple-500'     },
  post:     { label: 'Évaluation finale',             desc: 'Compare votre état avec le début de séance pour mesurer les bénéfices et ajuster les prochaines séances.', color: 'text-nc-muted',  bar: 'bg-nc-muted/40'    },
}

/* ── Questionnaire subjectif ── */
function SubjectiveForm({ keys, labels, title, onSubmit }) {
  const [vals, setVals] = useState(Object.fromEntries(keys.map(k => [k, 5])))
  return (
    <div className="card p-6 space-y-5 max-w-md mx-auto">
      <h2 className="text-sm font-bold text-nc-text">{title}</h2>
      {keys.map((k, i) => (
        <div key={k}>
          <div className="flex justify-between text-xs text-nc-muted mb-1.5">
            <span>{labels[i]}</span>
            <span className="font-mono font-bold text-nc-text">{vals[k]}/10</span>
          </div>
          <input type="range" min={1} max={10} value={vals[k]}
            onChange={e => setVals(p => ({ ...p, [k]: parseInt(e.target.value) }))}
            className="w-full accent-nc-accent" />
        </div>
      ))}
      <button onClick={() => onSubmit(vals)}
        className="w-full btn-primary py-2.5 rounded-xl text-sm font-semibold">
        Valider →
      </button>
    </div>
  )
}

/* ── Rapport de séance ── */
function SessionReport({ score, blocResults, palierAfter, isBilan, sessionNumber, nextSessionDate, nextIntervalDays, onContinue }) {
  const avg = blocResults.length > 0
    ? (blocResults.reduce((s, b) => s + b.success_rate, 0) / blocResults.length * 100).toFixed(0)
    : 0

  const formattedNextDate = nextSessionDate
    ? new Date(nextSessionDate).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })
    : null

  return (
    <div className="max-w-lg mx-auto space-y-5">
      {/* Bravo header */}
      <div className="text-center space-y-2">
        <div className="w-16 h-16 rounded-2xl bg-emerald-500/15 flex items-center justify-center mx-auto">
          <CheckCircle2 className="w-8 h-8 text-emerald-400" />
        </div>
        <h2 className="text-xl font-bold text-nc-text">
          Bravo ! Séance {sessionNumber} terminée avec succès
        </h2>
        <p className="text-sm text-nc-muted">
          Excellent travail — votre cerveau vient de réaliser un entraînement complet.
        </p>
      </div>

      {/* Prochain rendez-vous */}
      {formattedNextDate && (
        <div className="p-4 rounded-2xl bg-nc-accent/8 border border-nc-accent/25 flex items-center gap-3">
          <span className="text-2xl">📅</span>
          <div>
            <p className="text-xs font-semibold text-nc-accent">Prochain rendez-vous recommandé</p>
            <p className="text-sm font-bold text-nc-text capitalize">{formattedNextDate}</p>
            <p className="text-[11px] text-nc-muted mt-0.5">
              Minimum {nextIntervalDays} jour{nextIntervalDays > 1 ? 's' : ''} entre deux séances selon le protocole.
              Un rapport d'évaluation vous a été envoyé par email.
            </p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Score',          value: `${score}/100`, color: 'text-nc-accent' },
          { label: 'Taux succès',    value: `${avg}%`,       color: 'text-emerald-400' },
          { label: 'Palier actuel',  value: palierAfter,     color: 'text-purple-400' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card p-3 text-center">
            <p className={`text-xl font-bold font-mono ${color}`}>{value}</p>
            <p className="text-[10px] text-nc-muted mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      <div className="card p-4 space-y-2">
        <p className="text-xs font-semibold text-nc-muted uppercase tracking-wide mb-2">Détail blocs</p>
        {blocResults.map((b, i) => (
          <div key={i} className="flex items-center gap-3 text-xs">
            <span className="text-nc-muted w-12">Bloc {i + 1}</span>
            <div className="flex-1 h-1.5 rounded-full bg-nc-surface2 overflow-hidden">
              <div className={`h-full rounded-full transition-all ${b.success_rate >= 0.6 ? 'bg-emerald-500' : b.success_rate >= 0.4 ? 'bg-yellow-500' : 'bg-red-500'}`}
                style={{ width: `${b.success_rate * 100}%` }} />
            </div>
            <span className="font-mono w-10 text-right">{(b.success_rate * 100).toFixed(0)}%</span>
            {b.fatigue && <span className="text-orange-400">⚠ fatigue</span>}
          </div>
        ))}
      </div>

      {isBilan && (
        <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/25 flex items-center gap-3">
          <span className="text-2xl">⭐</span>
          <div>
            <p className="text-sm font-semibold text-amber-300">Séance de bilan</p>
            <p className="text-xs text-amber-400/70">Un rapport de progression détaillé est disponible.</p>
          </div>
          <button onClick={() => onContinue('bilan')}
            className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-semibold shrink-0">
            Voir le bilan <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      <button onClick={() => onContinue('dashboard')}
        className="w-full btn-primary py-3 rounded-xl text-sm font-semibold">
        Retour au programme →
      </button>
    </div>
  )
}

/* ════════════════════════════════════════════════════════
   Page ProtocolSession
═══════════════════════════════════════════════════════ */
export default function ProtocolSession() {
  const navigate  = useNavigate()
  const location  = useLocation()
  const { n }     = useParams()
  const sessionN  = parseInt(n)

  const { eegState: navEegState = 'neutral', source: navSource = 'protocol' } = location.state ?? {}

  const [config,      setConfig]      = useState(null)
  const [sessionId,   setSessionId]   = useState(null)
  const [feedSessId,  setFeedSessId]  = useState(null)
  const [phaseIdx,    setPhaseIdx]    = useState(0)
  const [elapsed,     setElapsed]     = useState(0)
  const [interBloc,   setInterBloc]   = useState(false)
  const [ibCount,     setIbCount]     = useState(20)
  const [subjectivePre, setSubjectivePre]  = useState(null)
  const [subjectivePost, setSubjectivePost] = useState(null)
  const [currentMedia, setCurrentMedia]    = useState(null)
  const [blocResults,  setBlocResults]     = useState([])
  const [currentThr,   setCurrentThr]      = useState(0.3)
  const [fatigue,      setFatigue]         = useState(false)
  const [done,         setDone]            = useState(false)
  const [finalReport,  setFinalReport]     = useState(null)
  const [loading,      setLoading]         = useState(true)
  const timerRef = useRef(null)

  const phase = SESSION_PHASES[phaseIdx]
  const isBloc = BLOC_IDS.includes(phase?.id)
  const blocNum = isBloc ? BLOC_NUM(phase.id) : 0

  /* ── Charger config + démarrer session ── */
  useEffect(() => {
    let cancelled = false
    setLoading(true)
    API(`/sessions/${sessionN}/start`, 'POST')
      .then(async data => {
        if (cancelled) return
        setConfig(data)
        setSessionId(data.session_id)
        setCurrentThr(data.alpha_target_min || 0.3)
        try {
          const fs = await feedbackApi.startSession('neurofeedback', {})
          if (!cancelled) setFeedSessId(fs.session_id)
        } catch {}
      })
      .catch(e => { if (!cancelled) { alert('Impossible de démarrer la séance : ' + (e.message || '')); navigate('/protocol') } })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, [sessionN])

  /* ── Timer phase ── */
  const startPhaseTimer = useCallback(() => {
    if (!phase) return
    clearInterval(timerRef.current)
    setElapsed(0)
    timerRef.current = setInterval(() => {
      setElapsed(e => {
        if (e + 1 >= phase.duration) {
          clearInterval(timerRef.current)
          handlePhaseEnd()
        }
        return e + 1
      })
    }, 1000)
  }, [phase])

  useEffect(() => () => clearInterval(timerRef.current), [])

  const handlePhaseEnd = useCallback(async () => {
    if (isBloc) {
      // Fin de bloc → adapter seuil
      try {
        const sr = Math.random() * 0.4 + 0.4  // simulation — remplacer par vraie donnée EEG
        const r  = await API(`/sessions/${sessionN}/bloc-end`, 'POST', {
          session_id:        sessionId,
          bloc_number:       blocNum,
          success_rate:      sr,
          alpha_avg:         currentThr * (0.9 + Math.random() * 0.2),
          theta_avg:         0.25,
          baseline_theta:    0.22,
          current_threshold: currentThr,
        })
        setBlocResults(prev => [...prev, { success_rate: sr, fatigue: r.fatigue_detected }])
        setCurrentThr(r.new_threshold)
        setFatigue(r.fatigue_detected)

        if (phaseIdx < SESSION_PHASES.length - 1 && BLOC_IDS.includes(SESSION_PHASES[phaseIdx + 1]?.id)) {
          // Pause inter-bloc 20s
          setInterBloc(true)
          setIbCount(20)
          const ib = setInterval(() => {
            setIbCount(c => {
              if (c <= 1) { clearInterval(ib); setInterBloc(false); nextPhase(); return 0 }
              return c - 1
            })
          }, 1000)
          return
        }
      } catch {}
    }
    nextPhase()
  }, [phaseIdx, isBloc, blocNum, sessionId, currentThr])

  const nextPhase = () => {
    if (phaseIdx < SESSION_PHASES.length - 1) {
      setPhaseIdx(i => i + 1)
    } else {
      completSession()
    }
  }

  const completSession = async () => {
    try {
      const rates = blocResults.map(b => b.success_rate)
      const r = await API(`/sessions/${sessionN}/complete`, 'PUT', {
        session_id:          sessionId,
        blocs_success_rates: rates,
        ml_confidence_avg:   0.75,
        artifact_rate:       0.05,
        subjective_pre:      subjectivePre,
        subjective_post:     subjectivePost,
      })
      setFinalReport(r)
      setDone(true)
    } catch (e) {
      alert('Erreur finalisation : ' + e.message)
    }
  }

  /* ── Démarrer le timer à chaque changement de phase ── */
  useEffect(() => {
    if (!config || loading || interBloc) return
    if (['pre', 'post'].includes(phase?.id)) return  // phases avec formulaire
    startPhaseTimer()
  }, [phaseIdx, config, loading, interBloc])

  /* ── Média feedback (blocs) ── */
  useEffect(() => {
    if (!isBloc || !feedSessId || !config) return
    const allowedTypes = config.feedback_types || ['audio', 'image']
    feedbackApi.recommend(feedSessId, navEegState, allowedTypes[0])
      .then(r => setCurrentMedia(r.media))
      .catch(() => {})
  }, [phaseIdx, feedSessId, config])

  const handleSkip = () => {
    if (!feedSessId || !currentMedia) return
    feedbackApi.skip(feedSessId, currentMedia.id)
      .then(() => feedbackApi.recommend(feedSessId, 'neutral'))
      .then(r => setCurrentMedia(r.media))
      .catch(() => {})
  }

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
    </div>
  )

  if (done && finalReport) return (
    <div className="max-w-xl mx-auto px-4 py-6">
      <SessionReport
        score={finalReport.score}
        blocResults={blocResults}
        palierAfter={finalReport.palier_after}
        isBilan={config?.is_bilan}
        sessionNumber={sessionN}
        nextSessionDate={finalReport.next_session_date}
        nextIntervalDays={finalReport.next_interval_days}
        onContinue={(dest) => {
          if (dest === 'bilan') navigate(`/protocol/bilan/${sessionN}`)
          else navigate('/protocol')
        }}
      />
    </div>
  )

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-5">

      {/* Header */}
      <div className="flex items-center gap-3 flex-wrap">
        <button onClick={() => navigate('/protocol')}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="w-10 h-10 rounded-2xl bg-nc-accent/15 flex items-center justify-center">
          <Brain className="w-5 h-5 text-nc-accent" />
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-nc-text">Séance {sessionN}</h1>
          <p className="text-xs text-nc-muted">
            {config?.palier} · Phase {config?.phase} · {config?.is_bilan ? '⭐ Bilan' : 'Standard'}
          </p>
        </div>
        {isBloc && (
          <div className="text-right">
            <p className="text-sm font-bold font-mono text-nc-accent">Bloc {blocNum}/6</p>
            <p className="text-[10px] text-nc-muted">Seuil : {currentThr.toFixed(3)}</p>
          </div>
        )}
      </div>

      {/* Barre progression phases */}
      <div className="flex gap-1">
        {SESSION_PHASES.map((p, i) => (
          <div key={p.id} className={`h-1.5 rounded-full flex-1 transition-all
            ${i < phaseIdx ? 'bg-emerald-500' : i === phaseIdx ? 'bg-nc-accent animate-pulse' : 'bg-nc-surface2'}`} />
        ))}
      </div>

      {/* Bannière utilité de la phase courante */}
      {phase && PHASE_UTILITY[phase.id] && (
        <div className="card px-4 py-3 flex items-start gap-3 border border-nc-border/50">
          <Info className={`w-4 h-4 mt-0.5 shrink-0 ${PHASE_UTILITY[phase.id].color}`} />
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <span className={`text-xs font-semibold ${PHASE_UTILITY[phase.id].color}`}>
                {PHASE_UTILITY[phase.id].label}
              </span>
              {/* Mini barre d'utilité */}
              <div className="flex-1 h-1 rounded-full bg-nc-surface2 overflow-hidden max-w-[80px]">
                <div className={`h-full rounded-full ${PHASE_UTILITY[phase.id].bar}`}
                     style={{ width: `${phaseIdx / (SESSION_PHASES.length - 1) * 100}%` }} />
              </div>
              <span className="text-[10px] text-nc-muted font-mono shrink-0">
                {phaseIdx + 1}/{SESSION_PHASES.length}
              </span>
            </div>
            <p className="text-[11px] text-nc-muted leading-relaxed">{PHASE_UTILITY[phase.id].desc}</p>
          </div>
          {/* Bouton passer (seulement pour phases non-critiques) */}
          {['rest_ec','rest_eo','rest_fin'].includes(phase?.id) && (
            <button
              onClick={nextPhase}
              className="flex items-center gap-1 text-[10px] text-nc-muted hover:text-yellow-400 transition-colors shrink-0 px-2 py-1 rounded-lg hover:bg-yellow-500/10 border border-transparent hover:border-yellow-500/20"
              title="Passer cette étape (non recommandé)"
            >
              <SkipForward className="w-3 h-3" /> Passer
            </button>
          )}
        </div>
      )}

      {/* Pause inter-bloc */}
      {interBloc && (
        <div className="card p-8 text-center space-y-4 border border-nc-accent/20">
          <p className="text-lg font-bold text-nc-text">Pause — Détente</p>
          <p className="text-5xl font-mono font-bold text-nc-accent">{ibCount}s</p>
          <p className="text-sm text-nc-muted">Relâchez les épaules, respirez profondément.</p>
        </div>
      )}

      {!interBloc && (
        <>
          {/* Phase PRE — questionnaire */}
          {phase?.id === 'pre' && !subjectivePre && (
            <SubjectiveForm
              keys={['fatigue','stress','motivation']}
              labels={['Fatigue', 'Stress', 'Motivation']}
              title="Comment vous sentez-vous avant la séance ?"
              onSubmit={v => { setSubjectivePre(v); nextPhase() }}
            />
          )}

          {/* Phase POST — questionnaire */}
          {phase?.id === 'post' && !subjectivePost && (
            <SubjectiveForm
              keys={['focus','calme','fatigue']}
              labels={['Concentration ressentie', 'Calme', 'Fatigue']}
              title="Comment vous sentez-vous après la séance ?"
              onSubmit={v => { setSubjectivePost(v); completSession() }}
            />
          )}

          {/* Repos yeux fermés */}
          {phase?.id === 'rest_ec' && (
            <div className="card p-8 text-center space-y-4">
              <p className="text-6xl">😌</p>
              <p className="text-sm font-semibold text-nc-text">Fermez les yeux — respirez naturellement</p>
              <p className="text-3xl font-mono font-bold text-nc-accent">
                {Math.floor((phase.duration - elapsed) / 60)}:{String((phase.duration - elapsed) % 60).padStart(2, '0')}
              </p>
              <p className="text-xs text-nc-muted">Établissement de la référence alpha du jour</p>
            </div>
          )}

          {/* Repos yeux ouverts */}
          {phase?.id === 'rest_eo' && (
            <div className="card p-8 text-center space-y-4">
              <FocusPoint />
              <p className="text-3xl font-mono font-bold text-nc-accent">
                {Math.floor((phase.duration - elapsed) / 60)}:{String((phase.duration - elapsed) % 60).padStart(2, '0')}
              </p>
            </div>
          )}

          {/* Blocs de feedback */}
          {isBloc && (
            <div className="space-y-4">
              {fatigue && (
                <div className="p-3 rounded-xl bg-orange-500/10 border border-orange-500/25 flex items-center gap-3">
                  <AlertCircle className="w-4 h-4 text-orange-400 shrink-0" />
                  <p className="text-xs text-orange-400">Fatigue détectée — passage en mode relaxation guidée.</p>
                </div>
              )}

              <div className="card p-4 flex items-center gap-4">
                <Activity className="w-5 h-5 text-nc-accent shrink-0" />
                <div className="flex-1">
                  <p className="text-xs text-nc-muted">Seuil alpha cible</p>
                  <div className="h-2 rounded-full bg-nc-surface2 overflow-hidden mt-1">
                    <div className="h-full rounded-full bg-nc-accent transition-all" style={{ width: `${Math.min(100, currentThr * 100)}%` }} />
                  </div>
                </div>
                <span className="font-mono font-bold text-nc-accent text-sm">{currentThr.toFixed(3)}</span>
              </div>

              <SessionBlockTimer
                blocNumber={blocNum}
                totalBlocs={6}
                elapsed={elapsed}
                duration={phase.duration}
              />

              {fatigue ? (
                <BreathingGuide />
              ) : currentMedia ? (
                <MediaZone
                  media={currentMedia}
                  sessionId={feedSessId}
                  eegState={navEegState}
                  onSkip={handleSkip}
                  onMediaEnd={() => {}}
                />
              ) : (
                <div className="card p-10 text-center">
                  <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin mx-auto" />
                  <p className="text-sm text-nc-muted mt-3">Chargement du média…</p>
                </div>
              )}
            </div>
          )}

          {/* Repos guidé final */}
          {phase?.id === 'rest_fin' && (
            <div className="card p-6 space-y-4 text-center">
              <p className="text-lg font-bold text-nc-text">Repos guidé — Décompression</p>
              <BreathingGuide />
              <p className="text-3xl font-mono font-bold text-nc-accent">
                {Math.floor((phase.duration - elapsed) / 60)}:{String((phase.duration - elapsed) % 60).padStart(2, '0')}
              </p>
            </div>
          )}

          {/* Avancement manuel (phases sans timer auto) */}
          {!['pre', 'post', 'rest_ec', 'rest_eo', 'rest_fin'].includes(phase?.id) && !isBloc && (
            <button onClick={nextPhase} className="w-full btn-primary py-3 rounded-xl text-sm font-semibold">
              Continuer <ChevronRight className="w-4 h-4 inline ml-1" />
            </button>
          )}
        </>
      )}
    </div>
  )
}
