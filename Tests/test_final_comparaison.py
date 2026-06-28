"""
NeuroCap – Comparaison Finale : Baselines ML vs Deep Learning (Régression)
==========================================================================
Agrège les résultats des deux suites de test et produit la recommandation finale.

Sources (par target conc / stress) :
  Baselines → reports/Tests/baselines/results_{target}.csv
  DL        → reports/Tests/deep_learning/results_{target}.csv
  LOSO DL   → reports/Tests/deep_learning/loso_summary.csv

Paradigme : régression continue (scores 0-10), seuil=5.0
Score composite : 35%R² + 30%(AUC-0.5)×2 + 20%(1-MAE/10) + 15%F1

Usage :
    python Tests/test_baselines.py          # étape 1
    python Tests/test_deep_learning.py      # étape 2
    python Tests/test_final_comparison.py   # étape 3

    # Lire directement les JSON d'entraînement :
    python Tests/test_final_comparison.py --from-training

Sorties :
    reports/Tests/final/
        ├── unified_ranking_conc.csv / unified_ranking_stress.csv
        ├── comparison_bars_conc.png / comparison_bars_stress.png
        ├── scatter_r2_auc_conc.png  / scatter_r2_auc_stress.png
        ├── boxplot_categories.png
        └── FINAL_DECISION_REPORT.txt
"""

import sys
import json
import warnings
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

warnings.filterwarnings('ignore')

# ─── Chemins ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_BL_DIR = PROJECT_ROOT / 'reports' / 'Tests' / 'baselines'
TEST_DL_DIR = PROJECT_ROOT / 'reports' / 'Tests' / 'deep_learning'

TRAIN_BL_BASE = PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline'
TRAIN_DL_BASE = PROJECT_ROOT / 'reports' / 'Regression' / 'DL'

REPORT_DIR = PROJECT_ROOT / 'reports' / 'Tests' / 'final'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

TARGETS      = ['conc', 'stress']
SCORE_THR    = 5.0
EXPERIMENTS  = ['A', 'B', 'C', 'D', 'FULL']
FEAT_CONFIGS = ['feat15', 'feat15_smote', 'feat78', 'feat78_smote']

PALETTE = {'Baseline ML': '#E74C3C', 'Deep Learning': '#2980B9'}

ALL_DL_MODELS = [
    'CNN1D', 'CNN2D', 'CNN3D', 'EEGNet', 'TCN',
    'CNN_LSTM_Att', 'CNN_GRU_Att',
    'LSTM_1L', 'LSTM_2L', 'LSTM_Att',
    'BiLSTM_1L', 'BiLSTM_2L', 'BiLSTM_Att',
    'GRU_1L', 'GRU_2L', 'GRU_Att',
    'BiGRU_1L', 'BiGRU_2L', 'BiGRU_Att',
]

MODEL_NAMES_BL = ['SVR', 'Random_Forest', 'XGBoost', 'LightGBM']


# ─── Score composite ──────────────────────────────────────────────────────────
def composite_score(row: dict) -> float:
    return (0.35 * max(row.get('r2', 0), 0)
            + 0.30 * (max(row.get('auc_roc', 0.5), 0.5) - 0.5) * 2
            + 0.20 * max(1 - row.get('mae', 10) / 10, 0)
            + 0.15 * max(row.get('f1_macro', 0), 0))


# ─── Chargement résultats test ────────────────────────────────────────────────
def load_test_csv(csv_path: Path, category: str) -> tuple:
    """Charge un CSV de résultats et ajoute la colonne 'category'."""
    if not csv_path.exists():
        return None, f"introuvable : {csv_path.name}"
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return None, f"erreur lecture CSV : {e}"
    if df.empty:
        return None, "CSV vide"
    df['category'] = category
    # Uniformiser le nom du modèle pour l'affichage
    if 'model_feat' in df.columns and 'model' not in df.columns:
        df['model'] = df['model_feat']
    elif 'model' not in df.columns:
        df['model'] = '?'
    return df, None


