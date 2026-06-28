"""
=============================================================================
NeuroCap — Comparaison SMOTE : 4 approches (Régression)
compare_regression_smote.py
=============================================================================
Compare les 4 approches issues des 4 scripts de régression :

  feat15        baseline_ML_regression.py
  feat15_smote  baseline_ML_regression_smote.py
  feat78        baseline_ML_regression_feature_eng.py
  feat78_smote  baseline_ML_regression_feature_eng_smote.py

FOCUS : impact SMOTE + sample_weight + Youden sur les métriques
        d'imbalance (Sensitivity, Specificity, MCC, AUC) tout en
        vérifiant que MAE/R² ne se dégradent pas.

RÉFÉRENCES :
  [1] Chawla et al. (2002) SMOTE  — JAIR 16:321-357
  [2] He & Garcia (2009)          — IEEE TKDE 21(9)
  [3] Youden (1950)               — Cancer 3(1):32-35
  [4] Chicco & Jurman (2020) MCC  — BMC Genomics 21:6

SORTIES :
  reports/Regression/Comparison_SMOTE/{conc,stress}/
    figures/
      01_sensitivity_4way.png     ← PRINCIPAL : impact SMOTE sur Sensitivity
      02_specificity_4way.png
      03_mcc_4way.png
      04_auc_4way.png
      05_delta_smote_heatmap.png  ← ΔSMOTE = SMOTE − baseline (Sens/MCC/AUC)
      06_mae_r2_impact.png        ← SMOTE ne dégrade pas la régression ?
      07_youden_vs_std5.png       ← comparaison seuil Youden vs seuil fixe 5.0
      08_ece_4way.png
      09_radar_full.png
      10_summary_table.png
      00_global_overview.png    ← DASHBOARD GLOBAL (toutes métriques clés)
    comparison_table_{target}.csv
    comparison_summary_{target}.txt
=============================================================================
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')

# ─── Chemins ─────────────────────────────────────────────────────────────────
PROJECT_ROOT       = Path(__file__).resolve().parents[3]
BASE_ROOT          = PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline'
FEAT15_ROOT        = BASE_ROOT / 'feat15'
FEAT15_SMOTE_ROOT  = BASE_ROOT / 'feat15_smote'
FEAT78_ROOT        = BASE_ROOT / 'feat78'
FEAT78_SMOTE_ROOT  = BASE_ROOT / 'feat78_smote'
OUT_ROOT           = PROJECT_ROOT / 'reports' / 'Regression' /  "Baseline" / 'Comparison_SMOTE'

EXPERIMENTS = ['A', 'B', 'C', 'D', 'FULL']
MODEL_NAMES = ['SVR', 'Random Forest', 'XGBoost', 'LightGBM', 'Stacking']
TARGETS     = ['conc', 'stress']

# ─── Couleurs des 4 approches ─────────────────────────────────────────────────
APPROACH_KEYS   = ['feat15', 'feat15_smote', 'feat78', 'feat78_smote']
APPROACH_LABELS = {
    'feat15':       'Baseline (15f)',
    'feat15_smote': 'SMOTE (15f)',
    'feat78':       'FeatEng (78f)',
    'feat78_smote': 'SMOTE+Youden (78f)',
}
APPROACH_COLORS = {
    'feat15':       '#AED6F1',
    'feat15_smote': '#1A5276',
    'feat78':       '#A9DFBF',
    'feat78_smote': '#1E8449',
}
APPROACH_HATCH = {
    'feat15':       '//',
    'feat15_smote': '',
    'feat78':       '//',
    'feat78_smote': '',
}

MODEL_COLORS = {
    'SVR':           '#E74C3C',
    'Random Forest': '#2980B9',
    'XGBoost':       '#27AE60',
    'LightGBM':      '#F39C12',
    'Stacking':      '#8E44AD',
}
EXP_LABEL = {'A': 'A\n(×1)', 'B': 'B\n(×2)', 'C': 'C\n(×3)',
             'D': 'D\n(×2)', 'FULL': 'FULL\n(×4)'}

SMOTE_PAIRS = [('feat15', 'feat15_smote'), ('feat78', 'feat78_smote')]


# ─────────────────────────────────────────────────────────────────────────────
# CHARGEMENT
# ─────────────────────────────────────────────────────────────────────────────
def load_json(path: Path, label: str) -> dict | None:
    if not path.exists():
        print(f"  [SKIP] {label:40s} → {path.name} introuvable")
        return None
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  OK  {label:40s} → {path.relative_to(PROJECT_ROOT)}")
    return data


def extract_metrics(json_data: dict) -> dict:
    """
    JSON → dict {exp: {model: {metric: val}}}.
    Gère les 2 formats : baseline (sans _std5) et smote (avec _std5/youden).
    """
    raw = json_data.get('loso', json_data)
    out = {}
    for exp, models in raw.items():
        if exp not in EXPERIMENTS:
            continue
        out[exp] = {}
        for mn, m in models.items():
            if mn.startswith('_'):
                continue
            prof = m.get('professional', {})
            bci  = prof.get('bootstrap_ci', {})
            perm = prof.get('permutation', {})
            cal  = prof.get('calibration', {})
            ba   = prof.get('bland_altman', {})
            ic   = prof.get('icc', {})

            entry = {
                # Métriques de régression
                'mae':          float(m.get('mae',  999.)),
                'rmse':         float(m.get('rmse', 999.)),
                'r2':           float(m.get('r2',   -99.)),
                # Métriques d'imbalance — seuil Youden (ou fixe=5.0 si pas de smote)
                'auc':          float(m.get('auc_roc',     0.)),
                'sensitivity':  float(m.get('sensitivity', 0.)),
                'specificity':  float(m.get('specificity', 0.)),
                'mcc':          float(m.get('mcc',         0.)),
                'balanced_acc': float(m.get('balanced_accuracy', 0.)),
                'pr_auc':       float(m.get('pr_auc',      0.)),
                'f1_macro':     float(m.get('f1_macro',    0.)),
                'f1_weighted':  float(m.get('f1_weighted', 0.)),
                'accuracy':     float(m.get('accuracy',    0.)),
                # Métriques seuil fixe=5.0 (présentes dans les versions _smote)
                'auc_std5':     float(m.get('auc_roc_std5',     m.get('auc_roc', 0.))),
                'sens_std5':    float(m.get('sensitivity_std5', m.get('sensitivity', 0.))),
                'spec_std5':    float(m.get('specificity_std5', m.get('specificity', 0.))),
                'mcc_std5':     float(m.get('mcc_std5',         m.get('mcc', 0.))),
                # Seuil Youden
                'youden_mean':  float(m.get('youden_mean', 5.0)),
                'youden_std':   float(m.get('youden_std',  0.0)),
                'smote_folds':  int(m.get('smote_folds', 0)),
                # Niveaux 2-5
                'auc_ci_lo':    float(bci.get('auc_roc', {}).get('ci_lo', 0.)),
                'auc_ci_hi':    float(bci.get('auc_roc', {}).get('ci_hi', 0.)),
                'r2_ci_lo':     float(bci.get('r2',      {}).get('ci_lo', 0.)),
                'r2_ci_hi':     float(bci.get('r2',      {}).get('ci_hi', 0.)),
                'auc_pvalue':   float(perm.get('auc_roc', {}).get('p_value', 1.)),
                'ece':          float(cal.get('ece',    0.)),
                'bland_bias':   float(ba.get('bias',    0.)),
                'icc':          float(ic.get('icc',     0.)),
            }
            out[exp][mn] = entry
    return out


# ─────────────────────────────────────────────────────────────────────────────
# BUILD DATAFRAME UNIFIÉ (4 approches)
# ─────────────────────────────────────────────────────────────────────────────
def build_dataframe(all_metrics: dict[str, dict]) -> pd.DataFrame:
    rows = []
    for ak, metrics in all_metrics.items():
        if metrics is None:
            continue
        label = APPROACH_LABELS[ak]
        for exp, models in metrics.items():
            for mn, m in models.items():
                rows.append({
                    'Approach':    label,
                    'ApproachKey': ak,
                    'Experiment':  exp,
                    'Model':       mn,
                    'MAE':         m['mae'],
                    'RMSE':        m['rmse'],
                    'R2':          m['r2'],
                    'AUC':         m['auc'],
                    'Sensitivity': m['sensitivity'],
                    'Specificity': m['specificity'],
                    'MCC':         m['mcc'],
                    'Balanced_Acc':m['balanced_acc'],
                    'PR_AUC':      m['pr_auc'],
                    'F1_macro':    m['f1_macro'],
                    'F1_weighted': m['f1_weighted'],
                    'Accuracy':    m['accuracy'],
                    'AUC_std5':    m['auc_std5'],
                    'Sens_std5':   m['sens_std5'],
                    'Spec_std5':   m['spec_std5'],
                    'MCC_std5':    m['mcc_std5'],
                    'Youden_mean': m['youden_mean'],
                    'Youden_std':  m['youden_std'],
                    'SMOTE_folds': m['smote_folds'],
                    'AUC_CI_LO':   m['auc_ci_lo'],
                    'AUC_CI_HI':   m['auc_ci_hi'],
                    'AUC_Pvalue':  m['auc_pvalue'],
                    'ECE':         m['ece'],
                    'Bland_Bias':  m['bland_bias'],
                    'ICC':         m['icc'],
                })
    df = pd.DataFrame(rows)

    # Δ SMOTE : SMOTE − baseline pour chaque paire
    for base_key, smote_key in SMOTE_PAIRS:
        sfx_b = base_key.replace('feat', 'f').replace('_smote', '')
        sfx_s = smote_key.replace('feat', 'f')
        for metric in ['Sensitivity', 'Specificity', 'MCC', 'AUC', 'R2', 'MAE',
                        'F1_macro', 'F1_weighted', 'Balanced_Acc', 'PR_AUC']:
            if base_key not in df['ApproachKey'].values or smote_key not in df['ApproachKey'].values:
                continue
            b_df = df[df['ApproachKey'] == base_key ][['Experiment', 'Model', metric]]
            s_df = df[df['ApproachKey'] == smote_key][['Experiment', 'Model', metric]]
            mg = s_df.merge(b_df, on=['Experiment', 'Model'], suffixes=('_s', '_b'))
            sign = -1. if metric == 'MAE' else 1.
            mg[f'Delta_{metric}_{sfx_s}'] = sign * (mg[f'{metric}_s'] - mg[f'{metric}_b'])
            df = df.merge(mg[['Experiment', 'Model', f'Delta_{metric}_{sfx_s}']],
                          on=['Experiment', 'Model'], how='left')
    return df


# ─────────────────────────────────────────────────────────────────────────────
# HELPER : barplot 4 approches pour une métrique
# ─────────────────────────────────────────────────────────────────────────────
def plot_4way_barplot(df, metric, title, filename, figures_dir, ylim=(0, 1.15)):
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]
    avail  = [ak for ak in APPROACH_KEYS if ak in df['ApproachKey'].unique()]
    n_exp  = len(exps)
    n_appr = len(avail)
    bar_w  = 0.8 / n_appr

    fig, axes = plt.subplots(1, n_exp, figsize=(3.5 * n_exp, 5.5), sharey=True)
    if n_exp == 1:
        axes = [axes]

    for ax, exp in zip(axes, exps):
        x = np.arange(len(models))
        for i, ak in enumerate(avail):
            vals = []
            for mn in models:
                row = df[(df['ApproachKey'] == ak) &
                         (df['Experiment']  == exp) &
                         (df['Model']       == mn)]
                vals.append(float(row[metric].values[0]) if len(row) > 0 else 0.)
            offset = (i - (n_appr - 1) / 2) * bar_w
            bars   = ax.bar(x + offset, vals, bar_w,
                            color=APPROACH_COLORS[ak],
                            hatch=APPROACH_HATCH[ak],
                            edgecolor='white', alpha=0.9,
                            label=APPROACH_LABELS[ak] if exp == exps[0] else '_nolegend_')
            for bar, val in zip(bars, vals):
                if abs(val) > 0.01:
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.01,
                            f'{val:.2f}', ha='center', va='bottom',
                            fontsize=5.5, rotation=55)
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=40, ha='right', fontsize=7)
        ax.set_title(EXP_LABEL.get(exp, exp), fontsize=10, fontweight='bold')
        ax.set_ylabel(metric if ax == axes[0] else '')
        ax.axhline(0.5, color='gray', lw=1, ls='--', alpha=0.5)
        ax.set_ylim(ylim)
        ax.grid(axis='y', alpha=0.3)

    handles = [mpatches.Patch(color=APPROACH_COLORS[ak],
                               hatch=APPROACH_HATCH[ak],
                               label=APPROACH_LABELS[ak])
               for ak in avail]
    fig.legend(handles=handles, loc='upper center', ncol=len(avail),
               bbox_to_anchor=(0.5, 1.04), fontsize=9)
    fig.suptitle(title, fontsize=12, fontweight='bold', y=1.08)
    plt.tight_layout()
    plt.savefig(str(figures_dir / filename), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  OK  {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 5 — Heatmap ΔSMOTE (par paire base/smote, par métrique)
# ─────────────────────────────────────────────────────────────────────────────
def plot_delta_smote_heatmap(df, figures_dir):
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]

    pairs  = [(ak_b, ak_s) for ak_b, ak_s in SMOTE_PAIRS
              if ak_b in df['ApproachKey'].unique() and ak_s in df['ApproachKey'].unique()]
    if not pairs:
        print("  [SKIP] 05_delta_smote_heatmap.png — pas de paire baseline+SMOTE")
        return

    metrics_plot = ['Sensitivity', 'Specificity', 'MCC', 'AUC']
    n_pairs = len(pairs)
    n_metrics = len(metrics_plot)

    fig, axes = plt.subplots(n_pairs, n_metrics,
                             figsize=(4.5 * n_metrics, 3.5 * n_pairs + 0.8))
    if n_pairs == 1:
        axes = axes.reshape(1, -1)

    for row_idx, (base_key, smote_key) in enumerate(pairs):
        sfx_s = smote_key.replace('feat', 'f')
        smote_df = df[df['ApproachKey'] == smote_key]

        for col_idx, metric in enumerate(metrics_plot):
            ax   = axes[row_idx, col_idx]
            dcol = f'Delta_{metric}_{sfx_s}'

            if dcol not in smote_df.columns:
                ax.set_visible(False)
                continue

            pivot = pd.DataFrame(index=models, columns=exps, dtype=float)
            for exp in exps:
                for mn in models:
                    row = smote_df[(smote_df['Experiment'] == exp) &
                                   (smote_df['Model']      == mn)]
                    if not row.empty and dcol in row.columns:
                        v = row[dcol].values[0]
                        pivot.loc[mn, exp] = round(float(v), 4) if not np.isnan(v) else 0.

            pivot = pivot.astype(float)
            valid = pivot.values[~np.isnan(pivot.values)]
            vabs  = max(abs(valid).max(), 0.01) if len(valid) else 0.1

            sns.heatmap(pivot, ax=ax,
                        cmap='RdYlGn', center=0, vmin=-vabs, vmax=vabs,
                        annot=True, fmt='.3f', annot_kws={'size': 9, 'weight': 'bold'},
                        linewidths=0.5, linecolor='white',
                        cbar_kws={'label': f'Δ{metric}', 'shrink': 0.8})

            smote_label = APPROACH_LABELS[smote_key]
            base_label  = APPROACH_LABELS[base_key]
            sign_note   = "(SMOTE − baseline)" if metric != 'MAE' else "(baseline − SMOTE)"
            ax.set_title(f'Δ{metric} {sign_note}\n{smote_label} vs {base_label}',
                         fontsize=9, fontweight='bold')
            ax.set_xlabel('Expérience', fontsize=8)
            ax.set_ylabel('Régresseur', fontsize=8)

    fig.suptitle('Impact SMOTE+sample_weight+Youden  |  vert=amélioration · rouge=dégradation\n'
                 '[Ref 1] Chawla 2002  [Ref 2] He&Garcia 2009  [Ref 3] Youden 1950',
                 fontsize=11, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(str(figures_dir / '05_delta_smote_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  OK  05_delta_smote_heatmap.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 6 — MAE & R² : SMOTE ne dégrade pas la régression
# ─────────────────────────────────────────────────────────────────────────────
def plot_mae_r2_impact(df, figures_dir, target):
    exps  = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    avail = [ak for ak in APPROACH_KEYS if ak in df['ApproachKey'].unique()]
    x     = np.arange(len(exps))

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    for ax, (metric, ylabel, best_fn) in zip(axes, [
        ('MAE', 'MAE ↓ (meilleur modèle)', min),
        ('R2',  'R² ↑ (meilleur modèle)',  max),
    ]):
        for ak in avail:
            vals = []
            for exp in exps:
                sub = df[(df['ApproachKey'] == ak) & (df['Experiment'] == exp)]
                if sub.empty:
                    vals.append(np.nan)
                else:
                    vals.append(float(best_fn(sub[metric])))
            vals_arr = np.array(vals, dtype=float)
            ax.plot(x, vals_arr, marker='o', lw=2.2,
                    color=APPROACH_COLORS[ak],
                    ls='--' if 'smote' not in ak else '-',
                    label=APPROACH_LABELS[ak], markersize=8, zorder=3)
            ax.fill_between(x, vals_arr, alpha=0.08, color=APPROACH_COLORS[ak])
        ax.set_xticks(x)
        ax.set_xticklabels([EXP_LABEL.get(e, e) for e in exps], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(ylabel, fontsize=10, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)

    fig.suptitle(f'Régression — SMOTE dégrade-t-il MAE/R² ? ({target})\n'
                 f'(tiret=baseline · plein=SMOTE)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(str(figures_dir / '06_mae_r2_impact.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  OK  06_mae_r2_impact.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 7 — Youden vs seuil fixe 5.0
# ─────────────────────────────────────────────────────────────────────────────
def plot_youden_vs_std5(df, figures_dir, target):
    smote_data = df[df['ApproachKey'].str.contains('smote')]
    if smote_data.empty:
        print("  [SKIP] 07_youden_vs_std5.png — pas de données SMOTE")
        return

    exps   = [e for e in EXPERIMENTS if e in smote_data['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in smote_data['Model'].unique()]
    n_exp  = len(exps)

    fig, axes = plt.subplots(2, n_exp, figsize=(3.2 * n_exp, 8))
    if n_exp == 1:
        axes = axes.reshape(2, 1)

    for row_idx, (m_youden, m_std5, ylabel) in enumerate([
        ('Sensitivity', 'Sens_std5', 'Sensitivity'),
        ('MCC',         'MCC_std5',  'MCC'),
    ]):
        for col_idx, exp in enumerate(exps):
            ax = axes[row_idx, col_idx]
            x  = np.arange(len(models))
            for ak, col_p, pat, lbl in [
                ('feat15_smote', APPROACH_COLORS['feat15_smote'], '', 'SMOTE15 Youden'),
                ('feat78_smote', APPROACH_COLORS['feat78_smote'], '', 'SMOTE78 Youden'),
            ]:
                sub = smote_data[(smote_data['ApproachKey'] == ak) &
                                 (smote_data['Experiment']  == exp)]
                if sub.empty:
                    continue

                vals_y = [float(sub[sub['Model'] == mn][m_youden].values[0])
                          if not sub[sub['Model'] == mn].empty else 0.
                          for mn in models]
                vals_5 = [float(sub[sub['Model'] == mn][m_std5].values[0])
                          if not sub[sub['Model'] == mn].empty else 0.
                          for mn in models]

                w = 0.18
                off_y = -w * 1.2 if '15' in ak else w * 1.2
                off_5 = -w * 0.2 if '15' in ak else w * 0.2

                ax.bar(x + off_y, vals_y, w, color=col_p, alpha=0.9, edgecolor='white',
                       label=f'{lbl}' if col_idx == 0 and row_idx == 0 else '_nolegend_')
                ax.bar(x + off_5, vals_5, w, color=col_p, alpha=0.4, edgecolor='gray',
                       hatch='//',
                       label=f'{lbl.replace("Youden","std5")}' if col_idx == 0 and row_idx == 0 else '_nolegend_')

            ax.axhline(0.5, color='gray', lw=1, ls='--', alpha=0.5)
            ax.set_xticks(x)
            ax.set_xticklabels(models, rotation=40, ha='right', fontsize=7)
            ax.set_ylim(0, 1.1)
            ax.set_ylabel(ylabel if col_idx == 0 else '')
            ax.set_title(EXP_LABEL.get(exp, exp) if row_idx == 0 else '')
            ax.grid(axis='y', alpha=0.3)

    fig.legend(loc='upper center', ncol=4, bbox_to_anchor=(0.5, 1.03), fontsize=8)
    fig.suptitle(f'Seuil Youden (plein) vs Seuil fixe=5.0 (hachuré) — {target}\n'
                 f'[Ref 3] Youden (1950) : seuil optimal argmax(TPR-FPR)',
                 fontsize=11, fontweight='bold', y=1.06)
    plt.tight_layout()
    plt.savefig(str(figures_dir / '07_youden_vs_std5.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  OK  07_youden_vs_std5.png")


def plot_ece_4way(df, figures_dir, target):
    """Figure 8 — ECE (calibration) et ICC (fiabilité) pour les 4 approches."""
    if df['ECE'].abs().sum() < 1e-4:
        print("  [SKIP] 08_ece_4way.png — ECE non disponible")
        return

    avail    = [ak for ak in APPROACH_KEYS if ak in df['ApproachKey'].unique()]
    models   = [m for m in MODEL_NAMES  if m in df['Model'].unique()]
    best_exp = df.loc[df['AUC'].idxmax(), 'Experiment'] if not df.empty else 'A'

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    x     = np.arange(len(models))
    n_a   = len(avail)
    bar_w = 0.75 / n_a

    for ax, (metric, ylabel, threshold, thr_label) in zip(axes, [
        ('ECE', 'ECE ↓ (≤0.05 = bien calibré)', 0.05, 'Seuil acceptable (0.05) — Guo 2017'),
        ('ICC', 'ICC ↑ (≥0.90 = excellent)',     0.90, 'Seuil excellent (0.90) — Koo 2016'),
    ]):
        for i, ak in enumerate(avail):
            vals = []
            for mn in models:
                row = df[(df['ApproachKey']==ak)&(df['Experiment']==best_exp)&(df['Model']==mn)]
                vals.append(float(row[metric].values[0]) if not row.empty else 0.)
            offset = (i - (n_a - 1) / 2) * bar_w
            bars = ax.bar(x + offset, vals, bar_w,
                          color=APPROACH_COLORS[ak], hatch=APPROACH_HATCH[ak],
                          edgecolor='white', alpha=0.9, label=APPROACH_LABELS[ak])
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x()+bar.get_width()/2, v+0.003,
                        f'{v:.3f}', ha='center', va='bottom', fontsize=7, fontweight='bold')
        ax.axhline(threshold, color='green', lw=1.5, ls='--', label=thr_label)
        ax.set_xticks(x); ax.set_xticklabels(models, rotation=30, ha='right', fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(f'{metric} — {target}  (Exp.{best_exp})', fontsize=10, fontweight='bold')
        ax.legend(fontsize=7, ncol=2); ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(str(figures_dir / '08_ece_4way.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  OK  08_ece_4way.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 9 — Radar 4 approches (Exp FULL)
# ─────────────────────────────────────────────────────────────────────────────
def plot_radar_4way(df, figures_dir, exp_ref='FULL'):
    avail = [ak for ak in APPROACH_KEYS if ak in df['ApproachKey'].unique()]
    metrics_r = ['R2', 'AUC', 'Sensitivity', 'MCC', 'MAE_inv']
    labels_r  = ['R²', 'AUC', 'Sensitivity', 'MCC', '1/MAE']
    N         = len(metrics_r)
    angles    = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles   += angles[:1]

    df_r = df.copy()
    df_r['MAE_inv'] = 1. / (df_r['MAE'] + 1e-6)

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    for ak in avail:
        col = APPROACH_COLORS[ak]
        ls  = '--' if 'smote' not in ak else '-'
        sub = df_r[(df_r['ApproachKey'] == ak) & (df_r['Experiment'] == exp_ref)]
        if sub.empty:
            sub = df_r[df_r['ApproachKey'] == ak]
            if sub.empty:
                continue
            sub = df_r[(df_r['ApproachKey'] == ak) &
                       (df_r['Experiment'] == sub['Experiment'].iloc[-1])]
        best_row  = sub.loc[sub['R2'].idxmax()]
        norm_vals = []
        for mr in metrics_r:
            col_all = df_r[mr].replace([np.inf, -np.inf], np.nan).dropna()
            mn_v, mx_v = col_all.min(), col_all.max()
            v = float(best_row[mr])
            norm_vals.append((v - mn_v) / (mx_v - mn_v + 1e-9))
        norm_vals += norm_vals[:1]
        ax.plot(angles, norm_vals, lw=2.5, ls=ls, color=col,
                label=f"{APPROACH_LABELS[ak]} ({best_row['Model'][:3]})")
        ax.fill(angles, norm_vals, alpha=0.1, color=col)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels_r, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.50', '0.75', '1.00'], fontsize=7, color='gray')
    ax.grid(alpha=0.4)
    ax.set_title(f'Radar 4 approches — Exp {exp_ref}  (LOSO)',
                 fontsize=11, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.45, 1.2), fontsize=8)
    plt.tight_layout()
    plt.savefig(str(figures_dir / '09_radar_full.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  OK  09_radar_full.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 10 — Tableau de synthèse
# ─────────────────────────────────────────────────────────────────────────────
def plot_summary_table(df, figures_dir, target):
    avail  = [ak for ak in APPROACH_KEYS if ak in df['ApproachKey'].unique()]
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    records = []
    for exp in exps:
        for ak in avail:
            sub = df[(df['ApproachKey'] == ak) & (df['Experiment'] == exp)]
            if sub.empty:
                continue
            best = sub.loc[sub['R2'].idxmax()]
            records.append({
                'Exp':         exp,
                'Approche':    APPROACH_LABELS[ak],
                'Modèle':      best['Model'],
                'MAE':         f"{best['MAE']:.4f}",
                'R²':          f"{best['R2']:.4f}",
                'AUC(Y)':      f"{best['AUC']:.4f}",
                'Sens(Y)':     f"{best['Sensitivity']:.4f}",
                'Spec(Y)':     f"{best['Specificity']:.4f}",
                'MCC(Y)':      f"{best['MCC']:.4f}",
                'Youden':      f"{best['Youden_mean']:.3f}",
            })

    df_tbl  = pd.DataFrame(records)
    cols    = ['Exp', 'Approche', 'Modèle', 'MAE', 'R²', 'AUC(Y)',
               'Sens(Y)', 'Spec(Y)', 'MCC(Y)', 'Youden']
    n_rows  = len(df_tbl)

    fig, ax = plt.subplots(figsize=(22, max(3.5, n_rows * 0.58 + 1.5)))
    ax.axis('off')
    tbl = ax.table(cellText=df_tbl[cols].values.tolist(),
                   colLabels=cols, cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(8)
    tbl.scale(1.0, 1.9)

    bg_map = {
        'feat15':       '#D6EAF8',
        'feat15_smote': '#AED6F1',
        'feat78':       '#D5F5E3',
        'feat78_smote': '#A9DFBF',
    }
    for col in range(len(cols)):
        tbl[(0, col)].set_facecolor('#1A3A4A')
        tbl[(0, col)].set_text_props(color='white', fontweight='bold')

    avail_labels = {APPROACH_LABELS[ak]: ak for ak in avail}
    for row_idx, record in enumerate(df_tbl[cols].values.tolist(), start=1):
        ak_name = avail_labels.get(record[1], 'feat15')
        bg      = bg_map.get(ak_name, '#F9F9F9')
        for col in range(len(cols)):
            tbl[(row_idx, col)].set_facecolor(bg)

    ax.set_title(
        f'NeuroCap — Synthèse 4 approches : feat15 · feat15_smote · feat78 · feat78_smote\n'
        f'{target.upper()} | LOSO | Seuil Youden dynamique | '
        f'[Ref 1] Chawla 2002  [Ref 3] Youden 1950',
        fontsize=11, fontweight='bold', pad=18,
    )
    plt.tight_layout()
    plt.savefig(str(figures_dir / '10_summary_table.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  OK  10_summary_table.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 00 — DASHBOARD GLOBAL (vue d'ensemble par état cognitif)
# ─────────────────────────────────────────────────────────────────────────────
def plot_global_overview(df, figures_dir, target):
    """
    Figure 00 — Dashboard complet SMOTE : 4 lignes × 5 cols.

    Ligne 1 : métriques d'imbalance essentielles  (Sensitivity, MCC, F1_macro, PR_AUC, AUC)
    Ligne 2 : métriques professionnelles           (Specificity, F1_weighted, Balanced_Acc, R², MAE)
    Ligne 3 : ΔSensitivity heatmaps (×2 paires) + Radar 6 axes
    Ligne 4 : évolution MAE/R² par expérience + Youden vs std5

    NOTE : Accuracy seule exclue — inadaptée au déséquilibre (71 % Low →
           un modèle trivial atteindrait 0.71 sans apprentissage).
           Remplacée par : MCC, F1_macro, PR_AUC, Balanced_Acc.
    """
    exps    = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models  = [m for m in MODEL_NAMES  if m in df['Model'].unique()]
    avail   = [ak for ak in APPROACH_KEYS if ak in df['ApproachKey'].unique()]
    exp_ref = 'FULL' if 'FULL' in exps else exps[-1]
    n_appr  = len(avail)
    bar_w   = 0.72 / max(n_appr, 1)

    fig = plt.figure(figsize=(24, 24))
    gs  = fig.add_gridspec(4, 5, hspace=0.60, wspace=0.42,
                           top=0.93, bottom=0.04, left=0.06, right=0.97)

    fig.suptitle(
        f'NeuroCap — Comparaison SMOTE  |  {target.upper()}  |  LOSO\n'
        f'feat15 · feat15_smote · feat78 · feat78_smote   —   Exp. {exp_ref}\n'
        f'⚠ Accuracy exclue (non pertinente sur données déséquilibrées)  '
        f'→  MCC · F1_macro · PR_AUC · Balanced_Acc utilisés',
        fontsize=13, fontweight='bold'
    )

    handles = [mpatches.Patch(color=APPROACH_COLORS[ak], hatch=APPROACH_HATCH[ak],
                               label=APPROACH_LABELS[ak]) for ak in avail]
    fig.legend(handles=handles, loc='upper right',
               bbox_to_anchor=(0.97, 0.96), fontsize=8, ncol=2,
               title='Approche', title_fontsize=8)

    def _barplot_row(gs_row, metrics_list, row_note=''):
        """Helper : trace 5 barplots 4-approches sur une ligne du GridSpec."""
        for col_i, (metric, ylabel, ylim, hline) in enumerate(metrics_list):
            ax = fig.add_subplot(gs[gs_row, col_i])
            x  = np.arange(len(models))
            for i, ak in enumerate(avail):
                vals = []
                for mn in models:
                    row = df[(df['ApproachKey']==ak)&
                             (df['Experiment']==exp_ref)&
                             (df['Model']==mn)]
                    vals.append(float(row[metric].values[0]) if not row.empty else 0.)
                offset = (i - (n_appr - 1) / 2) * bar_w
                ax.bar(x + offset, vals, bar_w,
                       color=APPROACH_COLORS[ak], hatch=APPROACH_HATCH[ak],
                       alpha=0.90, edgecolor='white')
                for bar, v in zip(ax.patches[-len(models):], vals):
                    if abs(v) > 0.01:
                        ax.text(bar.get_x()+bar.get_width()/2,
                                bar.get_height() + (0.012 if v >= 0 else -0.04),
                                f'{v:.2f}', ha='center',
                                va='bottom' if v >= 0 else 'top',
                                fontsize=4.5, rotation=55, color='#2C3E50')
            if hline is not None:
                ax.axhline(hline, color='gray', lw=0.8, ls='--', alpha=0.5)
            ax.set_xticks(x)
            ax.set_xticklabels([m[:3] for m in models], fontsize=6.5)
            ax.set_title(ylabel, fontsize=9, fontweight='bold')
            if ylim:
                ax.set_ylim(ylim)
            ax.grid(axis='y', alpha=0.3)

    # ── Ligne 0 : métriques d'imbalance essentielles ─────────────────────────
    _barplot_row(0, [
        ('Sensitivity', 'Sensitivity ↑\n(TPR — rappel High)',  (0., 1.15), 0.5),
        ('MCC',         'MCC ↑\n(gold standard imbalance)',    (-0.5,1.15), 0.0),
        ('F1_macro',    'F1 Macro ↑\n(moyenne non pondérée)',  (0., 1.15), 0.5),
        ('PR_AUC',      'PR-AUC ↑\n(Précision-Rappel)',        (0., 1.15), None),
        ('AUC',         'AUC ROC ↑\n(discrimination globale)', (0.2,1.05), 0.5),
    ])

    # ── Ligne 1 : métriques professionnelles complémentaires ─────────────────
    _barplot_row(1, [
        ('Specificity',  'Specificity ↑\n(TNR — ne pas sur-alarmer)', (0., 1.15), 0.5),
        ('F1_weighted',  'F1 Weighted ↑\n(pondéré par support)',      (0., 1.15), 0.5),
        ('Balanced_Acc', 'Balanced Acc ↑\n(moyenne TPR+TNR)',         (0., 1.15), 0.5),
        ('R2',           'R² ↑\n(qualité régression)',                 None,      0.0),
        ('MAE',          'MAE ↓\n(erreur absolue moyenne)',            None,      None),
    ])

    # ── Ligne 2 : ΔSensitivity heatmaps (×2) + Radar ─────────────────────────
    pairs = [(ak_b, ak_s) for ak_b, ak_s in SMOTE_PAIRS
             if ak_b in df['ApproachKey'].unique() and ak_s in df['ApproachKey'].unique()]

    for p_idx, (base_key, smote_key) in enumerate(pairs[:2]):
        ax_h  = fig.add_subplot(gs[2, p_idx*2 : p_idx*2+2])
        sfx_s = smote_key.replace('feat', 'f')
        dcol  = f'Delta_Sensitivity_{sfx_s}'
        smote_df = df[df['ApproachKey'] == smote_key]
        pivot = pd.DataFrame(index=models, columns=exps, dtype=float)
        for exp in exps:
            for mn in models:
                row = smote_df[(smote_df['Experiment']==exp)&(smote_df['Model']==mn)]
                if not row.empty and dcol in row.columns:
                    v = row[dcol].values[0]
                    try:
                        pivot.loc[mn, exp] = round(float(v), 4) if not np.isnan(float(v)) else 0.
                    except (TypeError, ValueError):
                        pivot.loc[mn, exp] = 0.
        pivot = pivot.astype(float)
        valid = pivot.values[~np.isnan(pivot.values)]
        vabs  = max(abs(valid).max(), 0.01) if len(valid) else 0.1
        sns.heatmap(pivot, ax=ax_h, cmap='RdYlGn', center=0, vmin=-vabs, vmax=vabs,
                    annot=True, fmt='.3f', annot_kws={'size': 9, 'weight': 'bold'},
                    linewidths=0.5, linecolor='white',
                    cbar_kws={'label': 'ΔSensitivity (SMOTE−baseline)', 'shrink': 0.8})
        ax_h.set_title(
            f'ΔSensitivity · {APPROACH_LABELS[smote_key]}\nvs {APPROACH_LABELS[base_key]}'
            f'   🟢 SMOTE améliore   🔴 SMOTE dégrade',
            fontsize=9, fontweight='bold'
        )

    # Radar 6 axes (col 4)
    ax_rad = fig.add_subplot(gs[2, 4], projection='polar')
    metrics_r = ['R2', 'AUC', 'Sensitivity', 'MCC', 'F1_macro', 'PR_AUC']
    labels_r  = ['R²', 'AUC', 'Sens', 'MCC', 'F1mac', 'PR-AUC']
    N      = len(metrics_r)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist() + [0]
    df_r   = df.copy()
    for ak in avail:
        col = APPROACH_COLORS[ak]; ls = '--' if 'smote' not in ak else '-'
        sub = df_r[(df_r['ApproachKey']==ak)&(df_r['Experiment']==exp_ref)]
        if sub.empty:
            continue
        best_row  = sub.loc[sub['MCC'].idxmax()]
        norm_vals = []
        for mr in metrics_r:
            col_all = df_r[mr].replace([np.inf, -np.inf], np.nan).dropna()
            mn_v, mx_v = col_all.min(), col_all.max()
            norm_vals.append((float(best_row[mr]) - mn_v) / (mx_v - mn_v + 1e-9))
        norm_vals += norm_vals[:1]
        ax_rad.plot(angles, norm_vals, lw=2.2, ls=ls, color=col,
                    label=APPROACH_LABELS[ak][:10])
        ax_rad.fill(angles, norm_vals, alpha=0.10, color=col)
    ax_rad.set_xticks(angles[:-1])
    ax_rad.set_xticklabels(labels_r, fontsize=8)
    ax_rad.set_ylim(0, 1)
    ax_rad.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax_rad.set_yticklabels(['0.25','0.50','0.75','1.00'], fontsize=5, color='gray')
    ax_rad.grid(alpha=0.4)
    ax_rad.set_title(f'Radar (best MCC)\nExp {exp_ref}', fontsize=9, fontweight='bold', pad=14)
    ax_rad.legend(loc='upper right', bbox_to_anchor=(2.2, 1.25), fontsize=6.5)

    # ── Ligne 3 : évolution MAE & R² par expérience (×2 cols) + Youden (1 col) ─
    for col_i, (metric, ylabel, best_fn) in enumerate([
        ('MAE', 'MAE ↓  (meilleur modèle)', min),
        ('R2',  'R² ↑  (meilleur modèle)',  max),
    ]):
        ax = fig.add_subplot(gs[3, col_i*2 : col_i*2+2])
        x  = np.arange(len(exps))
        for ak in avail:
            vals = []
            for exp in exps:
                sub = df[(df['ApproachKey']==ak)&(df['Experiment']==exp)]
                vals.append(float(best_fn(sub[metric])) if not sub.empty else np.nan)
            va = np.array(vals, dtype=float)
            ax.plot(x, va, marker='o', lw=2,
                    color=APPROACH_COLORS[ak],
                    ls='--' if 'smote' not in ak else '-',
                    label=APPROACH_LABELS[ak], markersize=6, zorder=3)
            ax.fill_between(x, va, alpha=0.07, color=APPROACH_COLORS[ak])
        if metric == 'R2':
            ax.axhline(0., color='#E74C3C', lw=1, ls=':', alpha=0.6, label='R²=0 (baseline trivial)')
        ax.set_xticks(x)
        ax.set_xticklabels([EXP_LABEL.get(e, e) for e in exps], fontsize=7)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.set_title(f'Évolution {ylabel}', fontsize=9, fontweight='bold')
        ax.legend(fontsize=6); ax.grid(alpha=0.3)

    # Youden vs std5 — Sensitivity + MCC côte à côte (col 4)
    ax_y = fig.add_subplot(gs[3, 4])
    smote_data = df[df['ApproachKey'].str.contains('smote')]
    if not smote_data.empty:
        x = np.arange(len(models))
        for ak, col_p in [('feat15_smote', APPROACH_COLORS['feat15_smote']),
                           ('feat78_smote', APPROACH_COLORS['feat78_smote'])]:
            if ak not in smote_data['ApproachKey'].unique():
                continue
            sub = smote_data[(smote_data['ApproachKey']==ak)&
                             (smote_data['Experiment']==exp_ref)]
            if sub.empty:
                continue
            vals_y = [float(sub[sub['Model']==mn]['Sensitivity'].values[0])
                      if not sub[sub['Model']==mn].empty else 0. for mn in models]
            vals_5 = [float(sub[sub['Model']==mn]['Sens_std5'].values[0])
                      if not sub[sub['Model']==mn].empty else 0. for mn in models]
            lbl   = '15f' if '15' in ak else '78f'
            off_y = -0.18 if '15' in ak else 0.18
            ax_y.bar(x + off_y - 0.09, vals_y, 0.18, color=col_p, alpha=0.9,
                     edgecolor='white', label=f'{lbl} Youden (opt.)')
            ax_y.bar(x + off_y + 0.09, vals_5, 0.18, color=col_p, alpha=0.4,
                     edgecolor='gray', hatch='//', label=f'{lbl} seuil=5.0')
        ax_y.axhline(0.5, color='gray', lw=1, ls='--', alpha=0.5, label='chance (0.5)')
        ax_y.set_xticks(x)
        ax_y.set_xticklabels([m[:3] for m in models], fontsize=6.5)
        ax_y.set_ylim(0, 1.15)
        ax_y.set_ylabel('Sensitivity', fontsize=8)
        ax_y.set_title('Youden optimal (plein)\nvs seuil fixe=5.0 (hachuré)',
                       fontsize=8, fontweight='bold')
        ax_y.legend(fontsize=5.5, ncol=2); ax_y.grid(axis='y', alpha=0.3)
    else:
        ax_y.axis('off')
        ax_y.text(0.5, 0.5, 'Données SMOTE\nnon disponibles',
                  ha='center', va='center', fontsize=10, color='gray',
                  transform=ax_y.transAxes)

    plt.savefig(str(figures_dir / '00_global_overview.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  OK  00_global_overview.png")


# ─────────────────────────────────────────────────────────────────────────────
# RAPPORT TEXTE
# ─────────────────────────────────────────────────────────────────────────────
def generate_text_report(df, out_dir, target):
    """
    Rapport texte structuré identique à compare_regression_features.py,
    adapté pour 4 approches SMOTE avec métriques complètes :
    MAE · RMSE · R² · F1mac · F1w · BalAcc · AUC · Sens · Spec · MCC · PR_AUC · Deploy · Youden · ΔSens
    Accuracy exclue : inadaptée au déséquilibre (71 % Low).
    """
    avail  = [ak for ak in APPROACH_KEYS if ak in df['ApproachKey'].unique()]
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]

    has_prof = df['AUC_CI_LO'].abs().sum() > 1e-4
    has_f1   = 'F1_macro' in df.columns and df['F1_macro'].abs().sum() > 0
    has_ci   = df['AUC_CI_LO'].abs().sum() > 1e-4

    W = 175
    lines = [
        "=" * W,
        f"NeuroCap — Comparaison SMOTE — {target.upper()}",
        f"4 approches : feat15 · feat15_smote · feat78 · feat78_smote",
        "=" * W,
        "",
        "Protocole : LOSO (Leave-One-Subject-Out) | Low=0-5 / High=5-10",
        "Légende   : (Y)=seuil Youden dynamique · std5=seuil fixe 5.0",
        "⚠  Accuracy exclue — inadaptée au déséquilibre (71 % Low → trivial=0.71 sans apprentissage)",
        "   Remplacées par : MCC · F1_macro · PR_AUC · Balanced_Acc",
        "",
    ]

    # ── En-tête du tableau principal ─────────────────────────────────────────
    hdr = (f"{'Approche':22s} {'Exp':5s} {'Modèle':15s} "
           f"{'MAE':>8s} {'RMSE':>8s} {'R²':>8s} "
           f"{'F1mac':>7s} {'F1w':>7s} {'BalAcc':>7s} "
           f"{'AUC(Y)':>8s} {'Sens(Y)':>8s} {'Spec(Y)':>8s} {'MCC(Y)':>8s} "
           f"{'PR_AUC':>8s} {'Youden':>7s} {'ΔSens':>9s}")
    lines += [hdr, "─" * W]

    # ── Tableau complet ───────────────────────────────────────────────────────
    for exp in exps:
        for ak in avail:
            label = APPROACH_LABELS[ak]
            for mn in models:
                row = df[(df['ApproachKey'] == ak) &
                         (df['Experiment']  == exp) &
                         (df['Model']       == mn)]
                if row.empty:
                    continue
                r = row.iloc[0]

                # ΔSens : SMOTE − baseline correspondant
                delta_sens = '        —'
                if 'smote' in ak:
                    sfx_s = ak.replace('feat', 'f')
                    dcol  = f'Delta_Sensitivity_{sfx_s}'
                    if dcol in r.index and not pd.isna(r.get(dcol)):
                        delta_sens = f'{float(r[dcol]):+9.4f}'

                f1mac  = float(r['F1_macro'])    if has_f1 else 0.
                f1w    = float(r['F1_weighted'])  if has_f1 else 0.
                balacc = float(r['Balanced_Acc']) if has_f1 else 0.
                prauc  = float(r['PR_AUC'])

                lines.append(
                    f"{label:22s} {exp:5s} {mn:15s} "
                    f"{r['MAE']:>8.4f} {r['RMSE']:>8.4f} {r['R2']:>8.4f} "
                    f"{f1mac:>7.4f} {f1w:>7.4f} {balacc:>7.4f} "
                    f"{r['AUC']:>8.4f} {r['Sensitivity']:>8.4f} "
                    f"{r['Specificity']:>8.4f} {r['MCC']:>8.4f} "
                    f"{prauc:>8.4f} "
                    f"{r['Youden_mean']:>7.3f} {delta_sens:>9s}"
                )
        lines.append("")

    # ── Meilleurs modèles (par R²) ────────────────────────────────────────────
    lines += ["=" * W, "MEILLEURS MODÈLES (par R²)", "=" * W]
    for ak in avail:
        label = APPROACH_LABELS[ak]
        sub   = df[df['ApproachKey'] == ak]
        if sub.empty:
            continue
        best = sub.loc[sub['R2'].idxmax()]
        line = (f"  {label:22s} → {best['Model']:16s} | Exp {best['Experiment']} | "
                f"MAE={best['MAE']:.4f}  R²={best['R2']:.4f}")
        if has_f1:
            line += f"  F1mac={best['F1_macro']:.4f}"
        line += f"  AUC={best['AUC']:.4f}  Sens={best['Sensitivity']:.4f}  MCC={best['MCC']:.4f}"
        lines.append(line)

    # ── Meilleurs modèles (par MCC) ───────────────────────────────────────────
    lines += ["", "MEILLEURS MODÈLES (par MCC)", "─" * W]
    for ak in avail:
        label = APPROACH_LABELS[ak]
        sub   = df[df['ApproachKey'] == ak]
        if sub.empty:
            continue
        best = sub.loc[sub['MCC'].idxmax()]
        line = (f"  {label:22s} → {best['Model']:16s} | Exp {best['Experiment']} | "
                f"MCC={best['MCC']:.4f}  Sens={best['Sensitivity']:.4f}  "
                f"Spec={best['Specificity']:.4f}  AUC={best['AUC']:.4f}")
        if has_f1:
            line += (f"  F1mac={best['F1_macro']:.4f}  F1w={best['F1_weighted']:.4f}"
                     f"  BalAcc={best['Balanced_Acc']:.4f}  PR_AUC={best['PR_AUC']:.4f}")
        lines.append(line)

    # ── Métriques professionnelles (meilleur MCC) ─────────────────────────────
    if has_prof:
        lines += ["", "MÉTRIQUES PROFESSIONNELLES (meilleur MCC)", "─" * W]
        for ak in avail:
            label = APPROACH_LABELS[ak]
            sub   = df[df['ApproachKey'] == ak]
            if sub.empty:
                continue
            best = sub.loc[sub['MCC'].idxmax()]
            f1mac_str  = f"  F1_macro={best['F1_macro']:.4f}" if has_f1 else ''
            balacc_str = f"  Balanced_Acc={best['Balanced_Acc']:.4f}" if has_f1 else ''
            prauc_str  = f"  PR-AUC={best['PR_AUC']:.4f}" if has_f1 else ''
            ci_str     = (f"  AUC CI 95% = [{best['AUC_CI_LO']:.4f}, {best['AUC_CI_HI']:.4f}]"
                          f"  p={best['AUC_Pvalue']:.4f}"
                          f"  {'✅ sig.' if best['AUC_Pvalue'] < 0.05 else '❌ ns'}"
                          if has_ci else '')
            lines.append(
                f"  {label:22s} → {best['Model']:16s} | Exp {best['Experiment']}\n"
                f"    Sensitivity={best['Sensitivity']:.4f}  Specificity={best['Specificity']:.4f}"
                f"  MCC={best['MCC']:.4f}{prauc_str}{f1mac_str}{balacc_str}\n"
                f"    {ci_str}\n"
                f"    ECE={best['ECE']:.4f}  Bland-bias={best['Bland_Bias']:+.4f}"
                f"  ICC={best['ICC']:.3f}"
                f"  Youden={best['Youden_mean']:.3f}±{best['Youden_std']:.3f}"
            )

    # ── Impact SMOTE global ───────────────────────────────────────────────────
    lines += ["", "=" * W, "IMPACT SMOTE — ΔSens · ΔMCC · ΔAUC · ΔF1mac · ΔPR_AUC (SMOTE − baseline)",
              "─" * W]
    for base_key, smote_key in SMOTE_PAIRS:
        if base_key not in df['ApproachKey'].unique():
            continue
        if smote_key not in df['ApproachKey'].unique():
            continue
        lines.append(f"  {APPROACH_LABELS[smote_key]} vs {APPROACH_LABELS[base_key]}:")
        sub_s = df[df['ApproachKey'] == smote_key]
        sub_b = df[df['ApproachKey'] == base_key]
        for mn in models:
            row_s = sub_s[sub_s['Model'] == mn]
            row_b = sub_b[sub_b['Model'] == mn]
            if row_s.empty or row_b.empty:
                continue
            best_s = row_s.loc[row_s['R2'].idxmax()]
            best_b = row_b.loc[row_b['R2'].idxmax()]
            d_sens = best_s['Sensitivity'] - best_b['Sensitivity']
            d_mcc  = best_s['MCC']         - best_b['MCC']
            d_auc  = best_s['AUC']         - best_b['AUC']
            d_f1   = (best_s['F1_macro']   - best_b['F1_macro'])   if has_f1 else 0.
            d_pr   = (best_s['PR_AUC']     - best_b['PR_AUC'])     if has_f1 else 0.
            d_r2   = best_s['R2']          - best_b['R2']
            d_mae  = best_b['MAE']         - best_s['MAE']
            lines.append(
                f"    {mn:16s} → ΔSens={d_sens:+.4f}  ΔMCC={d_mcc:+.4f}"
                f"  ΔAUC={d_auc:+.4f}  ΔF1mac={d_f1:+.4f}  ΔPR_AUC={d_pr:+.4f}"
                f"  ΔR²={d_r2:+.4f}  ΔMAE={d_mae:+.4f}"
            )
        lines.append("")

    # ── Recommandation ────────────────────────────────────────────────────────
    lines += ["=" * W, "RECOMMANDATION (meilleur MCC par approche)", "─" * W]
    for ak in avail:
        sub = df[df['ApproachKey'] == ak]
        if sub.empty:
            continue
        best = sub.loc[sub['MCC'].idxmax()]
        line = (f"  {APPROACH_LABELS[ak]:25s} → {best['Model']:14s} | Exp {best['Experiment']:4s} | "
                f"MCC={best['MCC']:.4f}  Sens={best['Sensitivity']:.4f}  "
                f"Spec={best['Specificity']:.4f}  AUC={best['AUC']:.4f}")
        if has_f1:
            line += f"  F1mac={best['F1_macro']:.4f}  BalAcc={best['Balanced_Acc']:.4f}"
        line += f"  R²={best['R2']:.4f}"
        lines.append(line)

    best_smote_mcc = (df[df['ApproachKey'].str.contains('smote')]['MCC'].max()
                      if any('smote' in ak for ak in avail) else None)
    best_base_mcc  = (df[~df['ApproachKey'].str.contains('smote')]['MCC'].max()
                      if any('smote' not in ak for ak in avail) else None)
    if best_smote_mcc is not None and best_base_mcc is not None:
        delta_mcc_global = best_smote_mcc - best_base_mcc
        lines += [
            "",
            f"  ΔMCC global (SMOTE − baseline) : {delta_mcc_global:+.4f}",
            f"  → {'✅ SMOTE améliore la détection High' if delta_mcc_global > 0.02 else '⚠ Gain MCC < 0.02 — SMOTE peu décisif sur ce target'}",
        ]

    lines += [
        "",
        "Références :",
        "  [1] Chawla et al. (2002) SMOTE — JAIR 16:321-357",
        "  [2] He & Garcia (2009) Imbalanced Learning — IEEE TKDE 21(9):1263-1284",
        "  [3] Youden (1950) Index for rating diagnostic tests — Cancer 3(1):32-35",
        "  [4] Chicco & Jurman (2020) MCC vs F1 — BMC Genomics 21:6",
        "=" * W,
    ]

    report = "\n".join(lines)
    path   = out_dir / f'comparison_summary_{target}.txt'
    path.write_text(report, encoding='utf-8')
    print(f"  OK  comparison_summary_{target}.txt")
    print("\n" + report)
    return report


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RUN_TARGET
# ─────────────────────────────────────────────────────────────────────────────
def run_target(target):
    print(f"\n{'='*70}")
    print(f"TARGET : {target.upper()}")
    print(f"{'='*70}")

    json_paths = {
        'feat15':       FEAT15_ROOT       / target / f'results_{target}.json',
        'feat15_smote': FEAT15_SMOTE_ROOT / target / f'results_{target}.json',
        'feat78':       FEAT78_ROOT       / target / f'results_{target}.json',
        'feat78_smote': FEAT78_SMOTE_ROOT / target / f'results_{target}.json',
    }

    loaded = {}
    print("\nChargement :")
    for ak, path in json_paths.items():
        data = load_json(path, ak)
        if data is not None:
            loaded[ak] = extract_metrics(data)
        else:
            loaded[ak] = None

    if all(v is None for v in loaded.values()):
        print(f"  Aucun JSON disponible pour {target} — skipped")
        return

    avail = [ak for ak, v in loaded.items() if v is not None]
    print(f"  Approches disponibles : {avail}")

    df = build_dataframe(loaded)
    if df.empty:
        print(f"  DataFrame vide pour {target}")
        return

    out_dir     = OUT_ROOT / target
    figures_dir = out_dir  / 'figures'
    out_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_dir / f'comparison_table_{target}.csv',
              index=False, float_format='%.4f')
    print(f"\n  OK  comparison_table_{target}.csv ({len(df)} lignes)\n")

    print("── Figure globale ──")
    plot_global_overview(df, figures_dir, target)

    print("\n── Figures métriques d'imbalance ──")
    plot_4way_barplot(df, 'Sensitivity',
                      f'Sensitivity (TPR) — 4 approches ({target})',
                      '01_sensitivity_4way.png', figures_dir)
    plot_4way_barplot(df, 'Specificity',
                      f'Specificity (TNR) — 4 approches ({target})',
                      '02_specificity_4way.png', figures_dir)
    plot_4way_barplot(df, 'MCC',
                      f'MCC — 4 approches ({target})  [Ref 4] Chicco 2020',
                      '03_mcc_4way.png', figures_dir, ylim=(-0.5, 1.15))
    plot_4way_barplot(df, 'AUC',
                      f'AUC ROC — 4 approches ({target})',
                      '04_auc_4way.png', figures_dir)

    print("\n── Figures SMOTE ──")
    plot_delta_smote_heatmap(df, figures_dir)
    plot_mae_r2_impact(df, figures_dir, target)
    plot_youden_vs_std5(df, figures_dir, target)
    plot_ece_4way(df, figures_dir, target)
    plot_radar_4way(df, figures_dir)
    plot_summary_table(df, figures_dir, target)

    print("\n── Rapport ──")
    generate_text_report(df, out_dir, target)


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("NeuroCap — Comparaison SMOTE : 4 approches (Régression)")
    print("feat15 · feat15_smote · feat78 · feat78_smote")
    print()
    print("Réfs : [1] Chawla 2002  [2] He&Garcia 2009  [3] Youden 1950")
    print("=" * 70)
    print(f"Sortie : {OUT_ROOT.relative_to(PROJECT_ROOT)}/")
    print()
    print("NOTE : Lancez d'abord les 4 scripts pour générer les results.json :")
    print("  python src/models/baselines/baseline_ML_regression.py")
    print("  python src/models/baselines/baseline_ML_regression_smote.py")
    print("  python src/models/baselines/baseline_ML_regression_feature_eng.py")
    print("  python src/models/baselines/baseline_ML_regression_feature_eng_smote.py")
    print()

    for target in TARGETS:
        run_target(target)

    print(f"\n{'='*70}")
    print("Terminé")
    print(f"Rapports : {OUT_ROOT.relative_to(PROJECT_ROOT)}/")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
