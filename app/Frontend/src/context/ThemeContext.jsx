import { createContext, useContext, useEffect, useState } from 'react'

const ThemeContext = createContext()

const STORAGE_KEY = 'neurocap_theme'

function getEffective(theme) {
  if (theme === 'auto') {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  }
  return theme
}

function applyTheme(effective) {
  const root = document.documentElement
  /* Brief transition class so colors animate smoothly */
  root.classList.add('theme-transition')
  root.classList.toggle('dark', effective === 'dark')
  setTimeout(() => root.classList.remove('theme-transition'), 300)
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(
    () => localStorage.getItem(STORAGE_KEY) || 'auto'
  )

  const effectiveTheme = getEffective(theme)

  /* Apply on mount and whenever theme changes */
  useEffect(() => {
    applyTheme(effectiveTheme)
    localStorage.setItem(STORAGE_KEY, theme)
  }, [theme, effectiveTheme])

  /* Listen for OS preference when mode is 'auto' */
  useEffect(() => {
    if (theme !== 'auto') return
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => applyTheme(getEffective('auto'))
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [theme])

  const setTheme = (next) => setThemeState(next)

  return (
    <ThemeContext.Provider value={{ theme, setTheme, effectiveTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const ctx = useContext(ThemeContext)
  if (!ctx) throw new Error('useTheme must be used within ThemeProvider')
  return ctx
}
