# dsp/dual_classifier.py
"""
DualClassifier v3 — NeuroCap Production
=========================================
Modèles retenus selon §4.5 du CdC (sélection sur 210 configurations) :

  Concentration : EEGNet — DL FULL                     ✅ Recommandé
    Score composite S = 0,789  (#1 / 210 configs)
    AUC = 0,751 | MCC = 0,673 | Sensitivity = 0,994 | Specificity = 0,557
    Path : models/Regression/DL/EEGNet/conc/EEGNet_conc_FULL_best.pt

  Stress : EEGNet_LayerReplacement — TL FULL           ⚠️ Conditionnel
    Score composite S = 0,525
    AUC = 0,607 | Balanced Accuracy = 0,601 | MCC = 0,196 | R² = −0,052
    Path : models/Regression/TL/EEGNet_LayerReplacement/stress/EEGNet_LR_stress_FULL_best.pt
    ⚠ Réserve clinique : indicateur orientatif — Fp2 seul non validé pour le stress

Architecture : EEGNet (Conv2d, monocanal Fp2, 1000 samples @ 250 Hz)
Score : régression 0–10, seuil de décision binaire à 5,0.
Normalisation sigmoid → (0, 10) garantit deux barres toujours non nulles.
"""

import sys
import math
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger("NeuroCap")

_PROJECT_ROOT = Path(__file__).resolve().parents[6]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ── Chemins modèles ──────────────────────────────────────────────────────────
_DL_DIR       = _PROJECT_ROOT / "models" / "Regression" / "DL"
_TL_DIR       = _PROJECT_ROOT / "models" / "Regression" / "TL" / "EEGNet_LayerReplacement"
_PERSONAL_DIR = _PROJECT_ROOT / "models" / "personal"

SCORE_THR  = 5.0    # seuil décision binaire Low/High (identique à l'entraînement)
EPOCH_SAMP = 1000   # 4 s @ 250 Hz

# ── Métriques officielles CdC §4.5 ──────────────────────────────────────────
_CONC_META = {
    "model":            "EEGNet/conc (DL FULL)",
    "composite_score":  0.789,
    "auc":              0.751,
    "mcc":              0.673,
    "sensitivity":      0.994,
    "specificity":      0.557,
    "r2":               0.072,
    "clinical_status":  "validated",
    "clinical_reserve": False,
}

_STRESS_META = {
    "model":            "EEGNet_LR/stress (TL FULL)",
    "composite_score":  0.525,
    "auc":              0.607,
    "mcc":              0.196,
    "sensitivity":      0.615,
    "specificity":      0.587,
    "balanced_accuracy": 0.601,
    "r2":               -0.052,
    "clinical_status":  "conditional",
    "clinical_reserve": True,
    "reserve_msg": (
        "Indicateur orientatif — La mesure du stress par EEG frontal seul (Fp2) "
        "n'est pas cliniquement validée. Ne pas utiliser pour une décision thérapeutique."
    ),
}


# ── Normalisation sigmoid ─────────────────────────────────────────────────────
def _sigmoid_score(raw: float) -> float:
    """
    Mappe un score brut de régression vers (0, 10) via sigmoid centrée à SCORE_THR=5.0.
    scale=2.0 → passage de ~1.3 (raw=0) à ~8.7 (raw=10).
    Garantit deux barres toujours non nulles dans le dashboard.
    """
    return 10.0 / (1.0 + math.exp(-(raw - SCORE_THR) / 2.0))


