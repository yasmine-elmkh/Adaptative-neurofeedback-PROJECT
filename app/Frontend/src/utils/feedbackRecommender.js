/**
 * Règles de recommandation automatique de feedback EEG.
 * Aucun appel API — calcul 100% côté client.
 * Compatible avec les clés du backend (rel_alpha, theta_beta, engagement…)
 * et celles du format normalisé du prompt (alpha_power, tbr, ei…).
 *
 * Paramètre `palier` (1-4) contrôle les types disponibles :
 *   P1 : respiration + audio uniquement (Protocole — Phase Initiation)
 *   P2 : + visuel (images, vidéos)
 *   P3 : tout + jeux cognitifs
 *   P4 : feedback réduit — pas de jeux (phase Autonomie/transfert)
 */

// Types autorisés par palier (cohérent avec EEGFeedbackMode)
// illusion = illusions optiques HTML internes (Feedback_METADATA/illusions/)
const PALIER_ALLOWED = {
  1: ['breathing', 'audio'],
  2: ['breathing', 'audio', 'image', 'video'],
  3: ['breathing', 'audio', 'image', 'video', 'game', 'illusion'],
  4: ['breathing', 'audio', 'image'],
}

function getAllowed(palier) {
  return PALIER_ALLOWED[palier] ?? PALIER_ALLOWED[2]
}

// Force le type vers le meilleur autorisé si le candidat est bloqué
function applyPalierConstraint(candidate, palier) {
  const allowed = getAllowed(palier)
  if (allowed.includes(candidate.type)) return candidate

  // Remplacer par le meilleur équivalent autorisé
  if (candidate.type === 'game') {
    // Jeu → illusion (si disponible) ou image ou audio selon le palier
    const alt = allowed.includes('illusion') ? 'illusion'
              : allowed.includes('image')    ? 'image'
              : 'audio'
    return {
      ...candidate,
      type: alt,
      subtype: null,
      reason: candidate.reason +
        ` (Jeu non disponible au Palier ${palier} — feedback ${alt} sélectionné à la place.)`,
    }
  }
  if (candidate.type === 'illusion') {
    // Illusion → image ou audio si non autorisée
    const alt = allowed.includes('image') ? 'image' : 'audio'
    return {
      ...candidate,
      type: alt,
      subtype: alt === 'image' ? 'static' : null,
      reason: candidate.reason +
        ` (Illusion non disponible au Palier ${palier} — feedback ${alt} sélectionné.)`,
    }
  }
  if (candidate.type === 'video') {
    const alt = allowed.includes('image') ? 'image' : 'audio'
    return { ...candidate, type: alt, subtype: alt === 'image' ? 'static' : null }
  }
  // Fallback absolu
  return { ...candidate, type: allowed[0] ?? 'breathing', subtype: null }
}

