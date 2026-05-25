// games/PuzzleGame.jsx — Taquin 3×3 adaptatif EEG
import { useState, useEffect, useCallback } from 'react'

const P = { accent: '#B87B9E', text: '#2B2A4A', text2: '#9A8BAE', good: '#7BC4A0', bad: '#E87B9E' }

function shuffle(tiles, moves) {
  const t = [...tiles]
  let blank = t.indexOf(0)
  const dirs = [-3, 3, -1, 1]
  for (let i = 0; i < moves; i++) {
    const row = Math.floor(blank / 3)
    const col = blank % 3
    const valid = dirs.filter(d => {
      const n = blank + d
      if (n < 0 || n > 8) return false
      if (d === -1 && col === 0) return false
      if (d ===  1 && col === 2) return false
      return true
    })
    const d = valid[Math.floor(Math.random() * valid.length)]
    t[blank] = t[blank + d]
    t[blank + d] = 0
    blank += d
  }
  return t
}

function isSolved(tiles) {
  return tiles.every((v, i) => v === (i === 8 ? 0 : i + 1))
}

function getShuffleMoves(eegState) {
  if (eegState === 'focus')  return 80
  if (eegState === 'stress') return 20
  return 40
}

export default function PuzzleGame({ eegState, onWin, gameData }) {
  const GOAL = [1, 2, 3, 4, 5, 6, 7, 8, 0]

  // gameData.n_pieces → déduit la difficulté (9=facile, 16=moyen, 25=hard)
  const derivedMoves = gameData?.n_pieces
    ? (gameData.n_pieces <= 9 ? 20 : gameData.n_pieces <= 16 ? 40 : 80)
    : getShuffleMoves(eegState)

  const buildPuzzle = useCallback(() =>
    shuffle([...GOAL], derivedMoves), [eegState, derivedMoves])

  const [tiles,  setTiles]  = useState(() => buildPuzzle())
  const [moves,  setMoves]  = useState(0)
  const [won,    setWon]    = useState(false)
  const [time,   setTime]   = useState(0)
  const [active, setActive] = useState(true)

  useEffect(() => {
    setTiles(buildPuzzle())
    setMoves(0)
    setWon(false)
    setTime(0)
    setActive(true)
  }, [eegState])

  useEffect(() => {
    if (!active || won) return
    const id = setInterval(() => setTime(t => t + 1), 1000)
    return () => clearInterval(id)
  }, [active, won])

  const handleTile = (idx) => {
    if (won) return
    const blank = tiles.indexOf(0)
    const row = Math.floor(idx / 3)
    const bRow = Math.floor(blank / 3)
    const col = idx % 3
    const bCol = blank % 3
    const adjacent = (Math.abs(row - bRow) + Math.abs(col - bCol)) === 1
    if (!adjacent) return
    const next = [...tiles]
    next[blank] = next[idx]
    next[idx] = 0
    setTiles(next)
    const m = moves + 1
    setMoves(m)
    if (isSolved(next)) {
      setWon(true)
      setActive(false)
      onWin && onWin({ moves: m, time })
    }
  }

  const reset = () => {
    setTiles(buildPuzzle())
    setMoves(0)
    setWon(false)
    setTime(0)
    setActive(true)
  }

  const formatTime = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`

  const DIFF_LABEL = { focus: 'Difficile', stress: 'Facile', neutral: 'Moyen', relax: 'Moyen', distracted: 'Facile' }

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif", padding: '0.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: P.text2, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          Taquin 3×3
        </span>
        <div style={{ display: 'flex', gap: 10 }}>
          <span style={{ fontSize: 11, color: P.text2 }}>⏱ <b style={{ color: P.accent }}>{formatTime(time)}</b></span>
          <span style={{ fontSize: 11, color: P.text2 }}>🔀 <b style={{ color: P.text }}>{moves}</b></span>
        </div>
      </div>

      <div style={{
        fontSize: 9, fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase',
        color: eegState === 'focus' ? P.bad : eegState === 'stress' ? P.good : P.accent,
        marginBottom: 8, textAlign: 'right'
      }}>
        {DIFF_LABEL[eegState] || 'Moyen'}
      </div>

      {won && (
        <div style={{ textAlign: 'center', padding: '12px', marginBottom: 10, background: 'rgba(123,196,160,0.15)', borderRadius: 12, border: '1px solid rgba(123,196,160,0.4)', color: '#065F46', fontWeight: 700, fontSize: 15 }}>
          🎉 Résolu en {moves} coups et {formatTime(time)} !
        </div>
      )}

      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 4, maxWidth: 220, margin: '0 auto 12px',
      }}>
        {tiles.map((val, idx) => (
          <div
            key={idx}
            onClick={() => handleTile(idx)}
            style={{
              aspectRatio: '1',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderRadius: 10, fontSize: 22, fontWeight: 700,
              cursor: val === 0 ? 'default' : 'pointer',
              background: val === 0
                ? 'rgba(184,123,158,0.08)'
                : won
                  ? 'rgba(123,196,160,0.2)'
                  : `linear-gradient(135deg, rgba(247,243,250,0.95), rgba(217,201,229,0.5))`,
              border: val === 0
                ? '1.5px dashed rgba(184,123,158,0.2)'
                : won
                  ? '1.5px solid rgba(123,196,160,0.5)'
                  : '1.5px solid rgba(184,123,158,0.25)',
              color: won ? '#065F46' : P.text,
              boxShadow: val !== 0 ? '0 2px 8px rgba(184,123,158,0.15)' : 'none',
              transition: 'all 0.15s',
              userSelect: 'none',
            }}
          >
            {val !== 0 ? val : ''}
          </div>
        ))}
      </div>

      <div style={{ fontSize: 11, color: P.text2, textAlign: 'center', marginBottom: 10 }}>
        Glissez les tuiles pour remettre <b>1→8</b> dans l'ordre
      </div>

      <button onClick={reset} style={{
        width: '100%', padding: '8px', borderRadius: 10,
        background: 'rgba(255,255,255,0.3)', border: '1px solid rgba(184,123,158,0.2)',
        color: P.text2, fontSize: 12, cursor: 'pointer',
      }}>
        ↺ Nouveau puzzle
      </button>
    </div>
  )
}
