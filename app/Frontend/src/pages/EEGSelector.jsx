import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Radio, FileText, ArrowRight, Zap, Brain, BarChart3, Clock,
  Wifi, ChevronDown, ChevronUp, BookOpen, CheckCircle2, AlertTriangle,
  Info, ChevronRight,
} from 'lucide-react'

/* ── Schéma SVG de la tête avec positions 10-20 ── */
function HeadSchema() {
  return (
    <svg viewBox="0 0 280 300" className="w-full max-w-xs mx-auto" aria-label="Schéma placement électrodes">
      <ellipse cx="140" cy="145" rx="100" ry="120" fill="#0a0e1a" stroke="rgba(0,212,255,.3)" strokeWidth="2" />
      <ellipse cx="40"  cy="145" rx="10" ry="18" fill="#0e1420" stroke="rgba(0,212,255,.2)" strokeWidth="1.5" />
      <ellipse cx="240" cy="145" rx="10" ry="18" fill="#0e1420" stroke="rgba(0,212,255,.2)" strokeWidth="1.5" />
      <path d="M 130 30 Q 140 10 150 30" fill="none" stroke="rgba(0,212,255,.2)" strokeWidth="1.5" />
      <line x1="140" y1="25" x2="140" y2="265" stroke="rgba(255,255,255,.06)" strokeWidth="1" strokeDasharray="4,4" />
      <line x1="40"  y1="145" x2="240" y2="145" stroke="rgba(255,255,255,.06)" strokeWidth="1" strokeDasharray="4,4" />

      <circle cx="168" cy="60" r="12" fill="rgba(0,212,255,.18)" stroke="#00d4ff" strokeWidth="2.5" />
      <text x="168" y="65" textAnchor="middle" fill="#00d4ff" fontSize="9" fontWeight="bold" fontFamily="monospace">Fp2</text>

      <circle cx="245" cy="150" r="10" fill="rgba(16,185,129,.12)" stroke="#10b981" strokeWidth="2" />
      <text x="245" y="155" textAnchor="middle" fill="#10b981" fontSize="8" fontWeight="bold" fontFamily="monospace">M2</text>

      <circle cx="35" cy="150" r="10" fill="rgba(245,158,11,.12)" stroke="#f59e0b" strokeWidth="2" />
      <text x="35" y="155" textAnchor="middle" fill="#f59e0b" fontSize="8" fontWeight="bold" fontFamily="monospace">M1</text>

      {[
        { x: 112, y: 60,  label: 'Fp1' },
        { x: 140, y: 48,  label: 'Fpz' },
        { x: 90,  y: 95,  label: 'F7'  },
        { x: 140, y: 95,  label: 'Fz'  },
        { x: 190, y: 95,  label: 'F8'  },
        { x: 140, y: 145, label: 'Cz'  },
        { x: 140, y: 200, label: 'Pz'  },
        { x: 140, y: 248, label: 'Oz'  },
      ].map(({ x, y, label }) => (
        <g key={label}>
          <circle cx={x} cy={y} r="7" fill="rgba(255,255,255,.03)" stroke="rgba(255,255,255,.12)" strokeWidth="1.2" />
          <text x={x} y={y + 4} textAnchor="middle" fill="rgba(255,255,255,.25)" fontSize="7" fontFamily="monospace">{label}</text>
        </g>
      ))}

      <path d="M 168 72 Q 200 100 230 140 Q 240 145 245 150"
        fill="none" stroke="rgba(0,212,255,.4)" strokeWidth="1.5" strokeDasharray="3,3" />
      <path d="M 35 150 Q 30 130 38 115"
        fill="none" stroke="rgba(245,158,11,.4)" strokeWidth="1.5" strokeDasharray="3,3" />

      <rect x="10" y="268" width="260" height="28" rx="5" fill="rgba(255,255,255,.02)" stroke="rgba(255,255,255,.05)" strokeWidth="1" />
      <circle cx="22"  cy="282" r="5" fill="rgba(0,212,255,.3)"   stroke="#00d4ff" strokeWidth="1.5" />
      <text x="31" y="286" fill="rgba(255,255,255,.5)" fontSize="8" fontFamily="monospace">Active</text>
      <circle cx="80"  cy="282" r="5" fill="rgba(16,185,129,.2)"  stroke="#10b981" strokeWidth="1.5" />
      <text x="89" y="286" fill="rgba(255,255,255,.5)" fontSize="8" fontFamily="monospace">Référence</text>
      <circle cx="155" cy="282" r="5" fill="rgba(245,158,11,.2)"  stroke="#f59e0b" strokeWidth="1.5" />
      <text x="164" y="286" fill="rgba(255,255,255,.5)" fontSize="8" fontFamily="monospace">Masse</text>
    </svg>
  )
}

