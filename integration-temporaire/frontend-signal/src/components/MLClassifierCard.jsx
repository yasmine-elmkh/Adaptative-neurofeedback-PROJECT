/**
 * MLClassifierCard — Affiche le résultat du classifieur LightGBM FeatEng.
 *
 * Reçoit `prediction` = epoch_result.ml_prediction depuis le WebSocket :
 *   { concentration, stress, state, confidence, uncertain, mode }
 *
 * Règle CdC §2.5.1 : si uncertain=true (confidence < 0.60),
 * afficher un avertissement — ce résultat n'est PAS transmis
 * comme feedback au patient.
 */

const f1p = v => typeof v === 'number' ? `${(v * 100).toFixed(1)}%` : '—'

/* ── Barre de probabilité animée ─────────────────────────────── */
function ProbBar({ label, value, color, isMain }) {
  const pct = typeof value === 'number' ? value * 100 : 0
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        marginBottom: 5, alignItems: 'baseline',
      }}>
        <span style={{
          fontSize: 10, color: isMain ? color : '#5a6a7e',
          fontFamily: "'Space Mono',monospace", letterSpacing: .5,
          fontWeight: isMain ? 700 : 400,
        }}>
          {label}
        </span>
        <span style={{
          fontSize: 12, fontFamily: "'Space Mono',monospace",
          fontWeight: 700, color: isMain ? color : '#4a5a6e',
        }}>
          {f1p(value)}
        </span>
      </div>
      {/* Track */}
      <div style={{
        height: 6, background: 'rgba(255,255,255,.05)',
        borderRadius: 3, overflow: 'hidden',
      }}>
        {/* Fill animé via CSS transition */}
        <div style={{
          height: '100%',
          width: `${Math.min(100, Math.max(0, pct))}%`,
          background: isMain
            ? `linear-gradient(90deg, ${color}88, ${color})`
            : `rgba(255,255,255,.07)`,
          borderRadius: 3,
          transition: 'width .45s ease',
          boxShadow: isMain ? `0 0 8px ${color}44` : 'none',
        }} />
      </div>
    </div>
  )
}

