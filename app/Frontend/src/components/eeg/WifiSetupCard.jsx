import { useState, useEffect, useRef } from 'react'
import { Wifi, CheckCircle2, ChevronRight } from 'lucide-react'
import { eeg as eegApi } from '../../utils/api'

/**
 * Panneau de configuration WiFi ESP32.
 * Utilisé dans EEGLive et CalibrationSession.
 */
export default function WifiSetupCard({ status, onClose }) {
  const [networks, setNetworks] = useState([])
  const [ssid,     setSsid]     = useState('')
  const [password, setPassword] = useState('')
  const [phase,    setPhase]    = useState('idle') // idle | confirming | waiting | done | error
  const [errMsg,   setErrMsg]   = useState('')
  const [pending,  setPending]  = useState('')
  const pollRef = useRef(null)

  useEffect(() => {
    eegApi.wifiNetworks().then(d => setNetworks(d.networks || [])).catch(() => {})
  }, [])

  function startPolling() {
    clearInterval(pollRef.current)
    let tries = 0
    pollRef.current = setInterval(async () => {
      tries++
      if (tries > 90) {
        clearInterval(pollRef.current)
        setPhase('error')
        setErrMsg('Timeout 90s — vérifiez SSID et mot de passe')
        return
      }
      try {
        const s = await eegApi.status()
        if (s.wifi_result?.success)
          { clearInterval(pollRef.current); setPhase('done') }
        else if (s.wifi_result?.success === false)
          { clearInterval(pollRef.current); setPhase('error'); setErrMsg(`Échec : ${s.wifi_result.reason ?? 'réseau introuvable'}`) }
      } catch {}
    }, 1000)
  }

  async function doConnect() {
    setPhase('waiting'); setErrMsg('')
    try {
      if (networks.includes(pending) && !password) await eegApi.wifiUseSaved(pending)
      else await eegApi.wifiConfigure(pending || ssid, password)
      startPolling()
    } catch (e) { setPhase('error'); setErrMsg(e?.response?.data?.error || e.message) }
  }

  function submitNew(e) {
    e.preventDefault()
    if (!ssid.trim()) return
    setPending(ssid.trim())
    setPhase('confirming')
  }

  useEffect(() => () => clearInterval(pollRef.current), [])

  if (phase === 'done') return (
    <div className="card p-8 text-center space-y-4">
      <CheckCircle2 className="w-12 h-12 text-emerald-400 mx-auto" />
      <p className="font-semibold text-nc-text">WiFi configuré !</p>
      <p className="text-xs text-nc-muted">
        ESP32 connecté. Reconnectez votre PC à votre réseau WiFi domestique si nécessaire.
      </p>
      <button onClick={onClose} className="btn-primary px-6 py-2.5 rounded-xl text-sm font-semibold">
        Continuer →
      </button>
    </div>
  )

  if (phase === 'confirming') return (
    <div className="card p-6 space-y-4">
      <p className="text-sm font-semibold text-nc-text">Confirmer la connexion</p>
      <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/20 text-sm text-nc-text">
        Réseau : <strong>{pending}</strong>
      </div>
      <div className="space-y-1">
        <label className="text-xs text-nc-muted">
          Mot de passe {networks.includes(pending) ? '(optionnel si mémorisé)' : ''}
        </label>
        <input type="password" className="input w-full" value={password}
          onChange={e => setPassword(e.target.value)} placeholder="••••••••" />
      </div>
      <div className="flex gap-3">
        <button onClick={doConnect} className="btn-primary flex-1 py-2.5 rounded-xl text-sm font-semibold">
          Confirmer
        </button>
        <button onClick={() => setPhase('idle')} className="btn-ghost flex-1 py-2.5 rounded-xl text-sm">
          Annuler
        </button>
      </div>
    </div>
  )

  if (phase === 'waiting') return (
    <div className="card p-8 text-center space-y-4">
      <div className="w-10 h-10 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin mx-auto" />
      <p className="text-sm text-nc-text">
        Connexion de l'ESP32 à <strong>{pending}</strong>…
      </p>
      <p className="text-xs text-nc-muted">Attente de confirmation (jusqu'à 90 s)</p>
    </div>
  )

  return (
    <div className="card p-6 space-y-5">
      <div className="flex items-center gap-2">
        <Wifi className="w-5 h-5 text-nc-accent" />
        <h3 className="font-semibold text-nc-text text-sm">Configuration WiFi ESP32</h3>
      </div>

      <div className="p-3 rounded-xl bg-blue-500/8 border border-blue-500/20 text-xs text-blue-300 leading-relaxed">
        <strong>Procédure :</strong> Connectez d'abord votre PC au hotspot{' '}
        <code className="bg-black/30 px-1 rounded">NeuroCap-XXXX</code> affiché sur l'ESP32,
        puis entrez les identifiants de votre réseau WiFi domestique (2,4 GHz uniquement).
      </div>

      {errMsg && (
        <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-xs text-red-300">
          {errMsg}
        </div>
      )}

      {status?.esp32_ap_detected && (
        <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300">
          📡 ESP32 détecté : <strong>{status.esp32_ap_ssid}</strong>
        </div>
      )}

      {networks.length > 0 && (
        <div>
          <p className="text-[10px] font-semibold text-nc-muted uppercase tracking-wide mb-2">
            Réseaux mémorisés
          </p>
          <div className="space-y-1">
            {networks.map(net => (
              <button key={net}
                onClick={() => { setPending(net); setPhase('confirming') }}
                className="w-full flex items-center justify-between px-3 py-2 rounded-xl
                           bg-blue-500/5 border border-blue-500/15 hover:bg-blue-500/10
                           text-sm text-nc-text transition-colors">
                <span className="flex items-center gap-2">
                  <Wifi className="w-3.5 h-3.5 text-nc-accent" />{net}
                </span>
                <ChevronRight className="w-3.5 h-3.5 text-nc-muted" />
              </button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={submitNew} className="space-y-3">
        <p className="text-[10px] font-semibold text-nc-muted uppercase tracking-wide">Nouveau réseau</p>
        <div className="space-y-1">
          <label className="text-xs text-nc-muted">SSID (2,4 GHz uniquement)</label>
          <input type="text" className="input w-full" value={ssid}
            onChange={e => setSsid(e.target.value)}
            placeholder="MonWiFi_2.4G" autoComplete="off" />
        </div>
        <div className="space-y-1">
          <label className="text-xs text-nc-muted">Mot de passe</label>
          <input type="password" className="input w-full" value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="••••••••" autoComplete="off" />
        </div>
        <button type="submit" disabled={!ssid.trim()}
          className="btn-primary w-full py-2.5 rounded-xl text-sm font-semibold disabled:opacity-40">
          📡 Configurer l'ESP32
        </button>
      </form>

      <button onClick={() => eegApi.wifiReset().catch(() => {})}
        className="text-xs text-nc-danger hover:underline w-full text-center">
        Effacer les réseaux mémorisés (reset)
      </button>
    </div>
  )
}
