# backend/dsp/ml_classifier.py
"""
Classifieur LightGBM FeatEng temps réel — NeuroCap v3.0.

Modèle unique : LightGBM entraîné sur 63 features FeatEng, validé LOSO.
Pas d'autre modèle — pas de fallback Baseline.

Pipeline :
  ml_features dict (63 features, calculées par epochs.py sur epoch z-scorée)
      → np.array dans l'ordre get_feature_names()
      → StandardScaler.transform()
      → LightGBM.predict_proba()
      → {concentration, stress, state, confidence, uncertain}

Seuil incertitude : confidence < 0.60 (CdC NeuroCap §2.5.1).
Labels : 0 = Concentration, 1 = Stress.

Modèle : models/baseline_FeatEng/baseline_models/LightGBM_concentration_vs_stress.joblib
Scaler : models/baseline_FeatEng/baseline_models/LightGBM_scaler.joblib
"""

import sys
import logging
import numpy as np
from pathlib import Path

logger = logging.getLogger("NeuroCap")

# ── Chemins ── racine EEG_project/ (6 niveaux au-dessus de dsp/) ───────
# dsp → eeg → services → app(pkg) → Backend → app(outer) → EEG_project
_PROJECT_ROOT = Path(__file__).resolve().parents[6]
_MODEL_DIR    = _PROJECT_ROOT / "models" / "baseline_FeatEng" / "baseline_models"
_MODEL_FILE   = "LightGBM_concentration_vs_stress.joblib"
_SCALER_FILE  = "LightGBM_scaler.joblib"

# ── Import feature_eng (get_feature_names pour l'ordre des colonnes) ───
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

_get_feature_names = None
try:
    from src.data.feature_eng import get_feature_names as _gfn
    _get_feature_names = _gfn
except Exception as _e:
    logger.error(
        f"[MLClassifier] src/data/feature_eng.py introuvable : {_e}\n"
        "Vérifiez que le projet NeuroCap est accessible depuis ce chemin."
    )

CONFIDENCE_THR = 0.60   # CdC §2.5.1


# ═══════════════════════════════════════════════════════════════════════
class MLClassifier:
    """
    Classifieur LightGBM FeatEng temps réel.

    Reçoit le dict `ml_features` pré-calculé par epochs.py
    (63 features extraites de l'époque z-scorée avec feature_eng.py)
    et retourne les probabilités d'état cognitif.

    Usage :
        clf  = MLClassifier()
        pred = clf.predict_from_dict(epoch_result["ml_features"])
        # → {"concentration": 0.73, "stress": 0.27,
        #    "state": "concentration", "confidence": 0.73,
        #    "uncertain": False}
    """

    def __init__(self):
        import joblib

        model_path  = _MODEL_DIR / _MODEL_FILE
        scaler_path = _MODEL_DIR / _SCALER_FILE

        if not model_path.exists():
            raise FileNotFoundError(
                f"[MLClassifier] Modèle FeatEng introuvable :\n"
                f"  {model_path}\n"
                f"Entraînez d'abord le modèle avec src/models/baselines/baseline_ML_feature_eng.py"
            )

        self._model  = joblib.load(model_path)
        self._scaler = joblib.load(scaler_path) if scaler_path.exists() else None

        # Ordre canonique des features — identique à l'entraînement
        if _get_feature_names is None:
            raise RuntimeError(
                "[MLClassifier] feature_eng.py non importable — "
                "impossible de déterminer l'ordre des features."
            )
        self._feat_names = _get_feature_names()

        # Indices des classes dans predict_proba
        classes = list(getattr(self._model, "classes_", [0, 1]))
        self._idx_conc   = classes.index(0) if 0 in classes else 0
        self._idx_stress = classes.index(1) if 1 in classes else 1

        logger.info(
            f"[MLClassifier] Prêt — FeatEng {len(self._feat_names)} features | "
            f"scaler={'oui' if self._scaler else 'non'} | "
            f"modèle={model_path.name}"
        )

    # ── API publique ───────────────────────────────────────────────

    def predict_from_dict(self, ml_features: dict) -> dict:
        """
        Prédit l'état cognitif depuis le dict de 63 features FeatEng.

        Paramètres
        ----------
        ml_features : dict
            Retourné par feature_eng.extract_all_features(epoch_z).
            Calculé dans epochs.py sur l'époque filtrée z-scorée.

        Retourne
        --------
        dict : concentration, stress, state, confidence, uncertain
        """
        if not ml_features:
            return self._uncertain("dict vide")

        try:
            feats = np.array(
                [ml_features.get(n, 0.0) for n in self._feat_names],
                dtype=np.float64,
            ).reshape(1, -1)

            if self._scaler is not None:
                feats = self._scaler.transform(feats)

            proba    = self._model.predict_proba(feats)[0]
            p_conc   = float(proba[self._idx_conc])
            p_stress = float(proba[self._idx_stress])
            conf     = max(p_conc, p_stress)

            return {
                "concentration": round(p_conc,   4),
                "stress":        round(p_stress,  4),
                "state":         "stress" if p_stress > p_conc else "concentration",
                "confidence":    round(conf,      4),
                "uncertain":     conf < CONFIDENCE_THR,
            }

        except Exception as exc:
            logger.warning(f"[MLClassifier] predict_from_dict : {exc}")
            return self._uncertain(str(exc))

    @staticmethod
    def _uncertain(reason: str = "") -> dict:
        return {
            "concentration": 0.5,
            "stress":        0.5,
            "state":         "uncertain",
            "confidence":    0.5,
            "uncertain":     True,
            "error":         reason,
        }
