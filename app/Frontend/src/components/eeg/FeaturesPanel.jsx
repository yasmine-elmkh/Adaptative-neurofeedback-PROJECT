import { useState, createContext, useContext } from 'react'
import { useTheme } from '../../context/ThemeContext'

const f4 = v => typeof v === 'number' ? v.toFixed(4) : '—'
const f3 = v => typeof v === 'number' ? v.toFixed(3) : '—'
const f1 = v => typeof v === 'number' ? v.toFixed(1) : '—'

// ── Thème clair / sombre ─────────────────────────────────────────────────────
const T_DARK = {
  groupBg:          '#0a0e18',
  groupBorder:      'rgba(255,255,255,.05)',
  cellBg:           'rgba(255,255,255,.02)',
  cellBorder:       'rgba(255,255,255,.04)',
  cellWarnBorder:   'rgba(245,166,35,.15)',
  cellAccentBorder: 'rgba(0,229,176,.12)',
  cellDefaultClr:   '#c9d8e8',
  labelClr:         '#4a5a6e',
  descClr:          '#3a4a5e',
  bodyClr:          '#6a7a8e',
  toggleBg:         'rgba(255,255,255,.03)',
  progressTrack:    'rgba(255,255,255,.06)',
  btnActiveClr:     '#00e5b0',
  btnActiveBg:      'rgba(0,229,176,.12)',
  btnActiveBorder:  'rgba(0,229,176,.3)',
  btnInactiveClr:   '#3a4a5e',
  legendBg:         'rgba(255,255,255,.02)',
  legendBorder:     'rgba(255,255,255,.04)',
  legendTitleClr:   '#3a4a5e',
  legendTextClr:    '#5a6a7e',
  epochClr:         '#3a4a5e',
  sectionBg:        '#0a0e18',
  sectionBorder:    'rgba(255,255,255,.05)',
  sectionLabelClr:  '#6a7a8e',
  sectionDescClr:   '#4a5a6e',
  sectionChevron:   '#3a4a5e',
  brainLabelClr:    '#4a5a6e',
  brainDescClr:     '#6a7a8e',
}
const T_LIGHT = {
  groupBg:          '#f9fafb',
  groupBorder:      'rgba(0,0,0,.08)',
  cellBg:           'rgba(0,0,0,.03)',
  cellBorder:       'rgba(0,0,0,.07)',
  cellWarnBorder:   'rgba(245,166,35,.3)',
  cellAccentBorder: 'rgba(0,180,140,.25)',
  cellDefaultClr:   '#111827',
  labelClr:         '#6b7280',
  descClr:          '#9ca3af',
  bodyClr:          '#374151',
  toggleBg:         'rgba(0,0,0,.04)',
  progressTrack:    'rgba(0,0,0,.08)',
  btnActiveClr:     '#059669',
  btnActiveBg:      'rgba(5,150,105,.1)',
  btnActiveBorder:  'rgba(5,150,105,.3)',
  btnInactiveClr:   '#9ca3af',
  legendBg:         'rgba(0,0,0,.02)',
  legendBorder:     'rgba(0,0,0,.07)',
  legendTitleClr:   '#6b7280',
  legendTextClr:    '#374151',
  epochClr:         '#6b7280',
  sectionBg:        '#f9fafb',
  sectionBorder:    'rgba(0,0,0,.08)',
  sectionLabelClr:  '#374151',
  sectionDescClr:   '#6b7280',
  sectionChevron:   '#9ca3af',
  brainLabelClr:    '#6b7280',
  brainDescClr:     '#374151',
}

const PanelThemeCtx = createContext(T_DARK)

// ── Interprétations vulgarisées ──────────────────────────────────────────────

