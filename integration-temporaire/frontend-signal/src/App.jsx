/**
 * NeuroCap EEG Dashboard — v8.0
 * Compatible : server_final.py v7.1+ · firmware ESP32 v4.9
 *
 * WebSocket entrant :
 *   init · esp32_status · electrode · eeg · epoch · epoch_rejected
 *   baseline_ready · wifi_config_result · esp32_announce
 *
 * WebSocket sortant :
 *   { command: "FINALISE_BASELINE" | "START_REC" | "STOP_REC" | "ANALYZE_NOW" }
 */

import { useState, useEffect, useRef, useCallback } from 'react'
import axios from 'axios'

import { useWebSocket } from './hooks/useWebSocket.js'
import { useRecording } from './hooks/useRecording.js'

import SignalCanvas      from './components/SignalCanvas.jsx'
import BatteryIndicator  from './components/BatteryIndicator.jsx'
import BandBars          from './components/BandBars.jsx'
import FeaturesPanel     from './components/FeaturesPanel.jsx'
import EpochHistory      from './components/EpochHistory.jsx'
import Sidebar           from './components/Sidebar.jsx'
import MLClassifierCard  from './components/MLClassifierCard.jsx'
import FileAnalysisTab   from './components/FileAnalysisTab.jsx'
import Toast, { useToast } from './components/Toast.jsx'

const API  = '/api'   // proxy Vite → http://localhost:8765/api
const TABS = ['LIVE SIGNAL', 'FEATURES', 'HISTORIQUE', 'RAPPORT', 'ANALYSE FICHIER']

const f3 = v => typeof v === 'number' ? v.toFixed(3) : '—'
const f4 = v => typeof v === 'number' ? v.toFixed(4) : '—'
const f1 = (v, u='') => typeof v === 'number' ? `${v.toFixed(1)}${u?' '+u:''}` : '—'

// ─── Composants UI locaux ──────────────────────────────────────────────────

function Sep() {
  return <div style={{ width:1, height:22, background:'rgba(255,255,255,.06)', flexShrink:0 }} />
}

function Btn({ children, onClick, disabled, variant='ghost', style:ext }) {
  const V = {
    ghost:  { bg:'transparent',            bc:'rgba(255,255,255,.1)',    c:'#5a6a7e' },
    accent: { bg:'#00e5b0',                bc:'#00e5b0',                  c:'#000', fw:700 },
    warn:   { bg:'#f5a623',                bc:'#f5a623',                  c:'#000', fw:700 },
    danger: { bg:'#ff4d6d',                bc:'#ff4d6d',                  c:'#fff', fw:700 },
  }[variant] || {}
  return (
    <button onClick={onClick} disabled={disabled} style={{
      padding:'5px 13px', borderRadius:7,
      fontFamily:"'Space Mono',monospace", fontSize:9, letterSpacing:.5,
      cursor: disabled ? 'not-allowed' : 'pointer',
      opacity: disabled ? .3 : 1, transition:'all .15s',
      border:'1px solid', background:V.bg, borderColor:V.bc, color:V.c, fontWeight:V.fw||400,
      display:'inline-flex', alignItems:'center', gap:5,
      ...ext,
    }}>{children}</button>
  )
}

function StatusDot({ active, label, pulse }) {
  return (
    <div style={{ display:'flex', alignItems:'center', gap:6 }}>
      <div style={{
        width:7, height:7, borderRadius:'50%',
        background: active ? '#00e5b0' : '#2a3a4e',
        boxShadow:  active ? '0 0 6px rgba(0,229,176,.5)' : 'none',
        animation:  pulse && active ? 'blink 2s infinite' : 'none',
        transition: 'all .3s',
      }} />
      <span style={{ fontSize:10, color: active ? '#00e5b0' : '#4a5a6e',
                     fontFamily:"'Space Mono',monospace", whiteSpace:'nowrap' }}>
        {label}
      </span>
    </div>
  )
}

