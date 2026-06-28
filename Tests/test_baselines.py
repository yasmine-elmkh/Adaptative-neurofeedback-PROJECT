"""
NeuroCap – Test Suite Baselines Régression
==========================================
Évalue SVR / Random Forest / XGBoost / LightGBM sur DEUX sources :

  1. Métriques sauvegardées (results_*.json) — lues depuis reports/Regression/Baseline/
     • Meilleure expérience par modèle (max R²) dans le JSON d'entraînement

  2. Évaluation directe sur X_test.npy / feat78_test.npy (holdout)
     • feat15       : extraction à la volée depuis data/Regression/augmented/
     • feat15_smote : idem, modèle SMOTE
     • feat78       : chargement de Features/{target}/feat78_test.npy
     • feat78_smote : idem, modèle SMOTE

Deux targets séparés : conc et stress.

Usage :
    python Tests/test_baselines.py              # tous les modèles × configs
    python Tests/test_baselines.py SVR          # un seul classifieur
    python Tests/test_baselines.py SVR conc     # classifieur + target

Sorties :
    reports/Tests/baselines/
        ├── results_conc.csv / results_stress.csv
        ├── ranking_conc.png / ranking_stress.png
        ├── heatmap_conc.png / heatmap_stress.png
        └── decision_report.txt
"""

import sys
import json
import time
import warnings
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import joblib
from sklearn.metrics import roc_auc_score, f1_score

warnings.filterwarnings('ignore')

# ─── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR     = PROJECT_ROOT / 'data'    / 'Regression' / 'augmented'
FEAT_ROOT    = PROJECT_ROOT / 'Features'
MODEL_BASE   = PROJECT_ROOT / 'models'  / 'Regression' / 'Baseline'
REPORT_BASE  = PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline'
REPORT_DIR   = PROJECT_ROOT / 'reports' / 'Tests' / 'baselines'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

# ─── sys.path pour extract_feat15 ─────────────────────────────────────────────
_DATA_SRC = PROJECT_ROOT / 'src' / 'data'
if str(_DATA_SRC) not in sys.path:
    sys.path.insert(0, str(_DATA_SRC))

try:
    from features_extraction import get_feature_vector as _get_fv
    _HAS_FEAT15 = True
except ImportError:
    _HAS_FEAT15 = False

# ─── Constantes ───────────────────────────────────────────────────────────────
TARGETS     = ['conc', 'stress']
SCORE_THR   = 5.0

MODEL_NAMES = ['SVR', 'Random Forest', 'XGBoost', 'LightGBM']

COLORS = {
    'SVR':           '#E74C3C',
    'Random Forest': '#2980B9',
    'XGBoost':       '#27AE60',
    'LightGBM':      '#F39C12',
}

# ─── Configs features × modèles ───────────────────────────────────────────────
# feat_type   : 'raw' (extraction feat15 à la volée) ou 'feat78' (préchargé)
# model_suffix: suffixe du fichier .joblib
# scaler_suffix: suffixe du fichier scaler .joblib
FEAT_CONFIGS = {
    'feat15': {
        'model_root':    MODEL_BASE / 'feat15',
        'report_root':   REPORT_BASE / 'feat15',
        'feat_type':     'raw',
        'model_suffix':  '_regressor.joblib',
        'scaler_suffix': '_scaler.joblib',
    },
    'feat15_smote': {
        'model_root':    MODEL_BASE / 'feat15_smote',
        'report_root':   REPORT_BASE / 'feat15_smote',
        'feat_type':     'raw',
        'model_suffix':  '_smote.joblib',
        'scaler_suffix': '_scaler_smote.joblib',
    },
    'feat78': {
        'model_root':    MODEL_BASE / 'feat78',
        'report_root':   REPORT_BASE / 'feat78',
        'feat_type':     'feat78',
        'model_suffix':  '_regressor.joblib',
        'scaler_suffix': '_scaler.joblib',
    },
    'feat78_smote': {
        'model_root':    MODEL_BASE / 'feat78_smote',
        'report_root':   REPORT_BASE / 'feat78_smote',
        'feat_type':     'feat78',
        'model_suffix':  '_feat78_smote.joblib',
        'scaler_suffix': '_scaler_feat78_smote.joblib',
    },
}