def load_test_results(target: str) -> tuple:
    """
    Charge résultats baselines + DL depuis les CSVs de test.
    Retourne (df_merged, source_note).
    """
    frames, notes = [], []

    df_bl, err = load_test_csv(TEST_BL_DIR / f'results_{target}.csv', 'Baseline ML')
    if df_bl is not None:
        frames.append(df_bl)
        notes.append(f"Baselines : {len(df_bl)} entrées")
    else:
        notes.append(f"Baselines [{target}] : {err}")

    df_dl, err = load_test_csv(TEST_DL_DIR / f'results_{target}.csv', 'Deep Learning')
    if df_dl is not None:
        frames.append(df_dl)
        notes.append(f"DL : {len(df_dl)} entrées")
    else:
        notes.append(f"DL [{target}] : {err}")

    if not frames:
        return None, " | ".join(notes)
    return pd.concat(frames, ignore_index=True), " | ".join(notes)


# ─── Fallback : métriques d'entraînement ──────────────────────────────────────
def load_training_baseline(target: str) -> tuple:
    """Lit results_{target}.json depuis reports/Regression/Baseline/feat15/{target}/."""
    rows = []
    for feat_key in FEAT_CONFIGS:
        json_path = TRAIN_BL_BASE / feat_key / target / f'results_{target}.json'
        if not json_path.exists():
            continue
        try:
            with open(json_path) as f:
                data = json.load(f)
        except Exception:
            continue
        for r in data.get('loso', []):
            mn = r.get('model', '?').replace(' ', '_')
            rows.append({
                'model':     f"{mn}-{feat_key}",
                'model_feat':f"{mn}-{feat_key}",
                'feat_key':  feat_key,
                'target':    target,
                'exp':       r.get('exp', '?'),
                'source':    'training_json',
                'mae':       r.get('mae',     99.0),
                'rmse':      r.get('rmse',    99.0),
                'r2':        r.get('r2',      -99.0),
                'auc_roc':   r.get('auc_roc', r.get('auc', 0.5)),
                'f1_macro':  r.get('f1_macro', 0.0),
                'category':  'Baseline ML',
            })
    if not rows:
        return None, f"aucun results_{{target}}.json baseline trouvé pour {target}"
    df = pd.DataFrame(rows)
    # Garder meilleure exp par modèle
    df = (df.loc[df.groupby('model')['r2'].idxmax()]
            .reset_index(drop=True))
    return df, None


def load_training_dl(target: str) -> tuple:
    """Lit metrics.json depuis reports/Regression/DL/{model}/{target}/{exp}/."""
    rows = []
    for model in ALL_DL_MODELS:
        best_m, best_exp = None, None
        for exp in EXPERIMENTS:
            p = TRAIN_DL_BASE / model / target / exp / 'metrics.json'
            if not p.exists():
                continue
            try:
                with open(p) as f:
                    m = json.load(f)
            except Exception:
                continue
            if best_m is None or m.get('mae', 99) < best_m.get('mae', 99):
                best_m, best_exp = m, exp
        if best_m is None:
            continue
        rows.append({
            'model':    model,
            'target':   target,
            'exp':      best_exp,
            'source':   'training_json',
            'mae':      best_m.get('mae',     99.0),
            'rmse':     best_m.get('rmse',    99.0),
            'r2':       best_m.get('r2',      -99.0),
            'auc_roc':  best_m.get('auc_roc', 0.5),
            'f1_macro': best_m.get('f1_macro', 0.0),
            'category': 'Deep Learning',
        })
    if not rows:
        return None, f"aucun metrics.json DL trouvé pour {target}"
    return pd.DataFrame(rows), None


