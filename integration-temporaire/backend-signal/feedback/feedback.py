from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from feedback.bridge import FeedbackBridge
from supabase_client import supabase   # Connexion Supabase

router = APIRouter(prefix="/api/feedback", tags=["feedback"])
bridge = FeedbackBridge()

class StartRequest(BaseModel):
    patient_id: str
    objective: str = "stress_reduction"

class RecommendRequest(BaseModel):
    session_id: str
    eeg_state: str
    features: dict

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

@router.post("/start")
async def start_session(req: StartRequest):
    session_id, session = bridge.start_session(req.patient_id, req.objective)
    return {"session_id": session_id}

@router.post("/recommend")
async def recommend(req: RecommendRequest):
    action = bridge.on_epoch(req.session_id, req.eeg_state, req.features)
    if action:
        return action
    raise HTTPException(404, "No recommendation available")

@router.post("/submit")
async def submit_feedback(req: FeedbackRequest):
    session = bridge.active_sessions.get(req.session_id)
    if session and session.current_item:
        # Mettre à jour les poids Thompson (backend)
        session.engine.sampler.update(
            session.current_item,
            success=req.liked,
            eeg_state=session.last_state   # état EEG lors de la recommandation
        )
        # Sauvegarde dans Supabase (table media_interactions)
        try:
            # Récupérer l'id du média à partir du filename
            media_resp = supabase.table('medias').select('id').eq('filename', session.current_item).execute()
            if media_resp.data:
                media_id = media_resp.data[0]['id']
                # Calculer la durée écoulée depuis le début de l'item
                duration = None
                if session.item_history and session.item_history[-1].get('duration_s'):
                    duration = session.item_history[-1]['duration_s']
                supabase.table('media_interactions').insert({
                    'user_id': session.user_id,
                    'media_id': media_id,
                    'session_id': req.session_id,
                    'interaction_type': 'like' if req.liked else 'skip',
                    'rating_value': req.note_concentration if req.liked else None,
                    'duration_seconds': duration,
                    'progress_percent': 100 if req.liked else None,
                    'created_at': datetime.now().isoformat()
                }).execute()
                print(f"[Feedback] Interaction enregistrée: {session.current_item} liked={req.liked}")
        except Exception as e:
            print(f"[Feedback] Erreur insertion media_interactions: {e}")
    return {"status": "ok"}

@router.post("/next")
async def next_recommendation(req: SkipRequest):
    """Prochain item sans pénalité (après soumission de feedback)."""
    action = bridge.next_item(req.session_id)
    if action:
        return action
    raise HTTPException(404, "Session introuvable ou état non initialisé")

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