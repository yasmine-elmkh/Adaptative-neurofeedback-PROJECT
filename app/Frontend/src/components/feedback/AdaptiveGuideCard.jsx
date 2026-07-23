import { useState, useEffect } from 'react'

const p = (v, d = 0) => { const n = parseFloat(v); return isNaN(n) ? d : n }

const STATE_COLOR = {
  stress:        { color: 'text-blue-400',    bg: 'bg-blue-500/8',    border: 'border-blue-500/20'    },
  concentration: { color: 'text-emerald-400', bg: 'bg-emerald-500/8', border: 'border-emerald-500/20' },
  neutral:       { color: 'text-purple-400',  bg: 'bg-purple-500/8',  border: 'border-purple-500/20'  },
}

// ── Générateurs par type ──────────────────────────────────────────────────────

function audioGuide(state, f) {
  const tempo     = p(f.tempo_bpm, 0)
  const centroid  = p(f.spec_centroid_mean, 1000)
  const eBass     = p(f.energy_bass, 0.3)
  const eMid      = p(f.energy_mid, 0.4)
  const harm      = p(f.harm_perc_ratio, 0.5)
  const rms       = p(f.rms_mean, 0.1)
  const condition = (f.condition || '').toLowerCase()

  const isNature    = tempo < 10
  const isSlow      = tempo >= 10 && tempo < 80
  const isFast      = tempo > 110
  const isBassHeavy = eBass > 0.5
  const isHarmonic  = harm > 0.65
  const isPercussive = harm < 0.4
  const isQuiet     = rms < 0.05

  const C = STATE_COLOR[state] ?? STATE_COLOR.neutral

  if (isNature || (isBassHeavy && isQuiet)) {
    return {
      icon: '🌿', title: `Son naturel / ambient${tempo > 0 ? ` — ${Math.round(tempo)} BPM` : ''}`, ...C,
      tip: `Son ambiant · énergie basses ${Math.round(eBass * 100)}% · centroïde ${Math.round(centroid)} Hz → activation des ondes alpha, réduction du cortisol (Thaut 1999).`,
      steps: [
        'Fermez les yeux — laissez le son remplir votre espace mental',
        'Respirez lentement en 4-7-8 (inspir 4s, hold 7s, expir 8s)',
        'Ne cherchez pas à analyser les sons — laissez l\'état venir',
        'Si une pensée distrait, revenez aux basses fréquences',
      ],
      science: `tempo=${Math.round(tempo)} BPM · centroïde=${Math.round(centroid)} Hz · bass=${Math.round(eBass * 100)}% · condition=${condition}`,
    }
  }

  if (isSlow && isHarmonic) {
    return {
      icon: '🎵', title: `Musique lente harmonique — ${Math.round(tempo)} BPM`, ...C,
      tip: `Tempo ${Math.round(tempo)} BPM · ratio harmonique ${Math.round(harm * 100)}% · centroïde ${Math.round(centroid)} Hz → synchronisation alpha/theta, relaxation profonde (Sammler 2007).`,
      steps: [
        `Laissez votre respiration se synchroniser au tempo de ${Math.round(tempo)} BPM naturellement`,
        'Focalisez sur les harmoniques — sons mélodiques plutôt que percussifs',
        'Évitez d\'analyser la mélodie — laissez l\'état émotionnel venir',
        `Énergie concentrée sur les ${isBassHeavy ? 'basses' : 'médiums'} — ${isBassHeavy ? 'ancrage' : 'équilibre'} cortical`,
      ],
      science: `tempo=${Math.round(tempo)} BPM · harm=${Math.round(harm * 100)}% · bass=${Math.round(eBass * 100)}% · mid=${Math.round(eMid * 100)}% · rms=${rms.toFixed(3)}`,
    }
  }

  if (isFast) {
    return {
      icon: '🎯', title: `Musique rythmée — ${Math.round(tempo)} BPM`, ...C,
      tip: `Tempo ${Math.round(tempo)} BPM · énergie médiums ${Math.round(eMid * 100)}% · ${isPercussive ? 'ratio percussif dominant' : `harmonique ${Math.round(harm * 100)}%`} → ancrage des oscillations beta frontales (Engel & Fries 2010).`,
      steps: [
        `Le rythme de ${Math.round(tempo)} BPM synchronise vos oscillations beta frontales`,
        'Gardez les yeux ouverts — restez en mode actif et concentré',
        'Laissez le tempo ancrer votre attention sans effort conscient',
        'Évaluez l\'impact sur votre concentration avec les étoiles',
      ],
      science: `tempo=${Math.round(tempo)} BPM · mid=${Math.round(eMid * 100)}% · harm=${Math.round(harm * 100)}% · rms=${rms.toFixed(3)} · condition=${condition}`,
    }
  }

  // Medium tempo / mixed
  return {
    icon: '🧠', title: `Audio adaptatif — ${Math.round(tempo)} BPM`, ...C,
    tip: `Tempo ${Math.round(tempo)} BPM · profil ${isHarmonic ? 'harmonique' : 'mixte'} · centroïde ${Math.round(centroid)} Hz → calibration de votre réponse EEG, prior Thompson Sampling.`,
    steps: [
      'Écoutez attentivement les différentes textures sonores',
      'Notez ce qui attire ou dérange votre attention',
      'Respirez normalement — ne forcez aucun état',
      'Chaque évaluation améliore la prochaine sélection adaptative',
    ],
    science: `tempo=${Math.round(tempo)} BPM · harm=${Math.round(harm * 100)}% · bass=${Math.round(eBass * 100)}% · mid=${Math.round(eMid * 100)}%`,
  }
}

