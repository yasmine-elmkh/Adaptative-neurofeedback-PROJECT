"""
NeuroCap – Test Fine-tuning Régression
=======================================
Évalue la capacité d'adaptation rapide d'un modèle DL pré-entraîné (régression)
à un nouveau contexte via fine-tuning sur un petit jeu de données labellisé.

Cibles     : conc (score concentration 0-10) | stress (score stress 0-10)
Modèles    : toute architecture DL depuis models/Regression/DL/

Scénarios :
  1. Adaptation standard : fine-tune sur 20 % de X_val → évalue sur X_test.
  2. Adaptation par sujet (LOSO-style) : pour chaque sujet de test,
     fine-tune sur k% de ses données, évalue sur le reste.

Stratégies de fine-tuning comparées :
  A. Full         – tous les paramètres, LR très faible
  B. Head-only    – seule la dernière couche linéaire (FC / head)
  C. Layer-wise   – tête d'abord, puis dégel progressif du feature extractor

Métriques régression : MAE, RMSE, R², AUC (seuil SCORE_THRESHOLD = 5.0)

Usage :
    cd EEG_project
    python Tests/test_finetuning.py                          # auto (meilleur modèle)
    python Tests/test_finetuning.py --model EEGNet           # modèle spécifique
    python Tests/test_finetuning.py --target stress          # cible stress
    python Tests/test_finetuning.py --ft-ratio 0.1           # 10 % du val pour FT
    python Tests/test_finetuning.py --extended               # analyses étendues

Sorties :
    reports/Tests/finetuning/
        ├── results_before_after.csv
        ├── finetuning_curves.png
        ├── before_after_bars.png
        ├── subject_adaptation.png
        ├── strategy_comparison.png
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
import pandas as pd

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

# ── Chemins ────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCH_DIR     = PROJECT_ROOT / 'src' / 'models' / 'deep_learning' / 'architectures'
DL_UTILS_DIR = PROJECT_ROOT / 'src' / 'models' / 'deep_learning'
DL_MODEL_BASE = PROJECT_ROOT / 'models' / 'Regression' / 'TL'
REPORT_DIR    = PROJECT_ROOT / 'reports' / 'Tests' / 'finetuning'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROJECT_ROOT / 'src' / 'models'))
sys.path.insert(0, str(DL_UTILS_DIR))

DEVICE         = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
SCORE_THRESHOLD = 5.0
EXP_PRIORITY   = ['FULL', 'D', 'C', 'B', 'A']

# Fine-tuning hyperparamètres
FT_LR_FULL    = 1e-4
FT_LR_HEAD    = 5e-4
FT_EPOCHS     = 20
FT_PATIENCE   = 5
FT_BATCH_SIZE = 16
GRAD_CLIP     = 1.0

# Mapping dossiers TL → préfixes de fichiers
TL_STRATEGY_MAP = {
    'EEGNet_FeatureExtraction': 'EEGNet_FE',
    'EEGNet_FullFT':            'EEGNet_FFT',
    'EEGNet_LayerReplacement':  'EEGNet_LR',
}
TL_SHORTCODE_MAP = {          # shortcode CSV → dossier TL
    'LR':  'EEGNet_LayerReplacement',
    'FFT': 'EEGNet_FullFT',
    'FE':  'EEGNet_FeatureExtraction',
}
TL_CSV = (PROJECT_ROOT / 'reports' / 'Regression' / 'Comparaison_TL'
          / 'comparison_tl_regression.csv')

# Mapping architecture → (fichier_stem, classe)
DL_ARCH_MAP = {
    'CNN1D':        ('CNN1D',      'CNN1D'),
    'CNN2D':        ('CNN2D',      'CNN2D'),
    'CNN3D':        ('CNN3D',      'CNN3D'),
    'EEGNet':       ('EEGNet',     'EEGNet'),
    'TCN':          ('TCN',        'TCN'),
    'CNN_LSTM_Att': ('CNN_LSTM_Att', 'CNN_LSTM_Att'),
    'CNN_GRU_Att':  ('CNN_GRU_Att',  'CNN_GRU_Att'),
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

# ── Import metrics_professional ────────────────────────────────────────────────
try:
    from metrics_professional import compute_full_metrics
    HAS_METRICS_PRO = True
except ImportError:
    HAS_METRICS_PRO = False
    print("  ⚠ metrics_professional non disponible — métriques simplifiées")


def _basic_metrics(y_true, y_pred):
    """Métriques de régression minimales sans metrics_professional."""
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    mae  = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2   = r2_score(y_true, y_pred)
    # AUC binaire sur seuil
    from sklearn.metrics import roc_auc_score
    try:
        auc = roc_auc_score((y_true >= SCORE_THRESHOLD).astype(int),
                            (y_pred >= SCORE_THRESHOLD).astype(int))
    except Exception:
        auc = 0.5
    return {'mae': mae, 'rmse': rmse, 'r2': r2, 'auc_roc': auc}


# ── Cache des classes importées ────────────────────────────────────────────────
_model_cache: dict = {}


def import_model_class(model_name: str):
    if model_name in _model_cache:
        return _model_cache[model_name]
    if model_name not in DL_ARCH_MAP:
        raise ValueError(f"Modèle inconnu : {model_name}")
    file_stem, class_name = DL_ARCH_MAP[model_name]
    arch_path = ARCH_DIR / f'{file_stem}.py'
    if not arch_path.exists():
        raise FileNotFoundError(f"Architecture introuvable : {arch_path}")
    for p in [str(ARCH_DIR), str(DL_UTILS_DIR)]:
        if p not in sys.path:
            sys.path.insert(0, p)
    spec   = importlib.util.spec_from_file_location(file_stem, arch_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cls = getattr(module, class_name)
    _model_cache[model_name] = cls
    return cls


def find_best_tl_weights(target: str):
    """Cherche le meilleur .pt TL pour (cible) — priorité via CSV deploy_score."""
    if TL_CSV.exists():
        df = pd.read_csv(TL_CSV)
        df_t = df[df['target'] == target].sort_values('deploy_score', ascending=False)
        for _, row in df_t.iterrows():
            folder = TL_SHORTCODE_MAP.get(row['strategy'])
            prefix = TL_STRATEGY_MAP.get(folder)
            if folder and prefix:
                pt = DL_MODEL_BASE / folder / target / f"{prefix}_{target}_{row['exp']}_best.pt"
                if pt.exists():
                    return pt, row['exp']
    # Fallback: scan toutes les stratégies TL
    for folder, prefix in TL_STRATEGY_MAP.items():
        for exp in EXP_PRIORITY:
            pt = DL_MODEL_BASE / folder / target / f"{prefix}_{target}_{exp}_best.pt"
            if pt.exists():
                return pt, exp
    return None, None


def find_best_weights(model_name: str, target: str):
    """Trouve le meilleur .pt pour (modèle, cible) — priorité FULL → A.
    Pour EEGNet, cherche aussi dans les sous-dossiers TL si le chemin DL est absent."""
    model_dir = DL_MODEL_BASE / model_name / target
    for exp in EXP_PRIORITY:
        pt = model_dir / f"{model_name}_{target}_{exp}_best.pt"
        if pt.exists():
            return pt, exp
    # EEGNet : chercher dans les sous-dossiers TL
    if model_name == 'EEGNet':
        return find_best_tl_weights(target)
    return None, None


def load_pretrained_model(model_name: str, target: str):
    """Charge le modèle pré-entraîné (n_classes=1 pour régression)."""
    try:
        ModelClass = import_model_class(model_name)
    except Exception as e:
        return None, None, f"Import : {e}"
    pt_path, exp_used = find_best_weights(model_name, target)
    if pt_path is None:
        return None, None, f"Aucun .pt trouvé pour {model_name}/{target}"
    try:
        model = ModelClass(n_classes=1).to(DEVICE)
    except TypeError:
        try:
            model = ModelClass().to(DEVICE)
        except Exception as e:
            return None, None, f"Instanciation : {e}"
    try:
        state = torch.load(pt_path, map_location=DEVICE, weights_only=True)
        model.load_state_dict(state)
        print(f"  Modèle chargé : {pt_path.name} (exp {exp_used})")
        return model, exp_used, None
    except Exception as e:
        return None, None, f"Chargement poids : {e}"


# ── Données ────────────────────────────────────────────────────────────────────
def load_data(target: str):
    d = PROJECT_ROOT / 'data' / 'Regression' / 'augmented' / target
    X_val  = np.load(d / 'X_val.npy')
    y_val  = np.load(d / 'y_val.npy').astype(np.float32)
    X_test = np.load(d / 'X_test.npy')
    y_test = np.load(d / 'y_test.npy').astype(np.float32)
    sid_path = d / 'subject_ids_test.npy'
    sids = np.load(sid_path).flatten() if sid_path.exists() else None
    return X_val, y_val, X_test, y_test, sids


# ── Évaluation régression ──────────────────────────────────────────────────────
def evaluate_model(model: nn.Module, X: np.ndarray, y: np.ndarray) -> dict:
    model.eval()
    X_t = torch.FloatTensor(X)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)
    preds = []
    with torch.no_grad():
        for i in range(0, len(X_t), 256):
            out = model(X_t[i:i+256].to(DEVICE))
            if isinstance(out, (tuple, list)):
                out = out[0]
            preds.append(out.squeeze(1).cpu().numpy())
    y_pred = np.clip(np.concatenate(preds), 0.0, 10.0)
    if HAS_METRICS_PRO:
        m = compute_full_metrics(y, y_pred, SCORE_THRESHOLD)
    else:
        m = _basic_metrics(y, y_pred)
    m['y_pred'] = y_pred.tolist()
    m['n_samples'] = len(y)
    return m


# ── Fine-tuning régression ─────────────────────────────────────────────────────
def finetune_model(model: nn.Module, X_ft: np.ndarray, y_ft: np.ndarray,
                   X_eval: np.ndarray, y_eval: np.ndarray,
                   strategy: str = 'full',
                   lr: float = FT_LR_FULL,
                   epochs: int = FT_EPOCHS,
                   patience: int = FT_PATIENCE) -> tuple:
    """
    Fine-tune le modèle pré-entraîné pour la régression.

    Stratégies :
      'full'      – tous les paramètres avec lr bas
      'head_only' – seule la dernière couche linéaire
      'layerwise' – tête d'abord, dégel progressif

    Retourne : (model_ft, history)
    """
    model_ft = copy.deepcopy(model).to(DEVICE)

    # ── Configuration des paramètres ──────────────────────────────────────────
    if strategy == 'head_only':
        for p in model_ft.parameters():
            p.requires_grad = False
        head_found = False
        for attr in ['fc', 'head', 'label_head', 'classifier', 'out']:
            head = getattr(model_ft, attr, None)
            if head is not None:
                for p in head.parameters():
                    p.requires_grad = True
                head_found = True
                break
        if not head_found:
            for p in list(model_ft.parameters())[-4:]:
                p.requires_grad = True
        print(f"    [Head-only] {sum(p.numel() for p in model_ft.parameters() if p.requires_grad):,} params")

    elif strategy == 'layerwise':
        for p in model_ft.parameters():
            p.requires_grad = False
        for attr in ['fc', 'head', 'label_head', 'classifier', 'out']:
            head = getattr(model_ft, attr, None)
            if head is not None:
                for p in head.parameters():
                    p.requires_grad = True
                break
        print(f"    [Layer-wise] début head seule, dégel progressif")

    else:  # 'full'
        for p in model_ft.parameters():
            p.requires_grad = True
        print(f"    [Full] {sum(p.numel() for p in model_ft.parameters()):,} params")

    # ── DataLoader ────────────────────────────────────────────────────────────
    X_t = torch.FloatTensor(X_ft)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)
    y_t = torch.FloatTensor(y_ft)

    X_ev = torch.FloatTensor(X_eval)
    if X_ev.dim() == 2:
        X_ev = X_ev.unsqueeze(1)
    y_ev = torch.FloatTensor(y_eval)

    criterion = nn.HuberLoss(delta=1.0)
    loader    = DataLoader(TensorDataset(X_t, y_t), batch_size=FT_BATCH_SIZE, shuffle=True)
    optimizer = optim.AdamW(
        [p for p in model_ft.parameters() if p.requires_grad],
        lr=FT_LR_HEAD if strategy == 'head_only' else lr,
        weight_decay=1e-4,
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=lr * 0.01)

    history = {
        'train_loss': [], 'val_loss': [],
        'train_mae': [],  'val_mae': [],
        'strategy': strategy, 'epochs': [],
    }
    best_vl, best_st, pc = float('inf'), None, 0

    for epoch in range(epochs):
        # Dégel progressif à mi-chemin (layer-wise)
        if strategy == 'layerwise' and epoch == epochs // 2:
            for attr in ['rnn', 'feature_extractor', 'conv_layers', 'cnn', 'encoder']:
                layer = getattr(model_ft, attr, None)
                if layer is not None:
                    for p in layer.parameters():
                        p.requires_grad = True
            extra = [p for p in model_ft.parameters()
                     if p.requires_grad and not any(
                         p is q for q in optimizer.param_groups[0]['params'])]
            if extra:
                optimizer.add_param_group({'params': extra, 'lr': lr * 0.1})
            print(f"    [Layer-wise] époque {epoch+1} : dégel feature extractor")

        model_ft.train()
        tl_sum = tmae_sum = n_tr = 0
        for xb, yb in loader:
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad(set_to_none=True)
            out    = model_ft(xb)
            logits = out[0] if isinstance(out, (tuple, list)) else out
            pred   = logits.squeeze(1)
            loss   = criterion(pred, yb)
            loss.backward()
            nn.utils.clip_grad_norm_(model_ft.parameters(), GRAD_CLIP)
            optimizer.step()
            n       = len(yb)
            tl_sum  += loss.item() * n
            tmae_sum += torch.abs(pred.detach() - yb).sum().item()
            n_tr    += n

        scheduler.step()
        train_loss = tl_sum   / max(n_tr, 1)
        train_mae  = tmae_sum / max(n_tr, 1)

        model_ft.eval()
        with torch.no_grad():
            out_val = model_ft(X_ev.to(DEVICE))
            lv      = out_val[0] if isinstance(out_val, (tuple, list)) else out_val
            pred_v  = lv.squeeze(1)
            val_loss = criterion(pred_v, y_ev.to(DEVICE)).item()
            val_mae  = float(torch.abs(pred_v - y_ev.to(DEVICE)).mean())

        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['train_mae'].append(train_mae)
        history['val_mae'].append(val_mae)
        history['epochs'].append(epoch + 1)

        if val_loss < best_vl:
            best_vl, best_st, pc = val_loss, copy.deepcopy(model_ft.state_dict()), 0
        else:
            pc += 1
            if pc >= patience:
                print(f"    Early stopping à l'époque {epoch+1}")
                break

    if best_st:
        model_ft.load_state_dict(best_st)
    return model_ft, history


# ── Sélection automatique du meilleur modèle ──────────────────────────────────
def auto_select_best_model(target: str):
    """Choisit le modèle ayant le meilleur R² LOSO disponible."""
    candidates = []
    for model_name in DL_ARCH_MAP:
        pt, _ = find_best_weights(model_name, target)
        if pt is None:
            continue
        r2 = 0.0
        loso_path = (PROJECT_ROOT / 'reports' / 'Regression' / 'DL'
                     / model_name / target / 'LOSO' / 'metrics.json')
        if loso_path.exists():
            with open(loso_path) as f:
                m = json.load(f)
            r2 = m.get('r2', 0.0)
        candidates.append((model_name, r2))
    if not candidates:
        return None, 0.0
    candidates.sort(key=lambda x: x[1], reverse=True)
    return candidates[0]


# ── Adaptation par sujet ───────────────────────────────────────────────────────
def run_subject_adaptation(model_name: str, target: str, ft_ratio: float = 0.1):
    X_test_path = PROJECT_ROOT / 'data' / 'Regression' / 'augmented' / target / 'X_test.npy'
    y_test_path = PROJECT_ROOT / 'data' / 'Regression' / 'augmented' / target / 'y_test.npy'
    sid_path    = PROJECT_ROOT / 'data' / 'Regression' / 'augmented' / target / 'subject_ids_test.npy'

    if not X_test_path.exists() or not sid_path.exists():
        print("  subject_ids_test.npy introuvable — adaptation par sujet ignorée")
        return []

    X_all = np.load(X_test_path)
    y_all = np.load(y_test_path).astype(np.float32)
    sids  = np.load(sid_path).flatten()
    if len(sids) != len(X_all):
        sids = sids[:len(X_all)]

    model_base, _, err = load_pretrained_model(model_name, target)
    if model_base is None:
        print(f"  Impossible de charger {model_name}/{target} : {err}")
        return []

    results = []
    for subj in np.unique(sids):
        mask = sids == subj
        X_s, y_s = X_all[mask], y_all[mask]
        if len(X_s) < 4:
            continue
        n_ft   = max(2, int(len(X_s) * ft_ratio))
        idx    = np.random.permutation(len(X_s))
        X_ft   = X_s[idx[:n_ft]];    y_ft   = y_s[idx[:n_ft]]
        X_eval = X_s[idx[n_ft:]];    y_eval = y_s[idx[n_ft:]]
        if len(X_eval) == 0:
            continue

        met_before = evaluate_model(model_base, X_eval, y_eval)
        model_ft, _ = finetune_model(
            model_base, X_ft, y_ft, X_eval, y_eval,
            strategy='head_only', lr=FT_LR_HEAD, epochs=10, patience=3)
        met_after = evaluate_model(model_ft, X_eval, y_eval)

        mae_gain = met_before['mae'] - met_after['mae']   # positif = amélioration
        r2_gain  = met_after['r2']  - met_before['r2']

        results.append({
            'subject':      int(subj),
            'n_total':      len(X_s),
            'n_ft':         n_ft,
            'n_eval':       len(X_eval),
            'mae_before':   met_before['mae'],
            'mae_after':    met_after['mae'],
            'mae_gain':     mae_gain,
            'r2_before':    met_before['r2'],
            'r2_after':     met_after['r2'],
            'r2_gain':      r2_gain,
        })
        print(f"    Sujet {int(subj):2d}: MAE {met_before['mae']:.3f} → "
              f"{met_after['mae']:.3f} (Δ={mae_gain:+.3f})  "
              f"R² {met_before['r2']:.3f} → {met_after['r2']:.3f}")

    return results


# ── Visualisations ─────────────────────────────────────────────────────────────
def plot_finetune_curves(histories: dict, save_path: Path, model_name: str, target: str):
    strategies = [s for s in histories if histories[s] is not None]
    if not strategies:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = {'full': '#2ECC71', 'head_only': '#3498DB', 'layerwise': '#E74C3C'}
    labels = {'full': 'Full', 'head_only': 'Head-only', 'layerwise': 'Layer-wise'}
    for strat in strategies:
        h   = histories[strat]
        col = colors.get(strat, 'gray')
        lbl = labels.get(strat, strat)
        axes[0].plot(h['epochs'], h['val_loss'], '-o', ms=3, lw=1.5, color=col, label=lbl)
        axes[1].plot(h['epochs'], h['val_mae'],  '-o', ms=3, lw=1.5, color=col, label=lbl)
    for ax, ylabel, title in zip(axes,
                                  ['Huber Val Loss', 'Val MAE'],
                                  ['Perte de validation', 'MAE de validation']):
        ax.set_xlabel('Époque')
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontweight='bold')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
    fig.suptitle(f'Fine-tuning – {model_name} / {target.upper()}', fontsize=13)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_before_after(rows: list, save_path: Path):
    if not rows:
        return
    df = pd.DataFrame(rows)
    strategies = df['strategy'].unique()
    x = np.arange(len(strategies))

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Fine-tuning Régression – Avant vs Après (par stratégie)',
                 fontsize=13, fontweight='bold')

    for ax, (metric_b, metric_a, ylabel) in zip(axes, [
        ('before_mae',  'after_mae',  'MAE (↓)'),
        ('before_r2',   'after_r2',   'R² (↑)'),
        ('before_auc',  'after_auc',  'AUC'),
    ]):
        w = 0.38
        b_vals = [df[df['strategy'] == s][metric_b].values[0] for s in strategies]
        a_vals = [df[df['strategy'] == s][metric_a].values[0] for s in strategies]
        ax.bar(x - w/2, b_vals, w, label='Avant FT', color='#E74C3C', alpha=0.8)
        ax.bar(x + w/2, a_vals, w, label='Après FT', color='#27AE60', alpha=0.8)
        for xi, (bv, av) in enumerate(zip(b_vals, a_vals)):
            gain = av - bv
            col  = '#27AE60' if (gain >= 0 and ylabel != 'MAE (↓)') or \
                               (gain <= 0 and ylabel == 'MAE (↓)') else '#E74C3C'
            ax.text(xi, max(av, bv) + 0.005, f'{gain:+.3f}',
                    ha='center', va='bottom', fontsize=8, color=col, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(strategies, rotation=30, ha='right', fontsize=9)
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_subject_adaptation(results: list, save_path: Path):
    if not results:
        return
    df = pd.DataFrame(results).sort_values('mae_gain', ascending=False)
    colors_mae = ['#27AE60' if g >= 0 else '#E74C3C' for g in df['mae_gain']]
    n_pos = (df['mae_gain'] >= 0).sum()

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('Adaptation par sujet – Gain MAE après fine-tuning',
                 fontsize=13, fontweight='bold')

    ax = axes[0]
    bars = ax.barh(df['subject'].astype(str), df['mae_gain'], color=colors_mae, alpha=0.85)
    ax.axvline(0, color='black', lw=0.8)
    ax.set_xlabel('Δ MAE (avant − après, ↑ = amélioration)')
    ax.set_title(f'Gain MAE par sujet ({n_pos}/{len(df)} sujets améliorés)', fontweight='bold')
    ax.grid(axis='x', alpha=0.3)

    ax2 = axes[1]
    ax2.scatter(df['r2_before'], df['r2_after'], s=100, c=colors_mae,
                edgecolors='white', lw=0.5, zorder=5)
    for _, r in df.iterrows():
        ax2.annotate(f"S{int(r['subject'])}", (r['r2_before'], r['r2_after']),
                     textcoords='offset points', xytext=(3, 2), fontsize=7)
    lo = min(df['r2_before'].min(), df['r2_after'].min()) - 0.03
    hi = max(df['r2_before'].max(), df['r2_after'].max()) + 0.03
    ax2.plot([lo, hi], [lo, hi], 'k--', lw=1.2, label='y = x')
    ax2.set_xlabel('R² avant adaptation')
    ax2.set_ylabel('R² après adaptation')
    ax2.set_title('R² Avant vs Après – par sujet', fontweight='bold')
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ── Main ───────────────────────────────────────────────────────────────────────
def main(model_name: str = None, target: str = 'conc',
         ft_ratio: float = 0.2, extended: bool = False):
    print("=" * 75)
    print("NeuroCap – Test Fine-tuning Régression")
    print(f"Device : {DEVICE}  |  Cible : {target.upper()}")
    print("=" * 75)

    # Sélection du modèle
    if model_name is None:
        print(f"\n  Sélection automatique du meilleur modèle ({target.upper()})...")
        model_name, loso_r2 = auto_select_best_model(target)
        if model_name is None:
            print(f"\n[ERREUR] Aucun modèle pré-entraîné trouvé dans {DL_MODEL_BASE}")
            return
        print(f"  Sélectionné : {model_name}  |  LOSO R² = {loso_r2:.4f}")
    else:
        print(f"\n  Modèle : {model_name} / {target.upper()}")

    # Chargement des données
    print("\n  Chargement des données...")
    try:
        X_val, y_val, X_test, y_test, sids = load_data(target)
    except FileNotFoundError as e:
        print(f"[ERREUR] Données introuvables : {e}")
        return
    print(f"  Val  : {len(X_val)} epochs  | scores [{y_val.min():.1f}–{y_val.max():.1f}]")
    print(f"  Test : {len(X_test)} epochs  | scores [{y_test.min():.1f}–{y_test.max():.1f}]")

    # Dataset de fine-tuning : fraction du val set
    n_ft   = max(10, int(len(X_val) * ft_ratio))
    idx    = np.random.permutation(len(X_val))
    X_ft   = X_val[idx[:n_ft]];    y_ft   = y_val[idx[:n_ft]]
    X_eval = X_val[idx[n_ft:]];    y_eval = y_val[idx[n_ft:]]
    print(f"  Fine-tuning sur {n_ft} epochs ({ft_ratio*100:.0f}% du val)")
    print(f"  Validation FT  : {len(X_eval)} epochs")

    # Chargement du modèle pré-entraîné
    print(f"\n  Chargement du modèle pré-entraîné {model_name}/{target}...")
    model_base, exp_used, err = load_pretrained_model(model_name, target)
    if model_base is None:
        print(f"[ERREUR] {err}")
        return

    # Métriques AVANT fine-tuning
    print("\n  Évaluation AVANT fine-tuning (X_test)...")
    met_before = evaluate_model(model_base, X_test, y_test)
    print(f"  AVANT : MAE={met_before['mae']:.4f}  "
          f"R²={met_before['r2']:.4f}  AUC={met_before['auc_roc']:.4f}")

    # Fine-tuning 3 stratégies
    strategies    = ['full', 'head_only', 'layerwise']
    strategy_rows = []
    histories     = {}

    for strat in strategies:
        print(f"\n{'─'*60}")
        print(f"  Stratégie : {strat.upper()}")
        t0 = time.time()
        model_ft, history = finetune_model(
            model_base, X_ft, y_ft, X_eval, y_eval,
            strategy=strat,
            lr=FT_LR_FULL if strat == 'full' else FT_LR_HEAD,
            epochs=FT_EPOCHS, patience=FT_PATIENCE)
        elapsed = time.time() - t0

        met_after = evaluate_model(model_ft, X_test, y_test)
        histories[strat] = history

        row = {
            'model':          model_name,
            'target':         target,
            'strategy':       strat,
            'ft_epochs':      len(history['epochs']),
            'ft_time_sec':    elapsed,
            'n_ft_samples':   n_ft,
            'before_mae':     met_before['mae'],
            'before_r2':      met_before['r2'],
            'before_auc':     met_before['auc_roc'],
            'after_mae':      met_after['mae'],
            'after_r2':       met_after['r2'],
            'after_auc':      met_after['auc_roc'],
            'gain_mae':       met_before['mae'] - met_after['mae'],   # ↑ = meilleur
            'gain_r2':        met_after['r2']   - met_before['r2'],
            'gain_auc':       met_after['auc_roc'] - met_before['auc_roc'],
        }
        strategy_rows.append(row)

        print(f"  APRÈS  : MAE={met_after['mae']:.4f}  "
              f"R²={met_after['r2']:.4f}  AUC={met_after['auc_roc']:.4f}  "
              f"(ΔMAE={row['gain_mae']:+.4f}  ΔR²={row['gain_r2']:+.4f})  {elapsed:.1f}s")

        ft_model_path = REPORT_DIR / f"{model_name}_{target}_{strat}_finetuned.pt"
        torch.save(model_ft.state_dict(), ft_model_path)

    # Tableau récapitulatif
    df_strat = pd.DataFrame(strategy_rows)
    df_strat.to_csv(REPORT_DIR / 'results_before_after.csv', index=False)
    best_strat = df_strat.loc[df_strat['after_r2'].idxmax()]

    print(f"\n{'='*75}")
    print(f"COMPARAISON STRATÉGIES DE FINE-TUNING (sur X_test.npy / {target.upper()})")
    print(f"{'='*75}")
    print(f"{'Stratégie':<14}  {'MAE Avant':>9}  {'MAE Après':>9}  {'Δ MAE':>7}  "
          f"{'R² Avant':>8}  {'R² Après':>8}  {'Δ R²':>6}  {'Temps':>6}")
    print("─" * 80)
    for _, r in df_strat.iterrows():
        flag = ' ←' if r['strategy'] == best_strat['strategy'] else ''
        print(f"{r['strategy']:<14}  {r['before_mae']:>9.4f}  {r['after_mae']:>9.4f}  "
              f"{r['gain_mae']:>+7.4f}  {r['before_r2']:>8.4f}  {r['after_r2']:>8.4f}  "
              f"{r['gain_r2']:>+6.4f}  {r['ft_time_sec']:>5.1f}s{flag}")

    print(f"\n★ Meilleure stratégie : {best_strat['strategy']}  "
          f"(R² = {best_strat['after_r2']:.4f}  MAE = {best_strat['after_mae']:.4f})")

    # Adaptation par sujet
    print(f"\n{'─'*75}")
    print("ADAPTATION PAR SUJET (LOSO-style, head-only)")
    print(f"{'─'*75}")
    subj_results = run_subject_adaptation(model_name, target, ft_ratio=0.1)
    df_subj = None
    if subj_results:
        df_subj = pd.DataFrame(subj_results)
        df_subj.to_csv(REPORT_DIR / 'subject_adaptation.csv', index=False)
        avg_mae_gain = df_subj['mae_gain'].mean()
        avg_r2_gain  = df_subj['r2_gain'].mean()
        n_pos_mae    = (df_subj['mae_gain'] >= 0).sum()
        print(f"\n  Gain moyen MAE : {avg_mae_gain:+.4f}")
        print(f"  Gain moyen R²  : {avg_r2_gain:+.4f}")
        print(f"  Sujets améliorés (MAE) : {n_pos_mae}/{len(df_subj)}")

    # Graphiques
    print("\nGénération des graphiques...")
    plot_finetune_curves(histories, REPORT_DIR / 'finetuning_curves.png', model_name, target)
    plot_before_after(strategy_rows, REPORT_DIR / 'before_after_bars.png')
    if subj_results:
        plot_subject_adaptation(subj_results, REPORT_DIR / 'subject_adaptation.png')

    # Rapport texte
    with open(REPORT_DIR / 'finetuning_report.txt', 'w', encoding='utf-8') as f:
        f.write("NeuroCap – Rapport de Fine-tuning Régression\n")
        f.write("=" * 65 + "\n\n")
        f.write(f"Modèle pré-entraîné  : {model_name}\n")
        f.write(f"Cible                : {target.upper()}\n")
        f.write(f"Expérience de base   : {exp_used}\n")
        f.write(f"Dataset fine-tuning  : X_val.npy ({ft_ratio*100:.0f}%, {n_ft} epochs)\n")
        f.write(f"Dataset évaluation   : X_test.npy ({len(X_test)} epochs)\n\n")
        f.write("MÉTRIQUES AVANT FINE-TUNING\n" + "─" * 40 + "\n")
        f.write(f"  MAE   : {met_before['mae']:.4f}\n")
        f.write(f"  RMSE  : {met_before.get('rmse', 0):.4f}\n")
        f.write(f"  R²    : {met_before['r2']:.4f}\n")
        f.write(f"  AUC   : {met_before['auc_roc']:.4f}\n\n")
        f.write("RÉSULTATS PAR STRATÉGIE\n" + "─" * 65 + "\n")
        f.write(f"{'Stratégie':<14} {'MAE Avant':>9} {'MAE Après':>9} {'Δ MAE':>7} "
                f"{'R² Après':>8} {'Temps':>6}\n")
        f.write("─" * 55 + "\n")
        for _, r in df_strat.iterrows():
            f.write(f"{r['strategy']:<14} {r['before_mae']:>9.4f} "
                    f"{r['after_mae']:>9.4f} {r['gain_mae']:>+7.4f} "
                    f"{r['after_r2']:>8.4f} {r['ft_time_sec']:>5.1f}s\n")
        f.write(f"\nMeilleure stratégie : {best_strat['strategy']}\n")
        f.write(f"  MAE final : {best_strat['after_mae']:.4f}\n")
        f.write(f"  R² final  : {best_strat['after_r2']:.4f}\n")
        if df_subj is not None:
            f.write(f"\nADAPTATION PAR SUJET\n" + "─" * 40 + "\n")
            f.write(f"  Sujets testés     : {len(df_subj)}\n")
            f.write(f"  Gain moyen MAE    : {df_subj['mae_gain'].mean():+.4f}\n")
            f.write(f"  Gain moyen R²     : {df_subj['r2_gain'].mean():+.4f}\n")
            f.write(f"  Sujets améliorés  : {(df_subj['mae_gain']>=0).sum()}/{len(df_subj)}\n")

    # JSON
    best_row = best_strat.to_dict()
    with open(REPORT_DIR / 'results.json', 'w') as f:
        json.dump({
            'model':          model_name,
            'target':         target,
            'exp_used':       exp_used,
            'ft_ratio':       ft_ratio,
            'n_ft_samples':   n_ft,
            'before': {
                'mae': met_before['mae'], 'r2': met_before['r2'],
                'auc': met_before['auc_roc'],
            },
            'best_strategy': best_strat['strategy'],
            'best_after': {
                'mae': best_row['after_mae'], 'r2': best_row['after_r2'],
                'auc': best_row['after_auc'],
            },
            'gain_mae': best_row['gain_mae'],
            'gain_r2':  best_row['gain_r2'],
            'all_strategies': [{k: v for k, v in r.items()} for r in strategy_rows],
            'subject_adaptation': subj_results if subj_results else [],
        }, f, indent=2, default=str)

    print(f"\n{'='*75}")
    print(f"Sorties : {REPORT_DIR}")
    print(f"  • results_before_after.csv    ← métriques avant/après par stratégie")
    print(f"  • finetuning_curves.png       ← courbes Huber Loss / MAE")
    print(f"  • before_after_bars.png       ← comparaison graphique")
    if subj_results:
        print(f"  • subject_adaptation.png / .csv")
    print(f"  • finetuning_report.txt       ← rapport détaillé")
    print(f"  • results.json")
    print(f"{'='*75}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='NeuroCap – Test Fine-tuning Régression')
    parser.add_argument('--model',    type=str, default=None,
                        help='Nom du modèle (ex: EEGNet, BiLSTM_1L)')
    parser.add_argument('--target',   type=str, default='conc',
                        choices=['conc', 'stress'],
                        help='Cible de régression (défaut : conc)')
    parser.add_argument('--ft-ratio', type=float, default=0.2,
                        help='Fraction du val set pour fine-tuning (défaut 0.2)')
    parser.add_argument('--extended', action='store_true',
                        help='Analyses étendues (sample efficiency)')
    args = parser.parse_args()

    main(model_name=args.model, target=args.target,
         ft_ratio=args.ft_ratio, extended=args.extended)
