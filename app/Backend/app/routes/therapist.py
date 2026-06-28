"""
NeuroCap — Routes Thérapeute
GET    /api/therapist/patients                         → Liste des patients assignés (enrichie)
GET    /api/therapist/patients/{id}                    → Détail d'un patient
GET    /api/therapist/patients/{id}/sessions           → Historique sessions
GET    /api/therapist/patients/{id}/profile            → Profil EEG (lecture seule)
GET    /api/therapist/patients/{id}/notes              → Notes cliniques
POST   /api/therapist/patients/{id}/notes              → Ajouter une note
GET    /api/therapist/patients/{id}/export             → Export CSV sessions
GET    /api/therapist/patients/{id}/recommendation     → Recommandation active
POST   /api/therapist/patients/{id}/recommendation     → Créer / mettre à jour recommandation
PUT    /api/therapist/patients/{id}/palier             → Ajuster le palier EEG
PATCH  /api/therapist/patients/{id}/active             → Activer / désactiver le compte

Nécessite role='therapist' ou 'admin'.
"""

import csv
import io
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_therapist_user
from app.schemas import (
    PatientSummary, TherapistNoteCreate, TherapistNoteOut,
    TherapistRecommendationCreate, TherapistRecommendationOut,
    PalierAdjust, SessionResponse, EEGProfileOut,
)
from app.schemas.media_reco import TherapeuticPlaylistRequest, PlaylistWithMedia
from app.services.media_recommendation import (
    get_profile_categories,
    score_media,
    get_liked_media_ids,
    PALIER_MAX_DURATION,
    CALMING_CATEGORIES,
)
from app.services.session_media_bridge import get_patient_eeg_profile

router = APIRouter(prefix="/api/therapist", tags=["Thérapeute"])

PALIER_MAP = {
    "P1": "P1_INITIATION", "P2": "P2_APPRENTISSAGE",
    "P3": "P3_MAITRISE", "P4": "P4_AUTONOMIE",
}


def _normalize_palier(p: Optional[str]) -> Optional[str]:
    if not p:
        return None
    return PALIER_MAP.get(p, p)


async def _check_assignment(patient_id: str, therapist: dict, db: AsyncClient) -> dict:
    """Vérifie que le patient existe et est assigné à ce thérapeute (admin bypasse)."""
    p_resp = await (
        db.table("users")
        .select("id,email,username,first_name,last_name,is_active,therapist_id,created_at,role")
        .eq("id", patient_id)
        .execute()
    )
    patient = p_resp.data[0] if p_resp.data else None
    if not patient:
        raise HTTPException(status_code=404, detail="Patient introuvable")
    if therapist["role"] != "admin" and patient.get("therapist_id") != therapist["id"]:
        raise HTTPException(status_code=403, detail="Ce patient ne vous est pas assigné")
    return patient


