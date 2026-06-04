import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Music, ListMusic, Star, ThumbsUp, ThumbsDown, ChevronRight,
  Plus, Brain, FileText, Sparkles, RefreshCw, PlayCircle, AlertCircle,
} from 'lucide-react'
import { useAuthStore } from '../stores'
import { recommendations as recoApi } from '../utils/api'

// ── Helpers ───────────────────────────────────────────────────────────────────

function StatBadge({ label, value, color = 'text-nc-accent' }) {
  return (
    <div className="card p-4 text-center">
      <p className={`text-2xl font-bold font-mono ${color}`}>{value}</p>
      <p className="text-xs text-nc-muted mt-1">{label}</p>
    </div>
  )
}

// ── Recommendations card ──────────────────────────────────────────────────────

function RecommendationCard({ rec }) {
  const score = Math.round((rec.score || 0) * 100)
  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-nc-surface2 border border-nc-border hover:border-nc-accent/40 transition-colors">
      <div className="w-9 h-9 rounded-xl bg-nc-accent/15 flex items-center justify-center shrink-0">
        <Sparkles className="w-4 h-4 text-nc-accent" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-nc-text truncate">
          {rec.media?.filename || rec.media_id || 'Média recommandé'}
        </p>
        {rec.reason && (
          <p className="text-[10px] text-nc-muted truncate">{rec.reason}</p>
        )}
      </div>
      <div className="text-right shrink-0">
        <p className="text-sm font-bold text-emerald-400">{score}%</p>
        <p className="text-[9px] text-nc-muted">score</p>
      </div>
    </div>
  )
}

// ── Playlist card ─────────────────────────────────────────────────────────────