export function recommendFeedback(eegState, features = {}, confidence = 0, palier = 2) {
  const tbr    = features.theta_beta   ?? features.tbr          ?? 0
  const ei     = features.engagement   ?? features.ei           ?? 0
  const alpha  = features.rel_alpha    ?? features.alpha_power  ?? 0
  const beta   = features.rel_beta     ?? features.beta_power   ?? 0
  const theta  = features.rel_theta    ?? features.theta_power  ?? 0
  const stress = features.stress_idx   ?? 0
  const rms    = features.rms_uv       ?? 0
  const conf   = confidence ?? 0

  const pct  = v => `${(v * 100).toFixed(1)}%`
  const f2   = v => v.toFixed(2)
  const stateLabel = { stress:'stress', stressed:'stress', concentration:'concentration', focused:'concentration' }[eegState] ?? 'neutre'

  const featureSummary = () =>
    `α ${pct(alpha)} · β ${pct(beta)} · θ ${pct(theta)} · TBR ${f2(tbr)} · EI ${f2(ei)}` +
    (rms > 0 ? ` · RMS ${rms.toFixed(1)} µV` : '') +
    (stress > 0 ? ` · Stress β/α ${f2(stress)}` : '')

  // ── 1. Confiance insuffisante ─────────────────────────────────────────────
  if (conf < 0.55) {
    return applyPalierConstraint({
      type:    'breathing',
      subtype: '4-4',
      reason:
        `Confiance de classification insuffisante (${Math.round(conf * 100)}% < 55%). ` +
        `Profil EEG actuel : ${featureSummary()}. ` +
        `Un exercice de respiration va stabiliser le signal avant d'approfondir l'analyse.`,
      guide:
        'Ferme les yeux. Inspire 4 s, expire 4 s. Laisse ton corps se stabiliser — la classification s\'améliorera.',
    }, palier)
  }

  // ── 2. Stress ─────────────────────────────────────────────────────────────
  if (eegState === 'stress' || eegState === 'stressed') {

    if (tbr > 2.5) {
      return applyPalierConstraint({
        type:    'breathing',
        subtype: '4-6',
        reason:
          `État ${stateLabel} confirmé à ${Math.round(conf * 100)}% de confiance. ` +
          `TBR élevé (${f2(tbr)} > 2.5) : ratio Theta/Beta pathologique signalant une activation corticale sous-optimale. ` +
          `${featureSummary()}. ` +
          `La respiration 4-6 active le nerf vague, réduit le cortisol et favorise la remontée de l'alpha.`,
        guide:
          'Inspire 4 secondes, expire 6 secondes. Sens tes épaules descendre à chaque expiration. Répète 5 cycles minimum.',
      }, palier)
    }

    if (stress > 2.5 || (beta > 0.38 && alpha < 0.18)) {
      return applyPalierConstraint({
        type:    'audio',
        subtype: null,
        reason:
          `État ${stateLabel} · Indice β/α élevé (${f2(stress)}) : beta largement dominant sur alpha. ` +
          `${featureSummary()}. ` +
          `Un fond sonore à basses fréquences (nature, binaural) abaisse l'activité du cortex préfrontal dorsolatéral et favorise la récupération alpha.`,
        guide:
          'Écoute sans chercher à analyser. Volume modéré, yeux mi-clos. Laisse le son occuper ton attention passivement.',
      }, palier)
    }

    return applyPalierConstraint({
      type:    'audio',
      subtype: null,
      reason:
        `État ${stateLabel} détecté (confiance ${Math.round(conf * 100)}%). ` +
        `${featureSummary()}. ` +
        `Un fond sonore apaisant favorise la déconnexion du mode par défaut et réduit l'activation corticale.`,
      guide:
        'Écoute sans chercher à analyser. Laisse le son occuper ton attention de façon passive.',
    }, palier)
  }

  // ── 3. Concentration ──────────────────────────────────────────────────────
  if (eegState === 'concentration' || eegState === 'focused') {

    if (ei > 0.75) {
      const subtype = tbr < 1.5 ? 'memory' : 'calcul'
      const gameName = subtype === 'memory' ? 'Mémoire' : 'Calcul mental'
      return applyPalierConstraint({
        type:    'game',
        subtype,
        reason:
          `État ${stateLabel} · EI élevé (${f2(ei)} > 0.75) : implication cognitive forte. ` +
          `TBR ${f2(tbr)} ${tbr < 1.5 ? '< 1.5 → mémoire spatiale' : '≥ 1.5 → calcul frontal'}. ` +
          `${featureSummary()}. ` +
          `Le jeu ${gameName} exploite l'état de flow actuel pour renforcer la neuroplasticité sans dépasser la zone proximale de développement.`,
        guide:
          "Joue en maintenant une attention douce — ni forcée, ni relâchée. Observe comment ton cerveau gère l'effort.",
      }, palier)
    }

    // Illusion figure-fond ou géométrique pour engagement cortical soutenu
    if (alpha > 0.20 && beta > 0.22) {
      return applyPalierConstraint({
        type:    'illusion',
        subtype: null,
        reason:
          `État ${stateLabel} · Alpha (${pct(alpha)}) + Beta (${pct(beta)}) co-actifs : engagement cortical soutenu sans surcharge. ` +
          `${featureSummary()}. ` +
          `Une illusion optique (distorsion / figure-fond) sollicite le cortex pariétal et préfrontal de façon contrôlée, renforçant la flexibilité attentionnelle.`,
        guide:
          "Fixe l'illusion sans forcer. Laisse ton cerveau percevoir les deux interprétations naturellement — c'est cet effort doux qui entraîne la plasticité.",
      }, palier)
    }

    if (alpha > 0.28 && beta > 0.20) {
      return applyPalierConstraint({
        type:    'image',
        subtype: 'static',
        reason:
          `État ${stateLabel} · Alpha soutenu (${pct(alpha)}) avec beta actif (${pct(beta)}) : équilibre relaxation-vigilance. ` +
          `${featureSummary()}. ` +
          `Une image calme et géométriquement riche soutient l'état alpha sans surcharger le cortex préfrontal (Berman et al., 2014).`,
        guide:
          "Fixe l'image sans effort. Laisse ton regard explorer librement pendant 1 à 2 minutes.",
      }, palier)
    }

    return applyPalierConstraint({
      type:    'game',
      subtype: 'puzzle',
      reason:
        `État ${stateLabel} modéré (EI ${f2(ei)}, alpha ${pct(alpha)}). ` +
        `${featureSummary()}. ` +
        `Un puzzle engage progressivement les réseaux fronto-pariétaux sans forcer une concentration intense.`,
      guide:
        "Prends ton temps. Il n'y a pas d'objectif de vitesse. L'important est de rester présent.",
    }, palier)
  }

  // ── 4. Incertain / neutre ─────────────────────────────────────────────────
  // Illusion de transition (mouvement perçu léger) pour engager progressivement
  if (palier >= 3) {
    return applyPalierConstraint({
      type:    'illusion',
      subtype: null,
      reason:
        `État incertain ou neutre (confiance ${Math.round(conf * 100)}%). ` +
        `${featureSummary()}. ` +
        `Une illusion optique de transition engage le cortex visuel passivement, aidant le système à cerner ton profil EEG sans sollicitation cognitive active.`,
      guide:
        "Regarde simplement. Aucun effort requis — laisse l'image faire son effet sur ton cerveau.",
    }, palier)
  }

  return applyPalierConstraint({
    type:    'game',
    subtype: 'puzzle',
    reason:
      `État incertain ou neutre (confiance ${Math.round(conf * 100)}%). ` +
      `${featureSummary()}. ` +
      `Un puzzle léger favorise l'engagement progressif et permet au système de mieux cerner ton profil cérébral sur les prochaines époques.`,
    guide:
      "Prends ton temps. Il n'y a pas d'objectif de vitesse. L'important est de rester présent.",
  }, palier)
}

