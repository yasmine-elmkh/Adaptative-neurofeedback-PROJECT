import { useState, useEffect, useCallback } from 'react'
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, RadialBarChart, RadialBar,
} from 'recharts'
import { admin as adminApi } from '../utils/api'
import { useAuthStore } from '../stores'
import UserFormModal from '../components/UserFormModal'
import {
  Users, Shield, Activity, Trash2, RefreshCw, Search, Plus,
  UserCheck, Pencil, AlertTriangle, TrendingUp, CheckCircle,
  XCircle, ChevronDown, Clock, BarChart2,
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

/* ─── Custom donut label ─────────────────────────────────────────────────── */
function DonutLabel({ cx, cy, total }) {
  return (
    <text x={cx} y={cy} textAnchor="middle" dominantBaseline="central">
      <tspan x={cx} dy="-0.4em" className="text-2xl font-bold" style={{ fill: 'currentColor', fontSize: 22, fontWeight: 700 }}>
        {total}
      </tspan>
      <tspan x={cx} dy="1.4em" style={{ fill: '#6b7280', fontSize: 11 }}>
        utilisateurs
      </tspan>
    </text>
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

/* ─── Main component ─────────────────────────────────────────────────────── */
export default function AdminDashboard() {
  const selfId = useAuthStore((s) => s.user?.id)

  const [stats,      setStats]      = useState(null)
  const [users,      setUsers]      = useState([])
  const [therapists, setTherapists] = useState([])
  const [loading,    setLoading]    = useState(true)
  const [warnings,   setWarnings]   = useState([])

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

  /* ── Derived data for charts ── */
  const roleData = ROLES.map(r => ({
    name: r.charAt(0).toUpperCase() + r.slice(1),
    value: users.filter(u => u.role === r).length,
    color: ROLE_COLOR[r],
  })).filter(d => d.value > 0)

  const sessionBarData = stats ? [
    { label: 'Total',      value: stats.total_sessions,       fill: '#3b82f6' },
    { label: 'Complétées', value: stats.completed_sessions,   fill: '#22c55e' },
    { label: 'Ce mois',    value: stats.sessions_this_month,  fill: '#f59e0b' },
  ] : []

  const engagementData = stats ? [
    { name: 'Engagement', value: stats.engagement_rate, fill: '#a855f7' },
  ] : []

  const filtered = users.filter(u => {
    const q = search.toLowerCase()
    return (
      (!roleFilter || u.role === roleFilter) &&
      (!q || u.email.toLowerCase().includes(q) ||
             `${u.first_name ?? ''} ${u.last_name ?? ''}`.toLowerCase().includes(q))
    )
  })

  const kpis = [
    { icon: Users,       label: 'Utilisateurs',     value: stats?.total_users,         color: 'text-nc-text',     bg: 'bg-nc-surface2' },
    { icon: UserCheck,   label: 'Patients actifs',  value: stats?.active_patients,      color: 'text-blue-400',    bg: 'bg-blue-500/10' },
    { icon: Users,       label: 'Thérapeutes',      value: stats?.total_therapists,     color: 'text-green-400',   bg: 'bg-green-500/10' },
    { icon: Activity,    label: 'Sessions / mois',  value: stats?.sessions_this_month,  color: 'text-yellow-400',  bg: 'bg-yellow-500/10' },
    { icon: TrendingUp,  label: 'Score moyen',      value: stats?.avg_session_score != null ? `${stats.avg_session_score}%` : null, color: 'text-nc-accent', bg: 'bg-nc-accent/10' },
    { icon: BarChart2,   label: 'Engagement',       value: `${stats?.engagement_rate ?? 0}%`, color: 'text-purple-400',  bg: 'bg-purple-500/10' },
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

      {/* ── Warnings (non-blocking) ── */}
      {warnings.length > 0 && (
        <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 text-xs">
          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <div className="flex-1 space-y-0.5">
            {warnings.map((w, i) => <p key={i}>{w}</p>)}
          </div>
          <button onClick={load} className="underline whitespace-nowrap hover:no-underline">Réessayer</button>
        </div>
      )}

      {/* ── 6 KPI cards ── */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {kpis.map(({ icon, label, value, color, bg }) => (
          <KpiCard key={label} icon={icon} label={label} value={value} color={color} bg={bg} loading={loading && !stats} />
        ))}
      </div>

      {/* ── Charts row ── */}
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
                  <Pie
                    data={roleData}
                    cx="50%"
                    cy="50%"
                    innerRadius={48}
                    outerRadius={70}
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {roleData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} stroke="transparent" />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ background: 'var(--nc-surface)', border: '1px solid var(--nc-border)', borderRadius: 12, fontSize: 12 }}
                    formatter={(v, n) => [`${v} utilisateur(s)`, n]}
                  />
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
                  <Tooltip
                    contentStyle={{ background: 'var(--nc-surface)', border: '1px solid var(--nc-border)', borderRadius: 12, fontSize: 12 }}
                    cursor={{ fill: 'rgba(255,255,255,0.04)' }}
                  />
                  <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                    {sessionBarData.map((entry, i) => (
                      <Cell key={i} fill={entry.fill} />
                    ))}
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
                <RadialBarChart
                  cx="50%"
                  cy="50%"
                  innerRadius="55%"
                  outerRadius="80%"
                  data={[{ name: 'Engagement', value: stats?.engagement_rate ?? 0, fill: '#a855f7' }]}
                  startAngle={90}
                  endAngle={90 - 360 * ((stats?.engagement_rate ?? 0) / 100)}
                >
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

      {/* ── Users table ── */}
      <div className="card overflow-hidden">
        {/* Toolbar */}
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

        {/* Footer */}
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
