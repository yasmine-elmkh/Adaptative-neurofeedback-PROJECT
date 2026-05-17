import { useState, useEffect, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useAuthStore } from '../stores'
import { sessions as sessionsApi, profile as profileApi } from '../utils/api'
import {
  LayoutDashboard, TrendingUp, TrendingDown, Activity, Award, ChartBar,
  Play, CalendarDays, Target, Cpu, WifiOff, X, Star, Flame, Zap,
  Trophy, Brain, AlertTriangle, ChevronDown,
} from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Legend, ReferenceLine,
} from 'recharts'
import Brain3D from '../components/Brain3D'
import RecommendationEngine from '../components/RecommendationEngine'

// ── Simulation data factory ──────────────────────────────────────────────────
function generateSimSessions(count = 10) {
  const now = Date.now()
  return Array.from({ length: count }, (_, i) => {
    const p     = i / Math.max(count - 1, 1)
    const score = Math.min(91, Math.max(12, 28 + p * 52 + (Math.random() - 0.5) * 18))
    const tbr   = Math.max(1.8, 4.1 - p * 2.0 + (Math.random() - 0.5) * 0.75)
    const sr    = Math.min(0.93, Math.max(0.15, 0.30 + p * 0.55 + (Math.random() - 0.5) * 0.12))
    return {
      id: `sim-${i}`,
      created_at: new Date(now - (count - i) * 2 * 86400e3).toISOString(),
      session_score: score,
      avg_tbr: tbr,
      success_rate: sr,
      objective: i % 3 === 0 ? 'relaxation' : 'concentration',
      status: 'completed',
    }
  })
}

// ── Trend helpers ─────────────────────────────────────────────────────────────
function computeTrend(data, field) {
  if (data.length < 4) return null
  const half = Math.floor(data.length / 2)
  const recent = data.slice(-half).reduce((s, x) => s + (x[field] ?? 0), 0) / half
  const older  = data.slice(0, half).reduce((s, x) => s + (x[field] ?? 0), 0) / half
  if (!older) return null
  return parseFloat(((recent - older) / older * 100).toFixed(1))
}

function predictNextScore(data) {
  if (data.length < 3) return null
  const last3 = data.slice(-3).map(s => s.session_score ?? 0)
  const ma = last3.reduce((a, b) => a + b, 0) / 3
  // Simple linear extrapolation
  const slope = (last3[2] - last3[0]) / 2
  return Math.min(100, Math.max(0, ma + slope * 0.5)).toFixed(1)
}

// ── Badges ───────────────────────────────────────────────────────────────────
function computeBadges(data) {
  const badges = []
  const now = Date.now()
  const weekAgo = now - 7 * 86400e3
  const thisWeek = data.filter(s => new Date(s.created_at).getTime() > weekAgo)

  if (data.length >= 1)  badges.push({ id: 'debutant',   label: 'Débutant',    icon: Star,   color: 'text-nc-muted' })
  if (data.length >= 5)  badges.push({ id: 'avance',     label: 'Avancé',      icon: Zap,    color: 'text-nc-accent' })
  if (data.length >= 10) badges.push({ id: 'expert',     label: 'Expert',      icon: Trophy, color: 'text-yellow-400' })
  if (thisWeek.length >= 3) badges.push({ id: 'regulier', label: 'Régulier',   icon: Flame,  color: 'text-orange-400' })
  if (data.length >= 2) {
    const trend = computeTrend(data, 'session_score')
    if (trend !== null && trend >= 10) badges.push({ id: 'progresseur', label: 'Progresseur', icon: TrendingUp, color: 'text-green-400' })
  }
  const avgScore = data.reduce((s, x) => s + (x.session_score ?? 0), 0) / Math.max(data.length, 1)
  if (avgScore >= 70) badges.push({ id: 'maitre', label: 'Maître', icon: Brain, color: 'text-purple-400' })

  return badges
}

