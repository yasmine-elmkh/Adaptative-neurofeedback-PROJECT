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

    # Toutes les sessions complétées (pour stats globales + évolution)
    all_sess_resp = await (
        db.table("sessions")
        .select("id,score,created_at,status,objective")
        .eq("user_id", patient_id)
        .eq("status", "completed")
        .order("created_at", desc=True)
        .execute()
    )
    all_sessions = all_sess_resp.data or []

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
