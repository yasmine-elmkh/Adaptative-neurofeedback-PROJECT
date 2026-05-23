"""Pont entre le pipeline DSP et le moteur de recommandation."""
import asyncio
import uuid
from .recommender import RecommendationEngine, Session

class FeedbackBridge:
    def __init__(self):
        self.engine = RecommendationEngine()
        self.active_sessions = {}  # session_id → Session
    
    def start_session(self, patient_id, objective="stress_reduction"):
        session = Session(self.engine, objective=objective, user_id=patient_id)
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = session
        return session_id, session
    
    def on_epoch(self, session_id, eeg_state, eeg_features, forced_type=None):
        session = self.active_sessions.get(session_id)
        if session:
            return session.on_epoch(eeg_state, eeg_features, forced_type=forced_type)
        return None

    def skip(self, session_id, forced_type=None):
        session = self.active_sessions.get(session_id)
        if session:
            return session.on_skip(forced_type=forced_type)
        return None

    def sam_rating(self, session_id, score):
        session = self.active_sessions.get(session_id)
        if session:
            session.on_sam_rating(score)

    def next_item(self, session_id: str, forced_type=None):
        """Prochain item sans pénalité (après soumission de feedback)."""
        session = self.active_sessions.get(session_id)
        if session and session.last_state:
            return session._select_and_play(session.last_state, session.last_feats, forced_type=forced_type)
        return None

    async def end_session(self, session_id, broadcast_fn=None):
        session = self.active_sessions.pop(session_id, None)
        if session:
            result = await session.end_session()
            if broadcast_fn:
                asyncio.create_task(session.generate_report_async(result, broadcast_fn))
            return result
        return None