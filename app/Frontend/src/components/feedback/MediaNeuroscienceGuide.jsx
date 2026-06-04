import { useState, useEffect } from 'react'

/* ── Brain wave vocabulary (plain language) ─────────────────────────────────── */
const WAVES = {
  alpha: {
    name: 'Alpha', hz: '8–13 Hz', color: '#5BA85B', bg: 'rgba(91,168,91,0.12)', border: 'rgba(91,168,91,0.3)',
    feel: 'Calme éveillé',
    plain: 'Votre cerveau est détendu mais attentif — comme après une bonne respiration ou une promenade en nature.',
    icon: '🧘',
    meter: 'rel_alpha',
  },
  beta: {
    name: 'Beta', hz: '13–30 Hz', color: '#E8A020', bg: 'rgba(232,160,32,0.12)', border: 'rgba(232,160,32,0.3)',
    feel: 'Concentration active',
    plain: 'Votre cerveau est en mode "travail" — pensée analytique, résolution de problèmes, attention soutenue.',
    icon: '⚡',
    meter: 'rel_beta',
  },
  theta: {
    name: 'Theta', hz: '4–8 Hz', color: '#8B4EC2', bg: 'rgba(139,78,194,0.12)', border: 'rgba(139,78,194,0.3)',
    feel: 'Méditation / créativité',
    plain: 'Votre cerveau entre en mode créatif profond — idées intuitives, relaxation physique intense, rêverie consciente.',
    icon: '🌀',
    meter: 'rel_theta',
  },
  gamma: {
    name: 'Gamma', hz: '30–100 Hz', color: '#D94A4A', bg: 'rgba(217,74,74,0.12)', border: 'rgba(217,74,74,0.3)',
    feel: 'Traitement cognitif élevé',
    plain: 'Votre cerveau traite de l\'information complexe à haute vitesse — insight, apprentissage rapide, binding perceptif.',
    icon: '🧠',
    meter: null,
  },
}

/* ── Which wave does each media/state combination TARGET ─────────────────────── */
function getTarget(mediaType, eegState, mediaCategory) {
  const cat = (mediaCategory || '').toLowerCase()

  if (mediaType === 'audio') {
    if (eegState === 'stress')         return 'alpha'
    if (eegState === 'concentration')  return 'beta'
    return 'alpha'
  }
  if (mediaType === 'image') {
    if (eegState === 'stress')         return 'alpha'
    if (eegState === 'concentration')  return 'beta'
    return 'alpha'
  }
  if (mediaType === 'video') {
    if (eegState === 'stress')         return 'alpha'
    if (eegState === 'concentration')  return 'beta'
    return 'alpha'
  }
  if (mediaType === 'game') {
    if (cat.includes('colori') || cat.includes('color')) return 'alpha'
    if (cat.includes('calcul') || cat.includes('sudoku') || cat.includes('enigme')) return 'beta'
    if (cat.includes('memoire') || cat.includes('memory')) return 'beta'
    if (cat.includes('puzzle')) return eegState === 'stress' ? 'alpha' : 'beta'
    if (eegState === 'stress') return 'alpha'
    return 'beta'
  }
  return 'alpha'
}

