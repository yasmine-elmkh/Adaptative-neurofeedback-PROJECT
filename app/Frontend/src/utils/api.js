import axios from 'axios'

const API = axios.create({ baseURL: '/api' })
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('neurocap_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

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

// ── EEG Temps Réel (/api/eeg/*) ──────────────────────────────────────────────
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
