/**
 * FileAnalysisTab.jsx — Analyse offline de fichier EEG
 * Formats acceptés : .edf, .csv, .txt
 * Pipeline : Golden Filter → z-score → 63 FeatEng → LightGBM
 */

import { useState, useRef, useCallback } from 'react'
import axios from 'axios'

const API = '/api'

// ── Palette ──────────────────────────────────────────────────────────────────
const C = {
  conc:    '#00e5b0',
  stress:  '#ff4d6d',
  uncert:  '#f5a623',
  neutral: '#4da6ff',
  bg:      '#07090f',
  card:    '#0a0e18',
  border:  'rgba(255,255,255,.07)',
  text:    '#c9d8e8',
  muted:   '#4a5a6e',
}

function stateColor(pred) {
  if (!pred) return C.muted
  if (pred.uncertain) return C.uncert
  return pred.state === 'concentration' ? C.conc : C.stress
}

function StateChip({ pred }) {
  if (!pred) return <span style={{ color: C.muted, fontSize: 11 }}>—</span>
  const color = stateColor(pred)
  const label = pred.uncertain
    ? '⚠ INCERTAIN'
    : pred.state === 'concentration' ? '🎯 CONCENTRATION' : '⚡ STRESS'
  return (
    <span style={{
      background: `${color}18`, border: `1px solid ${color}50`,
      color, borderRadius: 5, padding: '2px 8px', fontSize: 10,
      fontWeight: 700, letterSpacing: .5, whiteSpace: 'nowrap',
    }}>
      {label}
    </span>
  )
}

function ConfBar({ value, color }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
      <div style={{
        flex: 1, height: 5, background: 'rgba(255,255,255,.06)',
        borderRadius: 3, overflow: 'hidden',
      }}>
        <div style={{
          width: `${(value * 100).toFixed(1)}%`,
          height: '100%', background: color,
          borderRadius: 3, transition: 'width .3s ease',
        }} />
      </div>
      <span style={{ fontSize: 10, color, minWidth: 38, textAlign: 'right' }}>
        {(value * 100).toFixed(1)} %
      </span>
    </div>
  )
}

