"""
NeuroCap — Routes Administration
GET    /api/admin/stats                  → Statistiques globales (6 KPIs)
GET    /api/admin/users                  → Liste utilisateurs enrichie (stats sessions)
GET    /api/admin/users/{id}             → Détail utilisateur
POST   /api/admin/users                  → Créer un utilisateur
PUT    /api/admin/users/{id}             → Modifier rôle / statut / thérapeute
DELETE /api/admin/users/{id}             → Supprimer (soft delete)
GET    /api/admin/therapists             → Liste des thérapeutes (pour assignation)
POST   /api/admin/assign-patient         → Assigner/désassigner un patient
GET    /api/admin/settings               → Lire la configuration système
PUT    /api/admin/settings/{key}         → Modifier un paramètre système
GET    /api/admin/audit-logs             → Journal d'audit (filtrable)

Toutes ces routes nécessitent le rôle 'admin'.
"""

import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_admin_user, hash_password
from app.schemas import (
    AdminStats, UserOut, UserWithStats, AuditLogOut, UserRoleUpdate,
    UserCreateByAdmin, PatientAssign,
    SystemSettingOut, SystemSettingUpdate,
    EmailReminderRequest, EmailReminderAllRequest,
)
from app.services.email_service import send_reminder_email, EmailSendError

router = APIRouter(prefix="/api/admin", tags=["Administration"])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


async def _audit(db, admin_id: str, action: str, details: str = ""):
    try:
        await db.table("audit_logs").insert({
            "id": str(uuid.uuid4()),
            "user_id": admin_id,
            "action": action,
            "details": details,
            "created_at": _now(),
        }).execute()
    except Exception:
        pass  # audit is non-blocking


# ── Stats ─────────────────────────────────────────────────────────────────────

@router.get("/stats", response_model=AdminStats)
async def get_stats(
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """6 KPIs globaux — dashboard administrateur."""
    # ── Users ──────────────────────────────────────────────────────────────────
    try:
        all_users_resp = await db.table("users").select("id,role,is_active,deleted_at").execute()
        users_data = [u for u in (all_users_resp.data or []) if not u.get("deleted_at")]
    except Exception:
        # deleted_at column may not exist yet — fall back
        all_users_resp = await db.table("users").select("id,role,is_active").execute()
        users_data = all_users_resp.data or []
    total_users    = len(users_data)
    active_users   = sum(1 for u in users_data if u.get("is_active"))
    total_therapists = sum(1 for u in users_data if u.get("role") == "therapist")
    patient_ids    = {u["id"] for u in users_data if u.get("role") in ("patient", "user")}

    # ── Sessions ────────────────────────────────────────────────────────────────
    all_sess_resp  = await db.table("sessions").select("id,user_id,status,score,created_at,duration_seconds").execute()
    sessions_data  = all_sess_resp.data or []
    total_sessions = len(sessions_data)
    completed      = [s for s in sessions_data if s.get("status") == "completed"]

    # Sessions this month (30 days)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    sessions_this_month = sum(1 for s in sessions_data if (s.get("created_at") or "") >= cutoff)

    # Active patients: patients with ≥1 session
    session_user_ids = {s["user_id"] for s in sessions_data}
    active_patients  = len(patient_ids & session_user_ids)

    # Avg score + duration
    scores    = [s["score"] for s in completed if s.get("score") is not None]
    durations = [s["duration_seconds"] for s in completed if s.get("duration_seconds") is not None]

    # Engagement rate: users with ≥3 sessions / total users
    user_sess_counts = Counter(s["user_id"] for s in sessions_data)
    engaged = sum(1 for c in user_sess_counts.values() if c >= 3)
    engagement_rate = round(engaged / total_users * 100, 1) if total_users else 0.0

    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        total_therapists=total_therapists,
        active_patients=active_patients,
        total_sessions=total_sessions,
        completed_sessions=len(completed),
        sessions_this_month=sessions_this_month,
        avg_session_score=round(sum(scores) / len(scores), 1) if scores else None,
        avg_session_duration=round(sum(durations) / len(durations), 1) if durations else None,
        engagement_rate=engagement_rate,
    )


# ── List users (enriched with session stats) ──────────────────────────────────

