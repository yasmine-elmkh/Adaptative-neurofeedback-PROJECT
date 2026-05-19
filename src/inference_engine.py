"""
NeuroCap – Moteur d'Inférence Unifié
======================================
Résout le problème d'intégration pipeline → modèle :

  Le hardware (AD8232 + ESP32) produit un epoch brut de 1000 échantillons.
  À partir de cet epoch, on peut calculer :
    • 15 features  → pour les modèles Baseline ML
    • 63 features  → pour les modèles FeatEng ML
    • signal brut  → pour les modèles Deep Learning

  Ce module unifie les 3 voies dans une seule interface.

UTILISATION (dans le backend FastAPI) :
─────────────────────────────────────────
  from src.inference_engine import InferenceEngine, ModelType

  # Choisir le modèle (une fois au démarrage)
  engine = InferenceEngine(model_type=ModelType.FEATENG_LGBM)
  # ou
  engine = InferenceEngine(model_type=ModelType.DL_EEGNET)
  # ou
  engine = InferenceEngine(model_type=ModelType.BEST_AUTO)  # sélection auto

  # Prédire (à chaque epoch reçue du hardware)
  result = engine.predict(epoch_1000_samples)
  # → {'concentration': 72.3, 'stress': 27.7, 'state': 'Concentration',
  #    'confidence': 72.3, 'uncertain': False}

FLUX COMPLET :
─────────────
  ESP32 → WebSocket → pipeline_fp2.py → epoch (1000 éch.) → InferenceEngine → résultat
"""

import sys
import warnings
import importlib
import importlib.util
import time
from enum import Enum
from pathlib import Path
from typing import Optional

import numpy as np
import joblib

warnings.filterwarnings('ignore')

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Ajout des répertoires sources au path pour les imports internes
for _p in [
    str(PROJECT_ROOT / 'src' / 'data'),
    str(PROJECT_ROOT / 'src' / 'models' / 'deep_learning'),
    str(PROJECT_ROOT / 'src' / 'models' / 'deep_learning' / 'architectures'),
]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


# ============================================================================
# CONSTANTES
# ============================================================================
FS            = 250   # Hz — identique hardware ESP32
EPOCH_SAMPLES = 1000  # 4 s × 250 Hz
CONFIDENCE_THR = 0.60 # Seuil CdC §2.5.1 : en-dessous = epoch incertaine


# ============================================================================
# ENUM — Types de modèles disponibles
# ============================================================================
class ModelType(str, Enum):
    # ── Baseline ML (15 features) ───────────────────────────────────────────
    BASELINE_SVM  = "baseline_svm"
    BASELINE_RF   = "baseline_rf"
    BASELINE_XGBT = "baseline_xgb"
    BASELINE_LGBM = "baseline_lgbm"

    # ── FeatEng ML (63 features) ────────────────────────────────────────────
    FEATENG_SVM   = "feateng_svm"
    FEATENG_RF    = "feateng_rf"
    FEATENG_XGBT  = "feateng_xgb"
    FEATENG_LGBM  = "feateng_lgbm"   # ← meilleur baseline selon tests

    # ── Deep Learning (signal brut 1000 samples) ────────────────────────────
    DL_CNN1D       = "dl_CNN1D"
    DL_CNN2D       = "dl_CNN2D"
    DL_CNN3D       = "dl_CNN3D"
    DL_EEGNET      = "dl_EEGNet"
    DL_TCN         = "dl_TCN"
    DL_CNN_LSTM    = "dl_CNN_LSTM_Att"
    DL_CNN_GRU     = "dl_CNN_GRU_Att"
    DL_LSTM_1L     = "dl_LSTM_1L"
    DL_LSTM_2L     = "dl_LSTM_2L"
    DL_BILSTM_1L   = "dl_BiLSTM_1L"
    DL_BILSTM_2L   = "dl_BiLSTM_2L"
    DL_GRU_1L      = "dl_GRU_1L"
    DL_GRU_2L      = "dl_GRU_2L"
    DL_BIGRU_1L    = "dl_BiGRU_1L"
    DL_BIGRU_2L    = "dl_BiGRU_2L"
    DL_LSTM_ATT    = "dl_LSTM_Att"
    DL_BILSTM_ATT  = "dl_BiLSTM_Att"
    DL_GRU_ATT     = "dl_GRU_Att"
    DL_BIGRU_ATT   = "dl_BiGRU_Att"

    # ── Sélection automatique (lit les résultats de tests) ──────────────────
    BEST_AUTO      = "best_auto"


# ── Mapping interne ─────────────────────────────────────────────────────────

