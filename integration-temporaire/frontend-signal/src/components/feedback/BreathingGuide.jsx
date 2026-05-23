/**
 * BreathingGuide.jsx — Cercle animé pour respiration guidée
 * Rythmes : Box (4-4-4-4), 4-7-8, Cohérence cardiaque (5-5)
 * Challenge : maintenir Beta < 0.4 pendant 60s (Calm Challenge)
 */

import { useState, useEffect, useRef } from 'react';

const RHYTHMS = {
  box: {
    name: 'Box Breathing 4-4-4-4',
    phases: ['Inspirez', 'Retenez', 'Expirez', 'Retenez'],
    durations: [4, 4, 4, 4],
    scale: [1.4, 1.4, 0.8, 0.8],
  },
  fourSeven: {
    name: '4-7-8 Relaxation',
    phases: ['Inspirez', 'Retenez', 'Expirez'],
    durations: [4, 7, 8],
    scale: [1.4, 1.4, 0.8],
  },
  coherence: {
    name: 'Cohérence cardiaque 5-5',
    phases: ['Inspirez', 'Expirez'],
    durations: [5, 5],
    scale: [1.4, 0.8],
  },
};

const P = {
  bg: '#C5D3E8',
  accent: '#B87B9E',
  text: '#2B2A4A',
  text2: '#9A8BAE',
  conc: '#7BC4A0',
  stress: '#E87B9E',
};

export default function BreathingGuide({ eegBeta = 0.3, onComplete, onChallengeProgress }) {
  const getRhythm = () => {
    if (eegBeta > 0.75) return RHYTHMS.box;
    if (eegBeta > 0.5) return RHYTHMS.fourSeven;
    return RHYTHMS.coherence;
  };

  const [rhythm, setRhythm] = useState(getRhythm());
  const [phaseIdx, setPhaseIdx] = useState(0);
  const [counter, setCounter] = useState(rhythm.durations[0]);
  const [cycle, setCycle] = useState(0);
  const [scale, setScale] = useState(rhythm.scale[0]);
  const [challengeActive, setChallengeActive] = useState(false);
  const [challengeProgress, setChallengeProgress] = useState(0);
  const [challengeSuccess, setChallengeSuccess] = useState(false);
  const intervalRef = useRef(null);
  const challengeTimerRef = useRef(null);
  const TOTAL_CYCLES = 3;

  useEffect(() => {
    const newRhythm = getRhythm();
    setRhythm(newRhythm);
    setPhaseIdx(0);
    setCounter(newRhythm.durations[0]);
    setScale(newRhythm.scale[0]);
    setCycle(0);
  }, [eegBeta]);

  useEffect(() => {
    if (cycle >= TOTAL_CYCLES) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      if (onComplete) onComplete(challengeSuccess);
      return;
    }

    intervalRef.current = setInterval(() => {
      setCounter((prev) => {
        if (prev <= 1) {
          const nextPhase = (phaseIdx + 1) % rhythm.phases.length;
          setPhaseIdx(nextPhase);
          const newCounter = rhythm.durations[nextPhase];
          setScale(rhythm.scale[nextPhase]);
          if (nextPhase === 0) setCycle((c) => c + 1);
          return newCounter;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [phaseIdx, rhythm, cycle, challengeSuccess, onComplete]);

  useEffect(() => {
    if (challengeSuccess) return;

    if (eegBeta < 0.4) {
      if (!challengeActive) {
        setChallengeActive(true);
        if (challengeTimerRef.current) clearInterval(challengeTimerRef.current);
        challengeTimerRef.current = setInterval(() => {
          setChallengeProgress((prev) => {
            const next = prev + 1;
            if (onChallengeProgress) onChallengeProgress(next);
            if (next >= 60) {
              if (challengeTimerRef.current) clearInterval(challengeTimerRef.current);
              setChallengeSuccess(true);
              setChallengeActive(false);
            }
            return next;
          });
        }, 1000);
      }
    } else {
      if (challengeActive) {
        if (challengeTimerRef.current) clearInterval(challengeTimerRef.current);
        setChallengeActive(false);
        setChallengeProgress(0);
        if (onChallengeProgress) onChallengeProgress(0);
      }
    }

    return () => {
      if (challengeTimerRef.current) clearInterval(challengeTimerRef.current);
    };
  }, [eegBeta, challengeActive, challengeSuccess, onChallengeProgress]);

  const phaseLabel = rhythm.phases[phaseIdx];
  let ringColor;
  if (eegBeta > 0.6) ringColor = P.stress;
  else if (eegBeta < 0.4) ringColor = P.conc;
  else ringColor = P.accent;

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: 400,
      }}
    >
      <div style={{ textAlign: 'center', marginBottom: 16 }}>
        <div
          style={{
            fontSize: 12,
            color: P.text2,
            fontFamily: "'DM Mono', monospace",
            letterSpacing: 1,
          }}
        >
          {rhythm.name}
        </div>
        <div style={{ fontSize: 10, color: P.text2, marginTop: 4 }}>
          Cycle {cycle + 1}/{TOTAL_CYCLES}
        </div>
      </div>

      <div
        style={{
          position: 'relative',
          width: 200,
          height: 200,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: 24,
        }}
      >
        <div
          style={{
            position: 'absolute',
            width: 200,
            height: 200,
            borderRadius: '50%',
            border: `2px solid ${ringColor}30`,
          }}
        />
        <div
          style={{
            width: `${scale * 100}px`,
            height: `${scale * 100}px`,
            borderRadius: '50%',
            background: `linear-gradient(135deg, ${ringColor}30, ${ringColor}10)`,
            border: `3px solid ${ringColor}`,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            transition: 'all 1s ease-in-out',
            boxShadow: `0 0 30px ${ringColor}40`,
          }}
        >
          <div
            style={{
              fontSize: 32,
              fontFamily: "'DM Mono', monospace",
              fontWeight: 700,
              color: ringColor,
            }}
          >
            {counter}
          </div>
        </div>
      </div>

      <div
        style={{
          fontSize: 18,
          fontWeight: 600,
          color: ringColor,
          marginBottom: 8,
          letterSpacing: 1,
        }}
      >
        {phaseLabel}
      </div>

      <div style={{ width: '100%', maxWidth: 300, marginTop: 20 }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: 10,
            color: P.text2,
            marginBottom: 4,
          }}
        >
          <span>🧘 Calm Challenge</span>
          <span>
            {challengeSuccess ? '✅ Réussi !' : `${challengeProgress}s / 60s`}
          </span>
        </div>
        <div
          style={{
            height: 6,
            background: 'rgba(255,255,255,0.4)',
            borderRadius: 3,
            overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${(challengeProgress / 60) * 100}%`,
              height: '100%',
              background: challengeSuccess ? P.conc : P.accent,
              transition: 'width 1s linear',
            }}
          />
        </div>
        {!challengeSuccess && eegBeta >= 0.4 && challengeProgress === 0 && (
          <div
            style={{
              fontSize: 10,
              color: P.text2,
              marginTop: 6,
              fontFamily: "'DM Mono', monospace",
            }}
          >
            ⚡ Beta = {eegBeta.toFixed(2)} — le challenge démarre quand Beta {'<'} 0.4
          </div>
        )}
      </div>
    </div>
  );
}