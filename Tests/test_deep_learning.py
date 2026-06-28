"""
NeuroCap – Test Suite Deep Learning Régression (19 architectures)
==================================================================
Évalue chaque architecture DL sur DEUX sources :

  1. Métriques sauvegardées (metrics.json) — lues depuis reports/Regression/DL/
     • Expériences A/B/C/D/FULL  → métriques sur X_test (holdout par sujet)
     • LOSO                      → métriques LOSO par target

  2. Évaluation directe sur X_test.npy (holdout)
     • Charge le meilleur .pt   → models/Regression/DL/{model}/{target}/
     • Prédit scores continus   → MAE, RMSE, R², AUC-ROC, F1-macro
     • AUCUN softmax — sortie scalaire (régression)

Deux targets évalués séparément : conc et stress.

Usage :
    python Tests/test_deep_learning.py            # tous les modèles
    python Tests/test_deep_learning.py CNN1D      # un seul modèle
    python Tests/test_deep_learning.py CNN1D conc # modèle + target

Sorties :
    reports/Tests/deep_learning/
        ├── results_conc.csv / results_stress.csv
        ├── ranking_conc.png / ranking_stress.png
        ├── heatmap_conc.png / heatmap_stress.png
        ├── loso_summary.csv
        └── decision_report.txt
"""

import sys
import json
import time
import importlib.util
import warnings
from pathlib import Path

import numpy as np
import torch
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.metrics import roc_auc_score, f1_score

warnings.filterwarnings('ignore')

# ─── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARCH_DIR     = PROJECT_ROOT / 'src' / 'models' / 'deep_learning' / 'architectures'
DL_UTILS_DIR = PROJECT_ROOT / 'src' / 'models' / 'deep_learning'
DATA_DIR     = PROJECT_ROOT / 'data' / 'Regression' / 'augmented'
DL_OUTPUTS   = PROJECT_ROOT / 'reports' / 'Regression' / 'DL'
MODEL_BASE   = PROJECT_ROOT / 'models' / 'Regression' / 'DL'
REPORT_DIR   = PROJECT_ROOT / 'reports' / 'Tests' / 'deep_learning'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

TARGETS     = ['conc', 'stress']
EXPERIMENTS = ['A', 'B', 'C', 'D', 'FULL']
SCORE_THR   = 5.0

# ─── Mapping fichier → classe ──────────────────────────────────────────────
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
    'LSTM_Att':     ('LSTM_ATT',   'LSTM_Att'),
    'BiLSTM_1L':    ('BILSTM1L',   'BiLSTM_1L'),
    'BiLSTM_2L':    ('BILSTM2L',   'BiLSTM_2L'),
    'BiLSTM_Att':   ('BILSTM_ATT', 'BiLSTM_Att'),
    'GRU_1L':       ('GRU1L',      'GRU_1L'),
    'GRU_2L':       ('GRU2L',      'GRU_2L'),
    'GRU_Att':      ('GRU_ATT',    'GRU_Att'),
    'BiGRU_1L':     ('BIGRU1L',    'BiGRU_1L'),
    'BiGRU_2L':     ('BIGRU2L',    'BiGRU_2L'),
    'BiGRU_Att':    ('BIGRU_ATT',  'BiGRU_Att'),
}
ALL_MODELS = list(ARCH_MAP.keys())


# ─── Chargement métriques sauvegardées ────────────────────────────────────
def load_saved_metrics(model: str, target: str, exp: str):
    """Lit metrics.json sauvegardé pendant l'entraînement."""
    p = DL_OUTPUTS / model / target / exp / 'metrics.json'
    if not p.exists():
        return None
    with open(p) as f:
        return json.load(f)


def load_loso_metrics(model: str, target: str):
    """Lit metrics.json LOSO."""
    p = DL_OUTPUTS / model / target / 'LOSO' / 'metrics.json'
    if not p.exists():
        return None
    with open(p) as f:
        return json.load(f)