function imageGuide(state, f) {
  const brightness  = p(f.brightness_mean, 0.5)
  const contrast    = p(f.contrast, 0.3)
  const edgeDensity = p(f.edge_density, 0.2)
  const saturation  = p(f.saturation_mean, 0.4)
  const warmCold    = p(f.warm_cold_ratio, 1)
  const symmetry    = p(f.symmetry, 0.5)
  const entropy     = p(f.entropy, 5)
  const condition   = (f.condition || '').toLowerCase()

  const isBright      = brightness > 0.6
  const isSimple      = edgeDensity < 0.12
  const isComplex     = edgeDensity > 0.30
  const isLowContrast = contrast < 0.25
  const isHighContrast = contrast > 0.5
  const isWarm        = warmCold > 1.2
  const isCool        = warmCold < 0.5
  const isSymmetric   = symmetry > 0.65

  const C = STATE_COLOR[state] ?? STATE_COLOR.neutral
  const toneDesc = isWarm ? 'teintes chaudes' : isCool ? 'teintes froides/bleues' : 'teintes neutres'

  if (isBright && isLowContrast && isSimple) {
    return {
      icon: '🌿', title: `Image apaisante — luminosité ${Math.round(brightness * 100)}%, faible contraste`, ...C,
      tip: `Luminosité ${Math.round(brightness * 100)}% · contraste ${Math.round(contrast * 100)}% · peu de bords (${Math.round(edgeDensity * 100)}%) · ${toneDesc} · symétrie ${Math.round(symmetry * 100)}% → réduction de l'arousal visuel, valence positive (Valdez & Mehrabian 1994, Berman 2014).`,
      steps: [
        'Balayez l\'image lentement — pas de fixation forcée sur un seul point',
        `Laissez votre regard sur les zones ${isBright ? 'lumineuses et douces' : 'harmonieuses'}`,
        'Évitez les saccades oculaires rapides — restez fluide',
        'Respirez 4s / 4s / 6s pendant que vous regardez',
      ],
      science: `brightness=${Math.round(brightness * 100)}% · contrast=${Math.round(contrast * 100)}% · edge=${Math.round(edgeDensity * 100)}% · symm=${Math.round(symmetry * 100)}% · warm_cold=${warmCold.toFixed(2)} · condition=${condition}`,
    }
  }

  if (isComplex || isHighContrast) {
    return {
      icon: '🔍', title: `Image de focalisation — ${isHighContrast ? `contraste ${Math.round(contrast * 100)}%` : `densité bords ${Math.round(edgeDensity * 100)}%`}`, ...C,
      tip: `Densité de bords ${Math.round(edgeDensity * 100)}% · contraste ${Math.round(contrast * 100)}% · entropie ${entropy.toFixed(1)} bits · ${toneDesc} → engagement attentionnel, activation gamma et circuits frontaux (Berman 2014).`,
      steps: [
        'Choisissez un détail précis et fixez-le pendant 5 secondes',
        'Cherchez les lignes directrices et les patterns de l\'image',
        isSymmetric ? 'Explorez la symétrie — elle structure l\'attention fovéale' : 'Identifiez les 3 zones d\'intérêt les plus saillantes',
        'Évaluez si l\'image soutient votre concentration active',
      ],
      science: `brightness=${Math.round(brightness * 100)}% · contrast=${Math.round(contrast * 100)}% · edge=${Math.round(edgeDensity * 100)}% · entropy=${entropy.toFixed(1)} · warm_cold=${warmCold.toFixed(2)} · condition=${condition}`,
    }
  }

  return {
    icon: '🧠', title: `Image de calibration — profil équilibré`, ...C,
    tip: `Luminosité ${Math.round(brightness * 100)}% · contraste ${Math.round(contrast * 100)}% · symétrie ${Math.round(symmetry * 100)}% · ${toneDesc} → exploration de votre réponse EEG aux stimuli visuels, calibration CBF cosine.`,
    steps: [
      'Observez l\'ensemble de l\'image pendant 10 secondes sans analyse',
      'Explorez ensuite les détails qui attirent naturellement votre regard',
      'Notez 3 éléments marquants dans votre tête',
      'Donnez votre ressenti honnête avec les étoiles',
    ],
    science: `brightness=${Math.round(brightness * 100)}% · contrast=${Math.round(contrast * 100)}% · edge=${Math.round(edgeDensity * 100)}% · symm=${Math.round(symmetry * 100)}% · condition=${condition}`,
  }
}

