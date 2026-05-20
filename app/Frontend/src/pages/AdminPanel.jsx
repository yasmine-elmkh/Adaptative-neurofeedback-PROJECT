import { useState, useEffect, useCallback } from 'react'
import { admin as adminApi } from '../utils/api'
import {
  Shield, RefreshCw, AlertTriangle, Settings,
  UserCheck, ClipboardList, Search, Save, ChevronRight,
  Bell, Brain, Zap, Bot, Lock, Globe2, Download,
  ToggleLeft, ToggleRight, SlidersHorizontal, ArrowRight,
  X, Check,
} from 'lucide-react'

/* ─── Audit badge colours ────────────────────────────────────────────────── */
const LOG_BADGE = (action) => {
  if (!action)                                 return 'bg-nc-surface2 text-nc-muted border-nc-border'
  if (['LOGIN', 'SESSION_CREATE', 'USER_CREATED', 'SESSION_START'].includes(action))
                                               return 'bg-green-500/10 text-green-400 border-green-500/20'
  if (['USER_DELETED', 'CALIBRATION_FAILED'].includes(action))
                                               return 'bg-nc-danger/10 text-nc-danger border-nc-danger/20'
  if (['ROLE_CHANGE', 'SETTINGS_UPDATE', 'SETTINGS_CHANGED', 'PASSWORD_CHANGE'].includes(action))
                                               return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20'
  if (['CALIBRATION'].includes(action))        return 'bg-purple-500/10 text-purple-400 border-purple-500/20'
  if (action.startsWith('DATA_EXPORT') || action === 'EXPORT_DATA')
                                               return 'bg-nc-accent/10 text-nc-accent border-nc-accent/20'
  if (action.startsWith('ASSISTANT_FEEDBACK')) return 'bg-orange-500/10 text-orange-400 border-orange-500/20'
  if (['PATIENT_ASSIGNED', 'SESSION_END'].includes(action))
                                               return 'bg-blue-500/10 text-blue-400 border-blue-500/20'
  if (['RAG_QUERY', 'FEEDBACK_MODE_CHANGE'].includes(action))
                                               return 'bg-pink-500/10 text-pink-400 border-pink-500/20'
  return 'bg-nc-surface2 text-nc-muted border-nc-border'
}