// ── Calendar Heatmap ─────────────────────────────────────────────────────────
function CalendarHeatmap({ data }) {
  const now = new Date()
  const cells = useMemo(() => {
    const map = {}
    data.forEach(s => {
      const d = new Date(s.created_at).toDateString()
      if (!map[d]) map[d] = []
      map[d].push(s.session_score ?? 0)
    })

    const result = []
    for (let i = 83; i >= 0; i--) {
      const d = new Date(now.getTime() - i * 86400e3)
      const key = d.toDateString()
      const scores = map[key] ?? []
      const avg = scores.length ? scores.reduce((a, b) => a + b, 0) / scores.length : null
      result.push({ date: d, avg, count: scores.length })
    }
    return result
  }, [data])

  const scoreToColor = (avg) => {
    if (avg === null) return 'bg-nc-border/40'
    if (avg >= 75) return 'bg-green-500'
    if (avg >= 55) return 'bg-nc-accent'
    if (avg >= 35) return 'bg-yellow-500'
    return 'bg-nc-danger'
  }

  return (
    <div className="card p-5 space-y-3">
      <div className="flex items-center gap-2">
        <CalendarDays className="w-4 h-4 text-nc-accent" />
        <h2 className="font-semibold text-nc-text text-sm">Calendrier des sessions (12 semaines)</h2>
      </div>
      <div className="overflow-x-auto -mx-1">
        <div className="grid gap-1 min-w-[360px] px-1" style={{ gridTemplateColumns: 'repeat(12, 1fr)' }}>
          {Array.from({ length: 12 }, (_, week) =>
            cells.slice(week * 7, week * 7 + 7).map((cell, day) => (
              <div
                key={`${week}-${day}`}
                title={cell.avg !== null
                  ? `${cell.date.toLocaleDateString()} — ${cell.count} session(s) — score moy. ${cell.avg.toFixed(0)}%`
                  : cell.date.toLocaleDateString()}
                className={`w-full aspect-square rounded-sm ${scoreToColor(cell.avg)} transition-opacity hover:opacity-80 cursor-default`}
              />
            ))
          )}
        </div>
      </div>
      <div className="flex items-center gap-3 text-[10px] text-nc-muted">
        <span>Moins</span>
        {['bg-nc-border/40','bg-nc-danger','bg-yellow-500','bg-nc-accent','bg-green-500'].map(c => (
          <span key={c} className={`w-3 h-3 rounded-sm ${c}`} />
        ))}
        <span>Plus</span>
      </div>
    </div>
  )
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
            {trend >= 0
              ? <TrendingUp className="w-3 h-3" />
              : <TrendingDown className="w-3 h-3" />}
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

// ── Simulation metric gauge ───────────────────────────────────────────────────
function SimMetric({ label, value, max = 1, unit = 'pct', color }) {
  const pct = Math.round(Math.min(100, (value / max) * 100))
  const display = unit === 'pct' ? `${Math.round(value * 100)}%` : value.toFixed(2)
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs">
        <span className="text-nc-muted">{label}</span>
        <span className="font-mono font-bold" style={{ color }}>{display}</span>
      </div>
      <div className="h-1.5 bg-nc-border rounded-full overflow-hidden">
        <div className="h-full rounded-full transition-all duration-500"
             style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  )
}

// ── Simulation scenarios ──────────────────────────────────────────────────────
const SIM_SCENARIOS = [
  { id: 'progressive',  label: 'Concentration progressive', desc: 'Montée lente vers la concentration' },
  { id: 'stress',       label: 'Stress croissant',          desc: 'TBR qui augmente avec le temps' },
  { id: 'recovery',     label: 'Récupération',              desc: 'Stress initial puis récupération' },
  { id: 'random',       label: 'Aléatoire',                 desc: 'Signal synthétique bruité' },
]