def load_results_for_target(target: str, from_training: bool) -> tuple:
    """
    Charge les données pour un target. Fallback automatique sur training JSON si besoin.
    Retourne (df, source_note).
    """
    if not from_training:
        df, note = load_test_results(target)
        if df is not None and not df.empty:
            return df, note

    # Fallback (ou mode --from-training explicite)
    frames, notes = [], []
    df_bl, err = load_training_baseline(target)
    if df_bl is not None:
        frames.append(df_bl)
        notes.append(f"BL training JSON ({len(df_bl)} entrées)")
    else:
        notes.append(f"BL training : {err}")

    df_dl, err = load_training_dl(target)
    if df_dl is not None:
        frames.append(df_dl)
        notes.append(f"DL training JSON ({len(df_dl)} modèles)")
    else:
        notes.append(f"DL training : {err}")

    if not frames:
        return None, " | ".join(notes)
    return pd.concat(frames, ignore_index=True), "[fallback training] " + " | ".join(notes)


# ─── Préparation DataFrame ─────────────────────────────────────────────────────
def prepare_df(df: pd.DataFrame) -> pd.DataFrame:
    """Normalise les types et calcule le score composite."""
    for col in ['mae', 'rmse', 'r2', 'auc_roc', 'f1_macro']:
        df[col] = pd.to_numeric(df.get(col, 0), errors='coerce').fillna(0.0)
    df['composite'] = df.apply(composite_score, axis=1)
    return df.sort_values('composite', ascending=False).reset_index(drop=True)


