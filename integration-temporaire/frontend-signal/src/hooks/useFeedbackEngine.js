// hooks/useFeedbackEngine.js
import { getMediaByFilename, updateMediaWeights, getRecommandation } from '../lib/supabase'

const API = '/api'

/**
 * Enrichit une action backend (filename, type) avec les données Supabase (url_cloudinary, id, features).
 * Ajoute toujours un champ `action: 'play'` pour que FeedbackSession puisse détecter un media valide.
 * Si filename est null, tente un fallback Supabase par eegState + mediaType.
 */
async function resolveMedia(action, eegState, mediaType = null) {
  if (!action) return null

  // Filename manquant → fallback direct Supabase
  if (!action.filename) {
    const fallback = await getRecommandation(eegState, action.type || mediaType)
    if (!fallback) return null
    return { ...fallback, eeg_state: eegState, game_data: null, action: 'play' }
  }

  const media = await getMediaByFilename(action.filename)
  const base = media || {
    filename:      action.filename,
    type:          action.type || 'audio',
    url_cloudinary: null,
    cloudinary_url: null,
  }

  return {
    ...base,
    // Le type du backend fait autorité (il connaît le vrai type du fichier)
    type:      action.type || base.type,
    eeg_state: eegState,
    game_data: action.game || null,
    action:    'play',           // ← preserve pour le check dans FeedbackSession
  }
}

export function useFeedbackEngine() {

  const startSession = async (patientId, objective) => {
    const res = await fetch(`${API}/feedback/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ patient_id: patientId, objective }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.detail || 'Erreur démarrage session')
    return data.session_id
  }

  /**
   * Demande une recommandation au backend en respectant le type forcé.
   * Fallback sur Supabase si le backend échoue ou retourne un filename null.
   */
  const recommend = async (sessionId, eegState, features, mediaType = null) => {
    try {
      const res = await fetch(`${API}/feedback/recommend`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          eeg_state:  eegState,
          features:   features || {},
          media_type: mediaType,
        }),
      })
      if (!res.ok) throw new Error(`Backend ${res.status}`)
      const action = await res.json()
      const media  = await resolveMedia(action, eegState, mediaType)
      if (media) return media
    } catch (e) {
      console.warn('[FeedbackEngine] Backend recommend échoué, fallback Supabase:', e.message)
    }
    // Fallback direct Supabase
    const fallback = await getRecommandation(eegState, mediaType)
    if (!fallback) return null
    return { ...fallback, eeg_state: eegState, game_data: null, action: 'play' }
  }

  /**
   * Soumet un feedback utilisateur.
   * media peut être l'objet complet ou juste un string (filename).
   */
  const submitFeedback = async (sessionId, media, liked, ressenti, noteConc, noteStress) => {
    const filename = typeof media === 'string' ? media : (media?.filename || '')

    await fetch(`${API}/feedback/submit`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id:         sessionId,
        recommandation_id:  filename,
        liked,
        ressenti,
        note_concentration: noteConc,
        note_stress:        noteStress,
      }),
    })

    // Mise à jour Thompson Sampling dans Supabase (si objet complet disponible)
    if (media?.id && media?.eeg_state !== undefined) {
      await updateMediaWeights(media.id, media.eeg_state, liked)
    }
  }

  /**
   * Prochain item sans pénalité (après feedback soumis).
   * Toujours passer eegState pour que resolveMedia choisisse la bonne catégorie.
   */
  const nextItem = async (sessionId, eegState, mediaType = null) => {
    const res = await fetch(`${API}/feedback/next`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
    if (!res.ok) return null
    const action = await res.json()
    return await resolveMedia(action, eegState || 'neutral', mediaType)
  }

  const skipItem = async (sessionId, eegState, mediaType = null) => {
    const res = await fetch(`${API}/feedback/skip`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
    const data = await res.json()
    if (!data || data.status === 'no_action') return null
    return await resolveMedia(data, eegState || 'neutral', mediaType)
  }

  const endSession = async (sessionId) => {
    const res = await fetch(`${API}/feedback/end`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId }),
    })
    return await res.json()
  }

  /**
   * Justification dynamique + guide d'utilisation pour un média.
   * Retourne { justification, guide: [...], type } ou null si erreur.
   */
  const justify = async (mediaId, userId, eegState) => {
    if (mediaId == null) return null
    try {
      const res = await fetch(`${API}/feedback/justify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          media_id:  mediaId,
          user_id:   userId || 'anonymous',
          eeg_state: eegState || 'neutral',
        }),
      })
      if (!res.ok) return null
      return await res.json()
    } catch {
      return null
    }
  }

  return { startSession, recommend, submitFeedback, nextItem, skipItem, endSession, justify }
}
