# backend/dsp/artifacts.py
"""
Détection d'artefacts, monitoring électrodes, Contact Quality Estimator.

Ref : AD8232 datasheet §Lead-Off Detection
      Kanoga & Mitsukura 2017 §2.2
      Goncharova et al. 2003 (EMG ratio)
      Urigüen & Garcia-Zapirain 2015 (EOG)
      Jayant & Noll 1984 (Spectral Flatness Measure)
      Liao et al. 2012 (dry electrode impedance)
"""

import time
import numpy as np
import scipy.signal
import scipy.stats
from collections import deque
from utils.constants import FS


# ═══════════════════════════════════════════════════════════════════
# ELECTRODE MONITOR
# ═══════════════════════════════════════════════════════════════════

class ElectrodeMonitor:
    """
    Surveille le bit lead-off de l'AD8232.
      lo_plus==0 AND lo_minus==0  →  electrode_ok = True
      lo_plus==1 OR  lo_minus==1  →  electrode_ok = False

    LIMITATION : le bit LO est un seuil fixe ~40-100 kΩ.
    Une électrode tenue en main peut avoir LO=0 sans être sur le scalp.
    → Utiliser ContactQualityEstimator pour un diagnostic complet.
    """
    HEARTBEAT_INTERVAL = 0.5   # s — 2 heartbeats/s

    def __init__(self):
        self._lo_plus  = 1     # déconnecté par défaut (conservateur)
        self._lo_minus = 1
        self._last_hb  = 0.0

    def update(self, lo_plus: int, lo_minus: int):
        self._lo_plus  = int(lo_plus)
        self._lo_minus = int(lo_minus)

    @property
    def electrode_ok(self) -> bool:
        return (self._lo_plus == 0) and (self._lo_minus == 0)

    @property
    def lo_score(self) -> int:
        """Score LO partiel pour le CQE : 30 si connecté, 0 sinon."""
        return 30 if self.electrode_ok else 0

    @property
    def status_detail(self) -> dict:
        return {
            "electrode_ok":  self.electrode_ok,
            "fp2_connected": (self._lo_plus  == 0),
            "m2_connected":  (self._lo_minus == 0),
        }

    def should_send_heartbeat(self) -> bool:
        now = time.monotonic()
        if now - self._last_hb >= self.HEARTBEAT_INTERVAL:
            self._last_hb = now
            return True
        return False


# ═══════════════════════════════════════════════════════════════════
# CONTACT QUALITY ESTIMATOR (CQE)
# ═══════════════════════════════════════════════════════════════════

