/**
 * AppRouter.jsx — Routage principal NeuroCap EEG
 *
 * Flux :
 *   WelcomePage
 *     ├── [Casque NeuroCap]  → WifiSetup → Dashboard live (App.jsx)
 *     ├── [Fichier EEG]      → FileDashboard (upload + résultats ML)
 *     │                           └── [Neurofeedback] → FeedbackSetup → FeedbackSession → FeedbackReport
 *     └── [NeuroFeedback]    → NeuroFeedbackHub (Protocole 15 + Feedback libre fusionnés)
 *                                 ├── [Protocole] → FeedbackSession → FeedbackReport → hub
 *                                 └── [Feedback libre] → FeedbackSession → FeedbackReport → hub
 */

import { useState } from 'react'
import WelcomePage        from './WelcomePage'
import WifiSetup          from './WifiSetup'
import FileDashboard      from './FileDashboard'
import Dashboard          from '../App'
import FeedbackSetup      from '../pages/FeedbackSetup'
import FeedbackSession    from '../pages/FeedbackSession'
import FeedbackReport     from '../pages/FeedbackReport'
import NeuroFeedbackHub   from './NeuroFeedbackHub'

export default function AppRouter() {
  // 'welcome' | 'hardware-wifi' | 'hardware-live' | 'file'
  // 'neurofeedback'
  // 'feedback-setup' | 'feedback-session' | 'feedback-report'
  const [mode, setMode] = useState('welcome')

  // Données transmises entre les pages feedback
  const [feedbackData,    setFeedbackData]    = useState(null)
  const [feedbackSession, setFeedbackSession] = useState(null)
  const [feedbackReport,  setFeedbackReport]  = useState(null)

  // Permet de savoir où revenir après le rapport (hub ou file)
  const [returnMode, setReturnMode] = useState('file')

  // ── Welcome ──────────────────────────────────────────────────────
  if (mode === 'welcome') {
    return (
      <WelcomePage
        onHardware={() => setMode('hardware-wifi')}
        onFile={() => setMode('file')}
        onNeuroFeedback={() => setMode('neurofeedback')}
      />
    )
  }

  // ── Hub NeuroFeedback (Protocole 15 + Feedback libre) ────────────
  if (mode === 'neurofeedback') {
    return (
      <NeuroFeedbackHub
        userId="demo"
        onBack={() => setMode('welcome')}
        onStartProtocolSession={(sessionN) => {
          setReturnMode('neurofeedback')
          setFeedbackSession({ sessionId: null, eegState: 'neutral', features: {}, sessionN })
          setMode('feedback-session')
        }}
        onStartFeedback={(sessionId, eegState, features) => {
          setReturnMode('neurofeedback')
          setFeedbackSession({ sessionId, eegState, features })
          setMode('feedback-session')
        }}
      />
    )
  }

  // ── Mode hardware : WiFi setup ────────────────────────────────────
  if (mode === 'hardware-wifi') {
    return (
      <WifiSetup
        onDone={() => setMode('hardware-live')}
        onBack={() => setMode('welcome')}
      />
    )
  }

  // ── Mode hardware : dashboard temps réel ─────────────────────────
  if (mode === 'hardware-live') {
    return <Dashboard onBack={() => setMode('welcome')} />
  }

  // ── Mode fichier : upload + résultats ────────────────────────────
  if (mode === 'file') {
    return (
      <FileDashboard
        onBack={() => setMode('welcome')}
        onFeedback={(data) => {
          setFeedbackData(data)
          setReturnMode('file')
          setMode('feedback-setup')
        }}
      />
    )
  }

  // ── ÉCRAN 1 — configuration de la séance (depuis fichier EEG) ────
  if (mode === 'feedback-setup') {
    return (
      <FeedbackSetup
        data={feedbackData}
        onStart={(sessionId, eegState, features) => {
          setFeedbackSession({ sessionId, eegState, features })
          setMode('feedback-session')
        }}
        onBack={() => setMode(feedbackData ? 'file' : 'welcome')}
      />
    )
  }

  // ── ÉCRAN 2 — session active ──────────────────────────────────────
  if (mode === 'feedback-session') {
    return (
      <FeedbackSession
        sessionId={feedbackSession?.sessionId}
        eegState={feedbackSession?.eegState ?? 'neutral'}
        features={feedbackSession?.features ?? {}}
        onEnd={(report) => {
          setFeedbackReport(report)
          setMode('feedback-report')
        }}
        onBack={() => setMode(returnMode === 'neurofeedback' ? 'neurofeedback' : 'feedback-setup')}
      />
    )
  }

  // ── ÉCRAN 3 — rapport de séance ───────────────────────────────────
  if (mode === 'feedback-report') {
    return (
      <FeedbackReport
        report={feedbackReport}
        onClose={() => setMode(returnMode)}
        onNewSession={() => {
          if (returnMode === 'neurofeedback') {
            setMode('neurofeedback')
          } else {
            setMode('feedback-setup')
          }
        }}
      />
    )
  }

  return null
}