const GUIDE = {
  rel_delta: {
    label: 'Ondes Delta δ', band: '1–4 Hz', color: '#818cf8', icon: '💤',
    interp: v => {
      if (v > 0.45) return { label: 'Très élevé — somnolence / fatigue profonde', level: 'warn', txt: 'Votre cerveau est en mode récupération. Difficile de rester alerte.' }
      if (v > 0.30) return { label: 'Élevé — fatigue présente', level: 'mid', txt: 'Signal de fatigue modérée. Préférez des stimuli doux.' }
      if (v > 0.15) return { label: 'Normal', level: 'ok', txt: 'Niveau basal sain. Présent durant le sommeil lent.' }
      return { label: 'Faible — bon éveil', level: 'ok', txt: 'Cerveau bien éveillé, peu de delta.' }
    },
    min: 0, max: 0.6, unit: '',
  },
  rel_theta: {
    label: 'Ondes Thêta θ', band: '6–8 Hz', color: '#f59e0b', icon: '🌀',
    interp: v => {
      if (v > 0.35) return { label: 'Très élevé — état méditatif / rêverie', level: 'mid', txt: 'État de créativité, mémoire émotionnelle. Peut indiquer distraction.' }
      if (v > 0.22) return { label: 'Élevé — relaxation mentale', level: 'ok', txt: 'Bon pour la créativité et la mémorisation.' }
      if (v > 0.12) return { label: 'Normal', level: 'ok', txt: 'Niveau typique en veille détendue.' }
      return { label: 'Faible — focus actif', level: 'ok', txt: 'Esprit focalisé sur une tâche précise.' }
    },
    min: 0, max: 0.5, unit: '',
  },
  rel_alpha: {
    label: 'Ondes Alpha α', band: '8–13 Hz', color: '#10b981', icon: '🧘',
    interp: v => {
      if (v > 0.40) return { label: 'Très élevé — relaxation profonde', level: 'best', txt: 'Excellent état de calme alerte. Cerveau réceptif et disponible. Cible neurofeedback atteinte.' }
      if (v > 0.25) return { label: 'Bon — détendu et attentif', level: 'ok', txt: 'État idéal entre détente et concentration. Alpha dominant.' }
      if (v > 0.15) return { label: 'Modéré — normal', level: 'mid', txt: 'Niveau basal. Ni trop stressé ni trop relaxé.' }
      return { label: 'Faible — stress ou concentration intense', level: 'warn', txt: 'Alpha supprimé : cerveau en alerte ou sous pression.' }
    },
    min: 0, max: 0.6, unit: '',
  },
  rel_beta: {
    label: 'Ondes Bêta β', band: '13–30 Hz', color: '#3b82f6', icon: '⚡',
    interp: v => {
      if (v > 0.45) return { label: 'Très élevé — surcharge cognitive / stress', level: 'warn', txt: 'Beta dominant : cerveau en surchauffe. Signe possible de rumination ou anxiété.' }
      if (v > 0.30) return { label: 'Élevé — concentration active', level: 'ok', txt: 'Traitement cognitif intense. Bon pour résoudre des problèmes.' }
      if (v > 0.20) return { label: 'Normal', level: 'ok', txt: 'Niveau typique en veille active.' }
      return { label: 'Faible — détendu', level: 'ok', txt: 'Peu d\'activité cognitive — repos mental.' }
    },
    min: 0, max: 0.6, unit: '',
  },
  rel_gamma_low: {
    label: 'Ondes Gamma γ', band: '30–45 Hz', color: '#ef4444', icon: '🔥',
    interp: v => {
      if (v > 0.15) return { label: 'Élevé — traitement cognitif haut niveau', level: 'mid', txt: 'Intégration multimodale active. Vérifier absence d\'artefacts musculaires.' }
      if (v > 0.06) return { label: 'Normal', level: 'ok', txt: 'Activité gamma physiologique normale.' }
      return { label: 'Faible', level: 'ok', txt: 'Peu d\'activité gamma — état de repos.' }
    },
    min: 0, max: 0.25, unit: '',
  },
  engagement: {
    label: 'Engagement β/(α+θ)', color: '#00e5b0', icon: '🎯',
    interp: v => {
      if (v > 2.0) return { label: 'Très engagé — alerte maximale', level: 'ok', txt: 'Engagement cognitif élevé. Excellent pour tâches d\'attention soutenue. (Pope 1995)' }
      if (v > 1.0) return { label: 'Engagé — focus actif', level: 'ok', txt: 'Bon niveau d\'implication cognitive.' }
      if (v > 0.5) return { label: 'Modéré', level: 'mid', txt: 'Engagement correct.' }
      return { label: 'Faible — somnolence / distraction', level: 'warn', txt: 'Manque d\'engagement. Possible somnolence ou manque de motivation.' }
    },
    min: 0, max: 3, unit: '',
  },
  stress_idx: {
    label: 'Indice de stress β/α', color: '#f87171', icon: '😰',
    interp: v => {
      if (v > 3.0) return { label: 'Stress élevé', level: 'warn', txt: 'Beta largement dominant sur alpha. Cerveau en état d\'alerte prolongée.' }
      if (v > 2.0) return { label: 'Stress modéré', level: 'mid', txt: 'Tension cognitive présente. Préférez des stimuli apaisants.' }
      if (v > 1.2) return { label: 'Normal', level: 'ok', txt: 'Équilibre beta/alpha sain.' }
      return { label: 'Très calme', level: 'best', txt: 'Alpha dominant sur beta — état de relaxation profonde.' }
    },
    min: 0, max: 5, unit: '',
  },
  theta_alpha: {
    label: 'Ratio θ/α', color: '#fbbf24', icon: '🧩',
    interp: v => {
      if (v > 2.0) return { label: 'Élevé — fatigue / inattention', level: 'warn', txt: 'Theta > alpha : cerveau en mode détendu ou fatigué.' }
      if (v > 1.0) return { label: 'Modéré — relaxation', level: 'mid', txt: 'Theta légèrement dominant.' }
      if (v > 0.5) return { label: 'Normal — équilibré', level: 'ok', txt: 'Bon équilibre theta/alpha.' }
      return { label: 'Faible — focus actif', level: 'ok', txt: 'Alpha > theta : cerveau focalisé.' }
    },
    min: 0, max: 3, unit: '',
  },
  alpha_beta: {
    label: 'Ratio α/β (Calme)', color: '#6ee7b7', icon: '⚖️',
    interp: v => {
      if (v > 1.5) return { label: 'Très calme', level: 'best', txt: 'Alpha largement dominant — état de sérénité.' }
      if (v > 0.8) return { label: 'Détendu', level: 'ok', txt: 'Bon équilibre, alpha légèrement dominant.' }
      if (v > 0.5) return { label: 'Équilibré', level: 'ok', txt: 'Balance alpha/beta normale.' }
      return { label: 'Activé / stressé', level: 'warn', txt: 'Beta domine alpha — cerveau en mode action ou stress.' }
    },
    min: 0, max: 2.5, unit: '',
  },
  hjorth_activity: {
    label: 'Hjorth — Activité', color: '#a78bfa', icon: '📈',
    interp: v => {
      if (v > 200) return { label: 'Très élevé — possible artefact', level: 'warn', txt: 'Amplitude signal très forte. Vérifiez le contact des électrodes.' }
      if (v > 50)  return { label: 'Élevé — signal robuste', level: 'ok', txt: 'Bonne puissance du signal EEG.' }
      if (v > 5)   return { label: 'Normal', level: 'ok', txt: 'Amplitude physiologique typique.' }
      return { label: 'Faible — signal faible', level: 'warn', txt: 'Amplitude basse. Vérifiez le contact des électrodes.' }
    },
    min: 0, max: 300, unit: 'µV²',
  },
  hjorth_mobility: {
    label: 'Hjorth — Mobilité', color: '#a78bfa', icon: '〰️',
    interp: v => {
      if (v > 1.0) return { label: 'Fréquence dominante élevée', level: 'mid', txt: 'Signal riche en hautes fréquences (beta/gamma).' }
      if (v > 0.3) return { label: 'Normal', level: 'ok', txt: 'Fréquence dominante dans la plage alpha/beta.' }
      return { label: 'Basse fréquence dominante', level: 'mid', txt: 'Signal dominé par delta/theta.' }
    },
    min: 0, max: 1.5, unit: '',
  },
  hjorth_complexity: {
    label: 'Hjorth — Complexité', color: '#a78bfa', icon: '🌊',
    interp: v => {
      if (v > 5) return { label: 'Très complexe — signal varié', level: 'ok', txt: 'Spectre fréquentiel diversifié, signal riche.' }
      if (v > 2) return { label: 'Complexité normale', level: 'ok', txt: 'Variation fréquentielle typique.' }
      return { label: 'Peu complexe — signal monotone', level: 'mid', txt: 'Signal dominé par une seule composante fréquentielle.' }
    },
    min: 0, max: 8, unit: '',
  },
  sef95: {
    label: 'SEF95 — Fréquence limite', color: '#f472b6', icon: '📊',
    interp: v => {
      if (v > 25) return { label: 'Élevé — activité beta/gamma', level: 'mid', txt: '95% de la puissance spectrale sous 25+ Hz. Cognition active.' }
      if (v > 15) return { label: 'Normal — alpha/beta', level: 'ok', txt: 'Spectre équilibré, plage alpha-beta dominante.' }
      if (v > 8)  return { label: 'Bas — theta/alpha', level: 'mid', txt: 'Activité dominée par les basses fréquences. Détente ou fatigue.' }
      return { label: 'Très bas — delta dominant', level: 'warn', txt: 'Sommeil ou forte somnolence.' }
    },
    min: 0, max: 40, unit: 'Hz',
  },
  spectral_entropy: {
    label: 'Entropie spectrale', color: '#f472b6', icon: '🎲',
    interp: v => {
      if (v > 0.8) return { label: 'Très élevée — spectre plat', level: 'mid', txt: 'Énergie distribuée uniformément. Possible artefact ou activité très diffuse.' }
      if (v > 0.5) return { label: 'Normal — spectre varié', level: 'ok', txt: 'Bonne diversité spectrale. Cerveau actif sur plusieurs bandes.' }
      if (v > 0.3) return { label: 'Bas — bande dominante', level: 'ok', txt: 'Une ou deux fréquences dominent le spectre.' }
      return { label: 'Très bas — signal très concentré', level: 'mid', txt: 'Quasi-sinusoïde : possible stimulation ou très fort alpha.' }
    },
    min: 0, max: 1, unit: '',
  },
  pac_theta_gamma: {
    label: 'PAC θ→γ (Mémoire)', color: '#06b6d4', icon: '🔗',
    interp: v => {
      if (v > 0.4) return { label: 'Couplage fort — traitement actif', level: 'best', txt: 'Couplage phase-amplitude theta-gamma élevé : consolidation mémoire active. (Tort 2010)' }
      if (v > 0.2) return { label: 'Couplage modéré', level: 'ok', txt: 'Interaction theta-gamma présente — engagement cognitif.' }
      if (v > 0.05) return { label: 'Couplage faible', level: 'mid', txt: 'Peu d\'interaction entre theta et gamma.' }
      return { label: 'Pas de couplage', level: 'mid', txt: 'Indépendance theta/gamma — état de repos.' }
    },
    min: 0, max: 0.6, unit: '',
  },
  fractal_dim: {
    label: 'Dimension fractale (HFD)', color: '#ec4899', icon: '🔮',
    interp: v => {
      if (v > 1.8) return { label: 'Très complexe', level: 'ok', txt: 'Signal hautement irrégulier — activité cérébrale intense et diverse.' }
      if (v > 1.5) return { label: 'Complexité normale', level: 'ok', txt: 'Dimension fractale typique d\'un EEG sain (1.5–1.8).' }
      if (v > 1.2) return { label: 'Signal régulier', level: 'mid', txt: 'Signal moins complexe — dominance d\'un rythme particulier.' }
      return { label: 'Signal très régulier', level: 'warn', txt: 'Dimension fractale basse : possible artefact ou état pathologique.' }
    },
    min: 1, max: 2, unit: '',
  },
  rms_uv: {
    label: 'RMS amplitude', color: '#f472b6', icon: '📡',
    interp: v => {
      if (v > 200) return { label: 'Très élevé — artefact probable', level: 'warn', txt: 'Clignement, mouvement de tête ou mauvais contact électrode.' }
      if (v > 50)  return { label: 'Élevé — signal fort', level: 'mid', txt: 'Amplitude robuste, vérifiez l\'absence de tension musculaire.' }
      if (v > 5)   return { label: 'Normal — bon signal EEG', level: 'ok', txt: 'Amplitude physiologique typique (5–50 µV).' }
      return { label: 'Très faible — signal bruit', level: 'warn', txt: 'Signal trop faible. Vérifiez les électrodes.' }
    },
    min: 0, max: 250, unit: 'µV',
  },
}

