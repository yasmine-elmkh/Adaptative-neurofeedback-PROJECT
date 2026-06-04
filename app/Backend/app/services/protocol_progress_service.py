"""
NeuroCap — Service de progression calendaire du protocole

Gère user_protocol_progress :
  - Initialisation à la calibration (S1)
  - Mise à jour automatique après chaque séance
  - Génération du calendrier prévisionnel (profils A/B/C)
  - Décisions de bilan (B1/B2/B3)
  - Détection des critères d'arrêt anticipé
"""

from __future__ import annotations

import logging
import uuid
from datetime import date, datetime, timezone, timedelta
from statistics import mean
from typing import Optional

from supabase import AsyncClient

logger = logging.getLogger(__name__)

# ── Structure protocole par profil ───────────────────────────────────────────

PROTOCOL_STRUCTURE: dict[str, dict] = {
    "A": {   # Répondeur rapide : 12 séances ~8 semaines
        "total": 12,
        "phases": {
            "phase1_discovery":     {"range": (1, 3),   "interval_days": 7},
            "phase2_training":      {"range": (4, 8),   "interval_days": 4},
            "phase3_consolidation": {"range": (9, 12),  "interval_days": 4},
        },
        "palier_map": {"P1": (1, 2), "P2": (3, 5), "P3": (6, 9), "P4": (10, 12)},
        "bilan_sessions": {4, 8, 12},
    },
    "B": {   # Standard : 15 séances ~10 semaines
        "total": 15,
        "phases": {
            "phase1_discovery":     {"range": (1, 3),   "interval_days": 5},
            "phase2_training":      {"range": (4, 10),  "interval_days": 3},
            "phase3_consolidation": {"range": (11, 15), "interval_days": 3},
        },
        "palier_map": {"P1": (1, 3), "P2": (4, 7), "P3": (8, 12), "P4": (13, 15)},
        "bilan_sessions": {5, 10, 15},
    },
    "C": {   # Répondeur lent : 18 séances ~12 semaines
        "total": 18,
        "phases": {
            "phase1_discovery":     {"range": (1, 5),   "interval_days": 7},
            "phase2_training":      {"range": (6, 13),  "interval_days": 4},
            "phase3_consolidation": {"range": (14, 18), "interval_days": 4},
        },
        "palier_map": {"P1": (1, 5), "P2": (6, 9), "P3": (10, 14), "P4": (15, 18)},
        "bilan_sessions": {5, 10, 15},
    },
}

# ── Détection profil cognitif ────────────────────────────────────────────────

def detect_cognitive_profile(
    alpha_beta_ratio: float,
    alpha_blocking_pct: float,
) -> str:
    """
    Détermine le profil A/B/C à partir des données de calibration.
    - A (Hyperactif) : ratio α/β > 1.5 ET blocage > 30 %
    - C (Hypoactif)  : ratio α/β < 0.8 OU blocage < 15 %
    - B (Standard)   : reste
    """
    if alpha_beta_ratio > 1.5 and alpha_blocking_pct > 30:
        return "A"
    if alpha_beta_ratio < 0.8 or alpha_blocking_pct < 15:
        return "C"
    return "B"


# ── Helpers par session ───────────────────────────────────────────────────────

def get_phase_for_session(session_num: int, profile: str) -> str:
    structure = PROTOCOL_STRUCTURE.get(profile, PROTOCOL_STRUCTURE["B"])
    for phase_name, conf in structure["phases"].items():
        lo, hi = conf["range"]
        if lo <= session_num <= hi:
            return phase_name
    return "phase3_consolidation"


def get_palier_for_session(session_num: int, profile: str) -> str:
    palier_map = PROTOCOL_STRUCTURE.get(profile, PROTOCOL_STRUCTURE["B"])["palier_map"]
    for palier, (lo, hi) in palier_map.items():
        if lo <= session_num <= hi:
            return palier
    return "P4"


# ── Génération du calendrier prévisionnel ────────────────────────────────────

def generate_planned_calendar(
    profile: str,
    start_date: date,
) -> tuple[list[dict], date]:
    """
    Génère la liste des séances planifiées avec leurs dates prévisionnelles.
    Retourne (planned_session_dates, planned_end_date).
    """
    structure = PROTOCOL_STRUCTURE.get(profile, PROTOCOL_STRUCTURE["B"])
    total = structure["total"]
    bilans = structure["bilan_sessions"]
    result: list[dict] = []
    current = start_date

    for n in range(1, total + 1):
        phase = get_phase_for_session(n, profile)
        palier = get_palier_for_session(n, profile)
        interval = structure["phases"][phase]["interval_days"]
        planned_date = current + timedelta(days=(interval if n > 1 else 0))
        current = planned_date

        result.append({
            "session_num":     n,
            "planned_date":    planned_date.isoformat(),
            "phase":           phase,
            "palier":          palier,
            "is_bilan":        n in bilans,
            "is_calibration":  n == 1,
        })

    # S16 suivi (optionnelle, 7 jours après la dernière)
    result.append({
        "session_num":  16,
        "planned_date": (current + timedelta(days=7)).isoformat(),
        "phase":        "followup",
        "palier":       None,
        "is_bilan":     False,
        "is_calibration": False,
        "is_followup":  True,
    })

    return result, current