function videoGuide(state, f) {
  const flow       = p(f.optical_flow_mean, 1.5)
  const regularity = p(f.motion_regularity, 5)
  const sceneRate  = p(f.scene_change_rate, 0.1)
  const colorTemp  = p(f.color_temp_k, 4500)
  const brightness = p(f.brightness_mean, 0.5)
  const condition  = (f.condition || '').toLowerCase()

  // optical_flow_mean in this dataset is in pixel units (not normalized 0-1)
  const isSlowFlow = flow < 1.2
  const isFastFlow = flow > 3.5
  const isStable   = sceneRate < 0.05
  const isWarm     = colorTemp < 4200
  const isCool     = colorTemp > 5800
  const tempDesc   = isWarm ? 'chaude (apaisante)' : isCool ? 'froide (stimulante)' : 'neutre'

  const C = STATE_COLOR[state] ?? STATE_COLOR.neutral

  if (isSlowFlow && isStable) {
    return {
      icon: '🌊', title: `Vidéo apaisante — flux ${flow.toFixed(2)}, scènes stables`, ...C,
      tip: `Flux optique lent (${flow.toFixed(2)} px) · ${sceneRate < 0.01 ? 'aucun changement de scène' : `${Math.round(sceneRate * 60)} changements/min`} · température ${Math.round(colorTemp)} K ${tempDesc} → synchronisation visuo-respiratoire, réduction activation corticale (Grill-Spector 2001).`,
      steps: [
        'Laissez vos yeux suivre le mouvement sans effort actif',
        `Flux de ${flow.toFixed(2)} — respirez au rythme visuel perçu, lent et régulier`,
        'Évitez de cligner excessivement — regard doux et posé',
        'Si l\'esprit s\'emballe, revenez au mouvement à l\'écran',
      ],
      science: `optical_flow=${flow.toFixed(2)} · scene_rate=${sceneRate.toFixed(3)} · color_temp=${Math.round(colorTemp)} K · brightness=${Math.round(brightness * 100)}% · condition=${condition}`,
    }
  }

  if (isFastFlow) {
    return {
      icon: '🎬', title: `Vidéo de stimulation — flux ${flow.toFixed(2)}`, ...C,
      tip: `Flux optique élevé (${flow.toFixed(2)} px) · ${Math.round(sceneRate * 60)} changements/min · luminosité ${Math.round(brightness * 100)}% · température ${tempDesc} → engagement de l'attention soutenue, circuits frontaux et pariétaux.`,
      steps: [
        'Suivez activement chaque changement de scène et de mouvement',
        'Anticipez la prochaine transition visuelle',
        'Restez en mode observateur actif — pensée analytique',
        'Évaluez si la vidéo soutient votre flux de concentration',
      ],
      science: `optical_flow=${flow.toFixed(2)} · scene_rate=${sceneRate.toFixed(3)} · color_temp=${Math.round(colorTemp)} K · condition=${condition}`,
    }
  }

  return {
    icon: '🧠', title: `Vidéo adaptative — flux ${flow.toFixed(2)}`, ...C,
    tip: `Flux optique moyen (${flow.toFixed(2)} px) · régularité ${Math.round(regularity)} · température ${Math.round(colorTemp)} K ${tempDesc} → exploration de votre réponse EEG aux stimuli dynamiques.`,
    steps: [
      'Regardez naturellement, sans effort de concentration',
      'Notez si le contenu vous calme, stimule, ou est neutre',
      'Votre évaluation entraîne le moteur adaptatif en temps réel',
      'Utilisez "Passer" librement — le skip est une donnée utile',
    ],
    science: `optical_flow=${flow.toFixed(2)} · regularity=${Math.round(regularity)} · scene_rate=${sceneRate.toFixed(3)} · color_temp=${Math.round(colorTemp)} K · condition=${condition}`,
  }
}

