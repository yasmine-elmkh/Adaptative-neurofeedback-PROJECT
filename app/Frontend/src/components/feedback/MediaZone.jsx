import { useState, useEffect, useRef } from 'react'
import AudioFeedback    from './AudioFeedback'
import ImageFeedback    from './ImageFeedback'
import VideoFeedback    from './VideoFeedback'
import GameFeedback     from './GameFeedback'
import IllusionFeedback from './IllusionFeedback'
import { SkipForward, Sparkles } from 'lucide-react'
import { feedback as fbApi } from '../../utils/api'

const MIN_SKIP_DELAY = {
  audio:    30,
  image:    10,
  video:    20,
  game:     60,
  illusion: 25,
}

const TYPE_ICON = { audio: '🎵', image: '🖼️', video: '🎬', game: '🎮', illusion: '🌀' }

export default function MediaZone({ media, eegState = 'neutral', sessionId, eegFeatures, onSkip, onMediaEnd, onGameWin }) {
  const [elapsed,   setElapsed]   = useState(0)
  const [canSkip,   setCanSkip]   = useState(false)
  const [guide,     setGuide]     = useState(null)
  const [guideVisible, setGuideVisible] = useState(false)
  const guideTimerRef = useRef(null)

  // Reset + fetch guide IA quand le média change
  useEffect(() => {
    if (!media) return
    setElapsed(0)
    setCanSkip(false)
    setGuide(null)
    setGuideVisible(false)
    clearTimeout(guideTimerRef.current)

    const minDelay = MIN_SKIP_DELAY[media.type] ?? 15
    const timer    = setInterval(() => {
      setElapsed(e => {
        const next = e + 1
        if (next >= minDelay) {
          setCanSkip(true)
          clearInterval(timer)
        }
        return next
      })
    }, 1000)

    // Fetch guide IA (si session connue)
    if (sessionId && media.id) {
      fbApi.guide(sessionId, media.id, eegState, eegFeatures)
        .then(res => {
          if (res?.guide) {
            setGuide(res.guide)
            // Afficher après 1.5s pour laisser le média charger
            guideTimerRef.current = setTimeout(() => setGuideVisible(true), 1500)
          }
        })
        .catch(() => {})
    }

    return () => {
      clearInterval(timer)
      clearTimeout(guideTimerRef.current)
    }
  }, [media?.id])

  if (!media) return (
    <div className="flex flex-col items-center justify-center gap-4 h-48 rounded-2xl border border-nc-border bg-nc-surface2/30">
      <div className="w-8 h-8 border-2 border-nc-accent/30 border-t-nc-accent rounded-full animate-spin" />
      <p className="text-sm text-nc-muted">En attente du premier média…</p>
    </div>
  )

  return (
    <div className="space-y-3">
      {/* Header média */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-lg">{TYPE_ICON[media.type] ?? '📄'}</span>
          <span className="text-xs font-medium text-nc-muted capitalize">{media.type}</span>
          <span className="text-xs text-nc-muted/50">· {media.filename?.replace(/\.[^.]+$/, '') ?? ''}</span>
        </div>

        {/* Bouton skip (apparaît après délai min) */}
        <button
          onClick={onSkip}
          disabled={!canSkip}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border transition-all
            ${canSkip
              ? 'border-nc-border text-nc-muted hover:text-nc-text hover:bg-nc-surface2 cursor-pointer'
              : 'border-transparent text-nc-muted/30 cursor-not-allowed'}`}
        >
          <SkipForward className="w-3.5 h-3.5" />
          {canSkip ? 'Passer' : `Passer (${MIN_SKIP_DELAY[media.type] - elapsed}s)`}
        </button>
      </div>

      {/* Rendu média selon type */}
      <div className="rounded-2xl overflow-hidden bg-nc-surface2/20 border border-nc-border/30">
        {media.type === 'audio' && (
          <div className="p-6">
            <AudioFeedback src={media.url_cloudinary || media.url} onEnded={onMediaEnd} />
          </div>
        )}
        {media.type === 'image' && (
          <ImageFeedback
            src={media.url_cloudinary || media.url}
            initialPreset={media.preset ?? 'Naturel'}
            eegState={eegState}
          />
        )}
        {media.type === 'video' && (
          <VideoFeedback src={media.url_cloudinary || media.url} onEnded={onMediaEnd} />
        )}
        {media.type === 'game' && (
          <div className="p-4">
            <GameFeedback
              game={media}
              eegState={eegState}
              onWin={onGameWin ?? onMediaEnd}
            />
          </div>
        )}
        {media.type === 'illusion' && (
          <div className="p-4">
            <IllusionFeedback
              eegState={eegState}
              onEnd={onMediaEnd}
            />
          </div>
        )}
      </div>

      {/* ── Guide IA personnalisé ── */}
      {guide && (
        <div className={`transition-all duration-700 ${guideVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'}`}>
          <div className="flex items-start gap-2.5 px-4 py-3 rounded-2xl
                          bg-nc-accent/8 border border-nc-accent/20">
            <Sparkles className="w-3.5 h-3.5 text-nc-accent shrink-0 mt-0.5" />
            <p className="text-xs text-nc-muted leading-relaxed">{guide}</p>
            <button
              onClick={() => setGuideVisible(false)}
              className="text-nc-muted/40 hover:text-nc-muted transition-colors shrink-0 ml-auto text-[10px]"
              title="Fermer le guide"
            >✕</button>
          </div>
        </div>
      )}
    </div>
  )
}
