"""
NeuroCap — Routes Recommandation Média ↔ EEG

POST /api/sessions/{session_id}/media-recommendation    → reco live EEG
POST /api/sessions/{session_id}/media-feedback          → feedback post-session
POST /api/eeg-reports/{report_id}/generate-media-recommendations → reco offline
POST /api/finetuning/{job_id}/update-media-scoring      → recalcul post fine-tuning
GET  /api/patients/{patient_id}/dashboard               → tableau de bord unifié
POST /api/patients/{patient_id}/playlists               → créer playlist personnelle
GET  /api/patients/{patient_id}/playlists               → lister playlists
GET  /api/patients/{patient_id}/offline-recommendations/{report_id} → recos offline
PATCH /api/patients/{patient_id}/offline-recommendations/{rec_id}/feedback → like/dislike
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Path
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user, get_therapist_user
from app.schemas.media_reco import (
    SessionMediaRecommendRequest,
    SessionMediaFeedbackRequest,
    TherapeuticPlaylistRequest,
    PlaylistCreate,
    PlaylistOut,
    PlaylistWithMedia,
    RecommendationsMediaOut,
    OfflineRecommendationOut,
    OfflineRecommendationFeedback,
    PatientDashboard,
    SessionWithMediaSummary,
    EEGReportSummary,
)
from app.services.media_recommendation import (
    generate_live_recommendations,
    update_user_preferences,
    recalculate_scores_after_finetuning,
    purge_expired_recommendations,
    CALMING_CATEGORIES,
    PALIER_MAX_DURATION,
    get_profile_categories,
)
from app.services.session_media_bridge import (
    get_session_eeg_state,
    check_consecutive_stress_blocks,
    get_patient_eeg_profile,
    mark_recommendation_clicked,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Recommandation Média"])


# ── Helper : vérification accès patient ──────────────────────────────────────

async def _check_patient_access(patient_id: str, current_user: dict, db: AsyncClient) -> dict:
    """Vérifie que l'utilisateur peut accéder aux données du patient."""
    role = current_user.get("role", "patient")

    if role == "admin":
        pass
    elif role == "therapist":
        resp = await db.table("users").select("therapist_id").eq("id", patient_id).limit(1).execute()
        if not resp.data or resp.data[0].get("therapist_id") != current_user["id"]:
            raise HTTPException(status_code=403, detail="Patient non assigné")
    else:
        if patient_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Accès non autorisé")

    resp = await db.table("users").select("*").eq("id", patient_id).limit(1).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    return resp.data[0]


# ── A. Recommandation média live (session EEG temps réel) ────────────────────

