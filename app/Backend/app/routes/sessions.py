"""
NeuroCap — Routes Sessions
GET  /api/sessions           → Liste des sessions de l'utilisateur
POST /api/sessions           → Créer une session
GET  /api/sessions/{id}      → Détail d'une session
GET  /api/sessions/{id}/report → Rapport de session
GET  /api/sessions/{id}/export → Export CSV
"""

import csv
import io
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import SessionCreate, SessionResponse, SessionReport

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _get_session_or_404(session_id: str, user_id: str, db: AsyncClient) -> dict:
    """Récupère une session ou lève HTTP 404 si introuvable / appartient à un autre utilisateur."""
    resp = await db.table("sessions").select("*").eq("id", session_id).eq("user_id", user_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Session introuvable")
    return resp.data[0]


def _default_recommendations(score) -> str:
    """Recommandations par défaut si la session n'en a pas encore."""
    if score is None:
        return "Session en cours ou données insuffisantes."
    score = float(score)
    if score >= 70:
        return "Excellente session ! Continuez à ce rythme ou passez au palier suivant."
    if score >= 50:
        return "Bonne session. Votre cerveau s'adapte progressivement."
    if score >= 30:
        return "Session correcte. Essayez un environnement plus calme."
    return "Session difficile. Vérifiez le placement des électrodes et réessayez."


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Liste les sessions de l'utilisateur, triées par date décroissante."""
    resp = await (
        db.table("sessions")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return resp.data


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    data: SessionCreate,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Crée une nouvelle session en statut 'pending'."""
    objective    = data.objective    if data.objective    in ("concentration", "relaxation") else "concentration"
    feedback_mode = data.feedback_mode if data.feedback_mode in ("visual", "audio", "game")  else "visual"

    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    new_session = {
        "id": session_id,
        "user_id": current_user["id"],
        "objective": objective,
        "feedback_mode": feedback_mode,
        "status": "pending",
        "n_blocks": 0,
        "n_epochs_total": 0,
        "n_epochs_rejected": 0,
        "created_at": now,
    }
    resp = await db.table("sessions").insert(new_session).execute()

    # Audit
    await db.table("audit_logs").insert({
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "action": "SESSION_CREATE",
        "details": f"session={session_id} objective={objective} mode={feedback_mode}",
        "created_at": now,
    }).execute()

    return resp.data[0]


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Retourne le détail d'une session."""
    return await _get_session_or_404(session_id, current_user["id"], db)


@router.get("/{session_id}/report", response_model=SessionReport)
async def get_report(
    session_id: str,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Rapport complet d'une session :
    timelines de concentration/stress + recommandations.
    """
    session = await _get_session_or_404(session_id, current_user["id"], db)

    # Charger les événements de la session triés par timestamp
    resp = await (
        db.table("session_events")
        .select("concentration_rate,stress_rate")
        .eq("session_id", session_id)
        .order("timestamp")
        .execute()
    )
    events = resp.data

    conc_timeline    = [e["concentration_rate"] for e in events]
    stress_timeline  = [e["stress_rate"]        for e in events]
    threshold_timeline: list = []  # calculé en temps réel par le moteur adaptatif

    recs = session.get("recommendations") or _default_recommendations(session.get("score"))

    return SessionReport(
        session=session,
        events_count=len(events),
        concentration_timeline=conc_timeline,
        stress_timeline=stress_timeline,
        threshold_timeline=threshold_timeline,
        recommendations=recs,
    )


@router.get("/{session_id}/export")
async def export_csv(
    session_id: str,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Export CSV de tous les événements d'une session."""
    await _get_session_or_404(session_id, current_user["id"], db)

    resp = await (
        db.table("session_events")
        .select("*")
        .eq("session_id", session_id)
        .order("timestamp")
        .execute()
    )
    events = resp.data

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "timestamp", "concentration_rate", "stress_rate", "confidence",
        "tbr", "ei", "power_alpha", "power_beta", "power_theta",
        "signal_quality", "is_artifact", "block_number",
    ])
    for e in events:
        writer.writerow([
            e.get("timestamp", ""),
            e.get("concentration_rate"), e.get("stress_rate"), e.get("confidence"),
            e.get("tbr"), e.get("ei"),
            e.get("power_alpha"), e.get("power_beta"), e.get("power_theta"),
            e.get("signal_quality"), e.get("is_artifact"), e.get("block_number"),
        ])

    output.seek(0)
    filename = f"session_{session_id[:8]}.csv"

    # Audit
    await db.table("audit_logs").insert({
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "action": "DATA_EXPORT",
        "details": f"session={session_id} format=csv events={len(events)}",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/export/all")
async def export_all_sessions_csv(
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Export CSV de toutes les sessions de l'utilisateur (métriques agrégées)."""
    resp = await (
        db.table("sessions")
        .select("*")
        .eq("user_id", current_user["id"])
        .order("created_at")
        .execute()
    )
    sessions = resp.data or []

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "session_num", "date", "objective", "feedback_mode", "status",
        "duration_sec", "score", "avg_concentration", "avg_stress", "avg_tbr",
        "n_blocks", "n_epochs", "recommendations",
    ])
    for i, s in enumerate(sessions, 1):
        writer.writerow([
            i,
            s.get("created_at", ""),
            s.get("objective", ""),
            s.get("feedback_mode", ""),
            s.get("status", ""),
            s.get("duration_seconds", ""),
            s.get("score", ""),
            s.get("avg_concentration", ""),
            s.get("avg_stress", ""),
            s.get("avg_tbr", ""),
            s.get("n_blocks", ""),
            s.get("n_epochs_total", ""),
            (s.get("recommendations") or "").replace("\n", " "),
        ])

    output.seek(0)

    # Audit
    await db.table("audit_logs").insert({
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "action": "DATA_EXPORT_ALL",
        "details": f"sessions_count={len(sessions)} format=csv",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }).execute()

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=neurocap_sessions.csv"},
    )
