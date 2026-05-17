/**
 * NeuroCap — Page d'accueil publique
 *
 * Accessible SANS authentification.
 * Montre la plateforme mais sans les sections qui nécessitent un compte.
 * Les boutons "Se connecter" / "Créer un compte" mènent vers /login et /register.
 */
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { useTheme } from '../context/ThemeContext'
import {
  Brain, Activity, Cpu, ShieldCheck, Zap, BarChart2,
  LogIn, UserPlus, Sun, Moon, Monitor, Globe, ChevronDown, ArrowRight,
} from 'lucide-react'
import { useState } from 'react'

const THEMES = [
  { key: 'auto',  Icon: Monitor },
  { key: 'light', Icon: Sun     },
  { key: 'dark',  Icon: Moon    },
]
const LANGS = [
  { key: 'fr', label: 'FR', flag: '🇫🇷' },
  { key: 'en', label: 'EN', flag: '🇬🇧' },
  { key: 'ar', label: 'AR', flag: '🇲🇦' },
]

/* ── Top-bar (theme + language — identique à Login/Register) ── */
function TopBar() {
  const { theme, setTheme } = useTheme()
  const { i18n } = useTranslation()
  const [langOpen, setLangOpen] = useState(false)
  const ThemeIcon = THEMES.find(t => t.key === theme)?.Icon ?? Monitor
  const cycleTheme = () => {
    const idx = THEMES.findIndex(t => t.key === theme)
    setTheme(THEMES[(idx + 1) % THEMES.length].key)
  }
  return (
    <header className="fixed top-0 inset-x-0 z-40 flex items-center justify-between px-6 py-3
                       bg-nc-bg/80 backdrop-blur-md border-b border-nc-border">
      {/* Brand */}
      <div className="flex items-center gap-2.5">
        <div className="w-8 h-8 rounded-xl flex items-center justify-center"
             style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.5))' }}>
          <Brain className="w-4 h-4 text-white" />
        </div>
        <span className="font-bold text-nc-text text-sm tracking-wide">NeuroCap</span>
      </div>

      {/* Controls */}
      <div className="flex items-center gap-2">
        {/* Theme */}
        <button onClick={cycleTheme}
                className="p-2 rounded-xl bg-nc-surface border border-nc-border text-nc-muted hover:text-nc-accent transition-all">
          <ThemeIcon className="w-4 h-4" />
        </button>

        {/* Language */}
        <div className="relative">
          <button onClick={() => setLangOpen(o => !o)}
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-nc-surface border border-nc-border text-nc-muted hover:text-nc-accent transition-all">
            <Globe className="w-4 h-4" />
            <span className="text-xs font-semibold uppercase">{i18n.language}</span>
            <ChevronDown className="w-3 h-3" />
          </button>
          {langOpen && (
            <div className="absolute top-full mt-2 end-0 bg-nc-surface border border-nc-border rounded-2xl shadow-glass-lg overflow-hidden z-50 animate-fade-in">
              {LANGS.map(({ key, label, flag }) => (
                <button key={key}
                        onClick={() => { i18n.changeLanguage(key); setLangOpen(false) }}
                        className={`flex items-center gap-3 w-full px-4 py-2.5 text-sm transition-colors
                                    ${i18n.language === key ? 'text-nc-accent bg-nc-accent/10 font-semibold' : 'text-nc-text hover:bg-nc-surface2'}`}>
                  <span>{flag}</span>{label}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Auth CTAs */}
        <Link to="/login"
              className="hidden sm:flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium
                         text-nc-muted hover:text-nc-accent border border-nc-border hover:border-nc-accent transition-all">
          <LogIn className="w-4 h-4" />
          <span>Connexion</span>
        </Link>
        <Link to="/register"
              className="hidden sm:flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-medium btn-primary">
          <UserPlus className="w-4 h-4" />
          <span>Inscription</span>
        </Link>
      </div>
    </header>
  )
}

/* ── Animated EEG wave SVG ── */
function EEGWave({ className = '' }) {
  return (
    <svg viewBox="0 0 800 120" className={className} fill="none" preserveAspectRatio="none">
      <polyline
        points="0,60 40,60 60,20 80,100 100,40 120,80 140,60 180,60 200,30 220,90 240,50 260,70 280,60 320,60 340,25 360,95 380,45 400,75 420,60 460,60 480,35 500,85 520,50 540,70 560,60 600,60 620,20 640,100 660,40 680,80 700,60 760,60 780,45 800,60"
        stroke="rgb(var(--nc-accent))" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
        className="animate-pulse-slow"
      />
    </svg>
  )
}

/* ── Feature card ── */
function FeatureCard({ icon: Icon, title, desc, color }) {
  return (
    <div className="card p-6 flex flex-col gap-4 hover:border-nc-accent/40 transition-colors group">
      <div className="w-12 h-12 rounded-2xl flex items-center justify-center"
           style={{ background: `${color}18` }}>
        <Icon className="w-6 h-6" style={{ color }} />
      </div>
      <div>
        <h3 className="font-semibold text-nc-text mb-1 group-hover:text-nc-accent transition-colors">{title}</h3>
        <p className="text-sm text-nc-muted leading-relaxed">{desc}</p>
      </div>
    </div>
  )
}

/* ── Demo metric chip ── */
function MetricChip({ label, value, unit }) {
  return (
    <div className="card-glass px-4 py-3 flex flex-col gap-0.5 min-w-[100px]">
      <span className="text-xs text-nc-muted">{label}</span>
      <span className="text-xl font-bold text-nc-accent">{value}<span className="text-sm font-normal text-nc-muted ml-0.5">{unit}</span></span>
    </div>
  )
}

export default function Landing() {
  const { t } = useTranslation()

  const FEATURES = [
    {
      icon: Activity,
      title: 'Signal EEG temps réel',
      desc:  'Acquisition mono-canal Fp2 à 250 Hz via AD8232 + ESP32. Visualisation et analyse instantanées.',
      color: 'rgb(var(--nc-accent))',
    },
    {
      icon: Cpu,
      title: 'IA adaptive (EEGNet)',
      desc:  'Classificateur profond EEGNet + moteur EWMA adaptatif basé sur Mou et al. 2024.',
      color: 'rgb(var(--nc-success))',
    },
    {
      icon: Zap,
      title: 'Neurofeedback multimodal',
      desc:  'Retours visuels, sonores et ludiques. Difficulté auto-ajustée selon votre profil cognitif.',
      color: 'rgb(var(--nc-warning))',
    },
    {
      icon: BarChart2,
      title: 'Rapports & historique',
      desc:  "Visualisez votre progression. Export CSV, score de session, TBR, indice d'engagement.",
      color: 'rgb(var(--nc-accent))',
    },
    {
      icon: ShieldCheck,
      title: 'Données sécurisées',
      desc:  'Chiffrement JWT, protection anti-brute force, hébergement Supabase conforme RGPD.',
      color: 'rgb(var(--nc-success))',
    },
    {
      icon: Brain,
      title: 'Assistant IA cognitif',
      desc:  'RAG conversationnel pour comprendre vos résultats EEG et recevoir des conseils personnalisés.',
      color: 'rgb(var(--nc-warning))',
    },
  ]

  return (
    <div className="min-h-screen bg-nc-bg text-nc-text">
      <TopBar />

      {/* ── Hero ── */}
      <section className="relative pt-28 pb-20 px-6 overflow-hidden">
        {/* Background glows */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <div className="absolute -top-32 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full opacity-20"
               style={{ background: 'radial-gradient(circle, rgb(var(--nc-accent)) 0%, transparent 70%)' }} />
        </div>

        {/* EEG wave decoration */}
        <div className="absolute bottom-0 inset-x-0 h-20 opacity-30 pointer-events-none">
          <EEGWave className="w-full h-full" />
        </div>

        <div className="relative max-w-3xl mx-auto text-center space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-nc-accent/10 border border-nc-accent/20 text-nc-accent text-xs font-semibold uppercase tracking-widest">
            <Activity className="w-3.5 h-3.5" />
            Neurofeedback EEG Adaptatif
          </div>

          {/* Title */}
          <h1 className="text-4xl sm:text-5xl font-extrabold text-nc-text leading-tight">
            Entraînez votre{' '}
            <span className="text-nc-accent">cerveau</span>{' '}
            avec NeuroCap
          </h1>

          <p className="text-lg text-nc-muted max-w-xl mx-auto leading-relaxed">
            Plateforme professionnelle de neurofeedback EEG temps réel.
            Concentrez-vous mieux, gérez votre stress et suivez votre progression cognitive.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <Link to="/register"
                  className="btn-primary flex items-center gap-2 px-6 py-3 text-base">
              <UserPlus className="w-5 h-5" />
              Créer un compte gratuit
              <ArrowRight className="w-4 h-4" />
            </Link>
            <Link to="/login"
                  className="flex items-center gap-2 px-6 py-3 text-base rounded-xl border border-nc-border
                             text-nc-muted hover:text-nc-accent hover:border-nc-accent transition-all">
              <LogIn className="w-5 h-5" />
              Déjà inscrit ? Se connecter
            </Link>
          </div>

          {/* Live demo metrics — read-only, pas d'authentification requise */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-6">
            <MetricChip label="Fréquence"    value="250"  unit="Hz" />
            <MetricChip label="Latence"      value="< 2"  unit="s"  />
            <MetricChip label="Précision IA" value="82"   unit="%"  />
            <MetricChip label="Protocoles"   value="4"    unit="niveaux" />
          </div>
        </div>
      </section>

      {/* ── Features ── */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold text-nc-text">Tout ce dont vous avez besoin</h2>
            <p className="text-nc-muted mt-2">
              Une suite complète pour le neurofeedback clinique et la recherche cognitive.
            </p>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {FEATURES.map((f) => (
              <FeatureCard key={f.title} {...f} />
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA bottom ── */}
      <section className="py-16 px-6">
        <div className="max-w-2xl mx-auto text-center space-y-5">
          <h2 className="text-2xl font-bold text-nc-text">
            Prêt à commencer votre entraînement ?
          </h2>
          <p className="text-nc-muted">
            Créez votre compte en moins de 30 secondes.
            Aucune carte bancaire requise.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link to="/register" className="btn-primary flex items-center gap-2 px-8 py-3 text-base">
              <UserPlus className="w-5 h-5" />
              Commencer maintenant
            </Link>
            <Link to="/login" className="text-sm text-nc-muted hover:text-nc-accent transition-colors">
              J'ai déjà un compte →
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ── */}
      <footer className="border-t border-nc-border py-6 px-6 text-center">
        <p className="text-xs text-nc-muted/60">
          NeuroCap · Easy Medical Device · 2026 · CdC conforme AD8232 + ESP32
        </p>
      </footer>
    </div>
  )
}
