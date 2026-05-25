import { useState } from 'react'

const PRESETS = [
  { label: 'Naturel', values: { brightness: 1.0, contrast: 1.0, saturate: 1.0, blur: 0   }, desc: 'Image originale' },
  { label: 'Calme',   values: { brightness: 0.85, contrast: 0.72, saturate: 0.55, blur: 1.5 }, desc: '↑ Ondes alpha — relaxation' },
  { label: 'Focus',   values: { brightness: 1.1, contrast: 1.25, saturate: 1.0, blur: 0   }, desc: '↑ Ondes beta — concentration' },
  { label: 'Énergie', values: { brightness: 1.2, contrast: 1.15, saturate: 1.45, blur: 0  }, desc: '↑ Éveil cortical' },
]

const PARAMS = [
  { key: 'brightness', label: 'Luminosité', min: 0.3, max: 2.0, step: 0.05, format: v => Math.round(v * 100) + '%' },
  { key: 'contrast',   label: 'Contraste',  min: 0.3, max: 2.0, step: 0.05, format: v => Math.round(v * 100) + '%' },
  { key: 'saturate',   label: 'Saturation', min: 0.0, max: 2.0, step: 0.05, format: v => Math.round(v * 100) + '%' },
  { key: 'blur',       label: 'Flou',       min: 0,   max: 8,   step: 0.25, format: v => v.toFixed(1) + ' px' },
]

export default function ImageFeedback({ src, alt }) {
  const [values, setValues]               = useState({ brightness: 1.0, contrast: 1.0, saturate: 1.0, blur: 0 })
  const [showControls, setShowControls]   = useState(false)
  const [activePreset, setActivePreset]   = useState('Naturel')

  const cssFilter = `brightness(${values.brightness}) contrast(${values.contrast}) saturate(${values.saturate}) blur(${values.blur}px)`

  return (
    <div style={{ fontFamily: "'Outfit', sans-serif" }}>
      <div style={{ position: 'relative', textAlign: 'center', marginBottom: 10 }}>
        <img
          src={src}
          alt={alt || 'Image thérapeutique'}
          style={{ maxWidth: '100%', maxHeight: 380, borderRadius: 12, objectFit: 'cover', filter: cssFilter, transition: 'filter 0.3s ease' }}
        />
        <button
          onClick={() => setShowControls(s => !s)}
          style={{
            position: 'absolute', top: 8, right: 8,
            padding: '4px 10px', borderRadius: 6, fontSize: 10,
            background: showControls ? 'rgba(120,80,160,0.85)' : 'rgba(20,16,30,0.75)',
            border: '1px solid rgba(184,123,200,0.4)',
            color: showControls ? '#e0d0f0' : '#9a8bb0',
            cursor: 'pointer', backdropFilter: 'blur(4px)', fontWeight: 600,
          }}
        >
          {showControls ? '✕ Fermer' : '🎛 Ajuster'}
        </button>
      </div>

      {showControls && (
        <div style={{ background: 'rgba(20,16,30,0.7)', borderRadius: 12, border: '1px solid rgba(184,123,200,0.2)', padding: '12px 14px' }}>
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 10, color: '#7a6890', fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase', marginBottom: 6 }}>
              Préréglages EEG
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {PRESETS.map(p => (
                <button
                  key={p.label}
                  onClick={() => { setValues({ ...p.values }); setActivePreset(p.label) }}
                  title={p.desc}
                  style={{
                    padding: '4px 10px', borderRadius: 6, fontSize: 10, cursor: 'pointer',
                    background: activePreset === p.label ? 'rgba(184,123,200,0.3)' : 'rgba(255,255,255,0.04)',
                    border: activePreset === p.label ? '1px solid rgba(184,123,200,0.6)' : '1px solid rgba(255,255,255,0.1)',
                    color: activePreset === p.label ? '#d0a0e8' : '#7a6890',
                    fontWeight: activePreset === p.label ? 700 : 400,
                  }}
                >{p.label}</button>
              ))}
            </div>
          </div>

          {PARAMS.map(p => {
            const pct = ((values[p.key] - p.min) / (p.max - p.min)) * 100
            return (
              <div key={p.key} style={{ marginBottom: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                  <span style={{ fontSize: 11, color: '#c0b8d0', fontWeight: 600 }}>{p.label}</span>
                  <span style={{ fontSize: 11, color: '#9a8bb0', fontFamily: 'monospace' }}>{p.format(values[p.key])}</span>
                </div>
                <div style={{ position: 'relative', height: 6, borderRadius: 3, background: 'rgba(255,255,255,0.08)' }}>
                  <div style={{ position: 'absolute', left: 0, width: pct + '%', height: '100%', borderRadius: 3, background: 'linear-gradient(90deg, #7a4a90, #c07ae0)' }} />
                  <input
                    type="range" min={p.min} max={p.max} step={p.step} value={values[p.key]}
                    onChange={e => { setValues(prev => ({ ...prev, [p.key]: parseFloat(e.target.value) })); setActivePreset(null) }}
                    style={{ position: 'absolute', inset: 0, width: '100%', opacity: 0, cursor: 'pointer', margin: 0, height: '100%' }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
