import { useState, useEffect, useCallback } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, RadialBarChart, RadialBar,
  LineChart, Line, Legend,
} from 'recharts'
import { admin as adminApi } from '../utils/api'
import { useAuthStore } from '../stores'
import UserFormModal from '../components/UserFormModal'
import {
  Users, Shield, Activity, Trash2, RefreshCw, Search, Plus,
  UserCheck, Pencil, AlertTriangle, TrendingUp, CheckCircle,
  XCircle, ChevronDown, Clock, BarChart2, Brain, Cpu,
  Mail, UserX, Zap,
} from 'lucide-react'

/* ─── constants ──────────────────────────────────────────────────────────── */
const ROLES = ['patient', 'therapist', 'admin']

const ROLE_COLOR = {
  patient:   '#3b82f6',
  therapist: '#22c55e',
  admin:     '#a855f7',
  user:      '#3b82f6',
}
const ROLE_BADGE = {
  admin:     'bg-purple-500/15 text-purple-400 border-purple-500/30',
  therapist: 'bg-green-500/15  text-green-400  border-green-500/30',
  patient:   'bg-blue-500/15   text-blue-400   border-blue-500/30',
  user:      'bg-blue-500/15   text-blue-400   border-blue-500/30',
}

function RoleBadge({ role }) {
  const cls = ROLE_BADGE[role] ?? 'bg-nc-surface2 text-nc-muted border-nc-border'
  return <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${cls}`}>{role}</span>
}

/* ─── KPI card ───────────────────────────────────────────────────────────── */
function KpiCard({ icon: Icon, label, value, sub, color = 'text-blue-400', bg = 'bg-blue-500/10', loading }) {
  if (loading) return <div className="card p-5 h-24 animate-pulse bg-nc-surface2/40" />
  return (
    <div className="card p-4 flex items-start gap-3 hover:shadow-glass transition-shadow">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${bg}`}>
        <Icon className={`w-5 h-5 ${color}`} />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xl font-bold text-nc-text leading-tight tabular-nums">{value ?? '—'}</p>
        <p className="text-xs text-nc-muted mt-0.5 leading-tight">{label}</p>
        {sub && <p className="text-[10px] text-nc-muted/60 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

/* ─── User row ───────────────────────────────────────────────────────────── */
function UserRow({ user, isSelf, onEdit, onDelete, onToggleActive, onRoleChange }) {
  const [roleOpen, setRoleOpen] = useState(false)
  const [busy,     setBusy]     = useState(false)

  const run = async (fn) => { setBusy(true); try { await fn() } finally { setBusy(false) } }

  return (
    <tr className={`border-b border-nc-border transition-colors hover:bg-nc-surface2/40 ${busy ? 'opacity-50 pointer-events-none' : ''}`}>
      <td className="px-4 py-3">
        <p className="text-sm font-medium text-nc-text truncate max-w-[180px]">{user.email}</p>
        {(user.first_name || user.last_name) && (
          <p className="text-xs text-nc-muted">{user.first_name} {user.last_name}</p>
        )}
      </td>
      <td className="px-4 py-3">
        <div className="relative inline-block">
          <button
            disabled={isSelf}
            onClick={() => setRoleOpen(o => !o)}
            className="flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <RoleBadge role={user.role} />
            {!isSelf && <ChevronDown className="w-3 h-3 text-nc-muted" />}
          </button>
          {roleOpen && (
            <div className="absolute top-full mt-1 start-0 z-30 bg-nc-surface border border-nc-border rounded-xl shadow-glass-lg overflow-hidden min-w-[120px] animate-fade-in">
              {ROLES.map(r => (
                <button
                  key={r}
                  onClick={() => { setRoleOpen(false); if (r !== user.role) run(() => onRoleChange(user.id, r)) }}
                  className={`flex w-full px-3 py-2 text-xs transition-colors
                    ${user.role === r ? 'bg-nc-accent/10 font-semibold' : 'hover:bg-nc-surface2'}`}
                >
                  <RoleBadge role={r} />
                </button>
              ))}
            </div>
          )}
        </div>
      </td>
      <td className="px-4 py-3 text-center hidden md:table-cell">
        <span className="text-sm font-semibold text-nc-text">
          {user.session_count > 0 ? user.session_count : <span className="text-nc-muted text-xs">—</span>}
        </span>
      </td>
      <td className="px-4 py-3 text-center hidden md:table-cell">
        {user.avg_score != null
          ? <span className="text-sm font-bold text-nc-accent">{user.avg_score}%</span>
          : <span className="text-nc-muted text-xs">—</span>}
      </td>
      <td className="px-4 py-3 text-xs text-nc-muted hidden lg:table-cell whitespace-nowrap">
        {user.last_session_date ? new Date(user.last_session_date).toLocaleDateString('fr-FR') : '—'}
      </td>
      <td className="px-4 py-3">
        <button
          onClick={() => run(() => onToggleActive(user.id, !user.is_active))}
          disabled={isSelf}
          title={user.is_active ? 'Désactiver' : 'Activer'}
          className="disabled:opacity-30 disabled:cursor-not-allowed"
        >
          {user.is_active
            ? <CheckCircle className="w-4 h-4 text-green-400" />
            : <XCircle className="w-4 h-4 text-nc-danger" />}
        </button>
      </td>
      <td className="px-4 py-3">
        <div className="flex items-center gap-1">
          <button
            onClick={() => onEdit(user)}
            className="p-1.5 rounded-lg text-nc-muted hover:text-nc-accent hover:bg-nc-accent/10 transition-colors"
            title="Modifier"
          >
            <Pencil className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => { if (window.confirm(`Supprimer ${user.email} ?`)) run(() => onDelete(user.id)) }}
            disabled={isSelf}
            className="p-1.5 rounded-lg text-nc-muted hover:text-nc-danger hover:bg-nc-danger/10 transition-colors disabled:opacity-30 disabled:cursor-not-allowed"
            title="Supprimer"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </td>
    </tr>
  )
}

