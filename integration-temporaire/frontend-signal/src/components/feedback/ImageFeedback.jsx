// ImageFeedback.jsx — Image thérapeutique avec contrôles visuels + guide utilisateur EEG
import { useState } from 'react'

const PRESETS = [
  { label: 'Naturel',  values: { brightness: 1.0, contrast: 1.0, saturate: 1.0, blur: 0   }, desc: 'Image originale sans modification' },
  { label: 'Calme',    values: { brightness: 0.85, contrast: 0.72, saturate: 0.55, blur: 1.5 }, desc: '↑ Ondes alpha — favorise la relaxation' },
  { label: 'Focus',    values: { brightness: 1.1, contrast: 1.25, saturate: 1.0, blur: 0   }, desc: '↑ Ondes beta — améliore la concentration' },
  { label: 'Énergie',  values: { brightness: 1.2, contrast: 1.15, saturate: 1.45, blur: 0  }, desc: '↑ Éveil cortical — stimulation cognitive' },
]

const PARAMS = [
  {
    key: 'brightness', label: 'Luminosité', unit: '', min: 0.3, max: 2.0, step: 0.05,
    format: v => Math.round(v * 100) + '%',
    guide: {
      low:  'Faible luminosité → ↑ mélatonine, ↑ ondes alpha pariétales, état propice à la méditation et au sommeil léger (Cajochen et al., 2005).',
      high: 'Forte luminosité → suppression de la mélatonine, ↑ éveil cortical et ↑ ondes beta frontales (Vandewalle et al., 2007).',
      ref:  'Cajochen C. et al. (2005). High sensitivity of human melatonin, alertness, thermoregulation and heart rate to short wavelength light. J Clin Endocrinol Metab.',
    }
  },
  {
    key: 'contrast', label: 'Contraste', unit: '', min: 0.3, max: 2.0, step: 0.05,
    format: v => Math.round(v * 100) + '%',
    guide: {
      low:  'Bas contraste → réduction de l\'activation du cortex visuel V1, moins de charge cognitive, utile en état de stress pour diminuer l\'arousal (Berman et al., 2014).',
      high: 'Haut contraste → recrutement accru du cortex occipital, ↑ charge attentionnelle, utile pour sortir d\'un état de somnolence (Norcia et al., 2015).',
      ref:  'Berman M.G. et al. (2014). Interacting with nature improves cognition and affect. Landscape and Urban Planning.',
    }
  },
  {
    key: 'saturate', label: 'Saturation', unit: '', min: 0.0, max: 2.0, step: 0.05,
    format: v => Math.round(v * 100) + '%',
    guide: {
      low:  'Désaturation (niveaux de gris) → ↓ activation de l\'amygdale, réduction de l\'arousal émotionnel, ↑ alpha temporal (Russell & Mehrabian, 1994).',
      high: 'Forte saturation → ↑ activation limbique et orbitofrontale, arousal émotionnel élevé pouvant moduler les oscillations gamma (Valdez & Mehrabian, 1994).',
      ref:  'Valdez P. & Mehrabian A. (1994). Effects of color on emotions. J Exp Psychol Gen. doi:10.1037/0096-3445.123.4.394',
    }
  },
  {
    key: 'blur', label: 'Flou', unit: 'px', min: 0, max: 8, step: 0.25,
    format: v => v.toFixed(1) + ' px',
    guide: {
      low:  'Netteté élevée (flou = 0) → traitement visuel détaillé, engagement du cortex pariétal dorsal, utile pour les tâches nécessitant une attention focalisée.',
      high: 'Flou fort → réduction de la précision spatiale, ↓ sollicitation du cortex visuel V4/V5, effet apaisant similaire à la stimulation alpha transcrânienne (Angelakis et al., 2007).',
      ref:  'Angelakis E. et al. (2007). EEG neurofeedback: a brief overview and an example of peak alpha frequency training. Clin Neuropsychol.',
    }
  },
]

