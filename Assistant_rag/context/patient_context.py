"""
Assemblage du contexte patient depuis Supabase.

Récupère en parallèle (séquentiel pour compatibilité supabase-py async) :
  - eeg_profiles     → profil EEG, IAPF, TBR baseline, palier
  - sessions         → 10 dernières séances (score, TBR, concentration, stress)
  - eeg_reports      → dernier rapport EEG (dominant state, pcts)
  - protocol_sessions → phase actuelle, numéro de séance

Calcule : score moyen, tendance, prédiction prochaine séance.
"""

import logging
from typing import Dict

from supabase import AsyncClient

logger = logging.getLogger(__name__)


async def build_user_context(user_id: str, db: AsyncClient) -> Dict:
    """
    Retourne un dictionnaire avec toutes les métriques du patient
    prêtes à être injectées dans le prompt RAG via fmt_patient().
    """

    # ── Profil EEG ────────────────────────────────────────────────────────────
    try:
        r = await (
            db.table("eeg_profiles")
            .select(
                "profile_type, iapf, baseline_tbr, baseline_alpha, "
                "baseline_beta, baseline_theta, reactivity_score, "
                "palier, current_threshold"
            )
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        profile = (r.data or [{}])[0]
    except Exception:
        profile = {}

    # ── Historique séances (10 dernières) ─────────────────────────────────────
    try:
        r = await (
            db.table("sessions")
            .select("id, score, avg_tbr, avg_concentration, avg_stress, created_at, objective")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        sessions = r.data or []
    except Exception:
        sessions = []

    # ── Dernier rapport EEG ───────────────────────────────────────────────────
    try:
        r = await (
            db.table("eeg_reports")
            .select(
                "dominant_state, concentration_pct, stress_pct, "
                "mean_confidence, n_epochs_accepted, n_epochs_rejected, "
                "duration_s, created_at"
            )
            .eq("patient_id", user_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        last_report = (r.data or [{}])[0]
    except Exception:
        last_report = {}

    # ── Protocole ─────────────────────────────────────────────────────────────
    try:
        r = await (
            db.table("protocol_sessions")
            .select("session_number, phase, status, score")
            .eq("user_id", user_id)
            .order("session_number", desc=True)
            .limit(1)
            .execute()
        )
        last_proto = (r.data or [{}])[0]
    except Exception:
        last_proto = {}

    # ── Calculs statistiques ──────────────────────────────────────────────────
    scores = [s["score"] for s in sessions if s.get("score") is not None]
    avg_score = round(sum(scores) / len(scores), 1) if scores else None

    score_trend = None
    if len(scores) >= 6:
        recent = sum(scores[:3]) / 3
        older  = sum(scores[3:6]) / 3
        if older:
            score_trend = round((recent - older) / older * 100, 1)

    conc_vals   = [s["avg_concentration"] for s in sessions if s.get("avg_concentration")]
    stress_vals = [s["avg_stress"]        for s in sessions if s.get("avg_stress")]
    avg_conc    = round(sum(conc_vals)   / len(conc_vals),   1) if conc_vals   else None
    avg_stress  = round(sum(stress_vals) / len(stress_vals), 1) if stress_vals else None

    predicted = round(sum(scores[:3]) / 3, 1) if len(scores) >= 3 else None

    n_acc = last_report.get("n_epochs_accepted") or 0
    n_rej = last_report.get("n_epochs_rejected") or 0

    return {
        "total_sessions":         len(sessions),
        "current_phase":          last_proto.get("phase"),
        "profile":                profile.get("profile_type", "B"),
        "iapf":                   profile.get("iapf"),
        "baseline_tbr":           profile.get("baseline_tbr"),
        "baseline_alpha":         profile.get("baseline_alpha"),
        "baseline_beta":          profile.get("baseline_beta"),
        "baseline_theta":         profile.get("baseline_theta"),
        "reactivity_score":       profile.get("reactivity_score"),
        "palier":                 profile.get("palier"),
        "current_threshold":      profile.get("current_threshold"),
        "avg_score":              avg_score,
        "score_trend":            score_trend,
        "avg_concentration_pct":  avg_conc,
        "avg_stress_pct":         avg_stress,
        "last_avg_tbr":           sessions[0].get("avg_tbr")   if sessions else None,
        "last_objective":         sessions[0].get("objective") if sessions else None,
        "predicted_next_score":   predicted,
        "last_dominant_state":    last_report.get("dominant_state"),
        "last_concentration_pct": last_report.get("concentration_pct"),
        "last_stress_pct":        last_report.get("stress_pct"),
        "mean_confidence":        last_report.get("mean_confidence"),
        "n_epochs_accepted":      n_acc,
        "n_epochs_total":         n_acc + n_rej,
    }
