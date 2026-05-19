import { useState, useEffect } from 'react'
import WifiSetup from './WifiSetup'
import Dashboard from '../App'

const API_BASE = `http://${window.location.hostname}:8000/api`

export default function AppRouter() {
  const [wifiConfigured, setWifiConfigured] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkStatus()
    const interval = setInterval(checkStatus, 3000)
    return () => clearInterval(interval)
  }, [])

  async function checkStatus() {
    try {
      const r = await fetch(`${API_BASE}/status`, {
        signal: AbortSignal.timeout(3000)
      })
      const data = await r.json()
      if (data.wifi_configured || data.esp32_connected) {
        setWifiConfigured(true)
      }
    } catch {
      // serveur pas joignable
    } finally {
      setLoading(false)
    }
  }

  // Écran chargement
  if (loading) return (
    <div style={{
      minHeight: '100vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', background: '#07090f',
      fontFamily: "'DM Sans',system-ui,sans-serif",
    }}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <div style={{
        width: 32, height: 32, border: '3px solid rgba(77,166,255,.2)',
        borderTopColor: '#4da6ff', borderRadius: '50%',
        animation: 'spin .8s linear infinite', marginBottom: 12,
      }} />
      <div style={{ color: '#4a5a6e', fontSize: 12 }}>Chargement NeuroCap…</div>
    </div>
  )

  // WiFi pas encore configuré → page Setup
  if (!wifiConfigured) {
    return <WifiSetup onDone={() => setWifiConfigured(true)} />
  }

  // WiFi OK → Dashboard (App.jsx)
  return <Dashboard />
}