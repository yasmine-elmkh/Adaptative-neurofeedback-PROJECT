import { useState, useRef, useEffect } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../context/ThemeContext'
import { useAuthStore } from '../stores'
import {
  Brain, LayoutDashboard, Activity, History, MessageSquareText,
  CircleUser, LogOut, Sun, Moon, Monitor, ChevronDown, Menu, X,
  Globe, Shield, Users,
} from 'lucide-react'

/* ── Theme cycle: auto → light → dark → auto ── */
const THEMES = [
  { key: 'auto',  Icon: Monitor, label: 'theme.auto' },
  { key: 'light', Icon: Sun,     label: 'theme.light' },
  { key: 'dark',  Icon: Moon,    label: 'theme.dark' },
]

/* ── Language definitions ── */
const LANGUAGES = [
  { key: 'fr', label: 'Français', flag: '🇫🇷' },
  { key: 'en', label: 'English',  flag: '🇬🇧' },
  { key: 'ar', label: 'العربية',  flag: '🇲🇦' },
]

/* ── Dropdown wrapper (closes on outside click) ── */
function Dropdown({ trigger, children, align = 'end' }) {
  const [open, setOpen] = useState(false)
  const ref = useRef()

  useEffect(() => {
    const handle = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false) }
    document.addEventListener('mousedown', handle)
    return () => document.removeEventListener('mousedown', handle)
  }, [])

  const alignClass = align === 'end' ? 'end-0' : 'start-0'

  return (
    <div ref={ref} className="relative">
      <div onClick={() => setOpen((o) => !o)}>{trigger}</div>
      {open && (
        <div
          className={`absolute top-full mt-2 ${alignClass} z-50 min-w-[160px]
                      bg-nc-surface border border-nc-border rounded-2xl shadow-glass-lg
                      animate-fade-in overflow-hidden`}
          onClick={() => setOpen(false)}
        >
          {children}
        </div>
      )}
    </div>
  )
}

/* ── Theme switcher button ── */
function ThemeSwitcher() {
  const { theme, setTheme } = useTheme()
  const { t } = useTranslation()
  const current = THEMES.find((t) => t.key === theme) ?? THEMES[0]
  const { Icon } = current

  return (
    <Dropdown
      trigger={
        <button
          className="btn-ghost p-2 rounded-xl text-nc-muted hover:text-nc-text"
          title={t('theme.label')}
        >
          <Icon className="w-[18px] h-[18px]" />
        </button>
      }
    >
      {THEMES.map(({ key, Icon: TIcon, label }) => (
        <button
          key={key}
          onClick={() => setTheme(key)}
          className={`flex items-center gap-3 w-full px-4 py-2.5 text-sm transition-colors
                      ${theme === key
                        ? 'text-nc-accent bg-nc-accent/10 font-semibold'
                        : 'text-nc-text hover:bg-nc-surface2'}`}
        >
          <TIcon className="w-4 h-4" />
          {t(label)}
          {theme === key && <span className="ms-auto w-1.5 h-1.5 rounded-full bg-nc-accent" />}
        </button>
      ))}
    </Dropdown>
  )
}

/* ── Language switcher button ── */
function LangSwitcher() {
  const { i18n, t } = useTranslation()
  const current = LANGUAGES.find((l) => l.key === i18n.language) ?? LANGUAGES[0]

  return (
    <Dropdown
      trigger={
        <button
          className="btn-ghost flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-nc-muted hover:text-nc-text"
          title={t('lang.label')}
        >
          <Globe className="w-4 h-4" />
          <span className="text-xs font-semibold uppercase">{current.key}</span>
          <ChevronDown className="w-3 h-3" />
        </button>
      }
    >
      {LANGUAGES.map(({ key, label, flag }) => (
        <button
          key={key}
          onClick={() => i18n.changeLanguage(key)}
          className={`flex items-center gap-3 w-full px-4 py-2.5 text-sm transition-colors
                      ${i18n.language === key
                        ? 'text-nc-accent bg-nc-accent/10 font-semibold'
                        : 'text-nc-text hover:bg-nc-surface2'}`}
        >
          <span className="text-base">{flag}</span>
          {label}
          {i18n.language === key && <span className="ms-auto w-1.5 h-1.5 rounded-full bg-nc-accent" />}
        </button>
      ))}
    </Dropdown>
  )
}

