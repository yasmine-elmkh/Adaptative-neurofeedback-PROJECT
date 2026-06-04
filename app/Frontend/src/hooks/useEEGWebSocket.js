import { useRef, useCallback, useEffect, useState } from 'react'

const WS_URL = '/ws/eeg'
const BACKOFF_MIN = 1_000
const BACKOFF_MAX = 30_000

export function useEEGWebSocket() {
  const wsRef      = useRef(null)
  const timerRef   = useRef(null)
  const mountedRef = useRef(true)
  const backoffRef = useRef(BACKOFF_MIN)

  const [connected,      setConnected]      = useState(false)
  const [eegFrame,       setEegFrame]       = useState(null)
  const [epochFrame,     setEpochFrame]     = useState(null)
  const [rejectedFrame,  setRejectedFrame]  = useState(null)
  const [initFrame,      setInitFrame]      = useState(null)
  const [esp32Status,    setEsp32Status]    = useState(null)

  const scheduleReconnect = useCallback(() => {
    if (!mountedRef.current) return
    timerRef.current = setTimeout(() => {
      backoffRef.current = Math.min(backoffRef.current * 2, BACKOFF_MAX)
      connect()
    }, backoffRef.current)
  }, [])

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
        backoffRef.current = BACKOFF_MIN
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
        scheduleReconnect()
      }

      ws.onerror = () => { /* géré par onclose */ }
    } catch {
      scheduleReconnect()
    }
  }, [scheduleReconnect])

  const send = useCallback((command, extra = {}) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ command, ...extra }))
    }
  }, [])

  const reconnect = useCallback(() => {
    clearTimeout(timerRef.current)
    backoffRef.current = BACKOFF_MIN
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    connect()
  }, [connect])

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