# ── Décision de bilan ────────────────────────────────────────────────────────

def determine_bilan_decision(avg_success_rate: float) -> str:
    if avg_success_rate >= 0.65:
        return "continue"
    if avg_success_rate >= 0.40:
        return "adjust_palier"
    return "repeat_phase"


# ── Initialisation à S1 ──────────────────────────────────────────────────────

async def initialize_user_progress(
    user_id: str,
    profile_type: str,
    start_date: Optional[date],
    db: AsyncClient,
) -> dict:
    """
    Crée ou met à jour user_protocol_progress lors de la calibration (S1).
    Génère le calendrier prévisionnel selon le profil détecté.
    """
    if start_date is None:
        start_date = date.today()

    planned_dates, planned_end = generate_planned_calendar(profile_type, start_date)

    now = datetime.now(timezone.utc).isoformat()
    row = {
        "user_id":               user_id,
        "current_session_number": 1,
        "total_sessions_completed": 1,
        "current_phase":         "phase1_discovery",
        "current_palier":        "P1",
        "cognitive_profile":     profile_type,
        "profile_detected_at":   now,
        "planned_start_date":    start_date.isoformat(),
        "planned_end_date":      planned_end.isoformat(),
        "planned_session_dates": planned_dates,
        "actual_start_date":     start_date.isoformat(),
        "actual_session_dates":  [{
            "session_num": 1,
            "actual_date": now,
            "status": "completed",
            "score": 80,
            "palier": "P1",
        }],
        "status":    "in_progress",
        "updated_at": now,
    }

    try:
        # Upsert sur user_id (UNIQUE constraint)
        await db.table("user_protocol_progress").upsert(row, on_conflict="user_id").execute()
    except Exception as exc:
        logger.error("initialize_user_progress: %s", exc)

    return row


# ── Mise à jour après chaque séance ──────────────────────────────────────────

