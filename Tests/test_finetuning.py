"""
NeuroCap – Test Fine-tuning (Transfer Learning / Adaptation de Domaine)
=========================================================================
Évalue la capacité d'adaptation rapide d'un modèle pré-entraîné DL ou DANN
à un nouveau contexte via fine-tuning sur un petit jeu de données labellisé.

Scénarios d'adaptation testés :
  1. Adaptation standard : fine-tune sur X_val.npy → évalue sur X_test.npy
     Simule un utilisateur fournissant quelques minutes de données étiquetées
     pour personnaliser son modèle.

  2. Adaptation par sujet (LOSO-style) : pour chaque sujet de test,
     fine-tune sur k% de ses données, évalue sur le reste.
     Simule la personnalisation pour un nouveau sujet.

Stratégies de fine-tuning comparées :
  A. Full fine-tuning       – tous les paramètres, LR très faible
  B. Head-only fine-tuning  – seule la tête de classification est entraînée
  C. Layer-wise fine-tuning – dégelez progressivement (tête → encodeur)

Sources de modèles pré-entraînés :
  - DL baseline  : models/deep_learning/DL_models/{model}/{model}_FULL_best.pt
  - DANN         : models/deep_learning/DANN_models/{model}_DANN/{model}_DANN_FULL_best.pt
  Le script choisit automatiquement le meilleur (par F1-MACRO LOSO si disponible).

Usage :
    cd EEG_project
    python Tests/test_finetuning.py                      # auto (meilleur modèle)
    python Tests/test_finetuning.py --model BiLSTM_1L    # modèle DL spécifique
    python Tests/test_finetuning.py --model BiLSTM_1L_DANN --dann
    python Tests/test_finetuning.py --ft-ratio 0.1       # 10% du val pour fine-tune

Sorties :
    reports/Tests/finetuning/
        ├── results_before_after.csv
        ├── finetuning_curves.png        ← courbes de loss pendant le fine-tune
        ├── before_after_bars.png        ← comparaison avant/après
        ├── subject_adaptation.png       ← adaptation par sujet (si LOSO)
        ├── strategy_comparison.png      ← Full vs Head-only vs Layer-wise
        └── finetuning_report.txt
"""

import sys
import importlib
import importlib.util
import warnings
import json
import copy
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix,
)

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT_ROOT  = Path(__file__).resolve().parents[1]
ARCH_DIR      = PROJECT_ROOT / 'src' / 'models' / 'deep_learning' / 'architectures'
ARCH_DANN_DIR = PROJECT_ROOT / 'src' / 'models' / 'deep_learning' / 'architectures_DANN'
DL_UTILS_DIR  = PROJECT_ROOT / 'src' / 'models' / 'deep_learning'
DATA_DIR      = PROJECT_ROOT / 'data' / 'Augmentation' / 'datasets_augmented'
DL_MODEL_BASE   = PROJECT_ROOT / 'models' / 'deep_learning' / 'DL_models'
DANN_MODEL_BASE = PROJECT_ROOT / 'models' / 'deep_learning' / 'DANN_models'
DL_OUTPUTS      = PROJECT_ROOT / 'reports' / 'deep_learning' / 'DL_outputs'
DANN_OUTPUTS    = PROJECT_ROOT / 'reports' / 'deep_learning' / 'DANN_outputs'
DL_TEST_JSON    = PROJECT_ROOT / 'reports' / 'Tests' / 'deep_learning' / 'results.json'
DANN_TEST_JSON  = PROJECT_ROOT / 'reports' / 'Tests' / 'dann' / 'results.json'
REPORT_DIR      = PROJECT_ROOT / 'reports' / 'Tests' / 'finetuning'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DEVICE       = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
EXP_PRIORITY = ['FULL', 'D', 'C', 'B', 'A']

# Fine-tuning hyperparamètres
FT_LR_FULL     = 1e-4    # LR full fine-tuning (10x plus petit que LR original)
FT_LR_HEAD     = 5e-4    # LR head-only (un peu plus grand car moins de paramètres)
FT_EPOCHS      = 20      # Nombre d'epochs de fine-tuning
FT_PATIENCE    = 5       # Early stopping
FT_BATCH_SIZE  = 16      # Petit batch pour les petits datasets
GRAD_CLIP      = 1.0

# Mapping DL model → (fichier_stem, classe)
DL_ARCH_MAP = {
    'CNN1D':        ('CNN1D',      'CNN1D'),
    'CNN2D':        ('CNN2D',      'CNN2D'),
    'CNN3D':        ('CNN3D',      'CNN3D'),
    'EEGNet':       ('EEGNet',     'EEGNet'),
    'TCN':          ('TCN',        'TCN'),
    'CNN_LSTM_Att': ('CNN_LSTM',   'CNN_LSTM_Att'),
    'CNN_GRU_Att':  ('CNN_GRU',    'CNN_GRU_Att'),
    'LSTM_1L':      ('LSTM1L',     'LSTM_1L'),
    'LSTM_2L':      ('LSTM2L',     'LSTM_2L'),
    'BiLSTM_1L':    ('BILSTM1L',   'BiLSTM_1L'),
    'BiLSTM_2L':    ('BILSTM2L',   'BiLSTM_2L'),
    'GRU_1L':       ('GRU1L',      'GRU_1L'),
    'GRU_2L':       ('GRU2L',      'GRU_2L'),
    'BiGRU_1L':     ('BIGRU1L',    'BiGRU_1L'),
    'BiGRU_2L':     ('BIGRU2L',    'BiGRU_2L'),
    'LSTM_Att':     ('LSTM_ATT',   'LSTM_Att'),
    'BiLSTM_Att':   ('BILSTM_ATT', 'BiLSTM_Att'),
    'GRU_Att':      ('GRU_ATT',    'GRU_Att'),
    'BiGRU_Att':    ('BIGRU_ATT',  'BiGRU_Att'),
}

