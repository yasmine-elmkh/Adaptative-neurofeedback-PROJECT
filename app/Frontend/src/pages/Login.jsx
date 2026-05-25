import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../context/ThemeContext'
import { useAuthStore } from '../stores'
import { Mail, Lock, LogIn, Sun, Moon, Monitor, Globe, ChevronDown } from 'lucide-react'

const THEMES = [
  { key: 'auto',  Icon: Monitor },
  { key: 'light', Icon: Sun },
  { key: 'dark',  Icon: Moon },
]
const LANGS = [
  { key: 'fr', label: 'FR', flag: '🇫🇷' },
  { key: 'en', label: 'EN', flag: '🇬🇧' },
  { key: 'ar', label: 'AR', flag: '🇲🇦' },
]

function AuthTopBar() {
  const { theme, setTheme } = useTheme()
  const { i18n } = useTranslation()
  const [langOpen, setLangOpen] = useState(false)
  const ThemeIcon = THEMES.find((t) => t.key === theme)?.Icon ?? Monitor
  const cycleTheme = () => {
    const idx = THEMES.findIndex((t) => t.key === theme)
    setTheme(THEMES[(idx + 1) % THEMES.length].key)
  }
  return (
    <div className="absolute top-4 end-4 z-20 flex items-center gap-2">
      <button onClick={cycleTheme}
              className="p-2 rounded-xl bg-nc-surface/70 border border-nc-border text-nc-muted hover:text-nc-accent backdrop-blur-sm transition-all">
        <ThemeIcon className="w-4 h-4" />
      </button>
      <div className="relative">
        <button onClick={() => setLangOpen((o) => !o)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-nc-surface/70 border border-nc-border text-nc-muted hover:text-nc-accent backdrop-blur-sm transition-all">
          <Globe className="w-4 h-4" />
          <span className="text-xs font-semibold uppercase">{i18n.language}</span>
          <ChevronDown className="w-3 h-3" />
        </button>
        {langOpen && (
          <div className="absolute top-full mt-2 end-0 bg-nc-surface border border-nc-border rounded-2xl shadow-glass-lg overflow-hidden z-30 animate-fade-in">
            {LANGS.map(({ key, label, flag }) => (
              <button key={key} onClick={() => { i18n.changeLanguage(key); setLangOpen(false) }}
                      className={`flex items-center gap-3 w-full px-4 py-2.5 text-sm transition-colors
                                  ${i18n.language === key ? 'text-nc-accent bg-nc-accent/10 font-semibold' : 'text-nc-text hover:bg-nc-surface2'}`}>
                <span>{flag}</span>{label}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

function BrainBg() {
  return (
    <svg viewBox="0 0 400 400" className="w-full h-full opacity-20" fill="none">
      <defs>
        <radialGradient id="g1" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="rgb(var(--nc-accent))" stopOpacity="0.8" />
          <stop offset="100%" stopColor="rgb(var(--nc-accent))" stopOpacity="0" />
        </radialGradient>
      </defs>
      <path d="M20 200 Q 50 150 80 200 T 140 200 T 200 200 T 260 200 T 320 200 T 380 200"
            stroke="rgb(var(--nc-accent))" strokeWidth="2" strokeLinecap="round" />
      <path d="M20 220 Q 60 170 100 220 T 180 220 T 260 180 T 340 220 T 380 220"
            stroke="rgb(var(--nc-accent))" strokeWidth="1.5" strokeOpacity="0.5" strokeLinecap="round" />
      {[[200,200],[120,160],[280,160],[160,270],[240,270]].map(([cx,cy],i) => (
        <g key={i}>
          <circle cx={cx} cy={cy} r="28" fill="url(#g1)" />
          <circle cx={cx} cy={cy} r="6" fill="rgb(var(--nc-accent))" fillOpacity="0.7" />
        </g>
      ))}
      {[[200,200,120,160],[200,200,280,160],[200,200,160,270],[200,200,240,270]].map(([x1,y1,x2,y2],i) => (
        <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke="rgb(var(--nc-accent))" strokeOpacity="0.3" strokeWidth="1.5" />
      ))}
    </svg>
  )
}

export default function Login() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const login = useAuthStore((s) => s.login)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error,     setError]     = useState('')
  const [errorType, setErrorType] = useState('')  // 'no_account' | 'wrong_password' | ''
  const [loading,   setLoading]   = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setErrorType('')
    setLoading(true)
    try {
      await login(email, password)
      const user = useAuthStore.getState().user
      const role = user?.role ?? 'patient'
      if (role === 'admin')           navigate('/admin')
      else if (role === 'therapist')  navigate('/therapist')
      else                            navigate('/dashboard')
    } catch (err) {
      const status = err?.response?.status
      const detail = err?.response?.data?.detail || err.message || ''
      if (status === 404 || detail.toLowerCase().includes('aucun compte') || detail.toLowerCase().includes('no account')) {
        setErrorType('no_account')
        setError(t('auth.login.error_no_account'))
      } else if (status === 401 || detail.toLowerCase().includes('mot de passe') || detail.toLowerCase().includes('password')) {
        setErrorType('wrong_password')
        setError(t('auth.login.error_wrong_password'))
      } else {
        setErrorType('')
        setError(detail || t('auth.login.error_generic'))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen bg-nc-bg">

      {/* ── Left: Auth form ─────────────────────────────────────── */}
      <div className="relative flex items-center justify-center w-full lg:w-1/2 min-h-screen overflow-hidden">
        <AuthTopBar />

        {/* Background decorations */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute -top-40 -start-40 w-[600px] h-[600px] rounded-full"
               style={{ background: 'radial-gradient(circle, rgb(var(--nc-accent)/0.12) 0%, transparent 70%)' }} />
          <div className="absolute -bottom-40 -end-40 w-[500px] h-[500px] rounded-full"
               style={{ background: 'radial-gradient(circle, rgb(var(--nc-accent)/0.08) 0%, transparent 70%)' }} />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-[500px] h-[500px]"><BrainBg /></div>
          </div>
        </div>

        {/* Card */}
        <div className="relative z-10 w-full max-w-[420px] px-4 animate-slide-up">
          <div className="card p-8 space-y-6">

            {/* Logo */}
            <div className="flex flex-col items-center gap-3">
              <img src="/NeuroCap_Logo.png" alt="NeuroCap" className="w-14 h-14 object-contain" />
              <div className="text-center">
                <h1 className="text-2xl font-bold text-nc-text">{t('auth.login.title')}</h1>
                <p className="text-sm text-nc-muted mt-1">{t('auth.login.subtitle')}</p>
              </div>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="label">{t('auth.login.email')}</label>
                <div className="relative">
                  <Mail className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nc-muted pointer-events-none" />
                  <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                         placeholder={t('auth.login.email_placeholder')}
                         className="input input-icon" required autoComplete="email" />
                </div>
              </div>

              <div>
                <label className="label">{t('auth.login.password')}</label>
                <div className="relative">
                  <Lock className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nc-muted pointer-events-none" />
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                         placeholder={t('auth.login.password_placeholder')}
                         className="input input-icon" required autoComplete="current-password" />
                </div>
              </div>

              {error && (
                <div className="px-4 py-3 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm space-y-1">
                  <p>{error}</p>
                  {errorType === 'no_account' && (
                    <p className="text-nc-muted text-xs">
                      {t('auth.login.no_account')}{' '}
                      <Link to="/register" className="text-nc-accent hover:underline font-medium">
                        {t('auth.login.sign_up')}
                      </Link>
                    </p>
                  )}
                </div>
              )}

              <button type="submit" disabled={loading} className="btn-primary w-full mt-2">
                {loading ? (
                  <span className="flex items-center gap-2">
                    <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    {t('auth.login.loading')}
                  </span>
                ) : (
                  <>
                    <LogIn className="w-4 h-4" />
                    {t('auth.login.submit')}
                  </>
                )}
              </button>
            </form>

            <p className="text-center text-sm text-nc-muted">
              {t('auth.login.no_account')}{' '}
              <Link to="/register" className="text-nc-accent hover:underline font-medium">
                {t('auth.login.sign_up')}
              </Link>
            </p>
          </div>

          <p className="text-center text-xs text-nc-muted/60 mt-4">NeuroCap · Easy Medical Device · 2026</p>
        </div>
      </div>

      {/* ── Right: Brain video ──────────────────────────────────── */}
      <div className="hidden lg:block relative w-1/2 overflow-hidden">
        {/* Video */}
        <video
          src="/video/Brain.mp4"
          autoPlay
          muted
          loop
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
        />

        {/* Dark overlay so text is readable */}
        <div className="absolute inset-0 bg-black/40" />

        {/* Left-edge fade to blend with form panel */}
        <div className="absolute inset-y-0 start-0 w-24 z-10"
             style={{ background: 'linear-gradient(to right, rgb(var(--nc-bg)), transparent)' }} />

        {/* Branding overlay */}
        <div className="absolute inset-0 z-10 flex flex-col justify-end p-10">
          <div className="space-y-2">
            <p className="text-white/90 text-3xl font-bold tracking-tight">{t('app.name')}</p>
            <p className="text-white/60 text-base">{t('app.tagline')}</p>
            <p className="text-white/40 text-sm">{t('app.company')}</p>
          </div>
        </div>
      </div>

    </div>
  )
}
