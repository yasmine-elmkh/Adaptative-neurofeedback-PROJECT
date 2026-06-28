import { useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Upload, FileText, ArrowLeft, AlertTriangle,
  CheckCircle2, ChevronLeft, ChevronRight, RefreshCw,
  HelpCircle, Sparkles, Download, Activity,
} from 'lucide-react'
import { eeg as eegApi } from '../utils/api'

/* ── Métadonnées état ML ── */
const ML_STATE = {
  concentration: {
    label: 'Concentration', color: 'text-emerald-400',
    bg: 'bg-emerald-500/10', border: 'border-emerald-500/25', icon: '🎯',
  },
  stress: {
    label: 'Stress', color: 'text-red-400',
    bg: 'bg-red-500/10', border: 'border-red-500/25', icon: '⚡',
  },
  neutral: {
    label: 'Neutre', color: 'text-blue-400',
    bg: 'bg-blue-500/10', border: 'border-blue-500/25', icon: '〜',
  },
  uncertain: {
    label: 'Incertain', color: 'text-yellow-400',
    bg: 'bg-yellow-500/10', border: 'border-yellow-500/25', icon: '⚠',
  },
}

const QUALITY_META = {
  bonne:    { label: 'Signal bon',     color: 'text-emerald-400', dot: 'bg-emerald-400' },
  moyenne:  { label: 'Signal moyen',   color: 'text-yellow-400',  dot: 'bg-yellow-400'  },
  mauvaise: { label: 'Signal faible',  color: 'text-red-400',     dot: 'bg-red-400'     },
}

const PAGE_SIZE = 25

/* ── Export JSON ── */
function exportJSON(result) {
  const payload = {
    filename:       result.filename,
    duration_s:     result.duration_s,
    fs:             result.fs,
    signal_quality: result.signal_quality,
    n_epochs_total:    result.n_epochs_total,
    n_epochs_accepted: result.n_epochs_accepted,
    summary:        result.summary,
    exported_at:    new Date().toISOString(),
  }
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' })
  const url  = URL.createObjectURL(blob)
  const a    = document.createElement('a')
  a.href     = url
  a.download = `neurocap_${result.filename?.replace(/\.[^.]+$/, '') ?? 'eeg'}_${Date.now()}.json`
  a.click()
  URL.revokeObjectURL(url)
}