function SimLivePanel({ liveEEG, scenario, setScenario, onArtifact, artifactActive, t }) {
  const [scenarioOpen, setScenarioOpen] = useState(false)
  const current = SIM_SCENARIOS.find(s => s.id === scenario) ?? SIM_SCENARIOS[0]

  return (
    <div className="card overflow-hidden border border-nc-warning/30 animate-fade-in">
      {/* Header */}
      <div className="px-5 py-3 bg-nc-warning/10 border-b border-nc-warning/20 flex items-center gap-2 flex-wrap">
        <Cpu className="w-4 h-4 text-nc-warning" />
        <span className="text-sm font-semibold text-nc-warning">{t('simulation.live_panel')}</span>

        {/* Scenario picker */}
        <div className="relative ms-auto">
          <button
            onClick={() => setScenarioOpen(o => !o)}
            className="flex items-center gap-1.5 text-xs text-nc-muted bg-nc-surface border border-nc-border px-2.5 py-1.5 rounded-lg hover:text-nc-text transition-colors"
          >
            <span>{current.label}</span>
            <ChevronDown className="w-3 h-3" />
          </button>
          {scenarioOpen && (
            <div className="absolute top-full mt-1 end-0 z-20 bg-nc-surface border border-nc-border rounded-xl shadow-glass-lg min-w-[200px] animate-fade-in overflow-hidden">
              {SIM_SCENARIOS.map(s => (
                <button key={s.id}
                  onClick={() => { setScenario(s.id); setScenarioOpen(false) }}
                  className={`flex flex-col w-full text-start px-3 py-2.5 text-xs transition-colors
                              ${s.id === scenario ? 'bg-nc-accent/10 text-nc-accent' : 'text-nc-text hover:bg-nc-surface2'}`}>
                  <span className="font-medium">{s.label}</span>
                  <span className="text-nc-muted">{s.desc}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Artifact button */}
        <button
          onClick={onArtifact}
          className={`flex items-center gap-1.5 text-xs px-2.5 py-1.5 rounded-lg border transition-colors
                      ${artifactActive
                        ? 'bg-nc-danger/20 border-nc-danger/50 text-nc-danger'
                        : 'bg-nc-surface border-nc-border text-nc-muted hover:text-nc-text'}`}
        >
          <AlertTriangle className="w-3 h-3" />
          Artefact
        </button>

        <span className="flex items-center gap-1.5 text-xs text-nc-success font-medium ms-2">
          <span className="w-2 h-2 rounded-full bg-nc-success animate-pulse" />
          {artifactActive ? <span className="text-nc-danger">Artefact détecté</span> : t('simulation.signal_good')}
        </span>
      </div>

      {/* Brain + metrics */}
      <div className="grid md:grid-cols-2 gap-0">
        <div className="relative h-80 bg-nc-bg/40">
          <div className="absolute inset-0">
            <Brain3D
              concentration={artifactActive ? 0.1 : liveEEG.concentration}
              stress={artifactActive ? 0.9 : liveEEG.stress}
              className="w-full h-full"
            />
          </div>
          {artifactActive && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="px-4 py-2 bg-nc-danger/80 text-white text-xs font-bold rounded-xl animate-pulse">
                ARTEFACT — Signal dégradé
              </div>
            </div>
          )}
        </div>
        <div className="p-5 flex flex-col justify-center gap-5 border-t md:border-t-0 md:border-s border-nc-border/40">
          <SimMetric label={t('simulation.concentration')} value={artifactActive ? 0.05 : liveEEG.concentration} unit="pct" color="rgb(var(--nc-accent))" />
          <SimMetric label={t('simulation.stress')}        value={artifactActive ? 0.95 : liveEEG.stress}        unit="pct" color="rgb(var(--nc-danger))" />
          <SimMetric label={t('simulation.tbr')}           value={artifactActive ? 5.8 : liveEEG.tbr}  max={6}   unit="raw" color="rgb(var(--nc-warning))" />
          <SimMetric label={t('simulation.alpha')}         value={artifactActive ? 0.05 : liveEEG.alpha}          unit="pct" color="rgb(var(--nc-success))" />
          <div className="text-[10px] text-nc-muted border-t border-nc-border/40 pt-2">
            Scénario : <span className="font-semibold text-nc-text">{current.label}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function EmptyState({ t }) {
  const navigate = useNavigate()
  return (
    <div className="flex flex-col items-center justify-center py-24 gap-4 animate-fade-in">
      <div className="w-20 h-20 rounded-full flex items-center justify-center" style={{ background: 'rgb(var(--nc-accent)/0.1)' }}>
        <Activity className="w-10 h-10 text-nc-accent" />
      </div>
      <h3 className="text-xl font-semibold text-nc-text">{t('dashboard.no_sessions')}</h3>
      <p className="text-nc-muted text-sm">{t('dashboard.no_sessions_sub')}</p>
      <button className="btn-primary mt-2" onClick={() => navigate('/session/new')}>
        <Play className="w-4 h-4" />
        {t('dashboard.start_session')}
      </button>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function DashboardPage() {
  const { t }    = useTranslation()
  const { user } = useAuthStore()
  const navigate = useNavigate()

  const [sessionList, setSessionList] = useState([])
  const [loading,     setLoading]     = useState(true)
  const [eegProfile,  setEegProfile]  = useState(null)
  const [objFilter,   setObjFilter]   = useState('all')  // 'all' | 'concentration' | 'relaxation'

  const [simMode,        setSimMode]        = useState(false)
  const [simSessions,    setSimSessions]    = useState([])
  const [simScenario,    setSimScenario]    = useState('progressive')
  const [artifactActive, setArtifactActive] = useState(false)
  const [liveEEG, setLiveEEG] = useState({ concentration: 0.50, stress: 0.30, tbr: 3.20, alpha: 0.62 })

  useEffect(() => {
    sessionsApi.list()
      .then((d) => setSessionList(Array.isArray(d) ? d : []))
      .catch(() => setSessionList([]))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    profileApi.get().then(setEegProfile).catch(() => {})
  }, [])

  useEffect(() => {
    if (simMode) setSimSessions(generateSimSessions(10))
    else setSimSessions([])
  }, [simMode])

  useEffect(() => {
    if (!simMode) return
    const start = Date.now() / 1000
    const iv = setInterval(() => {
      const t   = Date.now() / 1000
      const age = t - start           // seconds elapsed in simulation
      const p   = Math.min(1, age / 120)  // progress 0→1 over 2 min

      let conc, stress, tbr, alpha
      switch (simScenario) {
        case 'stress':
          conc   = Math.max(0, Math.min(1, 0.40 - p * 0.25 + (Math.random() - 0.5) * 0.08))
          stress = Math.max(0, Math.min(1, 0.30 + p * 0.55 + (Math.random() - 0.5) * 0.07))
          tbr    = Math.max(1, 2.5 + p * 2.8 + (Math.random() - 0.5) * 0.3)
          alpha  = Math.max(0, Math.min(1, 0.65 - p * 0.35 + (Math.random() - 0.5) * 0.06))
          break
        case 'recovery':
          conc   = Math.max(0, Math.min(1, 0.25 + p * 0.55 + Math.sin(t * 0.3) * 0.1))
          stress = Math.max(0, Math.min(1, 0.70 - p * 0.50 + (Math.random() - 0.5) * 0.06))
          tbr    = Math.max(1, 4.5 - p * 2.5 + (Math.random() - 0.5) * 0.25)
          alpha  = Math.max(0, Math.min(1, 0.35 + p * 0.40 + (Math.random() - 0.5) * 0.07))
          break
        case 'random':
          conc   = Math.max(0, Math.min(1, 0.50 + Math.sin(t * 0.28) * 0.32 + (Math.random() - 0.5) * 0.14))
          stress = Math.max(0, Math.min(1, 0.30 + Math.sin(t * 0.19 + 1.2) * 0.22 + (Math.random() - 0.5) * 0.13))
          tbr    = Math.max(1, 3.2 + Math.sin(t * 0.14) * 1.4 + (Math.random() - 0.5) * 0.6)
          alpha  = Math.max(0, Math.min(1, 0.60 + Math.sin(t * 0.24 + 0.5) * 0.26 + (Math.random() - 0.5) * 0.12))
          break
        default: // progressive
          conc   = Math.max(0, Math.min(1, 0.28 + p * 0.58 + Math.sin(t * 0.22) * 0.08))
          stress = Math.max(0, Math.min(1, 0.45 - p * 0.28 + (Math.random() - 0.5) * 0.07))
          tbr    = Math.max(1, 4.0 - p * 2.0 + (Math.random() - 0.5) * 0.25)
          alpha  = Math.max(0, Math.min(1, 0.45 + p * 0.38 + (Math.random() - 0.5) * 0.07))
      }
      setLiveEEG({ concentration: conc, stress, tbr, alpha })
    }, 500)
    return () => clearInterval(iv)
  }, [simMode, simScenario])

  const activeData = simMode ? simSessions : sessionList

  // Filtered data for chart
  const filteredData = useMemo(() =>
    objFilter === 'all'
      ? activeData
      : activeData.filter(s => s.objective === objFilter),
    [activeData, objFilter]
  )

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

  if (!simMode && !sessionList.length) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex justify-end mb-4">
          <button className="btn-ghost text-sm flex items-center gap-2" onClick={() => setSimMode(true)}>
            <Cpu className="w-4 h-4" />
            {t('simulation.start')}
          </button>
        </div>
        <EmptyState t={t} />
      </div>
    )
  }

  // ── Stats ────────────────────────────────────────────────────────────────────
  const total      = activeData.length
  const avgScore   = (activeData.reduce((s, x) => s + (x.session_score ?? 0), 0) / Math.max(total, 1)).toFixed(1)
  const avgTBR     = (activeData.reduce((s, x) => s + (x.avg_tbr ?? 0), 0) / Math.max(total, 1)).toFixed(2)
  const scoreTrend = computeTrend(activeData, 'session_score')
  const tbrTrend   = computeTrend(activeData, 'avg_tbr')
  const nextScore  = predictNextScore(activeData)
  const badges     = computeBadges(activeData)

  const chartData  = filteredData.map((s, i) => ({
    name:          `S${i + 1}`,
    score:         s.session_score != null ? parseFloat(s.session_score.toFixed(1)) : null,
    tbr_scaled:    s.avg_tbr != null ? parseFloat((s.avg_tbr * 10).toFixed(1)) : null,
    objective:     s.objective,
  }))

  return (
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
        <div className="flex items-center gap-2 shrink-0 self-start sm:self-auto">
          {simMode ? (
            <button
              className="flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold
                         bg-nc-warning/15 border border-nc-warning/40 text-nc-warning hover:bg-nc-warning/25 transition-colors"
              onClick={() => setSimMode(false)}
            >
              <X className="w-4 h-4" />
              {t('simulation.stop')}
            </button>
          ) : (
            <button className="btn-ghost text-sm flex items-center gap-2" onClick={() => setSimMode(true)}>
              <Cpu className="w-4 h-4" />
              {t('simulation.start')}
            </button>
          )}
          {!simMode && (
            <button className="btn-primary" onClick={() => navigate('/session/new')}>
              <Play className="w-4 h-4" />
              {t('dashboard.start_session')}
            </button>
          )}
        </div>
      </div>

      {/* ── Simulation banner ── */}
      {simMode && (
        <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-nc-warning/10 border border-nc-warning/30 animate-fade-in">
          <WifiOff className="w-4 h-4 text-nc-warning shrink-0" />
          <p className="text-sm font-semibold text-nc-warning">{t('simulation.banner')}</p>
          <span className="ms-auto text-xs text-nc-muted">{t('simulation.banner_sub')}</span>
        </div>
      )}

      {/* ── Sim live panel ── */}
      {simMode && (
        <SimLivePanel
          liveEEG={liveEEG}
          scenario={simScenario}
          setScenario={setSimScenario}
          onArtifact={() => {
            setArtifactActive(true)
            setTimeout(() => setArtifactActive(false), 2500)
          }}
          artifactActive={artifactActive}
          t={t}
        />
      )}

      {/* ── Stats row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Award}      label={t('dashboard.stats.total_sessions')} value={total}            color="nc-accent"  />
        <StatCard icon={Target}     label={t('dashboard.stats.avg_score')}      value={`${avgScore}%`}   color="nc-success"  trend={scoreTrend} />
        <StatCard icon={ChartBar}   label={t('dashboard.stats.avg_tbr')}        value={avgTBR}            color="nc-warning"  trend={tbrTrend !== null ? -tbrTrend : null} />
        <StatCard icon={TrendingUp} label="Prochain score estimé"               value={nextScore ? `~${nextScore}%` : '—'}  color="nc-accent" />
      </div>

      {/* ── Badges ── */}
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

      {/* ── Main grid: chart + recommendation ── */}
      <div className="grid lg:grid-cols-3 gap-6">

        {/* Score line chart (2/3) */}
        <div className="lg:col-span-2 card p-6 space-y-4">
          <div className="flex items-center gap-2 flex-wrap">
            <TrendingUp className="w-4 h-4 text-nc-accent" />
            <h2 className="font-semibold text-nc-text">{t('dashboard.sections.score_history')}</h2>
            <span className="ms-auto badge-muted">{filteredData.length} sessions</span>

            {/* Objective filter */}
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
            <LineChart data={chartData} margin={{ top: 4, right: 8, bottom: 0, left: -20 }}>
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
              <Line
                type="monotone" dataKey="score" name="Score (%)"
                stroke="rgb(var(--nc-accent))" strokeWidth={2.5}
                dot={{ fill: 'rgb(var(--nc-accent))', r: 4 }}
                activeDot={{ r: 6 }}
                connectNulls
              />
              <Line
                type="monotone" dataKey="tbr_scaled" name="TBR ×10"
                stroke="rgb(var(--nc-warning))" strokeWidth={1.5} strokeDasharray="4 2"
                dot={false} connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Recommendation (1/3) */}
        <RecommendationEngine sessions={activeData} eegProfile={eegProfile} />
      </div>

      {/* ── Calendar heatmap ── */}
      <CalendarHeatmap data={activeData} />

      {/* ── Session history table ── */}
      <div className="card overflow-hidden">
        <div className="px-6 py-4 border-b border-nc-border flex items-center gap-2">
          <CalendarDays className="w-4 h-4 text-nc-accent" />
          <h2 className="font-semibold text-nc-text">{t('dashboard.sections.session_history')}</h2>
          {simMode && (
            <span className="ms-auto text-xs font-semibold text-nc-warning bg-nc-warning/10 px-2 py-0.5 rounded-full border border-nc-warning/30">
              {t('simulation.title')}
            </span>
          )}
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
              {activeData.map((s, i) => {
                const prev = activeData[i - 1]
                const scoreDelta = prev ? (s.session_score ?? 0) - (prev.session_score ?? 0) : null
                return (
                  <tr
                    key={s.id ?? i}
                    className="border-b border-nc-border/50 hover:bg-nc-surface2 transition-colors cursor-pointer"
                    onClick={() => !simMode && navigate(`/session/${s.id}`)}
                  >
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
    </div>
  )
}
