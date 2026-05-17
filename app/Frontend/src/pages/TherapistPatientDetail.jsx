import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { therapist as therapistApi } from '../utils/api'
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend,
  BarChart, Bar, Cell,
} from 'recharts'
import {
  ArrowLeft, Brain, Download, Star, Plus, AlertTriangle,
  TrendingUp, TrendingDown, Minus, Activity, Target, Zap,
  UserX, UserCheck, ChevronDown, Check, Calendar, BarChart2,
  MessageSquareText, Settings2,
} from 'lucide-react'

/* ─── constants ───────────────────────────────────────────────────────────── */
const STATUS_COLOR = {
  completed: 'text-green-400', running: 'text-nc-accent',
  pending: 'text-nc-muted', cancelled: 'text-nc-danger',
}
const PALIER_OPTIONS = [
  { value: 'P1_INITIATION',    label: 'P1 – Initiation' },
  { value: 'P2_APPRENTISSAGE', label: 'P2 – Apprentissage' },
  { value: 'P3_MAITRISE',      label: 'P3 – Maîtrise' },
  { value: 'P4_AUTONOMIE',     label: 'P4 – Autonomie' },
]
const PALIER_COLORS = {
  P1_INITIATION: '#3b82f6', P2_APPRENTISSAGE: '#f59e0b',
  P3_MAITRISE: '#f97316', P4_AUTONOMIE: '#22c55e',
}
const PALIER_IDX = { P1_INITIATION: 0, P2_APPRENTISSAGE: 1, P3_MAITRISE: 2, P4_AUTONOMIE: 3 }
const PROFILE_INFO = {
  A: { label: 'Très réactif', color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/30' },
  B: { label: 'Standard',     color: 'text-nc-accent',  bg: 'bg-nc-accent/10',  border: 'border-nc-accent/30' },
  C: { label: 'Faible réactivité', color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
}

/* ─── helpers ─────────────────────────────────────────────────────────────── */
function TrendBadge({ value }) {
  if (value === null || value === undefined) return <Minus className="w-3.5 h-3.5 text-nc-muted" />
  if (value > 0) return (
    <span className="flex items-center gap-0.5 text-green-400 text-xs font-semibold">
      <TrendingUp className="w-3 h-3" />+{Math.abs(value)}%
    </span>
  )
  return (
    <span className="flex items-center gap-0.5 text-nc-danger text-xs font-semibold">
      <TrendingDown className="w-3 h-3" />-{Math.abs(value)}%
    </span>
  )
}

function InfoChip({ label, value, color = 'text-nc-text' }) {
  return (
    <div className="bg-nc-surface2 rounded-xl px-4 py-3 min-w-[90px] text-center">
      <p className={`text-base font-bold ${color}`}>{value ?? '—'}</p>
      <p className="text-[10px] text-nc-muted mt-0.5">{label}</p>
    </div>
  )
}

/* ─── Score + TBR chart ────────────────────────────────────────────────────── */
function ScoreChart({ sessions }) {
  const data = [...sessions]
    .filter(s => s.status === 'completed')
    .reverse()
    .map((s, i) => ({
      name: `S${i + 1}`,
      score: s.score ?? null,
      concentration: s.avg_concentration !== null && s.avg_concentration !== undefined
        ? Math.round((s.avg_concentration) * 100) : null,
      tbr: s.avg_tbr ?? null,
    }))

  if (!data.length) return (
    <div className="flex items-center justify-center h-40 text-nc-muted text-sm">
      <Activity className="w-5 h-5 me-2 opacity-40" />Pas encore de données
    </div>
  )

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 4, right: 8, left: -24, bottom: 0 }}>
        <XAxis dataKey="name" tick={{ fontSize: 10, fill: 'rgb(var(--nc-muted))' }} />
        <YAxis tick={{ fontSize: 10, fill: 'rgb(var(--nc-muted))' }} domain={[0, 100]} />
        <Tooltip
          contentStyle={{ background: 'rgb(var(--nc-surface))', border: '1px solid rgb(var(--nc-border))', borderRadius: 12, fontSize: 12 }}
          labelStyle={{ color: 'rgb(var(--nc-text))' }}
        />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Line type="monotone" dataKey="score"         stroke="rgb(var(--nc-accent))" strokeWidth={2} dot={false} name="Score %" connectNulls />
        <Line type="monotone" dataKey="concentration" stroke="#4ade80"               strokeWidth={2} dot={false} name="Concentration %" connectNulls />
        <Line type="monotone" dataKey="tbr"           stroke="#f59e0b"               strokeWidth={1.5} dot={false} name="TBR" connectNulls strokeDasharray="4 2" />
      </LineChart>
    </ResponsiveContainer>
  )
}