_ARCH_MAP = {
    "CNN1D":        ("CNN1D",      "CNN1D"),
    "CNN2D":        ("CNN2D",      "CNN2D"),
    "CNN3D":        ("CNN3D",      "CNN3D"),
    "EEGNet":       ("EEGNet",     "EEGNet"),
    "TCN":          ("TCN",        "TCN"),
    "CNN_LSTM_Att": ("CNN_LSTM",   "CNN_LSTM_Att"),
    "CNN_GRU_Att":  ("CNN_GRU",    "CNN_GRU_Att"),
    "LSTM_1L":      ("LSTM1L",     "LSTM_1L"),
    "LSTM_2L":      ("LSTM2L",     "LSTM_2L"),
    "BiLSTM_1L":    ("BILSTM1L",   "BiLSTM_1L"),
    "BiLSTM_2L":    ("BILSTM2L",   "BiLSTM_2L"),
    "GRU_1L":       ("GRU1L",      "GRU_1L"),
    "GRU_2L":       ("GRU2L",      "GRU_2L"),
    "BiGRU_1L":     ("BIGRU1L",    "BiGRU_1L"),
    "BiGRU_2L":     ("BIGRU2L",    "BiGRU_2L"),
    "LSTM_Att":     ("LSTM_ATT",   "LSTM_Att"),
    "BiLSTM_Att":   ("BILSTM_ATT", "BiLSTM_Att"),
    "GRU_Att":      ("GRU_ATT",    "GRU_Att"),
    "BiGRU_Att":    ("BIGRU_ATT",  "BiGRU_Att"),
}

_ML_NAME_MAP = {
    "svm":  "SVM",
    "rf":   "Random_Forest",
    "xgb":  "XGBoost",
    "lgbm": "LightGBM",
}

_EXP_PRIORITY = ['FULL', 'D', 'C', 'B', 'A']


# ============================================================================
# EXTRACTION DE FEATURES — couche d'abstraction
# ============================================================================
def _extract_15_features(epoch: np.ndarray) -> np.ndarray:
    """
    Calcule les 15 features de base depuis un epoch de 1000 échantillons.
    Utilisées par les modèles Baseline ML.
    Identique au pipeline hardware (pipeline_fp2.py).
    """
    from features_extraction import get_feature_vector
    return get_feature_vector(epoch)


def _extract_63_features(epoch: np.ndarray) -> np.ndarray:
    """
    Calcule les ~63 features avancées depuis le même epoch de 1000 échantillons.
    Utilisées par les modèles FeatEng ML.

    Comprend les 15 features de base + DWT + entropies + texture + transitions.
    → Calculées depuis le MÊME epoch brut, pas de données supplémentaires.
    """
    from feature_eng import extract_all_features
    feat_dict = extract_all_features(epoch)
    return np.array(list(feat_dict.values()), dtype=np.float32)


def _prepare_dl_tensor(epoch: np.ndarray):
    """
    Convertit un epoch (1000,) en tenseur PyTorch (1, 1, 1000) pour les DL.
    """
    import torch
    t = torch.FloatTensor(epoch)
    if t.dim() == 1:
        t = t.unsqueeze(0).unsqueeze(0)  # (1, 1, 1000)
    return t


