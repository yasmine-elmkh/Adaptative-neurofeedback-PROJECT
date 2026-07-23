import { useState } from 'react'
import { CheckCircle2, Award, Send, Download, Loader2, Check } from 'lucide-react'

function MetricCard({ label, value, unit, color }) {
  return (
    <div className="card p-4 text-center">
      <p className={`text-2xl font-bold font-mono ${color ?? 'text-nc-text'}`}>{value}</p>
      {unit && <p className="text-[10px] text-nc-muted">{unit}</p>}
      <p className="text-xs text-nc-muted mt-1">{label}</p>
    </div>
  )
}

export default function FeedbackReport({ report, metrics, sessionId, onFinalized }) {
  const [therapistState, setTherapistState] = useState('idle') // idle | loading | done | error
  const [pdfState,       setPdfState]       = useState('idle')
  const [finalizing,     setFinalizing]     = useState(false)

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
  const token  = () => localStorage.getItem('neurocap_token')

  const bothDone = therapistState === 'done' && pdfState === 'done'

  async function handleSendTherapist() {
    if (!sessionId || therapistState !== 'idle') return
    setTherapistState('loading')
    try {
      const r = await fetch(`/api/feedback/sessions/${sessionId}/send-therapist`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token()}` },
      })
      if (!r.ok) throw new Error()
      setTherapistState('done')
    } catch {
      setTherapistState('error')
    }
  }

  async function handleDownloadPdf() {
    if (!sessionId || pdfState !== 'idle') return
    setPdfState('loading')
    try {
      const r = await fetch(`/api/feedback/sessions/${sessionId}/progress-pdf`, {
        headers: { Authorization: `Bearer ${token()}` },
      })
      if (!r.ok) throw new Error()
      const blob = await r.blob()
      const url  = URL.createObjectURL(blob)
      const a    = document.createElement('a')
      a.href     = url
      a.download = `NeuroCap_Seance_rapport.pdf`
      a.click()
      URL.revokeObjectURL(url)
      setPdfState('done')
    } catch {
      setPdfState('error')
    }
  }

  async function handleFinalize() {
    if (!sessionId || !bothDone || finalizing) return
    setFinalizing(true)
    try {
      await fetch(`/api/feedback/sessions/${sessionId}/finalize`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token()}` },
      })
    } catch { /* ignore */ }
    onFinalized?.()
  }

  function ActionBtn({ state, onClick, icon: Icon, label, doneLabel }) {
    const isDone    = state === 'done'
    const isLoading = state === 'loading'
    const isError   = state === 'error'
    return (
      <button
        onClick={onClick}
        disabled={isDone || isLoading}
        className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold transition-all border
          ${isDone
            ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400 cursor-default'
            : isError
            ? 'bg-red-500/10 border-red-500/30 text-red-400'
            : 'border-nc-accent/30 bg-nc-accent/10 text-nc-accent hover:bg-nc-accent/20'
          }`}
      >
        {isLoading
          ? <Loader2 className="w-4 h-4 animate-spin" />
          : isDone
          ? <Check className="w-4 h-4" />
          : <Icon className="w-4 h-4" />
        }
        {isDone ? doneLabel : isError ? 'Réessayer' : label}
      </button>
    )
  }

  return (
    <div className="space-y-5">
      {/* En-tête résultat */}
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

      {/* Zone validation finale */}
      {sessionId && (
        <div className={`card p-4 space-y-3 border ${bothDone ? 'border-emerald-500/30 bg-emerald-500/5' : 'border-nc-accent/15'}`}>
          <p className="text-xs font-semibold text-nc-text">
            Pour valider la séance, effectuez les deux actions ci-dessous :
          </p>
          <div className="flex flex-wrap gap-3">
            <ActionBtn
              state={therapistState}
              onClick={handleSendTherapist}
              icon={Send}
              label="Envoyer au thérapeute"
              doneLabel="Envoyé au thérapeute"
            />
            <ActionBtn
              state={pdfState}
              onClick={handleDownloadPdf}
              icon={Download}
              label="Télécharger PDF d'avancement"
              doneLabel="PDF téléchargé"
            />
          </div>

          {bothDone && (
            <button
              onClick={handleFinalize}
              disabled={finalizing}
              className="w-full flex items-center justify-center gap-2 btn-primary py-2.5 rounded-xl text-sm font-semibold"
            >
              {finalizing
                ? <><Loader2 className="w-4 h-4 animate-spin" /> Finalisation…</>
                : <><Check className="w-4 h-4" /> Terminer la séance</>
              }
            </button>
          )}
        </div>
      )}
    </div>
  )
}
