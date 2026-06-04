"""
NeuroCap — Moteur du protocole 15 séances
Phases, paliers, seuils adaptatifs, critères d'arrêt.
Basé sur Mou et al. 2024, Wu et al. 2022, Bazanova & Aftanas 2010.
"""

from __future__ import annotations
from datetime import datetime
from statistics import mean
from typing import Optional

# ── Structure du protocole ────────────────────────────────────────────────────

PROTOCOL_PHASES = {
    1: {"sessions": range(1, 4),   "freq_per_week": 1, "min_interval_days": 5},
    2: {"sessions": range(4, 11),  "freq_per_week": 2, "min_interval_days": 2},
    3: {"sessions": range(11, 16), "freq_per_week": 2, "min_interval_days": 2},
}

BILAN_SESSIONS = {5, 10, 15}

MIN_INTERVAL_ABSOLUTE_H = 48   # jamais moins de 48h entre deux séances


def get_phase(session_number: int) -> int:
    if session_number <= 3:   return 1
    if session_number <= 10:  return 2
    return 3


def get_min_interval_days(session_number: int) -> int:
    return PROTOCOL_PHASES[get_phase(session_number)]["min_interval_days"]


def can_start_session(
    next_session_number: int,
    last_completed_at: Optional[datetime],
) -> tuple[bool, str]:
    """Vérifie l'intervalle minimal avant de démarrer la séance N."""
    if last_completed_at is None:
        return True, ""

    elapsed_h = (datetime.utcnow() - last_completed_at).total_seconds() / 3600

    if elapsed_h < MIN_INTERVAL_ABSOLUTE_H:
        return False, (
            f"Intervalle minimal absolu de 48h non respecté "
            f"({elapsed_h:.0f}h écoulées)"
        )

    min_h = get_min_interval_days(next_session_number) * 24
    if elapsed_h < min_h:
        return False, (
            f"Intervalle minimal de {min_h // 24} jours non respecté "
            f"pour la phase {get_phase(next_session_number)} "
            f"({elapsed_h:.0f}h/{min_h:.0f}h)"
        )

    return True, ""


# ── Configuration des paliers ─────────────────────────────────────────────────

PALIER_CONFIG = {
    "P1": {
        "alpha_target_min_pct": 0.85,
        "alpha_target_max_pct": 0.95,
        "threshold_step":        1.0,
        "feedback_types":       ["audio"],
        "game_enabled":          False,
        "visual_enabled":        False,
        "breathing_guide":       False,
    },
    "P2": {
        "alpha_target_min_pct": 0.95,
        "alpha_target_max_pct": 1.10,
        "threshold_step":        0.5,
        "feedback_types":       ["audio", "image", "breathing"],
        "game_enabled":          True,
        "visual_enabled":        True,
        "breathing_guide":       True,
    },
    "P3": {
        "alpha_target_min_pct": 1.10,
        "alpha_target_max_pct": 1.25,
        "threshold_step":        0.3,
        "feedback_types":       ["audio", "image", "video", "game"],
        "game_enabled":          True,
        "visual_enabled":        True,
        "breathing_guide":       True,
    },
    "P4": {
        "alpha_target_min_pct": 1.25,
        "alpha_target_max_pct": 1.40,
        "threshold_step":        0.2,
        "feedback_types":       ["game", "image"],
        "game_enabled":          True,
        "visual_enabled":        True,
        "breathing_guide":       False,
    },
}

PALIERS_THETA = {
    "P1": {"min": 0.20, "max": 0.45, "step": 1.0},
    "P2": {"min": 0.40, "max": 0.60, "step": 0.5},
    "P3": {"min": 0.55, "max": 0.75, "step": 0.3},
    "P4": {"min": 0.70, "max": 0.90, "step": 0.2},
}

PALIER_ORDER = ["P1", "P2", "P3", "P4"]


# ── Adaptation inter-blocs ────────────────────────────────────────────────────

def adapt_threshold_after_bloc(
    current_threshold: float,
    bloc_success_rate: float,
    palier: str,
    bloc_theta_power: float,
    baseline_theta: float,
) -> tuple[float, str]:
    """
    Retourne (new_threshold, action_reason).
    Règle Mou et al. 2024 + détection fatigue thêta.
    """
    step  = PALIERS_THETA[palier]["step"]
    p_min = PALIERS_THETA[palier]["min"]
    p_max = PALIERS_THETA[palier]["max"]

    if bloc_theta_power > 2.0 * baseline_theta:
        return current_threshold, "fatigue_detected"

    if bloc_success_rate > 0.60:
        new_thr = min(current_threshold + step, p_max)
        reason  = f"succès {bloc_success_rate*100:.0f}% > 60 % → seuil +{step}"
    elif bloc_success_rate < 0.40:
        new_thr = max(current_threshold - step, p_min)
        reason  = f"succès {bloc_success_rate*100:.0f}% < 40 % → seuil -{step}"
    else:
        new_thr = current_threshold
        reason  = f"succès {bloc_success_rate*100:.0f}% ∈ [40–60 %] → seuil stable"

    return round(new_thr, 3), reason