DANN_ARCH_MAP = {
    'CNN1D_DANN':        ('CNN1D_DANN',      'CNN1D_DANN'),
    'CNN2D_DANN':        ('CNN2D_DANN',      'CNN2D_DANN'),
    'CNN3D_DANN':        ('CNN3D_DANN',      'CNN3D_DANN'),
    'TCN_DANN':          ('TCN_DANN',        'TCN_DANN'),
    'EEGNet_DANN':       ('EEGNet_DANN',     'EEGNet_DANN'),
    'LSTM_1L_DANN':      ('LSTM1L_DANN',     'LSTM_1L_DANN'),
    'LSTM_2L_DANN':      ('LSTM2L_DANN',     'LSTM_2L_DANN'),
    'LSTM_Att_DANN':     ('LSTM_ATT_DANN',   'LSTM_Att_DANN'),
    'BiLSTM_1L_DANN':    ('BILSTM1L_DANN',   'BiLSTM_1L_DANN'),
    'BiLSTM_2L_DANN':    ('BILSTM2L_DANN',   'BiLSTM_2L_DANN'),
    'BiLSTM_Att_DANN':   ('BILSTM_ATT_DANN', 'BiLSTM_Att_DANN'),
    'GRU_1L_DANN':       ('GRU1L_DANN',      'GRU_1L_DANN'),
    'GRU_2L_DANN':       ('GRU2L_DANN',      'GRU_2L_DANN'),
    'GRU_Att_DANN':      ('GRU_ATT_DANN',    'GRU_Att_DANN'),
    'BiGRU_1L_DANN':     ('BIGRU1L_DANN',    'BiGRU_1L_DANN'),
    'BiGRU_2L_DANN':     ('BIGRU2L_DANN',    'BiGRU_2L_DANN'),
    'BiGRU_Att_DANN':    ('BIGRU_ATT_DANN',  'BiGRU_Att_DANN'),
    'CNN_LSTM_Att_DANN': ('CNN_LSTM_DANN',   'CNN_LSTM_Att_DANN'),
    'CNN_GRU_Att_DANN':  ('CNN_GRU_DANN',    'CNN_GRU_Att_DANN'),
}


# ============================================================================
# UTILITAIRES : CHARGEMENT MODÈLE
# ============================================================================
_model_cache = {}


def import_model_class(model_name: str, is_dann: bool = False):
    key = (model_name, is_dann)
    if key in _model_cache:
        return _model_cache[key]

    arch_map = DANN_ARCH_MAP if is_dann else DL_ARCH_MAP
    arch_dir = ARCH_DANN_DIR if is_dann else ARCH_DIR

    if model_name not in arch_map:
        raise ValueError(f"Modèle inconnu : {model_name}")

    file_stem, class_name = arch_map[model_name]
    arch_path = arch_dir / f'{file_stem}.py'
    if not arch_path.exists():
        raise FileNotFoundError(f"Architecture introuvable : {arch_path}")

    for p in [str(arch_dir), str(DL_UTILS_DIR)]:
        if p not in sys.path:
            sys.path.insert(0, p)

    spec   = importlib.util.spec_from_file_location(file_stem, arch_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cls = getattr(module, class_name)
    _model_cache[key] = cls
    return cls


def find_best_weights(model_name: str, is_dann: bool = False):
    """Trouve le meilleur fichier .pt pour le modèle donné."""
    model_base = DANN_MODEL_BASE if is_dann else DL_MODEL_BASE
    model_dir  = model_base / model_name
    for exp in EXP_PRIORITY:
        pt = model_dir / f'{model_name}_{exp}_best.pt'
        if pt.exists():
            return pt, exp
    return None, None


def load_pretrained_model(model_name: str, is_dann: bool = False):
    """Charge le modèle pré-entraîné. Retourne (model, exp_used, erreur)."""
    try:
        ModelClass = import_model_class(model_name, is_dann)
    except Exception as e:
        return None, None, f"Import : {e}"

    pt_path, exp_used = find_best_weights(model_name, is_dann)
    if pt_path is None:
        return None, None, f"Aucun .pt trouvé pour {model_name}"

    model = ModelClass().to(DEVICE)
    try:
        try:
            state = torch.load(pt_path, map_location=DEVICE, weights_only=True)
        except Exception:
            state = torch.load(pt_path, map_location=DEVICE)
        model.load_state_dict(state)
        print(f"  Modèle chargé : {pt_path.name} (exp {exp_used})")
        return model, exp_used, None
    except Exception as e:
        return None, None, f"Chargement poids : {e}"


# ============================================================================
# UTILITAIRES : ÉVALUATION
# ============================================================================
def evaluate_model(model: nn.Module, X: np.ndarray, y: np.ndarray,
                   is_dann: bool = False):
    """Évalue le modèle sur (X, y). Gère les modèles DANN (sortie duale)."""
    model.eval()
    X_t = torch.FloatTensor(X)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)

    all_probs, all_preds = [], []
    with torch.no_grad():
        for i in range(0, len(X_t), 256):
            batch = X_t[i:i+256].to(DEVICE)
            out   = model(batch, lambda_grl=0.0) if is_dann else model(batch)
            logits = out[0] if isinstance(out, (tuple, list)) else out
            probs  = torch.softmax(logits, 1).cpu().numpy()
            preds  = logits.argmax(1).cpu().numpy()
            all_probs.append(probs)
            all_preds.append(preds)

    probs = np.concatenate(all_probs)
    preds = np.concatenate(all_preds)

    cm = confusion_matrix(y, preds)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, cm[0, 0])
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    auc_val = 0.5
    if len(np.unique(y)) > 1:
        try:
            auc_val = roc_auc_score(y, probs[:, 1])
        except Exception:
            pass

    return {
        'accuracy':      accuracy_score(y, preds),
        'f1_macro':      f1_score(y, preds, average='macro', zero_division=0),
        'f1_binary':     f1_score(y, preds, zero_division=0),
        'precision':     precision_score(y, preds, zero_division=0),
        'recall':        recall_score(y, preds, zero_division=0),
        'specificity':   spec,
        'auc':           auc_val,
        'pct_uncertain': float(np.sum(np.max(probs, 1) < 0.60) / len(y) * 100),
        'n_samples':     len(y),
        'probs':         probs,
        'preds':         preds,
    }


