import numpy as np
import random
from .recommender import RecommendationEngine  # ou réutiliser la logique

class MediaSelector:
    """Sélectionne le média le plus adapté à l’état EEG."""
    def __init__(self, engine):
        self.engine = engine
    
    def select(self, eeg_state, eeg_features, media_type, exclude=None):
        return self.engine.select(eeg_state, eeg_features, media_type, exclude)
    
    def select_game(self, eeg_state, eeg_features, history):
        return self.engine.select_game(eeg_state, eeg_features, history)