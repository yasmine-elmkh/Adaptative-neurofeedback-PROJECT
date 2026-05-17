"""
NeuroCap — Service de Traitement du Signal EEG
================================================
Pipeline de prétraitement temps réel (CdC Section 2.1) :
  Signal brut → Filtrage → Normalisation → Extraction features

Budget latence : < 150ms pour le prétraitement + < 40ms pour les features
= 190ms total (objectif CdC : < 250ms pour prétraitement + features)

Étapes :
  1. Filtre passe-bande Butterworth 0.5-45 Hz (zéro-phase)
  2. Filtre Notch 50 Hz (réseau électrique marocain)
  3. Normalisation z-score par epoch
  4. Détection d'artefacts (amplitude > 150 µV)
  5. Extraction des features : PSD, ratios cognitifs, Hjorth
"""

import numpy as np
from scipy import signal as scipy_signal
from typing import Dict, Optional, Tuple

# ── Constantes EEG ───────────────────────────────────────────────────────
FS = 250  # Fréquence d'échantillonnage (Hz)

# Bandes de fréquence EEG standard
BANDS = {
    "delta": (0.5, 4),    # δ — sommeil profond
    "theta": (4, 8),      # θ — somnolence, méditation
    "alpha": (8, 13),     # α — repos éveillé, relaxation
    "beta":  (13, 30),    # β — attention, concentration
    "gamma": (30, 45),    # γ — traitement cognitif complexe
}

# Sous-bande high-beta (indicateur de stress)
HIGH_BETA = (20, 30)

# Seuil de rejet d'artefact (µV)
ARTIFACT_THRESHOLD = 150.0


# ============================================================================
# FILTRAGE NUMÉRIQUE
# ============================================================================

def design_bandpass(lowcut: float = 0.5, highcut: float = 45.0, order: int = 4):
    """
    Conçoit un filtre passe-bande Butterworth.

    Paramètres :
        lowcut  : fréquence de coupure basse (Hz)
        highcut : fréquence de coupure haute (Hz)
        order   : ordre du filtre (4 = bon compromis pente/stabilité)

    Retourne : coefficients (b, a) du filtre IIR
    """
    nyq = FS / 2.0
    b, a = scipy_signal.butter(order, [lowcut / nyq, highcut / nyq], btype="band")
    return b, a


def design_notch(freq: float = 50.0, quality: float = 30.0):
    """
    Conçoit un filtre coupe-bande (Notch) pour supprimer le 50 Hz.

    Le réseau électrique marocain est à 50 Hz (norme européenne).
    Ce filtre supprime le bruit secteur sans affecter le signal EEG.

    quality : facteur de qualité (plus élevé = filtre plus étroit)
    """
    b, a = scipy_signal.iirnotch(freq, quality, FS)
    return b, a


# Pré-calculer les coefficients (appelé une seule fois au démarrage)
_bp_b, _bp_a = design_bandpass()
_notch_b, _notch_a = design_notch()


def filter_epoch(epoch: np.ndarray) -> np.ndarray:
    """
    Applique le pipeline de filtrage complet sur un epoch EEG.

    Pipeline :
      1. Passe-bande Butterworth 0.5-45 Hz (supprime dérive DC + HF)
      2. Notch 50 Hz (supprime le bruit secteur)

    filtfilt = filtre zéro-phase (pas de décalage temporel)

    Paramètres :
        epoch : array (N,) — signal brut d'un epoch

    Retourne : array (N,) — signal filtré
    """
    # Passe-bande
    filtered = scipy_signal.filtfilt(_bp_b, _bp_a, epoch)
    # Notch 50 Hz
    filtered = scipy_signal.filtfilt(_notch_b, _notch_a, filtered)
    return filtered


# ============================================================================
# NORMALISATION
# ============================================================================

def zscore_epoch(epoch: np.ndarray) -> np.ndarray:
    """
    Normalisation z-score : (x - mean) / std.

    Centre le signal autour de 0 et normalise la variance à 1.
    Indispensable pour que le modèle DL reçoive des valeurs comparables
    entre sujets et sessions (CdC Section 2.1, étape 5).
    """
    std = np.std(epoch)
    if std < 1e-10:
        return np.zeros_like(epoch)
    return (epoch - np.mean(epoch)) / std


# ============================================================================
# DÉTECTION D'ARTEFACTS
# ============================================================================

def detect_artifact(epoch: np.ndarray, threshold: float = ARTIFACT_THRESHOLD) -> bool:
    """
    Détecte si un epoch contient un artefact (mouvement, clignement).

    Critère simple : amplitude maximale > seuil (150 µV par défaut).
    Les epochs artefactés sont exclus du feedback mais enregistrés
    en base avec is_artifact=True.

    Retourne : True si artefact détecté
    """
    return bool(np.max(np.abs(epoch)) > threshold)


# ============================================================================
# EXTRACTION DE FEATURES (CdC Section 2.3)
# ============================================================================

