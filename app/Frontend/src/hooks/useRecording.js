import { useState, useRef, useCallback, useEffect } from 'react'
import { eeg as eegApi } from '../utils/api'

/**
 * useRecording — gestion d'un enregistrement CSV EEG avec minuterie.
 *
 * Retourne :
 *   rec     — enregistrement actif
 *   paused  — en pause
 *   recT    — durée en secondes
 *   start() — démarre l'enregistrement (POST /api/eeg/recording/start)
 *   pause() — pause locale (timer seulement)
 *   resume()— reprend le timer
 *   stop()  — arrête (POST /api/eeg/recording/stop)
 *   fmt(s)  — formate MM:SS
 */
export function useRecording() {
  const [rec,    setRec]    = useState(false)
  const [paused, setPaused] = useState(false)
  const [recT,   setRecT]   = useState(0)

  const intervalRef = useRef(null)
  const startRef    = useRef(null)
  const pauseAccRef = useRef(0)
  const pauseAtRef  = useRef(null)

  const tick = useCallback(() => {
    if (!startRef.current) return
    const elapsed = (Date.now() - startRef.current - pauseAccRef.current) / 1000
    setRecT(Math.floor(elapsed))
  }, [])

  const start = useCallback(async () => {
    try {
      await eegApi.startRecording()
      startRef.current    = Date.now()
      pauseAccRef.current = 0
      pauseAtRef.current  = null
      setRec(true)
      setPaused(false)
      setRecT(0)
      intervalRef.current = setInterval(tick, 500)
    } catch (e) {
      console.error('[Rec] start error:', e)
    }
  }, [tick])

  const pause = useCallback(() => {
    if (!rec || paused) return
    setPaused(true)
    pauseAtRef.current = Date.now()
    clearInterval(intervalRef.current)
  }, [rec, paused])

  const resume = useCallback(() => {
    if (!rec || !paused) return
    if (pauseAtRef.current) {
      pauseAccRef.current += Date.now() - pauseAtRef.current
      pauseAtRef.current = null
    }
    setPaused(false)
    intervalRef.current = setInterval(tick, 500)
  }, [rec, paused, tick])

  const stop = useCallback(async () => {
    clearInterval(intervalRef.current)
    try {
      await eegApi.stopRecording()
    } catch (e) {
      console.error('[Rec] stop error:', e)
    }
    setRec(false)
    setPaused(false)
  }, [])

  const fmt = useCallback((s) => {
    const mm = String(Math.floor(s / 60)).padStart(2, '0')
    const ss = String(s % 60).padStart(2, '0')
    return `${mm}:${ss}`
  }, [])

  useEffect(() => () => clearInterval(intervalRef.current), [])

  return { rec, paused, recT, start, pause, resume, stop, fmt }
}