function MetricCard({ label, value, unit, warn, accent }) {
  return (
    <div style={{
      background:'#0b0f18',
      border:`1px solid ${warn?'rgba(245,166,35,.2)':accent?'rgba(0,229,176,.15)':'rgba(255,255,255,.05)'}`,
      borderRadius:10, padding:'11px 13px',
    }}>
      <div style={{ fontSize:9, color:'#4a5a6e', marginBottom:5, letterSpacing:.5, textTransform:'uppercase' }}>
        {label}
      </div>
      <div style={{
        fontFamily:"'Space Mono',monospace", fontSize:15, fontWeight:700, lineHeight:1,
        color: warn ? '#f5a623' : accent ? '#00e5b0' : '#d0dce8',
      }}>
        {value}
        {unit && <span style={{ fontSize:9, fontWeight:400, color:'#4a5a6e', marginLeft:3 }}>{unit}</span>}
      </div>
    </div>
  )
}

// ─── APP ──────────────────────────────────────────────────────────────────

export default function App({ onBack } = {}) {
  const [tab, setTab] = useState(0)

  // Connexion
  const [wsConnected,    setWsConnected]    = useState(false)
  const [esp32Connected, setEsp32Connected] = useState(false)
  const [esp32Ip,        setEsp32Ip]        = useState('')
  const [baselineOk,     setBaselineOk]     = useState(false)

  // Signal
  const [battV,       setBattV]       = useState(0)
  const [bands,       setBands]       = useState({ delta:.2,theta:.2,alpha:.2,beta:.2,gamma:.2 })
  const [eegState,    setEegState]    = useState('neutral')
  const [focus,       setFocus]       = useState(1)
  const [stress,      setStress]      = useState(1)
  const [rawMetrics,  setRawMetrics]  = useState({})
  const [calProgress, setCalProgress] = useState(0)
  const [lastSample,  setLastSample]  = useState(null)

  // Électrodes
  const [electrodeOk,  setElectrodeOk]  = useState(false)
  const [fp2Connected, setFp2Connected] = useState(false)
  const [m2Connected,  setM2Connected]  = useState(false)

  // Classification ML
  const [mlPrediction,  setMlPrediction]  = useState(null)

  // Époques
  const [epochs,        setEpochs]        = useState([])
  const [currentEpoch,  setCurrentEpoch]  = useState(null)
  const [epochCount,    setEpochCount]    = useState(0)
  const [rejectedCount, setRejectedCount] = useState(0)

  const { toast, toastState } = useToast()
  const rec = useRecording()
  const manualClose = useRef(false)

  // ── Qualité signal ──
  const qi = (() => {
    if (!wsConnected)          return { label:'✕ Déconnecté',     cls:'fail' }
    if (!electrodeOk)          return { label:'✕ Électrodes KO',  cls:'fail' }
    if (!rawMetrics.rms_raw)   return { label:'⋯ En attente…',    cls:'idle' }
    if (rawMetrics.rms_raw < 2) return { label:'✕ Signal faible', cls:'fail' }
    if (rawMetrics.rms_raw > 200) return { label:'⚠ Amplitude forte', cls:'warn' }
    return { label:'✓ Signal OK', cls:'ok' }
  })()

  // ── Handler WebSocket ──
  const handleMessage = useCallback((d) => {
    switch (d.type) {

      case 'init':
        setEsp32Connected(!!d.esp32_connected)
        setEsp32Ip(d.esp32_ip || '')
        setBaselineOk(!!d.baseline_ok)
        if (d.electrode_ok !== undefined) {
          setElectrodeOk(!!d.electrode_ok)
          setFp2Connected(!!d.fp2_connected)
          setM2Connected(!!d.m2_connected)
        }
        break

      case 'esp32_status':
        setEsp32Connected(!!d.connected)
        setEsp32Ip(d.ip || '')
        if (!d.connected) {
          setElectrodeOk(false); setFp2Connected(false); setM2Connected(false)
        }
        break

      case 'electrode':
        setElectrodeOk(!!d.electrode_ok)
        setFp2Connected(!!d.fp2_connected)
        setM2Connected(!!d.m2_connected)
        break

      case 'eeg':
        setLastSample({ uv: d.uv, filtered: d.filtered })
        if (d.electrode_ok !== undefined) {
          setElectrodeOk(!!d.electrode_ok)
          setFp2Connected(!!d.fp2_connected)
          setM2Connected(!!d.m2_connected)
        }
        if (d.bands)                      setBands(d.bands)
        if (d.state)                      setEegState(d.state)
        if (d.focus  !== undefined)       setFocus(d.focus)
        if (d.stress !== undefined)       setStress(d.stress)
        if (d.raw_metrics)                setRawMetrics(d.raw_metrics)
        if (d.batt_V !== undefined)       setBattV(d.batt_V)
        if (d.cal_progress !== undefined) setCalProgress(d.cal_progress)
        break

      case 'epoch':
        setCurrentEpoch(d)
        setEpochCount(d.stats?.accepted   ?? 0)
        setRejectedCount(d.stats?.rejected ?? 0)
        if (d.ml_prediction) setMlPrediction(d.ml_prediction)
        setEpochs(prev => {
          const next = [...prev, {
            idx: d.epoch_idx, timestamp: d.timestamp,
            features: d.features, graph: d.graph, rejected: false,
            ml_prediction: d.ml_prediction ?? null,
          }]
          return next.length > 60 ? next.slice(-60) : next
        })
        break

      case 'epoch_rejected':
        setRejectedCount(p => p + 1)
        setEpochs(prev => {
          const next = [...prev, { idx:prev.length+1, timestamp:new Date().toISOString(),
                                   rejected:true, reason:d.reason||'rejeté' }]
          return next.length > 60 ? next.slice(-60) : next
        })
        break

      case 'baseline_ready':
        setBaselineOk(!!d.success)
        toast(d.success ? '✓ Baseline finalisée' : "⚠ Pas assez d'époques")
        break

      case 'esp32_announce':
        toast(`📡 ESP32 détecté — ${d.ip}`)
        break

      case 'wifi_config_result':
        toast(d.success ? `✓ WiFi OK — ${d.ip}` : `✕ WiFi échoué : ${d.reason||'erreur'}`)
        break

      default: break
    }
  }, [toast])

  // ── WebSocket ──
  const { send, connect: wsConnect, disconnect: wsDisconnect } = useWebSocket(
    'ws://localhost:8765/ws',
    { onOpen:()=>setWsConnected(true), onClose:()=>setWsConnected(false), onMessage:handleMessage }
  )

  // Auto-connexion
  useEffect(() => {
    const t = setTimeout(() => wsConnect(), 300)
    return () => clearTimeout(t)
  }, [wsConnect])

  // Reconnexion auto (3s)
  useEffect(() => {
    if (!wsConnected && !manualClose.current) {
      const t = setTimeout(() => wsConnect(), 3000)
      return () => clearTimeout(t)
    }
  }, [wsConnected, wsConnect])

  // ── Actions ──
  const handleBaseline = () => { send({ command:'FINALISE_BASELINE' }); toast('Baseline en cours…') }
  const handleAnalyze  = () => { send({ command:'ANALYZE_NOW' }); toast('Analyse lancée…') }

  const handleExportCSV = async () => {
    try {
      const r = await axios.get(`${API}/recording/export`, { responseType:'blob' })
      const url = URL.createObjectURL(r.data)
      Object.assign(document.createElement('a'), {
        href: url,
        download: `neurocap_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.csv`
      }).click()
      URL.revokeObjectURL(url)
      toast('✓ CSV téléchargé')
    } catch { toast('✕ Aucun enregistrement') }
  }

  const handleReplay = (ep) => {
    if (!ep.rejected) {
      setCurrentEpoch({ features:ep.features, graph:ep.graph, epoch_idx:ep.idx })
      setTab(1)
    }
    toast(`Replay époque #${ep.idx}`)
  }

  const feat  = currentEpoch?.features ?? {}
  const graph = currentEpoch?.graph    ?? {}

  // ── RENDER ──
  return (
    <div style={{ display:'flex', flexDirection:'column', height:'100vh', overflow:'hidden', background:'#07090f' }}>
      <style>{`
        @keyframes blink  { 0%,100%{opacity:1} 50%{opacity:.15} }
        @keyframes fadeIn { from{opacity:0;transform:translateY(4px)} to{opacity:1;transform:translateY(0)} }
      `}</style>

      {/* ══ HEADER LIGNE 1 ══ */}
      <header style={{
        height:50, background:'#080c14',
        borderBottom:'1px solid rgba(255,255,255,.05)',
        display:'flex', alignItems:'center', padding:'0 18px', gap:14, flexShrink:0,
      }}>
        <div style={{ flexShrink:0 }}>
          <div style={{ fontFamily:"'Space Mono',monospace", fontSize:12, fontWeight:700,
                        letterSpacing:2.5, color:'#00e5b0' }}>
            NEUROCAP <span style={{ color:'#2a3a4e', fontWeight:400 }}>EEG</span>
          </div>
          <div style={{ fontSize:8, color:'#2a3a4e', letterSpacing:1, marginTop:1 }}>
            v8 · Fp2 · 250 Hz · GAIN_TWO · 62.5 µV/LSB
          </div>
        </div>
        <Sep />
        <BatteryIndicator voltage={battV} />
        <Sep />

        {/* Badge REC */}
        <div style={{
          display:'flex', alignItems:'center', gap:6,
          padding:'4px 12px', background:'rgba(255,255,255,.02)',
          border:'1px solid rgba(255,255,255,.05)', borderRadius:6,
          fontFamily:"'Space Mono',monospace", fontSize:9, color:'#4a5a6e',
        }}>
          <div style={{
            width:7, height:7, borderRadius:'50%',
            background: rec.rec ? (rec.paused?'#f5a623':'#ff4d6d') : '#2a3a4e',
            animation: rec.rec && !rec.paused ? 'blink 1s infinite' : 'none',
          }} />
          {rec.rec ? (rec.paused ? `PAUSE ${rec.fmt(rec.recT)}` : `REC ${rec.fmt(rec.recT)}`) : 'LIVE'}
        </div>

        <div style={{ marginLeft:'auto', display:'flex', gap:8, alignItems:'center' }}>
          <span className={`q-badge q-${qi.cls}`}>{qi.label}</span>
          <Sep />
          <Btn onClick={handleExportCSV}>⬇ CSV</Btn>
          {onBack && (
            <>
              <Sep />
              <Btn onClick={onBack}>← Accueil</Btn>
            </>
          )}
        </div>
      </header>

      {/* ══ HEADER LIGNE 2 — statuts ══ */}
      <div style={{
        height:30, background:'rgba(0,229,176,.015)',
        borderBottom:'1px solid rgba(255,255,255,.04)',
        display:'flex', alignItems:'center', padding:'0 18px', gap:24, flexShrink:0,
      }}>
        <StatusDot active={wsConnected}    label={wsConnected?'WebSocket OK':'WebSocket —'} />
        <StatusDot active={esp32Connected} label={esp32Connected?`ESP32 ${esp32Ip}`:'ESP32 —'} pulse />
        <div style={{ display:'flex', gap:8 }}>
          {[{id:'Fp2',ok:fp2Connected},{id:'M2',ok:m2Connected},{id:'M1',ok:true}].map(({id,ok}) => (
            <span key={id} style={{
              fontFamily:"'Space Mono',monospace", fontSize:9, padding:'1px 7px', borderRadius:4,
              background: ok?'rgba(0,229,176,.08)':'rgba(255,77,109,.08)',
              color:       ok?'#00e5b0':'#ff4d6d',
              border:`1px solid ${ok?'rgba(0,229,176,.2)':'rgba(255,77,109,.2)'}`,
            }}>{id} {ok?'✓':'✕'}</span>
          ))}
        </div>
        <div style={{ marginLeft:'auto', display:'flex', gap:16, color:'#4a5a6e', fontSize:10 }}>
          <span>Cal. <span style={{ fontFamily:"'Space Mono',monospace",
                                   color:calProgress>=100?'#00e5b0':'#f5a623' }}>
            {Math.round(calProgress)}%</span></span>
          <span>Époques <span style={{ fontFamily:"'Space Mono',monospace", color:'#00e5b0' }}>
            {epochCount}</span></span>
          <span>Rejetées <span style={{ fontFamily:"'Space Mono',monospace", color:'#f5a623' }}>
            {rejectedCount}</span></span>
        </div>
      </div>

      {/* ══ HEADER LIGNE 3 — onglets + actions ══ */}
      <div style={{
        height:42, background:'#080c14',
        borderBottom:'1px solid rgba(255,255,255,.05)',
        display:'flex', alignItems:'center', padding:'0 18px', gap:2, flexShrink:0,
      }}>
        {TABS.map((t,i) => (
          <button key={t} onClick={() => setTab(i)} style={{
            height:'100%', padding:'0 18px', border:'none',
            borderBottom:`2px solid ${tab===i?'#00e5b0':'transparent'}`,
            background:'transparent', fontFamily:"'Space Mono',monospace",
            fontSize:9, letterSpacing:1, textTransform:'uppercase',
            color: tab===i?'#00e5b0':'#3a4a5e', cursor:'pointer', transition:'all .15s',
          }}>{t}</button>
        ))}
        <div style={{ marginLeft:'auto', display:'flex', gap:6, alignItems:'center' }}>
          {!rec.rec
            ? <Btn variant="accent" onClick={rec.start}>▶ START</Btn>
            : rec.paused
              ? <><Btn variant="accent" onClick={rec.resume}>▶ RESUME</Btn>
                  <Btn variant="danger" onClick={rec.stop}>■ STOP</Btn></>
              : <><Btn variant="warn"  onClick={rec.pause}>⏸ PAUSE</Btn>
                  <Btn variant="danger" onClick={rec.stop}>■ STOP</Btn></>
          }
          <Sep />
          <Btn onClick={handleBaseline}>BASELINE</Btn>
          <Btn onClick={handleAnalyze} disabled={epochCount===0}>ANALYZE</Btn>
          <Sep />
          <Btn onClick={() => { manualClose.current=false; wsConnect() }}
               disabled={wsConnected}>CONNECT</Btn>
          <Btn onClick={() => { manualClose.current=true; wsDisconnect() }}
               disabled={!wsConnected}>✕ DÉCO</Btn>
        </div>
      </div>

      {/* ══ BODY ══ */}
      <div style={{ flex:1, display:'flex', overflow:'hidden' }}>

        <Sidebar
          state={eegState} focus={focus} stress={stress} bands={bands}
          electrodeOk={electrodeOk} fp2Connected={fp2Connected} m2Connected={m2Connected}
          calProgress={calProgress} rawMetrics={rawMetrics}
          pipeActive={wsConnected && electrodeOk}
          epochCount={epochCount} rejectedCount={rejectedCount}
        />

        <main style={{ flex:1, overflowY:'auto', padding:18,
                       display:'flex', flexDirection:'column', gap:14 }}>

          {/* ══ TAB 0 — LIVE SIGNAL ══ */}
          {tab === 0 && (
            <>
              {/* Oscilloscope */}
              <div style={{
                height:300, background:'#060a12',
                border:'1px solid rgba(255,255,255,.05)',
                borderRadius:14, padding:'12px 14px',
                display:'flex', flexDirection:'column', gap:8,
              }}>
                <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                  <span style={{ fontFamily:"'Space Mono',monospace", fontSize:9,
                                 letterSpacing:1.5, color:'#3a4a5e' }}>
                    LIVE EEG · Fp2 · 250 Hz · ±µV
                  </span>
                  <StatusDot active={electrodeOk} label={electrodeOk?'Électrodes OK':'Électrodes KO'} />
                </div>
                <div style={{ flex:1, minHeight:0 }}>
                  <SignalCanvas wsData={lastSample} electrodeOk={electrodeOk} />
                </div>
              </div>

              {/* 6 métriques */}
              <div style={{ display:'grid', gridTemplateColumns:'repeat(6,1fr)', gap:10 }}>
                <MetricCard label="RMS"          value={f1(rawMetrics.rms_raw)} unit="µV" />
                <MetricCard label="Peak"         value={f1(rawMetrics.peak)}    unit="µV" warn={rawMetrics.peak>300} />
                <MetricCard label="Engagement"   value={f3(feat.engagement)}    accent={feat.engagement>1.5} />
                <MetricCard label="Stress β/α"   value={f3(feat.stress_idx)}    warn={feat.stress_idx>2} />
                <MetricCard label="SEF95"        value={f1(feat.sef95)}         unit="Hz" />
                <MetricCard label="PAC θ→γ"      value={f4(feat.pac_theta_gamma)} accent={feat.pac_theta_gamma>0.3} />
              </div>

              {/* ── Classifieur ML ── */}
              <MLClassifierCard prediction={mlPrediction} />

              {/* Features rapides */}
              {currentEpoch ? (
                <div style={{ display:'grid', gridTemplateColumns:'repeat(3,1fr)', gap:12 }}>
                  {/* Bandes rel. */}
                  <div style={{ background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)',
                                borderRadius:12, padding:'12px 14px' }}>
                    <div style={{ fontSize:9, color:'#4da6ff', letterSpacing:1,
                                  textTransform:'uppercase', marginBottom:10 }}>
                      Puissances relatives
                    </div>
                    <BandBars bands={bands} />
                  </div>
                  {/* Hjorth */}
                  <div style={{ background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)',
                                borderRadius:12, padding:'12px 14px' }}>
                    <div style={{ fontSize:9, color:'#00e5b0', letterSpacing:1,
                                  textTransform:'uppercase', marginBottom:10 }}>
                      Hjorth Parameters
                    </div>
                    {[['Activity',  feat.hjorth_activity],
                      ['Mobility',  feat.hjorth_mobility],
                      ['Complexity',feat.hjorth_complexity]].map(([l,v]) => (
                      <div key={l} style={{ display:'flex', justifyContent:'space-between',
                                           padding:'5px 0', borderBottom:'1px solid rgba(255,255,255,.04)',
                                           fontSize:11 }}>
                        <span style={{ color:'#4a5a6e' }}>{l}</span>
                        <span style={{ fontFamily:"'Space Mono',monospace", color:'#c9d8e8' }}>{f4(v)}</span>
                      </div>
                    ))}
                  </div>
                  {/* Fractal */}
                  <div style={{ background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)',
                                borderRadius:12, padding:'12px 14px' }}>
                    <div style={{ fontSize:9, color:'#ec4899', letterSpacing:1,
                                  textTransform:'uppercase', marginBottom:10 }}>
                      Fractal & PAC
                    </div>
                    {[['PAC θ→γ',   feat.pac_theta_gamma],
                      ['FD global', feat.fractal_dim],
                      ['Clustering',feat.fd_clustering_coeff],
                      ['Jaccard',   feat.fd_jaccard_mean]].map(([l,v]) => (
                      <div key={l} style={{ display:'flex', justifyContent:'space-between',
                                           padding:'5px 0', borderBottom:'1px solid rgba(255,255,255,.04)',
                                           fontSize:11 }}>
                        <span style={{ color:'#4a5a6e' }}>{l}</span>
                        <span style={{ fontFamily:"'Space Mono',monospace", color:'#c9d8e8' }}>{f4(v)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div style={{
                  background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)',
                  borderRadius:14, padding:48, textAlign:'center',
                  color:'#3a4a5e', fontSize:13, lineHeight:1.9,
                }}>
                  <div style={{ fontSize:32, marginBottom:12 }}>📊</div>
                  En attente de la première époque (4s de signal)…<br/>
                  <span style={{ fontSize:11 }}>Connectez les électrodes Fp2 · M2 · M1</span>
                </div>
              )}
            </>
          )}

          {/* ══ TAB 1 — FEATURES ══ */}
          {tab === 1 && (
            <FeaturesPanel features={feat} graph={graph} epochIdx={currentEpoch?.epoch_idx} />
          )}

          {/* ══ TAB 2 — HISTORIQUE ══ */}
          {tab === 2 && (
            <EpochHistory epochs={epochs} onReplay={handleReplay} />
          )}

          {/* ══ TAB 3 — RAPPORT ══ */}
          {tab === 3 && (
            <div style={{
              background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)',
              borderRadius:14, padding:28,
            }}>
              <div style={{ fontFamily:"'Space Mono',monospace", fontSize:10, color:'#4a5a6e',
                            letterSpacing:2, textTransform:'uppercase', marginBottom:20 }}>
                Rapport de session
              </div>

              {epochCount === 0 ? (
                <div style={{ color:'#3a4a5e', textAlign:'center', padding:'40px 0', fontSize:13, lineHeight:1.9 }}>
                  <div style={{ fontSize:32, marginBottom:12 }}>📝</div>
                  Aucune époque enregistrée.
                </div>
              ) : (
                <>
                  <div style={{ border:'1px solid rgba(255,255,255,.05)', borderRadius:10,
                                overflow:'hidden', marginBottom:20 }}>
                    {[
                      ['ESP32 IP',           esp32Ip||'—'],
                      ['Tension batterie',   battV>0?`${battV.toFixed(2)} V`:'—'],
                      ['Époques acceptées',  epochCount-rejectedCount, true],
                      ['Époques rejetées',   rejectedCount, false, rejectedCount>0],
                      ["Taux d'acceptation", `${Math.round(((epochCount-rejectedCount)/Math.max(1,epochCount))*100)}%`],
                      ['État dominant',      eegState.toUpperCase()],
                      ['Focus moyen',        f3(focus)],
                      ['Stress moyen β/α',   f3(stress), false, stress>2],
                      ['Baseline',           baselineOk?'✓ Calculée':'— Non calculée', baselineOk],
                      ['── ML Classifieur ──', ''],
                      ['État ML (dernier)',   mlPrediction ? (mlPrediction.uncertain ? '⚠ Incertain' : mlPrediction.state?.toUpperCase() || '—') : '—', mlPrediction && !mlPrediction.uncertain && mlPrediction.state==='concentration', mlPrediction && !mlPrediction.uncertain && mlPrediction.state==='stress'],
                      ['Concentration ML',   mlPrediction ? f1(mlPrediction.concentration*100,'%') : '—', mlPrediction?.state==='concentration'],
                      ['Stress ML',          mlPrediction ? f1(mlPrediction.stress*100,'%')        : '—', false, mlPrediction?.state==='stress'],
                      ['Confiance',          mlPrediction ? f1(mlPrediction.confidence*100,'%')    : '—', mlPrediction?.confidence>=0.6, mlPrediction?.uncertain],
                      ['Mode',               mlPrediction?.mode || '—'],
                      ['── Signal ──', ''],
                      ['PAC θ→γ',            f4(feat.pac_theta_gamma)],
                      ['FD global',          f4(feat.fractal_dim)],
                      ['SEF95',              f1(feat.sef95,'Hz')],
                      ['Entropie spectrale', f4(feat.spectral_entropy)],
                      ['Hjorth Complexity',  f4(feat.hjorth_complexity)],
                    ].map(([lbl,val,acc,wrn],i) => (
                      <div key={lbl} style={{
                        display:'flex', justifyContent:'space-between', alignItems:'center',
                        padding:'9px 16px',
                        background: i%2===0?'rgba(255,255,255,.01)':'transparent',
                        borderBottom:'1px solid rgba(255,255,255,.03)', fontSize:12,
                      }}>
                        <span style={{ color:'#5a6a7e' }}>{lbl}</span>
                        <span style={{
                          fontFamily:"'Space Mono',monospace", fontWeight:600,
                          color: acc?'#00e5b0':wrn?'#f5a623':'#c9d8e8',
                        }}>{val}</span>
                      </div>
                    ))}
                  </div>
                  <div style={{ display:'flex', gap:10 }}>
                    <Btn variant="accent" onClick={handleAnalyze}>🔍 ANALYZE</Btn>
                    <Btn variant="accent" onClick={handleExportCSV}>⬇ CSV</Btn>
                    <Btn onClick={handleBaseline}>BASELINE</Btn>
                  </div>
                </>
              )}
            </div>
          )}

          {/* ══ TAB 4 — ANALYSE FICHIER ══ */}
          {tab === 4 && (
            <FileAnalysisTab />
          )}

        </main>
      </div>

      <Toast message={toastState.message} show={toastState.show} />
    </div>
  )
}
