import { create } from 'zustand'
import { auth } from '../utils/api'

// ── Auth Store ─────────────────────────────────────────────
export const useAuthStore = create((set, get) => ({
  user: null,
  token: localStorage.getItem('neurocap_token'),
  loading: false,
  login: async (email, password) => {
    const res = await auth.login(email, password)
    localStorage.setItem('neurocap_token', res.access_token)
    localStorage.setItem('neurocap_refresh', res.refresh_token)
    const user = await auth.me()
    set({ user, token: res.access_token })
  },
  register: async (email, password, firstName, lastName, verificationCode) => {
    const res = await auth.register(email, password, firstName, lastName, verificationCode)
    localStorage.setItem('neurocap_token', res.access_token)
    localStorage.setItem('neurocap_refresh', res.refresh_token)
    const user = await auth.me()
    set({ user, token: res.access_token })
  },
  logout: () => {
    localStorage.clear()
    set({ user: null, token: null })
  },
  fetchUser: async () => {
    try {
      const user = await auth.me()
      set({ user })
    } catch {
      // Token invalide ou expiré — nettoyer le localStorage et déconnecter
      localStorage.removeItem('neurocap_token')
      localStorage.removeItem('neurocap_refresh')
      set({ user: null, token: null })
    }
  },
}))

// ── Session WebSocket Store ────────────────────────────────
export const useSessionStore = create((set, get) => ({
  ws: null,
  connected: false,
  sessionId: null,
  frame: null,
  concentration: 0,
  stress: 0,
  signalQuality: 0,
  threshold: 0.5,
  ewma: 0.5,
  blockNumber: 1,
  blockTimeSec: 0,
  successRate: 0,
  features: {},
  feedbackCommand: {},
  history: [],
  maxHistory: 360,
  isPaused: false,
  feedbackMode: 'visual',

  connect: (sessionId, token) => {
    const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'
    const ws = new WebSocket(`${wsUrl}/ws/session/${sessionId}?token=${token || localStorage.getItem('neurocap_token')}`)
    
    ws.onopen = () => set({ connected: true, sessionId })
    ws.onmessage = (event) => {
      const frame = JSON.parse(event.data)
      const history = [...get().history, frame].slice(-get().maxHistory)
      set({
        frame,
        concentration: frame.concentration,
        stress: frame.stress,
        signalQuality: frame.signal_quality,
        threshold: frame.threshold,
        ewma: frame.ewma ?? frame.concentration,
        blockNumber: frame.block_number,
        blockTimeSec: frame.block_time_sec,
        successRate: frame.success_rate ?? 0,
        features: frame.features ?? {},
        feedbackCommand: frame.feedback_command ?? {},
        history,
      })
    }
    ws.onclose = () => set({ connected: false, ws: null })
    ws.onerror = () => set({ connected: false })
    set({ ws, sessionId, history: [], frame: null })
  },

  disconnect: () => {
    const { ws } = get()
    if (ws) ws.close()
    set({ ws: null, connected: false, sessionId: null, history: [], frame: null })
  },

  sendAction: (action) => {
    const { ws } = get()
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action }))
    }
  },

  togglePause: () => {
    const paused = !get().isPaused
    get().sendAction(paused ? 'pause' : 'resume')
    set({ isPaused: paused })
  },

  setFeedbackMode: (mode) => {
    get().sendAction(`set_feedback_mode:${mode}`)
    set({ feedbackMode: mode })
  },
}))