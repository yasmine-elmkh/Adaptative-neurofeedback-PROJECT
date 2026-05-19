/**
 * AppRouter.jsx — Routage principal NeuroCap EEG
 *
 * Flux :
 *   WelcomePage
 *     ├── [Casque NeuroCap] → WifiSetup → Dashboard live (App.jsx)
 *     └── [Fichier EEG]     → FileDashboard (upload + résultats ML)
 */

import { useState } from 'react'
import WelcomePage   from './WelcomePage'
import WifiSetup     from './WifiSetup'
import FileDashboard from './FileDashboard'
import Dashboard     from '../App'

export default function AppRouter() {
  // 'welcome' | 'hardware-wifi' | 'hardware-live' | 'file'
  const [mode, setMode] = useState('welcome')

  // ── Welcome ──────────────────────────────────────────────────────
  if (mode === 'welcome') {
    return (
      <WelcomePage
        onHardware={() => setMode('hardware-wifi')}
        onFile={() => setMode('file')}
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
    return <FileDashboard onBack={() => setMode('welcome')} />
  }

  return null
}
