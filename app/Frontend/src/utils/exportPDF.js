import jsPDF from 'jspdf'

/**
 * Generate a PDF report for a completed calibration session.
 */
export function exportCalibrationPDF(profile, userEmail = '') {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' })
  const W      = doc.internal.pageSize.getWidth()
  const pageH  = doc.internal.pageSize.getHeight()
  const margin = 20
  let y = margin

  // ── Header ──────────────────────────────────────────────────────────────
  doc.setFillColor(24, 40, 72)
  doc.rect(0, 0, W, 30, 'F')
  // gradient band
  doc.setFillColor(108, 99, 255, 0.7)
  doc.rect(0, 0, W / 2, 30, 'F')
  doc.setFontSize(20)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(255, 255, 255)
  doc.text('NeuroCap', margin, 13)
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('Rapport de Calibration EEG — Séance 1', margin, 22)
  y = 40

  const line = (txt, size = 11, bold = false, color = [30, 30, 50]) => {
    doc.setFontSize(size)
    doc.setFont('helvetica', bold ? 'bold' : 'normal')
    doc.setTextColor(...color)
    doc.text(txt, margin, y)
    y += size * 0.52
  }

  const hr = (gap = 5) => {
    doc.setDrawColor(200, 210, 230)
    doc.line(margin, y, W - margin, y)
    y += gap
  }

  const kv = (label, value, valueColor = [30, 30, 50]) => {
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(100, 110, 140)
    doc.text(label, margin, y)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(...valueColor)
    doc.text(String(value ?? '—'), margin + 70, y)
    y += 6
  }

  // ── Section titre ────────────────────────────────────────────────────────
  line('Calibration EEG Individuelle — Résultats', 14, true, [40, 60, 120])
  y += 2
  hr()

  // ── Date & email ─────────────────────────────────────────────────────────
  kv('Date', new Date().toLocaleString('fr-FR'))
  if (userEmail) kv('Envoyé à', userEmail, [80, 100, 180])
  y += 3
  hr()

  // ── Profil neurophysiologique ─────────────────────────────────────────────
  line('Profil Neurophysiologique', 12, true, [40, 60, 120])
  y += 2

  const ptype = profile?.profile_type ?? '—'
  const typeColor = ptype === 'A' ? [34, 197, 94] : ptype === 'C' ? [239, 68, 68] : [99, 102, 241]
  kv('Profil cognitif', `Type ${ptype}`, typeColor)
  kv('IAPF',            profile?.iapf != null ? `${profile.iapf} Hz` : '—')
  kv('Plage alpha',     profile?.alpha_band_lo != null
    ? `${profile.alpha_band_lo} – ${profile.alpha_band_hi} Hz`
    : '—')
  kv('P_alpha_ref',     profile?.p_alpha_ref != null ? profile.p_alpha_ref.toFixed(4) : '—')
  kv('ERD alpha',       profile?.erd_pct != null ? `${profile.erd_pct}%` : '—')
  kv('Seuil adaptatif', profile?.threshold_current != null
    ? profile.threshold_current.toFixed(4)
    : '—')
  y += 3
  hr()

  // ── Palier de départ ─────────────────────────────────────────────────────
  line('Programme personnalisé', 12, true, [40, 60, 120])
  y += 2
  const palier = profile?.palier_initial ?? 'P1'
  const palierDesc = {
    P1: 'Initiation — feedback sonore uniquement',
    P2: 'Apprentissage — son + visuel',
    P3: 'Maîtrise — feedback complet + jeux',
    P4: 'Autonomie progressive',
  }[palier] ?? palier
  kv('Palier initial', `${palier} — ${palierDesc}`, [108, 99, 255])
  y += 4

  // ── Explication profil ────────────────────────────────────────────────────
  const profileExplain = {
    A: 'Profil alpha dominant : forte réactivité à la relaxation. Vos ondes alpha de repos sont élevées et répondent bien aux exercices de détente guidée.',
    B: 'Profil équilibré alpha/beta : réponse mixte aux stimuli. Vous bénéficierez des deux modalités de feedback (concentration et relaxation).',
    C: 'Profil beta dominant : activation cognitive élevée. Votre entraînement ciblera la régulation des ondes beta et la réduction du TBR.',
  }[ptype] ?? 'Profil établi selon vos mesures neurophysiologiques individuelles.'

  doc.setFillColor(240, 244, 255)
  const explLines = doc.splitTextToSize(profileExplain, W - margin * 2 - 10)
  const boxH = explLines.length * 5 + 12
  doc.roundedRect(margin, y, W - margin * 2, boxH, 3, 3, 'F')
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(50, 60, 90)
  doc.text(explLines, margin + 5, y + 7)
  y += boxH + 6
  hr()

  // ── Prochaines étapes ─────────────────────────────────────────────────────
  line('Prochaines étapes', 12, true, [40, 60, 120])
  y += 2
  const steps = [
    '• S2–S5  : Phase d\'initiation — Apprentissage du protocole de base.',
    '• S6–S10 : Phase intensive — Consolidation neurofonctionnelle.',
    '• S11–S15: Phase de maîtrise — Autonomie et transfert des acquis.',
    '• Séances de bilan après S5, S10 et S15 pour ajuster le palier.',
  ]
  steps.forEach(s => {
    doc.setFontSize(10)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(50, 60, 90)
    doc.text(s, margin, y)
    y += 6
  })
  y += 4

  // ── Footer ────────────────────────────────────────────────────────────────
  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(160, 170, 190)
  doc.text(
    `NeuroCap — Calibration EEG — Généré le ${new Date().toLocaleString('fr-FR')} — Confidentiel patient`,
    margin,
    pageH - 10,
  )

  doc.save(`neurocap_calibration_${new Date().toISOString().slice(0, 10)}.pdf`)
}

