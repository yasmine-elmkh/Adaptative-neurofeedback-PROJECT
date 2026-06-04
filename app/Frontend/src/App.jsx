import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'

import Landing            from './pages/Landing'
import Login              from './pages/Login'
import Register           from './pages/Register'
import Dashboard          from './pages/DashboardPage'
import AdminDashboard     from './pages/AdminDashboard'
import History            from './pages/History'
import Assistant          from './pages/Assistant'
import Profile            from './pages/Profile'
import AdminPanel         from './pages/AdminPanel'
import TherapistDashboard      from './pages/TherapistDashboard'
import TherapistPatientDetail  from './pages/TherapistPatientDetail'
import EEGSelector             from './pages/EEGSelector'
import EEGPage                 from './pages/EEGPage'
import EEGLive                 from './pages/EEGLive'
import EEGFile                 from './pages/EEGFile'
import ElectrodeGuide          from './pages/ElectrodeGuide'
import FeedbackPage             from './pages/FeedbackPage'
import FeedbackSession          from './pages/FeedbackSession'
import EEGFeedbackMode          from './pages/EEGFeedbackMode'
import ProtocolDashboard        from './pages/ProtocolDashboard'
import CalibrationSession       from './pages/CalibrationSession'
import ProtocolSession          from './pages/ProtocolSession'
import ProtocolBilan            from './pages/ProtocolBilan'
import SessionEntry             from './pages/SessionEntry'
import PatientMediaDashboard    from './pages/PatientMediaDashboard'
import SessionSetup             from './pages/SessionSetup'
import NeurofeedbackSession     from './pages/NeurofeedbackSession'

import { useAuthStore } from './stores'

/* Hydrate user from stored token on first render (page refresh case) */
function PrivateRoute({ children }) {
  const token     = useAuthStore((s) => s.token)
  const user      = useAuthStore((s) => s.user)
  const fetchUser = useAuthStore((s) => s.fetchUser)

  useEffect(() => {
    if (token && !user) fetchUser()
  }, [token, user, fetchUser])

  if (!token) return <Navigate to="/login" replace />
  return children
}

function PublicRoute({ children }) {
  const token = useAuthStore((s) => s.token)
  return token ? <Navigate to="/dashboard" replace /> : children
}

/* Role-aware dashboard: admin → AdminDashboard, others → patient Dashboard */
function DashboardRoute() {
  const user      = useAuthStore((s) => s.user)
  const token     = useAuthStore((s) => s.token)
  const fetchUser = useAuthStore((s) => s.fetchUser)

  useEffect(() => {
    if (token && !user) fetchUser()
  }, [token, user, fetchUser])

  if (!token) return <Navigate to="/login" replace />
  if (!user) return (
    <div className="flex items-center justify-center h-[60vh]">
      <div className="w-8 h-8 border-2 border-nc-accent border-t-transparent rounded-full animate-spin" />
    </div>
  )
  if (user.role === 'admin')     return <AdminDashboard />
  if (user.role === 'therapist') return <TherapistDashboard />
  return <Dashboard />
}

/* Role-gated route — shows spinner while user object is being loaded */
function RoleRoute({ children, roles }) {
  const user  = useAuthStore((s) => s.user)
  const token = useAuthStore((s) => s.token)
  if (!token) return <Navigate to="/login" replace />
  if (!user) return (
    <div className="flex items-center justify-center h-[60vh]">
      <div className="w-8 h-8 border-2 border-nc-accent border-t-transparent rounded-full animate-spin" />
    </div>
  )
  const role = user.role ?? 'patient'
  if (!roles.includes(role)) return <Navigate to="/dashboard" replace />
  return children
}

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Landing />} />

        <Route path="/login"    element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />

        <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
          <Route path="/dashboard"    element={<DashboardRoute />} />
          <Route path="/history"      element={<History />} />
          <Route path="/history/:id"  element={<History />} />
          <Route path="/assistant"    element={<Assistant />} />
          <Route path="/profile"      element={<Profile />} />

          {/* EEG — tabs live / upload */}
          <Route path="/eeg"              element={<EEGPage tab="live" />} />
          <Route path="/eeg/live"         element={<EEGPage tab="live" />} />
          <Route path="/eeg/upload"       element={<EEGPage tab="upload" />} />
          {/* Rétro-compatibilité anciens liens */}
          <Route path="/eeg-live"         element={<EEGPage tab="live" />} />
          <Route path="/eeg-file"         element={<EEGPage tab="upload" />} />
          <Route path="/electrode-guide"  element={<ElectrodeGuide />} />
          <Route path="/feedback"         element={<FeedbackPage />} />
          <Route path="/feedback/session" element={<FeedbackSession />} />
          <Route path="/eeg-feedback"     element={<EEGFeedbackMode />} />

          {/* Protocole 15 séances */}
          <Route path="/protocol"                   element={<ProtocolDashboard />} />
          <Route path="/protocol/calibration"       element={<CalibrationSession />} />
          <Route path="/protocol/entry/:n"          element={<SessionEntry />} />
          <Route path="/protocol/session/:n"        element={<ProtocolSession />} />
          <Route path="/protocol/bilan/:n"          element={<ProtocolBilan />} />

          {/* Session setup + neurofeedback stepper */}
          <Route path="/session/setup"   element={<SessionSetup />} />
          <Route path="/neurofeedback"   element={<NeurofeedbackSession />} />

          {/* Médias, playlists et recommandations patient */}
          <Route path="/media-dashboard"            element={<PatientMediaDashboard />} />

          {/* Admin only */}
          <Route path="/admin" element={
            <RoleRoute roles={['admin']}>
              <AdminPanel />
            </RoleRoute>
          } />

          {/* Therapist + admin */}
          <Route path="/therapist" element={
            <RoleRoute roles={['therapist', 'admin']}>
              <TherapistDashboard />
            </RoleRoute>
          } />
          <Route path="/therapist/patient/:patientId" element={
            <RoleRoute roles={['therapist', 'admin']}>
              <TherapistPatientDetail />
            </RoleRoute>
          } />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  )
}
