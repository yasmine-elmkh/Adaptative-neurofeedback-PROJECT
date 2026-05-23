/**
 * EEGLiveMonitor — barres de bandes + explications cliquables pour l'utilisateur
 * Chaque bande est interactive : clic → explication clinique en français
 * Bouton "?" → glossaire des 15 features originales du pipeline
 */

import { useState } from 'react'
import { useEEGWebSocket } from '../../hooks/useEEGWebSocket'

const BAND_COLORS = {
  delta: '#7BC4A0', theta: '#7BA8C4', alpha: '#B87B9E', beta: '#C4A87B', gamma: '#E87B9E',
}

const BAND_INFO = {
  delta: {
    label:   'Delta · 0.5–4 Hz',
    emoji:   '😴',
    short:   'Sommeil / fatigue',
    explain: 'Ondes lentes dominantes pendant le sommeil profond et la récupération. Un delta élevé en état d\'éveil peut indiquer de la fatigue ou du bruit dans le signal. Valeur normale éveillé : 10–20 %.',
    ref:     'Cohen 2014',
  },
  theta: {
    label:   'Theta · 4–8 Hz',
    emoji:   '💭',
    short:   'Mémoire / rêverie',
    explain: 'Associé à la créativité, la méditation et l\'apprentissage. Élevé lors de la distraction ou d\'un état de demi-sommeil. Indice TDAH : theta/beta > 3 est cliniquement significatif. Valeur normale : 15–25 %.',
    ref:     'Klimesch 1999',
  },
  alpha: {
    label:   'Alpha · 8–13 Hz',
    emoji:   '🧘',
    short:   'Relaxation alerte',
    explain: 'La bande cible du protocole NeuroCap. Alpha élevé (> 30 %) indique un état de relaxation alerte — optimal pour l\'apprentissage. C\'est exactement ce que vous entraînez avec le neurofeedback.',
    ref:     'Mou et al. 2024',
  },
  beta: {
    label:   'Beta · 13–30 Hz',
    emoji:   '🧠',
    short:   'Cognition / stress',
    explain: 'Reflète l\'attention, la concentration et le traitement cognitif actif. Un beta très élevé (> 40 %) est associé au stress et à l\'anxiété. L\'indice de stress β/α surveille ce rapport en temps réel.',
    ref:     'Pope et al. 1995',
  },
  gamma: {
    label:   'Gamma · 30–40 Hz',
    emoji:   '⚡',
    short:   'Traitement haut niv.',
    explain: 'Intégration sensorielle de haut niveau et conscience. Très sensible aux artefacts musculaires (EMG) — un pic gamma isolé peut être un clignement ou une contraction du visage, pas nécessairement du cerveau.',
    ref:     'Bhargava 2020',
  },
}

const FEATURES_15 = [
  { name: 'rel_delta … rel_gamma',  cat: 'Puissances relatives', desc: 'Proportion de chaque bande sur la puissance totale (PSD Welch, fenêtre Hann). Invariantes au gain ADC du casque.' },
  { name: 'engagement = β/(α+θ)',   cat: 'Ratio cognitif', desc: 'Indice d\'implication mentale (Pope 1995). > 1.5 = forte concentration active.' },
  { name: 'stress_idx = β/α',       cat: 'Ratio cognitif', desc: 'Rapport bêta/alpha. > 2 = stress actif. Seuil NeuroCap : > 0.5 → déclenche la respiration guidée.' },
  { name: 'theta_alpha = θ/α',      cat: 'Ratio cognitif', desc: 'Indicateur de somnolence. Discriminant p<0.001 entre concentration et stress (Salam 2026).' },
  { name: 'alpha_beta = α/β',       cat: 'Ratio cognitif', desc: 'Rapport calme/activation. Élevé = paisible, bas = alerte ou stress.' },
  { name: 'hjorth_activity',        cat: 'Hjorth (1970)', desc: 'Variance du signal — énergie instantanée en µV².' },
  { name: 'hjorth_mobility',        cat: 'Hjorth (1970)', desc: 'Fréquence caractéristique estimée par le rapport des dérivées.' },
  { name: 'hjorth_complexity',      cat: 'Hjorth (1970)', desc: 'Irrégularité fréquentielle. Bas en concentration, élevé sous stress.' },
  { name: 'spectral_entropy',       cat: 'Complexité', desc: 'Entropie de Shannon sur le PSD. Signal sinusoïdal = 0, bruit blanc = 1.' },
  { name: 'sef95',                  cat: 'Complexité', desc: 'Fréquence sous laquelle se trouve 95 % de l\'énergie spectrale. Baisse lors de la relaxation alpha.' },
  { name: 'rms_uv',                 cat: 'Amplitude', desc: 'Valeur RMS en µV. Amplitude globale. Normale Fp2 éveillé : 5–50 µV.' },
]

