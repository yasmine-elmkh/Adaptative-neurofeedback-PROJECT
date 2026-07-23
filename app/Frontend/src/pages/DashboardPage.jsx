import { useState, useEffect, useMemo, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../stores'
import { sessions as sessionsApi, eeg as eegApi, assistant as assistantApi } from '../utils/api'
import SessionCalendar from '../components/SessionCalendar'

/* ── Widget Protocole (mini-carte dans le dashboard) ── */
function ProtocolWidget() {
  const navigate = useNavigate()
  const [status, setStatus] = useState(null)

  useEffect(() => {
    const headers = { Authorization: `Bearer ${localStorage.getItem('neurocap_token')}` }
    // Fetch both protocol/status and sessions/calendar in parallel
    // to reconcile counts (protocol_sessions vs feedback_sessions tables)
    Promise.all([
      fetch('/api/protocol/status', { headers }).then(r => r.json()).catch(() => ({})),
      fetch('/api/sessions/calendar', { headers }).then(r => r.json()).catch(() => ({})),
    ]).then(([protocolData, calData]) => {
      const calCompleted   = calData?.total_completed  ?? 0
      const protCompleted  = protocolData?.total_completed ?? 0
      const totalCompleted = Math.max(calCompleted, protCompleted)
      const nextNum        = calData?.next_session_number ?? protocolData?.next_session_number ?? 1
      setStatus({
        ...protocolData,
        total_completed:     totalCompleted,
        next_session_number: nextNum,
        calibration_done:    totalCompleted > 0 || protocolData?.calibration_done,
      })
    }).catch(() => {})
  }, [])

  if (!status) return null

  const n = status.next_session_number
  const s1Done = status.calibration_done

  return (
    <div className="card p-4 flex items-center gap-4 border border-nc-accent/20 bg-nc-accent/4">
      <div className="w-10 h-10 rounded-2xl bg-nc-accent/15 flex items-center justify-center shrink-0">
        <Brain className="w-5 h-5 text-nc-accent" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-nc-text">
          Programme NeuroCap
          {!s1Done && <span className="ml-2 text-[10px] text-amber-400 font-normal">⚠ Calibration requise</span>}
        </p>
        <p className="text-xs text-nc-muted truncate">
          {status.total_completed}/15 séances · Palier {status.current_palier || 'P1'}
          {n <= 15 && ` · Prochaine : S${n}`}
          {status.current_phase && ` · Phase ${status.current_phase}`}
        </p>
      </div>
      <button
        onClick={() => navigate(s1Done ? '/protocol' : '/protocol/calibration')}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl btn-primary text-xs font-semibold shrink-0">
        {!s1Done ? 'Calibrer →' : 'Voir →'}
      </button>
    </div>
  )
}
import {
  LayoutDashboard, TrendingUp, TrendingDown, Activity, Award, ChartBar,
  Play, CalendarDays, Target, Star, Flame, Zap,
  Trophy, Brain, FileText, MessageSquareText, X, Send, Bot, User, Sparkles, Music,
  Upload, ChevronRight, Radio,
} from 'lucide-react'
import {
  LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Legend, ReferenceLine,
} from 'recharts'

// ── Trend helpers ─────────────────────────────────────────────────────────────
function computeTrend(data, field) {
  if (data.length < 4) return null
  const half   = Math.floor(data.length / 2)
  const recent = data.slice(-half).reduce((s, x) => s + (x[field] ?? 0), 0) / half
  const older  = data.slice(0, half).reduce((s, x) => s + (x[field] ?? 0), 0) / half
  if (!older) return null
  return parseFloat(((recent - older) / older * 100).toFixed(1))
}

function predictNextScore(data) {
  if (data.length < 3) return null
  const last3  = data.slice(-3).map(s => s.session_score ?? 0)
  const ma     = last3.reduce((a, b) => a + b, 0) / 3
  const slope  = (last3[2] - last3[0]) / 2
  return Math.min(100, Math.max(0, ma + slope * 0.5)).toFixed(1)
}

// ── Badges ───────────────────────────────────────────────────────────────────
function computeBadges(data) {
  const badges  = []
  const now     = Date.now()
  const weekAgo = now - 7 * 86400e3
  const thisWeek = data.filter(s => new Date(s.created_at).getTime() > weekAgo)

  if (data.length >= 1)     badges.push({ id: 'debutant',    label: 'Débutant',    icon: Star,      color: 'text-nc-muted'    })
  if (data.length >= 5)     badges.push({ id: 'avance',      label: 'Avancé',      icon: Zap,       color: 'text-nc-accent'   })
  if (data.length >= 10)    badges.push({ id: 'expert',      label: 'Expert',      icon: Trophy,    color: 'text-yellow-400'  })
  if (thisWeek.length >= 3) badges.push({ id: 'regulier',    label: 'Régulier',    icon: Flame,     color: 'text-orange-400'  })
  if (data.length >= 2) {
    const trend = computeTrend(data, 'session_score')
    if (trend !== null && trend >= 10)
      badges.push({ id: 'progresseur', label: 'Progresseur', icon: TrendingUp, color: 'text-green-400' })
  }
  const avgScore = data.reduce((s, x) => s + (x.session_score ?? 0), 0) / Math.max(data.length, 1)
  if (avgScore >= 70) badges.push({ id: 'maitre', label: 'Maître', icon: Brain, color: 'text-purple-400' })
  return badges
}

// ── StatCard ─────────────────────────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, color = 'nc-accent', trend }) {
  const colorMap = {
    'nc-accent':  'rgb(var(--nc-accent))',
    'nc-success': 'rgb(var(--nc-success))',
    'nc-warning': 'rgb(var(--nc-warning))',
    'nc-danger':  'rgb(var(--nc-danger))',
  }
  const c = colorMap[color] ?? colorMap['nc-accent']
  return (
    <div className="card p-5 flex items-start gap-4 hover:shadow-md transition-shadow animate-fade-in">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0"
           style={{ background: `${c}20` }}>
        <Icon className="w-5 h-5" style={{ color: c }} />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-nc-muted uppercase tracking-wider truncate">{label}</p>
        <p className="text-2xl font-bold text-nc-text mt-0.5">{value}</p>
        {trend !== null && trend !== undefined && (
          <div className={`flex items-center gap-0.5 text-xs mt-1 font-semibold
                          ${trend >= 0 ? 'text-green-400' : 'text-nc-danger'}`}>
            {trend >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {trend >= 0 ? '+' : ''}{trend}% vs 1ère moitié
          </div>
        )}
      </div>
    </div>
  )
}

// ── Custom Tooltip ────────────────────────────────────────────────────────────
function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="card px-3 py-2 text-xs shadow-glass min-w-[120px]">
      <p className="text-nc-muted mb-1.5 font-medium">{label}</p>
      {payload.map((p) => (
        <p key={p.name} className="font-semibold flex justify-between gap-4" style={{ color: p.color }}>
          <span>{p.name}</span>
          <span>{p.value?.toFixed(1)}%</span>
        </p>
      ))}
    </div>
  )
}