/* ── Composant principal ─────────────────────────────────────── */
export default function MLClassifierCard({ prediction }) {

  /* État d'attente */
  if (!prediction || prediction.mode === 'fallback') {
    return (
      <div style={cardStyle('#0a0e18', 'rgba(255,255,255,.05)')}>
        <Header />
        <div style={{
          textAlign: 'center', padding: '28px 0',
          color: '#3a4a5e', fontSize: 12, lineHeight: 1.8,
        }}>
          <div style={{ fontSize: 28, marginBottom: 10 }}>🧠</div>
          En attente de la première époque classifiée…
          {prediction?.error && (
            <div style={{
              marginTop: 8, fontSize: 10, color: '#f5a623',
              fontFamily: "'Space Mono',monospace",
            }}>
              ⚠ {prediction.error}
            </div>
          )}
        </div>
      </div>
    )
  }

  const { concentration, stress, state, confidence, uncertain, mode } = prediction

  const isConc    = state === 'concentration'
  const mainColor = uncertain ? '#f5a623' : isConc ? '#00e5b0' : '#ff4d6d'
  const stateLabel = uncertain
    ? 'INCERTAIN'
    : isConc ? 'CONCENTRATION' : 'STRESS'
  const stateIcon  = uncertain ? '⚠' : isConc ? '🎯' : '⚡'

  return (
    <div style={cardStyle(
      uncertain ? 'rgba(245,166,35,.04)' : isConc ? 'rgba(0,229,176,.03)' : 'rgba(255,77,109,.04)',
      uncertain ? 'rgba(245,166,35,.2)'  : isConc ? 'rgba(0,229,176,.15)' : 'rgba(255,77,109,.2)',
    )}>
      <Header mode={mode} />

      {/* État principal + confiance */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 18,
      }}>
        {/* Badge état */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 10,
          padding: '10px 16px',
          background: `${mainColor}14`,
          border: `1px solid ${mainColor}33`,
          borderRadius: 10,
          flexShrink: 0,
        }}>
          <span style={{ fontSize: 20 }}>{stateIcon}</span>
          <div>
            <div style={{
              fontFamily: "'Space Mono',monospace", fontSize: 13, fontWeight: 700,
              color: mainColor, letterSpacing: 1,
            }}>
              {stateLabel}
            </div>
            <div style={{ fontSize: 9, color: '#4a5a6e', marginTop: 2 }}>
              État cognitif ML
            </div>
          </div>
        </div>

        {/* Confiance */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 9, color: '#3a4a5e', marginBottom: 4, letterSpacing: .5 }}>
            CONFIANCE
          </div>
          <div style={{
            fontFamily: "'Space Mono',monospace", fontSize: 22, fontWeight: 700,
            color: confidence >= 0.6 ? mainColor : '#f5a623',
          }}>
            {f1p(confidence)}
          </div>
          {/* Mini arc confiance */}
          <div style={{ marginTop: 4, height: 3, width: 70, marginLeft: 'auto',
                        background: 'rgba(255,255,255,.05)', borderRadius: 2 }}>
            <div style={{
              height: '100%', borderRadius: 2,
              width: `${Math.round(confidence * 100)}%`,
              background: confidence >= 0.6 ? mainColor : '#f5a623',
              transition: 'width .45s ease',
            }} />
          </div>
        </div>
      </div>

      {/* Barres de probabilité */}
      <ProbBar
        label="Concentration"
        value={concentration}
        color="#00e5b0"
        isMain={!uncertain && isConc}
      />
      <ProbBar
        label="Stress"
        value={stress}
        color="#ff4d6d"
        isMain={!uncertain && !isConc}
      />

      {/* Avertissement incertitude (CdC §2.5.1) */}
      {uncertain && (
        <div style={{
          marginTop: 12, padding: '8px 12px',
          background: 'rgba(245,166,35,.06)',
          border: '1px solid rgba(245,166,35,.2)',
          borderRadius: 8, fontSize: 10, color: '#f5a623',
          fontFamily: "'Space Mono',monospace", lineHeight: 1.6,
        }}>
          ⚠ Époque incertaine — confiance {f1p(confidence)} {'<'} 60 %
          <span style={{ color: '#5a6a7e', marginLeft: 6 }}>(CdC §2.5.1)</span>
          <br />
          <span style={{ color: '#4a5a6e', fontSize: 9 }}>
            Ce résultat n'est pas utilisé pour le feedback patient.
          </span>
        </div>
      )}

      {/* Footer mode */}
      <div style={{
        marginTop: 12, paddingTop: 8,
        borderTop: '1px solid rgba(255,255,255,.04)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <span style={{ fontSize: 9, color: '#3a4a5e', fontFamily: "'Space Mono',monospace" }}>
          {mode === 'FeatEng' ? '63 features · FeatEng' : '15 features · Baseline'}
        </span>
        <span style={{ fontSize: 9, color: '#3a4a5e', fontFamily: "'Space Mono',monospace" }}>
          LightGBM · LOSO validé
        </span>
      </div>
    </div>
  )
}

/* ── Helpers locaux ──────────────────────────────────────────── */
function Header({ mode }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      marginBottom: 16,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <div style={{
          width: 7, height: 7, borderRadius: 2,
          background: '#a78bfa', boxShadow: '0 0 8px #a78bfa55',
        }} />
        <span style={{
          fontFamily: "'Space Mono',monospace", fontSize: 9,
          letterSpacing: 1.5, textTransform: 'uppercase', color: '#a78bfa',
        }}>
          Classifieur ML · LightGBM
        </span>
      </div>
      {mode && (
        <span style={{
          fontSize: 8, color: '#3a4a5e',
          fontFamily: "'Space Mono',monospace",
          padding: '2px 7px', borderRadius: 4,
          background: 'rgba(255,255,255,.03)',
          border: '1px solid rgba(255,255,255,.06)',
        }}>
          {mode}
        </span>
      )}
    </div>
  )
}

function cardStyle(bg, border) {
  return {
    background: bg,
    border: `1px solid ${border}`,
    borderRadius: 12,
    padding: '14px 16px',
    transition: 'all .3s ease',
  }
}
