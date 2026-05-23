/**
 * ProtocolDashboard — Tableau de bord 15 séances
 * Mou et al. 2024 (npj Science of Learning) — alpha neurofeedback adaptatif
 *
 * API utilisée (déjà disponible dans neurofeedback_protocol.py) :
 *   GET /api/protocol/user/{user_id}
 *   → { user_id, sessions_done, next_session, palier, palier_info, p_alpha_hist, history }
 *   Chaque session dans history : { session_n, palier, started_at, ended_at, taux_succes_global, blocs[] }
 */

import { useState, useEffect } from 'react'

// ─── Constantes ───────────────────────────────────────────────────────────────

const PHASES = [
  { id: 1, label: 'Découverte',    sessions: [1, 2, 3],                 color: '#7BC4A0' },
  { id: 2, label: 'Entraînement',  sessions: [4, 5, 6, 7, 8, 9, 10],   color: '#7BA8C4' },
  { id: 3, label: 'Consolidation', sessions: [11, 12, 13, 14, 15],      color: '#B87B9E' },
]
const BILAN_SESSIONS = new Set([5, 10, 15])

const PALIER_COLORS = { P1: '#7BC4A0', P2: '#7BA8C4', P3: '#B87B9E', P4: '#E87B9E' }

const PALIER_DESC = {
  P1: 'Découverte · S1-S3 · facteur 85–90 %',
  P2: 'Apprentissage · S4-S7 · facteur 95–110 %',
  P3: 'Consolidation · S8-S12 · facteur 110–125 %',
  P4: 'Maîtrise · S13-S15 · facteur 125–140 %',
}

const P = {
  bg: '#C5D3E8', card: 'rgba(247,243,250,0.55)',
  border: 'rgba(255,255,255,0.45)', text: '#2B2A4A', text2: '#9A8BAE',
  accent: '#B87B9E', shadow: 'rgba(180,169,196,0.35)',
}

// ─── Session Circle ───────────────────────────────────────────────────────────

