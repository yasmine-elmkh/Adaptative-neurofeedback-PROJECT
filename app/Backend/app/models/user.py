"""
NeuroCap — Modèles ORM (SQLAlchemy)
Compatible SQLite (dev) et PostgreSQL/Supabase (prod).
Tables : toutes les 23 tables du schéma supabase_complete.sql
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, Float, Integer, DateTime, Text,
    ForeignKey, Index, Date,
)
try:
    from sqlalchemy import JSON
except ImportError:
    from sqlalchemy.types import Text as JSON  # fallback SQLite
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


# ── Énumérations (stockées comme String pour compatibilité SQLite) ────────────

class UserRole(str, enum.Enum):
    user      = "user"       # rétrocompat — alias patient
    patient   = "patient"
    therapist = "therapist"
    admin     = "admin"


class ProfileType(str, enum.Enum):
    A = "A"
    B = "B"
    C = "C"


class SessionStatus(str, enum.Enum):
    pending = "pending"
    calibrating = "calibrating"
    running = "running"
    paused = "paused"
    completed = "completed"
    cancelled = "cancelled"
    error = "error"


class SessionObjective(str, enum.Enum):
    concentration = "concentration"
    relaxation = "relaxation"


class FeedbackMode(str, enum.Enum):
    visual = "visual"
    audio = "audio"
    game = "game"


def _uuid():
    return str(uuid.uuid4())


def _now():
    return datetime.utcnow()


# ── Table 1 : users ───────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), default="", nullable=False)
    last_name  = Column(String(100), default="", nullable=False)
    role = Column(String(20), default=UserRole.patient.value, nullable=False)
    therapist_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    profiles = relationship(
        "EEGProfile", back_populates="user",
        cascade="all, delete-orphan", lazy="selectin",
    )
    sessions = relationship(
        "Session", back_populates="user",
        cascade="all, delete-orphan", lazy="selectin",
    )
    audit_logs = relationship(
        "AuditLog", back_populates="user", cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<User {self.username} ({self.email})>"


# ── Table 2 : eeg_profiles ───────────────────────────────────────────────────

class EEGProfile(Base):
    __tablename__ = "eeg_profiles"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    profile_type = Column(String(2), default=ProfileType.B.value)
    iapf = Column(Float, nullable=True)
    baseline_tbr = Column(Float, nullable=True)
    baseline_alpha = Column(Float, nullable=True)
    baseline_beta = Column(Float, nullable=True)
    baseline_theta = Column(Float, nullable=True)
    reactivity_score = Column(Float, nullable=True)
    current_threshold = Column(Float, default=0.5)
    palier = Column(String(10), default="P1")
    calibrated_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    user = relationship("User", back_populates="profiles")

    def __repr__(self):
        return f"<EEGProfile user={self.user_id} type={self.profile_type}>"


# ── Table 3 : sessions ───────────────────────────────────────────────────────

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    objective = Column(String(20), default=SessionObjective.concentration.value)
    feedback_mode = Column(String(10), default=FeedbackMode.visual.value)
    status = Column(String(20), default=SessionStatus.pending.value, nullable=False)

    score = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    avg_concentration = Column(Float, nullable=True)
    avg_stress = Column(Float, nullable=True)
    avg_tbr = Column(Float, nullable=True)
    avg_ei = Column(Float, nullable=True)
    n_blocks = Column(Integer, default=0)
    n_epochs_total = Column(Integer, default=0)
    n_epochs_rejected = Column(Integer, default=0)
    recommendations = Column(Text, nullable=True)

    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_now)

    user = relationship("User", back_populates="sessions")
    events = relationship(
        "SessionEvent", back_populates="session",
        cascade="all, delete-orphan", lazy="selectin",
    )

    def __repr__(self):
        return f"<Session {self.id} status={self.status}>"


# ── Table 4 : session_events ─────────────────────────────────────────────────

class SessionEvent(Base):
    __tablename__ = "session_events"

    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    timestamp = Column(DateTime, default=_now, nullable=False)
    concentration_rate = Column(Float, nullable=False)
    stress_rate = Column(Float, nullable=False)
    confidence = Column(Float, nullable=True)
    tbr = Column(Float, nullable=True)
    ei = Column(Float, nullable=True)
    abr = Column(Float, nullable=True)
    power_alpha = Column(Float, nullable=True)
    power_beta = Column(Float, nullable=True)
    power_theta = Column(Float, nullable=True)
    signal_quality = Column(Float, nullable=True)
    is_artifact = Column(Boolean, default=False)
    feedback_mode = Column(String(10), nullable=True)
    feedback_active = Column(Boolean, default=True)
    block_number = Column(Integer, nullable=True)

    session = relationship("Session", back_populates="events")


Index("ix_session_events_session_ts", SessionEvent.session_id, SessionEvent.timestamp)


# ── Table 5 : audit_logs ─────────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"),
                     nullable=True, index=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)

    user = relationship("User", back_populates="audit_logs")


# ── Table 6 : eeg_reports ────────────────────────────────────────────────────

class EEGReport(Base):
    __tablename__ = "eeg_reports"

    id = Column(String(36), primary_key=True, default=_uuid)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    source = Column(String(20), default="file", nullable=False)
    filename = Column(Text, nullable=True)
    n_epochs = Column(Integer, default=0)
    n_accepted = Column(Integer, default=0)
    dominant_state = Column(String(30), nullable=True)
    concentration_pct = Column(Float, nullable=True)
    stress_pct = Column(Float, nullable=True)
    uncertain_pct = Column(Float, nullable=True)
    avg_confidence = Column(Float, nullable=True)
    duration_s = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    epochs_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=_now)


# ── Table 7 : training_epochs ────────────────────────────────────────────────

class TrainingEpoch(Base):
    __tablename__ = "training_epochs"

    id = Column(String(36), primary_key=True, default=_uuid)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    report_id = Column(String(36), ForeignKey("eeg_reports.id", ondelete="SET NULL"),
                       nullable=True)
    predicted_label = Column(String(30), default="uncertain", nullable=False)
    confidence = Column(Float, default=0, nullable=False)
    features = Column(JSON, default=dict, nullable=False)
    is_high_confidence = Column(Boolean, default=True)
    used_in_finetuning = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_now)


# ── Table 8 : finetuning_jobs ────────────────────────────────────────────────

class FinetuningJob(Base):
    __tablename__ = "finetuning_jobs"

    id = Column(String(36), primary_key=True, default=_uuid)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    trigger_type = Column(String(30), default="manual", nullable=False)
    status = Column(String(20), default="pending", nullable=False)
    n_epochs_used = Column(Integer, default=0)
    accuracy_before = Column(Float, nullable=True)
    accuracy_after = Column(Float, nullable=True)
    model_version = Column(Integer, nullable=True)
    checkpoint_path = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=_now)
    finished_at = Column(DateTime, nullable=True)


# ── Table 9 : therapist_notes ────────────────────────────────────────────────

class TherapistNote(Base):
    __tablename__ = "therapist_notes"

    id = Column(String(36), primary_key=True, default=_uuid)
    therapist_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False, index=True)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    content = Column(Text, default="", nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)


# ── Table 10 : therapist_recommendations ─────────────────────────────────────

class TherapistRecommendation(Base):
    __tablename__ = "therapist_recommendations"

    id = Column(String(36), primary_key=True, default=_uuid)
    therapist_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False, index=True)
    recommended_objective = Column(Text, nullable=True)
    weekly_target = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


# ── Table 11 : system_settings ───────────────────────────────────────────────

class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=_now, onupdate=_now)


# ── Table 12 : medias ────────────────────────────────────────────────────────

class Media(Base):
    __tablename__ = "medias"

    id = Column(String(36), primary_key=True, default=_uuid)
    type = Column(String(20), default="audio", nullable=False)
    filename = Column(Text, default="", nullable=False)
    url = Column(Text, default="", nullable=False)
    eeg_target_state = Column(String(20), default="all")
    features = Column(JSON, default=dict)
    item_weights_alpha = Column(Float, default=1.0)
    item_weights_beta = Column(Float, default=1.0)
    game_prefix = Column(String(50), nullable=True)
    difficulty_level = Column(Integer, default=1)
    duration_seconds = Column(Integer, nullable=True)
    content_format = Column(String(20), default="standard")
    category = Column(String(50), nullable=True)
    tempo_bpm = Column(Float, nullable=True)
    brightness = Column(Float, nullable=True)
    saturation = Column(Float, nullable=True)
    contrast = Column(Float, nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=_now)


# ── Table 13 : feedback_sessions ─────────────────────────────────────────────

class FeedbackSession(Base):
    __tablename__ = "feedback_sessions"

    id = Column(String(36), primary_key=True, default=_uuid)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=True, index=True)
    session_number = Column(Integer, nullable=True)
    phase = Column(String(50), nullable=True)
    palier = Column(Integer, default=1)
    objective = Column(String(50), default="concentration")
    status = Column(String(20), default="pending")
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Float, nullable=True)
    score = Column(Integer, nullable=True)
    delta_alpha = Column(Float, nullable=True)
    delta_beta = Column(Float, nullable=True)
    session_success = Column(Boolean, nullable=True)
    items_played = Column(Integer, default=0)
    items_efficaces = Column(Integer, default=0)
    eeg_snapshot = Column(JSON, nullable=True)
    report_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)


# ── Table 14 : feedback_session_events ───────────────────────────────────────

class FeedbackSessionEvent(Base):
    __tablename__ = "feedback_session_events"

    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(String(36), ForeignKey("feedback_sessions.id", ondelete="CASCADE"),
                        nullable=True, index=True)
    event_type = Column(String(50), nullable=True)
    event_data = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=_now)


# ── Table 15 : media_interactions ────────────────────────────────────────────

class MediaInteraction(Base):
    __tablename__ = "media_interactions"

    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(String(36), ForeignKey("feedback_sessions.id", ondelete="CASCADE"),
                        nullable=True, index=True)
    patient_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"),
                        nullable=True, index=True)
    media_id = Column(String(36), ForeignKey("medias.id", ondelete="SET NULL"),
                      nullable=True)
    liked = Column(Boolean, nullable=True)
    sam_score = Column(Integer, nullable=True)
    note_concentration = Column(Integer, nullable=True)
    note_stress = Column(Integer, nullable=True)
    was_skipped = Column(Boolean, default=False)
    delta_alpha = Column(Float, nullable=True)
    delta_beta = Column(Float, nullable=True)
    efficace = Column(Boolean, nullable=True)
    duration_played = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=_now)


# ── Table 16 : protocol_sessions ─────────────────────────────────────────────

class ProtocolSession(Base):
    __tablename__ = "protocol_sessions"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=True, index=True)
    session_number = Column(Integer, default=1)
    phase = Column(Integer, default=1)
    palier = Column(String(10), default="P1")
    is_bilan = Column(Boolean, default=False)
    status = Column(String(20), default="pending")
    scheduled_date = Column(Date, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    score = Column(Integer, nullable=True)
    success_rate = Column(Float, nullable=True)
    alpha_power_ref = Column(Float, nullable=True)
    iapf = Column(Float, nullable=True)
    subjective_pre = Column(JSON, nullable=True)
    subjective_post = Column(JSON, nullable=True)
    artifact_rate = Column(Float, default=0.0)
    notes = Column(Text, nullable=True)
    bilan_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_now)


# ── Table 17 : protocol_blocs ────────────────────────────────────────────────

class ProtocolBloc(Base):
    __tablename__ = "protocol_blocs"

    id = Column(String(36), primary_key=True, default=_uuid)
    session_id = Column(String(36), ForeignKey("protocol_sessions.id", ondelete="CASCADE"),
                        nullable=True, index=True)
    bloc_number = Column(Integer, default=1)
    threshold_start = Column(Float, nullable=True)
    threshold_end = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)
    alpha_avg = Column(Float, nullable=True)
    theta_avg = Column(Float, nullable=True)
    adaptation_reason = Column(Text, nullable=True)
    fatigue_detected = Column(Boolean, default=False)
    duration_s = Column(Integer, default=180)
    created_at = Column(DateTime, default=_now)


# ── Table 18 : user_media_preferences ────────────────────────────────────────

class UserMediaPreference(Base):
    __tablename__ = "user_media_preferences"

    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     primary_key=True)
    preferred_categorie = Column(String(50), primary_key=True)
    preferred_type = Column(String(20), nullable=True)
    avg_tempo_bpm = Column(Float, nullable=True)
    avg_brightness = Column(Float, nullable=True)
    avg_saturation = Column(Float, nullable=True)
    avg_contrast = Column(Float, nullable=True)
    preferences_vector = Column(JSON, nullable=True)
    last_updated = Column(DateTime, default=_now, nullable=False)


# ── Table 19 : recommendations_media ─────────────────────────────────────────

class RecommendationMedia(Base):
    __tablename__ = "recommendations_media"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    media_id = Column(String(36), ForeignKey("medias.id", ondelete="CASCADE"),
                      nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    reason = Column(Text, nullable=True)
    generated_at = Column(DateTime, default=_now, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    is_clicked = Column(Boolean, default=False, nullable=False)


# ── Table 20 : playlists ─────────────────────────────────────────────────────

class Playlist(Base):
    __tablename__ = "playlists"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    name = Column(Text, default="", nullable=False)
    description = Column(Text, nullable=True)
    created_by_role = Column(String(20), default="patient", nullable=False)
    is_therapeutic = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=_now, nullable=False)
    updated_at = Column(DateTime, default=_now, onupdate=_now, nullable=False)


# ── Table 21 : playlist_media ─────────────────────────────────────────────────

class PlaylistMedia(Base):
    __tablename__ = "playlist_media"

    playlist_id = Column(String(36), ForeignKey("playlists.id", ondelete="CASCADE"),
                         primary_key=True)
    media_id = Column(String(36), ForeignKey("medias.id", ondelete="CASCADE"),
                      primary_key=True)
    position = Column(Integer, default=1, nullable=False)
    added_at = Column(DateTime, default=_now, nullable=False)


# ── Table 22 : offline_recommendations ───────────────────────────────────────

class OfflineRecommendation(Base):
    __tablename__ = "offline_recommendations"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)
    report_id = Column(String(36), nullable=True, index=True)
    filename = Column(Text, default="", nullable=False)
    epoch_idx = Column(Integer, default=0, nullable=False)
    eeg_state = Column(String(20), default="neutral", nullable=False)
    media_id = Column(String(36), ForeignKey("medias.id", ondelete="CASCADE"),
                      nullable=False)
    media_type = Column(String(20), default="audio", nullable=False)
    score = Column(Float, default=0.0, nullable=False)
    liked = Column(Boolean, nullable=True)
    feedback_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_now, nullable=False)


# ── Table 23 : user_protocol_progress ────────────────────────────────────────

class UserProtocolProgress(Base):
    __tablename__ = "user_protocol_progress"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, unique=True, index=True)
    current_session_number = Column(Integer, default=0, nullable=False)
    total_sessions_completed = Column(Integer, default=0, nullable=False)
    current_phase = Column(String(50), default="not_started", nullable=False)
    current_palier = Column(String(10), default="P1", nullable=False)
    cognitive_profile = Column(String(2), nullable=True)
    profile_detected_at = Column(DateTime, nullable=True)
    planned_start_date = Column(Date, nullable=True)
    planned_end_date = Column(Date, nullable=True)
    planned_session_dates = Column(JSON, default=list)
    actual_start_date = Column(Date, nullable=True)
    actual_session_dates = Column(JSON, default=list)
    bilan_b1_completed = Column(Boolean, default=False)
    bilan_b1_date = Column(DateTime, nullable=True)
    bilan_b1_score = Column(Float, nullable=True)
    bilan_b1_decision = Column(String(30), nullable=True)
    bilan_b2_completed = Column(Boolean, default=False)
    bilan_b2_date = Column(DateTime, nullable=True)
    bilan_b2_score = Column(Float, nullable=True)
    bilan_b2_decision = Column(String(30), nullable=True)
    bilan_b3_completed = Column(Boolean, default=False)
    bilan_b3_date = Column(DateTime, nullable=True)
    bilan_b3_score = Column(Float, nullable=True)
    bilan_b3_decision = Column(String(30), nullable=True)
    followup_completed = Column(Boolean, default=False)
    followup_date = Column(DateTime, nullable=True)
    followup_retention_score = Column(Float, nullable=True)
    avg_session_score = Column(Float, nullable=True)
    success_rate_global = Column(Float, nullable=True)
    alpha_beta_trend = Column(Float, nullable=True)
    last_threshold_value = Column(Float, nullable=True)
    early_stop_reason = Column(Text, nullable=True)
    early_stop_session = Column(Integer, nullable=True)
    early_stop_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="enrolled", nullable=False)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)
