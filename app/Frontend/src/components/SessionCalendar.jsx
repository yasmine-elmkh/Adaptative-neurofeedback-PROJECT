import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { calendar as calendarApi, protocol as protocolApi } from '../utils/api'
import { Star, CheckCircle2, Clock, XCircle, Calendar, Lock, AlertCircle, ArrowRight, RefreshCw } from 'lucide-react'

/* ── Couleurs par statut ── */
const STATUS_STYLE = {
  completed:           { bg: 'bg-emerald-500/15', border: 'border-emerald-500/30', text: 'text-emerald-400', label: 'Complétée'        },
  scheduled:           { bg: 'bg-blue-500/15',    border: 'border-blue-500/30',    text: 'text-blue-400',    label: 'Planifiée'        },
  upcoming:            { bg: 'bg-nc-surface2',    border: 'border-nc-border',      text: 'text-nc-muted',    label: 'À venir'          },
  missed:              { bg: 'bg-red-500/10',     border: 'border-red-500/25',     text: 'text-red-400',     label: 'Manquée'          },
  running:             { bg: 'bg-yellow-500/10',  border: 'border-yellow-500/25',  text: 'text-yellow-400',  label: 'En cours'         },
  pending_validation:  { bg: 'bg-orange-500/10',  border: 'border-orange-500/25',  text: 'text-orange-400',  label: 'En validation'    },
}