async def _enrich_patient(patient: dict, db: AsyncClient) -> dict:
    """Ajoute les métriques de sessions + profil EEG à un dict patient."""
    patient_id = patient["id"]

    # Lire depuis feedback_sessions (nouveau système neurofeedback)
    fb_resp = await (
        db.table("feedback_sessions")
        .select("id,score,started_at,completed_at,status,objective")
        .eq("patient_id", patient_id)
        .eq("status", "completed")
        .order("completed_at", desc=True)
        .execute()
    )
    all_sessions = fb_resp.data or []

    # Normaliser le champ date (feedback_sessions utilise completed_at, sessions utilise created_at)
    for s in all_sessions:
        s.setdefault("created_at", s.get("completed_at") or s.get("started_at"))

    # Fallback 1 : ancienne table sessions si feedback_sessions vide
    if not all_sessions:
        old_resp = await (
            db.table("sessions")
            .select("id,score,created_at,status,objective")
            .eq("user_id", patient_id)
            .eq("status", "completed")
            .order("created_at", desc=True)
            .execute()
        )
        all_sessions = old_resp.data or []

    # Fallback 2 : eeg_reports (analyses fichiers EEG) si toujours vide
    if not all_sessions:
        rpt_resp = await (
            db.table("eeg_reports")
            .select("id,concentration_pct,stress_pct,created_at")
            .eq("patient_id", patient_id)
            .order("created_at", desc=True)
            .execute()
        )
        for r in (rpt_resp.data or []):
            c = r.get("concentration_pct")
            s = r.get("stress_pct")
            if c is not None or s is not None:
                vals = [v for v in [c, s] if v is not None]
                all_sessions.append({
                    "score": round(sum(vals) / len(vals), 1),
                    "created_at": r["created_at"],
                    "status": "completed",
                    "objective": "Analyse fichier EEG",
                })

    last_session_date = None
    last_session_objective = None
    last_session_score = None
    avg_score_all = None
    avg_score_last5 = None
    score_trend = None
    evolution_pct = None

    if all_sessions:
        last = all_sessions[0]
        last_session_date = datetime.fromisoformat(last["created_at"])
        last_session_objective = last.get("objective")
        last_session_score = last.get("score")

        all_scores = [s["score"] for s in all_sessions if s.get("score") is not None]
        if all_scores:
            avg_score_all = round(sum(all_scores) / len(all_scores), 1)

        last5_scores = [s["score"] for s in all_sessions[:5] if s.get("score") is not None]
        if last5_scores:
            avg_score_last5 = round(sum(last5_scores) / len(last5_scores), 1)

        # Tendance : moyenne des 2 dernières vs les autres
        if len(all_scores) >= 2:
            recent = sum(all_scores[:2]) / 2
            older = sum(all_scores[2:]) / max(1, len(all_scores[2:]))
            if older:
                score_trend = round((recent - older) / older * 100, 1)

        # Évolution absolue : première session vs dernière
        if len(all_scores) >= 2:
            first_score = all_scores[-1]
            last_score = all_scores[0]
            if first_score:
                evolution_pct = round((last_score - first_score) / first_score * 100, 1)

    # Profil EEG
    prof_resp = await (
        db.table("eeg_profiles")
        .select("palier,profile_type")
        .eq("user_id", patient_id)
        .execute()
    )
    eeg = prof_resp.data[0] if prof_resp.data else {}

    return {
        **patient,
        "session_count": len(all_sessions),
        "last_session_date": last_session_date,
        "last_session_objective": last_session_objective,
        "last_session_score": last_session_score,
        "avg_score_last5": avg_score_last5,
        "avg_score_all": avg_score_all,
        "score_trend": score_trend,
        "evolution_pct": evolution_pct,
        "palier": _normalize_palier(eeg.get("palier")),
        "profile_type": eeg.get("profile_type"),
    }


# ── List patients ─────────────────────────────────────────────────────────────

