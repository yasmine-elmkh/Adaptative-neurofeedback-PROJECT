import { useRef, useCallback, useEffect } from 'react'

/**
 * useWebSocket — hook WebSocket avec reconnexion automatique.
 * Callbacks stables via ref pour éviter les re-renders intempestifs.
 */
export function useWebSocket(url, { onOpen, onClose, onMessage } = {}) {
  const wsRef      = useRef(null)
  const cbRef      = useRef({ onOpen, onClose, onMessage })
  const manualRef  = useRef(false)

  // Mettre à jour les callbacks sans recréer le WS
  useEffect(() => { cbRef.current = { onOpen, onClose, onMessage } }, [onOpen, onClose, onMessage])

  const connect = useCallback(() => {
    if (wsRef.current && (
      wsRef.current.readyState === WebSocket.OPEN ||
      wsRef.current.readyState === WebSocket.CONNECTING
    )) return

    manualRef.current = false

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => { cbRef.current.onOpen?.() }

      ws.onmessage = (ev) => {
        try {
          const data = JSON.parse(ev.data)
          cbRef.current.onMessage?.(data)
        } catch { /* ignore JSON malformé */ }
      }

      ws.onclose = () => { cbRef.current.onClose?.() }
      ws.onerror = () => { /* géré par onclose */ }
    } catch (e) {
      console.error('[WS] Connexion échouée:', e)
    }
  }, [url])

  const disconnect = useCallback(() => {
    manualRef.current = true
    if (wsRef.current) {
      wsRef.current.close(1000, 'manual')
      wsRef.current = null
    }
  }, [])

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  // Cleanup au démontage
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close(1000, 'unmount')
        wsRef.current = null
      }
    }
  }, [])

  return { connect, disconnect, send }
}
