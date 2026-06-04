"""
NeuroCap — Route de log EEG Feedback (mode libre, hors protocole 15 séances)
POST /api/eeg-feedback/log → enregistre une interaction dans eeg_feedback_logs

Non bloquant : si la table n'existe pas encore, retourne {"logged": false} sans erreur.

Schema Supabase à créer :
    CREATE TABLE eeg_feedback_logs (
        id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        user_id          UUID REFERENCES users(id),
        source           TEXT,          -- 'live' | 'offline'
        eeg_state        TEXT,
        confidence       FLOAT,
        feedback_type    TEXT,
        feedback_subtype TEXT,
        user_sam_score   INTEGER,
        liked            BOOLEAN,
        duration_seconds INTEGER,
        created_at       TIMESTAMPTZ DEFAULT now()
    );
"""

import uuid
import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from supabase import AsyncClient

from app.core.database import get_db
from app.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/eeg-feedback", tags=["EEG Feedback Log"])


class FeedbackLogRequest(BaseModel):
    source:           str   = "live"     # 'live' | 'offline'
    eeg_state:        str   = "neutral"
    confidence:       float = 0.0
    feedback_type:    str   = "game"
    feedback_subtype: Optional[str]  = None
    user_sam_score:   Optional[int]  = Field(None, ge=1, le=5)
    liked:            Optional[bool] = None
    duration_seconds: int   = 0


@router.post("/log")
async def log_feedback_interaction(
    data: FeedbackLogRequest,
    current_user=Depends(get_current_user),
    db: AsyncClient = Depends(get_db),
):
    """
    Enregistre une interaction de feedback EEG libre (non bloquant).
    Silencieux si la table n'existe pas encore en base.
    """
    try:
        await db.table("eeg_feedback_logs").insert({
            "id":               str(uuid.uuid4()),
            "user_id":          current_user["id"],
            "source":           data.source,
            "eeg_state":        data.eeg_state,
            "confidence":       data.confidence,
            "feedback_type":    data.feedback_type,
            "feedback_subtype": data.feedback_subtype,
            "user_sam_score":   data.user_sam_score,
            "liked":            data.liked,
            "duration_seconds": data.duration_seconds,
            "created_at":       datetime.now(timezone.utc).isoformat(),
        }).execute()
        return {"logged": True}
    except Exception as e:
        logger.info("eeg_feedback_logs insert skipped (table may not exist): %s", e)
        return {"logged": False}