def compute_psd(epoch: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calcule la densité spectrale de puissance (PSD) par la méthode de Welch.

    Welch : découpe le signal en segments, applique une fenêtre de Hann,
    calcule le FFT de chaque segment et moyenne les résultats.
    → Estimation robuste et lissée de la PSD.

    Retourne : (freqs, psd) — vecteurs de fréquences et de puissance
    """
    freqs, psd = scipy_signal.welch(
        epoch, fs=FS,
        nperseg=min(256, len(epoch)),  # taille du segment
        noverlap=128,                  # overlap 50%
        window="hann",
    )
    return freqs, psd


def compute_band_powers(freqs: np.ndarray, psd: np.ndarray) -> Dict[str, float]:
    """
    Calcule la puissance dans chaque bande de fréquence EEG.

    Intègre la PSD sur chaque bande (trapèze numérique).
    Retourne les puissances absolues en µV²/Hz.
    """
    powers = {}
    for band_name, (f_low, f_high) in BANDS.items():
        mask = (freqs >= f_low) & (freqs <= f_high)
        if np.any(mask):
            powers[band_name] = float(np.trapz(psd[mask], freqs[mask]))
        else:
            powers[band_name] = 0.0

    # High-beta (sous-bande stress)
    hb_mask = (freqs >= HIGH_BETA[0]) & (freqs <= HIGH_BETA[1])
    powers["high_beta"] = float(np.trapz(psd[hb_mask], freqs[hb_mask])) if np.any(hb_mask) else 0.0

    return powers


def compute_cognitive_ratios(powers: Dict[str, float]) -> Dict[str, float]:
    """
    Calcule les ratios cognitifs NeuroCap (CdC Section 2.3).

      TBR = θ/β      — Theta/Beta Ratio (attention/concentration)
      ABR = α/β      — Alpha/Beta Ratio (relaxation/activation)
      EI  = β/(α+θ)  — Engagement Index (engagement cognitif)

    Ces ratios sont les features les plus discriminantes pour
    la classification concentration/stress.
    """
    theta = powers.get("theta", 0.0)
    alpha = powers.get("alpha", 0.0)
    beta = powers.get("beta", 0.0)

    # Protection division par zéro
    eps = 1e-10

    return {
        "tbr": theta / (beta + eps),
        "abr": alpha / (beta + eps),
        "ei": beta / (alpha + theta + eps),
    }


def compute_hjorth(epoch: np.ndarray) -> Dict[str, float]:
    """
    Calcule les paramètres de Hjorth (features temporelles).

      Activité   : variance du signal (énergie)
      Mobilité   : fréquence moyenne (pente spectrale)
      Complexité : largeur de bande (régularité)

    Ces paramètres temporels complètent les features fréquentielles
    et sont très rapides à calculer (< 1ms).
    """
    # Activité = variance
    activity = float(np.var(epoch))

    # Dérivée première
    d1 = np.diff(epoch)
    d1_var = np.var(d1)

    # Dérivée seconde
    d2 = np.diff(d1)
    d2_var = np.var(d2)

    eps = 1e-10

    # Mobilité = sqrt(var(d1) / var(signal))
    mobility = float(np.sqrt(d1_var / (activity + eps)))

    # Complexité = mobilité(d1) / mobilité(signal)
    mobility_d1 = float(np.sqrt(d2_var / (d1_var + eps)))
    complexity = mobility_d1 / (mobility + eps)

    return {
        "activity": activity,
        "mobility": mobility,
        "complexity": complexity,
    }


def compute_iapf(freqs: np.ndarray, psd: np.ndarray) -> float:
    """
    Calcule l'Individual Alpha Peak Frequency (IAPF).

    L'IAPF est la fréquence où la PSD est maximale dans la bande alpha
    (7-13 Hz). C'est un marqueur neurophysiologique individuel stable
    qui personnalise les seuils du moteur adaptatif.

    Retourne : fréquence du pic alpha (Hz), ou 10.0 par défaut
    """
    alpha_mask = (freqs >= 7) & (freqs <= 13)
    if not np.any(alpha_mask):
        return 10.0  # valeur par défaut

    alpha_freqs = freqs[alpha_mask]
    alpha_psd = psd[alpha_mask]

    return float(alpha_freqs[np.argmax(alpha_psd)])


# ============================================================================
# PIPELINE COMPLET (appelé toutes les 500ms)
# ============================================================================

def process_epoch(raw_epoch: np.ndarray) -> Dict:
    """
    Pipeline complet de traitement d'un epoch EEG.

    Entrée : signal brut (1000 échantillons = 4s à 250Hz)
    Sortie : dictionnaire avec toutes les features extraites

    Pipeline :
      1. Filtrage (Butterworth + Notch)
      2. Détection d'artefact
      3. Normalisation z-score
      4. PSD (Welch)
      5. Puissances par bande
      6. Ratios cognitifs (TBR, ABR, EI)
      7. Paramètres de Hjorth
      8. IAPF

    Temps d'exécution typique : < 10ms sur CPU
    """
    # 1. Filtrage
    filtered = filter_epoch(raw_epoch)

    # 2. Détection d'artefact (sur le signal filtré)
    is_artifact = detect_artifact(filtered)

    # 3. Normalisation z-score
    normalized = zscore_epoch(filtered)

    # 4-5. PSD et puissances par bande
    freqs, psd = compute_psd(filtered)
    powers = compute_band_powers(freqs, psd)

    # 6. Ratios cognitifs
    ratios = compute_cognitive_ratios(powers)

    # 7. Paramètres de Hjorth
    hjorth = compute_hjorth(filtered)

    # 8. IAPF
    iapf = compute_iapf(freqs, psd)

    # Score de qualité du signal (basé sur le SNR)
    total_power = sum(powers.values())
    noise_power = powers.get("gamma", 0) + powers.get("delta", 0)
    signal_quality = max(0, min(100, (1 - noise_power / (total_power + 1e-10)) * 100))

    return {
        "normalized_epoch": normalized,
        "is_artifact": is_artifact,
        "powers": powers,
        "ratios": ratios,
        "hjorth": hjorth,
        "iapf": iapf,
        "signal_quality": round(signal_quality, 1),
    }