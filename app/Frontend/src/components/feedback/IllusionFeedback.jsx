import { useState, useEffect, useCallback } from 'react'

const EEG_BADGE_COLOR = {
  'Beta occipital V5':      '#6c63ff',
  'Alpha-Beta frontal':     '#43e97b',
  'Gamma parietal V5':      '#f9ca24',
  'Adaptation retinienne V5': '#43b0e9',
  'Orientation V1':         '#ff6584',
  'Gamma MT':               '#c0b0ff',
  'V4 couleur':             '#f7b267',
}

const EFFET_ICON = {
  focalisation:       '🎯',
  decentrage:         '🌊',
  relaxation_active:  '🍃',
}

export default function IllusionFeedback({ eegState = 'neutral', onEnd }) {
  const [illusions, setIllusions] = useState([])
  const [idx,       setIdx]       = useState(0)
  const [loading,   setLoading]   = useState(true)
  const [error,     setError]     = useState(null)
  const [elapsed,   setElapsed]   = useState(0)
  const [zoomed,    setZoomed]    = useState(false)

  const closeZoom = useCallback(() => setZoomed(false), [])
  useEffect(() => {
    if (!zoomed) return
    const handler = (e) => { if (e.key === 'Escape') closeZoom() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [zoomed, closeZoom])

  useEffect(() => {
    setLoading(true)
    setError(null)
    fetch(`/api/media/illusions/internal?eeg_state=${encodeURIComponent(eegState)}`)
      .then(r => r.ok ? r.json() : Promise.reject(r.status))
      .then(data => {
        if (!Array.isArray(data) || data.length === 0) {
          setError('Aucune illusion disponible pour cet état.')
          setIllusions([])
        } else {
          setIllusions(data)
          setIdx(0)
        }
        setLoading(false)
      })
      .catch(() => {
        setError('Impossible de charger les illusions.')
        setLoading(false)
      })
  }, [eegState])

  const current = illusions[idx] ?? null
  const duree   = parseInt(current?.duree_recommandee_s || 30, 10)
  const isLast  = idx === illusions.length - 1

  // Auto-avance : quand le timer atteint la durée, passe à la suivante ou termine
  useEffect(() => {
    setElapsed(0)
    if (!current) return
    const iv = setInterval(() => {
      setElapsed(e => {
        const next = e + 1
        if (next >= duree) {
          clearInterval(iv)
          if (isLast) {
            onEnd?.()
          } else {
            setIdx(i => i + 1)
          }
        }
        return next
      })
    }, 1000)
    return () => clearInterval(iv)
  }, [current?.id, duree, isLast])

  if (loading) return (
    <div style={{ textAlign: 'center', padding: '2.5rem', color: '#9A8BAE', fontFamily: "'Outfit',sans-serif" }}>
      <div style={{ fontSize: 22, marginBottom: 8 }}>🌀</div>
      Chargement des illusions…
    </div>
  )

  if (error || !current) return (
    <div style={{ textAlign: 'center', padding: '2rem', color: '#9A8BAE', fontFamily: "'Outfit',sans-serif", fontSize: 13 }}>
      {error ?? 'Aucune illusion disponible.'}
    </div>
  )

  const htmlSrc  = `/api/media/illusions/html/${encodeURIComponent(current.filename)}`
  const badge    = current.badge_eeg ?? ''
  const effet    = current.effet_cognitif ?? ''
  const titre    = current.titre ?? current.filename
  const progress = Math.min((elapsed / duree) * 100, 100)
  const remaining = Math.max(duree - elapsed, 0)

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif" }}>

      {/* ── Lightbox zoom ── */}
      {zoomed && (
        <div
          onClick={closeZoom}
          style={{
            position: 'fixed', inset: 0, zIndex: 9999,
            background: 'rgba(0,0,0,0.92)', backdropFilter: 'blur(8px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <iframe
            key={current.filename + '_zoom'}
            src={htmlSrc}
            sandbox="allow-scripts allow-same-origin"
            onClick={e => e.stopPropagation()}
            style={{
              width: '94vw', height: '90vh', border: 'none', display: 'block',
              borderRadius: 16, boxShadow: '0 8px 60px rgba(0,0,0,0.7)',
            }}
            title={titre}
          />
          <button
            onClick={closeZoom}
            style={{
              position: 'fixed', top: 18, right: 18,
              width: 36, height: 36, borderRadius: 10,
              background: 'rgba(40,30,60,0.9)', border: '1px solid rgba(255,255,255,0.15)',
              color: '#c0b0ff', fontSize: 16, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >✕</button>
        </div>
      )}

      {/* ── En-tête ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span style={{ fontSize: 13, fontWeight: 700, color: '#d0c0f0' }}>
          {EFFET_ICON[effet] ?? '🌀'} {titre}
        </span>
        <span style={{ fontSize: 9, color: '#7a6890' }}>
          {idx + 1} / {illusions.length}
        </span>
      </div>

      {/* ── Badges ── */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 10, flexWrap: 'wrap' }}>
        {badge && (
          <span style={{
            fontSize: 9, fontWeight: 700, padding: '3px 8px', borderRadius: 6,
            background: (EEG_BADGE_COLOR[badge] ?? '#6c63ff') + '22',
            border: `1px solid ${EEG_BADGE_COLOR[badge] ?? '#6c63ff'}55`,
            color: EEG_BADGE_COLOR[badge] ?? '#c0b0ff',
            letterSpacing: 0.5,
          }}>⚡ {badge}</span>
        )}
        {effet && (
          <span style={{
            fontSize: 9, fontWeight: 600, padding: '3px 8px', borderRadius: 6,
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.12)',
            color: '#9a8bb0',
          }}>{EFFET_ICON[effet] ?? ''} {effet.replace('_', ' ')}</span>
        )}
        <span style={{
          fontSize: 9, color: '#7a6890',
          padding: '3px 8px', borderRadius: 6,
          background: 'rgba(255,255,255,0.04)',
          border: '1px solid rgba(255,255,255,0.08)',
        }}>⏱ {remaining}s</span>
      </div>

      {/* ── iframe ── */}
      <div style={{ position: 'relative', borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(184,123,200,0.2)' }}>
        <iframe
          key={current.filename}
          src={htmlSrc}
          sandbox="allow-scripts allow-same-origin"
          style={{ width: '100%', height: 380, border: 'none', display: 'block' }}
          title={titre}
        />
        <button
          onClick={() => setZoomed(true)}
          title="Agrandir"
          style={{
            position: 'absolute', top: 8, left: 8,
            padding: '4px 10px', borderRadius: 6, fontSize: 10,
            background: 'rgba(20,16,30,0.75)',
            border: '1px solid rgba(184,123,200,0.4)',
            color: '#9a8bb0',
            cursor: 'pointer', backdropFilter: 'blur(4px)', fontWeight: 600,
          }}
        >⛶ Agrandir</button>
      </div>

      {/* ── Barre de progression auto ── */}
      <div style={{ marginTop: 10, height: 3, borderRadius: 2, background: 'rgba(255,255,255,0.07)', overflow: 'hidden' }}>
        <div style={{
          height: '100%', borderRadius: 2,
          width: progress + '%',
          background: 'linear-gradient(90deg,#6c63ff,#c07ae0)',
          transition: 'width 1s linear',
        }} />
      </div>
    </div>
  )
}
