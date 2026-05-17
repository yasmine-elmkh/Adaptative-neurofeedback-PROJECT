"""
Schémas Pydantic pour les sessions et données EEG
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SessionObjectiveEnum(str, Enum):
    CONCENTRATION = "concentration"
    STRESS_REDUCTION = "stress_reduction"


class SessionStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    INTERRUPTED = "interrupted"


class BlockMetrics(BaseModel):
    """Métriques d'un bloc de 3 minutes"""
    block: int
    score: float = Field(..., ge=0, le=100)
    success_rate: float = Field(..., ge=0, le=1)
    threshold: float
    avg_alpha: Optional[float] = None
    avg_beta: Optional[float] = None
    avg_theta: Optional[float] = None


class SessionCreate(BaseModel):
    """Schéma pour démarrer une session (POST /sessions)"""
    objective: SessionObjectiveEnum = SessionObjectiveEnum.CONCENTRATION


class SessionResponse(BaseModel):
    """Schéma de réponse session (GET /sessions/{id})"""
    id: str
    user_id: str
    session_number: int
    objective: str
    status: str
    session_score: Optional[float] = None
    avg_tbr: Optional[float] = None
    success_rate: Optional[float] = None
    blocks_history: Optional[List[BlockMetrics]] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EEGStreamData(BaseModel):
    """
    Données EEG en streaming (WebSocket - émises chaque 500ms)
    Format JSON émis vers le frontend
    """
    timestamp: datetime
    p_concentration: float = Field(..., ge=0, le=1, description="P(Concentration)")
    p_stress: float = Field(..., ge=0, le=1, description="P(Stress)")
    p_alpha: Optional[float] = None
    p_beta: Optional[float] = None
    p_theta: Optional[float] = None
    tbr: Optional[float] = None
    signal_quality: float = Field(..., ge=0, le=1, description="0-1: Qualité du signal")
    model_latency_ms: float = Field(..., description="Latence de l'inférence IA (ms)")