function ParamSlider({ param, value, onChange, isOpen, onToggleGuide }) {
  const pct = ((value - param.min) / (param.max - param.min)) * 100

  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 3 }}>
        <span style={{ fontSize: 11, color: '#c0b8d0', fontWeight: 600 }}>{param.label}</span>
        <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
          <span style={{ fontSize: 11, color: '#9a8bb0', fontFamily: 'monospace' }}>{param.format(value)}</span>
          <button
            onClick={onToggleGuide}
            title="Guide scientifique"
            style={{
              width: 16, height: 16, borderRadius: '50%', border: '1px solid rgba(184,123,200,0.4)',
              background: isOpen ? 'rgba(184,123,200,0.25)' : 'transparent',
              color: isOpen ? '#c07ae0' : '#7a6890', fontSize: 9, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 0,
            }}
          >?</button>
        </div>
      </div>
      <div style={{ position: 'relative', height: 6, borderRadius: 3, background: 'rgba(255,255,255,0.08)', marginBottom: 3 }}>
        <div style={{ position: 'absolute', left: 0, width: pct + '%', height: '100%', borderRadius: 3, background: 'linear-gradient(90deg, #7a4a90, #c07ae0)' }} />
        <input
          type="range" min={param.min} max={param.max} step={param.step} value={value}
          onChange={e => onChange(parseFloat(e.target.value))}
          style={{ position: 'absolute', inset: 0, width: '100%', opacity: 0, cursor: 'pointer', margin: 0, height: '100%' }}
        />
      </div>
      {isOpen && (
        <div style={{ marginTop: 6, padding: '8px 10px', borderRadius: 8, background: 'rgba(120,80,160,0.12)', border: '1px solid rgba(184,123,200,0.2)', fontSize: 10, color: '#b0a0c0', lineHeight: 1.5 }}>
          <div style={{ marginBottom: 4 }}>
            <span style={{ color: '#7bbfdf', fontWeight: 700 }}>↓ Faible — </span>{param.guide.low}
          </div>
          <div style={{ marginBottom: 4 }}>
            <span style={{ color: '#e0a060', fontWeight: 700 }}>↑ Élevé — </span>{param.guide.high}
          </div>
          <div style={{ color: '#7a6a8a', fontStyle: 'italic', borderTop: '1px solid rgba(184,123,200,0.15)', paddingTop: 4, marginTop: 2 }}>
            📚 {param.guide.ref}
          </div>
        </div>
      )}
    </div>
  )
}

export default function ImageFeedback({ src, alt }) {
  const [values, setValues] = useState({ brightness: 1.0, contrast: 1.0, saturate: 1.0, blur: 0 })
  const [showControls, setShowControls] = useState(false)
  const [openGuides, setOpenGuides] = useState({})
  const [activePreset, setActivePreset] = useState('Naturel')

  const cssFilter = `brightness(${values.brightness}) contrast(${values.contrast}) saturate(${values.saturate}) blur(${values.blur}px)`

  const applyPreset = (preset) => {
    setValues({ ...preset.values })
    setActivePreset(preset.label)
  }

  const handleSlider = (key, val) => {
    setValues(prev => ({ ...prev, [key]: val }))
    setActivePreset(null)
  }

  const toggleGuide = (key) => {
    setOpenGuides(prev => ({ ...prev, [key]: !prev[key] }))
  }

  return (
    <div style={{ fontFamily: "'Outfit', sans-serif" }}>
      {/* Image principale */}
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
            border: '1px solid rgba(184,123,200,0.4)', color: showControls ? '#e0d0f0' : '#9a8bb0',
            cursor: 'pointer', backdropFilter: 'blur(4px)', fontWeight: 600,
          }}
        >
          {showControls ? '✕ Fermer' : '🎛 Ajuster'}
        </button>
      </div>

      {/* Panneau de contrôles */}
      {showControls && (
        <div style={{ background: 'rgba(20,16,30,0.7)', borderRadius: 12, border: '1px solid rgba(184,123,200,0.2)', padding: '12px 14px' }}>

          {/* Presets */}
          <div style={{ marginBottom: 12 }}>
            <div style={{ fontSize: 10, color: '#7a6890', fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase', marginBottom: 6 }}>
              Préréglages EEG
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {PRESETS.map(p => (
                <button
                  key={p.label}
                  onClick={() => applyPreset(p)}
                  title={p.desc}
                  style={{
                    padding: '4px 10px', borderRadius: 6, fontSize: 10, cursor: 'pointer',
                    background: activePreset === p.label ? 'rgba(184,123,200,0.3)' : 'rgba(255,255,255,0.04)',
                    border: activePreset === p.label ? '1px solid rgba(184,123,200,0.6)' : '1px solid rgba(255,255,255,0.1)',
                    color: activePreset === p.label ? '#d0a0e8' : '#7a6890',
                    fontWeight: activePreset === p.label ? 700 : 400,
                  }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* Sliders */}
          <div style={{ borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: 12, marginBottom: 10 }}>
            <div style={{ fontSize: 10, color: '#7a6890', fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase', marginBottom: 8 }}>
              Réglage manuel <span style={{ color: '#5a4870', fontWeight: 400 }}>— cliquez sur ? pour le guide EEG</span>
            </div>
            {PARAMS.map(p => (
              <ParamSlider
                key={p.key}
                param={p}
                value={values[p.key]}
                onChange={val => handleSlider(p.key, val)}
                isOpen={!!openGuides[p.key]}
                onToggleGuide={() => toggleGuide(p.key)}
              />
            ))}
          </div>

          {/* Note générale */}
          <div style={{ padding: '8px 10px', borderRadius: 8, background: 'rgba(60,40,80,0.3)', border: '1px solid rgba(120,80,160,0.2)', fontSize: 10, color: '#9a8baa', lineHeight: 1.6 }}>
            <span style={{ color: '#c0a0d8', fontWeight: 700 }}>Guide général — </span>
            Pour un état <b style={{ color: '#7bbfdf' }}>relaxé (↑ alpha)</b>, privilégiez des images sombres, peu contrastées et désaturées avec un léger flou.
            Pour un état <b style={{ color: '#e0a060' }}>concentré (↑ beta)</b>, préférez des images lumineuses, contrastées et nettes.
          </div>
        </div>
      )}
    </div>
  )
}
