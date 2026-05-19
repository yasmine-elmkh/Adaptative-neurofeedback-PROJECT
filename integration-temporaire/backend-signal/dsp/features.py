# backend/dsp/features.py
"""
Extraction de features EEG spectrales, temporelles et de complexité.

Changements vs original :
  - Bandes : delta 1-4 Hz, theta 6-8 Hz (pas 4-8), gamma_low 30-45 Hz
  - Normalisation : toutes puissances relatives à P_total(1-45 Hz)
  - RMS sur epoch_ac centré (pas epoch brut avec DC offset)
  - Graphe fractal supprimé (vecteur constant → bruit pur)
  - PAC proxy supprimé (non conforme Tort 2010)
  - Entropie spectrale normalisée par log2(N_bins) → valeur 0-1
  - Ratios cognitifs sur P_rel uniquement

Ref : Cohen 2014 ch.10-19 (Hjorth, Welch, entropie)
      Higuchi 1988, Kesić & Spasić 2016, Li et al. 2024 (HFD)
      Klimesch 1999 (bandes cognitives)
      Goncharova 2003 (flag EMG)
"""

import numpy as np
from scipy.signal import welch
from scipy.stats  import skew, kurtosis as scipy_kurtosis
from utils.constants import FS


# ═══════════════════════════════════════════════════════════════════
# BANDES v8.0
# ═══════════════════════════════════════════════════════════════════
#
# Theta : 6-8 Hz (pas 4-8 Hz)
#   4-6 Hz contaminé par drift électrode sèche + EOG résiduel.
#   Theta cognitif frontal se situe dans 6-8 Hz.
#   Ref : Klimesch 1999, Ratti et al. 2017
#
# Delta : 1-4 Hz (pas 0.5-4 Hz)
#   HP 1 Hz supprime le drift de polarisation < 1 Hz.
#
# Gamma-bas : 30-45 Hz (pas 30-40 Hz)
#   BP 45 Hz donne accès à tout le gamma-bas.
#   ATTENTION : 35-45 Hz aussi utilisé comme flag EMG.

BANDS_V8 = {
    "delta":      (1.0,  4.0),
    "theta":      (6.0,  8.0),
    "alpha":      (8.0, 13.0),
    "beta":       (13.0, 30.0),
    "beta_high":  (20.0, 30.0),
    "gamma_low":  (30.0, 45.0),
}

TOTAL_BAND   = (1.0, 45.0)
EMG_FLAG_BAND = (35.0, 45.0)


# ═══════════════════════════════════════════════════════════════════
# HIGUCHI FRACTAL DIMENSION
# ═══════════════════════════════════════════════════════════════════

def higuchi_fd(signal: np.ndarray, kmax: int = 8) -> float:
    """
    Higuchi Fractal Dimension — monocanal EEG.
    kmax=8 recommandé pour FS=250 Hz, fenêtre 4 s.

    Valeurs de référence (Fp2, éveillé yeux ouverts) :
      HFD 1.8-2.2 → signal cortical normal
      HFD < 1.5   → trop régulier (artefact / saturation)
      HFD > 2.5   → très irrégulier (EMG / mouvement)

    Ref : Higuchi 1988, Kesić & Spasić 2016, Li et al. 2024
    """
    n  = len(signal)
    lk = np.zeros(kmax)

    for k in range(1, kmax + 1):
        lm = np.zeros(k)
        for m in range(1, k + 1):
            n_max = int(np.floor((n - m) / k))
            if n_max < 2:
                lm[m - 1] = 0.0
                continue
            indices  = np.arange(m - 1, m - 1 + n_max * k, k)
            if len(indices) + 1 <= n:
                diff_sum = np.sum(np.abs(np.diff(signal[indices])))
            else:
                diff_sum = 0.0
            lm[m - 1] = (diff_sum * (n - 1) / (n_max * k)) / k
        lk[k - 1] = np.mean(lm[lm > 0]) if np.any(lm > 0) else 0.0

    valid = lk > 0
    if valid.sum() < 2:
        return 1.5   # valeur neutre si calcul impossible

    log_k = np.log(np.arange(1, kmax + 1)[valid])
    log_l = np.log(lk[valid])
    try:
        slope, _ = np.polyfit(log_k, log_l, 1)
        return round(float(-slope), 4)
    except Exception:
        return 1.5


# ═══════════════════════════════════════════════════════════════════
# SEF95
# ═══════════════════════════════════════════════════════════════════

def compute_sef95(psd: np.ndarray, freqs: np.ndarray) -> float:
    """
    Fréquence sous laquelle se trouve 95 % de la puissance totale.
    Ref. : Duffy et al. 1994.
    """
    try:
        cumsum = np.cumsum(psd)
        total  = cumsum[-1]
        if total < 1e-30:
            return 0.0
        idx = np.searchsorted(cumsum, 0.95 * total)
        return round(float(freqs[min(idx, len(freqs) - 1)]), 2)
    except Exception:
        return 0.0