export default function EEGLiveMonitor({ wsUrl = 'ws://localhost:8765/ws' }) {
  const { epoch, eegBands, isConnected } = useEEGWebSocket(wsUrl)
  const [activeBand, setActiveBand]      = useState(null)
  const [showGlossary, setShowGlossary]  = useState(false)

  const bands = epoch?.features
    ? {
        delta: epoch.features.rel_delta || 0,
        theta: epoch.features.rel_theta || 0,
        alpha: epoch.features.rel_alpha || 0,
        beta:  epoch.features.rel_beta  || 0,
        gamma: epoch.features.rel_gamma || 0,
      }
    : eegBands || { delta: 0, theta: 0, alpha: 0, beta: 0, gamma: 0 }

  const state      = epoch?.state      || 'neutral'
  const confidence = epoch?.confidence || 0

  return (
    <div style={{ marginBottom: 16 }}>

      {/* En-tête */}
      <div style={{ fontSize: 9, fontFamily: "'DM Mono',monospace", letterSpacing: 2, color: '#9A8BAE', marginBottom: 10, textTransform: 'uppercase' }}>
        EEG en direct {!isConnected && <span style={{ color: '#E87B9E' }}>· Déconnecté</span>}
      </div>

      {/* État + confiance */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, padding: '7px 10px', background: 'rgba(255,255,255,0.25)', borderRadius: 10 }}>
        <div style={{
          width: 8, height: 8, borderRadius: '50%',
          background: isConnected ? BAND_COLORS.alpha : '#E87B9E',
          animation: isConnected ? 'elPulse 1.5s ease-in-out infinite' : 'none',
        }} />
        <span style={{ fontWeight: 700, color: '#2B2A4A', fontSize: 12 }}>{state.toUpperCase()}</span>
        {confidence > 0 && (
          <span style={{ fontSize: 9, color: '#9A8BAE', fontFamily: "'DM Mono',monospace", marginLeft: 'auto' }}>
            {Math.round(confidence * 100)}% conf.
          </span>
        )}
      </div>

      {/* Barres de bandes — cliquables pour explication */}
      {Object.entries(bands).map(([band, val]) => {
        const info     = BAND_INFO[band]
        const isActive = activeBand === band
        return (
          <div key={band} onClick={() => setActiveBand(isActive ? null : band)} style={{ marginBottom: 8, cursor: 'pointer' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3, alignItems: 'center' }}>
              <span style={{ fontSize: 9, fontFamily: "'DM Mono',monospace", color: BAND_COLORS[band], textTransform: 'uppercase', display: 'flex', alignItems: 'center', gap: 4 }}>
                {info.emoji} {band}
                <span style={{ color: '#9A8BAE', fontSize: 8, fontStyle: 'italic', fontFamily: 'sans-serif', textTransform: 'none' }}>
                  {info.short}
                </span>
              </span>
              <span style={{ fontSize: 9, fontFamily: "'DM Mono',monospace", fontWeight: 700, color: BAND_COLORS[band] }}>
                {Math.round(val * 100)}%
              </span>
            </div>
            <div style={{ height: 6, background: 'rgba(255,255,255,0.4)', borderRadius: 3, overflow: 'hidden' }}>
              <div style={{ width: `${Math.min(val * 100, 100)}%`, height: '100%', background: BAND_COLORS[band], borderRadius: 3, transition: 'width 0.3s ease' }} />
            </div>
            {isActive && (
              <div style={{ marginTop: 5, padding: '7px 9px', borderRadius: 8, background: `${BAND_COLORS[band]}18`, border: `1px solid ${BAND_COLORS[band]}40`, fontSize: 10, color: '#2B2A4A', lineHeight: 1.55 }}>
                <div style={{ fontWeight: 700, color: BAND_COLORS[band], marginBottom: 3 }}>{info.label}</div>
                {info.explain}
                <div style={{ marginTop: 4, fontSize: 9, color: '#9A8BAE', fontFamily: "'DM Mono',monospace" }}>Réf. {info.ref}</div>
              </div>
            )}
          </div>
        )
      })}

      {/* Bouton glossaire 15 features */}
      <button
        onClick={() => setShowGlossary(g => !g)}
        style={{ width: '100%', marginTop: 8, padding: '5px 0', borderRadius: 8, border: '1px solid rgba(184,123,158,0.3)', background: showGlossary ? 'rgba(184,123,158,0.1)' : 'transparent', color: '#B87B9E', fontSize: 9, fontFamily: "'DM Mono',monospace", letterSpacing: 1, cursor: 'pointer' }}
      >
        {showGlossary ? '▲ Fermer le glossaire' : '? Que signifient les features ?'}
      </button>

      {showGlossary && (
        <div style={{ marginTop: 8 }}>
          <div style={{ fontSize: 9, color: '#9A8BAE', fontFamily: "'DM Mono',monospace", letterSpacing: 1, marginBottom: 5 }}>
            15 FEATURES EEG — pipeline DSP v7
          </div>
          {FEATURES_15.map((f, i) => (
            <div key={i} style={{ padding: '5px 8px', marginBottom: 4, background: 'rgba(255,255,255,0.2)', borderRadius: 7, border: '1px solid rgba(255,255,255,0.3)' }}>
              <div style={{ fontWeight: 700, fontSize: 10, color: '#2B2A4A', marginBottom: 2 }}>
                {f.name} <span style={{ fontWeight: 400, color: '#9A8BAE', fontSize: 9 }}>· {f.cat}</span>
              </div>
              <div style={{ fontSize: 10, color: '#4a5a6e', lineHeight: 1.5 }}>{f.desc}</div>
            </div>
          ))}
          <div style={{ marginTop: 6, fontSize: 9, color: '#9A8BAE', fontFamily: "'DM Mono',monospace", textAlign: 'center' }}>
            v8 actuel : 63 features (+ DWT · entropies · QuadTPat)
          </div>
        </div>
      )}

      <style>{`
        @keyframes elPulse {
          0%, 100% { opacity: 1; transform: scale(1); }
          50% { opacity: 0.6; transform: scale(0.8); }
        }
      `}</style>
    </div>
  )
}
