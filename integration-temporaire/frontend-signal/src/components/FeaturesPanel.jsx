/**
 * FeaturesPanel — affiche toutes les features calculées par server_final.py :
 * - 5 puissances relatives (rel_delta…rel_gamma)
 * - 4 ratios cognitifs (engagement, stress_idx, theta_beta, alpha_beta)
 * - 3 paramètres Hjorth (activity, mobility, complexity)
 * - 4 spectraux (spectral_entropy, sef95, rms, mean_amp)
 * - 3 distribution (skewness, kurtosis, zcr)
 * - PAC θ→γ (Tort 2010)
 * - 4 fractal/graphe (Al-Salman 2019)
 * - 5 dB vs baseline
 */

const f4 = v => typeof v === 'number' ? v.toFixed(4) : '—'
const f3 = v => typeof v === 'number' ? v.toFixed(3) : '—'
const f1 = v => typeof v === 'number' ? v.toFixed(1) : '—'

function Group({ title, color, children }) {
  return (
    <div style={{
      background:'#0a0e18', border:'1px solid rgba(255,255,255,.05)',
      borderRadius:12, padding:'14px 16px',
    }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:12 }}>
        <div style={{ width:7, height:7, borderRadius:2, background:color, boxShadow:`0 0 8px ${color}55` }} />
        <span style={{ fontFamily:"'Space Mono',monospace", fontSize:9, letterSpacing:1.5,
                       textTransform:'uppercase', color }}>{title}</span>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill,minmax(110px,1fr))', gap:7 }}>
        {children}
      </div>
    </div>
  )
}

function Cell({ label, value, desc, color, warn, accent }) {
  const c = warn ? '#f5a623' : accent ? '#00e5b0' : color || '#c9d8e8'
  return (
    <div style={{
      background:'rgba(255,255,255,.02)', borderRadius:8,
      padding:'9px 10px',
      border:`1px solid ${warn ? 'rgba(245,166,35,.15)' : accent ? 'rgba(0,229,176,.12)' : 'rgba(255,255,255,.04)'}`,
    }}>
      <div style={{ fontSize:8, color:'#4a5a6e', marginBottom:4, lineHeight:1.3 }}>{label}</div>
      <div style={{ fontFamily:"'Space Mono',monospace", fontSize:13, fontWeight:700, color:c }}>
        {value}
      </div>
      {desc && <div style={{ fontSize:8, color:'#3a4a5e', marginTop:3 }}>{desc}</div>}
    </div>
  )
}

export default function FeaturesPanel({ features: f = {}, graph = {}, epochIdx }) {
  return (
    <div style={{ display:'flex', flexDirection:'column', gap:14, animation:'fadeIn .3s ease' }}>

      {epochIdx && (
        <div style={{ fontFamily:"'Space Mono',monospace", fontSize:10, color:'#3a4a5e' }}>
          Époque #{epochIdx} — Windowed 4s · 75% overlap · Welch PSD
        </div>
      )}

      {/* ── Puissances relatives ── */}
      <Group title="Puissances relatives (Cohen 2014)" color="#4da6ff">
        <Cell label="δ Delta 0.5–4 Hz"  value={f4(f.rel_delta)} desc="Sommeil profond"   color="#818cf8" />
        <Cell label="θ Theta 4–8 Hz"    value={f4(f.rel_theta)} desc="Mémoire / rêverie" color="#f59e0b" />
        <Cell label="α Alpha 8–13 Hz"   value={f4(f.rel_alpha)} desc="Relaxation/alerte" color="#10b981" accent={f.rel_alpha > 0.3} />
        <Cell label="β Beta 13–30 Hz"   value={f4(f.rel_beta)}  desc="Cognition active"  color="#3b82f6" />
        <Cell label="γ Gamma 30–40 Hz"  value={f4(f.rel_gamma)} desc="Traitement haut"   color="#ef4444" />
      </Group>

      {/* ── Ratios cognitifs ── */}
      <Group title="Ratios cognitifs" color="#00e5b0">
        <Cell label="Engagement β/(α+θ)" value={f3(f.engagement)}  desc="EI Pope 1995"  accent={f.engagement > 1.5} />
        <Cell label="Stress β/α"          value={f3(f.stress_idx)} desc="Indice stress"  warn={f.stress_idx > 2} />
        <Cell label="θ/β (TDAH)"          value={f3(f.theta_beta)} desc="Relaxation" />
        <Cell label="α/β (Détente)"        value={f3(f.alpha_beta)} desc="Calme/Activé" />
      </Group>

      {/* ── Hjorth ── */}
      <Group title="Paramètres Hjorth (Cohen 2014 ch.17)" color="#a78bfa">
        <Cell label="Activity (Var)"    value={f4(f.hjorth_activity)}   desc="Amplitude²" />
        <Cell label="Mobility √(V1/V0)" value={f4(f.hjorth_mobility)}   desc="Fréquence moy." />
        <Cell label="Complexity"        value={f4(f.hjorth_complexity)} desc="Variation fréq." />
      </Group>

      {/* ── Spectral ── */}
      <Group title="Analyse spectrale" color="#f472b6">
        <Cell label="SEF95 (Hz)"       value={f1(f.sef95)}            desc="95% énergie sous" />
        <Cell label="Entropie spec."   value={f4(f.spectral_entropy)} desc="Complexité PSD" />
        <Cell label="RMS (µV)"         value={f4(f.rms)}              desc="Amplitude eff." />
        <Cell label="Amp. moy. (µV)"   value={f4(f.mean_amp)} />
      </Group>

      {/* ── Distribution temporelle ── */}
      <Group title="Distribution temporelle" color="#f59e0b">
        <Cell label="Skewness"  value={f4(f.skewness)} desc="Asymétrie" warn={Math.abs(f.skewness) > 2} />
        <Cell label="Kurtosis"  value={f4(f.kurtosis)} desc="Aplatissement (artefacts)" warn={f.kurtosis > 5} />
        <Cell label="ZCR"       value={f4(f.zcr)}      desc="Zero-crossing rate" />
      </Group>

      {/* ── PAC ── */}
      <Group title="PAC θ→γ (Tort et al. 2010)" color="#06b6d4">
        <Cell label="PAC θ→γ proxy"  value={f4(f.pac_theta_gamma)} desc="Corrél. env.γ / phase θ" accent={f.pac_theta_gamma > 0.3} />
      </Group>

      {/* ── Fractal + Graphe ── */}
      <Group title="Dimension Fractale + Graphe (Al-Salman 2019)" color="#ec4899">
        <Cell label="FD global"       value={f4(f.fractal_dim)}         desc="Box-counting moyen" />
        <Cell label="Degree dist."    value={f4(f.fd_degree_dist_mean)} desc="Degré moyen graphe" />
        <Cell label="Clustering coef" value={f4(f.fd_clustering_coeff)} desc="Connectivité locale" />
        <Cell label="Jaccard moyen"   value={f4(f.fd_jaccard_mean)}     desc="Similarité voisins" />
      </Group>

      {/* ── dB vs Baseline ── */}
      {(f.db_alpha !== undefined) && (
        <Group title="Puissance dB vs Baseline" color="#6ee7b7">
          {['delta','theta','alpha','beta','gamma'].map(b => (
            <Cell key={b}
              label={`${b} dB`}
              value={f3(f[`db_${b}`])}
              desc="vs baseline"
              accent={f[`db_${b}`] > 1}
              warn={f[`db_${b}`] < -5}
            />
          ))}
        </Group>
      )}
    </div>
  )
}