# ─── Extraction feat15 ────────────────────────────────────────────────────────
def extract_feat15(X_signals: np.ndarray) -> np.ndarray:
    """Calcule les 15 features spectrales sur un batch de signaux bruts."""
    if not _HAS_FEAT15:
        raise RuntimeError("features_extraction.py introuvable — impossible d'extraire feat15")
    feats = np.array([_get_fv(ep) for ep in X_signals], dtype=np.float32)
    return np.nan_to_num(feats, nan=0.0, posinf=0.0, neginf=0.0)


# ─── Chargement features + y_test ─────────────────────────────────────────────
def load_test_features(feat_type: str, target: str):
    """
    Charge X_test et y_test selon le type de features.
    Retourne (X, y, erreur).
    """
    y_path = DATA_DIR / target / 'y_test.npy'
    if not y_path.exists():
        return None, None, f"y_test.npy introuvable : {y_path}"
    y = np.load(y_path).astype(np.float32)

    if feat_type == 'raw':
        x_path = DATA_DIR / target / 'X_test.npy'
        if not x_path.exists():
            return None, None, f"X_test.npy introuvable : {x_path}"
        X_raw = np.load(x_path)
        if len(X_raw) == 0:
            return None, None, "X_test.npy vide"
        try:
            X = extract_feat15(X_raw)
        except RuntimeError as e:
            return None, None, str(e)
    else:
        x_path = FEAT_ROOT / target / 'feat78_test.npy'
        if not x_path.exists():
            return None, None, f"feat78_test.npy introuvable : {x_path}"
        X = np.load(x_path).astype(np.float32)

    if len(X) != len(y):
        return None, None, f"Taille incohérente X={len(X)} y={len(y)}"
    return X, y, None


# ─── Chargement modèle ────────────────────────────────────────────────────────
def load_model(mn: str, target: str, cfg: dict):
    """
    Charge modèle + scaler depuis MODEL_ROOT / target / f'{mn_safe}{target}{suffix}'.
    Retourne (model, scaler, erreur).
    """
    mn_safe      = mn.replace(' ', '_')
    model_dir    = cfg['model_root'] / target
    model_path   = model_dir / f'{mn_safe}_{target}{cfg["model_suffix"]}'
    scaler_path  = model_dir / f'{mn_safe}_{target}{cfg["scaler_suffix"]}'

    if not model_path.exists():
        return None, None, f"modèle introuvable : {model_path.name}"
    if not scaler_path.exists():
        return None, None, f"scaler introuvable : {scaler_path.name}"

    try:
        model  = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
    except Exception as e:
        return None, None, f"erreur chargement : {e}"
    return model, scaler, None


# ─── Métriques ────────────────────────────────────────────────────────────────
def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray, thr=SCORE_THR) -> dict:
    """MAE, RMSE, R², AUC-ROC, F1-macro avec seuil thr."""
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


# ─── Métriques sauvegardées ───────────────────────────────────────────────────
def load_saved_best(feat_key: str, mn: str, target: str) -> dict | None:
    """
    Lit results_{target}.json depuis reports/Regression/Baseline/{feat_key}/{target}/
    et retourne les métriques de la meilleure expérience (max R²) pour ce modèle.
    """
    json_path = FEAT_CONFIGS[feat_key]['report_root'] / target / f'results_{target}.json'
    if not json_path.exists():
        return None
    try:
        with open(json_path) as f:
            data = json.load(f)
    except Exception:
        return None

    # 'loso' est un dict {exp: {model_name: metrics_dict}}
    loso = data.get('loso', {})
    best = None
    for exp, models in loso.items():
        if exp.startswith('_') or not isinstance(models, dict):
            continue
        m = models.get(mn)
        if not isinstance(m, dict):
            continue
        if best is None or m.get('r2', -99) > best.get('r2', -99):
            best = dict(m)
            best['exp']   = exp
            best['model'] = mn
    return best


