// games/CalculGame.jsx — Calcul mental adaptatif EEG
// Avec gameData (CAL_NIVx.json) : expression unique depuis Cloudinary
// Sans gameData : mode multi-rounds aléatoire EEG-adaptatif
import { useState, useEffect, useCallback, useRef } from 'react'

const P = { accent: '#B87B9E', text: '#2B2A4A', text2: '#9A8BAE', good: '#7BC4A0', bad: '#E87B9E' }

function makeChoices(answer) {
  const wrongs = new Set()
  while (wrongs.size < 3) {
    const delta = Math.floor(Math.random() * 6) + 1
    const w = answer + (Math.random() < 0.5 ? 1 : -1) * delta
    if (w !== answer && w > 0) wrongs.add(w)
  }
  return [...Array.from(wrongs), answer].sort(() => Math.random() - 0.5)
}

function SingleCalc({ gameData, onWin }) {
  const answer  = gameData.reponse_attendue
  const [choices]  = useState(() => makeChoices(answer))
  const [chosen,   setChosen]  = useState(null)

  const handleAnswer = (val) => {
    if (chosen !== null) return
    setChosen(val)
    if (val === answer) setTimeout(() => onWin && onWin({ level: gameData.level }), 900)
  }

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif", padding: '0.5rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: P.text2, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          Calcul — {gameData.label || 'Niv.' + gameData.level}
        </span>
        <span style={{ fontSize: 10, color: P.text2 }}>
          {gameData.features?.operation_type?.replace(/_/g,' ') || ''}
        </span>
      </div>

      <div style={{
        background: `linear-gradient(135deg, rgba(184,123,158,0.12), rgba(154,107,142,0.08))`,
        borderRadius: 16, padding: '24px', marginBottom: 16,
        border: '1px solid rgba(184,123,158,0.25)', textAlign: 'center',
      }}>
        <span style={{ fontSize: 36, fontWeight: 800, color: P.text, letterSpacing: 2 }}>
          {gameData.expression} = ?
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
        {choices.map((val, i) => {
          const isCorrect = val === answer
          const isChosen  = chosen === val
          let bg = 'rgba(255,255,255,0.4)', border = '1px solid rgba(184,123,158,0.2)', color = P.text
          if (chosen !== null) {
            if (isCorrect)     { bg = 'rgba(123,196,160,0.2)'; border = `1px solid ${P.good}`; color = '#065F46' }
            else if (isChosen) { bg = 'rgba(232,123,158,0.15)'; border = `1px solid ${P.bad}`; color = '#991B1B' }
          }
          return (
            <button key={i} onClick={() => handleAnswer(val)} style={{
              padding: '16px 10px', borderRadius: 12, cursor: chosen !== null ? 'default' : 'pointer',
              background: bg, border, color, fontSize: 22, fontWeight: 700, transition: 'all 0.2s',
            }}>
              {chosen !== null && isCorrect ? '✅ ' : chosen !== null && isChosen && !isCorrect ? '❌ ' : ''}
              {val}
            </button>
          )
        })}
      </div>

      {chosen !== null && chosen !== answer && (
        <div style={{ marginTop: 10, padding: '8px 12px', borderRadius: 10, background: 'rgba(123,196,160,0.1)', border: '1px solid rgba(123,196,160,0.3)', fontSize: 12, color: '#065F46', textAlign: 'center' }}>
          La réponse était <b>{answer}</b>
        </div>
      )}
    </div>
  )
}

function getConfig(eegState) {
  if (eegState === 'focus')  return { ops: ['+', '-', '×', '÷'], maxN: 12, timer: 8,  rounds: 8,  label: 'Expert' }
  if (eegState === 'stress') return { ops: ['+', '-'],           maxN: 10, timer: 15, rounds: 5,  label: 'Facile' }
  return                            { ops: ['+', '-', '×'],      maxN: 10, timer: 10, rounds: 6,  label: 'Moyen'  }
}