// ── Session Mode Modal ────────────────────────────────────────────────────────
function SessionModeModal({ onClose }) {
  const navigate = useNavigate()

  const modes = [
    {
      key: 'live',
      icon: Radio,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/15',
      title: 'EEG en direct',
      desc: 'Positionner le casque, acquisition temps réel, classification automatique',
      path: '/eeg/live',
    },
    {
      key: 'offline',
      icon: Upload,
      color: 'text-purple-400',
      bg: 'bg-purple-500/15',
      title: 'Fichier EEG (offline)',
      desc: 'Téléverser un fichier CSV/EDF — classification puis neurofeedback',
      path: '/eeg/upload',
    },
    {
      key: 'manual',
      icon: Brain,
      color: 'text-nc-accent',
      bg: 'bg-nc-accent/15',
      title: 'Au choix',
      desc: 'Décrire votre état manuellement, sans casque ni fichier',
      path: '/feedback',
    },
  ]

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(0,0,0,0.55)', backdropFilter: 'blur(6px)' }}
      onClick={onClose}
    >
      <div
        className="card max-w-md w-full p-6 space-y-5 animate-fade-in"
        onClick={e => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-bold text-nc-text">Démarrer une séance</h2>
            <p className="text-xs text-nc-muted mt-0.5">Choisissez votre mode d'acquisition EEG</p>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-xl text-nc-muted hover:bg-nc-surface2 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3">
          {modes.map(({ key, icon: Icon, color, bg, title, desc, path }) => (
            <button
              key={key}
              onClick={() => { onClose(); navigate(path) }}
              className="w-full card p-4 flex items-center gap-4 hover:border-nc-accent/40 transition-all text-start group"
            >
              <div className={`w-10 h-10 rounded-2xl ${bg} flex items-center justify-center shrink-0`}>
                <Icon className={`w-5 h-5 ${color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-nc-text">{title}</p>
                <p className="text-xs text-nc-muted leading-relaxed mt-0.5">{desc}</p>
              </div>
              <ChevronRight className="w-4 h-4 text-nc-muted group-hover:text-nc-accent transition-colors shrink-0" />
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── Empty state ───────────────────────────────────────────────────────────────
function EmptyState({ t, onStartSession }) {
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4 animate-fade-in">
      <div className="w-20 h-20 rounded-full flex items-center justify-center"
           style={{ background: 'rgb(var(--nc-accent)/0.1)' }}>
        <Activity className="w-10 h-10 text-nc-accent" />
      </div>
      <h3 className="text-xl font-semibold text-nc-text">{t('dashboard.no_sessions')}</h3>
      <p className="text-nc-muted text-sm text-center max-w-sm">{t('dashboard.no_sessions_sub')}</p>
      <div className="flex gap-3 mt-2 flex-wrap justify-center">
        <button className="btn-primary" onClick={onStartSession}>
          <Play className="w-4 h-4" />
          {t('dashboard.start_session')}
        </button>
      </div>
    </div>
  )
}

// ── EEG Recordings Panel ──────────────────────────────────────────────────────
const DOMINANT_LABEL = {
  stress:        { label: 'Stress',        cssVar: 'nc-danger'  },
  concentration: { label: 'Concentration', cssVar: 'nc-accent'  },
  neutral:       { label: 'Neutre',        cssVar: 'nc-muted'   },
  uncertain:     { label: 'Incertain',     cssVar: 'nc-muted'   },
}

function EEGRecordingsPanel({ reports, sessions }) {
  const sorted    = [...reports].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
  const total     = reports.length
  const liveCount = reports.filter(r => r.type === 'live').length
  const fileCount = reports.filter(r => r.type === 'file').length

  const avgStress = reports.reduce((s, r) => s + (r.stress_pct        ?? 0), 0) / Math.max(total, 1)
  const avgConc   = reports.reduce((s, r) => s + (r.concentration_pct ?? 0), 0) / Math.max(total, 1)

  const half = Math.floor(sorted.length / 2)
  const stressTrend = sorted.length >= 4 ? (() => {
    const recent = sorted.slice(-half).reduce((s, r) => s + (r.stress_pct ?? 0), 0) / half
    const older  = sorted.slice(0,  half).reduce((s, r) => s + (r.stress_pct ?? 0), 0) / half
    return older ? parseFloat(((recent - older) / older * 100).toFixed(1)) : null
  })() : null
  const concTrend = sorted.length >= 4 ? (() => {
    const recent = sorted.slice(-half).reduce((s, r) => s + (r.concentration_pct ?? 0), 0) / half
    const older  = sorted.slice(0,  half).reduce((s, r) => s + (r.concentration_pct ?? 0), 0) / half
    return older ? parseFloat(((recent - older) / older * 100).toFixed(1)) : null
  })() : null

  const chartData = sorted.map(r => ({
    name:          new Date(r.created_at).toLocaleDateString('fr', { month: 'short', day: 'numeric' }),
    stress:        r.stress_pct        != null ? Math.round(r.stress_pct)        : null,
    concentration: r.concentration_pct != null ? Math.round(r.concentration_pct) : null,
  }))

  // Impact sessions neurofeedback : comparer état EEG avant 1ère session vs après dernière
  let sessionImpact = null
  if (sessions.length > 0 && sorted.length >= 2) {
    const sortedSess = [...sessions].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
    const firstSess  = new Date(sortedSess[0].created_at)
    const lastSess   = new Date(sortedSess[sortedSess.length - 1].created_at)
    const before     = sorted.filter(r => new Date(r.created_at) < firstSess)
    const after      = sorted.filter(r => new Date(r.created_at) > lastSess)
    if (before.length > 0 && after.length > 0) {
      const avgBStress = before.reduce((s, r) => s + (r.stress_pct        ?? 0), 0) / before.length
      const avgAStress = after.reduce((s, r)  => s + (r.stress_pct        ?? 0), 0) / after.length
      const avgBConc   = before.reduce((s, r) => s + (r.concentration_pct ?? 0), 0) / before.length
      const avgAConc   = after.reduce((s, r)  => s + (r.concentration_pct ?? 0), 0) / after.length
      sessionImpact = {
        stressDelta: parseFloat((avgAStress - avgBStress).toFixed(1)),
        concDelta:   parseFloat((avgAConc   - avgBConc  ).toFixed(1)),
        n_sessions:  sessions.length,
      }
    }
  }

  const lastReport  = sorted[sorted.length - 1]
  const lastDomInfo = lastReport
    ? (DOMINANT_LABEL[lastReport.dominant_state] ?? { label: lastReport.dominant_state ?? '—', cssVar: 'nc-muted' })
    : null

  return (
    <div className="space-y-6 animate-fade-in">

      {/* ── Header ── */}
      <div className="flex items-center gap-2 flex-wrap">
        <Activity className="w-4 h-4 text-nc-accent" />
        <h2 className="font-semibold text-nc-text">Enregistrements EEG</h2>
        <span className="badge-muted">{total} enregistrement{total > 1 ? 's' : ''}</span>
        <span className="text-xs text-nc-muted">({liveCount} live · {fileCount} fichier)</span>
      </div>

      {/* ── Stat cards ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={FileText}   label="Total enregistrements"  value={total}                       color="nc-accent"  />
        <StatCard icon={Activity}   label="Stress moyen"           value={`${avgStress.toFixed(1)}%`}  color="nc-danger"  trend={stressTrend !== null ? -stressTrend : null} />
        <StatCard icon={Brain}      label="Concentration moyenne"  value={`${avgConc.toFixed(1)}%`}    color="nc-success" trend={concTrend} />
        <StatCard
          icon={TrendingUp}
          label="État dominant (dernier)"
          value={lastDomInfo?.label ?? '—'}
          color={lastReport
            ? ({ stress: 'nc-danger', concentration: 'nc-accent', neutral: 'nc-muted', uncertain: 'nc-warning' }[lastReport.dominant_state] ?? 'nc-accent')
            : 'nc-accent'}
        />
      </div>

      {/* ── Trend chart ── */}
      {chartData.length >= 2 && (
        <div className="card p-6 space-y-4">
          <div className="flex items-center gap-2 flex-wrap">
            <ChartBar className="w-4 h-4 text-nc-accent" />
            <h3 className="font-semibold text-nc-text text-sm">Évolution stress / concentration</h3>
            <div className="ms-auto flex items-center gap-4 text-xs">
              {stressTrend !== null && (
                <span className={`flex items-center gap-1 font-semibold ${stressTrend > 0 ? 'text-nc-danger' : 'text-nc-success'}`}>
                  {stressTrend > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  Stress {stressTrend > 0 ? '+' : ''}{stressTrend}%
                </span>
              )}
              {concTrend !== null && (
                <span className={`flex items-center gap-1 font-semibold ${concTrend > 0 ? 'text-nc-success' : 'text-nc-warning'}`}>
                  {concTrend > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                  Concentration {concTrend > 0 ? '+' : ''}{concTrend}%
                </span>
              )}
            </div>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={chartData} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
              <defs>
                <linearGradient id="gradStress" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="rgb(var(--nc-danger))" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="rgb(var(--nc-danger))" stopOpacity={0.0} />
                </linearGradient>
                <linearGradient id="gradConc" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="rgb(var(--nc-accent))" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="rgb(var(--nc-accent))" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--nc-border))" />
              <XAxis dataKey="name" tick={{ fill: 'rgb(var(--nc-muted))', fontSize: 10 }} axisLine={false} tickLine={false} />
              <YAxis domain={[0, 100]} tick={{ fill: 'rgb(var(--nc-muted))', fontSize: 10 }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: 11, color: 'rgb(var(--nc-muted))' }} />
              <Area type="monotone" dataKey="stress"        name="Stress (%)"        stroke="rgb(var(--nc-danger))" strokeWidth={2} fill="url(#gradStress)" connectNulls />
              <Area type="monotone" dataKey="concentration" name="Concentration (%)" stroke="rgb(var(--nc-accent))" strokeWidth={2} fill="url(#gradConc)"   connectNulls />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* ── Session impact ── */}
      {sessionImpact && (
        <div className="card p-5 border border-nc-accent/20">
          <div className="flex items-center gap-2 mb-4">
            <Brain className="w-4 h-4 text-nc-accent" />
            <h3 className="font-semibold text-nc-text text-sm">Impact des sessions neurofeedback</h3>
            <span className="badge-muted">{sessionImpact.n_sessions} session{sessionImpact.n_sessions > 1 ? 's' : ''}</span>
          </div>
          <div className="grid grid-cols-2 gap-6">
            <div className="space-y-1">
              <p className="text-xs text-nc-muted uppercase tracking-wider">Évolution du stress</p>
              <div className={`flex items-center gap-2 text-xl font-bold ${sessionImpact.stressDelta <= 0 ? 'text-nc-success' : 'text-nc-danger'}`}>
                {sessionImpact.stressDelta <= 0 ? <TrendingDown className="w-5 h-5" /> : <TrendingUp className="w-5 h-5" />}
                {sessionImpact.stressDelta >= 0 ? '+' : ''}{sessionImpact.stressDelta}%
              </div>
              <p className="text-xs text-nc-muted">{sessionImpact.stressDelta <= 0 ? 'Réduction' : 'Augmentation'} après les sessions</p>
            </div>
            <div className="space-y-1">
              <p className="text-xs text-nc-muted uppercase tracking-wider">Évolution de la concentration</p>
              <div className={`flex items-center gap-2 text-xl font-bold ${sessionImpact.concDelta >= 0 ? 'text-nc-success' : 'text-nc-warning'}`}>
                {sessionImpact.concDelta >= 0 ? <TrendingUp className="w-5 h-5" /> : <TrendingDown className="w-5 h-5" />}
                {sessionImpact.concDelta >= 0 ? '+' : ''}{sessionImpact.concDelta}%
              </div>
              <p className="text-xs text-nc-muted">{sessionImpact.concDelta >= 0 ? 'Amélioration' : 'Diminution'} après les sessions</p>
            </div>
          </div>
        </div>
      )}

      {/* ── Recent recordings table ── */}
      <div className="card overflow-hidden">
        <div className="px-6 py-4 border-b border-nc-border flex items-center gap-2">
          <FileText className="w-4 h-4 text-nc-accent" />
          <h3 className="font-semibold text-nc-text text-sm">Derniers enregistrements</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-nc-border text-nc-muted text-xs uppercase tracking-wider">
                <th className="py-3 px-6 text-start font-medium">Date</th>
                <th className="py-3 px-4 text-start font-medium">Type</th>
                <th className="py-3 px-4 text-center font-medium">Stress</th>
                <th className="py-3 px-4 text-center font-medium">Concentration</th>
                <th className="py-3 px-4 text-center font-medium">État dominant</th>
                <th className="py-3 px-4 text-center font-medium">Confiance</th>
              </tr>
            </thead>
            <tbody>
              {[...sorted].reverse().slice(0, 10).map((r, i) => {
                const dom = DOMINANT_LABEL[r.dominant_state] ?? { label: r.dominant_state ?? '—', cssVar: 'nc-muted' }
                return (
                  <tr key={r.id ?? i} className="border-b border-nc-border/50 hover:bg-nc-surface2 transition-colors">
                    <td className="py-3 px-6 text-nc-muted">
                      {new Date(r.created_at).toLocaleString('fr', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3 px-4">
                      <span className={`text-xs font-semibold px-2 py-0.5 rounded-full
                        ${r.type === 'live' ? 'bg-green-500/10 text-green-400' : 'bg-purple-500/10 text-purple-400'}`}>
                        {r.type === 'live' ? '● Live' : '◆ Fichier'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center font-semibold text-nc-danger">
                      {r.stress_pct != null ? `${r.stress_pct.toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3 px-4 text-center font-semibold text-nc-accent">
                      {r.concentration_pct != null ? `${r.concentration_pct.toFixed(1)}%` : '—'}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-xs font-semibold" style={{ color: `rgb(var(--${dom.cssVar}))` }}>
                        {dom.label}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-center text-nc-muted">
                      {r.mean_confidence != null ? `${(r.mean_confidence * 100).toFixed(0)}%` : '—'}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}


// ── Mini assistant flottant ──────────────────────────────────────────────────
let _fid = 0
const mkFMsg = (role, text, sources = []) => ({ id: ++_fid, role, text, sources })

// Suggestions rapides contextuelles (NEJM RAG article : patient education use case)
const QUICK_SUGGESTIONS = [
  { label: '📊 Expliquer mon dashboard', action: 'explain' },
  { label: '🎯 Comment améliorer mon TBR ?', action: 'ask', text: 'Comment améliorer mon TBR et ma concentration ?' },
  { label: '😤 Réduire mon stress EEG', action: 'ask', text: 'Quels exercices faire pour réduire mon stress avant une séance ?' },
  { label: '📈 Ma progression', action: 'ask', text: 'Comment interpréter ma progression sur le programme ?' },
]

function FloatingAssistant({ open, onToggle }) {
  const [messages,     setMessages]     = useState([])
  const [input,        setInput]        = useState('')
  const [loading,      setLoading]      = useState(false)
  const [showSuggest,  setShowSuggest]  = useState(true)
  const bottomRef = useRef()

  useEffect(() => {
    if (open && messages.length === 0) {
      setMessages([mkFMsg('assistant',
        'Bonjour ! Je suis NeuroCoach, votre assistant NeuroCap.\n\n' +
        'Je peux analyser vos résultats EEG, expliquer vos métriques et vous guider dans votre programme de 15 séances.'
      )])
    }
  }, [open])

  useEffect(() => {
    if (open) bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, open])

  const _ragErrMsg = (err) => {
    if (!err?.response) return 'Impossible de joindre le serveur. Vérifiez que le backend est démarré sur le port 8001.'
    const status = err.response.status
    if (status === 401) return 'Session expirée. Reconnectez-vous.'
    if (status === 422) return 'Requête invalide (422). Contactez le support.'
    if (status === 500) {
      const detail = err.response.data?.detail || ''
      return `Erreur serveur (500)${detail ? ' : ' + detail.slice(0, 120) : ''}. Vérifiez les logs backend.`
    }
    return `Erreur ${status}. Réessayez.`
  }

  const send = useCallback(async (text = input.trim()) => {
    if (!text || loading) return
    setMessages(m => [...m, mkFMsg('user', text)])
    setInput('')
    setLoading(true)
    setShowSuggest(false)
    try {
      const res    = await assistantApi.ask(text, null, null)
      const answer = res.answer ?? res.response ?? 'Une erreur est survenue.'
      setMessages(m => [...m, mkFMsg('assistant', answer, res.sources || [])])
    } catch (err) {
      setMessages(m => [...m, mkFMsg('assistant', _ragErrMsg(err))])
    } finally {
      setLoading(false)
    }
  }, [input, loading])

  const handleExplain = useCallback(async () => {
    setMessages(m => [...m, mkFMsg('user', '📊 Explique-moi tous mes résultats du dashboard')])
    setShowSuggest(false)
    setLoading(true)
    try {
      const res    = await assistantApi.explain()
      const answer = res.answer ?? res.response ?? 'Une erreur est survenue.'
      setMessages(m => [...m, mkFMsg('assistant', answer, res.sources || [])])
    } catch (err) {
      setMessages(m => [...m, mkFMsg('assistant', _ragErrMsg(err))])
    } finally {
      setLoading(false)
    }
  }, [loading])

  const handleSuggestion = useCallback((s) => {
    if (s.action === 'explain') handleExplain()
    else send(s.text)
  }, [handleExplain, send])

  return (
    <>
      {/* Panel chat flottant */}
      {open && (
        <div
          className="fixed bottom-6 end-6 z-50 flex flex-col rounded-2xl shadow-glass-lg border border-nc-border overflow-hidden animate-fade-in"
          style={{ width: 560, height: 'calc(100vh - 5rem)', background: 'rgb(var(--nc-surface))' }}
        >
          {/* Header */}
          <div className="flex items-center gap-3 px-5 py-4 border-b border-nc-border shrink-0"
               style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)/0.12), rgb(var(--nc-accent)/0.05))' }}>
            <div className="w-10 h-10 rounded-2xl flex items-center justify-center text-white shrink-0"
                 style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' }}>
              <Sparkles className="w-5 h-5" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-base font-bold text-nc-text">NeuroCoach</p>
              <p className="text-xs text-nc-muted">Assistant EEG · RAG · Données personnelles</p>
            </div>
            <button onClick={onToggle} className="p-1.5 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map(m => (
              <div key={m.id} className={`flex gap-2.5 ${m.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5
                                 ${m.role === 'user' ? 'bg-nc-accent/20 text-nc-accent' : 'text-white'}`}
                     style={m.role !== 'user' ? { background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' } : {}}>
                  {m.role === 'user' ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                </div>
                <div className="flex flex-col gap-1 max-w-[85%]">
                  <div className={`px-3.5 py-2.5 rounded-xl text-sm leading-relaxed whitespace-pre-wrap
                                   ${m.role === 'user'
                                     ? 'bg-nc-accent text-white rounded-tr-sm'
                                     : 'bg-nc-surface2 text-nc-text rounded-tl-sm border border-nc-border'}`}>
                    {m.text}
                  </div>
                  {/* Sources — traçabilité (NEJM RAG article Table 1) */}
                  {m.role === 'assistant' && m.sources?.length > 0 && (
                    <div className="flex flex-wrap gap-1 px-0.5">
                      {m.sources.slice(0, 2).map(s => (
                        <span key={s} className="text-[9px] px-1.5 py-0.5 rounded-full bg-nc-surface2
                                                  border border-nc-border text-nc-muted truncate max-w-[140px]">
                          {s}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Suggestions rapides */}
            {showSuggest && messages.length <= 1 && !loading && (
              <div className="space-y-1.5 animate-fade-in">
                {QUICK_SUGGESTIONS.map(s => (
                  <button
                    key={s.label}
                    onClick={() => handleSuggestion(s)}
                    className="w-full text-left px-4 py-2.5 rounded-xl text-sm text-nc-muted
                               bg-nc-surface2 border border-nc-border hover:border-nc-accent/40
                               hover:text-nc-accent transition-all"
                  >
                    {s.label}
                  </button>
                ))}
              </div>
            )}

            {loading && (
              <div className="flex gap-2">
                <div className="w-6 h-6 rounded-full flex items-center justify-center text-white shrink-0"
                     style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' }}>
                  <Bot className="w-3 h-3" />
                </div>
                <div className="px-3 py-2.5 rounded-xl bg-nc-surface2 border border-nc-border flex items-center gap-2">
                  <div className="flex gap-1">
                    {[0,1,2].map(i => (
                      <div key={i} className="w-1.5 h-1.5 rounded-full bg-nc-accent/70 animate-bounce"
                           style={{ animationDelay: `${i * 0.15}s` }} />
                    ))}
                  </div>
                  <span className="text-[10px] text-nc-muted">Analyse en cours…</span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-nc-border shrink-0">
            <div className="flex gap-2.5">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() } }}
                placeholder="Posez votre question…"
                className="flex-1 bg-nc-surface2 border border-nc-border rounded-xl px-4 py-2.5 text-sm
                           text-nc-text placeholder:text-nc-muted focus:outline-none
                           focus:border-nc-accent/60 transition-colors"
              />
              <button
                onClick={() => send()}
                disabled={!input.trim() || loading}
                className="w-10 h-10 rounded-xl flex items-center justify-center text-white transition-all disabled:opacity-40"
                style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.7))' }}
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Bouton flottant — toujours visible */}
      <button
        onClick={onToggle}
        className="fixed bottom-6 end-6 z-50 w-14 h-14 rounded-2xl text-white shadow-glass-lg
                   flex items-center justify-center transition-all hover:scale-110 active:scale-95"
        style={{ background: open
          ? 'linear-gradient(135deg, rgb(var(--nc-accent)/0.7), rgb(var(--nc-accent)/0.5))'
          : 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.7))' }}
        title="NeuroCoach — Assistant EEG"
      >
        {open ? <X className="w-5 h-5" /> : <MessageSquareText className="w-5 h-5" />}
      </button>
    </>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const { t }    = useTranslation()
  const { user } = useAuthStore()
  const navigate = useNavigate()

  const [sessionList,    setSessionList]    = useState([])
  const [loading,        setLoading]        = useState(true)
  const [objFilter,      setObjFilter]      = useState('all')
  const [eegReports,     setEegReports]     = useState([])
  const [assistantOpen,  setAssistantOpen]  = useState(false)

  useEffect(() => {
    sessionsApi.list()
      .then(d => setSessionList(Array.isArray(d) ? d : []))
      .catch(() => setSessionList([]))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    eegApi.myReports(100)
      .then(d => setEegReports(Array.isArray(d) ? d : []))
      .catch(() => {})
  }, [])

  const filteredData = useMemo(() =>
    objFilter === 'all'
      ? sessionList
      : sessionList.filter(s => s.objective === objFilter),
    [sessionList, objFilter]
  )

  // ── Loading ──────────────────────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-2 border-nc-accent border-t-transparent rounded-full animate-spin" />
          <p className="text-nc-muted text-sm">{t('dashboard.loading')}</p>
        </div>
      </div>
    )
  }

  // ── Completely empty ─────────────────────────────────────────────────────────
  if (!sessionList.length && !eegReports.length) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-nc-muted text-sm">
            <LayoutDashboard className="w-4 h-4" />
            <span>{t('dashboard.title')}</span>
            <span className="text-nc-text font-semibold ms-1">
              {user?.first_name || user?.email?.split('@')[0] || ''}
            </span>
          </div>
          <button className="btn-primary shrink-0" onClick={() => navigate('/session/setup')}>
            <Play className="w-4 h-4" />
            {t('dashboard.start_session')}
          </button>
        </div>
        <SessionCalendar patientId={user?.id} />
        <EmptyState t={t} onStartSession={() => navigate('/session/setup')} />
      </div>
    )
  }

  // ── Session stats (computed only when sessions exist) ────────────────────────
  const total      = sessionList.length
  const avgScore   = (sessionList.reduce((s, x) => s + (x.session_score ?? 0), 0) / Math.max(total, 1)).toFixed(1)
  const avgTBR     = (sessionList.reduce((s, x) => s + (x.avg_tbr       ?? 0), 0) / Math.max(total, 1)).toFixed(2)
  const scoreTrend = computeTrend(sessionList, 'session_score')
  const tbrTrend   = computeTrend(sessionList, 'avg_tbr')
  const nextScore  = predictNextScore(sessionList)
  const badges     = computeBadges(sessionList)

  const sessionChartData = filteredData.map((s, i) => ({
    name:       `S${i + 1}`,
    score:      s.session_score != null ? parseFloat(s.session_score.toFixed(1)) : null,
    tbr_scaled: s.avg_tbr       != null ? parseFloat((s.avg_tbr * 10).toFixed(1)) : null,
  }))

  // ── Main layout ──────────────────────────────────────────────────────────────
  return (
    <div style={{ paddingRight: assistantOpen ? '568px' : '0', transition: 'padding-right 0.35s cubic-bezier(0.4,0,0.2,1)' }}>
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">

      {/* ── Header ── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 animate-slide-up">
        <div>
          <div className="flex items-center gap-2 text-nc-muted text-sm mb-1">
            <LayoutDashboard className="w-4 h-4" />
            {t('dashboard.title')}
          </div>
          <h1 className="text-3xl font-bold text-nc-text">
            {t('dashboard.welcome')}{' '}
            {user?.first_name || user?.email?.split('@')[0] || '—'}
          </h1>
          <p className="text-nc-muted mt-1">{t('dashboard.subtitle')}</p>
        </div>
        <button className="btn-primary shrink-0 self-start sm:self-auto" onClick={() => navigate('/session/setup')}>
          <Play className="w-4 h-4" />
          {t('dashboard.start_session')}
        </button>
      </div>

      {/* ── Widget Prochain protocole ── */}
      <ProtocolWidget userId={user?.id} />

      {/* ── Widget Médias & Recommandations ── */}
      <div
        onClick={() => navigate('/media-dashboard')}
        className="card p-4 flex items-center gap-4 border border-purple-500/20 bg-purple-500/4 cursor-pointer hover:border-purple-500/40 transition-colors"
      >
        <div className="w-10 h-10 rounded-2xl bg-purple-500/15 flex items-center justify-center shrink-0">
          <Music className="w-5 h-5 text-purple-400" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-nc-text">Médias & Recommandations</p>
          <p className="text-xs text-nc-muted truncate">Playlists, recos EEG adaptatives, analyses offline</p>
        </div>
        <span className="text-xs text-purple-400 font-semibold shrink-0">Voir →</span>
      </div>

      {/* ── Calendrier protocole 15 séances ── */}
      <SessionCalendar patientId={user?.id} />

      {/* ── EEG Recordings (section principale — toujours au top) ── */}
      {eegReports.length > 0 && (
        <EEGRecordingsPanel
          reports={eegReports}
          sessions={sessionList}
        />
      )}

      {/* ── Section sessions neurofeedback (visible uniquement si sessions) ── */}
      {sessionList.length > 0 && (
        <>
          {/* Stats sessions */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard icon={Award}      label={t('dashboard.stats.total_sessions')} value={total}                               color="nc-accent"  />
            <StatCard icon={Target}     label={t('dashboard.stats.avg_score')}      value={`${avgScore}%`}                      color="nc-success" trend={scoreTrend} />
            <StatCard icon={ChartBar}   label={t('dashboard.stats.avg_tbr')}        value={avgTBR}                              color="nc-warning" trend={tbrTrend !== null ? -tbrTrend : null} />
            <StatCard icon={TrendingUp} label="Prochain score estimé"               value={nextScore ? `~${nextScore}%` : '—'} color="nc-accent"  />
          </div>

          {/* Badges */}
          {badges.length > 0 && (
            <div className="flex flex-wrap gap-2 animate-fade-in">
              {badges.map(({ id, label, icon: Icon, color }) => (
                <div key={id}
                     className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-nc-surface border border-nc-border text-sm font-medium">
                  <Icon className={`w-3.5 h-3.5 ${color}`} />
                  <span className="text-nc-text">{label}</span>
                </div>
              ))}
            </div>
          )}

          {/* Score chart */}
          <div className="card p-6 space-y-4">
              <div className="flex items-center gap-2 flex-wrap">
                <TrendingUp className="w-4 h-4 text-nc-accent" />
                <h2 className="font-semibold text-nc-text">{t('dashboard.sections.score_history')}</h2>
                <span className="ms-auto badge-muted">{filteredData.length} sessions</span>
                <div className="flex gap-1 ms-2">
                  {['all','concentration','relaxation'].map(k => (
                    <button
                      key={k}
                      onClick={() => setObjFilter(k)}
                      className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors
                                  ${objFilter === k
                                    ? 'bg-nc-accent text-white'
                                    : 'bg-nc-surface2 text-nc-muted hover:text-nc-text'}`}
                    >
                      {k === 'all' ? 'Tous' : k === 'concentration' ? 'Concentration' : 'Relaxation'}
                    </button>
                  ))}
                </div>
              </div>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={sessionChartData} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgb(var(--nc-border))" />
                  <XAxis dataKey="name" tick={{ fill: 'rgb(var(--nc-muted))', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fill: 'rgb(var(--nc-muted))', fontSize: 11 }} axisLine={false} tickLine={false} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend wrapperStyle={{ fontSize: 11, color: 'rgb(var(--nc-muted))' }} />
                  {nextScore && (
                    <ReferenceLine y={parseFloat(nextScore)}
                      stroke="rgb(var(--nc-accent))" strokeDasharray="4 4" strokeWidth={1}
                      label={{ value: `≈${nextScore}%`, position: 'insideTopRight', fill: 'rgb(var(--nc-accent))', fontSize: 10 }} />
                  )}
                  <Line type="monotone" dataKey="score" name="Score (%)"
                    stroke="rgb(var(--nc-accent))" strokeWidth={2.5}
                    dot={{ fill: 'rgb(var(--nc-accent))', r: 4 }} activeDot={{ r: 6 }} connectNulls />
                  <Line type="monotone" dataKey="tbr_scaled" name="TBR ×10"
                    stroke="rgb(var(--nc-warning))" strokeWidth={1.5} strokeDasharray="4 2"
                    dot={false} connectNulls />
                </LineChart>
              </ResponsiveContainer>
          </div>

          {/* Session history table */}
          <div className="card overflow-hidden">
            <div className="px-6 py-4 border-b border-nc-border flex items-center gap-2">
              <CalendarDays className="w-4 h-4 text-nc-accent" />
              <h2 className="font-semibold text-nc-text">{t('dashboard.sections.session_history')}</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-nc-border text-nc-muted text-xs uppercase tracking-wider">
                    <th className="py-3 px-6 text-start font-medium">{t('dashboard.table.session')}</th>
                    <th className="py-3 px-4 text-start font-medium">{t('dashboard.table.date')}</th>
                    <th className="py-3 px-4 text-start font-medium">{t('dashboard.table.objective')}</th>
                    <th className="py-3 px-4 text-center font-medium">{t('dashboard.table.score')}</th>
                    <th className="py-3 px-4 text-center font-medium">{t('dashboard.table.tbr')}</th>
                    <th className="py-3 px-4 text-center font-medium">{t('dashboard.table.success_rate')}</th>
                  </tr>
                </thead>
                <tbody>
                  {sessionList.map((s, i) => {
                    const prev       = sessionList[i - 1]
                    const scoreDelta = prev ? (s.session_score ?? 0) - (prev.session_score ?? 0) : null
                    return (
                      <tr key={s.id ?? i}
                          className="border-b border-nc-border/50 hover:bg-nc-surface2 transition-colors">
                        <td className="py-3 px-6 font-semibold text-nc-text">S{i + 1}</td>
                        <td className="py-3 px-4 text-nc-muted">{new Date(s.created_at).toLocaleDateString()}</td>
                        <td className="py-3 px-4">
                          <span className="badge-accent capitalize">{s.objective ?? '—'}</span>
                        </td>
                        <td className="py-3 px-4 text-center">
                          <div className="flex items-center justify-center gap-1">
                            <span className="font-bold text-nc-accent">{s.session_score?.toFixed(1) ?? '—'}%</span>
                            {scoreDelta !== null && (
                              <span className={`text-xs font-medium ${scoreDelta >= 0 ? 'text-green-400' : 'text-nc-danger'}`}>
                                {scoreDelta >= 0 ? '▲' : '▼'}{Math.abs(scoreDelta).toFixed(0)}
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="py-3 px-4 text-center font-mono text-nc-text">{s.avg_tbr?.toFixed(2) ?? '—'}</td>
                        <td className="py-3 px-4 text-center">
                          <span className={`font-semibold ${(s.success_rate ?? 0) >= 0.7 ? 'text-nc-success' : 'text-nc-warning'}`}>
                            {((s.success_rate ?? 0) * 100).toFixed(0)}%
                          </span>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

    </div>
    <FloatingAssistant open={assistantOpen} onToggle={() => setAssistantOpen(o => !o)} />
    </div>
  )
}