/* ── Context-aware guide text ─────────────────────────────────────────────────── */
const CONTEXT = {
  audio: {
    stress: {
      why: 'Ce son a été sélectionné parce que votre cerveau montre des signes de suractivation (ondes bêta trop dominantes). Les fréquences basses et le tempo lent vont progressivement "ralentir" votre activité neurale.',
      how: ['Fermez les yeux si possible', 'Respirez lentement — 4 s inspirer, 6 s expirer', 'Laissez le son vous "porter" sans effort d\'analyse', 'Si votre esprit s\'emballe, revenez au son'],
      feature: 'tempo_bpm < 100 · energy_bass élevé · spec_centroid faible',
    },
    concentration: {
      why: 'Ce son a été choisi pour maintenir votre zone de concentration optimale. Le tempo modéré et la structure rythmique soutiennent l\'activité bêta sans surcharge cognitive.',
      how: ['Continuez votre activité normalement', 'Le son travaille en arrière-plan — ne l\'analysez pas', 'Si vous vous sentez distrait, baissez le volume mentalement', 'Évaluez : le son aide-t-il votre focus ?'],
      feature: 'tempo_bpm 100–140 · onset_strength modéré · spectral_stationarity élevé',
    },
    neutral: {
      why: 'Phase d\'exploration : le système mesure comment votre cerveau réagit à ce profil sonore spécifique pour calibrer vos préférences neurophysiologiques.',
      how: ['Écoutez attentivement pendant 30 secondes', 'Notez ce qui attire ou dérange (étoiles)', 'Respirez normalement — ne forcez rien', 'Chaque évaluation améliore la prochaine sélection'],
      feature: 'Calibration Thompson Sampling · prior informé features statiques',
    },
  },
  image: {
    stress: {
      why: 'Cette image a des caractéristiques visuelles (teinte douce, faible contraste, bords rares) qui activent le système parasympathique — l\'inverse de la réponse de stress.',
      how: ['Balayez l\'image lentement, sans fixer', 'Portez attention aux zones lumineuses et douces', 'Évitez les saccades rapides — mouvement oculaire fluide', 'Respirez 4/4/6 pendant que vous regardez'],
      feature: 'brightness 0.3–0.7 · edge_density < 0.15 · saturation < 0.5 · hue vert/bleu',
    },
    concentration: {
      why: 'Cette image stimule les réseaux d\'attention fovéale grâce à sa densité de bords et son contraste modéré. Elle engage le cortex visuel dorsal sans surcharger le système.',
      how: ['Choisissez un détail et fixez-le 5 secondes', 'Cherchez des patterns ou lignes directrices', 'Comptez mentalement des éléments si possible', 'Évaluez : l\'image soutient-elle votre concentration ?'],
      feature: 'edge_density > 0.15 · contrast 0.2–0.35 · saturation 0.5–0.8',
    },
    neutral: {
      why: 'L\'IA cartographie vos préférences visuelles. Votre réponse à cette image (hue, luminosité, texture) sera croisée avec votre signal EEG pour affiner les prochaines sélections.',
      how: ['Observez l\'ensemble pendant 10 secondes', 'Explorez les détails qui attirent votre regard', 'Donnez votre ressenti honnête avec les étoiles', 'Pas de bonne ou mauvaise réponse'],
      feature: 'Cosine similarity CBF · hue_mean · warm_cold_ratio · CNN PCA',
    },
  },
  video: {
    stress: {
      why: 'Ce flux vidéo lent et régulier synchronise votre système visuel avec un rythme alpha. Le mouvement prévisible "réinitialise" votre cortex surchargé.',
      how: ['Laissez vos yeux suivre le mouvement naturellement', 'Respirez au rythme visuel perçu — lent et régulier', 'Évitez de cligner excessivement', 'Si votre esprit s\'emballe, revenez au mouvement'],
      feature: 'optical_flow_mean < 4 · motion_regularity > 5 · scene_change_rate = 0',
    },
    concentration: {
      why: 'Ce contenu vidéo engage l\'attention soutenue via un flux optique modéré et des transitions contrôlées. Il maintient vos circuits frontaux actifs sans atteindre le seuil de distraction.',
      how: ['Suivez activement chaque changement de scène', 'Anticipez le prochain mouvement', 'Restez en mode "observateur actif"', 'Évaluez si la vidéo soutient votre flux'],
      feature: 'optical_flow_mean 3–7 · scene_change_rate 0.2–0.5 · edge_density_mean modéré',
    },
    neutral: {
      why: 'Phase d\'exploration visuelle : le moteur mesure votre réponse EEG à ce profil de mouvement et de couleur pour calibrer vos préférences vidéo.',
      how: ['Regardez naturellement, sans effort', 'Notez si le contenu vous calme ou vous stimule', 'Utilisez "Passer" librement — le skip est une donnée utile', 'Votre évaluation entraîne le moteur en temps réel'],
      feature: 'EEG delta 32s · optical_flow · color_temp_k · motion_regularity',
    },
  },
  game: {
    stress: {
      why: 'Ce jeu a été sélectionné pour son effet méditatif (coloriage, motifs simples). L\'attention portée au geste répétitif réduit l\'hyperactivité du DMN — effet similaire à la pleine conscience.',
      how: ['Remplissez chaque zone lentement', 'Focalisez sur le mouvement, pas le résultat', 'Choisissez les couleurs instinctivement', 'Si vous faites une erreur, continuez — le process est thérapeutique'],
      feature: 'cognitive_load faible · memory_demand faible · game_level 1–2',
    },
    concentration: {
      why: 'Ce jeu cognitif a été choisi selon votre delta_alpha EEG. Le niveau s\'adapte automatiquement : il monte si votre taux d\'erreur est < 20% et descend si > 60%.',
      how: ['Résolvez méthodiquement, une étape à la fois', 'Ne sautez pas d\'étapes — la progression est thérapeutique', 'Si bloqué, respirez et re-visualisez le problème', 'Le score n\'est pas l\'objectif — l\'engagement l\'est'],
      feature: 'cognitive_load élevé · logic_demand > 0.8 · game_level adaptatif (ZPD)',
    },
    neutral: {
      why: 'L\'IA explore vos préférences cognitives. Votre performance (error_rate, temps) sera croisée avec votre signal EEG pour sélectionner le type de jeu et le niveau optimal.',
      how: ['Jouez à votre rythme naturel', 'Ne forcez pas les performances', 'Évaluez honnêtement avec les étoiles', 'Chaque partie calibre le niveau suivant'],
      feature: 'Exploration Thompson Sampling · ratio α/β · error_rate · reaction_time',
    },
  },
}

