/**
 * NeuroCap – Live Session Page
 * WebSocket real-time EEG session with feedback (visual/sound/game).
 */
import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useSessionStore } from '../stores'
import { DualGauge } from '../components/EEGGauge'
import SignalQuality from '../components/SignalQuality'
import { VisualFeedback, SoundFeedback, GameFeedback } from '../components/FeedbackRenderer'
import {
  LineChart, Line, XAxis, YAxis, ResponsiveContainer, CartesianGrid,
} from 'recharts'
import Brain3D from '../components/Brain3D'
import TopoMap2D from '../components/TopoMap2D'
import {
  Pause, Play, Square, Eye, Volume2, Gamepad2, Timer, Box, Map,
} from 'lucide-react'

const MODE_OPTIONS_KEYS = ['visual', 'sound', 'game']
const MODE_ICONS = { visual: Eye, sound: Volume2, game: Gamepad2 }

export default function SessionLive() {
  const { t } = useTranslation()
  const { id } = useParams()
  const navigate = useNavigate()
  const {
    connect, disconnect, connected,
    concentration, stress, signalQuality, threshold, ewma,
    blockNumber, blockTimeSec, successRate,
    features, feedbackCommand, history,
    isPaused, togglePause, feedbackMode, setFeedbackMode,
  } = useSessionStore()

  const [ending, setEnding] = useState(false)
  const [brainView, setBrainView] = useState('3d')

  useEffect(() => {
    connect(id)
    return () => disconnect()
  }, [id])

  const handleEnd = () => {
    setEnding(true)
    disconnect()
    setTimeout(() => navigate(`/history/${id}`), 500)
  }

  // Chart data (last 60 frames)
  const chartData = history.slice(-60).map((f, i) => ({
    t: i,
    conc: f.concentration,
    seuil: f.threshold,
  }))

  const blockProgress = Math.min(100, (blockTimeSec / 180) * 100)

  return (
    <div className="h-full flex flex-col">
      {/* ── Top bar ── */}
      <div className="flex items-center justify-between px-6 py-3 border-b border-neuro-border bg-neuro-surface/50">
        <div className="flex items-center gap-4">
          <SignalQuality quality={signalQuality} connected={connected} />
          <div className="h-4 w-px bg-neuro-border" />
          <div className="flex items-center gap-2 text-sm">
            <Timer className="w-4 h-4 text-neuro-muted" />
            <span className="text-neuro-text font-mono">
              Bloc {blockNumber}/6
            </span>
            <div className="w-24 h-1.5 bg-neuro-border rounded-full overflow-hidden">
              <div
                className="h-full bg-neuro-accent rounded-full transition-all duration-500"
                style={{ width: `${blockProgress}%` }}
              />
            </div>
          </div>
          <div className="hidden sm:flex items-center gap-2 text-xs text-neuro-muted">
            Taux: <span className="text-neuro-text font-mono">{(successRate * 100).toFixed(0)}%</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button onClick={togglePause} className="btn-ghost flex items-center gap-1.5 text-sm">
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            {isPaused ? t('session.resume') : t('session.pause')}
          </button>
          <button onClick={handleEnd} className="btn-ghost text-neuro-danger flex items-center gap-1.5 text-sm">
            <Square className="w-4 h-4" /> {t('session.end_session')}
          </button>
        </div>
      </div>

      {/* ── Main content ── */}
      <div className="flex-1 grid lg:grid-cols-3 gap-4 p-4 overflow-hidden">
        {/* Left — Gauges + features */}
        <div className="space-y-4">
          {/* Gauges */}
          <div className="glass-card p-6 flex justify-center">
            <DualGauge concentration={concentration} stress={stress} size={120} />
          </div>

          {/* Features */}
          <div className="glass-card p-5 space-y-3">
            <h3 className="text-xs font-medium text-neuro-muted uppercase tracking-wider mb-3">
              EEG Features
            </h3>
            {[
              { label: 'Alpha', value: features.alpha, unit: 'µV²' },
              { label: 'TBR', value: features.theta_beta_ratio, unit: '' },
              { label: 'Engagement', value: features.engagement_index, unit: '' },
              { label: 'IAPF', value: features.iapf, unit: 'Hz' },
              { label: 'EWMA', value: ewma, unit: '' },
              { label: 'Seuil', value: threshold, unit: '' },
            ].map(({ label, value, unit }) => (
              <div key={label} className="flex justify-between items-center">
                <span className="text-xs text-neuro-muted">{label}</span>
                <span className="text-sm font-mono text-neuro-text">
                  {value != null ? (typeof value === 'number' ? value.toFixed(3) : value) : '—'}
                  <span className="text-neuro-muted ml-1 text-[10px]">{unit}</span>
                </span>
              </div>
            ))}
          </div>

          {/* Mode selector */}
          <div className="glass-card p-4">
            <h3 className="text-xs font-medium text-neuro-muted uppercase tracking-wider mb-3">
              {t('session.feedback_mode')}
            </h3>
            <div className="flex gap-2">
              {MODE_OPTIONS_KEYS.map((key) => {
                const Icon = MODE_ICONS[key]
                return (
                  <button
                    key={key}
                    onClick={() => setFeedbackMode(key)}
                    className={`flex-1 flex flex-col items-center gap-1.5 py-3 rounded-xl transition-all ${
                      feedbackMode === key
                        ? 'bg-neuro-accent/15 text-neuro-accent border border-neuro-accent/30'
                        : 'bg-neuro-surface text-neuro-muted hover:text-neuro-text border border-transparent'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="text-[10px] uppercase tracking-wider">{t(`session.modes.${key}`)}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Brain visualization toggle */}
          <div className="glass-card p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-xs font-medium text-neuro-muted uppercase tracking-wider">
                Cerveau
              </h3>
              <div className="flex gap-1 bg-neuro-bg rounded-lg p-0.5">
                <button
                  onClick={() => setBrainView('3d')}
                  className={`px-2 py-1 rounded text-[10px] ${brainView === '3d' ? 'bg-neuro-accent/15 text-neuro-accent' : 'text-neuro-muted'}`}
                >
                  <Box className="w-3 h-3" />
                </button>
                <button
                  onClick={() => setBrainView('2d')}
                  className={`px-2 py-1 rounded text-[10px] ${brainView === '2d' ? 'bg-neuro-accent/15 text-neuro-accent' : 'text-neuro-muted'}`}
                >
                  <Map className="w-3 h-3" />
                </button>
              </div>
            </div>
            <div className="h-[180px]">
              {brainView === '3d' ? (
                <Brain3D concentration={concentration} stress={stress} />
              ) : (
                <div className="flex justify-center">
                  <TopoMap2D concentration={concentration} features={features} size={170} />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Center — Feedback renderer */}
        <div className="glass-card p-6 flex items-center justify-center min-h-[300px]">
          {feedbackMode === 'visual' && (
            <VisualFeedback
              concentration={concentration}
              intensity={feedbackCommand.intensity ?? 0.5}
              isSuccess={feedbackCommand.is_success}
            />
          )}
          {feedbackMode === 'sound' && (
            <SoundFeedback
              concentration={concentration}
              intensity={feedbackCommand.intensity ?? 0.5}
              isPaused={isPaused}
            />
          )}
          {feedbackMode === 'game' && (
            <GameFeedback concentration={concentration} threshold={threshold} />
          )}
        </div>

        {/* Right — Real-time chart */}
        <div className="glass-card p-5 flex flex-col">
          <h3 className="text-xs font-medium text-neuro-muted uppercase tracking-wider mb-4">
            Concentration temps réel
          </h3>
          <div className="flex-1 min-h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#2a365440" />
                <XAxis hide />
                <YAxis domain={[0, 1]} tick={{ fill: '#64748b', fontSize: 10 }} />
                <Line
                  type="monotone" dataKey="conc" stroke="#00d4ff"
                  strokeWidth={2} dot={false} isAnimationActive={false}
                />
                <Line
                  type="monotone" dataKey="seuil" stroke="#f59e0b"
                  strokeWidth={1} strokeDasharray="4 4" dot={false} isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center gap-4 mt-3 text-xs text-neuro-muted">
            <span className="flex items-center gap-1.5">
              <div className="w-3 h-0.5 bg-neuro-accent rounded" /> Concentration
            </span>
            <span className="flex items-center gap-1.5">
              <div className="w-3 h-0.5 bg-neuro-warning rounded border-dashed" /> Seuil
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}