# ============================================================================
# FINE-TUNING
# ============================================================================
def finetune_model(model: nn.Module, X_ft: np.ndarray, y_ft: np.ndarray,
                   X_eval: np.ndarray, y_eval: np.ndarray,
                   strategy: str = 'full', is_dann: bool = False,
                   lr: float = FT_LR_FULL, epochs: int = FT_EPOCHS,
                   patience: int = FT_PATIENCE):
    """
    Fine-tune le modèle pré-entraîné.

    Stratégies :
      'full'      – tous les paramètres avec lr bas
      'head_only' – seule la dernière couche de classification
      'layerwise' – tête d'abord, puis on dégèle progressivement

    Retourne : (model_ft, history, metrics_ft)
    """
    model_ft = copy.deepcopy(model)
    model_ft = model_ft.to(DEVICE)

    # ── Configuration des paramètres selon la stratégie ───────────────────
    if strategy == 'head_only':
        # Gèle tout sauf le dernier module (label_head / classifier)
        for name, param in model_ft.named_parameters():
            param.requires_grad = False
        # Dégèle le label_head (ou dernier fc)
        head_found = False
        for attr in ['label_head', 'classifier', 'fc', 'head']:
            head = getattr(model_ft, attr, None)
            if head is not None:
                for p in head.parameters():
                    p.requires_grad = True
                head_found = True
                break
        if not head_found:
            # Fallback : dégèle tous les Linear de la dernière couche
            params = list(model_ft.parameters())
            for p in params[-4:]:
                p.requires_grad = True
        trainable = sum(p.numel() for p in model_ft.parameters() if p.requires_grad)
        print(f"    [Head-only] {trainable:,} paramètres entraînables")

    elif strategy == 'layerwise':
        # Phase 1 : tête seule (même que head_only)
        for param in model_ft.parameters():
            param.requires_grad = False
        for attr in ['label_head', 'classifier', 'fc', 'head']:
            head = getattr(model_ft, attr, None)
            if head is not None:
                for p in head.parameters():
                    p.requires_grad = True
                break
        # Phase 2 (mi-entraînement) : on dégèlera le RNN/CNN progressivement
        # → géré dans la boucle d'entraînement
        trainable = sum(p.numel() for p in model_ft.parameters() if p.requires_grad)
        print(f"    [Layer-wise] Début head seule ({trainable:,} params), dégel progressif")

    else:  # 'full'
        for param in model_ft.parameters():
            param.requires_grad = True
        trainable = sum(p.numel() for p in model_ft.parameters() if p.requires_grad)
        print(f"    [Full] {trainable:,} paramètres entraînables")

    # ── DataLoader fine-tuning ─────────────────────────────────────────────
    X_t = torch.FloatTensor(X_ft)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)
    y_t = torch.LongTensor(y_ft)

    # Poids de classe
    cc = np.bincount(y_ft.astype(int))
    cw = (torch.FloatTensor(len(y_ft) / (2 * cc)).to(DEVICE)
          if len(cc) >= 2 and min(cc) > 0 else None)
    criterion = nn.CrossEntropyLoss(weight=cw)

    dataset  = TensorDataset(X_t, y_t)
    loader   = DataLoader(dataset, batch_size=FT_BATCH_SIZE, shuffle=True)

    X_ev = torch.FloatTensor(X_eval)
    if X_ev.dim() == 2:
        X_ev = X_ev.unsqueeze(1)
    y_ev = torch.LongTensor(y_eval)

    optimizer = optim.AdamW(
        [p for p in model_ft.parameters() if p.requires_grad],
        lr=FT_LR_HEAD if strategy == 'head_only' else lr,
        weight_decay=1e-4
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=lr * 0.01)

    history = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': [],
               'strategy': strategy, 'epochs': []}
    best_vl = float('inf')
    best_st = None
    pc      = 0

    for epoch in range(epochs):
        # Dégel progressif (layer-wise) : à mi-chemin on dégèle le feature extractor
        if strategy == 'layerwise' and epoch == epochs // 2:
            for attr in ['rnn', 'feature_extractor', 'conv_layers', 'cnn']:
                layer = getattr(model_ft, attr, None)
                if layer is not None:
                    for p in layer.parameters():
                        p.requires_grad = True
            optimizer.add_param_group({'params': [
                p for p in model_ft.parameters()
                if p.requires_grad and not any(
                    p is q for q in optimizer.param_groups[0]['params']
                )
            ], 'lr': lr * 0.1})
            print(f"    [Layer-wise] Époque {epoch+1}: dégel feature extractor")

        model_ft.train()
        total_loss, correct, total = 0.0, 0, 0
        for xb, yb in loader:
            xb = xb.to(DEVICE)
            yb = yb.to(DEVICE)
            optimizer.zero_grad(set_to_none=True)
            out = model_ft(xb, lambda_grl=0.0) if is_dann else model_ft(xb)
            logits = out[0] if isinstance(out, (tuple, list)) else out
            loss   = criterion(logits, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model_ft.parameters(), GRAD_CLIP)
            optimizer.step()
            n = len(yb)
            total_loss += loss.item() * n
            correct    += (logits.argmax(1) == yb).sum().item()
            total      += n

        scheduler.step()
        train_loss = total_loss / max(total, 1)
        train_acc  = correct   / max(total, 1)

        # Validation
        model_ft.eval()
        with torch.no_grad():
            out_val = model_ft(X_ev.to(DEVICE), lambda_grl=0.0) if is_dann else model_ft(X_ev.to(DEVICE))
            logits_val = out_val[0] if isinstance(out_val, (tuple, list)) else out_val
            val_loss   = criterion(logits_val, y_ev.to(DEVICE)).item()
            val_acc    = accuracy_score(y_eval, logits_val.argmax(1).cpu().numpy())

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_acc'].append(train_acc)
        history['val_acc'].append(val_acc)
        history['epochs'].append(epoch + 1)

        if val_loss < best_vl:
            best_vl = val_loss
            best_st = copy.deepcopy(model_ft.state_dict())
            pc = 0
        else:
            pc += 1
            if pc >= patience:
                print(f"    Early stopping à l'époque {epoch+1}")
                break

    if best_st:
        model_ft.load_state_dict(best_st)

    return model_ft, history


# ============================================================================
# SÉLECTION AUTOMATIQUE DU MEILLEUR MODÈLE
# ============================================================================
def auto_select_best_model():
    """
    Choisit le meilleur modèle pré-entraîné disponible (DL ou DANN) basé sur
    les métriques LOSO si disponibles, sinon premier modèle avec un .pt.
    Retourne (model_name, is_dann, f1_macro_loso).
    """
    candidates = []

    # Vérifie les modèles DL
    for model_name in DL_ARCH_MAP:
        pt, _ = find_best_weights(model_name, is_dann=False)
        if pt is None:
            continue
        f1 = 0.0
        loso_path = DL_OUTPUTS / model_name / 'LOSO_exp_A' / 'metrics.json'
        if loso_path.exists():
            with open(loso_path) as f:
                m = json.load(f)
            f1 = m.get('f1_macro', 0)
        candidates.append((model_name, False, f1))

    # Vérifie les modèles DANN
    for model_name in DANN_ARCH_MAP:
        pt, _ = find_best_weights(model_name, is_dann=True)
        if pt is None:
            continue
        f1 = 0.0
        loso_path = DANN_OUTPUTS / model_name / 'LOSO_exp_A' / 'metrics.json'
        if loso_path.exists():
            with open(loso_path) as f:
                m = json.load(f)
            f1 = m.get('f1_macro', 0)
        candidates.append((model_name, True, f1))

    if not candidates:
        return None, False, 0.0

    # Trie par F1-MACRO LOSO décroissant
    candidates.sort(key=lambda x: x[2], reverse=True)
    return candidates[0]


