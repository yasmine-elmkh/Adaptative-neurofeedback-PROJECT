import { useEffect, useRef, useCallback, useState } from 'react'
import { createFeedbackWS } from '../utils/api'

const BACKOFF_MIN = 1_000
const BACKOFF_MAX = 30_000

export function useFeedbackSocket(sessionId) {
  const wsRef          = useRef(null)
  const timerRef       = useRef(null)
  const mountedRef     = useRef(true)
  const backoffRef     = useRef(BACKOFF_MIN)

  const [connected,     setConnected]     = useState(false)
  const [currentMedia,  setCurrentMedia]  = useState(null)
  const [sessionReport, setSessionReport] = useState(null)

  const send = useCallback((payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(payload))
    }
  }, [])

  useEffect(() => {
    if (!sessionId) return
    mountedRef.current = true
    backoffRef.current = BACKOFF_MIN

    const connect = () => {
      if (!mountedRef.current) return
      try {
        const ws = createFeedbackWS(sessionId)
        wsRef.current = ws

        ws.onopen = () => {
          if (!mountedRef.current) { ws.close(); return }
          backoffRef.current = BACKOFF_MIN
          setConnected(true)
        }

        ws.onclose = () => {
          setConnected(false)
          if (!mountedRef.current) return
          timerRef.current = setTimeout(() => {
            backoffRef.current = Math.min(backoffRef.current * 2, BACKOFF_MAX)
            connect()
          }, backoffRef.current)
        }

        ws.onerror = () => ws.close()

        ws.onmessage = (evt) => {
          try {
            const msg = JSON.parse(evt.data)
            if (msg.action === 'play' && msg.media) {
              setCurrentMedia(msg.media)
            } else if (msg.action === 'session_ended') {
              setSessionReport({ report: msg.report, metrics: msg.metrics })
            }
          } catch {}
        }
      } catch {}
    }

    connect()

    return () => {
      mountedRef.current = false
      clearTimeout(timerRef.current)
      wsRef.current?.close()
      wsRef.current = null
    }
  }, [sessionId])

  return { connected, currentMedia, sessionReport, send }
}
