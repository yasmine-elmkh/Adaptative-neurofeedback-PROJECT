"""
NeuroCap — Service de Classification EEG
Tente de charger un modèle PyTorch entraîné (EEGNet/CNN-LSTM).
Repli sur une heuristique spectrale si le modèle est absent.
"""

import logging
import os
from typing import Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# ── Tentative d'import PyTorch (optionnel au runtime) ────────────────────────
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch non disponible — repli sur heuristique spectrale")


# ── Modèle EEGNet léger (si PyTorch disponible) ───────────────────────────────

if TORCH_AVAILABLE:
    class _EEGNetLite(nn.Module):
        """EEGNet adapté 1 canal, 1000 échantillons (4s @ 250 Hz)."""
        def __init__(self, n_classes: int = 2, samples: int = 1000):
            super().__init__()
            F1, D, F2 = 8, 2, 16
            self.temporal = nn.Sequential(
                nn.Conv2d(1, F1, (1, 64), padding=(0, 32), bias=False),
                nn.BatchNorm2d(F1),
            )
            self.depthwise = nn.Sequential(
                nn.Conv2d(F1, D * F1, (1, 1), groups=F1, bias=False),
                nn.BatchNorm2d(D * F1),
                nn.ELU(),
                nn.AvgPool2d((1, 4)),
                nn.Dropout(0.5),
            )
            self.separable = nn.Sequential(
                nn.Conv2d(D * F1, F2, (1, 16), padding=(0, 8), bias=False),
                nn.BatchNorm2d(F2),
                nn.ELU(),
                nn.AvgPool2d((1, 8)),
                nn.Dropout(0.5),
            )
            # Compute flatten size
            with torch.no_grad():
                dummy = torch.zeros(1, 1, 1, samples)
                x = self.temporal(dummy)
                x = self.depthwise(x)
                x = self.separable(x)
                flat = x.flatten(1).shape[1]
            self.classifier = nn.Sequential(
                nn.Flatten(),
                nn.Linear(flat, n_classes),
            )

        def forward(self, x):
            x = self.temporal(x)
            x = self.depthwise(x)
            x = self.separable(x)
            return self.classifier(x)


# ── Service principal ─────────────────────────────────────────────────────────

class EEGClassifier:
    """
    Interface unique de classification EEG.
    Chargement paresseux du modèle PyTorch à la première prédiction.
    """

    N_CLASSES = 2
    EPOCH_SAMPLES = 1000
    CONFIDENCE_THRESHOLD = 0.60

    def __init__(self, model_path: Optional[str] = None):
        self._model_path = model_path or os.path.join(
            os.path.dirname(__file__), "../../../models/best_model.pt"
        )
        self._model = None
        self._use_heuristic = not TORCH_AVAILABLE

    def _load_model(self):
        if not TORCH_AVAILABLE:
            return
        try:
            model = _EEGNetLite(n_classes=self.N_CLASSES, samples=self.EPOCH_SAMPLES)
            model.load_state_dict(
                torch.load(self._model_path, map_location="cpu", weights_only=True)
            )
            model.eval()
            self._model = model
            logger.info(f"Modèle EEGNet chargé depuis {self._model_path}")
        except (FileNotFoundError, Exception) as e:
            logger.warning(f"Modèle introuvable ({e}) — repli heuristique")
            self._use_heuristic = True

    def predict(self, features: Dict) -> Dict:
        """
        Classifie un epoch EEG traité.

        Entrée  : sortie de signal_processing.process_epoch()
        Sortie  : {'concentration_rate', 'stress_rate', 'confidence', 'tbr', 'ei', 'iapf'}
        """
        if not self._use_heuristic and self._model is None:
            self._load_model()

        if self._use_heuristic or self._model is None:
            return self._heuristic_predict(features)

        return self._torch_predict(features)

    def _torch_predict(self, features: Dict) -> Dict:
        try:
            epoch = features.get("normalized_epoch")
            if epoch is None or len(epoch) != self.EPOCH_SAMPLES:
                return self._heuristic_predict(features)

            x = torch.tensor(epoch, dtype=torch.float32).reshape(1, 1, 1, self.EPOCH_SAMPLES)
            with torch.no_grad():
                logits = self._model(x)
                probs = torch.softmax(logits, dim=1).squeeze().numpy()

            concentration_rate = float(probs[0]) * 100
            stress_rate = float(probs[1]) * 100
            confidence = float(np.max(probs)) * 100

            return self._build_result(concentration_rate, stress_rate, confidence, features)
        except Exception as e:
            logger.error(f"Erreur inférence PyTorch : {e}")
            return self._heuristic_predict(features)

    def _heuristic_predict(self, features: Dict) -> Dict:
        """
        Heuristique spectrale basée sur TBR, EI et puissance alpha.
        Utilisée quand le modèle DL n'est pas disponible.
        """
        ratios = features.get("ratios", {})
        powers = features.get("powers", {})
        is_artifact = features.get("is_artifact", False)

        if is_artifact:
            return self._build_result(50.0, 50.0, 0.0, features)

        tbr = ratios.get("tbr", 2.5)
        ei = ratios.get("ei", 0.5)
        alpha = powers.get("alpha", 1.0)
        high_beta = powers.get("high_beta", 0.5)

        # TBR bas + EI élevé → concentration
        conc_score = max(0.0, min(1.0, (1 / (1 + tbr)) * 0.6 + ei * 0.4))
        # TBR élevé + high-beta élevé → stress
        stress_score = max(0.0, min(1.0, (tbr / 5.0) * 0.5 + (high_beta / (alpha + 1e-9)) * 0.5))

        # Normaliser pour que la somme ≈ 1
        total = conc_score + stress_score + 1e-9
        concentration_rate = (conc_score / total) * 100
        stress_rate = (stress_score / total) * 100
        confidence = max(concentration_rate, stress_rate)

        return self._build_result(concentration_rate, stress_rate, confidence, features)

    @staticmethod
    def _build_result(
        concentration_rate: float,
        stress_rate: float,
        confidence: float,
        features: Dict,
    ) -> Dict:
        ratios = features.get("ratios", {})
        return {
            "concentration_rate": round(concentration_rate, 2),
            "stress_rate": round(stress_rate, 2),
            "confidence": round(confidence, 2),
            "tbr": round(ratios.get("tbr", 0.0), 4),
            "ei": round(ratios.get("ei", 0.0), 4),
            "iapf": round(features.get("iapf", 10.0), 2),
        }


# Singleton partagé entre sessions WebSocket
classifier = EEGClassifier()
