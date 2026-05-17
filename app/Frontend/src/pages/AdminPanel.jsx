import { useState, useEffect, useCallback } from 'react'
import { admin as adminApi } from '../utils/api'
import {
  Shield, RefreshCw, AlertTriangle, Settings,
  UserCheck, ClipboardList, Search, Save,
} from 'lucide-react'

/* ─── constants ─────────────────────────────────────────────────────────── */
const LOG_BADGE = (action) => {
  if (!action)                              return 'bg-nc-surface2 text-nc-muted border-nc-border'
  if (action === 'LOGIN')                   return 'bg-green-500/10 text-green-400 border-green-500/20'
  if (action === 'USER_DELETED')            return 'bg-nc-danger/10 text-nc-danger border-nc-danger/20'
  if (action === 'ROLE_CHANGE')             return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
  if (action === 'CALIBRATION')             return 'bg-purple-500/10 text-purple-400 border-purple-500/20'
  if (action.startsWith('DATA_EXPORT'))     return 'bg-nc-accent/10 text-nc-accent border-nc-accent/20'
  if (action === 'SESSION_CREATE')          return 'bg-green-500/10 text-green-400 border-green-500/20'
  if (action.startsWith('ASSISTANT_FEEDBACK')) return 'bg-orange-500/10 text-orange-400 border-orange-500/20'
  if (action === 'SETTINGS_CHANGED')        return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
  if (action === 'PATIENT_ASSIGNED')        return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
  if (action === 'USER_CREATED')            return 'bg-green-500/10 text-green-400 border-green-500/20'
  return 'bg-nc-surface2 text-nc-muted border-nc-border'
}