# ═══════════════════════════════════════════════════════════════════
# EXTRACTION FEATURES PRINCIPALE
# ═══════════════════════════════════════════════════════════════════

def extract_features(epoch_filtered: np.ndarray,
                     db_powers:      dict,
                     emg_ratio:      float = 0.0) -> dict:
    """
    Extrait toutes les features sur une époque filtrée et centrée.

    Paramètres
    ----------
    epoch_filtered : np.ndarray
        Signal post-filtrage Golden Filter (déjà centré autour de 0).
    db_powers : dict
        Puissances normalisées en dB vs baseline (PreprocessingPipeline).
    emg_ratio : float
        Ratio EMG brut de l'ArtifactDetector (transmis au frontend).

    Retourne
    --------
    dict — vecteur de 25+ features.

    IMPORTANT : epoch_filtered doit être centré (DC ≈ 0).
    filter_epoch() fait déjà la soustraction médiane.
    On soustrait la moyenne ici pour neutraliser toute dérive résiduelle.
    """

    # Centrage final (sécurité)
    epoch_ac = epoch_filtered - np.mean(epoch_filtered)

    # Garde 1 : si std > 10000 µV → DC non supprimé, passer à la médiane (Widmann 2015)
    if float(np.std(epoch_ac)) > 10000.0:
        epoch_ac = epoch_filtered - np.median(epoch_filtered)

    # Garde 2 : si encore > 5000 µV → époque irrécupérable, retourner features neutres
    if float(np.std(epoch_ac)) > 5000.0:
        return {
            "rms_uv": 0.0, "mean_amp": 0.0,
            "rel_delta": 0.2, "rel_theta": 0.2,
            "rel_alpha": 0.2, "rel_beta": 0.2,
            "rel_gamma_low": 0.2,
            "engagement": 0.0, "stress_idx": 0.0,
            "theta_alpha": 0.0, "alpha_beta": 0.0,
            "hjorth_activity": 0.0, "hjorth_mobility": 0.0,
            "hjorth_complexity": 0.0,
            "fractal_dim": 1.5, "spectral_entropy": 0.0,
            "sef95": 0.0, "skewness": 0.0,
            "kurtosis": 0.0, "zcr": 0.0,
            "emg_ratio": 0.0, "pac_theta_gamma": 0.0,
        }

    n = len(epoch_ac)

    # ── Estimateur de Welch ──────────────────────────────────────
    # nperseg = FS = 1 s → résolution fréquentielle = 1.0 Hz
    # Ref : Cohen 2014 ch.11, Stoica & Moses 2005
    f, psd = welch(
        epoch_ac, FS,
        nperseg  = min(FS, n),
        noverlap = min(FS // 2, n // 2),
        window   = "hann",
        scaling  = "density",
        detrend  = "constant",
    )

    # ── Puissances par bande ─────────────────────────────────────

    def bp(lo: float, hi: float) -> float:
        mask = (f >= lo) & (f <= hi)
        return float(np.trapezoid(psd[mask], f[mask])) if mask.any() else 0.0

    p_delta     = bp(1.0,  4.0)
    p_theta     = bp(6.0,  8.0)   # theta cognitif 6-8 Hz
    p_alpha     = bp(8.0,  13.0)
    p_beta      = bp(13.0, 30.0)
    p_beta_high = bp(20.0, 30.0)
    p_gamma_low = bp(30.0, 45.0)
    p_total     = bp(1.0,  45.0) + 1e-30

    # Puissances relatives — OBLIGATOIRE pour électrodes à impédance variable
    # P_rel stable à ±10 % malgré variations impédance 10-200 kΩ
    # Ref : Liao et al. 2012
    rel_delta     = round(p_delta     / p_total, 5)
    rel_theta     = round(p_theta     / p_total, 5)
    rel_alpha     = round(p_alpha     / p_total, 5)
    rel_beta      = round(p_beta      / p_total, 5)
    rel_beta_high = round(p_beta_high / p_total, 5)
    rel_gamma_low = round(p_gamma_low / p_total, 5)

    # ── Ratios cognitifs (sur P_rel uniquement) ──────────────────
    # Ref : Pope et al. 1995, Gevins & Smith 2003, Klimesch 1999
    # NOTE : valables uniquement en comparaison intra-sujet vs baseline.
    engagement  = round(rel_beta / (rel_alpha + rel_theta + 1e-30), 4)
    stress_idx  = round(rel_beta_high / (rel_alpha + 1e-30), 4)
    theta_alpha = round(rel_theta / (rel_alpha + 1e-30), 4)
    alpha_beta  = round(rel_alpha / (rel_beta  + 1e-30), 4)

    # ── Paramètres Hjorth ────────────────────────────────────────
    # Calculés sur epoch_ac (signal centré post-filtrage)
    # Ref : Hjorth 1970, Cohen 2014 ch.11
    d1   = np.diff(epoch_ac)
    d2   = np.diff(d1)
    var0 = float(np.var(epoch_ac)) + 1e-30
    var1 = float(np.var(d1))       + 1e-30
    var2 = float(np.var(d2))       + 1e-30
    mob  = float(np.sqrt(var1 / var0))
    comp = float(np.sqrt(var2 / var1) / mob) if mob > 0 else 0.0

    # ── Entropie spectrale normalisée ────────────────────────────
    # Normalisée par log2(N_bins) → valeur entre 0 et 1
    # > 0.9 : spectre diffus (EMG/bruit) ; < 0.6 : pic dominant
    psd_n    = psd / (psd.sum() + 1e-30)
    n_bins   = len(psd)
    s_entr   = float(-np.sum(psd_n * np.log2(psd_n + 1e-30)))
    s_entr_n = round(s_entr / np.log2(n_bins), 4) if n_bins > 1 else 0.0

    # ── SEF95 ────────────────────────────────────────────────────
    sef95 = compute_sef95(psd, f)

    # ── HFD Higuchi ──────────────────────────────────────────────
    hfd = higuchi_fd(epoch_ac, kmax=8)

    # ── RMS corrigé ──────────────────────────────────────────────
    # Sur epoch_ac centré → valeur physiologique 2-50 µV au repos
    # BUG original : np.sqrt(np.mean(epoch**2)) avec DC ~1 650 000 µV
    rms_uv   = round(float(np.sqrt(np.mean(epoch_ac ** 2))), 4)
    mean_amp = round(float(np.mean(np.abs(epoch_ac))),        4)

    # ── Distribution temporelle ──────────────────────────────────
    skewness = round(float(skew(epoch_ac)),              4)
    kurtosis = round(float(scipy_kurtosis(epoch_ac)),    4)
    zcr      = round(float(np.mean(np.diff(np.sign(epoch_ac)) != 0)), 4)

    # ── PAC θ→γ proxy (Tort et al. 2010 — corrélation enveloppe) ──
    try:
        from scipy.signal import butter, filtfilt, hilbert
        b_t, a_t = butter(4, [6.0 / (FS / 2), 8.0 / (FS / 2)],   btype='band')
        theta_sig = filtfilt(b_t, a_t, epoch_ac)
        b_g, a_g = butter(4, [30.0 / (FS / 2), 45.0 / (FS / 2)], btype='band')
        gamma_sig = filtfilt(b_g, a_g, epoch_ac)
        theta_phase = np.angle(hilbert(theta_sig))
        gamma_env   = np.abs(hilbert(gamma_sig))
        pac_proxy   = float(np.abs(np.mean(gamma_env * np.exp(1j * theta_phase))))
        gamma_mean  = float(np.mean(gamma_env)) + 1e-30
        pac_proxy   = round(pac_proxy / gamma_mean, 4)
    except Exception:
        pac_proxy = 0.0

    # ── Assemblage ───────────────────────────────────────────────
    return {
        # Puissances relatives
        "rel_delta":     rel_delta,
        "rel_theta":     rel_theta,
        "rel_alpha":     rel_alpha,
        "rel_beta":      rel_beta,
        "rel_beta_high": rel_beta_high,
        "rel_gamma_low": rel_gamma_low,
        # Ratios cognitifs (intra-sujet uniquement)
        "engagement":    engagement,
        "stress_idx":    stress_idx,
        "theta_alpha":   theta_alpha,
        "alpha_beta":    alpha_beta,
        # Hjorth
        "hjorth_activity":   round(var0, 4),
        "hjorth_mobility":   round(mob,  4),
        "hjorth_complexity": round(comp, 4),
        # Complexité non-linéaire (HFD remplace graphe fractal dégénéré)
        "fractal_dim":   hfd,
        # Spectral
        "spectral_entropy": s_entr_n,
        "sef95":            sef95,
        # Amplitude (sur signal AC centré)
        "rms_uv":   rms_uv,
        "mean_amp": mean_amp,
        # Distribution
        "skewness": skewness,
        "kurtosis": kurtosis,
        "zcr":      zcr,
        # PAC couplage phase-amplitude θ→γ
        "pac_theta_gamma": pac_proxy,
        # Contrôle qualité (transmis au frontend)
        "emg_ratio": round(emg_ratio, 4),
        # dB vs baseline
        **{f"db_{k}": round(v, 3) for k, v in db_powers.items()},
    }