class ContactQualityEstimator:
    """
    Score 0-100 de qualité de contact électrode-peau.
    Fenêtre glissante de 2 s, mise à jour toutes les 500 ms.

    Score  < 40  → INVALID  : données rejetées
    Score 40-59  → POOR     : flag low_quality
    Score 60-79  → FAIR     : utilisable avec précautions
    Score  ≥ 80  → GOOD     : données fiables

    Critères (total 100 pts) :
      1. Bit LO AD8232              (0 ou 30 pts)
      2. Variance AC                (0-25 pts)
      3. Spectral Flatness Measure  (0-25 pts)
      4. Taux de dérive DC          (0-20 pts)

    Ref : Jayant & Noll 1984 (SFM), Liao et al. 2012
    """

    WINDOW_S = 2

    def __init__(self, fs: int = FS):
        self.fs     = fs
        self._buf   = deque(maxlen=fs * self.WINDOW_S)
        self._score = 0
        self._label = "invalid"
        self._detail = {}

    def push_sample(self, uv: float):
        """Appeler à chaque échantillon brut (250 Hz)."""
        self._buf.append(uv)

    def update(self, lo_score: int) -> int:
        """
        Recalcule le score. Appeler toutes les ~500 ms.

        lo_score : 0 ou 30, depuis ElectrodeMonitor.lo_score
        Retourne : int score 0-100
        """
        if len(self._buf) < self.fs // 2:
            self._score = 0
            self._label = "invalid"
            return 0

        epoch    = np.array(self._buf, dtype=float)
        epoch_ac = epoch - np.median(epoch)

        s_var   = self._score_variance(epoch_ac)
        s_sfm   = self._score_sfm(epoch_ac)
        s_drift = self._score_drift(epoch_ac)

        total = int(np.clip(lo_score + s_var + s_sfm + s_drift, 0, 100))

        self._score = total
        self._label = (
            "invalid" if total < 40 else
            "poor"    if total < 60 else
            "fair"    if total < 80 else
            "good"
        )
        self._detail = {
            "lo_score": lo_score, "var_score": s_var,
            "sfm_score": s_sfm,  "drift_score": s_drift,
        }
        return total

    @property
    def score(self) -> int:   return self._score
    @property
    def label(self) -> str:   return self._label
    @property
    def is_valid(self) -> bool: return self._score >= 40
    @property
    def is_good(self)  -> bool: return self._score >= 60
    @property
    def detail(self) -> dict: return dict(self._detail)

    def _score_variance(self, epoch_ac: np.ndarray) -> int:
        v = float(np.var(epoch_ac))
        if v < 1.0:       return 0
        elif v < 5.0:     return 10
        elif v <= 300.0:  return 25
        elif v <= 1000.0: return 15
        else:             return 0

    def _score_sfm(self, epoch_ac: np.ndarray) -> int:
        try:
            f, psd = scipy.signal.welch(
                epoch_ac, self.fs, nperseg=min(self.fs, len(epoch_ac)))
            mask  = (f >= 1.0) & (f <= 45.0)
            psd_b = psd[mask]
            if len(psd_b) < 3 or psd_b.sum() < 1e-20:
                return 0
            sfm = float(
                np.exp(np.mean(np.log(psd_b + 1e-30)))
                / (np.mean(psd_b) + 1e-30)
            )
        except Exception:
            return 0
        if sfm > 0.7:   return 0
        elif sfm > 0.4: return 10
        else:           return 25

    def _score_drift(self, epoch_ac: np.ndarray) -> int:
        try:
            t     = np.arange(len(epoch_ac)) / self.fs
            slope = float(np.polyfit(t, epoch_ac, 1)[0])
            drift = abs(slope)
            var   = float(np.var(epoch_ac))
        except Exception:
            return 0
        if drift < 2.0:
            return 20 if (5.0 < var < 300.0) else 5
        elif drift < 50.0:   return 15
        elif drift < 200.0:  return 8
        else:                return 0


# ═══════════════════════════════════════════════════════════════════
# ARTIFACT DETECTOR
# ═══════════════════════════════════════════════════════════════════

