/**
 * NeuroCap – RecommendationEngine
 * Rules-based recommendation system following the NeuroCap protocol:
 * 15 sessions · 4 paliers · 3 profile types (A/B/C) · Mou et al. 2024 thresholds
 */
import { useMemo } from 'react'
import { useTranslation } from 'react-i18next'
import { Zap, Heart, Trophy, RefreshCw, TrendingUp, Brain } from 'lucide-react'

// ── Protocol palier boundaries ─────────────────────────────────────────────
const PALIERS = [
  { id: 'P1_INITIATION',    max: 5  },
  { id: 'P2_APPRENTISSAGE', max: 10 },
  { id: 'P3_MAITRISE',      max: 13 },
  { id: 'P4_AUTONOMIE',     max: Infinity },
]

function getPalier(n) {
  return PALIERS.find((p) => n <= p.max) ?? PALIERS.at(-1)
}

// ── Core recommendation logic ──────────────────────────────────────────────
function computeRec(sessions, eegProfile) {
  const n       = sessions.length
  const profile = eegProfile?.profile_type ?? 'B'

  if (n === 0) return { type: 'start',    icon: Brain,      level: 'info' }
  if (n >= 15) return { type: 'complete', icon: Trophy,     level: 'success' }

  const palier  = getPalier(n)
  const recent  = sessions.slice(-3)
  const avgScore = recent.reduce((s, x) => s + (x.session_score ?? 0), 0) / recent.length
  const avgTBR   = recent.reduce((s, x) => s + (x.avg_tbr    ?? 0), 0) / recent.length

  const firstScore = sessions[0]?.session_score ?? 0
  const lastScore  = sessions.at(-1)?.session_score ?? 0
  const scoreDelta = n > 1 ? lastScore - firstScore : 0

  // High TBR (stress / unfocused) — highest priority
  if (avgTBR > 4.5) {
    return { type: 'stress', icon: Heart, level: 'warning', tbr: avgTBR.toFixed(2) }
  }

  // Declining performance + low score → rest advised
  if (avgScore < 25 && scoreDelta < -5) {
    return { type: 'rest', icon: RefreshCw, level: 'warning' }
  }

  // P4 – Autonomie
  if (palier.id === 'P4_AUTONOMIE') {
    if (avgScore >= 70) return { type: 'complete', icon: Trophy, level: 'success' }
    return { type: 'concentration', icon: Zap, level: 'info', palier: palier.id }
  }

  // P3 – Maîtrise
  if (palier.id === 'P3_MAITRISE') {
    if (avgTBR > 3.5 || profile === 'C') {
      return { type: 'regulation', icon: Heart, level: 'info', palier: palier.id }
    }
    return { type: 'concentration', icon: Zap, level: 'info', palier: palier.id }
  }

  // P2 – Apprentissage
  if (palier.id === 'P2_APPRENTISSAGE') {
    if (profile === 'C') {
      return { type: 'regulation', icon: Heart, level: 'info', palier: palier.id }
    }
    if (avgScore >= 55) {
      return { type: 'concentration', icon: Zap, level: 'info', palier: palier.id }
    }
    return { type: 'maintain', icon: TrendingUp, level: 'info', palier: palier.id }
  }

  // P1 – Initiation
  if (profile === 'A') return { type: 'concentration', icon: Zap,       level: 'info', palier: palier.id }
  if (profile === 'C') return { type: 'regulation',    icon: Heart,     level: 'info', palier: palier.id }
  return                      { type: 'maintain',      icon: TrendingUp, level: 'info', palier: palier.id }
}

// ── Styles per urgency level ───────────────────────────────────────────────
const STYLES = {
  info:    { wrap: 'border-nc-accent/30  bg-nc-accent/5',  icon: 'text-nc-accent'  },
  warning: { wrap: 'border-nc-warning/30 bg-nc-warning/5', icon: 'text-nc-warning' },
  success: { wrap: 'border-nc-success/30 bg-nc-success/5', icon: 'text-nc-success' },
}

// ── Component ──────────────────────────────────────────────────────────────
export default function RecommendationEngine({ sessions = [], eegProfile = null }) {
  const { t } = useTranslation()
  const rec = useMemo(() => computeRec(sessions, eegProfile), [sessions, eegProfile])
  const { wrap, icon: iconCls } = STYLES[rec.level] ?? STYLES.info
  const Icon = rec.icon

  return (
    <div className={`card p-6 border ${wrap} flex flex-col gap-3 animate-fade-in`}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <Icon className={`w-5 h-5 shrink-0 ${iconCls}`} />
        <h3 className={`font-semibold text-sm uppercase tracking-wider ${iconCls}`}>
          {t('recommendation.title')}
        </h3>
      </div>

      {/* Action */}
      <p className="text-nc-text font-semibold leading-snug">
        {t(`recommendation.${rec.type}.action`)}
      </p>

      {/* Reason */}
      <p className="text-nc-muted text-sm leading-relaxed flex-1">
        {t(`recommendation.${rec.type}.reason`, { tbr: rec.tbr ?? '' })}
      </p>

      {/* Palier badge */}
      {rec.palier && (
        <div className="flex items-center gap-2 pt-1 border-t border-nc-border/40">
          <span className="text-xs text-nc-muted">{t('profile.palier_current')}:</span>
          <span className={`text-xs font-bold ${iconCls}`}>
            {t(`profile.paliers.${rec.palier}.label`)}
          </span>
        </div>
      )}

      {/* Profile type if available */}
      {eegProfile?.profile_type && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-nc-muted">{t('profile.sections.eeg_profile')}:</span>
          <span className={`text-xs font-semibold ${iconCls}`}>
            {t(`profile.types.${eegProfile.profile_type}.label`)}
          </span>
        </div>
      )}
    </div>
  )
}