// ── Couleurs d'état ──────────────────────────────────────────────────────────
const LEVEL_COLOR = { best: '#00e5b0', ok: '#4da6ff', mid: '#f5a623', warn: '#ff4d6d' }
const LEVEL_BG    = {
  best: 'rgba(0,229,176,.08)', ok: 'rgba(77,166,255,.06)',
  mid:  'rgba(245,166,35,.08)', warn: 'rgba(255,77,109,.08)',
}

// ── Synthèse état cérébral ───────────────────────────────────────────────────
function getBrainState(f) {
  if (!f || typeof f.rel_alpha !== 'number') return null
  const alpha  = f.rel_alpha  ?? 0
  const beta   = f.rel_beta   ?? 0
  const theta  = f.rel_theta  ?? 0
  const stress = f.stress_idx ?? 0
  const engage = f.engagement ?? 0

  if (stress > 2.5 || (beta > 0.4 && alpha < 0.18))
    return { state: 'STRESS',        color: '#ff4d6d', icon: '😰', desc: 'Beta élevé, alpha supprimé — cerveau en alerte ou sous pression' }
  if (alpha > 0.32 && stress < 1.5)
    return { state: 'RELAXATION',    color: '#00e5b0', icon: '🧘', desc: 'Alpha dominant — état idéal pour la récupération et la réceptivité' }
  if (engage > 1.5 && beta > 0.25 && alpha > 0.15)
    return { state: 'CONCENTRATION', color: '#4da6ff', icon: '🎯', desc: 'Engagement élevé — cerveau actif et focalisé' }
  if (theta > 0.30 && engage < 0.7)
    return { state: 'SOMNOLENCE',    color: '#f5a623', icon: '😴', desc: 'Theta élevé, engagement bas — tendance à la rêverie ou fatigue' }
  return { state: 'NEUTRE',          color: '#9A8BAE', icon: '😌', desc: 'État équilibré sans dominance marquée' }
}