/** Texte du guide par état EEG (affiché dans le panneau gauche). */
export function stateGuideText(eegState) {
  if (eegState === 'stress' || eegState === 'stressed') {
    return "Laisse ton regard se détendre. Suis le rythme respiratoire si affiché. Tu n'as rien à forcer — observe simplement ce qui se passe."
  }
  if (eegState === 'concentration' || eegState === 'focused') {
    return "Ton cerveau est en état actif. Engage-toi dans le contenu proposé avec une attention détendue. Ni trop tendu, ni distrait."
  }
  return "Prends un moment pour t'installer confortablement. Quelques respirations profondes avant de commencer."
}

/**
 * Guide contextuel pour un type de média donné selon l'état EEG.
 * Utilisé dans le panneau de sélection manuelle.
 */
export function getMediaGuidance(mediaType, eegState) {
  const guides = {
    audio: {
      stress:     "Sons < 70 BPM avec rythme binaural alpha/theta. Évitez les rythmes rapides (> 90 BPM).",
      focus:      "Sons rythmés 70-100 BPM, rythme binaural bêta pour maintenir l'engagement.",
      relax:      "Sons 60-80 BPM, rythme binaural alpha, enveloppe descendante.",
      transition: "Sons neutres 60-80 BPM. Laissez le système adapter progressivement.",
    },
    image: {
      stress:     "Images nature verte/bleue, faible saturation, horizon visible. Évitez rouge/orange.",
      focus:      "Images bleues/grises, complexité modérée, haute luminosité.",
      relax:      "Paysages naturels, saturation douce, présence d'horizon.",
      transition: "Images neutres, peu de complexité visuelle.",
    },
    illusion: {
      stress:     "Illusions douces uniquement (afterimage, couleur complémentaire). Évitez le mouvement perçu intense.",
      focus:      "Illusions figure-fond ou distorsions géométriques — entraînent la flexibilité cognitive.",
      relax:      "Illusions de mouvement lent ou afterimage. Durée : 20-35s.",
      transition: "Illusions légères (intensité ≤ 3), durée courte. Idéal pour sortir du stress.",
    },
    game: {
      stress:     "Jeux charge légère (1-2/5), récompense immédiate. Évitez les multi-tâches.",
      focus:      "Jeux charge 3-4/5, attention focalisée ou divisée.",
      relax:      "Jeux contemplatifs, charge 1-2/5, durée < 2 min.",
      transition: "Jeux d'inhibition ou de mémoire, charge modérée (2-3/5).",
    },
  }

  const stateKey = { stress: 'stress', stressed: 'stress', concentration: 'focus', focused: 'focus' }[eegState]
    ?? (eegState === 'relax' ? 'relax' : 'transition')

  return guides[mediaType]?.[stateKey] ?? "Sélection automatique selon votre état EEG."
}