function SessionCircle({ n, status, taux, palier, sessionData, onClick }) {
  const [hovered, setHovered] = useState(false)
  const isBilan = BILAN_SESSIONS.has(n)

  const styles = {
    locked:    { bg: 'rgba(255,255,255,0.15)', border: 'rgba(255,255,255,0.25)', color: '#9A8BAE' },
    available: { bg: 'rgba(184,123,158,0.2)',  border: '#B87B9E',                color: '#B87B9E' },
    completed: { bg: isBilan ? 'rgba(255,215,0,0.15)' : 'rgba(123,196,160,0.2)', border: isBilan ? '#FFD700' : '#7BC4A0', color: isBilan ? '#8B6914' : '#3a7a5e' },
  }
  const s = styles[status] || styles.locked
  const score = taux != null ? Math.round(taux * 100) : null

  return (
    <div style={{ position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
      <button
        onClick={() => onClick(n, status)}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
        style={{
          width: 50, height: 50, borderRadius: '50%',
          background: s.bg, border: `2px solid ${s.border}`, color: s.color,
          fontSize: status === 'available' ? 16 : 12, fontWeight: 700,
          cursor: status === 'locked' ? 'not-allowed' : 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'all .2s ease', fontFamily: "'DM Mono',monospace",
          animation: status === 'available' ? 'circPulse 2s ease-in-out infinite' : 'none',
          transform: hovered && status !== 'locked' ? 'scale(1.1)' : 'scale(1)',
          boxShadow: hovered && status !== 'locked' ? `0 0 18px ${s.border}70` : 'none',
        }}
      >
        {status === 'completed' ? (isBilan ? '★' : '✓') : (status === 'available' ? '▶' : n)}
      </button>

      <span style={{ fontSize: 8, color: P.text2, fontFamily: "'DM Mono',monospace" }}>S{n}</span>

      {score !== null && status === 'completed' && (
        <span style={{ fontSize: 8, fontFamily: "'DM Mono',monospace", color: score >= 60 ? '#3a7a5e' : '#8a5a4e', fontWeight: 700 }}>
          {score}%
        </span>
      )}

      {/* Tooltip hover */}
      {hovered && sessionData && (
        <div style={{
          position: 'absolute', bottom: '115%', left: '50%', transform: 'translateX(-50%)',
          background: 'rgba(43,42,74,0.96)', borderRadius: 10, padding: '10px 12px',
          width: 175, zIndex: 200, border: '1px solid rgba(255,255,255,0.15)',
          boxShadow: '0 8px 24px rgba(0,0,0,0.3)', pointerEvents: 'none',
        }}>
          <div style={{ fontSize: 10, fontWeight: 700, color: '#fff', marginBottom: 4 }}>Séance {sessionData.session_n}</div>
          <div style={{ fontSize: 9, color: '#9A8BAE', lineHeight: 1.7 }}>
            📅 {sessionData.ended_at ? sessionData.ended_at.slice(0, 10) : '—'}<br />
            ✅ Taux succès : <b style={{ color: '#7BC4A0' }}>{sessionData.taux_succes_global != null ? Math.round(sessionData.taux_succes_global * 100) + '%' : '—'}</b><br />
            🏅 Palier : {sessionData.palier}<br />
            📊 Blocs : {sessionData.blocs?.length ?? 0}
          </div>
          <div style={{ position: 'absolute', top: '100%', left: '50%', transform: 'translateX(-50%)', width: 0, height: 0, borderLeft: '5px solid transparent', borderRight: '5px solid transparent', borderTop: '5px solid rgba(43,42,74,0.96)' }} />
        </div>
      )}
    </div>
  )
}

// ─── Stat Card ────────────────────────────────────────────────────────────────

function StatCard({ label, value, sub, color }) {
  return (
    <div style={{ flex: 1, minWidth: 110, background: P.card, borderRadius: 14, padding: '14px 16px', border: `1px solid ${P.border}`, backdropFilter: 'blur(10px)', boxShadow: `0 4px 16px ${P.shadow}` }}>
      <div style={{ fontSize: 9, color: P.text2, fontFamily: "'DM Mono',monospace", letterSpacing: 1, marginBottom: 6, textTransform: 'uppercase' }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 800, color: color || P.text, lineHeight: 1.1 }}>{value}</div>
      {sub && <div style={{ fontSize: 10, color: P.text2, marginTop: 4 }}>{sub}</div>}
    </div>
  )
}

// ─── Graphe SVG de progression ────────────────────────────────────────────────

function ProgressGraph({ history }) {
  if (!history || history.length === 0) return null
  const completed = history.filter(s => s.ended_at && s.taux_succes_global != null)
  if (completed.length < 2) return null
  const W = 380, H = 72

  const pts = completed.map((s, i) => ({
    x: 20 + (i / (completed.length - 1)) * (W - 40),
    y: H - 10 - s.taux_succes_global * (H - 20),
    n: s.session_n,
    bilan: BILAN_SESSIONS.has(s.session_n),
    val: s.taux_succes_global,
  }))

  const path = pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ')

  return (
    <div style={{ marginTop: 16 }}>
      <div style={{ fontSize: 9, color: P.text2, fontFamily: "'DM Mono',monospace", letterSpacing: 1, marginBottom: 8 }}>TAUX DE SUCCÈS PAR SÉANCE (%)</div>
      <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ overflow: 'visible' }}>
        {[0.25, 0.5, 0.6, 0.75].map(v => (
          <line key={v} x1={20} y1={H - 10 - v * (H - 20)} x2={W - 20} y2={H - 10 - v * (H - 20)}
            stroke="rgba(43,42,74,0.08)" strokeWidth={1} strokeDasharray={v === 0.6 ? '4,4' : '2,6'} />
        ))}
        <text x={4} y={H - 10 - 0.6 * (H - 20) + 3} fill="#C4A87B" fontSize={7} fontFamily="'DM Mono',monospace">60%</text>
        {[25, 50, 75, 100].map(v => (
          <text key={v} x={4} y={H - 10 - (v / 100) * (H - 20) + 3} fill="#9A8BAE" fontSize={6} fontFamily="'DM Mono',monospace">{v}</text>
        ))}
        <path d={path} fill="none" stroke="#B87B9E" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        {pts.map(pt => (
          <g key={pt.n}>
            <circle cx={pt.x} cy={pt.y} r={pt.bilan ? 6 : 4} fill={pt.bilan ? '#FFD700' : '#B87B9E'} stroke="white" strokeWidth={1.5} />
            {pt.bilan && <text x={pt.x} y={pt.y - 9} textAnchor="middle" fill="#8B6914" fontSize={7}>★</text>}
            <text x={pt.x} y={H + 1} textAnchor="middle" fill="#9A8BAE" fontSize={6} fontFamily="'DM Mono',monospace">S{pt.n}</text>
          </g>
        ))}
      </svg>
    </div>
  )
}

