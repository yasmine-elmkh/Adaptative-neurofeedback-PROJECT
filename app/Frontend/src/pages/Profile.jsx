import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { profile as profileApi, sessions as sessionsApi, auth as authApi } from '../utils/api'
import { useAuthStore } from '../stores'
import {
  User, Brain, Zap, Target, Activity, RefreshCw, ShieldCheck, CalendarDays,
  TrendingUp, Award, BarChart3, Users, Mail, BadgeCheck, KeyRound, Eye, EyeOff, Check,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'

// ── Constants ─────────────────────────────────────────────────────────────────
const PALIERS = [
  { key: 'P1_INITIATION',    label: 'P1 – Initiation',    sessions: '1-5',   maxSessions: 5  },
  { key: 'P2_APPRENTISSAGE', label: 'P2 – Apprentissage', sessions: '6-10',  maxSessions: 10 },
  { key: 'P3_MAITRISE',      label: 'P3 – Maîtrise',      sessions: '11-13', maxSessions: 13 },
  { key: 'P4_AUTONOMIE',     label: 'P4 – Autonomie',     sessions: '14+',   maxSessions: 15 },
]
const PALIER_KEYS_COMPAT = {
  P1: 'P1_INITIATION', P2: 'P2_APPRENTISSAGE', P3: 'P3_MAITRISE', P4: 'P4_AUTONOMIE',
}
const PROFILE_INFO = {
  A: { label: 'Très réactif',     desc: 'Alpha robuste, réactivité élevée. Neurofeedback efficace dès les premières sessions.' },
  B: { label: 'Standard',          desc: 'Profil équilibré. Protocole standard NeuroCap sur 15 sessions.' },
  C: { label: 'Faible réactivité', desc: 'Alpha peu marqué. Seuil réduit, progression plus graduelle recommandée.' },
}

// ── Sub-components ─────────────────────────────────────────────────────────────
function MetricCard({ icon: Icon, label, value, desc, color = 'text-nc-accent' }) {
  return (
    <div className="card p-4 space-y-2">
      <div className="flex items-center gap-2">
        <Icon className={`w-4 h-4 ${color}`} />
        <span className="text-xs text-nc-muted uppercase tracking-wider">{label}</span>
      </div>
      <p className={`text-2xl font-bold font-mono ${color}`}>{value}</p>
      <p className="text-[11px] text-nc-muted leading-snug">{desc}</p>
    </div>
  )
}

function IAPFSpectrum({ iapf, baselineAlpha, baselineBeta, baselineTheta }) {
  if (!baselineAlpha && !baselineBeta && !baselineTheta) return null
  const bands = [
    { name: 'Delta\n(1-4)',  power: 0.5,              color: '#6b7280' },
    { name: 'Theta\n(4-8)',  power: baselineTheta ?? 0, color: 'rgb(var(--nc-warning))' },
    { name: 'Alpha\n(8-13)', power: baselineAlpha ?? 0, color: 'rgb(var(--nc-accent))' },
    { name: 'Beta\n(13-30)', power: baselineBeta  ?? 0, color: 'rgb(var(--nc-success))' },
    { name: 'Gamma\n(30+)',  power: 0.2,              color: '#6b7280' },
  ]
  const CustomBar = ({ x, y, width, height, color }) => (
    <rect x={x} y={y} width={width} height={height} fill={color} rx={3} />
  )
  return (
    <div className="card p-5 space-y-3">
      <div className="flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-nc-accent" />
        <h3 className="text-sm font-semibold text-nc-text">Spectre EEG de référence</h3>
        {iapf && (
          <span className="ms-auto text-xs text-nc-accent font-mono font-semibold">
            IAPF = {iapf.toFixed(1)} Hz
          </span>
        )}
      </div>
      <ResponsiveContainer width="100%" height={140}>
        <BarChart data={bands} margin={{ top: 4, right: 4, bottom: 0, left: -28 }}>
          <XAxis dataKey="name" tick={{ fill: 'rgb(var(--nc-muted))', fontSize: 10 }}
                 axisLine={false} tickLine={false} interval={0} />
          <YAxis tick={{ fill: 'rgb(var(--nc-muted))', fontSize: 10 }} axisLine={false} tickLine={false} />
          <Tooltip formatter={(v) => [`${v.toFixed(3)} µV²/Hz`, 'Puissance']}
                   contentStyle={{ background: 'rgb(var(--nc-surface))', border: '1px solid rgb(var(--nc-border))', borderRadius: 8, fontSize: 11 }} />
          <Bar dataKey="power" radius={[3, 3, 0, 0]} shape={<CustomBar />}>
            {bands.map((b, i) => <Cell key={i} fill={b.color} />)}
          </Bar>
          {iapf && (
            <ReferenceLine x="Alpha\n(8-13)" stroke="rgb(var(--nc-accent))" strokeDasharray="3 3"
              label={{ value: `IAPF ${iapf.toFixed(1)}Hz`, position: 'top', fill: 'rgb(var(--nc-accent))', fontSize: 9 }} />
          )}
        </BarChart>
      </ResponsiveContainer>
      <div className="flex items-center gap-4 text-[10px] text-nc-muted flex-wrap">
        {[{ label: 'Theta', color: 'bg-nc-warning' }, { label: 'Alpha', color: 'bg-nc-accent' }, { label: 'Beta', color: 'bg-nc-success' }]
          .map(({ label, color }) => (
            <span key={label} className="flex items-center gap-1">
              <span className={`w-2.5 h-2.5 rounded-sm ${color}`} />{label}
            </span>
          ))}
      </div>
    </div>
  )
}

function PalierProgress({ sessionCount, palierKey }) {
  const normalizedKey = PALIER_KEYS_COMPAT[palierKey] ?? palierKey
  const currentIdx    = PALIERS.findIndex(p => p.key === normalizedKey)
  const current       = PALIERS[currentIdx] ?? PALIERS[0]
  const next          = PALIERS[currentIdx + 1]
  const progress      = next
    ? Math.min(100, ((sessionCount - (currentIdx * 5)) / 5) * 100)
    : 100

  return (
    <div className="card p-6 space-y-5">
      <div className="flex items-center gap-2">
        <Activity className="w-4 h-4 text-nc-accent" />
        <h3 className="font-semibold text-nc-text text-sm">Progression du protocole</h3>
        <span className="ms-auto badge-muted">{sessionCount} session(s)</span>
      </div>
      <div className="flex items-center gap-0">
        {PALIERS.map((p, i) => {
          const done   = i < currentIdx
          const active = i === currentIdx
          return (
            <div key={p.key} className="flex items-center flex-1 last:flex-none">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 transition-all
                              ${done   ? 'bg-nc-success text-white'
                              : active ? 'bg-nc-accent text-white shadow-accent'
                              : 'bg-nc-surface2 text-nc-muted border border-nc-border'}`}>
                {done ? '✓' : i + 1}
              </div>
              {i < PALIERS.length - 1 && (
                <div className={`h-0.5 flex-1 mx-1 rounded-full transition-all ${done ? 'bg-nc-success' : 'bg-nc-border'}`} />
              )}
            </div>
          )
        })}
      </div>
      <div className="grid grid-cols-4 gap-1 text-[10px]">
        {PALIERS.map((p, i) => (
          <div key={p.key} className={`text-center ${i === currentIdx ? 'text-nc-accent font-semibold' : 'text-nc-muted'}`}>
            {p.label}
          </div>
        ))}
      </div>
      {next ? (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs text-nc-muted">
            <span>Vers {next.label}</span>
            <span className="font-semibold text-nc-accent">{Math.round(progress)}%</span>
          </div>
          <div className="h-2 bg-nc-border rounded-full overflow-hidden">
            <div className="h-full rounded-full bg-nc-accent transition-all duration-700" style={{ width: `${progress}%` }} />
          </div>
          <p className="text-[10px] text-nc-muted">{next.sessions} sessions requises pour {next.label}</p>
        </div>
      ) : (
        <div className="flex items-center gap-2 text-nc-success text-sm font-semibold">
          <Award className="w-4 h-4" />
          Protocole complet ! Niveau Autonomie atteint.
        </div>
      )}
    </div>
  )
}

/* ── Password change section (all roles) ─────────────────────────────────── */
function PasswordChangeSection() {
  const [open,     setOpen]     = useState(false)
  const [current,  setCurrent]  = useState('')
  const [next,     setNext]     = useState('')
  const [confirm,  setConfirm]  = useState('')
  const [showPwd,  setShowPwd]  = useState(false)
  const [saving,   setSaving]   = useState(false)
  const [success,  setSuccess]  = useState(false)
  const [error,    setError]    = useState('')

  const reset = () => { setCurrent(''); setNext(''); setConfirm(''); setError(''); setSuccess(false) }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    if (next !== confirm) { setError('Les mots de passe ne correspondent pas'); return }
    if (next.length < 8)  { setError('Le nouveau mot de passe doit contenir au moins 8 caractères'); return }
    setSaving(true)
    try {
      await authApi.changePassword(current, next)
      setSuccess(true)
      reset()
      setTimeout(() => { setOpen(false); setSuccess(false) }, 2000)
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'Erreur lors du changement de mot de passe')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => { setOpen(o => !o); reset() }}
        className="flex items-center gap-3 w-full px-5 py-4 hover:bg-nc-surface2 transition-colors"
      >
        <KeyRound className="w-4 h-4 text-nc-muted" />
        <span className="text-sm font-medium text-nc-text flex-1 text-start">Changer le mot de passe</span>
        <span className={`text-xs text-nc-muted transition-transform ${open ? 'rotate-180' : ''}`}>▾</span>
      </button>

      {open && (
        <form onSubmit={handleSubmit} className="px-5 pb-5 space-y-3 border-t border-nc-border">
          {success && (
            <div className="flex items-center gap-2 text-green-400 text-sm py-2">
              <Check className="w-4 h-4" />Mot de passe modifié avec succès
            </div>
          )}
          {error && <p className="text-nc-danger text-xs py-1">{error}</p>}

          {[
            { label: 'Mot de passe actuel', val: current, set: setCurrent },
            { label: 'Nouveau mot de passe', val: next, set: setNext },
            { label: 'Confirmer le nouveau', val: confirm, set: setConfirm },
          ].map(({ label, val, set }) => (
            <div key={label} className="space-y-1">
              <label className="text-xs text-nc-muted">{label}</label>
              <div className="relative">
                <input
                  type={showPwd ? 'text' : 'password'}
                  value={val}
                  onChange={e => set(e.target.value)}
                  required
                  className="input w-full pe-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPwd(s => !s)}
                  className="absolute end-3 top-1/2 -translate-y-1/2 text-nc-muted hover:text-nc-text"
                  tabIndex={-1}
                >
                  {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          ))}

          <div className="flex gap-2 pt-1">
            <button
              type="submit"
              disabled={saving}
              className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm disabled:opacity-60"
            >
              {saving ? 'Enregistrement…' : 'Mettre à jour'}
            </button>
            <button
              type="button"
              onClick={() => { setOpen(false); reset() }}
              className="btn-ghost px-4 py-2 rounded-xl text-sm text-nc-muted"
            >
              Annuler
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

/* ── Therapist profile view (no EEG data) ──────────────────────────────────── */
function TherapistProfile({ user }) {
  const infoRows = [
    { icon: Mail,       label: 'Email',         value: user?.email },
    { icon: BadgeCheck, label: 'Rôle',          value: 'Thérapeute' },
    { icon: User,       label: 'Nom complet',   value: user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : '—' },
    { icon: CalendarDays, label: 'Membre depuis', value: user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' }) : '—' },
  ]

  return (
    <div className="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      <h1 className="text-3xl font-bold text-nc-text">Mon profil</h1>

      {/* Avatar card */}
      <div className="card p-6 flex items-center gap-5">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shrink-0"
             style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.5))' }}>
          {(user?.first_name || user?.email || 'T').charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-lg font-bold text-nc-text truncate">
            {user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.email}
          </p>
          <p className="text-sm text-nc-muted">{user?.email}</p>
          <span className="inline-flex items-center gap-1.5 mt-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-green-500/15 text-green-400 border border-green-500/30">
            <Users className="w-3 h-3" />
            Thérapeute
          </span>
        </div>
      </div>

      {/* Info rows */}
      <div className="card divide-y divide-nc-border overflow-hidden">
        {infoRows.map(({ icon: Icon, label, value }) => (
          <div key={label} className="flex items-center gap-4 px-5 py-4">
            <Icon className="w-4 h-4 text-nc-muted shrink-0" />
            <span className="text-xs text-nc-muted w-28 shrink-0">{label}</span>
            <span className="text-sm font-medium text-nc-text">{value}</span>
          </div>
        ))}
      </div>

      {/* Notice */}
      <div className="card p-5 flex items-start gap-4 border-nc-border">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-green-500/10 shrink-0">
          <Brain className="w-4 h-4 text-green-400" />
        </div>
        <div>
          <p className="text-sm font-semibold text-nc-text">Compte thérapeute</p>
          <p className="text-sm text-nc-muted mt-1">
            Ce compte est dédié au suivi clinique de vos patients. Les données EEG et de calibration
            ne s'appliquent pas aux thérapeutes — elles sont propres à chaque patient.
          </p>
          <p className="text-xs text-nc-muted mt-2">
            Pour consulter les données EEG d'un patient, rendez-vous dans l'onglet <strong>Mes patients</strong>.
          </p>
        </div>
      </div>

      <PasswordChangeSection />
    </div>
  )
}

/* ── Admin profile view ────────────────────────────────────────────────────── */
function AdminProfile({ user }) {
  const infoRows = [
    { icon: Mail,         label: 'Email',         value: user?.email },
    { icon: BadgeCheck,   label: 'Rôle',          value: 'Administrateur' },
    { icon: User,         label: 'Nom complet',   value: user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : '—' },
    { icon: CalendarDays, label: 'Membre depuis', value: user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' }) : '—' },
  ]

  return (
    <div className="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      <h1 className="text-3xl font-bold text-nc-text">Mon profil</h1>

      <div className="card p-6 flex items-center gap-5">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shrink-0"
             style={{ background: 'linear-gradient(135deg, #a855f7, rgba(168,85,247,0.5))' }}>
          {(user?.first_name || user?.email || 'A').charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-lg font-bold text-nc-text truncate">
            {user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.email}
          </p>
          <p className="text-sm text-nc-muted">{user?.email}</p>
          <span className="inline-flex items-center gap-1.5 mt-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/15 text-purple-400 border border-purple-500/30">
            Administrateur
          </span>
        </div>
      </div>

      <div className="card divide-y divide-nc-border overflow-hidden">
        {infoRows.map(({ icon: Icon, label, value }) => (
          <div key={label} className="flex items-center gap-4 px-5 py-4">
            <Icon className="w-4 h-4 text-nc-muted shrink-0" />
            <span className="text-xs text-nc-muted w-28 shrink-0">{label}</span>
            <span className="text-sm font-medium text-nc-text">{value}</span>
          </div>
        ))}
      </div>

      <PasswordChangeSection />
    </div>
  )
}

// ── Main ──────────────────────────────────────────────────────────────────────
export default function Profile() {
  const { t }    = useTranslation()
  const { user } = useAuthStore()
  const role     = user?.role ?? 'patient'

  const [profileData,   setProfileData]   = useState(null)
  const [sessionCount,  setSessionCount]  = useState(0)
  const [loading,       setLoading]       = useState(true)
  const [calibrating,   setCalibrating]   = useState(false)

  useEffect(() => {
    if (role !== 'patient') {
      setLoading(false)
      return
    }
    Promise.all([
      profileApi.get(),
      sessionsApi.list().catch(() => []),
    ]).then(([prof, sess]) => {
      setProfileData(prof)
      setSessionCount(Array.isArray(sess) ? sess.filter(s => s.status === 'completed').length : 0)
    }).catch(() => {})
      .finally(() => setLoading(false))
  }, [role])

  const handleRecalibrate = async () => {
    setCalibrating(true)
    try {
      const result = await profileApi.calibrate({
        iapf: 10.0 + Math.random() * 2 - 1,
        baseline_tbr: 2.5 + Math.random(),
        baseline_alpha: 15 + Math.random() * 10,
        baseline_beta:  8 + Math.random() * 5,
        baseline_theta: 10 + Math.random() * 8,
        reactivity_score: 0.3 + Math.random() * 0.6,
      })
      setProfileData(result)
    } catch (err) {
      alert(err?.response?.data?.detail ?? err.message)
    } finally {
      setCalibrating(false)
    }
  }

  /* ── Role-specific views ── */
  if (role === 'therapist') return <TherapistProfile user={user} />
  if (role === 'admin')     return <AdminProfile user={user} />

  /* ── Patient view ── */
  if (loading) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="w-8 h-8 border-2 border-nc-accent border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const profileType = profileData?.profile_type ?? null
  const palierKey   = profileData?.palier ?? 'P1'
  const info        = profileType ? (PROFILE_INFO[profileType] ?? PROFILE_INFO.B) : null
  const colorMap    = { A: 'text-nc-success', B: 'text-nc-accent', C: 'text-nc-warning' }
  const color       = colorMap[profileType] ?? 'text-nc-accent'

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">

      <h1 className="text-3xl font-bold text-nc-text">{t('profile.title')}</h1>

      {/* ── User info ── */}
      <div className="card p-6 flex items-center gap-5">
        <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-white text-2xl font-bold shrink-0"
             style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.5))' }}>
          {(user?.first_name || user?.email || 'U').charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0 flex-1">
          <p className="text-lg font-bold text-nc-text truncate">
            {user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : user?.email}
          </p>
          <p className="text-sm text-nc-muted truncate">{user?.email}</p>
          <div className="flex items-center gap-3 mt-1.5 flex-wrap">
            <span className="badge-muted capitalize">{user?.role ?? 'patient'}</span>
            {user?.created_at && (
              <span className="text-xs text-nc-muted flex items-center gap-1">
                <CalendarDays className="w-3 h-3" />
                Depuis {new Date(user.created_at).toLocaleDateString()}
              </span>
            )}
          </div>
        </div>
      </div>

      {/* ── EEG Profile (patients only) ── */}
      <div className="card p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-nc-muted text-xs uppercase tracking-wider font-semibold">
            <Brain className="w-3.5 h-3.5" />
            Profil EEG cognitif
          </div>
          <button onClick={handleRecalibrate} disabled={calibrating} className="btn-ghost flex items-center gap-2 text-xs">
            <RefreshCw className={`w-3.5 h-3.5 ${calibrating ? 'animate-spin' : ''}`} />
            {calibrating ? 'Calibration…' : t('profile.recalibrate')}
          </button>
        </div>

        {profileType ? (
          <>
            <div className="rounded-2xl p-5 border"
                 style={{ background: 'rgb(var(--nc-accent)/0.07)', borderColor: 'rgb(var(--nc-accent)/0.25)' }}>
              <div className="flex items-center gap-3 mb-2">
                <span className={`text-3xl font-black ${color}`}>Type {profileType}</span>
                <span className={`text-sm font-semibold ${color} opacity-80`}>— {info.label}</span>
              </div>
              <p className="text-sm text-nc-muted leading-relaxed">{info.desc}</p>
              {profileData?.calibrated_at && (
                <p className="text-[10px] text-nc-muted mt-2 flex items-center gap-1">
                  <CalendarDays className="w-3 h-3" />
                  Calibré le {new Date(profileData.calibrated_at).toLocaleString()}
                </p>
              )}
            </div>
            <div className="grid grid-cols-2 gap-4">
              <MetricCard icon={Activity}   color={color} label="IAPF"          value={`${profileData.iapf?.toFixed(1) ?? '—'} Hz`} desc="Fréquence de pic alpha individuelle." />
              <MetricCard icon={Zap}        color={color} label="Alpha baseline" value={profileData.baseline_alpha?.toFixed(2) ?? '—'} desc="Puissance alpha de repos (µV²/Hz)." />
              <MetricCard icon={Target}     color={color} label="TBR baseline"   value={profileData.baseline_tbr?.toFixed(2) ?? '—'}   desc="Ratio theta/beta de repos." />
              <MetricCard icon={ShieldCheck} color={color} label="Réactivité"    value={profileData.reactivity_score?.toFixed(2) ?? '—'} desc="Score de réactivité alpha (0→1)." />
            </div>
            <IAPFSpectrum
              iapf={profileData.iapf}
              baselineAlpha={profileData.baseline_alpha}
              baselineBeta={profileData.baseline_beta}
              baselineTheta={profileData.baseline_theta}
            />
          </>
        ) : (
          <div className="text-center py-12 space-y-3">
            <div className="w-14 h-14 rounded-full bg-nc-surface2 flex items-center justify-center mx-auto">
              <Brain className="w-7 h-7 text-nc-muted" />
            </div>
            <p className="font-semibold text-nc-text">{t('profile.no_profile')}</p>
            <p className="text-sm text-nc-muted">{t('profile.no_profile_sub')}</p>
            <button onClick={handleRecalibrate} disabled={calibrating} className="btn-primary mt-2">
              {calibrating ? t('profile.calibrating') : t('profile.launch_calibration')}
            </button>
          </div>
        )}
      </div>

      {/* ── Palier progress ── */}
      <PalierProgress sessionCount={sessionCount} palierKey={palierKey} />

      {/* ── Recommendation ── */}
      {profileType && (
        <div className="card p-5 flex items-start gap-4">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-nc-accent/15 shrink-0">
            <TrendingUp className="w-4 h-4 text-nc-accent" />
          </div>
          <div>
            <p className="text-sm font-semibold text-nc-text mb-1">Recommandation personnalisée</p>
            <p className="text-sm text-nc-muted">
              {profileType === 'A' && 'Votre réactivité alpha est excellente. Augmentez progressivement la durée des sessions.'}
              {profileType === 'B' && 'Protocole standard recommandé. Maintenez 3 sessions / semaine pour consolider les progrès.'}
              {profileType === 'C' && 'TBR élevé détecté. Privilégiez les exercices de respiration abdominale avant chaque session.'}
            </p>
          </div>
        </div>
      )}

      <PasswordChangeSection />
    </div>
  )
}
