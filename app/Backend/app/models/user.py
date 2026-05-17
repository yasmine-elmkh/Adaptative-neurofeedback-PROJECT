"""
NeuroCap — Modèles ORM (SQLAlchemy)
Compatible SQLite (dev) et PostgreSQL/Supabase (prod).
Tables : users, eeg_profiles, sessions, session_events, audit_logs
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, Float, Integer, DateTime, Text,
    ForeignKey, Index,
)
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