# ── Architecture EEGNet (inline, sans dépendance externe) ────────────────────
def _build_eegnet(n_out: int = 1, F1: int = 8, D: int = 2, F2: int = 16):
    """
    EEGNet [Lawhern et al., 2018] — convolutions dépthwise séparables.
    Input  : (B, 1, 1, 1000)  — signal monocanal Fp2 @ 250 Hz
    Output : (B, 1)           — score de régression brut
    F1=8, D=2, F2=16 : paramètres standards mono-électrode.
    """
    try:
        import torch
        import torch.nn as nn

        class _EEGNet(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1   = nn.Conv2d(1, F1, (1, 64), padding=(0, 32), bias=False)
                self.bn1     = nn.BatchNorm2d(F1)
                self.dw      = nn.Conv2d(F1, F1 * D, (1, 1), groups=F1, bias=False)
                self.bn2     = nn.BatchNorm2d(F1 * D)
                self.elu     = nn.ELU()
                self.pool1   = nn.AvgPool2d((1, 4))
                self.drop1   = nn.Dropout(0.5)
                self.sep_dw  = nn.Conv2d(F1 * D, F1 * D, (1, 16),
                                         padding=(0, 8), groups=F1 * D, bias=False)
                self.sep_pw  = nn.Conv2d(F1 * D, F2, (1, 1), bias=False)
                self.bn3     = nn.BatchNorm2d(F2)
                self.pool2   = nn.AvgPool2d((1, 8))
                self.drop2   = nn.Dropout(0.5)
                self._n_feat = self._compute_n_feat()
                self.fc      = nn.Linear(self._n_feat, n_out)

            def _compute_n_feat(self):
                with torch.no_grad():
                    return self._forward_feat(
                        torch.zeros(1, 1, 1, EPOCH_SAMP)
                    ).shape[1]

            def _forward_feat(self, x):
                x = self.bn1(self.conv1(x))
                x = self.elu(self.bn2(self.dw(x)))
                x = self.drop1(self.pool1(x))
                x = self.sep_pw(self.sep_dw(x))
                x = self.elu(self.bn3(x))
                return self.drop2(self.pool2(x)).flatten(1)

            def forward(self, x):
                if x.dim() == 3:          # (B, 1, T) → (B, 1, 1, T)
                    x = x.unsqueeze(1)
                return self.fc(self._forward_feat(x))

        return _EEGNet()

    except ImportError:
        return None


# ════════════════════════════════════════════════════════════════════════════
class DualClassifier:
    """
    Deux modèles EEGNet indépendants sur le même signal Fp2 (1000 @ 250 Hz) :

      Concentration : EEGNet DL FULL   (AUC=0.751, S=0.789 — meilleur DL)
      Stress        : EEGNet_LR TL FULL (AUC=0.607, profil équilibré)

    predict() → deux scores dans (0, 10), jamais 0.
    Le score stress inclut une réserve clinique (flag clinical_reserve=True).
    """

    def __init__(self):
        self._conc_model   = None
        self._stress_model = None
        self._torch        = None
        self._load_base_models()

        ok_c = self._conc_model   is not None
        ok_s = self._stress_model is not None

        parts = []
        if ok_c: parts.append(f"EEGNet/conc AUC={_CONC_META['auc']}")
        if ok_s: parts.append(f"EEGNet_LR/stress AUC={_STRESS_META['auc']}")

        if parts:
            logger.info(f"[DualClassifier] ✓ {' | '.join(parts)}")
        else:
            logger.warning("[DualClassifier] Aucun modèle chargé — fichiers .pt manquants")

    # ── Chargement ───────────────────────────────────────────────────────────

    def _load_base_models(self):
        try:
            import torch
            self._torch = torch
        except ImportError:
            logger.warning("[DualClassifier] PyTorch non disponible")
            return

        # Concentration — EEGNet DL FULL (#1 / 210 configs)
        conc_pt = _DL_DIR / "EEGNet" / "conc" / "EEGNet_conc_FULL_best.pt"
        self._conc_model = self._load_pt(conc_pt, "EEGNet/conc")

        # Stress — EEGNet_LayerReplacement TL FULL (seul profil équilibré)
        stress_pt = _TL_DIR / "stress" / "EEGNet_LR_stress_FULL_best.pt"
        self._stress_model = self._load_pt(stress_pt, "EEGNet_LR/stress")

    def _load_pt(self, path: Path, label: str):
        if not path.exists():
            logger.warning(f"[DualClassifier] Fichier manquant : {path}")
            return None
        model = _build_eegnet(n_out=1)
        if model is None:
            return None
        try:
            sd = self._torch.load(path, map_location="cpu", weights_only=True)
            model.load_state_dict(sd)
            model.eval()
            logger.info(f"[DualClassifier] {label} ← {path.name}")
            return model
        except Exception as exc:
            logger.warning(f"[DualClassifier] Erreur {label} : {exc}")
            return None

    # ── Prédiction ───────────────────────────────────────────────────────────

    def predict(self, epoch_filtered, ml_features: dict = None) -> dict:
        """
        Prédit concentration ET stress depuis le même signal Fp2.

        Paramètres
        ----------
        epoch_filtered : list | ndarray — 1000 samples filtrés (FilterBank).
        ml_features    : ignoré, conservé pour compatibilité ascendante.

        Retourne
        --------
        {
          "concentration": {"score": 7.2, "pct": 72.0, "state": "concentrated",
                            "auc": 0.751, "clinical_reserve": False, ...},
          "stress":        {"score": 2.4, "pct": 24.0, "state": "relaxed",
                            "auc": 0.607, "clinical_reserve": True,
                            "reserve_msg": "Indicateur orientatif...", ...},
          "dominant":      "concentration",
          "uncertain":     False,
          "state":         "concentration",
          "confidence":    0.72,
        }
        """
        ep = self._prepare(epoch_filtered)

        c_res = self._run(ep, self._conc_model,   _CONC_META,   "concentrated", "not_concentrated")
        s_res = self._run(ep, self._stress_model,  _STRESS_META, "stressed",     "relaxed")

        c_score = c_res["score"]
        s_score = s_res["score"]

        if c_score >= SCORE_THR and s_score < SCORE_THR:
            dominant = "concentration"
        elif s_score >= SCORE_THR and c_score < SCORE_THR:
            dominant = "stress"
        elif c_score >= SCORE_THR and s_score >= SCORE_THR:
            dominant = "concentration" if c_score >= s_score else "stress"
        else:
            dominant = "neutral"

        any_error = bool(c_res.get("error") or s_res.get("error"))

        return {
            "concentration": c_res,
            "stress":        s_res,
            "dominant":      dominant,
            "uncertain":     any_error,
            "state":         dominant,
            "confidence":    round(max(c_score, s_score) / 10.0, 4),
        }

    # ── Utilitaires ──────────────────────────────────────────────────────────

    def _prepare(self, epoch_filtered) -> "np.ndarray | None":
        if epoch_filtered is None:
            return None
        try:
            ep = np.asarray(epoch_filtered, dtype=np.float32).flatten()
            if len(ep) != EPOCH_SAMP:
                ep = np.pad(ep, (0, max(0, EPOCH_SAMP - len(ep))))[:EPOCH_SAMP]
            std = float(np.std(ep))
            if std > 1e-10:
                ep = (ep - float(np.mean(ep))) / std
            return ep
        except Exception:
            return None

    def _run(self, ep, model, meta: dict, state_pos: str, state_neg: str) -> dict:
        base = {k: v for k, v in meta.items()}
        fallback_score = 2.5   # score par défaut si modèle indisponible
        if model is None:
            return {**base, "score": fallback_score, "pct": fallback_score * 10,
                    "state": "unavailable", "error": "modèle non chargé"}
        if ep is None:
            return {**base, "score": fallback_score, "pct": fallback_score * 10,
                    "state": "unavailable", "error": "signal invalide"}
        try:
            # EEGNet attend (B, 1, 1, T) — forward() gère le unsqueeze si besoin
            x = self._torch.FloatTensor(ep).reshape(1, 1, 1, EPOCH_SAMP)
            with self._torch.no_grad():
                raw = float(model(x).item())
            score = _sigmoid_score(raw)
            return {
                **base,
                "score": round(score, 3),
                "pct":   round(score * 10.0, 1),
                "state": state_pos if score >= SCORE_THR else state_neg,
            }
        except Exception as exc:
            logger.debug(f"[DualClassifier] inférence error : {exc}")
            return {**base, "score": fallback_score, "pct": fallback_score * 10,
                    "state": "error", "error": str(exc)}

    # ── Modèles personnels (fine-tuning patient) ──────────────────────────────

    def load_personal_models(self, patient_id: str) -> bool:
        """Charge les modèles fine-tunés personnels si disponibles."""
        import glob
        pid8   = patient_id[:8]
        loaded = False
        for task, attr in [("conc", "_conc_model"), ("stress", "_stress_model")]:
            files = sorted(glob.glob(str(_PERSONAL_DIR / f"patient_{pid8}_{task}_v*.pt")))
            if files and self._torch is not None:
                m = self._load_pt(Path(files[-1]), f"personal/{task}")
                if m:
                    setattr(self, attr, m)
                    loaded = True
        return loaded

    # ── Health check ─────────────────────────────────────────────────────────

    @property
    def status(self) -> dict:
        """Santé des modèles — endpoint /api/eeg/models/status."""
        return {
            "conc_loaded":    self._conc_model   is not None,
            "stress_loaded":  self._stress_model is not None,
            "architecture":   "EEGNet (Conv2d, F1=8, D=2, F2=16)",
            "input_shape":    "(B, 1, 1, 1000)",
            "score_thr":      SCORE_THR,
            "normalization":  "sigmoid(raw - 5.0, scale=2.0) → (0, 10)",
            "conc_metrics":   _CONC_META,
            "stress_metrics": _STRESS_META,
        }

    @staticmethod
    def unavailable() -> dict:
        return {
            "concentration": {"score": 2.5, "pct": 25.0, "state": "unavailable", **_CONC_META},
            "stress":        {"score": 2.5, "pct": 25.0, "state": "unavailable", **_STRESS_META},
            "dominant":   "neutral",
            "uncertain":  True,
            "state":      "neutral",
            "confidence": 0.0,
        }
