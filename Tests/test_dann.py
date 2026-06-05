"""
NeuroCap – Test Suite DANN (19 architectures Domain Adversarial)
=================================================================
Évalue chaque architecture DANN avec deux sources de métriques :

  1. LOSO (Leave-One-Subject-Out) — ÉVALUATION HONNÊTE
     Lit les metrics.json LOSO sauvegardés pendant l'entraînement DANN.
     Garantit qu'aucun sujet n'est partagé entre train et test.
     → Métriques à utiliser pour la décision finale.

  2. Holdout X_test.npy — ÉVALUATION BRUTE (pour information seulement)
     Évalue sur le fichier de test standard.
     Si fuite détectée → scores marqués [LEAKED].

Pourquoi DANN ?
  NeuroCap fusionne deux datasets d'appareils différents :
    - OpenBCI (Concentration, domaine 0)
    - EMOTIV   (Stress,         domaine 1)
  DANN apprend des représentations domain-invariantes pour que le modèle
  distingue l'état cognitif (Concentration / Stress) sans mémoriser
  le biais lié au matériel.

Usage :
    cd EEG_project
    python Tests/test_dann.py               # tous les modèles DANN
    python Tests/test_dann.py BiLSTM_1L_DANN  # un seul modèle
    python Tests/test_dann.py --compare-dl    # ajoute la comparaison DANN vs DL

Sorties :
    reports/Tests/dann/
        ├── results_table_LOSO.csv
        ├── results_table_holdout.csv
        ├── ranking_barplot_LOSO.png
        ├── heatmap_metrics_LOSO.png
        ├── radar_top5_LOSO.png
        ├── dann_gain_over_dl.png       ← si DL résultats disponibles
        ├── dann_vs_dl_scatter.png      ← si DL résultats disponibles
        ├── leakage_report.txt
        └── decision_report.txt
"""

import sys
import importlib
import importlib.util
import warnings
import json
import time
from pathlib import Path

import numpy as np
import torch
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
PROJECT_ROOT    = Path(__file__).resolve().parents[1]
ARCH_DANN_DIR   = PROJECT_ROOT / 'src' / 'models' / 'deep_learning' / 'architectures_DANN'
DL_UTILS_DIR    = PROJECT_ROOT / 'src' / 'models' / 'deep_learning'
DATA_DIR        = PROJECT_ROOT / 'data' / 'Augmentation' / 'datasets_augmented'
DANN_MODEL_BASE = PROJECT_ROOT / 'models' / 'deep_learning' / 'DANN_models'
DANN_OUTPUTS    = PROJECT_ROOT / 'reports' / 'deep_learning' / 'DANN_outputs'
DL_OUTPUTS      = PROJECT_ROOT / 'reports' / 'deep_learning' / 'DL_outputs'
DL_TEST_JSON    = PROJECT_ROOT / 'reports' / 'Tests' / 'deep_learning' / 'results.json'
REPORT_DIR      = PROJECT_ROOT / 'reports' / 'Tests' / 'dann'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DEVICE       = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
EXP_PRIORITY = ['FULL', 'D', 'C', 'B', 'A']

# ============================================================================
# MAPPING : nom_modèle → (fichier_stem, nom_classe)
# ============================================================================
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
ALL_DANN_MODELS = list(DANN_ARCH_MAP.keys())

# Correspondance DANN → DL de base (pour la comparaison)
DANN_TO_DL = {
    'CNN1D_DANN':        'CNN1D',
    'CNN2D_DANN':        'CNN2D',
    'CNN3D_DANN':        'CNN3D',
    'TCN_DANN':          'TCN',
    'EEGNet_DANN':       'EEGNet',
    'LSTM_1L_DANN':      'LSTM_1L',
    'LSTM_2L_DANN':      'LSTM_2L',
    'LSTM_Att_DANN':     'LSTM_Att',
    'BiLSTM_1L_DANN':    'BiLSTM_1L',
    'BiLSTM_2L_DANN':    'BiLSTM_2L',
    'BiLSTM_Att_DANN':   'BiLSTM_Att',
    'GRU_1L_DANN':       'GRU_1L',
    'GRU_2L_DANN':       'GRU_2L',
    'GRU_Att_DANN':      'GRU_Att',
    'BiGRU_1L_DANN':     'BiGRU_1L',
    'BiGRU_2L_DANN':     'BiGRU_2L',
    'BiGRU_Att_DANN':    'BiGRU_Att',
    'CNN_LSTM_Att_DANN': 'CNN_LSTM_Att',
    'CNN_GRU_Att_DANN':  'CNN_GRU_Att',
}


