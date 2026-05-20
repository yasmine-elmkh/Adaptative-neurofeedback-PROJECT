"""
NeuroCap — Conditions de déclenchement du fine-tuning automatique
==================================================================
Règles d'activité :
  - Dernière activité (session OU rapport EEG) ≤ 14 jours
  - ≥ 3 activités dans les 30 derniers jours
  - ≥ 100 époques fiables récentes (confiance ≥ 0.85) dans les 30 jours

Seuils fine-tuning :
  v1 : 2 000 époques fiables, ≥ 25 jours depuis calibration
  v2 : 4 000 nouvelles époques fiables, ≥ 60 jours depuis v1
  maintenance : ≥ 180 jours depuis dernier fine-tuning
  drift : accuracy 20 dernières sessions < 85%, ≥ 7 jours depuis dernier FT
"""
from datetime import datetime, timezone, timedelta

ACTIVITY_MAX_IDLE_DAYS    = 14
ACTIVITY_MIN_ACTIONS_30D  = 3
ACTIVITY_MIN_EPOCHS_30D   = 100

V1_EPOCHS_NEEDED  = 2000
V2_EPOCHS_NEEDED  = 4000
V2_DELAY_DAYS     = 60
MAINTENANCE_DAYS  = 180
CAL_GRACE_DAYS    = 25
DRIFT_ACCURACY    = 0.85
DRIFT_COOLDOWN    = 7


async def get_activity(patient_id: str, db) -> dict:
    """Retourne les métriques d'activité récente du patient."""
    now    = datetime.now(timezone.utc)
    cutoff = (now - timedelta(days=30)).isoformat()

    # Dernière session
    r1 = await db.table("sessions") \
        .select("created_at") \
        .eq("user_id", patient_id) \
        .order("created_at", desc=True) \
        .limit(1).execute()
    last_sess_dt = (
        datetime.fromisoformat(r1.data[0]["created_at"].replace("Z", "+00:00"))
        if r1.data else None
    )

    # Dernier rapport EEG (proxy activité pour patients sans sessions)
    r2 = await db.table("eeg_reports") \
        .select("created_at") \
        .eq("patient_id", patient_id) \
        .order("created_at", desc=True) \
        .limit(1).execute()
    last_rep_dt = (
        datetime.fromisoformat(r2.data[0]["created_at"].replace("Z", "+00:00"))
        if r2.data else None
    )

    # Dernière activité = max(session, rapport)
    candidates = [d for d in [last_sess_dt, last_rep_dt] if d]
    last_activity = max(candidates) if candidates else None
    days_idle = (now - last_activity).days if last_activity else None

    # Compteurs 30 jours
    r3 = await db.table("sessions").select("id", count="exact") \
        .eq("user_id", patient_id).gte("created_at", cutoff).execute()
    sessions_30d = r3.count or 0

    r4 = await db.table("eeg_reports").select("id", count="exact") \
        .eq("patient_id", patient_id).gte("created_at", cutoff).execute()
    reports_30d = r4.count or 0

    activity_total_30d = sessions_30d + reports_30d

    # Époques fiables récentes
    r5 = await db.table("training_epochs").select("id", count="exact") \
        .eq("patient_id", patient_id) \
        .eq("is_high_confidence", True) \
        .gte("created_at", cutoff).execute()
    reliable_30d = r5.count or 0

    is_active = (
        days_idle is not None
        and days_idle <= ACTIVITY_MAX_IDLE_DAYS
        and activity_total_30d >= ACTIVITY_MIN_ACTIONS_30D
        and reliable_30d >= ACTIVITY_MIN_EPOCHS_30D
    )

    return {
        "is_active":             is_active,
        "last_activity_at":      last_activity.isoformat() if last_activity else None,
        "days_idle":             days_idle,
        "sessions_last_30d":     sessions_30d,
        "reports_last_30d":      reports_30d,
        "activity_total_30d":    activity_total_30d,
        "reliable_epochs_30d":   reliable_30d,
    }


async def check_finetune_trigger(patient_id: str, profile: dict, db) -> tuple:
    """
    Détermine si un fine-tuning doit être déclenché.
    Retourne (should_trigger: bool, reason: str, trigger_type: str | None).
    trigger_type: 'v1' | 'v2' | 'drift' | 'maintenance' | None
    """
    activity = await get_activity(patient_id, db)
    if not activity["is_active"]:
        return False, "Patient inactif", None

    now     = datetime.now(timezone.utc)
    version = profile.get("finetuned_version") or 0

    last_ft_str = profile.get("last_finetune_at")
    last_ft_dt  = (
        datetime.fromisoformat(str(last_ft_str).replace("Z", "+00:00"))
        if last_ft_str else None
    )

    # Époques haute confiance non encore utilisées
    r = await db.table("training_epochs").select("id", count="exact") \
        .eq("patient_id", patient_id) \
        .eq("is_high_confidence", True) \
        .eq("used_in_finetuning", False).execute()
    unused_hc = r.count or 0

    if version == 0:
        cal_str  = profile.get("calibrated_at")
        days_cal = 0
        if cal_str:
            cal_dt   = datetime.fromisoformat(str(cal_str).replace("Z", "+00:00"))
            days_cal = (now - cal_dt).days
        if unused_hc >= V1_EPOCHS_NEEDED and days_cal >= CAL_GRACE_DAYS:
            return True, f"v1 : {unused_hc} époques fiables disponibles", "v1"

    elif version == 1 and last_ft_dt:
        days_since = (now - last_ft_dt).days
        if unused_hc >= V2_EPOCHS_NEEDED and days_since >= V2_DELAY_DAYS:
            return True, f"v2 : {unused_hc} nouvelles époques", "v2"

    elif version >= 2 and last_ft_dt:
        days_since = (now - last_ft_dt).days
        if days_since >= MAINTENANCE_DAYS:
            return True, f"Maintenance semestrielle ({days_since}j depuis dernier FT)", "maintenance"

    # Dérive de performance
    acc = profile.get("last_20_sessions_accuracy")
    if acc is not None and float(acc) < DRIFT_ACCURACY:
        if last_ft_dt and (now - last_ft_dt).days >= DRIFT_COOLDOWN:
            return True, f"Dérive détectée (accuracy={float(acc):.0%})", "drift"

    return False, "Conditions non remplies", None
