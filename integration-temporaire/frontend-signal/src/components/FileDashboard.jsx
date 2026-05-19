/**
 * FileDashboard.jsx — Dashboard mode fichier EEG offline
 * Remplace le dashboard live quand l'utilisateur choisit "Fichier EEG"
 * Pipeline : upload → /api/analyze_file → affichage résultats ML
 */

import { useState, useRef, useCallback } from 'react'
import axios from 'axios'

const API = '/api'

// ── Palette (identique au dashboard live) ────────────────────────────────────
const C = {
  conc:   '#00e5b0',
  stress: '#ff4d6d',
  uncert: '#f5a623',
  purple: '#a78bfa',
  bg:     '#07090f',
  card:   '#0a0e18',
  border: 'rgba(255,255,255,.07)',
  text:   '#c9d8e8',
  muted:  '#4a5a6e',
}

function stateColor(pred) {
  if (!pred) return C.muted
  if (pred.uncertain) return C.uncert
  return pred.state === 'concentration' ? C.conc : C.stress
}

// ── Barre de probabilité ──────────────────────────────────────────────────────
function ProbBar({ label, value, color }) {
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
        <span style={{ fontSize: 11, color: C.muted }}>{label}</span>
        <span style={{ fontSize: 12, fontWeight: 700, color, fontFamily: 'monospace' }}>
          {(value * 100).toFixed(1)} %
        </span>
      </div>
      <div style={{ height: 6, background: 'rgba(255,255,255,.06)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{
          width: `${(value * 100).toFixed(1)}%`, height: '100%',
          background: color, borderRadius: 3,
          transition: 'width .5s ease',
        }} />
      </div>
    </div>
  )
}

// ── Carte classifieur ML (résumé fichier) ─────────────────────────────────────
function MLSummaryCard({ summary, filename }) {
  const color = summary.dominant_state === 'concentration' ? C.conc
              : summary.dominant_state === 'stress'        ? C.stress
              : C.muted

  const stateLabel = summary.dominant_state === 'concentration' ? '🎯 CONCENTRATION'
                   : summary.dominant_state === 'stress'        ? '⚡ STRESS'
                   : '— NEUTRE'

  return (
    <div style={{
      background: C.card,
      border: `1.5px solid ${color}40`,
      borderRadius: 14,
      padding: '20px 22px',
      boxShadow: `0 0 30px ${color}0d`,
    }}>
      {/* En-tête */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: C.purple, letterSpacing: 1 }}>
          🧠 CLASSIFIEUR ML — RÉSULTAT FICHIER
        </div>
        <div style={{ fontSize: 9, color: C.muted }}>LightGBM · LOSO validé</div>
      </div>

      {/* État dominant */}
      <div style={{
        fontSize: 22, fontWeight: 900, color,
        marginBottom: 6, letterSpacing: -.5,
      }}>
        {stateLabel}
      </div>
      <div style={{ fontSize: 11, color: C.muted, marginBottom: 20 }}>
        {filename} · {summary.n_classified} époques · Confiance moy.{' '}
        <span style={{ color, fontWeight: 700 }}>
          {(summary.mean_confidence * 100).toFixed(1)} %
        </span>
      </div>

      {/* Barres */}
      <ProbBar
        label="Concentration"
        value={summary.concentration_pct / 100}
        color={C.conc}
      />
      <ProbBar
        label="Stress"
        value={summary.stress_pct / 100}
        color={C.stress}
      />
      <ProbBar
        label="Incertain"
        value={summary.uncertain_pct / 100}
        color={C.uncert}
      />

      {/* Pied */}
      <div style={{
        marginTop: 14, paddingTop: 10,
        borderTop: '1px solid rgba(255,255,255,.05)',
        fontSize: 9, color: '#1e2d3d',
        display: 'flex', justifyContent: 'space-between',
      }}>
        <span>FeatEng · 63 features</span>
        <span>Golden Filter · zero-phase</span>
        <span>LOSO cross-validation</span>
      </div>
    </div>
  )
}