@router.get("/patients", response_model=List[PatientSummary])
async def list_patients(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    resp = await (
        db.table("users")
        .select("id,email,username,first_name,last_name,is_active,therapist_id,created_at,role")
        .eq("therapist_id", therapist["id"])
        .in_("role", ["patient", "user"])
        .range(offset, offset + limit - 1)
        .execute()
    )
    patients = resp.data or []
    result = []
    for p in patients:
        result.append(await _enrich_patient(p, db))
    return result


# ── Single patient ─────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}", response_model=PatientSummary)
async def get_patient(
    patient_id: str,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    patient = await _check_assignment(patient_id, therapist, db)
    return await _enrich_patient(patient, db)


# ── Sessions ──────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/sessions", response_model=List[SessionResponse])
async def patient_sessions(
    patient_id: str,
    limit: int = Query(50, ge=1, le=200),
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    await _check_assignment(patient_id, therapist, db)
    resp = await (
        db.table("sessions")
        .select("*")
        .eq("user_id", patient_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return resp.data or []


# ── EEG profile ───────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/profile", response_model=EEGProfileOut)
async def get_patient_profile(
    patient_id: str,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    await _check_assignment(patient_id, therapist, db)
    prof_resp = await db.table("eeg_profiles").select("*").eq("user_id", patient_id).execute()
    if not prof_resp.data:
        raise HTTPException(status_code=404, detail="Profil EEG non trouvé")
    return prof_resp.data[0]


# ── Notes ─────────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/notes", response_model=List[TherapistNoteOut])
async def get_notes(
    patient_id: str,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    await _check_assignment(patient_id, therapist, db)
    resp = await (
        db.table("therapist_notes")
        .select("*")
        .eq("therapist_id", therapist["id"])
        .eq("patient_id", patient_id)
        .order("created_at", desc=True)
        .execute()
    )
    return resp.data or []


@router.post("/patients/{patient_id}/notes", response_model=TherapistNoteOut, status_code=201)
async def add_note(
    patient_id: str,
    body: TherapistNoteCreate,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    await _check_assignment(patient_id, therapist, db)
    now = datetime.now(timezone.utc).isoformat()
    note = {
        "id": str(uuid.uuid4()),
        "therapist_id": therapist["id"],
        "patient_id": patient_id,
        "content": body.content,
        "created_at": now,
        "updated_at": now,
    }
    resp = await db.table("therapist_notes").insert(note).execute()
    return resp.data[0]


# ── Recommendation ────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/recommendation", response_model=Optional[TherapistRecommendationOut])
async def get_recommendation(
    patient_id: str,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    """Retourne la recommandation active la plus récente pour ce patient."""
    await _check_assignment(patient_id, therapist, db)
    try:
        resp = await (
            db.table("therapist_recommendations")
            .select("*")
            .eq("patient_id", patient_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return resp.data[0] if resp.data else None
    except Exception:
        return None


@router.post("/patients/{patient_id}/recommendation", response_model=TherapistRecommendationOut, status_code=201)
async def set_recommendation(
    patient_id: str,
    body: TherapistRecommendationCreate,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    """Crée une nouvelle recommandation (objectif, rythme, message) pour le patient."""
    await _check_assignment(patient_id, therapist, db)
    now = datetime.now(timezone.utc).isoformat()
    rec = {
        "id": str(uuid.uuid4()),
        "therapist_id": therapist["id"],
        "patient_id": patient_id,
        "recommended_objective": body.recommended_objective,
        "weekly_sessions_target": body.weekly_sessions_target,
        "message": body.message,
        "created_at": now,
    }
    try:
        resp = await db.table("therapist_recommendations").insert(rec).execute()
        return resp.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur DB : {e}")


# ── Adjust palier ─────────────────────────────────────────────────────────────

@router.put("/patients/{patient_id}/palier", status_code=204)
async def adjust_palier(
    patient_id: str,
    body: PalierAdjust,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    """Ajuste manuellement le palier EEG du patient (P1–P4)."""
    await _check_assignment(patient_id, therapist, db)
    normalized = _normalize_palier(body.palier)
    # Upsert dans eeg_profiles
    prof_resp = await db.table("eeg_profiles").select("id").eq("user_id", patient_id).execute()
    if prof_resp.data:
        await (
            db.table("eeg_profiles")
            .update({"palier": normalized})
            .eq("user_id", patient_id)
            .execute()
        )
    else:
        await (
            db.table("eeg_profiles")
            .insert({
                "id": str(uuid.uuid4()),
                "user_id": patient_id,
                "palier": normalized,
                "created_at": datetime.now(timezone.utc).isoformat(),
            })
            .execute()
        )
    return Response(status_code=204)


# ── Toggle active ─────────────────────────────────────────────────────────────

@router.patch("/patients/{patient_id}/active", status_code=204)
async def toggle_active(
    patient_id: str,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    """Bascule l'état actif/inactif du compte patient."""
    patient = await _check_assignment(patient_id, therapist, db)
    new_state = not patient.get("is_active", True)
    await (
        db.table("users")
        .update({"is_active": new_state, "updated_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", patient_id)
        .execute()
    )
    return Response(status_code=204)


# ── EEG Reports ──────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/eeg-reports")
async def get_patient_eeg_reports(
    patient_id: str,
    limit: int = Query(50, ge=1, le=200),
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    """Retourne les rapports EEG (live + fichier) envoyés par ce patient."""
    await _check_assignment(patient_id, therapist, db)
    try:
        resp = await (
            db.table("eeg_reports")
            .select("*")
            .eq("patient_id", patient_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or []
    except Exception:
        return []


# ── Export CSV ────────────────────────────────────────────────────────────────

@router.get("/patients/{patient_id}/export")
async def export_patient_csv(
    patient_id: str,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    patient = await _check_assignment(patient_id, therapist, db)
    sessions_resp = await (
        db.table("sessions")
        .select("*")
        .eq("user_id", patient_id)
        .order("created_at", desc=False)
        .execute()
    )
    sessions = sessions_resp.data or []

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "session_num", "date", "objective", "feedback_mode", "status",
        "duration_sec", "score", "avg_concentration", "avg_stress", "avg_tbr",
        "n_blocks", "n_epochs", "recommendations",
    ])
    for i, s in enumerate(sessions, 1):
        writer.writerow([
            i, s.get("created_at", ""), s.get("objective", ""),
            s.get("feedback_mode", ""), s.get("status", ""),
            s.get("duration_seconds", ""), s.get("score", ""),
            s.get("avg_concentration", ""), s.get("avg_stress", ""),
            s.get("avg_tbr", ""), s.get("n_blocks", ""),
            s.get("n_epochs_total", ""),
            (s.get("recommendations") or "").replace("\n", " "),
        ])

    output.seek(0)
    name = (patient.get("first_name") or patient.get("email", "patient")).replace(" ", "_")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=neurocap_{name}.csv"},
    )


# ── Playlist thérapeutique ─────────────────────────────────────────────────────

@router.post(
    "/patients/{patient_id}/therapeutic-playlist",
    response_model=PlaylistWithMedia,
    status_code=201,
)
async def create_therapeutic_playlist(
    patient_id: str,
    body: TherapeuticPlaylistRequest,
    therapist=Depends(get_therapist_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Crée automatiquement une playlist thérapeutique pour un patient.

    Logique :
    1. Lire therapist_recommendations (objectif, rythme) pour ce patient
    2. Lire eeg_profiles (profile_type, palier)
    3. Filtrer les médias alignés avec l'objectif, le profil et les préférences
    4. Prioriser les médias bien notés (liked = True ou sam_score >= 4)
    5. Créer la playlist + insérer les items dans playlist_media
    """
    patient = await _check_assignment(patient_id, therapist, db)

    # Récupérer la dernière recommandation du thérapeute
    rec_resp = await (
        db.table("therapist_recommendations")
        .select("recommended_objective,weekly_target,notes")
        .eq("patient_id", patient_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    therapist_rec = rec_resp.data[0] if rec_resp.data else {}
    objective = body.recommended_objective or therapist_rec.get("recommended_objective") or "relaxation"

    # Profil EEG
    profile_type, palier = await get_patient_eeg_profile(patient_id, db)

    # Médias bien notés par le patient
    liked_ids = await get_liked_media_ids(patient_id, db)

    # Charger tous les médias
    medias_resp = await db.table("medias").select("*").execute()
    all_medias: list[dict] = medias_resp.data or []

    # Mapper objectif thérapeutique → catégories cibles
    OBJECTIVE_CATEGORIES = {
        "concentration": ["focus", "rhythmic", "energetic", "stimulating"],
        "relaxation":    ["nature", "binaural", "meditation", "calming", "ambient"],
        "stress":        ["nature", "binaural", "calming", "meditation", "relaxation"],
    }
    target_cats = OBJECTIVE_CATEGORIES.get(objective, get_profile_categories(profile_type))

    # Déterminer l'état EEG cible selon l'objectif
    eeg_state_for_obj = {
        "concentration": "focus",
        "relaxation":    "neutral",
        "stress":        "stress",
    }.get(objective, "neutral")

    # Filtrer et scorer les médias
    pool = [
        m for m in all_medias
        if (m.get("category") or "").lower() in target_cats
    ]
    if not pool:
        pool = all_medias

    scored = [
        (m, score_media(m, profile_type, eeg_state_for_obj, palier, liked_ids))
        for m in pool
    ]
    # Trier : likés en tête, puis par score
    scored.sort(key=lambda x: (str(x[0].get("id", "")) in liked_ids, x[1]), reverse=True)

    # Sélectionner max 20 médias pour la playlist
    playlist_items = [m for m, s in scored[:20] if s > 0]

    now = datetime.now(timezone.utc).isoformat()
    playlist_id = str(uuid.uuid4())

    # Créer la playlist
    pl = {
        "id":               playlist_id,
        "user_id":          patient_id,
        "name":             body.name,
        "description":      body.description or f"Playlist thérapeutique — objectif {objective}",
        "created_by_role":  "therapist",
        "is_therapeutic":   True,
        "created_at":       now,
        "updated_at":       now,
    }
    pl_resp = await db.table("playlists").insert(pl).execute()

    # Insérer les médias dans playlist_media (alternance focus/relax si possible)
    focus_items  = [m for m in playlist_items if (m.get("category") or "").lower() in ("focus", "rhythmic", "energetic")]
    relax_items  = [m for m in playlist_items if (m.get("category") or "").lower() in CALMING_CATEGORIES]
    other_items  = [m for m in playlist_items if m not in focus_items and m not in relax_items]

    # Alterner focus / relax / autres
    ordered: list[dict] = []
    fi, ri, oi = 0, 0, 0
    while fi < len(focus_items) or ri < len(relax_items) or oi < len(other_items):
        if fi < len(focus_items):
            ordered.append(focus_items[fi]); fi += 1
        if ri < len(relax_items):
            ordered.append(relax_items[ri]); ri += 1
        if oi < len(other_items):
            ordered.append(other_items[oi]); oi += 1

    for pos, media in enumerate(ordered[:20], start=1):
        try:
            await db.table("playlist_media").insert({
                "playlist_id": playlist_id,
                "media_id":    str(media["id"]),
                "position":    pos,
                "added_at":    now,
            }).execute()
        except Exception as exc:
            import logging as _log
            _log.getLogger(__name__).warning("insert playlist_media: %s", exc)

    return PlaylistWithMedia(
        **(pl_resp.data[0] if pl_resp.data else pl),
        items=ordered[:20],
    )
