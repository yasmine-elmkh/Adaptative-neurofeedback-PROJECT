import { useState, useEffect, useCallback } from 'react'

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

/* ── Illusions optiques interactives embarquées ── */
const BUILTIN_ILLUSIONS = [
  {
    key: 'rotating_circles',
    label: '⭕ Cercles rotatifs',
    desc: 'Illusion de rotation — fixez le centre',
    html: `<!DOCTYPE html><html><head><style>
      body{margin:0;background:#1a1a2e;display:flex;align-items:center;justify-content:center;height:100vh;overflow:hidden;}
      .wrap{position:relative;width:300px;height:300px;}
      .ring{position:absolute;border-radius:50%;border:8px solid transparent;animation:spin linear infinite;}
      .r1{width:280px;height:280px;top:10px;left:10px;border-top-color:#6c63ff;border-bottom-color:#6c63ff;animation-duration:3s;}
      .r2{width:220px;height:220px;top:40px;left:40px;border-left-color:#ff6584;border-right-color:#ff6584;animation-duration:2s;animation-direction:reverse;}
      .r3{width:160px;height:160px;top:70px;left:70px;border-top-color:#43e97b;border-bottom-color:#43e97b;animation-duration:1.5s;}
      .r4{width:100px;height:100px;top:100px;left:100px;border-left-color:#f9ca24;border-right-color:#f9ca24;animation-duration:1s;animation-direction:reverse;}
      .dot{position:absolute;width:16px;height:16px;background:#fff;border-radius:50%;top:50%;left:50%;transform:translate(-50%,-50%);}
      @keyframes spin{to{transform:rotate(360deg);}}
      p{color:#9a8bb0;font-family:sans-serif;font-size:12px;text-align:center;position:fixed;bottom:10px;width:100%;}
    </style></head><body>
    <div class="wrap"><div class="ring r1"></div><div class="ring r2"></div><div class="ring r3"></div><div class="ring r4"></div><div class="dot"></div></div>
    <p>Fixez le point blanc — les anneaux semblent tourner</p>
    </body></html>`,
  },
  {
    key: 'checker_shadow',
    label: '🟫 Échiquier d\'Adelson',
    desc: 'A et B paraissent différents — ils sont identiques',
    html: `<!DOCTYPE html><html><head><style>
      body{margin:0;background:#1a1a2e;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;}
      canvas{border-radius:12px;}
      p{color:#9a8bb0;font-size:12px;margin-top:12px;text-align:center;}
    </style></head><body>
    <canvas id="c" width="300" height="300"></canvas>
    <p>Les cases A et B ont exactement la même couleur (#787878)</p>
    <script>
      const c=document.getElementById('c'),ctx=c.getContext('2d');
      const sz=37.5;
      for(let r=0;r<8;r++)for(let col=0;col<8;col++){
        ctx.fillStyle=(r+col)%2===0?'#c0c0c0':'#404040';
        ctx.fillRect(col*sz,r*sz,sz,sz);
      }
      // Cylindre
      const g=ctx.createRadialGradient(210,90,10,210,90,80);
      g.addColorStop(0,'rgba(80,80,80,0.9)');g.addColorStop(1,'rgba(0,0,0,0)');
      ctx.fillStyle=g;ctx.beginPath();ctx.ellipse(210,150,55,160,0,0,Math.PI*2);ctx.fill();
      // Marquer A et B
      ctx.fillStyle='rgba(255,100,100,0.9)';ctx.font='bold 14px sans-serif';
      ctx.fillText('A',88,230);ctx.fillText('B',172,117);
      // Patch révélateur
      ctx.strokeStyle='rgba(255,200,0,0.6)';ctx.lineWidth=2;
      ctx.strokeRect(75,210,37,37);ctx.strokeRect(158,98,37,37);
    </script></body></html>`,
  },
  {
    key: 'motion_aftereffect',
    label: '🌀 Spirale de Archimède',
    desc: 'Fixez 30s — le monde semble se déformer',
    html: `<!DOCTYPE html><html><head><style>
      body{margin:0;background:#1a1a2e;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;}
      canvas{cursor:pointer;}
      p{color:#9a8bb0;font-family:sans-serif;font-size:11px;margin-top:8px;text-align:center;}
      button{margin-top:8px;padding:6px 16px;border-radius:8px;background:#6c63ff;color:#fff;border:none;cursor:pointer;font-size:12px;}
    </style></head><body>
    <canvas id="s" width="300" height="300"></canvas>
    <p>Fixez le centre pendant 30 secondes, puis regardez votre main</p>
    <button onclick="dir=-dir">Inverser</button>
    <script>
      const canvas=document.getElementById('s'),ctx=canvas.getContext('2d');
      let angle=0,dir=1;
      function draw(){
        ctx.clearRect(0,0,300,300);
        ctx.save();ctx.translate(150,150);
        for(let i=0;i<600;i++){
          const a=i*0.12+angle,r=i*0.38;
          const x=r*Math.cos(a),y=r*Math.sin(a);
          const t=i/600;
          ctx.beginPath();ctx.arc(x,y,1.2,0,Math.PI*2);
          ctx.fillStyle=\`hsl(\${i*0.6+angle*20},70%,\${40+t*30}%)\`;
          ctx.fill();
        }
        ctx.restore();
        angle+=0.025*dir;
        requestAnimationFrame(draw);
      }
      draw();
    </script></body></html>`,
  },
  {
    key: 'hermann_grid',
    label: '⬛ Grille de Hermann',
    desc: 'Des points gris apparaissent aux intersections',
    html: `<!DOCTYPE html><html><head><style>
      body{margin:0;background:#1a1a2e;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;}
      .grid{display:grid;grid-template-columns:repeat(7,36px);grid-template-rows:repeat(7,36px);gap:6px;background:#e0e0e0;padding:6px;border-radius:4px;}
      .cell{width:36px;height:36px;background:#1a1a2e;}
      p{color:#9a8bb0;font-family:sans-serif;font-size:11px;margin-top:12px;text-align:center;}
    </style></head><body>
    <div class="grid" id="g"></div>
    <p>Des points gris fantômes apparaissent aux intersections — ils disparaissent si on les fixe</p>
    <script>
      const g=document.getElementById('g');
      for(let i=0;i<49;i++){const d=document.createElement('div');d.className='cell';g.appendChild(d);}
    </script></body></html>`,
  },
  {
    key: 'cafe_wall',
    label: '🏛 Illusion du Café Wall',
    desc: 'Les lignes paraissent inclinées — elles sont parallèles',
    html: `<!DOCTYPE html><html><head><style>
      body{margin:0;background:#1a1a2e;display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;}
      canvas{border-radius:8px;}
      p{color:#9a8bb0;font-family:sans-serif;font-size:11px;margin-top:10px;text-align:center;}
    </style></head><body>
    <canvas id="cw" width="300" height="260"></canvas>
    <p>Les séparations horizontales semblent diverger — elles sont parfaitement droites</p>
    <script>
      const c=document.getElementById('cw'),ctx=c.getContext('2d');
      const rows=6,cols=6,tw=50,th=38,offset=25;
      for(let r=0;r<rows;r++){
        const off=r%2===0?0:offset;
        for(let co=0;co<cols;co++){
          ctx.fillStyle=(co+r)%2===0?'#ffffff':'#222222';
          ctx.fillRect(co*tw+off,r*th,tw,th);
        }
        ctx.fillStyle='#888';
        ctx.fillRect(0,r*th+th-2,c.width,4);
      }
    </script></body></html>`,
  },
]

