import { useState, useRef, useCallback, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8765/api'

export function useRecording() {
  const [rec,   setRec]   = useState(false)
  const [paused,setPaused] = useState(false)
  const [recT,  setRecT]  = useState(0)
  const timerRef = useRef(null)
  const t0Ref    = useRef(0)
  const pauseAcc = useRef(0)
  const pauseT   = useRef(0)

  const tick = useCallback(() => {
    setRecT(pauseAcc.current + (Date.now() - t0Ref.current))
  }, [])

  const start = useCallback(async () => {
    try { await axios.post(`${API}/recording/start`) } catch { /* ignore */ }
    pauseAcc.current = 0
    t0Ref.current = Date.now()
    setRec(true); setRecT(0); setPaused(false)
    timerRef.current = setInterval(tick, 500)
  }, [tick])

  const pause = useCallback(() => {
    clearInterval(timerRef.current)
    pauseAcc.current += Date.now() - t0Ref.current
    setPaused(true)
  }, [])

  const resume = useCallback(() => {
    t0Ref.current = Date.now()
    setPaused(false)
    timerRef.current = setInterval(tick, 500)
  }, [tick])

  const stop = useCallback(async () => {
    clearInterval(timerRef.current)
    try { await axios.post(`${API}/recording/stop`) } catch { /* ignore */ }
    setRec(false); setPaused(false); setRecT(0)
    pauseAcc.current = 0
  }, [])

  useEffect(() => () => clearInterval(timerRef.current), [])

  const fmt = useCallback((ms) => {
    const s = Math.floor(ms / 1000)
    const m = Math.floor(s / 60)
    return `${String(m).padStart(2,'0')}:${String(s % 60).padStart(2,'0')}`
  }, [])

  return { rec, paused, recT, start, pause, resume, stop, fmt }
}