# ─── Évaluation holdout ───────────────────────────────────────────────────────
def evaluate_holdout(mn: str, target: str, feat_key: str) -> tuple:
    """
    Charge modèle + features → évalue sur holdout X_test.
    Retourne (metrics_dict, erreur).
    """
    cfg = FEAT_CONFIGS[feat_key]

    X, y, err = load_test_features(cfg['feat_type'], target)
    if err:
        return None, err

    model, scaler, err = load_model(mn, target, cfg)
    if err:
        return None, err

    try:
        Xs = scaler.transform(X)
        t0 = time.time()
        y_pred = np.clip(model.predict(Xs).astype(np.float32), 0.0, 10.0)
        elapsed_ms = (time.time() - t0) * 1000 / len(y)
    except Exception as e:
        return None, f"inférence : {e}"

    m = compute_metrics(y, y_pred)
    m['inference_ms_per_epoch'] = elapsed_ms
    m['n_test'] = len(y)
    return m, None


# ─── Visualisations ───────────────────────────────────────────────────────────
def plot_ranking(df: pd.DataFrame, target: str, save_path: Path):
    metrics = [('mae', 'MAE ↓', True), ('r2', 'R² ↑', False), ('auc_roc', 'AUC-ROC ↑', False)]
    fig, axes = plt.subplots(1, 3, figsize=(21, max(6, len(df) * 0.5)))
    cmap = plt.cm.tab20(np.linspace(0, 1, len(df)))

    for ax, (metric, label, invert) in zip(axes, metrics):
        sorted_df = df.sort_values(metric, ascending=not invert)
        bars = ax.barh(sorted_df['model_feat'], sorted_df[metric],
                       color=cmap[:len(sorted_df)], alpha=0.85)
        ax.set_xlabel(label)
        ax.set_title(label, fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        for bar, val in zip(bars, sorted_df[metric]):
            ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2,
                    f'{val:.3f}', va='center', fontsize=7)

    fig.suptitle(f'NeuroCap – Baselines Régression — {target.upper()} (meilleure exp.)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_heatmap(df: pd.DataFrame, target: str, save_path: Path):
    cols = ['mae', 'rmse', 'r2', 'auc_roc', 'f1_macro']
    lbls = ['MAE', 'RMSE', 'R²', 'AUC-ROC', 'F1-macro']
    heat = df.set_index('model_feat')[cols].copy()
    heat.columns = lbls
    heat = heat.sort_values('MAE')

    fig, ax = plt.subplots(figsize=(10, max(5, len(df) * 0.5)))
    norm_heat = heat.copy()
    for col in ['MAE', 'RMSE']:
        col_min, col_max = norm_heat[col].min(), norm_heat[col].max()
        if col_max > col_min:
            norm_heat[col] = 1 - (norm_heat[col] - col_min) / (col_max - col_min)
    sns.heatmap(norm_heat, annot=heat, fmt='.3f', cmap='RdYlGn',
                vmin=0, vmax=1, linewidths=0.5, ax=ax,
                cbar_kws={'label': 'Score normalisé (vert=bon)'})
    ax.set_title(f'Heatmap Baselines Régression — {target.upper()}',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def composite_score(row: dict) -> float:
    return (0.35 * max(row.get('r2', 0), 0)
            + 0.30 * (max(row.get('auc_roc', 0.5), 0.5) - 0.5) * 2
            + 0.20 * max(1 - row.get('mae', 10) / 10, 0)
            + 0.15 * max(row.get('f1_macro', 0), 0))


# ─── Main ─────────────────────────────────────────────────────────────────────
def main(models_to_test=None, targets_to_test=None):
    print("=" * 75)
    print("NeuroCap – Test Suite Baselines Régression")
    print(f"Seuil Low/High : {SCORE_THR}")
    print("=" * 75)

    target_models  = models_to_test  or MODEL_NAMES
    target_targets = targets_to_test or TARGETS

    all_rows = {t: [] for t in TARGETS}

    for mn in target_models:
        if mn not in MODEL_NAMES:
            print(f"\n[SKIP] Modèle inconnu : {mn}")
            continue

        print(f"\n{'─'*65}")
        print(f"  Modèle : {mn}")

        for target in target_targets:
            print(f"\n  ── {target.upper()} ──")

            for feat_key in FEAT_CONFIGS:
                label = f"{mn}/{feat_key}"

                # ── 1. Métriques sauvegardées ────────────────────────────────
                saved = load_saved_best(feat_key, mn, target)
                if saved is not None:
                    row = {
                        'model':      mn,
                        'feat_key':   feat_key,
                        'model_feat': f"{mn.replace(' ','_')}-{feat_key}",
                        'target':     target,
                        'exp':        saved.get('exp', '?'),
                        'source':     'saved_metrics',
                        'mae':        saved.get('mae',     99.0),
                        'rmse':       saved.get('rmse',    99.0),
                        'r2':         saved.get('r2',      -99.0),
                        'auc_roc':    saved.get('auc_roc', saved.get('auc', 0.5)),
                        'f1_macro':   saved.get('f1_macro', 0.0),
                        'deploy_score': (saved.get('deploy') or {}).get('total_score', 0.0),
                    }
                    row['composite'] = composite_score(row)
                    all_rows[target].append(row)
                    print(f"  [{feat_key:<14} Sauvegardé Exp.{row['exp']}] "
                          f"MAE={row['mae']:.3f}  R²={row['r2']:.3f}  "
                          f"AUC={row['auc_roc']:.3f}  F1={row['f1_macro']:.3f}")
                else:
                    print(f"  [{feat_key:<14} Sauvegardé] Aucun résultat JSON trouvé")

                # ── 2. Évaluation directe sur holdout ────────────────────────
                m_ho, err = evaluate_holdout(mn, target, feat_key)
                if m_ho is not None:
                    print(f"  [{feat_key:<14} Holdout]    "
                          f"MAE={m_ho['mae']:.3f}  R²={m_ho['r2']:.3f}  "
                          f"AUC={m_ho['auc_roc']:.3f}  "
                          f"Lat={m_ho['inference_ms_per_epoch']:.3f}ms/ep  "
                          f"N={m_ho['n_test']}")
                else:
                    print(f"  [{feat_key:<14} Holdout]    {err}")

    # ─── Tableaux et graphiques par target ───────────────────────────────────
    for target in target_targets:
        rows = all_rows[target]
        if not rows:
            print(f"\n[{target.upper()}] Aucune métrique disponible.")
            continue

        df = (pd.DataFrame(rows)
              .sort_values('composite', ascending=False)
              .reset_index(drop=True))
        df.index += 1
        df.index.name = 'Rang'

        print(f"\n{'='*75}")
        print(f"CLASSEMENT {target.upper()} (score composite = 35%R² + 30%AUC + 20%MAE + 15%F1)")
        print(f"{'='*75}")
        print(f"{'Rang':>4}  {'Modèle-Features':<34}  {'Exp':>4}  "
              f"{'MAE':>6}  {'RMSE':>6}  {'R²':>7}  {'AUC':>6}  {'F1':>6}  {'Score':>7}")
        print("-" * 75)
        for rank, row in df.iterrows():
            marker = " ★" if rank == 1 else "  "
            print(f"{rank:>4}{marker} {row['model_feat']:<34}  {str(row['exp']):>4}  "
                  f"{row['mae']:>6.3f}  {row['rmse']:>6.3f}  "
                  f"{row['r2']:>7.3f}  {row['auc_roc']:>6.3f}  "
                  f"{row['f1_macro']:>6.3f}  {row['composite']:>7.4f}")

        best = df.iloc[0]
        print(f"\n★ Meilleur baseline {target.upper()} : {best['model_feat']}  "
              f"(Exp.{best['exp']})  Score={best['composite']:.4f}")

        # CSV
        csv_path = REPORT_DIR / f'results_{target}.csv'
        df.reset_index().to_csv(csv_path, index=False)

        # Plots
        plot_ranking(df.reset_index(), target, REPORT_DIR / f'ranking_{target}.png')
        plot_heatmap(df.reset_index(), target, REPORT_DIR / f'heatmap_{target}.png')

        # Comparaison feat15 vs feat78 par modèle
        print(f"\n{'─'*75}")
        print(f"IMPACT DES FEATURES — {target.upper()}")
        print(f"{'─'*75}")
        for m in MODEL_NAMES:
            mname = m.replace(' ', '_')
            r15  = df[df['model_feat'] == f"{mname}-feat15"]
            r78  = df[df['model_feat'] == f"{mname}-feat78"]
            if r15.empty or r78.empty:
                continue
            r2_15 = r15.iloc[0]['r2']
            r2_78 = r78.iloc[0]['r2']
            delta = r2_78 - r2_15
            sign  = "+" if delta >= 0 else ""
            winner = "feat78" if delta > 0.001 else ("feat15" if delta < -0.001 else "Egal")
            print(f"  {m:<16} feat15 R²={r2_15:.4f}  feat78 R²={r2_78:.4f}  "
                  f"Δ={sign}{delta:.4f}  → {winner}")

    # ─── Rapport de décision ─────────────────────────────────────────────────
    report_path = REPORT_DIR / 'decision_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("NeuroCap – Rapport de Décision Baselines Régression\n")
        f.write("=" * 70 + "\n\n")
        f.write("Paradigme : régression continue (scores 0-10)\n")
        f.write(f"Seuil binarisation : {SCORE_THR}\n")
        f.write("Score composite : 35%R² + 30%(AUC-0.5)×2 + 20%(1-MAE/10) + 15%F1\n\n")

        for target in target_targets:
            rows = all_rows[target]
            if not rows:
                continue
            df = (pd.DataFrame(rows)
                  .sort_values('composite', ascending=False)
                  .reset_index(drop=True))
            f.write(f"\n{'='*70}\n")
            f.write(f"TARGET : {target.upper()}\n")
            f.write(f"{'='*70}\n")
            f.write(f"{'Rang':<5} {'Modèle-Features':<36} {'MAE':>6} {'R²':>7} "
                    f"{'AUC':>6} {'F1':>6} {'Score':>7}\n")
            f.write("-" * 70 + "\n")
            for rank, row in df.iterrows():
                f.write(f"{rank+1:<5} {row['model_feat']:<36} "
                        f"{row['mae']:>6.3f} {row['r2']:>7.3f} "
                        f"{row['auc_roc']:>6.3f} {row['f1_macro']:>6.3f} "
                        f"{row['composite']:>7.4f}\n")

            best = df.iloc[0]
            f.write(f"\nRECOMMANDATION {target.upper()} : {best['model_feat']}\n")
            f.write(f"  R²      = {best['r2']:.4f}\n")
            f.write(f"  AUC-ROC = {best['auc_roc']:.4f}\n")
            f.write(f"  MAE     = {best['mae']:.4f}\n")
            f.write(f"  F1-macro= {best['f1_macro']:.4f}\n")
            f.write(f"  Score   = {best['composite']:.4f}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write("Avantages Baselines ML :\n")
        f.write("  + Interprétabilité : features spectrales lisibles\n")
        f.write("  + Latence ultra-faible (< 1 ms par epoch)\n")
        f.write("  + Déploiement embarqué possible (ESP32 / Raspberry Pi)\n")
        f.write("  + Aucun GPU requis pour l'inférence\n")
        f.write("  + Robuste sur petits datasets\n")

    print(f"\n{'='*75}")
    print(f"Sorties sauvegardées dans : {REPORT_DIR}")
    print(f"  • results_conc.csv / results_stress.csv")
    print(f"  • ranking_conc.png / ranking_stress.png")
    print(f"  • heatmap_conc.png / heatmap_stress.png")
    print(f"  • decision_report.txt")
    print(f"{'='*75}")


if __name__ == '__main__':
    models_arg = None
    target_arg = None
    if len(sys.argv) >= 2:
        models_arg = [sys.argv[1]]
    if len(sys.argv) >= 3:
        target_arg = [sys.argv[2]]
    main(models_arg, target_arg)
