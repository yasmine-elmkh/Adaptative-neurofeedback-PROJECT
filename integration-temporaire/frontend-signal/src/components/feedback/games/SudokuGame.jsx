// games/SudokuGame.jsx
// Sans gameData : 4×4 intégré EEG-adaptatif
// Avec gameData (SDK_NIVx.json) : 9×9 réel depuis Cloudinary
import { useState, useEffect } from 'react'

const P = { accent: '#B87B9E', text: '#2B2A4A', text2: '#9A8BAE', good: '#7BC4A0', bad: '#E87B9E' }

// ── Mode 4×4 intégré ─────────────────────────────────────────────────────────
const PUZZLES4 = {
  easy:   [1,2,0,4,  3,4,1,0,  2,0,4,1,  4,1,0,3],
  medium: [0,2,3,0,  3,0,0,2,  2,0,0,1,  0,1,2,0],
  hard:   [0,0,3,4,  0,0,0,2,  2,0,4,0,  4,0,0,0],
}
const SOL4 = [1,2,3,4, 3,4,1,2, 2,3,4,1, 4,1,2,3]

function diff4(eegState) {
  if (eegState === 'focus') return 'hard'
  if (eegState === 'stress') return 'easy'
  return 'medium'
}
function conflict4(grid, idx, val) {
  const row = Math.floor(idx / 4), col = idx % 4
  const br = Math.floor(row / 2) * 2, bc = Math.floor(col / 2) * 2
  for (let i = 0; i < 4; i++) {
    if (i !== col && grid[row*4+i] === val) return true
    if (i !== row && grid[i*4+col] === val) return true
  }
  for (let r = br; r < br+2; r++)
    for (let c = bc; c < bc+2; c++)
      if (r*4+c !== idx && grid[r*4+c] === val) return true
  return false
}

// ── Mode 9×9 Cloudinary ──────────────────────────────────────────────────────
function conflict9(grid, idx, val) {
  const row = Math.floor(idx / 9), col = idx % 9
  const br = Math.floor(row / 3) * 3, bc = Math.floor(col / 3) * 3
  for (let i = 0; i < 9; i++) {
    if (i !== col && grid[row*9+i] === val) return true
    if (i !== row && grid[i*9+col] === val) return true
  }
  for (let r = br; r < br+3; r++)
    for (let c = bc; c < bc+3; c++)
      if (r*9+c !== idx && grid[r*9+c] === val) return true
  return false
}