/* ── Schéma du headband AD8232 ── */
function HeadbandDiagram() {
  return (
    <div className="relative w-full aspect-[3/1] max-w-lg mx-auto">
      <svg viewBox="0 0 420 140" className="w-full h-full">
        <rect x="10" y="55" width="400" height="30" rx="15"
          fill="rgba(0,212,255,.06)" stroke="rgba(0,212,255,.25)" strokeWidth="1.5" />

        <rect x="30" y="45" width="40" height="50" rx="8"
          fill="rgba(0,212,255,.12)" stroke="#00d4ff" strokeWidth="2" />
        <text x="50" y="68" textAnchor="middle" fill="#00d4ff" fontSize="9" fontWeight="bold" fontFamily="monospace">Fp2</text>
        <text x="50" y="80" textAnchor="middle" fill="rgba(0,212,255,.6)" fontSize="7" fontFamily="monospace">IN+</text>
        <circle cx="50" cy="92" r="5" fill="rgba(0,212,255,.3)" stroke="#00d4ff" strokeWidth="1.5" />

        <rect x="200" y="45" width="40" height="50" rx="8"
          fill="rgba(16,185,129,.1)" stroke="#10b981" strokeWidth="1.5" />
        <text x="220" y="68" textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="bold" fontFamily="monospace">M2</text>
        <text x="220" y="80" textAnchor="middle" fill="rgba(16,185,129,.6)" fontSize="7" fontFamily="monospace">IN-</text>
        <circle cx="220" cy="92" r="5" fill="rgba(16,185,129,.25)" stroke="#10b981" strokeWidth="1.5" />

        <rect x="360" y="45" width="40" height="50" rx="8"
          fill="rgba(245,158,11,.08)" stroke="#f59e0b" strokeWidth="1.5" />
        <text x="380" y="68" textAnchor="middle" fill="#f59e0b" fontSize="9" fontWeight="bold" fontFamily="monospace">M1</text>
        <text x="380" y="80" textAnchor="middle" fill="rgba(245,158,11,.6)" fontSize="7" fontFamily="monospace">GND</text>
        <circle cx="380" cy="92" r="5" fill="rgba(245,158,11,.2)" stroke="#f59e0b" strokeWidth="1.5" />

        <line x1="70" y1="70" x2="200" y2="70" stroke="rgba(0,212,255,.3)" strokeWidth="1.5" strokeDasharray="4,3" />
        <line x1="240" y1="70" x2="360" y2="70" stroke="rgba(16,185,129,.3)" strokeWidth="1.5" strokeDasharray="4,3" />

        <rect x="280" y="15" width="60" height="25" rx="5"
          fill="rgba(255,255,255,.04)" stroke="rgba(255,255,255,.12)" strokeWidth="1" />
        <text x="310" y="30" textAnchor="middle" fill="rgba(255,255,255,.4)" fontSize="8" fontFamily="monospace">AD8232</text>
        <line x1="310" y1="40" x2="310" y2="55" stroke="rgba(255,255,255,.15)" strokeWidth="1" />

        <rect x="130" y="10" width="70" height="28" rx="5"
          fill="rgba(0,212,255,.06)" stroke="rgba(0,212,255,.2)" strokeWidth="1" />
        <text x="165" y="26" textAnchor="middle" fill="rgba(0,212,255,.5)" fontSize="8" fontFamily="monospace">ESP32</text>
        <line x1="165" y1="38" x2="165" y2="55" stroke="rgba(0,212,255,.2)" strokeWidth="1" />

        <text x="165" y="10" textAnchor="middle" fill="rgba(0,212,255,.3)" fontSize="10" fontFamily="monospace">📶</text>
      </svg>
    </div>
  )
}