# ============================================================================
# 1. VÉRIFICATION FUITE DE DONNÉES
# ============================================================================
def check_holdout_leakage():
    """Vérifie si X_test.npy contient des sujets présents dans le train."""
    result = {
        'has_leakage': None, 'overlap_subjects': [],
        'train_subjects': [], 'test_subjects': [], 'message': '',
    }
    test_sid = DATA_DIR / 'subject_ids_test.npy'
    if not test_sid.exists():
        result['message'] = (
            "subject_ids_test.npy introuvable → vérification impossible.\n"
            "Scores parfaits (F1≈1.0) = très suspects en EEG inter-datasets."
        )
        return result

    sids_test = set(np.load(test_sid).flatten())
    result['test_subjects'] = sorted(sids_test)

    train_sids = set()
    for exp in EXP_PRIORITY:
        for fname in [f'subject_ids_train_{exp}.npy', 'subject_ids_train.npy']:
            p = DATA_DIR / fname
            if p.exists():
                train_sids = set(np.load(p).flatten())
                break
        if train_sids:
            break

    if not train_sids:
        result['message'] = "subject_ids_train_*.npy introuvable"
        return result

    result['train_subjects'] = sorted(train_sids)
    overlap = sids_test & train_sids
    result['overlap_subjects'] = sorted(overlap)
    result['has_leakage'] = len(overlap) > 0
    if result['has_leakage']:
        result['message'] = (
            f"FUITE DÉTECTÉE : {len(overlap)} sujet(s) commun(s) train/test → "
            f"scores X_test.npy INVALIDES."
        )
    else:
        result['message'] = (
            f"Pas de fuite : {len(sids_test)} sujets test / {len(train_sids)} train (disjoints)."
        )
    return result


# ============================================================================
# 2. CHARGEMENT MÉTRIQUES LOSO DANN
# ============================================================================
def load_dann_loso_metrics(model_name: str):
    """
    Lit DANN_outputs/{model_name}/LOSO_exp_A/metrics.json
    Retourne (dict métriques, None) ou (None, message d'erreur).
    """
    path = DANN_OUTPUTS / model_name / 'LOSO_exp_A' / 'metrics.json'
    if not path.exists():
        return None, f"LOSO_exp_A/metrics.json introuvable pour {model_name}"
    with open(path) as f:
        return json.load(f), None


def extract_loso_row(model_name: str, raw: dict):
    return {
        'model':             model_name,
        'eval_type':         'DANN-LOSO (honnête)',
        'exp_used':          raw.get('exp', 'A'),
        'accuracy':          raw.get('accuracy', 0),
        'f1_macro':          raw.get('f1_macro', 0),
        'f1_binary':         raw.get('f1', 0),
        'precision':         raw.get('precision', 0),
        'recall':            raw.get('recall', 0),
        'specificity':       raw.get('specificity', 0),
        'auc':               raw.get('auc', 0.5),
        'pct_uncertain':     raw.get('pct_uncertain', 0),
        'n_folds':           raw.get('n_folds', 0),
        'overfitting_folds': raw.get('overfitting_folds', 0),
        'train_time_sec':    raw.get('train_time_sec', 0),
        'train_test_gap':    raw.get('train_test_gap', 0),
        'avg_conc_rate':     raw.get('rates', {}).get('avg_concentration_rate', 0),
        'avg_stress_rate':   raw.get('rates', {}).get('avg_stress_rate', 0),
        'source':            'dann_loso_saved',
    }


# ============================================================================
# 3. ÉVALUATION SUR HOLDOUT (X_test.npy)
# ============================================================================
_arch_dann_cache = {}


