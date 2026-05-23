// games/MemoryGame.jsx
// Sans gameData : appariement de cartes emoji EEG-adaptatif
// Avec gameData (MEM_NIVx.json) : rappel de séquence de chiffres
import { useState, useEffect, useCallback, useRef } from 'react'

const P = { accent: '#B87B9E', text: '#2B2A4A', text2: '#9A8BAE', good: '#7BC4A0', bad: '#E87B9E' }

// ── Mode rappel de séquence (Cloudinary) ──────────────────────────────────────
function SequenceRecall({ gameData, onWin }) {
  const seq       = gameData.sequence
  const displayMs = gameData.display_ms || 800
  const choices   = gameData.choices || [1,2,3,4,5,6,7,8,9]

  const [phase,     setPhase]     = useState('ready')   // ready | flash | recall | result
  const [flashIdx,  setFlashIdx]  = useState(0)
  const [userInput, setUserInput] = useState([])
  const [result,    setResult]    = useState(null)       // 'win' | 'fail'
  const timerRef = useRef(null)

  const startFlash = () => {
    setPhase('flash')
    setFlashIdx(0)
    setUserInput([])
    setResult(null)
  }

  // Avance dans la séquence flash
  useEffect(() => {
    if (phase !== 'flash') return
    if (flashIdx < seq.length) {
      timerRef.current = setTimeout(() => setFlashIdx(i => i + 1), displayMs)
    } else {
      timerRef.current = setTimeout(() => setPhase('recall'), 400)
    }
    return () => clearTimeout(timerRef.current)
  }, [phase, flashIdx])

  const handleChoice = (val) => {
    if (phase !== 'recall') return
    const next = [...userInput, val]
    setUserInput(next)
    if (next.length === seq.length) {
      const ok = next.every((v, i) => v === seq[i])
      setResult(ok ? 'win' : 'fail')
      setPhase('result')
      if (ok) onWin && onWin({ level: gameData.level, sequence: seq.length })
    }
  }

  const reset = () => { setPhase('ready'); setFlashIdx(0); setUserInput([]); setResult(null) }

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif", padding: '0.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: P.text2, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          Mémoire séquentielle — {gameData.label || 'Niv.' + gameData.level}
        </span>
        <span style={{ fontSize: 11, color: P.text2 }}>
          {seq.length} chiffres · {displayMs}ms
        </span>
      </div>

      {/* Phase : prêt */}
      {phase === 'ready' && (
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <div style={{ fontSize: 13, color: P.text2, marginBottom: 16 }}>
            Mémorisez la suite de <b>{seq.length} chiffres</b> affichés un par un.
          </div>
          <button onClick={startFlash} style={{
            padding: '12px 28px', borderRadius: 12, border: 'none',
            background: `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
            color: 'white', fontWeight: 700, fontSize: 14, cursor: 'pointer',
          }}>
            ▶ Démarrer
          </button>
        </div>
      )}

      {/* Phase : flash */}
      {phase === 'flash' && (
        <div style={{ textAlign: 'center', padding: '16px 0' }}>
          <div style={{ fontSize: 11, color: P.text2, marginBottom: 12 }}>
            {flashIdx < seq.length ? `Chiffre ${flashIdx + 1} / ${seq.length}` : 'Préparez-vous…'}
          </div>
          <div style={{
            width: 100, height: 100, borderRadius: 20, margin: '0 auto',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: flashIdx < seq.length
              ? `linear-gradient(135deg, ${P.accent}, #9A6B8E)`
              : 'rgba(184,123,158,0.1)',
            fontSize: 52, fontWeight: 800, color: 'white',
            boxShadow: flashIdx < seq.length ? `0 8px 24px rgba(184,123,158,0.4)` : 'none',
            transition: 'all 0.2s',
          }}>
            {flashIdx < seq.length ? seq[flashIdx] : '…'}
          </div>
          {/* Progress dots */}
          <div style={{ display: 'flex', gap: 4, justifyContent: 'center', marginTop: 14 }}>
            {seq.map((_, i) => (
              <div key={i} style={{
                width: 8, height: 8, borderRadius: '50%',
                background: i < flashIdx ? P.accent : 'rgba(184,123,158,0.2)',
                transition: 'background 0.2s',
              }} />
            ))}
          </div>
        </div>
      )}

      {/* Phase : rappel */}
      {phase === 'recall' && (
        <div>
          <div style={{ fontSize: 12, color: P.text2, textAlign: 'center', marginBottom: 12 }}>
            Reproduisez la séquence dans l'ordre — {userInput.length}/{seq.length}
          </div>
          {/* Saisie en cours */}
          <div style={{ display: 'flex', gap: 6, justifyContent: 'center', marginBottom: 14, minHeight: 40, flexWrap: 'wrap' }}>
            {seq.map((_, i) => (
              <div key={i} style={{
                width: 34, height: 34, borderRadius: 8,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                background: i < userInput.length ? `linear-gradient(135deg, ${P.accent}, #9A6B8E)` : 'rgba(184,123,158,0.1)',
                border: `1.5px solid ${i < userInput.length ? P.accent : 'rgba(184,123,158,0.25)'}`,
                color: 'white', fontWeight: 700, fontSize: 16,
              }}>
                {i < userInput.length ? userInput[i] : ''}
              </div>
            ))}
          </div>
          {/* Pavé de choix */}
          <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap' }}>
            {choices.map(v => (
              <button key={v} onClick={() => handleChoice(v)} style={{
                width: 40, height: 40, borderRadius: 10, border: 'none',
                background: `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
                color: 'white', fontSize: 16, fontWeight: 700, cursor: 'pointer',
              }}>{v}</button>
            ))}
            {userInput.length > 0 && (
              <button onClick={() => setUserInput(u => u.slice(0, -1))} style={{
                width: 40, height: 40, borderRadius: 10,
                border: '1.5px solid rgba(184,123,158,0.3)',
                background: 'rgba(255,255,255,0.4)', color: P.text2, fontSize: 14, cursor: 'pointer',
              }}>⌫</button>
            )}
          </div>
        </div>
      )}

      {/* Phase : résultat */}
      {phase === 'result' && (
        <div style={{ textAlign: 'center', padding: '16px 0' }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>{result === 'win' ? '🎉' : '😅'}</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: result === 'win' ? '#065F46' : P.bad, marginBottom: 8 }}>
            {result === 'win' ? 'Séquence correcte !' : 'Pas tout à fait…'}
          </div>
          {result === 'fail' && (
            <div style={{ fontSize: 12, color: P.text2, marginBottom: 12 }}>
              Séquence : <b style={{ color: P.accent }}>{seq.join(' – ')}</b>
              <br/>Votre réponse : <b style={{ color: P.bad }}>{userInput.join(' – ')}</b>
            </div>
          )}
          <button onClick={reset} style={{
            padding: '10px 24px', borderRadius: 12, border: 'none',
            background: `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
            color: 'white', fontWeight: 700, fontSize: 14, cursor: 'pointer',
          }}>↺ Réessayer</button>
        </div>
      )}
    </div>
  )
}

// ── Mode carte emoji intégré ──────────────────────────────────────────────────
const EMOJIS_POOL = ['🌸','🌊','🦋','🌙','⭐','🎵','🌿','🔮','🍃','🌺','🐬','🌈']

function buildCards(count) {
  const emojis = EMOJIS_POOL.slice(0, count / 2)
  const pairs  = [...emojis, ...emojis]
  for (let i = pairs.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [pairs[i], pairs[j]] = [pairs[j], pairs[i]]
  }
  return pairs.map((emoji, id) => ({ id, emoji, flipped: false, matched: false }))
}

function getDifficulty(eegState) {
  if (eegState === 'focus') return { count: 16, cols: 4, label: 'Difficile' }
  if (eegState === 'stress') return { count: 8,  cols: 4, label: 'Facile' }
  return { count: 12, cols: 4, label: 'Moyen' }
}

function CardMatch({ eegState, onWin }) {
  const diff = getDifficulty(eegState)
  const [cards,   setCards]   = useState(() => buildCards(diff.count))
  const [flipped, setFlipped] = useState([])
  const [locked,  setLocked]  = useState(false)
  const [moves,   setMoves]   = useState(0)
  const [won,     setWon]     = useState(false)

  const reset = useCallback(() => {
    const d = getDifficulty(eegState)
    setCards(buildCards(d.count)); setFlipped([]); setLocked(false); setMoves(0); setWon(false)
  }, [eegState])

  useEffect(() => { reset() }, [eegState])

  const handleFlip = (idx) => {
    if (locked || cards[idx].flipped || cards[idx].matched) return
    const nc = cards.map((c, i) => i === idx ? { ...c, flipped: true } : c)
    const nf = [...flipped, idx]
    setCards(nc); setFlipped(nf)
    if (nf.length === 2) {
      setLocked(true); setMoves(m => m + 1)
      const [a, b] = nf
      if (nc[a].emoji === nc[b].emoji) {
        setTimeout(() => {
          setCards(c => c.map((card, i) => i === a || i === b ? { ...card, matched: true } : card))
          setFlipped([]); setLocked(false)
        }, 600)
      } else {
        setTimeout(() => {
          setCards(c => c.map((card, i) => i === a || i === b ? { ...card, flipped: false } : card))
          setFlipped([]); setLocked(false)
        }, 1000)
      }
    }
  }

  useEffect(() => {
    if (cards.length > 0 && cards.every(c => c.matched)) { setWon(true); onWin && onWin(diff.label) }
  }, [cards])

  const matched = cards.filter(c => c.matched).length / 2

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif", padding: '0.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: P.text2, letterSpacing: 1.5, textTransform: 'uppercase' }}>Jeu de Mémoire</span>
        <div style={{ display: 'flex', gap: 8 }}>
          <span style={{ fontSize: 11, color: P.text2 }}>Coups: <b style={{ color: P.accent }}>{moves}</b></span>
          <span style={{ fontSize: 11, color: P.text2 }}>Paires: <b style={{ color: P.good }}>{matched}/{diff.count/2}</b></span>
        </div>
      </div>
      {won && <div style={{ textAlign: 'center', padding: '12px', marginBottom: 10, background: 'rgba(123,196,160,0.15)', borderRadius: 12, border: '1px solid rgba(123,196,160,0.4)', color: '#065F46', fontWeight: 700, fontSize: 15 }}>🎉 Toutes les paires trouvées en {moves} coups !</div>}
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${diff.cols}, 1fr)`, gap: 6, maxWidth: diff.count === 16 ? 280 : 210, margin: '0 auto 12px' }}>
        {cards.map((card, idx) => (
          <div key={card.id} onClick={() => handleFlip(idx)} style={{
            aspectRatio: '1', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: card.flipped || card.matched ? 22 : 14,
            cursor: card.matched ? 'default' : 'pointer',
            background: card.matched ? 'rgba(123,196,160,0.2)' : card.flipped ? 'rgba(247,243,250,0.9)' : `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
            border: `1.5px solid ${card.matched ? 'rgba(123,196,160,0.4)' : card.flipped ? 'rgba(184,123,158,0.3)' : 'transparent'}`,
            transition: 'all 0.3s', userSelect: 'none',
            color: card.matched ? '#065F46' : P.text,
          }}>
            {card.flipped || card.matched ? card.emoji : '?'}
          </div>
        ))}
      </div>
      <button onClick={reset} style={{ width: '100%', padding: '8px', borderRadius: 10, background: 'rgba(255,255,255,0.3)', border: '1px solid rgba(184,123,158,0.2)', color: P.text2, fontSize: 12, cursor: 'pointer' }}>↺ Nouvelle partie</button>
    </div>
  )
}

// ── Export principal ──────────────────────────────────────────────────────────
export default function MemoryGame({ eegState, onWin, gameData }) {
  if (gameData?.sequence)
    return <SequenceRecall gameData={gameData} onWin={onWin} />
  return <CardMatch eegState={eegState} onWin={onWin} />
}
