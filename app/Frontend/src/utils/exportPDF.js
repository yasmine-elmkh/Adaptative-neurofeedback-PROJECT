import jsPDF from 'jspdf'

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
