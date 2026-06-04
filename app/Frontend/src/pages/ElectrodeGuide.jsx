import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle2, AlertTriangle, ChevronRight, BookOpen, Zap, Info } from 'lucide-react'

/* ── Schéma SVG de la tête avec positions 10-20 ────────────────────────────── */
function HeadSchema() {
  return (
    <svg viewBox="0 0 280 300" className="w-full max-w-xs mx-auto" aria-label="Schéma placement électrodes">
      {/* Tête */}
      <ellipse cx="140" cy="145" rx="100" ry="120" fill="#0a0e1a" stroke="rgba(0,212,255,.3)" strokeWidth="2" />
      {/* Oreilles */}
      <ellipse cx="40"  cy="145" rx="10" ry="18" fill="#0e1420" stroke="rgba(0,212,255,.2)" strokeWidth="1.5" />
      <ellipse cx="240" cy="145" rx="10" ry="18" fill="#0e1420" stroke="rgba(0,212,255,.2)" strokeWidth="1.5" />
      {/* Nez */}
      <path d="M 130 30 Q 140 10 150 30" fill="none" stroke="rgba(0,212,255,.2)" strokeWidth="1.5" />
      {/* Croix centrale */}
      <line x1="140" y1="25" x2="140" y2="265" stroke="rgba(255,255,255,.06)" strokeWidth="1" strokeDasharray="4,4" />
      <line x1="40"  y1="145" x2="240" y2="145" stroke="rgba(255,255,255,.06)" strokeWidth="1" strokeDasharray="4,4" />

      {/* ── Électrodes principales ── */}
      {/* Fp2 — électrode active (front droit) */}
      <circle cx="168" cy="60" r="12" fill="rgba(0,212,255,.18)" stroke="#00d4ff" strokeWidth="2.5" />
      <text x="168" y="65" textAnchor="middle" fill="#00d4ff" fontSize="9" fontWeight="bold" fontFamily="monospace">Fp2</text>

      {/* M2 — mastoïde droite (référence) */}
      <circle cx="245" cy="150" r="10" fill="rgba(16,185,129,.12)" stroke="#10b981" strokeWidth="2" />
      <text x="245" y="155" textAnchor="middle" fill="#10b981" fontSize="8" fontWeight="bold" fontFamily="monospace">M2</text>

      {/* M1 — mastoïde gauche (masse) */}
      <circle cx="35" cy="150" r="10" fill="rgba(245,158,11,.12)" stroke="#f59e0b" strokeWidth="2" />
      <text x="35" y="155" textAnchor="middle" fill="#f59e0b" fontSize="8" fontWeight="bold" fontFamily="monospace">M1</text>

      {/* Autres positions (référence visuelle) */}
      {[
        { x: 112, y: 60,  label: 'Fp1' },
        { x: 140, y: 48,  label: 'Fpz' },
        { x: 90,  cy: 90, label: 'F7',  cx: 90, y: 95 },
        { x: 140, y: 95,  label: 'Fz'  },
        { x: 190, y: 90,  label: 'F8',  cx: 190 },
        { x: 140, y: 145, label: 'Cz'  },
        { x: 140, y: 200, label: 'Pz'  },
        { x: 140, y: 248, label: 'Oz'  },
      ].map(({ x, y, label }) => (
        <g key={label}>
          <circle cx={x} cy={y} r="7" fill="rgba(255,255,255,.03)" stroke="rgba(255,255,255,.12)" strokeWidth="1.2" />
          <text x={x} y={y + 4} textAnchor="middle" fill="rgba(255,255,255,.25)" fontSize="7" fontFamily="monospace">{label}</text>
        </g>
      ))}

      {/* Fil de connexion Fp2 → headband */}
      <path d="M 168 72 Q 200 100 230 140 Q 240 145 245 150"
        fill="none" stroke="rgba(0,212,255,.4)" strokeWidth="1.5" strokeDasharray="3,3" />
      <path d="M 35 150 Q 30 130 38 115"
        fill="none" stroke="rgba(245,158,11,.4)" strokeWidth="1.5" strokeDasharray="3,3" />

      {/* Légende */}
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

/* ── Schéma du headband AD8232 ─────────────────────────────────────────────── */
function HeadbandDiagram() {
  return (
    <div className="relative w-full aspect-[3/1] max-w-lg mx-auto">
      <svg viewBox="0 0 420 140" className="w-full h-full">
        {/* Bandeau */}
        <rect x="10" y="55" width="400" height="30" rx="15"
          fill="rgba(0,212,255,.06)" stroke="rgba(0,212,255,.25)" strokeWidth="1.5" />

        {/* Électrode Fp2 (front gauche du headband = front droit de la tête) */}
        <rect x="30" y="45" width="40" height="50" rx="8"
          fill="rgba(0,212,255,.12)" stroke="#00d4ff" strokeWidth="2" />
        <text x="50" y="68" textAnchor="middle" fill="#00d4ff" fontSize="9" fontWeight="bold" fontFamily="monospace">Fp2</text>
        <text x="50" y="80" textAnchor="middle" fill="rgba(0,212,255,.6)" fontSize="7" fontFamily="monospace">IN+</text>
        <circle cx="50" cy="92" r="5" fill="rgba(0,212,255,.3)" stroke="#00d4ff" strokeWidth="1.5" />

        {/* Électrode M2 (mastoïde droite = derrière l'oreille droite) */}
        <rect x="200" y="45" width="40" height="50" rx="8"
          fill="rgba(16,185,129,.1)" stroke="#10b981" strokeWidth="1.5" />
        <text x="220" y="68" textAnchor="middle" fill="#10b981" fontSize="9" fontWeight="bold" fontFamily="monospace">M2</text>
        <text x="220" y="80" textAnchor="middle" fill="rgba(16,185,129,.6)" fontSize="7" fontFamily="monospace">IN-</text>
        <circle cx="220" cy="92" r="5" fill="rgba(16,185,129,.25)" stroke="#10b981" strokeWidth="1.5" />

        {/* Électrode M1 (mastoïde gauche) */}
        <rect x="360" y="45" width="40" height="50" rx="8"
          fill="rgba(245,158,11,.08)" stroke="#f59e0b" strokeWidth="1.5" />
        <text x="380" y="68" textAnchor="middle" fill="#f59e0b" fontSize="9" fontWeight="bold" fontFamily="monospace">M1</text>
        <text x="380" y="80" textAnchor="middle" fill="rgba(245,158,11,.6)" fontSize="7" fontFamily="monospace">GND</text>
        <circle cx="380" cy="92" r="5" fill="rgba(245,158,11,.2)" stroke="#f59e0b" strokeWidth="1.5" />

        {/* Fils */}
        <line x1="70" y1="70" x2="200" y2="70" stroke="rgba(0,212,255,.3)" strokeWidth="1.5" strokeDasharray="4,3" />
        <line x1="240" y1="70" x2="360" y2="70" stroke="rgba(16,185,129,.3)" strokeWidth="1.5" strokeDasharray="4,3" />

        {/* AD8232 module */}
        <rect x="280" y="15" width="60" height="25" rx="5"
          fill="rgba(255,255,255,.04)" stroke="rgba(255,255,255,.12)" strokeWidth="1" />
        <text x="310" y="30" textAnchor="middle" fill="rgba(255,255,255,.4)" fontSize="8" fontFamily="monospace">AD8232</text>
        <line x1="310" y1="40" x2="310" y2="55" stroke="rgba(255,255,255,.15)" strokeWidth="1" />

        {/* ESP32 */}
        <rect x="130" y="10" width="70" height="28" rx="5"
          fill="rgba(0,212,255,.06)" stroke="rgba(0,212,255,.2)" strokeWidth="1" />
        <text x="165" y="26" textAnchor="middle" fill="rgba(0,212,255,.5)" fontSize="8" fontFamily="monospace">ESP32</text>
        <line x1="165" y1="38" x2="165" y2="55" stroke="rgba(0,212,255,.2)" strokeWidth="1" />

        {/* WiFi symbol */}
        <text x="165" y="10" textAnchor="middle" fill="rgba(0,212,255,.3)" fontSize="10" fontFamily="monospace">📶</text>
      </svg>
    </div>
  )
}

/* ── Page principale ─────────────────────────────────────────────────────────── */
export default function ElectrodeGuide({ onComplete, onSkip } = {}) {
  const navigate  = useNavigate()
  const [consent, setConsent] = useState(false)
  const [checked, setChecked] = useState({
    c1: false, c2: false, c3: false, c4: false, c5: false,
  })

  const allChecked = Object.values(checked).every(Boolean)

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 py-8 space-y-8">

      {/* ── En-tête scientifique ── */}
      <div className="space-y-2">
        <div className="flex items-center gap-2 text-nc-accent text-xs font-mono uppercase tracking-widest">
          <BookOpen className="w-4 h-4" />
          Guide de Pose des Électrodes — NeuroCap v2.1
        </div>
        <h1 className="text-3xl font-bold text-nc-text">
          Placement des Électrodes EEG
        </h1>
        <p className="text-nc-muted leading-relaxed max-w-2xl">
          Le système NeuroCap utilise le montage <strong>Fp2–M2–M1</strong> conformément au système international
          10-20 (Jasper, 1958). Ce guide décrit la procédure de préparation cutanée et de mise en place
          du headband AD8232 pour garantir un signal EEG de qualité optimale.
        </p>
      </div>

      {/* ── Schéma tête + headband ── */}
      <div className="grid md:grid-cols-2 gap-6">
        <div className="card p-6">
          <h2 className="text-sm font-semibold text-nc-text mb-1">
            Système international 10-20
          </h2>
          <p className="text-xs text-nc-muted mb-4">
            Positions standardisées selon Jasper (1958) — vue dorsale
          </p>
          <HeadSchema />
        </div>

        <div className="card p-6">
          <h2 className="text-sm font-semibold text-nc-text mb-1">
            Headband NeuroCap — AD8232
          </h2>
          <p className="text-xs text-nc-muted mb-4">
            Configuration des 3 électrodes et connexion ESP32
          </p>
          <HeadbandDiagram />
          <div className="mt-4 space-y-1.5">
            {[
              { color: 'text-nc-accent',    label: 'Fp2 (IN+)',  desc: 'Frontal supérieur droit — électrode active' },
              { color: 'text-emerald-400',  label: 'M2 (IN−)',   desc: 'Mastoïde derrière oreille droite — référence' },
              { color: 'text-yellow-400',   label: 'M1 (GND)',   desc: 'Mastoïde derrière oreille gauche — masse' },
            ].map(({ color, label, desc }) => (
              <div key={label} className="flex items-start gap-2 text-xs">
                <span className={`font-mono font-bold ${color} shrink-0 w-16`}>{label}</span>
                <span className="text-nc-muted">{desc}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Protocole de préparation ── */}
      <div className="card p-6">
        <h2 className="text-sm font-semibold text-nc-text mb-4 flex items-center gap-2">
          <Zap className="w-4 h-4 text-nc-accent" /> Protocole de préparation cutanée
        </h2>
        <div className="grid sm:grid-cols-2 gap-4">
          {[
            {
              step: '01', title: 'Préparation de la peau',
              desc: 'Nettoyez la zone Fp2 (2 cm au-dessus de l\'arcade sourcilière droite) et les mastoïdes avec une lingette imbibée d\'alcool isopropylique à 70°. Laissez sécher 30 secondes. Une légère abrasion douce avec un abrasif EEG améliore le contact.',
            },
            {
              step: '02', title: 'Application du gel conducteur',
              desc: 'Appliquez une petite quantité de gel électrolytique (type Ten20® ou Signagel®) sur chaque électrode. Le gel doit remplir le bol de l\'électrode sans déborder. Vérifiez que les électrodes sont propres et non oxydées.',
            },
            {
              step: '03', title: 'Mise en place du headband',
              desc: 'Positionnez le headband de façon à ce que l\'électrode Fp2 soit centrée sur le front, côté droit, à environ 2 cm au-dessus du coin externe de l\'œil droit. Les électrodes M1 et M2 doivent reposer sur les apophyses mastoïdes.',
            },
            {
              step: '04', title: 'Vérification de la qualité',
              desc: 'L\'impédance cible est < 10 kΩ. Dans NeuroCap, la qualité de contact est mesurée par le score CQE (Contact Quality Estimate). Un score > 60% indique un bon contact. La courbe EEG doit montrer un signal stable et non saturé (±150 µV max).',
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

      {/* ── Précautions ── */}
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

      {/* ── Spécifications techniques ── */}
      <div className="card p-5">
        <h2 className="text-sm font-semibold text-nc-text mb-4 flex items-center gap-2">
          <Info className="w-4 h-4 text-nc-muted" /> Spécifications du pipeline de traitement
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: 'Canal actif',        value: 'Fp2 (frontal)' },
            { label: 'Référence',          value: 'M2 (mastoïde D)' },
            { label: 'Fréquence',          value: '250 Hz' },
            { label: 'Filtre Golden',      value: '1–45 Hz (IIR)' },
            { label: 'Taille époque',      value: '4s (1000 samples)' },
            { label: 'Overlap',            value: '75% (250 samples)' },
            { label: 'Features ML',        value: '63 (LightGBM LOSO)' },
            { label: 'Classifieur',        value: 'Z-score individuel' },
          ].map(({ label, value }) => (
            <div key={label} className="bg-nc-surface2/50 rounded-xl p-3">
              <p className="text-[10px] text-nc-muted uppercase tracking-wide">{label}</p>
              <p className="text-xs font-mono font-semibold text-nc-text mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {/* ── Checklist avant démarrage ── */}
      <div className="card p-6">
        <h2 className="text-sm font-semibold text-nc-text mb-4">
          Checklist avant de commencer la session
        </h2>
        <div className="space-y-3">
          {[
            { id: 'c1', text: 'La peau est propre et légèrement abrasée aux zones de contact.' },
            { id: 'c2', text: 'Le gel conducteur est appliqué sur les 3 électrodes.' },
            { id: 'c3', text: 'Le headband est positionné correctement : Fp2 sur le front droit, M1/M2 sur les mastoïdes.' },
            { id: 'c4', text: 'L\'ESP32 est allumé et le câble USB/batterie est connecté.' },
            { id: 'c5', text: 'Je suis dans un environnement calme, éloigné des sources d\'interférence électromagnétique.' },
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

      {/* ── Consentement éclairé ── */}
      <div className="card p-6 border-nc-accent/20 bg-nc-accent/5">
        <h2 className="text-sm font-semibold text-nc-text mb-3">Consentement éclairé</h2>
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

      {/* ── Bouton accès EEG Live ── */}
      <div className="flex justify-end gap-3">
        {onSkip ? (
          <button onClick={onSkip} className="btn-ghost px-6 py-3 rounded-xl text-sm">
            Passer →
          </button>
        ) : (
          <button onClick={() => navigate('/dashboard')} className="btn-ghost px-6 py-3 rounded-xl text-sm">
            Retour au tableau de bord
          </button>
        )}
        <button
          onClick={() => onComplete ? onComplete() : navigate('/eeg-live')}
          disabled={!consent || !allChecked}
          className="btn-primary flex items-center gap-2 px-6 py-3 rounded-xl text-sm font-semibold
                     disabled:opacity-40 disabled:cursor-not-allowed"
        >
          J'ai compris — continuer
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

      {!consent && (
        <p className="text-xs text-nc-muted text-center pb-2">
          Complétez la checklist et donnez votre consentement pour accéder au Live EEG.
        </p>
      )}
    </div>
  )
}
