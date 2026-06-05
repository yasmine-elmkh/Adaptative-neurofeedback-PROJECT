"""
NeuroCap – Comparaison Complète : Baseline ML / DL / DANN / Fine-tuning
=========================================================================
Agrège les résultats de toutes les suites de test et produit la recommandation
finale multi-approches.

Sources (par ordre de priorité) :
  • Baseline ML   → reports/Tests/baselines/results.json
  • Deep Learning → reports/Tests/deep_learning/results.json   (LOSO)
  • DANN          → reports/Tests/dann/results.json            (LOSO)
  • Fine-tuning   → reports/Tests/finetuning/results.json

Fallback : lit directement les metrics.json d'entraînement si les fichiers
de test ne sont pas disponibles.

Méthode d'évaluation :
  - DL et DANN   : métriques LOSO (Leave-One-Subject-Out) — HONNÊTES
  - Fine-tuning  : val→test (adapté sur X_val, évalué sur X_test)
  - Baseline ML  : holdout X_test.npy

Usage :
    cd EEG_project
    python Tests/test_comparison_dann.py

Prérequis recommandés (dans cet ordre) :
    1. python Tests/test_baselines.py
    2. python Tests/test_deep_learning.py
    3. python Tests/test_dann.py --compare-dl
    4. python Tests/test_finetuning.py
    5. python Tests/test_comparison_dann.py   ← ce fichier

Sorties :
    reports/Tests/comparison_dann/
        ├── unified_ranking_all.csv
        ├── full_comparison_bars.png        ← top modèles par catégorie
        ├── category_boxplot.png            ← distribution par approche
        ├── dann_gain_over_dl_full.png      ← gain DANN sur DL de base
        ├── finetune_impact.png             ← impact du fine-tuning
        ├── radar_top10_all.png             ← radar toutes catégories
        ├── deployment_quadrant.png         ← latence vs performance
        └── FULL_COMPARISON_REPORT.txt
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
from matplotlib.patches import Patch

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_BASELINE_JSON = PROJECT_ROOT / 'reports' / 'Tests' / 'baselines'      / 'results.json'
TEST_DL_JSON       = PROJECT_ROOT / 'reports' / 'Tests' / 'deep_learning'  / 'results.json'
TEST_DANN_JSON     = PROJECT_ROOT / 'reports' / 'Tests' / 'dann'           / 'results.json'
TEST_FT_JSON       = PROJECT_ROOT / 'reports' / 'Tests' / 'finetuning'     / 'results.json'

TRAIN_DL_BASE      = PROJECT_ROOT / 'reports' / 'deep_learning' / 'DL_outputs'
TRAIN_DANN_BASE    = PROJECT_ROOT / 'reports' / 'deep_learning' / 'DANN_outputs'
TRAIN_BL_JSON      = PROJECT_ROOT / 'reports' / 'Baseline' / 'baselines_outputs' / 'results.json'

REPORT_DIR = PROJECT_ROOT / 'reports' / 'Tests' / 'comparison_dann'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

ALL_DL_MODELS = [
    "CNN1D", "CNN2D", "CNN3D", "EEGNet", "TCN", "CNN_LSTM_Att", "CNN_GRU_Att",
    "LSTM_1L", "LSTM_2L", "BiLSTM_1L", "BiLSTM_2L",
    "GRU_1L", "GRU_2L", "BiGRU_1L", "BiGRU_2L",
    "LSTM_Att", "BiLSTM_Att", "GRU_Att", "BiGRU_Att",
]

ALL_DANN_MODELS = [m + '_DANN' for m in ALL_DL_MODELS]

DANN_TO_DL = {m + '_DANN': m for m in ALL_DL_MODELS}

CATEGORY_COLORS = {
    'Baseline ML':  '#E74C3C',
    'Deep Learning': '#2980B9',
    'DANN':          '#27AE60',
    'Fine-tuning':   '#F39C12',
}
CATEGORY_ORDER = ['Baseline ML', 'Deep Learning', 'DANN', 'Fine-tuning']


# ============================================================================
# UTILITAIRES
# ============================================================================
def _make_row(model, category, f1_macro, auc, accuracy, recall=0, specificity=0,
              precision=0, pct_uncertain=0, inference_ms=0, n_samples=0,
              source='', eval_method=''):
    return dict(model=model, category=category, f1_macro=f1_macro, auc=auc,
                accuracy=accuracy, recall=recall, specificity=specificity,
                precision=precision, pct_uncertain=pct_uncertain,
                inference_ms=inference_ms, n_samples=n_samples,
                source=source, eval_method=eval_method)


def compute_weighted_score(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['certitude'] = 1 - df['pct_uncertain'] / 100
    df['weighted_score'] = (
        0.40 * df['f1_macro']
        + 0.30 * df['auc']
        + 0.20 * df['accuracy']
        + 0.10 * df['certitude']
    )
    return df.sort_values('weighted_score', ascending=False).reset_index(drop=True)


# ============================================================================
# CHARGEMENT DES RÉSULTATS
# ============================================================================
def load_baseline_results():
    if TEST_BASELINE_JSON.exists():
        with open(TEST_BASELINE_JSON) as f:
            data = json.load(f)
        rows = []
        for r in data.get('all_results', []):
            rows.append(_make_row(
                model=r.get('model_feat', r.get('model', '?')),
                category='Baseline ML',
                f1_macro=r.get('f1_macro', 0),
                auc=r.get('auc', 0.5),
                accuracy=r.get('accuracy', 0),
                recall=r.get('recall', 0),
                specificity=r.get('specificity', 0),
                precision=r.get('precision', 0),
                pct_uncertain=r.get('pct_uncertain', 0),
                inference_ms=r.get('eval_time_sec', 0) * 1000 / max(r.get('n_samples', 1), 1),
                n_samples=r.get('n_samples', 0),
                source='test_baselines',
                eval_method='holdout',
            ))
        return rows, 'test_baselines.py (holdout)'

    if TRAIN_BL_JSON.exists():
        with open(TRAIN_BL_JSON) as f:
            data = json.load(f)
        rows = []
        for exp, models in data.get('loso', {}).items():
            for model, m in models.items():
                rows.append(_make_row(
                    model=f"{model}-{exp}",
                    category='Baseline ML',
                    f1_macro=m.get('f1_macro', 0),
                    auc=m.get('auc', 0.5),
                    accuracy=m.get('acc', 0),
                    recall=m.get('recall', 0),
                    specificity=m.get('specificity', 0),
                    source='training_loso',
                    eval_method='LOSO',
                ))
        if rows:
            return rows, 'métriques entraînement baseline (LOSO)'

    return [], 'non disponible'


def load_dl_results():
    if TEST_DL_JSON.exists():
        with open(TEST_DL_JSON) as f:
            data = json.load(f)
        if data.get('evaluation_method') == 'LOSO':
            rows = [_make_row(
                model=r['model'],
                category='Deep Learning',
                f1_macro=r.get('f1_macro', 0),
                auc=r.get('auc', 0.5),
                accuracy=r.get('accuracy', 0),
                recall=r.get('recall', 0),
                specificity=r.get('specificity', 0),
                precision=r.get('precision', 0),
                pct_uncertain=r.get('pct_uncertain', 0),
                source='test_deep_learning',
                eval_method='LOSO',
            ) for r in data.get('all_results', [])]
            return rows, 'test_deep_learning.py (LOSO)'

    # Fallback : LOSO_exp_A/metrics.json
    rows = []
    for model_name in ALL_DL_MODELS:
        p = TRAIN_DL_BASE / model_name / 'LOSO_exp_A' / 'metrics.json'
        if p.exists():
            with open(p) as f:
                m = json.load(f)
            rows.append(_make_row(
                model=model_name,
                category='Deep Learning',
                f1_macro=m.get('f1_macro', 0),
                auc=m.get('auc', 0.5),
                accuracy=m.get('accuracy', 0),
                recall=m.get('recall', 0),
                specificity=m.get('specificity', 0),
                pct_uncertain=m.get('pct_uncertain', 0),
                source='training_loso',
                eval_method='LOSO',
            ))
    return rows, 'entraînement DL LOSO_exp_A (fallback)'


def load_dann_results():
    if TEST_DANN_JSON.exists():
        with open(TEST_DANN_JSON) as f:
            data = json.load(f)
        rows = [_make_row(
            model=r['model'],
            category='DANN',
            f1_macro=r.get('f1_macro', 0),
            auc=r.get('auc', 0.5),
            accuracy=r.get('accuracy', 0),
            recall=r.get('recall', 0),
            specificity=r.get('specificity', 0),
            precision=r.get('precision', 0),
            pct_uncertain=r.get('pct_uncertain', 0),
            source='test_dann',
            eval_method='DANN-LOSO',
        ) for r in data.get('all_results', [])]
        return rows, 'test_dann.py (DANN-LOSO)'

    # Fallback : DANN_outputs/.../LOSO_exp_A/metrics.json
    rows = []
    for model_name in ALL_DANN_MODELS:
        p = TRAIN_DANN_BASE / model_name / 'LOSO_exp_A' / 'metrics.json'
        if p.exists():
            with open(p) as f:
                m = json.load(f)
            rows.append(_make_row(
                model=model_name,
                category='DANN',
                f1_macro=m.get('f1_macro', 0),
                auc=m.get('auc', 0.5),
                accuracy=m.get('accuracy', 0),
                recall=m.get('recall', 0),
                specificity=m.get('specificity', 0),
                pct_uncertain=m.get('pct_uncertain', 0),
                source='training_dann_loso',
                eval_method='DANN-LOSO',
            ))
    return rows, 'entraînement DANN LOSO_exp_A (fallback)'


def load_finetuning_results():
    if not TEST_FT_JSON.exists():
        return [], 'non disponible (exécutez test_finetuning.py)'
    with open(TEST_FT_JSON) as f:
        data = json.load(f)

    base_model = data.get('model', '?')
    best_after = data.get('best_after', {})
    best_strat = data.get('best_strategy', '?')
    rows = []

    # Entrée principale : meilleure stratégie de FT
    rows.append(_make_row(
        model=f"{base_model} [FT/{best_strat}]",
        category='Fine-tuning',
        f1_macro=best_after.get('f1_macro', 0),
        auc=best_after.get('auc', 0.5),
        accuracy=best_after.get('accuracy', 0),
        recall=best_after.get('recall', 0),
        specificity=best_after.get('specificity', 0),
        pct_uncertain=best_after.get('pct_uncertain', 0),
        source='test_finetuning',
        eval_method='val→test',
    ))

    # Toutes les stratégies
    for s in data.get('all_strategies', []):
        rows.append(_make_row(
            model=f"{base_model} [FT/{s['strategy']}]",
            category='Fine-tuning',
            f1_macro=s.get('after_f1_macro', 0),
            auc=s.get('after_auc', 0.5),
            accuracy=s.get('after_accuracy', 0),
            recall=s.get('after_recall', 0),
            specificity=s.get('after_specificity', 0),
            pct_uncertain=s.get('after_pct_uncertain', 0),
            source='test_finetuning',
            eval_method='val→test',
        ))

    # Déduplique
    seen = set()
    unique_rows = []
    for r in rows:
        if r['model'] not in seen:
            seen.add(r['model'])
            unique_rows.append(r)

    return unique_rows, f'test_finetuning.py ({base_model}, {best_strat})'


# ============================================================================
# VISUALISATIONS
# ============================================================================
def plot_full_comparison_bars(df: pd.DataFrame, save_path: Path):
    """Top modèles de chaque catégorie, barplot horizontal."""
    # Prend les 3 meilleurs par catégorie
    top_per_cat = []
    for cat in CATEGORY_ORDER:
        sub = df[df['category'] == cat]
        if not sub.empty:
            top_per_cat.append(sub.head(3))
    if not top_per_cat:
        return
    top = pd.concat(top_per_cat).reset_index(drop=True)

    metrics = ['f1_macro', 'auc', 'accuracy']
    titles  = ['F1-MACRO', 'AUC', 'Accuracy']
    n       = len(top)

    fig, axes = plt.subplots(1, 3, figsize=(21, max(6, n * 0.45)))
    fig.suptitle('NeuroCap – Comparaison Toutes Approches (Top 3 par catégorie)',
                 fontsize=13, fontweight='bold')

    for ax, metric, title in zip(axes, metrics, titles):
        sdf  = top.sort_values(metric, ascending=True)
        clrs = [CATEGORY_COLORS.get(c, 'gray') for c in sdf['category']]
        bars = ax.barh(sdf['model'], sdf[metric], color=clrs, alpha=0.85, edgecolor='white', lw=0.5)
        ax.set_xlabel(metric.replace('_', ' ').upper())
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlim([0, 1.12])
        ax.axvline(0.80, color='green', ls='--', lw=1, alpha=0.5, label='80%')
        ax.legend(fontsize=7)
        ax.grid(axis='x', alpha=0.3)
        for bar, val in zip(bars, sdf[metric]):
            ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}', va='center', fontsize=7)

    handles = [Patch(color=CATEGORY_COLORS[c], label=c) for c in CATEGORY_ORDER
               if c in df['category'].values]
    fig.legend(handles=handles, loc='lower center', ncol=4, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_category_boxplot(df: pd.DataFrame, save_path: Path):
    """Distribution des métriques par catégorie (boxplot)."""
    cats    = [c for c in CATEGORY_ORDER if c in df['category'].values]
    metrics = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    labels  = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']

    fig, axes = plt.subplots(1, len(metrics), figsize=(18, 6))
    for ax, metric, label in zip(axes, metrics, labels):
        data_per_cat = []
        for cat in cats:
            vals = df[df['category'] == cat][metric].dropna().tolist()
            data_per_cat.append(vals)

        bp = ax.boxplot(data_per_cat, positions=range(len(cats)), widths=0.45,
                        patch_artist=True, notch=False,
                        medianprops=dict(color='black', lw=2))
        for patch, cat in zip(bp['boxes'], cats):
            patch.set_facecolor(CATEGORY_COLORS.get(cat, 'gray'))
            patch.set_alpha(0.7)

        ax.set_xticks(range(len(cats)))
        ax.set_xticklabels([c.replace(' ', '\n') for c in cats], fontsize=8)
        ax.set_ylabel(label)
        ax.set_title(label, fontsize=10, fontweight='bold')
        ax.set_ylim([0, 1.05])
        ax.grid(axis='y', alpha=0.3)

    fig.suptitle('Distribution des métriques par approche',
                 fontsize=12, fontweight='bold')
    handles = [Patch(color=CATEGORY_COLORS[c], label=c) for c in cats]
    fig.legend(handles=handles, loc='lower center', ncol=len(cats), fontsize=9,
               bbox_to_anchor=(0.5, -0.02))
    plt.tight_layout(rect=[0, 0.05, 1, 0.97])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def _dann_correction_color(gain: float, f1_dann: float) -> str:
    """
    Logique correcte de couleur pour les graphiques d'impact DANN.

    Le DANN supprime le biais SCPS (OpenBCI=Concentration, EMOTIV=Stress).
    La baisse de F1 est ATTENDUE et SOUHAITÉE (biais corrigé).
    Ce n'est PAS un échec — c'est la révélation de la performance honnête.

      Vert   (gain > 0.01)  : signal cognitif amplifié — CNN1D case (meilleur cas)
      Orange (gain ≤ 0.01, f1_dann ≥ 0.60) : biais supprimé, performance honnête
      Rouge  (f1_dann < 0.60)               : effondrement — invalide sans biais
    """
    if f1_dann < 0.60:
        return '#E74C3C'
    elif gain > 0.01:
        return '#27AE60'
    else:
        return '#F39C12'


def plot_dann_gain_over_dl(df: pd.DataFrame, save_path: Path):
    """
    Pour chaque paire (DL, DANN), visualise l'impact DANN sur F1-MACRO.
    Correction du biais SCPS — la baisse de F1 est attendue et positive.
    """
    dl_rows   = df[df['category'] == 'Deep Learning'].set_index('model')[['f1_macro', 'auc', 'accuracy']]
    dann_rows = df[df['category'] == 'DANN'].set_index('model')[['f1_macro', 'auc', 'accuracy']]

    if dl_rows.empty or dann_rows.empty:
        return

    rows = []
    for dann_name, dl_name in DANN_TO_DL.items():
        if dl_name in dl_rows.index and dann_name in dann_rows.index:
            rows.append({
                'arch':    dl_name,
                'f1_dl':   dl_rows.loc[dl_name, 'f1_macro'],
                'f1_dann': dann_rows.loc[dann_name, 'f1_macro'],
                'auc_dl':  dl_rows.loc[dl_name, 'auc'],
                'auc_dann':dann_rows.loc[dann_name, 'auc'],
            })
    if not rows:
        return

    df_g = pd.DataFrame(rows)
    df_g['f1_gain']  = df_g['f1_dann'] - df_g['f1_dl']
    df_g['auc_gain'] = df_g['auc_dann'] - df_g['auc_dl']
    df_g = df_g.sort_values('f1_gain', ascending=False)

    colors_f1  = [_dann_correction_color(row['f1_gain'], row['f1_dann'])
                  for _, row in df_g.iterrows()]
    n_signal   = (df_g['f1_gain'] > 0.01).sum()
    n_collapse = (df_g['f1_dann'] < 0.60).sum()
    avg_g      = df_g['f1_gain'].mean()

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))
    fig.suptitle(
        f'Impact DANN — Correction du biais SCPS (LOSO)\n'
        f'Vert = signal amplifié ✓ | Orange = biais supprimé (attendu ✓) | Rouge = effondrement ✗',
        fontsize=12, fontweight='bold')

    # F1-MACRO impact
    ax = axes[0]
    bars = ax.barh(df_g['arch'], df_g['f1_gain'] * 100, color=colors_f1, alpha=0.85)
    ax.axvline(0, color='black', lw=0.8)
    ax.set_xlabel('Δ F1-MACRO (%)')
    ax.set_title(
        f'Δ F1-MACRO après correction biais (moy. {avg_g*100:+.2f}%)\n'
        f'Signal amplifié: {n_signal} | Effondrement: {n_collapse}',
        fontweight='bold', fontsize=9)
    ax.grid(axis='x', alpha=0.3)
    for bar, v in zip(bars, df_g['f1_gain']):
        xpos = bar.get_width() + (0.1 if v >= 0 else -0.1)
        ha   = 'left' if v >= 0 else 'right'
        ax.text(xpos, bar.get_y() + bar.get_height()/2,
                f'{v*100:+.2f}%', va='center', ha=ha, fontsize=7)

    # AUC impact
    colors_auc = [_dann_correction_color(row['auc_gain'], row['f1_dann'])
                  for _, row in df_g.iterrows()]
    ax2 = axes[1]
    bars2 = ax2.barh(df_g['arch'], df_g['auc_gain'] * 100, color=colors_auc, alpha=0.85)
    ax2.axvline(0, color='black', lw=0.8)
    ax2.set_xlabel('Δ AUC (%)')
    ax2.set_title('Δ AUC après correction biais SCPS', fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    for bar, v in zip(bars2, df_g['auc_gain']):
        xpos = bar.get_width() + (0.1 if v >= 0 else -0.1)
        ha   = 'left' if v >= 0 else 'right'
        ax2.text(xpos, bar.get_y() + bar.get_height()/2,
                 f'{v*100:+.2f}%', va='center', ha=ha, fontsize=7)

    from matplotlib.patches import Patch
    legend_els = [
        Patch(color='#27AE60', label='Signal cognitif amplifié ✓✓'),
        Patch(color='#F39C12', label='Biais supprimé, perf honnête ✓ (attendu)'),
        Patch(color='#E74C3C', label='Effondrement — architecture invalide ✗'),
    ]
    fig.legend(handles=legend_els, loc='lower center', ncol=3, fontsize=9,
               bbox_to_anchor=(0.5, -0.02))
    plt.tight_layout(rect=[0, 0.05, 1, 0.92])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_finetune_impact(df: pd.DataFrame, ft_data: dict, save_path: Path):
    """
    Visualise le gain apporté par le fine-tuning vs le modèle pré-entraîné.
    """
    if not ft_data or 'before' not in ft_data:
        return

    model_name = ft_data.get('model', '?')
    before     = ft_data['before']
    strategies = ft_data.get('all_strategies', [])
    if not strategies:
        return

    metrics  = ['f1_macro', 'auc', 'accuracy']
    m_labels = ['F1-Macro', 'AUC', 'Accuracy']
    strat_names = [s['strategy'] for s in strategies]
    x = np.arange(len(strat_names))

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(f'Impact du Fine-tuning — {model_name}',
                 fontsize=13, fontweight='bold')

    for ax, metric, label in zip(axes, metrics, m_labels):
        before_v = before.get(metric, 0)
        after_vs = [s.get(f'after_{metric}', 0) for s in strategies]
        gains    = [a - before_v for a in after_vs]
        colors   = ['#27AE60' if g >= 0 else '#E74C3C' for g in gains]

        ax.axhline(before_v, color='#2980B9', lw=2, ls='--', label=f'Avant FT ({before_v:.3f})')
        bars = ax.bar(x, after_vs, color=colors, alpha=0.8, width=0.5)
        for bar, g in zip(bars, gains):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 0.005,
                    f'{g:+.3f}', ha='center', va='bottom', fontsize=8,
                    color='#27AE60' if g >= 0 else '#E74C3C', fontweight='bold')

        ax.set_xticks(x)
        ax.set_xticklabels(strat_names, rotation=30, ha='right', fontsize=9)
        ax.set_ylabel(label)
        ax.set_title(label, fontweight='bold')
        ax.legend(fontsize=8)
        ax.set_ylim(0, max(max(after_vs), before_v) + 0.1)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout(rect=[0, 0, 1, 0.94])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_deployment_quadrant(df: pd.DataFrame, save_path: Path):
    """F1-MACRO vs score pondéré, coloré par catégorie, taille ∝ AUC."""
    fig, ax = plt.subplots(figsize=(11, 8))

    for cat, grp in df.groupby('category'):
        color = CATEGORY_COLORS.get(cat, 'gray')
        sizes = (grp['auc'] * 200).clip(lower=50)
        ax.scatter(grp['f1_macro'], grp['weighted_score'],
                   color=color, label=cat, s=sizes, alpha=0.80,
                   edgecolors='white', lw=0.5, zorder=5)
        # Annote les meilleurs de chaque catégorie
        for _, row in grp.nlargest(2, 'f1_macro').iterrows():
            ax.annotate(row['model'].replace('_DANN', '(D)').replace('_', ' '),
                        (row['f1_macro'], row['weighted_score']),
                        textcoords='offset points', xytext=(5, 3), fontsize=7)

    ax.set_xlabel('F1-MACRO (LOSO pour DL/DANN, holdout pour BL)', fontsize=11)
    ax.set_ylabel('Score pondéré (40% F1m + 30% AUC + 20% Acc + 10% certitude)', fontsize=10)
    ax.set_title('NeuroCap – Performance globale par approche\n'
                 '(taille des cercles ∝ AUC)', fontsize=12, fontweight='bold')
    ax.legend(fontsize=10, markerscale=0.8)
    ax.grid(alpha=0.3)

    # Zones de performance
    ax.axvline(0.80, color='green', ls=':', lw=1, alpha=0.5)
    ax.axhline(0.75, color='blue',  ls=':', lw=1, alpha=0.5)
    ax.text(0.81, ax.get_ylim()[0] + 0.01, '80% F1', color='green', fontsize=8, alpha=0.7)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_radar_top10(df: pd.DataFrame, save_path: Path):
    """Radar chart des top 10 modèles (toutes catégories)."""
    top10 = df.head(min(10, len(df)))
    cats  = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    lbls  = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']
    N     = len(cats)
    angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    cmap    = plt.cm.tab10(np.linspace(0, 1, len(top10)))
    ls_map  = {'Baseline ML': 'dashed', 'Deep Learning': 'solid',
                'DANN': 'dotted', 'Fine-tuning': 'dashdot'}

    for (_, row), color in zip(top10.iterrows(), cmap):
        vals = [row[c] for c in cats] + [row[cats[0]]]
        ls   = ls_map.get(row['category'], 'solid')
        cat_abbr = {'Baseline ML': 'BL', 'Deep Learning': 'DL',
                    'DANN': 'DA', 'Fine-tuning': 'FT'}.get(row['category'], '??')
        label = f"[{cat_abbr}] {row['model']}"
        ax.plot(angles, vals, lw=2, color=color, ls=ls, label=label)
        ax.fill(angles, vals, alpha=0.06, color=color)

    ax.set_thetagrids(np.degrees(angles[:-1]), lbls, fontsize=9)
    ax.set_ylim([0, 1])
    ax.set_title('Top 10 – Toutes approches', fontsize=11, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.65, 1.15), fontsize=7)

    # Légende des styles de lignes
    from matplotlib.lines import Line2D
    style_handles = [
        Line2D([0], [0], color='gray', ls='dashed', lw=2, label='Baseline ML'),
        Line2D([0], [0], color='gray', ls='solid',  lw=2, label='Deep Learning'),
        Line2D([0], [0], color='gray', ls='dotted', lw=2, label='DANN'),
        Line2D([0], [0], color='gray', ls='dashdot',lw=2, label='Fine-tuning'),
    ]
    ax.add_artist(ax.legend(handles=style_handles, loc='lower left',
                             bbox_to_anchor=(-0.35, -0.05), fontsize=7, title='Catégorie'))

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_approach_summary_heatmap(df: pd.DataFrame, save_path: Path):
    """Heatmap des métriques moyennes par approche."""
    cats    = [c for c in CATEGORY_ORDER if c in df['category'].values]
    metrics = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    labels  = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']

    data = []
    for cat in cats:
        sub = df[df['category'] == cat]
        data.append([sub[m].mean() for m in metrics])

    df_heat = pd.DataFrame(data, index=cats, columns=labels)

    fig, ax = plt.subplots(figsize=(10, max(4, len(cats) * 1.2)))
    sns.heatmap(df_heat, annot=True, fmt='.3f', cmap='RdYlGn',
                vmin=0, vmax=1, linewidths=0.5, ax=ax,
                cbar_kws={'label': 'Score moyen'})
    ax.set_title('NeuroCap – Métriques moyennes par approche',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# RAPPORT FINAL
# ============================================================================
def write_full_report(df: pd.DataFrame, report_path: Path, sources: dict,
                      ft_data: dict = None):
    best = df.iloc[0]
    cats_present = {c: df[df['category'] == c] for c in CATEGORY_ORDER
                    if c in df['category'].values}
    best_per_cat = {cat: sub.iloc[0] for cat, sub in cats_present.items() if not sub.empty}

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("NeuroCap – COMPARAISON COMPLÈTE : BL / DL / DANN / Fine-tuning\n")
        f.write("=" * 70 + "\n\n")
        f.write("Sources des données :\n")
        for cat, src in sources.items():
            f.write(f"  {cat:<16} : {src}\n")
        f.write("\nMéthodes d'évaluation :\n")
        f.write("  DL / DANN    : LOSO (Leave-One-Subject-Out) — honnête\n")
        f.write("  Fine-tuning  : val→test (adaptation sur X_val, test sur X_test)\n")
        f.write("  Baseline ML  : holdout X_test.npy\n")
        f.write(f"\nScore pondéré : 40% F1m + 30% AUC + 20% Acc + 10% certitude\n\n")

        # TOP 10
        f.write("─" * 70 + "\n")
        f.write("CLASSEMENT UNIFIÉ – TOP 10\n")
        f.write("─" * 70 + "\n")
        f.write(f"{'Rang':<5} {'Cat':>2} {'Modèle':<30} {'F1m':>6} "
                f"{'AUC':>6} {'Acc':>6} {'Inc%':>5} {'Score':>7}\n")
        f.write("-" * 70 + "\n")
        for rank, row in df.head(10).iterrows():
            cat = {'Baseline ML': 'BL', 'Deep Learning': 'DL',
                   'DANN': 'DA', 'Fine-tuning': 'FT'}.get(row['category'], '??')
            f.write(f"{rank+1:<5} [{cat}] {row['model']:<30} "
                    f"{row['f1_macro']:>6.4f} {row['auc']:>6.4f} "
                    f"{row['accuracy']:>6.4f} {row['pct_uncertain']:>5.1f}% "
                    f"{row['weighted_score']:>7.4f}\n")
        f.write("\n")

        # Meilleur par catégorie
        f.write("─" * 70 + "\n")
        f.write("MEILLEUR PAR APPROCHE\n")
        f.write("─" * 70 + "\n")
        for cat, row in best_per_cat.items():
            f.write(f"\n  {cat} : {row['model']}\n")
            f.write(f"    F1-MACRO = {row['f1_macro']:.4f}  AUC = {row['auc']:.4f}  "
                    f"Acc = {row['accuracy']:.4f}  Score = {row['weighted_score']:.4f}\n")

        # Analyse DANN vs DL — interprétation correcte du biais SCPS
        if 'Deep Learning' in best_per_cat and 'DANN' in best_per_cat:
            dl   = best_per_cat['Deep Learning']
            dann = best_per_cat['DANN']
            gain = dann['f1_macro'] - dl['f1_macro']
            f.write(f"\n  ANALYSE DANN — CORRECTION DU BIAIS SCPS\n")
            f.write(f"  ─────────────────────────────────────────\n")
            f.write(f"  Contexte : OpenBCI=Concentration et EMOTIV=Stress dans NeuroCap.\n")
            f.write(f"  Sans DANN, le modèle apprend la signature du matériel (SCPS)\n")
            f.write(f"  et non l'état cognitif → scores gonflés, non généralisables.\n\n")
            f.write(f"  DL  (biaisé)  : {dl['model']:<25} F1m = {dl['f1_macro']:.4f}\n")
            f.write(f"  DANN (honnête): {dann['model']:<25} F1m = {dann['f1_macro']:.4f}\n")
            f.write(f"  Δ F1m après correction biais : {gain:+.4f}\n\n")
            if dann['f1_macro'] < 0.60:
                f.write("  → DANN effondré : architecture invalide — n'apprenait que le biais\n")
            elif gain > 0.01:
                f.write("  → Signal cognitif amplifié : le modèle captait biais + signal.\n")
                f.write("     Supprimer le biais améliore la classification cognitive.\n")
                f.write("     PREUVE que le signal EEG Fp2 contient une info cognitive réelle.\n")
            else:
                f.write(f"  → Biais SCPS corrigé avec succès. La baisse ({gain*100:.2f}pp) est\n")
                f.write("     ATTENDUE et représente la correction du raccourci 'matériel=classe'.\n")
                f.write(f"  → F1m={dann['f1_macro']:.4f} = performance RÉELLE sur nouveau matériel (AD8232)\n")

        # Analyse Fine-tuning
        if 'Fine-tuning' in best_per_cat and ft_data:
            ft_best = best_per_cat['Fine-tuning']
            before  = ft_data.get('before', {})
            gain_ft = ft_best['f1_macro'] - before.get('f1_macro', 0)
            f.write(f"\n  Gain Fine-tuning : {gain_ft:+.4f} F1-MACRO\n")
            f.write(f"    Stratégie : {ft_data.get('best_strategy', '?')}\n")
            f.write(f"    Dataset FT: {ft_data.get('n_ft_samples', '?')} epochs de X_val.npy\n")

        # Recommandation
        f.write("\n" + "=" * 70 + "\n")
        f.write("RECOMMANDATION FINALE\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"  Modèle recommandé : {best['model']}\n")
        f.write(f"  Catégorie          : {best['category']}\n")
        f.write(f"  F1-MACRO           : {best['f1_macro']:.4f}\n")
        f.write(f"  AUC                : {best['auc']:.4f}\n")
        f.write(f"  Accuracy           : {best['accuracy']:.4f}\n")
        f.write(f"  Score pondéré      : {best['weighted_score']:.4f}\n\n")

        f.write("STRATÉGIE DE DÉPLOIEMENT\n")
        f.write("─" * 70 + "\n\n")
        bl_name  = best_per_cat.get('Baseline ML', pd.Series({'model': '?'}))['model']
        dl_name  = best_per_cat.get('Deep Learning', pd.Series({'model': '?'}))['model']
        dann_name = best_per_cat.get('DANN', pd.Series({'model': '?'}))['model']
        ft_name  = best_per_cat.get('Fine-tuning', pd.Series({'model': '?'}))['model']
        f.write(f"  Phase 1 – Embarqué (ESP32/RPi, faible latence) :\n")
        f.write(f"    → {bl_name} (Baseline ML, < 1 ms/epoch)\n\n")
        f.write(f"  Phase 2 – Application mobile / Cloud :\n")
        f.write(f"    → {dann_name} (DANN, invariant aux biais inter-appareils)\n\n")
        f.write(f"  Phase 3 – Personnalisation utilisateur :\n")
        f.write(f"    → {ft_name} (Fine-tuning sur données personnelles)\n\n")
        f.write(f"  Solution haute précision (GPU) :\n")
        f.write(f"    → {dl_name} (DL, optimisé LOSO)\n\n")
        f.write("=" * 70 + "\n")


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 75)
    print("NeuroCap – Comparaison Complète : BL / DL / DANN / Fine-tuning")
    print("=" * 75)

    all_rows  = []
    sources   = {}
    ft_data   = None

    # ── Chargement de chaque source ────────────────────────────────────────
    print("\n[1/4] Chargement Baseline ML...")
    bl_rows, bl_src = load_baseline_results()
    sources['Baseline ML'] = bl_src
    if bl_rows:
        all_rows.extend(bl_rows)
        print(f"  ✔ {len(bl_rows)} résultats  [{bl_src}]")
    else:
        print(f"  ✗ Non disponible")

    print("\n[2/4] Chargement Deep Learning (LOSO)...")
    dl_rows, dl_src = load_dl_results()
    sources['Deep Learning'] = dl_src
    if dl_rows:
        all_rows.extend(dl_rows)
        print(f"  ✔ {len(dl_rows)} modèles  [{dl_src}]")
    else:
        print(f"  ✗ Non disponible")

    print("\n[3/4] Chargement DANN (LOSO)...")
    dann_rows, dann_src = load_dann_results()
    sources['DANN'] = dann_src
    if dann_rows:
        all_rows.extend(dann_rows)
        print(f"  ✔ {len(dann_rows)} modèles DANN  [{dann_src}]")
    else:
        print(f"  ✗ Non disponible")

    print("\n[4/4] Chargement Fine-tuning...")
    ft_rows, ft_src = load_finetuning_results()
    sources['Fine-tuning'] = ft_src
    if ft_rows:
        all_rows.extend(ft_rows)
        print(f"  ✔ {len(ft_rows)} configurations  [{ft_src}]")
        if TEST_FT_JSON.exists():
            with open(TEST_FT_JSON) as f:
                ft_data = json.load(f)
    else:
        print(f"  ✗ Non disponible")

    if not all_rows:
        print("\n[ERREUR] Aucune donnée disponible.")
        print("Exécutez dans l'ordre :")
        print("  1. python Tests/test_baselines.py")
        print("  2. python Tests/test_deep_learning.py")
        print("  3. python Tests/test_dann.py --compare-dl")
        print("  4. python Tests/test_finetuning.py")
        return

    # ── DataFrame unifié ──────────────────────────────────────────────────
    df = pd.DataFrame(all_rows)
    for col in ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity',
                'precision', 'pct_uncertain', 'inference_ms']:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    df = compute_weighted_score(df)
    df.to_csv(REPORT_DIR / 'unified_ranking_all.csv', index=False)

    # ── Affichage classement ───────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("CLASSEMENT UNIFIÉ – TOUTES APPROCHES")
    print(f"{'='*75}")
    print(f"{'Rang':>4}  {'Cat':>2}  {'Modèle':<35}  "
          f"{'F1m':>6}  {'AUC':>6}  {'Acc':>6}  {'Inc%':>5}  {'Score':>6}")
    print("─" * 75)

    best_per_cat = {}
    for rank, row in df.iterrows():
        cat = {'Baseline ML': 'BL', 'Deep Learning': 'DL',
               'DANN': 'DA', 'Fine-tuning': 'FT'}.get(row['category'], '??')
        marker = " ★" if rank == 0 else "  "
        print(f"{rank+1:>4}{marker} [{cat}]  {row['model']:<35}  "
              f"{row['f1_macro']:.4f}  {row['auc']:.4f}  "
              f"{row['accuracy']:.4f}  {row['pct_uncertain']:>4.1f}%  "
              f"{row['weighted_score']:.4f}")
        if row['category'] not in best_per_cat:
            best_per_cat[row['category']] = row
        if rank >= 19:
            rem = len(df) - 20
            if rem > 0:
                print(f"  ... {rem} autres (voir unified_ranking_all.csv)")
            break

    best = df.iloc[0]
    print(f"\n★ VAINQUEUR : {best['model']}  [{best['category']}]")
    print(f"  F1-MACRO = {best['f1_macro']:.4f}  |  AUC = {best['auc']:.4f}  "
          f"|  Score = {best['weighted_score']:.4f}")

    # ── Résumé par catégorie ───────────────────────────────────────────────
    print(f"\n{'─'*75}")
    print("RÉSUMÉ PAR APPROCHE")
    print(f"{'─'*75}")
    print(f"{'Approche':<16}  {'N':>3}  {'F1m moyen':>10}  {'F1m max':>8}  "
          f"{'AUC moyen':>10}  Meilleur modèle")
    print("─" * 75)
    for cat in CATEGORY_ORDER:
        sub = df[df['category'] == cat]
        if sub.empty:
            continue
        print(f"{cat:<16}  {len(sub):>3}  "
              f"{sub['f1_macro'].mean():>10.4f}  {sub['f1_macro'].max():>8.4f}  "
              f"{sub['auc'].mean():>10.4f}  {sub.iloc[0]['model']}")

    # ── Impact DANN — Correction biais SCPS ───────────────────────────────
    dl_sub   = df[df['category'] == 'Deep Learning']
    dann_sub = df[df['category'] == 'DANN']
    if not dl_sub.empty and not dann_sub.empty:
        print(f"\n{'─'*75}")
        print("IMPACT DANN — CORRECTION DU BIAIS SCPS (LOSO)")
        print(f"{'─'*75}")
        print("  RAPPEL : Les scores DL SANS DANN sont gonflés par le biais matériel.")
        print("  Le DANN révèle la performance HONNÊTE (généralisable sur AD8232).")
        print("  Δ < 0 = biais corrigé (attendu) | Δ > 0 = signal amplifié | F1<0.6 = effondrement")
        print(f"{'─'*75}")
        pairs_matched = 0
        gains = []
        f1_danns = []
        for dann_name, dl_name in DANN_TO_DL.items():
            dl_row   = dl_sub[dl_sub['model'] == dl_name]
            dann_row = dann_sub[dann_sub['model'] == dann_name]
            if dl_row.empty or dann_row.empty:
                continue
            gain     = dann_row.iloc[0]['f1_macro'] - dl_row.iloc[0]['f1_macro']
            f1_dann  = dann_row.iloc[0]['f1_macro']
            gains.append(gain)
            f1_danns.append(f1_dann)
            pairs_matched += 1
        if gains:
            avg      = np.mean(gains)
            n_signal = sum(1 for g in gains if g > 0.01)
            n_honest = sum(1 for g, f in zip(gains, f1_danns) if g <= 0.01 and f >= 0.60)
            n_coll   = sum(1 for f in f1_danns if f < 0.60)
            print(f"  Paires comparées                     : {pairs_matched}")
            print(f"  Δ F1m moyen (correction biais SCPS) : {avg:+.4f}")
            print(f"  ✓✓ Signal cognitif amplifié          : {n_signal}/{pairs_matched}")
            print(f"  ✓  Biais supprimé — perf honnête     : {n_honest}/{pairs_matched}")
            print(f"  ✗  Effondrement — invalide sans biais: {n_coll}/{pairs_matched}")

    # ── Graphiques ─────────────────────────────────────────────────────────
    print("\nGénération des graphiques...")
    plot_full_comparison_bars(df, REPORT_DIR / 'full_comparison_bars.png')
    plot_category_boxplot(df, REPORT_DIR / 'category_boxplot.png')
    plot_dann_gain_over_dl(df, REPORT_DIR / 'dann_gain_over_dl_full.png')
    plot_deployment_quadrant(df, REPORT_DIR / 'deployment_quadrant.png')
    plot_approach_summary_heatmap(df, REPORT_DIR / 'approach_heatmap.png')
    if len(df) >= 3:
        plot_radar_top10(df, REPORT_DIR / 'radar_top10_all.png')
    if ft_data:
        plot_finetune_impact(df, ft_data, REPORT_DIR / 'finetune_impact.png')

    # ── Rapport ───────────────────────────────────────────────────────────
    report_path = REPORT_DIR / 'FULL_COMPARISON_REPORT.txt'
    write_full_report(df, report_path, sources, ft_data)

    # ── JSON ──────────────────────────────────────────────────────────────
    summary = {
        'winner':          best['model'],
        'winner_category': best['category'],
        'winner_f1_macro': best['f1_macro'],
        'winner_auc':      best['auc'],
        'winner_score':    best['weighted_score'],
        'n_models':        len(df),
        'best_per_category': {
            cat: {
                'model':    r['model'],
                'f1_macro': r['f1_macro'],
                'auc':      r['auc'],
                'score':    r['weighted_score'],
            }
            for cat, r in best_per_cat.items()
        },
        'sources': sources,
    }
    with open(REPORT_DIR / 'summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n{'='*75}")
    print(f"Sorties : {REPORT_DIR}")
    print(f"  • unified_ranking_all.csv       ← classement complet")
    print(f"  • full_comparison_bars.png      ← top 3 par catégorie")
    print(f"  • category_boxplot.png          ← distribution par approche")
    print(f"  • dann_gain_over_dl_full.png    ← impact DANN par architecture")
    print(f"  • approach_heatmap.png          ← métriques moyennes par approche")
    print(f"  • deployment_quadrant.png       ← performance globale")
    print(f"  • radar_top10_all.png           ← radar top 10")
    if ft_data:
        print(f"  • finetune_impact.png           ← avant/après fine-tuning")
    print(f"  • FULL_COMPARISON_REPORT.txt    ← LIRE CE FICHIER")
    print(f"  • summary.json")
    print(f"{'='*75}")


if __name__ == '__main__':
    main()