@router.post("/api/sessions/{session_id}/media-recommendation")
async def session_media_recommendation(
    session_id: str,
    body: SessionMediaRecommendRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Retourne le top-5 des médias recommandés selon l'état EEG de la session.

    Logique :
    1. Calcule l'état EEG (stress/focus/neutral) depuis les 30 derniers events
    2. Vérifie si stress prolongé (3+ blocs > 0.7) → priorité calming
    3. Charge le profil EEG (profile_type, palier)
    4. Génère et sauvegarde les recommandations
    """
    user_id = current_user["id"]

    # Vérifier que la session appartient à l'utilisateur (ou admin/thérapeute)
    sess_resp = await db.table("sessions").select("user_id").eq("id", session_id).limit(1).execute()
    if not sess_resp.data:
        # Essayer feedback_sessions
        sess_resp = await db.table("feedback_sessions").select("patient_id").eq("id", session_id).limit(1).execute()
        if not sess_resp.data:
            raise HTTPException(status_code=404, detail="Session introuvable")
        owner_id = sess_resp.data[0].get("patient_id")
    else:
        owner_id = sess_resp.data[0].get("user_id")

    role = current_user.get("role", "patient")
    if role not in ("admin", "therapist") and owner_id != user_id:
        raise HTTPException(status_code=403, detail="Session non autorisée")

    target_user_id = owner_id or user_id

    # État EEG courant
    eeg_state, avg_conc, avg_stress = await get_session_eeg_state(session_id, db)

    # Détection stress prolongé
    calming = body.force_calming or await check_consecutive_stress_blocks(session_id, db)

    # Profil EEG
    profile_type, palier = await get_patient_eeg_profile(target_user_id, db)

    # Génération recommandations
    top_medias = await generate_live_recommendations(
        user_id=target_user_id,
        session_id=session_id,
        eeg_state=eeg_state,
        profile_type=profile_type,
        palier=palier,
        calming_priority=calming,
        db=db,
        top_n=5,
    )

    return {
        "session_id": session_id,
        "eeg_state": eeg_state,
        "avg_concentration": avg_conc,
        "avg_stress": avg_stress,
        "calming_priority": calming,
        "profile_type": profile_type,
        "palier": palier,
        "block_number": body.current_block_number,
        "recommendations": top_medias,
    }


# ── B. Feedback post-session média ────────────────────────────────────────────

@router.post("/api/sessions/{session_id}/media-feedback")
async def session_media_feedback(
    session_id: str,
    body: SessionMediaFeedbackRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Enregistre le feedback média post-session et met à jour les préférences.

    Pour chaque item :
    - Log dans media_interactions (table existante)
    - Si rating_value → mise à jour user_media_preferences
    - Si progress_percent > 50% → marquer is_clicked dans recommendations_media
    - Si interaction_type = complete ET progress_percent > 90 → déclencher update prefs
    """
    user_id = current_user["id"]
    now = datetime.now(timezone.utc).isoformat()
    processed = 0

    # media_interactions.session_id est UUID REFERENCES feedback_sessions(id).
    # Si le session_id vient de la table 'sessions' (TEXT), il n'est pas dans
    # feedback_sessions → on laisse NULL pour respecter la contrainte FK.
    feedback_session_id: Optional[str] = None
    try:
        fs = await db.table("feedback_sessions").select("id").eq("id", session_id).limit(1).execute()
        if fs.data:
            feedback_session_id = session_id
    except Exception:
        pass

    for item in body.items:
        media_resp = await db.table("medias").select("*").eq("id", item.media_id).limit(1).execute()
        if not media_resp.data:
            logger.warning("media_feedback: media %s introuvable", item.media_id)
            continue
        media = media_resp.data[0]

        # Log interaction dans la table existante
        try:
            await db.table("media_interactions").insert({
                "id":          str(uuid.uuid4()),
                "session_id":  feedback_session_id,  # NULL si session vient de 'sessions' (pas feedback_sessions)
                "patient_id":  user_id,
                "media_id":    item.media_id,
                "liked":       item.interaction_type == "like" or (item.rating_value or 0) >= 4,
                "sam_score":   int(item.rating_value) if item.rating_value else None,
                "was_skipped": item.interaction_type == "skip",
                "duration_played": item.duration_seconds,
                "efficace":    (item.progress_percent or 0) > 70,
                "created_at":  now,
            }).execute()
        except Exception as exc:
            logger.warning("insert media_interactions: %s", exc)

        # Mise à jour préférences si noté
        if item.rating_value:
            await update_user_preferences(user_id, media, item.rating_value, db)

        # Marquer recommendation cliquée si vue > 50%
        if (item.progress_percent or 0) > 50:
            await mark_recommendation_clicked(user_id, item.media_id, db)

        # Mise à jour auto si complete + > 90%
        if item.interaction_type == "complete" and (item.progress_percent or 0) > 90:
            if not item.rating_value:
                await update_user_preferences(user_id, media, 4.0, db)

        processed += 1

    return {"status": "ok", "processed": processed}


# ── C. Rapport EEG offline → recommandations ─────────────────────────────────

@router.post("/api/eeg-reports/{report_id}/generate-media-recommendations")
async def generate_offline_recommendations(
    report_id: str,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Génère des offline_recommendations pour chaque époque du rapport EEG.

    Logique :
    1. Lire eeg_reports (patient_id, dominant_state, epochs_json, filename)
    2. Pour chaque époque (ou représentant par état), choisir le meilleur média
    3. Insérer dans offline_recommendations
    4. Agréger par état EEG → insérer dans recommendations_media
    """
    # Charger le rapport
    rep_resp = await (
        db.table("eeg_reports")
        .select("*")
        .eq("id", report_id)
        .limit(1)
        .execute()
    )
    if not rep_resp.data:
        raise HTTPException(status_code=404, detail="Rapport EEG introuvable")

    report = rep_resp.data[0]
    patient_id = report["patient_id"]

    # Contrôle accès
    role = current_user.get("role", "patient")
    if role not in ("admin", "therapist") and patient_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")

    # Profil EEG du patient
    profile_type, palier = await get_patient_eeg_profile(patient_id, db)

    # Charger les médias
    medias_resp = await db.table("medias").select("*").execute()
    all_medias: list[dict] = medias_resp.data or []

    filename = report.get("filename") or f"report_{report_id}"
    epochs_json: list[dict] = report.get("epochs_json") or []

    # Déterminer l'état par époque depuis epochs_json
    # Format attendu : [{"epoch_idx": 0, "state": "focus", "confidence": 0.9, ...}, ...]
    # Si pas d'epochs_json, on construit 3 epochs représentatifs depuis dominant_state

    if not epochs_json:
        dominant = report.get("dominant_state") or "neutral"
        epochs_json = [{"epoch_idx": 0, "state": dominant, "confidence": 1.0}]

    # Médias déjà likés (bonus)
    from app.services.media_recommendation import get_liked_media_ids, score_media
    liked_ids = await get_liked_media_ids(patient_id, db)

    inserted = 0
    state_best: dict[str, tuple] = {}  # eeg_state → (media, score)
    now = datetime.now(timezone.utc).isoformat()

    # Limite : 10MB max → échantillonner si trop d'époques
    sample = epochs_json if len(epochs_json) <= 100 else epochs_json[::max(1, len(epochs_json)//100)]

    for ep in sample:
        epoch_idx = ep.get("epoch_idx", 0)
        raw_state = ep.get("state") or ep.get("ml_prediction", {}).get("state") or "neutral"

        # Mapper concentration/stress → stress/focus/neutral
        if raw_state in ("concentration",):
            eeg_state = "focus"
        elif raw_state in ("stress",):
            eeg_state = "stress"
        else:
            eeg_state = "neutral"

        # Scorer tous les médias pour cet état
        scored = [
            (m, score_media(m, profile_type, eeg_state, palier, liked_ids))
            for m in all_medias
        ]
        if not scored:
            continue
        best_media, best_score = max(scored, key=lambda x: x[1])

        if best_score <= 0:
            continue

        # Insérer dans offline_recommendations
        try:
            await db.table("offline_recommendations").insert({
                "id":         str(uuid.uuid4()),
                "user_id":    patient_id,
                "report_id":  report_id,
                "filename":   filename,
                "epoch_idx":  epoch_idx,
                "eeg_state":  eeg_state,
                "media_id":   str(best_media["id"]),
                "media_type": best_media.get("type", "audio"),
                "score":      round(best_score, 4),
                "created_at": now,
            }).execute()
            inserted += 1
        except Exception as exc:
            logger.warning("insert offline_recommendations: %s", exc)

        # Conserver le meilleur par état pour recommendations_media
        if eeg_state not in state_best or best_score > state_best[eeg_state][1]:
            state_best[eeg_state] = (best_media, best_score)

    # Agréger dans recommendations_media
    from datetime import timedelta
    expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    for eeg_state, (media, score) in state_best.items():
        try:
            await (
                db.table("recommendations_media")
                .upsert(
                    {
                        "id":           str(uuid.uuid4()),
                        "user_id":      patient_id,
                        "media_id":     str(media["id"]),
                        "score":        round(score, 4),
                        "reason":       f"generated_from_eeg_report_{report_id}|state={eeg_state}",
                        "generated_at": now,
                        "expires_at":   expires,
                        "is_clicked":   False,
                    },
                    on_conflict="user_id,media_id",
                )
                .execute()
            )
        except Exception as exc:
            logger.warning("upsert recommendations_media (offline): %s", exc)

    return {
        "report_id":   report_id,
        "patient_id":  patient_id,
        "epochs_processed": len(sample),
        "offline_inserted": inserted,
        "aggregated_by_state": {s: str(m["id"]) for s, (m, _) in state_best.items()},
    }


# ── D. Fine-tuning → mise à jour scoring média ───────────────────────────────

@router.post("/api/finetuning/{job_id}/update-media-scoring")
async def update_media_scoring_after_finetuning(
    job_id: str,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Après un fine-tuning réussi, recalcule les scores de recommandation du patient.

    Logique :
    1. Lire finetuning_jobs (patient_id, accuracy_after, model_version)
    2. Mettre à jour eeg_profiles (finetuned_version, last_20_sessions_accuracy)
    3. Recalculer les scores recommendations_media
    """
    role = current_user.get("role", "patient")
    if role not in ("admin", "therapist"):
        raise HTTPException(status_code=403, detail="Réservé aux thérapeutes / admin")

    job_resp = await (
        db.table("finetuning_jobs")
        .select("*")
        .eq("id", job_id)
        .limit(1)
        .execute()
    )
    if not job_resp.data:
        raise HTTPException(status_code=404, detail="Job de fine-tuning introuvable")

    job = job_resp.data[0]
    if job.get("status") != "done":
        raise HTTPException(status_code=400, detail="Fine-tuning non terminé")

    patient_id    = job["patient_id"]
    accuracy_after = float(job.get("accuracy_after") or 0.5)
    model_version  = job.get("model_version")

    # Mettre à jour eeg_profiles
    now = datetime.now(timezone.utc).isoformat()
    try:
        await (
            db.table("eeg_profiles")
            .update({
                "finetuned_version":         model_version,
                "last_20_sessions_accuracy": accuracy_after,
                "last_finetune_at":          now,
                "updated_at":                now,
            })
            .eq("user_id", patient_id)
            .execute()
        )
    except Exception as exc:
        logger.warning("update eeg_profiles after finetuning: %s", exc)

    # Recalculer les scores
    updated = await recalculate_scores_after_finetuning(patient_id, accuracy_after, db)

    return {
        "job_id":        job_id,
        "patient_id":    patient_id,
        "accuracy_after": accuracy_after,
        "model_version":  model_version,
        "recommendations_updated": updated,
    }


# ── E. Dashboard patient unifié ───────────────────────────────────────────────

@router.get("/api/patients/{patient_id}/dashboard", response_model=PatientDashboard)
async def get_patient_dashboard(
    patient_id: str,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Vue unifiée d'un patient :
    sessions récentes + profil EEG + recommandations + playlists + rapports EEG.
    """
    patient = await _check_patient_access(patient_id, current_user, db)

    # Profil EEG
    prof_resp = await (
        db.table("eeg_profiles").select("*").eq("user_id", patient_id).limit(1).execute()
    )
    profile = prof_resp.data[0] if prof_resp.data else {}

    # Sessions récentes (10 dernières)
    sess_resp = await (
        db.table("sessions")
        .select("id,objective,status,score,avg_concentration,avg_stress,created_at")
        .eq("user_id", patient_id)
        .order("created_at", desc=True)
        .limit(10)
        .execute()
    )
    sessions_raw = sess_resp.data or []

    recent_sessions = []
    for s in sessions_raw:
        # Compter les interactions média par session
        try:
            mi_resp = await (
                db.table("media_interactions")
                .select("id")
                .eq("session_id", s["id"])
                .execute()
            )
            media_count = len(mi_resp.data or [])
        except Exception:
            media_count = 0

        recent_sessions.append(SessionWithMediaSummary(
            id=s["id"],
            objective=s.get("objective", ""),
            status=s.get("status", ""),
            score=s.get("score"),
            avg_concentration=s.get("avg_concentration"),
            avg_stress=s.get("avg_stress"),
            created_at=s["created_at"],
            media_count=media_count,
        ))

    # Score moyen global
    all_scores = [s.get("score") for s in sessions_raw if s.get("score") is not None]
    avg_score = round(sum(all_scores) / len(all_scores), 1) if all_scores else None

    # Recommandations en attente (non cliquées)
    recs_resp = await (
        db.table("recommendations_media")
        .select("*")
        .eq("user_id", patient_id)
        .eq("is_clicked", False)
        .order("score", desc=True)
        .limit(10)
        .execute()
    )
    pending_recs = [RecommendationsMediaOut(**r) for r in (recs_resp.data or [])]

    # Playlists
    pl_resp = await (
        db.table("playlists")
        .select("*")
        .eq("user_id", patient_id)
        .order("created_at", desc=True)
        .execute()
    )
    playlists = [PlaylistOut(**p) for p in (pl_resp.data or [])]

    # Rapports EEG récents (5 derniers)
    rep_resp = await (
        db.table("eeg_reports")
        .select("id,source,filename,dominant_state,concentration_pct,stress_pct,n_epochs,created_at")
        .eq("patient_id", patient_id)
        .order("created_at", desc=True)
        .limit(5)
        .execute()
    )
    eeg_reports = []
    for r in (rep_resp.data or []):
        try:
            off_resp = await (
                db.table("offline_recommendations")
                .select("id")
                .eq("report_id", r["id"])
                .execute()
            )
            off_count = len(off_resp.data or [])
        except Exception:
            off_count = 0

        eeg_reports.append(EEGReportSummary(
            id=r["id"],
            source=r.get("source"),
            filename=r.get("filename"),
            dominant_state=r.get("dominant_state"),
            concentration_pct=r.get("concentration_pct"),
            stress_pct=r.get("stress_pct"),
            n_epochs=r.get("n_epochs") or 0,
            created_at=r["created_at"],
            offline_recommendations_count=off_count,
        ))

    # Statut fine-tuning
    ft_resp = await (
        db.table("finetuning_jobs")
        .select("status")
        .eq("patient_id", patient_id)
        .order("started_at", desc=True)
        .limit(1)
        .execute()
    )
    ft_status = ft_resp.data[0]["status"] if ft_resp.data else None

    palier = str(profile.get("palier") or "P1")
    if "_" in palier:
        palier = palier.split("_")[0]

    return PatientDashboard(
        user_id=patient_id,
        first_name=patient.get("first_name"),
        last_name=patient.get("last_name"),
        profile_type=profile.get("profile_type"),
        palier=palier,
        finetuned_version=profile.get("finetuned_version"),
        last_finetune_at=profile.get("last_finetune_at"),
        total_sessions=len(sessions_raw),
        avg_session_score=avg_score,
        recent_sessions=recent_sessions,
        pending_recommendations=pending_recs,
        playlists=playlists,
        recent_eeg_reports=eeg_reports,
        finetuning_status=ft_status,
    )


# ── F. Gestion des playlists patient ─────────────────────────────────────────

@router.post("/api/patients/{patient_id}/playlists", response_model=PlaylistOut, status_code=201)
async def create_patient_playlist(
    patient_id: str,
    body: PlaylistCreate,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Crée une playlist personnelle pour un patient."""
    await _check_patient_access(patient_id, current_user, db)
    now = datetime.now(timezone.utc).isoformat()
    pl = {
        "id":               str(uuid.uuid4()),
        "user_id":          patient_id,
        "name":             body.name,
        "description":      body.description,
        "created_by_role":  current_user.get("role", "patient"),
        "is_therapeutic":   False,
        "created_at":       now,
        "updated_at":       now,
    }
    resp = await db.table("playlists").insert(pl).execute()
    return resp.data[0]


@router.get("/api/patients/{patient_id}/playlists", response_model=List[PlaylistOut])
async def list_patient_playlists(
    patient_id: str,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Liste les playlists d'un patient."""
    await _check_patient_access(patient_id, current_user, db)
    resp = await (
        db.table("playlists")
        .select("*")
        .eq("user_id", patient_id)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


# ── G. Offline recommendations ────────────────────────────────────────────────

@router.get(
    "/api/patients/{patient_id}/offline-recommendations/{report_id}",
    response_model=List[OfflineRecommendationOut],
)
async def get_offline_recommendations(
    patient_id: str,
    report_id: str,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Retourne les offline_recommendations d'un rapport EEG."""
    await _check_patient_access(patient_id, current_user, db)
    resp = await (
        db.table("offline_recommendations")
        .select("*")
        .eq("user_id", patient_id)
        .eq("report_id", report_id)
        .order("epoch_idx")
        .execute()
    )
    return resp.data or []


@router.patch("/api/patients/{patient_id}/offline-recommendations/{rec_id}/feedback")
async def submit_offline_feedback(
    patient_id: str,
    rec_id: str,
    body: OfflineRecommendationFeedback,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Enregistre le like/dislike différé sur une offline_recommendation."""
    await _check_patient_access(patient_id, current_user, db)
    now = datetime.now(timezone.utc).isoformat()
    await (
        db.table("offline_recommendations")
        .update({"liked": body.liked, "feedback_at": now})
        .eq("id", rec_id)
        .eq("user_id", patient_id)
        .execute()
    )
    return {"status": "ok", "liked": body.liked}