@router.get("/users")  # No response_model — avoids Pydantic validation errors on null DB fields
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    role_filter: Optional[str] = Query(None, description="Filtrer par rôle"),
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Liste tous les utilisateurs enrichis de leurs statistiques de sessions."""
    try:
        query = db.table("users").select("*").order("created_at", desc=True)
        if role_filter:
            query = query.eq("role", role_filter)
        try:
            query = query.is_("deleted_at", "null")
            resp = await query.range(offset, offset + limit - 1).execute()
        except Exception:
            # deleted_at column may not exist
            query2 = db.table("users").select("*").order("created_at", desc=True)
            if role_filter:
                query2 = query2.eq("role", role_filter)
            resp = await query2.range(offset, offset + limit - 1).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur chargement utilisateurs: {str(e)}")

    users = resp.data or []
    if not users:
        return []

    # Fetch session stats in a single query
    user_ids = [u["id"] for u in users]
    try:
        sess_resp = await (
            db.table("sessions")
            .select("user_id,score,status,created_at")
            .in_("user_id", user_ids)
            .execute()
        )
        all_sessions = sess_resp.data or []
    except Exception:
        all_sessions = []

    user_sessions: dict = defaultdict(list)
    for s in all_sessions:
        user_sessions[s["user_id"]].append(s)

    result = []
    for u in users:
        uid  = u["id"]
        sess = user_sessions[uid]
        completed_scores = [s["score"] for s in sess if s.get("status") == "completed" and s.get("score") is not None]
        last_date = max((s["created_at"] for s in sess), default=None) if sess else None
        # Build a clean dict with fallbacks for every field — never raises Pydantic errors
        result.append({
            "id":                u.get("id", ""),
            "email":             u.get("email", ""),
            "username":          u.get("username") or (u.get("email", "")).split("@")[0],
            "first_name":        u.get("first_name") or "",
            "last_name":         u.get("last_name") or "",
            "role":              u.get("role") or "patient",
            "therapist_id":      u.get("therapist_id"),
            "is_active":         bool(u.get("is_active", True)),
            "created_at":        u.get("created_at"),
            "session_count":     len(sess),
            "avg_score":         round(sum(completed_scores) / len(completed_scores), 1) if completed_scores else None,
            "last_session_date": last_date,
        })
    return result


# ── Get single user ───────────────────────────────────────────────────────────

@router.get("/users/{user_id}")  # No response_model
async def get_user(
    user_id: str,
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Détail d'un utilisateur avec ses statistiques."""
    resp = await db.table("users").select("*").eq("id", user_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    u = resp.data[0]
    sess_resp = await db.table("sessions").select("user_id,score,status,created_at").eq("user_id", user_id).execute()
    sess = sess_resp.data or []
    completed_scores = [s["score"] for s in sess if s.get("status") == "completed" and s.get("score") is not None]
    last_date = max((s["created_at"] for s in sess), default=None) if sess else None
    return {
        "id":                u.get("id", ""),
        "email":             u.get("email", ""),
        "username":          u.get("username") or (u.get("email", "")).split("@")[0],
        "first_name":        u.get("first_name") or "",
        "last_name":         u.get("last_name") or "",
        "role":              u.get("role") or "patient",
        "therapist_id":      u.get("therapist_id"),
        "is_active":         bool(u.get("is_active", True)),
        "created_at":        u.get("created_at"),
        "session_count":     len(sess),
        "avg_score":         round(sum(completed_scores) / len(completed_scores), 1) if completed_scores else None,
        "last_session_date": last_date,
    }


# ── List therapists (for patient assignment dropdown) ─────────────────────────

@router.get("/therapists")  # No response_model
async def list_therapists(
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Liste tous les thérapeutes actifs (pour le menu déroulant d'assignation)."""
    try:
        resp = await (
            db.table("users")
            .select("*")
            .eq("role", "therapist")
            .eq("is_active", True)
            .is_("deleted_at", "null")
            .order("last_name")
            .execute()
        )
    except Exception:
        resp = await (
            db.table("users")
            .select("*")
            .eq("role", "therapist")
            .eq("is_active", True)
            .execute()
        )
    return [
        {
            "id":           u.get("id", ""),
            "email":        u.get("email", ""),
            "username":     u.get("username") or (u.get("email", "")).split("@")[0],
            "first_name":   u.get("first_name") or "",
            "last_name":    u.get("last_name") or "",
            "role":         u.get("role", "therapist"),
            "therapist_id": u.get("therapist_id"),
            "is_active":    bool(u.get("is_active", True)),
            "created_at":   u.get("created_at"),
        }
        for u in (resp.data or [])
    ]


# ── Create user ───────────────────────────────────────────────────────────────

@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(
    data: UserCreateByAdmin,
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Crée un utilisateur (patient ou thérapeute) depuis le panneau admin."""
    # Check email uniqueness
    existing = await db.table("users").select("id").eq("email", data.email).execute()
    if existing.data:
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    # Derive username
    if data.first_name and data.last_name:
        base_username = f"{data.first_name.lower()}.{data.last_name.lower()}"
    else:
        base_username = data.email.split("@")[0]

    username = base_username
    suffix = 0
    while True:
        resp = await db.table("users").select("id").eq("username", username).execute()
        if not resp.data:
            break
        suffix += 1
        username = f"{base_username}{suffix}"

    now = _now()
    user_id = str(uuid.uuid4())
    payload = {
        "id": user_id,
        "email": data.email,
        "username": username,
        "first_name": data.first_name or "",
        "last_name": data.last_name or "",
        "hashed_password": hash_password(data.password),
        "role": data.role,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    if data.therapist_id:
        payload["therapist_id"] = data.therapist_id
    resp = await db.table("users").insert(payload).execute()
    if not resp.data:
        raise HTTPException(status_code=500, detail="Erreur lors de la création")

    await _audit(db, admin["id"], "USER_CREATED",
                 f"email={data.email} role={data.role} by={admin['email']}")
    return resp.data[0]


# ── Update user ───────────────────────────────────────────────────────────────

@router.put("/users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    body: UserRoleUpdate,
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Modifier le rôle, le statut actif ou le thérapeute assigné."""
    resp = await db.table("users").select("id,role,email").eq("id", user_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    update: dict = {"role": body.role, "updated_at": _now()}
    if body.is_active is not None:
        update["is_active"] = body.is_active
    if body.therapist_id is not None:
        update["therapist_id"] = body.therapist_id or None

    updated = await db.table("users").update(update).eq("id", user_id).execute()
    old_role = resp.data[0].get("role", "?")
    await _audit(db, admin["id"], "ROLE_CHANGE",
                 f"user={user_id} {old_role}→{body.role} active={body.is_active}")
    return updated.data[0]


# ── Soft-delete user ──────────────────────────────────────────────────────────

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    hard: bool = Query(False, description="True = suppression définitive"),
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Supprimer un utilisateur (soft par défaut, hard si ?hard=true)."""
    if user_id == admin["id"]:
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas vous supprimer")

    resp = await db.table("users").select("id,email").eq("id", user_id).execute()
    if not resp.data:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    email = resp.data[0].get("email", "")

    if hard:
        await db.table("users").delete().eq("id", user_id).execute()
        await _audit(db, admin["id"], "USER_DELETED", f"HARD user={user_id} email={email}")
    else:
        await db.table("users").update({"deleted_at": _now(), "is_active": False}).eq("id", user_id).execute()
        await _audit(db, admin["id"], "USER_DELETED", f"SOFT user={user_id} email={email}")


# ── Assign patient to therapist ───────────────────────────────────────────────

@router.post("/assign-patient", status_code=204)
async def assign_patient(
    data: PatientAssign,
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Assigne ou désassigne un patient à un thérapeute (therapist_id=null = désassigner)."""
    p = await db.table("users").select("id,email").eq("id", data.patient_id).execute()
    if not p.data:
        raise HTTPException(status_code=404, detail="Patient introuvable")

    if data.therapist_id:
        t = await db.table("users").select("id,role").eq("id", data.therapist_id).execute()
        if not t.data or t.data[0].get("role") not in ("therapist", "admin"):
            raise HTTPException(status_code=400, detail="Thérapeute invalide")

    await db.table("users").update({
        "therapist_id": data.therapist_id,
        "updated_at": _now(),
    }).eq("id", data.patient_id).execute()

    await _audit(db, admin["id"], "PATIENT_ASSIGNED",
                 f"patient={data.patient_id} → therapist={data.therapist_id}")


# ── System settings ───────────────────────────────────────────────────────────

@router.get("/settings", response_model=list[SystemSettingOut])
async def get_settings(
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Lire tous les paramètres système."""
    resp = await db.table("system_settings").select("*").order("key").execute()
    return resp.data or []


@router.put("/settings/{key}", response_model=SystemSettingOut)
async def update_setting(
    key: str,
    body: SystemSettingUpdate,
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Modifier un paramètre système."""
    now = _now()
    resp = await db.table("system_settings").upsert({
        "key": key,
        "value": body.value,
        "updated_at": now,
    }).execute()

    await _audit(db, admin["id"], "SETTINGS_CHANGED", f"key={key} value={body.value}")
    return resp.data[0]


# ── Audit logs ────────────────────────────────────────────────────────────────

@router.get("/audit-logs", response_model=list[AuditLogOut])
async def list_audit_logs(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    action: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None, description="ISO date (ex: 2026-01-01)"),
    date_to: Optional[str] = Query(None, description="ISO date (ex: 2026-12-31)"),
    admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """Journal d'audit filtrable par action, utilisateur et plage de dates."""
    query = (
        db.table("audit_logs")
        .select("*")
        .order("created_at", desc=True)
        .range(offset, offset + limit - 1)
    )
    if action:
        query = query.eq("action", action)
    if user_id:
        query = query.eq("user_id", user_id)
    if date_from:
        query = query.gte("created_at", date_from)
    if date_to:
        query = query.lte("created_at", date_to + "T23:59:59Z")

    resp = await query.execute()
    return resp.data or []


# ── Email reminders ───────────────────────────────────────────────────────────

def _days_inactive(last_session_date: str | None) -> int:
    if not last_session_date:
        return 9999
    try:
        last = datetime.fromisoformat(last_session_date.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - last).days
    except Exception:
        return 9999


@router.post("/send-reminder", status_code=200)
async def send_reminder_to_user(
    data: EmailReminderRequest,
    current_admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Envoie un email de rappel à un utilisateur spécifique.
    """
    resp = await db.table("users").select("id,email,first_name,is_active").eq("id", data.user_id).execute()
    user = resp.data[0] if resp.data else None
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")

    # Récupère la date de dernière session
    sess = await db.table("sessions").select("started_at").eq("user_id", data.user_id)\
        .order("started_at", desc=True).limit(1).execute()
    last_date = sess.data[0]["started_at"] if sess.data else None
    days = _days_inactive(last_date)

    try:
        await send_reminder_email(
            to_email=user["email"],
            first_name=user.get("first_name") or "",
            days_inactive=days if days < 9999 else 0,
            admin_message=data.message,
        )
    except EmailSendError as exc:
        raise HTTPException(status_code=503, detail=str(exc))

    await _audit(db, current_admin["id"], "EMAIL_REMINDER_SENT",
                 f"Rappel envoyé à {user['email']} (user_id={data.user_id})")

    return {"success": True, "email": user["email"]}


@router.post("/send-reminder-all", status_code=200)
async def send_reminder_to_all_inactive(
    data: EmailReminderAllRequest,
    current_admin=Depends(get_admin_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Envoie un email de rappel à tous les patients inactifs depuis N jours.
    Retourne le nombre de succès et d'échecs.
    """
    cutoff = (datetime.now(timezone.utc) - timedelta(days=data.days_inactive)).isoformat()

    # Récupère les patients actifs avec leurs dernières sessions
    users_resp = await db.table("users").select("id,email,first_name")\
        .eq("role", "patient").eq("is_active", True).execute()
    all_patients = users_resp.data or []

    sent, failed, skipped = 0, 0, 0
    errors = []

    for u in all_patients:
        sess = await db.table("sessions").select("started_at").eq("user_id", u["id"])\
            .order("started_at", desc=True).limit(1).execute()
        last_date = sess.data[0]["started_at"] if sess.data else None
        days = _days_inactive(last_date)

        if days < data.days_inactive:
            skipped += 1
            continue

        try:
            await send_reminder_email(
                to_email=u["email"],
                first_name=u.get("first_name") or "",
                days_inactive=days if days < 9999 else 0,
                admin_message=data.message,
            )
            sent += 1
        except EmailSendError as exc:
            failed += 1
            errors.append({"email": u["email"], "error": str(exc)})

    await _audit(db, current_admin["id"], "EMAIL_REMINDER_ALL",
                 f"Rappels envoyés : {sent} succès, {failed} échecs, {skipped} actifs ignorés")

    return {"sent": sent, "failed": failed, "skipped": skipped, "errors": errors}