def best_saved_metrics(model: str, target: str):
    """Retourne les métriques de la meilleure expérience (plus petit MAE)."""
    best_m, best_exp = None, None
    for exp in EXPERIMENTS:
        m = load_saved_metrics(model, target, exp)
        if m is None:
            continue
        if best_m is None or m.get('mae', 99) < best_m.get('mae', 99):
            best_m, best_exp = m, exp
    return best_m, best_exp


# ─── Chargement modèle + inférence ────────────────────────────────────────
_arch_cache = {}

def import_arch_class(model: str):
    if model in _arch_cache:
        return _arch_cache[model]
    file_stem, class_name = ARCH_MAP[model]
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
    _arch_cache[model] = cls
    return cls


def find_best_pt(model: str, target: str):
    """Cherche le meilleur .pt (FULL > D > C > B > A)."""
    d = MODEL_BASE / model / target
    for exp in ['FULL', 'D', 'C', 'B', 'A']:
        pt = d / f'{model}_{target}_{exp}_best.pt'
        if pt.exists():
            return pt, exp
    return None, None


def predict_regression(model_obj, X: np.ndarray) -> np.ndarray:
    """Prédit des scores continus — sortie scalaire (régression, pas softmax)."""
    model_obj.eval()
    X_t = torch.FloatTensor(X)
    if X_t.dim() == 2:
        X_t = X_t.unsqueeze(1)
    preds = []
    with torch.no_grad():
        for i in range(0, len(X_t), 256):
            out = model_obj(X_t[i:i+256].to(DEVICE)).squeeze(1).cpu().numpy()
            preds.append(out)
    return np.clip(np.concatenate(preds), 0.0, 10.0)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, thr=SCORE_THR):
    """MAE, RMSE, R², AUC-ROC, F1-macro sur seuil thr."""
    mae  = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    r2   = float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0
    y_bin = (y_true >= thr).astype(int)
    auc, f1m = 0.5, 0.0
    if len(np.unique(y_bin)) > 1:
        try:
            auc = float(roc_auc_score(y_bin, y_pred))
        except Exception:
            pass
        y_pred_bin = (y_pred >= thr).astype(int)
        f1m = float(f1_score(y_bin, y_pred_bin, average='macro', zero_division=0))
    return {'mae': mae, 'rmse': rmse, 'r2': r2, 'auc_roc': auc, 'f1_macro': f1m}


def evaluate_on_holdout(model: str, target: str):
    """
    Charge le .pt et évalue sur X_test.npy (holdout par sujet).
    Retourne (metrics_dict, exp_used, error_str).
    """
    X_path = DATA_DIR / target / 'X_test.npy'
    y_path = DATA_DIR / target / 'y_test.npy'
    if not X_path.exists():
        return None, None, f"X_test.npy introuvable pour {target}"

    X_test = np.load(X_path)
    y_test = np.load(y_path).astype(np.float32)

    pt_path, exp_used = find_best_pt(model, target)
    if pt_path is None:
        return None, None, f"aucun .pt trouvé dans {MODEL_BASE / model / target}"

    try:
        ModelClass = import_arch_class(model)
    except Exception as e:
        return None, None, f"import : {e}"

    try:
        model_obj = ModelClass().to(DEVICE)
        try:
            state = torch.load(pt_path, map_location=DEVICE, weights_only=True)
        except Exception:
            state = torch.load(pt_path, map_location=DEVICE)
        model_obj.load_state_dict(state)
    except Exception as e:
        return None, None, f"chargement poids : {e}"

    t0 = time.time()
    y_pred = predict_regression(model_obj, X_test)
    elapsed_ms = (time.time() - t0) * 1000 / len(y_test)

    m = compute_metrics(y_test, y_pred)
    m['inference_ms_per_epoch'] = elapsed_ms
    m['n_test'] = len(y_test)
    m['exp_pt'] = exp_used
    return m, exp_used, None