# ── Adaptation inter-séances (palier) ─────────────────────────────────────────

def evaluate_palier_progression(
    recent_sessions: list[dict],
    current_palier: str,
) -> tuple[str, str]:
    """
    Évalue si le palier doit monter, descendre ou rester.
    Règle montée  : succès moyen ≥ 65 % sur 3 séances consécutives.
    Règle descente : succès moyen < 35 % sur 2 séances consécutives.
    """
    idx = PALIER_ORDER.index(current_palier)

    if len(recent_sessions) >= 3:
        avg_3 = mean((s.get("success_rate") or 0.0) for s in recent_sessions[-3:])
        if avg_3 >= 0.65 and idx < 3:
            return (
                PALIER_ORDER[idx + 1],
                f"succès moyen {avg_3*100:.0f} % ≥ 65 % sur 3 séances → montée palier",
            )

    if len(recent_sessions) >= 2:
        avg_2 = mean((s.get("success_rate") or 0.0) for s in recent_sessions[-2:])
        if avg_2 < 0.35 and idx > 0:
            return (
                PALIER_ORDER[idx - 1],
                f"succès moyen {avg_2*100:.0f} % < 35 % sur 2 séances → retour palier",
            )

    return current_palier, "palier stable"


# ── Score de séance ───────────────────────────────────────────────────────────

def compute_session_score(
    blocs_success_rate: list[float],
    ml_confidence_avg: float,
) -> int:
    """Score 0–100 (70 % blocs + 30 % confiance ML)."""
    avg_success = mean(blocs_success_rate) if blocs_success_rate else 0.0
    score = int(avg_success * 70 + ml_confidence_avg * 30)
    return max(0, min(100, score))


# ── Critères d'arrêt anticipé ─────────────────────────────────────────────────

def check_early_stop_criteria(
    recent_5_sessions: list[dict],
    recent_3_sessions: list[dict],
    theta_fatigue_rate: float,
    subjective_score_avg: float,
) -> tuple[bool, str]:
    """
    Vérifie les 4 critères d'arrêt anticipé.
    Retourne (should_stop, reason).
    """
    # 1 — Aucune progression sur 5 séances
    if len(recent_5_sessions) >= 5:
        scores = [s["score"] for s in recent_5_sessions]
        if max(scores) - min(scores) < 5 and mean(scores) < 50:
            return True, (
                "Absence de progression sur 5 séances consécutives — "
                "consultation encadrant recommandée"
            )

    # 2 — Fatigue EEG excessive
    if theta_fatigue_rate > 0.50:
        return True, (
            "Fatigue EEG excessive (thêta > 3× baseline > 50 % du temps) — "
            "espacement à 1 séance/semaine requis"
        )

    # 3 — Bien-être subjectif trop bas
    if len(recent_3_sessions) >= 3:
        welfare = [s.get("subjective_welfare", 5) for s in recent_3_sessions]
        if mean(welfare) < 4.0:
            return True, (
                "Score de bien-être post-séance < 4/10 sur 3 séances — "
                "arrêt et révision du protocole"
            )

    # 4 — Artefacts non contrôlables
    if len(recent_3_sessions) >= 1:
        artifacts = [s.get("artifact_rate", 0) for s in recent_3_sessions]
        if mean(artifacts) > 0.40:
            return True, (
                "Taux d'artefacts EEG > 40 % — vérification matérielle requise"
            )

    return False, ""


# ── Helpers ───────────────────────────────────────────────────────────────────

def build_session_config(
    session_number: int,
    palier: str,
    p_alpha_ref: float,
) -> dict:
    """Retourne la configuration complète d'une séance (seuils, types feedback)."""
    phase  = get_phase(session_number)
    cfg    = PALIER_CONFIG[palier]
    is_bil = session_number in BILAN_SESSIONS

    return {
        "session_number":   session_number,
        "phase":            phase,
        "palier":           palier,
        "is_bilan":         is_bil,
        "bilan_type":       f"B{[5,10,15].index(session_number)+1}" if is_bil else None,
        "n_blocs":          6,
        "bloc_duration_s":  180,
        "inter_bloc_s":     20,
        "rest_pre_s":       120,   # repos yeux fermés au début
        "rest_post_s":      180,   # repos guidé final
        "alpha_target_min": round(p_alpha_ref * cfg["alpha_target_min_pct"], 6),
        "alpha_target_max": round(p_alpha_ref * cfg["alpha_target_max_pct"], 6),
        "threshold_step":   cfg["threshold_step"],
        "feedback_types":   cfg["feedback_types"],
        "game_enabled":     cfg["game_enabled"],
        "visual_enabled":   cfg["visual_enabled"],
        "breathing_guide":  cfg["breathing_guide"],
        "min_interval_days": get_min_interval_days(session_number),
    }