// ── Barre d'interprétation ───────────────────────────────────────────────────
function GuideStat({ cfg, value }) {
  const T = useContext(PanelThemeCtx)
  if (!cfg) return null
  const interp = cfg.interp(value ?? 0)
  const pct    = Math.min(100, Math.max(0, ((value ?? 0) - cfg.min) / (cfg.max - cfg.min) * 100))
  const c      = LEVEL_COLOR[interp.level]

  return (
    <div style={{ padding:'10px 12px', borderRadius:10, background:LEVEL_BG[interp.level], border:`1px solid ${c}22` }}>
      <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:6 }}>
        <span style={{ fontSize:14 }}>{cfg.icon}</span>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontSize:9, color:T.labelClr, letterSpacing:.5 }}>{cfg.label}</div>
          <div style={{ fontSize:10, fontWeight:700, color:c, marginTop:1 }}>{interp.label}</div>
        </div>
        <div style={{ fontFamily:"'Space Mono',monospace", fontSize:11, color:c, flexShrink:0 }}>
          {typeof value === 'number'
            ? (cfg.unit === 'Hz' ? f1(value) : value < 10 ? f3(value) : Math.round(value))
            : '—'}
          {cfg.unit ? ' ' + cfg.unit : ''}
        </div>
      </div>
      <div style={{ height:5, borderRadius:3, background:T.progressTrack, marginBottom:6, overflow:'hidden' }}>
        <div style={{ width:`${pct}%`, height:'100%', borderRadius:3,
                      background:`linear-gradient(90deg, ${c}80, ${c})`, transition:'width .4s' }} />
      </div>
      <div style={{ fontSize:10, color:T.bodyClr, lineHeight:1.5 }}>{interp.txt}</div>
    </div>
  )
}

