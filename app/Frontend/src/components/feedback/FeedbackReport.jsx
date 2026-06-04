import { CheckCircle2, Award } from 'lucide-react'

function MetricCard({ label, value, unit, color }) {
  return (
    <div className="card p-4 text-center">
      <p className={`text-2xl font-bold font-mono ${color ?? 'text-nc-text'}`}>{value}</p>
      {unit && <p className="text-[10px] text-nc-muted">{unit}</p>}
      <p className="text-xs text-nc-muted mt-1">{label}</p>
    </div>
  )
}

export default function FeedbackReport({ report, metrics, onClose }) {
  if (!metrics) return null

  const {
    items_played = 0,
    items_efficaces = 0,
    delta_alpha_global = 0,
    delta_beta_global = 0,
    session_success = false,
    score = 0,
  } = metrics

  const effPct = items_played > 0 ? Math.round((items_efficaces / items_played) * 100) : 0

  return (
    <div className="space-y-5">
      {/* Titre */}
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-2xl flex items-center justify-center
          ${session_success ? 'bg-emerald-500/15' : 'bg-yellow-500/10'}`}>
          {session_success
            ? <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            : <Award className="w-5 h-5 text-yellow-400" />}
        </div>
        <div>
          <h2 className="text-lg font-bold text-nc-text">
            {session_success ? 'Séance réussie !' : 'Séance terminée'}
          </h2>
          <p className="text-xs text-nc-muted">
            {session_success
              ? 'Votre cerveau a montré des améliorations significatives.'
              : 'Bonne séance — continuez à pratiquer régulièrement.'}
          </p>
        </div>
      </div>

      {/* Métriques */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <MetricCard
          label="Score global"
          value={score}
          unit="/100"
          color={score >= 70 ? 'text-emerald-400' : score >= 40 ? 'text-yellow-400' : 'text-red-400'}
        />
        <MetricCard
          label="Médias efficaces"
          value={`${items_efficaces}/${items_played}`}
          unit={`${effPct}%`}
          color="text-blue-400"
        />
        <MetricCard
          label="Delta Alpha"
          value={delta_alpha_global >= 0 ? `+${delta_alpha_global.toFixed(3)}` : delta_alpha_global.toFixed(3)}
          unit="relax ↑"
          color={delta_alpha_global > 0 ? 'text-emerald-400' : 'text-red-400'}
        />
        <MetricCard
          label="Delta Beta"
          value={delta_beta_global <= 0 ? `${delta_beta_global.toFixed(3)}` : `+${delta_beta_global.toFixed(3)}`}
          unit="stress ↓"
          color={delta_beta_global < 0 ? 'text-emerald-400' : 'text-yellow-400'}
        />
      </div>

      {/* Rapport IA */}
      {report ? (
        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-nc-accent animate-pulse" />
            <h3 className="text-sm font-semibold text-nc-text">Analyse IA — Claude</h3>
          </div>
          <div className="text-sm text-nc-text/90 leading-relaxed whitespace-pre-wrap">
            {report}
          </div>
        </div>
      ) : (
        <div className="card p-5 flex items-center gap-3 text-nc-muted">
          <div className="w-5 h-5 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
          <p className="text-sm">Génération du rapport IA en cours…</p>
        </div>
      )}

      {onClose && (
        <button
          onClick={onClose}
          className="btn-primary w-full py-3 rounded-xl text-sm font-semibold"
        >
          Terminer la séance
        </button>
      )}
    </div>
  )
}
