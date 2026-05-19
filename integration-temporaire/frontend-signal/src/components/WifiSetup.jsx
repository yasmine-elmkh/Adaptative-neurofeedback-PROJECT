/**
 * WifiSetup.jsx — NeuroCap WiFi Configuration
 * Affiche : réseaux mémorisés + formulaire nouveau réseau
 * Les réseaux apparaissent dynamiquement quand l'ESP32 répond
 */

import { useState, useEffect, useRef } from 'react'
import axios from 'axios'

const API_CANDIDATES = [
  `http://${window.location.hostname}:8765/api`,
  'http://localhost:8765/api',
  'http://127.0.0.1:8765/api',
]

// ── Styles ──────────────────────────────────────────────────────────
const S = {
  page: {
    minHeight: '100vh', display: 'flex', alignItems: 'flex-start',
    justifyContent: 'center', background: '#07090f', padding: '24px 16px',
    fontFamily: "'DM Sans',system-ui,sans-serif",
    overflowY: 'auto',
  },
  card: {
    background: '#0e1420', border: '1px solid rgba(255,255,255,.08)',
    borderRadius: 16, padding: '24px 24px', width: '100%', maxWidth: 460,
    color: '#c9d8e8',
  },
  logo: { display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 },
  icon: {
    width: 36, height: 36, borderRadius: 10, flexShrink: 0,
    background: 'linear-gradient(135deg,#00e5b0,#3b82f6)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18,
  },
  title: { fontSize: 16, fontWeight: 700, color: '#f1f5f9', margin: 0 },
  sub:   { fontSize: 10, color: '#4a5a6e', margin: 0 },
  section: {
    background: 'rgba(255,255,255,.015)', border: '1px solid rgba(255,255,255,.05)',
    borderRadius: 10, padding: '12px 14px', marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 10, fontWeight: 700, color: '#4a5a6e', letterSpacing: 1,
    textTransform: 'uppercase', marginBottom: 10,
  },
  label: {
    display: 'block', fontSize: 10, fontWeight: 600, color: '#6a7a8e',
    marginBottom: 4, letterSpacing: .3,
  },
  input: {
    width: '100%', background: '#07090f', border: '1px solid rgba(255,255,255,.1)',
    borderRadius: 7, padding: '9px 12px', color: '#f1f5f9', fontSize: 13,
    outline: 'none', boxSizing: 'border-box', marginBottom: 10,
  },
  btn: {
    width: '100%', padding: '11px', border: 'none', borderRadius: 8,
    fontSize: 13, fontWeight: 700, cursor: 'pointer', letterSpacing: .3,
    background: 'linear-gradient(135deg,#00e5b0,#3b82f6)', color: '#000',
  },
  btnOff: {
    width: '100%', padding: '11px', border: '1px solid rgba(255,255,255,.06)',
    borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: 'not-allowed',
    background: 'rgba(255,255,255,.04)', color: '#3a4a5e',
  },
  btnDanger: {
    width: '100%', padding: '9px', border: '1px solid rgba(255,77,109,.2)',
    borderRadius: 7, fontSize: 11, fontWeight: 600, cursor: 'pointer',
    background: 'rgba(255,77,109,.06)', color: '#fca5a5', marginTop: 8,
  },
  netBtn: {
    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
    width: '100%', background: 'rgba(77,166,255,.04)',
    border: '1px solid rgba(77,166,255,.18)', borderRadius: 7,
    padding: '9px 12px', color: '#f1f5f9', fontSize: 12,
    cursor: 'pointer', marginBottom: 6, textAlign: 'left',
    transition: 'background .15s',
  },
  alertG: {
    background: 'rgba(0,229,176,.05)', border: '1px solid rgba(0,229,176,.2)',
    borderRadius: 7, padding: '8px 12px', marginBottom: 12,
    fontSize: 11, color: '#00e5b0',
  },
  alertB: {
    background: 'rgba(77,166,255,.05)', border: '1px solid rgba(77,166,255,.2)',
    borderRadius: 7, padding: '8px 12px', marginBottom: 12,
    fontSize: 11, color: '#93c5fd', lineHeight: 1.6,
  },
  alertR: {
    background: 'rgba(255,77,109,.07)', border: '1px solid rgba(255,77,109,.2)',
    borderRadius: 7, padding: '8px 12px', marginBottom: 12,
    fontSize: 11, color: '#fca5a5',
  },
  alertY: {
    background: 'rgba(245,166,35,.06)', border: '1px solid rgba(245,166,35,.2)',
    borderRadius: 7, padding: '8px 12px', marginBottom: 12,
    fontSize: 11, color: '#f5a623', lineHeight: 1.6,
  },
  spin: {
    display: 'inline-block', width: 12, height: 12,
    border: '2px solid #4da6ff', borderTopColor: 'transparent',
    borderRadius: '50%', animation: 'spin .7s linear infinite',
    marginRight: 6, verticalAlign: 'middle',
  },
  divider: {
    border: 'none', borderTop: '1px solid rgba(255,255,255,.05)', margin: '14px 0',
  },
  footer: { marginTop: 12, fontSize: 9, color: '#1e2d3d', textAlign: 'center' },
  warn: { fontSize: 9, color: '#f5a623', marginTop: -7, marginBottom: 10 },
  emptyNets: {
    fontSize: 11, color: '#3a4a5e', textAlign: 'center', padding: '8px 0',
  },
  confirmBox: {
    background: 'rgba(77,166,255,.04)', border: '1px solid rgba(77,166,255,.15)',
    borderRadius: 8, padding: '10px 14px', marginBottom: 14,
  },
  row: { display: 'flex', gap: 8, marginBottom: 8 },
  halfBtn: {
    flex: 1, padding: '9px', border: 'none', borderRadius: 7,
    fontSize: 12, fontWeight: 700, cursor: 'pointer', textAlign: 'center',
  },
}