/* ══════════════════════════════════════════════════════════════════════════ */
/*  ASSIGN TAB                                                                */
/* ══════════════════════════════════════════════════════════════════════════ */
function AssignTab({ users }) {
  const [search,            setSearch]            = useState('')
  const [selectedTherapist, setSelectedTherapist] = useState(null)
  const [assignLoading,     setAssignLoading]     = useState(null)
  const [reassignTarget,    setReassignTarget]    = useState(null)
  const [localUsers,        setLocalUsers]        = useState(users)

  useEffect(() => { setLocalUsers(users) }, [users])

  /* only real therapists — admins are excluded */
  const therapists = localUsers.filter(u => u.role === 'therapist')

  const unassigned = localUsers.filter(u =>
    (u.role === 'patient' || u.role === 'user') &&
    !u.therapist_id &&
    (search === '' || u.email.toLowerCase().includes(search.toLowerCase()) ||
      `${u.first_name ?? ''} ${u.last_name ?? ''}`.toLowerCase().includes(search.toLowerCase()))
  )

  const assignedToSelected = selectedTherapist
    ? localUsers.filter(u =>
        (u.role === 'patient' || u.role === 'user') &&
        u.therapist_id === selectedTherapist.id
      )
    : []

  /* all assigned patients regardless of therapist */
  const allAssigned = localUsers.filter(u =>
    (u.role === 'patient' || u.role === 'user') && u.therapist_id
  )

  const assign = async (patientId, therapistId) => {
    setAssignLoading(patientId)
    try {
      await adminApi.assignPatient(patientId, therapistId)
      setLocalUsers(prev => prev.map(u => u.id === patientId ? { ...u, therapist_id: therapistId } : u))
      setReassignTarget(null)
    } finally { setAssignLoading(null) }
  }

  const unassign = async (patientId) => {
    setAssignLoading(patientId)
    try {
      await adminApi.assignPatient(patientId, null)
      setLocalUsers(prev => prev.map(u => u.id === patientId ? { ...u, therapist_id: null } : u))
    } finally { setAssignLoading(null) }
  }

  const therapistName = (id) => {
    const t = localUsers.find(u => u.id === id)
    return t ? (t.first_name ? `${t.first_name} ${t.last_name}` : t.email) : '—'
  }

  return (
    <div className="space-y-6">

      {/* ── Summary row ── */}
      <div className="grid grid-cols-3 gap-3">
        {[
          { label: 'Thérapeutes',       value: therapists.length,  color: 'text-green-400',  bg: 'bg-green-500/10' },
          { label: 'Patients assignés', value: allAssigned.length, color: 'text-blue-400',   bg: 'bg-blue-500/10' },
          { label: 'Non assignés',      value: localUsers.filter(u => (u.role === 'patient' || u.role === 'user') && !u.therapist_id).length,
            color: 'text-yellow-400', bg: 'bg-yellow-500/10' },
        ].map(({ label, value, color, bg }) => (
          <div key={label} className={`card p-4 flex items-center gap-3 ${bg}`}>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-nc-muted">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-4">

        {/* ── Left: Therapists ── */}
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-nc-border">
            <h3 className="font-semibold text-nc-text text-sm">Thérapeutes</h3>
            <p className="text-xs text-nc-muted mt-0.5">Sélectionnez pour gérer les patients</p>
          </div>
          <div className="divide-y divide-nc-border">
            {therapists.map(t => {
              const count = localUsers.filter(u => u.therapist_id === t.id).length
              const isSelected = selectedTherapist?.id === t.id
              return (
                <button
                  key={t.id}
                  onClick={() => setSelectedTherapist(isSelected ? null : t)}
                  className={`w-full flex items-center gap-3 px-4 py-3 text-start transition-colors
                              ${isSelected ? 'bg-nc-accent/10 border-l-2 border-nc-accent' : 'hover:bg-nc-surface2 border-l-2 border-transparent'}`}
                >
                  <div className="w-9 h-9 rounded-full flex items-center justify-center bg-green-500/15 text-green-400 text-sm font-bold shrink-0">
                    {(t.first_name || t.email).charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-nc-text truncate">
                      {t.first_name ? `${t.first_name} ${t.last_name}` : t.email}
                    </p>
                    <p className="text-xs text-nc-muted truncate">{t.email}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400">
                      {count}
                    </span>
                    <ChevronRight className={`w-4 h-4 text-nc-muted transition-transform ${isSelected ? 'rotate-90' : ''}`} />
                  </div>
                </button>
              )
            })}
            {therapists.length === 0 && (
              <p className="px-4 py-8 text-sm text-nc-muted text-center">Aucun thérapeute</p>
            )}
          </div>
        </div>

        {/* ── Right: Patients ── */}
        <div className="space-y-4">

          {/* Assigned to selected therapist */}
          {selectedTherapist && (
            <div className="card overflow-hidden">
              <div className="p-4 border-b border-nc-border flex items-center justify-between">
                <h3 className="font-semibold text-nc-text text-sm">
                  Patients de {selectedTherapist.first_name || selectedTherapist.email}
                </h3>
                <span className="badge-muted">{assignedToSelected.length}</span>
              </div>
              <div className="divide-y divide-nc-border max-h-60 overflow-y-auto">
                {assignedToSelected.map(p => (
                  <div key={p.id} className={`flex items-center gap-3 px-4 py-3 ${assignLoading === p.id ? 'opacity-50' : ''}`}>
                    <div className="w-7 h-7 rounded-full bg-blue-500/10 text-blue-400 flex items-center justify-center text-xs font-bold shrink-0">
                      {(p.first_name || p.email).charAt(0).toUpperCase()}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-nc-text truncate">{p.first_name} {p.last_name}</p>
                      <p className="text-xs text-nc-muted truncate">{p.email}</p>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      {/* Reassign dropdown */}
                      {reassignTarget === p.id ? (
                        <div className="flex items-center gap-1">
                          <select
                            className="input text-xs py-1 px-2"
                            defaultValue=""
                            onChange={e => e.target.value && assign(p.id, e.target.value)}
                          >
                            <option value="">Choisir…</option>
                            {therapists.filter(t => t.id !== selectedTherapist.id).map(t => (
                              <option key={t.id} value={t.id}>
                                {t.first_name ? `${t.first_name} ${t.last_name}` : t.email}
                              </option>
                            ))}
                          </select>
                          <button onClick={() => setReassignTarget(null)}
                                  className="p-1 text-nc-muted hover:text-nc-text">
                            <X className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      ) : (
                        <button
                          onClick={() => setReassignTarget(p.id)}
                          disabled={assignLoading === p.id}
                          className="text-xs text-nc-accent hover:underline disabled:opacity-50"
                          title="Changer de thérapeute"
                        >
                          <ArrowRight className="w-3.5 h-3.5" />
                        </button>
                      )}
                      <button
                        onClick={() => unassign(p.id)}
                        disabled={assignLoading === p.id}
                        className="text-xs text-nc-danger hover:underline disabled:opacity-50"
                      >
                        Retirer
                      </button>
                    </div>
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
                <div key={p.id} className={`flex items-center gap-3 px-4 py-3 ${assignLoading === p.id ? 'opacity-50' : ''}`}>
                  <div className="w-7 h-7 rounded-full bg-nc-surface2 text-nc-muted flex items-center justify-center text-xs font-bold shrink-0">
                    {(p.first_name || p.email).charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-nc-text truncate">{p.first_name} {p.last_name}</p>
                    <p className="text-xs text-nc-muted truncate">{p.email}</p>
                  </div>
                  {selectedTherapist ? (
                    <button
                      onClick={() => assign(p.id, selectedTherapist.id)}
                      disabled={assignLoading === p.id}
                      className="text-xs text-nc-accent hover:underline disabled:opacity-50 flex items-center gap-1 shrink-0"
                    >
                      <Check className="w-3 h-3" /> Assigner
                    </button>
                  ) : (
                    <select
                      className="input text-xs py-1 px-2 shrink-0 max-w-[160px]"
                      defaultValue=""
                      disabled={assignLoading === p.id || therapists.length === 0}
                      onChange={e => e.target.value && assign(p.id, e.target.value)}
                    >
                      <option value="" disabled>
                        {therapists.length === 0 ? 'Aucun thérapeute' : 'Assigner à…'}
                      </option>
                      {therapists.map(t => (
                        <option key={t.id} value={t.id}>
                          {t.first_name ? `${t.first_name} ${t.last_name}` : t.email}
                        </option>
                      ))}
                    </select>
                  )}
                </div>
              ))}
              {unassigned.length === 0 && (
                <p className="px-4 py-4 text-xs text-nc-muted text-center">
                  {search ? 'Aucun résultat' : 'Tous les patients sont assignés'}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* ── All assigned patients table ── */}
      {allAssigned.length > 0 && (
        <div className="card overflow-hidden">
          <div className="p-4 border-b border-nc-border">
            <h3 className="font-semibold text-nc-text text-sm">Vue d'ensemble des assignations</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-nc-border bg-nc-surface2/40">
                  {['Patient', 'Email', 'Thérapeute', 'Actions'].map(h => (
                    <th key={h} className="px-4 py-3 text-start text-xs font-semibold text-nc-muted uppercase tracking-wide">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {allAssigned.map(p => (
                  <tr key={p.id} className="border-b border-nc-border hover:bg-nc-surface2/40">
                    <td className="px-4 py-3 text-sm font-medium text-nc-text">
                      {p.first_name} {p.last_name}
                    </td>
                    <td className="px-4 py-3 text-xs text-nc-muted">{p.email}</td>
                    <td className="px-4 py-3">
                      <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-500/10 text-green-400 border border-green-500/20">
                        {therapistName(p.therapist_id)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <select
                          className="input text-xs py-1 px-2"
                          value={p.therapist_id}
                          onChange={e => assign(p.id, e.target.value)}
                          disabled={assignLoading === p.id}
                        >
                          {therapists.map(t => (
                            <option key={t.id} value={t.id}>
                              {t.first_name ? `${t.first_name} ${t.last_name}` : t.email}
                            </option>
                          ))}
                        </select>
                        <button
                          onClick={() => unassign(p.id)}
                          disabled={assignLoading === p.id}
                          className="text-xs text-nc-danger hover:underline disabled:opacity-50"
                        >
                          Désassigner
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

/* ══════════════════════════════════════════════════════════════════════════ */
/*  SETTINGS TAB — categorised                                                */
/* ══════════════════════════════════════════════════════════════════════════ */

const SETTINGS_CATEGORIES = [
  {
    key: 'general',
    label: 'Général',
    icon: Globe2,
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    settings: [
      { key: 'platform_name',    label: 'Nom de la plateforme',     type: 'text',   default: 'NeuroCap' },
      { key: 'admin_email',      label: 'Email administrateur',     type: 'email',  default: '' },
      { key: 'maintenance_mode', label: 'Mode maintenance',         type: 'toggle', default: 'false' },
    ],
  },
  {
    key: 'security',
    label: 'Sécurité',
    icon: Lock,
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    settings: [
      { key: 'jwt_expiry_minutes',   label: 'Durée JWT (minutes)',           type: 'number', default: '60',  min: 5,   max: 1440 },
      { key: 'min_password_length',  label: 'Longueur min. mot de passe',    type: 'number', default: '8',   min: 6,   max: 32 },
      { key: 'require_uppercase',    label: 'Majuscule requise',             type: 'toggle', default: 'true' },
      { key: 'require_digit',        label: 'Chiffre requis',                type: 'toggle', default: 'true' },
      { key: 'enable_2fa',           label: '2FA activé (optionnel)',        type: 'toggle', default: 'false' },
      { key: 'max_concurrent_sessions', label: 'Sessions simultanées max',  type: 'number', default: '3',   min: 1,   max: 10 },
    ],
  },
  {
    key: 'ai',
    label: 'IA / Protocole',
    icon: Brain,
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
    settings: [
      { key: 'confidence_threshold', label: 'Seuil de confiance',           type: 'slider', default: '0.60', min: 0,  max: 1,   step: 0.01 },
      { key: 'mou_rule_low',         label: 'Règle Mou — seuil bas (%)',    type: 'number', default: '40',  min: 10,  max: 49 },
      { key: 'mou_rule_high',        label: 'Règle Mou — seuil haut (%)',   type: 'number', default: '60',  min: 51,  max: 90 },
      { key: 'block_duration_min',   label: 'Durée d\'un bloc (min)',       type: 'number', default: '3',   min: 1,   max: 15 },
      { key: 'blocks_per_session',   label: 'Blocs par session',            type: 'number', default: '6',   min: 2,   max: 12 },
      { key: 'adaptive_engine',      label: 'Moteur adaptatif activé',      type: 'toggle', default: 'true' },
    ],
  },
  {
    key: 'rag',
    label: 'RAG',
    icon: Bot,
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
    settings: [
      { key: 'llm_model',    label: 'Modèle LLM',                  type: 'select', default: 'mistral', options: ['mistral', 'llama2', 'phi', 'gemma', 'mixtral'] },
      { key: 'ollama_url',   label: 'URL Ollama',                  type: 'text',   default: 'http://localhost:11434' },
      { key: 'rag_temperature', label: 'Température',              type: 'slider', default: '0.30', min: 0.1, max: 1.0, step: 0.05 },
      { key: 'rag_top_k',    label: 'Documents retournés (top-k)', type: 'number', default: '3',  min: 1,   max: 20 },
    ],
  },
  {
    key: 'feedback',
    label: 'Feedback',
    icon: Zap,
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10',
    settings: [
      { key: 'feedback_visual',  label: 'Mode visuel activé',       type: 'toggle', default: 'true' },
      { key: 'feedback_sound',   label: 'Mode sonore activé',       type: 'toggle', default: 'true' },
      { key: 'feedback_game',    label: 'Mode jeu activé',          type: 'toggle', default: 'true' },
      { key: 'max_sound_volume', label: 'Volume max sonore (%)',    type: 'slider', default: '80',  min: 0, max: 100, step: 1 },
      { key: 'game_sensitivity', label: 'Sensibilité jeu (seuil)', type: 'slider', default: '0.50', min: 0, max: 1,   step: 0.01 },
    ],
  },
  {
    key: 'notifications',
    label: 'Notifications',
    icon: Bell,
    color: 'text-green-400',
    bg: 'bg-green-500/10',
    settings: [
      { key: 'welcome_email',       label: 'Email de bienvenue',               type: 'toggle', default: 'true' },
      { key: 'session_report_email', label: 'Rapport de session par email',    type: 'toggle', default: 'false' },
      { key: 'low_score_alert',     label: 'Alerte score faible consécutif',   type: 'toggle', default: 'true' },
    ],
  },
]

function ToggleSwitch({ value, onChange }) {
  const on = value === 'true' || value === true
  return (
    <button
      type="button"
      onClick={() => onChange(on ? 'false' : 'true')}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${on ? 'bg-nc-accent' : 'bg-nc-border'}`}
    >
      <span className={`inline-block h-4 w-4 transform rounded-full bg-white shadow transition-transform ${on ? 'translate-x-6' : 'translate-x-1'}`} />
    </button>
  )
}

function SettingRow({ def, value, onChange, saving, onSave, isDirty }) {
  return (
    <div className="flex flex-wrap items-center gap-4 px-5 py-4 hover:bg-nc-surface2/30 transition-colors">
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-nc-text">{def.label}</p>
        <p className="text-[11px] text-nc-muted font-mono mt-0.5">{def.key}</p>
      </div>
      <div className="flex items-center gap-3 shrink-0">
        {def.type === 'toggle' && (
          <ToggleSwitch value={value} onChange={onChange} />
        )}
        {def.type === 'slider' && (
          <div className="flex items-center gap-3">
            <input
              type="range"
              min={def.min}
              max={def.max}
              step={def.step}
              value={value ?? def.default}
              onChange={e => onChange(e.target.value)}
              className="w-32 accent-[rgb(var(--nc-accent))]"
            />
            <span className="text-sm font-mono text-nc-accent w-12 text-center">{parseFloat(value ?? def.default).toFixed(def.step < 0.1 ? 2 : def.step < 1 ? 2 : 0)}</span>
          </div>
        )}
        {def.type === 'select' && (
          <select
            className="input text-sm py-1.5 px-3"
            value={value ?? def.default}
            onChange={e => onChange(e.target.value)}
          >
            {def.options.map(o => <option key={o} value={o}>{o}</option>)}
          </select>
        )}
        {(def.type === 'text' || def.type === 'email' || def.type === 'number') && (
          <input
            type={def.type === 'number' ? 'number' : def.type}
            min={def.min}
            max={def.max}
            className="input text-sm py-1.5 px-3 w-44 font-mono"
            value={value ?? def.default}
            onChange={e => onChange(e.target.value)}
          />
        )}
        {def.type !== 'toggle' && (
          <button
            onClick={onSave}
            disabled={!isDirty || saving}
            className="btn-primary flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs disabled:opacity-40"
          >
            {saving ? <span className="w-3 h-3 border border-white/30 border-t-white rounded-full animate-spin" /> : <Save className="w-3 h-3" />}
            Sauver
          </button>
        )}
        {def.type === 'toggle' && isDirty && (
          <button
            onClick={onSave}
            disabled={saving}
            className="text-xs text-nc-accent hover:underline disabled:opacity-40"
          >
            {saving ? '…' : 'Sauver'}
          </button>
        )}
      </div>
    </div>
  )
}

function SettingsTab() {
  const [activeCategory, setActiveCategory] = useState('general')
  const [serverVals,     setServerVals]     = useState({})
  const [drafts,         setDrafts]         = useState({})
  const [loading,        setLoading]        = useState(true)
  const [saving,         setSaving]         = useState({})
  const [error,          setError]          = useState('')
  const [savedKeys,      setSavedKeys]      = useState([])

  useEffect(() => {
    adminApi.getSettings()
      .then(data => {
        const map = {}
        data.forEach(s => { map[s.key] = s.value })
        setServerVals(map)
        setDrafts(map)
      })
      .catch(() => setError('Impossible de charger les paramètres'))
      .finally(() => setLoading(false))
  }, [])

  const saveSetting = async (key, value) => {
    setSaving(s => ({ ...s, [key]: true }))
    try {
      await adminApi.updateSetting(key, value)
      setServerVals(prev => ({ ...prev, [key]: value }))
      setSavedKeys(prev => [...prev, key])
      setTimeout(() => setSavedKeys(prev => prev.filter(k => k !== key)), 2000)
    } catch {
      setError(`Erreur lors de la sauvegarde de ${key}`)
    } finally {
      setSaving(s => ({ ...s, [key]: false }))
    }
  }

  const getValue = (def) => drafts[def.key] ?? def.default
  const isDirty  = (def) => (drafts[def.key] ?? def.default) !== (serverVals[def.key] ?? def.default)

  const activeCat = SETTINGS_CATEGORIES.find(c => c.key === activeCategory)

  if (loading) return (
    <div className="flex justify-center py-16">
      <span className="w-6 h-6 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
    </div>
  )

  return (
    <div className="flex gap-5">
      {/* Sidebar */}
      <div className="w-48 shrink-0 space-y-1">
        {SETTINGS_CATEGORIES.map(({ key, label, icon: Icon, color, bg }) => (
          <button
            key={key}
            onClick={() => setActiveCategory(key)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all text-start
                        ${activeCategory === key
                          ? `${bg} ${color}`
                          : 'text-nc-muted hover:text-nc-text hover:bg-nc-surface2'}`}
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        {error && (
          <div className="flex items-center gap-2 px-4 py-3 mb-4 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm">
            <AlertTriangle className="w-4 h-4 shrink-0" />
            <span className="flex-1">{error}</span>
            <button onClick={() => setError('')}><X className="w-4 h-4" /></button>
          </div>
        )}

        {activeCat && (
          <div className="card overflow-hidden">
            <div className={`p-5 border-b border-nc-border flex items-center gap-3 ${activeCat.bg}`}>
              <activeCat.icon className={`w-5 h-5 ${activeCat.color}`} />
              <div>
                <h3 className="font-semibold text-nc-text">{activeCat.label}</h3>
                <p className="text-xs text-nc-muted mt-0.5">{activeCat.settings.length} paramètre(s)</p>
              </div>
            </div>
            <div className="divide-y divide-nc-border">
              {activeCat.settings.map(def => (
                <SettingRow
                  key={def.key}
                  def={def}
                  value={getValue(def)}
                  onChange={v => setDrafts(d => ({ ...d, [def.key]: v }))}
                  saving={!!saving[def.key]}
                  onSave={() => saveSetting(def.key, getValue(def))}
                  isDirty={isDirty(def)}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════════════════════════════════ */
/*  AUDIT TAB                                                                 */
/* ══════════════════════════════════════════════════════════════════════════ */

const KNOWN_ACTIONS = [
  'LOGIN',
  'USER_CREATED', 'USER_DELETED',
  'PASSWORD_CHANGE',
  'ROLE_CHANGE',
  'SETTINGS_UPDATE',
  'SESSION_START', 'SESSION_END',
  'CALIBRATION', 'CALIBRATION_FAILED',
  'DATA_EXPORT', 'DATA_EXPORT_ALL', 'EXPORT_DATA',
  'PATIENT_ASSIGNED',
  'FEEDBACK_MODE_CHANGE',
  'ASSISTANT_FEEDBACK_UP', 'ASSISTANT_FEEDBACK_DOWN',
  'RAG_QUERY',
]

function AuditTab() {
  const [logs,         setLogs]         = useState([])
  const [loading,      setLoading]      = useState(false)
  const [actionFilter, setActionFilter] = useState('')
  const [userFilter,   setUserFilter]   = useState('')
  const [dateFrom,     setDateFrom]     = useState('')
  const [dateTo,       setDateTo]       = useState('')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const data = await adminApi.auditLogs(
        500,
        actionFilter || null,
        userFilter   || null,
        dateFrom     || null,
        dateTo       || null,
      )
      setLogs(data)
    } catch {
      setLogs([])
    } finally { setLoading(false) }
  }, [actionFilter, userFilter, dateFrom, dateTo])

  useEffect(() => { load() }, [load])

  const exportCSV = () => {
    const header = 'Action,Détails,IP,Date'
    const rows = logs.map(l =>
      `"${l.action}","${(l.details || '').replace(/"/g, '""')}","${l.ip_address || ''}","${new Date(l.created_at).toLocaleString('fr-FR')}"`
    )
    const csv  = [header, ...rows].join('\n')
    const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8;' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `audit_${new Date().toISOString().slice(0, 10)}.csv`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="card p-4 flex flex-wrap gap-3 items-center">
        <select
          className="input w-52 text-sm"
          value={actionFilter}
          onChange={e => setActionFilter(e.target.value)}
        >
          <option value="">Toutes les actions</option>
          {KNOWN_ACTIONS.map(a => <option key={a} value={a}>{a}</option>)}
        </select>
        <input
          className="input w-60 text-sm"
          placeholder="User ID (UUID)"
          value={userFilter}
          onChange={e => setUserFilter(e.target.value)}
        />
        <div className="flex items-center gap-2">
          <input type="date" className="input text-sm" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
          <span className="text-nc-muted text-xs">→</span>
          <input type="date" className="input text-sm" value={dateTo} onChange={e => setDateTo(e.target.value)} />
        </div>
        <div className="flex items-center gap-2 ms-auto">
          <button
            onClick={exportCSV}
            disabled={logs.length === 0}
            className="btn-ghost flex items-center gap-1.5 px-3 py-2 rounded-xl text-sm text-nc-muted hover:text-nc-text disabled:opacity-40"
            title="Exporter CSV"
          >
            <Download className="w-4 h-4" />
            CSV
          </button>
          <button
            onClick={load}
            className="btn-ghost p-2 rounded-xl text-nc-muted hover:text-nc-text"
            title="Actualiser"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Table */}
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
                {logs.map((log, i) => (
                  <tr key={log.id ?? i} className="border-b border-nc-border hover:bg-nc-surface2/50">
                    <td className="px-4 py-3">
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${LOG_BADGE(log.action)}`}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-xs text-nc-muted hidden md:table-cell max-w-xs truncate" title={log.details}>
                      {log.details || '—'}
                    </td>
                    <td className="px-4 py-3 text-xs text-nc-muted hidden lg:table-cell font-mono">
                      {log.ip_address || '—'}
                    </td>
                    <td className="px-4 py-3 text-xs text-nc-muted whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString('fr-FR')}
                    </td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-nc-muted text-sm">
                      Aucune entrée d'audit
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
        <div className="px-4 py-3 border-t border-nc-border flex items-center justify-between text-xs text-nc-muted">
          <span>{logs.length} entrée(s)</span>
          {logs.length > 0 && (
            <button onClick={exportCSV} className="flex items-center gap-1 hover:text-nc-text transition-colors">
              <Download className="w-3 h-3" /> Exporter CSV
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

/* ══════════════════════════════════════════════════════════════════════════ */
/*  MAIN COMPONENT                                                             */
/* ══════════════════════════════════════════════════════════════════════════ */
export default function AdminPanel() {
  const [tab,     setTab]     = useState('assign')
  const [users,   setUsers]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

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
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
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

      {/* Content */}
      {tab === 'assign'   && <AssignTab users={loading ? [] : users} />}
      {tab === 'settings' && <SettingsTab />}
      {tab === 'audit'    && <AuditTab />}
    </div>
  )
}
