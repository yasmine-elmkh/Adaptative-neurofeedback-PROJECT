import { getMediaByFilename, updateMediaWeights, getRecommandation } from '../lib/supabase'

const API = '/api'

async function resolveMedia(action, eegState, mediaType = null) {
  if (!action) return null
  if (!action.filename) {
    const fallback = await getRecommandation(eegState, action.type || mediaType)
    if (!fallback) return null
    return { ...fallback, eeg_state: eegState, game_data: null, action: 'play' }
  }
  const media = await getMediaByFilename(action.filename)
  const base = media || { filename: action.filename, type: action.type || 'audio', url_cloudinary: null }
  return {
    ...base,
    type:      action.type || base.type,
    eeg_state: eegState,
    game_data: action.game || null,
    action:    'play',
  }
}

export function useFeedbackEngine() {

  const startSession = async (patientId, objective) => {
    try {
      const res = await fetch(`${API}/feedback/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patient_id: patientId, objective }),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || 'Erreur démarrage session')
      return data.session_id
    } catch (e) {
      // Fallback: generate a local session id
      console.warn('[FeedbackEngine] startSession fallback:', e.message)
      return `local_${Date.now()}`
    }
  }

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
      console.warn('[FeedbackEngine] recommend fallback Supabase:', e.message)
    }
    const fallback = await getRecommandation(eegState, mediaType)
    if (!fallback) return null
    return { ...fallback, eeg_state: eegState, game_data: null, action: 'play' }
  }

  const submitFeedback = async (sessionId, media, liked, ressenti, noteConc, noteStress) => {
    const filename = typeof media === 'string' ? media : (media?.filename || '')
    try {
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
    } catch (e) {
      console.warn('[FeedbackEngine] submitFeedback fallback:', e.message)
    }
    if (media?.id && media?.eeg_state !== undefined) {
      await updateMediaWeights(media.id, media.eeg_state, liked)
    }
  }

  const nextItem = async (sessionId, eegState, mediaType = null) => {
    try {
      const res = await fetch(`${API}/feedback/next`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      })
      if (!res.ok) throw new Error()
      const action = await res.json()
      return await resolveMedia(action, eegState || 'neutral', mediaType)
    } catch {
      return null
    }
  }

  const skipItem = async (sessionId, eegState, mediaType = null) => {
    try {
      const res = await fetch(`${API}/feedback/skip`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      })
      const data = await res.json()
      if (!data || data.status === 'no_action') return null
      return await resolveMedia(data, eegState || 'neutral', mediaType)
    } catch {
      return null
    }
  }

  const endSession = async (sessionId) => {
    try {
      const res = await fetch(`${API}/feedback/end`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId }),
      })
      return await res.json()
    } catch {
      return { duration_min: 0, history: [], items_played: 0 }
    }
  }

  const justify = async (mediaId, userId, eegState) => {
    if (mediaId == null) return null
    try {
      const res = await fetch(`${API}/feedback/justify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ media_id: mediaId, user_id: userId || 'anonymous', eeg_state: eegState || 'neutral' }),
      })
      if (!res.ok) return null
      return await res.json()
    } catch {
      return null
    }
  }

  return { startSession, recommend, submitFeedback, nextItem, skipItem, endSession, justify }
}