// ── Table des époques ─────────────────────────────────────────────────────────
function EpochTable({ epochs }) {
  const [page, setPage] = useState(0)
  const PER_PAGE = 25
  const total = Math.ceil(epochs.length / PER_PAGE)
  const slice = epochs.slice(page * PER_PAGE, (page + 1) * PER_PAGE)

  return (
    <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: '16px 18px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div style={{ fontSize: 10, fontWeight: 700, color: C.muted, letterSpacing: 1 }}>
          DÉTAIL PAR ÉPOQUE ({epochs.length} classifiées)
        </div>
        {total > 1 && (
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <NavBtn disabled={page === 0} onClick={() => setPage(p => Math.max(0, p - 1))}>‹</NavBtn>
            <span style={{ fontSize: 10, color: C.muted }}>{page + 1} / {total}</span>
            <NavBtn disabled={page === total - 1} onClick={() => setPage(p => Math.min(total - 1, p + 1))}>›</NavBtn>
          </div>
        )}
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11, fontFamily: 'monospace' }}>
          <thead>
            <tr>
              {['#', 'Temps', 'État', 'Conc.', 'Stress', 'Confiance', 'Amp.'].map(h => (
                <th key={h} style={{
                  padding: '6px 10px', textAlign: 'left',
                  color: C.muted, fontSize: 9, fontWeight: 700, letterSpacing: .5,
                  borderBottom: `1px solid ${C.border}`, whiteSpace: 'nowrap',
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slice.map((ep, i) => {
              const p  = ep.ml_prediction
              const sc = p ? stateColor(p) : C.muted
              return (
                <tr key={ep.epoch_idx} style={{ background: i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,.012)' }}>
                  <td style={td}>{ep.epoch_idx}</td>
                  <td style={td}>{ep.time_s.toFixed(1)} s</td>
                  <td style={td}>
                    {p ? (
                      <span style={{
                        background: `${sc}18`, border: `1px solid ${sc}40`,
                        color: sc, borderRadius: 4, padding: '2px 7px',
                        fontSize: 9, fontWeight: 700,
                      }}>
                        {p.uncertain ? '⚠ INCERT.' : p.state === 'concentration' ? '🎯 CONC.' : '⚡ STRESS'}
                      </span>
                    ) : '—'}
                  </td>
                  <td style={{ ...td, color: C.conc }}>
                    {p ? `${(p.concentration * 100).toFixed(1)}%` : '—'}
                  </td>
                  <td style={{ ...td, color: C.stress }}>
                    {p ? `${(p.stress * 100).toFixed(1)}%` : '—'}
                  </td>
                  <td style={{ ...td, color: sc, fontWeight: 700 }}>
                    {p ? `${(p.confidence * 100).toFixed(1)}%` : '—'}
                  </td>
                  <td style={{ ...td, color: C.muted }}>
                    {ep.amplitude_uv} µV
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}

const td = {
  padding: '6px 10px',
  borderBottom: '1px solid rgba(255,255,255,.03)',
  color: '#c9d8e8', verticalAlign: 'middle',
}

function NavBtn({ disabled, onClick, children }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{
      background: 'rgba(255,255,255,.06)', border: '1px solid rgba(255,255,255,.1)',
      borderRadius: 5, color: '#c9d8e8', padding: '3px 9px',
      cursor: disabled ? 'not-allowed' : 'pointer', fontSize: 13,
      opacity: disabled ? .3 : 1,
    }}>{children}</button>
  )
}

// ── Zone de dépôt fichier ─────────────────────────────────────────────────────
function DropZone({ onFile, loading }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  const handleDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) onFile(f)
  }, [onFile])

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !loading && inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? C.purple : 'rgba(255,255,255,.12)'}`,
        borderRadius: 14, padding: '52px 28px', textAlign: 'center',
        cursor: loading ? 'wait' : 'pointer',
        background: dragging ? 'rgba(167,139,250,.04)' : 'rgba(255,255,255,.015)',
        transition: 'all .2s',
        userSelect: 'none',
      }}
    >
      <input ref={inputRef} type="file" accept=".edf,.csv,.txt"
        style={{ display: 'none' }}
        onChange={e => { const f = e.target.files[0]; if (f) onFile(f); e.target.value = '' }}
      />

      {loading ? (
        <>
          <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
          <div style={{
            width: 32, height: 32, margin: '0 auto 16px',
            border: '3px solid rgba(167,139,250,.2)', borderTopColor: C.purple,
            borderRadius: '50%', animation: 'spin .8s linear infinite',
          }} />
          <div style={{ fontSize: 15, color: C.purple, fontWeight: 700, marginBottom: 6 }}>
            Analyse en cours…
          </div>
          <div style={{ fontSize: 11, color: C.muted }}>
            Filtrage DSP · 63 features FeatEng · LightGBM
          </div>
        </>
      ) : (
        <>
          <div style={{ fontSize: 44, marginBottom: 14 }}>📂</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: '#f1f5f9', marginBottom: 8 }}>
            Déposer votre fichier EEG ici
          </div>
          <div style={{ fontSize: 11, color: C.muted, marginBottom: 18, lineHeight: 1.7 }}>
            ou cliquer pour sélectionner
          </div>
          <div style={{ display: 'inline-flex', gap: 8, marginBottom: 16 }}>
            {['.edf', '.csv', '.txt'].map(ext => (
              <span key={ext} style={{
                background: `${C.purple}15`, border: `1px solid ${C.purple}30`,
                borderRadius: 5, padding: '3px 10px',
                fontSize: 11, color: C.purple, fontFamily: 'monospace',
              }}>{ext}</span>
            ))}
          </div>
          <div style={{ fontSize: 10, color: '#2a3a4e', lineHeight: 1.8 }}>
            Signal canal Fp2 · 250 Hz · minimum 4 secondes<br />
            CSV : colonnes 'raw' / 'uv' / 'voltage' ou première colonne numérique
          </div>
        </>
      )}
    </div>
  )
}

// ── Composant principal ───────────────────────────────────────────────────────
export default function FileDashboard({ onBack }) {
  const [loading,  setLoading]  = useState(false)
  const [result,   setResult]   = useState(null)
  const [error,    setError]    = useState(null)

  const handleFile = useCallback(async (file) => {
    setLoading(true); setError(null); setResult(null)

    const form = new FormData()
    form.append('file', file)

    try {
      const resp = await axios.post(`${API}/analyze_file`, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 180_000,
      })
      setResult(resp.data)
    } catch (e) {
      setError(e.response?.data?.detail || e.message || 'Erreur inconnue')
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <div style={{
      minHeight: '100vh', background: C.bg,
      fontFamily: "'DM Sans', system-ui, sans-serif",
    }}>

      {/* ── Header ────────────────────────────────────────────────── */}
      <div style={{
        background: 'rgba(10,14,24,.95)',
        borderBottom: `1px solid ${C.border}`,
        padding: '0 20px',
        display: 'flex', alignItems: 'center', gap: 14,
        height: 52, position: 'sticky', top: 0, zIndex: 100,
      }}>
        <button onClick={onBack} style={{
          background: 'rgba(255,255,255,.05)',
          border: '1px solid rgba(255,255,255,.08)',
          borderRadius: 7, color: C.muted, padding: '5px 12px',
          cursor: 'pointer', fontSize: 11, fontWeight: 600,
        }}>
          ← Accueil
        </button>

        <div style={{ width: 1, height: 20, background: C.border }} />

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{
            width: 28, height: 28, borderRadius: 8,
            background: 'linear-gradient(135deg,#a78bfa,#3b82f6)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 14,
          }}>🧠</div>
          <div>
            <div style={{ fontSize: 13, fontWeight: 700, color: '#f1f5f9' }}>NeuroCap EEG</div>
            <div style={{ fontSize: 9, color: C.purple }}>MODE FICHIER — OFFLINE</div>
          </div>
        </div>

        <div style={{ flex: 1 }} />

        {result && (
          <button onClick={() => { setResult(null); setError(null) }} style={{
            background: 'rgba(255,255,255,.04)',
            border: '1px solid rgba(255,255,255,.08)',
            borderRadius: 7, color: C.muted, padding: '5px 12px',
            cursor: 'pointer', fontSize: 11,
          }}>
            + Nouveau fichier
          </button>
        )}
      </div>

      {/* ── Contenu ────────────────────────────────────────────────── */}
      <div style={{
        maxWidth: 900, margin: '0 auto', padding: '28px 20px 60px',
      }}>

        {/* ─── Pas encore de résultat : zone upload ─── */}
        {!result && (
          <>
            <div style={{ marginBottom: 24 }}>
              <div style={{ fontSize: 18, fontWeight: 800, color: '#f1f5f9', marginBottom: 6 }}>
                Analyse de fichier EEG
              </div>
              <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.7 }}>
                Importez votre enregistrement EEG. Le backend applique le même pipeline DSP
                qu'en temps réel : filtrage Golden Filter zero-phase, extraction de 63 features
                FeatEng, puis classification par le modèle LightGBM entraîné (LOSO).
              </div>
            </div>

            <DropZone onFile={handleFile} loading={loading} />

            {error && (
              <div style={{
                marginTop: 16,
                background: 'rgba(255,77,109,.07)',
                border: '1px solid rgba(255,77,109,.25)',
                borderRadius: 9, padding: '12px 16px',
                fontSize: 12, color: '#fca5a5', lineHeight: 1.6,
              }}>
                ❌ {error}
              </div>
            )}
          </>
        )}

        {/* ─── Résultats ─── */}
        {result && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>

            {/* Titre */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontSize: 18, fontWeight: 800, color: '#f1f5f9' }}>
                  Résultats de classification
                </div>
                <div style={{ fontSize: 11, color: C.muted, marginTop: 3 }}>
                  {result.duration_s} s · {result.fs} Hz · {result.n_epochs_accepted} époques acceptées
                  / {result.n_epochs_total} totales
                </div>
              </div>
            </div>

            {/* Carte ML principale */}
            <MLSummaryCard summary={result.summary} filename={result.filename} />

            {/* Infos rapides */}
            <div style={{
              display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: 12,
            }}>
              {[
                { label: 'Concentration', value: `${result.summary.concentration_pct.toFixed(1)} %`, color: C.conc },
                { label: 'Stress',        value: `${result.summary.stress_pct.toFixed(1)} %`,        color: C.stress },
                { label: 'Incertain',     value: `${result.summary.uncertain_pct.toFixed(1)} %`,     color: C.uncert },
                { label: 'Confiance moy.', value: `${(result.summary.mean_confidence * 100).toFixed(1)} %`, color: '#c9d8e8' },
              ].map(({ label, value, color }) => (
                <div key={label} style={{
                  background: C.card, border: `1px solid ${C.border}`,
                  borderRadius: 10, padding: '14px 16px',
                }}>
                  <div style={{ fontSize: 9, color: C.muted, letterSpacing: .5, marginBottom: 6 }}>
                    {label.toUpperCase()}
                  </div>
                  <div style={{ fontSize: 22, fontWeight: 800, color }}>{value}</div>
                </div>
              ))}
            </div>

            {/* Table époques */}
            {result.epochs?.length > 0
              ? <EpochTable epochs={result.epochs} />
              : (
                <div style={{
                  background: C.card, border: `1px solid ${C.border}`,
                  borderRadius: 12, padding: 24,
                  fontSize: 12, color: C.muted, textAlign: 'center',
                }}>
                  Aucune époque acceptée — vérifiez la qualité du signal
                </div>
              )
            }
          </div>
        )}
      </div>
    </div>
  )
}
