// games/EnigmeGame.jsx — Énigmes et devinettes
// Avec gameData (ENI_NIVx.json) : question + réponse entière depuis Cloudinary
// Sans gameData : pool de devinettes MCQ intégré EEG-adaptatif
import { useState, useEffect } from 'react'

const P = { accent: '#B87B9E', text: '#2B2A4A', text2: '#9A8BAE', good: '#7BC4A0', bad: '#E87B9E' }

function makeNumChoices(answer) {
  const wrongs = new Set()
  const range = Math.max(3, Math.abs(answer))
  while (wrongs.size < 3) {
    const delta = Math.floor(Math.random() * range) + 1
    const w = answer + (Math.random() < 0.5 ? 1 : -1) * delta
    if (w !== answer && w >= 0) wrongs.add(w)
  }
  return [...Array.from(wrongs), answer].sort(() => Math.random() - 0.5)
}

function SingleEnigme({ gameData, onWin }) {
  const answer = gameData.reponse_attendue
  const [choices]  = useState(() => makeNumChoices(answer))
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
          Énigme — {gameData.label || 'Niv.' + gameData.level}
        </span>
        <span style={{ fontSize: 10, color: P.text2 }}>
          {gameData.etapes_mentales ? `${gameData.etapes_mentales} étape(s)` : ''}
        </span>
      </div>

      <div style={{
        background: 'rgba(255,255,255,0.5)', borderRadius: 14, padding: '16px',
        border: '1px solid rgba(184,123,158,0.2)', marginBottom: 16, minHeight: 70,
        display: 'flex', alignItems: 'center',
      }}>
        <span style={{ fontSize: 14, color: P.text, lineHeight: 1.7, fontStyle: 'italic' }}>
          "{gameData.question}"
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
              padding: '14px 10px', borderRadius: 12, cursor: chosen !== null ? 'default' : 'pointer',
              background: bg, border, color, fontSize: 20, fontWeight: 700, transition: 'all 0.2s',
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
          {gameData.explication ? ` — ${gameData.explication}` : ''}
        </div>
      )}
    </div>
  )
}

const ENIGMES = [
  { q: "Plus je sèche, plus je suis mouillée. Qui suis-je ?", r: ["Une serviette", "La mer", "La pluie", "Un nuage"], a: 0 },
  { q: "J'ai des feuilles mais je ne suis pas un arbre. Je réponds sans bouche. Qui suis-je ?", r: ["Un tableau", "Un livre", "Une fleur", "Un buisson"], a: 1 },
  { q: "Je cours sans jambes, je murmure sans bouche. Qui suis-je ?", r: ["Le vent", "Un cheval", "Une rivière", "Un fantôme"], a: 2 },
  { q: "Plus je vieillis, plus je me dresse. Qui suis-je ?", r: ["Une bougie", "Un arbre", "Un humain", "La lune"], a: 0 },
  { q: "On me jette quand on a besoin de moi et on me reprend quand on n'a plus besoin. Qui suis-je ?", r: ["Une clé", "Un ancre", "Une corde", "Un parachute"], a: 1 },
  { q: "Je n'ai ni début ni fin mais j'ai un milieu. Qui suis-je ?", r: ["Le temps", "Un cercle", "L'espace", "Un donut"], a: 1 },
  { q: "Je parle toutes les langues mais je n'ai pas de voix. Qui suis-je ?", r: ["Un dictionnaire", "Un interprète", "Un traducteur", "Un livre"], a: 0 },
  { q: "Je suis devant toi mais je ne se vois pas. Qui suis-je ?", r: ["L'avenir", "L'air", "Ton ombre", "Un miroir"], a: 0 },
  { q: "Qu'est-ce qu'un crocodile qui surveille des valises ?", r: ["Un gardien", "Un crocodile-bag", "Un sac à croco", "Un porteur"], a: 2 },
  { q: "Je vis dans l'obscurité, je meurs à la lumière. Qui suis-je ?", r: ["Un vampire", "Un secret", "La nuit", "Une bougie"], a: 1 },
  { q: "Je tourne sans jamais m'arrêter depuis des milliards d'années. Qui suis-je ?", r: ["La Terre", "Une horloge", "Un moulin", "Un tourbillon"], a: 0 },
  { q: "Je suis toujours devant vous mais on ne me voit jamais. Qui suis-je ?", r: ["Le futur", "La vérité", "Votre dos", "L'invisible"], a: 0 },
  { q: "Plus on m'enlève, plus je grandis. Qui suis-je ?", r: ["Une dette", "Un trou", "Une bougie", "Une usine"], a: 1 },
  { q: "Je commence la nuit et je termine le matin. Qui suis-je ?", r: ["La lune", "La lettre N", "Le sommeil", "Une étoile"], a: 1 },
]

function getSubset(eegState) {
  if (eegState === 'stress') return ENIGMES.slice(0, 5)
  if (eegState === 'focus')  return ENIGMES
  return ENIGMES.slice(0, 10)
}