/* ── Main Layout ── */
export default function Layout() {
  const { t } = useTranslation()
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)

  const role = user?.role ?? 'patient'

  const NAV_ITEMS = [
    { to: '/dashboard',   Icon: LayoutDashboard,    key: 'nav.dashboard', roles: null,                    exclude: [] },
    { to: '/session/new', Icon: Activity,            key: 'nav.session',   roles: null,                    exclude: ['admin', 'therapist'] },
    { to: '/history',     Icon: History,             key: 'nav.history',   roles: null,                    exclude: ['admin', 'therapist'] },
    { to: '/assistant',   Icon: MessageSquareText,   key: 'nav.assistant', roles: null,                    exclude: ['admin', 'therapist'] },
    { to: '/profile',     Icon: CircleUser,          key: 'nav.profile',   roles: null,                    exclude: [] },
    { to: '/therapist',   Icon: Users,               key: 'nav.therapist', roles: ['therapist', 'admin'],  exclude: ['admin'] },
    { to: '/admin',       Icon: Shield,              key: 'nav.admin',     roles: ['admin'],               exclude: [] },
  ].filter(item =>
    (!item.roles || item.roles.includes(role)) &&
    !item.exclude.includes(role)
  )

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const userInitial = user?.email?.charAt(0).toUpperCase() ?? 'U'

  return (
    <div className="min-h-screen flex flex-col bg-nc-bg">
      {/* ══════════════════════ TOP NAVBAR ══════════════════════ */}
      <header className="sticky top-0 z-50 border-b border-nc-border"
              style={{ background: 'rgb(var(--nc-surface)/0.8)', backdropFilter: 'blur(20px)' }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center gap-4">

          {/* ── Logo ── */}
          <NavLink to="/dashboard" className="flex items-center gap-2.5 shrink-0 me-4">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center"
                 style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' }}>
              <Brain className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-lg text-nc-text tracking-tight">NeuroCap</span>
          </NavLink>

          {/* ── Desktop nav ── */}
          <nav className="hidden md:flex items-center gap-1 flex-1">
            {NAV_ITEMS.map(({ to, Icon, key }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) =>
                  `flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-medium transition-all
                   ${isActive
                     ? 'bg-nc-accent/15 text-nc-accent'
                     : 'text-nc-muted hover:text-nc-text hover:bg-nc-surface2'}`
                }
              >
                <Icon className="w-4 h-4" />
                {t(key)}
              </NavLink>
            ))}
          </nav>

          {/* ── Right controls ── */}
          <div className="flex items-center gap-1 ms-auto">
            <ThemeSwitcher />
            <LangSwitcher />

            {/* User avatar menu */}
            <Dropdown
              trigger={
                <button className="flex items-center gap-2 px-2 py-1.5 rounded-xl
                                   hover:bg-nc-surface2 transition-colors ms-1">
                  <div className="w-7 h-7 rounded-full flex items-center justify-center
                                  text-xs font-bold text-white"
                       style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' }}>
                    {userInitial}
                  </div>
                  <span className="hidden sm:block text-xs font-medium text-nc-muted max-w-[100px] truncate">
                    {user?.email}
                  </span>
                  <ChevronDown className="w-3.5 h-3.5 text-nc-muted" />
                </button>
              }
            >
              <div className="px-4 py-3 border-b border-nc-border">
                <p className="text-sm font-semibold text-nc-text truncate">{user?.email}</p>
                <p className="text-xs text-nc-muted capitalize mt-0.5">{user?.role}</p>
              </div>
              <NavLink to="/profile"
                className="flex items-center gap-3 px-4 py-2.5 text-sm text-nc-text hover:bg-nc-surface2 transition-colors">
                <CircleUser className="w-4 h-4 text-nc-muted" />
                {t('nav.profile')}
              </NavLink>
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 w-full px-4 py-2.5 text-sm text-nc-danger hover:bg-nc-danger/10 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                {t('nav.logout')}
              </button>
            </Dropdown>

            {/* Mobile hamburger */}
            <button
              className="md:hidden p-2 rounded-xl text-nc-muted hover:text-nc-text hover:bg-nc-surface2 ms-1"
              onClick={() => setMobileOpen((o) => !o)}
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* ══════════════════════ MOBILE DRAWER ══════════════════════ */}
      {mobileOpen && (
        <div className="md:hidden fixed inset-0 z-40 flex" onClick={() => setMobileOpen(false)}>
          <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
          <nav
            className="relative ms-auto w-72 bg-nc-surface h-full flex flex-col py-6 px-4 gap-1 shadow-glass-lg animate-slide-right"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center gap-2.5 mb-6 px-2">
              <Brain className="w-6 h-6 text-nc-accent" />
              <span className="font-bold text-nc-text">NeuroCap</span>
            </div>

            {NAV_ITEMS.map(({ to, Icon, key }) => (
              <NavLink
                key={to}
                to={to}
                onClick={() => setMobileOpen(false)}
                className={({ isActive }) =>
                  `flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all
                   ${isActive
                     ? 'bg-nc-accent/15 text-nc-accent'
                     : 'text-nc-muted hover:text-nc-text hover:bg-nc-surface2'}`
                }
              >
                <Icon className="w-4 h-4" />
                {t(key)}
              </NavLink>
            ))}

            <div className="mt-auto border-t border-nc-border pt-4">
              <button
                onClick={handleLogout}
                className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm text-nc-danger hover:bg-nc-danger/10 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                {t('nav.logout')}
              </button>
            </div>
          </nav>
        </div>
      )}

      {/* ══════════════════════ PAGE CONTENT ══════════════════════ */}
      <main className="flex-1 min-h-0 pb-16 md:pb-0">
        <Outlet />
      </main>

      {/* ══════════════════════ FOOTER (desktop only) ══════════════════════ */}
      <footer className="hidden md:block border-t border-nc-border py-5">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <div className="flex items-center gap-2 text-xs text-nc-muted">
            <Brain className="w-3.5 h-3.5 text-nc-accent" />
            <span>© 2026 NeuroCap — Easy Medical Device</span>
          </div>
          <span className="text-[10px] text-nc-muted/60">
            AD8232 + ESP32 · Fp2 · 250 Hz · CDC §2.5
          </span>
        </div>
      </footer>

      {/* ══════════════════════ MOBILE BOTTOM NAV ══════════════════════ */}
      <nav className="md:hidden fixed bottom-0 inset-x-0 z-50 border-t border-nc-border"
           style={{ background: 'rgb(var(--nc-surface)/0.95)', backdropFilter: 'blur(20px)' }}>
        <div className="flex items-center justify-around px-2 py-1.5">
          {NAV_ITEMS.slice(0, 5).map(({ to, Icon, key }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex flex-col items-center gap-0.5 px-3 py-1.5 rounded-xl transition-all
                 ${isActive ? 'text-nc-accent' : 'text-nc-muted hover:text-nc-text'}`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-[9px] font-medium">{t(key)}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
