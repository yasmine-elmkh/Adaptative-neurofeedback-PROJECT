"""
NeuroCap — Schémas Pydantic (validation requêtes / sérialisation réponses)
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, EmailStr, Field


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    username: Optional[str] = Field(None, min_length=3, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    therapist_id: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class UserRoleUpdate(BaseModel):
    role: str = Field(pattern="^(patient|therapist|admin)$")
    is_active: Optional[bool] = None
    therapist_id: Optional[str] = None


class TherapistNoteCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class TherapistNoteOut(BaseModel):
    id: str
    therapist_id: str
    patient_id: str
    content: str
    created_at: datetime
    model_config = {"from_attributes": True}


class PatientSummary(BaseModel):
    id: str
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool
    therapist_id: Optional[str] = None
    created_at: Optional[datetime] = None
    # Session stats
    session_count: int = 0
    last_session_date: Optional[datetime] = None
    last_session_objective: Optional[str] = None
    last_session_score: Optional[float] = None
    avg_score_last5: Optional[float] = None
    avg_score_all: Optional[float] = None
    score_trend: Optional[float] = None
    evolution_pct: Optional[float] = None  # first vs last session score
    # EEG profile (read-only snapshot)
    palier: Optional[str] = None
    profile_type: Optional[str] = None
    model_config = {"from_attributes": True}


class PasswordChange(BaseModel):
    current_password: Optional[str] = None
    new_password: str = Field(min_length=8)


class TherapistRecommendationCreate(BaseModel):
    recommended_objective: Optional[str] = Field(None, pattern="^(concentration|relaxation|stress)$")
    weekly_sessions_target: Optional[int] = Field(None, ge=1, le=7)
    message: Optional[str] = Field(None, max_length=500)


class TherapistRecommendationOut(BaseModel):
    id: str
    patient_id: str
    therapist_id: str
    recommended_objective: Optional[str] = None
    weekly_sessions_target: Optional[int] = None
    message: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class PalierAdjust(BaseModel):
    palier: str = Field(pattern="^(P1_INITIATION|P2_APPRENTISSAGE|P3_MAITRISE|P4_AUTONOMIE|P1|P2|P3|P4)$")


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    refresh_token: str


# ── Profil EEG ────────────────────────────────────────────────────────────────

class EEGProfileOut(BaseModel):
    id: str
    user_id: str
    profile_type: Optional[str] = None
    iapf: Optional[float] = None
    baseline_tbr: Optional[float] = None
    baseline_alpha: Optional[float] = None
    baseline_beta: Optional[float] = None
    baseline_theta: Optional[float] = None
    reactivity_score: Optional[float] = None
    current_threshold: Optional[float] = None
    palier: Optional[str] = None
    calibrated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CalibrationData(BaseModel):
    iapf: float = Field(ge=7.0, le=13.0)
    baseline_tbr: float = Field(ge=0.0)
    baseline_alpha: float = Field(ge=0.0)
    baseline_beta: float = Field(ge=0.0)
    baseline_theta: float = Field(ge=0.0)
    reactivity_score: float = Field(ge=0.0, le=1.0)


# ── Sessions ──────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    objective: str = "concentration"
    feedback_mode: str = "visual"


class SessionResponse(BaseModel):
    id: str
    user_id: str
    objective: str
    feedback_mode: str
    status: str
    score: Optional[float] = None
    duration_seconds: Optional[int] = None
    avg_concentration: Optional[float] = None
    avg_stress: Optional[float] = None
    avg_tbr: Optional[float] = None
    n_blocks: int = 0
    recommendations: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class SessionReport(BaseModel):
    session: SessionResponse
    events_count: int
    concentration_timeline: List[float]
    stress_timeline: List[float]
    threshold_timeline: List[float]
    recommendations: str


# ── Assistant ─────────────────────────────────────────────────────────────────

class UserCreateByAdmin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="patient", pattern="^(patient|therapist|admin)$")
    therapist_id: Optional[str] = None


class PatientAssign(BaseModel):
    patient_id: str
    therapist_id: Optional[str] = None  # None = désassigner


class SystemSettingOut(BaseModel):
    key: str
    value: str
    description: Optional[str] = None
    updated_at: Optional[datetime] = None


class SystemSettingUpdate(BaseModel):
    value: str = Field(min_length=0, max_length=500)


class AssistantRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    session_id: Optional[str] = None
    eeg_context: Optional[dict] = None  # client-supplied EEG snapshot for richer RAG context


class AssistantResponse(BaseModel):
    answer: str
    sources: List[str] = []


class AssistantFeedback(BaseModel):
    message_index: int
    feedback: str = Field(pattern="^(up|down)$")
    question: Optional[str] = None
    answer: Optional[str] = None


# ── Admin ─────────────────────────────────────────────────────────────────────

class AdminStats(BaseModel):
    total_users: int
    active_users: int
    total_therapists: int
    active_patients: int
    total_sessions: int
    completed_sessions: int
    sessions_this_month: int
    avg_session_score: Optional[float] = None
    avg_session_duration: Optional[float] = None
    engagement_rate: float = 0.0


class UserWithStats(UserOut):
    session_count: int = 0
    avg_score: Optional[float] = None
    last_session_date: Optional[datetime] = None


class AuditLogOut(BaseModel):
    id: str
    user_id: Optional[str] = None
    action: str
    details: Optional[str] = None
    ip_address: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── EEG Reports ──────────────────────────────────────────────────────────────

class EEGReportCreate(BaseModel):
    type: str = Field(default='live', pattern="^(live|file)$")
    filename: Optional[str] = None
    duration_s: Optional[float] = None
    n_epochs_accepted: int = 0
    n_epochs_rejected: int = 0
    dominant_state: Optional[str] = None
    concentration_pct: Optional[float] = None
    stress_pct: Optional[float] = None
    uncertain_pct: Optional[float] = None
    mean_confidence: Optional[float] = None
    states_json: Optional[dict] = None
    notes: Optional[str] = Field(None, max_length=1000)


class EEGReportOut(BaseModel):
    id: str
    patient_id: str
    therapist_id: Optional[str] = None
    type: str
    filename: Optional[str] = None
    duration_s: Optional[float] = None
    n_epochs_accepted: int = 0
    n_epochs_rejected: int = 0
    dominant_state: Optional[str] = None
    concentration_pct: Optional[float] = None
    stress_pct: Optional[float] = None
    uncertain_pct: Optional[float] = None
    mean_confidence: Optional[float] = None
    states_json: Optional[dict] = None
    notes: Optional[str] = None
    created_at: datetime
    model_config = {"from_attributes": True}


# ── WebSocket frame ───────────────────────────────────────────────────────────

class WSFrame(BaseModel):
    timestamp: str
    concentration: float
    stress: float
    features: dict = {}
    threshold: float
    ewma: float
    feedback_command: dict = {}
    signal_quality: float
    block_number: int = 1
    block_time_sec: float = 0.0
    success_rate: float = 0.0