/* ─── Palier progress bar ──────────────────────────────────────────────────── */
function PalierProgressBar({ palier }) {
  const idx = PALIER_IDX[palier] ?? 0
  return (
    <div className="space-y-3">
      <div className="flex items-center gap-0">
        {PALIER_OPTIONS.map((p, i) => {
          const done   = i < idx
          const active = i === idx
          const color  = PALIER_COLORS[p.value]
          return (
            <div key={p.value} className="flex items-center flex-1 last:flex-none">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 border-2 transition-all
                              ${done   ? 'bg-green-500 border-green-500 text-white'
                              : active ? 'text-white border-transparent'
                              : 'bg-nc-surface2 border-nc-border text-nc-muted'}`}
                   style={active ? { background: color, borderColor: color } : {}}>
                {done ? '✓' : i + 1}
              </div>
              {i < PALIER_OPTIONS.length - 1 && (
                <div className={`h-0.5 flex-1 mx-1 rounded-full transition-all ${done ? 'bg-green-500' : 'bg-nc-border'}`} />
              )}
            </div>
          )
        })}
      </div>
      <div className="grid grid-cols-4 gap-1 text-[10px]">
        {PALIER_OPTIONS.map((p, i) => (
          <div key={p.value} className={`text-center ${i === idx ? 'font-semibold' : 'text-nc-muted'}`}
               style={i === idx ? { color: PALIER_COLORS[p.value] } : {}}>
            {p.label}
          </div>
        ))}
      </div>
    </div>
  )
}

/* ─── Sessions table ──────────────────────────────────────────────────────── */
function SessionsTable({ sessions }) {
  if (!sessions.length) return (
    <p className="text-center text-nc-muted text-sm py-8">Aucune session enregistrée</p>
  )
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-nc-border bg-nc-surface2/50">
            {['#','Date','Objectif','Score','TBR','Durée','Blocs','Statut'].map(h => (
              <th key={h} className="px-3 py-2.5 text-start text-xs font-semibold text-nc-muted uppercase tracking-wide whitespace-nowrap">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sessions.map((s, i) => (
            <tr key={s.id} className="border-b border-nc-border hover:bg-nc-surface2/50">
              <td className="px-3 py-2.5 text-xs text-nc-muted">{i + 1}</td>
              <td className="px-3 py-2.5 text-xs text-nc-muted whitespace-nowrap">
                {new Date(s.created_at).toLocaleDateString('fr-FR')}
              </td>
              <td className="px-3 py-2.5 text-xs text-nc-text capitalize">{s.objective ?? '—'}</td>
              <td className="px-3 py-2.5 text-sm font-bold text-nc-accent">
                {s.score !== null && s.score !== undefined ? `${s.score}%` : '—'}
              </td>
              <td className="px-3 py-2.5 text-xs text-yellow-400 font-mono">
                {s.avg_tbr !== null && s.avg_tbr !== undefined ? s.avg_tbr.toFixed(2) : '—'}
              </td>
              <td className="px-3 py-2.5 text-xs text-nc-muted">
                {s.duration_seconds ? `${Math.round(s.duration_seconds / 60)} min` : '—'}
              </td>
              <td className="px-3 py-2.5 text-xs text-nc-muted">{s.n_blocks ?? '—'}</td>
              <td className={`px-3 py-2.5 text-xs font-medium capitalize ${STATUS_COLOR[s.status] ?? 'text-nc-muted'}`}>
                {s.status}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/* ─── Notes panel ─────────────────────────────────────────────────────────── */
function NotesPanel({ patientId }) {
  const [notes,   setNotes]   = useState([])
  const [newNote, setNewNote] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving,  setSaving]  = useState(false)

  useEffect(() => {
    therapistApi.getNotes(patientId)
      .then(setNotes).catch(() => {}).finally(() => setLoading(false))
  }, [patientId])

  const handleAdd = async () => {
    if (!newNote.trim()) return
    setSaving(true)
    try {
      const note = await therapistApi.addNote(patientId, newNote.trim())
      setNotes(prev => [note, ...prev])
      setNewNote('')
    } catch {}
    finally { setSaving(false) }
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <textarea
          rows={3}
          placeholder="Ajouter une note clinique privée…"
          value={newNote}
          onChange={e => setNewNote(e.target.value)}
          className="input w-full resize-none"
        />
        <button
          onClick={handleAdd}
          disabled={!newNote.trim() || saving}
          className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm disabled:opacity-60"
        >
          <Plus className="w-3.5 h-3.5" />
          {saving ? 'Enregistrement…' : 'Ajouter la note'}
        </button>
      </div>
      {loading ? (
        <div className="flex justify-center py-6">
          <span className="w-5 h-5 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
        </div>
      ) : notes.length === 0 ? (
        <p className="text-center text-nc-muted text-sm py-6">Aucune note pour ce patient</p>
      ) : (
        <div className="space-y-3">
          {notes.map(n => (
            <div key={n.id} className="p-4 rounded-xl bg-nc-surface2 space-y-1.5">
              <p className="text-sm text-nc-text whitespace-pre-wrap leading-relaxed">{n.content}</p>
              <p className="text-[10px] text-nc-muted">{new Date(n.created_at).toLocaleString('fr-FR')}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/* ─── Actions panel ────────────────────────────────────────────────────────── */
function ActionsPanel({ patientId, patient, profile, onRefresh }) {
  const [rec,         setRec]         = useState(null)
  const [recLoading,  setRecLoading]  = useState(true)
  const [objective,   setObjective]   = useState('')
  const [weekly,      setWeekly]      = useState('')
  const [message,     setMessage]     = useState('')
  const [savingRec,   setSavingRec]   = useState(false)
  const [recSaved,    setRecSaved]    = useState(false)

  const [selectedPalier, setSelectedPalier] = useState(profile?.palier ?? '')
  const [savingPalier,   setSavingPalier]   = useState(false)
  const [palierSaved,    setPalierSaved]    = useState(false)

  const [togglingActive, setTogglingActive] = useState(false)

  useEffect(() => {
    therapistApi.getRecommendation(patientId)
      .then(data => {
        setRec(data)
        if (data) {
          setObjective(data.recommended_objective ?? '')
          setWeekly(data.weekly_sessions_target?.toString() ?? '')
          setMessage(data.message ?? '')
        }
      })
      .catch(() => {})
      .finally(() => setRecLoading(false))
  }, [patientId])

  const handleSaveRec = async () => {
    setSavingRec(true)
    try {
      const saved = await therapistApi.setRecommendation(patientId, {
        recommended_objective: objective || null,
        weekly_sessions_target: weekly ? parseInt(weekly) : null,
        message: message || null,
      })
      setRec(saved)
      setRecSaved(true)
      setTimeout(() => setRecSaved(false), 2000)
    } catch {}
    finally { setSavingRec(false) }
  }

  const handleSavePalier = async () => {
    if (!selectedPalier) return
    setSavingPalier(true)
    try {
      await therapistApi.adjustPalier(patientId, selectedPalier)
      setPalierSaved(true)
      setTimeout(() => { setPalierSaved(false); onRefresh() }, 1500)
    } catch {}
    finally { setSavingPalier(false) }
  }

  const handleToggleActive = async () => {
    setTogglingActive(true)
    try {
      await therapistApi.toggleActive(patientId)
      onRefresh()
    } catch {}
    finally { setTogglingActive(false) }
  }

  const isActive = patient?.is_active ?? true

  return (
    <div className="space-y-5">

      {/* ── Recommandation ── */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-nc-accent" />
          <h3 className="text-sm font-semibold text-nc-text">Recommandation au patient</h3>
          {rec && <span className="ms-auto text-[10px] text-nc-muted">Dernière : {new Date(rec.created_at).toLocaleDateString('fr-FR')}</span>}
        </div>

        {recLoading ? (
          <div className="flex justify-center py-4">
            <span className="w-5 h-5 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
          </div>
        ) : (
          <div className="space-y-3">
            {/* Objectif recommandé */}
            <div className="space-y-1.5">
              <label className="text-xs text-nc-muted">Objectif conseillé</label>
              <div className="flex gap-2">
                {[
                  { val: 'concentration', label: 'Concentration', color: 'border-blue-500/50 text-blue-400 bg-blue-500/10' },
                  { val: 'relaxation',    label: 'Relaxation',    color: 'border-green-500/50 text-green-400 bg-green-500/10' },
                  { val: 'stress',        label: 'Anti-stress',   color: 'border-yellow-500/50 text-yellow-400 bg-yellow-500/10' },
                ].map(({ val, label, color }) => (
                  <button
                    key={val}
                    onClick={() => setObjective(o => o === val ? '' : val)}
                    className={`flex-1 py-2 rounded-xl text-xs font-semibold border transition-all
                      ${objective === val ? color : 'border-nc-border text-nc-muted hover:text-nc-text'}`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Sessions/semaine */}
            <div className="space-y-1.5">
              <label className="text-xs text-nc-muted">Objectif sessions / semaine</label>
              <div className="flex gap-2">
                {['1','2','3','4','5'].map(n => (
                  <button
                    key={n}
                    onClick={() => setWeekly(w => w === n ? '' : n)}
                    className={`w-9 h-9 rounded-xl text-sm font-semibold border transition-all
                      ${weekly === n
                        ? 'bg-nc-accent/15 border-nc-accent text-nc-accent'
                        : 'border-nc-border text-nc-muted hover:text-nc-text'}`}
                  >
                    {n}
                  </button>
                ))}
              </div>
            </div>

            {/* Message */}
            <div className="space-y-1.5">
              <label className="text-xs text-nc-muted">Message (optionnel)</label>
              <textarea
                rows={2}
                value={message}
                onChange={e => setMessage(e.target.value)}
                placeholder="Encouragement, conseil, remarque…"
                className="input w-full resize-none text-sm"
                maxLength={500}
              />
            </div>

            <button
              onClick={handleSaveRec}
              disabled={savingRec}
              className="btn-primary flex items-center gap-2 px-4 py-2 rounded-xl text-sm disabled:opacity-60"
            >
              {recSaved ? <><Check className="w-3.5 h-3.5" /> Envoyée</> : savingRec ? 'Envoi…' : 'Envoyer la recommandation'}
            </button>
          </div>
        )}
      </div>

      {/* ── Ajuster le palier ── */}
      <div className="card p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Settings2 className="w-4 h-4 text-nc-accent" />
          <h3 className="text-sm font-semibold text-nc-text">Ajuster le palier de difficulté</h3>
        </div>
        <div className="space-y-2">
          <div className="grid grid-cols-2 gap-2">
            {PALIER_OPTIONS.map(({ value, label }) => {
              const color = PALIER_COLORS[value]
              return (
                <button
                  key={value}
                  onClick={() => setSelectedPalier(value)}
                  className={`py-2.5 rounded-xl text-sm font-semibold border transition-all
                    ${selectedPalier === value
                      ? 'text-white border-transparent'
                      : 'border-nc-border text-nc-muted hover:text-nc-text'}`}
                  style={selectedPalier === value ? { background: color, borderColor: color } : {}}
                >
                  {label}
                </button>
              )
            })}
          </div>
          <button
            onClick={handleSavePalier}
            disabled={!selectedPalier || savingPalier}
            className="btn-primary flex items-center gap-2 px-4 py-2 rounded-xl text-sm disabled:opacity-60 w-full justify-center"
          >
            {palierSaved ? <><Check className="w-3.5 h-3.5" /> Palier mis à jour</> : savingPalier ? 'Mise à jour…' : 'Appliquer le palier'}
          </button>
        </div>
      </div>

      {/* ── Activer / désactiver ── */}
      <div className={`card p-5 flex items-center gap-4 ${!isActive ? 'border-nc-danger/30 bg-nc-danger/5' : ''}`}>
        <div className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 ${isActive ? 'bg-green-500/10' : 'bg-nc-danger/10'}`}>
          {isActive ? <UserCheck className="w-5 h-5 text-green-400" /> : <UserX className="w-5 h-5 text-nc-danger" />}
        </div>
        <div className="flex-1">
          <p className="text-sm font-semibold text-nc-text">
            Compte {isActive ? 'actif' : 'désactivé'}
          </p>
          <p className="text-xs text-nc-muted">
            {isActive
              ? 'Le patient peut se connecter et lancer des sessions.'
              : 'Le patient ne peut plus se connecter à l\'application.'}
          </p>
        </div>
        <button
          onClick={handleToggleActive}
          disabled={togglingActive}
          className={`px-4 py-2 rounded-xl text-sm font-semibold transition-all disabled:opacity-60
            ${isActive
              ? 'bg-nc-danger/10 text-nc-danger hover:bg-nc-danger/20 border border-nc-danger/30'
              : 'bg-green-500/10 text-green-400 hover:bg-green-500/20 border border-green-500/30'}`}
        >
          {togglingActive ? '…' : isActive ? 'Désactiver' : 'Réactiver'}
        </button>
      </div>
    </div>
  )
}

/* ─── main page ──────────────────────────────────────────────────────────── */
export default function TherapistPatientDetail() {
  const { patientId } = useParams()
  const navigate = useNavigate()

  const [patient,   setPatient]   = useState(null)
  const [sessions,  setSessions]  = useState([])
  const [profile,   setProfile]   = useState(null)
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState('')
  const [tab,       setTab]       = useState('overview')
  const [exporting, setExporting] = useState(false)

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    const [info, sess, prof] = await Promise.allSettled([
      therapistApi.patientInfo(patientId),
      therapistApi.patientSessions(patientId, 100),
      therapistApi.patientProfile(patientId),
    ])
    if (info.status === 'fulfilled') setPatient(info.value)
    if (sess.status === 'fulfilled') setSessions(sess.value)
    if (prof.status === 'fulfilled') setProfile(prof.value)
    const denied = [info, sess].find(r => r.status === 'rejected' && r.reason?.response?.status === 403)
    if (denied) setError('Accès refusé — ce patient ne vous est pas assigné.')
    setLoading(false)
  }, [patientId])

  useEffect(() => { load() }, [load])

  const handleExport = async () => {
    setExporting(true)
    try {
      const res = await therapistApi.exportPatient(patientId)
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `neurocap_patient_${patientId}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch {}
    finally { setExporting(false) }
  }

  /* Quick stats from loaded sessions */
  const completed   = sessions.filter(s => s.status === 'completed')
  const scores      = completed.map(s => s.score).filter(x => x !== null && x !== undefined)
  const avgScore    = scores.length ? Math.round(scores.reduce((a, b) => a + b, 0) / scores.length) : null
  const lastSession = sessions[0] ?? null
  let evolution = null
  if (scores.length >= 2) {
    const first = scores[scores.length - 1]
    const last  = scores[0]
    if (first) evolution = Math.round((last - first) / first * 100)
  }

  const TABS = [
    { key: 'overview', label: 'Vue d\'ensemble' },
    { key: 'sessions', label: `Sessions (${sessions.length})` },
    { key: 'actions',  label: 'Actions' },
    { key: 'notes',    label: 'Notes cliniques' },
  ]

  const palierLabel = profile?.palier
    ? PALIER_OPTIONS.find(p => p.value === profile.palier)?.label ?? profile.palier
    : null
  const profileInfo = profile?.profile_type ? PROFILE_INFO[profile.profile_type] : null

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-8 space-y-6">

      {/* ── Back + header ── */}
      <div className="flex items-start gap-4">
        <button
          onClick={() => navigate('/therapist')}
          className="mt-1 p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors shrink-0"
        >
          <ArrowLeft className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 flex-1 min-w-0">
          {patient && (
            <div className={`w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold text-white shrink-0 ${!patient.is_active ? 'opacity-50' : ''}`}
                 style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.5))' }}>
              {patient.first_name
                ? `${patient.first_name[0]}${patient.last_name?.[0] ?? ''}`.toUpperCase()
                : (patient.email || '?')[0].toUpperCase()}
            </div>
          )}
          <div className="min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h1 className="text-2xl font-bold text-nc-text truncate">
                {patient
                  ? (patient.first_name && patient.last_name
                      ? `${patient.first_name} ${patient.last_name}`
                      : patient.email)
                  : 'Détail patient'}
              </h1>
              {patient && !patient.is_active && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-nc-danger/10 text-nc-danger border border-nc-danger/30">Inactif</span>
              )}
            </div>
            <p className="text-xs text-nc-muted mt-0.5">
              {patient?.email}
              {patient?.created_at && <span> · Inscrit {new Date(patient.created_at).toLocaleDateString('fr-FR')}</span>}
              {profile?.profile_type && <span className="text-nc-accent"> · Type {profile.profile_type}</span>}
              {palierLabel && <span> · {palierLabel}</span>}
            </p>
          </div>
        </div>

        <button
          onClick={handleExport}
          disabled={exporting || sessions.length === 0}
          className="btn-ghost flex items-center gap-2 px-4 py-2 rounded-xl text-sm text-nc-muted hover:text-nc-text border border-nc-border disabled:opacity-40 shrink-0"
        >
          <Download className="w-4 h-4" />
          {exporting ? 'Export…' : 'CSV'}
        </button>
      </div>

      {error && (
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm">
          <AlertTriangle className="w-4 h-4 shrink-0" />{error}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center py-20">
          <span className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          {/* ── KPI chips ── */}
          <div className="flex flex-wrap gap-3">
            <InfoChip label="Sessions" value={sessions.length} />
            <InfoChip label="Score moyen" value={avgScore !== null ? `${avgScore}%` : null} color="text-nc-accent" />
            <InfoChip
              label="Évolution"
              value={evolution !== null ? (evolution > 0 ? `+${evolution}%` : `${evolution}%`) : null}
              color={evolution === null ? 'text-nc-muted' : evolution > 0 ? 'text-green-400' : 'text-nc-danger'}
            />
            {lastSession?.created_at && (
              <InfoChip label="Dernière session" value={new Date(lastSession.created_at).toLocaleDateString('fr-FR')} />
            )}
            {patient?.avg_score_last5 !== undefined && patient?.avg_score_last5 !== null && (
              <InfoChip label="Moy. 5 dern." value={`${patient.avg_score_last5}%`} color="text-nc-accent" />
            )}
          </div>

          {/* ── Tabs ── */}
          <div className="flex gap-1 border-b border-nc-border overflow-x-auto">
            {TABS.map(({ key, label }) => (
              <button
                key={key}
                onClick={() => setTab(key)}
                className={`px-4 py-2.5 text-sm font-medium border-b-2 transition-all -mb-px whitespace-nowrap
                            ${tab === key ? 'border-nc-accent text-nc-accent' : 'border-transparent text-nc-muted hover:text-nc-text'}`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* ══ TAB: Overview ══ */}
          {tab === 'overview' && (
            <div className="space-y-4">
              {/* EEG Profile card */}
              {profile ? (
                <div className="card p-5 space-y-4">
                  <div className="flex items-center gap-2">
                    <Brain className="w-4 h-4 text-nc-accent" />
                    <h3 className="text-sm font-semibold text-nc-text">Profil EEG cognitif</h3>
                    <span className="ms-auto text-xs text-nc-muted">Lecture seule</span>
                  </div>

                  {profileInfo && (
                    <div className={`rounded-xl px-4 py-3 border flex items-center gap-3 ${profileInfo.bg} ${profileInfo.border}`}>
                      <span className={`text-2xl font-black ${profileInfo.color}`}>Type {profile.profile_type}</span>
                      <span className={`text-sm font-medium ${profileInfo.color} opacity-80`}>— {profileInfo.label}</span>
                    </div>
                  )}

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {[
                      { label: 'IAPF', value: profile.iapf !== null ? `${profile.iapf?.toFixed(1)} Hz` : '—', color: 'text-nc-accent' },
                      { label: 'TBR baseline', value: profile.baseline_tbr?.toFixed(2) ?? '—', color: 'text-yellow-400' },
                      { label: 'Alpha baseline', value: profile.baseline_alpha?.toFixed(2) ?? '—', color: 'text-nc-accent' },
                      { label: 'Réactivité', value: profile.reactivity_score?.toFixed(2) ?? '—', color: 'text-green-400' },
                    ].map(({ label, value, color }) => (
                      <div key={label} className="bg-nc-surface2 rounded-xl p-3 text-center">
                        <p className={`text-base font-bold font-mono ${color}`}>{value}</p>
                        <p className="text-[10px] text-nc-muted mt-0.5">{label}</p>
                      </div>
                    ))}
                  </div>

                  {/* Palier progress */}
                  {profile.palier && (
                    <div className="pt-2 border-t border-nc-border space-y-2">
                      <p className="text-xs text-nc-muted uppercase tracking-wider font-semibold">Palier actuel</p>
                      <PalierProgressBar palier={profile.palier} />
                    </div>
                  )}
                </div>
              ) : (
                <div className="card p-8 text-center">
                  <Brain className="w-10 h-10 mx-auto mb-3 opacity-20 text-nc-muted" />
                  <p className="text-nc-muted text-sm">Profil EEG non calibré</p>
                </div>
              )}

              {/* Score evolution chart */}
              {completed.length > 0 && (
                <div className="card p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-nc-accent" />
                    <h3 className="text-sm font-semibold text-nc-text">Évolution au fil des sessions</h3>
                  </div>
                  <ScoreChart sessions={sessions} />
                </div>
              )}
            </div>
          )}

          {/* ══ TAB: Sessions ══ */}
          {tab === 'sessions' && (
            <div className="space-y-4">
              {completed.length > 0 && (
                <div className="card p-5 space-y-3">
                  <div className="flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-nc-accent" />
                    <h3 className="text-sm font-semibold text-nc-text">Courbes d'évolution</h3>
                  </div>
                  <ScoreChart sessions={sessions} />
                </div>
              )}
              <div className="card overflow-hidden">
                <div className="px-4 py-3 border-b border-nc-border flex items-center gap-2">
                  <Activity className="w-4 h-4 text-nc-muted" />
                  <p className="text-sm font-semibold text-nc-text">Historique complet des sessions</p>
                  <span className="ms-auto text-xs text-nc-muted">{sessions.length} session(s)</span>
                </div>
                <SessionsTable sessions={sessions} />
              </div>
            </div>
          )}

          {/* ══ TAB: Actions ══ */}
          {tab === 'actions' && (
            <ActionsPanel
              patientId={patientId}
              patient={patient}
              profile={profile}
              onRefresh={load}
            />
          )}

          {/* ══ TAB: Notes ══ */}
          {tab === 'notes' && (
            <div className="card p-5">
              <div className="flex items-center gap-2 mb-4">
                <MessageSquareText className="w-4 h-4 text-nc-muted" />
                <h3 className="text-sm font-semibold text-nc-text">Notes cliniques privées</h3>
              </div>
              <NotesPanel patientId={patientId} />
            </div>
          )}
        </>
      )}
    </div>
  )
}