// ── Mode expert : groupes ────────────────────────────────────────────────────
function Group({ title, color, children }) {
  const T = useContext(PanelThemeCtx)
  return (
    <div style={{ background:T.groupBg, border:`1px solid ${T.groupBorder}`, borderRadius:12, padding:'14px 16px' }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12 }}>
        <div style={{ width:7, height:7, borderRadius:2, background:color, boxShadow:`0 0 8px ${color}55` }} />
        <span style={{ fontFamily:"'Space Mono',monospace", fontSize:9, letterSpacing:1.5, textTransform:'uppercase', color }}>{title}</span>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(110px,1fr))', gap:7 }}>
        {children}
      </div>
    </div>
  )
}

function Cell({ label, value, desc, color, warn, accent }) {
  const T = useContext(PanelThemeCtx)
  const c = warn ? '#f5a623' : accent ? '#00e5b0' : color || T.cellDefaultClr
  return (
    <div style={{ background:T.cellBg, borderRadius:8, padding:'9px 10px',
                  border:`1px solid ${warn ? T.cellWarnBorder : accent ? T.cellAccentBorder : T.cellBorder}` }}>
      <div style={{ fontSize:8, color:T.labelClr, marginBottom:4, lineHeight:1.3 }}>{label}</div>
      <div style={{ fontFamily:"'Space Mono',monospace", fontSize:13, fontWeight:700, color:c }}>{value}</div>
      {desc && <div style={{ fontSize:8, color:T.descClr, marginTop:3 }}>{desc}</div>}
    </div>
  )
}