# ============================================================================
# ADAPTATION PAR SUJET (LOSO-style)
# ============================================================================
def run_subject_adaptation(model_name: str, is_dann: bool, ft_ratio: float = 0.1):
    """
    Pour chaque sujet du test, fine-tune sur ft_ratio de ses epochs,
    évalue sur le reste. Compare avec le modèle pré-entraîné sans adaptation.

    Retourne une liste de dicts avec les résultats par sujet.
    """
    X_test_path = DATA_DIR / 'X_test.npy'
    y_test_path = DATA_DIR / 'y_test.npy'
    sid_path    = DATA_DIR / 'subject_ids_test.npy'

    if not X_test_path.exists() or not sid_path.exists():
        print("  subject_ids_test.npy introuvable, adaptation par sujet ignorée")
        return []

    X_all = np.load(X_test_path)
    y_all = np.load(y_test_path)
    sids  = np.load(sid_path).flatten()
    if len(sids) != len(X_all):
        sids = sids[:len(X_all)]

    model_base, _, err = load_pretrained_model(model_name, is_dann)
    if model_base is None:
        print(f"  Impossible de charger {model_name} : {err}")
        return []

    unique_subjects = np.unique(sids)
    results = []

    for subj in unique_subjects:
        mask = (sids == subj)
        X_s, y_s = X_all[mask], y_all[mask]
        if len(X_s) < 4:
            continue

        n_ft    = max(2, int(len(X_s) * ft_ratio))
        idx     = np.random.permutation(len(X_s))
        X_ft    = X_s[idx[:n_ft]]
        y_ft    = y_s[idx[:n_ft]]
        X_eval  = X_s[idx[n_ft:]]
        y_eval  = y_s[idx[n_ft:]]
        if len(X_eval) == 0 or len(np.unique(y_eval)) < 2:
            continue

        # Métriques avant fine-tune
        met_before = evaluate_model(model_base, X_eval, y_eval, is_dann)

        # Fine-tune (head-only pour la rapidité)
        model_ft, _ = finetune_model(
            model_base, X_ft, y_ft, X_eval, y_eval,
            strategy='head_only', is_dann=is_dann,
            lr=FT_LR_HEAD, epochs=10, patience=3)

        met_after = evaluate_model(model_ft, X_eval, y_eval, is_dann)

        results.append({
            'subject':          int(subj),
            'n_total':          len(X_s),
            'n_ft':             n_ft,
            'n_eval':           len(X_eval),
            'f1_before':        met_before['f1_macro'],
            'acc_before':       met_before['accuracy'],
            'auc_before':       met_before['auc'],
            'f1_after':         met_after['f1_macro'],
            'acc_after':        met_after['accuracy'],
            'auc_after':        met_after['auc'],
            'f1_gain':          met_after['f1_macro'] - met_before['f1_macro'],
        })
        print(f"    Sujet {int(subj):2d}: F1 {met_before['f1_macro']:.3f} → "
              f"{met_after['f1_macro']:.3f} ({met_after['f1_macro']-met_before['f1_macro']:+.3f})")

    return results