function generateQ(ops, maxN) {
  const op = ops[Math.floor(Math.random() * ops.length)]
  let a, b, answer
  if (op === '+') {
    a = 1 + Math.floor(Math.random() * maxN)
    b = 1 + Math.floor(Math.random() * maxN)
    answer = a + b
  } else if (op === '-') {
    b = 1 + Math.floor(Math.random() * maxN)
    a = b + Math.floor(Math.random() * maxN)
    answer = a - b
  } else if (op === '×') {
    a = 2 + Math.floor(Math.random() * (Math.min(maxN, 9) - 1))
    b = 2 + Math.floor(Math.random() * (Math.min(maxN, 9) - 1))
    answer = a * b
  } else {
    b = 1 + Math.floor(Math.random() * 9)
    answer = 1 + Math.floor(Math.random() * 9)
    a = b * answer
  }
  // 3 wrong choices
  const wrongs = new Set()
  while (wrongs.size < 3) {
    const delta = Math.floor(Math.random() * 5) + 1
    const sign = Math.random() < 0.5 ? 1 : -1
    const w = answer + sign * delta
    if (w !== answer && w > 0) wrongs.add(w)
  }
  const choices = [...Array.from(wrongs), answer].sort(() => Math.random() - 0.5)
  return { a, b, op, answer, choices }
}

