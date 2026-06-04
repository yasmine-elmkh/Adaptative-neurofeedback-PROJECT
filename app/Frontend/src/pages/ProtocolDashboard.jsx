import { useState, useEffect, useCallback, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Brain, Star, CheckCircle2, Lock, Clock, Calendar, ArrowRight,
  TrendingUp, Award, ChevronRight, AlertCircle, Zap, RefreshCw,
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts'
import { protocol as protocolApi } from '../utils/api'

const PALIER_COLORS = { P1: '#a78bfa', P2: '#60a5fa', P3: '#34d399', P4: '#fbbf24' }
const PALIER_DESC   = {
  P1: '85–95 % baseline · Son seul · Introduction',
  P2: '95–110 % baseline · Son + visuel · Apprentissage',
  P3: '110–125 % baseline · Complet + jeux · Maîtrise',
  P4: '125–140 % baseline · Autonomie progressive · Expert',
}

const STATUS_STYLE = {
  completed:   { bg: 'bg-emerald-500/15', border: 'border-emerald-500/30', text: 'text-emerald-400' },
  in_progress: { bg: 'bg-yellow-500/10',  border: 'border-yellow-500/25',  text: 'text-yellow-400'  },
  scheduled:   { bg: 'bg-blue-500/10',    border: 'border-blue-500/20',    text: 'text-blue-400'    },
  upcoming:    { bg: 'bg-nc-surface2',    border: 'border-nc-border',      text: 'text-nc-muted'    },
  missed:      { bg: 'bg-red-500/10',     border: 'border-red-500/20',     text: 'text-red-400'     },
}

function SessionMini({ session, nextNum, s1Done, onClick }) {
  const n  = session.session_number
  const st = STATUS_STYLE[session.status] ?? STATUS_STYLE.upcoming
  const locked = n > 1 && !s1Done

  return (
    <div
      onClick={!locked ? onClick : undefined}
      title={locked ? 'Séance 1 requise' : `S${n} — ${session.status}`}
      className={`relative flex flex-col items-center justify-center p-2 rounded-xl border transition-all
        ${st.bg} ${st.border}
        ${n === nextNum && !locked ? 'ring-2 ring-nc-accent ring-offset-1 ring-offset-nc-bg scale-105' : ''}
        ${locked ? 'opacity-30 cursor-not-allowed' : 'cursor-pointer hover:scale-105 hover:shadow-md'}`}
    >
      {session.is_bilan && (
        <Star className="absolute -top-1.5 -right-1.5 w-3 h-3 text-amber-400 fill-amber-400" />
      )}
      <span className="text-[9px] font-bold text-nc-muted">S{n}</span>
      {session.status === 'completed'
        ? <CheckCircle2 className="w-4 h-4 text-emerald-400 mt-0.5" />
        : locked
        ? <Lock className="w-3.5 h-3.5 text-nc-muted/40 mt-0.5" />
        : n === nextNum
        ? <ArrowRight className="w-4 h-4 text-nc-accent mt-0.5" />
        : <span className="text-nc-muted/50 text-xs mt-0.5">—</span>}
      {session.score != null && (
        <span className="text-[8px] font-mono text-emerald-400">{session.score}</span>
      )}
    </div>
  )
}

export default function ProtocolDashboard() {
  const navigate = useNavigate()
  const [status,   setStatus]   = useState(null)
  const [calendar, setCalendar] = useState(null)
  const [progress, setProgress] = useState(null)
  const [loading,  setLoading]  = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const lastFetchRef = useRef(0)

  const fetchData = useCallback(async (silent = false) => {
    const now = Date.now()
    // Dé-dupliquer : pas plus d'un fetch par 3 secondes
    if (now - lastFetchRef.current < 3000) return
    lastFetchRef.current = now

    if (!silent) setLoading(true)
    else setRefreshing(true)

    try {
      const [s, c, p] = await Promise.all([
        protocolApi.status(),
        protocolApi.calendar(),
        protocolApi.progress().catch(() => null),
      ])
      setStatus(s)
      setCalendar(c)
      setProgress(p)
    } catch (err) {
      console.error('ProtocolDashboard fetch:', err)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  // Fetch initial
  useEffect(() => { fetchData() }, [fetchData])

  // Auto-refresh quand la page redevient visible (retour depuis une séance)
  useEffect(() => {
    const handleVisibility = () => {
      if (document.visibilityState === 'visible') fetchData(true)
    }
    document.addEventListener('visibilitychange', handleVisibility)
    return () => document.removeEventListener('visibilitychange', handleVisibility)
  }, [fetchData])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
    </div>
  )

  const sessions   = calendar?.sessions || []
  const nextNum    = calendar?.next_session_number || 1
  const completed  = sessions.filter(s => s.status === 'completed').length
  const s1Done     = completed > 0 && sessions.find(s => s.session_number === 1)?.status === 'completed'
  const totalTarget = progress?.cognitive_profile === 'A' ? 12 : progress?.cognitive_profile === 'C' ? 18 : 15
  const progressPct = Math.round((completed / totalTarget) * 100)
  const palier     = status?.current_palier || 'P1'
  const palierIdx  = ['P1','P2','P3','P4'].indexOf(palier)
  const palierColor = PALIER_COLORS[palier] || '#a78bfa'

  const phase1 = sessions.filter(s => s.phase === 'phase1')
  const phase2 = sessions.filter(s => s.phase === 'phase2')
  const phase3 = sessions.filter(s => s.phase === 'phase3')

  const chartData = sessions
    .filter(s => s.status === 'completed' && s.score != null)
    .map(s => ({ name: `S${s.session_number}`, score: s.score, palier: s.palier }))

  const handleCardClick = (session) => {
    navigate(`/protocol/entry/${session.session_number}`)
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-6 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="w-12 h-12 rounded-2xl bg-nc-accent/15 flex items-center justify-center">
          <Brain className="w-6 h-6 text-nc-accent" />
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-nc-text">Protocole NeuroCap</h1>
          <p className="text-sm text-nc-muted">
            Programme individuel de neurofeedback —{' '}
            {progress?.cognitive_profile === 'A' ? '12' : progress?.cognitive_profile === 'C' ? '18' : '15'} séances
            {progress?.cognitive_profile && (
              <span className="ml-2 text-xs font-semibold px-1.5 py-0.5 rounded-full bg-purple-500/15 text-purple-300">
                Profil {progress.cognitive_profile}
              </span>
            )}
          </p>
        </div>
        {/* Bouton refresh manuel */}
        <button
          onClick={() => fetchData(true)}
          disabled={refreshing}
          title="Actualiser le calendrier"
          className="p-2 rounded-xl text-nc-muted hover:text-nc-accent hover:bg-nc-surface2 transition-colors"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-nc-accent' : ''}`} />
        </button>
        {status?.can_start && nextNum <= 15 && (
          <button
            onClick={() => navigate(`/protocol/entry/${nextNum}`)}
            className="btn-primary flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold"
          >
            <Zap className="w-4 h-4" />
            {nextNum === 1 ? 'Démarrer S1' : `Démarrer S${nextNum}`}
          </button>
        )}
        {!status?.can_start && status?.block_reason && (
          <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-yellow-500/10 border border-yellow-500/25 text-xs text-yellow-400">
            <Clock className="w-3.5 h-3.5 shrink-0" />
            {status.block_reason}
          </div>
        )}
      </div>

      {/* S1 banner si non fait */}
      {!s1Done && (
        <div className="card p-4 border-2 border-amber-500/40 bg-amber-500/6 flex items-center gap-4">
          <AlertCircle className="w-6 h-6 text-amber-400 shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-amber-300">Calibration obligatoire — Séance 1</p>
            <p className="text-xs text-amber-400/70 mt-0.5">
              La calibration individuelle (30 min) est requise pour personnaliser le protocole.
              Sans elle, les séances S2–S15 restent bloquées.
            </p>
          </div>
          <button onClick={() => navigate('/protocol/entry/1')}
            className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-amber-500 text-white text-sm font-semibold shrink-0">
            Commencer <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Stats + palier */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Séances complétées', value: `${completed}/${totalTarget}`, color: 'text-nc-accent' },
          { label: 'Progression',         value: `${progressPct}%`, color: 'text-emerald-400' },
          { label: 'Palier actuel',        value: palier,           color: palierColor, style: true },
          { label: 'Profil cognitif',      value: `Type ${status?.profile_type || '—'}`, color: 'text-purple-400' },
        ].map(({ label, value, color, style }) => (
          <div key={label} className="card p-4 text-center">
            <p className="text-2xl font-bold font-mono" style={style ? { color } : undefined}>
              <span className={style ? '' : color}>{value}</span>
            </p>
            <p className="text-xs text-nc-muted mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Palier barre de progression */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-bold text-nc-text">Palier de difficulté</h2>
          <span className="text-xs font-mono px-2 py-0.5 rounded-full" style={{ background: `${palierColor}20`, color: palierColor }}>
            {palier}
          </span>
        </div>
        <div className="flex gap-2">
          {['P1','P2','P3','P4'].map((p, i) => (
            <div key={p} className="flex-1 space-y-1.5">
              <div className={`h-2 rounded-full transition-all ${i <= palierIdx ? '' : 'opacity-20'}`}
                   style={{ background: i <= palierIdx ? PALIER_COLORS[p] : '#333' }} />
              <p className={`text-[9px] text-center font-semibold ${i === palierIdx ? 'text-nc-text' : 'text-nc-muted/50'}`}>{p}</p>
            </div>
          ))}
        </div>
        <p className="text-xs text-nc-muted">{PALIER_DESC[palier]}</p>
        <div className="grid grid-cols-2 gap-2 text-xs">
          {palierIdx < 3 && (
            <div className="p-2 rounded-xl bg-emerald-500/8 border border-emerald-500/20 text-emerald-400">
              ↑ Montée palier : succès moyen ≥ 65 % sur 3 séances
            </div>
          )}
          {palierIdx > 0 && (
            <div className="p-2 rounded-xl bg-red-500/8 border border-red-500/20 text-red-400">
              ↓ Retour palier : succès moyen {'<'} 35 % sur 2 séances
            </div>
          )}
        </div>
      </div>

      {/* Grille séances */}
      <div className="card p-5 space-y-5">
        <h2 className="text-sm font-bold text-nc-text">Programme des 15 séances</h2>

        {[
          { label: 'Phase 1 — Initiation', desc: '1 séance/semaine · 5 jours min', sessions: phase1, cols: 3, color: 'text-purple-400' },
          { label: 'Phase 2 — Apprentissage', desc: '2 séances/semaine · 2 jours min', sessions: phase2, cols: 7, color: 'text-blue-400' },
          { label: 'Phase 3 — Maîtrise', desc: '2 séances/semaine · 2 jours min', sessions: phase3, cols: 5, color: 'text-emerald-400' },
        ].map(({ label, desc, sessions: ss, cols, color }) => ss.length > 0 && (
          <div key={label} className="space-y-2">
            <div className="flex items-center gap-2">
              <span className={`text-xs font-semibold ${color}`}>{label}</span>
              <span className="text-[10px] text-nc-muted">{desc}</span>
            </div>
            <div className={`grid gap-2`} style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}>
              {ss.map(s => (
                <SessionMini
                  key={s.session_number}
                  session={s}
                  nextNum={nextNum}
                  s1Done={s1Done}
                  onClick={() => handleCardClick(s)}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Courbe scores */}
      {chartData.length >= 2 && (
        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-nc-accent" />
            <h2 className="text-sm font-bold text-nc-text">Évolution du score</h2>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9a8bb0' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#9a8bb0' }} />
              <Tooltip contentStyle={{ background: '#1e1b2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
              <Line type="monotone" dataKey="score" stroke="#6c63ff" strokeWidth={2} dot={{ fill: '#6c63ff', r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Prochaine séance */}
      {nextNum <= 15 && (
        <div className="card p-4 flex items-center gap-3">
          <Calendar className="w-5 h-5 text-nc-accent shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-nc-text">
              Prochaine : S{nextNum}
              {nextNum === 1 && <span className="ml-2 text-xs text-amber-400">— Calibration individuelle</span>}
              {[5,10,15].includes(nextNum) && <span className="ml-2 text-xs text-amber-400">⭐ Séance de bilan</span>}
            </p>
            {/* Date planifiée depuis user_protocol_progress */}
            {(() => {
              const planned = (progress?.planned_session_dates || []).find(p => p.session_num === nextNum)
              return planned?.planned_date ? (
                <p className="text-xs text-nc-muted mt-0.5">
                  Planifiée le{' '}
                  <span className="text-blue-400 font-medium">
                    {new Date(planned.planned_date).toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' })}
                  </span>
                </p>
              ) : null
            })()}
          </div>
          {status?.can_start && (
            <button
              onClick={() => navigate(`/protocol/entry/${nextNum}`)}
              className="flex items-center gap-1.5 btn-primary px-4 py-2 rounded-xl text-sm font-semibold shrink-0">
              Démarrer <ChevronRight className="w-4 h-4" />
            </button>
          )}
        </div>
      )}

      {completed >= totalTarget && (
        <div className="card p-6 text-center border border-emerald-500/25 bg-emerald-500/8">
          <Award className="w-10 h-10 text-emerald-400 mx-auto mb-3" />
          <p className="text-lg font-bold text-emerald-400">Protocole complété !</p>
          <p className="text-sm text-nc-muted mt-1">Félicitations — 15 séances terminées.</p>
        </div>
      )}
    </div>
  )
}