export default function ImageFeedback({ src, alt, onIllusionSelect }) {
  const [values,       setValues]       = useState({ brightness: 1.0, contrast: 1.0, saturate: 1.0, blur: 0 })
  const [showControls, setShowControls] = useState(false)
  const [activePreset, setActivePreset] = useState('Naturel')
  const [mode,         setMode]         = useState('image')
  const [zoomed,       setZoomed]       = useState(false)

  const [selIllusion,  setSelIllusion]  = useState(null)
  const [remoteIllusions, setRemoteIllusions] = useState([])   // from Supabase
  const [illusionSource,  setIllusionSource]  = useState('all') // 'remote' | 'builtin' | 'all'
  const [remoteIdx,       setRemoteIdx]       = useState(0)

  const cssFilter = `brightness(${values.brightness}) contrast(${values.contrast}) saturate(${values.saturate}) blur(${values.blur}px)`

  /* Fetch illusion images from Supabase on mount */
  useEffect(() => {
    fetch('/api/media/illusions')
      .then(r => r.ok ? r.json() : [])
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setRemoteIllusions(data)
          setRemoteIdx(Math.floor(Math.random() * data.length))
          setIllusionSource('remote')
        }
      })
      .catch(() => {})
  }, [])

  const pickRandomBuiltin = useCallback(() => {
    const idx = Math.floor(Math.random() * BUILTIN_ILLUSIONS.length)
    setSelIllusion({ ...BUILTIN_ILLUSIONS[idx], remote: false })
  }, [])

  const pickNextRemote = useCallback(() => {
    setRemoteIdx(i => (i + 1) % remoteIllusions.length)
  }, [remoteIllusions.length])

  const pickRandom = useCallback(() => {
    if (illusionSource === 'remote' && remoteIllusions.length > 0) {
      pickNextRemote()
    } else {
      pickRandomBuiltin()
    }
  }, [illusionSource, remoteIllusions.length, pickNextRemote, pickRandomBuiltin])

  /* Dès que l'onglet illusion est ouvert */
  useEffect(() => {
    if (mode === 'illusion' && !selIllusion && illusionSource === 'builtin') {
      pickRandomBuiltin()
    }
  }, [mode, illusionSource])

  /* Escape ferme le zoom */
  useEffect(() => {
    if (!zoomed) return
    const handler = (e) => { if (e.key === 'Escape') setZoomed(false) }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [zoomed])

  return (
    <div style={{ fontFamily: "'Outfit', sans-serif" }}>

      {/* ── Lightbox zoom ── */}
      {zoomed && (
        <div
          onClick={() => setZoomed(false)}
          style={{
            position: 'fixed', inset: 0, zIndex: 9999,
            background: 'rgba(0,0,0,0.88)', backdropFilter: 'blur(8px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'zoom-out',
          }}
        >
          <img
            src={src}
            alt=""
            onClick={e => e.stopPropagation()}
            style={{
              maxWidth: '92vw', maxHeight: '88vh',
              borderRadius: 16, objectFit: 'contain',
              filter: cssFilter, boxShadow: '0 8px 60px rgba(0,0,0,0.7)',
              cursor: 'default',
            }}
          />
          <button
            onClick={() => setZoomed(false)}
            style={{
              position: 'fixed', top: 18, right: 18,
              width: 36, height: 36, borderRadius: 10,
              background: 'rgba(40,30,60,0.9)', border: '1px solid rgba(255,255,255,0.15)',
              color: '#c0b0ff', fontSize: 16, cursor: 'pointer',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}
          >✕</button>
        </div>
      )}

      {/* ── Onglets Image / Illusions optiques ── */}
      <div style={{ display: 'flex', gap: 6, marginBottom: 10 }}>
        {[
          { key: 'image',    label: '🖼 Image thérapeutique' },
          { key: 'illusion', label: '🌀 Illusions optiques' },
        ].map(tab => (
          <button
            key={tab.key}
            onClick={() => { setMode(tab.key); setSelIllusion(null) }}
            style={{
              flex: 1, padding: '6px 10px', borderRadius: 8, fontSize: 11, cursor: 'pointer',
              background: mode === tab.key ? 'rgba(108,99,255,0.25)' : 'rgba(255,255,255,0.04)',
              border: mode === tab.key ? '1.5px solid rgba(108,99,255,0.5)' : '1px solid rgba(255,255,255,0.1)',
              color: mode === tab.key ? '#c0b0ff' : '#7a6890',
              fontWeight: mode === tab.key ? 700 : 400,
            }}
          >{tab.label}</button>
        ))}
      </div>

      {/* ══ MODE IMAGE ══════════════════════════════════════════════════════════ */}
      {mode === 'image' && (
        <>
          <div style={{ position: 'relative', textAlign: 'center', marginBottom: 10 }}>
            <img
              src={src}
              alt=""
              onClick={() => setZoomed(true)}
              style={{ maxWidth: '100%', maxHeight: 340, borderRadius: 12, objectFit: 'cover', filter: cssFilter, transition: 'filter 0.3s ease', cursor: 'zoom-in' }}
            />
            {/* Bouton zoom plein écran */}
            <button
              onClick={() => setZoomed(true)}
              title="Agrandir"
              style={{
                position: 'absolute', top: 8, left: 8,
                padding: '4px 10px', borderRadius: 6, fontSize: 10,
                background: 'rgba(20,16,30,0.75)',
                border: '1px solid rgba(184,123,200,0.4)',
                color: '#9a8bb0',
                cursor: 'pointer', backdropFilter: 'blur(4px)', fontWeight: 600,
              }}
            >⛶ Agrandir</button>
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
            >{showControls ? '✕ Fermer' : '🎛 Ajuster'}</button>
          </div>

          {showControls && (
            <div style={{ background: 'rgba(20,16,30,0.7)', borderRadius: 12, border: '1px solid rgba(184,123,200,0.2)', padding: '12px 14px' }}>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 10, color: '#7a6890', fontWeight: 700, letterSpacing: 1.2, textTransform: 'uppercase', marginBottom: 6 }}>
                  Préréglages EEG
                </div>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                  {PRESETS.map(p => (
                    <button key={p.label} onClick={() => { setValues({ ...p.values }); setActivePreset(p.label) }} title={p.desc}
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
                      <input type="range" min={p.min} max={p.max} step={p.step} value={values[p.key]}
                        onChange={e => { setValues(prev => ({ ...prev, [p.key]: parseFloat(e.target.value) })); setActivePreset(null) }}
                        style={{ position: 'absolute', inset: 0, width: '100%', opacity: 0, cursor: 'pointer', margin: 0, height: '100%' }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </>
      )}

      {/* ══ MODE ILLUSIONS OPTIQUES ════════════════════════════════════════════ */}
      {mode === 'illusion' && (
        <div>
          {/* Source toggle */}
          <div style={{ display: 'flex', gap: 5, marginBottom: 10 }}>
            {remoteIllusions.length > 0 && (
              <button
                onClick={() => setIllusionSource('remote')}
                style={{
                  flex: 1, padding: '5px 8px', borderRadius: 7, fontSize: 10, cursor: 'pointer',
                  background: illusionSource === 'remote' ? 'rgba(108,99,255,0.25)' : 'rgba(255,255,255,0.04)',
                  border: illusionSource === 'remote' ? '1.5px solid rgba(108,99,255,0.5)' : '1px solid rgba(255,255,255,0.1)',
                  color: illusionSource === 'remote' ? '#c0b0ff' : '#7a6890',
                  fontWeight: illusionSource === 'remote' ? 700 : 400,
                }}
              >🖼 Images ({remoteIllusions.length})</button>
            )}
            <button
              onClick={() => { setIllusionSource('builtin'); pickRandomBuiltin() }}
              style={{
                flex: 1, padding: '5px 8px', borderRadius: 7, fontSize: 10, cursor: 'pointer',
                background: illusionSource === 'builtin' ? 'rgba(108,99,255,0.25)' : 'rgba(255,255,255,0.04)',
                border: illusionSource === 'builtin' ? '1.5px solid rgba(108,99,255,0.5)' : '1px solid rgba(255,255,255,0.1)',
                color: illusionSource === 'builtin' ? '#c0b0ff' : '#7a6890',
                fontWeight: illusionSource === 'builtin' ? 700 : 400,
              }}
            >🌀 Interactives ({BUILTIN_ILLUSIONS.length})</button>
          </div>

          {/* ── Remote images from Supabase ── */}
          {illusionSource === 'remote' && remoteIllusions.length > 0 && (() => {
            const img = remoteIllusions[remoteIdx]
            return (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <div>
                    <span style={{ fontSize: 11, color: '#c0b0ff', fontWeight: 600 }}>{img.filename || 'Illusion optique'}</span>
                    <span style={{ fontSize: 9, color: '#7a6890', marginLeft: 8 }}>{remoteIdx + 1} / {remoteIllusions.length}</span>
                  </div>
                  <button
                    onClick={pickNextRemote}
                    style={{ fontSize: 10, color: '#9a8bb0', background: 'none', border: '1px solid rgba(154,139,176,0.3)', borderRadius: 6, cursor: 'pointer', padding: '3px 10px' }}
                  >Suivante →</button>
                </div>
                <div style={{ textAlign: 'center' }}>
                  <img
                    src={img.url}
                    alt={img.filename || ''}
                    style={{ maxWidth: '100%', maxHeight: 400, borderRadius: 12, objectFit: 'contain', cursor: 'zoom-in' }}
                    onClick={() => setZoomed(true)}
                  />
                </div>
                {/* Zoom lightbox for remote illusion */}
                {zoomed && (
                  <div onClick={() => setZoomed(false)} style={{ position: 'fixed', inset: 0, zIndex: 9999, background: 'rgba(0,0,0,0.9)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'zoom-out' }}>
                    <img src={img.url} alt="" style={{ maxWidth: '94vw', maxHeight: '92vh', borderRadius: 16, objectFit: 'contain' }} onClick={e => e.stopPropagation()} />
                    <button onClick={() => setZoomed(false)} style={{ position: 'fixed', top: 18, right: 18, width: 36, height: 36, borderRadius: 10, background: 'rgba(40,30,60,0.9)', border: '1px solid rgba(255,255,255,0.15)', color: '#c0b0ff', fontSize: 16, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>✕</button>
                  </div>
                )}
                {/* Thumbnail strip */}
                {remoteIllusions.length > 1 && (
                  <div style={{ display: 'flex', gap: 5, marginTop: 10, overflowX: 'auto', paddingBottom: 4 }}>
                    {remoteIllusions.map((il, i) => (
                      <img
                        key={il.id || i}
                        src={il.url}
                        alt=""
                        onClick={() => setRemoteIdx(i)}
                        style={{
                          width: 52, height: 40, objectFit: 'cover', borderRadius: 6, cursor: 'pointer', flexShrink: 0,
                          border: i === remoteIdx ? '2px solid #6c63ff' : '2px solid rgba(255,255,255,0.08)',
                          opacity: i === remoteIdx ? 1 : 0.55,
                          transition: 'opacity 0.2s, border 0.2s',
                        }}
                      />
                    ))}
                  </div>
                )}
              </div>
            )
          })()}

          {/* ── Builtin interactive HTML illusions ── */}
          {illusionSource === 'builtin' && selIllusion && (
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                <span style={{ fontSize: 11, color: '#9a8bb0' }}>{selIllusion.desc}</span>
                <button onClick={pickRandomBuiltin} style={{ fontSize: 10, color: '#9a8bb0', background: 'none', border: '1px solid rgba(154,139,176,0.3)', borderRadius: 6, cursor: 'pointer', padding: '3px 10px' }}>
                  Autre →
                </button>
              </div>
              <iframe
                srcDoc={selIllusion.html}
                sandbox="allow-scripts"
                style={{ width: '100%', height: 380, border: 'none', borderRadius: 12 }}
                title={selIllusion.label}
              />
            </div>
          )}
        </div>
      )}
    </div>
  )
}
