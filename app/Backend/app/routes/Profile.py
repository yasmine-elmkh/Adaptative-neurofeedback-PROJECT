"""
NeuroCap — Routes Profil EEG
GET  /api/profile/me          → Profil EEG de l'utilisateur connecté
POST /api/profile/calibration → Enregistrer les données de calibration
"""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas import EEGProfileOut, CalibrationData

router = APIRouter(prefix="/api/profile", tags=["Profil EEG"])


@router.get("/me", response_model=EEGProfileOut)
async def get_profile(
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Retourne le profil EEG de l'utilisateur.
    Crée un profil par défaut (type B, seuil 0.5) si aucun n'existe encore.
    """
    resp = await db.table("eeg_profiles").select("*").eq("user_id", current_user["id"]).execute()

    if resp.data:
        return resp.data[0]

    # Profil initial créé automatiquement à la première visite
    profile_id = str(uuid.uuid4())
    new_profile = {
        "id": profile_id,
        "user_id": current_user["id"],
        "profile_type": "B",
        "current_threshold": 0.5,
        "palier": "P1",
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    resp = await db.table("eeg_profiles").insert(new_profile).execute()
    return resp.data[0]


@router.post("/calibration", response_model=EEGProfileOut)
async def calibrate_profile(
    data: CalibrationData,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Enregistre les mesures de calibration EEG et calcule le profil cognitif.

    Règles de classification (CdC §2.5.2) :
      - Réactivité > 0.7  → Profil A (seuil 0.60) — très réactif
      - Réactivité ≥ 0.4  → Profil B (seuil 0.50) — standard
      - Réactivité < 0.4  → Profil C (seuil 0.35) — faible réactivité
    """
    # Déterminer le profil et le seuil adaptatif initial
    if data.reactivity_score > 0.7:
        profile_type, threshold = "A", 0.60
    elif data.reactivity_score >= 0.4:
        profile_type, threshold = "B", 0.50
    else:
        profile_type, threshold = "C", 0.35

    now = datetime.now(timezone.utc).isoformat()
    updates = {
        "profile_type": profile_type,
        "iapf": data.iapf,
        "baseline_tbr": data.baseline_tbr,
        "baseline_alpha": data.baseline_alpha,
        "baseline_beta": data.baseline_beta,
        "baseline_theta": data.baseline_theta,
        "reactivity_score": data.reactivity_score,
        "current_threshold": threshold,
        "palier": "P1",
        "calibrated_at": now,
        "updated_at": now,
    }

    # Vérifier si un profil existe déjà
    existing = await db.table("eeg_profiles").select("id").eq("user_id", current_user["id"]).execute()

    if existing.data:
        resp = await (
            db.table("eeg_profiles")
            .update(updates)
            .eq("user_id", current_user["id"])
            .execute()
        )
    else:
        updates["id"] = str(uuid.uuid4())
        updates["user_id"] = current_user["id"]
        resp = await db.table("eeg_profiles").insert(updates).execute()

    # Audit
    await db.table("audit_logs").insert({
        "id": str(uuid.uuid4()),
        "user_id": current_user["id"],
        "action": "CALIBRATION",
        "details": f"profile_type={profile_type} iapf={data.iapf} tbr={data.baseline_tbr:.3f} reactivity={data.reactivity_score:.2f}",
        "created_at": now,
    }).execute()

    return resp.data[0]
