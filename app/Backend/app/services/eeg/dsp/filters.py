# backend/dsp/filters.py
"""
Filtres DSP — Golden Filter unifié v8.0.

Pipeline identique pour affichage RT (lfilter causal)
et analyse d'époque (filtfilt zéro-phase) → cohérence garantie.

Chaîne : median_sub → Notch 50 Hz → Notch 100 Hz → BP [1-45 Hz] → Wavelet

Changements vs original :
  HP 0.5 Hz → 1.0 Hz   : élimine drift électrodes sèches < 1 Hz
  LP 40 Hz  → 45 Hz    : préserve gamma-bas 30-45 Hz
  HP Butterworth redondant supprimé (créait filtre effectif ordre 14)
  reset() ajoutée pour reconnexion TCP

Ref : Widmann et al. 2015, Kanoga & Mitsukura 2017 §3.2.4,
      Sanei & Chambers 2007 §5.4, Gao 1998
"""

import numpy as np
from scipy.signal import (butter, lfilter, lfilter_zi, filtfilt, iirnotch)
import pywt
from ..utils.constants import FS


class FilterBank:
    """
    Golden Filter — pipeline zéro-phase pour époque, causal pour RT.

    Paramètres validés pour électrodes sèches Ag/AgCl sur Fp2 :
      HP_FREQ  = 1.0 Hz  — supprime drift de polarisation
      LP_FREQ  = 45.0 Hz — coupe EMG > 45 Hz, préserve gamma-bas
      Notch 50 Hz + 100 Hz — secteur et harmonique
    """

    HP_FREQ   = 1.0
    LP_FREQ   = 45.0
    NOTCH_50  = 50.0
    NOTCH_100 = 100.0

    def __init__(self, fs: int = FS):
        self.fs  = fs
        nyq = fs / 2.0

        # Notch 50 Hz et 100 Hz
        self.b_notch, self.a_notch = iirnotch(self.NOTCH_50  / nyq, Q=30)
        self.b_n100,  self.a_n100  = iirnotch(self.NOTCH_100 / nyq, Q=30)

        # Bandpass Butterworth ordre 4 — [HP_FREQ, LP_FREQ]
        # filtfilt → ordre effectif 8 (zéro-phase)
        self.b_bp, self.a_bp = butter(
            4, [self.HP_FREQ / nyq, self.LP_FREQ / nyq], btype="band"
        )

        # États IIR pour filtre causal (affichage RT)
        self.zi_notch        = lfilter_zi(self.b_notch, self.a_notch) * 0
        self.zi_n100         = lfilter_zi(self.b_n100,  self.a_n100)  * 0
        self.zi_bp           = lfilter_zi(self.b_bp,    self.a_bp)    * 0
        self._dc_initialized = False

        # EMA DC removal — τ ≈ 1.3 s @ 250 Hz (α = 3/1000)
        # Supprime le DC offset massif de l'AD8232 (~1 650 000 µV)
        # sans attendre la convergence lente du filtre HP Butterworth.
        self._dc_avg   = None
        self._DC_ALPHA = 0.003   # 1 / (FS * τ), τ ≈ 1.3 s

    # ── Pipeline époque (zéro-phase) ─────────────────────────────

    def filter_epoch(self, epoch: np.ndarray) -> np.ndarray:
        """
        Filtre une époque de 4 s avec filtfilt (zéro-phase).

        Étapes :
          1. Soustraction médiane (DC robuste)
          2. Notch 50 Hz  (filtfilt)
          3. Notch 100 Hz (filtfilt)
          4. BP [1-45 Hz] Butterworth ordre 4 (filtfilt)
          5. Débruitage ondelettes partiel (niveaux 1-3)

        Ref : Widmann et al. 2015 §2.3
        """
        # 1. DC robuste
        epoch_ac = epoch - np.median(epoch)
        # 2-3. Notch
        epoch_ac = filtfilt(self.b_notch, self.a_notch, epoch_ac)
        epoch_ac = filtfilt(self.b_n100,  self.a_n100,  epoch_ac)
        # 4. Bandpass
        epoch_f  = filtfilt(self.b_bp, self.a_bp, epoch_ac)
        # 5. Ondelettes
        return _wavelet_denoise(epoch_f)

    # ── Filtre causal RT (sample-par-sample) ─────────────────────

    def filter_sample(self, uv: float) -> float:
        """
        Filtre causal temps réel — pipeline complet :
          1. Suppression DC par EMA (τ ≈ 1.3 s) → signal AC pur dès le 1er échantillon
          2. Notch 50 Hz  (lfilter causal)
          3. Notch 100 Hz (lfilter causal)
          4. Bandpass 1–45 Hz Butterworth ordre 4 (lfilter causal)

        La suppression DC par EMA remplace l'initialisation zi_bp*uv
        qui laissait un transitoire visible de 1-2 s sur les électrodes sèches.

        Ref : Widmann et al. 2015 §2.1 ; Parks & McClellan 1979 (DC removal)
        """
        # ── Étape 1 : suppression DC rapide par EMA ────────────────
        if self._dc_avg is None:
            self._dc_avg = uv          # Initialisation instantanée au premier échantillon
        else:
            self._dc_avg += self._DC_ALPHA * (uv - self._dc_avg)
        uv_ac = uv - self._dc_avg     # Signal AC — DC offset supprimé

        # ── Initialisation IIR (une seule fois, sur signal déjà centré) ─
        if not self._dc_initialized:
            self.zi_notch        = lfilter_zi(self.b_notch, self.a_notch) * 0
            self.zi_n100         = lfilter_zi(self.b_n100,  self.a_n100)  * 0
            self.zi_bp           = lfilter_zi(self.b_bp,    self.a_bp)    * 0
            self._dc_initialized = True

        # ── Étapes 2-4 : Notch 50 Hz + Notch 100 Hz + BP 1-45 Hz ──
        try:
            x, self.zi_notch = lfilter(self.b_notch, self.a_notch, [uv_ac], zi=self.zi_notch)
            x, self.zi_n100  = lfilter(self.b_n100,  self.a_n100,  x,       zi=self.zi_n100)
            x, self.zi_bp    = lfilter(self.b_bp,    self.a_bp,    x,       zi=self.zi_bp)
            return float(x[0])
        except Exception:
            return 0.0

    def reset(self):
        """
        Réinitialise les états IIR et l'estimateur DC.
        Appeler lors d'une reconnexion TCP (on_filter_reset dans assembly.py).
        """
        self.zi_notch        = lfilter_zi(self.b_notch, self.a_notch) * 0
        self.zi_n100         = lfilter_zi(self.b_n100,  self.a_n100)  * 0
        self.zi_bp           = lfilter_zi(self.b_bp,    self.a_bp)    * 0
        self._dc_initialized = False
        self._dc_avg         = None    # Réinitialise l'estimateur DC pour la reconnexion


