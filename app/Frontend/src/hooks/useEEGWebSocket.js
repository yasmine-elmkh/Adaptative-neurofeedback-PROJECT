import { useRef, useCallback, useEffect, useState } from 'react'

const WS_URL = '/ws/eeg'

/**
 * useEEGWebSocket — connexion au WebSocket EEG temps réel.
 *
 * Retourne :
 *   connected    — état de la connexion
 *   eegFrame     — dernier sample EEG reçu (type:"eeg")
 *   epochFrame   — dernière époque acceptée (type:"epoch")
 *   initFrame    — message d'init (esp32_connected, wifi_configured…)
 *   esp32Status  — dernier message esp32_status
 *   send(cmd)    — envoyer une commande (FINALISE_BASELINE, START_REC…)
 *   reconnect()  — forcer la reconnexion
 */
export function useEEGWebSocket() {
  const wsRef      = useRef(null)
  const timerRef   = useRef(null)
  const mountedRef = useRef(true)

  const [connected,      setConnected]      = useState(false)
  const [eegFrame,       setEegFrame]       = useState(null)
  const [epochFrame,     setEpochFrame]     = useState(null)
  const [rejectedFrame,  setRejectedFrame]  = useState(null)
  const [initFrame,      setInitFrame]      = useState(null)
  const [esp32Status,    setEsp32Status]    = useState(null)

  const connect = useCallback(() => {
    if (!mountedRef.current) return
    if (wsRef.current && wsRef.current.readyState <= WebSocket.OPEN) return

    const token = localStorage.getItem('neurocap_token')
    const url   = token ? `${WS_URL}?token=${token}` : WS_URL

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        if (!mountedRef.current) { ws.close(); return }
        setConnected(true)
      }

      ws.onmessage = (ev) => {
        try {
          const msg = JSON.parse(ev.data)
          switch (msg.type) {
            case 'eeg':             setEegFrame(msg);      break
            case 'epoch':           setEpochFrame(msg);    break
            case 'epoch_rejected':  setRejectedFrame(msg); break
            case 'init':            setInitFrame(msg);     break
            case 'esp32_status':    setEsp32Status(msg);   break
            case 'electrode':       setEsp32Status(prev => ({ ...prev, ...msg })); break
            default: break
          }
        } catch { /* JSON malformé */ }
      }

      ws.onclose = () => {
        setConnected(false)
        // Reconnexion automatique toutes les 3s
        if (mountedRef.current) {
          timerRef.current = setTimeout(connect, 3000)
        }
      }

      ws.onerror = () => { /* géré par onclose */ }
    } catch (e) {
      console.error('[WS/EEG] Connexion échouée:', e)
      if (mountedRef.current) {
        timerRef.current = setTimeout(connect, 3000)
      }
    }
  }, [])

  const send = useCallback((command, extra = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command, ...extra }))
    }
  }, [])

  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    connect()
  }, [connect])

  // Connexion initiale
  useEffect(() => {
    mountedRef.current = true
    connect()
    return () => {
      mountedRef.current = false
      clearTimeout(timerRef.current)
      if (wsRef.current) {
        wsRef.current.close(1000, 'unmount')
        wsRef.current = null
      }
    }
  }, [connect])

  return { connected, eegFrame, epochFrame, rejectedFrame, initFrame, esp32Status, send, reconnect }
}
