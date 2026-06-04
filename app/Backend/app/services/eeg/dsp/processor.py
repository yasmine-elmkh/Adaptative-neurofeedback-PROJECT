# backend/dsp/processor.py
"""
Processeur EEG temps réel avec classification d'état cognitif — v8.0.

Changements vs original :
  - Bandes v8.0 : theta 6-8 Hz, delta 1-4 Hz, gamma_low 30-45 Hz
  - push() accepte lo_score → transmis au CQE
  - CQE mis à jour toutes les 500 ms
  - Classification Z-score individuel + hystérésis 3 epochs (anti-flickering)
  - État "invalid" si CQE < 60 ou emg_ratio > 0.20
  - reset() unifié : filtres + CQE (appelé par on_filter_reset dans assembly.py)
  - metrics() enrichi : cqe_score, cqe_label, emg_ratio, baseline_ready

Ref : Klimesch 1999, Gevins & Smith 2003, Pope et al. 1995,
      Cohen 2014, Goncharova 2003
"""

import time
import numpy as np
from scipy.signal import welch
from collections  import deque

from .epochs       import EpochExtractor
from .artifacts    import ContactQualityEstimator
from ..utils.constants import FS

# Classifieur ML (LightGBM entraîné LOSO) — chargement optionnel
_ml_clf = None
try:
    from .ml_classifier import MLClassifier
    _ml_clf = MLClassifier()
except Exception as _e:
    import logging as _logging
    _logging.getLogger("NeuroCap").warning(
        f"[Processor] MLClassifier non chargé ({_e}). "
        "Classification ML désactivée — Z-score uniquement."
    )

# Bandes v8.0 pour le Welch temps réel
_BANDS_RT = {
    "delta":      (1.0,  4.0),
    "theta":      (6.0,  8.0),
    "alpha":      (8.0, 13.0),
    "beta":       (13.0, 30.0),
    "beta_high":  (20.0, 30.0),
    "gamma_low":  (30.0, 45.0),
}
_EMG_BAND  = (35.0, 45.0)
_TOTAL_RT  = (1.0,  45.0)


# ═══════════════════════════════════════════════════════════════════
# COGNITIVE STATE CLASSIFIER
# ═══════════════════════════════════════════════════════════════════

class CognitiveStateClassifier:
    """
    Classification d'état cognitif basée sur Z-scores individuels.

    États : focused / stressed / relaxed / neutral / invalid

    Règles (Z-scores par rapport à la baseline du sujet) :
      INVALID    : CQE < 60  OU  emg_ratio > 0.20
      FOCUSED    : Z_theta > +1.0  ET  Z_beta ∈ [-0.5, +1.5]  ET  Z_alpha > -1.5
      STRESSED   : Z_beta_high > +1.5  ET  Z_alpha < -1.0
      RELAXED    : Z_alpha > +1.0  ET  Z_beta < -0.5
      NEUTRAL    : tout le reste

    Hystérésis : MIN_STATE_EPOCHS epochs consécutives requises
    pour changer d'état (~3 s avec overlap 75 %).

    AVERTISSEMENT : estimation probabiliste intra-sujet uniquement.
    Pas de valeur diagnostique clinique.
    Ref : Klimesch 1999, Gevins & Smith 2003
    """

    MIN_STATE_EPOCHS = 3

    Z_THETA_FOCUS    = 1.0
    Z_BETA_HI_STRESS = 1.5
    Z_ALPHA_STRESS   = -1.0
    Z_ALPHA_RELAX    = 1.0
    Z_BETA_RELAX     = -0.5
    Z_ALPHA_MIN      = -1.5

    def __init__(self):
        self._current    = "neutral"
        self._candidate  = "neutral"
        self._cand_count = 0
        self._mu    = {}
        self._sigma = {}
        self._baseline_ready = False

    def set_baseline(self, mu: dict, sigma: dict):
        """
        Reçoit la baseline individuelle (µ et σ des puissances relatives).
        Appelé depuis api.py après finalise_baseline().
        """
        self._mu    = dict(mu)
        self._sigma = dict(sigma)
        self._baseline_ready = True

    @property
    def baseline_ready(self) -> bool:
        return self._baseline_ready

    def update(self, bands_rel: dict,
               cqe_score: int, emg_ratio: float) -> str:
        """
        Calcule l'état et applique l'hystérésis.
        Retourne l'état courant (string).
        """
        raw = self._classify(bands_rel, cqe_score, emg_ratio)

        if raw == self._candidate:
            self._cand_count += 1
        else:
            self._candidate  = raw
            self._cand_count = 1

        if self._cand_count >= self.MIN_STATE_EPOCHS:
            self._current = self._candidate

        return self._current

    @property
    def state(self) -> str:
        return self._current

    def _z(self, key: str, value: float) -> float:
        if not self._baseline_ready:
            return 0.0
        mu    = self._mu.get(key, 0.0)
        sigma = self._sigma.get(key, 1.0) + 1e-10
        return (value - mu) / sigma

    def _classify(self, bands: dict,
                  cqe_score: int, emg_ratio: float) -> str:
        if cqe_score < 60 or emg_ratio > 0.20:
            return "invalid"
        if not self._baseline_ready:
            return "neutral"

        z_theta   = self._z("theta",     bands.get("theta",     0.0))
        z_alpha   = self._z("alpha",     bands.get("alpha",     0.0))
        z_beta    = self._z("beta",      bands.get("beta",      0.0))
        z_beta_hi = self._z("beta_high", bands.get("beta_high", 0.0))

        if (z_theta > self.Z_THETA_FOCUS
                and -0.5 <= z_beta <= 1.5
                and z_alpha > self.Z_ALPHA_MIN):
            return "focused"

        if (z_beta_hi > self.Z_BETA_HI_STRESS
                and z_alpha < self.Z_ALPHA_STRESS):
            return "stressed"

        if (z_alpha > self.Z_ALPHA_RELAX
                and z_beta < self.Z_BETA_RELAX):
            return "relaxed"

        return "neutral"