/* ── Phases ── */
const PHASE_LABELS = {
  phase1: { label: 'Phase 1 — Initiation',       color: 'text-purple-400',  bg: 'bg-purple-500/10'  },
  phase2: { label: 'Phase 2 — Apprentissage',    color: 'text-blue-400',    bg: 'bg-blue-500/10'    },
  phase3: { label: 'Phase 3 — Maîtrise',         color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
}

function PhaseLabel({ phase }) {
  const p = PHASE_LABELS[phase] ?? PHASE_LABELS.phase1
  return (
    <span className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full ${p.bg} ${p.color}`}>
      {p.label}
    </span>
  )
}

function SessionCard({ session, isNext, s1Complete, plannedDate, onClick }) {
  const n  = session.session_number
  const st = STATUS_STYLE[session.status] ?? STATUS_STYLE.upcoming
  const bilan = session.bilan_type
  const isS1  = n === 1
  const locked = n > 1 && !s1Complete

  return (
    <div
      onClick={onClick}
      className={`relative p-3 rounded-2xl border transition-all cursor-pointer
        ${locked ? 'opacity-40 cursor-not-allowed' : 'hover:scale-105 hover:shadow-lg'}
        ${st.bg} ${st.border}
        ${isNext && !locked ? 'ring-2 ring-nc-accent ring-offset-2 ring-offset-nc-bg scale-105' : ''}
        ${isS1 && !session.status === 'completed' ? 'ring-2 ring-amber-400/50' : ''}
        ${session.status === 'upcoming' && !isNext && !locked ? 'opacity-50' : ''}`}
    >
      {/* Badge bilan */}
      {bilan && (
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-amber-500 flex items-center justify-center shadow-lg z-10">
          <Star className="w-3 h-3 text-white fill-white" />
        </div>
      )}

      {/* Icône verrou si bloqué */}
      {locked && (
        <div className="absolute -top-1.5 -left-1.5 w-5 h-5 rounded-full bg-nc-surface2 border border-nc-border flex items-center justify-center z-10">
          <Lock className="w-2.5 h-2.5 text-nc-muted" />
        </div>
      )}

      {/* S1 : badge spécial CALIBRATION */}
      {isS1 && (
        <div className="absolute -top-2 -left-2 z-10">
          <span className="text-[8px] font-bold px-1.5 py-0.5 rounded-full bg-amber-500 text-white shadow">CAL</span>
        </div>
      )}

      {/* Numéro séance */}
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs font-bold text-nc-muted">S{n}</span>
        {bilan && <span className="text-[9px] font-bold text-amber-400">{bilan}</span>}
      </div>

      {/* Score si complétée */}
      {session.status === 'completed' && session.score != null ? (
        <div className="text-center">
          <span className="text-lg font-bold font-mono text-emerald-400">{session.score}</span>
          <span className="text-[9px] text-nc-muted block">/100</span>
        </div>
      ) : (session.status === 'scheduled' && session.scheduled_date) || plannedDate ? (
        <div className="text-center">
          <Calendar className="w-3.5 h-3.5 text-blue-400 mx-auto mb-0.5" />
          <span className="text-[9px] text-blue-400 font-medium">
            {new Date(plannedDate || session.scheduled_date).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })}
          </span>
        </div>
      ) : (
        <div className="h-8 flex items-center justify-center">
          {session.status === 'completed'  && <CheckCircle2 className="w-5 h-5 text-emerald-400" />}
          {session.status === 'running'    && <Clock className="w-5 h-5 text-yellow-400 animate-pulse" />}
          {session.status === 'missed'     && <XCircle className="w-5 h-5 text-red-400" />}
          {session.status === 'upcoming'   && !locked && <span className="text-nc-muted/50 text-base font-bold">—</span>}
          {locked && <Lock className="w-4 h-4 text-nc-muted/40" />}
        </div>
      )}

      <p className={`text-center text-[9px] font-medium mt-1 ${st.text}`}>{st.label}</p>
    </div>
  )
}

export default function SessionCalendar({ patientId, onClose, autoRefresh = false }) {
  const navigate = useNavigate()
  const [data,       setData]       = useState(null)
  const [progress,   setProgress]   = useState(null)
  const [loading,    setLoading]    = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [error,      setError]      = useState('')

  const fetchData = useCallback(async (silent = false) => {
    if (!silent) setLoading(true)
    else setRefreshing(true)
    setError('')
    try {
      const [calData, progData] = await Promise.all([
        calendarApi.get(patientId),
        protocolApi.progress().catch(() => null),
      ])
      setData(calData)
      setProgress(progData)
    } catch {
      setError('Impossible de charger le calendrier')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [patientId])

  useEffect(() => { fetchData() }, [fetchData])

  // Auto-refresh quand la page redevient visible (retour depuis une séance)
  useEffect(() => {
    if (!autoRefresh) return
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') fetchData(true)
    }
    document.addEventListener('visibilitychange', handleVisibility)
    return () => document.removeEventListener('visibilitychange', handleVisibility)
  }, [autoRefresh, fetchData])

  if (loading) return (
    <div className="card p-8 flex items-center justify-center gap-3">
      <div className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
      <span className="text-sm text-nc-muted">Chargement du calendrier…</span>
    </div>
  )

  if (error) return (
    <div className="card p-6 text-center text-red-400 text-sm">{error}</div>
  )

  const sessions  = data?.sessions || []
  const nextNum   = data?.next_session_number || 1
  const completed = data?.total_completed || 0

  const s1 = sessions.find(s => s.session_number === 1)
  const s1Complete = s1?.status === 'completed'

  const phase1 = sessions.filter(s => s.phase === 'phase1')
  const phase2 = sessions.filter(s => s.phase === 'phase2')
  const phase3 = sessions.filter(s => s.phase === 'phase3')

  const totalTarget = progress?.cognitive_profile === 'A' ? 12 : progress?.cognitive_profile === 'C' ? 18 : 15
  const calProgress = Math.round((completed / totalTarget) * 100)

  // Map dates planifiées (depuis user_protocol_progress)
  const plannedMap = {}
  for (const p of (progress?.planned_session_dates || [])) {
    plannedMap[p.session_num] = p.planned_date
  }

  const handleCardClick = (session) => {
    if (session.session_number === 1) {
      navigate('/protocol/calibration')
    } else if (!s1Complete) {
      return // bloqué
    } else if (session.status !== 'upcoming' && session.status !== 'missed') {
      navigate(`/protocol/session/${session.session_number}`)
    }
  }

  return (
    <div className="card p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-lg font-bold text-nc-text">Protocole de traitement</h2>
          <p className="text-xs text-nc-muted mt-0.5">
            {completed}/{progress?.cognitive_profile === 'A' ? 12 : progress?.cognitive_profile === 'C' ? 18 : 15} séances complétées
            {progress?.cognitive_profile && (
              <span className="ml-2 font-semibold text-purple-400">· Profil {progress.cognitive_profile}</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* Bouton rafraîchir */}
          <button
            onClick={() => fetchData(true)}
            disabled={refreshing}
            title="Actualiser"
            className="p-1.5 rounded-lg text-nc-muted hover:text-nc-accent hover:bg-nc-surface2 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? 'animate-spin text-nc-accent' : ''}`} />
          </button>
          <div className="text-right">
            <p className="text-2xl font-bold font-mono text-nc-accent">{calProgress}%</p>
            <p className="text-[10px] text-nc-muted">progression</p>
          </div>
          {onClose && (
            <button onClick={onClose}
              className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
              ✕
            </button>
          )}
        </div>
      </div>

      {/* ── BANNER SÉANCE 1 OBLIGATOIRE ── */}
      {!s1Complete ? (
        <div className="p-4 rounded-2xl border-2 border-amber-500/50 bg-amber-500/8 space-y-3">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-amber-500/20 flex items-center justify-center shrink-0">
              <AlertCircle className="w-5 h-5 text-amber-400" />
            </div>
            <div className="flex-1">
              <p className="text-sm font-bold text-amber-300">Séance 1 — Calibration obligatoire</p>
              <p className="text-xs text-amber-200/70 mt-1 leading-relaxed">
                La Séance 1 est une calibration individuelle de 30 minutes. Elle mesure votre profil EEG unique
                (fréquence alpha individuelle, seuil de référence, type cognitif A/B/C) et personnalise le protocole
                pour toutes les séances suivantes. Sans cette calibration, les séances S2 à S15 sont inaccessibles.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 text-center">
            {[
              { label: 'Repos yeux fermés',   time: '5 min', icon: '😌' },
              { label: 'Repos yeux ouverts',  time: '5 min', icon: '👁' },
              { label: 'Tâche cognitive',      time: '5 min', icon: '🧮' },
            ].map(({ label, time, icon }) => (
              <div key={label} className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20">
                <div className="text-lg mb-0.5">{icon}</div>
                <p className="text-[9px] font-medium text-amber-300">{label}</p>
                <p className="text-[9px] text-amber-400/70">{time}</p>
              </div>
            ))}
          </div>

          <button
            onClick={() => navigate('/protocol/calibration')}
            className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl
                       bg-amber-500 hover:bg-amber-400 text-white font-semibold text-sm transition-colors"
          >
            Commencer la calibration (Séance 1)
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      ) : (
        /* S1 complétée — badge succès */
        <div className="p-3 rounded-xl border border-emerald-500/30 bg-emerald-500/8 flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <div>
            <p className="text-sm font-semibold text-emerald-300">Calibration complétée ✓</p>
            <p className="text-xs text-emerald-400/60">Profil EEG établi — séances S2–S15 déverrouillées</p>
          </div>
        </div>
      )}

      {/* Barre de progression */}
      <div className="space-y-1.5">
        <div className="h-2 rounded-full bg-nc-surface2 overflow-hidden">
          <div
            className="h-full rounded-full bg-gradient-to-r from-purple-500 via-blue-500 to-emerald-500 transition-all duration-700"
            style={{ width: `${calProgress}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-nc-muted">
          <span>Initiation</span><span>Apprentissage</span><span>Maîtrise</span>
        </div>
      </div>

      {/* Légende */}
      <div className="flex flex-wrap gap-3 text-[10px]">
        {Object.entries(STATUS_STYLE).map(([k, v]) => (
          <span key={k} className={`flex items-center gap-1 px-2 py-0.5 rounded-full border ${v.bg} ${v.border} ${v.text}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${v.text.replace('text-', 'bg-')}`} />
            {v.label}
          </span>
        ))}
        <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-500/10 border border-amber-500/25 text-amber-400">
          <Star className="w-2.5 h-2.5 fill-amber-400" /> Bilan obligatoire
        </span>
        <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-nc-surface2 border border-nc-border text-nc-muted">
          <Lock className="w-2.5 h-2.5" /> Bloquée (S1 requise)
        </span>
      </div>

      {/* Phase 1 : S1–S3 */}
      {phase1.length > 0 && (
        <div className="space-y-2">
          <PhaseLabel phase="phase1" />
          <p className="text-[10px] text-nc-muted">
            1 séance/semaine · intervalle min. 5 jours
            {!s1Complete && <span className="ml-2 text-amber-400 font-semibold">⚠ S1 calibration requise</span>}
          </p>
          <div className="grid grid-cols-3 gap-2">
            {phase1.map(s => (
              <SessionCard
                key={s.session_number}
                session={s}
                isNext={s.session_number === nextNum}
                s1Complete={s1Complete}
                plannedDate={plannedMap[s.session_number]}
                onClick={() => handleCardClick(s)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Phase 2 : S4–S10 */}
      {phase2.length > 0 && (
        <div className="space-y-2">
          <PhaseLabel phase="phase2" />
          <p className="text-[10px] text-nc-muted">2 séances/semaine · intervalle min. 2-3 jours</p>
          <div className="grid grid-cols-7 gap-2">
            {phase2.map(s => (
              <SessionCard
                key={s.session_number}
                session={s}
                isNext={s.session_number === nextNum}
                s1Complete={s1Complete}
                plannedDate={plannedMap[s.session_number]}
                onClick={() => handleCardClick(s)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Phase 3 : S11–S15 */}
      {phase3.length > 0 && (
        <div className="space-y-2">
          <PhaseLabel phase="phase3" />
          <p className="text-[10px] text-nc-muted">2 séances/semaine · intervalle min. 2-3 jours</p>
          <div className="grid grid-cols-5 gap-2">
            {phase3.map(s => (
              <SessionCard
                key={s.session_number}
                session={s}
                isNext={s.session_number === nextNum}
                s1Complete={s1Complete}
                plannedDate={plannedMap[s.session_number]}
                onClick={() => handleCardClick(s)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Prochaine séance */}
      {nextNum <= 15 && (
        <div className="p-3 rounded-xl bg-nc-accent/8 border border-nc-accent/20 flex items-center gap-3">
          <Calendar className="w-5 h-5 text-nc-accent shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-nc-text">
              Prochaine séance : S{nextNum}
              {nextNum === 1 && <span className="ml-2 text-[10px] text-amber-400 font-normal">— Calibration individuelle</span>}
              {[5,10,15].includes(nextNum) && <span className="ml-2 text-[10px] text-amber-400 font-normal">⭐ Bilan</span>}
            </p>
            <p className="text-xs text-nc-muted">
              {plannedMap[nextNum]
                ? <>Planifiée le <span className="text-blue-400 font-medium">
                    {new Date(plannedMap[nextNum]).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
                  </span></>
                : sessions.find(s => s.session_number === nextNum)?.scheduled_date
                  ? `Recommandée le ${new Date(sessions.find(s => s.session_number === nextNum).scheduled_date).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}`
                  : nextNum === 1
                    ? 'Commencez dès maintenant — aucun délai requis'
                    : 'Date à planifier avec votre thérapeute'}
            </p>
          </div>
          {nextNum === 1 && (
            <button
              onClick={() => navigate('/protocol/calibration')}
              className="btn-primary flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold shrink-0"
            >
              Commencer <ArrowRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      )}

      {completed >= 15 && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/25 text-center">
          <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
          <p className="text-sm font-bold text-emerald-400">Protocole complété !</p>
          <p className="text-xs text-nc-muted mt-1">Félicitations pour avoir terminé les 15 séances.</p>
        </div>
      )}
    </div>
  )
}