# ============================================================================
# MOTEUR D'INFÉRENCE
# ============================================================================
class InferenceEngine:
    """
    Interface unifiée pour tous les modèles NeuroCap.

    Accepte un epoch EEG brut (1000 échantillons prétraités)
    et retourne les probabilités d'état cognitif.

    La sélection du type de features est automatique selon le modèle :
        Baseline ML  → 15 features (< 5 ms)
        FeatEng ML   → 63 features (< 40 ms)
        Deep Learning → signal brut (variable selon l'architecture)
    """

    def __init__(self, model_type: ModelType = ModelType.BEST_AUTO,
                 exp: str = 'FULL'):
        """
        Paramètres :
            model_type : type de modèle (voir ModelType)
            exp        : expérience d'augmentation à utiliser (FULL, D, C, B, A)
        """
        self.model_type = model_type
        self.exp        = exp
        self.model      = None
        self.scaler     = None
        self.device     = None
        self._kind      = None   # 'baseline', 'feateng', 'dl'
        self._loaded    = False
        self._load()

    # ─── Chargement ────────────────────────────────────────────────────────
    def _load(self):
        mt = self.model_type

        if mt == ModelType.BEST_AUTO:
            mt = self._resolve_best()

        if mt.value.startswith('baseline_'):
            self._load_baseline(mt)
        elif mt.value.startswith('feateng_'):
            self._load_feateng(mt)
        elif mt.value.startswith('dl_'):
            self._load_dl(mt)
        else:
            raise ValueError(f"ModelType inconnu : {mt}")

        self._loaded = True

    def _resolve_best(self) -> ModelType:
        """
        Choisit automatiquement le meilleur modèle disponible
        en lisant les résultats des tests (summary.json).
        """
        summary_path = PROJECT_ROOT / 'reports' / 'Tests' / 'final' / 'summary.json'
        if summary_path.exists():
            import json
            with open(summary_path) as f:
                s = json.load(f)
            winner_cat = s.get('winner_category', '')
            winner     = s.get('winner', '')
            if winner_cat == 'Baseline ML':
                clf = winner.split('-')[0].lower()
                feat = 'feateng' if 'FeatEng' in winner else 'baseline'
                key  = f"{feat}_{clf}"
                try:
                    return ModelType(key)
                except ValueError:
                    pass
            elif winner_cat == 'Deep Learning':
                key = f"dl_{winner}"
                try:
                    return ModelType(key)
                except ValueError:
                    pass

        # Fallback : LightGBM FeatEng (meilleur baseline selon tests courants)
        print("[InferenceEngine] Pas de summary.json → fallback LightGBM FeatEng")
        return ModelType.FEATENG_LGBM

    def _load_baseline(self, mt: ModelType):
        clf_key = mt.value.replace('baseline_', '')
        clf_name = _ML_NAME_MAP.get(clf_key)
        if clf_name is None:
            raise ValueError(f"Classifieur inconnu : {clf_key}")

        model_dir = PROJECT_ROOT / 'models' / 'Baseline' / 'baseline_models'
        self.model, self.scaler = _load_ml_model(clf_name, model_dir)
        self._kind = 'baseline'
        print(f"[InferenceEngine] Chargé : {clf_name} (15 features)")

    def _load_feateng(self, mt: ModelType):
        clf_key = mt.value.replace('feateng_', '')
        clf_name = _ML_NAME_MAP.get(clf_key)
        if clf_name is None:
            raise ValueError(f"Classifieur inconnu : {clf_key}")

        model_dir = PROJECT_ROOT / 'models' / 'baseline_FeatEng' / 'baseline_models'
        self.model, self.scaler = _load_ml_model(clf_name, model_dir)
        self._kind = 'feateng'
        print(f"[InferenceEngine] Chargé : {clf_name} FeatEng (63 features)")

    def _load_dl(self, mt: ModelType):
        import torch
        arch_name = mt.value.replace('dl_', '')
        if arch_name not in _ARCH_MAP:
            raise ValueError(f"Architecture DL inconnue : {arch_name}")

        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Trouver le .pt le plus récent (FULL → D → C → B → A)
        model_dir = PROJECT_ROOT / 'models' / 'deep_learning' / 'DL_models' / arch_name
        pt_path, exp_used = None, None
        for exp in _EXP_PRIORITY:
            p = model_dir / f'{arch_name}_{exp}_best.pt'
            if p.exists():
                pt_path, exp_used = p, exp
                break

        if pt_path is None:
            raise FileNotFoundError(
                f"Aucun fichier .pt trouvé pour {arch_name} dans {model_dir}\n"
                f"Entraînez d'abord le modèle : python src/models/deep_learning/architectures/{arch_name}.py"
            )

        # Import dynamique de la classe d'architecture
        file_stem, class_name = _ARCH_MAP[arch_name]
        arch_dir = PROJECT_ROOT / 'src' / 'models' / 'deep_learning' / 'architectures'
        spec   = importlib.util.spec_from_file_location(
            file_stem, arch_dir / f'{file_stem}.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        ModelClass = getattr(module, class_name)

        self.model = ModelClass().to(self.device)
        try:
            state = torch.load(pt_path, map_location=self.device, weights_only=True)
        except Exception:
            state = torch.load(pt_path, map_location=self.device)
        self.model.load_state_dict(state)
        self.model.eval()

        self._kind = 'dl'
        print(f"[InferenceEngine] Chargé : {arch_name} DL (Exp.{exp_used}, {self.device})")

    # ─── Prédiction ─────────────────────────────────────────────────────────
    def predict(self, epoch: np.ndarray) -> dict:
        """
        Prédit l'état cognitif à partir d'un epoch EEG brut prétraité.

        Entrée :
            epoch : np.ndarray (1000,) — epoch de 4 s @ 250 Hz,
                    déjà filtré et normalisé en z-score par epoch
                    (même preprocessing que pipeline_fp2.py)

        Sortie : dict
            concentration : float (0–100) — probabilité en %
            stress        : float (0–100) — probabilité en %
            state         : str  — 'Concentration' | 'Stress' | 'Incertain'
            confidence    : float (0–100) — max(P(C), P(S)) × 100
            uncertain     : bool  — True si max(P) < seuil CdC (0.60)
            latency_ms    : float — temps de traitement en ms
        """
        if not self._loaded:
            raise RuntimeError("Moteur non chargé — appelez _load() d'abord")

        epoch = np.array(epoch, dtype=np.float32).flatten()
        if len(epoch) != EPOCH_SAMPLES:
            raise ValueError(
                f"Epoch doit avoir {EPOCH_SAMPLES} échantillons, "
                f"reçu : {len(epoch)}"
            )

        t0 = time.perf_counter()

        if self._kind == 'baseline':
            probs = self._predict_ml(epoch, n_features=15)
        elif self._kind == 'feateng':
            probs = self._predict_ml(epoch, n_features=63)
        elif self._kind == 'dl':
            probs = self._predict_dl(epoch)
        else:
            raise RuntimeError(f"Kind inconnu : {self._kind}")

        latency_ms = (time.perf_counter() - t0) * 1000

        p_conc = float(probs[0]) * 100
        p_stress = float(probs[1]) * 100
        confidence = max(p_conc, p_stress)
        uncertain  = confidence < (CONFIDENCE_THR * 100)

        if uncertain:
            state = 'Incertain'
        elif p_conc >= p_stress:
            state = 'Concentration'
        else:
            state = 'Stress'

        return {
            'concentration': round(p_conc, 2),
            'stress':        round(p_stress, 2),
            'state':         state,
            'confidence':    round(confidence, 2),
            'uncertain':     uncertain,
            'latency_ms':    round(latency_ms, 3),
        }

    def predict_batch(self, epochs: np.ndarray) -> list:
        """
        Prédit sur plusieurs epochs.

        Entrée : epochs (N, 1000) numpy array
        Sortie : liste de N dicts (même format que predict())
        """
        epochs = np.array(epochs, dtype=np.float32)
        if epochs.ndim == 1:
            epochs = epochs.reshape(1, -1)
        return [self.predict(ep) for ep in epochs]

    # ─── Helpers internes ────────────────────────────────────────────────────
    def _predict_ml(self, epoch: np.ndarray, n_features: int) -> np.ndarray:
        """Extrait les features, applique le scaler, prédit."""
        if n_features == 15:
            features = _extract_15_features(epoch).reshape(1, -1)
        else:
            features = _extract_63_features(epoch).reshape(1, -1)

        if self.scaler is not None:
            features = self.scaler.transform(features)

        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(features)[0]
        else:
            pred = self.model.predict(features)[0]
            return np.array([1 - pred, pred], dtype=np.float32)

    def _predict_dl(self, epoch: np.ndarray) -> np.ndarray:
        """Convertit en tenseur, passe dans le réseau, retourne les probabilités."""
        import torch
        x = _prepare_dl_tensor(epoch).to(self.device)
        with torch.no_grad():
            out   = self.model(x)
            probs = torch.softmax(out, dim=1).cpu().numpy()[0]
        return probs

    # ─── Info ────────────────────────────────────────────────────────────────
    def __repr__(self):
        status = "chargé" if self._loaded else "non chargé"
        return (f"InferenceEngine(type={self.model_type}, "
                f"kind={self._kind}, {status})")


# ============================================================================
# HELPERS : chargement des modèles ML
# ============================================================================
def _load_ml_model(clf_name: str, model_dir: Path):
    """Charge un modèle ML + scaler depuis le répertoire sauvegardé."""
    scaler_path = model_dir / f'{clf_name}_scaler.joblib'
    if not scaler_path.exists():
        raise FileNotFoundError(f"Scaler introuvable : {scaler_path}")

    scaler = joblib.load(scaler_path)

    if clf_name == 'XGBoost':
        from xgboost import XGBClassifier
        model_path = model_dir / f'{clf_name}_concentration_vs_stress.json'
        if not model_path.exists():
            raise FileNotFoundError(f"Modèle XGBoost introuvable : {model_path}")
        model = XGBClassifier(verbosity=0)
        model.load_model(str(model_path))
    else:
        model_path = model_dir / f'{clf_name}_concentration_vs_stress.joblib'
        if not model_path.exists():
            raise FileNotFoundError(f"Modèle introuvable : {model_path}")
        model = joblib.load(model_path)

    return model, scaler


# ============================================================================
# LISTE DES MODÈLES DISPONIBLES
# ============================================================================
def list_available_models() -> dict:
    """
    Retourne un dict des modèles disponibles avec leurs chemins de fichiers.
    Utile pour inspecter ce qui a été entraîné.
    """
    available = {'baseline': [], 'feateng': [], 'dl': []}

    # Baselines 15f
    base_dir = PROJECT_ROOT / 'models' / 'Baseline' / 'baseline_models'
    for clf in ['SVM', 'Random_Forest', 'XGBoost', 'LightGBM']:
        ext = '.json' if clf == 'XGBoost' else '.joblib'
        p = base_dir / f'{clf}_concentration_vs_stress{ext}'
        if p.exists():
            available['baseline'].append(clf)

    # FeatEng 63f
    eng_dir = PROJECT_ROOT / 'models' / 'baseline_FeatEng' / 'baseline_models'
    for clf in ['SVM', 'Random_Forest', 'XGBoost', 'LightGBM']:
        ext = '.json' if clf == 'XGBoost' else '.joblib'
        p = eng_dir / f'{clf}_concentration_vs_stress{ext}'
        if p.exists():
            available['feateng'].append(clf)

    # DL
    dl_dir = PROJECT_ROOT / 'models' / 'deep_learning' / 'DL_models'
    for arch in _ARCH_MAP:
        arch_dir = dl_dir / arch
        for exp in _EXP_PRIORITY:
            if (arch_dir / f'{arch}_{exp}_best.pt').exists():
                available['dl'].append(f"{arch} (Exp.{exp})")
                break

    return available


# ============================================================================
# TEST RAPIDE EN LIGNE DE COMMANDE
# ============================================================================
if __name__ == '__main__':
    import json

    print("=" * 65)
    print("NeuroCap – Test du moteur d'inférence")
    print("=" * 65)

    # Modèles disponibles
    avail = list_available_models()
    print(f"\nModèles disponibles :")
    print(f"  Baseline 15f : {avail['baseline']}")
    print(f"  FeatEng  63f : {avail['feateng']}")
    print(f"  DL           : {len(avail['dl'])} architectures → {avail['dl'][:5]}...")

    # Epoch de test (z-score simulé)
    np.random.seed(42)
    test_epoch = np.random.randn(EPOCH_SAMPLES).astype(np.float32)
    test_epoch = (test_epoch - test_epoch.mean()) / (test_epoch.std() + 1e-8)

    models_to_test = []

    # Test Baseline 15f
    if avail['baseline']:
        clf = avail['baseline'][0]
        key_map = {'SVM': ModelType.BASELINE_SVM, 'Random_Forest': ModelType.BASELINE_RF,
                   'XGBoost': ModelType.BASELINE_XGBT, 'LightGBM': ModelType.BASELINE_LGBM}
        models_to_test.append(('Baseline 15f', key_map.get(clf, ModelType.BASELINE_LGBM)))

    # Test FeatEng 63f
    if avail['feateng']:
        clf = avail['feateng'][0]
        key_map = {'SVM': ModelType.FEATENG_SVM, 'Random_Forest': ModelType.FEATENG_RF,
                   'XGBoost': ModelType.FEATENG_XGBT, 'LightGBM': ModelType.FEATENG_LGBM}
        models_to_test.append(('FeatEng 63f', key_map.get(clf, ModelType.FEATENG_LGBM)))

    # Test DL (premier disponible)
    if avail['dl']:
        arch = avail['dl'][0].split(' ')[0]
        try:
            models_to_test.append(('DL', ModelType(f"dl_{arch}")))
        except ValueError:
            pass

    print("\n" + "─" * 65)
    print(f"{'Modèle':<25} {'État':>14} {'Conc%':>6} {'Stress%':>7} "
          f"{'Conf%':>6} {'Incert':>7} {'Lat(ms)':>8}")
    print("─" * 65)

    for label, mt in models_to_test:
        try:
            engine = InferenceEngine(model_type=mt)
            res    = engine.predict(test_epoch)
            inc    = "OUI" if res['uncertain'] else "non"
            print(f"  {label:<23} {res['state']:>14} {res['concentration']:>6.1f} "
                  f"{res['stress']:>7.1f} {res['confidence']:>6.1f} "
                  f"{inc:>7} {res['latency_ms']:>8.3f}")
        except Exception as e:
            print(f"  {label:<23} [ERREUR] {e}")

    print("─" * 65)
    print("\nPour intégrer dans le backend FastAPI :")
    print("  from src.inference_engine import InferenceEngine, ModelType")
    print("  engine = InferenceEngine(ModelType.BEST_AUTO)")
    print("  result = engine.predict(epoch_1000_samples)")