/* ── Guide complet intégré ── */
function FullElectrodeGuide({ onStartLive }) {
  const [consent, setConsent] = useState(false)
  const [checked, setChecked] = useState({ c1: false, c2: false, c3: false, c4: false, c5: false })
  const allChecked = Object.values(checked).every(Boolean)

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Intro */}
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-nc-accent text-xs font-mono uppercase tracking-widest">
          <BookOpen className="w-4 h-4" />
          Guide de Pose des Électrodes — NeuroCap v2.1
        </div>
        <p className="text-nc-muted leading-relaxed text-sm max-w-2xl">
          Le système NeuroCap utilise le montage <strong className="text-nc-text">Fp2–M2–M1</strong> conformément au système international
          10-20 (Jasper, 1958). Ce guide décrit la procédure de préparation cutanée et de mise en place
          du headband AD8232 pour garantir un signal EEG de qualité optimale.
        </p>
      </div>

      {/* Schémas */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-nc-text mb-1">Système international 10-20</h3>
          <p className="text-xs text-nc-muted mb-4">Positions standardisées selon Jasper (1958) — vue dorsale</p>
          <HeadSchema />
        </div>
        <div className="card p-6">
          <h3 className="text-sm font-semibold text-nc-text mb-1">Headband NeuroCap — AD8232</h3>
          <p className="text-xs text-nc-muted mb-4">Configuration des 3 électrodes et connexion ESP32</p>
          <HeadbandDiagram />
          <div className="mt-4 space-y-1.5">
            {[
              { color: 'text-nc-accent',   label: 'Fp2 (IN+)', desc: 'Frontal supérieur droit — électrode active' },
              { color: 'text-emerald-400', label: 'M2 (IN−)',  desc: 'Mastoïde derrière oreille droite — référence' },
              { color: 'text-yellow-400',  label: 'M1 (GND)',  desc: 'Mastoïde derrière oreille gauche — masse' },
            ].map(({ color, label, desc }) => (
              <div key={label} className="flex items-start gap-2 text-xs">
                <span className={`font-mono font-bold ${color} shrink-0 w-16`}>{label}</span>
                <span className="text-nc-muted">{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Protocole */}
      <div className="card p-6">
        <h3 className="text-sm font-semibold text-nc-text mb-4 flex items-center gap-2">
          <Zap className="w-4 h-4 text-nc-accent" /> Protocole de préparation cutanée
        </h3>
        <div className="grid sm:grid-cols-2 gap-4">
          {[
            {
              step: '01', title: 'Préparation de la peau',
              desc: "Nettoyez la zone Fp2 (2 cm au-dessus de l'arcade sourcilière droite) et les mastoïdes avec une lingette imbibée d'alcool isopropylique à 70°. Laissez sécher 30 secondes. Une légère abrasion douce avec un abrasif EEG améliore le contact.",
            },
            {
              step: '02', title: 'Application du gel conducteur',
              desc: 'Appliquez une petite quantité de gel électrolytique (type Ten20® ou Signagel®) sur chaque électrode. Le gel doit remplir le bol de l\'électrode sans déborder. Vérifiez que les électrodes sont propres et non oxydées.',
            },
            {
              step: '03', title: 'Mise en place du headband',
              desc: "Positionnez le headband de façon à ce que l'électrode Fp2 soit centrée sur le front, côté droit, à environ 2 cm au-dessus du coin externe de l'œil droit. Les électrodes M1 et M2 doivent reposer sur les apophyses mastoïdes.",
            },
            {
              step: '04', title: 'Vérification de la qualité',
              desc: "L'impédance cible est < 10 kΩ. Dans NeuroCap, la qualité de contact est mesurée par le score CQE (Contact Quality Estimate). Un score > 60% indique un bon contact. La courbe EEG doit montrer un signal stable et non saturé (±150 µV max).",
            },
          ].map(({ step, title, desc }) => (
            <div key={step} className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-nc-accent/15 text-nc-accent text-sm font-bold
                              flex items-center justify-center shrink-0 mt-0.5 font-mono">
                {step}
              </div>
              <div>
                <p className="text-sm font-semibold text-nc-text mb-1">{title}</p>
                <p className="text-xs text-nc-muted leading-relaxed">{desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Précautions */}
      <div className="card p-5 border-yellow-500/20 bg-yellow-500/5">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-yellow-300 mb-2">Précautions importantes</p>
            <ul className="text-xs text-yellow-200/70 space-y-1 list-disc list-inside">
              <li>Ne jamais utiliser cet appareil en présence de lésions cutanées ou d'implants électroniques actifs (pacemaker).</li>
              <li>Ce dispositif est destiné à des fins de recherche et de bien-être uniquement — il ne constitue pas un dispositif médical diagnostic.</li>
              <li>Les électrodes doivent être nettoyées après chaque utilisation à l'alcool isopropylique 70%.</li>
              <li>Ne pas utiliser plus de 60 minutes consécutives pour éviter une irritation cutanée.</li>
              <li>En cas de démangeaisons, brûlures ou inconfort, retirer immédiatement le headband.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Specs techniques */}
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-nc-text mb-4 flex items-center gap-2">
          <Info className="w-4 h-4 text-nc-muted" /> Spécifications du pipeline de traitement
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Canal actif',    value: 'Fp2 (frontal)'     },
            { label: 'Référence',      value: 'M2 (mastoïde D)'   },
            { label: 'Fréquence',      value: '250 Hz'            },
            { label: 'Filtre Golden',  value: '1–45 Hz (IIR)'     },
            { label: 'Taille époque',  value: '4s (1000 samples)' },
            { label: 'Overlap',        value: '75% (250 samples)' },
            { label: 'Modèle IA',      value: 'EEGNet Conv2d'     },
            { label: 'Stratégie',      value: 'DL + TL (FULL)'   },
          ].map(({ label, value }) => (
            <div key={label} className="bg-nc-surface2/50 rounded-xl p-3">
              <p className="text-[10px] text-nc-muted uppercase tracking-wide">{label}</p>
              <p className="text-xs font-mono font-semibold text-nc-text mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Checklist */}
      <div className="card p-6">
        <h3 className="text-sm font-semibold text-nc-text mb-4">Checklist avant de commencer la session</h3>
        <div className="space-y-3">
          {[
            { id: 'c1', text: 'La peau est propre et légèrement abrasée aux zones de contact.' },
            { id: 'c2', text: 'Le gel conducteur est appliqué sur les 3 électrodes.' },
            { id: 'c3', text: 'Le headband est positionné correctement : Fp2 sur le front droit, M1/M2 sur les mastoïdes.' },
            { id: 'c4', text: "L'ESP32 est allumé et le câble USB/batterie est connecté." },
            { id: 'c5', text: "Je suis dans un environnement calme, éloigné des sources d'interférence électromagnétique." },
          ].map(({ id, text }) => (
            <label key={id} className="flex items-start gap-3 cursor-pointer group">
              <div className="relative shrink-0 mt-0.5">
                <input type="checkbox" className="sr-only"
                  checked={checked[id]}
                  onChange={e => setChecked(prev => ({ ...prev, [id]: e.target.checked }))} />
                <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all
                  ${checked[id] ? 'bg-nc-accent border-nc-accent' : 'border-nc-border group-hover:border-nc-accent/50'}`}>
                  {checked[id] && <CheckCircle2 className="w-3.5 h-3.5 text-nc-bg" />}
                </div>
              </div>
              <span className={`text-sm leading-relaxed transition-colors
                ${checked[id] ? 'text-nc-text line-through opacity-60' : 'text-nc-muted'}`}>
                {text}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Consentement */}
      <div className="card p-6 border-nc-accent/20 bg-nc-accent/5">
        <h3 className="text-sm font-semibold text-nc-text mb-3">Consentement éclairé</h3>
        <p className="text-xs text-nc-muted leading-relaxed mb-4">
          En cochant la case ci-dessous, je déclare avoir lu et compris ce guide de pose des électrodes.
          Je confirme que je n'ai aucune contre-indication à l'utilisation de ce dispositif (lésion cutanée,
          implant électronique actif, épilepsie photosensible). Je comprends que NeuroCap est un outil
          de recherche et de bien-être, et non un dispositif médical diagnostic. Les données EEG collectées
          sont stockées de façon chiffrée et pseudonymisée conformément au RGPD.
        </p>
        <label className="flex items-start gap-3 cursor-pointer group">
          <div className="relative shrink-0 mt-0.5">
            <input type="checkbox" className="sr-only"
              checked={consent}
              onChange={e => setConsent(e.target.checked)} />
            <div className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-all
              ${consent ? 'bg-nc-accent border-nc-accent' : 'border-nc-border group-hover:border-nc-accent/50'}`}>
              {consent && <CheckCircle2 className="w-3.5 h-3.5 text-nc-bg" />}
            </div>
          </div>
          <span className={`text-sm font-medium leading-relaxed
            ${consent ? 'text-nc-accent' : 'text-nc-text'}`}>
            J'ai lu et compris ce guide. Je consens à la collecte de mes données EEG dans le cadre
            du protocole NeuroCap et aux conditions décrites ci-dessus.
          </span>
        </label>
      </div>

      {/* CTA */}
      <div className="flex justify-end">
        <button
          onClick={onStartLive}
          disabled={!consent || !allChecked}
          className="btn-primary flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          J'ai compris — démarrer le Live EEG
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>
      {(!consent || !allChecked) && (
        <p className="text-xs text-nc-muted text-center pb-2">
          Complétez la checklist et donnez votre consentement pour accéder au Live EEG.
        </p>
      )}
    </div>
  )
}

export default function EEGSelector() {
  const navigate = useNavigate()
  const [showGuide, setShowGuide] = useState(false)

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-12 space-y-10">

      {/* ── En-tête ── */}
      <div className="text-center space-y-3">
        <div className="w-16 h-16 rounded-3xl bg-nc-accent/15 flex items-center justify-center mx-auto">
          <Brain className="w-8 h-8 text-nc-accent" />
        </div>
        <h1 className="text-3xl font-bold text-nc-text">Analyse EEG</h1>
        <p className="text-base text-nc-muted max-w-lg mx-auto">
          Choisissez votre mode d'analyse : signal temps réel avec le casque NeuroCap,
          ou classification d'un fichier EEG existant.
        </p>
      </div>

      {/* ── Cartes de choix ── */}
      <div className="grid md:grid-cols-2 gap-6">

        {/* Carte 1 — Live Hardware */}
        <button
          onClick={() => navigate('/eeg-live')}
          className="card p-8 text-start space-y-5 border-nc-border hover:border-nc-accent/40
                     hover:bg-nc-accent/5 transition-all duration-200 group cursor-pointer"
        >
          <div className="w-14 h-14 rounded-2xl bg-nc-accent/15 flex items-center justify-center
                          group-hover:scale-110 transition-transform duration-200">
            <Radio className="w-7 h-7 text-nc-accent" />
          </div>

          <div>
            <h2 className="text-xl font-bold text-nc-text">EEG Temps Réel</h2>
            <p className="text-sm text-nc-muted mt-1">Casque NeuroCap · ESP32 · AD8232</p>
          </div>

          <ul className="space-y-2.5">
            {[
              [Zap,      'Signal en direct à 250 Hz'],
              [Wifi,     'Configuration WiFi ESP32 intégrée'],
              [Brain,    'Classification cognitif automatique'],
              [BarChart3,'63 features FeatEng + DSP v8.0'],
              [Clock,    'Enregistrement CSV session'],
            ].map(([Icon, text]) => (
              <li key={text} className="flex items-center gap-2 text-sm text-nc-muted">
                <Icon className="w-4 h-4 text-nc-accent shrink-0" />
                {text}
              </li>
            ))}
          </ul>

          <div className="flex items-center gap-2 text-nc-accent font-semibold text-sm pt-1">
            Démarrer la session
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </button>

        {/* Carte 2 — Analyse fichier */}
        <button
          onClick={() => navigate('/eeg-file')}
          className="card p-8 text-start space-y-5 border-nc-border hover:border-purple-400/40
                     hover:bg-purple-500/5 transition-all duration-200 group cursor-pointer"
        >
          <div className="w-14 h-14 rounded-2xl bg-purple-500/15 flex items-center justify-center
                          group-hover:scale-110 transition-transform duration-200">
            <FileText className="w-7 h-7 text-purple-400" />
          </div>

          <div>
            <h2 className="text-xl font-bold text-nc-text">Analyser un fichier</h2>
            <p className="text-sm text-nc-muted mt-1">EDF · CSV · TXT — analyse hors ligne</p>
          </div>

          <ul className="space-y-2.5">
            {[
              [FileText,  'Formats EDF, CSV et TXT'],
              [Brain,     'Classification LightGBM epoch par epoch'],
              [BarChart3, 'Résumé de session complet'],
              [Zap,       'Rééchantillonnage automatique à 250 Hz'],
              [Clock,     'Résultats instantanés sans matériel'],
            ].map(([Icon, text]) => (
              <li key={text} className="flex items-center gap-2 text-sm text-nc-muted">
                <Icon className="w-4 h-4 text-purple-400 shrink-0" />
                {text}
              </li>
            ))}
          </ul>

          <div className="flex items-center gap-2 text-purple-400 font-semibold text-sm pt-1">
            Choisir un fichier
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </div>
        </button>
      </div>

      {/* ── Guide électrodes expandable (complet) ── */}
      <div className="space-y-3">
        <button
          onClick={() => setShowGuide(v => !v)}
          className="w-full card p-4 flex items-center gap-3 hover:border-nc-accent/40 hover:bg-nc-accent/5 transition-all duration-200 group"
        >
          <div className="w-9 h-9 rounded-xl bg-nc-accent/12 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
            <BookOpen className="w-4 h-4 text-nc-accent" />
          </div>
          <div className="flex-1 text-start">
            <p className="text-sm font-semibold text-nc-text">Guide de pose des électrodes</p>
            <p className="text-xs text-nc-muted mt-0.5">Première utilisation ? Suivez le protocole complet avant de démarrer.</p>
          </div>
          <div className="flex items-center gap-2 text-nc-accent text-xs font-medium shrink-0">
            {showGuide ? 'Masquer' : 'Afficher'}
            {showGuide ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        </button>

        {showGuide && (
          <FullElectrodeGuide onStartLive={() => navigate('/eeg-live')} />
        )}
      </div>

      {/* ── Specs techniques ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { label: 'Fréquence',    value: '250 Hz',     sub: 'Fp2 canal unique'   },
          { label: 'Époque',       value: '4 s',        sub: 'Overlap 75%'        },
          { label: 'Modèle',       value: 'EEGNet',     sub: 'Conv2d monocanal'   },
          { label: 'Stratégie',    value: 'DL + TL',   sub: 'AUC 0.75 / 0.61'   },
        ].map(({ label, value, sub }) => (
          <div key={label} className="card p-4 text-center">
            <p className="text-lg font-bold font-mono text-nc-accent">{value}</p>
            <p className="text-xs text-nc-text font-medium mt-0.5">{label}</p>
            <p className="text-[10px] text-nc-muted">{sub}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