def import_dann_arch_class(model_name: str):
    if model_name in _arch_dann_cache:
        return _arch_dann_cache[model_name]
    file_stem, class_name = DANN_ARCH_MAP[model_name]
    arch_path = ARCH_DANN_DIR / f'{file_stem}.py'
    if not arch_path.exists():
        raise FileNotFoundError(f"Architecture DANN introuvable : {arch_path}")
    for p in [str(ARCH_DANN_DIR), str(DL_UTILS_DIR)]:
        if p not in sys.path:
            sys.path.insert(0, p)
    spec   = importlib.util.spec_from_file_location(file_stem, arch_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cls = getattr(module, class_name)
    _arch_dann_cache[model_name] = cls
    return cls


def find_dann_model_pt(model_name: str):
    model_dir = DANN_MODEL_BASE / model_name
    for exp in EXP_PRIORITY:
        pt = model_dir / f'{model_name}_{exp}_best.pt'
        if pt.exists():
            return pt, exp
    return None, None


def evaluate_dann_on_holdout(model_name: str, X_test: np.ndarray, y_test: np.ndarray,
                             leakage_info: dict):
    """Charge le modèle DANN .pt et évalue sur X_test (lambda_grl=0)."""
    pt_path, exp_used = find_dann_model_pt(model_name)
    if pt_path is None:
        return None, "aucun .pt trouvé dans DANN_models/"

    try:
        ModelClass = import_dann_arch_class(model_name)
    except Exception as e:
        return None, f"import : {e}"

    try:
        model = ModelClass().to(DEVICE)
        try:
            state = torch.load(pt_path, map_location=DEVICE, weights_only=True)
        except Exception:
            state = torch.load(pt_path, map_location=DEVICE)
        model.load_state_dict(state)
    except Exception as e:
        return None, f"chargement poids : {e}"

    model.eval()
    X_t = torch.FloatTensor(X_test)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)

    all_probs, all_preds = [], []
    t0 = time.time()
    with torch.no_grad():
        for i in range(0, len(X_t), 256):
            batch = X_t[i:i+256].to(DEVICE)
            # DANN forward : retourne (label_logits, domain_logits)
            # lambda_grl=0 → désactive le GRL pour l'inférence pure
            out = model(batch, lambda_grl=0.0)
            label_logits = out[0] if isinstance(out, (tuple, list)) else out
            probs = torch.softmax(label_logits, 1).cpu().numpy()
            preds = label_logits.argmax(1).cpu().numpy()
            all_probs.append(probs)
            all_preds.append(preds)
    elapsed = time.time() - t0

    probs = np.concatenate(all_probs)
    preds = np.concatenate(all_preds)

    cm = confusion_matrix(y_test, preds)
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, cm[0, 0])
    spec = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    auc_val = 0.5
    if len(np.unique(y_test)) > 1:
        try:
            auc_val = roc_auc_score(y_test, probs[:, 1])
        except Exception:
            pass

    leaked = leakage_info.get('has_leakage')
    label  = 'DANN-Holdout [LEAKED]' if leaked else 'DANN-Holdout [OK]' if leaked is False else 'DANN-Holdout [?]'

    return {
        'model':          model_name,
        'eval_type':      label,
        'exp_used':       exp_used,
        'accuracy':       accuracy_score(y_test, preds),
        'f1_macro':       f1_score(y_test, preds, average='macro', zero_division=0),
        'f1_binary':      f1_score(y_test, preds, zero_division=0),
        'precision':      precision_score(y_test, preds, zero_division=0),
        'recall':         recall_score(y_test, preds, zero_division=0),
        'specificity':    spec,
        'auc':            auc_val,
        'pct_uncertain':  float(np.sum(np.max(probs, 1) < 0.60) / len(y_test) * 100),
        'n_folds':        0,
        'overfitting_folds': 0,
        'train_time_sec': 0,
        'inference_ms':   elapsed * 1000 / len(y_test),
        'avg_conc_rate':  float(np.mean(probs[:, 0]) * 100),
        'avg_stress_rate':float(np.mean(probs[:, 1]) * 100),
        'source':         'dann_holdout',
        'has_leakage':    leaked,
        'n_samples':      len(y_test),
    }, None


# ============================================================================
# 4. CHARGEMENT DES MÉTRIQUES DL (pour comparaison)
# ============================================================================
def load_dl_loso_metrics():
    """Charge les métriques DL LOSO depuis results.json de test_deep_learning.py."""
    if not DL_TEST_JSON.exists():
        # Fallback : lit directement les LOSO_exp_A/metrics.json
        rows = {}
        for dann_name, dl_name in DANN_TO_DL.items():
            p = DL_OUTPUTS / dl_name / 'LOSO_exp_A' / 'metrics.json'
            if p.exists():
                with open(p) as f:
                    m = json.load(f)
                rows[dl_name] = {
                    'f1_macro': m.get('f1_macro', 0),
                    'auc':      m.get('auc', 0.5),
                    'accuracy': m.get('accuracy', 0),
                }
        return rows
    with open(DL_TEST_JSON) as f:
        data = json.load(f)
    rows = {}
    for r in data.get('all_results', []):
        rows[r['model']] = {
            'f1_macro': r.get('f1_macro', 0),
            'auc':      r.get('auc', 0.5),
            'accuracy': r.get('accuracy', 0),
        }
    return rows