# ═══════════════════════════════════════════════════════════════════
# REAL-TIME PROCESSOR
# ═══════════════════════════════════════════════════════════════════

class RealTimeProcessor:
    """
    Point d'entrée principal du DSP.

    Responsabilités :
      1. Filtre causal sample-par-sample (affichage)
      2. Extraction d'époques (EpochExtractor)
      3. Welch 1 Hz sur buffer 10 s (bandes dashboard)
      4. CQE mis à jour toutes les 500 ms
      5. Classification Z-score + hystérésis

    Intégration api.py :
      flt, epoch = rt.push(uv,
                           electrode_ok = electrode_mon.electrode_ok,
                           lo_score     = electrode_mon.lo_score)
    """

    WELCH_INTERVAL_S = 1.0
    CQE_INTERVAL_S   = 0.5

    def __init__(self, fs: int = FS):
        self.fs      = fs
        self.epocher = EpochExtractor(fs)
        self._raw_buf = deque(maxlen=fs * 10)

        # Welch RT
        self._welch_t        = 0.0
        self._welch_bands_rel = {b: 1.0 / len(_BANDS_RT) for b in _BANDS_RT}
        self._welch_emg       = 0.0

        # CQE
        self._cqe       = ContactQualityEstimator(fs)
        self._cqe_t     = 0.0
        self._cqe_score = 0

        # Classification
        self._classifier = CognitiveStateClassifier()

        self._warmup_samples = 0
        self._WARMUP_N       = 500  # 2s @ 250 Hz — laisse le filtre IIR converger

    # ── API principale ───────────────────────────────────────────

    def push(self, uv: float,
             electrode_ok: bool = True,
             lo_score:     int  = 0):
        """
        Traite un échantillon brut.

        Paramètres
        ----------
        uv            : float — valeur brute ADS1115 (µV, DC offset inclus)
        electrode_ok  : bool  — bit LO AD8232
        lo_score      : int   — 0 ou 30, depuis ElectrodeMonitor.lo_score

        IMPORTANT : dans api.py, appeler ainsi :
            flt, epoch = rt.push(
                uv,
                electrode_ok = electrode_mon.electrode_ok,
                lo_score     = electrode_mon.lo_score
            )

        Retourne
        --------
        (flt: float, epoch_result: dict | None)
        """
        # 1. Filtre causal → signal pour affichage
        flt = self.epocher.pipeline.filter_sample(uv)
        self._raw_buf.append(flt)

        # 2. CQE sample-par-sample
        self._cqe.push_sample(uv)

        now = time.monotonic()

        # 3. Mise à jour CQE toutes les 500 ms
        if now - self._cqe_t >= self.CQE_INTERVAL_S:
            self._cqe_score = self._cqe.update(lo_score)
            self._cqe_t = now

        # 4. Welch toutes les 1 s (sur ≥ 2 s de signal)
        if (now - self._welch_t >= self.WELCH_INTERVAL_S
                and len(self._raw_buf) >= self.fs * 2):
            self._update_welch()
            self._welch_t = now

        # 5. Extraction d'époque (ignorée pendant le warm-up du filtre IIR)
        self._warmup_samples += 1
        if self._warmup_samples > self._WARMUP_N:
            epoch_result = self.epocher.push(uv, electrode_ok)
        else:
            epoch_result = None

        # 6. Mise à jour classification si époque acceptée
        if epoch_result is not None and epoch_result.get("type") == "epoch":
            feat = epoch_result.get("features", {})

            # 6a. Classification Z-score (intra-sujet, toujours active)
            bands_rel = {
                k: feat.get(f"rel_{k}", 0.0)
                for k in ["delta", "theta", "alpha", "beta", "beta_high", "gamma_low"]
            }
            self._classifier.update(
                bands_rel,
                self._cqe_score,
                feat.get("emg_ratio", 0.0)
            )

            # 6b. Classification ML — LightGBM FeatEng (LOSO)
            # ml_features est calculé par epochs.py sur l'époque z-scorée.
            if _ml_clf is not None:
                ml_feats = epoch_result.get("ml_features")
                if ml_feats:
                    epoch_result["ml_prediction"] = _ml_clf.predict_from_dict(ml_feats)

        return flt, epoch_result

    def set_baseline(self, mu: dict, sigma: dict):
        """
        Injecte la baseline individuelle pour activer la classification.
        Appelé depuis api.py après POST /api/baseline/finalise.
        """
        self._classifier.set_baseline(mu, sigma)

    def reset(self):
        """
        Réinitialise les filtres IIR et le CQE.
        Appeler lors d'une reconnexion TCP (on_filter_reset dans assembly.py).
        """
        self.epocher.pipeline.filters.reset()
        self._cqe            = ContactQualityEstimator(self.fs)
        self._cqe_score      = 0
        self._warmup_samples = 0

    # ── Métriques WebSocket ──────────────────────────────────────

    def metrics(self) -> dict:
        """Métriques temps réel pour le dashboard (mise à jour ~1 Hz)."""
        return {
            "bands":          self._welch_bands_rel,
            "state":          self._classifier.state,
            "baseline_ready": self._classifier.baseline_ready,
            "cqe_score":      self._cqe_score,
            "cqe_label":      self._cqe.label,
            "emg_ratio":      round(self._welch_emg, 4),
            "epoch_stats": {
                "total":    self.epocher.n_total,
                "accepted": self.epocher.n_accepted,
                "rejected": self.epocher.n_rejected,
                "eog":      self.epocher.n_eog,
                "emg_flag": self.epocher.n_emg_flag,
            },
        }

    def raw_metrics(self) -> dict:
        """Métriques debug du signal filtré, sur composante AC (médiane retirée)."""
        # 750 samples = 3 s @ 250 Hz — couvre le transitoire du DCRemover (τ ≈ 3 s)
        _SETTLED_N = max(self._WARMUP_N, int(self.fs * 3))
        if self._warmup_samples < _SETTLED_N:
            return {"rms_uv": 0.0, "peak_uv": 0.0, "dc_uv": 0.0, "settling": True}
        if not self._raw_buf:
            return {"rms_uv": 0.0, "peak_uv": 0.0, "dc_uv": 0.0, "settling": True}
        arr    = np.array(list(self._raw_buf)[-self.fs * 2:])
        arr_ac = arr - np.median(arr)
        rms_uv  = round(float(np.sqrt(np.mean(arr_ac ** 2))), 2)
        peak_uv = round(float(np.max(np.abs(arr_ac))),        2)
        # Valeurs > 500 000 µV → signal aberrant (filtre divergé, hardware KO)
        # Seuil large pour couvrir les gains AD8232 élevés (×100–×1000)
        if rms_uv > 500_000:
            return {"rms_uv": 0.0, "peak_uv": 0.0, "dc_uv": 0.0, "settling": True}
        return {
            "rms_uv":  rms_uv,
            "peak_uv": peak_uv,
            "dc_uv":   round(float(np.mean(arr)), 1),
            "settling": False,
        }

    # ── Welch interne ────────────────────────────────────────────

    def _update_welch(self):
        arr = np.array(list(self._raw_buf)[-self.fs * 2:])
        try:
            fw, pxx = welch(
                arr, self.fs,
                nperseg=min(self.fs, len(arr)),
                window="hann",
                noverlap=min(self.fs // 2, len(arr) // 2),
                scaling="density",
            )

            def bp(lo, hi):
                mask = (fw >= lo) & (fw <= hi)
                return float(np.trapz(pxx[mask], fw[mask])) if mask.any() else 0.0

            abs_b   = {name: bp(lo, hi) for name, (lo, hi) in _BANDS_RT.items()}
            p_emg   = bp(*_EMG_BAND)
            p_total = bp(*_TOTAL_RT) + 1e-30

            self._welch_bands_rel = {k: round(v / p_total, 5) for k, v in abs_b.items()}
            self._welch_emg       = round(p_emg / p_total, 4)

        except Exception:
            pass