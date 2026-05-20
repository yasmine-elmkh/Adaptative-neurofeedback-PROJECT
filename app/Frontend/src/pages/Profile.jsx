import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { profile as profileApi, sessions as sessionsApi, auth as authApi, eeg as eegApi } from '../utils/api'
import { useAuthStore } from '../stores'
import {
  User, Brain, Zap, Target, Activity, RefreshCw, ShieldCheck, CalendarDays,
  TrendingUp, Award, BarChart3, Users, Mail, BadgeCheck, KeyRound,
  Eye, EyeOff, Check, Cpu, CheckCircle, Clock, AlertCircle,
} from 'lucide-react'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'

// ── Paliers ───────────────────────────────────────────────────────────────────
const PALIERS = [
  { key: 'P1_INITIATION',    label: 'P1 – Initiation',    sessions: '1-5',   maxSessions: 5  },
  { key: 'P2_APPRENTISSAGE', label: 'P2 – Apprentissage', sessions: '6-10',  maxSessions: 10 },
  { key: 'P3_MAITRISE',      label: 'P3 – Maîtrise',      sessions: '11-13', maxSessions: 13 },
  { key: 'P4_AUTONOMIE',     label: 'P4 – Autonomie',     sessions: '14+',   maxSessions: 15 },
]
const PALIER_KEYS_COMPAT = {
  P1: 'P1_INITIATION', P2: 'P2_APPRENTISSAGE', P3: 'P3_MAITRISE', P4: 'P4_AUTONOMIE',
}

// ── Profils A / B / C — complets ─────────────────────────────────────────────
const PROFILE_INFO = {
  A: {
    label:      'Très réactif',
    color:      'text-nc-success',
    bg:         'bg-nc-success/8',
    border:     'border-nc-success/25',
    gradient:   'from-nc-success/15 to-nc-success/5',
    sessions:   12,
    palierStart:'P2 (Apprentissage)',
    threshold:  '95% baseline',
    feedback:   'Sonore + visuel + jeu dès S2',
    criteria: [
      'Alpha / Beta > 1,5',
      'Réactivité alpha (ERD) > 30 %',
    ],
    desc: 'Alpha robuste, réactivité élevée. Le cerveau module déjà bien les ondes alpha — neurofeedback efficace dès les premières sessions, progression rapide attendue.',
    protocol: [
      { label: 'Phase découverte', value: 'S1–S2 (2 séances)' },
      { label: 'Seuils',          value: '95–110 % baseline' },
      { label: 'Feedback',        value: 'Sonore + visuel + jeu dès S2' },
      { label: 'Fine-tuning IA',  value: 'Optionnel à 1 mois' },
    ],
  },
  B: {
    label:      'Standard',
    color:      'text-nc-accent',
    bg:         'bg-nc-accent/8',
    border:     'border-nc-accent/25',
    gradient:   'from-nc-accent/15 to-nc-accent/5',
    sessions:   15,
    palierStart:'P1 (Initiation)',
    threshold:  '95% baseline',
    feedback:   'Sonore + visuel à partir de S3',
    criteria: [
      'Alpha / Beta compris entre 0,8 et 1,5',
      'Réactivité alpha (ERD) entre 15 % et 30 %',
    ],
    desc: 'Profil équilibré. Capacité de modulation présente mais nécessite de l\'entraînement. Protocole standard NeuroCap sur 15 sessions.',
    protocol: [
      { label: 'Phase découverte', value: 'S1–S3 (3 séances)' },
      { label: 'Seuils',          value: '85–95 % baseline' },
      { label: 'Feedback',        value: 'Sonore + visuel à partir de S3' },
      { label: 'Fine-tuning IA',  value: 'Recommandé à 1 mois' },
    ],
  },
  C: {
    label:      'Faible réactivité',
    color:      'text-nc-warning',
    bg:         'bg-nc-warning/8',
    border:     'border-nc-warning/25',
    gradient:   'from-nc-warning/15 to-nc-warning/5',
    sessions:   18,
    palierStart:'P1 (Initiation étendu)',
    threshold:  '70% baseline',
    feedback:   'Sonore uniquement — pas de jeu avant S8',
    criteria: [
      'Alpha / Beta < 0,8',
      'OU réactivité alpha (ERD) < 15 %',
    ],
    desc: 'Alpha peu marqué. Risque d\'appartenir aux ~38 % de non-répondeurs. Approche différenciée : seuil réduit, progression graduelle, fine-tuning IA obligatoire.',
    protocol: [
      { label: 'Phase découverte', value: 'S1–S5 (5 séances)' },
      { label: 'Seuils',          value: '70–85 % baseline' },
      { label: 'Feedback',        value: 'Sonore uniquement (jeu après S8)' },
      { label: 'Fine-tuning IA',  value: 'Obligatoire à 1 mois et 3 mois' },
    ],
  },
}