class ArtifactDetector:
    """
    Détection multi-critères sur époque 4 s.

    Stratégie :
      Rejet TOTAL  → electrode_off / flat_line / extreme_peak / emg fort
      Marquage EOG → epoch retournée avec flags['eog']=True
      Flag EMG     → epoch retournée avec flags['emg_suspect']=True

    Toutes les amplitudes : sur epoch_ac = epoch - median(epoch).

    Seuils :
      flat_line     : std(AC) < 0.5 µV
      extreme_peak  : p-p(AC) > 500 µV
      EOG amplitude : max|AC| > 150 µV   (Fp2-spécifique)
      EOG kurtosis  : kurtosis > 4.0
      EOG spectral  : P(1-4Hz) / P(8-13Hz) > 2.5
      EMG suspect   : P(35-45Hz) / P(1-45Hz) > 0.20
      EMG rejet     : P(35-45Hz) / P(1-45Hz) > 0.40
      high_rms      : rms > median_cal + 5 × MAD_cal

    Ref : Kanoga & Mitsukura 2017, Goncharova 2003,
          Urigüen & Garcia-Zapirain 2015
    """

    FLAT_LINE_STD_UV    = 0.05
    EXTREME_PEAK_UV     = 500.0
    HIGH_RMS_MAD_FACTOR = 5.0

    BLINK_AMP_UV      = 150.0
    BLINK_KURTOSIS    = 4.0
    BLINK_DELTA_ALPHA = 2.5

    EMG_SUSPECT_THR = 0.20
    EMG_REJECT_THR  = 0.40

    CAL_DURATION_S = 60
    CAL_MIN_S      = 30

    def __init__(self, fs: int = FS):
        self.fs               = fs
        self._cal_buf         = deque(maxlen=fs * self.CAL_DURATION_S)
        self._cal_done        = False
        self._cal_prog        = 0.0
        self._cal_clean_count = 0

    # ── Calibration ──────────────────────────────────────────────

    def push_cal(self, uv: float):
        self._cal_buf.append(uv)
        n = len(self._cal_buf)
        self._cal_prog = min(100.0, n / (self.fs * self.CAL_DURATION_S) * 100)
        if n >= self.fs * self.CAL_MIN_S and not self._cal_done:
            self._cal_done = True

    def push_cal_clean_epoch(self, epoch_ac: np.ndarray):
        """Signale une époque propre (non EOG, non EMG) au buffer cal."""
        self._cal_clean_count += 1

    @property
    def cal_progress(self) -> float: return round(self._cal_prog, 1)
    @property
    def calibration_done(self) -> bool: return self._cal_done

    # ── Détection principale ──────────────────────────────────────

    def is_bad(self, epoch: np.ndarray,
               electrode_ok: bool = True) -> tuple:
        """
        Retourne (is_bad: bool, reason: str, flags: dict).

        flags :
          eog         : bool  — clignement oculaire
          emg_suspect : bool  — contamination EMG partielle
          emg_ratio   : float — ratio P(35-45Hz)/P(1-45Hz)
        """
        flags = {"eog": False, "emg_suspect": False, "emg_ratio": 0.0}

        if len(epoch) < self.fs // 2:
            return True, "too_short", flags

        if not electrode_ok:
            return True, "electrode_off", flags

        # Suppression DC robuste
        epoch_ac = epoch - np.median(epoch)

        if np.std(epoch_ac) < self.FLAT_LINE_STD_UV:
            return True, "flat_line", flags

        if np.ptp(epoch_ac) > self.EXTREME_PEAK_UV:
            return True, "extreme_peak", flags

        # EOG — marquage uniquement, pas rejet
        flags["eog"] = self._detect_eog(epoch_ac)

        # EMG
        emg_ratio = self._emg_ratio(epoch_ac)
        flags["emg_ratio"] = round(emg_ratio, 4)
        if emg_ratio > self.EMG_REJECT_THR:
            return True, "emg", flags
        if emg_ratio > self.EMG_SUSPECT_THR:
            flags["emg_suspect"] = True

        # High-RMS (seulement si calibration propre disponible)
        if self._cal_done and self._cal_clean_count >= 5:
            rms = float(np.sqrt(np.mean(epoch_ac ** 2)))
            if self._is_high_rms(rms):
                return True, "high_rms", flags

        return False, "", flags

    # ── Helpers ──────────────────────────────────────────────────

    def _detect_eog(self, epoch_ac: np.ndarray) -> bool:
        """Triple critère : amplitude ET kurtosis ET ratio delta/alpha."""
        if float(np.max(np.abs(epoch_ac))) <= self.BLINK_AMP_UV:
            return False
        if float(scipy.stats.kurtosis(epoch_ac)) <= self.BLINK_KURTOSIS:
            return False
        try:
            f, psd  = scipy.signal.welch(
                epoch_ac, self.fs,
                nperseg=min(self.fs, len(epoch_ac)), window="hann")
            p_d = float(np.trapezoid(psd[(f>=1.0)&(f<=4.0)], f[(f>=1.0)&(f<=4.0)]))
            p_a = float(np.trapezoid(psd[(f>=8.0)&(f<=13.0)], f[(f>=8.0)&(f<=13.0)])) + 1e-30
            return (p_d / p_a) > self.BLINK_DELTA_ALPHA
        except Exception:
            return False

    def _emg_ratio(self, epoch_ac: np.ndarray) -> float:
        """P(35-45 Hz) / P(1-45 Hz). Ref : Goncharova 2003."""
        try:
            f, psd  = scipy.signal.welch(
                epoch_ac, self.fs,
                nperseg=min(self.fs, len(epoch_ac)),
                window="hann", scaling="density")
            p_emg   = float(np.trapezoid(psd[(f>=35.0)&(f<=45.0)], f[(f>=35.0)&(f<=45.0)]))
            p_total = float(np.trapezoid(psd[(f>=1.0)&(f<=45.0)],  f[(f>=1.0)&(f<=45.0)])) + 1e-30
            return p_emg / p_total
        except Exception:
            return 0.0

    def _is_high_rms(self, rms: float) -> bool:
        """Seuil = median_cal + 5 × MAD, sur fenêtres de 1 s du buffer cal."""
        try:
            arr    = np.array(self._cal_buf, dtype=float)
            arr_ac = arr - np.median(arr)
            n_win  = self.fs
            rms_w  = [
                float(np.sqrt(np.mean(arr_ac[i:i+n_win]**2)))
                for i in range(0, len(arr_ac) - n_win, n_win // 2)
            ]
            if len(rms_w) < 4:
                return False
            a   = np.array(rms_w)
            med = np.median(a)
            mad = np.median(np.abs(a - med)) * 1.4826 + 1e-10
            return rms > med + self.HIGH_RMS_MAD_FACTOR * mad
        except Exception:
            return False