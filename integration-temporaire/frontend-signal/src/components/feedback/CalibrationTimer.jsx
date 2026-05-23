/**
 * CalibrationTimer.jsx — Timer 30s pour baseline EEG
 */

import { useState, useEffect } from 'react';

const P = {
  accent: '#B87B9E',
  text2: '#9A8BAE',
};

export default function CalibrationTimer({ onComplete, duration = 30 }) {
  const [seconds, setSeconds] = useState(duration);

  useEffect(() => {
    if (seconds <= 0) {
      onComplete();
      return;
    }
    const timer = setTimeout(() => setSeconds(s => s - 1), 1000);
    return () => clearTimeout(timer);
  }, [seconds, onComplete]);

  const progress = ((duration - seconds) / duration) * 100;

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: 48, fontFamily: "'DM Mono',monospace", color: P.accent, marginBottom: 12 }}>
        {seconds}s
      </div>
      <div style={{ height: 6, background: 'rgba(255,255,255,0.4)', borderRadius: 3, overflow: 'hidden', width: '100%', maxWidth: 300, margin: '0 auto' }}>
        <div style={{ width: `${progress}%`, height: '100%', background: P.accent, transition: 'width 1s linear' }} />
      </div>
      <div style={{ fontSize: 10, color: P.text2, marginTop: 8, fontFamily: "'DM Mono',monospace" }}>
        Calibration — restez immobile, yeux fermés
      </div>
    </div>
  );
}