function PlaylistCard({ playlist, onOpen }) {
  return (
    <div
      onClick={onOpen}
      className={`card p-4 cursor-pointer hover:shadow-md hover:border-nc-accent/30 transition-all space-y-2
        ${playlist.is_therapeutic ? 'border-emerald-500/25 bg-emerald-500/4' : ''}`}
    >
      <div className="flex items-center gap-2">
        <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0
          ${playlist.is_therapeutic ? 'bg-emerald-500/15' : 'bg-nc-accent/15'}`}>
          <ListMusic className={`w-4 h-4 ${playlist.is_therapeutic ? 'text-emerald-400' : 'text-nc-accent'}`} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-nc-text truncate">{playlist.name}</p>
          <p className="text-[10px] text-nc-muted">
            {playlist.is_therapeutic ? '⚕ Thérapeutique' : 'Personnelle'}
            {' · '}par {playlist.created_by_role}
          </p>
        </div>
        <ChevronRight className="w-4 h-4 text-nc-muted shrink-0" />
      </div>
      {playlist.description && (
        <p className="text-xs text-nc-muted line-clamp-2">{playlist.description}</p>
      )}
    </div>
  )
}

// ── Offline rec card ──────────────────────────────────────────────────────────

function OfflineRecCard({ rec, onFeedback }) {
  const stateColors = { focus: 'text-blue-400', stress: 'text-red-400', neutral: 'text-nc-muted' }
  const stateLabels = { focus: 'Concentration', stress: 'Stress', neutral: 'Neutre' }

  return (
    <div className="flex items-center gap-3 p-3 rounded-xl bg-nc-surface2 border border-nc-border">
      <div className="text-center shrink-0 w-10">
        <p className="text-[9px] text-nc-muted">époque</p>
        <p className="text-sm font-bold font-mono text-nc-text">{rec.epoch_idx}</p>
      </div>
      <div className="flex-1 min-w-0">
        <p className={`text-xs font-semibold ${stateColors[rec.eeg_state] || 'text-nc-muted'}`}>
          {stateLabels[rec.eeg_state] || rec.eeg_state}
        </p>
        <p className="text-[10px] text-nc-muted truncate">{rec.media_type}</p>
      </div>
      <p className="text-xs font-bold text-emerald-400 shrink-0">
        {Math.round((rec.score || 0) * 100)}%
      </p>
      {rec.liked == null ? (
        <div className="flex gap-1 shrink-0">
          <button
            onClick={() => onFeedback(rec.id, true)}
            className="p-1.5 rounded-lg hover:bg-emerald-500/15 text-nc-muted hover:text-emerald-400 transition-colors"
            title="J'aime"
          >
            <ThumbsUp className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => onFeedback(rec.id, false)}
            className="p-1.5 rounded-lg hover:bg-red-500/15 text-nc-muted hover:text-red-400 transition-colors"
            title="Je n'aime pas"
          >
            <ThumbsDown className="w-3.5 h-3.5" />
          </button>
        </div>
      ) : (
        <div className="shrink-0">
          {rec.liked
            ? <ThumbsUp className="w-3.5 h-3.5 text-emerald-400" />
            : <ThumbsDown className="w-3.5 h-3.5 text-red-400" />}
        </div>
      )}
    </div>
  )
}

// ── Create Playlist Modal ─────────────────────────────────────────────────────

function CreatePlaylistModal({ patientId, onClose, onCreate }) {
  const [name, setName] = useState('')
  const [desc, setDesc] = useState('')
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState('')

  const submit = async () => {
    if (!name.trim()) { setErr('Le nom est requis'); return }
    setLoading(true)
    setErr('')
    try {
      const pl = await recoApi.createPlaylist(patientId, name.trim(), desc.trim())
      onCreate(pl)
      onClose()
    } catch {
      setErr('Impossible de créer la playlist')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="card w-full max-w-sm mx-4 p-6 space-y-4">
        <h3 className="text-base font-bold text-nc-text">Nouvelle playlist</h3>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-nc-muted mb-1 block">Nom *</label>
            <input
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Ma playlist de concentration"
              className="w-full bg-nc-surface2 border border-nc-border rounded-xl px-3 py-2 text-sm text-nc-text placeholder:text-nc-muted focus:outline-none focus:border-nc-accent/60"
            />
          </div>
          <div>
            <label className="text-xs text-nc-muted mb-1 block">Description</label>
            <textarea
              value={desc}
              onChange={e => setDesc(e.target.value)}
              placeholder="Optionnel…"
              rows={2}
              className="w-full bg-nc-surface2 border border-nc-border rounded-xl px-3 py-2 text-sm text-nc-text placeholder:text-nc-muted focus:outline-none focus:border-nc-accent/60 resize-none"
            />
          </div>
        </div>
        {err && <p className="text-xs text-red-400">{err}</p>}
        <div className="flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 py-2 rounded-xl text-sm text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-colors border border-nc-border"
          >
            Annuler
          </button>
          <button
            onClick={submit}
            disabled={loading}
            className="flex-1 py-2 rounded-xl text-sm font-semibold btn-primary disabled:opacity-50"
          >
            {loading ? 'Création…' : 'Créer'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Offline Recommendations Section ──────────────────────────────────────────

function OfflineRecsSection({ patientId, reports }) {
  const [selectedReport, setSelectedReport] = useState(null)
  const [recs, setRecs] = useState([])
  const [loading, setLoading] = useState(false)

  const loadRecs = async (report) => {
    setSelectedReport(report)
    setLoading(true)
    try {
      const data = await recoApi.offlineRecs(patientId, report.id)
      setRecs(data || [])
    } catch {
      setRecs([])
    } finally {
      setLoading(false)
    }
  }

  const handleFeedback = async (recId, liked) => {
    try {
      await recoApi.offlineRecFeedback(patientId, recId, liked)
      setRecs(prev => prev.map(r => r.id === recId ? { ...r, liked } : r))
    } catch {
      // silently fail
    }
  }

  if (!reports.length) return (
    <div className="text-center py-8 text-nc-muted text-sm">
      <FileText className="w-8 h-8 mx-auto mb-2 opacity-30" />
      Aucun rapport EEG analysé pour le moment
    </div>
  )

  return (
    <div className="space-y-4">
      <p className="text-xs text-nc-muted">Sélectionnez un rapport EEG pour voir les recommandations par époque :</p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {reports.map(r => (
          <button
            key={r.id}
            onClick={() => loadRecs(r)}
            className={`text-left p-3 rounded-xl border transition-all text-sm
              ${selectedReport?.id === r.id
                ? 'border-nc-accent bg-nc-accent/8 text-nc-text'
                : 'border-nc-border bg-nc-surface2 text-nc-muted hover:border-nc-accent/40 hover:text-nc-text'}`}
          >
            <p className="font-semibold truncate">{r.filename || `Rapport ${r.id.slice(0, 8)}`}</p>
            <p className="text-[10px] mt-0.5">
              {r.dominant_state || '—'} · {r.offline_recommendations_count || 0} recos
            </p>
          </button>
        ))}
      </div>

      {selectedReport && (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <p className="text-xs font-semibold text-nc-text">
              Recommandations — {selectedReport.filename || selectedReport.id.slice(0, 8)}
            </p>
            {loading && <div className="w-3 h-3 border border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />}
          </div>
          {!loading && recs.length === 0 && (
            <div className="text-center py-4 text-nc-muted text-xs">
              <AlertCircle className="w-5 h-5 mx-auto mb-1 opacity-40" />
              Aucune recommandation générée — analysez le rapport d'abord
            </div>
          )}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {recs.map(r => (
              <OfflineRecCard key={r.id} rec={r} onFeedback={handleFeedback} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function PatientMediaDashboard() {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const patientId = user?.id

  const [dashboard, setDashboard] = useState(null)
  const [playlists, setPlaylists] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [showCreatePlaylist, setShowCreatePlaylist] = useState(false)
  const [activeTab, setActiveTab] = useState('recommendations')

  const fetchData = useCallback(async (silent = false) => {
    if (!patientId) return
    if (!silent) setLoading(true)
    else setRefreshing(true)
    try {
      const [dash, pls] = await Promise.all([
        recoApi.patientDashboard(patientId),
        recoApi.listPlaylists(patientId),
      ])
      setDashboard(dash)
      setPlaylists(pls || [])
    } catch {
      // ignore — show empty state
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [patientId])

  useEffect(() => { fetchData() }, [fetchData])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
    </div>
  )

  const pendingRecs = dashboard?.pending_recommendations || []
  const recentReports = dashboard?.recent_eeg_reports || []
  const totalRecs = pendingRecs.length
  const totalPlaylists = playlists.length

  const TABS = [
    { id: 'recommendations', label: 'Recommandations', icon: Sparkles, count: totalRecs },
    { id: 'playlists',       label: 'Playlists',       icon: ListMusic, count: totalPlaylists },
    { id: 'offline',         label: 'Analyses EEG',    icon: FileText,  count: recentReports.length },
  ]

  return (
    <div className="max-w-4xl mx-auto px-4 py-6 space-y-6">

      {/* Header */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="w-12 h-12 rounded-2xl bg-purple-500/15 flex items-center justify-center">
          <Music className="w-6 h-6 text-purple-400" />
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-nc-text">Médias & Recommandations</h1>
          <p className="text-sm text-nc-muted">
            Playlists personnelles, recommandations EEG et analyses offline
          </p>
        </div>
        <button
          onClick={() => fetchData(true)}
          disabled={refreshing}
          className="p-2 rounded-xl text-nc-muted hover:text-nc-accent hover:bg-nc-surface2 transition-colors"
          title="Actualiser"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin text-nc-accent' : ''}`} />
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <StatBadge label="Recommandations en attente" value={totalRecs} color="text-nc-accent" />
        <StatBadge label="Playlists" value={totalPlaylists} color="text-purple-400" />
        <StatBadge label="Rapports EEG" value={recentReports.length} color="text-emerald-400" />
      </div>

      {/* EEG profile summary */}
      {dashboard && (
        <div className="card p-4 flex items-center gap-3">
          <Brain className="w-5 h-5 text-nc-accent shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-semibold text-nc-text">
              Profil {dashboard.profile_type || '—'} · Palier {dashboard.palier || '—'}
            </p>
            <p className="text-xs text-nc-muted">
              {dashboard.total_sessions || 0} sessions ·{' '}
              score moyen{' '}
              {dashboard.avg_session_score != null ? `${dashboard.avg_session_score}%` : '—'}
              {dashboard.finetuning_status === 'done' && ' · Modèle personnalisé ✓'}
            </p>
          </div>
          <button
            onClick={() => navigate('/protocol')}
            className="flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-semibold btn-primary shrink-0"
          >
            Protocole <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-nc-surface2 border border-nc-border">
        {TABS.map(({ id, label, icon: Icon, count }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold transition-all
              ${activeTab === id
                ? 'bg-nc-accent text-white shadow-sm'
                : 'text-nc-muted hover:text-nc-text'}`}
          >
            <Icon className="w-3.5 h-3.5" />
            {label}
            {count > 0 && (
              <span className={`ml-1 px-1.5 py-0.5 rounded-full text-[9px] font-bold
                ${activeTab === id ? 'bg-white/20' : 'bg-nc-border text-nc-muted'}`}>
                {count}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="card p-5">

        {/* ── Recommandations ── */}
        {activeTab === 'recommendations' && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-nc-accent" />
              <h2 className="text-sm font-bold text-nc-text">Recommandations en attente</h2>
            </div>
            {pendingRecs.length === 0 ? (
              <div className="text-center py-8 text-nc-muted text-sm space-y-2">
                <Star className="w-8 h-8 mx-auto opacity-30" />
                <p>Aucune recommandation pour le moment</p>
                <p className="text-xs">Lancez une session EEG pour recevoir des suggestions adaptées</p>
                <button
                  onClick={() => navigate('/eeg')}
                  className="mt-2 flex items-center gap-1.5 mx-auto px-4 py-2 rounded-xl btn-primary text-xs font-semibold"
                >
                  <PlayCircle className="w-3.5 h-3.5" /> Démarrer une session EEG
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                {pendingRecs.map(r => (
                  <RecommendationCard key={r.id} rec={r} />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Playlists ── */}
        {activeTab === 'playlists' && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <ListMusic className="w-4 h-4 text-nc-accent" />
              <h2 className="text-sm font-bold text-nc-text">Mes playlists</h2>
              <button
                onClick={() => setShowCreatePlaylist(true)}
                className="ml-auto flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-semibold bg-nc-accent/10 text-nc-accent hover:bg-nc-accent/20 transition-colors"
              >
                <Plus className="w-3.5 h-3.5" /> Créer
              </button>
            </div>

            {playlists.length === 0 ? (
              <div className="text-center py-8 text-nc-muted text-sm space-y-2">
                <ListMusic className="w-8 h-8 mx-auto opacity-30" />
                <p>Aucune playlist pour le moment</p>
                <button
                  onClick={() => setShowCreatePlaylist(true)}
                  className="mt-2 flex items-center gap-1.5 mx-auto px-4 py-2 rounded-xl btn-primary text-xs font-semibold"
                >
                  <Plus className="w-3.5 h-3.5" /> Créer une playlist
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {playlists.map(pl => (
                  <PlaylistCard
                    key={pl.id}
                    playlist={pl}
                    onOpen={() => {}}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Analyses EEG offline ── */}
        {activeTab === 'offline' && (
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-nc-accent" />
              <h2 className="text-sm font-bold text-nc-text">Analyses EEG — Recommandations par époque</h2>
            </div>
            <OfflineRecsSection patientId={patientId} reports={recentReports} />
          </div>
        )}
      </div>

      {showCreatePlaylist && (
        <CreatePlaylistModal
          patientId={patientId}
          onClose={() => setShowCreatePlaylist(false)}
          onCreate={(pl) => setPlaylists(prev => [pl, ...prev])}
        />
      )}
    </div>
  )
}
