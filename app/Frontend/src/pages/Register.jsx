import { useState, useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../context/ThemeContext'
import { useAuthStore } from '../stores'
import { auth } from '../utils/api'
import {
  Mail, Lock, UserPlus, User, Sun, Moon, Monitor, Globe, ChevronDown,
  ArrowLeft, RefreshCw, CheckCircle, ShieldCheck, Check, X,
} from 'lucide-react'

/* ── Règles de sécurité du mot de passe ── */
const PASSWORD_RULES = [
  { key: 'length',    test: (p) => p.length >= 8,              label: 'auth.register.pw_length'    },
  { key: 'upper',     test: (p) => /[A-Z]/.test(p),            label: 'auth.register.pw_upper'     },
  { key: 'lower',     test: (p) => /[a-z]/.test(p),            label: 'auth.register.pw_lower'     },
  { key: 'digit',     test: (p) => /[0-9]/.test(p),            label: 'auth.register.pw_digit'     },
  { key: 'special',   test: (p) => /[^A-Za-z0-9]/.test(p),    label: 'auth.register.pw_special'   },
]

function PasswordStrength({ password }) {
  const { t } = useTranslation()
  const results = useMemo(
    () => PASSWORD_RULES.map((r) => ({ ...r, ok: r.test(password) })),
    [password]
  )
  const score = results.filter((r) => r.ok).length

  const strengthLabel = score <= 1 ? t('auth.register.pw_weak')
    : score <= 3 ? t('auth.register.pw_medium')
    : score === 4 ? t('auth.register.pw_good')
    : t('auth.register.pw_strong')

  const strengthColor = score <= 1 ? '#ef4444'
    : score <= 3 ? '#f59e0b'
    : score === 4 ? '#3b82f6'
    : '#10b981'

  if (!password) return null

  return (
    <div className="mt-2 space-y-2 animate-fade-in">
      {/* Barre de progression */}
      <div className="flex items-center gap-2">
        <div className="flex-1 flex gap-1 h-1.5">
          {[1, 2, 3, 4, 5].map((i) => (
            <div
              key={i}
              className="flex-1 rounded-full transition-all duration-300"
              style={{
                background: i <= score ? strengthColor : 'rgb(var(--nc-border))',
              }}
            />
          ))}
        </div>
        <span className="text-[11px] font-semibold shrink-0 transition-colors duration-300"
              style={{ color: strengthColor }}>
          {strengthLabel}
        </span>
      </div>

      {/* Checklist des règles */}
      <ul className="space-y-1">
        {results.map((r) => (
          <li key={r.key} className="flex items-center gap-2">
            <div
              className="w-4 h-4 rounded-full flex items-center justify-center shrink-0 transition-all duration-200"
              style={{
                background: r.ok ? '#10b981' : 'transparent',
                border: r.ok ? '2px solid #10b981' : '2px solid rgb(var(--nc-border))',
              }}
            >
              {r.ok
                ? <Check className="w-2.5 h-2.5 text-white" strokeWidth={3} />
                : <X className="w-2.5 h-2.5" style={{ color: 'rgb(var(--nc-muted))' }} strokeWidth={2.5} />
              }
            </div>
            <span className={`text-xs transition-colors duration-200 ${r.ok ? 'text-emerald-400' : 'text-nc-muted'}`}>
              {t(r.label)}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

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

export default function Register() {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const register = useAuthStore((s) => s.register)

  /* ── Formulaire ── */
  const [firstName, setFirstName] = useState('')
  const [lastName,  setLastName]  = useState('')
  const [email,     setEmail]     = useState('')
  const [password,  setPassword]  = useState('')
  const [confirm,   setConfirm]   = useState('')

  /* ── État UI ── */
  const [step,    setStep]    = useState('form')    // 'form' | 'verify'
  const [error,   setError]   = useState('')
  const [loading, setLoading] = useState(false)
  const [codeSent, setCodeSent] = useState(false)

  /* ── Code OTP ── */
  const [code,    setCode]    = useState('')
  const [devCode, setDevCode] = useState('')   // affiché en dev si SMTP non configuré

  /* ── Validation force du mot de passe ── */
  const pwRulesStatus = useMemo(
    () => PASSWORD_RULES.map((r) => r.test(password)),
    [password]
  )
  const pwStrong = pwRulesStatus.every(Boolean)

  /* ───────────────────────── Step 1 : envoyer le code ───────────────────────── */
  const handleSendCode = async (e) => {
    e.preventDefault()
    if (!pwStrong) return setError(t('auth.register.error_pw_weak'))
    if (password !== confirm) return setError(t('auth.register.error_mismatch'))
    setError('')
    setLoading(true)
    try {
      const res = await auth.sendCode(email)
      // Mode dev : le backend renvoie _dev_code si DEBUG=True et SMTP non configuré
      if (res?._dev_code) setDevCode(res._dev_code)
      setCodeSent(true)
      setStep('verify')
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message || t('auth.register.error_generic')
      if (err?.response?.status === 409) {
        setError(t('auth.register.error_email_exists'))
      } else {
        setError(detail)
      }
    } finally {
      setLoading(false)
    }
  }

  /* ───────────────────────── Step 2 : renvoyer le code ────────────────────── */
  const handleResend = async () => {
    setError('')
    setLoading(true)
    try {
      await auth.sendCode(email)
      setCodeSent(true)
      setError('')
    } catch (err) {
      setError(err?.response?.data?.detail || t('auth.register.error_generic'))
    } finally {
      setLoading(false)
    }
  }

  /* ───────────────────────── Step 2 : vérifier + créer ─────────────────────── */
  const handleVerify = async (e) => {
    e.preventDefault()
    if (code.length !== 8) return setError(t('auth.register.error_code_format'))
    setError('')
    setLoading(true)
    try {
      await register(email, password, firstName, lastName, code)
      navigate('/dashboard')
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message || t('auth.register.error_generic')
      if (detail.includes('expiré') || detail.includes('expired')) {
        setError(t('auth.register.error_code_expired'))
      } else if (detail.includes('incorrect') || detail.includes('invalid')) {
        setError(t('auth.register.error_code_invalid'))
      } else {
        setError(detail)
      }
    } finally {
      setLoading(false)
    }
  }

  /* ───────────────────────── Rendu ────────────────────────────────────────── */
  return (
    <div className="flex min-h-screen bg-nc-bg">

      {/* ── Left: Auth form ─────────────────────────────────────── */}
      <div className="relative flex items-center justify-center w-full lg:w-1/2 min-h-screen overflow-hidden">
        <AuthTopBar />

        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute -top-40 -end-40 w-[600px] h-[600px] rounded-full"
               style={{ background: 'radial-gradient(circle, rgb(var(--nc-accent)/0.12) 0%, transparent 70%)' }} />
          <div className="absolute -bottom-40 -start-40 w-[500px] h-[500px] rounded-full"
               style={{ background: 'radial-gradient(circle, rgb(var(--nc-accent)/0.08) 0%, transparent 70%)' }} />
        </div>

        <div className="relative z-10 w-full max-w-[420px] px-4 py-10 animate-slide-up">
          <div className="card p-8 space-y-6">

            {/* ══════ STEP 1 — Formulaire ══════ */}
            {step === 'form' && (
              <>
                <div className="flex flex-col items-center gap-3">
                  <img src="/NeuroCap_logo.png" alt="NeuroCap" className="w-14 h-14 object-contain" />
                  <div className="text-center">
                    <h1 className="text-2xl font-bold text-nc-text">{t('auth.register.title')}</h1>
                    <p className="text-sm text-nc-muted mt-1">{t('auth.register.subtitle')}</p>
                  </div>
                </div>

                <form onSubmit={handleSendCode} className="space-y-4">
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="label">{t('auth.register.first_name')}</label>
                      <div className="relative">
                        <User className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nc-muted pointer-events-none" />
                        <input type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)}
                               placeholder={t('auth.register.first_name_placeholder')}
                               className="input input-icon" required autoComplete="given-name" />
                      </div>
                    </div>
                    <div>
                      <label className="label">{t('auth.register.last_name')}</label>
                      <div className="relative">
                        <User className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nc-muted pointer-events-none" />
                        <input type="text" value={lastName} onChange={(e) => setLastName(e.target.value)}
                               placeholder={t('auth.register.last_name_placeholder')}
                               className="input input-icon" required autoComplete="family-name" />
                      </div>
                    </div>
                  </div>

                  <div>
                    <label className="label">{t('auth.register.email')}</label>
                    <div className="relative">
                      <Mail className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nc-muted pointer-events-none" />
                      <input type="email" value={email} onChange={(e) => setEmail(e.target.value)}
                             placeholder={t('auth.register.email_placeholder')}
                             className="input input-icon" required autoComplete="email" />
                    </div>
                  </div>

                  <div>
                    <label className="label">{t('auth.register.password')}</label>
                    <div className="relative">
                      <Lock className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nc-muted pointer-events-none" />
                      <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                             placeholder={t('auth.register.password_placeholder')}
                             className="input input-icon" required minLength={8} autoComplete="new-password" />
                    </div>
                    <PasswordStrength password={password} />
                  </div>

                  <div>
                    <label className="label">{t('auth.register.confirm')}</label>
                    <div className="relative">
                      <Lock className="absolute start-3 top-1/2 -translate-y-1/2 w-4 h-4 text-nc-muted pointer-events-none" />
                      <input type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)}
                             placeholder={t('auth.register.confirm_placeholder')}
                             className="input input-icon" required autoComplete="new-password" />
                    </div>
                  </div>

                  {error && (
                    <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm">
                      {error}
                    </div>
                  )}

                  <button type="submit" disabled={loading || !pwStrong}
                          className="btn-primary w-full mt-2 disabled:opacity-40 disabled:cursor-not-allowed">
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        {t('auth.register.sending_code')}
                      </span>
                    ) : (
                      <>
                        <Mail className="w-4 h-4" />
                        {t('auth.register.send_code')}
                      </>
                    )}
                  </button>
                </form>

                <p className="text-center text-sm text-nc-muted">
                  {t('auth.register.already')}{' '}
                  <Link to="/login" className="text-nc-accent hover:underline font-medium">
                    {t('auth.register.sign_in')}
                  </Link>
                </p>
              </>
            )}

            {/* ══════ STEP 2 — Vérification OTP ══════ */}
            {step === 'verify' && (
              <>
                <div className="flex flex-col items-center gap-3">
                  <div className="w-14 h-14 rounded-2xl bg-nc-accent/15 flex items-center justify-center">
                    <ShieldCheck className="w-7 h-7 text-nc-accent" />
                  </div>
                  <div className="text-center">
                    <h1 className="text-2xl font-bold text-nc-text">{t('auth.register.verify_email')}</h1>
                    <p className="text-sm text-nc-muted mt-1 leading-relaxed">
                      {t('auth.register.verify_subtitle', { email })}
                    </p>
                  </div>
                </div>

                {codeSent && (
                  <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
                    <CheckCircle className="w-4 h-4 shrink-0" />
                    {t('auth.register.code_sent')}
                  </div>
                )}

                {/* Bandeau dev : affiché uniquement si le backend est en mode DEBUG et SMTP non configuré */}
                {devCode && (
                  <div className="px-4 py-3 rounded-xl bg-yellow-500/10 border border-yellow-500/30 text-yellow-300 text-sm space-y-1">
                    <p className="font-semibold text-xs uppercase tracking-wide opacity-70">Mode dev — SMTP non configuré</p>
                    <p className="font-mono text-xl tracking-[0.4em] text-center font-bold">{devCode}</p>
                  </div>
                )}

                <form onSubmit={handleVerify} className="space-y-4">
                  <div>
                    <label className="label">{t('auth.register.verify_code')}</label>
                    <input
                      type="text"
                      inputMode="numeric"
                      pattern="[0-9]{8}"
                      maxLength={8}
                      value={code}
                      onChange={(e) => setCode(e.target.value.replace(/\D/g, '').slice(0, 8))}
                      placeholder={t('auth.register.verify_placeholder')}
                      className="input text-center font-mono text-2xl tracking-[0.5em] py-4"
                      required
                      autoFocus
                    />
                    <p className="text-xs text-nc-muted mt-1 text-center">{t('auth.register.verify_hint')}</p>
                  </div>

                  {error && (
                    <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm">
                      {error}
                    </div>
                  )}

                  <button type="submit" disabled={loading || code.length !== 8} className="btn-primary w-full">
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        {t('auth.register.verifying')}
                      </span>
                    ) : (
                      <>
                        <UserPlus className="w-4 h-4" />
                        {t('auth.register.verify_submit')}
                      </>
                    )}
                  </button>
                </form>

                <div className="flex items-center justify-between text-sm">
                  <button
                    onClick={() => { setStep('form'); setCode(''); setError(''); setCodeSent(false) }}
                    className="flex items-center gap-1.5 text-nc-muted hover:text-nc-text transition-colors"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    {t('auth.register.edit_email')}
                  </button>
                  <button
                    onClick={handleResend}
                    disabled={loading}
                    className="flex items-center gap-1.5 text-nc-accent hover:underline transition-colors disabled:opacity-50"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                    {t('auth.register.resend_code')}
                  </button>
                </div>
              </>
            )}

          </div>

          <p className="text-center text-xs text-nc-muted/60 mt-4">NeuroCap · Easy Medical Device · 2026</p>
        </div>
      </div>

      {/* ── Right: Brain video ──────────────────────────────────── */}
      <div className="hidden lg:block relative w-1/2 overflow-hidden">
        <video
          src="/video/Brain.mp4"
          autoPlay muted loop playsInline
          className="absolute inset-0 w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black/40" />
        <div className="absolute inset-y-0 start-0 w-24 z-10"
             style={{ background: 'linear-gradient(to right, rgb(var(--nc-bg)), transparent)' }} />
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