function MCQEnigme({ eegState, onWin }) {
  const pool = getSubset(eegState)
  const [idx,     setIdx]    = useState(0)
  const [answer,  setAnswer] = useState(null)
  const [score,   setScore]  = useState(0)
  const [total,   setTotal]  = useState(0)
  const [done,    setDone]   = useState(false)

  useEffect(() => {
    setIdx(Math.floor(Math.random() * pool.length))
    setAnswer(null)
    setScore(0)
    setTotal(0)
    setDone(false)
  }, [eegState])

  const current = pool[idx]

  const handleAnswer = (i) => {
    if (answer !== null) return
    setAnswer(i)
    const correct = i === current.a
    const newScore = score + (correct ? 1 : 0)
    const newTotal = total + 1
    setScore(newScore)
    setTotal(newTotal)
    if (newTotal >= 5) {
      setTimeout(() => { setDone(true); onWin && onWin(newScore) }, 1200)
    }
  }

  const next = () => {
    setAnswer(null)
    setIdx(i => {
      let next = i
      while (next === i) next = Math.floor(Math.random() * pool.length)
      return next
    })
  }

  const reset = () => {
    setIdx(Math.floor(Math.random() * pool.length))
    setAnswer(null)
    setScore(0)
    setTotal(0)
    setDone(false)
  }

  if (done) return (
    <div style={{ fontFamily: "'Outfit',sans-serif", textAlign: 'center', padding: '1.5rem' }}>
      <div style={{ fontSize: 40, marginBottom: 8 }}>{score >= 4 ? '🏆' : score >= 2 ? '🌟' : '💪'}</div>
      <div style={{ fontSize: 18, fontWeight: 700, color: P.text, marginBottom: 6 }}>
        {score} / 5 bonnes réponses
      </div>
      <div style={{ fontSize: 13, color: P.text2, marginBottom: 16 }}>
        {score >= 4 ? 'Excellent esprit analytique !' : score >= 2 ? 'Bonne réflexion !' : 'Continue à t\'exercer !'}
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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 14 }}>
        <span style={{ fontSize: 11, fontWeight: 700, color: P.text2, letterSpacing: 1.5, textTransform: 'uppercase' }}>
          Énigmes ({total}/5)
        </span>
        <span style={{ fontSize: 12, color: P.good, fontWeight: 700 }}>Score: {score}</span>
      </div>

      {/* Barre de progression */}
      <div style={{ height: 4, background: 'rgba(184,123,158,0.15)', borderRadius: 2, marginBottom: 16, overflow: 'hidden' }}>
        <div style={{ height: '100%', width: `${(total / 5) * 100}%`, background: P.accent, borderRadius: 2, transition: 'width 0.3s' }} />
      </div>

      <div style={{
        background: 'rgba(255,255,255,0.5)', borderRadius: 14, padding: '16px',
        border: '1px solid rgba(184,123,158,0.2)', marginBottom: 14, minHeight: 70,
        display: 'flex', alignItems: 'center',
      }}>
        <span style={{ fontSize: 14, color: P.text, lineHeight: 1.6, fontStyle: 'italic' }}>
          "{current.q}"
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {current.r.map((rep, i) => {
          const isCorrect = i === current.a
          const isChosen  = answer === i
          let bg = 'rgba(255,255,255,0.4)'
          let border = '1px solid rgba(184,123,158,0.2)'
          let color = P.text
          if (answer !== null) {
            if (isCorrect) { bg = 'rgba(123,196,160,0.2)'; border = `1px solid ${P.good}`; color = '#065F46' }
            else if (isChosen) { bg = 'rgba(232,123,158,0.15)'; border = `1px solid ${P.bad}`; color = '#991B1B' }
          }
          return (
            <button key={i} onClick={() => handleAnswer(i)} style={{
              padding: '10px 14px', borderRadius: 10, cursor: answer !== null ? 'default' : 'pointer',
              background: bg, border, color, textAlign: 'left', fontSize: 13, fontWeight: 500,
              transition: 'all 0.2s',
            }}>
              {answer !== null && isCorrect ? '✅ ' : answer !== null && isChosen && !isCorrect ? '❌ ' : `${String.fromCharCode(65+i)}. `}
              {rep}
            </button>
          )
        })}
      </div>

      {answer !== null && total < 5 && (
        <button onClick={next} style={{
          width: '100%', marginTop: 12, padding: '10px', borderRadius: 12, border: 'none',
          background: `linear-gradient(135deg, ${P.accent}, #9A6B8E)`,
          color: 'white', fontWeight: 700, fontSize: 13, cursor: 'pointer',
        }}>
          Énigme suivante →
        </button>
      )}
    </div>
  )
}

export default function EnigmeGame({ eegState, onWin, gameData }) {
  if (gameData?.question !== undefined)
    return <SingleEnigme gameData={gameData} onWin={onWin} />
  return <MCQEnigme eegState={eegState} onWin={onWin} />
}