function gameGuide(state, f, filename) {
  const folder    = (f.game_folder || '').toLowerCase()
  const prefix    = (filename || '').slice(0, 3).toLowerCase()

  let gf = {}
  try { gf = JSON.parse(f.features_json || '{}') } catch { /**/ }

  const level     = gf.game_level ?? gf.level ?? 1
  const diff      = (gf.difficulty || 'medium').toLowerCase()
  const cogLoad   = p(gf.cognitive_load, 0.5)
  const logic     = p(gf.logic_demand, 0.5)
  const memory    = p(gf.memory_demand, 0.3)
  const diffLabel = diff === 'easy' ? 'facile' : diff === 'hard' ? 'difficile' : 'moyen'

  const isEnigme    = folder.includes('enigme') || prefix === 'eni'
  const isColoriage = folder.includes('color') || prefix === 'col'
  const isSudoku    = folder.includes('sudoku') || prefix === 'sud'
  const isMemoire   = folder.includes('memo') || prefix === 'mem'

  const C = STATE_COLOR[state] ?? STATE_COLOR.neutral

  if (isEnigme) return {
    icon: '💡', title: `Énigme — Niveau ${level} (${diffLabel})`, ...C,
    tip: `Charge cognitive ${Math.round(cogLoad * 100)}% · logique ${Math.round(logic * 100)}% · mémoire ${Math.round(memory * 100)}% → activation préfrontale, décentrage des pensées ruminatives (Ochsner 2002).`,
    steps: [
      `Niveau ${diffLabel} — lisez l'énigme calmement, sans pression de temps`,
      'Inspirez profondément avant de répondre pour clarifier la réflexion',
      logic > 0.7 ? 'Raisonnez par étapes déductives successives' : 'Faites confiance à votre première intuition',
      'Si bloqué, passez : chaque skip affine la sélection adaptative',
    ],
    science: `folder=${f.game_folder} · level=${level} · difficulty=${diff} · cog_load=${Math.round(cogLoad * 100)}% · logic=${Math.round(logic * 100)}% · memory=${Math.round(memory * 100)}%`,
  }

  if (isColoriage) return {
    icon: '🎨', title: `Coloriage — Niveau ${level}`, ...C,
    tip: `Charge cognitive faible (${Math.round(cogLoad * 100)}%) · engagement moteur créatif → réduction de l'activation corticale, ancrage dans le présent (Clément 2015, Vygotsky 1978).`,
    steps: [
      'Remplissez chaque zone lentement — sans viser la perfection',
      'Focalisez sur le mouvement de coloration, pas sur le résultat',
      'Choisissez les couleurs instinctivement — laissez venir',
      'Si une erreur arrive, continuez — le process est thérapeutique',
    ],
    science: `folder=${f.game_folder} · level=${level} · cog_load=${Math.round(cogLoad * 100)}% · motor_skill=true`,
  }

  if (isSudoku) return {
    icon: '🔢', title: `Sudoku — Niveau ${level} (${diffLabel})`, ...C,
    tip: `Logique spatiale ${Math.round(logic * 100)}% · mémoire de travail ${Math.round(memory * 100)}% · charge cognitive ${Math.round(cogLoad * 100)}% → attention soutenue et WM multi-contrainte.`,
    steps: [
      'Commencez par les cases les plus contraintes — logique déductive',
      'Maintenez la carte mentale des lignes/colonnes/blocs complétés',
      'Respirez entre chaque décision — pas de précipitation',
      level >= 3 ? 'Planifiez 2-3 mouvements à l\'avance avant de placer' : 'Avancez case par case, validez avant de continuer',
    ],
    science: `folder=${f.game_folder} · level=${level} · logic=${Math.round(logic * 100)}% · memory=${Math.round(memory * 100)}% · cog_load=${Math.round(cogLoad * 100)}%`,
  }

  if (isMemoire) return {
    icon: '🃏', title: `Mémoire — Niveau ${level}`, ...C,
    tip: `Mémoire de travail ${Math.round(memory * 100)}% · charge cognitive ${Math.round(cogLoad * 100)}% → activation hippocampale, WM visuo-spatiale (Klingberg 2010).`,
    steps: [
      'Encodez activement : nommez mentalement chaque image 2-3 secondes',
      'Créez des associations visuelles entre les paires similaires',
      'Maintenez une image mentale de la position de chaque carte',
      memory > 0.6 ? 'Accélérez progressivement une fois les paires mémorisées' : 'Avancez à votre rythme naturel',
    ],
    science: `folder=${f.game_folder} · level=${level} · memory=${Math.round(memory * 100)}% · cog_load=${Math.round(cogLoad * 100)}%`,
  }

  return {
    icon: '🎮', title: `Jeu — Niveau ${level} (${diffLabel})`, ...C,
    tip: `Charge cognitive ${Math.round(cogLoad * 100)}% · logique ${Math.round(logic * 100)}% · mémoire ${Math.round(memory * 100)}% → engagement adaptatif.`,
    steps: [
      `Niveau ${diffLabel} — commencez à votre rythme naturel`,
      'Résolvez méthodiquement, une étape à la fois',
      'Le niveau s\'adapte automatiquement à vos performances',
      'Utilisez "Passer" librement si le jeu ne convient pas',
    ],
    science: `folder=${f.game_folder} · level=${level} · difficulty=${diff} · cog_load=${Math.round(cogLoad * 100)}%`,
  }
}

