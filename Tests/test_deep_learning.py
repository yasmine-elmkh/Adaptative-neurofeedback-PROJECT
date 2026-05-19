"""
NeuroCap – Test Suite Deep Learning (19 architectures)
=======================================================
Évalue chaque architecture DL avec DEUX sources de métriques :

  1. LOSO (Leave-One-Subject-Out) — ÉVALUATION HONNÊTE
     Lit les metrics.json LOSO sauvegardés pendant l'entraînement.
     Garantit qu'aucun sujet n'est partagé entre train et test.
     → Métriques à utiliser pour la décision finale.

  2. Holdout X_test.npy — ÉVALUATION BRUTE (pour information seulement)
     Détecte si les sujets du test se retrouvent dans le train.
     Si fuite détectée → scores marqués [LEAKED] et NON utilisés
     pour le classement.

Pourquoi les scores parfaits (F1=1.00) sont suspects ?
  Le fichier X_test.npy est généralement créé par split ALÉATOIRE
  d'époques, sans respecter les frontières de sujets. Des époques
  du même sujet se retrouvent en train ET en test. Le modèle a alors
  appris les patterns EEG propres à chaque sujet (signature personnelle),
  rendant la classification triviale. Ce n'est PAS une vraie performance.

Usage :
    cd EEG_project
    python Tests/test_deep_learning.py          # tous les modèles
    python Tests/test_deep_learning.py CNN1D    # un seul modèle

Sorties :
    reports/Tests/deep_learning/
        ├── results_table_LOSO.csv       ← classement honnête
        ├── results_table_holdout.csv    ← pour information
        ├── ranking_barplot_LOSO.png
        ├── heatmap_metrics_LOSO.png
        ├── radar_top5_LOSO.png
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
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCH_DIR     = PROJECT_ROOT / 'src' / 'models' / 'deep_learning' / 'architectures'
DL_UTILS_DIR = PROJECT_ROOT / 'src' / 'models' / 'deep_learning'
DATA_DIR     = PROJECT_ROOT / 'data' / 'Augmentation' / 'datasets_augmented'
MODEL_BASE   = PROJECT_ROOT / 'models' / 'deep_learning' / 'DL_models'
DL_OUTPUTS   = PROJECT_ROOT / 'reports' / 'deep_learning' / 'DL_outputs'
REPORT_DIR   = PROJECT_ROOT / 'reports' / 'Tests' / 'deep_learning'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
EXP_PRIORITY = ['FULL', 'D', 'C', 'B', 'A']

# ============================================================================
# MAPPING architecture
# ============================================================================
ARCH_MAP = {
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
ALL_MODELS = list(ARCH_MAP.keys())


# ============================================================================
# 1. VÉRIFICATION FUITE DE DONNÉES
# ============================================================================
def check_holdout_leakage():
    """
    Vérifie si les sujets du fichier X_test.npy se retrouvent
    aussi dans X_train_{exp}.npy.
    Retourne un dict avec has_leakage, overlap_subjects, message.
    """
    result = {
        'has_leakage': None,
        'overlap_subjects': [],
        'train_subjects': [],
        'test_subjects': [],
        'message': '',
        'sid_test_found': False,
    }

    # Cherche subject_ids_test.npy
    test_sid_path = DATA_DIR / 'subject_ids_test.npy'
    if not test_sid_path.exists():
        result['message'] = (
            "subject_ids_test.npy introuvable → "
            "impossible de vérifier la fuite automatiquement.\n"
            "Les scores parfaits (F1≈1.0) sont très suspects en EEG et\n"
            "indiquent probablement un split d'époques sans séparation par sujet."
        )
        result['has_leakage'] = None
        return result

    result['sid_test_found'] = True
    sids_test = set(np.load(test_sid_path).flatten())
    result['test_subjects'] = sorted(sids_test)

    # Cherche au moins un fichier subject_ids_train
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
            f"FUITE INTRA-SUJET DÉTECTÉE !\n"
            f"  {len(overlap)} sujet(s) partagé(s) entre train et test : {sorted(overlap)}\n"
            f"  Les scores sur X_test.npy sont INVALIDES pour évaluer la généralisation."
        )
    else:
        result['message'] = (
            f"Pas de fuite détectée (sujets train/test disjoints).\n"
            f"  {len(sids_test)} sujets de test, {len(train_sids)} sujets d'entraînement."
        )
    return result


# ============================================================================
# 2. LECTURE DES MÉTRIQUES LOSO (sauvegardées pendant l'entraînement)
# ============================================================================
def load_loso_metrics(model_name: str):
    """
    Lit le fichier LOSO_exp_A/metrics.json sauvegardé pendant l'entraînement.
    C'est l'évaluation HONNÊTE (aucun sujet partagé train/test).
    Retourne (dict métriques, None) ou (None, message d'erreur).
    """
    loso_path = DL_OUTPUTS / model_name / 'LOSO_exp_A' / 'metrics.json'
    if not loso_path.exists():
        return None, f"LOSO_exp_A/metrics.json introuvable pour {model_name}"
    with open(loso_path) as f:
        m = json.load(f)
    return m, None


def extract_loso_row(model_name: str, raw: dict):
    """Extrait les colonnes pertinentes du dict LOSO brut."""
    return {
        'model':          model_name,
        'eval_type':      'LOSO (honnête)',
        'exp_used':       raw.get('exp', 'A'),
        'accuracy':       raw.get('accuracy', 0),
        'f1_macro':       raw.get('f1_macro',  0),
        'f1_binary':      raw.get('f1', 0),
        'precision':      raw.get('precision', 0),
        'recall':         raw.get('recall', 0),
        'specificity':    raw.get('specificity', 0),
        'auc':            raw.get('auc', 0.5),
        'pct_uncertain':  raw.get('pct_uncertain', 0),
        'n_folds':        raw.get('n_folds', 0),
        'overfitting_folds': raw.get('overfitting_folds', 0),
        'train_time_sec': raw.get('train_time_sec', 0),
        'inference_ms':   0,
        'avg_conc_rate':  raw.get('rates', {}).get('avg_concentration_rate', 0),
        'avg_stress_rate':raw.get('rates', {}).get('avg_stress_rate', 0),
        'source':         'loso_saved',
    }


# ============================================================================
# 3. ÉVALUATION SUR HOLDOUT (X_test.npy) — pour information seulement
# ============================================================================
_arch_cache = {}

def import_arch_class(model_name: str):
    if model_name in _arch_cache:
        return _arch_cache[model_name]
    file_stem, class_name = ARCH_MAP[model_name]
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
    _arch_cache[model_name] = cls
    return cls


def find_best_model_pt(model_name: str):
    model_dir = MODEL_BASE / model_name
    for exp in EXP_PRIORITY:
        pt = model_dir / f'{model_name}_{exp}_best.pt'
        if pt.exists():
            return pt, exp
    return None, None


def evaluate_on_holdout(model_name: str, X_test: np.ndarray, y_test: np.ndarray,
                        leakage_info: dict):
    """
    Charge le .pt et évalue sur X_test.npy.
    Retourne (row_dict, error_str).
    """
    pt_path, exp_used = find_best_model_pt(model_name)
    if pt_path is None:
        return None, "aucun .pt trouvé"

    try:
        ModelClass = import_arch_class(model_name)
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
            out   = model(batch)
            probs = torch.softmax(out, 1).cpu().numpy()
            preds = out.argmax(1).cpu().numpy()
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
    label  = 'Holdout [LEAKED]' if leaked else 'Holdout [OK]' if leaked is False else 'Holdout [?]'

    row = {
        'model':         model_name,
        'eval_type':     label,
        'exp_used':      exp_used,
        'accuracy':      accuracy_score(y_test, preds),
        'f1_macro':      f1_score(y_test, preds, average='macro', zero_division=0),
        'f1_binary':     f1_score(y_test, preds, zero_division=0),
        'precision':     precision_score(y_test, preds, zero_division=0),
        'recall':        recall_score(y_test, preds, zero_division=0),
        'specificity':   spec,
        'auc':           auc_val,
        'pct_uncertain': float(np.sum(np.max(probs, 1) < 0.60) / len(y_test) * 100),
        'n_folds':       0,
        'overfitting_folds': 0,
        'train_time_sec':0,
        'inference_ms':  elapsed * 1000 / len(y_test),
        'avg_conc_rate': float(np.mean(probs[:, 0]) * 100),
        'avg_stress_rate':float(np.mean(probs[:, 1]) * 100),
        'source':        'holdout',
        'has_leakage':   leaked,
        'n_samples':     len(y_test),
    }
    return row, None


# ============================================================================
# 4. VISUALISATIONS
# ============================================================================
def plot_loso_ranking(df: pd.DataFrame, save_path: Path):
    """Barplot horizontal du classement LOSO (honnête)."""
    metrics = ['f1_macro', 'auc', 'accuracy']
    titles  = ['F1-MACRO (critère principal)', 'AUC', 'Accuracy']
    fig, axes = plt.subplots(1, 3, figsize=(20, max(7, len(df) * 0.4)))
    cmap = plt.cm.tab20(np.linspace(0, 1, len(df)))

    for ax, metric, title in zip(axes, metrics, titles):
        sorted_df = df.sort_values(metric, ascending=True)
        bars = ax.barh(sorted_df['model'], sorted_df[metric],
                       color=cmap[:len(sorted_df)], alpha=0.85)
        ax.set_xlabel(metric.replace('_', ' ').upper())
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlim([0, 1.1])
        ax.axvline(0.70, color='green', ls='--', lw=1, alpha=0.6, label='70%')
        ax.axvline(0.85, color='blue',  ls=':',  lw=1, alpha=0.6, label='85%')
        ax.legend(fontsize=7)
        ax.grid(axis='x', alpha=0.3)
        for bar, val in zip(bars, sorted_df[metric]):
            ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}', va='center', fontsize=7)

    fig.suptitle('NeuroCap – Classement DL (LOSO – évaluation honnête)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_loso_heatmap(df: pd.DataFrame, save_path: Path):
    metrics = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    labels  = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']
    df_heat = df.set_index('model')[metrics].copy()
    df_heat.columns = labels
    df_heat = df_heat.sort_values('F1-Macro', ascending=False)
    vmin = max(0, df_heat.values.min() - 0.05)

    fig, ax = plt.subplots(figsize=(10, max(6, len(df) * 0.45)))
    sns.heatmap(df_heat, annot=True, fmt='.3f', cmap='RdYlGn',
                vmin=vmin, vmax=1, linewidths=0.5, ax=ax,
                cbar_kws={'label': 'Score'})
    ax.set_title('Heatmap DL – Métriques LOSO (évaluation honnête)',
                 fontsize=12, fontweight='bold')
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
    ax.set_title('Radar – Top 5 DL (LOSO)', fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.15), fontsize=9)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_loso_vs_holdout(df_loso: pd.DataFrame, df_holdout: pd.DataFrame, save_path: Path):
    """
    Scatter : F1-MACRO LOSO (axe X) vs F1-MACRO Holdout (axe Y).
    Permet de visualiser l'inflation due à la fuite de données.
    La diagonale y=x = pas d'inflation.
    """
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

    lim_min = min(merged['f1_loso'].min(), merged['f1_holdout'].min()) - 0.02
    lim_max = 1.02
    ax.plot([lim_min, lim_max], [lim_min, lim_max], 'k--', lw=1.5,
            label='y=x (pas d\'inflation)')

    from matplotlib.patches import Patch
    handles = [
        Patch(color='#E74C3C', label='Fuite détectée (scores gonflés)'),
        Patch(color='#27AE60', label='Pas de fuite'),
        Patch(color='#F39C12', label='Inconnu'),
    ]
    ax.legend(handles=handles, fontsize=8)
    ax.set_xlabel('F1-MACRO LOSO (honnête)', fontsize=11)
    ax.set_ylabel('F1-MACRO Holdout (potentiellement gonflé)', fontsize=11)
    ax.set_title('Inflation des scores due à la fuite intra-sujet\n'
                 'Points au-dessus de y=x = scores artificiellement hauts',
                 fontsize=11, fontweight='bold')
    ax.grid(alpha=0.3)
    ax.set_xlim([lim_min, lim_max])
    ax.set_ylim([lim_min, lim_max])
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# 5. MAIN
# ============================================================================
def main(models_to_test=None):
    print("=" * 75)
    print("NeuroCap – Test Suite Deep Learning (évaluation honnête LOSO)")
    print(f"Device : {DEVICE}")
    print("=" * 75)

    # ─── Vérification fuite dans X_test.npy ──────────────────────────────────
    print("\n" + "─" * 75)
    print("VÉRIFICATION FUITE DE DONNÉES (X_test.npy)")
    print("─" * 75)
    leakage = check_holdout_leakage()
    print(leakage['message'])
    if leakage['has_leakage']:
        print("\n  CONSÉQUENCE : Les scores sur X_test.npy sont INVALIDES")
        print("  pour mesurer la généralisation inter-sujets.")
        print("  → Le classement utilisera UNIQUEMENT les métriques LOSO.")
    elif leakage['has_leakage'] is None:
        print("\n  ATTENTION : Sans subject_ids, on ne peut pas garantir")
        print("  l'absence de fuite. Scores parfaits (F1≈1.0) = suspect.")

    # Sauvegarde rapport fuite
    with open(REPORT_DIR / 'leakage_report.txt', 'w', encoding='utf-8') as f:
        f.write("NeuroCap – Rapport de vérification fuite de données\n")
        f.write("=" * 60 + "\n\n")
        f.write(leakage['message'] + "\n\n")
        if leakage['train_subjects']:
            f.write(f"Sujets train : {leakage['train_subjects']}\n")
        if leakage['test_subjects']:
            f.write(f"Sujets test  : {leakage['test_subjects']}\n")
        if leakage['overlap_subjects']:
            f.write(f"Sujets en commun : {leakage['overlap_subjects']}\n")
        f.write("\nExplication :\n")
        f.write("  Le fichier X_test.npy est souvent créé par split ALÉATOIRE\n")
        f.write("  des époques. Si le même sujet a des époques en train ET en test,\n")
        f.write("  le modèle a vu sa 'signature EEG personnelle' à l'entraînement.\n")
        f.write("  La classification devient triviale → F1 artificiellement parfait.\n")
        f.write("  La vraie métrique de généralisation = LOSO (Leave-One-Subject-Out).\n")

    # ─── Chargement des données holdout (pour info) ───────────────────────────
    X_test_loaded, y_test_loaded = None, None
    xp, yp = DATA_DIR / 'X_test.npy', DATA_DIR / 'y_test.npy'
    if xp.exists() and yp.exists():
        X_test_loaded = np.load(xp)
        y_test_loaded = np.load(yp)
        print(f"\n  Holdout : {len(X_test_loaded)} epochs "
              f"| {np.sum(y_test_loaded==0)} Conc, {np.sum(y_test_loaded==1)} Stress")

    target_models = models_to_test if models_to_test else ALL_MODELS
    loso_rows   = []
    holdout_rows = []
    no_loso     = []

    for model_name in target_models:
        if model_name not in ARCH_MAP:
            print(f"\n[SKIP] Modèle inconnu : {model_name}")
            continue

        print(f"\n{'─'*60}")
        print(f"  Modèle : {model_name}")

        # ── 1. Métriques LOSO (honnêtes) ──────────────────────────────────
        loso_raw, err_loso = load_loso_metrics(model_name)
        if loso_raw is not None:
            row_loso = extract_loso_row(model_name, loso_raw)
            loso_rows.append(row_loso)
            print(f"  [LOSO] F1-MACRO={row_loso['f1_macro']:.4f}  "
                  f"AUC={row_loso['auc']:.4f}  "
                  f"Acc={row_loso['accuracy']:.4f}  "
                  f"Folds={row_loso['n_folds']}")
        else:
            no_loso.append((model_name, err_loso))
            print(f"  [LOSO] Non disponible : {err_loso}")

        # ── 2. Évaluation holdout (pour comparer, marquer si leaked) ──────
        if X_test_loaded is not None:
            row_holdout, err_h = evaluate_on_holdout(
                model_name, X_test_loaded, y_test_loaded, leakage)
            if row_holdout:
                holdout_rows.append(row_holdout)
                leaked_label = '[LEAKED]' if leakage['has_leakage'] else \
                               '[OK]'     if leakage['has_leakage'] is False else '[?]'
                print(f"  [Holdout {leaked_label}] F1-MACRO={row_holdout['f1_macro']:.4f}  "
                      f"AUC={row_holdout['auc']:.4f}  "
                      f"Lat={row_holdout['inference_ms']:.3f} ms/ep")
                if leakage['has_leakage'] and row_holdout['f1_macro'] > 0.95:
                    inflation = row_holdout['f1_macro'] - (row_loso['f1_macro'] if loso_raw else 0)
                    print(f"  [!] Score gonflé : inflation estimée = +{inflation:.4f} "
                          f"(à cause de la fuite)")
            else:
                print(f"  [Holdout] Erreur : {err_h}")

    # ─── Résultats LOSO ───────────────────────────────────────────────────────
    if not loso_rows:
        print("\n" + "=" * 75)
        print("[ERREUR] Aucune métrique LOSO disponible.")
        print("Assurez-vous d'avoir entraîné les modèles avec DL_utils.py")
        print("(la fonction run_loso_validation génère LOSO_exp_A/metrics.json)")
        if no_loso:
            print("\nModèles sans LOSO :")
            for name, reason in no_loso:
                print(f"  - {name}: {reason}")
        return

    # ─── DataFrame LOSO & score pondéré ──────────────────────────────────────
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

    # ─── Affichage classement LOSO ───────────────────────────────────────────
    print(f"\n{'='*75}")
    print("CLASSEMENT LOSO – ÉVALUATION HONNÊTE (inter-sujets)")
    print("NB : ces métriques reflètent la vraie généralisation")
    print(f"{'='*75}")
    print(f"{'Rang':>4}  {'Modèle':<18}  "
          f"{'F1m':>6}  {'AUC':>6}  {'Acc':>6}  "
          f"{'Folds':>5}  {'OF%':>5}  {'Score':>6}")
    print("-" * 75)
    for rank, row in df_loso.iterrows():
        marker = " ★" if rank == 0 else "  "
        of_pct = (row['overfitting_folds'] / row['n_folds'] * 100
                  if row['n_folds'] > 0 else 0)
        print(f"{rank+1:>4}{marker} {row['model']:<18}  "
              f"{row['f1_macro']:.4f}  {row['auc']:.4f}  {row['accuracy']:.4f}  "
              f"{row['n_folds']:>5.0f}  {of_pct:>4.0f}%  {row['weighted_score']:.4f}")

    best = df_loso.iloc[0]
    print(f"\n★ Meilleure architecture DL (LOSO) : {best['model']}")
    print(f"  F1-MACRO = {best['f1_macro']:.4f}  |  AUC = {best['auc']:.4f}  "
          f"|  Accuracy = {best['accuracy']:.4f}")
    print(f"  Folds avec overfitting : {int(best['overfitting_folds'])}/{int(best['n_folds'])}")

    # ─── Comparaison LOSO vs Holdout (si disponible) ─────────────────────────
    if not df_holdout.empty and not df_loso.empty:
        print(f"\n{'─'*75}")
        print("COMPARAISON LOSO (honnête) vs Holdout (potentiellement gonflé)")
        print(f"{'─'*75}")
        print(f"{'Modèle':<20}  {'F1 LOSO':>8}  {'F1 Holdout':>10}  "
              f"{'Inflation':>10}  {'Fuite?':>7}")
        print("-" * 60)
        for _, lr in df_loso.iterrows():
            hrow = df_holdout[df_holdout['model'] == lr['model']]
            if hrow.empty:
                continue
            hr    = hrow.iloc[0]
            infl  = hr['f1_macro'] - lr['f1_macro']
            leak  = '  OUI' if hr.get('has_leakage') else ' NON' if hr.get('has_leakage') is False else '  ???'
            flag  = '  [!]' if infl > 0.05 else ''
            print(f"{lr['model']:<20}  {lr['f1_macro']:>8.4f}  {hr['f1_macro']:>10.4f}  "
                  f"{infl:>+10.4f}  {leak}{flag}")

    if no_loso:
        print(f"\nModèles sans métriques LOSO ({len(no_loso)}) :")
        for name, reason in no_loso:
            print(f"  - {name}: {reason}")

    # ─── Graphiques ──────────────────────────────────────────────────────────
    print("\nGénération des graphiques LOSO...")
    plot_loso_ranking(df_loso,  REPORT_DIR / 'ranking_barplot_LOSO.png')
    plot_loso_heatmap(df_loso,  REPORT_DIR / 'heatmap_metrics_LOSO.png')
    if len(df_loso) >= 3:
        plot_radar_top5(df_loso, REPORT_DIR / 'radar_top5_LOSO.png')
    if not df_holdout.empty:
        plot_loso_vs_holdout(df_loso, df_holdout, REPORT_DIR / 'loso_vs_holdout.png')

    # ─── Rapport de décision ─────────────────────────────────────────────────
    report_path = REPORT_DIR / 'decision_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("NeuroCap – Rapport de Décision Deep Learning\n")
        f.write("Évaluation LOSO (Leave-One-Subject-Out) – Honnête\n")
        f.write("=" * 65 + "\n\n")
        f.write("IMPORTANT : Ce rapport utilise les métriques LOSO, pas X_test.npy.\n")
        f.write("Le fichier X_test.npy peut avoir une fuite intra-sujet (voir leakage_report.txt).\n")
        f.write("En LOSO, chaque sujet est testé sur un modèle entraîné SANS lui.\n\n")
        f.write(f"Critère : F1-MACRO  "
                f"| Score = 40%F1m + 30%AUC + 20%Acc + 10%certitude\n\n")
        f.write(f"{'Rang':<5} {'Modèle':<18} {'F1m':>6} {'AUC':>6} "
                f"{'Acc':>6} {'Folds':>5} {'OF%':>5} {'Score':>7}\n")
        f.write("-" * 65 + "\n")
        for rank, row in df_loso.iterrows():
            of_pct = (row['overfitting_folds'] / row['n_folds'] * 100
                      if row['n_folds'] > 0 else 0)
            f.write(f"{rank+1:<5} {row['model']:<18} "
                    f"{row['f1_macro']:>6.4f} {row['auc']:>6.4f} "
                    f"{row['accuracy']:>6.4f} {row['n_folds']:>5.0f} "
                    f"{of_pct:>4.0f}%  {row['weighted_score']:>7.4f}\n")
        f.write("\n" + "=" * 65 + "\n")
        f.write(f"RECOMMANDATION DL (LOSO) : {best['model']}\n")
        f.write(f"  F1-MACRO  = {best['f1_macro']:.4f}\n")
        f.write(f"  AUC       = {best['auc']:.4f}\n")
        f.write(f"  Accuracy  = {best['accuracy']:.4f}\n")
        f.write(f"  Incertains = {best['pct_uncertain']:.1f}%\n")
        of_pct_best = (best['overfitting_folds'] / best['n_folds'] * 100
                       if best['n_folds'] > 0 else 0)
        f.write(f"  Folds avec overfitting : {int(best['overfitting_folds'])}"
                f"/{int(best['n_folds'])} ({of_pct_best:.0f}%)\n")

    # ─── Sauvegarde JSON ──────────────────────────────────────────────────────
    loso_save = [{k: v for k, v in r.items()} for r in loso_rows]
    with open(REPORT_DIR / 'results.json', 'w') as f:
        json.dump({
            'evaluation_method': 'LOSO',
            'best': best['model'],
            'best_f1_macro': best['f1_macro'],
            'best_weighted_score': best['weighted_score'],
            'leakage_detected': leakage['has_leakage'],
            'leakage_message': leakage['message'],
            'all_results': loso_save,
        }, f, indent=2, default=str)

    print(f"\n{'='*75}")
    print(f"Sorties : {REPORT_DIR}")
    print(f"  • results_table_LOSO.csv      ← classement principal (honnête)")
    print(f"  • results_table_holdout.csv   ← pour info seulement")
    print(f"  • ranking_barplot_LOSO.png")
    print(f"  • heatmap_metrics_LOSO.png")
    print(f"  • radar_top5_LOSO.png")
    print(f"  • loso_vs_holdout.png         ← visualise l'inflation des scores")
    print(f"  • leakage_report.txt          ← explication fuite de données")
    print(f"  • decision_report.txt")
    print(f"  • results.json")
    print(f"{'='*75}")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        requested = sys.argv[1:]
        valid   = [m for m in requested if m in ARCH_MAP]
        invalid = [m for m in requested if m not in ARCH_MAP]
        if invalid:
            print(f"[WARN] Modèles inconnus : {invalid}")
            print(f"Disponibles : {ALL_MODELS}")
        main(valid if valid else None)
    else:
        main()