// ── Conteneur de section guide ────────────────────────────────────────────────
function SectionGuide({ title, icon, desc, children }) {
  const T = useContext(PanelThemeCtx)
  const [open, setOpen] = useState(true)
  return (
    <div style={{ background:T.sectionBg, border:`1px solid ${T.sectionBorder}`, borderRadius:14, overflow:'hidden' }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{ width:'100%', padding:'12px 16px', background:'transparent', border:'none',
                 cursor:'pointer', display:'flex', alignItems:'center', gap:8, textAlign:'left' }}
      >
        <span style={{ fontSize:16 }}>{icon}</span>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontFamily:"'Space Mono',monospace", fontSize:9, letterSpacing:1.5,
                        textTransform:'uppercase', color:T.sectionLabelClr }}>{title}</div>
          {desc && <div style={{ fontSize:10, color:T.sectionDescClr, marginTop:2 }}>{desc}</div>}
        </div>
        <span style={{ fontSize:12, color:T.sectionChevron, transition:'transform .2s',
                        transform:open ? 'rotate(90deg)' : 'rotate(0deg)' }}>▶</span>
      </button>
      {open && <div style={{ padding:'0 14px 14px' }}>{children}</div>}
    </div>
  )
}

// ════════════════════════════════════════════════════════════════════════════
// COMPOSANT PRINCIPAL
// ════════════════════════════════════════════════════════════════════════════
export default function FeaturesPanel({ features: f = {}, epochIdx }) {
  const { effectiveTheme } = useTheme()
  const T = effectiveTheme === 'dark' ? T_DARK : T_LIGHT
  const [viewMode, setViewMode] = useState('guide')
  const brainState = getBrainState(f)

  return (
    <PanelThemeCtx.Provider value={T}>
      <div style={{ display:'flex', flexDirection:'column', gap:14 }}>

        {/* ── En-tête / Toggle mode ── */}
        <div style={{ display:'flex', alignItems:'center', gap:10, flexWrap:'wrap' }}>
          {epochIdx && (
            <div style={{ fontFamily:"'Space Mono',monospace", fontSize:10, color:T.epochClr, flex:1 }}>
              Époque #{epochIdx} · 4s · Welch PSD · 27 features v8.0
            </div>
          )}
          <div style={{ display:'flex', gap:2, background:T.toggleBg, borderRadius:8, padding:3 }}>
            {[['guide','🧠 Guide'], ['expert','⚙ Expert']].map(([m, label]) => (
              <button key={m} onClick={() => setViewMode(m)} style={{
                padding:'4px 14px', borderRadius:6, fontSize:10, cursor:'pointer',
                fontFamily:"'Space Mono',monospace",
                background: viewMode===m ? T.btnActiveBg   : 'transparent',
                border:     viewMode===m ? `1px solid ${T.btnActiveBorder}` : '1px solid transparent',
                color:      viewMode===m ? T.btnActiveClr  : T.btnInactiveClr,
                fontWeight: viewMode===m ? 700 : 400,
              }}>{label}</button>
            ))}
          </div>
        </div>

        {/* ════════════════════════════════════
            MODE GUIDE — Vulgarisé
            ════════════════════════════════════ */}
        {viewMode === 'guide' && (
          <>
            {/* Synthèse état cérébral */}
            {brainState && (
              <div style={{ display:'flex', alignItems:'center', gap:12, padding:'14px 18px',
                            borderRadius:14, background:`${brainState.color}0d`, border:`1px solid ${brainState.color}30` }}>
                <span style={{ fontSize:28 }}>{brainState.icon}</span>
                <div>
                  <div style={{ fontSize:9, color:T.brainLabelClr, letterSpacing:1.5, textTransform:'uppercase', marginBottom:3 }}>
                    État cérébral estimé
                  </div>
                  <div style={{ fontSize:16, fontWeight:800, color:brainState.color, letterSpacing:.5 }}>
                    {brainState.state}
                  </div>
                  <div style={{ fontSize:11, color:T.brainDescClr, marginTop:2, lineHeight:1.5 }}>{brainState.desc}</div>
                </div>
              </div>
            )}

            <SectionGuide title="Rythmes cérébraux" icon="🌊"
              desc="La puissance relative de chaque bande de fréquence exprime l'état mental dominant.">
              <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:8 }}>
                {['rel_alpha','rel_beta','rel_theta','rel_delta','rel_gamma_low'].map(k => (
                  <GuideStat key={k} cfg={GUIDE[k]} value={f[k]} />
                ))}
              </div>
            </SectionGuide>

            <SectionGuide title="Indices cognitifs" icon="🧩"
              desc="Des ratios entre bandes révèlent votre niveau de stress, d'engagement et de relaxation.">
              <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:8 }}>
                {['stress_idx','engagement','alpha_beta','theta_alpha'].map(k => (
                  <GuideStat key={k} cfg={GUIDE[k]} value={f[k]} />
                ))}
              </div>
            </SectionGuide>

            <SectionGuide title="Qualité et complexité du signal" icon="📡"
              desc="Ces valeurs indiquent la qualité du captage et la richesse du signal EEG.">
              <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:8 }}>
                {['rms_uv','sef95','spectral_entropy','hjorth_activity','hjorth_mobility','hjorth_complexity'].map(k => (
                  <GuideStat key={k} cfg={GUIDE[k]} value={f[k]} />
                ))}
              </div>
            </SectionGuide>

            <SectionGuide title="Connexions et complexité cérébrale" icon="🔗"
              desc="Le couplage entre fréquences et la dimension fractale mesurent la sophistication de l'activité cérébrale.">
              <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:8 }}>
                {['pac_theta_gamma','fractal_dim'].map(k => (
                  <GuideStat key={k} cfg={GUIDE[k]} value={f[k]} />
                ))}
              </div>
            </SectionGuide>

            {/* Légende */}
            <div style={{ display:'flex', gap:12, flexWrap:'wrap', padding:'10px 14px',
                          borderRadius:10, background:T.legendBg, border:`1px solid ${T.legendBorder}` }}>
              <div style={{ fontSize:9, color:T.legendTitleClr, letterSpacing:1, textTransform:'uppercase', marginRight:4 }}>Légende :</div>
              {[['best','Optimal'],['ok','Normal'],['mid','À surveiller'],['warn','Alerte']].map(([l,t]) => (
                <div key={l} style={{ display:'flex', alignItems:'center', gap:4 }}>
                  <div style={{ width:8, height:8, borderRadius:2, background:LEVEL_COLOR[l] }} />
                  <span style={{ fontSize:9, color:T.legendTextClr }}>{t}</span>
                </div>
              ))}
            </div>
          </>
        )}

        {/* ════════════════════════════════════
            MODE EXPERT — Valeurs brutes
            ════════════════════════════════════ */}
        {viewMode === 'expert' && (
          <>
            <Group title="Puissances relatives (bandes v8.0)" color="#4da6ff">
              <Cell label="δ Delta 1–4 Hz"      value={f4(f.rel_delta)}     desc="Sommeil profond"   color="#818cf8" />
              <Cell label="θ Theta 6–8 Hz"       value={f4(f.rel_theta)}     desc="Mémoire / rêverie" color="#f59e0b" />
              <Cell label="α Alpha 8–13 Hz"      value={f4(f.rel_alpha)}     desc="Relaxation/alerte" color="#10b981" accent={f.rel_alpha > 0.3} />
              <Cell label="β Beta 13–30 Hz"      value={f4(f.rel_beta)}      desc="Cognition active"  color="#3b82f6" />
              <Cell label="β↑ Beta-Hi 20–30 Hz"  value={f4(f.rel_beta_high)} desc="Stress cognitif"   color="#ec4899" />
              <Cell label="γ Gamma 30–45 Hz"     value={f4(f.rel_gamma_low)} desc="Traitement haut"   color="#ef4444" />
            </Group>

            <Group title="Ratios cognitifs" color="#00e5b0">
              <Cell label="Engagement β/(α+θ)"  value={f3(f.engagement)}   desc="EI Pope 1995"    accent={f.engagement > 1.5} />
              <Cell label="Stress β/α"           value={f3(f.stress_idx)}   desc="Indice stress"   warn={f.stress_idx > 2} />
              <Cell label="θ/α"                  value={f3(f.theta_alpha)}  desc="Fatigue/focus" />
              <Cell label="α/β (Détente)"        value={f3(f.alpha_beta)}   desc="Calme/Activé" />
            </Group>

            <Group title="Paramètres Hjorth (Cohen 2014 ch.17)" color="#a78bfa">
              <Cell label="Activity (Var)"     value={f4(f.hjorth_activity)}   desc="Amplitude²" />
              <Cell label="Mobility √(V1/V0)"  value={f4(f.hjorth_mobility)}   desc="Fréquence moy." />
              <Cell label="Complexity"         value={f4(f.hjorth_complexity)} desc="Variation fréq." />
            </Group>

            <Group title="Analyse spectrale" color="#f472b6">
              <Cell label="SEF95 (Hz)"       value={f1(f.sef95)}            desc="95% énergie sous" />
              <Cell label="Entropie spec."   value={f4(f.spectral_entropy)} desc="Complexité PSD" />
              <Cell label="RMS (µV)"         value={f4(f.rms_uv)}           desc="Amplitude eff." />
              <Cell label="Amp. moy. (µV)"   value={f4(f.mean_amp)} />
            </Group>

            <Group title="Distribution temporelle" color="#f59e0b">
              <Cell label="Skewness"  value={f4(f.skewness)} desc="Asymétrie"       warn={Math.abs(f.skewness ?? 0) > 2} />
              <Cell label="Kurtosis"  value={f4(f.kurtosis)} desc="Aplatissement"   warn={(f.kurtosis ?? 0) > 5} />
              <Cell label="ZCR"       value={f4(f.zcr)}      desc="Zero-crossing rate" />
            </Group>

            <Group title="PAC θ→γ (Tort et al. 2010)" color="#06b6d4">
              <Cell label="PAC θ→γ proxy" value={f4(f.pac_theta_gamma)} desc="Corrél. env.γ / phase θ" accent={(f.pac_theta_gamma ?? 0) > 0.3} />
            </Group>

            <Group title="Dimension Fractale Higuchi" color="#ec4899">
              <Cell label="HFD global" value={f4(f.fractal_dim)} desc="Higuchi kmax=8" />
            </Group>

            <Group title="EMG" color="#f87171">
              <Cell label="EMG ratio"   value={f4(f.emg_ratio)}   desc="P(35-45Hz)/P(1-45Hz)" warn={(f.emg_ratio ?? 0) > 0.2} />
            </Group>

            {f.db_alpha !== undefined && (
              <Group title="Puissance dB vs Baseline" color="#6ee7b7">
                {['delta','theta','alpha','beta','beta_high','gamma_low'].map(b => (
                  <Cell key={b} label={`${b} dB`} value={f3(f[`db_${b}`])} desc="vs baseline"
                    accent={(f[`db_${b}`] ?? 0) > 1} warn={(f[`db_${b}`] ?? 0) < -5} />
                ))}
              </Group>
            )}
          </>
        )}
      </div>
    </PanelThemeCtx.Provider>
  )
}
