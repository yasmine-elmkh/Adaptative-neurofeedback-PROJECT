/**
 * WelcomePage.jsx — Écran d'accueil NeuroCap
 * Demande à l'utilisateur : casque hardware OU fichier EEG
 */

import { useState } from 'react'

export default function WelcomePage({ onHardware, onFile, onNeuroFeedback }) {
  const [hovered, setHovered] = useState(null)  // 'hardware' | 'file' | 'neurofeedback' | null

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      background: '#07090f',
      fontFamily: "'DM Sans', system-ui, sans-serif",
      padding: '24px 16px',
    }}>

      {/* Logo + titre */}
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <div style={{
          width: 64, height: 64, borderRadius: 18, margin: '0 auto 18px',
          background: 'linear-gradient(135deg, #00e5b0, #3b82f6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 32, boxShadow: '0 0 40px rgba(0,229,176,.2)',
        }}>
          🧠
        </div>
        <h1 style={{
          fontSize: 26, fontWeight: 800, color: '#f1f5f9',
          margin: '0 0 8px', letterSpacing: -.5,
        }}>
          NeuroCap EEG
        </h1>
        <p style={{ fontSize: 13, color: '#4a5a6e', margin: 0 }}>
          Classification d'état cognitif en temps réel
        </p>
      </div>

      {/* Question */}
      <div style={{
        fontSize: 14, fontWeight: 600, color: '#c9d8e8',
        marginBottom: 28, textAlign: 'center', lineHeight: 1.6,
      }}>
        Comment souhaitez-vous utiliser l'application ?
      </div>

      {/* Trois cartes de choix */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: 20,
        width: '100%',
        maxWidth: 820,
      }}>

        {/* ── Carte Hardware ── */}
        <ChoiceCard
          icon="🎧"
          title="Casque NeuroCap"
          subtitle="Acquisition en temps réel"
          description={[
            'Connectez le casque NeuroCap via WiFi',
            'Visualisation du signal EEG en direct',
            'Classification époque par époque (250 Hz)',
            'Enregistrement CSV de session',
          ]}
          badge="TEMPS RÉEL"
          badgeColor="#00e5b0"
          accentColor="#00e5b0"
          hovered={hovered === 'hardware'}
          onMouseEnter={() => setHovered('hardware')}
          onMouseLeave={() => setHovered(null)}
          onClick={onHardware}
        />

        {/* ── Carte Fichier ── */}
        <ChoiceCard
          icon="📂"
          title="Fichier EEG"
          subtitle="Analyse offline"
          description={[
            'Importez un fichier .edf, .csv ou .txt',
            'Même pipeline DSP que le temps réel',
            'Classification de toutes les époques',
            'Résumé : concentration / stress / confiance',
          ]}
          badge="OFFLINE"
          badgeColor="#a78bfa"
          accentColor="#a78bfa"
          formats={['.edf', '.csv', '.txt']}
          hovered={hovered === 'file'}
          onMouseEnter={() => setHovered('file')}
          onMouseLeave={() => setHovered(null)}
          onClick={onFile}
        />

        {/* ── Carte NeuroFeedback (Protocole + Feedback libre fusionnés) ── */}
        <ChoiceCard
          icon="🧠"
          title="NeuroFeedback"
          subtitle="Protocole 15 séances + Feedback libre"
          description={[
            'Protocole adaptatif 15 séances · 4 paliers P1→P4',
            'Feedback libre déverrouillé après calibration',
            'Signal EEG temps réel intégré (Fp2 · 250 Hz)',
            'Seuil alpha adaptatif · Thompson Sampling',
          ]}
          badge="NEUROFEEDBACK"
          badgeColor="#B87B9E"
          accentColor="#B87B9E"
          hovered={hovered === 'neurofeedback'}
          onMouseEnter={() => setHovered('neurofeedback')}
          onMouseLeave={() => setHovered(null)}
          onClick={onNeuroFeedback}
        />
      </div>

      {/* Footer */}
      <div style={{
        marginTop: 48, fontSize: 10, color: '#1e2d3d', textAlign: 'center',
        lineHeight: 1.8,
      }}>
        NeuroCap EEG v7.3 · LightGBM · 63 features · LOSO validé<br />
        Canal Fp2 · 250 Hz · ADS1115 + AD8232
      </div>
    </div>
  )
}

// ── Composant carte de choix ──────────────────────────────────────────────────
function ChoiceCard({
  icon, title, subtitle, description, badge, badgeColor,
  accentColor, formats, hovered, onMouseEnter, onMouseLeave, onClick,
}) {
  return (
    <div
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      onClick={onClick}
      style={{
        background: hovered ? `${accentColor}08` : '#0a0e18',
        border: `1.5px solid ${hovered ? accentColor + '60' : 'rgba(255,255,255,.07)'}`,
        borderRadius: 16,
        padding: '28px 24px',
        cursor: 'pointer',
        transition: 'all .2s ease',
        boxShadow: hovered ? `0 0 30px ${accentColor}15` : 'none',
        userSelect: 'none',
      }}
    >
      {/* Icône + badge */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
        <div style={{
          fontSize: 36,
          filter: hovered ? 'none' : 'grayscale(30%)',
          transition: 'filter .2s',
        }}>
          {icon}
        </div>
        <span style={{
          background: `${badgeColor}18`,
          border: `1px solid ${badgeColor}40`,
          color: badgeColor,
          fontSize: 9, fontWeight: 800, letterSpacing: 1.2,
          padding: '3px 8px', borderRadius: 5,
        }}>
          {badge}
        </span>
      </div>

      {/* Titre */}
      <div style={{
        fontSize: 17, fontWeight: 800, color: '#f1f5f9',
        marginBottom: 4,
      }}>
        {title}
      </div>
      <div style={{ fontSize: 11, color: accentColor, marginBottom: 16, fontWeight: 600 }}>
        {subtitle}
      </div>

      {/* Liste des points */}
      <ul style={{ padding: 0, margin: '0 0 16px', listStyle: 'none' }}>
        {description.map((line, i) => (
          <li key={i} style={{
            fontSize: 11, color: '#6a7a8e',
            padding: '3px 0',
            display: 'flex', alignItems: 'flex-start', gap: 7,
          }}>
            <span style={{ color: accentColor, marginTop: 1, flexShrink: 0 }}>✓</span>
            {line}
          </li>
        ))}
      </ul>

      {/* Formats acceptés (mode fichier) */}
      {formats && (
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 20 }}>
          {formats.map(ext => (
            <span key={ext} style={{
              background: 'rgba(255,255,255,.04)',
              border: '1px solid rgba(255,255,255,.1)',
              borderRadius: 5, padding: '2px 8px',
              fontSize: 10, color: '#c9d8e8',
              fontFamily: 'monospace',
            }}>{ext}</span>
          ))}
        </div>
      )}

      {/* Bouton */}
      <div style={{
        width: '100%', padding: '11px', borderRadius: 9,
        background: hovered
          ? `linear-gradient(135deg, ${accentColor}, ${accentColor}99)`
          : 'rgba(255,255,255,.05)',
        border: hovered ? 'none' : `1px solid rgba(255,255,255,.08)`,
        color: hovered ? '#000' : '#6a7a8e',
        fontSize: 12, fontWeight: 700, textAlign: 'center',
        transition: 'all .2s ease',
        letterSpacing: .4,
      }}>
        {title === 'Casque NeuroCap'
          ? '→ Configurer le WiFi'
          : title === 'NeuroFeedback'
            ? '→ Ouvrir NeuroFeedback'
            : '→ Importer un fichier'}
      </div>
    </div>
  )
}
