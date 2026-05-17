import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { therapist as therapistApi } from '../utils/api'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell,
  PieChart, Pie, Legend,
} from 'recharts'
import {
  Users, TrendingUp, TrendingDown, Minus, ChevronRight,
  Calendar, AlertTriangle, RefreshCw, Activity, Star,
  UserCheck, BarChart2, Target, Search, Eye,
} from 'lucide-react'

/* ── constants ───────────────────────────────────────────────────────────── */
const PALIER = {
  P1_INITIATION:    { label: 'P1', color: '#3b82f6', cls: 'bg-blue-500/15 text-blue-400'   },
  P2_APPRENTISSAGE: { label: 'P2', color: '#22c55e', cls: 'bg-green-500/15 text-green-400' },
  P3_MAITRISE:      { label: 'P3', color: '#f97316', cls: 'bg-orange-500/15 text-orange-400' },
  P4_AUTONOMIE:     { label: 'P4', color: '#ef4444', cls: 'bg-red-500/15 text-red-400'     },
  P1: { label: 'P1', color: '#3b82f6', cls: 'bg-blue-500/15 text-blue-400'    },
  P2: { label: 'P2', color: '#22c55e', cls: 'bg-green-500/15 text-green-400'  },
  P3: { label: 'P3', color: '#f97316', cls: 'bg-orange-500/15 text-orange-400'},
  P4: { label: 'P4', color: '#ef4444', cls: 'bg-red-500/15 text-red-400'      },
}
const PALIER_FILTER_OPTIONS = [
  { value: '',               label: 'Tous les paliers' },
  { value: 'P1_INITIATION',    label: 'P1 – Initiation'    },
  { value: 'P2_APPRENTISSAGE', label: 'P2 – Apprentissage' },
  { value: 'P3_MAITRISE',      label: 'P3 – Maîtrise'      },
  { value: 'P4_AUTONOMIE',     label: 'P4 – Autonomie'     },
]

/* ── SVG circle progress ─────────────────────────────────────────────────── */
function CircleProgress({ value = 0, max = 100, size = 80, stroke = 8, color = 'rgb(var(--nc-accent))', label }) {
  const r   = (size - stroke) / 2
  const circ = 2 * Math.PI * r
  const offset = circ - (Math.min(value, max) / max) * circ
  const pct = Math.round((value / max) * 100)
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none"
                stroke="rgb(var(--nc-border))" strokeWidth={stroke} />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none"
                stroke={color} strokeWidth={stroke}
                strokeDasharray={circ} strokeDashoffset={offset}
                strokeLinecap="round"
                style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
      </svg>
      <span className="absolute text-sm font-bold text-nc-text">{label ?? `${pct}%`}</span>
    </div>
  )
}

/* ── KPI cards ────────────────────────────────────────────────────────────── */
function KpiSimple({ icon: Icon, label, value, color = 'text-nc-accent', bg = 'bg-nc-accent/10', sub }) {
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 ${bg}`}>
        <Icon className={`w-6 h-6 ${color}`} />
      </div>
      <div>
        <p className="text-2xl font-bold text-nc-text leading-none">{value ?? '—'}</p>
        <p className="text-xs text-nc-muted mt-1">{label}</p>
        {sub && <p className="text-[10px] text-nc-muted/70 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

function KpiCircle({ label, value, color, bg }) {
  return (
    <div className="card p-5 flex items-center gap-4">
      <CircleProgress value={value ?? 0} size={76} stroke={7} color={color} />
      <div>
        <p className="text-2xl font-bold text-nc-text leading-none">{value !== null && value !== undefined ? `${value}%` : '—'}</p>
        <p className="text-xs text-nc-muted mt-1">{label}</p>
      </div>
    </div>
  )
}

function KpiTrend({ label, value, bg = 'bg-nc-surface2', icon: Icon }) {
  const positive = value > 0
  const neutral  = value === 0 || value === null || value === undefined
  const color    = neutral ? 'text-nc-muted' : positive ? 'text-green-400' : 'text-nc-danger'
  const bgIcon   = neutral ? 'bg-nc-surface2' : positive ? 'bg-green-500/10' : 'bg-nc-danger/10'
  const TrendIcon = neutral ? Minus : positive ? TrendingUp : TrendingDown
  return (
    <div className="card p-5 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-2xl flex items-center justify-center shrink-0 ${bgIcon}`}>
        <TrendIcon className={`w-6 h-6 ${color}`} />
      </div>
      <div>
        <p className={`text-2xl font-bold leading-none ${color}`}>
          {value !== null && value !== undefined
            ? `${value > 0 ? '+' : ''}${value}%`
            : '—'}
        </p>
        <p className="text-xs text-nc-muted mt-1">{label}</p>
      </div>
    </div>
  )
}