// ── Composant ────────────────────────────────────────────────────────
export default function WifiSetup({ onDone, onBack }) {
  const [phase, _setPhase] = useState('loading')   // loading | ready | confirming | waiting | success | error
  const setPhase = (p) => { phaseRef.current = p; _setPhase(p) }
  const [networks, setNetworks] = useState([])
  const [ssid, setSsid] = useState('')
  const [password, setPassword] = useState('')
  const [errMsg, setErrMsg] = useState('')
  const [serverOk, setServerOk] = useState(null)
  const [foundApi, setFoundApi] = useState(null)
  const [resultIP, setResultIP] = useState('')
  const [pendingSsid, setPendingSsid] = useState('')
  const [espAP, setEspAP] = useState(null)
  const [netsLoading, setNetsLoading] = useState(true)

  const apiRef = useRef(null)
  const pollRef = useRef(null)
  const wsRef = useRef(null)
  const netPollRef = useRef(null)
  const phaseRef = useRef('loading')

  // ── Init ──────────────────────────────────────────────────────────
  useEffect(() => {
    findServer()
    return () => {
      if (pollRef.current) clearInterval(pollRef.current)
      if (netPollRef.current) clearInterval(netPollRef.current)
      if (wsRef.current) wsRef.current.close()
    }
  }, [])

  async function findServer() {
    for (const c of API_CANDIDATES) {
      try {
        const r = await axios.get(`${c}/status`, { timeout: 2500 })
        apiRef.current = c
        setFoundApi(c)
        setServerOk(true)
        if (r.data?.esp32_ap_detected) {
          setEspAP({ ssid: r.data.esp32_ap_ssid, ip: r.data.esp32_ip })
        }
        // Charger les réseaux
        fetchNetworks(c)
        connectWS()
        setPhase('ready')
        return
      } catch {}
    }
    setServerOk(false)
    setPhase('ready')
  }

  // ── Fetch réseaux (avec polling) ─────────────────────────────────
  async function fetchNetworks(base) {
    try {
      const r = await axios.get(`${base}/wifi/networks`, { timeout: 3000 })
      const nets = r.data?.networks || []
      if (nets.length > 0) {
        setNetworks(nets)
        setNetsLoading(false)
      }
      return nets
    } catch {
      return []
    }
  }

  // Polling réseaux toutes les 3s (l'ESP32 peut mettre du temps à répondre)
  useEffect(() => {
    if (!apiRef.current) return
    netPollRef.current = setInterval(async () => {
      if (networks.length === 0) {
        try {
          const r = await axios.get(`${apiRef.current}/wifi/networks`, { timeout: 3000 })
          const nets = r.data?.networks || []
          if (nets.length > 0) {
            setNetworks(nets)
            setNetsLoading(false)
          }
        } catch {}
      } else {
        setNetsLoading(false)
        clearInterval(netPollRef.current)
      }
    }, 3000)
    return () => clearInterval(netPollRef.current)
  }, [networks.length])

  // ── WebSocket ─────────────────────────────────────────────────────
  function connectWS() {
    const wsBase = (foundApi || apiRef.current || '')
      .replace('/api', '').replace('http', 'ws')
    const wsUrl = `${wsBase}/ws`
    try {
      const ws = new WebSocket(wsUrl)
      wsRef.current = ws

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          if (msg.type === 'wifi_result') {
            if (msg.success) {
              setResultIP(msg.ip || '')
              setPhase('success')
              if (pollRef.current) clearInterval(pollRef.current)
            } else {
              setErrMsg(`L'ESP32 n'a pas pu rejoindre '${msg.ssid}'. Vérifiez le mot de passe.`)
              setPhase('error')
              if (pollRef.current) clearInterval(pollRef.current)
            }
          }
          if (msg.type === 'esp32_ap_detected') {
            setEspAP({ ssid: msg.ssid, ip: msg.ip })
          }
        } catch {}
      }

      ws.onclose = () => {
        setTimeout(() => { if (phaseRef.current !== 'success') connectWS() }, 3000)
      }
      ws.onerror = () => {}
    } catch {}
  }

  // ── Actions ───────────────────────────────────────────────────────
  function handleSelectSaved(savedSsid) {
    setPendingSsid(savedSsid)
    setSsid(savedSsid)
    setPassword('')
    setErrMsg('')
    setPhase('confirming')
  }

  async function handleConfirmConnect() {
    setErrMsg('')
    setPhase('waiting')
    try {
      if (networks.includes(pendingSsid) && !password) {
        await axios.post(`${apiRef.current}/wifi/use_saved`,
          { ssid: pendingSsid }, { timeout: 10000 })
      } else {
        await axios.post(`${apiRef.current}/wifi/configure`,
          { ssid: pendingSsid, password }, { timeout: 10000 })
      }
      startTimeoutPolling()
    } catch (e) {
      setPhase('error')
      setErrMsg(e.response?.data?.detail || e.message || 'Erreur réseau')
    }
  }

  function handleSubmitNew(e) {
    e.preventDefault()
    if (!ssid.trim()) return
    setPendingSsid(ssid.trim())
    setErrMsg('')
    setPhase('confirming')
  }

  function startTimeoutPolling() {
    if (pollRef.current) clearInterval(pollRef.current)
    let attempts = 0
    pollRef.current = setInterval(async () => {
      attempts++
      if (attempts > 90) {
        clearInterval(pollRef.current)
        setPhase('error')
        setErrMsg('Timeout 90s. Vérifiez que ESP32 et PC sont sur le même réseau.')
        return
      }
      try {
        const r = await axios.get(`${apiRef.current}/status`, { timeout: 3000 })
        if (r.data?.wifi_result?.success) {
          clearInterval(pollRef.current)
          setResultIP(r.data.wifi_result.ip || '')
          setPhase('success')
        } else if (r.data?.wifi_result?.success === false) {
          clearInterval(pollRef.current)
          setErrMsg(`Connexion échouée: ${r.data.wifi_result.ssid}`)
          setPhase('error')
        }
      } catch {}
    }, 1000)
  }

  async function handleReset() {
    if (!confirm("Effacer tous les réseaux mémorisés sur l'ESP32 ?")) return
    try {
      await axios.post(`${apiRef.current}/wifi/reset`, {}, { timeout: 5000 })
      setNetworks([])
    } catch (e) {
      alert('Erreur reset: ' + e.message)
    }
  }

  function handleBack() {
    setPhase('ready')
    setPendingSsid('')
    setPassword('')
    setErrMsg('')
  }

  const isBusy = phase === 'waiting'

  // ── Rendu : succès ────────────────────────────────────────────────
  if (phase === 'success') return (
    <div style={S.page}>
      <div style={S.card}>
        <div style={{ textAlign: 'center', padding: '28px 0' }}>
          <div style={{ fontSize: 48, marginBottom: 14 }}>✅</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#00e5b0', marginBottom: 6 }}>
            WiFi configuré !
          </div>
          <div style={{ fontSize: 11, color: '#4a5a6e', marginBottom: 16 }}>
            ESP32 connecté • IP: <strong style={{ color: '#93c5fd' }}>{resultIP}</strong>
          </div>
          <div style={{ fontSize: 11, color: '#6a7a8e', marginBottom: 20, lineHeight: 1.6 }}>
            Reconnectez votre PC à votre box WiFi si nécessaire,<br/>
            puis accédez au dashboard.
          </div>
          <button style={S.btn} onClick={() => onDone?.()}>
            🧠 Accéder au Dashboard →
          </button>
        </div>
      </div>
    </div>
  )

  // ── Rendu : confirmation ──────────────────────────────────────────
  if (phase === 'confirming') return (
    <div style={S.page}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <div style={S.card}>
        <div style={S.logo}>
          <div style={S.icon}>🧠</div>
          <div><p style={S.title}>NeuroCap EEG</p><p style={S.sub}>Confirmer la connexion</p></div>
        </div>

        <div style={S.confirmBox}>
          <div style={{ fontSize: 11, color: '#93c5fd', marginBottom: 6 }}>
            <strong>Confirmer la connexion</strong>
          </div>
          <div style={{ fontSize: 13, color: '#f1f5f9' }}>
            Réseau : <strong>{pendingSsid}</strong>
          </div>
          {password && (
            <div style={{ fontSize: 11, color: '#6a7a8e', marginTop: 3 }}>
              Mot de passe : {'•'.repeat(password.length)}
            </div>
          )}
        </div>

        {networks.includes(pendingSsid) && !password && (
          <>
            <div style={{ fontSize: 10, color: '#4a5a6e', marginBottom: 6 }}>
              Nouveau mot de passe (optionnel) :
            </div>
            <input style={S.input} type="password" placeholder="laisser vide = mémorisé"
              value={password} onChange={e => setPassword(e.target.value)}/>
          </>
        )}

        <button style={S.btn} onClick={handleConfirmConnect}>
          ✓ Confirmer la connexion
        </button>
        <button style={S.btnDanger} onClick={handleBack}>← Annuler</button>
      </div>
    </div>
  )

  // ── Rendu : en attente ────────────────────────────────────────────
  if (phase === 'waiting') return (
    <div style={S.page}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <div style={S.card}>
        <div style={S.logo}>
          <div style={S.icon}>🧠</div>
          <div><p style={S.title}>NeuroCap EEG</p><p style={S.sub}>Connexion en cours</p></div>
        </div>
        <div style={{ ...S.alertB, textAlign: 'center', padding: '20px 14px' }}>
          <span style={S.spin}/>
          L'ESP32 tente de rejoindre <strong>{pendingSsid}</strong>…<br/>
          <span style={{ color: '#5a7090', fontSize: 10 }}>En attente de confirmation de l'ESP32</span>
        </div>
        <button style={S.btnDanger} onClick={() => { handleBack(); setPhase('ready'); }}>
          ← Annuler
        </button>
      </div>
    </div>
  )

  // ── Rendu : principal (ready / error / loading) ───────────────────
  return (
    <div style={S.page}>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
      <div style={S.card}>

        {/* Logo */}
        <div style={S.logo}>
          <div style={S.icon}>🧠</div>
          <div><p style={S.title}>NeuroCap EEG</p><p style={S.sub}>Configuration WiFi</p></div>
          {onBack && (
            <button onClick={onBack} style={{
              marginLeft: 'auto', background: 'rgba(255,255,255,.04)',
              border: '1px solid rgba(255,255,255,.08)', borderRadius: 6,
              color: '#4a5a6e', fontSize: 10, padding: '4px 10px', cursor: 'pointer',
            }}>← Accueil</button>
          )}
        </div>

        {/* ESP32 AP */}
        {espAP && (
          <div style={S.alertG}>
            📡 ESP32 détecté : <strong>{espAP.ssid}</strong>
          </div>
        )}

        {/* Serveur */}
        {serverOk === null && (
          <div style={S.alertB}><span style={S.spin}/>Recherche du serveur Python…</div>
        )}
        {serverOk === false && (
          <div style={S.alertY}>
            ⚠️ <strong>Serveur Python non joignable</strong><br/>
            Lancez <code style={{background:'rgba(0,0,0,.3)',padding:'1px 5px',borderRadius:3}}>
              python assembly.py</code> puis rafraîchissez
          </div>
        )}
        {serverOk === true && (
          <div style={S.alertG}>
            ✅ Serveur — <code style={{background:'rgba(0,0,0,.2)',padding:'1px 4px',borderRadius:3}}>
              {foundApi}</code>
          </div>
        )}

        {/* Erreur */}
        {errMsg && <div style={S.alertR}>❌ {errMsg}</div>}

        {/* ════════════════════════════════════════════════════════════
            SECTION 1 : Réseaux mémorisés (toujours visible)
            ════════════════════════════════════════════════════════════ */}
        <div style={S.section}>
          <div style={S.sectionTitle}>📶 Réseaux mémorisés</div>

          {netsLoading && networks.length === 0 ? (
            <div style={S.emptyNets}>
              <span style={S.spin}/> Recherche des réseaux mémorisés…
            </div>
          ) : networks.length === 0 ? (
            <div style={S.emptyNets}>Aucun réseau mémorisé sur l'ESP32</div>
          ) : (
            networks.map(net => (
              <button key={net} style={S.netBtn} onClick={() => handleSelectSaved(net)}>
                <span>📶 {net}</span>
                <span style={{ color: '#4da6ff', fontSize: 10 }}>Se connecter →</span>
              </button>
            ))
          )}
        </div>

        {/* ════════════════════════════════════════════════════════════
            SECTION 2 : Nouveau réseau
            ════════════════════════════════════════════════════════════ */}
        <div style={S.section}>
          <div style={S.sectionTitle}>➕ Nouveau réseau WiFi</div>

          <form onSubmit={handleSubmitNew}>
            <label style={S.label}>SSID (nom du réseau)</label>
            <input style={S.input} type="text" placeholder="MonWiFi_2.4G"
              value={ssid} onChange={e => setSsid(e.target.value)}
              disabled={isBusy} autoComplete="off"/>
            <div style={S.warn}>⚠ 2.4 GHz uniquement</div>

            <label style={S.label}>Mot de passe</label>
            <input style={S.input} type="password" placeholder="••••••••"
              value={password} onChange={e => setPassword(e.target.value)}
              disabled={isBusy} autoComplete="off"/>

            <button type="submit"
              style={ssid.trim() && serverOk ? S.btn : S.btnOff}
              disabled={!ssid.trim() || !serverOk}>
              📡 Configurer
            </button>
          </form>
        </div>

        {/* ════════════════════════════════════════════════════════════
            SECTION 3 : Actions + Procédure
            ════════════════════════════════════════════════════════════ */}
        <button style={S.btnDanger} onClick={handleReset}>
          🔄 Effacer réseaux mémorisés
        </button>

        <hr style={S.divider}/>

        <div style={{ fontSize: 10, color: '#3a4a5e', lineHeight: 1.8 }}>
          <strong style={{ color: '#4a5a6e' }}>Procédure :</strong><br/>
          ① PC connecté à <strong style={{color:'#f1f5f9'}}>NeuroCap-XXXX</strong><br/>
          ② Serveur Python lancé<br/>
          ③ Choisir ou entrer un réseau 2.4 GHz<br/>
          ④ Confirmer → ESP32 répond OK/FAIL<br/>
          ⑤ Reconnecter PC à la box → Dashboard
        </div>

        <p style={S.footer}>L'AP NeuroCap reste actif pendant la configuration</p>
      </div>
    </div>
  )
}