function MultiRoundCalc({ eegState, onWin }) {
  const cfg = getConfig(eegState)
  const [q,       setQ]       = useState(() => generateQ(cfg.ops, cfg.maxN))
  const [chosen,  setChosen]  = useState(null)
  const [score,   setScore]   = useState(0)
  const [round,   setRound]   = useState(0)
  const [timeLeft, setTimeLeft] = useState(cfg.timer)
  const [done,    setDone]    = useState(false)
  const [streak,  setStreak]  = useState(0)
  const timerRef = useRef(null)

  const nextQ = useCallback((newScore, newRound, newStreak) => {
    setChosen(null)
    if (newRound >= cfg.rounds) {
      setDone(true)
      onWin && onWin(newScore)
      return
    }
    setQ(generateQ(cfg.ops, cfg.maxN))
    setTimeLeft(cfg.timer)
    setScore(newScore)
    setRound(newRound)
    setStreak(newStreak)
  }, [cfg])

  // Timer countdown
  useEffect(() => {
    if (done || chosen !== null) return
    timerRef.current = setTimeout(() => {
      if (timeLeft <= 1) {
        setChosen(-1) // timeout = wrong
        setStreak(0)
        setTimeout(() => nextQ(score, round + 1, 0), 1200)
      } else {
        setTimeLeft(t => t - 1)
      }
    }, 1000)
    return () => clearTimeout(timerRef.current)
  }, [timeLeft, done, chosen])

  // Reset on eegState change
  useEffect(() => {
    const c = getConfig(eegState)
    setQ(generateQ(c.ops, c.maxN))
    setChosen(null)
    setScore(0)
    setRound(0)
    setTimeLeft(c.timer)
    setDone(false)
    setStreak(0)
  }, [eegState])

  const handleAnswer = (val) => {
    if (chosen !== null || done) return
    clearTimeout(timerRef.current)
    setChosen(val)
    const correct = val === q.answer
    const newScore = score + (correct ? 1 : 0)
    const newStreak = correct ? streak + 1 : 0
    setTimeout(() => nextQ(newScore, round + 1, newStreak), 1000)
  }

  const reset = () => {
    const c = getConfig(eegState)
    setQ(generateQ(c.ops, c.maxN))
    setChosen(null)
    setScore(0)
    setRound(0)
    setTimeLeft(c.timer)
    setDone(false)
    setStreak(0)
  }

  const timerPct = (timeLeft / cfg.timer) * 100
  const timerColor = timerPct > 50 ? P.good : timerPct > 25 ? '#F59E0B' : P.bad

  if (done) return (
    <div style={{ fontFamily: "'Outfit',sans-serif", textAlign: 'center', padding: '1.5rem' }}>
      <div style={{ fontSize: 40, marginBottom: 8 }}>
        {score >= cfg.rounds * 0.8 ? '🏆' : score >= cfg.rounds * 0.5 ? '🌟' : '💪'}
      </div>
      <div style={{ fontSize: 18, fontWeight: 700, color: P.text, marginBottom: 6 }}>
        {score} / {cfg.rounds} bonnes réponses
      </div>
      <div style={{ fontSize: 13, color: P.text2, marginBottom: 16 }}>
        {score >= cfg.rounds * 0.8 ? 'Calcul mental excellent !' : score >= cfg.rounds * 0.5 ? 'Bonne concentration !' : 'Entraîne-toi encore !'}
      </div>
      <button onClick={reset} style={{
        padding: '10px 24px', borderRadius: 12, border: 'none',
        background: `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
        color: 'white', fontWeight: 700, fontSize: 14, cursor: 'pointer',
      }}>
        Rejouer
      </button>
    </div>
  )

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif", padding: '0.5rem' }}>
      {/* En-tête */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: P.text2, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          Calcul Mental ({round}/{cfg.rounds})
        </span>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          {streak >= 2 && <span style={{ fontSize: 11, color: '#F59E0B', fontWeight: 700 }}>🔥×{streak}</span>}
          <span style={{ fontSize: 12, color: P.good, fontWeight: 700 }}>Score: {score}</span>
        </div>
      </div>

      {/* Barre de progression rounds */}
      <div style={{ height: 4, background: 'rgba(184,123,158,0.15)', borderRadius: 2, marginBottom: 12, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${(round / cfg.rounds) * 100}%`, background: P.accent, borderRadius: 2, transition: 'width 0.3s' }} />
      </div>

      {/* Timer */}
      <div style={{ marginBottom: 14 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
          <span style={{ fontSize: 10, color: P.text2 }}>Temps restant</span>
          <span style={{ fontSize: 12, fontWeight: 700, color: timerColor }}>{timeLeft}s</span>
        </div>
        <div style={{ height: 5, background: 'rgba(0,0,0,0.08)', borderRadius: 3, overflow: 'hidden' }}>
          <div style={{
            height: '100%', width: `${timerPct}%`, borderRadius: 3,
            background: timerColor, transition: 'width 1s linear, background 0.5s',
          }} />
        </div>
      </div>

      {/* Question */}
      <div style={{
        background: `linear-gradient(135deg, rgba(184,123,158,0.12), rgba(154,107,142,0.08))`,
        borderRadius: 16, padding: '20px', marginBottom: 14,
        border: '1px solid rgba(184,123,158,0.25)', textAlign: 'center',
      }}>
        <span style={{ fontSize: 32, fontWeight: 800, color: P.text, letterSpacing: 2 }}>
          {q.a} {q.op} {q.b} = ?
        </span>
      </div>

      {/* Choix */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 8 }}>
        {q.choices.map((val, i) => {
          const isCorrect = val === q.answer
          const isChosen  = chosen === val
          const isTimeout = chosen === -1
          let bg = 'rgba(255,255,255,0.4)'
          let border = '1px solid rgba(184,123,158,0.2)'
          let color = P.text
          if (chosen !== null && !isTimeout) {
            if (isCorrect)       { bg = 'rgba(123,196,160,0.2)'; border = `1px solid ${P.good}`; color = '#065F46' }
            else if (isChosen)   { bg = 'rgba(232,123,158,0.15)'; border = `1px solid ${P.bad}`; color = '#991B1B' }
          } else if (isTimeout && isCorrect) {
            bg = 'rgba(123,196,160,0.2)'; border = `1px solid ${P.good}`; color = '#065F46'
          }
          return (
            <button key={i} onClick={() => handleAnswer(val)} style={{
              padding: '14px 10px', borderRadius: 12, cursor: chosen !== null ? 'default' : 'pointer',
              background: bg, border, color, fontSize: 20, fontWeight: 700,
              transition: 'all 0.2s', textAlign: 'center',
            }}>
              {chosen !== null && isCorrect ? '✅ ' : chosen !== null && isChosen && !isCorrect ? '❌ ' : ''}
              {val}
            </button>
          )
        })}
      </div>

      {chosen === -1 && (
        <div style={{ marginTop: 10, padding: '8px 12px', borderRadius: 10, background: 'rgba(232,123,158,0.1)', border: '1px solid rgba(232,123,158,0.3)', fontSize: 12, color: '#991B1B', textAlign: 'center' }}>
          ⏰ Temps écoulé — La réponse était <b>{q.answer}</b>
        </div>
      )}
    </div>
  )
}

export default function CalculGame({ eegState, onWin, gameData }) {
  if (gameData?.expression !== undefined)
    return <SingleCalc gameData={gameData} onWin={onWin} />
  return <MultiRoundCalc eegState={eegState} onWin={onWin} />
}
