/**
 * FeaturesPanel — Valeurs brutes + Guide vulgarisé interactif
 * Mode EXPERT : toutes les features numériques brutes
 * Mode GUIDE  : barres interprétatives + langage accessible + état cérébral courant
 */
import { useState } from 'react'

const f4 = v => typeof v === 'number' ? v.toFixed(4) : '—'
const f3 = v => typeof v === 'number' ? v.toFixed(3) : '—'
const f1 = v => typeof v === 'number' ? v.toFixed(1) : '—'

// ── Interprétations vulgarisées ──────────────────────────────────────────────

const GUIDE = {
  rel_delta: {
    label: 'Ondes Delta δ', band: '0.5–4 Hz', color: '#818cf8',
    icon: '💤',
    interp: v => {
      if (v > 0.45) return { label: 'Très élevé — somnolence / fatigue profonde', level: 'warn', txt: 'Votre cerveau est en mode récupération. Difficile de rester alerte.' }
      if (v > 0.30) return { label: 'Élevé — fatigue présente', level: 'mid', txt: 'Signal de fatigue modérée. Préférez des stimuli doux.' }
      if (v > 0.15) return { label: 'Normal', level: 'ok', txt: 'Niveau basal sain. Présent durant le sommeil lent.' }
      return { label: 'Faible — bon éveil', level: 'ok', txt: 'Cerveau bien éveillé, peu de delta.' }
    },
    min: 0, max: 0.6, unit: '',
  },
  rel_theta: {
    label: 'Ondes Thêta θ', band: '4–8 Hz', color: '#f59e0b',
    icon: '🌀',
    interp: v => {
      if (v > 0.35) return { label: 'Très élevé — état méditatif / rêverie', level: 'mid', txt: 'État de créativité, mémoire émotionnelle. Peut indiquer distraction.' }
      if (v > 0.22) return { label: 'Élevé — relaxation mentale', level: 'ok', txt: 'Bon pour la créativité et la mémorisation.' }
      if (v > 0.12) return { label: 'Normal', level: 'ok', txt: 'Niveau typique en veille détendue.' }
      return { label: 'Faible — focus actif', level: 'ok', txt: 'Esprit focalisé sur une tâche précise.' }
    },
    min: 0, max: 0.5, unit: '',
  },
  rel_alpha: {
    label: 'Ondes Alpha α', band: '8–13 Hz', color: '#10b981',
    icon: '🧘',
    interp: v => {
      if (v > 0.40) return { label: 'Très élevé — relaxation profonde', level: 'best', txt: 'Excellent état de calme alerte. Cerveau réceptif et disponible. Cible neurofeedback atteinte.' }
      if (v > 0.25) return { label: 'Bon — détendu et attentif', level: 'ok', txt: 'État idéal entre détente et concentration. Alpha dominant.' }
      if (v > 0.15) return { label: 'Modéré — normal', level: 'mid', txt: 'Niveau basal. Ni trop stressé ni trop relaxé.' }
      return { label: 'Faible — stress ou concentration intense', level: 'warn', txt: 'Alpha supprimé : cerveau en alerte ou sous pression.' }
    },
    min: 0, max: 0.6, unit: '',
  },
  rel_beta: {
    label: 'Ondes Bêta β', band: '13–30 Hz', color: '#3b82f6',
    icon: '⚡',
    interp: v => {
      if (v > 0.45) return { label: 'Très élevé — surcharge cognitive / stress', level: 'warn', txt: 'Beta dominant : cerveau en surchauffe. Signe possible de rumination ou anxiété.' }
      if (v > 0.30) return { label: 'Élevé — concentration active', level: 'ok', txt: 'Traitement cognitif intense. Bon pour résoudre des problèmes.' }
      if (v > 0.20) return { label: 'Normal', level: 'ok', txt: 'Niveau typique en veille active.' }
      return { label: 'Faible — détendu', level: 'ok', txt: 'Peu d\'activité cognitive — repos mental.' }
    },
    min: 0, max: 0.6, unit: '',
  },
  rel_gamma: {
    label: 'Ondes Gamma γ', band: '30–40 Hz', color: '#ef4444',
    icon: '🔥',
    interp: v => {
      if (v > 0.15) return { label: 'Élevé — traitement cognitif haut niveau', level: 'mid', txt: 'Intégration multimodale active. Conscience et binding perceptuel. Vérifier absence d\'artefacts musculaires.' }
      if (v > 0.06) return { label: 'Normal', level: 'ok', txt: 'Activité gamma physiologique normale.' }
      return { label: 'Faible', level: 'ok', txt: 'Peu d\'activité gamma — état de repos.' }
    },
    min: 0, max: 0.25, unit: '',
  },
  engagement: {
    label: 'Engagement β/(α+θ)', color: '#00e5b0',
    icon: '🎯',
    interp: v => {
      if (v > 2.0) return { label: 'Très engagé — alerte maximale', level: 'ok', txt: 'Engagement cognitif élevé. Excellent pour tâches d\'attention soutenue. (Pope 1995)' }
      if (v > 1.0) return { label: 'Engagé — focus actif', level: 'ok', txt: 'Bon niveau d\'implication cognitive.' }
      if (v > 0.5) return { label: 'Modéré', level: 'mid', txt: 'Engagement correct.' }
      return { label: 'Faible — somnolence / distraction', level: 'warn', txt: 'Manque d\'engagement. Possible somnolence ou manque de motivation.' }
    },
    min: 0, max: 3, unit: '',
  },
  stress_idx: {
    label: 'Indice de stress β/α', color: '#f87171',
    icon: '😰',
    interp: v => {
      if (v > 3.0) return { label: 'Stress élevé', level: 'warn', txt: 'Beta largement dominant sur alpha. Cerveau en état d\'alerte prolongée.' }
      if (v > 2.0) return { label: 'Stress modéré', level: 'mid', txt: 'Tension cognitive présente. Préférez des stimuli apaisants.' }
      if (v > 1.2) return { label: 'Normal', level: 'ok', txt: 'Équilibre beta/alpha sain.' }
      return { label: 'Très calme', level: 'best', txt: 'Alpha dominant sur beta — état de relaxation profonde.' }
    },
    min: 0, max: 5, unit: '',
  },
  theta_beta: {
    label: 'Ratio θ/β (TDAH)', color: '#fbbf24',
    icon: '🧩',
    interp: v => {
      if (v > 3.0) return { label: 'Élevé — inattention possible', level: 'warn', txt: 'Ratio θ/β élevé associé aux états d\'inattention et au TDAH. (Monastra 2005)' }
      if (v > 1.5) return { label: 'Modéré — relaxation', level: 'mid', txt: 'Theta > beta : cerveau en mode détendu.' }
      if (v > 0.8) return { label: 'Normal — équilibré', level: 'ok', txt: 'Bon équilibre theta/beta.' }
      return { label: 'Faible — focus actif', level: 'ok', txt: 'Beta > theta : cerveau concentré et actif.' }
    },
    min: 0, max: 4, unit: '',
  },
  alpha_beta: {
    label: 'Ratio α/β (Calme)', color: '#6ee7b7',
    icon: '⚖️',
    interp: v => {
      if (v > 1.5) return { label: 'Très calme', level: 'best', txt: 'Alpha largement dominant — état de sérénité.' }
      if (v > 0.8) return { label: 'Détendu', level: 'ok', txt: 'Bon équilibre, alpha légèrement dominant.' }
      if (v > 0.5) return { label: 'Équilibré', level: 'ok', txt: 'Balance alpha/beta normale.' }
      return { label: 'Activé / stressé', level: 'warn', txt: 'Beta domine alpha — cerveau en mode action ou stress.' }
    },
    min: 0, max: 2.5, unit: '',
  },
  hjorth_activity: {
    label: 'Hjorth — Activité', color: '#a78bfa',
    icon: '📈',
    interp: v => {
      if (v > 200) return { label: 'Très élevé — possible artefact', level: 'warn', txt: 'Amplitude signal très forte. Vérifiez le contact des électrodes.' }
      if (v > 50) return { label: 'Élevé — signal robuste', level: 'ok', txt: 'Bonne puissance du signal EEG.' }
      if (v > 5) return { label: 'Normal', level: 'ok', txt: 'Amplitude physiologique typique.' }
      return { label: 'Faible — signal faible', level: 'warn', txt: 'Amplitude basse. Vérifiez le contact des électrodes.' }
    },
    min: 0, max: 300, unit: 'µV²',
  },
  hjorth_mobility: {
    label: 'Hjorth — Mobilité', color: '#a78bfa',
    icon: '〰️',
    interp: v => {
      if (v > 1.0) return { label: 'Fréquence dominante élevée', level: 'mid', txt: 'Signal riche en hautes fréquences (beta/gamma).' }
      if (v > 0.3) return { label: 'Normal', level: 'ok', txt: 'Fréquence dominante dans la plage alpha/beta.' }
      return { label: 'Basse fréquence dominante', level: 'mid', txt: 'Signal dominé par delta/theta.' }
    },
    min: 0, max: 1.5, unit: '',
  },
  hjorth_complexity: {
    label: 'Hjorth — Complexité', color: '#a78bfa',
    icon: '🌊',
    interp: v => {
      if (v > 5) return { label: 'Très complexe — signal varié', level: 'ok', txt: 'Spectre fréquentiel diversifié, signal riche.' }
      if (v > 2) return { label: 'Complexité normale', level: 'ok', txt: 'Variation fréquentielle typique.' }
      return { label: 'Peu complexe — signal monotone', level: 'mid', txt: 'Signal dominé par une seule composante fréquentielle.' }
    },
    min: 0, max: 8, unit: '',
  },
  sef95: {
    label: 'SEF95 — Fréquence limite', color: '#f472b6',
    icon: '📊',
    interp: v => {
      if (v > 25) return { label: 'Élevé — activité beta/gamma', level: 'mid', txt: '95% de la puissance spectrale sous 25+ Hz. Cognition active.' }
      if (v > 15) return { label: 'Normal — alpha/beta', level: 'ok', txt: 'Spectre équilibré, plage alpha-beta dominante.' }
      if (v > 8) return { label: 'Bas — theta/alpha', level: 'mid', txt: 'Activité dominée par les basses fréquences. Détente ou fatigue.' }
      return { label: 'Très bas — delta dominant', level: 'warn', txt: 'Sommeil ou forte somnolence.' }
    },
    min: 0, max: 40, unit: 'Hz',
  },
  spectral_entropy: {
    label: 'Entropie spectrale', color: '#f472b6',
    icon: '🎲',
    interp: v => {
      if (v > 0.8) return { label: 'Très élevée — spectre plat', level: 'mid', txt: 'Énergie distribuée uniformément sur toutes les fréquences. Possible artefact ou activité très diffuse.' }
      if (v > 0.5) return { label: 'Normal — spectre varié', level: 'ok', txt: 'Bonne diversité spectrale. Cerveau actif sur plusieurs bandes.' }
      if (v > 0.3) return { label: 'Bas — bande dominante', level: 'ok', txt: 'Une ou deux fréquences dominent le spectre.' }
      return { label: 'Très bas — signal très concentré', level: 'mid', txt: 'Quasi-sinusoïde : possible stimulation ou très fort alpha.' }
    },
    min: 0, max: 1, unit: '',
  },
  pac_theta_gamma: {
    label: 'PAC θ→γ (Mémoire)', color: '#06b6d4',
    icon: '🔗',
    interp: v => {
      if (v > 0.4) return { label: 'Couplage fort — traitement actif', level: 'best', txt: 'Couplage phase-amplitude theta-gamma élevé : consolidation mémoire active, apprentissage. (Tort 2010)' }
      if (v > 0.2) return { label: 'Couplage modéré', level: 'ok', txt: 'Interaction theta-gamma présente — engagement cognitif.' }
      if (v > 0.05) return { label: 'Couplage faible', level: 'mid', txt: 'Peu d\'interaction entre theta et gamma.' }
      return { label: 'Pas de couplage', level: 'mid', txt: 'Indépendance theta/gamma — état de repos.' }
    },
    min: 0, max: 0.6, unit: '',
  },
  fractal_dim: {
    label: 'Dimension fractale', color: '#ec4899',
    icon: '🔮',
    interp: v => {
      if (v > 1.8) return { label: 'Très complexe', level: 'ok', txt: 'Signal hautement irrégulier — activité cérébrale intense et diverse.' }
      if (v > 1.5) return { label: 'Complexité normale', level: 'ok', txt: 'Dimension fractale typique d\'un EEG sain (1.5–1.8).' }
      if (v > 1.2) return { label: 'Signal régulier', level: 'mid', txt: 'Signal moins complexe — dominance d\'un rythme particulier.' }
      return { label: 'Signal très régulier', level: 'warn', txt: 'Dimension fractale basse : possible artefact ou état pathologique.' }
    },
    min: 1, max: 2, unit: '',
  },
  rms: {
    label: 'RMS amplitude', color: '#f472b6',
    icon: '📡',
    interp: v => {
      if (v > 200) return { label: 'Très élevé — artefact probable', level: 'warn', txt: 'Clignement, mouvement de tête ou mauvais contact électrode.' }
      if (v > 50) return { label: 'Élevé — signal fort', level: 'mid', txt: 'Amplitude robuste, vérifiez l\'absence de tension musculaire.' }
      if (v > 5) return { label: 'Normal — bon signal EEG', level: 'ok', txt: 'Amplitude physiologique typique (5–50 µV).' }
      return { label: 'Très faible — signal bruit', level: 'warn', txt: 'Signal trop faible. Vérifiez les électrodes.' }
    },
    min: 0, max: 250, unit: 'µV',
  },
}

