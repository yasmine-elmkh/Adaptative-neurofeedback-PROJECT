from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from feedback.bridge import FeedbackBridge

router = APIRouter(prefix="/api/feedback", tags=["feedback"])
bridge = FeedbackBridge()

class StartRequest(BaseModel):
    patient_id: str
    objective: str = "stress_reduction"

class RecommendRequest(BaseModel):
    session_id: str
    eeg_state: str
    features: dict
    media_type: Optional[str] = None

class FeedbackRequest(BaseModel):
    session_id: str
    recommandation_id: str
    liked: bool
    ressenti: Optional[str] = None
    note_concentration: int = 3
    note_stress: int = 3

class SkipRequest(BaseModel):
    session_id: str

class SamRatingRequest(BaseModel):
    session_id: str
    score: int

class JustifyRequest(BaseModel):
    media_id: int
    user_id: str = "anonymous"
    eeg_state: str = "neutral"

@router.post("/start")
async def start_session(req: StartRequest):
    session_id, session = bridge.start_session(req.patient_id, req.objective)
    return {"session_id": session_id}

@router.post("/recommend")
async def recommend(req: RecommendRequest):
    action = bridge.on_epoch(req.session_id, req.eeg_state, req.features, forced_type=req.media_type)
    if action:
        return action
    raise HTTPException(404, "No recommendation available")

@router.post("/submit")
async def submit_feedback(req: FeedbackRequest):
    session = bridge.active_sessions.get(req.session_id)
    if session and session.current_item:
        session.engine.sampler.update(session.current_item, success=req.liked)
        session.engine._save_weights()
    return {"status": "ok"}

@router.post("/next")
async def next_recommendation(req: SkipRequest):
    """Prochain item sans pénalité (après soumission de feedback)."""
    action = bridge.next_item(req.session_id)
    if action:
        return action
    raise HTTPException(404, "Session introuvable ou état non initialisé")

@router.post("/justify")
async def justify_media(req: JustifyRequest):
    """Justification dynamique + guide d'utilisation pour un média."""
    try:
        from feedback.media_analyzer import generate_justification
        result = generate_justification(req.media_id, req.user_id, req.eeg_state)
        return result
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/skip")
async def skip(req: SkipRequest):
    action = bridge.skip(req.session_id)
    return action or {"status": "no_action"}

@router.post("/sam")
async def sam_rating(req: SamRatingRequest):
    bridge.sam_rating(req.session_id, req.score)
    return {"status": "ok"}

@router.post("/end")
async def end_session(req: SkipRequest):
    result = await bridge.end_session(req.session_id)
    return result or {"status": "no_session"}

@router.websocket("/ws/{session_id}")
async def websocket_feedback(websocket: WebSocket, session_id: str):
    await websocket.accept()
    session = bridge.active_sessions.get(session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    try:
        while True:
            data = await websocket.receive_text()
            # Traiter les commandes WebSocket (optionnel)
            pass
    except WebSocketDisconnect:
        pass