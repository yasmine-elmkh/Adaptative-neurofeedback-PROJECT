// integration-temporaire/frontend-signal/src/lib/supabase.js
import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = "https://qwxkhkumyokzykykindv.supabase.co"
const SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eGtoa3VteW9renlreWtpbmR2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODY4NTYyMiwiZXhwIjoyMDk0MjYxNjIyfQ.t0TAfEJfgeMqmBXh2UwOT4kU0ukZKf7I7IvlwMKHNHQ"

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)

// ─── Mapping état EEG → catégorie médias ──────────────────────
export const EEG_TO_CAT = {
  stress:     'relax',
  relax:      'relax',
  focus:      'focus',
  distracted: 'focus',
  neutral:    'transition',
  transition: 'transition',
}

// ─── Thompson Sampling (JS pur) ───────────────────────────────
function gammaSample(shape) {
  if (shape < 1) return gammaSample(1 + shape) * Math.pow(Math.random(), 1 / shape)
  const d = shape - 1 / 3, c = 1 / Math.sqrt(9 * d)
  while (true) {
    let x, v
    do { x = randn(); v = 1 + c * x } while (v <= 0)
    v = v * v * v
    const u = Math.random()
    if (u < 1 - 0.0331 * x * x * x * x) return d * v
    if (Math.log(u) < 0.5 * x * x + d * (1 - v + Math.log(v))) return d * v
  }
}
function randn() {
  let u = 0, v = 0
  while (!u) u = Math.random()
  while (!v) v = Math.random()
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v)
}
function betaSample(alpha, beta) {
  const x = gammaSample(alpha), y = gammaSample(beta)
  return x / (x + y)
}

// ─── MÉDIAS ───────────────────────────────────────────────────

/**
 * Résout l'URL Cloudinary d'un filename retourné par le backend.
 * Utilisé par useFeedbackEngine pour enrichir les recommandations.
 */
export async function getMediaByFilename(filename) {
  if (!filename) return null
  const { data, error } = await supabase
    .from('medias')
    .select('*')
    .eq('filename', filename)
    .single()
  if (error) {
    console.warn('[Supabase] getMediaByFilename:', error.message)
    return null
  }
  return data
}

/**
 * Sélection Thompson Sampling parmi tous les médias d'une catégorie.
 * Utilisé en fallback si le backend n'est pas disponible.
 */
export async function getRecommandation(eegState, mediaType = null) {
  const cat = EEG_TO_CAT[eegState] || 'transition'
  let query = supabase.from('medias').select('*').eq('categorie', cat).eq('actif', true).limit(5000)
  if (mediaType) query = query.eq('type', mediaType)
  const { data: medias, error } = await query
  if (error) throw error
  if (!medias || medias.length === 0)
    throw new Error(`Aucun média pour ${cat}`)

  let best = null, bestScore = -1
  for (const m of medias) {
    const w = m.features?.ts_weights?.[cat] || { alpha: 1, beta: 1 }
    const score = betaSample(w.alpha, w.beta)
    if (score > bestScore) { bestScore = score; best = m }
  }
  return best
}

/**
 * Met à jour les poids Thompson Sampling après un feedback (liked/disliked).
 * @param {string|number} mediaId  — id de la ligne medias
 * @param {string}        eegState — état EEG lors de la recommandation
 * @param {boolean}       liked    — true = positif, false = négatif
 */
export async function updateMediaWeights(mediaId, eegState, liked) {
  if (mediaId == null) return
  const cat = EEG_TO_CAT[eegState] || 'transition'

  const { data: media } = await supabase
    .from('medias').select('features').eq('id', mediaId).single()
  if (!media) return

  const features = media.features || {}
  const ts = features.ts_weights || {}
  const cur = ts[cat] || { alpha: 1, beta: 1 }
  if (liked) cur.alpha += 1
  else        cur.beta  += 1
  ts[cat] = cur
  features.ts_weights = ts

  await supabase.from('medias').update({ features }).eq('id', mediaId)
}

/**
 * Liste tous les médias actifs (pour admin / débogage).
 */
export async function getAllMedias(categorie = null) {
  let query = supabase.from('medias').select('*').eq('actif', true).order('filename').limit(5000)
  if (categorie) query = query.eq('categorie', categorie)
  const { data, error } = await query
  if (error) throw error
  return data || []
}