# ============================================================================
# VISUALISATIONS
# ============================================================================
def plot_finetune_curves(histories: dict, save_path: Path, model_name: str):
    """Courbes de loss/accuracy pour chaque stratégie de fine-tuning."""
    strategies = [s for s in histories if histories[s] is not None]
    if not strategies:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = {'full': '#2ECC71', 'head_only': '#3498DB', 'layerwise': '#E74C3C'}
    labels = {'full': 'Full fine-tuning', 'head_only': 'Head-only', 'layerwise': 'Layer-wise'}

    for strat in strategies:
        h   = histories[strat]
        ep  = h['epochs']
        col = colors.get(strat, 'gray')
        lbl = labels.get(strat, strat)
        axes[0].plot(ep, h['val_loss'],  '-o', ms=3, lw=1.5, color=col, label=lbl)
        axes[1].plot(ep, h['val_acc'],   '-o', ms=3, lw=1.5, color=col, label=lbl)

    for ax, ylabel, title in zip(axes,
                                  ['Val Loss', 'Val Accuracy'],
                                  ['Perte de validation (fine-tuning)',
                                   'Précision de validation (fine-tuning)']):
        ax.set_xlabel('Époque')
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    fig.suptitle(f'Fine-tuning – {model_name}', fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_before_after(rows: list, save_path: Path):
    """Barplot comparant les métriques avant/après fine-tuning par stratégie."""
    if not rows:
        return

    df = pd.DataFrame(rows)
    metrics  = ['accuracy', 'f1_macro', 'auc']
    m_labels = ['Accuracy', 'F1-Macro', 'AUC']
    strategies = df['strategy'].unique()
    x = np.arange(len(strategies))

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Fine-tuning – Avant vs Après (par stratégie)', fontsize=13, fontweight='bold')

    for ax, metric, label in zip(axes, metrics, m_labels):
        w  = 0.38
        b_vals = [df[df['strategy'] == s]['before_' + metric].values[0] for s in strategies]
        a_vals = [df[df['strategy'] == s]['after_' + metric].values[0]  for s in strategies]
        ax.bar(x - w/2, b_vals, w, label='Avant fine-tune', color='#E74C3C', alpha=0.8)
        ax.bar(x + w/2, a_vals, w, label='Après fine-tune', color='#27AE60', alpha=0.8)

        # Annotations gain
        for xi, (bv, av) in enumerate(zip(b_vals, a_vals)):
            gain = av - bv
            col  = '#27AE60' if gain >= 0 else '#E74C3C'
            ax.text(xi, max(av, bv) + 0.01, f'{gain:+.3f}',
                    ha='center', va='bottom', fontsize=8, color=col, fontweight='bold')

        ax.set_xticks(x)
        ax.set_xticklabels(strategies, rotation=30, ha='right', fontsize=9)
        ax.set_ylabel(label)
        ax.set_title(label, fontweight='bold')
        ax.legend(fontsize=8)
        ax.set_ylim(0, 1.1)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_subject_adaptation(results: list, save_path: Path):
    """Barplot du gain par sujet lors de l'adaptation personnalisée."""
    if not results:
        return

    df = pd.DataFrame(results).sort_values('f1_gain', ascending=False)
    colors = ['#27AE60' if g >= 0 else '#E74C3C' for g in df['f1_gain']]
    n_pos = (df['f1_gain'] >= 0).sum()

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Adaptation par sujet – Gain F1-MACRO après fine-tuning',
                 fontsize=13, fontweight='bold')

    # Barplot gain par sujet
    ax = axes[0]
    bars = ax.barh(df['subject'].astype(str), df['f1_gain'], color=colors, alpha=0.85)
    ax.axvline(0, color='black', lw=0.8)
    ax.set_xlabel('Δ F1-MACRO (après - avant)')
    ax.set_title(f'Gain par sujet ({n_pos}/{len(df)} sujets améliorés)', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    for bar, v in zip(bars, df['f1_gain']):
        ax.text(v + (0.003 if v >= 0 else -0.003),
                bar.get_y() + bar.get_height()/2,
                f'{v:+.3f}', va='center', ha='left' if v >= 0 else 'right', fontsize=7)

    # Scatter avant vs après
    ax2 = axes[1]
    ax2.scatter(df['f1_before'], df['f1_after'], s=100, c=colors,
                edgecolors='white', lw=0.5, zorder=5)
    for _, r in df.iterrows():
        ax2.annotate(f"S{int(r['subject'])}", (r['f1_before'], r['f1_after']),
                     textcoords='offset points', xytext=(3, 2), fontsize=7)
    lo = min(df['f1_before'].min(), df['f1_after'].min()) - 0.03
    hi = max(df['f1_before'].max(), df['f1_after'].max()) + 0.03
    ax2.plot([lo, hi], [lo, hi], 'k--', lw=1.2, label='y = x (pas de gain)')
    ax2.set_xlabel('F1-MACRO avant adaptation', fontsize=10)
    ax2.set_ylabel('F1-MACRO après adaptation',  fontsize=10)
    ax2.set_title('Avant vs Après – par sujet', fontweight='bold')
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_strategy_comparison(rows: list, save_path: Path):
    """Radar comparant les stratégies de fine-tuning."""
    if len(rows) < 2:
        return

    df   = pd.DataFrame(rows)
    cats  = ['after_accuracy', 'after_f1_macro', 'after_auc', 'after_recall', 'after_specificity']
    lbls  = ['Accuracy', 'F1-Macro', 'AUC', 'Recall', 'Specificité']
    N     = len(cats)
    angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors = plt.cm.tab10(np.linspace(0, 0.5, len(df)))

    for (_, row), color in zip(df.iterrows(), colors):
        vals  = [row[c] for c in cats] + [row[cats[0]]]
        strat = row['strategy']
        ax.plot(angles, vals, lw=2, color=color, label=strat)
        ax.fill(angles, vals, alpha=0.1, color=color)

    ax.set_thetagrids(np.degrees(angles[:-1]), lbls, fontsize=9)
    ax.set_ylim([0, 1])
    ax.set_title('Comparaison des stratégies de fine-tuning', fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.15), fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# COMPARAISON ÉTENDUE — nouvelles fonctions
# ============================================================================

DANN_TEST_JSON = PROJECT_ROOT / 'reports' / 'Tests' / 'dann'          / 'results.json'
DL_TEST_JSON   = PROJECT_ROOT / 'reports' / 'Tests' / 'deep_learning' / 'results.json'


def _load_loso_dict(json_path: Path, category: str) -> dict:
    """Charge un results.json de test et retourne {model: f1_macro}."""
    if not json_path.exists():
        return {}
    with open(json_path) as f:
        data = json.load(f)
    return {r['model']: r.get('f1_macro', 0)
            for r in data.get('all_results', [])}


def run_sample_efficiency_test(model_name: str, is_dann: bool,
                                X_val: np.ndarray, y_val: np.ndarray,
                                X_test: np.ndarray, y_test: np.ndarray) -> list:
    """
    Évalue comment la performance varie avec la taille du dataset de fine-tuning.
    Teste des fractions de 1% à 50% du val set.
    Retourne une liste de dicts {ratio, n_samples, f1_before, f1_after, gain}.
    """
    ratios = [0.01, 0.03, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]
    print(f"\n{'─'*60}")
    print(f"  EFFICACITÉ D'ÉCHANTILLONNAGE ({model_name})")
    print(f"{'─'*60}")

    model_base, _, err = load_pretrained_model(model_name, is_dann)
    if model_base is None:
        print(f"  Impossible de charger {model_name} : {err}")
        return []

    met_before = evaluate_model(model_base, X_test, y_test, is_dann)
    f1_before  = met_before['f1_macro']
    results = []
    idx = np.random.permutation(len(X_val))

    for ratio in ratios:
        n_ft = max(4, int(len(X_val) * ratio))
        if n_ft >= len(X_val) - 4:
            continue
        X_ft   = X_val[idx[:n_ft]]
        y_ft   = y_val[idx[:n_ft]]
        X_eval = X_val[idx[n_ft:]]
        y_eval = y_val[idx[n_ft:]]
        if len(np.unique(y_ft)) < 2:
            continue

        model_ft, _ = finetune_model(
            model_base, X_ft, y_ft, X_eval, y_eval,
            strategy='head_only', is_dann=is_dann,
            lr=FT_LR_HEAD, epochs=15, patience=4)

        met_after = evaluate_model(model_ft, X_test, y_test, is_dann)
        gain = met_after['f1_macro'] - f1_before
        results.append({
            'ratio':     ratio,
            'n_samples': n_ft,
            'f1_before': f1_before,
            'f1_after':  met_after['f1_macro'],
            'auc_after': met_after['auc'],
            'gain':      gain,
        })
        print(f"  {ratio*100:>5.0f}% ({n_ft:>4} samples) : "
              f"F1 {f1_before:.4f} → {met_after['f1_macro']:.4f}  ({gain:+.4f})")

    return results


def run_dann_vs_ft_comparison(X_val: np.ndarray, y_val: np.ndarray,
                               X_test: np.ndarray, y_test: np.ndarray) -> pd.DataFrame:
    """
    Pour chaque architecture disponible, compare :
      • F1 DL (LOSO sauvegardé)
      • F1 DANN (DANN-LOSO sauvegardé)
      • F1 FT (fine-tuning head-only sur 20% val)
    Retourne un DataFrame de comparaison.
    """
    print(f"\n{'─'*60}")
    print("  COMPARAISON : DL de base  vs  DANN  vs  Fine-tuning")
    print(f"{'─'*60}")

    dl_f1s   = _load_loso_dict(DL_TEST_JSON,   'DL')
    dann_f1s = _load_loso_dict(DANN_TEST_JSON, 'DANN')

    DANN_TO_DL_LOCAL = {m + '_DANN': m for m in DL_ARCH_MAP}
    rows = []

    for dann_name, dl_name in DANN_TO_DL_LOCAL.items():
        if dl_name not in dl_f1s and dann_name not in dann_f1s:
            continue

        dl_f1   = dl_f1s.get(dl_name, None)
        dann_f1 = dann_f1s.get(dann_name, None)

        # Fine-tune le modèle DL de base (si disponible)
        ft_f1 = None
        pt, _ = find_best_weights(dl_name, is_dann=False)
        if pt is not None:
            model_base, _, err = load_pretrained_model(dl_name, is_dann=False)
            if model_base is not None:
                n_ft  = max(4, int(len(X_val) * 0.20))
                idx   = np.random.permutation(len(X_val))
                X_ft  = X_val[idx[:n_ft]]
                y_ft  = y_val[idx[:n_ft]]
                X_ev  = X_val[idx[n_ft:]]
                y_ev  = y_val[idx[n_ft:]]
                if len(np.unique(y_ft)) >= 2 and len(X_ev) >= 4:
                    model_ft, _ = finetune_model(
                        model_base, X_ft, y_ft, X_ev, y_ev,
                        strategy='head_only', is_dann=False,
                        lr=FT_LR_HEAD, epochs=10, patience=3)
                    ft_f1 = evaluate_model(model_ft, X_test, y_test, is_dann=False)['f1_macro']

        rows.append({
            'architecture': dl_name,
            'f1_dl':   dl_f1,
            'f1_dann': dann_f1,
            'f1_ft':   ft_f1,
        })

        vals = []
        if dl_f1   is not None: vals.append(f"DL={dl_f1:.4f}")
        if dann_f1 is not None: vals.append(f"DANN={dann_f1:.4f}")
        if ft_f1   is not None: vals.append(f"FT={ft_f1:.4f}")
        print(f"  {dl_name:<20} : {' | '.join(vals)}")

    return pd.DataFrame(rows)


def plot_sample_efficiency(results: list, save_path: Path, model_name: str):
    """Courbe F1 en fonction du nombre de samples de fine-tuning."""
    if not results:
        return
    df = pd.DataFrame(results)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f'Efficacité d\'échantillonnage – Fine-tuning ({model_name})',
                 fontsize=12, fontweight='bold')

    # F1 vs n_samples
    ax = axes[0]
    ax.axhline(df['f1_before'].iloc[0], color='#E74C3C', ls='--', lw=2,
               label=f"Base (sans FT) : {df['f1_before'].iloc[0]:.4f}")
    ax.plot(df['n_samples'], df['f1_after'], 'o-', color='#27AE60',
            lw=2, ms=7, label='Après FT (head-only)')
    ax.fill_between(df['n_samples'],
                    df['f1_before'].iloc[0], df['f1_after'],
                    alpha=0.15, color='#27AE60')
    ax.set_xlabel("Nombre d'échantillons de fine-tuning")
    ax.set_ylabel('F1-MACRO')
    ax.set_title('F1-MACRO vs #samples FT')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    if df['f1_after'].max() > 0:
        ax.set_ylim(max(0, df['f1_after'].min() - 0.02),
                    min(1.02, df['f1_after'].max() + 0.02))

    # Gain vs ratio
    ax2 = axes[1]
    colors = ['#27AE60' if g >= 0 else '#E74C3C' for g in df['gain']]
    ax2.bar(df['ratio'] * 100, df['gain'] * 100, color=colors, alpha=0.8, width=2.5)
    ax2.axhline(0, color='black', lw=0.8)
    ax2.set_xlabel('Fraction du val set utilisée (%)')
    ax2.set_ylabel('Δ F1-MACRO (%)')
    ax2.set_title('Gain du FT selon la quantité de données')
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_dann_vs_ft_comparison(df_cmp: pd.DataFrame, save_path: Path):
    """
    Barplot multi-groupe : DL base / DANN / FT pour chaque architecture.
    Visualise quelle stratégie d'adaptation est la plus efficace.
    """
    if df_cmp.empty:
        return
    df = df_cmp.dropna(subset=['f1_dl']).copy().reset_index(drop=True)
    if df.empty:
        return

    archs = df['architecture'].values
    x     = np.arange(len(archs))
    w     = 0.26

    fig, axes = plt.subplots(1, 2, figsize=(18, 7))
    fig.suptitle('Stratégies d\'adaptation : DL de base vs DANN vs Fine-tuning',
                 fontsize=13, fontweight='bold')

    # Barplot absolu F1-MACRO
    ax = axes[0]
    if 'f1_dl' in df.columns:
        ax.bar(x - w, df['f1_dl'].fillna(0),   w, label='DL base (LOSO)',  color='#2980B9', alpha=0.85)
    if 'f1_dann' in df.columns:
        ax.bar(x,     df['f1_dann'].fillna(0),  w, label='DANN (LOSO)',     color='#27AE60', alpha=0.85)
    if 'f1_ft' in df.columns:
        ax.bar(x + w, df['f1_ft'].fillna(0),   w, label='FT head-only',    color='#F39C12', alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(archs, rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('F1-MACRO')
    ax.set_title('F1-MACRO par stratégie d\'adaptation')
    ax.legend(fontsize=9)
    ax.set_ylim(0, 1.08)
    ax.grid(axis='y', alpha=0.3)

    # Gain DANN et FT par rapport au DL base
    ax2 = axes[1]
    gain_dann = (df['f1_dann'] - df['f1_dl']).fillna(0)
    gain_ft   = (df['f1_ft']   - df['f1_dl']).fillna(0)
    ax2.bar(x - w/2, gain_dann * 100, w, label='Gain DANN', color='#27AE60', alpha=0.8)
    ax2.bar(x + w/2, gain_ft   * 100, w, label='Gain FT',   color='#F39C12', alpha=0.8)
    ax2.axhline(0, color='black', lw=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(archs, rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Δ F1-MACRO (%)')
    ax2.set_title('Gain DANN et FT vs DL de base')
    ax2.legend(fontsize=9)
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# MAIN
# ============================================================================
def main(model_name: str = None, is_dann: bool = False, ft_ratio: float = 0.2,
         extended: bool = False):
    print("=" * 75)
    print("NeuroCap – Test Fine-tuning (Adaptation de domaine / Transfer Learning)")
    print(f"Device : {DEVICE}")
    print("=" * 75)

    # ── Sélection du modèle ────────────────────────────────────────────────
    if model_name is None:
        print("\n  Sélection automatique du meilleur modèle pré-entraîné...")
        model_name, is_dann, loso_f1 = auto_select_best_model()
        if model_name is None:
            print("\n[ERREUR] Aucun modèle pré-entraîné trouvé.")
            print(f"  DL   : {DL_MODEL_BASE}")
            print(f"  DANN : {DANN_MODEL_BASE}")
            return
        dtype = 'DANN' if is_dann else 'DL'
        print(f"  Sélectionné : {model_name} ({dtype})  |  LOSO F1-MACRO = {loso_f1:.4f}")
    else:
        dtype = 'DANN' if is_dann else 'DL'
        print(f"\n  Modèle : {model_name} ({dtype})")

    # ── Chargement des données ─────────────────────────────────────────────
    print("\n  Chargement des données...")
    X_val  = np.load(DATA_DIR / 'X_val.npy')
    y_val  = np.load(DATA_DIR / 'y_val.npy')
    X_test = np.load(DATA_DIR / 'X_test.npy')
    y_test = np.load(DATA_DIR / 'y_test.npy')
    print(f"  Val   : {len(X_val)} epochs  |  Conc={np.sum(y_val==0)}, Stress={np.sum(y_val==1)}")
    print(f"  Test  : {len(X_test)} epochs  |  Conc={np.sum(y_test==0)}, Stress={np.sum(y_test==1)}")

    # Dataset de fine-tuning : fraction du val set
    n_ft   = max(10, int(len(X_val) * ft_ratio))
    idx    = np.random.permutation(len(X_val))
    X_ft   = X_val[idx[:n_ft]]
    y_ft   = y_val[idx[:n_ft]]
    X_eval = X_val[idx[n_ft:]]
    y_eval = y_val[idx[n_ft:]]
    print(f"  Fine-tuning sur {n_ft} epochs ({ft_ratio*100:.0f}% du val)")
    print(f"  Validation FT  : {len(X_eval)} epochs")

    # ── Chargement du modèle pré-entraîné ─────────────────────────────────
    print(f"\n  Chargement du modèle pré-entraîné {model_name}...")
    model_base, exp_used, err = load_pretrained_model(model_name, is_dann)
    if model_base is None:
        print(f"[ERREUR] {err}")
        return

    # ── Métriques AVANT fine-tuning ────────────────────────────────────────
    print("\n  Évaluation AVANT fine-tuning (X_test)...")
    met_before = evaluate_model(model_base, X_test, y_test, is_dann)
    print(f"  AVANT : F1m={met_before['f1_macro']:.4f}  "
          f"AUC={met_before['auc']:.4f}  Acc={met_before['accuracy']:.4f}")

    # ── Fine-tuning avec 3 stratégies ──────────────────────────────────────
    strategies = ['full', 'head_only', 'layerwise']
    strategy_rows = []
    histories = {}

    for strat in strategies:
        print(f"\n{'─'*60}")
        print(f"  Stratégie : {strat.upper()}")
        t0 = time.time()
        model_ft, history = finetune_model(
            model_base, X_ft, y_ft, X_eval, y_eval,
            strategy=strat, is_dann=is_dann,
            lr=FT_LR_FULL if strat == 'full' else FT_LR_HEAD,
            epochs=FT_EPOCHS, patience=FT_PATIENCE)
        elapsed = time.time() - t0

        met_after = evaluate_model(model_ft, X_test, y_test, is_dann)
        histories[strat] = history

        row = {
            'model':            model_name,
            'type':             dtype,
            'strategy':         strat,
            'ft_epochs':        len(history['epochs']),
            'ft_time_sec':      elapsed,
            'n_ft_samples':     n_ft,
            'before_accuracy':  met_before['accuracy'],
            'before_f1_macro':  met_before['f1_macro'],
            'before_auc':       met_before['auc'],
            'before_recall':    met_before['recall'],
            'before_specificity': met_before['specificity'],
            'after_accuracy':   met_after['accuracy'],
            'after_f1_macro':   met_after['f1_macro'],
            'after_auc':        met_after['auc'],
            'after_recall':     met_after['recall'],
            'after_specificity':met_after['specificity'],
            'after_pct_uncertain': met_after['pct_uncertain'],
            'gain_f1':          met_after['f1_macro'] - met_before['f1_macro'],
            'gain_acc':         met_after['accuracy'] - met_before['accuracy'],
            'gain_auc':         met_after['auc']      - met_before['auc'],
        }
        strategy_rows.append(row)

        sign_f1 = '+' if row['gain_f1'] >= 0 else ''
        print(f"  APRÈS  : F1m={met_after['f1_macro']:.4f}  "
              f"AUC={met_after['auc']:.4f}  Acc={met_after['accuracy']:.4f}  "
              f"(Δ F1m={sign_f1}{row['gain_f1']:.4f})  {elapsed:.1f}s")

        # Sauvegarde du modèle fine-tuné
        ft_model_path = REPORT_DIR / f"{model_name}_{strat}_finetuned.pt"
        torch.save(model_ft.state_dict(), ft_model_path)

    # ── Tableau récapitulatif ──────────────────────────────────────────────
    df_strat = pd.DataFrame(strategy_rows)
    df_strat.to_csv(REPORT_DIR / 'results_before_after.csv', index=False)

    best_strat = df_strat.loc[df_strat['after_f1_macro'].idxmax()]

    print(f"\n{'='*75}")
    print("COMPARAISON STRATÉGIES DE FINE-TUNING (sur X_test.npy)")
    print(f"{'='*75}")
    print(f"{'Stratégie':<14}  {'F1 Avant':>8}  {'F1 Après':>8}  {'Δ F1':>7}  "
          f"{'Acc Après':>9}  {'AUC Après':>9}  {'Temps':>6}")
    print("─" * 70)
    for _, r in df_strat.iterrows():
        flag = ' ←' if r['strategy'] == best_strat['strategy'] else ''
        print(f"{r['strategy']:<14}  {r['before_f1_macro']:>8.4f}  "
              f"{r['after_f1_macro']:>8.4f}  {r['gain_f1']:>+7.4f}  "
              f"{r['after_accuracy']:>9.4f}  {r['after_auc']:>9.4f}  "
              f"{r['ft_time_sec']:>5.1f}s{flag}")

    print(f"\n★ Meilleure stratégie : {best_strat['strategy']}  "
          f"(F1-MACRO = {best_strat['after_f1_macro']:.4f})")

    # ── Adaptation par sujet ───────────────────────────────────────────────
    print(f"\n{'─'*75}")
    print("ADAPTATION PAR SUJET (LOSO-style, head-only)")
    print(f"{'─'*75}")
    subj_results = run_subject_adaptation(model_name, is_dann, ft_ratio=0.1)
    if subj_results:
        df_subj = pd.DataFrame(subj_results)
        df_subj.to_csv(REPORT_DIR / 'subject_adaptation.csv', index=False)
        avg_gain = df_subj['f1_gain'].mean()
        n_pos    = (df_subj['f1_gain'] >= 0).sum()
        print(f"\n  Gain moyen F1-MACRO : {avg_gain:+.4f}")
        print(f"  Sujets améliorés    : {n_pos}/{len(df_subj)}")

    # ── Graphiques ─────────────────────────────────────────────────────────
    print("\nGénération des graphiques...")
    plot_finetune_curves(histories, REPORT_DIR / 'finetuning_curves.png', model_name)
    plot_before_after(strategy_rows, REPORT_DIR / 'before_after_bars.png')
    if len(strategy_rows) >= 2:
        plot_strategy_comparison(strategy_rows, REPORT_DIR / 'strategy_comparison.png')
    if subj_results:
        plot_subject_adaptation(subj_results, REPORT_DIR / 'subject_adaptation.png')

    # ── Rapport texte ──────────────────────────────────────────────────────
    with open(REPORT_DIR / 'finetuning_report.txt', 'w', encoding='utf-8') as f:
        f.write("NeuroCap – Rapport de Fine-tuning\n")
        f.write("=" * 65 + "\n\n")
        f.write(f"Modèle pré-entraîné  : {model_name} ({dtype})\n")
        f.write(f"Expérience de base   : {exp_used}\n")
        f.write(f"Dataset fine-tuning  : X_val.npy ({ft_ratio*100:.0f}%, {n_ft} epochs)\n")
        f.write(f"Dataset évaluation   : X_test.npy ({len(X_test)} epochs)\n\n")
        f.write("MÉTRIQUES AVANT FINE-TUNING\n")
        f.write("─" * 40 + "\n")
        f.write(f"  Accuracy   : {met_before['accuracy']:.4f}\n")
        f.write(f"  F1-Macro   : {met_before['f1_macro']:.4f}\n")
        f.write(f"  AUC        : {met_before['auc']:.4f}\n")
        f.write(f"  Recall     : {met_before['recall']:.4f}\n")
        f.write(f"  Specificité: {met_before['specificity']:.4f}\n\n")
        f.write("RÉSULTATS PAR STRATÉGIE\n")
        f.write("─" * 65 + "\n")
        f.write(f"{'Stratégie':<14} {'F1 Avant':>8} {'F1 Après':>8} {'Δ F1':>7} "
                f"{'AUC Après':>9} {'Temps':>6}\n")
        f.write("─" * 55 + "\n")
        for _, r in df_strat.iterrows():
            f.write(f"{r['strategy']:<14} {r['before_f1_macro']:>8.4f} "
                    f"{r['after_f1_macro']:>8.4f} {r['gain_f1']:>+7.4f} "
                    f"{r['after_auc']:>9.4f} {r['ft_time_sec']:>5.1f}s\n")
        f.write(f"\nMeilleure stratégie : {best_strat['strategy']}\n")
        f.write(f"  F1-MACRO final : {best_strat['after_f1_macro']:.4f}\n")
        f.write(f"  Gain total     : {best_strat['gain_f1']:+.4f}\n")
        if subj_results:
            f.write(f"\nADAPTATION PAR SUJET\n")
            f.write("─" * 40 + "\n")
            f.write(f"  Sujets testés     : {len(subj_results)}\n")
            f.write(f"  Gain moyen F1m    : {df_subj['f1_gain'].mean():+.4f}\n")
            f.write(f"  Sujets améliorés  : {(df_subj['f1_gain']>=0).sum()}/{len(df_subj)}\n")

    # ── JSON ──────────────────────────────────────────────────────────────
    best_row = best_strat.to_dict()
    with open(REPORT_DIR / 'results.json', 'w') as f:
        json.dump({
            'model': model_name,
            'type': dtype,
            'exp_used': exp_used,
            'ft_ratio': ft_ratio,
            'n_ft_samples': n_ft,
            'before': {
                'accuracy': met_before['accuracy'],
                'f1_macro': met_before['f1_macro'],
                'auc':      met_before['auc'],
                'recall':   met_before['recall'],
                'specificity': met_before['specificity'],
            },
            'best_strategy': best_strat['strategy'],
            'best_after': {
                'accuracy':    best_row['after_accuracy'],
                'f1_macro':    best_row['after_f1_macro'],
                'auc':         best_row['after_auc'],
                'recall':      best_row['after_recall'],
                'specificity': best_row['after_specificity'],
                'pct_uncertain': best_row['after_pct_uncertain'],
            },
            'gain_f1':  best_row['gain_f1'],
            'gain_acc': best_row['gain_acc'],
            'gain_auc': best_row['gain_auc'],
            'all_strategies': [
                {k: v for k, v in r.items()} for r in strategy_rows
            ],
            'subject_adaptation': subj_results if subj_results else [],
        }, f, indent=2, default=str)

    print(f"\n{'='*75}")
    print(f"Sorties : {REPORT_DIR}")
    print(f"  • results_before_after.csv    ← métriques avant/après par stratégie")
    print(f"  • finetuning_curves.png       ← courbes de loss FT")
    print(f"  • before_after_bars.png       ← comparaison graphique")
    print(f"  • strategy_comparison.png     ← radar des stratégies")
    if subj_results:
        print(f"  • subject_adaptation.png      ← adaptation par sujet")
        print(f"  • subject_adaptation.csv")
    print(f"  • finetuning_report.txt       ← rapport détaillé")
    print(f"  • results.json")
    print(f"{'='*75}")

    # ── Analyses étendues (--extended) ────────────────────────────────────
    if extended:
        print(f"\n{'='*75}")
        print("ANALYSES ÉTENDUES : EFFICACITÉ DES ÉCHANTILLONS + DANN vs FT")
        print(f"{'='*75}")

        # 1. Courbe d'efficacité des échantillons
        print("\n[1/2] Courbe d'efficacité des échantillons (sample efficiency)...")
        se_results = run_sample_efficiency_test(model_name, is_dann, X_val, y_val, X_test, y_test)
        if se_results:
            df_se = pd.DataFrame(se_results)
            df_se.to_csv(REPORT_DIR / 'sample_efficiency.csv', index=False)
            plot_sample_efficiency(se_results, REPORT_DIR / 'sample_efficiency.png', model_name)
            best_ratio = df_se.loc[df_se['f1_after'].idxmax()]
            print(f"  Meilleur ratio   : {best_ratio['ratio']*100:.0f}%  "
                  f"({int(best_ratio['n_samples'])} epochs) → F1={best_ratio['f1_after']:.4f}")

        # 2. Comparaison DANN vs Fine-tuning
        print("\n[2/2] Comparaison DANN vs Fine-tuning (tous architectures)...")
        df_cmp = run_dann_vs_ft_comparison(X_val, y_val, X_test, y_test)
        if df_cmp is not None and not df_cmp.empty:
            df_cmp.to_csv(REPORT_DIR / 'dann_vs_ft_comparison.csv', index=False)
            plot_dann_vs_ft_comparison(df_cmp, REPORT_DIR / 'dann_vs_ft_comparison.png')
            best_ft = df_cmp.loc[df_cmp['f1_ft'].idxmax()]
            print(f"\n  Meilleur modèle FT : {best_ft['architecture']}"
                  f"  F1={best_ft['f1_ft']:.4f}")
            print(f"  FT > DANN dans {(df_cmp['f1_ft'] > df_cmp['f1_dann']).sum()}/"
                  f"{len(df_cmp)} architectures")

        print(f"\n  Fichiers supplémentaires :")
        if se_results:
            print(f"    • sample_efficiency.csv / .png")
        if df_cmp is not None and not df_cmp.empty:
            print(f"    • dann_vs_ft_comparison.csv / .png")
        print(f"{'='*75}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='NeuroCap – Test Fine-tuning')
    parser.add_argument('--model',    type=str,  default=None,
                        help='Nom du modèle (ex: BiLSTM_1L, BiLSTM_1L_DANN)')
    parser.add_argument('--dann',     action='store_true',
                        help='Le modèle est un modèle DANN')
    parser.add_argument('--ft-ratio', type=float, default=0.2,
                        help='Fraction du val set pour fine-tuning (défaut 0.2)')
    parser.add_argument('--extended', action='store_true',
                        help='Activer les analyses étendues : sample efficiency + DANN vs FT')
    args = parser.parse_args()

    # Auto-détection DANN si nom contient _DANN
    if args.model and '_DANN' in args.model:
        args.dann = True

    main(model_name=args.model, is_dann=args.dann, ft_ratio=args.ft_ratio,
         extended=args.extended)