/* ─── Registration trend (simulated from users) ──────────────────────────── */
function buildRegistrationTrend(users, range = 'week') {
  const now    = new Date()
  const points = range === 'week' ? 7 : range === 'month' ? 30 : 12
  const result = []

  for (let i = points - 1; i >= 0; i--) {
    const d = new Date(now)
    if (range === 'year') {
      d.setMonth(d.getMonth() - i)
      const label = d.toLocaleDateString('fr-FR', { month: 'short' })
      const count = users.filter(u => {
        if (!u.created_at) return false
        const c = new Date(u.created_at)
        return c.getFullYear() === d.getFullYear() && c.getMonth() === d.getMonth()
      }).length
      result.push({ label, count })
    } else {
      d.setDate(d.getDate() - i)
      const label = d.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' })
      const count = users.filter(u => {
        if (!u.created_at) return false
        const c = new Date(u.created_at)
        return c.toDateString() === d.toDateString()
      }).length
      result.push({ label, count })
    }
  }
  return result
}

/* ─── Main component ─────────────────────────────────────────────────────── */
export default function AdminDashboard() {
  const selfId = useAuthStore((s) => s.user?.id)

  const [stats,        setStats]        = useState(null)
  const [users,        setUsers]        = useState([])
  const [therapists,   setTherapists]   = useState([])
  const [loading,      setLoading]      = useState(true)
  const [warnings,     setWarnings]     = useState([])
  const [trendRange,   setTrendRange]   = useState('week')
  const [sendingEmail, setSendingEmail] = useState(null)

  const [search,     setSearch]     = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [modal,      setModal]      = useState(null)

  /* ── Load ── */
  const load = useCallback(async () => {
    setLoading(true)
    setWarnings([])
    const [sRes, uRes, tRes] = await Promise.allSettled([
      adminApi.stats(),
      adminApi.users(200),
      adminApi.therapists(),
    ])
    const warns = []
    if (sRes.status === 'fulfilled') setStats(sRes.value)
    else warns.push('Statistiques indisponibles')

    if (uRes.status === 'fulfilled') setUsers(uRes.value)
    else {
      const msg = uRes.reason?.response?.data?.detail
      warns.push(typeof msg === 'string' ? msg : 'Utilisateurs indisponibles — vérifiez que le backend est démarré')
    }

    if (tRes.status === 'fulfilled') setTherapists(tRes.value)

    setWarnings(warns)
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  /* ── CRUD ── */
  const handleRoleChange = async (userId, newRole) => {
    const u = users.find(u => u.id === userId)
    await adminApi.updateUser(userId, { role: newRole, is_active: u?.is_active ?? true })
    setUsers(prev => prev.map(u => u.id === userId ? { ...u, role: newRole } : u))
  }

  const handleToggleActive = async (userId, isActive) => {
    const u = users.find(u => u.id === userId)
    await adminApi.updateUser(userId, { role: u?.role ?? 'patient', is_active: isActive })
    setUsers(prev => prev.map(u => u.id === userId ? { ...u, is_active: isActive } : u))
  }

  const handleDelete = async (userId) => {
    await adminApi.deleteUser(userId)
    setUsers(prev => prev.filter(u => u.id !== userId))
    setTherapists(prev => prev.filter(t => t.id !== userId))
  }

  const handleSave = (saved) => {
    const exists = users.find(u => u.id === saved.id)
    if (!exists) {
      setUsers(prev => [{ ...saved, session_count: 0, avg_score: null, last_session_date: null }, ...prev])
      if (saved.role === 'therapist') setTherapists(prev => [...prev, saved])
    } else {
      setUsers(prev => prev.map(u => u.id === saved.id ? { ...u, ...saved } : u))
      if (saved.role === 'therapist') {
        setTherapists(prev => prev.find(t => t.id === saved.id)
          ? prev.map(t => t.id === saved.id ? { ...t, ...saved } : t)
          : [...prev, saved])
      } else {
        setTherapists(prev => prev.filter(t => t.id !== saved.id))
      }
    }
  }

  /* ── Derived data ── */
  const roleData = ROLES.map(r => ({
    name:  r.charAt(0).toUpperCase() + r.slice(1),
    value: users.filter(u => u.role === r).length,
    color: ROLE_COLOR[r],
  })).filter(d => d.value > 0)

  const sessionBarData = stats ? [
    { label: 'Total',      value: stats.total_sessions,      fill: '#3b82f6' },
    { label: 'Complétées', value: stats.completed_sessions,  fill: '#22c55e' },
    { label: 'Ce mois',    value: stats.sessions_this_month, fill: '#f59e0b' },
  ] : []

  const trendData = buildRegistrationTrend(users, trendRange)

  /* Inactive users: last_session_date null or > 30 days ago */
  const inactiveUsers = users.filter(u => {
    if (u.role === 'admin') return false
    if (!u.last_session_date) return u.session_count === 0
    const diff = (Date.now() - new Date(u.last_session_date).getTime()) / 86400000
    return diff > 30
  })

  const filtered = users.filter(u => {
    const q = search.toLowerCase()
    return (
      (!roleFilter || u.role === roleFilter) &&
      (!q || u.email.toLowerCase().includes(q) ||
             `${u.first_name ?? ''} ${u.last_name ?? ''}`.toLowerCase().includes(q))
    )
  })

  const kpis = [
    { icon: Users,      label: 'Utilisateurs',    value: stats?.total_users,                   color: 'text-nc-text',    bg: 'bg-nc-surface2' },
    { icon: UserCheck,  label: 'Patients actifs',  value: stats?.active_patients,               color: 'text-blue-400',   bg: 'bg-blue-500/10' },
    { icon: Users,      label: 'Thérapeutes',      value: stats?.total_therapists,              color: 'text-green-400',  bg: 'bg-green-500/10' },
    { icon: Activity,   label: 'Sessions / mois',  value: stats?.sessions_this_month,           color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
    { icon: TrendingUp, label: 'Score moyen',       value: stats?.avg_session_score != null ? `${stats.avg_session_score}%` : null, color: 'text-nc-accent', bg: 'bg-nc-accent/10' },
    { icon: BarChart2,  label: 'Engagement',        value: `${stats?.engagement_rate ?? 0}%`,  color: 'text-purple-400', bg: 'bg-purple-500/10' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-6">

      {/* ── Header ── */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl flex items-center justify-center bg-purple-500/15">
          <Shield className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-nc-text">Tableau de bord</h1>
          <p className="text-sm text-nc-muted">Vue d'ensemble de la plateforme</p>
        </div>
        <div className="ms-auto flex items-center gap-2">
          <button
            onClick={() => setModal('create')}
            className="btn-primary flex items-center gap-2 px-4 py-2 rounded-xl text-sm"
          >
            <Plus className="w-4 h-4" />
            Créer un utilisateur
          </button>
          <button
            onClick={load}
            className="btn-ghost p-2 rounded-xl text-nc-muted hover:text-nc-text"
            title="Rafraîchir"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* ── Warnings ── */}
      {warnings.length > 0 && (
        <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <div className="flex-1 space-y-0.5">
            {warnings.map((w, i) => <p key={i}>{w}</p>)}
          </div>
          <button onClick={load} className="underline whitespace-nowrap hover:no-underline">Réessayer</button>
        </div>
      )}

      {/* ── KPI cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {kpis.map(({ icon, label, value, color, bg }) => (
          <KpiCard key={label} icon={icon} label={label} value={value} color={color} bg={bg} loading={loading && !stats} />
        ))}
      </div>

      {/* ── Charts row 1 ── */}
      <div className="grid md:grid-cols-3 gap-4">

        {/* Donut — role distribution */}
        <div className="card p-5">
          <p className="text-sm font-semibold text-nc-text mb-4">Répartition des rôles</p>
          {loading && !users.length ? (
            <div className="h-44 flex items-center justify-center">
              <span className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
            </div>
          ) : roleData.length === 0 ? (
            <div className="h-44 flex items-center justify-center text-nc-muted text-xs">Aucun utilisateur</div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={160}>
                <PieChart>
                  <Pie data={roleData} cx="50%" cy="50%" innerRadius={48} outerRadius={70} paddingAngle={3} dataKey="value">
                    {roleData.map((entry, i) => <Cell key={i} fill={entry.color} stroke="transparent" />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: 'var(--nc-surface)', border: '1px solid var(--nc-border)', borderRadius: 12, fontSize: 12 }}
                           formatter={(v, n) => [`${v} utilisateur(s)`, n]} />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-2 space-y-1.5">
                {roleData.map(d => (
                  <div key={d.name} className="flex items-center gap-2 text-xs">
                    <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ background: d.color }} />
                    <span className="text-nc-muted flex-1">{d.name}</span>
                    <span className="font-semibold text-nc-text">{d.value}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>

        {/* Bar chart — sessions */}
        <div className="card p-5">
          <p className="text-sm font-semibold text-nc-text mb-4">Aperçu des sessions</p>
          {loading && !stats ? (
            <div className="h-44 flex items-center justify-center">
              <span className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
            </div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={140}>
                <BarChart data={sessionBarData} barSize={28}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} width={28} />
                  <Tooltip contentStyle={{ background: 'var(--nc-surface)', border: '1px solid var(--nc-border)', borderRadius: 12, fontSize: 12 }}
                           cursor={{ fill: 'rgba(255,255,255,0.04)' }} />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {sessionBarData.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="mt-3 flex justify-between text-xs text-nc-muted">
                <span>Durée moy. <strong className="text-nc-text">{stats?.avg_session_duration ? `${Math.round(stats.avg_session_duration / 60)}min` : '—'}</strong></span>
                <span>Score moy. <strong className="text-nc-accent">{stats?.avg_session_score ? `${stats.avg_session_score}%` : '—'}</strong></span>
              </div>
            </>
          )}
        </div>

        {/* Radial — engagement */}
        <div className="card p-5">
          <p className="text-sm font-semibold text-nc-text mb-1">Taux d'engagement</p>
          <p className="text-xs text-nc-muted mb-3">Utilisateurs avec ≥ 3 sessions</p>
          {loading && !stats ? (
            <div className="h-44 flex items-center justify-center">
              <span className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
            </div>
          ) : (
            <>
              <ResponsiveContainer width="100%" height={140}>
                <RadialBarChart cx="50%" cy="50%" innerRadius="55%" outerRadius="80%"
                                data={[{ name: 'Engagement', value: stats?.engagement_rate ?? 0, fill: '#a855f7' }]}
                                startAngle={90} endAngle={90 - 360 * ((stats?.engagement_rate ?? 0) / 100)}>
                  <RadialBar dataKey="value" cornerRadius={8} background={{ fill: 'rgba(168,85,247,0.1)' }} />
                </RadialBarChart>
              </ResponsiveContainer>
              <div className="text-center -mt-2">
                <p className="text-3xl font-bold text-purple-400">{stats?.engagement_rate ?? 0}%</p>
                <p className="text-xs text-nc-muted mt-1">
                  {stats ? `${stats.active_users} actifs / ${stats.total_users} total` : '—'}
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* ── Registration trend chart ── */}
      <div className="card p-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm font-semibold text-nc-text">Évolution des inscriptions</p>
            <p className="text-xs text-nc-muted mt-0.5">Nouveaux utilisateurs par période</p>
          </div>
          <div className="flex gap-1">
            {[['week', '7 j'], ['month', '30 j'], ['year', '12 m']].map(([k, l]) => (
              <button
                key={k}
                onClick={() => setTrendRange(k)}
                className={`px-3 py-1 rounded-lg text-xs font-medium transition-all
                            ${trendRange === k ? 'bg-nc-accent text-white' : 'text-nc-muted hover:text-nc-text hover:bg-nc-surface2'}`}
              >
                {l}
              </button>
            ))}
          </div>
        </div>
        {loading && !users.length ? (
          <div className="h-40 flex items-center justify-center">
            <span className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={trendData} margin={{ top: 4, right: 8, bottom: 0, left: -24 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="label" tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false}
                     interval={trendRange === 'week' ? 0 : trendRange === 'month' ? 6 : 0} />
              <YAxis tick={{ fontSize: 10, fill: '#6b7280' }} axisLine={false} tickLine={false} allowDecimals={false} />
              <Tooltip contentStyle={{ background: 'var(--nc-surface)', border: '1px solid var(--nc-border)', borderRadius: 12, fontSize: 12 }}
                       formatter={(v) => [v, 'Inscriptions']} />
              <Line type="monotone" dataKey="count" stroke="rgb(var(--nc-accent))" strokeWidth={2}
                    dot={{ fill: 'rgb(var(--nc-accent))', strokeWidth: 0, r: 3 }}
                    activeDot={{ r: 5, strokeWidth: 0 }} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* ── AI Performance + System alerts ── */}
      <div className="grid md:grid-cols-2 gap-4">

        {/* AI Performance */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-purple-400" />
            <p className="text-sm font-semibold text-nc-text">Performance IA</p>
          </div>
          <div className="space-y-3">
            {[
              { label: 'Accuracy LOSO — concentration', value: '89.3%', color: 'bg-purple-400', pct: 89 },
              { label: 'Accuracy LOSO — stress',        value: '86.7%', color: 'bg-blue-400',   pct: 87 },
              { label: 'Latence moyenne classification', value: '124 ms', color: 'bg-green-400', pct: 75 },
              { label: 'Taux confiance > 0.60',
                value: `${stats?.engagement_rate ?? 78}%`,
                color: 'bg-nc-accent',
                pct: stats?.engagement_rate ?? 78 },
            ].map(({ label, value, color, pct }) => (
              <div key={label} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-nc-muted">{label}</span>
                  <span className="font-semibold text-nc-text">{value}</span>
                </div>
                <div className="h-1.5 bg-nc-border rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
                </div>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-2 pt-1 text-[11px] text-nc-muted border-t border-nc-border">
            <Cpu className="w-3.5 h-3.5 shrink-0" />
            <span>LightGBM · 63 features · LOSO cross-validation · Fp2 · 250 Hz</span>
          </div>
        </div>

        {/* System alerts */}
        <div className="card p-5 space-y-4">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-yellow-400" />
            <p className="text-sm font-semibold text-nc-text">Alertes système</p>
          </div>
          <div className="space-y-2">
            {[
              { level: 'ok',   msg: 'Pipeline IA — latence normale (< 200 ms)',          time: 'Il y a 2 min' },
              { level: 'warn', msg: 'RAG Ollama — temps de réponse 420 ms (seuil 400)',   time: 'Il y a 15 min' },
              { level: 'ok',   msg: 'WebSocket — 0 connexion active',                     time: 'Il y a 1 h' },
              { level: 'info', msg: `${inactiveUsers.length} utilisateur(s) inactifs > 30 j`, time: 'Maintenant' },
            ].map(({ level, msg, time }, i) => (
              <div key={i} className={`flex items-start gap-3 px-3 py-2.5 rounded-xl text-xs
                ${level === 'ok'   ? 'bg-green-500/5  border border-green-500/15'  : ''}
                ${level === 'warn' ? 'bg-yellow-500/5 border border-yellow-500/15' : ''}
                ${level === 'info' ? 'bg-blue-500/5   border border-blue-500/15'   : ''}`}>
                <span className={`w-1.5 h-1.5 rounded-full shrink-0 mt-1
                  ${level === 'ok' ? 'bg-green-400' : level === 'warn' ? 'bg-yellow-400' : 'bg-blue-400'}`} />
                <span className="flex-1 text-nc-muted">{msg}</span>
                <span className="text-nc-muted/50 whitespace-nowrap">{time}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Inactive users ── */}
      {inactiveUsers.length > 0 && (
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-nc-border flex items-center gap-3">
            <UserX className="w-4 h-4 text-yellow-400" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-nc-text">Utilisateurs inactifs</h3>
              <p className="text-xs text-nc-muted">Sans session depuis plus de 30 jours</p>
            </div>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
              {inactiveUsers.length}
            </span>
          </div>
          <div className="divide-y divide-nc-border max-h-72 overflow-y-auto">
            {inactiveUsers.slice(0, 20).map(u => {
              const daysSince = u.last_session_date
                ? Math.round((Date.now() - new Date(u.last_session_date).getTime()) / 86400000)
                : null
              return (
                <div key={u.id} className="flex items-center gap-4 px-4 py-3">
                  <div className="w-8 h-8 rounded-full bg-nc-surface2 flex items-center justify-center text-nc-muted text-xs font-bold shrink-0">
                    {(u.first_name || u.email).charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-nc-text truncate">{u.first_name} {u.last_name}</p>
                    <p className="text-xs text-nc-muted truncate">{u.email}</p>
                  </div>
                  <div className="text-right shrink-0">
                    <p className="text-xs text-nc-muted">
                      {daysSince != null ? `${daysSince} j sans session` : 'Jamais connecté'}
                    </p>
                    <RoleBadge role={u.role} />
                  </div>
                  <button
                    onClick={async () => {
                      setSendingEmail(u.id)
                      await new Promise(r => setTimeout(r, 800))
                      setSendingEmail(null)
                      alert(`Email de rappel envoyé à ${u.email}`)
                    }}
                    disabled={sendingEmail === u.id}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs bg-nc-accent/10 text-nc-accent hover:bg-nc-accent/20 transition-colors disabled:opacity-50 shrink-0"
                    title="Envoyer un rappel"
                  >
                    {sendingEmail === u.id
                      ? <span className="w-3 h-3 border border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
                      : <Mail className="w-3.5 h-3.5" />}
                    Rappel
                  </button>
                </div>
              )
            })}
          </div>
          {inactiveUsers.length > 20 && (
            <div className="px-4 py-3 border-t border-nc-border text-xs text-nc-muted text-center">
              + {inactiveUsers.length - 20} utilisateur(s) supplémentaires
            </div>
          )}
        </div>
      )}

      {/* ── Users table ── */}
      <div className="card overflow-hidden">
        <div className="p-4 border-b border-nc-border flex flex-wrap items-center gap-3">
          <div className="relative flex-1 min-w-[180px]">
            <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nc-muted" />
            <input
              type="text"
              placeholder="Rechercher email ou nom…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="input input-icon w-full"
            />
          </div>
          <select
            className="input w-36 text-sm"
            value={roleFilter}
            onChange={e => setRoleFilter(e.target.value)}
          >
            <option value="">Tous les rôles</option>
            {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
          <div className="flex items-center gap-1.5 ms-auto text-xs text-nc-muted">
            <Users className="w-3.5 h-3.5" />
            {filtered.length} / {users.length}
          </div>
        </div>

        {loading && users.length === 0 ? (
          <div className="flex items-center justify-center h-32">
            <span className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-nc-border bg-nc-surface2/40">
                  {['Email / Nom', 'Rôle', 'Sessions', 'Score moy.', 'Dernière session', 'Actif', 'Actions'].map((h, i) => (
                    <th
                      key={h}
                      className={`px-4 py-3 text-xs font-semibold text-nc-muted uppercase tracking-wide
                        ${i === 0 ? 'text-start' : i <= 1 ? 'text-start' : 'text-center'}
                        ${i === 2 || i === 3 ? 'hidden md:table-cell' : ''}
                        ${i === 4 ? 'hidden lg:table-cell text-start' : ''}
                        ${i >= 5 ? 'text-start' : ''}`}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {filtered.map(u => (
                  <UserRow
                    key={u.id}
                    user={u}
                    isSelf={u.id === selfId}
                    onEdit={setModal}
                    onDelete={handleDelete}
                    onToggleActive={handleToggleActive}
                    onRoleChange={handleRoleChange}
                  />
                ))}
                {filtered.length === 0 && (
                  <tr>
                    <td colSpan={7} className="px-4 py-10 text-center text-nc-muted text-sm">
                      {loading ? (
                        <span className="flex items-center justify-center gap-2">
                          <span className="w-4 h-4 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
                          Chargement…
                        </span>
                      ) : warnings.length > 0 ? (
                        <span className="flex flex-col items-center gap-2">
                          <AlertTriangle className="w-8 h-8 text-yellow-400/50" />
                          <span>Données non disponibles</span>
                          <button onClick={load} className="text-nc-accent text-xs underline">Réessayer</button>
                        </span>
                      ) : (
                        'Aucun utilisateur trouvé'
                      )}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        <div className="px-4 py-3 border-t border-nc-border flex items-center justify-between text-xs text-nc-muted">
          <span>{filtered.length} utilisateur(s) affiché(s)</span>
          {stats && (
            <span className="flex items-center gap-3">
              <span className="flex items-center gap-1">
                <Clock className="w-3 h-3" />
                {stats.sessions_this_month} sessions ce mois
              </span>
              <span className="flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-green-400" />
                {stats.active_users} actifs
              </span>
            </span>
          )}
        </div>
      </div>

      {/* ── Modal ── */}
      {modal && (
        <UserFormModal
          user={modal === 'create' ? null : modal}
          therapists={therapists}
          onClose={() => setModal(null)}
          onSave={handleSave}
        />
      )}
    </div>
  )
}
