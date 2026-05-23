import time
from .recommender import EEGBuffer, Session as BaseSession

class SessionState:
    """État simplifié d’une session (utilisé par le bridge)."""
    def __init__(self, session_id, patient_id):
        self.session_id = session_id
        self.patient_id = patient_id
        self.start_time = time.time()
        self.eeg_buffer = EEGBuffer()
        self.history = []
        self.current_media = None