/**
 * NeuroFeedbackHub.jsx — Interface unifiée NeuroFeedback
 *
 * Combine le Protocole 15 séances et le Feedback libre dans un seul écran.
 * Le Feedback libre se déverrouille après la calibration (1ère séance terminée).
 * Le widget EEG temps réel (MiniSignalWidget) est visible en permanence dans le header.
 */

import { useState, useEffect } from 'react'
import ProtocolDashboard from './protocol/ProtocolDashboard'
import FeedbackSetup     from '../pages/FeedbackSetup'
import MiniSignalWidget  from './feedback/MiniSignalWidget'

// ── Palette ───────────────────────────────────────────────────────────────────
const P = {
  bg:     '#C5D3E8',
  card:   'rgba(247,243,250,0.55)',
  border: 'rgba(255,255,255,0.45)',
  text:   '#2B2A4A',
  text2:  '#9A8BAE',
  accent: '#B87B9E',
  green:  '#7BC4A0',
  shadow: 'rgba(180,169,196,0.35)',
}

export default function NeuroFeedbackHub({
  userId = 'demo',
  onBack,
  onStartProtocolSession,
  onStartFeedback,
}) {
  const [tab,       setTab]       = useState('protocol')
  const [calibDone, setCalibDone] = useState(false)
  const [checking,  setChecking]  = useState(true)

  // Vérifie si la calibration a été effectuée (au moins 1 séance terminée ou p_alpha_hist dispo)
  useEffect(() => {
    fetch(`/api/protocol/user/${userId}`)
      .then(r => (r.ok ? r.json() : null))
      .then(d => {
        if (d) setCalibDone(d.sessions_done > 0 || d.p_alpha_hist != null)
      })
      .catch(() => {})
      .finally(() => setChecking(false))
  }, [userId])

  return (
    <div style={{
      minHeight: '100vh',
      fontFamily: "'DM Sans', system-ui, sans-serif",
      background: P.bg,
    }}>
      {/* ── Header fixe ── */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 200,
        background: 'rgba(197,211,232,0.97)',
        backdropFilter: 'blur(14px)',
        borderBottom: `1px solid ${P.border}`,
        boxShadow: `0 2px 16px ${P.shadow}`,
        padding: '10px 20px',
        display: 'flex', alignItems: 'center', gap: 14,
        flexWrap: 'wrap',
      }}>
        {/* Bouton retour */}
        {onBack && (
          <button
            onClick={onBack}
            style={{
              padding: '6px 14px', borderRadius: 9,
              border: `1px solid ${P.border}`, background: 'transparent',
              color: P.text2, fontSize: 12, cursor: 'pointer',
              flexShrink: 0,
            }}
          >
            ← Accueil
          </button>
        )}

        {/* Titre */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 10,
            background: 'linear-gradient(135deg, #B87B9E, #7BC4A0)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 18,
          }}>
            🧠
          </div>
          <div>
            <div style={{ fontSize: 16, fontWeight: 800, color: P.text, lineHeight: 1.1 }}>
              NeuroFeedback
            </div>
            <div style={{ fontSize: 9, color: P.text2, fontFamily: "'DM Mono',monospace", letterSpacing: 0.8 }}>
              NeuroCap EEG · Adaptatif
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: 6, marginLeft: 8 }}>
          <TabBtn
            active={tab === 'protocol'}
            onClick={() => setTab('protocol')}
            label="🎯 Protocole 15 séances"
          />
          <TabBtn
            active={tab === 'libre'}
            onClick={() => calibDone && setTab('libre')}
            label={calibDone ? '🧘 Feedback libre' : '🔒 Feedback libre'}
            disabled={!calibDone}
            title={!calibDone ? 'Terminez d\'abord la calibration (S1) pour déverrouiller' : ''}
          />
        </div>

        {/* Badge calibration */}
        {!checking && (
          <div style={{
            padding: '3px 10px', borderRadius: 20,
            background: calibDone ? 'rgba(123,196,160,0.2)' : 'rgba(196,168,123,0.2)',
            border: `1px solid ${calibDone ? P.green : '#C4A87B'}`,
            fontSize: 9, fontWeight: 700, fontFamily: "'DM Mono',monospace",
            color: calibDone ? '#3a7a5e' : '#8a6a3e',
            letterSpacing: 0.8, flexShrink: 0,
          }}>
            {calibDone ? '✓ CALIBRATION OK' : '⚠ CALIBRATION REQUISE'}
          </div>
        )}

        {/* Spacer */}
        <div style={{ flex: 1, minWidth: 0 }} />

        {/* Widget EEG temps réel */}
        <div style={{ width: 230, flexShrink: 0 }}>
          <MiniSignalWidget />
        </div>
      </div>

      {/* ── Contenu des onglets ── */}

      {/* Onglet Protocole */}
      {tab === 'protocol' && (
        <ProtocolDashboard
          userId={userId}
          onStartSession={(n) => {
            // Après avoir lancé la première séance, la calibration sera faite
            onStartProtocolSession && onStartProtocolSession(n)
          }}
          // Pas de onBack — le hub gère la navigation
        />
      )}

      {/* Onglet Feedback libre — verrouillé */}
      {tab === 'libre' && !calibDone && (
        <LockedFeedback onGoProtocol={() => setTab('protocol')} />
      )}

      {/* Onglet Feedback libre — déverrouillé */}
      {tab === 'libre' && calibDone && (
        <FeedbackSetup
          data={{ eegState: 'neutral', features: {} }}
          onStart={onStartFeedback}
          onBack={() => setTab('protocol')}
        />
      )}
    </div>
  )
}