function KpiEngagement({ value }) {
  const pct = value ?? 0
  return (
    <div className="card p-5 flex items-center gap-4">
      <CircleProgress value={pct} size={76} stroke={7} color="#60a5fa" />
      <div className="flex-1 min-w-0">
        <p className="text-2xl font-bold text-nc-text leading-none">{pct}%</p>
        <p className="text-xs text-nc-muted mt-1">Engagement / semaine</p>
        <div className="mt-2 h-1.5 bg-nc-border rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-blue-400 transition-all duration-700"
               style={{ width: `${pct}%` }} />
        </div>
      </div>
    </div>
  )
}

/* ── Palier pie chart ─────────────────────────────────────────────────────── */
function PalierPie({ patients }) {
  const counts = {}
  patients.forEach(p => {
    const key = p.palier ?? 'Non défini'
    counts[key] = (counts[key] ?? 0) + 1
  })
  const data = Object.entries(counts).map(([key, count]) => ({
    name: PALIER[key]?.label ?? key,
    value: count,
    color: PALIER[key]?.color ?? '#6b7280',
  }))
  if (!data.length) return (
    <div className="flex items-center justify-center h-40 text-nc-muted text-sm">Aucune donnée</div>
  )
  return (
    <ResponsiveContainer width="100%" height={200}>
      <PieChart>
        <Pie data={data} cx="50%" cy="50%" innerRadius={50} outerRadius={80}
             paddingAngle={3} dataKey="value">
          {data.map((entry, i) => <Cell key={i} fill={entry.color} />)}
        </Pie>
        <Tooltip
          formatter={(v, n) => [`${v} patient(s)`, n]}
          contentStyle={{ background: 'rgb(var(--nc-surface))', border: '1px solid rgb(var(--nc-border))', borderRadius: 10, fontSize: 12 }}
        />
        <Legend
          formatter={(v) => <span style={{ fontSize: 11, color: 'rgb(var(--nc-muted))' }}>{v}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  )
}

/* ── Score bar chart ─────────────────────────────────────────────────────── */
function ScoreBarChart({ patients }) {
  const data = patients
    .filter(p => p.avg_score_all !== null && p.avg_score_all !== undefined)
    .sort((a, b) => (b.avg_score_all ?? 0) - (a.avg_score_all ?? 0))
    .slice(0, 8)
    .map(p => ({
      name: p.first_name ? `${p.first_name.charAt(0)}. ${p.last_name ?? ''}`.trim() : p.email.split('@')[0],
      score: p.avg_score_all,
      palier: p.palier,
    }))

  if (!data.length) return (
    <div className="flex items-center justify-center h-40 text-nc-muted text-sm">Aucune donnée</div>
  )

  return (
    <ResponsiveContainer width="100%" height={200}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -24, bottom: 0 }}>
        <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'rgb(var(--nc-muted))' }} axisLine={false} tickLine={false} />
        <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: 'rgb(var(--nc-muted))' }} axisLine={false} tickLine={false} />
        <Tooltip
          formatter={(v) => [`${v}%`, 'Score moyen']}
          contentStyle={{ background: 'rgb(var(--nc-surface))', border: '1px solid rgb(var(--nc-border))', borderRadius: 10, fontSize: 12 }}
        />
        <Bar dataKey="score" radius={[4, 4, 0, 0]}>
          {data.map((d, i) => (
            <Cell key={i} fill={PALIER[d.palier]?.color ?? 'rgb(var(--nc-accent))'} opacity={0.85} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

/* ── Alerts block ─────────────────────────────────────────────────────────── */
function AlertsBlock({ inactive, stagnant, uncalibrated }) {
  const navigate = useNavigate()
  const all = [
    ...inactive.map(p => ({ ...p, _type: 'inactive', _label: `Inactif depuis ${p._days}j` })),
    ...stagnant.filter(p => !inactive.find(a => a.id === p.id)).map(p => ({ ...p, _type: 'stagnant', _label: 'Stagnation du score' })),
    ...uncalibrated.filter(p => !inactive.find(a => a.id === p.id) && !stagnant.find(a => a.id === p.id)).map(p => ({ ...p, _type: 'uncal', _label: 'Profil EEG manquant' })),
  ]

  const dotColor = { inactive: 'bg-nc-danger', stagnant: 'bg-yellow-400', uncal: 'bg-nc-muted' }

  if (!all.length) return (
    <div className="card p-6 text-center">
      <UserCheck className="w-8 h-8 mx-auto mb-2 text-green-400 opacity-70" />
      <p className="text-sm font-medium text-nc-text">Tous les patients sont actifs</p>
      <p className="text-xs text-nc-muted mt-1">Aucune alerte en ce moment</p>
    </div>
  )

  return (
    <div className="card overflow-hidden">
      <div className="flex items-center gap-2 px-4 py-3 border-b border-nc-border bg-yellow-500/5">
        <AlertTriangle className="w-4 h-4 text-yellow-400 shrink-0" />
        <p className="text-sm font-semibold text-nc-text">Nécessitent attention</p>
        <span className="ms-auto text-xs font-bold text-yellow-400">{all.length}</span>
      </div>
      <div className="divide-y divide-nc-border/40">
        {all.map(p => {
          const name = p.first_name && p.last_name ? `${p.first_name} ${p.last_name}` : p.email
          return (
            <div key={p.id + p._type} className="flex items-center gap-3 px-4 py-3 hover:bg-nc-surface2 transition-colors">
              <span className={`w-2 h-2 rounded-full shrink-0 ${dotColor[p._type]}`} />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-nc-text truncate">{name}</p>
                <p className="text-[10px] text-nc-muted">{p._label}</p>
              </div>
              <button
                onClick={() => navigate(`/therapist/patient/${p.id}`)}
                className="shrink-0 p-1.5 rounded-lg text-nc-muted hover:text-nc-accent hover:bg-nc-accent/10 transition-colors"
                title="Voir le patient"
              >
                <Eye className="w-3.5 h-3.5" />
              </button>
            </div>
          )
        })}
      </div>
    </div>
  )
}

/* ── Patient table ────────────────────────────────────────────────────────── */
function PatientTable({ patients }) {
  const navigate = useNavigate()
  const [search,      setSearch]      = useState('')
  const [palierFilter, setPalierFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  const filtered = patients.filter(p => {
    const nameMatch = `${p.first_name ?? ''} ${p.last_name ?? ''} ${p.email}`
      .toLowerCase().includes(search.toLowerCase())
    const palierMatch = !palierFilter || p.palier === palierFilter
    const statusMatch = !statusFilter
      || (statusFilter === 'active'   &&  p.is_active)
      || (statusFilter === 'inactive' && !p.is_active)
    return nameMatch && palierMatch && statusMatch
  })

  return (
    <div className="card overflow-hidden">
      {/* Toolbar */}
      <div className="flex flex-wrap gap-2 p-4 border-b border-nc-border bg-nc-surface2/30">
        <div className="relative flex-1 min-w-[160px]">
          <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-nc-muted" />
          <input
            type="text"
            placeholder="Rechercher…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="input w-full ps-8 py-1.5 text-sm"
          />
        </div>
        <select
          value={palierFilter}
          onChange={e => setPalierFilter(e.target.value)}
          className="input py-1.5 text-sm shrink-0"
        >
          {PALIER_FILTER_OPTIONS.map(o => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="input py-1.5 text-sm shrink-0"
        >
          <option value="">Tous les statuts</option>
          <option value="active">Actifs</option>
          <option value="inactive">Inactifs</option>
        </select>
        <span className="text-xs text-nc-muted self-center shrink-0">{filtered.length} résultat(s)</span>
      </div>

      {/* Table */}
      {filtered.length === 0 ? (
        <div className="py-12 text-center text-nc-muted text-sm">Aucun résultat</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-nc-border bg-nc-surface2/50">
                {['Patient','Dernière session','Score moy.','Tendance','Évolution','Palier',''].map(h => (
                  <th key={h} className="px-4 py-3 text-start text-xs font-semibold text-nc-muted uppercase tracking-wide whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map(p => {
                const name = p.first_name && p.last_name ? `${p.first_name} ${p.last_name}` : p.email
                const initials = p.first_name && p.last_name
                  ? `${p.first_name[0]}${p.last_name[0]}`.toUpperCase()
                  : p.email[0].toUpperCase()
                const palierCfg = PALIER[p.palier]
                const lastDateStr = p.last_session_date
                  ? new Date(p.last_session_date).toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' })
                  : null
                const evo = p.evolution_pct
                const trend = p.score_trend

                return (
                  <tr
                    key={p.id}
                    onClick={() => navigate(`/therapist/patient/${p.id}`)}
                    className="border-b border-nc-border hover:bg-nc-surface2/60 cursor-pointer transition-colors group"
                  >
                    {/* Patient */}
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className={`relative w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shrink-0 ${!p.is_active ? 'opacity-50' : ''}`}
                             style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.5))' }}>
                          {initials}
                          <span className={`absolute -bottom-0.5 -end-0.5 w-2.5 h-2.5 rounded-full border-2 border-nc-surface ${p.is_active ? 'bg-green-400' : 'bg-nc-muted'}`} />
                        </div>
                        <div className="min-w-0">
                          <p className="font-medium text-nc-text truncate group-hover:text-nc-accent transition-colors max-w-[130px]">{name}</p>
                          <p className="text-[10px] text-nc-muted truncate max-w-[130px]">{p.email}</p>
                        </div>
                      </div>
                    </td>

                    {/* Dernière session */}
                    <td className="px-4 py-3 whitespace-nowrap">
                      {lastDateStr ? (
                        <div>
                          <span className="text-nc-text">{lastDateStr}</span>
                          {p.last_session_score !== null && p.last_session_score !== undefined && (
                            <span className="ms-1 text-nc-accent font-semibold">{p.last_session_score}%</span>
                          )}
                        </div>
                      ) : <span className="text-nc-muted">—</span>}
                    </td>

                    {/* Score moyen */}
                    <td className="px-4 py-3">
                      {p.avg_score_all !== null && p.avg_score_all !== undefined ? (
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-nc-accent">{p.avg_score_all}%</span>
                          <div className="w-12 h-1.5 bg-nc-border rounded-full overflow-hidden">
                            <div className="h-full rounded-full"
                                 style={{ width: `${p.avg_score_all}%`, background: palierCfg?.color ?? 'rgb(var(--nc-accent))' }} />
                          </div>
                        </div>
                      ) : <span className="text-nc-muted">—</span>}
                    </td>

                    {/* Tendance (last sessions) */}
                    <td className="px-4 py-3">
                      {trend !== null && trend !== undefined ? (
                        <span className={`flex items-center gap-0.5 text-xs font-semibold whitespace-nowrap
                          ${trend > 0 ? 'text-green-400' : trend < 0 ? 'text-nc-danger' : 'text-nc-muted'}`}>
                          {trend > 0 ? <TrendingUp className="w-3 h-3" /> : trend < 0 ? <TrendingDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                          {trend > 0 ? `+${trend}` : trend}%
                        </span>
                      ) : <Minus className="w-3.5 h-3.5 text-nc-muted" />}
                    </td>

                    {/* Évolution (first vs last) */}
                    <td className="px-4 py-3">
                      {evo !== null && evo !== undefined ? (
                        <span className={`text-xs font-semibold ${evo > 0 ? 'text-green-400' : evo < 0 ? 'text-nc-danger' : 'text-nc-muted'}`}>
                          {evo > 0 ? '+' : ''}{evo}%
                        </span>
                      ) : <span className="text-nc-muted">—</span>}
                    </td>

                    {/* Palier */}
                    <td className="px-4 py-3">
                      {palierCfg ? (
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${palierCfg.cls}`}>
                          {palierCfg.label}
                        </span>
                      ) : <span className="text-nc-muted text-xs">—</span>}
                    </td>

                    {/* Action */}
                    <td className="px-4 py-3">
                      <button
                        onClick={e => { e.stopPropagation(); navigate(`/therapist/patient/${p.id}`) }}
                        className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-medium text-nc-muted hover:text-nc-accent hover:bg-nc-accent/10 border border-nc-border group-hover:border-nc-accent/30 transition-all whitespace-nowrap"
                      >
                        <Eye className="w-3 h-3" />
                        Voir
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

/* ── Main dashboard ───────────────────────────────────────────────────────── */
export default function TherapistDashboard() {
  const [patients, setPatients] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await therapistApi.patients()
      setPatients(data)
    } catch {
      setError('Impossible de charger les patients. Vérifiez que le backend est démarré.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  /* ── Derived stats ── */
  const now         = Date.now()
  const activeCount = patients.filter(p => p.is_active).length
  const totalSessions = patients.reduce((acc, p) => acc + (p.session_count ?? 0), 0)

  const allScores   = patients.flatMap(p => p.avg_score_all !== null && p.avg_score_all !== undefined ? [p.avg_score_all] : [])
  const avgScore    = allScores.length ? Math.round(allScores.reduce((a, b) => a + b, 0) / allScores.length) : null

  const evoValues   = patients.flatMap(p => p.evolution_pct !== null && p.evolution_pct !== undefined ? [p.evolution_pct] : [])
  const avgImprovement = evoValues.length
    ? Math.round(evoValues.reduce((a, b) => a + b, 0) / evoValues.length * 10) / 10
    : null

  const engagedThisWeek = patients.filter(p => {
    if (!p.last_session_date) return false
    return (now - new Date(p.last_session_date).getTime()) / 86400000 <= 7
  }).length
  const engagementRate = patients.length ? Math.round((engagedThisWeek / patients.length) * 100) : 0

  /* ── Alerts ── */
  const alertInactive = patients.filter(p => {
    const days = p.last_session_date
      ? Math.floor((now - new Date(p.last_session_date).getTime()) / 86400000)
      : 999
    p._days = days
    return days >= 7
  })
  const alertStagnant   = patients.filter(p => p.score_trend !== null && p.score_trend !== undefined && Math.abs(p.score_trend) < 2 && p.session_count >= 3)
  const alertUncalibrated = patients.filter(p => !p.profile_type && !p.palier)

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">

      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-nc-text">Tableau de bord thérapeute</h1>
          <p className="text-sm text-nc-muted mt-0.5">
            {patients.length} patient(s) assigné(s) · dernière mise à jour {new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
        <button
          onClick={load}
          className="btn-ghost p-2 rounded-xl text-nc-muted hover:text-nc-text"
          title="Rafraîchir"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {/* ── Error ── */}
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm">
          <AlertTriangle className="w-4 h-4 shrink-0" />{error}
          <button onClick={load} className="ms-auto underline text-xs">Réessayer</button>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <span className="w-10 h-10 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {/* ── KPI row ── */}
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-3">
            <KpiSimple
              icon={Users} label="Patients suivis"
              value={patients.length} sub={`${activeCount} actifs`}
              color="text-nc-accent" bg="bg-nc-accent/10"
            />
            <KpiSimple
              icon={Calendar} label="Sessions totales"
              value={totalSessions}
              color="text-blue-400" bg="bg-blue-500/10"
            />
            <KpiCircle
              label="Score moyen global"
              value={avgScore}
              color="rgb(var(--nc-accent))"
            />
            <KpiEngagement value={engagementRate} />
            <KpiTrend
              label="Amélioration moyenne"
              value={avgImprovement}
            />
          </div>

          {/* ── Charts row ── */}
          {patients.length > 0 && (
            <div className="grid lg:grid-cols-2 gap-4">
              {/* Score per patient */}
              <div className="card p-5 space-y-3">
                <div className="flex items-center gap-2">
                  <BarChart2 className="w-4 h-4 text-nc-accent" />
                  <h3 className="text-sm font-semibold text-nc-text">Score moyen par patient</h3>
                  <span className="ms-auto text-[10px] text-nc-muted">coloré par palier</span>
                </div>
                <ScoreBarChart patients={patients} />
                {/* Legend */}
                <div className="flex flex-wrap gap-3 pt-1">
                  {Object.entries({ P1_INITIATION: 'P1', P2_APPRENTISSAGE: 'P2', P3_MAITRISE: 'P3', P4_AUTONOMIE: 'P4' }).map(([key, lbl]) => (
                    <span key={key} className="flex items-center gap-1.5 text-[10px] text-nc-muted">
                      <span className="w-2.5 h-2.5 rounded-sm inline-block" style={{ background: PALIER[key]?.color }} />
                      {lbl}
                    </span>
                  ))}
                </div>
              </div>

              {/* Palier distribution */}
              <div className="card p-5 space-y-3">
                <div className="flex items-center gap-2">
                  <Target className="w-4 h-4 text-nc-accent" />
                  <h3 className="text-sm font-semibold text-nc-text">Répartition par palier</h3>
                </div>
                <PalierPie patients={patients} />
                {/* Summary chips */}
                <div className="flex flex-wrap gap-2 pt-1 justify-center">
                  {['P1_INITIATION','P2_APPRENTISSAGE','P3_MAITRISE','P4_AUTONOMIE'].map(key => {
                    const count = patients.filter(p => p.palier === key).length
                    if (!count) return null
                    const cfg = PALIER[key]
                    return (
                      <span key={key} className={`px-2.5 py-1 rounded-full text-xs font-semibold ${cfg.cls}`}>
                        {cfg.label}: {count}
                      </span>
                    )
                  })}
                  {patients.filter(p => !p.palier).length > 0 && (
                    <span className="px-2.5 py-1 rounded-full text-xs font-semibold bg-nc-surface2 text-nc-muted">
                      Non défini: {patients.filter(p => !p.palier).length}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ── Main content: table + alerts ── */}
          {patients.length === 0 ? (
            <div className="card p-16 text-center">
              <Users className="w-14 h-14 mx-auto mb-4 opacity-20 text-nc-muted" />
              <p className="text-nc-text font-semibold text-lg">Aucun patient assigné</p>
              <p className="text-sm text-nc-muted mt-2">Un administrateur peut vous assigner des patients via le panneau d'administration.</p>
            </div>
          ) : (
            <div className="grid lg:grid-cols-[1fr_280px] gap-4 items-start">

              {/* Patient table */}
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-nc-accent" />
                  <h2 className="text-sm font-semibold text-nc-text">Liste des patients</h2>
                </div>
                <PatientTable patients={patients} />
              </div>

              {/* Alerts sidebar */}
              <div className="space-y-3 lg:sticky lg:top-24">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="w-4 h-4 text-yellow-400" />
                  <h2 className="text-sm font-semibold text-nc-text">Alertes</h2>
                  {(alertInactive.length + alertStagnant.length + alertUncalibrated.length) > 0 && (
                    <span className="ms-auto text-xs font-bold px-1.5 py-0.5 rounded-full bg-yellow-500/15 text-yellow-400">
                      {alertInactive.length + alertStagnant.length + alertUncalibrated.length}
                    </span>
                  )}
                </div>
                <AlertsBlock
                  inactive={alertInactive}
                  stagnant={alertStagnant}
                  uncalibrated={alertUncalibrated}
                />

                {/* Quick stats in sidebar */}
                {patients.length > 0 && (
                  <div className="card p-4 space-y-3">
                    <p className="text-xs font-semibold text-nc-muted uppercase tracking-wider">Résumé rapide</p>
                    {[
                      { label: 'Patients actifs cette semaine', value: `${engagedThisWeek} / ${patients.length}` },
                      { label: 'Sans profil EEG', value: alertUncalibrated.length },
                      { label: 'En progression', value: patients.filter(p => (p.score_trend ?? 0) > 0).length },
                      { label: 'En régression', value: patients.filter(p => (p.score_trend ?? 0) < -2).length },
                    ].map(({ label, value }) => (
                      <div key={label} className="flex items-center justify-between text-xs">
                        <span className="text-nc-muted">{label}</span>
                        <span className="font-semibold text-nc-text">{value}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}