// ─── Composant principal ──────────────────────────────────────────────────────

export default function ProtocolDashboard({ userId = 'demo', onStartSession, onBack }) {
  const [data, setData]       = useState(null)
  const [loading, setLoading] = useState(true)
  const [demoMode, setDemoMode] = useState(false)

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch(`/api/protocol/user/${userId}`)
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        setData(await res.json())
      } catch (e) {
        console.warn('[ProtocolDashboard] API indisponible, mode démo', e.message)
        // Données démo pour visualiser le dashboard sans backend
        setData({
          user_id: userId, sessions_done: 3, next_session: 4,
          palier: 'P2', palier_info: { factor_min: 0.95, factor_max: 1.10, delta: 0.5 },
          p_alpha_hist: 14.2,
          history: [
            { session_n: 1, palier: 'P1', started_at: '2026-05-01T10:00:00', ended_at: '2026-05-01T10:35:00', taux_succes_global: 0.52, blocs: [{},{},{},{},{}] },
            { session_n: 2, palier: 'P1', started_at: '2026-05-05T10:00:00', ended_at: '2026-05-05T10:38:00', taux_succes_global: 0.61, blocs: [{},{},{},{},{}] },
            { session_n: 3, palier: 'P1', started_at: '2026-05-08T10:00:00', ended_at: '2026-05-08T10:36:00', taux_succes_global: 0.68, blocs: [{},{},{},{},{}] },
          ],
        })
        setDemoMode(true)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [userId])

  if (loading) {
    return (
      <div style={{ background: P.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ textAlign: 'center', color: P.text2, fontFamily: "'DM Mono',monospace" }}>
          <div style={{ fontSize: 28, marginBottom: 12 }}>🧠</div>Chargement du programme…
        </div>
      </div>
    )
  }

  // Construire la map session_n → données
  const historyMap = {}
  for (const s of (data?.history || [])) historyMap[s.session_n] = s
  const completedSet = new Set(Object.values(historyMap).filter(s => s.ended_at).map(s => s.session_n))
  const nextSession  = data?.next_session ?? 1
  const palier       = data?.palier ?? 'P1'
  const palierColor  = PALIER_COLORS[palier] ?? '#7BC4A0'

  const getStatus = (n) => {
    if (completedSet.has(n)) return 'completed'
    if (n === nextSession)   return 'available'
    return 'locked'
  }

  const history    = data?.history || []
  const completed  = history.filter(s => s.ended_at)
  const last5taux  = completed.slice(-5).map(s => s.taux_succes_global).filter(v => v != null)
  const avgTaux5   = last5taux.length ? Math.round(last5taux.reduce((a, b) => a + b, 0) / last5taux.length * 100) : null
  const nextBilan  = [5, 10, 15].find(b => b >= nextSession) ?? 15
  const bilanDelta = nextBilan - nextSession

  const handleCircleClick = (n, status) => {
    if (status === 'available' && onStartSession) onStartSession(n)
  }

  return (
    <div style={{ background: P.bg, minHeight: '100vh', fontFamily: "'DM Sans', system-ui, sans-serif", padding: '24px 20px' }}>
      <style>{`
        @keyframes circPulse { 0%,100%{box-shadow:0 0 0 0 rgba(184,123,158,.4)} 50%{box-shadow:0 0 0 10px rgba(184,123,158,0)} }
      `}</style>

      {/* ── En-tête ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 24 }}>
        <div>
          <div style={{ fontSize: 22, fontWeight: 800, color: P.text }}>Protocole 15 séances</div>
          <div style={{ fontSize: 12, color: P.text2, marginTop: 2 }}>Neurofeedback alpha adaptatif · Mou et al. 2024</div>
          {demoMode && <div style={{ fontSize: 10, color: '#C4A87B', marginTop: 4, fontFamily: "'DM Mono',monospace" }}>⚠ Mode démo — API non disponible</div>}
        </div>
        {onBack && (
          <button onClick={onBack} style={{ padding: '8px 16px', borderRadius: 10, border: `1px solid ${P.border}`, background: 'transparent', color: P.text2, fontSize: 12, cursor: 'pointer' }}>
            ← Accueil
          </button>
        )}
      </div>

      {/* ── Cards indicateurs ── */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 24 }}>
        <StatCard label="Séances complétées" value={`${completed.length} / 15`} sub={`Phase actuelle : ${PHASES.find(ph => ph.sessions.includes(nextSession))?.label ?? 'Terminé'}`} color="#7BC4A0" />
        <StatCard label="Palier actuel"       value={palier} sub={PALIER_DESC[palier]} color={palierColor} />
        <StatCard label="Score moyen (5 der.)" value={avgTaux5 != null ? `${avgTaux5}%` : '—'} sub={avgTaux5 >= 60 ? '✓ Objectif atteint (> 60%)' : 'Objectif : 60%'} color={avgTaux5 >= 60 ? '#7BC4A0' : '#C4A87B'} />
        <StatCard label="Prochain bilan" value={`S${nextBilan}`} sub={bilanDelta === 0 ? 'C\'est maintenant !' : `dans ${bilanDelta} séance(s)`} color="#FFD700" />
      </div>

      {/* ── Cercles 15 séances ── */}
      <div style={{ background: P.card, borderRadius: 20, padding: '22px', border: `1px solid ${P.border}`, backdropFilter: 'blur(12px)', boxShadow: `0 8px 32px ${P.shadow}`, marginBottom: 20 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: P.text, marginBottom: 20 }}>Progression des séances</div>
        {PHASES.map(phase => (
          <div key={phase.id} style={{ marginBottom: 22 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
              <div style={{ width: 4, height: 16, borderRadius: 2, background: phase.color }} />
              <span style={{ fontSize: 10, fontWeight: 700, color: phase.color, fontFamily: "'DM Mono',monospace", letterSpacing: 1, textTransform: 'uppercase' }}>
                Phase {phase.id} — {phase.label}
              </span>
              <div style={{ flex: 1, height: 1, background: `${phase.color}30` }} />
              <span style={{ fontSize: 9, color: P.text2, fontFamily: "'DM Mono',monospace" }}>
                {phase.sessions.filter(n => completedSet.has(n)).length}/{phase.sessions.length} séances
              </span>
            </div>
            <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', paddingLeft: 12 }}>
              {phase.sessions.map(n => (
                <SessionCircle key={n} n={n} status={getStatus(n)}
                  taux={historyMap[n]?.taux_succes_global}
                  palier={historyMap[n]?.palier}
                  sessionData={historyMap[n] || null}
                  onClick={handleCircleClick}
                />
              ))}
            </div>
          </div>
        ))}

        {/* Légende */}
        <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginTop: 8, paddingTop: 14, borderTop: '1px solid rgba(255,255,255,0.4)' }}>
          {[
            { bg: 'rgba(255,255,255,.15)', border: 'rgba(255,255,255,.25)', label: '🔒 Verrouillée' },
            { bg: 'rgba(184,123,158,.2)',  border: '#B87B9E',               label: '▶ Disponible — cliquez pour démarrer' },
            { bg: 'rgba(123,196,160,.2)', border: '#7BC4A0',               label: '✓ Complétée (survolez pour détails)' },
            { bg: 'rgba(255,215,0,.2)',   border: '#FFD700',               label: '★ Séance bilan' },
          ].map(({ bg, border, label }) => (
            <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <div style={{ width: 14, height: 14, borderRadius: '50%', background: bg, border: `2px solid ${border}` }} />
              <span style={{ fontSize: 9, color: P.text2 }}>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Graphe de progression ── */}
      {completed.length >= 2 && (
        <div style={{ background: P.card, borderRadius: 20, padding: '20px 24px', border: `1px solid ${P.border}`, backdropFilter: 'blur(12px)', boxShadow: `0 8px 32px ${P.shadow}`, marginBottom: 20 }}>
          <ProgressGraph history={history} />
        </div>
      )}

      {/* ── Bouton d'action ── */}
      <div style={{ textAlign: 'center', marginTop: 8 }}>
        {completed.length >= 15 ? (
          <button style={{ padding: '16px 40px', borderRadius: 18, background: 'linear-gradient(135deg, #FFD700, #C4A87B)', border: 'none', color: '#2B2A4A', fontSize: 15, fontWeight: 700, cursor: 'pointer' }}>
            ★ Programme terminé — Voir le rapport final
          </button>
        ) : BILAN_SESSIONS.has(nextSession) ? (
          <button onClick={() => onStartSession && onStartSession(nextSession)} style={{ padding: '16px 40px', borderRadius: 18, background: 'linear-gradient(135deg, #FFD700, #C4A87B)', border: 'none', color: '#2B2A4A', fontSize: 15, fontWeight: 700, cursor: 'pointer', boxShadow: '0 6px 24px rgba(255,215,0,.4)' }}>
            ★ Bilan S{nextSession} — Évaluation complète
          </button>
        ) : (
          <button onClick={() => onStartSession && onStartSession(nextSession)} style={{ padding: '16px 40px', borderRadius: 18, background: 'linear-gradient(135deg, #B87B9E, #9A6B8E)', border: 'none', color: 'white', fontSize: 15, fontWeight: 700, cursor: 'pointer', boxShadow: '0 6px 24px rgba(184,123,158,.45)' }}>
            ▶ Démarrer la séance S{nextSession}
          </button>
        )}
        <div style={{ marginTop: 10, fontSize: 11, color: P.text2 }}>
          Durée estimée : ~35–40 min · 5 blocs × 3 min · Palier {palier}
        </div>
      </div>

      {/* ── Explication du protocole ── */}
      <details style={{ marginTop: 20 }}>
        <summary style={{ cursor: 'pointer', fontSize: 11, color: P.text2, fontFamily: "'DM Mono',monospace", letterSpacing: 1, padding: '10px 0' }}>
          ? Comment fonctionne le protocole ?
        </summary>
        <div style={{ background: P.card, borderRadius: 16, padding: '16px 20px', border: `1px solid ${P.border}`, marginTop: 8, fontSize: 11, color: P.text, lineHeight: 1.8 }}>
          <b>Structure de chaque séance</b> (Mou et al. 2024) :<br />
          Baseline 2 min → Mesure IAPF 1 min → <b>5 blocs de 3 min</b> → Pauses 20 s → Repos final 3 min<br /><br />
          <b>Objectif de chaque bloc</b> : maintenir la puissance alpha au-dessus du seuil calculé depuis votre baseline.<br /><br />
          <b>Formule du seuil journalier</b> :<br />
          <code style={{ fontFamily: "'DM Mono',monospace", fontSize: 10, background: 'rgba(43,42,74,0.05)', padding: '2px 6px', borderRadius: 4 }}>
            Seuil = (0.70 × P_alpha_historique + 0.30 × P_alpha_aujourd'hui) × facteur_palier
          </code><br /><br />
          <b>Adaptation inter-blocs</b> : si taux succès {'>'} 60 % → seuil augmenté · si {'<'} 40 % → seuil réduit<br /><br />
          <b>Bilans obligatoires</b> à S5, S10 et S15 — évaluation de la progression globale.
        </div>
      </details>
    </div>
  )
}