// ── Carte résumé ─────────────────────────────────────────────────────────────
function SummaryCard({ result }) {
  const s = result.summary
  const dominantColor =
    s.dominant_state === 'concentration' ? C.conc :
    s.dominant_state === 'stress'        ? C.stress : C.muted

  return (
    <div style={{
      background: C.card, border: `1px solid ${dominantColor}40`,
      borderRadius: 12, padding: '18px 20px', marginBottom: 20,
    }}>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'flex-start', flexWrap: 'wrap', gap: 12,
      }}>

        {/* Infos fichier */}
        <div>
          <div style={{ fontSize: 11, color: C.muted, marginBottom: 4, letterSpacing: .5 }}>
            FICHIER ANALYSÉ
          </div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9', marginBottom: 2 }}>
            {result.filename}
          </div>
          <div style={{ fontSize: 11, color: C.muted }}>
            {result.duration_s} s · {result.fs} Hz · {result.n_epochs_accepted}/{result.n_epochs_total} époques
          </div>
        </div>

        {/* État dominant */}
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: 10, color: C.muted, marginBottom: 4, letterSpacing: .5 }}>
            ÉTAT DOMINANT
          </div>
          <div style={{ fontSize: 22, fontWeight: 800, color: dominantColor }}>
            {s.dominant_state === 'concentration' ? '🎯 CONCENTRATION' :
             s.dominant_state === 'stress'        ? '⚡ STRESS' : '—'}
          </div>
          <div style={{ fontSize: 11, color: C.muted, marginTop: 2 }}>
            Confiance moy. {(s.mean_confidence * 100).toFixed(1)} %
          </div>
        </div>
      </div>

      {/* Barres résumé */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 12, marginTop: 16,
      }}>
        {[
          { label: 'Concentration', value: s.concentration_pct, color: C.conc },
          { label: 'Stress',        value: s.stress_pct,        color: C.stress },
          { label: 'Incertain',     value: s.uncertain_pct,     color: C.uncert },
        ].map(({ label, value, color }) => (
          <div key={label}>
            <div style={{ fontSize: 9, color: C.muted, marginBottom: 5, letterSpacing: .5 }}>
              {label.toUpperCase()}
            </div>
            <div style={{
              height: 6, background: 'rgba(255,255,255,.06)',
              borderRadius: 3, overflow: 'hidden', marginBottom: 4,
            }}>
              <div style={{
                width: `${value}%`, height: '100%',
                background: color, borderRadius: 3,
                transition: 'width .5s ease',
              }} />
            </div>
            <div style={{ fontSize: 12, fontWeight: 700, color }}>
              {value.toFixed(1)} %
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Table des époques ─────────────────────────────────────────────────────────
function EpochTable({ epochs }) {
  const [page, setPage] = useState(0)
  const PER_PAGE = 30
  const total    = Math.ceil(epochs.length / PER_PAGE)
  const slice    = epochs.slice(page * PER_PAGE, (page + 1) * PER_PAGE)

  return (
    <div>
      <div style={{
        display: 'flex', justifyContent: 'space-between',
        alignItems: 'center', marginBottom: 10,
      }}>
        <div style={{ fontSize: 11, color: C.muted }}>
          {epochs.length} époques classifiées
        </div>
        {total > 1 && (
          <div style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
            <button onClick={() => setPage(p => Math.max(0, p - 1))}
              disabled={page === 0}
              style={{ ...btnStyle, opacity: page === 0 ? .3 : 1 }}>‹</button>
            <span style={{ fontSize: 10, color: C.muted }}>
              {page + 1} / {total}
            </span>
            <button onClick={() => setPage(p => Math.min(total - 1, p + 1))}
              disabled={page === total - 1}
              style={{ ...btnStyle, opacity: page === total - 1 ? .3 : 1 }}>›</button>
          </div>
        )}
      </div>

      <div style={{ overflowX: 'auto' }}>
        <table style={{
          width: '100%', borderCollapse: 'collapse',
          fontSize: 11, fontFamily: "'Space Mono', monospace",
        }}>
          <thead>
            <tr>
              {['#', 'Temps (s)', 'État', 'Concentration', 'Stress', 'Confiance', 'Amp. (µV)'].map(h => (
                <th key={h} style={{
                  padding: '6px 10px', textAlign: 'left',
                  color: C.muted, fontWeight: 600,
                  borderBottom: `1px solid ${C.border}`,
                  whiteSpace: 'nowrap',
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {slice.map((ep, i) => {
              const p = ep.ml_prediction
              const rowColor = i % 2 === 0 ? 'transparent' : 'rgba(255,255,255,.015)'
              return (
                <tr key={ep.epoch_idx} style={{ background: rowColor }}>
                  <td style={tdStyle}>{ep.epoch_idx}</td>
                  <td style={tdStyle}>{ep.time_s.toFixed(2)}</td>
                  <td style={tdStyle}><StateChip pred={p} /></td>
                  <td style={tdStyle}>
                    {p ? <ConfBar value={p.concentration} color={C.conc} /> : '—'}
                  </td>
                  <td style={tdStyle}>
                    {p ? <ConfBar value={p.stress} color={C.stress} /> : '—'}
                  </td>
                  <td style={{ ...tdStyle, color: p ? stateColor(p) : C.muted, fontWeight: 700 }}>
                    {p ? `${(p.confidence * 100).toFixed(1)} %` : '—'}
                  </td>
                  <td style={{ ...tdStyle, color: C.muted }}>
                    {ep.amplitude_uv}
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

const tdStyle = {
  padding: '6px 10px',
  borderBottom: '1px solid rgba(255,255,255,.03)',
  color: C.text,
  verticalAlign: 'middle',
}

const btnStyle = {
  background: 'rgba(255,255,255,.06)',
  border: '1px solid rgba(255,255,255,.1)',
  borderRadius: 5, color: C.text,
  padding: '3px 9px', cursor: 'pointer',
  fontSize: 13,
}

// ── Zone de dépôt ─────────────────────────────────────────────────────────────
function DropZone({ onFile, loading }) {
  const [dragging, setDragging] = useState(false)
  const inputRef = useRef(null)

  const handleDrop = useCallback((e) => {
    e.preventDefault()
    setDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) onFile(f)
  }, [onFile])

  const handleChange = useCallback((e) => {
    const f = e.target.files[0]
    if (f) onFile(f)
    e.target.value = ''
  }, [onFile])

  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragging(true) }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => !loading && inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? C.conc : 'rgba(255,255,255,.12)'}`,
        borderRadius: 12,
        padding: '40px 24px',
        textAlign: 'center',
        cursor: loading ? 'wait' : 'pointer',
        transition: 'border-color .2s, background .2s',
        background: dragging ? 'rgba(0,229,176,.04)' : 'rgba(255,255,255,.015)',
        userSelect: 'none',
      }}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".edf,.csv,.txt"
        style={{ display: 'none' }}
        onChange={handleChange}
      />
      {loading ? (
        <>
          <div style={{ fontSize: 32, marginBottom: 12 }}>⏳</div>
          <div style={{ fontSize: 14, color: C.conc, fontWeight: 700 }}>
            Analyse en cours…
          </div>
          <div style={{ fontSize: 11, color: C.muted, marginTop: 6 }}>
            Filtrage · Extraction 63 features · LightGBM
          </div>
        </>
      ) : (
        <>
          <div style={{ fontSize: 36, marginBottom: 12 }}>📂</div>
          <div style={{ fontSize: 14, fontWeight: 700, color: '#f1f5f9', marginBottom: 6 }}>
            Déposer un fichier EEG ici
          </div>
          <div style={{ fontSize: 11, color: C.muted, marginBottom: 14, lineHeight: 1.7 }}>
            ou cliquer pour sélectionner
          </div>
          <div style={{
            display: 'inline-flex', gap: 8, flexWrap: 'wrap', justifyContent: 'center',
          }}>
            {['.edf', '.csv', '.txt'].map(ext => (
              <span key={ext} style={{
                background: 'rgba(255,255,255,.06)',
                border: '1px solid rgba(255,255,255,.1)',
                borderRadius: 5, padding: '3px 10px',
                fontSize: 11, color: C.text, fontFamily: 'monospace',
              }}>{ext}</span>
            ))}
          </div>
          <div style={{ fontSize: 10, color: C.muted, marginTop: 14, lineHeight: 1.6 }}>
            Signal canal Fp2 · 250 Hz · minimum 4 secondes<br/>
            CSV : colonne 'raw' ou 'uv' ou première colonne numérique
          </div>
        </>
      )}
    </div>
  )
}

// ── Composant principal ───────────────────────────────────────────────────────
export default function FileAnalysisTab() {
  const [loading, setLoading]   = useState(false)
  const [result,  setResult]    = useState(null)
  const [error,   setError]     = useState(null)

  const handleFile = useCallback(async (file) => {
    setLoading(true)
    setError(null)
    setResult(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const resp = await axios.post(`${API}/analyze_file`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120_000,  // fichiers longs = traitement long
      })
      setResult(resp.data)
    } catch (e) {
      const msg = e.response?.data?.detail || e.message || 'Erreur inconnue'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <div style={{ padding: '0 0 40px' }}>

      {/* En-tête */}
      <div style={{ marginBottom: 20 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: '#f1f5f9', marginBottom: 4 }}>
          Analyse de fichier EEG offline
        </div>
        <div style={{ fontSize: 11, color: C.muted, lineHeight: 1.7 }}>
          Importez un fichier signal (.edf / .csv / .txt) pour obtenir la classification
          état cognitif époque par époque — même pipeline que le temps réel.
        </div>
      </div>

      {/* Zone de dépôt */}
      <DropZone onFile={handleFile} loading={loading} />

      {/* Erreur */}
      {error && (
        <div style={{
          marginTop: 16,
          background: 'rgba(255,77,109,.07)', border: '1px solid rgba(255,77,109,.25)',
          borderRadius: 9, padding: '12px 16px',
          fontSize: 12, color: '#fca5a5', lineHeight: 1.6,
        }}>
          ❌ {error}
        </div>
      )}

      {/* Résultats */}
      {result && (
        <div style={{ marginTop: 20 }}>

          {/* Bouton reset */}
          <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 12 }}>
            <button
              onClick={() => { setResult(null); setError(null) }}
              style={{
                background: 'rgba(255,255,255,.04)',
                border: '1px solid rgba(255,255,255,.08)',
                borderRadius: 7, color: C.muted,
                padding: '5px 14px', cursor: 'pointer', fontSize: 11,
              }}
            >
              ← Nouvelle analyse
            </button>
          </div>

          {/* Résumé */}
          <SummaryCard result={result} />

          {/* Table époques */}
          {result.epochs?.length > 0 ? (
            <div style={{
              background: C.card, border: `1px solid ${C.border}`,
              borderRadius: 12, padding: '16px 18px',
            }}>
              <div style={{
                fontSize: 10, fontWeight: 700, color: C.muted,
                letterSpacing: 1, marginBottom: 12,
              }}>
                DÉTAIL PAR ÉPOQUE
              </div>
              <EpochTable epochs={result.epochs} />
            </div>
          ) : (
            <div style={{
              background: C.card, border: `1px solid ${C.border}`,
              borderRadius: 12, padding: 20,
              fontSize: 12, color: C.muted, textAlign: 'center',
            }}>
              Aucune époque acceptée — vérifiez la qualité du signal
            </div>
          )}

          {/* Footer */}
          <div style={{
            marginTop: 14, fontSize: 9, color: '#1e2d3d', textAlign: 'center',
          }}>
            LightGBM · FeatEng · 63 features · LOSO validé · NeuroCap v7.3
          </div>
        </div>
      )}
    </div>
  )
}
