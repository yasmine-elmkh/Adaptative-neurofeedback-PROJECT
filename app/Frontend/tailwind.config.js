/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        /* ── CSS-variable–driven palette (auto-switches light ↔ dark) ── */
        'nc-bg':       'rgb(var(--nc-bg)       / <alpha-value>)',
        'nc-surface':  'rgb(var(--nc-surface)  / <alpha-value>)',
        'nc-surface2': 'rgb(var(--nc-surface2) / <alpha-value>)',
        'nc-text':     'rgb(var(--nc-text)     / <alpha-value>)',
        'nc-muted':    'rgb(var(--nc-muted)    / <alpha-value>)',
        'nc-accent':   'rgb(var(--nc-accent)   / <alpha-value>)',
        'nc-border':   'rgb(var(--nc-border)   / <alpha-value>)',
        'nc-success':  'rgb(var(--nc-success)  / <alpha-value>)',
        'nc-warning':  'rgb(var(--nc-warning)  / <alpha-value>)',
        'nc-danger':   'rgb(var(--nc-danger)   / <alpha-value>)',
        /* ── Legacy dark-only palette (backward compat) ── */
        'neuro-bg':      '#0f1117',
        'neuro-surface': '#1a1f2e',
        'neuro-text':    '#e2e8f0',
        'neuro-muted':   '#64748b',
        'neuro-accent':  '#00d4ff',
        'neuro-success': '#22c55e',
        'neuro-warning': '#f59e0b',
        'neuro-border':  '#2a3654',
      },
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        arabic:  ['Cairo', 'system-ui', 'sans-serif'],
      },
      animation: {
        'fade-in':     'fadeIn 0.3s ease-out',
        'slide-up':    'slideUp 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'slide-right': 'slideRight 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
        'pulse-slow':  'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'spin-slow':   'spin 3s linear infinite',
        'glow':        'glow 2s ease-in-out infinite alternate',
      },
      keyframes: {
        fadeIn:     { from: { opacity: 0 },                       to: { opacity: 1 } },
        slideUp:    { from: { opacity: 0, transform: 'translateY(16px)' }, to: { opacity: 1, transform: 'translateY(0)' } },
        slideRight: { from: { opacity: 0, transform: 'translateX(24px)' }, to: { opacity: 1, transform: 'translateX(0)' } },
        glow:       { from: { boxShadow: '0 0 8px rgb(var(--nc-accent)/0.3)' }, to: { boxShadow: '0 0 24px rgb(var(--nc-accent)/0.7)' } },
      },
      backdropBlur: { xs: '2px' },
      boxShadow: {
        'glass':  '0 4px 32px rgba(0,0,0,0.12), inset 0 1px 0 rgba(255,255,255,0.06)',
        'glass-lg': '0 8px 48px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.08)',
        'accent': '0 0 0 3px rgb(var(--nc-accent)/0.25)',
      },
    },
  },
  plugins: [],
}