// ── Sous-composants ───────────────────────────────────────────────────────────

function TabBtn({ active, onClick, label, disabled, title }) {
  const [hov, setHov] = useState(false)
  return (
    <button
      onClick={onClick}
      onMouseEnter={() => !disabled && setHov(true)}
      onMouseLeave={() => setHov(false)}
      title={title}
      style={{
        padding: '7px 18px', borderRadius: 20,
        border: active ? 'none' : `1px solid ${P.border}`,
        background: active
          ? 'linear-gradient(135deg, #B87B9E, #9A6B8E)'
          : hov && !disabled
            ? 'rgba(184,123,158,0.15)'
            : disabled ? 'rgba(255,255,255,0.15)' : 'rgba(255,255,255,0.45)',
        color: active ? 'white' : disabled ? P.text2 : P.text,
        fontSize: 12, fontWeight: 600,
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.55 : 1,
        transition: 'all .18s ease',
        boxShadow: active ? '0 3px 12px rgba(184,123,158,0.4)' : 'none',
        flexShrink: 0,
      }}
    >
      {label}
    </button>
  )
}

function LockedFeedback({ onGoProtocol }) {
  return (
    <div style={{
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      minHeight: 'calc(100vh - 80px)',
      padding: 40, textAlign: 'center',
    }}>
      <div style={{
        background: P.card, borderRadius: 24,
        padding: '40px 48px', maxWidth: 480,
        border: `1px solid ${P.border}`,
        backdropFilter: 'blur(12px)',
        boxShadow: `0 8px 32px ${P.shadow}`,
      }}>
        <div style={{ fontSize: 48, marginBottom: 16 }}>🔒</div>
        <div style={{ fontSize: 20, fontWeight: 800, color: P.text, marginBottom: 10 }}>
          Feedback libre verrouillé
        </div>
        <div style={{ fontSize: 13, color: P.text2, lineHeight: 1.8, marginBottom: 24 }}>
          Le feedback libre se déverrouille après avoir effectué la{' '}
          <b style={{ color: P.text }}>calibration (Séance S1)</b> dans le protocole.
          <br /><br />
          La calibration mesure votre <b style={{ color: P.text }}>baseline alpha individuelle</b>,
          indispensable pour personnaliser les stimuli de feedback.
        </div>

        <div style={{
          display: 'flex', flexDirection: 'column', gap: 8,
          fontSize: 12, color: P.text2, marginBottom: 28, textAlign: 'left',
        }}>
          {[
            '① Démarrez la Séance S1 dans l\'onglet Protocole',
            '② Effectuez la baseline (2 min, yeux fermés)',
            '③ Complétez les 5 blocs de neurofeedback alpha',
            '④ Le Feedback libre se déverrouille automatiquement',
          ].map((step, i) => (
            <div key={i} style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
              <span style={{ color: P.accent, fontWeight: 700, flexShrink: 0 }}>✓</span>
              {step}
            </div>
          ))}
        </div>

        <button
          onClick={onGoProtocol}
          style={{
            width: '100%', padding: '12px 0', borderRadius: 14,
            background: 'linear-gradient(135deg, #B87B9E, #9A6B8E)',
            border: 'none', color: 'white',
            fontSize: 14, fontWeight: 700, cursor: 'pointer',
            boxShadow: '0 4px 18px rgba(184,123,158,0.45)',
            transition: 'opacity .18s',
          }}
        >
          → Aller au Protocole 15 séances
        </button>
      </div>
    </div>
  )
}
