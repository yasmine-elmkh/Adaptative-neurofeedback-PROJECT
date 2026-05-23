/**
 * FixationPoint.jsx — Point lumineux pour recentrer l'attention
 * Timer de 60s, point qui pulse, mouvement aléatoire après 30s.
 */

import { useState, useEffect } from 'react';

const P = {
  bg: '#C5D3E8',
  accent: '#B87B9E',
  blue: '#7BA8C4',
  text: '#2B2A4A',
  text2: '#9A8BAE',
};

export default function FixationPoint({ onComplete }) {
  const [timeLeft, setTimeLeft] = useState(60);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [hint, setHint] = useState('Concentration...');

  useEffect(() => {
    if (timeLeft <= 0) {
      onComplete();
      return;
    }

    const timer = setInterval(() => {
      setTimeLeft(prev => {
        const newTime = prev - 1;
        const progress = ((60 - newTime) / 60) * 100;
        if (newTime < 30) {
          // Après 30s, le point bouge légèrement
          setPosition({
            x: (Math.random() - 0.5) * 20,
            y: (Math.random() - 0.5) * 20,
          });
        }
        if (progress < 40) setHint('Concentration...');
        else if (progress < 70) setHint('Bien ! Continuez...');
        else setHint('Excellent ! Encore un effort');
        return newTime;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [timeLeft, onComplete]);

  const progress = ((60 - timeLeft) / 60) * 100;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 400 }}>
      <div style={{ fontSize: 11, color: P.text2, marginBottom: 16, fontFamily: "'DM Mono',monospace", letterSpacing: 0.5 }}>
        Fixez le point sans bouger les yeux — {timeLeft}s
      </div>

      {/* Zone du point */}
      <div style={{
        width: '100%', maxWidth: 380, aspectRatio: '16/9',
        background: 'rgba(43,42,74,0.08)', borderRadius: 18,
        border: `1px solid rgba(255,255,255,0.4)`,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        position: 'relative', overflow: 'hidden', marginBottom: 16,
      }}>
        <div
          style={{
            width: 18, height: 18, borderRadius: '50%',
            background: P.blue,
            boxShadow: `0 0 0 6px rgba(123,168,196,0.2), 0 0 30px rgba(123,168,196,0.6)`,
            transition: 'transform 2s ease',
            transform: `translate(${position.x}px, ${position.y}px)`,
            animation: 'pulse 2s ease-in-out infinite',
          }}
        />
      </div>

      {/* Barre de progression */}
      <div style={{ width: '100%', maxWidth: 380 }}>
        <div style={{ height: 6, background: 'rgba(255,255,255,0.4)', borderRadius: 3, overflow: 'hidden', marginBottom: 6 }}>
          <div style={{ width: `${progress}%`, height: '100%', background: `linear-gradient(90deg, ${P.blue}, ${P.accent})`, borderRadius: 3, transition: 'width 1s linear' }} />
        </div>
        <div style={{ fontSize: 11, color: P.text2, textAlign: 'center', fontFamily: "'DM Mono',monospace", letterSpacing: 0.5 }}>
          {hint}
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { box-shadow: 0 0 0 6px rgba(123,168,196,0.2), 0 0 30px rgba(123,168,196,0.5); }
          50% { box-shadow: 0 0 0 12px rgba(123,168,196,0.1), 0 0 50px rgba(123,168,196,0.7); }
        }
      `}</style>
    </div>
  );
}