// ── Composant Sudoku 9×9 ─────────────────────────────────────────────────────
function Sudoku9({ gameData, onWin }) {
  const initial = gameData.puzzle
  const solution = gameData.solution
  const [grid,      setGrid]      = useState([...initial])
  const [selected,  setSelected]  = useState(null)
  const [won,       setWon]       = useState(false)
  const [conflicts, setConflicts] = useState(new Set())
  const [errors,    setErrors]    = useState(0)

  const reset = () => { setGrid([...initial]); setSelected(null); setWon(false); setConflicts(new Set()); setErrors(0) }

  const handleCell = (idx) => { if (initial[idx] === 0) setSelected(idx) }

  const handleNumber = (n) => {
    if (selected === null || won) return
    const next = [...grid]
    next[selected] = n
    const nc = new Set()
    next.forEach((v, i) => {
      if (v !== 0 && initial[i] === 0 && conflict9(next, i, v)) nc.add(i)
    })
    setGrid(next)
    setConflicts(nc)
    if (n !== 0 && solution[selected] !== n) setErrors(e => e + 1)
    if (next.every((v, i) => v === solution[i])) { setWon(true); onWin && onWin({ level: gameData.level, errors }) }
  }

  const filled = grid.filter((v, i) => v !== 0 && initial[i] === 0).length
  const total  = initial.filter(v => v === 0).length

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif", padding: '0.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: P.text2, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          Sudoku 9×9 — {gameData.label || 'Niv.' + gameData.level}
        </span>
        <div style={{ display: 'flex', gap: 10 }}>
          <span style={{ fontSize: 11, color: P.text2 }}>
            <b style={{ color: P.accent }}>{filled}</b>/{total}
          </span>
          {errors > 0 && <span style={{ fontSize: 11, color: P.bad }}>❌ {errors}</span>}
        </div>
      </div>

      {won && (
        <div style={{ textAlign: 'center', padding: '10px', marginBottom: 8, background: 'rgba(123,196,160,0.15)', borderRadius: 12, border: '1px solid rgba(123,196,160,0.4)', color: '#065F46', fontWeight: 700, fontSize: 14 }}>
          ✅ Sudoku résolu ! {errors === 0 ? '🏆 Sans erreur !' : `(${errors} erreurs)`}
        </div>
      )}

      {/* Grille 9×9 */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(9,1fr)', gap: 1, maxWidth: 310, margin: '0 auto 10px', background: 'rgba(184,123,158,0.3)', borderRadius: 8, padding: 2 }}>
        {grid.map((val, idx) => {
          const row = Math.floor(idx / 9), col = idx % 9
          const isFixed    = initial[idx] !== 0
          const isSelected = selected === idx
          const isConflict = conflicts.has(idx)
          const isSameBox  = selected !== null && Math.floor(Math.floor(selected/9)/3) === Math.floor(row/3) && Math.floor((selected%9)/3) === Math.floor(col/3)
          const thickR = (col === 2 || col === 5) ? '2px solid rgba(184,123,158,0.7)' : '1px solid rgba(184,123,158,0.15)'
          const thickB = (row === 2 || row === 5) ? '2px solid rgba(184,123,158,0.7)' : '1px solid rgba(184,123,158,0.15)'
          return (
            <div key={idx} onClick={() => handleCell(idx)} style={{
              width: '100%', aspectRatio: '1',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 13, fontWeight: isFixed ? 700 : 600,
              cursor: isFixed ? 'default' : 'pointer',
              background: isSelected    ? 'rgba(184,123,158,0.35)'
                        : isConflict    ? 'rgba(232,123,158,0.2)'
                        : isSameBox     ? 'rgba(184,123,158,0.08)'
                        : isFixed       ? 'rgba(255,255,255,0.7)'
                        : 'rgba(255,255,255,0.4)',
              color: isConflict ? P.bad : isFixed ? P.text : P.accent,
              borderRight: thickR, borderBottom: thickB,
              transition: 'background 0.1s',
              userSelect: 'none',
            }}>
              {val !== 0 ? val : ''}
            </div>
          )
        })}
      </div>

      {/* Pavé 1-9 */}
      <div style={{ display: 'flex', gap: 4, justifyContent: 'center', marginBottom: 8, flexWrap: 'wrap' }}>
        {[1,2,3,4,5,6,7,8,9].map(n => (
          <button key={n} onClick={() => handleNumber(n)} style={{
            width: 32, height: 32, borderRadius: 8, border: 'none',
            background: `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
            color: 'white', fontSize: 14, fontWeight: 700, cursor: 'pointer',
          }}>
            {n}
          </button>
        ))}
        <button onClick={() => handleNumber(0)} style={{
          width: 32, height: 32, borderRadius: 8, border: `1px solid rgba(184,123,158,0.3)`,
          background: 'rgba(255,255,255,0.4)', color: P.text2, fontSize: 12, cursor: 'pointer',
        }}>⌫</button>
      </div>

      <button onClick={reset} style={{
        width: '100%', padding: '7px', borderRadius: 10,
        background: 'rgba(255,255,255,0.3)', border: '1px solid rgba(184,123,158,0.2)',
        color: P.text2, fontSize: 12, cursor: 'pointer',
      }}>↺ Recommencer</button>
    </div>
  )
}

// ── Composant Sudoku 4×4 intégré ─────────────────────────────────────────────
function Sudoku4({ eegState, onWin }) {
  const diff    = diff4(eegState)
  const initial = PUZZLES4[diff]
  const [grid,      setGrid]      = useState([...initial])
  const [selected,  setSelected]  = useState(null)
  const [won,       setWon]       = useState(false)
  const [conflicts, setConflicts] = useState(new Set())

  useEffect(() => {
    const d = diff4(eegState)
    setGrid([...PUZZLES4[d]]); setSelected(null); setWon(false); setConflicts(new Set())
  }, [eegState])

  const handleCell = (idx) => { if (initial[idx] === 0) setSelected(idx) }
  const handleNumber = (n) => {
    if (selected === null) return
    const next = [...grid]
    next[selected] = n
    const nc = new Set()
    next.forEach((v, i) => { if (v !== 0 && initial[i] === 0 && conflict4(next, i, v)) nc.add(i) })
    setGrid(next); setConflicts(nc)
    if (next.every((v, i) => v === SOL4[i])) { setWon(true); onWin && onWin(diff) }
  }
  const reset = () => { setGrid([...initial]); setSelected(null); setWon(false); setConflicts(new Set()) }
  const DIFF_L = { easy: 'Facile', medium: 'Moyen', hard: 'Difficile' }

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif", padding: '0.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: P.text2, letterSpacing: 1.5, textTransform: 'uppercase' }}>Sudoku 4×4</span>
        <span style={{ fontSize: 10, fontWeight: 700, padding: '3px 10px', borderRadius: 20,
          background: diff === 'hard' ? 'rgba(232,123,158,0.15)' : diff === 'easy' ? 'rgba(123,196,160,0.15)' : 'rgba(184,123,158,0.15)',
          color: diff === 'hard' ? P.bad : diff === 'easy' ? P.good : P.accent,
          border: `1px solid ${diff === 'hard' ? 'rgba(232,123,158,0.4)' : diff === 'easy' ? 'rgba(123,196,160,0.4)' : 'rgba(184,123,158,0.3)'}`,
        }}>{DIFF_L[diff]}</span>
      </div>
      {won && <div style={{ textAlign: 'center', padding: '12px', marginBottom: 10, background: 'rgba(123,196,160,0.15)', borderRadius: 12, border: '1px solid rgba(123,196,160,0.4)', color: '#065F46', fontWeight: 700, fontSize: 15 }}>✅ Parfait ! Sudoku résolu !</div>}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 3, maxWidth: 220, margin: '0 auto 12px' }}>
        {grid.map((val, idx) => {
          const row = Math.floor(idx/4), col = idx%4
          const isFixed = initial[idx] !== 0, isSel = selected === idx, isConf = conflicts.has(idx)
          return (
            <div key={idx} onClick={() => handleCell(idx)} style={{
              width: 48, height: 48, display: 'flex', alignItems: 'center', justifyContent: 'center',
              borderRadius: 8, fontSize: 20, fontWeight: 700, cursor: isFixed ? 'default' : 'pointer',
              background: isSel ? 'rgba(184,123,158,0.25)' : isFixed ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.4)',
              color: isConf ? P.bad : isFixed ? P.text : P.accent,
              border: `1.5px solid ${isSel ? P.accent : isConf ? P.bad : 'rgba(184,123,158,0.2)'}`,
              borderRight: col === 1 ? '2px solid rgba(184,123,158,0.5)' : `1.5px solid rgba(184,123,158,0.2)`,
              borderBottom: row === 1 ? '2px solid rgba(184,123,158,0.5)' : `1.5px solid rgba(184,123,158,0.2)`,
              transition: 'all 0.15s',
            }}>{val !== 0 ? val : ''}</div>
          )
        })}
      </div>
      <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginBottom: 10 }}>
        {[1,2,3,4].map(n => (
          <button key={n} onClick={() => handleNumber(n)} style={{
            width: 44, height: 44, borderRadius: 10, border: 'none',
            background: `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
            color: 'white', fontSize: 18, fontWeight: 700, cursor: 'pointer',
          }}>{n}</button>
        ))}
        <button onClick={() => handleNumber(0)} style={{
          width: 44, height: 44, borderRadius: 10, border: '1.5px solid rgba(184,123,158,0.3)',
          background: 'rgba(255,255,255,0.4)', color: P.text2, fontSize: 14, cursor: 'pointer',
        }}>⌫</button>
      </div>
      <button onClick={reset} style={{ width: '100%', padding: '8px', borderRadius: 10, background: 'rgba(255,255,255,0.3)', border: '1px solid rgba(184,123,158,0.2)', color: P.text2, fontSize: 12, cursor: 'pointer' }}>↺ Recommencer</button>
    </div>
  )
}

// ── Export principal ──────────────────────────────────────────────────────────
export default function SudokuGame({ eegState, onWin, gameData }) {
  if (gameData?.puzzle?.length === 81)
    return <Sudoku9 gameData={gameData} onWin={onWin} />
  return <Sudoku4 eegState={eegState} onWin={onWin} />
}