// ── MetricCard ────────────────────────────────────────────────────────────────
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

// ── IAPFSpectrum ──────────────────────────────────────────────────────────────
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

// ── ProfileTypeCard ───────────────────────────────────────────────────────────
function ProfileTypeCard({ profileType, profileData, info }) {
  const alphaBeta = profileData?.baseline_alpha && profileData?.baseline_beta
    ? (profileData.baseline_alpha / profileData.baseline_beta).toFixed(2)
    : null
  const reactivity = profileData?.reactivity_score
    ? Math.round(profileData.reactivity_score * 100)
    : null

  return (
    <div className={`rounded-2xl p-5 border bg-gradient-to-br ${info.gradient} ${info.border}`}>
      {/* En-tête */}
      <div className="flex items-start justify-between gap-3 mb-4">
        <div>
          <div className="flex items-baseline gap-2">
            <span className={`text-3xl font-black ${info.color}`}>Type {profileType}</span>
            <span className={`text-sm font-semibold ${info.color} opacity-80`}>— {info.label}</span>
          </div>
          <p className="text-sm text-nc-muted leading-relaxed mt-1 max-w-md">{info.desc}</p>
          {profileData?.calibrated_at && (
            <p className="text-[10px] text-nc-muted mt-2 flex items-center gap-1">
              <CalendarDays className="w-3 h-3" />
              Calibré le {new Date(profileData.calibrated_at).toLocaleString()}
            </p>
          )}
        </div>
      </div>

      {/* Critères de classification */}
      <div className="mb-4">
        <p className="text-xs text-nc-muted uppercase tracking-wider font-semibold mb-2">
          Critères de classification
        </p>
        <div className="space-y-1.5">
          {info.criteria.map((c, i) => {
            const measured = i === 0 ? alphaBeta : reactivity !== null ? `${reactivity} %` : null
            return (
              <div key={i} className="flex items-center gap-2 text-xs">
                <CheckCircle className={`w-3.5 h-3.5 shrink-0 ${info.color}`} />
                <span className="text-nc-text">{c}</span>
                {measured && (
                  <span className={`ms-auto font-mono font-bold ${info.color}`}>
                    {measured}
                  </span>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Impact protocole */}
      <div>
        <p className="text-xs text-nc-muted uppercase tracking-wider font-semibold mb-2">
          Impact sur le protocole
        </p>
        <div className="grid grid-cols-2 gap-2">
          {info.protocol.map(({ label, value }) => (
            <div key={label} className="bg-nc-surface/60 rounded-xl px-3 py-2.5">
              <p className="text-[10px] text-nc-muted">{label}</p>
              <p className="text-xs font-semibold text-nc-text mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

// ── ProfilesExplained ─────────────────────────────────────────────────────────
function ProfilesExplained({ currentType }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="card overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2 w-full px-5 py-4 hover:bg-nc-surface2 transition-colors text-start"
      >
        <Brain className="w-4 h-4 text-nc-muted" />
        <span className="text-sm font-medium text-nc-text flex-1">Comprendre les profils A / B / C</span>
        <span className={`text-xs text-nc-muted transition-transform duration-200 ${open ? 'rotate-180' : ''}`}>▾</span>
      </button>

      {open && (
        <div className="border-t border-nc-border px-5 pb-5 pt-4 space-y-4">
          <p className="text-xs text-nc-muted">
            Les profils sont déterminés automatiquement lors de la calibration initiale,
            à partir du ratio alpha/beta et de la réactivité alpha (ERD).
          </p>
          <div className="grid gap-3">
            {Object.entries(PROFILE_INFO).map(([type, info]) => (
              <div key={type}
                   className={`rounded-xl p-4 border ${info.border} ${info.bg}
                               ${currentType === type ? 'ring-1 ring-offset-1 ring-current' : ''}`}>
                <div className="flex items-center gap-2 mb-2">
                  <span className={`text-base font-black ${info.color}`}>Type {type}</span>
                  <span className={`text-xs font-semibold ${info.color}`}>— {info.label}</span>
                  {currentType === type && (
                    <span className="ms-auto text-[10px] font-bold text-nc-muted">← votre profil</span>
                  )}
                </div>
                <ul className="space-y-1">
                  {info.criteria.map((c, i) => (
                    <li key={i} className="text-[11px] text-nc-muted flex items-start gap-1.5">
                      <span className={`mt-0.5 font-bold ${info.color}`}>•</span>{c}
                    </li>
                  ))}
                </ul>
                <div className="mt-2 grid grid-cols-2 gap-1 text-[10px]">
                  <span className="text-nc-muted">Sessions recommandées :</span>
                  <span className={`font-semibold ${info.color}`}>{info.sessions}</span>
                  <span className="text-nc-muted">Seuil initial :</span>
                  <span className={`font-semibold ${info.color}`}>{info.threshold}</span>
                  <span className="text-nc-muted">Palier de départ :</span>
                  <span className={`font-semibold ${info.color}`}>{info.palierStart}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── AIModelStatus ─────────────────────────────────────────────────────────────
const FT_V1 = 2000
const FT_V2 = 4000

function AIModelStatus({ profileType }) {
  const [ft,      setFt]      = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    eegApi.finetuningStatus()
      .then(d => setFt(d))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  const isProfileC = profileType === 'C'

  if (loading) {
    return (
      <div className="card p-6 flex items-center gap-3">
        <div className="w-5 h-5 border-2 border-nc-accent border-t-transparent rounded-full animate-spin shrink-0" />
        <span className="text-sm text-nc-muted">Chargement du statut IA…</span>
      </div>
    )
  }

  const activity  = ft?.activity ?? {}
  const version   = ft?.finetuned_version ?? 0
  const hasModel  = !!ft?.finetuned_model_checkpoint
  const lastFtAt  = ft?.last_finetune_at
  const unused    = ft?.unused_reliable_epochs ?? 0
  const total     = ft?.total_reliable_epochs  ?? 0
  const lastJob   = ft?.last_job
  const daysIdle  = activity.days_idle ?? null
  const isActive  = activity.is_active ?? false
  const isLongAbs = daysIdle !== null && daysIdle > 30

  // ── Statut activité ───────────────────────────────────────────────────────
  const ActivityBanner = () => {
    if (!ft) return null
    if (isLongAbs) return (
      <div className="rounded-xl bg-nc-danger/8 border border-nc-danger/20 p-4 flex items-start gap-3">
        <AlertCircle className="w-4 h-4 text-nc-danger shrink-0 mt-0.5" />
        <div>
          <p className="text-xs font-semibold text-nc-danger">Inactif — Personnalisation désactivée</p>
          <p className="text-[11px] text-nc-muted mt-0.5">
            Dernière activité il y a {daysIdle} jours.
            Faites 3 nouvelles sessions pour relancer la collecte de données.
          </p>
        </div>
      </div>
    )
    if (!isActive) return (
      <div className="rounded-xl bg-nc-warning/8 border border-nc-warning/20 p-4 flex items-start gap-3">
        <Clock className="w-4 h-4 text-nc-warning shrink-0 mt-0.5" />
        <div>
          <p className="text-xs font-semibold text-nc-warning">En attente — Pas d'activité récente</p>
          <p className="text-[11px] text-nc-muted mt-0.5">
            {daysIdle !== null
              ? `Dernière activité il y a ${daysIdle} jour${daysIdle > 1 ? 's' : ''}.`
              : 'Aucune activité détectée.'}
            {' '}
            {Math.max(0, 3 - (activity.activity_total_30d ?? 0))} activité(s) de plus nécessaires
            pour activer la personnalisation (seuil : 3 / 30 jours).
          </p>
        </div>
      </div>
    )
    return (
      <div className="rounded-xl bg-nc-success/8 border border-nc-success/20 p-3 flex items-center gap-2 flex-wrap">
        <CheckCircle className="w-4 h-4 text-nc-success shrink-0" />
        <span className="text-xs font-semibold text-nc-success">Actif — Collecte en cours</span>
        <span className="text-[11px] text-nc-muted ms-auto">
          {activity.activity_total_30d ?? 0} activité(s) ce mois · {activity.reliable_epochs_30d ?? 0} nouvelles époques fiables
        </span>
      </div>
    )
  }

  // ── Barre de progression ──────────────────────────────────────────────────
  let progressVal, progressMax, progressLabel, progressSub
  if (version === 0) {
    progressVal   = Math.min(unused, FT_V1)
    progressMax   = FT_V1
    progressLabel = `${unused.toLocaleString()} / ${FT_V1.toLocaleString()} époques fiables`
    progressSub   = `Fine-tuning v1 automatique dès ${FT_V1.toLocaleString()} époques`
  } else if (version === 1) {
    progressVal   = Math.min(unused, FT_V2)
    progressMax   = FT_V2
    progressLabel = `${unused.toLocaleString()} / ${FT_V2.toLocaleString()} nouvelles époques`
    progressSub   = `Fine-tuning v2 automatique dès ${FT_V2.toLocaleString()} nouvelles époques`
  } else {
    progressVal   = progressMax = 1
    progressLabel = 'Modèle pleinement personnalisé'
    progressSub   = 'Mise à jour automatique tous les 6 mois'
  }
  const pct = Math.min(100, Math.round((progressVal / progressMax) * 100))

  // ── Modèle actuel ─────────────────────────────────────────────────────────
  const modelLabel =
    version === 0 ? 'Modèle général (55 sujets)'
    : version === 1 ? 'Modèle personnalisé v1 actif'
    : `Modèle personnalisé v${version} actif`

  // ── Gain de précision (dernier job) ──────────────────────────────────────
  const showGain = lastJob?.status === 'completed'
    && lastJob?.accuracy_before != null
    && lastJob?.accuracy_after  != null
  const gainPct = showGain
    ? ((lastJob.accuracy_after - lastJob.accuracy_before) * 100).toFixed(1)
    : null

  // ── Calendrier des jalons ─────────────────────────────────────────────────
  const milestones = [
    {
      label:  'Calibration',
      sub:    'Première session',
      done:   total > 0 || version > 0,
      active: total === 0 && version === 0,
    },
    {
      label:  'Fine-tuning v1',
      sub:    `2 000 époques · ~1 mois`,
      done:   version >= 1,
      active: version === 0 && isActive,
      req:    isProfileC ? 'Obligatoire' : profileType === 'B' ? 'Recommandé' : 'Optionnel',
    },
    {
      label:  'Fine-tuning v2',
      sub:    '4 000 nouvelles époques · ~3 mois',
      done:   version >= 2,
      active: version === 1 && isActive,
      req:    isProfileC ? 'Obligatoire' : 'Recommandé',
    },
    {
      label:  'Mise à jour continue',
      sub:    'Automatique tous les 6 mois',
      done:   version >= 3,
      active: version >= 2,
    },
  ]

  return (
    <div className="card p-6 space-y-5">

      {/* ── Header ── */}
      <div className="flex items-center gap-2 flex-wrap">
        <Cpu className="w-4 h-4 text-nc-accent" />
        <h3 className="font-semibold text-nc-text text-sm">Modèle IA personnalisé</h3>
        <span className={`ms-auto text-xs font-semibold px-2 py-0.5 rounded-full border
          ${hasModel
            ? 'bg-nc-success/15 text-nc-success border-nc-success/30'
            : 'bg-nc-warning/15 text-nc-warning border-nc-warning/30'}`}>
          {hasModel ? `Personnalisé v${version}` : 'Modèle général'}
        </span>
      </div>

      {/* ── Bannière activité ── */}
      <ActivityBanner />

      {/* ── Modèle actuel + gain ── */}
      <div className="flex items-center gap-3 text-xs flex-wrap">
        <Brain className="w-4 h-4 text-nc-muted shrink-0" />
        <span className="text-nc-muted">Modèle actuel :</span>
        <span className="font-semibold text-nc-text">{modelLabel}</span>
        {showGain && (
          <span className={`ms-auto text-xs font-bold px-2 py-0.5 rounded-full
            ${parseFloat(gainPct) >= 0 ? 'bg-nc-success/15 text-nc-success' : 'bg-nc-warning/15 text-nc-warning'}`}>
            {parseFloat(gainPct) >= 0 ? '+' : ''}{gainPct}% de précision (dernier FT)
          </span>
        )}
      </div>

      {/* ── Dernière mise à jour ── */}
      {lastFtAt && (
        <p className="text-[10px] text-nc-muted flex items-center gap-1">
          <CalendarDays className="w-3 h-3" />
          Dernier fine-tuning : {new Date(lastFtAt).toLocaleDateString('fr', { day: 'numeric', month: 'long', year: 'numeric' })}
          {lastJob?.n_epochs_used && ` · ${lastJob.n_epochs_used.toLocaleString()} époques utilisées`}
        </p>
      )}

      {/* ── Barre de progression ── */}
      {version < 3 && (
        <div className="space-y-1.5">
          <div className="flex justify-between text-xs">
            <span className="text-nc-muted">{progressLabel}</span>
            <span className="font-semibold text-nc-accent">{pct} %</span>
          </div>
          <div className="h-2.5 bg-nc-border rounded-full overflow-hidden">
            <div
              className="h-full rounded-full bg-gradient-to-r from-nc-accent to-nc-success transition-all duration-700"
              style={{ width: `${pct}%` }}
            />
          </div>
          <p className="text-[10px] text-nc-muted">{progressSub}</p>
        </div>
      )}

      {/* ── Calendrier ── */}
      <div>
        <p className="text-xs text-nc-muted uppercase tracking-wider font-semibold mb-3">
          Calendrier d'apprentissage
        </p>
        <div className="relative">
          <div className="absolute left-3.5 top-4 bottom-4 w-0.5 bg-nc-border rounded-full" />
          <div className="space-y-4">
            {milestones.map((m, i) => (
              <div key={i} className="flex items-start gap-3 relative">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center shrink-0 z-10
                  border-2 transition-all
                  ${m.done   ? 'bg-nc-success border-nc-success text-white'
                  : m.active ? 'bg-nc-accent  border-nc-accent  text-white'
                  :            'bg-nc-surface  border-nc-border  text-nc-muted'}`}>
                  {m.done
                    ? <Check className="w-3 h-3" />
                    : <span className="text-[10px] font-bold">{i + 1}</span>}
                </div>
                <div className="flex-1 pt-0.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className={`text-xs font-semibold
                      ${m.done ? 'text-nc-success' : m.active ? 'text-nc-accent' : 'text-nc-muted'}`}>
                      {m.label}
                    </span>
                    {m.req && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full font-medium
                        ${m.req === 'Obligatoire' ? 'bg-nc-danger/15 text-nc-danger'
                          : m.req === 'Recommandé'  ? 'bg-nc-accent/15 text-nc-accent'
                          :                          'bg-nc-muted/10  text-nc-muted'}`}>
                        {m.req}
                      </span>
                    )}
                  </div>
                  <p className="text-[10px] text-nc-muted mt-0.5">{m.sub}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Explication ── */}
      <div className="rounded-xl bg-nc-surface2 p-4 space-y-2">
        <p className="text-xs font-semibold text-nc-text">Pourquoi ce délai ?</p>
        <p className="text-[11px] text-nc-muted leading-relaxed">
          Les données de calibration (repos) ne reflètent pas les états cognitifs réels.
          Le modèle apprend sur vos vraies séances — d'où l'attente de 2 000 époques fiables
          (confiance &gt; 85 %). Le fine-tuning est déclenché <strong>automatiquement la nuit</strong> dès
          que les conditions sont remplies et que vous êtes actif (≥ 3 sessions / 30 jours).
        </p>
        <div className="grid grid-cols-2 gap-2 pt-1 text-[10px]">
          <div><span className="text-nc-muted">Fine-tuning v1 :</span><span className="text-nc-text font-medium ms-1">+5 à +7 % précision</span></div>
          <div><span className="text-nc-muted">Fine-tuning v2 :</span><span className="text-nc-text font-medium ms-1">+2 à +5 % supplémentaires</span></div>
        </div>
      </div>

    </div>
  )
}

// ── PalierProgress ────────────────────────────────────────────────────────────
function PalierProgress({ sessionCount, palierKey }) {
  const normalizedKey = PALIER_KEYS_COMPAT[palierKey] ?? palierKey
  const currentIdx    = PALIERS.findIndex(p => p.key === normalizedKey)
  const current       = PALIERS[currentIdx] ?? PALIERS[0]
  const next          = PALIERS[currentIdx + 1]
  const progress      = next
    ? Math.min(100, ((sessionCount - currentIdx * 5) / 5) * 100)
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

// ── PasswordChangeSection ─────────────────────────────────────────────────────
function PasswordChangeSection() {
  const [open,    setOpen]    = useState(false)
  const [next,    setNext]    = useState('')
  const [confirm, setConfirm] = useState('')
  const [showPwd, setShowPwd] = useState(false)
  const [saving,  setSaving]  = useState(false)
  const [success, setSuccess] = useState(false)
  const [error,   setError]   = useState('')

  const reset = () => { setNext(''); setConfirm(''); setError(''); setSuccess(false) }

  const handleSubmit = async (e) => {
    e.preventDefault(); setError('')
    if (next !== confirm) { setError('Les mots de passe ne correspondent pas'); return }
    if (next.length < 8)  { setError('Minimum 8 caractères'); return }
    if (!/[A-Z]/.test(next)) { setError('Au moins une majuscule requise'); return }
    if (!/[0-9]/.test(next)) { setError('Au moins un chiffre requis'); return }
    setSaving(true)
    try {
      await authApi.changePassword(next)
      setSuccess(true); reset()
      setTimeout(() => { setOpen(false); setSuccess(false) }, 2000)
    } catch (err) {
      setError(err?.response?.data?.detail ?? 'Erreur lors du changement')
    } finally { setSaving(false) }
  }

  const strength = (() => {
    if (!next) return 0
    let s = 0
    if (next.length >= 8)           s++
    if (/[A-Z]/.test(next))         s++
    if (/[0-9]/.test(next))         s++
    if (/[^A-Za-z0-9]/.test(next))  s++
    return s
  })()
  const strengthLabel = ['', 'Faible', 'Moyen', 'Fort', 'Très fort'][strength]
  const strengthColor = ['', 'bg-nc-danger', 'bg-yellow-400', 'bg-green-400', 'bg-green-500'][strength]

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
        <form onSubmit={handleSubmit} className="px-5 pb-5 space-y-4 border-t border-nc-border">
          <div className="flex items-start gap-3 px-4 py-3 mt-3 rounded-xl bg-blue-500/5 border border-blue-500/20 text-blue-400 text-xs">
            <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5" />
            <span>Votre identité est vérifiée via votre session active. Aucun ancien mot de passe requis.</span>
          </div>
          {success && <div className="flex items-center gap-2 text-green-400 text-sm py-2"><Check className="w-4 h-4" />Mot de passe modifié</div>}
          {error   && <p className="text-nc-danger text-xs py-1">{error}</p>}
          <div className="space-y-1">
            <label className="text-xs text-nc-muted">Nouveau mot de passe</label>
            <div className="relative">
              <input type={showPwd ? 'text' : 'password'} value={next}
                onChange={e => setNext(e.target.value)} required className="input w-full pe-10" placeholder="••••••••" />
              <button type="button" onClick={() => setShowPwd(s => !s)}
                className="absolute end-3 top-1/2 -translate-y-1/2 text-nc-muted hover:text-nc-text" tabIndex={-1}>
                {showPwd ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {next && (
              <div className="space-y-1 pt-1">
                <div className="flex gap-1">{[1,2,3,4].map(i => <div key={i} className={`h-1 flex-1 rounded-full transition-all ${i <= strength ? strengthColor : 'bg-nc-border'}`} />)}</div>
                <p className="text-[10px] text-nc-muted">{strengthLabel} — min. 8 car., 1 majuscule, 1 chiffre</p>
              </div>
            )}
          </div>
          <div className="space-y-1">
            <label className="text-xs text-nc-muted">Confirmer</label>
            <div className="relative">
              <input type={showPwd ? 'text' : 'password'} value={confirm}
                onChange={e => setConfirm(e.target.value)} required className="input w-full pe-10" placeholder="••••••••" />
              {confirm && next && (
                <span className={`absolute end-3 top-1/2 -translate-y-1/2 text-xs ${confirm === next ? 'text-green-400' : 'text-nc-danger'}`}>
                  {confirm === next ? '✓' : '✗'}
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-2 pt-1">
            <button type="submit" disabled={saving} className="btn-primary flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm disabled:opacity-60">
              {saving ? 'Enregistrement…' : 'Mettre à jour'}
            </button>
            <button type="button" onClick={() => { setOpen(false); reset() }} className="btn-ghost px-4 py-2 rounded-xl text-sm text-nc-muted">
              Annuler
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

// ── TherapistProfile ──────────────────────────────────────────────────────────
function TherapistProfile({ user }) {
  const infoRows = [
    { icon: Mail,         label: 'Email',         value: user?.email },
    { icon: BadgeCheck,   label: 'Rôle',          value: 'Thérapeute' },
    { icon: User,         label: 'Nom complet',   value: user?.first_name && user?.last_name ? `${user.first_name} ${user.last_name}` : '—' },
    { icon: CalendarDays, label: 'Membre depuis', value: user?.created_at ? new Date(user.created_at).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' }) : '—' },
  ]
  return (
    <div className="max-w-xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">
      <h1 className="text-3xl font-bold text-nc-text">Mon profil</h1>
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
            <Users className="w-3 h-3" />Thérapeute
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
      <div className="card p-5 flex items-start gap-4">
        <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-green-500/10 shrink-0">
          <Brain className="w-4 h-4 text-green-400" />
        </div>
        <div>
          <p className="text-sm font-semibold text-nc-text">Compte thérapeute</p>
          <p className="text-sm text-nc-muted mt-1">
            Ce compte est dédié au suivi clinique. Les données EEG sont propres à chaque patient —
            consultez-les dans l'onglet <strong>Mes patients</strong>.
          </p>
        </div>
      </div>
      <PasswordChangeSection />
    </div>
  )
}

// ── AdminProfile ──────────────────────────────────────────────────────────────
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

  const [profileData,  setProfileData]  = useState(null)
  const [sessionCount, setSessionCount] = useState(0)
  const [loading,      setLoading]      = useState(true)
  const [calibrating,  setCalibrating]  = useState(false)

  useEffect(() => {
    if (role !== 'patient') { setLoading(false); return }
    Promise.all([
      profileApi.get(),
      sessionsApi.list().catch(() => []),
    ]).then(([prof, sess]) => {
      setProfileData(prof)
      setSessionCount(Array.isArray(sess) ? sess.filter(s => s.status === 'completed').length : 0)
    }).catch(() => {}).finally(() => setLoading(false))
  }, [role])

  const handleRecalibrate = async () => {
    setCalibrating(true)
    try {
      const result = await profileApi.calibrate({
        iapf:             10.0 + Math.random() * 2 - 1,
        baseline_tbr:     2.5  + Math.random(),
        baseline_alpha:   15   + Math.random() * 10,
        baseline_beta:    8    + Math.random() * 5,
        baseline_theta:   10   + Math.random() * 8,
        reactivity_score: 0.3  + Math.random() * 0.6,
      })
      setProfileData(result)
    } catch (err) {
      alert(err?.response?.data?.detail ?? err.message)
    } finally { setCalibrating(false) }
  }

  if (role === 'therapist') return <TherapistProfile user={user} />
  if (role === 'admin')     return <AdminProfile user={user} />

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

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6 animate-fade-in">

      <h1 className="text-3xl font-bold text-nc-text">{t('profile.title')}</h1>

      {/* ── Carte utilisateur ── */}
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

      {/* ── Profil EEG cognitif ── */}
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
            {/* Type card enrichi */}
            <ProfileTypeCard profileType={profileType} profileData={profileData} info={info} />

            {/* Mesures EEG */}
            <div className="grid grid-cols-2 gap-4">
              <MetricCard icon={Activity}    color={info.color} label="IAPF"          value={`${profileData.iapf?.toFixed(1) ?? '—'} Hz`}          desc="Fréquence de pic alpha individuelle." />
              <MetricCard icon={Zap}         color={info.color} label="Alpha baseline" value={profileData.baseline_alpha?.toFixed(2) ?? '—'}         desc="Puissance alpha de repos (µV²/Hz)." />
              <MetricCard icon={Target}      color={info.color} label="TBR baseline"   value={profileData.baseline_tbr?.toFixed(2) ?? '—'}           desc="Ratio theta/beta de repos." />
              <MetricCard icon={ShieldCheck} color={info.color} label="Réactivité"    value={`${Math.round((profileData.reactivity_score ?? 0) * 100)} %`} desc="Score ERD — blocage alpha (0→100 %)." />
            </div>

            {/* Spectre */}
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

      {/* ── Explication profils A/B/C ── */}
      <ProfilesExplained currentType={profileType} />

      {/* ── Progression protocole ── */}
      <PalierProgress sessionCount={sessionCount} palierKey={palierKey} />

      {/* ── Modèle IA personnalisé + fine-tuning automatique ── */}
      <AIModelStatus profileType={profileType} />

      <PasswordChangeSection />
    </div>
  )
}
