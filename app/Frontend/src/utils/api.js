import axios from 'axios'

const API = axios.create({ baseURL: '/api' })

API.interceptors.request.use((config) => {
  const token = localStorage.getItem('neurocap_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

let _refreshing = false
let _refreshQueue = []

API.interceptors.response.use(
  res => res,
  async err => {
    const original = err.config
    if (err.response?.status !== 401 || original._retry) {
      return Promise.reject(err)
    }

    const refreshToken = localStorage.getItem('neurocap_refresh')
    if (!refreshToken) {
      localStorage.removeItem('neurocap_token')
      localStorage.removeItem('neurocap_refresh')
      window.location.href = '/login'
      return Promise.reject(err)
    }

    if (_refreshing) {
      return new Promise((resolve, reject) => {
        _refreshQueue.push({ resolve, reject })
      }).then(token => {
        original.headers.Authorization = `Bearer ${token}`
        return API(original)
      })
    }

    original._retry = true
    _refreshing = true

    try {
      const { data } = await axios.post('/api/auth/refresh', { refresh_token: refreshToken })
      localStorage.setItem('neurocap_token', data.access_token)
      localStorage.setItem('neurocap_refresh', data.refresh_token)
      API.defaults.headers.common.Authorization = `Bearer ${data.access_token}`
      _refreshQueue.forEach(q => q.resolve(data.access_token))
      _refreshQueue = []
      original.headers.Authorization = `Bearer ${data.access_token}`
      return API(original)
    } catch {
      _refreshQueue.forEach(q => q.reject())
      _refreshQueue = []
      localStorage.removeItem('neurocap_token')
      localStorage.removeItem('neurocap_refresh')
      window.location.href = '/login'
      return Promise.reject(err)
    } finally {
      _refreshing = false
    }
  }
)

export const auth = {
  sendCode: (email) =>
    API.post('/auth/send-code', { email }).then(res => res.data),
  register: (email, password, firstName, lastName, verificationCode) =>
    API.post('/auth/register', {
      email, password,
      first_name: firstName,
      last_name: lastName,
      verification_code: verificationCode,
    }).then(res => res.data),
  login: (email, password) => API.post('/auth/login', { email, password }).then(res => res.data),
  me: () => API.get('/auth/me').then(res => res.data),
  changePassword: (newPassword) =>
    API.post('/auth/change-password', { new_password: newPassword }),
}

export const profile = {
  get: () => API.get('/profile/me').then(res => res.data),
  calibrate: (data) => API.post('/profile/calibration', data).then(res => res.data),
}

export const sessions = {
  list: () => API.get('/sessions').then(res => res.data),
  create: (mode) => API.post('/sessions', { feedback_mode: mode }).then(res => res.data),
  getReport: (id) => API.get(`/sessions/${id}/report`).then(res => res.data),
  exportCSV: (id) => API.get(`/sessions/${id}/export`, { responseType: 'blob' }),
  exportAll: () => API.get('/sessions/export/all', { responseType: 'blob' }),
}

export const assistant = {
  ask: (question, sessionId, eegContext) =>
    API.post('/assistant/ask', {
      question,
      session_id: sessionId || undefined,
      eeg_context: eegContext || undefined,
    }).then(res => res.data),
  feedback: (messageIndex, feedback, question, answer) =>
    API.post('/assistant/feedback', { message_index: messageIndex, feedback, question, answer }),
}

export const admin = {
  stats: () => API.get('/admin/stats').then(r => r.data),

  // Users (enriched with session stats)
  users: (limit = 50, offset = 0, roleFilter = null) =>
    API.get('/admin/users', {
      params: {
        limit,
        ...(offset > 0 && { offset }),
        ...(roleFilter && { role_filter: roleFilter }),
      },
    }).then(r => r.data),
  getUser: (id) => API.get(`/admin/users/${id}`).then(r => r.data),
  createUser: (data) => API.post('/admin/users', data).then(r => r.data),
  updateUser: (id, data) => API.put(`/admin/users/${id}`, data).then(r => r.data),
  deleteUser: (id, hard = false) => API.delete(`/admin/users/${id}`, { params: { hard } }),

  // Therapists list (for assignment dropdown)
  therapists: () => API.get('/admin/therapists').then(r => r.data),

  // Assignment
  assignPatient: (patientId, therapistId) =>
    API.post('/admin/assign-patient', { patient_id: patientId, therapist_id: therapistId || null }),

  // Settings
  getSettings: () => API.get('/admin/settings').then(r => r.data),
  updateSetting: (key, value) => API.put(`/admin/settings/${key}`, { value }).then(r => r.data),

  // Audit logs
  auditLogs: (limit = 100, action = null, userId = null, dateFrom = null, dateTo = null) =>
    API.get('/admin/audit-logs', {
      params: {
        limit,
        action: action || undefined,
        user_id: userId || undefined,
        date_from: dateFrom || undefined,
        date_to: dateTo || undefined,
      },
    }).then(r => r.data),

  // Email reminders
  sendReminder: (userId, message = '') =>
    API.post('/admin/send-reminder', { user_id: userId, message }).then(r => r.data),
  sendReminderAll: (message = '', daysInactive = 30) =>
    API.post('/admin/send-reminder-all', { message, days_inactive: daysInactive }).then(r => r.data),
}

export const therapist = {
  patients: () => API.get('/therapist/patients').then(r => r.data),
  patientInfo: (patientId) => API.get(`/therapist/patients/${patientId}`).then(r => r.data),
  patientSessions: (patientId, limit = 50) => API.get(`/therapist/patients/${patientId}/sessions`, { params: { limit } }).then(r => r.data),
  patientProfile: (patientId) => API.get(`/therapist/patients/${patientId}/profile`).then(r => r.data),
  getNotes: (patientId) => API.get(`/therapist/patients/${patientId}/notes`).then(r => r.data),
  addNote: (patientId, content) => API.post(`/therapist/patients/${patientId}/notes`, { content }).then(r => r.data),
  getRecommendation: (patientId) => API.get(`/therapist/patients/${patientId}/recommendation`).then(r => r.data),
  setRecommendation: (patientId, data) => API.post(`/therapist/patients/${patientId}/recommendation`, data).then(r => r.data),
  adjustPalier: (patientId, palier) => API.put(`/therapist/patients/${patientId}/palier`, { palier }),
  toggleActive: (patientId) => API.patch(`/therapist/patients/${patientId}/active`),
  exportPatient: (patientId) => API.get(`/therapist/patients/${patientId}/export`, { responseType: 'blob' }),
  getEEGReports: (patientId, limit = 50) => API.get(`/therapist/patients/${patientId}/eeg-reports`, { params: { limit } }).then(r => r.data),
}

export const createSessionWS = (sessionId) => {
  const token = localStorage.getItem('neurocap_token')
  return new WebSocket(`/ws/session/${sessionId}?token=${token}`)
}

export const createFeedbackWS = (sessionId) => {
  const token = localStorage.getItem('neurocap_token')
  const proto = window.location.protocol === 'https:' ? 'wss' : 'ws'
  return new WebSocket(`${proto}://${window.location.host}/api/feedback/ws/${sessionId}?token=${token}`)
}

// ── Media & Feedback (/api/media/*, /api/feedback/*) ─────────────────────────
export const media = {
  list: (mediaType, eegState) =>
    API.get('/media/list', {
      params: {
        ...(mediaType && { media_type: mediaType }),
        ...(eegState  && { eeg_state: eegState }),
      },
    }).then(r => r.data),
}

export const feedback = {
  status:        () =>
    API.get('/feedback/status').then(r => r.data),
  startSession:  (objective, eegSnapshot) =>
    API.post('/feedback/sessions', { objective, eeg_snapshot: eegSnapshot }).then(r => r.data),
  recommend:     (sessionId, eegState, mediaType, features, confidence) =>
    API.post('/feedback/recommend', {
      session_id:  sessionId,
      eeg_state:   eegState,
      media_type:  mediaType   || undefined,
      features:    features    || undefined,
      confidence:  confidence  != null ? confidence : undefined,
    }).then(r => r.data),
  submit:        (payload) =>
    API.post('/feedback/submit', payload).then(r => r.data),
  skip:          (sessionId, mediaId) =>
    API.post('/feedback/skip', { session_id: sessionId, media_id: mediaId }).then(r => r.data),
  sam:           (sessionId, score) =>
    API.post('/feedback/sam', { session_id: sessionId, score }).then(r => r.data),
  end:           (payload) =>
    API.post('/feedback/end', payload).then(r => r.data),
  guide:         (sessionId, mediaId, eegState, features) =>
    API.post('/feedback/media-guide', {
      session_id: sessionId,
      media_id:   mediaId,
      eeg_state:  eegState,
      features:   features || undefined,
    }).then(r => r.data),
}

// ── Calendrier sessions (/api/sessions/calendar) ─────────────────────────────
export const calendar = {
  get: (patientId) =>
    API.get('/sessions/calendar', { params: patientId ? { patient_id: patientId } : {} }).then(r => r.data),
}

// ── EEG Temps Réel (/api/eeg/*) ──────────────────────────────────────────────
// ── Protocole (/api/protocol/*) ──────────────────────────────────────────────
export const protocol = {
  status:           ()                  => API.get('/protocol/status').then(r => r.data),
  calendar:         ()                  => API.get('/protocol/calendar').then(r => r.data),
  progress:         ()                  => API.get('/protocol/progress').then(r => r.data),
  therapistProgress: ()                 => API.get('/protocol/progress/therapist').then(r => r.data),
  startSession:     (n)                 => API.post(`/protocol/sessions/${n}/start`).then(r => r.data),
  sessionConfig:    (n)                 => API.get(`/protocol/sessions/${n}/config`).then(r => r.data),
  blocEnd:          (n, body)           => API.post(`/protocol/sessions/${n}/bloc-end`, body).then(r => r.data),
  completeSession:  (n, body)           => API.put(`/protocol/sessions/${n}/complete`, body).then(r => r.data),
  bilan:            (n)                 => API.get(`/protocol/bilan/${n}`).then(r => r.data),
  profile:          ()                  => API.get('/protocol/profile').then(r => r.data),
  calibrationComplete: (body)           => API.post('/protocol/calibration/complete', body).then(r => r.data),
  updatePalier:     (body)              => API.put('/protocol/palier', body).then(r => r.data),
  dailyThreshold:   (body)             => API.post('/protocol/daily-threshold', body).then(r => r.data),
  earlyStop:        (reason, notes)    => API.post('/protocol/early-stop', { reason, notes }).then(r => r.data),
  scheduleFollowup: (plannedDate)      => API.post('/protocol/followup-schedule', { planned_date: plannedDate || undefined }).then(r => r.data),
}

export const eeg = {
  status:          () => API.get('/eeg/status').then(r => r.data),
  analyze:         () => API.get('/eeg/analyze').then(r => r.data),
  finaliseBaseline: () => API.post('/eeg/baseline/finalise').then(r => r.data),
  startRecording:  () => API.post('/eeg/recording/start').then(r => r.data),
  stopRecording:   () => API.post('/eeg/recording/stop').then(r => r.data),
  wifiNetworks:    () => API.get('/eeg/wifi/networks').then(r => r.data),
  wifiConfigure:   (ssid, password) => API.post('/eeg/wifi/configure', { ssid, password }).then(r => r.data),
  wifiUseSaved:    (ssid)           => API.post('/eeg/wifi/use_saved', { ssid }).then(r => r.data),
  wifiReset:       ()               => API.post('/eeg/wifi/reset').then(r => r.data),
  analyzeFile: (file) => {
    const fd = new FormData()
    fd.append('file', file)
    return API.post('/eeg/analyze_file', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then(r => r.data)
  },
  sendReport:       (payload)      => API.post('/eeg/report', payload).then(r => r.data),
  myReports:        (limit = 100)  => API.get('/eeg/my-reports', { params: { limit } }).then(r => r.data),
  finetuningStatus: ()             => API.get('/eeg/finetuning/status').then(r => r.data),
}

// ── Recommandations média (/api/sessions/*, /api/patients/*, /api/eeg-reports/*) ──
export const recommendations = {
  // A. Reco live pendant une session EEG
  sessionMediaReco: (sessionId, blockNumber, forceCalming = false) =>
    API.post(`/sessions/${sessionId}/media-recommendation`, {
      current_block_number: blockNumber,
      force_calming: forceCalming,
    }).then(r => r.data),

  // B. Feedback post-session (liste d'interactions média)
  sessionMediaFeedback: (sessionId, items) =>
    API.post(`/sessions/${sessionId}/media-feedback`, { items }).then(r => r.data),

  // C. Générer recos offline depuis un rapport EEG
  generateOfflineReco: (reportId) =>
    API.post(`/eeg-reports/${reportId}/generate-media-recommendations`).then(r => r.data),

  // D. Recalculer scores après fine-tuning
  updateScoringAfterFinetune: (jobId) =>
    API.post(`/finetuning/${jobId}/update-media-scoring`).then(r => r.data),

  // E. Dashboard patient unifié (sessions + profil + recos + playlists + rapports)
  patientDashboard: (patientId) =>
    API.get(`/patients/${patientId}/dashboard`).then(r => r.data),

  // F. Playlists patient
  createPlaylist: (patientId, name, description = '') =>
    API.post(`/patients/${patientId}/playlists`, { name, description }).then(r => r.data),
  listPlaylists: (patientId) =>
    API.get(`/patients/${patientId}/playlists`).then(r => r.data),

  // G. Offline recommendations par rapport EEG
  offlineRecs: (patientId, reportId) =>
    API.get(`/patients/${patientId}/offline-recommendations/${reportId}`).then(r => r.data),
  offlineRecFeedback: (patientId, recId, liked) =>
    API.patch(`/patients/${patientId}/offline-recommendations/${recId}/feedback`, {
      recommendation_id: recId, liked,
    }).then(r => r.data),
}

// ── Playlist thérapeutique thérapeute ────────────────────────────────────────
// (complète l'objet therapist)
export const therapistExtended = {
  createTherapeuticPlaylist: (patientId, name, description, recommendedObjective) =>
    API.post(`/therapist/patients/${patientId}/therapeutic-playlist`, {
      name,
      description,
      recommended_objective: recommendedObjective,
    }).then(r => r.data),
}
