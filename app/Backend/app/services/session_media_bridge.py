"""
NeuroCap — Pont Session EEG ↔ Recommandation Média

Fonctions utilitaires qui lisent l'état EEG temps réel d'une session
(session_events) pour piloter le moteur de recommandation média.
"""

import logging
from typing import Optional

from supabase import AsyncClient

from app.services.media_recommendation import determine_eeg_state

logger = logging.getLogger(__name__)


async def get_session_eeg_state(
    session_id: str,
    db: AsyncClient,
    last_n_events: int = 30,
) -> tuple[str, float, float]:
    """
    Calcule l'état EEG courant à partir des N derniers session_events.

    Retourne (eeg_state, avg_concentration, avg_stress).
    """
    try:
        resp = await (
            db.table("session_events")
            .select("concentration_rate,stress_rate")
            .eq("session_id", session_id)
            .eq("is_artifact", False)
            .order("timestamp", desc=True)
            .limit(last_n_events)
            .execute()
        )
        events = resp.data or []
    except Exception as exc:
        logger.warning("get_session_eeg_state: %s", exc)
        return "neutral", 0.5, 0.3

    if not events:
        return "neutral", 0.5, 0.3

    avg_conc  = sum(float(e.get("concentration_rate") or 0) for e in events) / len(events)
    avg_stress = sum(float(e.get("stress_rate") or 0)       for e in events) / len(events)
    state = determine_eeg_state(avg_conc, avg_stress)
    return state, round(avg_conc, 4), round(avg_stress, 4)


async def check_consecutive_stress_blocks(
    session_id: str,
    db: AsyncClient,
    threshold: float = 0.7,
    min_blocks: int = 3,
) -> bool:
    """
    Détecte si avg_stress > threshold pendant min_blocks blocs consécutifs.
    Règle métier : déclenche une recommandation calming prioritaire.
    """
    try:
        resp = await (
            db.table("session_events")
            .select("block_number,stress_rate")
            .eq("session_id", session_id)
            .eq("is_artifact", False)
            .order("timestamp", desc=True)
            .limit(200)
            .execute()
        )
        events = resp.data or []
    except Exception as exc:
        logger.warning("check_consecutive_stress_blocks: %s", exc)
        return False

    if not events:
        return False

    # Grouper par bloc
    block_stress: dict[int, list[float]] = {}
    for e in events:
        bn = e.get("block_number") or 0
        block_stress.setdefault(bn, []).append(float(e.get("stress_rate") or 0))

    # Vérifier blocs consécutifs les plus récents
    sorted_blocks = sorted(block_stress.keys(), reverse=True)
    consecutive = 0
    for bn in sorted_blocks[:min_blocks + 2]:
        vals = block_stress.get(bn, [])
        if not vals:
            break
        avg = sum(vals) / len(vals)
        if avg > threshold:
            consecutive += 1
        else:
            break

    return consecutive >= min_blocks


async def get_patient_eeg_profile(
    user_id: str,
    db: AsyncClient,
) -> tuple[str, str]:
    """
    Retourne (profile_type, palier) depuis eeg_profiles.
    Valeurs par défaut : ('B', 'P1').
    """
    try:
        resp = await (
            db.table("eeg_profiles")
            .select("profile_type,palier")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if resp.data:
            row = resp.data[0]
            palier = str(row.get("palier") or "P1")
            # Normaliser P1_INITIATION → P1 etc.
            if "_" in palier:
                palier = palier.split("_")[0]
            return str(row.get("profile_type") or "B"), palier
    except Exception as exc:
        logger.warning("get_patient_eeg_profile: %s", exc)
    return "B", "P1"


async def mark_recommendation_clicked(
    user_id: str,
    media_id: str,
    db: AsyncClient,
) -> None:
    """Marque une recommandation comme cliquée (progress_percent > 50%)."""
    try:
        await (
            db.table("recommendations_media")
            .update({"is_clicked": True})
            .eq("user_id", user_id)
            .eq("media_id", media_id)
            .execute()
        )
    except Exception as exc:
        logger.warning("mark_recommendation_clicked: %s", exc)


async def get_session_feedback_sessions_id(
    session_id: str,
    db: AsyncClient,
) -> Optional[str]:
    """
    Certaines sessions ont un feedback_sessions associé.
    Retourne l'id de la feedback_session correspondante si elle existe.
    Utilisé pour lier les media_interactions existantes à la session core.
    """
    try:
        resp = await (
            db.table("feedback_sessions")
            .select("id")
            .eq("id", session_id)
            .limit(1)
            .execute()
        )
        if resp.data:
            return resp.data[0]["id"]
    except Exception:
        pass
    return None
