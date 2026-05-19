# backend/dsp/epochs.py
"""
Pipeline de préprocessing et extraction d'époques EEG — v8.0.

Changements vs original :
  - Bandes BANDS_V8 (theta 6-8 Hz, delta 1-4 Hz, gamma 30-45 Hz)
  - Calibration 60 s minimum, exclusion EOG/EMG du buffer baseline
  - is_bad() retourne 3 valeurs (bad, reason, flags) → unpack correct
  - Marquage EOG (pas rejet total) → récupère les epochs avec clignements
  - epoch retournée contient eog_detected, emg_suspect, emg_ratio
  - extract_features() reçoit epoch filtrée et emg_ratio
  - Graphe fractal et fd_vector supprimés
  - Baseline : médiane (robuste) au lieu de moyenne

Ref : Cohen 2014 ch.10-19, Kanoga & Mitsukura 2017
"""

import numpy as np
from scipy.signal import welch, get_window
from datetime    import datetime
from collections import deque

from .artifacts import ArtifactDetector
from .filters   import FilterBank, wavelet_denoise_adaptive
from .features  import higuchi_fd, extract_features, BANDS_V8, TOTAL_BAND
from utils.constants import FS, EPOCH_SEC, EPOCH_SAMP, EPOCH_STEP


# ═══════════════════════════════════════════════════════════════════
# PREPROCESSING PIPELINE
# ═══════════════════════════════════════════════════════════════════