/* ── Résumé ML ── */
function MLSummaryCard({ summary, filename, duration_s, n_epochs_total, n_epochs_accepted, fs, signal_quality }) {
  const dom     = ML_STATE[summary.dominant_state] ?? ML_STATE.uncertain
  const confPct = Math.round((summary.mean_confidence ?? 0) * 100)
  const qMeta   = QUALITY_META[signal_quality] ?? QUALITY_META.moyenne

  const bars = [
    {
      label: 'Concentration',
      sub:   'EEGNet DL FULL · AUC 0,751 ✓',
      pct:   Math.min((summary.mean_conc_score   ?? 0) * 10, 100),
      color: 'bg-emerald-500',
    },
    {
      label: 'Stress',
      sub:   'EEGNet_LR TL FULL · AUC 0,607 ⚠',
      pct:   Math.min((summary.mean_stress_score ?? 0) * 10, 100),
      color: 'bg-orange-500',
    },
  ]

  return (
    <div className="card p-6 space-y-5">
      {/* En-tête */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h2 className="text-lg font-bold text-nc-text">Résultat d'analyse</h2>
          <p className="text-xs text-nc-muted font-mono mt-0.5 truncate max-w-sm">{filename}</p>
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {/* Qualité signal */}
          <span className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium
                            border border-current/20 bg-current/5 ${qMeta.color}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${qMeta.dot}`} />
            {qMeta.label}
          </span>
          {/* État dominant */}
          <span className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-bold border
                           ${dom.bg} ${dom.color} ${dom.border}`}>
            {dom.icon} État dominant : {dom.label}
          </span>
        </div>
      </div>

      {/* Stats rapides */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Durée',           value: `${Math.round(duration_s)}s`, sub: `${fs} Hz` },
          { label: 'Époques totales', value: n_epochs_total,               sub: `${n_epochs_accepted} acceptées` },
          { label: 'Classifiées',     value: summary.n_classified ?? 0,   sub: 'époques IA' },
          { label: 'Confiance moy.',  value: `${confPct}%`,               sub: 'Classifieur IA' },
        ].map(({ label, value, sub }) => (
          <div key={label} className="p-3 rounded-xl bg-nc-surface2 text-center">
            <p className="text-xl font-bold font-mono text-nc-text">{value}</p>
            <p className="text-[10px] text-nc-muted mt-0.5">{label}</p>
            <p className="text-[9px] text-nc-muted/60">{sub}</p>
          </div>
        ))}
      </div>

      {/* Barres scores IA — les DEUX modèles toujours visibles */}
      <div className="space-y-1">
        <p className="text-[10px] text-nc-muted/60 uppercase tracking-widest font-semibold mb-3">
          Scores modèles IA — 50 % = seuil de décision
        </p>
        {bars.map(({ label, sub, pct, color }) => (
          <div key={label} className="mb-3">
            <div className="flex justify-between text-xs mb-1">
              <span className="text-nc-muted font-medium">{label}
                <span className="ml-2 text-nc-muted/50 font-normal text-[10px]">{sub}</span>
              </span>
              <span className="font-mono font-semibold text-nc-text">{Math.round(pct)}%</span>
            </div>
            <div className="relative h-2.5 rounded-full bg-nc-surface2 overflow-hidden">
              <div
                className={`h-full rounded-full ${color} transition-all duration-700`}
                style={{ width: `${pct}%` }}
              />
              {/* Marqueur seuil 50% */}
              <div className="absolute top-0 bottom-0 w-px bg-nc-muted/30" style={{ left: '50%' }} />
            </div>
          </div>
        ))}
      </div>

      {/* Badges modèles — CdC §4.5 */}
      <div className="flex gap-2 flex-wrap items-center">
        <span className="text-[10px] text-nc-muted/60">Modèles IA actifs :</span>
        {[
          { name: 'EEGNet/conc (DL FULL)',    auc: '0.751', score: 'S=0,789', ok: (summary.mean_conc_score   ?? 0) > 0, warn: false },
          { name: 'EEGNet_LR/stress (TL FULL)', auc: '0.607', score: 'S=0,525', ok: (summary.mean_stress_score ?? 0) > 0, warn: true  },
        ].map(m => (
          <span key={m.name}
            className={`flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-mono border
                        ${m.ok
                          ? (m.warn
                              ? 'bg-yellow-500/5 border-yellow-500/20 text-yellow-400'
                              : 'bg-emerald-500/5 border-emerald-500/20 text-emerald-400')
                          : 'bg-red-500/5 border-red-500/20 text-red-400'}`}>
            <span className={`w-1.5 h-1.5 rounded-full ${m.ok ? (m.warn ? 'bg-yellow-400' : 'bg-emerald-400') : 'bg-red-400'}`} />
            {m.name} · AUC {m.auc} · {m.score}
          </span>
        ))}
      </div>

      {/* Réserve clinique stress — affichage obligatoire (CdC §4.5.2) */}
      <div className="p-3 rounded-xl bg-orange-500/8 border border-orange-500/20 flex items-start gap-2 text-xs text-orange-300">
        <HelpCircle className="w-4 h-4 shrink-0 mt-0.5" />
        <span>
          <strong>Indicateur orientatif (stress) —</strong> La mesure du stress par EEG frontal seul (Fp2)
          n'est pas cliniquement validée. AUC = 0,607, R² = −0,052. Ne pas utiliser pour une décision thérapeutique.
        </span>
      </div>

      {/* Alerte faible confiance */}
      {confPct < 60 && (
        <div className="p-3 rounded-xl bg-yellow-500/10 border border-yellow-500/20 flex items-start gap-2 text-xs text-yellow-300">
          <HelpCircle className="w-4 h-4 shrink-0 mt-0.5" />
          <span>Confiance moyenne faible ({confPct} %). Signal court ou bruité — résultats indicatifs.</span>
        </div>
      )}
    </div>
  )
}