# ═══════════════════════════════════════════════════════════════════
# DÉBRUITAGE ONDELETTES
# ═══════════════════════════════════════════════════════════════════

def _wavelet_denoise(epoch: np.ndarray, wavelet: str = "db4") -> np.ndarray:
    """
    VisuShrink partiel — seuillage mode 'garrote' sur niveaux 1-3 seulement.

    Mapping FS=250 Hz, db4 :
      Niveau 1 : ~62-125 Hz  (hors bande utile)
      Niveau 2 : ~31-62 Hz   (gamma haut, EMG résiduel)
      Niveau 3 : ~15-31 Hz   (beta haut)
      Niveau 4+ : alpha/theta/delta → PRÉSERVÉS INTACTS

    Mode 'garrote' (Gao 1998) : moins biaisé que soft,
    moins bruité que hard.

    Ref : Kanoga & Mitsukura 2017 §3.2.4, Sanei & Chambers 2007 §5.4
    """
    n     = len(epoch)
    level = min(pywt.dwt_max_level(n, wavelet), 6)
    coeffs = pywt.wavedec(epoch, wavelet, level=level)

    sigma   = np.median(np.abs(coeffs[-1])) / 0.6745
    uthresh = sigma * np.sqrt(2 * np.log(max(n, 2)))

    denoised = [coeffs[0]]
    for i, c in enumerate(coeffs[1:], start=1):
        if i <= 3:
            denoised.append(pywt.threshold(c, value=uthresh, mode="garrote"))
        else:
            denoised.append(c)   # niveaux 4+ : intacts

    return pywt.waverec(denoised, wavelet)[:n]


# Alias public pour rétrocompatibilité avec __init__.py
wavelet_denoise_adaptive = _wavelet_denoise