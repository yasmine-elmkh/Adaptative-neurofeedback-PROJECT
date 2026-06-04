"""
NeuroCap — Routes Protocole 15 séances
Préfixe : /api/protocol
"""

from __future__ import annotations
import logging
from datetime import datetime, date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_token_user_id
from app.services.protocol_engine import (
    get_phase, get_min_interval_days, can_start_session,
    adapt_threshold_after_bloc, evaluate_palier_progression,
    compute_session_score, check_early_stop_criteria,
    build_session_config, BILAN_SESSIONS, PALIER_ORDER,
)
from app.services.calibration_service import (
    compute_calibration_profile, compute_daily_threshold,
)
from app.services.protocol_progress_service import (
    initialize_user_progress,
    update_progress_after_session,
    get_user_progress,
    merge_calendar_with_progress,
    get_therapist_progress_dashboard,
    detect_cognitive_profile,
    PROTOCOL_STRUCTURE,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/protocol", tags=["Protocol"])


# ════════════════════════════════════════════════════════════════════
# Schémas Pydantic
# ════════════════════════════════════════════════════════════════════

class CalibrationPayload(BaseModel):
    epochs_c1:     list[dict] = Field(default_factory=list)
    epochs_c2:     list[dict] = Field(default_factory=list)
    epochs_c3:     list[dict] = Field(default_factory=list)
    epochs_c4:     list[dict] = Field(default_factory=list)
    questionnaire: dict       = Field(default_factory=dict)

class BlocEndPayload(BaseModel):
    session_id:       str
    bloc_number:      int
    success_rate:     float
    alpha_avg:        float
    theta_avg:        float
    baseline_theta:   float
    current_threshold: float
    duration_s:       int = 180

class SessionCompletePayload(BaseModel):
    session_id:          str
    blocs_success_rates: list[float]
    ml_confidence_avg:   float = 0.0
    artifact_rate:       float = 0.0
    subjective_pre:      Optional[dict] = None
    subjective_post:     Optional[dict] = None
    alpha_power_today:   Optional[float] = None

class PalierUpdatePayload(BaseModel):
    user_id: str
    palier:  str

class DailyThresholdPayload(BaseModel):
    p_alpha_today: float


# ════════════════════════════════════════════════════════════════════
# Helpers DB
# ════════════════════════════════════════════════════════════════════

async def _get_profile(db, user_id: str) -> dict:
    r = await db.table("eeg_profiles").select("*").eq("user_id", user_id).maybe_single().execute()
    return r.data or {}

async def _get_protocol_sessions(db, user_id: str) -> list[dict]:
    r = await db.table("protocol_sessions") \
        .select("*").eq("user_id", user_id) \
        .order("session_number").execute()
    return r.data or []

async def _upsert_profile(db, user_id: str, patch: dict):
    existing = await db.table("eeg_profiles").select("id").eq("user_id", user_id).maybe_single().execute()
    if existing.data:
        await db.table("eeg_profiles").update(patch).eq("user_id", user_id).execute()
    else:
        await db.table("eeg_profiles").insert({"user_id": user_id, **patch}).execute()


# ════════════════════════════════════════════════════════════════════
# GET /api/protocol/status
# ════════════════════════════════════════════════════════════════════

@router.get("/status")
async def get_protocol_status(
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """État du programme : séance courante, palier, phase, arrêt anticipé."""
    sessions = await _get_protocol_sessions(db, user_id)
    profile  = await _get_profile(db, user_id)

    completed  = [s for s in sessions if s["status"] == "completed"]
    next_num   = len(completed) + 1
    current_p  = profile.get("palier", "P1") or "P1"

    last_completed = None
    if completed:
        last_dt = sorted(completed, key=lambda s: s.get("completed_at") or "")[-1].get("completed_at")
        if last_dt:
            last_completed = datetime.fromisoformat(last_dt.replace("Z", "+00:00")).replace(tzinfo=None)

    can_start, reason = can_start_session(next_num, last_completed)

    # Arrêt anticipé
    recent_5 = [s for s in completed[-5:] if s.get("score") is not None]
    recent_3 = completed[-3:]
    stop, stop_reason = check_early_stop_criteria(recent_5, recent_3, 0.0, 7.0)

    return {
        "next_session_number": min(next_num, 16),
        "total_completed":     len(completed),
        "current_palier":      current_p,
        "current_phase":       get_phase(min(next_num, 15)),
        "calibration_done":    next_num > 1,
        "can_start":           can_start and not stop,
        "block_reason":        stop_reason if stop else reason,
        "early_stop":          stop,
        "profile_type":        profile.get("profile_type", "B"),
        "p_alpha_ref":         profile.get("p_alpha_ref"),
        "iapf":                profile.get("iapf"),
        "threshold_current":   profile.get("threshold_current"),
    }


# ════════════════════════════════════════════════════════════════════
# GET /api/protocol/calendar
# ════════════════════════════════════════════════════════════════════

@router.get("/calendar")
async def get_protocol_calendar(
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Retourne les 15 séances avec dates et statuts."""
    sessions   = await _get_protocol_sessions(db, user_id)
    completed  = [s for s in sessions if s["status"] == "completed"]
    next_num   = len(completed) + 1

    # Construire les 15 fiches séance
    result = []
    sess_map = {s["session_number"]: s for s in sessions}

    for n in range(1, 16):
        phase     = get_phase(n)
        is_bilan  = n in BILAN_SESSIONS
        bilan_type = f"B{[5,10,15].index(n)+1}" if is_bilan else None
        existing  = sess_map.get(n)

        if existing:
            entry = {**existing, "phase": f"phase{phase}", "is_bilan": is_bilan, "bilan_type": bilan_type}
        else:
            st = "upcoming"
            if n == next_num:
                st = "scheduled"
            entry = {
                "session_number": n,
                "phase":          f"phase{phase}",
                "palier":         "P1",
                "is_bilan":       is_bilan,
                "bilan_type":     bilan_type,
                "status":         st,
                "score":          None,
                "scheduled_date": None,
                "completed_at":   None,
            }
        result.append(entry)

    # Enrichir avec les dates planifiées de user_protocol_progress
    result = await merge_calendar_with_progress(result, user_id, db)

    return {
        "sessions":            result,
        "next_session_number": min(next_num, 16),
        "total_completed":     len(completed),
    }


# ════════════════════════════════════════════════════════════════════
# POST /api/protocol/sessions/{n}/start
# ════════════════════════════════════════════════════════════════════

@router.post("/sessions/{n}/start")
async def start_session(
    n:       int,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Démarre la séance N (vérifie intervalle + calibration)."""
    sessions  = await _get_protocol_sessions(db, user_id)
    profile   = await _get_profile(db, user_id)
    completed = [s for s in sessions if s["status"] == "completed"]

    # S2+ nécessite S1 complétée
    if n > 1 and not any(s["session_number"] == 1 for s in completed):
        raise HTTPException(400, "La calibration (Séance 1) est requise avant de commencer les séances suivantes.")

    # Vérifier intervalle
    last_completed = None
    if completed:
        last_dt = sorted(completed, key=lambda s: s.get("completed_at") or "")[-1].get("completed_at")
        if last_dt:
            last_completed = datetime.fromisoformat(last_dt.replace("Z", "+00:00")).replace(tzinfo=None)

    can, reason = can_start_session(n, last_completed)
    if not can:
        raise HTTPException(423, reason)

    # Idempotent: return existing in_progress session if one already exists
    existing_inprogress = next(
        (s for s in sessions if s["session_number"] == n and s["status"] == "in_progress"),
        None,
    )
    palier      = profile.get("palier", "P1") or "P1"
    phase       = get_phase(n)
    p_alpha_ref = profile.get("p_alpha_ref") or 0.3

    if existing_inprogress:
        session_id = existing_inprogress["id"]
    else:
        row = {
            "user_id":        user_id,
            "session_number": n,
            "phase":          phase,
            "palier":         palier,
            "is_bilan":       n in BILAN_SESSIONS,
            "status":         "in_progress",
            "created_at":     datetime.utcnow().isoformat(),
        }
        res = await db.table("protocol_sessions").insert(row).execute()
        session_id = res.data[0]["id"] if res.data else None

    config = build_session_config(n, palier, p_alpha_ref)
    return {"session_id": session_id, **config}


# ════════════════════════════════════════════════════════════════════
# GET /api/protocol/sessions/{n}/config
# ════════════════════════════════════════════════════════════════════

@router.get("/sessions/{n}/config")
async def get_session_config(
    n:       int,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Config de la séance (palier, seuils, blocs, types feedback)."""
    profile = await _get_profile(db, user_id)
    palier  = profile.get("palier", "P1") or "P1"
    p_alpha = profile.get("p_alpha_ref") or 0.3
    return build_session_config(n, palier, p_alpha)


# ════════════════════════════════════════════════════════════════════
# POST /api/protocol/sessions/{n}/bloc-end
# ════════════════════════════════════════════════════════════════════

@router.post("/sessions/{n}/bloc-end")
async def bloc_end(
    n:       int,
    body:    BlocEndPayload,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Fin d'un bloc → calcule et retourne le nouveau seuil."""
    profile = await _get_profile(db, user_id)
    palier  = profile.get("palier", "P1") or "P1"

    new_thr, reason = adapt_threshold_after_bloc(
        current_threshold  = body.current_threshold,
        bloc_success_rate  = body.success_rate,
        palier             = palier,
        bloc_theta_power   = body.theta_avg,
        baseline_theta     = body.baseline_theta,
    )

    # Enregistrer le bloc
    await db.table("protocol_blocs").insert({
        "session_id":       body.session_id,
        "bloc_number":      body.bloc_number,
        "threshold_start":  body.current_threshold,
        "threshold_end":    new_thr,
        "success_rate":     body.success_rate,
        "alpha_avg":        body.alpha_avg,
        "theta_avg":        body.theta_avg,
        "adaptation_reason": reason,
        "fatigue_detected":  reason == "fatigue_detected",
        "duration_s":        body.duration_s,
    }).execute()

    return {
        "new_threshold":    new_thr,
        "action_reason":    reason,
        "fatigue_detected": reason == "fatigue_detected",
        "palier":           palier,
    }


# ════════════════════════════════════════════════════════════════════
# PUT /api/protocol/sessions/{n}/complete
# ════════════════════════════════════════════════════════════════════

@router.put("/sessions/{n}/complete")
async def complete_session(
    n:       int,
    body:    SessionCompletePayload,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Marque la séance N comme terminée et met à jour le palier."""
    score = compute_session_score(body.blocs_success_rates, body.ml_confidence_avg)
    sr    = sum(body.blocs_success_rates) / max(len(body.blocs_success_rates), 1)

    # Mettre à jour la session
    await db.table("protocol_sessions").update({
        "status":         "completed",
        "score":          score,
        "success_rate":   sr,
        "artifact_rate":  body.artifact_rate,
        "subjective_pre":  body.subjective_pre,
        "subjective_post": body.subjective_post,
        "completed_at":    datetime.utcnow().isoformat(),
        "alpha_power_ref": body.alpha_power_today,
    }).eq("id", body.session_id).execute()

    # Évaluer progression de palier
    profile   = await _get_profile(db, user_id)
    sessions  = await _get_protocol_sessions(db, user_id)
    completed = [s for s in sessions if s["status"] == "completed"]

    current_palier = profile.get("palier", "P1") or "P1"
    new_palier, pal_reason = evaluate_palier_progression(completed, current_palier)

    # Mettre à jour le profil (seuil du jour + palier)
    profile_patch: dict = {"palier": new_palier}
    if body.alpha_power_today and profile.get("p_alpha_ref"):
        daily_thr = compute_daily_threshold(profile["p_alpha_ref"], body.alpha_power_today)
        profile_patch["threshold_current"] = daily_thr

    await _upsert_profile(db, user_id, profile_patch)

    # Mettre à jour user_protocol_progress en tâche de fond
    import asyncio as _asyncio
    _asyncio.create_task(
        update_progress_after_session(
            user_id=user_id,
            session_num=n,
            score=float(score),
            success_rate=sr,
            palier=new_palier,
            artifact_rate=body.artifact_rate,
            db=db,
        )
    )

    # Calculer la prochaine date recommandée
    from datetime import timedelta
    phase_num   = get_phase(n)
    interval    = get_min_interval_days(phase_num)
    next_date   = (date.today() + timedelta(days=interval)).isoformat()

    # Envoyer email rapport de séance au patient
    try:
        user_resp = await db.table("users").select("email,first_name").eq("id", user_id).maybe_single().execute()
        if user_resp.data:
            from app.services.email_service import send_session_report_email
            acquisition_type = "eeg_live"  # default; frontend peut passer ce champ
            _asyncio.create_task(send_session_report_email(
                to_email         = user_resp.data["email"],
                first_name       = user_resp.data.get("first_name", ""),
                session_number   = n,
                score            = score,
                success_rate     = sr,
                blocs            = body.blocs_success_rates,
                profile_type     = profile.get("profile_type", "B"),
                palier_before    = current_palier,
                palier_after     = new_palier,
                palier_reason    = pal_reason,
                next_date        = next_date,
                acquisition_type = acquisition_type,
                subjective_pre   = body.subjective_pre,
                subjective_post  = body.subjective_post,
            ))
    except Exception as e:
        logger.warning("Email rapport séance non envoyé : %s", e)

    return {
        "score":              score,
        "success_rate":       sr,
        "palier_before":      current_palier,
        "palier_after":       new_palier,
        "palier_reason":      pal_reason,
        "is_bilan":           n in BILAN_SESSIONS,
        "next_session_date":  next_date,
        "next_interval_days": interval,
    }


# ════════════════════════════════════════════════════════════════════
# GET /api/protocol/bilan/{session_number}
# ════════════════════════════════════════════════════════════════════

@router.get("/bilan/{session_number}")
async def get_bilan(
    session_number: int,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Rapport de bilan étendu pour S5, S10, S15."""
    if session_number not in BILAN_SESSIONS:
        raise HTTPException(400, "Le bilan n'est disponible que pour les séances 5, 10 et 15.")

    sessions  = await _get_protocol_sessions(db, user_id)
    profile   = await _get_profile(db, user_id)
    completed = [s for s in sessions if s["status"] == "completed"]

    covered = [s for s in completed if s["session_number"] <= session_number]
    bilan_idx = [5, 10, 15].index(session_number)
    bilan_type = f"B{bilan_idx + 1}"

    score_evolution       = [s.get("score", 0) for s in covered]
    success_rate_trend    = [round(s.get("success_rate", 0) * 100, 1) for s in covered]
    palier_evolution      = [s.get("palier", "P1") for s in covered]
    alpha_power_trend     = [s.get("alpha_power_ref") for s in covered]

    avg_success = sum(s.get("success_rate") or 0 for s in covered) / max(len(covered), 1)
    current_palier = profile.get("palier", "P1") or "P1"

    alpha_trend = 0.0
    valid_alpha = [a for a in alpha_power_trend if a is not None]
    if len(valid_alpha) >= 2:
        alpha_trend = valid_alpha[-1] - valid_alpha[0]

    new_palier, pal_decision_text = evaluate_palier_progression(covered, current_palier)
    palier_decision = (
        "upgrade"   if PALIER_ORDER.index(new_palier) > PALIER_ORDER.index(current_palier) else
        "downgrade" if PALIER_ORDER.index(new_palier) < PALIER_ORDER.index(current_palier) else
        "stable"
    )

    # Résumé questionnaires subjectifs
    pre_keys  = ["fatigue", "stress", "motivation"]
    post_keys = ["focus", "calme", "fatigue"]
    q_summary = {}
    for key in pre_keys + post_keys:
        vals = [
            (s.get("subjective_pre") or {}).get(key) or
            (s.get("subjective_post") or {}).get(key)
            for s in covered
        ]
        vals = [v for v in vals if v is not None]
        q_summary[key] = round(sum(vals) / len(vals), 1) if vals else None

    # Recommandation IA (texte simple si ai_report non disponible)
    recommendation = (
        f"Profil {profile.get('profile_type', 'B')} — {len(covered)} séances complétées. "
        f"Taux de succès moyen : {avg_success*100:.0f}%. "
        f"Palier actuel : {current_palier}. "
        f"Tendance alpha : {'en hausse' if alpha_trend > 0.01 else 'stable' if abs(alpha_trend) < 0.01 else 'en baisse'}. "
        "Continuez à maintenir votre pratique régulière."
    )

    try:
        from app.services.ai_report import generate_bilan_recommendation
        recommendation = await generate_bilan_recommendation(
            profile_type   = profile.get("profile_type", "B"),
            n_sessions     = len(covered),
            avg_success    = avg_success,
            score_evolution = score_evolution,
            current_palier = current_palier,
            alpha_trend    = alpha_trend,
            iapf           = profile.get("iapf", 10.0),
            alpha_lo       = profile.get("alpha_band_lo", 8.0),
            alpha_hi       = profile.get("alpha_band_hi", 12.0),
        )
    except Exception as e:
        logger.warning("AI bilan skipped: %s", e)

    return {
        "bilan_type":           bilan_type,
        "sessions_covered":     [s["session_number"] for s in covered],
        "score_evolution":      score_evolution,
        "success_rate_trend":   success_rate_trend,
        "palier_evolution":     palier_evolution,
        "alpha_power_trend":    alpha_power_trend,
        "iapf":                 profile.get("iapf"),
        "profile_type":         profile.get("profile_type", "B"),
        "current_palier":       current_palier,
        "palier_decision":      palier_decision,
        "palier_decision_text": pal_decision_text,
        "recommendation":       recommendation,
        "questionnaire_summary": q_summary,
        "alpha_trend":          round(alpha_trend, 4),
    }


# ════════════════════════════════════════════════════════════════════
# GET /api/protocol/profile
# ════════════════════════════════════════════════════════════════════

@router.get("/profile")
async def get_protocol_profile(
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Profil EEG calibré (IAPF, P_alpha_ref, type A/B/C)."""
    profile = await _get_profile(db, user_id)
    return profile or {"calibration_done": False}


# ════════════════════════════════════════════════════════════════════
# POST /api/protocol/calibration/complete
# ════════════════════════════════════════════════════════════════════

@router.post("/calibration/complete")
async def complete_calibration(
    body:    CalibrationPayload,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Soumet les données de calibration (Séance 1) et crée le profil EEG."""
    cal = compute_calibration_profile(
        epochs_c1     = body.epochs_c1,
        epochs_c2     = body.epochs_c2,
        epochs_c3     = body.epochs_c3,
        epochs_c4     = body.epochs_c4,
        questionnaire = body.questionnaire,
    )

    now = datetime.utcnow().isoformat()
    profile_patch = {
        **cal,
        "palier":           cal["palier_initial"],
        "calibration_date": now,
    }
    await _upsert_profile(db, user_id, profile_patch)

    # Marquer S1 comme complétée
    existing_s1 = await db.table("protocol_sessions") \
        .select("id").eq("user_id", user_id).eq("session_number", 1).maybe_single().execute()

    s1_row = {
        "user_id":        user_id,
        "session_number": 1,
        "phase":          1,
        "palier":         cal["palier_initial"],
        "is_bilan":       False,
        "status":         "completed",
        "completed_at":   now,
        "score":          80,
        "notes":          "Calibration individuelle complétée",
    }
    if existing_s1.data:
        await db.table("protocol_sessions").update(s1_row).eq("id", existing_s1.data["id"]).execute()
    else:
        await db.table("protocol_sessions").insert(s1_row).execute()

    # Initialiser user_protocol_progress avec le profil EEG détecté
    import asyncio as _asyncio
    _asyncio.create_task(initialize_user_progress(user_id, cal.get("profile_type", "B"), None, db))

    # Envoyer email récapitulatif au patient
    email_sent = False
    try:
        user_resp = await db.table("users").select("email,first_name").eq("id", user_id).maybe_single().execute()
        if user_resp.data:
            from app.services.email_service import send_calibration_email
            _asyncio.create_task(send_calibration_email(
                to_email   = user_resp.data["email"],
                first_name = user_resp.data.get("first_name", ""),
                profile    = cal,
            ))
            email_sent = True
    except Exception as e:
        logger.warning("Email calibration non envoyé : %s", e)

    return {"status": "ok", "profile": cal, "email_sent": email_sent}


# ════════════════════════════════════════════════════════════════════
# PUT /api/protocol/palier (thérapeute)
# ════════════════════════════════════════════════════════════════════

@router.put("/palier")
async def update_palier(
    body:    PalierUpdatePayload,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Mise à jour manuelle du palier par le thérapeute."""
    if body.palier not in PALIER_ORDER:
        raise HTTPException(400, f"Palier invalide. Valeurs acceptées : {PALIER_ORDER}")

    await db.table("eeg_profiles").update({"palier": body.palier}).eq("user_id", body.user_id).execute()
    return {"status": "ok", "palier": body.palier}


# ════════════════════════════════════════════════════════════════════
# POST /api/protocol/daily-threshold
# ════════════════════════════════════════════════════════════════════

@router.post("/daily-threshold")
async def compute_daily_thr(
    body:    DailyThresholdPayload,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Calcule le seuil du jour à partir de la mesure de repos."""
    profile = await _get_profile(db, user_id)
    ref     = profile.get("p_alpha_ref") or body.p_alpha_today

    daily_thr = compute_daily_threshold(ref, body.p_alpha_today)
    await _upsert_profile(db, user_id, {"threshold_current": daily_thr})

    return {"threshold_today": daily_thr, "p_alpha_ref_global": ref}


# ════════════════════════════════════════════════════════════════════
# GET /api/protocol/progress  — Progression calendaire complète
# ════════════════════════════════════════════════════════════════════

@router.get("/progress")
async def get_progress(
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """
    Retourne la progression calendaire complète (user_protocol_progress).
    Inclut : profil cognitif, calendrier prévisionnel, bilans, critères d'arrêt.
    """
    progress = await get_user_progress(user_id, db)
    if not progress:
        return {
            "user_id":       user_id,
            "status":        "not_started",
            "current_phase": "not_started",
            "total_sessions_completed": 0,
            "planned_session_dates": [],
        }

    profile = progress.get("cognitive_profile") or "B"
    structure = PROTOCOL_STRUCTURE.get(profile, PROTOCOL_STRUCTURE["B"])
    total_target = structure["total"]
    pct = round(progress.get("total_sessions_completed", 0) / total_target * 100, 1)

    return {
        **progress,
        "progress_percent": pct,
        "total_target_sessions": total_target,
    }


# ════════════════════════════════════════════════════════════════════
# GET /api/protocol/progress/therapist  — Dashboard thérapeute
# ════════════════════════════════════════════════════════════════════

@router.get("/progress/therapist")
async def get_therapist_progress(
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """
    Dashboard thérapeute : progression de tous les patients assignés.
    Retourne la vue v_user_protocol_summary pour chaque patient.
    """
    rows = await get_therapist_progress_dashboard(user_id, db)
    return {"patients": rows, "count": len(rows)}


# ════════════════════════════════════════════════════════════════════
# POST /api/protocol/early-stop  — Arrêt anticipé manuel
# ════════════════════════════════════════════════════════════════════

class EarlyStopPayload(BaseModel):
    reason: str = "user_request"
    notes:  Optional[str] = None

@router.post("/early-stop")
async def manual_early_stop(
    body:    EarlyStopPayload,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Marque le programme comme arrêté anticipativement."""
    sessions = await _get_protocol_sessions(db, user_id)
    completed = [s for s in sessions if s["status"] == "completed"]
    now = datetime.utcnow().isoformat()

    await (
        db.table("user_protocol_progress")
        .update({
            "status":             "early_stopped",
            "early_stop_reason":  body.reason,
            "early_stop_session": len(completed),
            "early_stop_date":    now,
            "updated_at":         now,
        })
        .eq("user_id", user_id)
        .execute()
    )
    return {"status": "ok", "early_stop_reason": body.reason}


# ════════════════════════════════════════════════════════════════════
# POST /api/protocol/followup-schedule — Planifier S16
# ════════════════════════════════════════════════════════════════════

class FollowupPayload(BaseModel):
    planned_date: Optional[str] = None  # ISO date

@router.post("/followup-schedule")
async def schedule_followup(
    body:    FollowupPayload,
    user_id: str = Depends(get_token_user_id),
    db       = Depends(get_db),
):
    """Planifie la séance de suivi S16 (1 semaine après S15 par défaut)."""
    from datetime import date as _date, timedelta as _td
    planned = body.planned_date or (_date.today() + _td(days=7)).isoformat()
    now = datetime.utcnow().isoformat()

    await (
        db.table("user_protocol_progress")
        .update({"updated_at": now})
        .eq("user_id", user_id)
        .execute()
    )

    # Mettre à jour la date planifiée dans planned_session_dates
    progress = await get_user_progress(user_id, db)
    if progress:
        planned_dates = progress.get("planned_session_dates") or []
        for item in planned_dates:
            if item.get("session_num") == 16:
                item["planned_date"] = planned
        await (
            db.table("user_protocol_progress")
            .update({"planned_session_dates": planned_dates, "updated_at": now})
            .eq("user_id", user_id)
            .execute()
        )

    return {"status": "ok", "followup_planned_date": planned}