async def update_progress_after_session(
    user_id: str,
    session_num: int,
    score: float,
    success_rate: float,
    palier: str,
    artifact_rate: float,
    db: AsyncClient,
) -> dict:
    """
    Appelé automatiquement à la fin de chaque séance (PUT /sessions/{n}/complete).
    Met à jour user_protocol_progress.
    """
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()

    # Lire la progression actuelle
    resp = await (
        db.table("user_protocol_progress")
        .select("*")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not resp.data:
        logger.warning("update_progress_after_session: no row for user %s — initialising", user_id)
        await initialize_user_progress(user_id, "B", date.today(), db)
        resp = await db.table("user_protocol_progress").select("*").eq("user_id", user_id).limit(1).execute()

    current = resp.data[0]
    profile = current.get("cognitive_profile") or "B"
    total_done = (current.get("total_sessions_completed") or 0) + 1

    # Calendrier réel : ajouter la séance
    actual_dates: list[dict] = current.get("actual_session_dates") or []
    # Éviter les doublons
    existing_nums = {e.get("session_num") for e in actual_dates}
    if session_num not in existing_nums:
        actual_dates.append({
            "session_num": session_num,
            "actual_date": now_iso,
            "status":      "completed",
            "score":       score,
            "success_rate": round(success_rate, 4),
            "palier":      palier,
        })

    # Calculs de progression
    all_scores   = [e.get("score") for e in actual_dates if e.get("score") is not None]
    all_sr       = [e.get("success_rate") for e in actual_dates if e.get("success_rate") is not None]
    avg_score    = round(mean(all_scores), 1) if all_scores else None
    avg_sr       = round(mean(all_sr), 4)     if all_sr     else None

    # Phase et palier courants
    new_phase  = get_phase_for_session(session_num, profile)
    new_palier = palier  # le palier vient du moteur protocol_engine

    # Critère d'arrêt anticipé
    stop_reason = _check_early_stop(all_scores, all_sr, artifact_rate)

    # Statut global
    structure = PROTOCOL_STRUCTURE.get(profile, PROTOCOL_STRUCTURE["B"])
    if stop_reason:
        new_status = "early_stopped"
    elif session_num >= structure["total"]:
        new_status = "completed"
    else:
        new_status = "in_progress"

    patch: dict = {
        "current_session_number":   session_num,
        "total_sessions_completed": total_done,
        "current_phase":            new_phase if not stop_reason else current.get("current_phase"),
        "current_palier":           new_palier,
        "actual_session_dates":     actual_dates,
        "avg_session_score":        avg_score,
        "success_rate_global":      avg_sr,
        "last_threshold_value":     None,
        "status":                   new_status,
        "updated_at":               now_iso,
    }

    # Bilans
    if session_num == 5:
        patch["bilan_b1_completed"] = True
        patch["bilan_b1_date"]      = now_iso
        patch["bilan_b1_score"]     = score
        patch["bilan_b1_decision"]  = determine_bilan_decision(avg_sr or 0)

    if session_num == 10:
        patch["bilan_b2_completed"] = True
        patch["bilan_b2_date"]      = now_iso
        patch["bilan_b2_score"]     = score
        patch["bilan_b2_decision"]  = determine_bilan_decision(avg_sr or 0)

    if session_num == 15:
        patch["bilan_b3_completed"] = True
        patch["bilan_b3_date"]      = now_iso
        patch["bilan_b3_score"]     = score
        patch["bilan_b3_decision"]  = determine_bilan_decision(avg_sr or 0)

    if stop_reason:
        patch["early_stop_reason"]  = stop_reason
        patch["early_stop_session"] = session_num
        patch["early_stop_date"]    = now_iso

    try:
        await (
            db.table("user_protocol_progress")
            .update(patch)
            .eq("user_id", user_id)
            .execute()
        )
    except Exception as exc:
        logger.error("update_progress_after_session: %s", exc)

    return {**current, **patch}


# ── Critères d'arrêt anticipé ────────────────────────────────────────────────

def _check_early_stop(
    all_scores: list[float],
    all_success_rates: list[float],
    artifact_rate: float,
) -> Optional[str]:
    """
    Vérifie les 3 critères d'arrêt automatique :
    1. Aucune progression sur 5 séances consécutives (delta < 5 pts)
    2. Bien-être bas (si wellbeing < 4/10 — simulé via score < 30 × 3)
    3. Artefacts > 40 %
    """
    # Critère artefacts
    if artifact_rate > 0.40:
        return "artifacts"

    # Critère pas de progression (5 séances min)
    if len(all_scores) >= 5:
        last5 = all_scores[-5:]
        if max(last5) - min(last5) < 5.0:
            return "no_progress"

    # Critère score faible persistant
    if len(all_scores) >= 3:
        last3 = all_scores[-3:]
        if all(s < 30 for s in last3):
            return "wellbeing"

    return None


# ── Lecture de la progression ────────────────────────────────────────────────

async def get_user_progress(user_id: str, db: AsyncClient) -> Optional[dict]:
    """Retourne la progression complète d'un utilisateur."""
    try:
        resp = await (
            db.table("user_protocol_progress")
            .select("*")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception as exc:
        logger.warning("get_user_progress: %s", exc)
        return None


async def merge_calendar_with_progress(
    calendar_sessions: list[dict],
    user_id: str,
    db: AsyncClient,
) -> list[dict]:
    """
    Fusionne le calendrier opérationnel (protocol_sessions) avec les dates
    prévisionnelles de user_protocol_progress.
    Ajoute 'planned_date' à chaque entrée du calendrier si disponible.
    """
    progress = await get_user_progress(user_id, db)
    if not progress:
        return calendar_sessions

    planned: list[dict] = progress.get("planned_session_dates") or []
    planned_map = {p["session_num"]: p for p in planned}

    enriched = []
    for s in calendar_sessions:
        n = s.get("session_number")
        plan = planned_map.get(n, {})
        enriched.append({
            **s,
            "planned_date":      plan.get("planned_date"),
            "is_calibration":    plan.get("is_calibration", False),
            "cognitive_profile": progress.get("cognitive_profile"),
        })

    return enriched


async def get_therapist_progress_dashboard(
    therapist_id: str,
    db: AsyncClient,
) -> list[dict]:
    """
    Retourne la progression de tous les patients du thérapeute (vue summary).
    """
    try:
        # Récupérer les patients du thérapeute
        patients_resp = await (
            db.table("users")
            .select("id")
            .eq("therapist_id", therapist_id)
            .execute()
        )
        patient_ids = [p["id"] for p in (patients_resp.data or [])]
        if not patient_ids:
            return []

        results = []
        for pid in patient_ids:
            row = await get_user_progress(pid, db)
            if row:
                # Calcul progress_percent
                profile = row.get("cognitive_profile") or "B"
                total_target = PROTOCOL_STRUCTURE.get(profile, PROTOCOL_STRUCTURE["B"])["total"]
                pct = round(row.get("total_sessions_completed", 0) / total_target * 100, 1)
                results.append({**row, "progress_percent": pct})

        return results
    except Exception as exc:
        logger.warning("get_therapist_progress_dashboard: %s", exc)
        return []
