"""
NeuroCap — Service de calibration individuelle (Séance 1)
Calculs : IAPF, P_alpha_ref, ERD, TBR, profil A/B/C.
Références : Bazanova & Aftanas 2010, Mou et al. 2024.
"""

from __future__ import annotations
import logging
from statistics import mean
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


# ── Calcul IAPF (Individual Alpha Peak Frequency) ────────────────────────────

def compute_iapf(epochs: list[dict]) -> float:
    """
    Calcule l'IAPF à partir des époques EEG repos yeux fermés (C1).
    Cherche le pic spectral dans la fenêtre 7–13 Hz via Welch PSD.
    Retourne 10.0 Hz par défaut si calcul impossible.
    """
    try:
        from scipy.signal import welch

        all_signals = []
        for ep in epochs:
            sig = ep.get("raw_signal") or ep.get("signal")
            if sig is not None:
                all_signals.extend(sig if isinstance(sig, list) else [sig])

        if len(all_signals) < 64:
            return 10.0

        x  = np.array(all_signals, dtype=float)
        fs = 250   # Hz — taux d'échantillonnage NeuroCap
        f, pxx = welch(x, fs=fs, nperseg=min(256, len(x)))

        # Fenêtre 7–13 Hz
        mask = (f >= 7.0) & (f <= 13.0)
        if not mask.any():
            return 10.0

        peak_idx = np.argmax(pxx[mask])
        iapf     = float(f[mask][peak_idx])
        return round(max(7.0, min(13.0, iapf)), 2)

    except Exception as e:
        logger.warning("IAPF calc failed: %s", e)
        return 10.0


# ── Extraction puissance alpha relative d'un lot d'époques ───────────────────

def _mean_feature(epochs: list[dict], key: str) -> float:
    vals = [
        ep.get("features", {}).get(key) or ep.get(key)
        for ep in epochs
    ]
    vals = [v for v in vals if v is not None]
    return mean(vals) if vals else 0.0


# ── Profil complet de calibration ────────────────────────────────────────────

def compute_calibration_profile(
    epochs_c1: list[dict],   # repos yeux fermés (5 min)
    epochs_c2: list[dict],   # repos yeux ouverts (5 min)
    epochs_c3: list[dict],   # tâche cognitive   (5 min)
    epochs_c4: list[dict],   # relaxation guidée (5 min)
    questionnaire: dict,
) -> dict:
    """
    Retourne le profil EEG individuel complet :
    p_alpha_ref, iapf, plage alpha, ERD, TBR, seuil initial, type A/B/C.
    """

    p_alpha_c1 = _mean_feature(epochs_c1, "rel_alpha")
    p_alpha_c2 = _mean_feature(epochs_c2, "rel_alpha")
    p_alpha_c4 = _mean_feature(epochs_c4, "rel_alpha")

    # P_alpha_ref = moyenne C1 et C4 (Bazanova & Aftanas 2010)
    p_alpha_ref = (p_alpha_c1 + p_alpha_c4) / 2

    # IAPF depuis C1
    iapf = compute_iapf(epochs_c1)
    alpha_lo = round(iapf - 2.0, 1)
    alpha_hi = round(iapf + 2.0, 1)

    # ERD : blocage alpha (C2 vs C1)
    erd_pct = 0.0
    if p_alpha_c1 > 1e-10:
        erd_pct = (p_alpha_c1 - p_alpha_c2) / p_alpha_c1 * 100
    erd_pct = round(erd_pct, 2)

    # TBR de référence (theta/beta C1)
    p_theta_ref = _mean_feature(epochs_c1, "rel_theta")
    p_beta_ref  = _mean_feature(epochs_c1, "rel_beta")
    tbr_ref     = p_theta_ref / (p_beta_ref + 1e-10)

    # Activation bêta tâche cognitive C3
    p_beta_c3 = _mean_feature(epochs_c3, "rel_beta")

    # Seuil initial S2 = P_alpha_ref × 0.95 (Mou et al. 2024)
    threshold_s2 = p_alpha_ref * 0.95

    # Classification profil
    alpha_beta_ratio = p_alpha_ref / (p_beta_ref + 1e-10)
    if   alpha_beta_ratio > 1.5 and erd_pct > 30:
        profile_type = "A"
    elif alpha_beta_ratio > 0.8 and erd_pct > 15:
        profile_type = "B"
    else:
        profile_type = "C"

    palier_initial = "P2" if profile_type == "A" else "P1"

    # Préférences sonores depuis questionnaire
    audio_pref = questionnaire.get("audio_preference", "nature")
    stress_level = questionnaire.get("stress_level", 5)
    focus_level  = questionnaire.get("focus_level",  5)
    meditation_exp = questionnaire.get("meditation_exp", "jamais")

    return {
        "p_alpha_ref":        round(p_alpha_ref, 6),
        "iapf":               round(iapf, 2),
        "alpha_band_lo":      alpha_lo,
        "alpha_band_hi":      alpha_hi,
        "erd_pct":            erd_pct,
        "tbr_ref":            round(tbr_ref, 4),
        "p_beta_cognitive":   round(p_beta_c3, 6),
        "threshold_s2":       round(threshold_s2, 6),
        "threshold_current":  round(threshold_s2, 6),
        "profile_type":       profile_type,
        "palier_initial":     palier_initial,
        "audio_preference":   audio_pref,
        "stress_baseline":    stress_level,
        "focus_baseline":     focus_level,
        "meditation_exp":     meditation_exp,
    }


# ── Recalibration inter-séances ───────────────────────────────────────────────

def compute_daily_threshold(
    p_alpha_ref_global: float,
    p_alpha_today: float,
) -> float:
    """
    Seuil du jour = 70 % historique + 30 % mesure du jour.
    Gère les variations circadiennes sans abandonner la ligne de base.
    """
    return round(0.70 * p_alpha_ref_global + 0.30 * p_alpha_today, 6)


# ── Questionnaire cognitif C6 ─────────────────────────────────────────────────

QUESTIONNAIRE_SCHEMA = {
    "concentration_habituelle": {"type": "int",    "min": 1, "max": 10},
    "stress_quotidien":         {"type": "int",    "min": 1, "max": 10},
    "motivation":               {"type": "int",    "min": 1, "max": 10},
    "meditation_exp":           {"type": "choice", "options": ["jamais", "parfois", "régulièrement"]},
    "audio_preference":         {"type": "choice", "options": ["bip", "nature", "musique"]},
    "audio_volume_pref":        {"type": "int",    "min": 1, "max": 5},
}


def validate_questionnaire(data: dict) -> tuple[bool, list[str]]:
    """Valide les réponses du questionnaire C6. Retourne (valid, errors)."""
    errors = []
    for key, schema in QUESTIONNAIRE_SCHEMA.items():
        val = data.get(key)
        if val is None:
            continue   # champs optionnels
        if schema["type"] == "int":
            if not isinstance(val, int) or not (schema["min"] <= val <= schema["max"]):
                errors.append(f"{key} doit être un entier entre {schema['min']} et {schema['max']}")
        elif schema["type"] == "choice":
            if val not in schema["options"]:
                errors.append(f"{key} doit être l'une des valeurs : {schema['options']}")
    return len(errors) == 0, errors
