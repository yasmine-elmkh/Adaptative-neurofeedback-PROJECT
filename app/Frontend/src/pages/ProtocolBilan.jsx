import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import {
  Award, TrendingUp, TrendingDown, Brain, ArrowLeft, ChevronRight, Star,
} from 'lucide-react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Cell,
} from 'recharts'

const API = (path) => fetch(`/api/protocol${path}`, {
  headers: { Authorization: `Bearer ${localStorage.getItem('neurocap_token')}` },
}).then(r => r.json())

const PALIER_COLORS = { P1: '#a78bfa', P2: '#60a5fa', P3: '#34d399', P4: '#fbbf24' }
const DECISION_STYLES = {
  upgrade:   { bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', text: 'text-emerald-400', icon: '↑', label: 'Montée de palier' },
  stable:    { bg: 'bg-blue-500/10',    border: 'border-blue-500/20',    text: 'text-blue-400',    icon: '→', label: 'Palier stable'     },
  downgrade: { bg: 'bg-yellow-500/10',  border: 'border-yellow-500/25',  text: 'text-yellow-400',  icon: '↓', label: 'Retour au palier précédent' },
}

const BILAN_LABELS = { 5: 'B1 — Bilan intermédiaire', 10: 'B2 — Bilan de mi-parcours', 15: 'B3 — Bilan final' }

export default function ProtocolBilan() {
  const navigate = useNavigate()
  const { n }    = useParams()
  const sessionN = parseInt(n)

  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState('')

  useEffect(() => {
    API(`/bilan/${sessionN}`)
      .then(d => {
        if (d.detail) setError(d.detail)
        else setData(d)
      })
      .catch(() => setError('Impossible de charger le bilan.'))
      .finally(() => setLoading(false))
  }, [sessionN])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
    </div>
  )

  if (error) return (
    <div className="max-w-lg mx-auto px-4 py-10 text-center">
      <p className="text-red-400 text-sm">{error}</p>
      <button onClick={() => navigate('/protocol')} className="mt-4 btn-primary px-4 py-2 rounded-xl text-sm">
        Retour au programme
      </button>
    </div>
  )

  const bilanLabel   = BILAN_LABELS[sessionN] || `Bilan S${sessionN}`
  const decision     = DECISION_STYLES[data.palier_decision] || DECISION_STYLES.stable
  const avgSuccess   = data.success_rate_trend?.reduce((s, v) => s + v, 0) / Math.max(data.success_rate_trend?.length, 1)

  const scoreChartData = (data.sessions_covered || []).map((sn, i) => ({
    name:    `S${sn}`,
    score:   data.score_evolution?.[i] ?? 0,
    alpha:   parseFloat(((data.alpha_power_trend?.[i] ?? 0) * 100).toFixed(2)),
    palier:  data.palier_evolution?.[i] ?? 'P1',
    success: data.success_rate_trend?.[i] ?? 0,
  }))

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-3 flex-wrap">
        <button onClick={() => navigate('/protocol')}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="w-10 h-10 rounded-2xl bg-amber-500/15 flex items-center justify-center">
          <Star className="w-5 h-5 text-amber-400 fill-amber-400" />
        </div>
        <div className="flex-1">
          <h1 className="text-xl font-bold text-nc-text">{bilanLabel}</h1>
          <p className="text-xs text-nc-muted">{data.sessions_covered?.length} séances analysées</p>
        </div>
        <span className="px-3 py-1.5 rounded-full bg-purple-500/15 border border-purple-500/25 text-purple-400 text-xs font-semibold">
          Profil {data.profile_type}
        </span>
      </div>

      {/* Indicateurs clés */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Séances couvertes', value: data.sessions_covered?.length || 0, color: 'text-nc-accent' },
          { label: 'Succès moyen',      value: `${avgSuccess?.toFixed(0)}%`, color: 'text-emerald-400' },
          { label: 'IAPF individuelle', value: `${data.iapf?.toFixed(1) ?? '—'} Hz`, color: 'text-blue-400' },
          { label: 'Palier actuel',     value: data.current_palier, color: PALIER_COLORS[data.current_palier] || '#a78bfa', style: true },
        ].map(({ label, value, color, style }) => (
          <div key={label} className="card p-3 text-center">
            <p className="text-xl font-bold font-mono" style={style ? { color } : undefined}>
              <span className={style ? '' : color}>{value}</span>
            </p>
            <p className="text-[10px] text-nc-muted mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {/* Décision palier */}
      <div className={`card p-4 flex items-center gap-4 border ${decision.border} ${decision.bg}`}>
        <span className={`text-3xl font-bold ${decision.text}`}>{decision.icon}</span>
        <div className="flex-1">
          <p className={`text-sm font-bold ${decision.text}`}>{decision.label}</p>
          <p className="text-xs text-nc-muted mt-0.5">{data.palier_decision_text}</p>
        </div>
      </div>

      {/* Graphique scores */}
      {scoreChartData.length >= 2 && (
        <div className="card p-5 space-y-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-nc-accent" />
            <h2 className="text-sm font-bold text-nc-text">Évolution du score</h2>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={scoreChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9a8bb0' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#9a8bb0' }} />
              <Tooltip contentStyle={{ background: '#1e1b2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
              <Line type="monotone" dataKey="score" stroke="#6c63ff" strokeWidth={2} dot={{ fill: '#6c63ff', r: 3 }} name="Score" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Histogramme taux de succès par bloc */}
      {scoreChartData.length >= 1 && (
        <div className="card p-5 space-y-3">
          <h2 className="text-sm font-bold text-nc-text">Taux de succès par séance</h2>
          <ResponsiveContainer width="100%" height={140}>
            <BarChart data={scoreChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9a8bb0' }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#9a8bb0' }} />
              <Tooltip contentStyle={{ background: '#1e1b2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
              <Bar dataKey="success" radius={4}>
                {scoreChartData.map((_, i) => (
                  <Cell key={i} fill={PALIER_COLORS[scoreChartData[i]?.palier] || '#6c63ff'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="flex gap-3 flex-wrap text-[9px]">
            {Object.entries(PALIER_COLORS).map(([p, c]) => (
              <span key={p} className="flex items-center gap-1 text-nc-muted">
                <span className="w-2 h-2 rounded-full" style={{ background: c }} />
                {p}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Tendance alpha */}
      {scoreChartData.length >= 2 && (
        <div className="card p-5 space-y-3">
          <h2 className="text-sm font-bold text-nc-text">Puissance alpha relative</h2>
          <ResponsiveContainer width="100%" height={120}>
            <LineChart data={scoreChartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9a8bb0' }} />
              <YAxis tick={{ fontSize: 10, fill: '#9a8bb0' }} />
              <Tooltip contentStyle={{ background: '#1e1b2e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8 }} />
              <Line type="monotone" dataKey="alpha" stroke="#34d399" strokeWidth={2} dot={{ fill: '#34d399', r: 2 }} name="Alpha %" />
            </LineChart>
          </ResponsiveContainer>
          <div className="flex items-center gap-2">
            {data.alpha_trend > 0.01
              ? <TrendingUp className="w-4 h-4 text-emerald-400" />
              : data.alpha_trend < -0.01
              ? <TrendingDown className="w-4 h-4 text-red-400" />
              : null}
            <span className="text-xs text-nc-muted">
              Tendance alpha : {data.alpha_trend > 0.01 ? 'en hausse ↑' : data.alpha_trend < -0.01 ? 'en baisse ↓' : 'stable →'}
            </span>
          </div>
        </div>
      )}

      {/* Profil EEG */}
      <div className="card p-5 space-y-3">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-nc-accent" />
          <h2 className="text-sm font-bold text-nc-text">Profil EEG individuel</h2>
        </div>
        {[
          ['Type cognitif',   `Profil ${data.profile_type}`],
          ['IAPF',            `${data.iapf?.toFixed(1) ?? '—'} Hz`],
          ['Plage alpha',     data.iapf ? `${(data.iapf - 2).toFixed(1)} – ${(data.iapf + 2).toFixed(1)} Hz` : '—'],
          ['Palier actuel',   data.current_palier],
          ['Décision palier', data.palier_decision_text],
        ].map(([k, v]) => (
          <div key={k} className="flex justify-between text-xs py-1.5 border-b border-nc-border/30 last:border-0">
            <span className="text-nc-muted">{k}</span>
            <span className="font-medium text-nc-text">{v}</span>
          </div>
        ))}
      </div>

      {/* Recommandation IA */}
      {data.recommendation && (
        <div className="card p-5 space-y-3 border border-nc-accent/20 bg-nc-accent/4">
          <div className="flex items-center gap-2">
            <Award className="w-4 h-4 text-nc-accent" />
            <h2 className="text-sm font-bold text-nc-text">Recommandation personnalisée</h2>
          </div>
          <p className="text-sm text-nc-muted leading-relaxed">{data.recommendation}</p>
        </div>
      )}

      {/* Questionnaire subjectif */}
      {data.questionnaire_summary && Object.keys(data.questionnaire_summary).length > 0 && (
        <div className="card p-5 space-y-3">
          <h2 className="text-sm font-bold text-nc-text">Ressenti moyen (questionnaires)</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {Object.entries(data.questionnaire_summary)
              .filter(([, v]) => v !== null)
              .map(([k, v]) => (
                <div key={k} className="text-center card p-3">
                  <p className="text-lg font-bold font-mono text-nc-accent">{v?.toFixed(1)}</p>
                  <p className="text-[10px] text-nc-muted capitalize mt-0.5">{k.replace('_', ' ')}</p>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 flex-wrap">
        <button onClick={() => navigate('/protocol')}
          className="flex-1 btn-primary flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-semibold">
          Continuer le programme <ChevronRight className="w-4 h-4" />
        </button>
        <button onClick={() => navigate('/assistant')}
          className="px-5 py-3 rounded-xl border border-nc-border text-sm text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors">
          Voir avec le thérapeute
        </button>
      </div>
    </div>
  )
}
