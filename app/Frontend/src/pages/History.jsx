import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { sessions as sessionsApi } from '../utils/api'
import { exportSessionPDF } from '../utils/exportPDF'
import {
  History as HistoryIcon, Download, Eye, Activity, CalendarDays,
  Clock, FileText, FileDown,
} from 'lucide-react'

const BASE = import.meta.env.VITE_API_URL || '/api'

function SkeletonRow() {
  return (
    <tr className="border-b border-nc-border/50">
      {[1,2,3,4,5,6].map((i) => (
        <td key={i} className="py-4 px-4">
          <div className="h-4 rounded bg-nc-surface2 animate-pulse" style={{ width: `${60 + i * 10}%` }} />
        </td>
      ))}
    </tr>
  )
}

export default function History() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [sessionList, setSessionList] = useState([])
  const [loading, setLoading]         = useState(true)
  const [exportingPDF, setExportingPDF] = useState(null)
  const [exportingAll,  setExportingAll]  = useState(false)

  useEffect(() => {
    sessionsApi.list()
      .then((d) => setSessionList(Array.isArray(d) ? d : []))
      .catch(() => setSessionList([]))
      .finally(() => setLoading(false))
  }, [])

  // ── Export single session CSV ────────────────────────────────────────────────
  const handleExportCSV = async (id, e) => {
    e.stopPropagation()
    try {
      const res = await sessionsApi.exportCSV(id)
      const url = URL.createObjectURL(res.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `session_${id.slice(0, 8)}.csv`
      a.click()
      URL.revokeObjectURL(url)
    } catch { /* silent */ }
  }

  // ── Export single session PDF ────────────────────────────────────────────────
  const handleExportPDF = async (session, e) => {
    e.stopPropagation()
    setExportingPDF(session.id)
    try {
      let report = null
      try { report = await sessionsApi.getReport(session.id) } catch {}
      await exportSessionPDF(session, report)
    } catch (err) {
      console.error('PDF export failed', err)
    } finally {
      setExportingPDF(null)
    }
  }

  // ── Export all sessions CSV ──────────────────────────────────────────────────
  const handleExportAll = async () => {
    setExportingAll(true)
    try {
      const token = localStorage.getItem('neurocap_token')
      const res = await fetch(`${BASE}/sessions/export/all`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('Export failed')
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'neurocap_sessions.csv'
      a.click()
      URL.revokeObjectURL(url)
    } catch {}
    finally { setExportingAll(false) }
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">

      {/* Header */}
      <div className="flex items-start justify-between animate-slide-up">
        <div>
          <div className="flex items-center gap-2 text-nc-muted text-sm mb-1">
            <HistoryIcon className="w-4 h-4" />
            {t('history.title')}
          </div>
          <h1 className="text-3xl font-bold text-nc-text">{t('history.title')}</h1>
        </div>
        {sessionList.length > 0 && (
          <button
            onClick={handleExportAll}
            disabled={exportingAll}
            className="btn-ghost flex items-center gap-2 text-sm"
          >
            <FileDown className="w-4 h-4" />
            {exportingAll ? 'Export…' : 'Export CSV global'}
          </button>
        )}
      </div>

      {/* Table card */}
      <div className="card overflow-hidden animate-fade-in">
        <div className="px-6 py-4 border-b border-nc-border flex items-center gap-2">
          <CalendarDays className="w-4 h-4 text-nc-accent" />
          <span className="font-semibold text-nc-text">{sessionList.length} {t('common.sessions')}</span>
        </div>

        {!loading && sessionList.length === 0 && (
          <div className="flex flex-col items-center justify-center py-20 gap-4">
            <div className="w-16 h-16 rounded-full flex items-center justify-center" style={{ background: 'rgb(var(--nc-accent)/0.1)' }}>
              <Activity className="w-8 h-8 text-nc-accent" />
            </div>
            <h3 className="font-semibold text-nc-text">{t('history.empty')}</h3>
            <p className="text-nc-muted text-sm">{t('history.empty_sub')}</p>
            <button className="btn-primary mt-1" onClick={() => navigate('/session/new')}>
              {t('dashboard.start_session')}
            </button>
          </div>
        )}

        {(loading || sessionList.length > 0) && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-nc-border text-nc-muted text-xs uppercase tracking-wider">
                  <th className="py-3 px-6 text-start font-medium">{t('history.table.session')}</th>
                  <th className="py-3 px-4 text-start font-medium">{t('history.table.date')}</th>
                  <th className="py-3 px-4 text-start font-medium">{t('history.table.type')}</th>
                  <th className="py-3 px-4 text-center font-medium">{t('history.table.duration')}</th>
                  <th className="py-3 px-4 text-center font-medium">{t('history.table.score')}</th>
                  <th className="py-3 px-4 text-center font-medium">{t('history.table.actions')}</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? [1,2,3,4,5].map((i) => <SkeletonRow key={i} />)
                  : sessionList.map((s, i) => {
                      const durationMin = s.duration_seconds ? Math.round(s.duration_seconds / 60) : null
                      const score = s.session_score ?? s.score ?? null
                      const isPDFing = exportingPDF === s.id
                      return (
                        <tr key={s.id ?? i}
                            className="border-b border-nc-border/50 hover:bg-nc-surface2 transition-colors cursor-pointer group"
                            onClick={() => navigate(`/session/${s.id}`)}>
                          <td className="py-3.5 px-6">
                            <div className="flex items-center gap-3">
                              <div className="w-8 h-8 rounded-xl flex items-center justify-center shrink-0"
                                   style={{ background: 'rgb(var(--nc-accent)/0.1)' }}>
                                <span className="text-xs font-bold text-nc-accent">{i + 1}</span>
                              </div>
                              <span className="font-medium text-nc-text">Session {i + 1}</span>
                            </div>
                          </td>
                          <td className="py-3.5 px-4 text-nc-muted">
                            <div className="flex items-center gap-1.5">
                              <CalendarDays className="w-3.5 h-3.5" />
                              {new Date(s.created_at).toLocaleDateString()}
                            </div>
                          </td>
                          <td className="py-3.5 px-4">
                            <span className="badge-accent capitalize">{s.objective ?? s.feedback_mode ?? '—'}</span>
                          </td>
                          <td className="py-3.5 px-4 text-center">
                            {durationMin !== null ? (
                              <div className="flex items-center justify-center gap-1 text-nc-muted">
                                <Clock className="w-3.5 h-3.5" />
                                {durationMin} {t('history.mins')}
                              </div>
                            ) : '—'}
                          </td>
                          <td className="py-3.5 px-4 text-center">
                            {score !== null ? (
                              <span className={`font-bold ${score >= 70 ? 'text-nc-success' : score >= 50 ? 'text-nc-warning' : 'text-nc-danger'}`}>
                                {score.toFixed(1)}%
                              </span>
                            ) : '—'}
                          </td>
                          <td className="py-3.5 px-4">
                            <div className="flex items-center justify-center gap-1">
                              {/* View */}
                              <button
                                className="btn-ghost p-2 rounded-lg"
                                onClick={(e) => { e.stopPropagation(); navigate(`/session/${s.id}`) }}
                                title="Voir le rapport"
                              >
                                <Eye className="w-3.5 h-3.5" />
                              </button>
                              {/* CSV */}
                              <button
                                className="btn-ghost p-2 rounded-lg"
                                onClick={(e) => handleExportCSV(s.id, e)}
                                title="Export CSV (événements)"
                              >
                                <Download className="w-3.5 h-3.5" />
                              </button>
                              {/* PDF */}
                              <button
                                className="btn-ghost p-2 rounded-lg"
                                onClick={(e) => handleExportPDF(s, e)}
                                disabled={isPDFing}
                                title="Export PDF"
                              >
                                {isPDFing
                                  ? <span className="w-3.5 h-3.5 border border-nc-accent/40 border-t-nc-accent rounded-full animate-spin inline-block" />
                                  : <FileText className="w-3.5 h-3.5" />}
                              </button>
                            </div>
                          </td>
                        </tr>
                      )
                    })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