function getContext(mediaType, eegState) {
  const t = mediaType || 'audio'
  const s = eegState || 'neutral'
  return CONTEXT[t]?.[s] || CONTEXT.audio.neutral
}

/* ── Simple wave meter ───────────────────────────────────────────────────────── */
function WaveMeter({ label, value, max = 60, color, isTarget, plain }) {
  const pct = Math.min(100, (value / max) * 100)
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
          <span style={{ fontSize: 10.5, fontWeight: isTarget ? 700 : 500, color: isTarget ? color : '#9a8bb0' }}>{label}</span>
          <span style={{ fontSize: 9, color: '#7a6890' }}>— {plain}</span>
        </div>
        <span style={{ fontSize: 10, fontFamily: 'monospace', color: isTarget ? color : '#7a6890', fontWeight: isTarget ? 700 : 400 }}>
          {value != null ? Math.round(value) + '%' : '—'}
        </span>
      </div>
      <div style={{ height: 5, borderRadius: 3, background: 'rgba(255,255,255,0.06)', overflow: 'hidden' }}>
        <div style={{
          width: pct + '%', height: '100%', borderRadius: 3,
          background: isTarget ? color : 'rgba(255,255,255,0.12)',
          transition: 'width 0.8s ease',
          boxShadow: isTarget ? `0 0 6px ${color}60` : 'none',
        }} />
      </div>
    </div>
  )
}

/* ── Target wave badge ───────────────────────────────────────────────────────── */
function TargetBadge({ wave }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10,
      background: wave.bg, border: `1px solid ${wave.border}`,
      borderRadius: 12, padding: '10px 14px', marginBottom: 10,
    }}>
      <div style={{
        width: 40, height: 40, borderRadius: 10, flexShrink: 0,
        background: `${wave.color}22`, border: `1.5px solid ${wave.color}50`,
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18,
      }}>{wave.icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 2 }}>
          <span style={{ fontSize: 12, fontWeight: 800, color: wave.color }}>Ondes {wave.name}</span>
          <span style={{ fontSize: 9, color: wave.color, background: `${wave.color}18`, border: `1px solid ${wave.color}40`, borderRadius: 8, padding: '1px 6px', fontFamily: 'monospace' }}>{wave.hz}</span>
        </div>
        <span style={{ fontSize: 11, fontWeight: 600, color: '#c0b8d0' }}>= {wave.feel}</span>
        <p style={{ fontSize: 10, color: '#9a8bb0', lineHeight: 1.55, marginTop: 3 }}>{wave.plain}</p>
      </div>
    </div>
  )
}