class PreprocessingPipeline:
    """
    Préprocessing zéro-phase + gestion baseline spectrale.

    Bandes v8.0 : delta 1-4, theta 6-8, alpha 8-13,
                  beta 13-30, beta_high 20-30, gamma_low 30-45
    """

    CAL_MIN_CLEAN = 10   # epochs propres minimales pour baseline fiable

    def __init__(self, fs: int = FS):
        self.fs        = fs
        self.baseline  = {}
        self._bl_epochs = []
        self.filters   = FilterBank(fs)
        self.detector  = ArtifactDetector(fs)

    # ── Délégation calibration ───────────────────────────────────

    def push_cal(self, uv: float):
        self.detector.push_cal(uv)

    @property
    def cal_progress(self) -> float:
        return self.detector.cal_progress

    @property
    def calibration_done(self) -> bool:
        return self.detector.calibration_done

    # ── Baseline spectrale ────────────────────────────────────────

    def _band_power(self, epoch_f: np.ndarray, lo: float, hi: float) -> float:
        """Puissance Welch dans [lo, hi] Hz sur signal déjà filtré."""
        f, psd = welch(
            epoch_f, self.fs,
            nperseg=min(self.fs, len(epoch_f)),
            window="hann",
            noverlap=min(self.fs // 2, len(epoch_f) // 2),
            scaling="density",
        )
        mask = (f >= lo) & (f <= hi)
        return float(np.trapezoid(psd[mask], f[mask])) if mask.any() else 0.0

    def add_baseline_epoch(self, epoch_f: np.ndarray):
        """
        Ajoute une époque PROPRE (non EOG, non EMG) au buffer baseline.
        Ne jamais appeler sur des époques artefactées.
        """
        self._bl_epochs.append(epoch_f.copy())
        self.detector.push_cal_clean_epoch(epoch_f)

    def finalise_baseline(self) -> bool:
        """
        Calcule la baseline sur les époques propres accumulées.
        Utilise la médiane (robuste aux outliers) plutôt que la moyenne.
        Retourne False si pas assez d'époques.
        """
        if len(self._bl_epochs) < self.CAL_MIN_CLEAN:
            return False
        for name, (lo, hi) in BANDS_V8.items():
            powers = [self._band_power(ep, lo, hi) for ep in self._bl_epochs]
            # médiane > moyenne : robuste aux époques residuellement bruitées
            self.baseline[name] = float(np.median(powers))
        return True

    def has_baseline(self) -> bool:
        return len(self.baseline) == len(BANDS_V8)

    def normalise_db(self, epoch_f: np.ndarray) -> dict:
        """
        dB = 10 × log10(P_current / P_baseline).
        Standard QEEG (Duffy et al. 1994).
        Retourne P_brute si baseline non disponible.
        """
        result = {}
        for name, (lo, hi) in BANDS_V8.items():
            p = self._band_power(epoch_f, lo, hi)
            if self.has_baseline():
                bl = self.baseline.get(name, p)
                result[name] = round(10.0 * np.log10((p + 1e-30) / (bl + 1e-30)), 3)
            else:
                result[name] = round(p, 6)
        return result

    # ── Filtrage RT (délégation) ──────────────────────────────────

    def filter_sample(self, uv: float) -> float:
        return self.filters.filter_sample(uv)


# ═══════════════════════════════════════════════════════════════════
# EPOCH EXTRACTOR
# ═══════════════════════════════════════════════════════════════════

class EpochExtractor:
    """
    Extraction d'époques glissantes avec pipeline DSP complet.

    Fenêtre : 4 s (1000 échantillons @ 250 Hz)
    Overlap  : 75 % → step 1 s (250 échantillons)

    Stratégie de rejet v8.0 :
      Rejet TOTAL  → electrode_off, flat_line, extreme_peak, emg fort
      Marquage EOG → epoch retournée avec eog_detected=True
      Flag EMG     → epoch retournée avec emg_suspect=True
    """

    def __init__(self, fs: int = FS,
                 win_sec: float = EPOCH_SEC,
                 overlap: float = 0.75):
        self.fs   = fs
        self.win  = int(win_sec * fs)               # 1000
        self.step = int(self.win * (1 - overlap))   # 250
        self._buf     = deque(maxlen=self.win)
        self._counter = 0
        self._hann    = get_window("hann", self.win)
        self.pipeline = PreprocessingPipeline(fs)

        self.n_total    = 0
        self.n_rejected = 0
        self.n_accepted = 0
        self.n_eog      = 0
        self.n_emg_flag = 0

    def push(self, uv: float, electrode_ok: bool = True):
        """
        Pousse un échantillon brut (µV, DC offset inclus).
        Retourne un dict d'époque ou None si pas encore prête.
        """
        self.pipeline.push_cal(uv)
        self._buf.append(uv)
        self._counter += 1
        if len(self._buf) < self.win or self._counter % self.step != 0:
            return None
        return self._process(np.array(self._buf, dtype=float), electrode_ok)

    def _process(self, raw_epoch: np.ndarray, electrode_ok: bool) -> dict:
        self.n_total += 1

        # ── Détection artefacts ───────────────────────────────────
        # is_bad() retourne 3 valeurs en v8.0 (bad, reason, flags)
        bad, reason, flags = self.pipeline.detector.is_bad(raw_epoch, electrode_ok)

        if bad:
            self.n_rejected += 1
            return {
                "type":     "epoch_rejected",
                "reason":   reason,
                "flags":    flags,
                "total":    self.n_total,
                "rejected": self.n_rejected,
            }

        # ── Golden Filter (zéro-phase) ────────────────────────────
        # filter_epoch() : median_sub + Notch50 + Notch100 + BP[1-45] + wavelet
        filtered = self.pipeline.filters.filter_epoch(raw_epoch)

        # ── Normalisation dB vs baseline ──────────────────────────
        db_powers = self.pipeline.normalise_db(filtered)

        # ── Features ─────────────────────────────────────────────
        emg_ratio = flags.get("emg_ratio", 0.0)
        features  = extract_features(filtered, db_powers, emg_ratio=emg_ratio)

        # ── Compteurs ────────────────────────────────────────────
        self.n_accepted += 1
        if flags.get("eog"):
            self.n_eog += 1
        if flags.get("emg_suspect"):
            self.n_emg_flag += 1

        # Baseline uniquement sur epochs propres (non EOG, non EMG)
        if not flags.get("eog") and not flags.get("emg_suspect"):
            if not self.pipeline.has_baseline():
                self.pipeline.add_baseline_epoch(filtered)

        # ── Résultat ──────────────────────────────────────────────
        return {
            "type":      "epoch",
            "epoch_idx": self.n_accepted,
            "timestamp": datetime.now().isoformat(),

            # Qualité de l'époque
            "eog_detected": flags.get("eog",          False),
            "emg_suspect":  flags.get("emg_suspect",   False),
            "emg_ratio":    emg_ratio,

            # Features DSP
            "features":  features,
            "db_powers": db_powers,
            "hfd":       features.get("fractal_dim", 1.5),

            # Statistiques session
            "stats": {
                "total":       self.n_total,
                "accepted":    self.n_accepted,
                "rejected":    self.n_rejected,
                "eog":         self.n_eog,
                "emg_flag":    self.n_emg_flag,
                "accept_rate": round(
                    self.n_accepted / self.n_total * 100, 1
                ) if self.n_total > 0 else 0.0,
            },
        }