// ── Couleurs d'état ──────────────────────────────────────────────────────────
const LEVEL_COLOR = {
  best: '#00e5b0',
  ok:   '#4da6ff',
  mid:  '#f5a623',
  warn: '#ff4d6d',
}
const LEVEL_BG = {
  best: 'rgba(0,229,176,.08)',
  ok:   'rgba(77,166,255,.06)',
  mid:  'rgba(245,166,35,.08)',
  warn: 'rgba(255,77,109,.08)',
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
  if (!cfg) return null
  const interp = cfg.interp(value ?? 0)
  const pct    = Math.min(100, Math.max(0,
    ((value ?? 0) - cfg.min) / (cfg.max - cfg.min) * 100
  ))
  const c = LEVEL_COLOR[interp.level]

  return (
    <div style={{
      padding: '10px 12px', borderRadius: 10,
      background: LEVEL_BG[interp.level],
      border: `1px solid ${c}22`,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 6 }}>
        <span style={{ fontSize: 14 }}>{cfg.icon}</span>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ fontSize: 9, color: '#4a5a6e', letterSpacing: .5 }}>{cfg.label}</div>
          <div style={{ fontSize: 10, fontWeight: 700, color: c, marginTop: 1 }}>{interp.label}</div>
        </div>
        <div style={{ fontFamily: "'Space Mono',monospace", fontSize: 11, color: c, flexShrink: 0 }}>
          {typeof value === 'number' ? (cfg.unit === 'Hz' ? f1(value) : (value < 10 ? f3(value) : Math.round(value))) : '—'}
          {cfg.unit ? ' ' + cfg.unit : ''}
        </div>
      </div>
      {/* Barre */}
      <div style={{ height: 5, borderRadius: 3, background: 'rgba(255,255,255,.06)', marginBottom: 6, overflow: 'hidden' }}>
        <div style={{ width: `${pct}%`, height: '100%', borderRadius: 3,
                      background: `linear-gradient(90deg, ${c}80, ${c})`, transition: 'width .4s' }} />
      </div>
      <div style={{ fontSize: 10, color: '#6a7a8e', lineHeight: 1.5 }}>{interp.txt}</div>
    </div>
  )
}