/* ── Assign Tab ── */
function AssignTab({ users }) {
  const [search, setSearch] = useState('')
  const [selectedTherapist, setSelectedTherapist] = useState(null)
  const [assignLoading, setAssignLoading] = useState(null)
  const [localUsers, setLocalUsers] = useState(users)

  useEffect(() => { setLocalUsers(users) }, [users])

  const therapists = localUsers.filter(u => u.role === 'therapist' || u.role === 'admin')
  const unassigned = localUsers.filter(u =>
    (u.role === 'patient' || u.role === 'user') &&
    !u.therapist_id &&
    (search === '' || u.email.toLowerCase().includes(search.toLowerCase()))
  )
  const assignedToSelected = selectedTherapist
    ? localUsers.filter(u => u.therapist_id === selectedTherapist.id)
    : []

  const assign = async (patientId, therapistId) => {
    setAssignLoading(patientId)
    try {
      await adminApi.assignPatient(patientId, therapistId)
      setLocalUsers(prev => prev.map(u => u.id === patientId ? { ...u, therapist_id: therapistId } : u))
    } finally { setAssignLoading(null) }
  }

  const unassign = async (patientId) => {
    setAssignLoading(patientId)
    try {
      await adminApi.assignPatient(patientId, null)
      setLocalUsers(prev => prev.map(u => u.id === patientId ? { ...u, therapist_id: null } : u))
    } finally { setAssignLoading(null) }
  }

  return (
    <div className="grid md:grid-cols-2 gap-4">
      {/* Therapists list */}
      <div className="card overflow-hidden">
        <div className="p-4 border-b border-nc-border">
          <h3 className="font-semibold text-nc-text text-sm">Thérapeutes</h3>
        </div>
        <div className="divide-y divide-nc-border">
          {therapists.map(t => {
            const count = localUsers.filter(u => u.therapist_id === t.id).length
            return (
              <button
                key={t.id}
                onClick={() => setSelectedTherapist(selectedTherapist?.id === t.id ? null : t)}
                className={`w-full flex items-center gap-3 px-4 py-3 text-start transition-colors
                            ${selectedTherapist?.id === t.id ? 'bg-nc-accent/10' : 'hover:bg-nc-surface2'}`}
              >
                <div className="w-8 h-8 rounded-full flex items-center justify-center bg-green-500/15 text-green-400 text-xs font-bold shrink-0">
                  {(t.first_name || t.email).charAt(0).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-nc-text truncate">{t.first_name} {t.last_name}</p>
                  <p className="text-xs text-nc-muted truncate">{t.email}</p>
                </div>
                <span className="text-xs text-nc-muted shrink-0">{count} patient(s)</span>
              </button>
            )
          })}
          {therapists.length === 0 && (
            <p className="px-4 py-6 text-sm text-nc-muted text-center">Aucun thérapeute</p>
          )}
        </div>
      </div>

      {/* Right panel */}
      <div className="space-y-4">
        {/* Assigned patients */}
        {selectedTherapist && (
          <div className="card overflow-hidden">
            <div className="p-4 border-b border-nc-border">
              <h3 className="font-semibold text-nc-text text-sm">
                Patients de {selectedTherapist.first_name || selectedTherapist.email}
              </h3>
            </div>
            <div className="divide-y divide-nc-border max-h-56 overflow-y-auto">
              {assignedToSelected.map(p => (
                <div key={p.id} className="flex items-center gap-3 px-4 py-2.5">
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-nc-text truncate">{p.first_name} {p.last_name}</p>
                    <p className="text-xs text-nc-muted truncate">{p.email}</p>
                  </div>
                  <button
                    onClick={() => unassign(p.id)}
                    disabled={assignLoading === p.id}
                    className="text-xs text-nc-danger hover:underline disabled:opacity-50"
                  >
                    Retirer
                  </button>
                </div>
              ))}
              {assignedToSelected.length === 0 && (
                <p className="px-4 py-4 text-xs text-nc-muted text-center">Aucun patient assigné</p>
              )}
            </div>
          </div>
        )}

        {/* Unassigned patients */}
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-nc-border flex items-center gap-3">
            <h3 className="font-semibold text-nc-text text-sm flex-1">Patients non assignés</h3>
            <div className="relative">
              <Search className="absolute start-2 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-nc-muted" />
              <input
                className="input py-1 ps-7 pe-2 text-xs w-44"
                placeholder="Rechercher…"
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
          </div>
          <div className="divide-y divide-nc-border max-h-64 overflow-y-auto">
            {unassigned.map(p => (
              <div key={p.id} className="flex items-center gap-3 px-4 py-2.5">
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-nc-text truncate">{p.first_name} {p.last_name}</p>
                  <p className="text-xs text-nc-muted truncate">{p.email}</p>
                </div>
                {selectedTherapist ? (
                  <button
                    onClick={() => assign(p.id, selectedTherapist.id)}
                    disabled={assignLoading === p.id}
                    className="text-xs text-nc-accent hover:underline disabled:opacity-50"
                  >
                    Assigner
                  </button>
                ) : (
                  <span className="text-xs text-nc-muted italic">Sélectionner un thérapeute</span>
                )}
              </div>
            ))}
            {unassigned.length === 0 && (
              <p className="px-4 py-4 text-xs text-nc-muted text-center">Aucun patient non assigné</p>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

/* ── Settings Tab ── */
function SettingsTab() {
  const [settings, setSettings] = useState([])
  const [loading, setLoading]   = useState(true)
  const [saving, setSaving]     = useState(null)
  const [drafts, setDrafts]     = useState({})
  const [error, setError]       = useState('')

  useEffect(() => {
    adminApi.getSettings()
      .then(data => {
        setSettings(data)
        const d = {}
        data.forEach(s => { d[s.key] = s.value })
        setDrafts(d)
      })
      .catch(() => setError('Impossible de charger les paramètres'))
      .finally(() => setLoading(false))
  }, [])

  const save = async (key) => {
    setSaving(key)
    try {
      const updated = await adminApi.updateSetting(key, drafts[key])
      setSettings(prev => prev.map(s => s.key === key ? updated : s))
    } catch {
      setError('Erreur lors de la sauvegarde')
    } finally { setSaving(null) }
  }

  if (loading) return (
    <div className="flex justify-center py-16">
      <span className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="space-y-3">
      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm">
          <AlertTriangle className="w-4 h-4 shrink-0" />{error}
        </div>
      )}
      <div className="card divide-y divide-nc-border overflow-hidden">
        {settings.map(s => (
          <div key={s.key} className="flex flex-wrap items-start gap-3 px-4 py-4">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-mono font-semibold text-nc-text">{s.key}</p>
              {s.description && <p className="text-xs text-nc-muted mt-0.5">{s.description}</p>}
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <input
                className="input w-28 text-sm py-1.5 text-center font-mono"
                value={drafts[s.key] ?? ''}
                onChange={e => setDrafts(d => ({ ...d, [s.key]: e.target.value }))}
              />
              <button
                onClick={() => save(s.key)}
                disabled={saving === s.key || drafts[s.key] === s.value}
                className="btn-primary flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs disabled:opacity-50"
              >
                {saving === s.key
                  ? <span className="w-3.5 h-3.5 border border-white/30 border-t-white rounded-full animate-spin" />
                  : <Save className="w-3.5 h-3.5" />}
                Sauver
              </button>
            </div>
          </div>
        ))}
        {settings.length === 0 && (
          <p className="px-4 py-8 text-sm text-nc-muted text-center">Aucun paramètre trouvé</p>
        )}
      </div>
    </div>
  )
}

/* ── Audit Tab ── */
function AuditTab() {
  const [logs, setLogs]             = useState([])
  const [loading, setLoading]       = useState(false)
  const [actionFilter, setActionFilter] = useState('')
  const [userFilter, setUserFilter] = useState('')
  const [dateFrom, setDateFrom]     = useState('')
  const [dateTo, setDateTo]         = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await adminApi.auditLogs(200, actionFilter || null, userFilter || null, dateFrom || null, dateTo || null)
      setLogs(data)
    } catch {
      setLogs([])
    } finally { setLoading(false) }
  }, [actionFilter, userFilter, dateFrom, dateTo])

  useEffect(() => { load() }, [load])

  const KNOWN_ACTIONS = [
    'LOGIN', 'USER_CREATED', 'USER_DELETED', 'ROLE_CHANGE', 'CALIBRATION',
    'SESSION_CREATE', 'DATA_EXPORT', 'DATA_EXPORT_ALL', 'SETTINGS_CHANGED',
    'PATIENT_ASSIGNED', 'ASSISTANT_FEEDBACK_UP', 'ASSISTANT_FEEDBACK_DOWN',
  ]

  return (
    <div className="space-y-4">
      <div className="card p-4 flex flex-wrap gap-3">
        <select className="input w-52 text-sm" value={actionFilter} onChange={e => setActionFilter(e.target.value)}>
          <option value="">Toutes les actions</option>
          {KNOWN_ACTIONS.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <input
          className="input w-64 text-sm"
          placeholder="User ID (UUID)"
          value={userFilter}
          onChange={e => setUserFilter(e.target.value)}
        />
        <div className="flex items-center gap-2">
          <input type="date" className="input text-sm" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
          <span className="text-nc-muted text-xs">→</span>
          <input type="date" className="input text-sm" value={dateTo} onChange={e => setDateTo(e.target.value)} />
        </div>
        <button onClick={load} className="btn-ghost p-2 rounded-xl text-nc-muted hover:text-nc-text" title="Actualiser">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      <div className="card overflow-hidden">
        {loading ? (
          <div className="flex justify-center py-16">
            <span className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-nc-border bg-nc-surface2/50">
                  <th className="px-4 py-3 text-start text-xs font-semibold text-nc-muted uppercase tracking-wide">Action</th>
                  <th className="px-4 py-3 text-start text-xs font-semibold text-nc-muted uppercase tracking-wide hidden md:table-cell">Détails</th>
                  <th className="px-4 py-3 text-start text-xs font-semibold text-nc-muted uppercase tracking-wide hidden lg:table-cell">IP</th>
                  <th className="px-4 py-3 text-start text-xs font-semibold text-nc-muted uppercase tracking-wide">Date</th>
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id} className="border-b border-nc-border hover:bg-nc-surface2/50">
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${LOG_BADGE(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-nc-muted hidden md:table-cell max-w-xs truncate">
                      {log.details || '—'}
                    </td>
                    <td className="px-4 py-3 text-xs text-nc-muted hidden lg:table-cell">{log.ip_address || '—'}</td>
                    <td className="px-4 py-3 text-xs text-nc-muted whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-nc-muted text-sm">Aucune entrée d'audit</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
        <div className="px-4 py-3 border-t border-nc-border text-xs text-nc-muted">{logs.length} entrée(s)</div>
      </div>
    </div>
  )
}

/* ─── Main component ─────────────────────────────────────────────────────── */
export default function AdminPanel() {
  const [tab, setTab]         = useState('assign')
  const [users, setUsers]     = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    const [usersResult] = await Promise.allSettled([adminApi.users(200)])
    if (usersResult.status === 'fulfilled') {
      setUsers(usersResult.value)
    } else {
      setError('Erreur de chargement des utilisateurs.')
    }
    setLoading(false)
  }, [])

  useEffect(() => { load() }, [load])

  const TABS = [
    { key: 'assign',   label: 'Assignations',     icon: UserCheck },
    { key: 'settings', label: 'Paramètres',       icon: Settings },
    { key: 'audit',    label: 'Journal d\'audit', icon: ClipboardList },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl flex items-center justify-center bg-purple-500/15">
          <Shield className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-nc-text">Administration</h1>
          <p className="text-sm text-nc-muted">Assignations, paramètres système et journal d'audit</p>
        </div>
        <button
          onClick={load}
          className="ms-auto btn-ghost p-2 rounded-xl text-nc-muted hover:text-nc-text"
          title="Rafraîchir"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm">
          <AlertTriangle className="w-4 h-4 shrink-0" />{error}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 border-b border-nc-border overflow-x-auto">
        {TABS.map(({ key, label, icon: Icon }) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 transition-all -mb-px whitespace-nowrap
                        ${tab === key
                          ? 'border-nc-accent text-nc-accent'
                          : 'border-transparent text-nc-muted hover:text-nc-text'}`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      {tab === 'assign'   && <AssignTab users={loading ? [] : users} />}
      {tab === 'settings' && <SettingsTab />}
      {tab === 'audit'    && <AuditTab />}
    </div>
  )
}