/* ── Tableau d'époques avec pagination ── */
function EpochTable({ epochs }) {
  const [page, setPage] = useState(0)
  const totalPages = Math.max(1, Math.ceil(epochs.length / PAGE_SIZE))
  const slice = epochs.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  return (
    <div className="card overflow-hidden">
      <div className="p-4 border-b border-nc-border flex items-center justify-between flex-wrap gap-2">
        <h3 className="text-sm font-semibold text-nc-text">Époques analysées</h3>
        <span className="text-xs text-nc-muted">
          {epochs.length} époques · page {page + 1} / {totalPages}
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-nc-border bg-nc-surface2/40">
              {['#', 'Temps', 'État ML', 'Confiance', 'Concentration', 'Stress', 'Amplitude µV', '⚠'].map(h => (
                <th key={h} className="px-3 py-2 text-start text-nc-muted font-semibold uppercase tracking-wide text-[10px]">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slice.map((ep) => {
              const pred  = ep.ml_prediction ?? {}
              const state = pred.uncertain ? 'uncertain' : (pred.state ?? 'uncertain')
              const sm    = ML_STATE[state] ?? ML_STATE.uncertain
              const conf  = Math.round((pred.confidence ?? 0) * 100)

              return (
                <tr key={ep.epoch_idx} className="border-b border-nc-border hover:bg-nc-surface2/40 transition-colors">
                  <td className="px-3 py-2 font-mono text-nc-muted">{ep.epoch_idx}</td>
                  <td className="px-3 py-2 font-mono text-nc-muted">{ep.time_s?.toFixed(1)}s</td>
                  <td className="px-3 py-2">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full
                                     text-[10px] font-bold border ${sm.bg} ${sm.color} ${sm.border}`}>
                      {sm.icon} {sm.label}
                    </span>
                  </td>
                  <td className="px-3 py-2">
                    <div className="flex items-center gap-2">
                      <div className="w-14 h-1.5 rounded-full bg-nc-surface2 overflow-hidden">
                        <div
                          className={`h-full rounded-full ${conf >= 60 ? 'bg-nc-accent' : 'bg-yellow-500'}`}
                          style={{ width: `${conf}%` }}
                        />
                      </div>
                      <span className="font-mono text-nc-text">{conf}%</span>
                    </div>
                  </td>
                  <td className="px-3 py-2 font-mono text-emerald-400">
                    {Math.round(pred.concentration?.pct ?? 0)}%
                  </td>
                  <td className="px-3 py-2 font-mono text-red-400">
                    {Math.round(pred.stress?.pct ?? 0)}%
                  </td>
                  <td className="px-3 py-2 font-mono text-nc-muted">
                    {ep.amplitude_uv?.toFixed(1) ?? '—'}
                  </td>
                  <td className="px-3 py-2">
                    {pred.uncertain
                      ? <span className="text-yellow-400 font-semibold">⚠</span>
                      : <span className="text-nc-muted">—</span>}
                  </td>
                </tr>
              )
            })}
            {slice.length === 0 && (
              <tr>
                <td colSpan={8} className="px-4 py-10 text-center text-nc-muted">
                  Aucune époque disponible.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {totalPages > 1 && (
        <div className="p-3 border-t border-nc-border flex items-center justify-end gap-3">
          <button
            disabled={page === 0}
            onClick={() => setPage(p => p - 1)}
            className="p-1.5 rounded-lg text-nc-muted hover:text-nc-text hover:bg-nc-surface2
                       disabled:opacity-30 transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-xs text-nc-muted font-mono">{page + 1} / {totalPages}</span>
          <button
            disabled={page >= totalPages - 1}
            onClick={() => setPage(p => p + 1)}
            className="p-1.5 rounded-lg text-nc-muted hover:text-nc-text hover:bg-nc-surface2
                       disabled:opacity-30 transition-colors"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  )
}

/* ── Page principale EEGFile ── */
export default function EEGFile() {
  const navigate   = useNavigate()
  const fileRef    = useRef()
  const [dragging, setDragging] = useState(false)
  const [loading,  setLoading]  = useState(false)
  const [result,   setResult]   = useState(null)
  const [error,    setError]    = useState('')
  const [progress, setProgress] = useState('')
  const [saved, setSaved] = useState(false)

  const handleFile = useCallback(async (file) => {
    if (!file) return
    const ext = file.name.split('.').pop().toLowerCase()
    if (!['edf', 'csv', 'txt'].includes(ext)) {
      setError(`Format non supporté : .${ext} — utilisez .edf, .csv ou .txt`)
      return
    }
    setError('')
    setResult(null)
    setSaved(false)
    setLoading(true)
    setProgress(`Lecture de ${file.name}…`)

    try {
      setProgress('Pipeline DSP v8.0 + Golden Filter + Classification IA en cours…')
      const data = await eegApi.analyzeFile(file)
      setResult(data)
      // Sauvegarde automatique — visible au thérapeute sans action patient
      const s = data.summary ?? {}
      try {
        await eegApi.sendReport({
          type:              'file',
          filename:          data.filename,
          duration_s:        data.duration_s,
          n_epochs_accepted: data.n_epochs_accepted,
          n_epochs_rejected: (data.n_epochs_total ?? 0) - (data.n_epochs_accepted ?? 0),
          dominant_state:    s.dominant_state,
          concentration_pct: s.mean_conc_score   != null ? parseFloat((s.mean_conc_score   * 10).toFixed(1)) : s.concentration_pct,
          stress_pct:        s.mean_stress_score  != null ? parseFloat((s.mean_stress_score * 10).toFixed(1)) : s.stress_pct,
          uncertain_pct:     s.uncertain_pct,
          mean_confidence:   s.mean_confidence,
          states_json:       {},
        })
        setSaved(true)
      } catch {
        // Silencieux si table non créée — le résultat s'affiche quand même
      }
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || 'Erreur lors de l\'analyse')
    } finally {
      setLoading(false)
      setProgress('')
    }
  }, [])

  const onDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file) handleFile(file)
  }, [handleFile])

  const onDragOver  = useCallback((e) => { e.preventDefault(); setDragging(true) },  [])
  const onDragLeave = useCallback(() => setDragging(false), [])

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 py-6 space-y-6">

      {/* ── En-tête ── */}
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/eeg')}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="w-10 h-10 rounded-2xl flex items-center justify-center bg-purple-500/15">
          <FileText className="w-5 h-5 text-purple-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-nc-text">Analyse de fichier EEG</h1>
          <p className="text-sm text-nc-muted">EDF · CSV · TXT — Analyse DSP + Classification IA</p>
        </div>
      </div>

      {/* ── Zone de dépôt ── */}
      {!result && !loading && (
        <div
          onClick={() => fileRef.current?.click()}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          className={`card p-14 text-center cursor-pointer transition-all duration-200 border-2 border-dashed
            ${dragging
              ? 'border-purple-400/70 bg-purple-500/10'
              : 'border-nc-border/60 hover:border-purple-400/40 hover:bg-purple-500/5'}`}
        >
          <div className="flex flex-col items-center gap-5">
            <div className={`w-16 h-16 rounded-2xl flex items-center justify-center transition-all
                            ${dragging ? 'bg-purple-500/30' : 'bg-purple-500/15'}`}>
              <Upload className={`w-8 h-8 transition-colors ${dragging ? 'text-purple-300' : 'text-purple-400'}`} />
            </div>

            <div>
              <p className="text-lg font-semibold text-nc-text">
                {dragging ? 'Déposez le fichier ici' : 'Glissez un fichier EEG ici'}
              </p>
              <p className="text-sm text-nc-muted mt-1">ou cliquez pour sélectionner depuis votre ordinateur</p>
            </div>

            <div className="flex gap-2">
              {['.EDF', '.CSV', '.TXT'].map(f => (
                <span key={f}
                  className="px-3 py-1.5 rounded-lg bg-nc-surface2 border border-nc-border
                             text-xs font-mono font-semibold text-nc-muted">
                  {f}
                </span>
              ))}
            </div>

            <div className="max-w-sm space-y-1 text-xs text-nc-muted/70">
              <p>Le signal sera rééchantillonné à 250 Hz si nécessaire.</p>
              <p>Durée recommandée : 30 s minimum pour de bons résultats.</p>
            </div>
          </div>
          <input
            ref={fileRef}
            type="file"
            accept=".edf,.csv,.txt"
            className="hidden"
            onChange={e => handleFile(e.target.files[0])}
          />
        </div>
      )}

      {/* ── Erreur ── */}
      {error && (
        <div className="card p-4 flex items-start gap-3 border-red-500/25 bg-red-500/5">
          <AlertTriangle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-red-400">Erreur d'analyse</p>
            <p className="text-xs text-nc-muted mt-0.5">{error}</p>
          </div>
          <button
            onClick={() => { setError(''); setResult(null) }}
            className="text-xs text-nc-muted hover:text-nc-text underline shrink-0"
          >
            Réessayer
          </button>
        </div>
      )}

      {/* ── Chargement ── */}
      {loading && (
        <div className="card p-14 text-center space-y-5">
          <div className="w-12 h-12 border-2 border-purple-400/30 border-t-purple-400 rounded-full animate-spin mx-auto" />
          <div>
            <p className="text-sm font-semibold text-nc-text">Analyse en cours…</p>
            <p className="text-xs text-nc-muted mt-1">{progress}</p>
          </div>
          <div className="flex justify-center gap-3 text-[10px] text-nc-muted/60 flex-wrap">
            <span>Golden Filter 1–45 Hz</span>
            <span>·</span>
            <span>Z-score époques</span>
            <span>·</span>
            <span>EEGNet Concentration (AUC 0,751)</span>
            <span>·</span>
            <span>EEGNet_LR Stress (AUC 0,607)</span>
          </div>
        </div>
      )}

      {/* ── Résultats ── */}
      {result && (
        <div className="space-y-5">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-2 flex-wrap">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span className="text-sm font-semibold text-nc-text">Analyse terminée avec succès</span>
              {saved && (
                <span className="flex items-center gap-1 text-xs font-medium text-emerald-400
                                 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
                  <CheckCircle2 className="w-3 h-3" /> Rapport enregistré pour le thérapeute
                </span>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              {/* Bouton feedback adaptatif */}
              <button
                onClick={() => {
                  const s = result.summary ?? {}
                  const acceptedEpochs = (result.epochs ?? []).filter(e => !e.ml_prediction?.uncertain)
                  const avgFeature = (key) => {
                    const vals = acceptedEpochs.map(e => e.features?.[key] ?? 0).filter(v => v > 0)
                    return vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0
                  }
                  navigate('/neurofeedback?mode=file', {
                    state: {
                      eeg_state:                 s.dominant_state ?? 'neutral',
                      classification_confidence:  s.mean_confidence ?? 0,
                      features_snapshot: {
                        rel_alpha:   avgFeature('rel_alpha'),
                        rel_beta:    avgFeature('rel_beta'),
                        rel_theta:   avgFeature('rel_theta'),
                        theta_beta:  avgFeature('theta_beta'),
                        engagement:  avgFeature('engagement'),
                        higuchi_fd:  avgFeature('higuchi_fd'),
                      },
                    },
                  })
                }}
                className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-xs font-semibold
                           btn-primary"
              >
                <Sparkles className="w-3.5 h-3.5" /> Obtenir un feedback adapté
              </button>
              <button
                onClick={() => exportJSON(result)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs text-nc-muted
                           hover:text-nc-text border border-nc-border hover:bg-nc-surface2 transition-colors"
              >
                <Download className="w-3.5 h-3.5" /> Exporter JSON
              </button>
              <button
                onClick={() => { setResult(null); setError(''); setSaved(false) }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs text-nc-muted
                           hover:text-nc-text border border-nc-border hover:bg-nc-surface2 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Analyser un autre fichier
              </button>
              <button
                onClick={() => navigate('/eeg')}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs text-nc-muted
                           hover:text-nc-text border border-nc-border hover:bg-nc-surface2 transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Retour
              </button>
            </div>
          </div>

          <MLSummaryCard
            summary={result.summary ?? {}}
            filename={result.filename}
            duration_s={result.duration_s}
            n_epochs_total={result.n_epochs_total}
            n_epochs_accepted={result.n_epochs_accepted}
            fs={result.fs}
            signal_quality={result.signal_quality ?? 'moyenne'}
          />

          {/* ── Carte CTA Neurofeedback ── */}
          {(() => {
            const s      = result.summary ?? {}
            const dom    = s.dominant_state ?? 'uncertain'
            const conf   = Math.round((s.mean_confidence ?? 0) * 100)
            const domMeta = ML_STATE[dom] ?? ML_STATE.uncertain

            const launchFeedback = () => {
              const accepted = (result.epochs ?? []).filter(e => !e.ml_prediction?.uncertain)
              const avg = key => {
                const vals = accepted.map(e => e.features?.[key] ?? 0).filter(v => v > 0)
                return vals.length > 0 ? vals.reduce((a, b) => a + b, 0) / vals.length : 0
              }
              navigate('/feedback/session', {
                state: {
                  eeg_state:                 dom,
                  classification_confidence:  s.mean_confidence ?? 0,
                  features_snapshot: {
                    rel_alpha:   avg('rel_alpha'),
                    rel_beta:    avg('rel_beta'),
                    rel_theta:   avg('rel_theta'),
                    theta_beta:  avg('theta_beta'),
                    engagement:  avg('engagement'),
                    higuchi_fd:  avg('higuchi_fd'),
                    stress_idx:  avg('stress_idx'),
                    rms_uv:      avg('rms_uv'),
                  },
                },
              })
            }

            return (
              <div className={`card p-6 flex items-center gap-5 flex-wrap border-2 ${domMeta.border} ${domMeta.bg}`}>
                <div className="w-14 h-14 rounded-2xl bg-nc-accent/15 flex items-center justify-center shrink-0">
                  <Sparkles className="w-7 h-7 text-nc-accent" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-base font-bold text-nc-text">Obtenir un neurofeedback personnalisé</p>
                  <p className="text-sm text-nc-muted mt-1 leading-relaxed">
                    État dominant détecté : <span className={`font-semibold ${domMeta.color}`}>{domMeta.label}</span>
                    {' '}({conf}% de confiance) — le système va recommander le feedback adapté à vos features EEG,{' '}
                    justifier son choix et vous guider pas à pas.
                  </p>
                  <p className="text-xs text-nc-muted/70 mt-1">
                    Jeux · Images · Vidéos · Audio · Respiration guidée — tous personnalisés selon votre profil
                  </p>
                </div>
                <button
                  onClick={launchFeedback}
                  className="btn-primary flex items-center gap-2 px-6 py-3 rounded-xl font-semibold shrink-0"
                >
                  <Sparkles className="w-5 h-5" />
                  Démarrer le neurofeedback →
                </button>
              </div>
            )
          })()}

          {result.epochs?.length > 0 && <EpochTable epochs={result.epochs} />}
        </div>
      )}
    </div>
  )
}
