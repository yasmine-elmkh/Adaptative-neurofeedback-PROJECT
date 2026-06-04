"""
NeuroCap — Routes Sessions
GET  /api/sessions              → Liste des sessions de l'utilisateur
POST /api/sessions              → Créer une session
GET  /api/sessions/calendar     → Calendrier 15 séances (protocole)
GET  /api/sessions/{id}         → Détail d'une session
GET  /api/sessions/{id}/report  → Rapport de session
GET  /api/sessions/{id}/export  → Export CSV
"""

import csv
import io
import uuid
from datetime import datetime, date, timezone, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import SessionCreate, SessionResponse, SessionReport

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


# ── Constantes protocole ──────────────────────────────────────────────────────

# Délais minimum entre séances selon la phase (en jours)
_MIN_INTERVAL = {"phase1": 5, "phase2": 2, "phase3": 2}

# Sessions bilan obligatoires
_BILAN_SESSIONS = {5: "B1", 10: "B2", 15: "B3"}

# Phase par numéro de séance
def _phase(n: int) -> str:
    if n <= 3:   return "phase1"
    if n <= 10:  return "phase2"
    return "phase3"


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

@router.get("/calendar")
async def get_session_calendar(
    patient_id: Optional[str] = Query(None),
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Retourne le calendrier des 15 séances du protocole pour un patient.
    Lit en priorité feedback_sessions (nouveau système adaptatif),
    avec fallback sur sessions (ancienne table) si feedback_sessions est vide.
    """
    role = current_user.get("role", "patient")
    uid = patient_id if patient_id and role in ("therapist", "admin") else current_user["id"]

    existing = []

    # ── Lecture depuis feedback_sessions (nouveau système) ──────────
    try:
        resp = await (
            db.table("feedback_sessions")
            .select("id,session_number,phase,palier,status,score,started_at,completed_at,created_at")
            .eq("patient_id", uid)
            .order("session_number", desc=False)
            .execute()
        )
        raw = resp.data or []
        # Normaliser les champs pour le frontend (ended_at → completed_at)
        for s in raw:
            s.setdefault("bilan_type", _BILAN_SESSIONS.get(s.get("session_number")))
            s.setdefault("scheduled_date", None)
            s["ended_at"] = s.get("completed_at")
            if s.get("session_number") and s.get("phase") is None:
                s["phase"] = _phase(s["session_number"])
        existing = raw
    except Exception:
        pass

    # ── Fallback : ancienne table sessions (colonnes variables) ─────
    if not existing:
        try:
            resp2 = await (
                db.table("sessions")
                .select("id,session_number,phase,palier,status,score,created_at,started_at,ended_at")
                .eq("user_id", uid)
                .order("created_at", desc=False)
                .execute()
            )
            raw2 = resp2.data or []
            for i, s in enumerate(raw2, 1):
                s.setdefault("session_number", i)
                s.setdefault("phase", _phase(s["session_number"]))
                s.setdefault("bilan_type", _BILAN_SESSIONS.get(s["session_number"]))
                s.setdefault("scheduled_date", None)
                s.setdefault("palier", 1)
            existing = raw2
        except Exception:
            pass

    # ── Recalculer session_number si absent ──────────────────────────
    for i, s in enumerate(existing, 1):
        if not s.get("session_number"):
            s["session_number"] = i
        s["bilan_type"] = _BILAN_SESSIONS.get(s["session_number"])

    # ── Construire les 15 cases ───────────────────────────────────────
    # Only sessions explicitly marked completed count toward progress.
    completed_nums = {s["session_number"] for s in existing if s.get("status") == "completed"}
    existing_nums  = {s["session_number"] for s in existing}
    calendar = list(existing)

    last_completed = None
    for s in sorted(existing, key=lambda x: x.get("session_number") or 0, reverse=True):
        if s.get("status") in ("completed",):
            last_completed = s
            break

    def _next_date(last_date_str: Optional[str], ph: str) -> Optional[str]:
        if not last_date_str:
            return date.today().isoformat()
        try:
            last = datetime.fromisoformat(last_date_str.replace("Z", "+00:00")).date()
        except Exception:
            return None
        delta = _MIN_INTERVAL.get(ph, 2)
        return (last + timedelta(days=delta)).isoformat()

    last_date = (last_completed or {}).get("ended_at") or (last_completed or {}).get("completed_at") or (last_completed or {}).get("created_at")
    next_num = max(completed_nums, default=0) + 1

    for n in range(next_num, 16):
        if n in existing_nums:  # already in calendar (any status) — don't duplicate
            continue
        ph = _phase(n)
        next_d = _next_date(last_date, ph) if n == next_num else None
        calendar.append({
            "session_number": n,
            "phase": ph,
            "status": "upcoming" if n != next_num else "scheduled",
            "bilan_type": _BILAN_SESSIONS.get(n),
            "scheduled_date": next_d,
            "score": None,
            "palier": None,
        })
        if next_d:
            last_date = next_d

    calendar.sort(key=lambda x: x.get("session_number") or 0)

    return {
        "sessions": calendar[:16],
        "total_completed": len(completed_nums),
        "next_session_number": next_num,
    }


@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """Liste les sessions complétées depuis feedback_sessions (protocole adaptatif)."""
    resp = await (
        db.table("feedback_sessions")
        .select("id,patient_id,session_number,objective,status,score,started_at,completed_at,created_at")
        .eq("patient_id", current_user["id"])
        .eq("status", "completed")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
        .execute()
    )
    return [
        {
            "id":             s["id"],
            "user_id":        s.get("patient_id") or "",
            "session_number": s.get("session_number") or 0,
            "objective":      s.get("objective") or "concentration",
            "feedback_mode":  s.get("feedback_mode") or "visual",
            "status":         "completed",
            "session_score":  s.get("score"),
            "avg_tbr":        None,
            "success_rate":   None,
            "blocks_history": None,
            "created_at":     s["created_at"],
            "started_at":     s.get("started_at"),
            "completed_at":   s.get("completed_at"),
        }
        for s in (resp.data or [])
    ]


@router.post("", response_model=SessionResponse, status_code=201)
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