function generateGuide(state, mediaType, filename, features) {
  if (mediaType === 'audio') return audioGuide(state, features)
  if (mediaType === 'image') return imageGuide(state, features)
  if (mediaType === 'video') return videoGuide(state, features)
  if (mediaType === 'game')  return gameGuide(state, features, filename)
  return { icon: '🧠', title: 'Guide adaptatif', ...STATE_COLOR.neutral, tip: '', steps: [], science: '' }
}

// ── Composant ──────────────────────────────────────────────────────────────────
export default function AdaptiveGuideCard({ eegState, currentMedia, blockIndex }) {
  const [features, setFeatures] = useState(null)
  const [loading,  setLoading]  = useState(false)

  useEffect(() => {
    if (!currentMedia?.filename) { setFeatures(null); return }
    setLoading(true)
    setFeatures(null)
    fetch(`/api/media/features?filename=${encodeURIComponent(currentMedia.filename)}&slim=true`)
      .then(r => r.ok ? r.json() : null)
      .then(data => { setFeatures(data && !data.detail ? data : null); setLoading(false) })
      .catch(() => { setFeatures(null); setLoading(false) })
  }, [currentMedia?.filename])

  if (!currentMedia) return null

  const blockLabel = blockIndex < 2 ? 'Découverte' : blockIndex < 4 ? 'Apprentissage' : 'Consolidation'
  const typeLabel  = { audio: 'Audio', image: 'Image', video: 'Vidéo', game: 'Jeu' }[currentMedia.type] ?? '—'

  const g = features
    ? generateGuide(eegState, currentMedia.type, currentMedia.filename, features)
    : {
        icon: loading ? '⏳' : '🧠',
        title: loading ? 'Analyse du média…' : 'Guide adaptatif',
        ...STATE_COLOR[eegState] ?? STATE_COLOR.neutral,
        tip: loading ? '' : 'Features non disponibles pour ce média.',
        steps: [], science: '',
      }

  return (
    <div className={`card p-4 space-y-3 border ${g.border} ${g.bg}`}>
      <div className="flex items-center gap-2">
        <span className="text-base">{g.icon}</span>
        <p className={`text-xs font-bold ${g.color} flex-1 leading-snug`}>{g.title}</p>
        <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-nc-surface2 text-nc-muted/60 font-mono">
          IA Guide
        </span>
      </div>

      {g.tip && (
        <p className="text-[11px] text-nc-muted leading-relaxed">{g.tip}</p>
      )}

      {g.steps.length > 0 && (
        <div className="space-y-1.5">
          {g.steps.map((s, i) => (
            <div key={i} className="flex items-start gap-2">
              <span className={`text-[10px] font-bold ${g.color} shrink-0 tabular-nums`}>{i + 1}.</span>
              <span className="text-[11px] text-nc-muted leading-tight">{s}</span>
            </div>
          ))}
        </div>
      )}

      {g.science && (
        <div className="p-2 rounded-lg bg-nc-surface2/40 border border-nc-border/30">
          <p className="text-[9px] text-nc-muted/50 font-mono leading-snug break-all">{g.science}</p>
        </div>
      )}

      <div className="pt-1 border-t border-nc-border/30 flex items-center justify-between">
        <p className="text-[10px] text-nc-muted/60">
          Bloc {blockIndex + 1}/6 · {blockLabel} · {typeLabel}
        </p>
        <p className="text-[9px] text-nc-muted/40">Adaptatif · NeuroCap</p>
      </div>
    </div>
  )
}