/**
 * Generate a PDF report for a single session.
 * Uses jsPDF text-only (no html2canvas) for fast generation without layout dependency.
 */
export async function exportSessionPDF(session, reportData) {
  const doc = new jsPDF({ unit: 'mm', format: 'a4' })
  const W = doc.internal.pageSize.getWidth()
  const margin = 20
  let y = margin

  const line = (txt, size = 11, bold = false, color = [30, 30, 50]) => {
    doc.setFontSize(size)
    doc.setFont('helvetica', bold ? 'bold' : 'normal')
    doc.setTextColor(...color)
    doc.text(txt, margin, y)
    y += size * 0.5
  }

  const hr = () => {
    doc.setDrawColor(200, 210, 230)
    doc.line(margin, y, W - margin, y)
    y += 5
  }

  // ── Header ──────────────────────────────────────────────────────────────────
  doc.setFillColor(24, 40, 72)
  doc.rect(0, 0, W, 28, 'F')
  doc.setFontSize(18)
  doc.setFont('helvetica', 'bold')
  doc.setTextColor(255, 255, 255)
  doc.text('NeuroCap', margin, 13)
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.text('Rapport de session EEG — Easy Medical Device', margin, 21)
  y = 36

  // ── Session identity ────────────────────────────────────────────────────────
  line(`Rapport de session`, 14, true, [40, 60, 120])
  y += 2
  hr()

  const s = session
  const rows = [
    ['Identifiant session', s.id ?? '—'],
    ['Date',               s.created_at ? new Date(s.created_at).toLocaleString() : '—'],
    ['Objectif',           s.objective ?? '—'],
    ['Feedback',           s.feedback_mode ?? '—'],
    ['Statut',             s.status ?? '—'],
    ['Durée',              s.duration_seconds ? `${Math.round(s.duration_seconds / 60)} min` : '—'],
    ['Blocs complétés',    String(s.n_blocks ?? '—')],
  ]
  rows.forEach(([label, value]) => {
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(100, 110, 140)
    doc.text(label, margin, y)
    doc.setFont('helvetica', 'normal')
    doc.setTextColor(30, 30, 50)
    doc.text(value, margin + 55, y)
    y += 6
  })
  y += 4
  hr()

  // ── Key metrics ──────────────────────────────────────────────────────────────
  line('Métriques clés', 12, true, [40, 60, 120])
  y += 2
  const metrics = [
    ['Score global',         s.score != null ? `${s.score.toFixed(1)} %` : '—'],
    ['Concentration moy.',   s.avg_concentration != null ? `${(s.avg_concentration).toFixed(1)} %` : '—'],
    ['Stress moyen',         s.avg_stress != null ? `${(s.avg_stress).toFixed(1)} %` : '—'],
    ['TBR moyen',            s.avg_tbr != null ? s.avg_tbr.toFixed(3) : '—'],
  ]
  metrics.forEach(([label, value]) => {
    doc.setFontSize(10)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(100, 110, 140)
    doc.text(label, margin, y)
    doc.setFont('helvetica', 'bold')
    doc.setTextColor(s.score >= 70 ? 22 : s.score >= 50 ? 200 : 200, s.score >= 70 ? 160 : s.score >= 50 ? 140 : 60, 22)
    doc.text(value, margin + 55, y)
    y += 6
  })
  y += 4
  hr()

  // ── Recommendations ──────────────────────────────────────────────────────────
  line('Recommandations', 12, true, [40, 60, 120])
  y += 2
  const rec = reportData?.recommendations || s.recommendations || 'Aucune recommandation disponible.'
  const lines = doc.splitTextToSize(rec, W - margin * 2)
  doc.setFontSize(10)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(50, 60, 90)
  doc.text(lines, margin, y)
  y += lines.length * 5 + 6
  hr()

  // ── Footer ───────────────────────────────────────────────────────────────────
  const pageH = doc.internal.pageSize.getHeight()
  doc.setFontSize(8)
  doc.setFont('helvetica', 'normal')
  doc.setTextColor(160, 170, 190)
  doc.text(`NeuroCap — Généré le ${new Date().toLocaleString()} — Confidentiel patient`, margin, pageH - 10)

  doc.save(`neurocap_session_${s.id?.slice(0, 8) ?? 'rapport'}.pdf`)
}