# ─── Visualisations ───────────────────────────────────────────────────────────
def plot_comparison_bars(df: pd.DataFrame, target: str, save_path: Path):
    """Barplot horizontal MAE / R² / AUC-ROC pour tous les modèles, coloré par catégorie."""
    top_n   = min(20, len(df))
    top     = df.head(top_n).copy()
    metrics = [('mae', 'MAE ↓', True), ('r2', 'R² ↑', False), ('auc_roc', 'AUC-ROC ↑', False)]

    fig, axes = plt.subplots(1, 3, figsize=(21, max(7, top_n * 0.5)))
    for ax, (metric, label, invert) in zip(axes, metrics):
        sorted_t = top.sort_values(metric, ascending=not invert)
        clrs = [PALETTE.get(c, '#7F8C8D') for c in sorted_t['category']]
        bars = ax.barh(sorted_t['model'], sorted_t[metric],
                       color=clrs, alpha=0.85)
        ax.set_xlabel(label)
        ax.set_title(label, fontsize=11, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        for bar, val in zip(bars, sorted_t[metric]):
            ax.text(bar.get_width() + 0.002, bar.get_y() + bar.get_height() / 2,
                    f'{val:.3f}', va='center', fontsize=7)

    from matplotlib.patches import Patch
    handles = [Patch(color=c, label=k) for k, c in PALETTE.items()]
    fig.legend(handles=handles, loc='lower center', ncol=2,
               fontsize=10, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle(f'NeuroCap – Comparaison Finale — {target.upper()}'
                 f'\n(Baseline ML vs Deep Learning)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_scatter_r2_auc(df: pd.DataFrame, target: str, save_path: Path):
    """Scatter R² vs AUC-ROC, coloré par catégorie, taille ∝ 1-MAE/10."""
    fig, ax = plt.subplots(figsize=(10, 7))

    for cat, grp in df.groupby('category'):
        sizes = np.clip((1 - grp['mae'] / 10) * 300, 30, 400)
        ax.scatter(grp['r2'], grp['auc_roc'],
                   color=PALETTE.get(cat, 'gray'), label=cat,
                   s=sizes, alpha=0.80, edgecolors='white', lw=0.5, zorder=5)
        for _, row in grp.nlargest(4, 'composite').iterrows():
            ax.annotate(row['model'], (row['r2'], row['auc_roc']),
                        textcoords='offset points', xytext=(5, 3), fontsize=7)

    ax.axhline(0.5, color='gray', ls='--', lw=0.8, alpha=0.5)
    ax.axvline(0.0, color='gray', ls='--', lw=0.8, alpha=0.5)
    ax.set_xlabel('R² ↑', fontsize=11)
    ax.set_ylabel('AUC-ROC ↑', fontsize=11)
    ax.set_title(f'Performance globale — {target.upper()} (taille ∝ qualité MAE)',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_category_boxplot(frames: dict, save_path: Path):
    """Boxplot MAE / R² / AUC-ROC pour Baselines vs DL — tous targets confondus."""
    metrics = [('mae', 'MAE ↓'), ('r2', 'R² ↑'), ('auc_roc', 'AUC-ROC ↑'),
               ('f1_macro', 'F1-macro ↑')]
    cats    = ['Baseline ML', 'Deep Learning']
    fig, axes = plt.subplots(1, len(metrics), figsize=(18, 5))

    all_df = pd.concat(frames.values(), ignore_index=True) if frames else pd.DataFrame()

    for ax, (metric, label) in zip(axes, metrics):
        for i, cat in enumerate(cats):
            sub = all_df[all_df['category'] == cat][metric].dropna()
            if sub.empty:
                continue
            ax.boxplot(sub, positions=[i], widths=0.4, patch_artist=True,
                       boxprops=dict(facecolor=PALETTE[cat], alpha=0.6),
                       medianprops=dict(color='black', lw=2))
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Baseline\nML', 'Deep\nLearning'], fontsize=8)
        ax.set_ylabel(label)
        ax.set_title(label, fontsize=10)
        ax.grid(axis='y', alpha=0.3)

    fig.suptitle('Distribution métriques : Baseline ML vs Deep Learning (tous targets)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ─── Rapport texte ────────────────────────────────────────────────────────────
def write_final_report(dfs: dict, report_path: Path, source_note: str):
    best_overall: dict = {}
    best_bl: dict      = {}
    best_dl: dict      = {}

    for target, df in dfs.items():
        if df is None or df.empty:
            continue
        best_overall[target] = df.iloc[0]
        bl = df[df['category'] == 'Baseline ML']
        dl = df[df['category'] == 'Deep Learning']
        best_bl[target] = bl.iloc[0] if not bl.empty else None
        best_dl[target] = dl.iloc[0] if not dl.empty else None

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("NeuroCap – RAPPORT DE DÉCISION FINALE (Régression)\n")
        f.write("Paradigme : scores continus 0-10 | Seuil : 5.0\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Source : {source_note}\n")
        f.write("Score composite : 35%R² + 30%(AUC-0.5)×2 + 20%(1-MAE/10) + 15%F1\n\n")

        for target in TARGETS:
            df = dfs.get(target)
            if df is None or df.empty:
                f.write(f"\n[{target.upper()}] Aucune donnée disponible.\n")
                continue

            f.write(f"\n{'='*70}\n")
            f.write(f"TARGET : {target.upper()}\n")
            f.write(f"{'='*70}\n\n")

            # Top 15
            f.write(f"{'Rang':<5} {'Cat':>3} {'Modèle':<34} "
                    f"{'MAE':>6} {'R²':>7} {'AUC':>6} {'F1':>6} {'Score':>7}\n")
            f.write("-" * 70 + "\n")
            for rank, row in df.head(15).iterrows():
                cat = 'BL' if row['category'] == 'Baseline ML' else 'DL'
                f.write(f"{rank+1:<5} [{cat}] {row['model']:<34} "
                        f"{row['mae']:>6.3f} {row['r2']:>7.3f} "
                        f"{row['auc_roc']:>6.3f} {row['f1_macro']:>6.3f} "
                        f"{row['composite']:>7.4f}\n")

            # Comparaison BL vs DL
            bo = best_overall.get(target)
            bb = best_bl.get(target)
            bd = best_dl.get(target)

            f.write(f"\nRECOMMANDATION {target.upper()} : {bo['model'] if bo is not None else '?'}\n")
            if bo is not None:
                f.write(f"  Catégorie : {bo['category']}\n")
                f.write(f"  R²        = {bo['r2']:.4f}\n")
                f.write(f"  AUC-ROC   = {bo['auc_roc']:.4f}\n")
                f.write(f"  MAE       = {bo['mae']:.4f}\n")
                f.write(f"  F1-macro  = {bo['f1_macro']:.4f}\n")
                f.write(f"  Score     = {bo['composite']:.4f}\n")

            if bb is not None and bd is not None:
                delta_r2  = bd['r2'] - bb['r2']
                delta_mae = bb['mae'] - bd['mae']
                sign_r2   = "+" if delta_r2  >= 0 else ""
                sign_mae  = "+" if delta_mae >= 0 else ""
                f.write(f"\nComparaison directe :\n")
                f.write(f"  Meilleur BL : {bb['model']:<30} R²={bb['r2']:.4f}  MAE={bb['mae']:.4f}\n")
                f.write(f"  Meilleur DL : {bd['model']:<30} R²={bd['r2']:.4f}  MAE={bd['mae']:.4f}\n")
                f.write(f"  ΔR² (DL-BL) = {sign_r2}{delta_r2:.4f}  "
                        f"ΔMAE (BL-DL) = {sign_mae}{delta_mae:.4f}\n")
                if abs(delta_r2) < 0.02:
                    f.write("  → Performances SIMILAIRES → préférer Baseline ML (embarqué, <1ms)\n")
                elif delta_r2 > 0.02:
                    f.write(f"  → DL MEILLEUR (ΔR²={sign_r2}{delta_r2:.4f}) → justifie la complexité\n")
                else:
                    f.write("  → Baseline ML MEILLEUR → choisir Baseline\n")

        # Stratégie déploiement
        f.write(f"\n{'='*70}\n")
        f.write("STRATÉGIE DE DÉPLOIEMENT\n")
        f.write(f"{'='*70}\n\n")
        for target in TARGETS:
            bb = best_bl.get(target)
            bd = best_dl.get(target)
            bl_name = bb['model'] if bb is not None else '?'
            dl_name = bd['model'] if bd is not None else '?'
            f.write(f"[{target.upper()}]\n")
            f.write(f"  Phase 1 – Embarqué (ESP32/RPi) : {bl_name}  (<1ms, CPU only)\n")
            f.write(f"  Phase 2 – Application mobile   : {dl_name}  (GPU/NPU recommandé)\n")
            f.write(f"  Phase 3 – Personnalisation      : Fine-tuning EEGNet (Transfer Learning)\n\n")

        f.write("=" * 70 + "\n")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main(from_training: bool = False):
    print("=" * 75)
    print("NeuroCap – Comparaison Finale Régression (Baselines vs DL)")
    print("=" * 75)

    mode_str = "[mode: training JSON]" if from_training else "[mode: test CSVs]"
    print(f"\n{mode_str}")

    dfs: dict        = {}
    source_notes     = []
    all_frames_boxplot = {}

    for target in TARGETS:
        print(f"\n{'─'*65}")
        print(f"  TARGET : {target.upper()}")

        df, note = load_results_for_target(target, from_training)
        source_notes.append(f"{target}: {note}")

        if df is None or df.empty:
            print(f"  [SKIP] {note}")
            dfs[target] = None
            continue

        df = prepare_df(df)
        dfs[target] = df
        all_frames_boxplot[target] = df

        print(f"  {note}")
        print(f"  {len(df[df['category']=='Baseline ML'])} configs BL  "
              f"+ {len(df[df['category']=='Deep Learning'])} modèles DL")

        # ── Classement console ───────────────────────────────────────────────
        print(f"\n  CLASSEMENT {target.upper()} (top 10)")
        print(f"  {'Rang':>4}  {'Cat':>3}  {'Modèle':<30}  "
              f"{'MAE':>6}  {'R²':>7}  {'AUC':>6}  {'F1':>6}  {'Score':>7}")
        print("  " + "-" * 70)
        for rank, row in df.head(10).iterrows():
            cat    = 'BL' if row['category'] == 'Baseline ML' else 'DL'
            marker = " ★" if rank == 0 else "  "
            print(f"  {rank+1:>4}{marker} [{cat}]  {row['model']:<30}  "
                  f"{row['mae']:>6.3f}  {row['r2']:>7.3f}  "
                  f"{row['auc_roc']:>6.3f}  {row['f1_macro']:>6.3f}  "
                  f"{row['composite']:>7.4f}")

        best = df.iloc[0]
        print(f"\n  ★ VAINQUEUR {target.upper()} : {best['model']}  "
              f"[{best['category']}]  Score={best['composite']:.4f}")

        bl_sub = df[df['category'] == 'Baseline ML']
        dl_sub = df[df['category'] == 'Deep Learning']
        if not bl_sub.empty and not dl_sub.empty:
            delta = dl_sub.iloc[0]['r2'] - bl_sub.iloc[0]['r2']
            sign  = "+" if delta >= 0 else ""
            winner = "DL" if delta > 0.02 else ("BL" if delta < -0.02 else "Egal")
            print(f"    BL R²={bl_sub.iloc[0]['r2']:.4f}  "
                  f"DL R²={dl_sub.iloc[0]['r2']:.4f}  "
                  f"ΔR²={sign}{delta:.4f}  → {winner}")

        # ── CSV + graphiques ─────────────────────────────────────────────────
        csv_path = REPORT_DIR / f'unified_ranking_{target}.csv'
        df.to_csv(csv_path, index=False)

        plot_comparison_bars(df, target,
                             REPORT_DIR / f'comparison_bars_{target}.png')
        plot_scatter_r2_auc(df, target,
                            REPORT_DIR / f'scatter_r2_auc_{target}.png')

    # ── Boxplot global (tous targets) ─────────────────────────────────────────
    if all_frames_boxplot:
        plot_category_boxplot(all_frames_boxplot, REPORT_DIR / 'boxplot_categories.png')

    # ── Rapport final ─────────────────────────────────────────────────────────
    write_final_report(dfs, REPORT_DIR / 'FINAL_DECISION_REPORT.txt',
                       " | ".join(source_notes))

    # ── Résumé JSON ───────────────────────────────────────────────────────────
    summary = {}
    for target in TARGETS:
        df = dfs.get(target)
        if df is None or df.empty:
            continue
        bl = df[df['category'] == 'Baseline ML']
        dl = df[df['category'] == 'Deep Learning']
        summary[target] = {
            'winner':          df.iloc[0]['model'],
            'winner_category': df.iloc[0]['category'],
            'winner_r2':       df.iloc[0]['r2'],
            'winner_mae':      df.iloc[0]['mae'],
            'winner_score':    df.iloc[0]['composite'],
            'best_baseline':   bl.iloc[0]['model']    if not bl.empty else None,
            'best_baseline_r2':bl.iloc[0]['r2']       if not bl.empty else None,
            'best_dl':         dl.iloc[0]['model']    if not dl.empty else None,
            'best_dl_r2':      dl.iloc[0]['r2']       if not dl.empty else None,
            'n_models':        len(df),
        }
    with open(REPORT_DIR / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n{'='*75}")
    print(f"Sorties : {REPORT_DIR}")
    print(f"  • unified_ranking_conc.csv / unified_ranking_stress.csv")
    print(f"  • comparison_bars_conc.png / comparison_bars_stress.png")
    print(f"  • scatter_r2_auc_conc.png  / scatter_r2_auc_stress.png")
    print(f"  • boxplot_categories.png")
    print(f"  • FINAL_DECISION_REPORT.txt")
    print(f"  • summary.json")
    print(f"{'='*75}")


if __name__ == '__main__':
    from_training = '--from-training' in sys.argv
    main(from_training=from_training)