# ─── Visualisations ───────────────────────────────────────────────────────
def plot_ranking(df: pd.DataFrame, target: str, save_path: Path):
    metrics = [('mae', 'MAE ↓', True), ('r2', 'R² ↑', False), ('auc_roc', 'AUC-ROC ↑', False)]
    fig, axes = plt.subplots(1, 3, figsize=(21, max(6, len(df) * 0.45)))
    cmap = plt.cm.tab20(np.linspace(0, 1, len(df)))

    for ax, (metric, label, invert) in zip(axes, metrics):
        sorted_df = df.sort_values(metric, ascending=not invert)
        bars = ax.barh(sorted_df['model'], sorted_df[metric],
                       color=cmap[:len(sorted_df)], alpha=0.85)
        ax.set_xlabel(label)
        ax.set_title(label, fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        for bar, val in zip(bars, sorted_df[metric]):
            ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2,
                    f'{val:.3f}', va='center', fontsize=7)

    fig.suptitle(f'NeuroCap – DL Régression — {target.upper()} (meilleure expérience)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_heatmap(df: pd.DataFrame, target: str, save_path: Path):
    cols  = ['mae', 'rmse', 'r2', 'auc_roc', 'f1_macro']
    lbls  = ['MAE', 'RMSE', 'R²', 'AUC-ROC', 'F1-macro']
    heat  = df.set_index('model')[cols].copy()
    heat.columns = lbls
    heat  = heat.sort_values('MAE')

    fig, ax = plt.subplots(figsize=(10, max(5, len(df) * 0.45)))
    # MAE et RMSE : vert = petit (bon) → inverser colormap
    norm_heat = heat.copy()
    for col in ['MAE', 'RMSE']:
        col_min = norm_heat[col].min()
        col_max = norm_heat[col].max()
        if col_max > col_min:
            norm_heat[col] = 1 - (norm_heat[col] - col_min) / (col_max - col_min)
    sns.heatmap(norm_heat, annot=heat, fmt='.3f', cmap='RdYlGn',
                vmin=0, vmax=1, linewidths=0.5, ax=ax,
                cbar_kws={'label': 'Score normalisé (vert=bon)'})
    ax.set_title(f'Heatmap DL Régression — {target.upper()}',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def composite_score(row):
    """Même formule que compare.py pour cohérence."""
    return (0.35 * max(row.get('r2', 0), 0)
            + 0.30 * (max(row.get('auc_roc', 0.5), 0.5) - 0.5) * 2
            + 0.20 * max(1 - row.get('mae', 10) / 10, 0)
            + 0.15 * max(row.get('f1_macro', 0), 0))


# ─── Main ─────────────────────────────────────────────────────────────────
def main(models_to_test=None, targets_to_test=None):
    print("=" * 75)
    print("NeuroCap – Test Suite DL Régression")
    print(f"Device : {DEVICE} | Seuil Low/High : {SCORE_THR}")
    print("=" * 75)

    target_models  = models_to_test  or ALL_MODELS
    target_targets = targets_to_test or TARGETS

    all_rows   = {t: [] for t in TARGETS}
    loso_rows  = []

    for model in target_models:
        if model not in ARCH_MAP:
            print(f"\n[SKIP] Modèle inconnu : {model}")
            continue

        print(f"\n{'─'*65}")
        print(f"  Modèle : {model}")

        for target in target_targets:
            print(f"\n  ── {target.upper()} ──")

            # ── 1. Métriques sauvegardées (meilleure expérience) ────────────
            best_m, best_exp = best_saved_metrics(model, target)
            if best_m is not None:
                row = {
                    'model':        model,
                    'target':       target,
                    'exp':          best_exp,
                    'source':       'saved_metrics',
                    'mae':          best_m.get('mae',      99.0),
                    'rmse':         best_m.get('rmse',     99.0),
                    'r2':           best_m.get('r2',       -99.0),
                    'auc_roc':      best_m.get('auc_roc',  0.5),
                    'f1_macro':     best_m.get('f1_macro', 0.0),
                    'deploy_score': (best_m.get('deploy') or {}).get('total_score', 0.0),
                    'train_time_s': best_m.get('train_time_sec', 0.0),
                }
                row['composite'] = composite_score(row)
                all_rows[target].append(row)
                print(f"  [Sauvegardé Exp.{best_exp}] "
                      f"MAE={row['mae']:.3f}  R²={row['r2']:.3f}  "
                      f"AUC={row['auc_roc']:.3f}  F1={row['f1_macro']:.3f}  "
                      f"Deploy={row['deploy_score']:.1f}")
            else:
                print(f"  [Sauvegardé] Aucun metrics.json trouvé")

            # ── 2. Évaluation directe sur holdout X_test.npy ────────────────
            m_ho, exp_pt, err = evaluate_on_holdout(model, target)
            if m_ho is not None:
                print(f"  [Holdout .pt Exp.{exp_pt}] "
                      f"MAE={m_ho['mae']:.3f}  R²={m_ho['r2']:.3f}  "
                      f"AUC={m_ho['auc_roc']:.3f}  "
                      f"Lat={m_ho['inference_ms_per_epoch']:.2f}ms/ep")
            else:
                print(f"  [Holdout] {err}")

            # ── 3. LOSO ─────────────────────────────────────────────────────
            loso_m = load_loso_metrics(model, target)
            if loso_m is not None:
                loso_rows.append({
                    'model':    model,
                    'target':   target,
                    'mae':      loso_m.get('mae',     99.0),
                    'rmse':     loso_m.get('rmse',    99.0),
                    'r2':       loso_m.get('r2',      -99.0),
                    'auc_roc':  loso_m.get('auc_roc', 0.5),
                    'f1_macro': loso_m.get('f1_macro', 0.0),
                    'n_folds':  loso_m.get('n_folds', 0),
                })
                print(f"  [LOSO]       "
                      f"MAE={loso_m.get('mae',0):.3f}  R²={loso_m.get('r2',0):.3f}  "
                      f"AUC={loso_m.get('auc_roc',0):.3f}  "
                      f"Folds={loso_m.get('n_folds',0)}")
            else:
                print(f"  [LOSO]       Non disponible")

    # ─── Tableaux et graphiques par target ───────────────────────────────────
    for target in target_targets:
        rows = all_rows[target]
        if not rows:
            print(f"\n[{target.upper()}] Aucune métrique disponible.")
            continue

        df = pd.DataFrame(rows).sort_values('composite', ascending=False).reset_index(drop=True)
        df.index += 1
        df.index.name = 'Rang'

        print(f"\n{'='*75}")
        print(f"CLASSEMENT {target.upper()} (score composite = 35%R² + 30%AUC + 20%MAE + 15%F1)")
        print(f"{'='*75}")
        print(f"{'Rang':>4}  {'Modèle':<16}  {'Exp':>4}  {'MAE':>6}  {'RMSE':>6}  "
              f"{'R²':>7}  {'AUC':>6}  {'F1':>6}  {'Deploy':>7}  {'Score':>7}")
        print("─" * 75)
        for rank, row in df.iterrows():
            marker = " ★" if rank == 1 else "  "
            print(f"{rank:>4}{marker} {row['model']:<16}  {row['exp']:>4}  "
                  f"{row['mae']:>6.3f}  {row['rmse']:>6.3f}  "
                  f"{row['r2']:>7.3f}  {row['auc_roc']:>6.3f}  "
                  f"{row['f1_macro']:>6.3f}  {row['deploy_score']:>7.1f}  "
                  f"{row['composite']:>7.4f}")

        # CSV
        df.to_csv(REPORT_DIR / f'results_{target}.csv')

        # Figures
        plot_ranking(df.reset_index(), target, REPORT_DIR / f'ranking_{target}.png')
        plot_heatmap(df.reset_index(), target, REPORT_DIR / f'heatmap_{target}.png')
        print(f"\n  ranking_{target}.png + heatmap_{target}.png")

    # ─── Tableau LOSO ─────────────────────────────────────────────────────────
    if loso_rows:
        df_loso = pd.DataFrame(loso_rows).sort_values(['target', 'mae'])
        df_loso.to_csv(REPORT_DIR / 'loso_summary.csv', index=False)

        print(f"\n{'='*75}")
        print("RÉSUMÉ LOSO")
        print(f"{'='*75}")
        print(f"{'Modèle':<16}  {'Target':>7}  {'MAE':>6}  {'R²':>7}  "
              f"{'AUC':>6}  {'F1':>6}  {'Folds':>5}")
        print("─" * 60)
        for _, r in df_loso.iterrows():
            print(f"{r['model']:<16}  {r['target']:>7}  {r['mae']:>6.3f}  "
                  f"{r['r2']:>7.3f}  {r['auc_roc']:>6.3f}  "
                  f"{r['f1_macro']:>6.3f}  {r['n_folds']:>5.0f}")

    # ─── Rapport de décision ──────────────────────────────────────────────────
    rpt = REPORT_DIR / 'decision_report.txt'
    with open(rpt, 'w', encoding='utf-8') as f:
        f.write("NeuroCap – Rapport de Décision DL Régression\n")
        f.write("=" * 65 + "\n")
        f.write(f"Seuil Low/High : {SCORE_THR} | Score composite : "
                f"35%R² + 30%AUC + 20%(1-MAE/10) + 15%F1\n\n")
        for target in target_targets:
            rows = all_rows[target]
            if not rows:
                continue
            df = pd.DataFrame(rows).sort_values('composite', ascending=False)
            best = df.iloc[0]
            f.write(f"\n{'─'*65}\n")
            f.write(f"TARGET : {target.upper()}\n")
            f.write(f"{'─'*65}\n")
            f.write(f"★ MEILLEUR : {best['model']} (Exp. {best['exp']})\n")
            f.write(f"  MAE={best['mae']:.4f}  RMSE={best['rmse']:.4f}  "
                    f"R²={best['r2']:.4f}\n")
            f.write(f"  AUC-ROC={best['auc_roc']:.4f}  F1-macro={best['f1_macro']:.4f}  "
                    f"Deploy={best['deploy_score']:.1f}/100\n\n")
            f.write(f"{'Rang':<5} {'Modèle':<16} {'Exp':>4} {'MAE':>7} "
                    f"{'R²':>7} {'AUC':>7} {'Score':>8}\n")
            f.write("-" * 55 + "\n")
            for rank, (_, row) in enumerate(df.iterrows(), 1):
                f.write(f"{rank:<5} {row['model']:<16} {row['exp']:>4} "
                        f"{row['mae']:>7.4f} {row['r2']:>7.4f} "
                        f"{row['auc_roc']:>7.4f} {row['composite']:>8.4f}\n")

    print(f"\n{'='*75}")
    print(f"Sorties : {REPORT_DIR}")
    print(f"  • results_conc.csv / results_stress.csv")
    print(f"  • ranking_conc.png / ranking_stress.png")
    print(f"  • heatmap_conc.png / heatmap_stress.png")
    print(f"  • loso_summary.csv")
    print(f"  • decision_report.txt")
    print(f"{'='*75}")


if __name__ == '__main__':
    args = sys.argv[1:]
    models  = [a for a in args if a in ARCH_MAP]
    targets = [a for a in args if a in TARGETS]
    unknown = [a for a in args if a not in ARCH_MAP and a not in TARGETS]
    if unknown:
        print(f"[WARN] Arguments inconnus : {unknown}")
        print(f"  Modèles  : {ALL_MODELS}")
        print(f"  Cibles   : {TARGETS}")
    main(models or None, targets or None)