// ── Mode expert : cellule compacte ───────────────────────────────────────────
function Group({ title, color, children }) {
  return (
    <div style={{ background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)', borderRadius:12, padding:'14px 16px' }}>
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
  const c = warn ? '#f5a623' : accent ? '#00e5b0' : color || '#c9d8e8'
  return (
    <div style={{ background:'rgba(255,255,255,.02)', borderRadius:8, padding:'9px 10px',
                  border:`1px solid ${warn?'rgba(245,166,35,.15)':accent?'rgba(0,229,176,.12)':'rgba(255,255,255,.04)'}` }}>
      <div style={{ fontSize:8, color:'#4a5a6e', marginBottom:4, lineHeight:1.3 }}>{label}</div>
      <div style={{ fontFamily:"'Space Mono',monospace", fontSize:13, fontWeight:700, color:c }}>{value}</div>
      {desc && <div style={{ fontSize:8, color:'#3a4a5e', marginTop:3 }}>{desc}</div>}
    </div>
  )
}

// ════════════════════════════════════════════════════════════════════════════
// COMPOSANT PRINCIPAL
// ════════════════════════════════════════════════════════════════════════════
export default function FeaturesPanel({ features: f = {}, graph = {}, epochIdx }) {
  const [viewMode, setViewMode] = useState('guide')  // 'guide' | 'expert'
  const [expanded, setExpanded] = useState(null)     // clé feature ouverte en guide

  const brainState = getBrainState(f)

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:14, animation:'fadeIn .3s ease' }}>

      {/* ── En-tête ── */}
      <div style={{ display:'flex', alignItems:'center', gap:10, flexWrap:'wrap' }}>
        {epochIdx && (
          <div style={{ fontFamily:"'Space Mono',monospace", fontSize:10, color:'#3a4a5e', flex:1 }}>
            Époque #{epochIdx} · 4s · Welch PSD · 27 features v8
          </div>
        )}
        {/* Toggle mode */}
        <div style={{ display:'flex', gap:2, background:'rgba(255,255,255,.03)', borderRadius:8, padding:3 }}>
          {[['guide','🧠 Guide'], ['expert','⚙ Expert']].map(([m, label]) => (
            <button key={m} onClick={() => setViewMode(m)} style={{
              padding:'4px 14px', borderRadius:6, fontSize:10, cursor:'pointer',
              fontFamily:"'Space Mono',monospace",
              background: viewMode===m ? 'rgba(0,229,176,.12)' : 'transparent',
              border: viewMode===m ? '1px solid rgba(0,229,176,.3)' : '1px solid transparent',
              color: viewMode===m ? '#00e5b0' : '#3a4a5e',
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
            <div style={{
              display:'flex', alignItems:'center', gap:12, padding:'14px 18px',
              borderRadius:14, background:`${brainState.color}0d`,
              border:`1px solid ${brainState.color}30`,
            }}>
              <span style={{ fontSize:28 }}>{brainState.icon}</span>
              <div>
                <div style={{ fontSize:9, color:'#4a5a6e', letterSpacing:1.5, textTransform:'uppercase', marginBottom:3 }}>
                  État cérébral estimé
                </div>
                <div style={{ fontSize:16, fontWeight:800, color:brainState.color, letterSpacing:.5 }}>
                  {brainState.state}
                </div>
                <div style={{ fontSize:11, color:'#6a7a8e', marginTop:2, lineHeight:1.5 }}>{brainState.desc}</div>
              </div>
            </div>
          )}

          {/* Section : Rythmes cérébraux */}
          <SectionGuide title="Rythmes cérébraux" icon="🌊" desc="La puissance relative de chaque bande de fréquence exprime l'état mental dominant.">
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:8 }}>
              {['rel_alpha','rel_beta','rel_theta','rel_delta','rel_gamma'].map(k => (
                <GuideStat key={k} cfg={GUIDE[k]} value={f[k]} />
              ))}
            </div>
          </SectionGuide>

          {/* Section : Indices cognitifs */}
          <SectionGuide title="Indices cognitifs" icon="🧩" desc="Des ratios entre bandes révèlent votre niveau de stress, d'engagement et de relaxation.">
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:8 }}>
              {['stress_idx','engagement','alpha_beta','theta_beta'].map(k => (
                <GuideStat key={k} cfg={GUIDE[k]} value={f[k]} />
              ))}
            </div>
          </SectionGuide>

          {/* Section : Qualité du signal */}
          <SectionGuide title="Qualité et complexité du signal" icon="📡" desc="Ces valeurs indiquent la qualité du captage et la richesse du signal EEG.">
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:8 }}>
              {['rms','sef95','spectral_entropy','hjorth_activity','hjorth_mobility','hjorth_complexity'].map(k => (
                <GuideStat key={k} cfg={GUIDE[k]} value={f[k]} />
              ))}
            </div>
          </SectionGuide>

          {/* Section : Connexions cérébrales */}
          <SectionGuide title="Connexions et complexité cérébrale" icon="🔗" desc="Le couplage entre fréquences et la dimension fractale mesurent la sophistication de l'activité cérébrale.">
            <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(200px,1fr))', gap:8 }}>
              {['pac_theta_gamma','fractal_dim'].map(k => (
                <GuideStat key={k} cfg={GUIDE[k]} value={f[k]} />
              ))}
            </div>
          </SectionGuide>

          {/* Légende */}
          <div style={{ display:'flex', gap:12, flexWrap:'wrap', padding:'10px 14px',
                        borderRadius:10, background:'rgba(255,255,255,.02)', border:'1px solid rgba(255,255,255,.04)' }}>
            <div style={{ fontSize:9, color:'#3a4a5e', letterSpacing:1, textTransform:'uppercase', marginRight:4 }}>Légende :</div>
            {[['best','Optimal'],['ok','Normal'],['mid','À surveiller'],['warn','Alerte']].map(([l,t]) => (
              <div key={l} style={{ display:'flex', alignItems:'center', gap:4 }}>
                <div style={{ width:8, height:8, borderRadius:2, background:LEVEL_COLOR[l] }} />
                <span style={{ fontSize:9, color:'#5a6a7e' }}>{t}</span>
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
          <Group title="Puissances relatives (Cohen 2014)" color="#4da6ff">
            <Cell label="δ Delta 0.5–4 Hz"  value={f4(f.rel_delta)} desc="Sommeil profond"   color="#818cf8" />
            <Cell label="θ Theta 4–8 Hz"    value={f4(f.rel_theta)} desc="Mémoire / rêverie" color="#f59e0b" />
            <Cell label="α Alpha 8–13 Hz"   value={f4(f.rel_alpha)} desc="Relaxation/alerte" color="#10b981" accent={f.rel_alpha > 0.3} />
            <Cell label="β Beta 13–30 Hz"   value={f4(f.rel_beta)}  desc="Cognition active"  color="#3b82f6" />
            <Cell label="γ Gamma 30–40 Hz"  value={f4(f.rel_gamma)} desc="Traitement haut"   color="#ef4444" />
          </Group>

          <Group title="Ratios cognitifs" color="#00e5b0">
            <Cell label="Engagement β/(α+θ)" value={f3(f.engagement)}  desc="EI Pope 1995"  accent={f.engagement > 1.5} />
            <Cell label="Stress β/α"          value={f3(f.stress_idx)} desc="Indice stress"  warn={f.stress_idx > 2} />
            <Cell label="θ/β (TDAH)"          value={f3(f.theta_beta)} desc="Relaxation" />
            <Cell label="α/β (Détente)"        value={f3(f.alpha_beta)} desc="Calme/Activé" />
          </Group>

          <Group title="Paramètres Hjorth (Cohen 2014 ch.17)" color="#a78bfa">
            <Cell label="Activity (Var)"    value={f4(f.hjorth_activity)}   desc="Amplitude²" />
            <Cell label="Mobility √(V1/V0)" value={f4(f.hjorth_mobility)}   desc="Fréquence moy." />
            <Cell label="Complexity"        value={f4(f.hjorth_complexity)} desc="Variation fréq." />
          </Group>

          <Group title="Analyse spectrale" color="#f472b6">
            <Cell label="SEF95 (Hz)"       value={f1(f.sef95)}            desc="95% énergie sous" />
            <Cell label="Entropie spec."   value={f4(f.spectral_entropy)} desc="Complexité PSD" />
            <Cell label="RMS (µV)"         value={f4(f.rms)}              desc="Amplitude eff." />
            <Cell label="Amp. moy. (µV)"   value={f4(f.mean_amp)} />
          </Group>

          <Group title="Distribution temporelle" color="#f59e0b">
            <Cell label="Skewness"  value={f4(f.skewness)} desc="Asymétrie" warn={Math.abs(f.skewness) > 2} />
            <Cell label="Kurtosis"  value={f4(f.kurtosis)} desc="Aplatissement" warn={f.kurtosis > 5} />
            <Cell label="ZCR"       value={f4(f.zcr)}      desc="Zero-crossing rate" />
          </Group>

          <Group title="PAC θ→γ (Tort et al. 2010)" color="#06b6d4">
            <Cell label="PAC θ→γ proxy" value={f4(f.pac_theta_gamma)} desc="Corrél. env.γ / phase θ" accent={f.pac_theta_gamma > 0.3} />
          </Group>

          <Group title="Dimension Fractale + Graphe (Al-Salman 2019)" color="#ec4899">
            <Cell label="FD global"       value={f4(f.fractal_dim)}         desc="Box-counting moyen" />
            <Cell label="Degree dist."    value={f4(f.fd_degree_dist_mean)} desc="Degré moyen graphe" />
            <Cell label="Clustering coef" value={f4(f.fd_clustering_coeff)} desc="Connectivité locale" />
            <Cell label="Jaccard moyen"   value={f4(f.fd_jaccard_mean)}     desc="Similarité voisins" />
          </Group>

          {f.db_alpha !== undefined && (
            <Group title="Puissance dB vs Baseline" color="#6ee7b7">
              {['delta','theta','alpha','beta','gamma'].map(b => (
                <Cell key={b} label={`${b} dB`} value={f3(f[`db_${b}`])} desc="vs baseline"
                  accent={f[`db_${b}`] > 1} warn={f[`db_${b}`] < -5} />
              ))}
            </Group>
          )}
        </>
      )}
    </div>
  )
}

// ── Conteneur de section guide ────────────────────────────────────────────────
function SectionGuide({ title, icon, desc, children }) {
  const [open, setOpen] = useState(true)
  return (
    <div style={{ background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)', borderRadius:14, overflow:'hidden' }}>
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width:'100%', padding:'12px 16px', background:'transparent', border:'none',
          cursor:'pointer', display:'flex', alignItems:'center', gap:8, textAlign:'left',
        }}
      >
        <span style={{ fontSize:16 }}>{icon}</span>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontFamily:"'Space Mono',monospace", fontSize:9, letterSpacing:1.5,
                        textTransform:'uppercase', color:'#6a7a8e' }}>{title}</div>
          {desc && <div style={{ fontSize:10, color:'#4a5a6e', marginTop:2 }}>{desc}</div>}
        </div>
        <span style={{ fontSize:12, color:'#3a4a5e', transition:'transform .2s',
                        transform: open ? 'rotate(90deg)' : 'rotate(0deg)' }}>▶</span>
      </button>
      {open && <div style={{ padding:'0 14px 14px' }}>{children}</div>}
    </div>
  )
}