/* ═══════════════════════════════════════════════════════════════════════════════
   Main component
═══════════════════════════════════════════════════════════════════════════════ */
export default function MediaNeuroscienceGuide({ mediaType, eegState, mediaCategory, eegBands }) {
  const [showScience, setShowScience] = useState(false)

  const targetKey = getTarget(mediaType, eegState, mediaCategory)
  const wave      = WAVES[targetKey]
  const ctx       = getContext(mediaType, eegState)

  // Live band values (0–1 from backend → convert to %)
  const alpha = eegBands?.rel_alpha != null ? eegBands.rel_alpha * 100 : null
  const beta  = eegBands?.rel_beta  != null ? eegBands.rel_beta  * 100 : null
  const theta = eegBands?.rel_theta != null ? eegBands.rel_theta * 100 : null

  const typeLabel = { audio: '🎵 Audio', image: '🖼 Image', video: '🎬 Vidéo', game: '🎮 Jeu' }[mediaType] || '🔬 Média'
  const stateLabel = { stress: 'Stress détecté', concentration: 'Concentration', neutral: 'Exploration' }[eegState] || 'Neutre'

  return (
    <div style={{ borderRadius: 14, border: `1px solid ${wave.border}`, background: wave.bg, overflow: 'hidden', fontFamily: "'Outfit', sans-serif" }}>

      {/* ── Header ── */}
      <div style={{ padding: '10px 14px 0' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 10 }}>
          <span style={{ fontSize: 11, fontWeight: 700, color: wave.color, flex: 1 }}>Guide adaptatif</span>
          <span style={{ fontSize: 9, color: '#7a6890', background: 'rgba(255,255,255,0.06)', padding: '2px 7px', borderRadius: 6, border: '1px solid rgba(255,255,255,0.08)' }}>{typeLabel}</span>
          <span style={{ fontSize: 9, color: wave.color, background: `${wave.color}15`, padding: '2px 7px', borderRadius: 6, border: `1px solid ${wave.color}35` }}>{stateLabel}</span>
        </div>

        {/* Target wave — the key section */}
        <div style={{ marginBottom: 2 }}>
          <p style={{ fontSize: 9, color: '#7a6890', textTransform: 'uppercase', letterSpacing: 0.8, fontWeight: 700, marginBottom: 6 }}>Ce média cible</p>
          <TargetBadge wave={wave} />
        </div>
      </div>

      {/* ── Live EEG bands (only when data available) ── */}
      {(alpha != null || beta != null || theta != null) && (
        <div style={{ padding: '8px 14px', background: 'rgba(0,0,0,0.15)', borderTop: '1px solid rgba(255,255,255,0.05)', borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
          <p style={{ fontSize: 9, color: '#7a6890', textTransform: 'uppercase', letterSpacing: 0.8, fontWeight: 700, marginBottom: 7 }}>Votre cerveau maintenant</p>
          <WaveMeter label="Alpha" value={alpha} color={WAVES.alpha.color} isTarget={targetKey === 'alpha'} plain="calme éveillé" />
          <WaveMeter label="Beta"  value={beta}  color={WAVES.beta.color}  isTarget={targetKey === 'beta'}  plain="actif / concentré" />
          <WaveMeter label="Theta" value={theta} color={WAVES.theta.color} isTarget={targetKey === 'theta'} plain="méditatif / créatif" />
        </div>
      )}

      {/* ── Why this media ── */}
      <div style={{ padding: '10px 14px' }}>
        <p style={{ fontSize: 9, color: '#7a6890', textTransform: 'uppercase', letterSpacing: 0.8, fontWeight: 700, marginBottom: 5 }}>Pourquoi ce média pour vous ?</p>
        <p style={{ fontSize: 11, color: '#c0b8d0', lineHeight: 1.65, marginBottom: 10 }}>{ctx.why}</p>

        <p style={{ fontSize: 9, color: '#7a6890', textTransform: 'uppercase', letterSpacing: 0.8, fontWeight: 700, marginBottom: 5 }}>Ce que vous devez faire</p>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 5, marginBottom: 10 }}>
          {ctx.how.map((step, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
              <div style={{
                width: 18, height: 18, borderRadius: 5, flexShrink: 0,
                background: `${wave.color}22`, border: `1px solid ${wave.color}40`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 9, fontWeight: 800, color: wave.color,
              }}>{i + 1}</div>
              <span style={{ fontSize: 11, color: '#c0b8d0', lineHeight: 1.55, paddingTop: 1 }}>{step}</span>
            </div>
          ))}
        </div>

        {/* Expandable science detail */}
        <button
          onClick={() => setShowScience(s => !s)}
          style={{
            display: 'flex', alignItems: 'center', gap: 5, width: '100%',
            background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 8, padding: '6px 10px', cursor: 'pointer', textAlign: 'left',
          }}
        >
          <span style={{ fontSize: 10, color: '#7a6890', flex: 1 }}>🔬 Détail neuroscientifique</span>
          <span style={{ fontSize: 10, color: '#7a6890', transform: showScience ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }}>›</span>
        </button>

        {showScience && (
          <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
            {/* All 3 other waves explained simply */}
            {Object.entries(WAVES).filter(([k]) => k !== targetKey && k !== 'gamma').map(([k, w]) => (
              <div key={k} style={{ display: 'flex', gap: 8, padding: '6px 8px', borderRadius: 8, background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)' }}>
                <span style={{ fontSize: 14, flexShrink: 0 }}>{w.icon}</span>
                <div>
                  <span style={{ fontSize: 10, fontWeight: 700, color: w.color }}>{w.name} ({w.hz})</span>
                  <span style={{ fontSize: 9.5, color: '#9a8bb0', display: 'block', lineHeight: 1.5 }}>{w.plain}</span>
                </div>
              </div>
            ))}
            {/* Feature info */}
            <div style={{ background: 'rgba(0,0,0,0.2)', borderRadius: 8, padding: '6px 10px' }}>
              <p style={{ fontSize: 8.5, color: '#6a5880', fontFamily: 'monospace', lineHeight: 1.7 }}>
                📊 Features IA : {ctx.feature}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