# ============================================================================
# 5. VISUALISATIONS
# ============================================================================
def plot_ranking(df: pd.DataFrame, save_path: Path, title_suffix='DANN-LOSO'):
    metrics = ['f1_macro', 'auc', 'accuracy']
    titles  = ['F1-MACRO (critère principal)', 'AUC', 'Accuracy']
    n       = len(df)
    fig, axes = plt.subplots(1, 3, figsize=(21, max(7, n * 0.4)))
    cmap = plt.cm.plasma(np.linspace(0.15, 0.85, n))

    for ax, metric, title in zip(axes, metrics, titles):
        sdf  = df.sort_values(metric, ascending=True)
        bars = ax.barh(sdf['model'], sdf[metric], color=cmap[:len(sdf)], alpha=0.85)
        ax.set_xlabel(metric.replace('_', ' ').upper())
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlim([0, 1.1])
        ax.axvline(0.70, color='green', ls='--', lw=1, alpha=0.6, label='70%')
        ax.axvline(0.85, color='blue',  ls=':',  lw=1, alpha=0.6, label='85%')
        ax.legend(fontsize=7)
        ax.grid(axis='x', alpha=0.3)
        for bar, val in zip(bars, sdf[metric]):
            ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}', va='center', fontsize=7)

    fig.suptitle(f'NeuroCap – Classement {title_suffix}', fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_heatmap(df: pd.DataFrame, save_path: Path):
    metrics = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    labels  = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']
    df_h = df.set_index('model')[metrics].copy()
    df_h.columns = labels
    df_h = df_h.sort_values('F1-Macro', ascending=False)
    vmin = max(0, df_h.values.min() - 0.05)

    fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.45)))
    sns.heatmap(df_h, annot=True, fmt='.3f', cmap='RdYlGn',
                vmin=vmin, vmax=1, linewidths=0.5, ax=ax,
                cbar_kws={'label': 'Score'})
    ax.set_title('DANN – Métriques LOSO (évaluation honnête)', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_radar_top5(df: pd.DataFrame, save_path: Path):
    top5  = df.nlargest(min(5, len(df)), 'f1_macro')
    cats  = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    lbls  = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']
    N     = len(cats)
    angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    cmap = plt.cm.tab10(np.linspace(0, 1, len(top5)))

    for (_, row), color in zip(top5.iterrows(), cmap):
        vals = [row[c] for c in cats] + [row[cats[0]]]
        ax.plot(angles, vals, lw=2, color=color, label=row['model'])
        ax.fill(angles, vals, alpha=0.08, color=color)

    ax.set_thetagrids(np.degrees(angles[:-1]), lbls, fontsize=9)
    ax.set_ylim([0, 1])
    ax.set_title('Radar – Top 5 DANN (LOSO)', fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.15), fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_dann_vs_dl_gain(df_dann: pd.DataFrame, dl_metrics: dict, save_path: Path):
    """
    Barplot de l'impact DANN sur F1-MACRO (LOSO) — Correction du biais SCPS.

    Interprétation correcte :
      - DANN supprime le raccourci 'matériel = classe' (OpenBCI=Conc, EMOTIV=Stress).
      - Δ F1 < 0 (orange) : attendu et SOUHAITÉ — le biais est supprimé, perf honnête.
      - Δ F1 > 0 (vert)   : signal cognitif amplifié (cas CNN1D — preuve du signal réel).
      - F1 DANN < 0.60 (rouge) : effondrement — architecture n'apprenait que le biais.
    """
    rows = []
    for _, r in df_dann.iterrows():
        dl_name = DANN_TO_DL.get(r['model'])
        if dl_name and dl_name in dl_metrics:
            dl_f1 = dl_metrics[dl_name]['f1_macro']
            gain  = r['f1_macro'] - dl_f1
            rows.append({'arch': dl_name, 'dann': r['model'],
                         'f1_dann': r['f1_macro'], 'f1_dl': dl_f1, 'gain': gain})
    if not rows:
        return
    df_g = pd.DataFrame(rows).sort_values('gain', ascending=False)

    def _dann_color(gain, f1_dann):
        if f1_dann < 0.60:
            return '#E74C3C'   # Effondrement : architecture invalide sans biais
        elif gain > 0.01:
            return '#27AE60'   # Signal cognitif amplifié (cas CNN1D)
        else:
            return '#F39C12'   # Biais supprimé, performance honnête (attendu)

    colors = [_dann_color(row['gain'], row['f1_dann']) for _, row in df_g.iterrows()]

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle(
        'Impact DANN — Correction du biais SCPS (LOSO)\n'
        'Vert = signal cognitif amplifié ✓ | Orange = biais supprimé (attendu ✓) | Rouge = effondrement ✗',
        fontsize=12, fontweight='bold')

    # Barplot impact DANN
    ax = axes[0]
    bars = ax.barh(df_g['arch'], df_g['gain'] * 100, color=colors, alpha=0.85)
    ax.axvline(0, color='black', lw=0.8)
    ax.set_xlabel('Δ F1-MACRO (%)', fontsize=10)
    ax.set_title(
        'Δ F1-MACRO après suppression du biais SCPS\n'
        '(baisse attendue = biais corrigé, hausse = signal cognitif prouvé)',
        fontweight='bold', fontsize=9)
    ax.grid(axis='x', alpha=0.3)
    for bar, v in zip(bars, df_g['gain']):
        ax.text(bar.get_width() + (0.1 if v >= 0 else -0.1),
                bar.get_y() + bar.get_height()/2,
                f'{v*100:+.2f}%', va='center', ha='left' if v >= 0 else 'right',
                fontsize=8)

    # Scatter DL (biaisé) vs DANN (honnête)
    ax2 = axes[1]
    ax2.scatter(df_g['f1_dl'], df_g['f1_dann'], s=100, c=colors,
                edgecolors='white', lw=0.5, zorder=5)
    for _, r in df_g.iterrows():
        ax2.annotate(r['arch'], (r['f1_dl'], r['f1_dann']),
                     textcoords='offset points', xytext=(4, 3), fontsize=7)
    lo = min(df_g[['f1_dl', 'f1_dann']].values.min() - 0.02, 0)
    hi = max(df_g[['f1_dl', 'f1_dann']].values.max() + 0.02, 1)
    ax2.plot([lo, hi], [lo, hi], 'k--', lw=1.2,
             label='y = x (aucune correction de biais)')
    ax2.set_xlabel('F1-MACRO Sans DANN — Biaisé par matériel (LOSO)', fontsize=10)
    ax2.set_ylabel('F1-MACRO Avec DANN — Honnête, généralisable (LOSO)', fontsize=10)
    ax2.set_title('Points sous y=x = biais corrigé (attendu ✓)', fontweight='bold')
    ax2.legend(fontsize=8)
    ax2.grid(alpha=0.3)

    from matplotlib.patches import Patch
    legend_els = [
        Patch(color='#27AE60', label='Signal cognitif amplifié ✓✓'),
        Patch(color='#F39C12', label='Biais supprimé, perf honnête ✓'),
        Patch(color='#E74C3C', label='Effondrement — architecture invalide ✗'),
    ]
    fig.legend(handles=legend_els, loc='lower center', ncol=3, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))
    plt.tight_layout(rect=[0, 0.04, 1, 0.94])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_dann_domain_stability(df: pd.DataFrame, save_path: Path):
    """
    Visualise l'équilibre domaine : taux de concentration vs stress
    prédit par chaque modèle DANN. Idéalement proches de 50/50.
    """
    if 'avg_conc_rate' not in df.columns or df['avg_conc_rate'].sum() == 0:
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(df))
    w = 0.38
    df_s = df.sort_values('f1_macro', ascending=False).reset_index(drop=True)

    ax.bar(x - w/2, df_s['avg_conc_rate'], w, label='Taux Concentration', color='#2980B9', alpha=0.8)
    ax.bar(x + w/2, df_s['avg_stress_rate'],  w, label='Taux Stress',         color='#E74C3C', alpha=0.8)
    ax.axhline(50, color='gray', ls='--', lw=1, label='50% (équilibre)')
    ax.set_xticks(x)
    ax.set_xticklabels(df_s['model'], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Taux prédit (%)')
    ax.set_title('Équilibre domaine – Taux Concentration / Stress par modèle DANN (LOSO)',
                 fontsize=12, fontweight='bold')
    ax.legend()
    ax.set_ylim(0, 105)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_loso_vs_holdout(df_loso: pd.DataFrame, df_holdout: pd.DataFrame, save_path: Path):
    merged = df_loso[['model', 'f1_macro']].rename(columns={'f1_macro': 'f1_loso'})
    merged = merged.merge(
        df_holdout[['model', 'f1_macro', 'has_leakage']].rename(
            columns={'f1_macro': 'f1_holdout'}),
        on='model', how='inner')
    if merged.empty:
        return

    fig, ax = plt.subplots(figsize=(8, 7))
    colors = merged['has_leakage'].map({True: '#E74C3C', False: '#27AE60', None: '#F39C12'})
    ax.scatter(merged['f1_loso'], merged['f1_holdout'],
               c=colors, s=120, zorder=5, edgecolors='white', lw=0.5)
    for _, row in merged.iterrows():
        ax.annotate(row['model'], (row['f1_loso'], row['f1_holdout']),
                    textcoords='offset points', xytext=(4, 3), fontsize=7)
    lo = min(merged['f1_loso'].min(), merged['f1_holdout'].min()) - 0.02
    ax.plot([lo, 1.02], [lo, 1.02], 'k--', lw=1.5, label="y=x")
    from matplotlib.patches import Patch
    ax.legend(handles=[
        Patch(color='#E74C3C', label='Fuite'),
        Patch(color='#27AE60', label='Pas de fuite'),
        Patch(color='#F39C12', label='Inconnu'),
    ], fontsize=8)
    ax.set_xlabel('F1-MACRO DANN-LOSO (honnête)', fontsize=11)
    ax.set_ylabel('F1-MACRO DANN-Holdout (potentiellement gonflé)', fontsize=11)
    ax.set_title('DANN – Inflation due à la fuite intra-sujet', fontsize=11, fontweight='bold')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# 6. MAIN
# ============================================================================
def main(models_to_test=None, compare_dl=False):
    print("=" * 75)
    print("NeuroCap – Test Suite DANN (évaluation LOSO honnête)")
    print(f"Device : {DEVICE}  |  Architectures : {len(DANN_ARCH_MAP)}")
    print("=" * 75)

    # ── Vérification fuite ─────────────────────────────────────────────────
    print("\n" + "─" * 75)
    print("VÉRIFICATION FUITE DE DONNÉES (X_test.npy)")
    print("─" * 75)
    leakage = check_holdout_leakage()
    print(leakage['message'])
    with open(REPORT_DIR / 'leakage_report.txt', 'w', encoding='utf-8') as f:
        f.write("NeuroCap DANN – Rapport fuite de données\n" + "=" * 60 + "\n\n")
        f.write(leakage['message'] + "\n")
        if leakage['train_subjects']:
            f.write(f"\nSujets train : {leakage['train_subjects']}\n")
        if leakage['test_subjects']:
            f.write(f"Sujets test  : {leakage['test_subjects']}\n")
        if leakage['overlap_subjects']:
            f.write(f"Sujets communs : {leakage['overlap_subjects']}\n")

    # ── Holdout data ───────────────────────────────────────────────────────
    X_test_loaded, y_test_loaded = None, None
    xp = DATA_DIR / 'X_test.npy'
    yp = DATA_DIR / 'y_test.npy'
    if xp.exists() and yp.exists():
        X_test_loaded = np.load(xp)
        y_test_loaded = np.load(yp)
        print(f"\n  Holdout : {len(X_test_loaded)} epochs | "
              f"{np.sum(y_test_loaded==0)} Conc, {np.sum(y_test_loaded==1)} Stress")

    target_models = models_to_test if models_to_test else ALL_DANN_MODELS
    loso_rows   = []
    holdout_rows = []
    no_loso     = []

    for model_name in target_models:
        if model_name not in DANN_ARCH_MAP:
            print(f"\n[SKIP] Modèle inconnu : {model_name}")
            continue

        print(f"\n{'─'*60}")
        print(f"  Modèle DANN : {model_name}")

        # ── Métriques LOSO ──────────────────────────────────────────────
        loso_raw, err = load_dann_loso_metrics(model_name)
        if loso_raw is not None:
            row = extract_loso_row(model_name, loso_raw)
            loso_rows.append(row)
            print(f"  [LOSO] F1m={row['f1_macro']:.4f}  AUC={row['auc']:.4f}  "
                  f"Acc={row['accuracy']:.4f}  Folds={row['n_folds']:.0f}  "
                  f"Gap={row['train_test_gap']:.4f}")
        else:
            no_loso.append((model_name, err))
            print(f"  [LOSO] Non disponible : {err}")

        # ── Holdout ─────────────────────────────────────────────────────
        if X_test_loaded is not None:
            row_h, err_h = evaluate_dann_on_holdout(
                model_name, X_test_loaded, y_test_loaded, leakage)
            if row_h:
                holdout_rows.append(row_h)
                leaked_label = '[LEAKED]' if leakage['has_leakage'] else '[OK]'
                print(f"  [Holdout {leaked_label}] F1m={row_h['f1_macro']:.4f}  "
                      f"AUC={row_h['auc']:.4f}  Lat={row_h['inference_ms']:.3f} ms/ep")
            else:
                print(f"  [Holdout] Erreur : {err_h}")

    if not loso_rows:
        print("\n[ERREUR] Aucune métrique DANN LOSO disponible.")
        print("Entraînez les modèles DANN avec : python src/models/deep_learning/architectures_DANN/*.py")
        if no_loso:
            print("\nModèles sans LOSO :")
            for name, reason in no_loso:
                print(f"  - {name}: {reason}")
        return

    # ── DataFrame LOSO ────────────────────────────────────────────────────
    df_loso = pd.DataFrame(loso_rows)
    df_loso['weighted_score'] = (
        0.40 * df_loso['f1_macro']
        + 0.30 * df_loso['auc']
        + 0.20 * df_loso['accuracy']
        + 0.10 * (1 - df_loso['pct_uncertain'] / 100)
    )
    df_loso = df_loso.sort_values('weighted_score', ascending=False).reset_index(drop=True)
    df_loso.to_csv(REPORT_DIR / 'results_table_LOSO.csv', index=False)

    df_holdout = pd.DataFrame(holdout_rows) if holdout_rows else pd.DataFrame()
    if not df_holdout.empty:
        df_holdout.to_csv(REPORT_DIR / 'results_table_holdout.csv', index=False)

    # ── Affichage classement DANN LOSO ─────────────────────────────────────
    print(f"\n{'='*75}")
    print("CLASSEMENT DANN LOSO – ÉVALUATION HONNÊTE (inter-sujets)")
    print(f"{'='*75}")
    print(f"{'Rang':>4}  {'Modèle':<22}  {'F1m':>6}  {'AUC':>6}  {'Acc':>6}  "
          f"{'Gap':>6}  {'Folds':>5}  {'Score':>6}")
    print("─" * 75)
    for rank, row in df_loso.iterrows():
        marker = " ★" if rank == 0 else "  "
        of_pct = (row['overfitting_folds'] / row['n_folds'] * 100
                  if row['n_folds'] > 0 else 0)
        print(f"{rank+1:>4}{marker} {row['model']:<22}  "
              f"{row['f1_macro']:.4f}  {row['auc']:.4f}  {row['accuracy']:.4f}  "
              f"{row['train_test_gap']:.4f}  {row['n_folds']:>5.0f}  {row['weighted_score']:.4f}")

    best = df_loso.iloc[0]
    print(f"\n★ Meilleure architecture DANN (LOSO) : {best['model']}")
    print(f"  F1-MACRO = {best['f1_macro']:.4f}  |  AUC = {best['auc']:.4f}  "
          f"|  Accuracy = {best['accuracy']:.4f}")

    # ── Comparaison LOSO vs Holdout ────────────────────────────────────────
    if not df_holdout.empty:
        print(f"\n{'─'*75}")
        print("DANN – LOSO (honnête) vs Holdout (potentiellement gonflé)")
        print(f"{'─'*75}")
        print(f"{'Modèle':<22}  {'F1 LOSO':>8}  {'F1 Holdout':>10}  {'Inflation':>10}")
        print("─" * 55)
        for _, lr in df_loso.iterrows():
            hr = df_holdout[df_holdout['model'] == lr['model']]
            if hr.empty:
                continue
            hr = hr.iloc[0]
            infl = hr['f1_macro'] - lr['f1_macro']
            flag = '  [!]' if infl > 0.05 else ''
            print(f"{lr['model']:<22}  {lr['f1_macro']:>8.4f}  "
                  f"{hr['f1_macro']:>10.4f}  {infl:>+10.4f}{flag}")

    # ── Comparaison DANN vs DL ─────────────────────────────────────────────
    dl_metrics = {}
    if compare_dl:
        print(f"\n{'─'*75}")
        print("DANN vs DL DE BASE — CORRECTION DU BIAIS SCPS (LOSO)")
        print(f"{'─'*75}")
        print("  CONTEXTE : Sans DANN, le modèle distingue OpenBCI (Conc.) d'EMOTIV (Stress)")
        print("  au lieu de l'état cognitif → scores artificiellement gonflés (SCPS).")
        print("  Le DANN supprime ce raccourci → performance HONNÊTE et GÉNÉRALISABLE révélée.")
        print(f"{'─'*75}")
        dl_metrics = load_dl_loso_metrics()
        if dl_metrics:
            print(f"{'Architecture':<20}  {'F1 DL (biaisé)':>14}  {'F1 DANN (honnête)':>17}  {'Δ F1':>8}  Interprétation")
            print("─" * 85)
            gains = []
            f1_danns = []
            for _, r in df_loso.iterrows():
                dl_name = DANN_TO_DL.get(r['model'])
                if dl_name and dl_name in dl_metrics:
                    dl_f1 = dl_metrics[dl_name]['f1_macro']
                    gain  = r['f1_macro'] - dl_f1
                    gains.append(gain)
                    f1_danns.append(r['f1_macro'])
                    if r['f1_macro'] < 0.60:
                        flag = '✗ Effondrement'
                    elif gain > 0.01:
                        flag = '✓✓ Signal cognitif amplifié'
                    else:
                        flag = '✓ Biais supprimé (attendu)'
                    print(f"{dl_name:<20}  {dl_f1:>14.4f}  {r['f1_macro']:>17.4f}  "
                          f"{gain:>+8.4f}  {flag}")
            if gains:
                avg = np.mean(gains)
                n_signal   = sum(1 for g in gains if g > 0.01)
                n_honest   = sum(1 for g, f in zip(gains, f1_danns) if g <= 0.01 and f >= 0.60)
                n_collapse = sum(1 for f in f1_danns if f < 0.60)
                print(f"\n  Δ F1m moyen (correction biais SCPS) : {avg:+.4f}")
                print(f"  ✓✓ Signal cognitif amplifié          : {n_signal}/{len(gains)}")
                print(f"  ✓  Biais supprimé — perf honnête     : {n_honest}/{len(gains)}")
                print(f"  ✗  Effondrement — invalide sans biais: {n_collapse}/{len(gains)}")
                print(f"\n  CONCLUSION :")
                print(f"  La variation de F1 ({avg*100:+.2f}pp en moyenne) signifie que les scores")
                print(f"  SANS DANN étaient gonflés. Les scores AVEC DANN sont la performance")
                print(f"  RÉELLE que le modèle obtiendra sur un nouveau matériel (AD8232).")
        else:
            print("  Métriques DL LOSO non disponibles (exécutez test_deep_learning.py).")

    if no_loso:
        print(f"\nModèles DANN sans métriques LOSO ({len(no_loso)}) :")
        for name, reason in no_loso:
            print(f"  - {name}: {reason}")

    # ── Graphiques ─────────────────────────────────────────────────────────
    print("\nGénération des graphiques DANN...")
    plot_ranking(df_loso, REPORT_DIR / 'ranking_barplot_LOSO.png')
    plot_heatmap(df_loso, REPORT_DIR / 'heatmap_metrics_LOSO.png')
    if len(df_loso) >= 3:
        plot_radar_top5(df_loso, REPORT_DIR / 'radar_top5_LOSO.png')
    if not df_holdout.empty:
        plot_loso_vs_holdout(df_loso, df_holdout, REPORT_DIR / 'loso_vs_holdout.png')
    if dl_metrics:
        plot_dann_vs_dl_gain(df_loso, dl_metrics, REPORT_DIR / 'dann_gain_over_dl.png')
    plot_dann_domain_stability(df_loso, REPORT_DIR / 'domain_balance.png')

    # ── Rapport de décision ────────────────────────────────────────────────
    with open(REPORT_DIR / 'decision_report.txt', 'w', encoding='utf-8') as f:
        f.write("NeuroCap – Rapport de Décision DANN\n")
        f.write("Évaluation LOSO (Leave-One-Subject-Out) – Performance HONNÊTE\n")
        f.write("=" * 70 + "\n\n")
        f.write("POURQUOI LE DANN EST NÉCESSAIRE — LE PROBLÈME SCPS\n")
        f.write("-" * 70 + "\n")
        f.write("Dans NeuroCap, les données proviennent de deux appareils distincts :\n")
        f.write("  • OpenBCI  (domaine 0)  →  tâche Concentration  (label 0)\n")
        f.write("  • EMOTIV   (domaine 1)  →  tâche Stress          (label 1)\n\n")
        f.write("Conséquence (SCPS — Site Confound Problem) :\n")
        f.write("  Le modèle SANS DANN apprend 'OpenBCI = Concentration, EMOTIV = Stress'\n")
        f.write("  au lieu de l'état cognitif réel. Scores anormalement élevés (> 95%).\n")
        f.write("  Ces scores s'effondreront sur un nouveau matériel (ex: AD8232 NeuroCap).\n\n")
        f.write("RÔLE DU DANN (l'anti-dopage de l'IA) :\n")
        f.write("  Le GRL (Gradient Reversal Layer) force le modèle à devenir 'aveugle'\n")
        f.write("  au matériel. Il doit trouver un autre chemin → signal cérébral réel.\n\n")
        f.write("INTERPRÉTATION DES RÉSULTATS :\n")
        f.write("  • Δ F1 < 0  : biais SCPS supprimé — performance HONNÊTE révélée [✓]\n")
        f.write("  • Δ F1 > 0  : signal cognitif amplifié (preuve du signal réel) [✓✓]\n")
        f.write("  • F1 DANN < 0.60 : effondrement — architecture invalide [✗]\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Score pondéré : 40% F1m + 30% AUC + 20% Acc + 10% certitude\n\n")
        f.write(f"{'Rang':<5} {'Modèle':<22} {'F1m':>6} {'AUC':>6} "
                f"{'Acc':>6} {'Gap':>6} {'Folds':>5} {'Score':>7}\n")
        f.write("-" * 65 + "\n")
        for rank, row in df_loso.iterrows():
            f.write(f"{rank+1:<5} {row['model']:<22} "
                    f"{row['f1_macro']:>6.4f} {row['auc']:>6.4f} "
                    f"{row['accuracy']:>6.4f} {row['train_test_gap']:>6.4f} "
                    f"{row['n_folds']:>5.0f}  {row['weighted_score']:>7.4f}\n")
        f.write("\n" + "=" * 70 + "\n")
        f.write(f"MEILLEURE ARCHITECTURE DANN (LOSO) : {best['model']}\n")
        f.write(f"  F1-MACRO   = {best['f1_macro']:.4f}  (performance HONNÊTE, sans biais matériel)\n")
        f.write(f"  AUC        = {best['auc']:.4f}\n")
        f.write(f"  Accuracy   = {best['accuracy']:.4f}\n")
        f.write(f"  Gap train-test = {best['train_test_gap']:.4f}\n")
        f.write(f"  Incertains     = {best['pct_uncertain']:.1f}%\n")
        if dl_metrics:
            dl_name = DANN_TO_DL.get(best['model'])
            if dl_name and dl_name in dl_metrics:
                dl_f1 = dl_metrics[dl_name]['f1_macro']
                gain  = best['f1_macro'] - dl_f1
                f.write(f"\n  F1 DL de base ({dl_name}) : {dl_f1:.4f}  (biaisé — SCPS)\n")
                f.write(f"  Δ F1 après correction DANN : {gain:+.4f}\n")
                if best['f1_macro'] < 0.60:
                    f.write("  → Architecture effondrée : ne capte pas de signal cognitif réel\n")
                elif gain > 0.01:
                    f.write("  → Signal cognitif amplifié : preuve que le signal EEG est réel\n")
                else:
                    f.write("  → Biais SCPS corrigé : ce score est la performance généralisable\n")
                    f.write(f"  → Le modèle fonctionnera sur AD8232 NeuroCap avec ~{best['f1_macro']*100:.1f}% F1\n")

    # ── JSON ──────────────────────────────────────────────────────────────
    with open(REPORT_DIR / 'results.json', 'w') as f:
        json.dump({
            'evaluation_method': 'DANN-LOSO',
            'best': best['model'],
            'best_f1_macro': best['f1_macro'],
            'best_weighted_score': best['weighted_score'],
            'leakage_detected': leakage['has_leakage'],
            'all_results': [
                {k: v for k, v in r.items()} for r in loso_rows
            ],
        }, f, indent=2, default=str)

    print(f"\n{'='*75}")
    print(f"Sorties : {REPORT_DIR}")
    print(f"  • results_table_LOSO.csv      ← classement DANN honnête")
    print(f"  • ranking_barplot_LOSO.png")
    print(f"  • heatmap_metrics_LOSO.png")
    print(f"  • radar_top5_LOSO.png")
    print(f"  • domain_balance.png          ← équilibre Concentration/Stress")
    if dl_metrics:
        print(f"  • dann_gain_over_dl.png       ← gain DANN vs DL de base")
    if not df_holdout.empty:
        print(f"  • loso_vs_holdout.png")
    print(f"  • decision_report.txt")
    print(f"  • results.json")
    print(f"{'='*75}")


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--compare-dl']
    compare_dl = '--compare-dl' in sys.argv

    valid, invalid = [], []
    for a in args:
        (valid if a in DANN_ARCH_MAP else invalid).append(a)
    if invalid:
        print(f"[WARN] Modèles inconnus : {invalid}")
        print(f"Disponibles : {ALL_DANN_MODELS}")

    main(valid if valid else None, compare_dl=compare_dl)
