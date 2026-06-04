"""
NeuroCap — Schémas Pydantic pour le module de recommandation média
"""

from datetime import datetime
from typing import Optional, List, Literal, Union
from uuid import UUID

from pydantic import BaseModel, Field


# ── Média enrichi ─────────────────────────────────────────────────────────────

class MediaOut(BaseModel):
    id: str
    type: str
    filename: str
    url: str
    eeg_target_state: Optional[str] = None
    category: Optional[str] = None
    tempo_bpm: Optional[float] = None
    brightness: Optional[float] = None
    saturation: Optional[float] = None
    contrast: Optional[float] = None
    duration_seconds: Optional[int] = None
    difficulty_level: Optional[int] = None
    game_prefix: Optional[str] = None
    metadata: Optional[dict] = None
    model_config = {"from_attributes": True}


# ── Préférences média utilisateur ────────────────────────────────────────────

class UserMediaPreferencesOut(BaseModel):
    user_id: str
    preferred_categorie: str
    preferred_type: Optional[str] = None
    avg_tempo_bpm: Optional[float] = None
    avg_brightness: Optional[float] = None
    avg_saturation: Optional[float] = None
    avg_contrast: Optional[float] = None
    preferences_vector: Optional[dict] = None
    last_updated: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ── Recommandations media ─────────────────────────────────────────────────────

class RecommendationsMediaOut(BaseModel):
    id: str
    user_id: str
    media_id: Union[int, str]
    score: float
    reason: Optional[str] = None
    generated_at: datetime
    expires_at: Optional[datetime] = None
    is_clicked: bool = False
    model_config = {"from_attributes": True}


class RecommendationsMediaWithMedia(RecommendationsMediaOut):
    media: Optional[MediaOut] = None


# ── Playlists ─────────────────────────────────────────────────────────────────

class PlaylistCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)


class PlaylistOut(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    created_by_role: str
    is_therapeutic: bool
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}


class PlaylistWithMedia(PlaylistOut):
    items: List[MediaOut] = []


# ── Recommandations offline ───────────────────────────────────────────────────

class OfflineRecommendationOut(BaseModel):
    id: str
    user_id: str
    report_id: Optional[str] = None
    filename: str
    epoch_idx: int
    eeg_state: str
    media_id: str
    media_type: str
    score: float
    liked: Optional[bool] = None
    feedback_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class OfflineRecommendationFeedback(BaseModel):
    recommendation_id: str
    liked: bool


# ── Entrées API ───────────────────────────────────────────────────────────────

class SessionMediaRecommendRequest(BaseModel):
    current_block_number: int = Field(1, ge=1, le=10)
    force_calming: bool = False


class MediaFeedbackItem(BaseModel):
    media_id: str
    interaction_type: Literal["view", "play", "pause", "complete", "like", "rating", "skip"]
    rating_value: Optional[float] = Field(None, ge=1, le=5)
    duration_seconds: Optional[int] = None
    progress_percent: Optional[float] = Field(None, ge=0, le=100)


class SessionMediaFeedbackRequest(BaseModel):
    items: List[MediaFeedbackItem] = Field(min_length=1)


class TherapeuticPlaylistRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    recommended_objective: Optional[str] = Field(
        None,
        pattern="^(concentration|relaxation|stress)$",
    )


# ── Scoring interne ───────────────────────────────────────────────────────────

class MediaScoringInput(BaseModel):
    user_id: str
    session_id: Optional[str] = None
    eeg_state: Literal["stress", "focus", "neutral"] = "neutral"
    profile_type: Literal["A", "B", "C"] = "B"
    palier: Literal["P1", "P2", "P3", "P4"] = "P1"
    force_calming: bool = False
    current_metrics: Optional[dict] = None


# ── Dashboard patient unifié ──────────────────────────────────────────────────

class SessionWithMediaSummary(BaseModel):
    id: str
    objective: str
    status: str
    score: Optional[float] = None
    avg_concentration: Optional[float] = None
    avg_stress: Optional[float] = None
    created_at: datetime
    media_count: int = 0


class EEGReportSummary(BaseModel):
    id: str
    source: Optional[str] = None
    filename: Optional[str] = None
    dominant_state: Optional[str] = None
    concentration_pct: Optional[float] = None
    stress_pct: Optional[float] = None
    n_epochs: int = 0
    created_at: datetime
    offline_recommendations_count: int = 0


class PatientDashboard(BaseModel):
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile_type: Optional[str] = None
    palier: Optional[str] = None
    finetuned_version: Optional[int] = None
    last_finetune_at: Optional[datetime] = None
    total_sessions: int = 0
    avg_session_score: Optional[float] = None
    recent_sessions: List[SessionWithMediaSummary] = []
    pending_recommendations: List[RecommendationsMediaOut] = []
    playlists: List[PlaylistOut] = []
    recent_eeg_reports: List[EEGReportSummary] = []
    finetuning_status: Optional[str] = None
