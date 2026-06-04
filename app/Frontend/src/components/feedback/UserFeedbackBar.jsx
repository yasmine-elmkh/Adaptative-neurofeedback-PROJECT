import { useState } from 'react'
import { ThumbsUp, ThumbsDown, SkipForward, Star } from 'lucide-react'

const EMOJIS = [
  { score: 1, emoji: '😞', label: 'Mal' },
  { score: 2, emoji: '😐', label: 'Neutre' },
  { score: 3, emoji: '😊', label: 'Bien' },
  { score: 4, emoji: '😄', label: 'Très bien' },
  { score: 5, emoji: '🤩', label: 'Excellent' },
]

export default function UserFeedbackBar({
  onSubmit,        // ({ liked, sam_score, note_concentration, note_stress }) => void
  onSkip,          // () => void
  canSkip = false,
  disabled = false,
}) {
  const [liked,          setLiked]          = useState(null)
  const [samScore,       setSamScore]       = useState(null)
  const [noteConc,       setNoteConc]       = useState(0)
  const [noteStress,     setNoteStress]     = useState(0)
  const [submitted,      setSubmitted]      = useState(false)

  function handleSubmit() {
    if (submitted || disabled) return
    setSubmitted(true)
    onSubmit?.({
      liked,
      sam_score:         samScore,
      note_concentration: noteConc || null,
      note_stress:        noteStress || null,
    })
  }

  if (submitted) return (
    <div className="flex items-center justify-center gap-2 py-3 text-emerald-400 text-sm font-medium">
      <span className="w-2 h-2 rounded-full bg-emerald-400" />
      Évaluation enregistrée
    </div>
  )

  return (
    <div className="space-y-3">
      {/* Ligne 1 : Like / Dislike + Émojis SAM + Skip */}
      <div className="flex items-center gap-4 flex-wrap">

        {/* Like / Dislike */}
        <div className="flex items-center gap-2">
          <button
            onClick={() => setLiked(liked === true ? null : true)}
            className={`p-2 rounded-xl border transition-all ${liked === true
              ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-400'
              : 'border-nc-border text-nc-muted hover:text-nc-text hover:bg-nc-surface2'}`}
          >
            <ThumbsUp className="w-4 h-4" />
          </button>
          <button
            onClick={() => setLiked(liked === false ? null : false)}
            className={`p-2 rounded-xl border transition-all ${liked === false
              ? 'bg-red-500/15 border-red-500/30 text-red-400'
              : 'border-nc-border text-nc-muted hover:text-nc-text hover:bg-nc-surface2'}`}
          >
            <ThumbsDown className="w-4 h-4" />
          </button>
        </div>

        {/* SAM émojis */}
        <div className="flex items-center gap-1">
          {EMOJIS.map(({ score, emoji, label }) => (
            <button
              key={score}
              onClick={() => setSamScore(samScore === score ? null : score)}
              title={label}
              className={`text-xl leading-none p-1 rounded-lg transition-all
                ${samScore === score
                  ? 'scale-125 opacity-100'
                  : 'opacity-50 hover:opacity-80 hover:scale-110'}`}
            >
              {emoji}
            </button>
          ))}
        </div>

        {/* Stars Focus */}
        <div className="flex items-center gap-1">
          <span className="text-[10px] text-nc-muted mr-1">Focus</span>
          {[1, 2, 3, 4, 5].map(n => (
            <button key={n} onClick={() => setNoteConc(noteConc === n ? 0 : n)}>
              <Star
                className={`w-3.5 h-3.5 transition-colors ${n <= noteConc ? 'text-yellow-400 fill-yellow-400' : 'text-nc-muted'}`}
              />
            </button>
          ))}
        </div>

        {/* Skip */}
        {canSkip && (
          <button
            onClick={onSkip}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium
                       border border-nc-border text-nc-muted hover:text-nc-text hover:bg-nc-surface2 transition-all ms-auto"
          >
            <SkipForward className="w-3.5 h-3.5" /> Passer
          </button>
        )}

        {/* Valider */}
        <button
          onClick={handleSubmit}
          disabled={disabled}
          className="flex items-center gap-1.5 px-4 py-1.5 rounded-xl text-xs font-semibold
                     bg-nc-accent/15 border border-nc-accent/30 text-nc-accent
                     hover:bg-nc-accent/25 transition-all disabled:opacity-40"
        >
          Évaluer
        </button>
      </div>
    </div>
  )
}
