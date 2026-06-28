"""
=============================================================================
NeuroCap — Comparaison feat15 vs feat78 (Régression)
compare_regression_features.py
=============================================================================
Lit les results_{target}.json produits par :
  baseline_ML_regression.py          → feat15
  baseline_ML_regression_feature_eng → feat78

Métriques : MAE, RMSE, R²  +  5 NIVEAUX PROFESSIONNELS
  Sensitivité, Spécificité, MCC, PR-AUC, Bootstrap CI, DeLong AUC CI
  Calibration ECE, ICC, Bland-Altman bias

Modèles : SVR, Random Forest, XGBoost, LightGBM

SORTIES :
  reports/Regression/Comparison_Features/{conc,stress}/
    figures/
      01_mae_barplot.png    02_r2_barplot.png     03_rmse_barplot.png
      04_gain_heatmap.png   05_radar_FULL.png      06_summary_table.png
      07_best_per_exp.png   08_f1mac_barplot.png   09_auc_barplot.png
      10_sensitivity_spec.png    ← NOUVEAU
      11_mcc_barplot.png         ← NOUVEAU
      12_ece_icc.png             ← NOUVEAU
      13_auc_bootstrap_ci.png    ← NOUVEAU
      00_global_overview.png    ← DASHBOARD GLOBAL (toutes métriques clés)
    comparison_table_{target}.csv
    comparison_summary_{target}.txt
    comparison_latex_{target}.txt
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

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parents[3]

FEAT15_ROOT = PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline' / 'feat15'
FEAT63_ROOT = PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline' / 'feat78'
OUT_ROOT    = PROJECT_ROOT / 'reports' / 'Regression' / "Baseline" /'Comparison_Features'

EXPERIMENTS  = ['A', 'B', 'C', 'D', 'FULL']
MODEL_NAMES  = ['SVR', 'Random Forest', 'XGBoost', 'LightGBM', 'Stacking']
TARGETS      = ['conc', 'stress']

APPROACH_LABELS = {
    'feat15': 'Baseline (15f)',
    'feat78': 'FeatEng (78f)',
}

C_BASE      = '#7FB3D3'
C_FEAT      = '#1A5276'
C_DELTA_POS = '#27AE60'
C_DELTA_NEG = '#E74C3C'

MODEL_COLORS = {
    'SVR':           '#E74C3C',
    'Random Forest': '#2980B9',
    'XGBoost':       '#27AE60',
    'LightGBM':      '#F39C12',
    'Stacking':      '#8E44AD',
}

EXP_LABEL = {'A': 'A\n(×1)', 'B': 'B\n(×2)', 'C': 'C\n(×3)',
             'D': 'D\n(×2)', 'FULL': 'FULL\n(×4)'}


# ============================================================================
# CHARGEMENT
# ============================================================================
def load_json(path: Path, label: str) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"❌ JSON introuvable : {path}\n"
            f"   → Lancez d'abord {label}"
        )
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  ✅ {label:40s} → {path.relative_to(PROJECT_ROOT)}")
    return data


def extract_metrics(json_data: dict) -> dict:
    """
    Normalise le JSON → dict unifié avec métriques classiques + professionnelles.
    Compatible avec l'ancien format (binned) et le nouveau (professional).
    """
    raw = json_data.get('loso', json_data)
    out = {}
    for exp, models in raw.items():
        if exp not in EXPERIMENTS:
            continue
        out[exp] = {}
        for model_name, m in models.items():
            # Ignorer les clés internes ajoutées par les nouveaux scripts
            if model_name.startswith('_'):
                continue
            # ─── Support ancien format (binned) ────────────────────────────
            bm   = m.get('binned', {})
            prof = m.get('professional', {})

            # Métriques de base (présentes dans les deux formats)
            entry = {
                'mae':          float(m.get('mae',  999.)),
                'rmse':         float(m.get('rmse', 999.)),
                'r2':           float(m.get('r2',   -99.)),
                # ─── Niveau 1 ─────────────────────────────────────────────
                # Nouveau format (professional) ou ancien (binned)
                'f1_weighted':  float(m.get('f1_weighted', bm.get('f1_weighted', 0.))),
                'f1_macro':     float(m.get('f1_macro',    bm.get('f1_macro',    0.))),
                'auc':          float(m.get('auc_roc',     bm.get('auc',         0.))),
                'accuracy':     float(m.get('accuracy',    bm.get('accuracy',    0.))),
                'sensitivity':  float(m.get('sensitivity', 0.)),
                'specificity':  float(m.get('specificity', 0.)),
                'mcc':          float(m.get('mcc',         0.)),
                'balanced_acc': float(m.get('balanced_accuracy', 0.)),
                'pr_auc':       float(m.get('pr_auc',      0.)),
                # ─── Niveau 2 : Bootstrap CI ──────────────────────────────
                'auc_ci_lo':    0., 'auc_ci_hi':  0.,
                'r2_ci_lo':     0., 'r2_ci_hi':   0.,
                'auc_pvalue':   1., 'r2_pvalue':  1.,
                # ─── Niveau 3 : Calibration + Bland-Altman + ICC ──────────
                'ece':          0., 'icc': 0., 'bland_bias': 0., 'loa_width': 0.,
            }

            # Extraire les métriques professionnelles si disponibles
            if prof:
                bci  = prof.get('bootstrap_ci', {})
                perm = prof.get('permutation', {})
                cal  = prof.get('calibration', {})
                ba   = prof.get('bland_altman', {})
                ic   = prof.get('icc', {})
                entry['auc_ci_lo']   = float(bci.get('auc_roc', {}).get('ci_lo', 0.))
                entry['auc_ci_hi']   = float(bci.get('auc_roc', {}).get('ci_hi', 0.))
                entry['r2_ci_lo']    = float(bci.get('r2', {}).get('ci_lo', 0.))
                entry['r2_ci_hi']    = float(bci.get('r2', {}).get('ci_hi', 0.))
                entry['auc_pvalue']  = float(perm.get('auc_roc', {}).get('p_value', 1.))
                entry['r2_pvalue']   = float(perm.get('r2', {}).get('p_value', 1.))
                entry['ece']         = float(cal.get('ece', 0.))
                entry['bland_bias']  = float(ba.get('bias', 0.))
                entry['loa_width']   = float(ba.get('loa_width', 0.))
                entry['icc']         = float(ic.get('icc', 0.))

            out[exp][model_name] = entry
    return out


# ============================================================================
# DATAFRAME UNIFIÉ
# ============================================================================
def build_dataframe(metrics15: dict, metrics63: dict) -> pd.DataFrame:
    rows = []
    for approach_key, metrics in [('feat15', metrics15), ('feat78', metrics63)]:
        label = APPROACH_LABELS[approach_key]
        for exp, models in metrics.items():
            for mn, m in models.items():
                rows.append({
                    'Approach':    label,
                    'ApproachKey': approach_key,
                    'Experiment':  exp,
                    'Model':       mn,
                    'MAE':         m['mae'],
                    'RMSE':        m['rmse'],
                    'R2':          m['r2'],
                    'F1_macro':    m['f1_macro'],
                    'F1_weighted': m['f1_weighted'],
                    'AUC':         m['auc'],
                    'Accuracy':    m['accuracy'],
                    # Métriques professionnelles
                    'Sensitivity':   m['sensitivity'],
                    'Specificity':   m['specificity'],
                    'MCC':           m['mcc'],
                    'Balanced_Acc':  m['balanced_acc'],
                    'PR_AUC':        m['pr_auc'],
                    'AUC_CI_LO':     m['auc_ci_lo'],
                    'AUC_CI_HI':    m['auc_ci_hi'],
                    'AUC_Pvalue':   m['auc_pvalue'],
                    'ECE':          m['ece'],
                    'ICC':          m['icc'],
                    'Bland_Bias':   m['bland_bias'],
                })

    df = pd.DataFrame(rows)

    # ΔR² = feat78 − feat15
    b  = df[df['ApproachKey'] == 'feat15'][['Experiment', 'Model', 'R2']]
    f  = df[df['ApproachKey'] == 'feat78'][['Experiment', 'Model', 'R2']]
    mg = f.merge(b, on=['Experiment', 'Model'], suffixes=('_63', '_15'))
    mg['Delta_R2'] = mg['R2_63'] - mg['R2_15']

    # ΔMAE = feat15 − feat78  (positif = feat78 mieux)
    bm  = df[df['ApproachKey'] == 'feat15'][['Experiment', 'Model', 'MAE']]
    fm  = df[df['ApproachKey'] == 'feat78'][['Experiment', 'Model', 'MAE']]
    mg2 = bm.merge(fm, on=['Experiment', 'Model'], suffixes=('_15', '_63'))
    mg2['Delta_MAE'] = mg2['MAE_15'] - mg2['MAE_63']

    # ΔF1mac = feat78 − feat15
    bf  = df[df['ApproachKey'] == 'feat15'][['Experiment', 'Model', 'F1_macro']]
    ff  = df[df['ApproachKey'] == 'feat78'][['Experiment', 'Model', 'F1_macro']]
    mg3 = ff.merge(bf, on=['Experiment', 'Model'], suffixes=('_63', '_15'))
    mg3['Delta_F1mac'] = mg3['F1_macro_63'] - mg3['F1_macro_15']

    # ΔAUC = feat78 − feat15
    ba  = df[df['ApproachKey'] == 'feat15'][['Experiment', 'Model', 'AUC']]
    fa  = df[df['ApproachKey'] == 'feat78'][['Experiment', 'Model', 'AUC']]
    mg4 = fa.merge(ba, on=['Experiment', 'Model'], suffixes=('_63', '_15'))
    mg4['Delta_AUC'] = mg4['AUC_63'] - mg4['AUC_15']

    df = df.merge(mg [['Experiment', 'Model', 'Delta_R2']],    on=['Experiment', 'Model'], how='left')
    df = df.merge(mg2[['Experiment', 'Model', 'Delta_MAE']],   on=['Experiment', 'Model'], how='left')
    df = df.merge(mg3[['Experiment', 'Model', 'Delta_F1mac']], on=['Experiment', 'Model'], how='left')
    df = df.merge(mg4[['Experiment', 'Model', 'Delta_AUC']],   on=['Experiment', 'Model'], how='left')

    # ΔModeCI AUC (feat78 − feat15)
    ba_auc  = df[df['ApproachKey'] == 'feat15'][['Experiment', 'Model', 'AUC']]
    fa_auc  = df[df['ApproachKey'] == 'feat78'][['Experiment', 'Model', 'MCC']]
    mg5 = fa_auc.merge(df[df['ApproachKey'] == 'feat15'][['Experiment', 'Model', 'MCC']],
                        on=['Experiment', 'Model'], suffixes=('_63', '_15'))
    mg5['Delta_MCC'] = mg5['MCC_63'] - mg5['MCC_15']
    df = df.merge(mg5[['Experiment', 'Model', 'Delta_MCC']], on=['Experiment', 'Model'], how='left')
    return df


# ============================================================================
# FIGURE 1-3, 8-9 — Barplot double (feat15 vs feat78) par métrique
# ============================================================================
def plot_barplot_metric(df, metric, title, filename, figures_dir, lower_is_better=False):
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]
    n_exp  = len(exps)

    fig, axes = plt.subplots(1, n_exp, figsize=(3.8 * n_exp, 5.5), sharey=True)
    if n_exp == 1:
        axes = [axes]

    bar_w = 0.32
    x     = np.arange(len(models))

    for ax, exp in zip(axes, exps):
        for j, (ak, col) in enumerate([('feat15', C_BASE), ('feat78', C_FEAT)]):
            vals = []
            for mn in models:
                row = df[(df['ApproachKey'] == ak) &
                         (df['Experiment']  == exp) &
                         (df['Model']       == mn)]
                vals.append(float(row[metric].values[0]) if len(row) > 0 else 0.)

            offset = (j - 0.5) * bar_w
            bars   = ax.bar(x + offset, vals, bar_w, color=col,
                            edgecolor='white', alpha=0.92,
                            label=APPROACH_LABELS[ak] if exp == exps[0] else '_nolegend_')
            for bar, val in zip(bars, vals):
                if abs(val) > 0.001:
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + (max(abs(v) for v in vals) * 0.02),
                            f'{val:.3f}', ha='center', va='bottom',
                            fontsize=6, rotation=50, color='#2C3E50')

        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=40, ha='right', fontsize=7.5)
        ax.set_title(EXP_LABEL.get(exp, exp), fontsize=11, fontweight='bold')
        ax.set_ylabel(metric if ax == axes[0] else '')
        ax.grid(axis='y', alpha=0.35)

    handles = [mpatches.Patch(color=C_BASE, label=APPROACH_LABELS['feat15']),
               mpatches.Patch(color=C_FEAT, label=APPROACH_LABELS['feat78'])]
    fig.legend(handles=handles, loc='upper center', ncol=2,
               bbox_to_anchor=(0.5, 1.03), fontsize=10)
    fig.suptitle(title, fontsize=13, fontweight='bold', y=1.07)
    plt.tight_layout()
    plt.savefig(str(figures_dir / filename), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ {filename}")


# ============================================================================
# FIGURE 4 — Heatmap ΔR²
# ============================================================================
def plot_gain_heatmap(df, figures_dir):
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]

    pivot = pd.DataFrame(index=models, columns=exps, dtype=float)
    for exp in exps:
        for mn in models:
            row = df[(df['ApproachKey'] == 'feat78') &
                     (df['Experiment']  == exp) &
                     (df['Model']       == mn)]
            if not row.empty and not pd.isna(row['Delta_R2'].values[0]):
                pivot.loc[mn, exp] = round(float(row['Delta_R2'].values[0]), 4)

    pivot  = pivot.astype(float)
    valid  = pivot.values[~np.isnan(pivot.values)]
    vabs   = max(abs(valid).max(), 0.01) if len(valid) > 0 else 0.1

    fig, ax = plt.subplots(figsize=(len(exps) * 1.8 + 1.5, len(models) * 1.1 + 1.5))
    sns.heatmap(pivot, ax=ax, cmap='RdYlGn', center=0, vmin=-vabs, vmax=vabs,
                annot=True, fmt='.4f', annot_kws={'size': 11, 'weight': 'bold'},
                linewidths=0.6, linecolor='white',
                cbar_kws={'label': 'ΔR²  (feat78 − feat15)', 'shrink': 0.8})
    ax.set_title('Gain ΔR² : feat78 vs feat15\n🟢 feat78 mieux    🔴 feat15 mieux',
                 fontsize=12, fontweight='bold', pad=14)
    ax.set_xlabel("Expérience d'augmentation", fontsize=10)
    ax.set_ylabel('Régresseur', fontsize=10)
    plt.tight_layout()
    plt.savefig(str(figures_dir / '04_gain_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 04_gain_heatmap.png")


# ============================================================================
# FIGURE 5 — Radar (Exp FULL, meilleur modèle)
# ============================================================================
def plot_radar(df, figures_dir, exp_ref='FULL'):
    metrics_r = ['R2', 'F1_macro', 'AUC', 'MAE_inv', 'RMSE_inv']
    labels_r  = ['R²', 'F1 macro', 'AUC', '1/MAE', '1/RMSE']
    N         = len(metrics_r)
    angles    = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles   += angles[:1]

    df_r = df.copy()
    eps  = 1e-6
    df_r['MAE_inv']  = 1. / (df_r['MAE']  + eps)
    df_r['RMSE_inv'] = 1. / (df_r['RMSE'] + eps)

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    for ak, col, ls, lw in [('feat15', C_BASE, '--', 2.5), ('feat78', C_FEAT, '-', 2.5)]:
        label = APPROACH_LABELS[ak]
        sub   = df_r[(df_r['ApproachKey'] == ak) & (df_r['Experiment'] == exp_ref)]
        if sub.empty:
            sub = df_r[df_r['ApproachKey'] == ak]
            if sub.empty:
                continue
            sub = df_r[(df_r['ApproachKey'] == ak) &
                       (df_r['Experiment'] == sub['Experiment'].iloc[-1])]

        best_row = sub.loc[sub['R2'].idxmax()]

        norm_vals = []
        for mr in metrics_r:
            col_vals = df_r[mr].replace([np.inf, -np.inf], np.nan).dropna()
            mn_v, mx_v = col_vals.min(), col_vals.max()
            v = float(best_row[mr])
            norm_vals.append((v - mn_v) / (mx_v - mn_v + 1e-9))
        norm_vals += norm_vals[:1]

        ax.plot(angles, norm_vals, lw=lw, ls=ls, color=col,
                label=f"{label}\n({best_row['Model']})")
        ax.fill(angles, norm_vals, alpha=0.12, color=col)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels_r, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.50', '0.75', '1.00'], fontsize=7, color='gray')
    ax.grid(alpha=0.4)
    ax.set_title(f'Radar — R²  F1macro  AUC  (Exp {exp_ref}, LOSO)',
                 fontsize=11, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.4, 1.15), fontsize=9)
    plt.tight_layout()
    plt.savefig(str(figures_dir / '05_radar_FULL.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 05_radar_FULL.png")


# ============================================================================
# FIGURE 6 — Tableau synthèse
# ============================================================================
def plot_summary_table(df, figures_dir):
    exps    = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    records = []
    for exp in exps:
        for ak in ['feat15', 'feat78']:
            label = APPROACH_LABELS[ak]
            sub   = df[(df['ApproachKey'] == ak) & (df['Experiment'] == exp)]
            if sub.empty:
                continue
            best = sub.loc[sub['R2'].idxmax()]
            delta_r2 = (f"{best['Delta_R2']:+.4f}"
                        if ak == 'feat78' and not pd.isna(best.get('Delta_R2'))
                        else '—')
            records.append({
                'Exp':     exp,
                'Approche': label,
                'Modèle':   best['Model'],
                'MAE':      f"{best['MAE']:.4f}",
                'R²':       f"{best['R2']:.4f}",
                'F1mac':    f"{best['F1_macro']:.4f}",
                'AUC':      f"{best['AUC']:.4f}",
                'Acc':      f"{best['Accuracy']:.4f}",
                'ΔR²':      delta_r2,
            })

    df_tbl    = pd.DataFrame(records)
    col_labels = ['Exp', 'Approche', 'Modèle', 'MAE', 'R²', 'F1mac', 'AUC', 'Acc', 'ΔR²']
    n_rows     = len(df_tbl)

    fig, ax = plt.subplots(figsize=(18, max(3.5, n_rows * 0.55 + 1.5)))
    ax.axis('off')
    tbl = ax.table(cellText=df_tbl[col_labels].values.tolist(),
                   colLabels=col_labels, cellLoc='center', loc='center')
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)
    tbl.scale(1.1, 2.0)

    for col in range(len(col_labels)):
        tbl[(0, col)].set_facecolor('#1A3A4A')
        tbl[(0, col)].set_text_props(color='white', fontweight='bold')

    for row_idx, record in enumerate(df_tbl[col_labels].values.tolist(), start=1):
        bg = '#D6EAF8' if 'Baseline' in record[1] else '#D5F5E3'
        for col in range(len(col_labels)):
            tbl[(row_idx, col)].set_facecolor(bg)
        val_str = record[8]  # ΔR² column
        if val_str not in ('—', ''):
            try:
                v = float(val_str)
                tbl[(row_idx, 8)].set_text_props(
                    color=C_DELTA_POS if v >= 0 else C_DELTA_NEG, fontweight='bold')
            except ValueError:
                pass

    ax.set_title('Synthèse Régression — feat15 vs feat78  (LOSO  |  Low:0-5 / High:5-10)',
                 fontsize=12, fontweight='bold', pad=18)
    plt.tight_layout()
    plt.savefig(str(figures_dir / '06_summary_table.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 06_summary_table.png")


# ============================================================================
# FIGURE 7 — Meilleur modèle par expérience (R², MAE, RMSE)
# ============================================================================
def plot_best_per_exp(df, figures_dir):
    exps = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    x    = np.arange(len(exps))

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    for metric, ylabel, ax in [('R2', 'R² ↑', axes[0]),
                                ('MAE', 'MAE ↓', axes[1]),
                                ('RMSE', 'RMSE ↓', axes[2])]:
        for ak, col, marker, ls in [('feat15', C_BASE, 'o', '--'),
                                     ('feat78', C_FEAT, 's', '-')]:
            vals, bests = [], []
            for exp in exps:
                sub = df[(df['ApproachKey'] == ak) & (df['Experiment'] == exp)]
                if sub.empty:
                    vals.append(np.nan); bests.append('')
                else:
                    best_row = sub.loc[sub['R2'].idxmax()]
                    vals.append(float(best_row[metric]))
                    bests.append(best_row['Model'][:3])
            vals_arr = np.array(vals, dtype=float)
            ax.plot(x, vals_arr, marker=marker, ls=ls, lw=2.2,
                    color=col, label=APPROACH_LABELS[ak], markersize=9, zorder=3)
            ax.fill_between(x, vals_arr, alpha=0.08, color=col)
            for xi, (val, bm) in enumerate(zip(vals_arr, bests)):
                if not np.isnan(val) and bm:
                    ax.annotate(bm, xy=(xi, val), xytext=(0, 9),
                                textcoords='offset points',
                                ha='center', fontsize=7, color=col, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([EXP_LABEL.get(e, e) for e in exps], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_title(ylabel, fontsize=10, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.35)

    fig.suptitle('Évolution des performances — feat15 vs feat78 (Régression)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(str(figures_dir / '07_best_per_exp.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 07_best_per_exp.png")


# ============================================================================
# FIGURE 8 — F1 macro barplot
# ============================================================================
def plot_f1mac_barplot(df, figures_dir, target):
    plot_barplot_metric(df, 'F1_macro',
                        f'F1 Macro LOSO — feat15 vs feat78 ({target})  [Low:0-5 / High:5-10]',
                        '08_f1mac_barplot.png', figures_dir)


# ============================================================================
# FIGURE 9 — AUC barplot
# ============================================================================
def plot_auc_barplot(df, figures_dir, target):
    plot_barplot_metric(df, 'AUC',
                        f'AUC LOSO — feat15 vs feat78 ({target})  [Low:0-5 / High:5-10]',
                        '09_auc_barplot.png', figures_dir)


# ============================================================================
# RAPPORT TEXTE + LATEX
# ============================================================================
def generate_reports(df, out_dir, target):
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]

    has_binned   = df['F1_macro'].abs().sum() > 0
    has_prof     = df['AUC_CI_LO'].abs().sum() > 1e-4

    lines = [
        "=" * 110,
        f"NeuroCap — Régression feat15 (15f) vs feat78 (78f) — {target}",
        "=" * 110,
        "",
        "Protocole       : LOSO (Leave-One-Subject-Out)",
        "Classi. binée   : Low=0-5  /  High=5-10",
        "",
    ]

    if has_binned:
        if has_prof:
            hdr = (f"{'Approche':22s} {'Exp':6s} {'Modèle':16s} "
                   f"{'MAE':>8s} {'RMSE':>8s} {'R²':>8s} "
                   f"{'F1mac':>7s} {'AUC':>7s} {'Sens':>7s} {'Spec':>7s} "
                   f"{'MCC':>7s} {'ΔR²':>9s}")
            lines += [hdr, "─" * 110]
        else:
            hdr = (f"{'Approche':22s} {'Exp':6s} {'Modèle':16s} "
                   f"{'MAE':>8s} {'RMSE':>8s} {'R²':>8s} "
                   f"{'F1mac':>7s} {'AUC':>7s} {'Acc':>7s} {'ΔR²':>9s}")
            lines += [hdr, "─" * 90]
    else:
        hdr = (f"{'Approche':22s} {'Exp':6s} {'Modèle':16s} "
               f"{'MAE':>8s} {'RMSE':>8s} {'R²':>8s} {'ΔR²':>9s}")
        lines += [hdr, "─" * 72]

    for exp in exps:
        for ak in ['feat15', 'feat78']:
            label = APPROACH_LABELS[ak]
            for mn in models:
                row = df[(df['ApproachKey'] == ak) &
                         (df['Experiment']  == exp) &
                         (df['Model']       == mn)]
                if row.empty:
                    continue
                r     = row.iloc[0]
                delta = (f"{r['Delta_R2']:+.4f}"
                         if ak == 'feat78' and not pd.isna(r.get('Delta_R2'))
                         else '       —')
                if has_binned and has_prof:
                    lines.append(
                        f"{label:22s} {exp:6s} {mn:16s} "
                        f"{r['MAE']:>8.4f} {r['RMSE']:>8.4f} {r['R2']:>8.4f} "
                        f"{r['F1_macro']:>7.4f} {r['AUC']:>7.4f} "
                        f"{r['Sensitivity']:>7.4f} {r['Specificity']:>7.4f} "
                        f"{r['MCC']:>7.4f} "
                        f"{delta:>9s}"
                    )
                elif has_binned:
                    lines.append(
                        f"{label:22s} {exp:6s} {mn:16s} "
                        f"{r['MAE']:>8.4f} {r['RMSE']:>8.4f} {r['R2']:>8.4f} "
                        f"{r['F1_macro']:>7.4f} {r['AUC']:>7.4f} {r['Accuracy']:>7.4f} "
                        f"{delta:>9s}"
                    )
                else:
                    lines.append(
                        f"{label:22s} {exp:6s} {mn:16s} "
                        f"{r['MAE']:>8.4f} {r['RMSE']:>8.4f} {r['R2']:>8.4f} {delta:>9s}"
                    )
        lines.append("")

    # Meilleurs
    lines += ["=" * 90, "MEILLEURS MODÈLES (par R²)", "=" * 90]
    for ak in ['feat15', 'feat78']:
        label = APPROACH_LABELS[ak]
        sub   = df[df['ApproachKey'] == ak]
        if sub.empty:
            continue
        best = sub.loc[sub['R2'].idxmax()]
        line = (f"  {label:22s} → {best['Model']:16s} | Exp {best['Experiment']} | "
                f"MAE={best['MAE']:.4f}  R²={best['R2']:.4f}")
        if has_binned:
            line += f"  F1mac={best['F1_macro']:.4f}  AUC={best['AUC']:.4f}"
        lines.append(line)

    if has_binned:
        lines += ["", "MEILLEURS MODÈLES (par AUC)", "─" * 50]
        for ak in ['feat15', 'feat78']:
            label = APPROACH_LABELS[ak]
            sub   = df[df['ApproachKey'] == ak]
            if sub.empty:
                continue
            best_auc = sub.loc[sub['AUC'].idxmax()]
            line = (f"  {label:22s} → {best_auc['Model']:16s} | Exp {best_auc['Experiment']} | "
                    f"AUC={best_auc['AUC']:.4f}  F1mac={best_auc['F1_macro']:.4f}  R²={best_auc['R2']:.4f}")
            if has_prof:
                line += (f"  Sens={best_auc['Sensitivity']:.4f}  Spec={best_auc['Specificity']:.4f}"
                         f"  MCC={best_auc['MCC']:.4f}")
            lines.append(line)

    if has_prof:
        lines += ["", "MÉTRIQUES PROFESSIONNELLES (meilleur R²)", "─" * 50]
        for ak in ['feat15', 'feat78']:
            label = APPROACH_LABELS[ak]
            sub   = df[df['ApproachKey'] == ak]
            if sub.empty:
                continue
            best = sub.loc[sub['R2'].idxmax()]
            lines.append(
                f"  {label:22s} → {best['Model']:16s} | Exp {best['Experiment']}\n"
                f"    Sensitivity={best['Sensitivity']:.4f}  Specificity={best['Specificity']:.4f}"
                f"  MCC={best['MCC']:.4f}  PR-AUC={best['PR_AUC']:.4f}\n"
                f"    AUC CI 95% = [{best['AUC_CI_LO']:.4f}, {best['AUC_CI_HI']:.4f}]"
                f"  p={best['AUC_Pvalue']:.4f}"
                f"  {'✅ sig.' if best['AUC_Pvalue'] < 0.05 else '❌ ns'}\n"
                f"    ECE={best['ECE']:.4f}  Bland-bias={best['Bland_Bias']:+.4f}"
                f"  ICC={best['ICC']:.3f}"
            )

    b_best = df[df['ApproachKey'] == 'feat15']['R2'].max()
    f_best = df[df['ApproachKey'] == 'feat78']['R2'].max()
    delta  = f_best - b_best
    winner = 'feat78 (Feature Engineering Avancé)' if delta > 0 else 'feat15 (Baseline léger)'
    lines += [
        "",
        f"  ΔR² global (feat78 − feat15) : {delta:+.4f}",
        f"  → Approche recommandée (R²)  : {winner}",
    ]
    if abs(delta) < 0.02:
        lines.append("  ⚠️  Gain < 0.02 : les deux approches sont équivalentes.")
        lines.append("     Préférer feat15 pour la latence embarquée (< 40 ms).")
    lines.append("=" * 90)

    report_text = "\n".join(lines)
    (out_dir / f'comparison_summary_{target}.txt').write_text(report_text, encoding='utf-8')
    print(f"  ✅ comparison_summary_{target}.txt")
    print("\n" + report_text)

    # LaTeX
    latex = [
        r"\begin{table}[htbp]",
        r"\centering",
        rf"\caption{{Régression LOSO : feat15 vs feat78 — {target}  (Low:0--5 / High:5--10)}}",
        rf"\label{{tab:regression_{target}}}",
        r"\small",
    ]
    if has_binned:
        latex += [r"\begin{tabular}{llccccccc}", r"\hline",
                  r"\textbf{Approche} & \textbf{Exp} & \textbf{Modèle} & "
                  r"\textbf{MAE} & \textbf{R²} & \textbf{F1mac} & \textbf{AUC} & \textbf{Acc} & "
                  r"$\boldsymbol{\Delta}$\textbf{R²} \\", r"\hline"]
    else:
        latex += [r"\begin{tabular}{llccccc}", r"\hline",
                  r"\textbf{Approche} & \textbf{Exp} & \textbf{Modèle} & "
                  r"\textbf{MAE} & \textbf{RMSE} & \textbf{R²} & "
                  r"$\boldsymbol{\Delta}$\textbf{R²} \\", r"\hline"]

    for exp in exps:
        for ak in ['feat15', 'feat78']:
            lshort = '15f' if ak == 'feat15' else '78f'
            for mn in models:
                row = df[(df['ApproachKey'] == ak) &
                         (df['Experiment']  == exp) &
                         (df['Model']       == mn)]
                if row.empty:
                    continue
                r = row.iloc[0]
                delta_str = (f"{r['Delta_R2']:+.4f}"
                             if ak == 'feat78' and not pd.isna(r.get('Delta_R2'))
                             else '--')
                if has_binned:
                    latex.append(
                        f"{lshort} & {exp} & {mn} & "
                        f"{r['MAE']:.4f} & {r['R2']:.4f} & "
                        f"{r['F1_macro']:.4f} & {r['AUC']:.4f} & {r['Accuracy']:.4f} & "
                        f"{delta_str} \\\\"
                    )
                else:
                    latex.append(
                        f"{lshort} & {exp} & {mn} & "
                        f"{r['MAE']:.4f} & {r['RMSE']:.4f} & {r['R2']:.4f} & {delta_str} \\\\"
                    )
        latex.append(r"\hline")
    latex += [r"\end{tabular}", r"\end{table}"]
    (out_dir / f'comparison_latex_{target}.txt').write_text("\n".join(latex), encoding='utf-8')
    print(f"  ✅ comparison_latex_{target}.txt")


# ============================================================================
# FIGURES PROFESSIONNELLES (Niveaux 1-5)
# ============================================================================

def plot_sensitivity_specificity(df, figures_dir, target):
    """Figure 10 — Sensitivity vs Specificity barplot double."""
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]
    n_exp  = len(exps)

    fig, axes = plt.subplots(2, n_exp, figsize=(3.5 * n_exp, 8))
    if n_exp == 1:
        axes = axes.reshape(2, 1)

    for row_idx, (metric, ylabel) in enumerate([('Sensitivity', 'Sensitivity (TPR)'),
                                                 ('Specificity', 'Specificity (TNR)')]):
        for col_idx, exp in enumerate(exps):
            ax = axes[row_idx, col_idx]
            x  = np.arange(len(models))
            for j, (ak, col) in enumerate([('feat15', C_BASE), ('feat78', C_FEAT)]):
                vals = []
                for mn in models:
                    row = df[(df['ApproachKey'] == ak) &
                             (df['Experiment']  == exp) &
                             (df['Model']       == mn)]
                    vals.append(float(row[metric].values[0]) if len(row) > 0 else 0.)
                offset = (j - 0.5) * 0.3
                ax.bar(x + offset, vals, 0.3, color=col, alpha=0.85, edgecolor='white',
                       label=APPROACH_LABELS[ak] if (row_idx == 0 and col_idx == 0) else '_nolegend_')
            ax.axhline(0.5, color='gray', lw=1, ls='--', alpha=0.6)
            ax.set_xticks(x); ax.set_xticklabels(models, rotation=40, ha='right', fontsize=7)
            ax.set_ylim(0, 1.1); ax.set_ylabel(ylabel if col_idx == 0 else '')
            ax.set_title(EXP_LABEL.get(exp, exp) if row_idx == 0 else '')
            ax.grid(axis='y', alpha=0.3)

    handles = [mpatches.Patch(color=C_BASE, label=APPROACH_LABELS['feat15']),
               mpatches.Patch(color=C_FEAT, label=APPROACH_LABELS['feat78'])]
    fig.legend(handles=handles, loc='upper center', ncol=2,
               bbox_to_anchor=(0.5, 1.02), fontsize=10)
    fig.suptitle(f'Sensitivity & Specificity — feat15 vs feat78 ({target})',
                 fontsize=12, fontweight='bold', y=1.04)
    plt.tight_layout()
    plt.savefig(str(figures_dir / '10_sensitivity_spec.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 10_sensitivity_spec.png")


def plot_mcc_barplot(df, figures_dir, target):
    """Figure 11 — MCC barplot avec hachures ΔMcc."""
    plot_barplot_metric(df, 'MCC',
                        f'MCC (Matthews Correlation Coefficient) — feat15 vs feat78 ({target})',
                        '11_mcc_barplot.png', figures_dir)


def plot_ece_icc_comparison(df, figures_dir, target):
    """Figure 12 — ECE (calibration) et ICC (fiabilité) par modèle."""
    if df['ECE'].abs().sum() < 1e-4:
        print("  [SKIP] 12_ece_icc.png — ECE non disponible")
        return

    models   = [m for m in MODEL_NAMES if m in df['Model'].unique()]
    best_exp = df.loc[df['AUC'].idxmax(), 'Experiment'] if not df.empty else 'A'

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    x = np.arange(len(models))

    for ax, (metric, ylabel, threshold, thr_label, lower_better) in zip(axes, [
        ('ECE', 'ECE ↓ (≤0.05 = bien calibré)', 0.05, 'Seuil acceptable (0.05)', True),
        ('ICC', 'ICC ↑ (≥0.90 = excellent)',      0.90, 'Seuil excellent (0.90)', False),
    ]):
        for j, (ak, col) in enumerate([('feat15', C_BASE), ('feat78', C_FEAT)]):
            vals = []
            for mn in models:
                row = df[(df['ApproachKey']==ak)&(df['Experiment']==best_exp)&(df['Model']==mn)]
                vals.append(float(row[metric].values[0]) if not row.empty else 0.)
            offset = (j - 0.5) * 0.35
            bars = ax.bar(x + offset, vals, 0.35, color=col, alpha=0.85,
                          edgecolor='white', label=APPROACH_LABELS[ak])
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x()+bar.get_width()/2, v+0.005,
                        f'{v:.3f}', ha='center', va='bottom', fontsize=7, fontweight='bold')
        ls = '--' if lower_better else '-.'
        ax.axhline(threshold, color='green', lw=1.5, ls=ls, label=thr_label)
        ax.set_xticks(x); ax.set_xticklabels(models, rotation=30, ha='right', fontsize=9)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.set_title(f'{metric} — {target}  (Exp.{best_exp})', fontsize=10, fontweight='bold')
        ax.legend(fontsize=8); ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(str(figures_dir / '12_ece_icc.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 12_ece_icc.png")


def plot_auc_bootstrap_ci(df, figures_dir, target):
    """Figure 13 — AUC avec barres d'erreur Bootstrap 95% CI + p-value."""
    if df['AUC_CI_LO'].abs().sum() < 1e-4:
        print("  [SKIP] 13_auc_bootstrap_ci.png — Bootstrap CI non disponible")
        return

    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]
    best_exp = df.loc[df['AUC'].idxmax(), 'Experiment'] if not df.empty else exps[-1]

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(models))

    for j, (ak, col) in enumerate([('feat15', C_BASE), ('feat78', C_FEAT)]):
        vals, err_lo, err_hi, pvals = [], [], [], []
        for mn in models:
            row = df[(df['ApproachKey'] == ak) &
                     (df['Experiment']  == best_exp) &
                     (df['Model']       == mn)]
            if len(row) > 0:
                r = row.iloc[0]
                vals.append(float(r['AUC']))
                err_lo.append(max(0, float(r['AUC']) - float(r['AUC_CI_LO'])))
                err_hi.append(max(0, float(r['AUC_CI_HI']) - float(r['AUC'])))
                pvals.append(float(r['AUC_Pvalue']))
            else:
                vals.append(0.); err_lo.append(0.); err_hi.append(0.); pvals.append(1.)

        offset = (j - 0.5) * 0.35
        bars   = ax.bar(x + offset, vals, 0.35, color=col, alpha=0.8,
                        edgecolor='white', label=APPROACH_LABELS[ak],
                        yerr=[err_lo, err_hi], capsize=5,
                        error_kw={'lw': 2, 'color': '#2C3E50'})

        for bar, v, p in zip(bars, vals, pvals):
            sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
            col_t = '#27AE60' if p < 0.05 else '#E74C3C'
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.02,
                    sig, ha='center', va='bottom', fontsize=9,
                    color=col_t, fontweight='bold')

    ax.axhline(0.5, color='gray', lw=1.5, ls='--', label='Baseline aléatoire (0.50)')
    ax.set_xticks(x); ax.set_xticklabels(models, rotation=30, ha='right', fontsize=9)
    ax.set_ylim(0.2, 1.05); ax.set_ylabel('AUC ROC ± 95% CI (Bootstrap)')
    ax.set_title(f'AUC ROC + Bootstrap 95% CI — {target}  (Exp.{best_exp})\n'
                 f'*=p<0.05  **=p<0.01  ***=p<0.001  ns=non significatif')
    ax.legend(fontsize=9); ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(figures_dir / '13_auc_bootstrap_ci.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 13_auc_bootstrap_ci.png")


# ============================================================================
# FIGURE 00 — DASHBOARD GLOBAL (vue d'ensemble par état cognitif)
# ============================================================================
def plot_global_overview(df, figures_dir, target):
    """Figure 00 — Dashboard feat15 vs feat78 : toutes métriques clés en 1 image."""
    exps    = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models  = [m for m in MODEL_NAMES  if m in df['Model'].unique()]
    exp_ref = 'FULL' if 'FULL' in exps else exps[-1]

    fig = plt.figure(figsize=(22, 16))
    gs  = fig.add_gridspec(3, 5, hspace=0.56, wspace=0.40,
                           top=0.90, bottom=0.06, left=0.06, right=0.97)

    fig.suptitle(
        f'NeuroCap — feat15 vs feat78  |  {target.upper()}  |  LOSO\n'
        f'Exp. {exp_ref}  —  Low : 0-5 / High : 5-10',
        fontsize=14, fontweight='bold'
    )

    # ── Ligne 1 : 5 métriques clés (barplot feat15 vs feat78, Exp ref) ──────
    bar_w = 0.30
    metrics_row1 = [
        ('MAE',         'MAE ↓'),
        ('R2',          'R² ↑'),
        ('AUC',         'AUC ↑'),
        ('Sensitivity', 'Sensitivity ↑'),
        ('MCC',         'MCC ↑'),
    ]
    for col_i, (metric, ylabel) in enumerate(metrics_row1):
        ax = fig.add_subplot(gs[0, col_i])
        x  = np.arange(len(models))
        for j, (ak, col) in enumerate([('feat15', C_BASE), ('feat78', C_FEAT)]):
            vals = []
            for mn in models:
                row = df[(df['ApproachKey']==ak)&(df['Experiment']==exp_ref)&(df['Model']==mn)]
                vals.append(float(row[metric].values[0]) if not row.empty else 0.)
            offset = (j - 0.5) * bar_w
            bars   = ax.bar(x + offset, vals, bar_w, color=col, alpha=0.88, edgecolor='white',
                            label=APPROACH_LABELS[ak] if col_i == 0 else '_nolegend_')
            vmax = max(abs(v) for v in vals) if vals else 1.
            for bar, v in zip(bars, vals):
                if abs(v) > 0.005:
                    ax.text(bar.get_x()+bar.get_width()/2,
                            bar.get_height() + vmax*0.03,
                            f'{v:.3f}', ha='center', va='bottom',
                            fontsize=5, rotation=55, color='#2C3E50')
        ax.set_xticks(x)
        ax.set_xticklabels([m[:3] for m in models], fontsize=7)
        ax.set_title(ylabel, fontsize=9, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

    handles = [mpatches.Patch(color=C_BASE, label=APPROACH_LABELS['feat15']),
               mpatches.Patch(color=C_FEAT, label=APPROACH_LABELS['feat78'])]
    fig.legend(handles=handles, loc='upper right',
               bbox_to_anchor=(0.97, 0.93), fontsize=9, ncol=2)

    # ── Ligne 2 : ΔR² heatmap (3 cols) + Radar (2 cols) ────────────────────
    ax_heat = fig.add_subplot(gs[1, :3])
    pivot   = pd.DataFrame(index=models, columns=exps, dtype=float)
    for exp in exps:
        for mn in models:
            row = df[(df['ApproachKey']=='feat78')&(df['Experiment']==exp)&(df['Model']==mn)]
            if not row.empty and 'Delta_R2' in row.columns:
                v = row['Delta_R2'].values[0]
                pivot.loc[mn, exp] = round(float(v), 4) if not pd.isna(v) else np.nan
    pivot = pivot.astype(float)
    valid = pivot.values[~np.isnan(pivot.values)]
    vabs  = max(abs(valid).max(), 0.01) if len(valid) > 0 else 0.1
    sns.heatmap(pivot, ax=ax_heat, cmap='RdYlGn', center=0, vmin=-vabs, vmax=vabs,
                annot=True, fmt='.4f', annot_kws={'size': 10, 'weight': 'bold'},
                linewidths=0.5, linecolor='white',
                cbar_kws={'label': 'ΔR²  (feat78−feat15)', 'shrink': 0.8})
    ax_heat.set_title('ΔR²  feat78 − feat15   |   🟢 feat78 mieux   🔴 feat15 mieux',
                      fontsize=10, fontweight='bold', pad=10)

    ax_rad = fig.add_subplot(gs[1, 3:], projection='polar')
    metrics_r = ['R2', 'F1_macro', 'AUC', 'MAE_inv', 'Sensitivity']
    labels_r  = ['R²', 'F1mac', 'AUC', '1/MAE', 'Sens']
    N      = len(metrics_r)
    angles = np.linspace(0, 2*np.pi, N, endpoint=False).tolist() + [0]
    df_r   = df.copy()
    df_r['MAE_inv'] = 1. / (df_r['MAE'] + 1e-6)
    for ak, col, ls in [('feat15', C_BASE, '--'), ('feat78', C_FEAT, '-')]:
        sub = df_r[(df_r['ApproachKey']==ak)&(df_r['Experiment']==exp_ref)]
        if sub.empty:
            continue
        best_row  = sub.loc[sub['R2'].idxmax()]
        norm_vals = []
        for mr in metrics_r:
            col_all  = df_r[mr].replace([np.inf, -np.inf], np.nan).dropna()
            mn_v, mx_v = col_all.min(), col_all.max()
            norm_vals.append((float(best_row[mr]) - mn_v) / (mx_v - mn_v + 1e-9))
        norm_vals += norm_vals[:1]
        ax_rad.plot(angles, norm_vals, lw=2.2, ls=ls, color=col,
                    label=f"{APPROACH_LABELS[ak]} ({best_row['Model'][:3]})")
        ax_rad.fill(angles, norm_vals, alpha=0.12, color=col)
    ax_rad.set_xticks(angles[:-1])
    ax_rad.set_xticklabels(labels_r, fontsize=8)
    ax_rad.set_ylim(0, 1)
    ax_rad.set_yticks([0.5, 1.0])
    ax_rad.set_yticklabels(['0.5', '1.0'], fontsize=6, color='gray')
    ax_rad.grid(alpha=0.4)
    ax_rad.set_title(f'Radar (Exp {exp_ref})', fontsize=9, fontweight='bold', pad=15)
    ax_rad.legend(loc='upper right', bbox_to_anchor=(1.6, 1.15), fontsize=7)

    # ── Ligne 3 : évolution MAE/R²/AUC par expérience (3 cols) + Deploy (2 cols) ─
    for col_i, (metric, ylabel) in enumerate([('MAE','MAE ↓'),('R2','R² ↑'),('AUC','AUC ↑')]):
        ax = fig.add_subplot(gs[2, col_i])
        x  = np.arange(len(exps))
        for ak, col, mk, ls in [('feat15',C_BASE,'o','--'),('feat78',C_FEAT,'s','-')]:
            vals, bests = [], []
            for exp in exps:
                sub = df[(df['ApproachKey']==ak)&(df['Experiment']==exp)]
                if sub.empty:
                    vals.append(np.nan); bests.append('')
                else:
                    br = sub.loc[sub['R2'].idxmax()]
                    vals.append(float(br[metric])); bests.append(br['Model'][:3])
            va = np.array(vals, dtype=float)
            ax.plot(x, va, marker=mk, ls=ls, lw=2, color=col, markersize=7,
                    label=APPROACH_LABELS[ak], zorder=3)
            ax.fill_between(x, va, alpha=0.07, color=col)
            for xi, (v, b) in enumerate(zip(va, bests)):
                if not np.isnan(v) and b:
                    ax.annotate(b, xy=(xi, v), xytext=(0, 7),
                                textcoords='offset points',
                                ha='center', fontsize=6, color=col, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels([EXP_LABEL.get(e, e) for e in exps], fontsize=7)
        ax.set_ylabel(ylabel, fontsize=8)
        ax.set_title(f'Évolution {ylabel}', fontsize=8, fontweight='bold')
        ax.legend(fontsize=6); ax.grid(alpha=0.3)

    ax_dep = fig.add_subplot(gs[2, 3:])
    if df['ECE'].abs().sum() > 1e-4:
        x = np.arange(len(models))
        for j, (ak, col) in enumerate([('feat15', C_BASE), ('feat78', C_FEAT)]):
            vals = []
            for mn in models:
                row = df[(df['ApproachKey']==ak)&(df['Experiment']==exp_ref)&(df['Model']==mn)]
                vals.append(float(row['ECE'].values[0]) if not row.empty else 0.)
            offset = (j - 0.5) * 0.32
            bars = ax_dep.bar(x + offset, vals, 0.32, color=col, alpha=0.85,
                              edgecolor='white', label=APPROACH_LABELS[ak])
            for bar, v in zip(bars, vals):
                ax_dep.text(bar.get_x()+bar.get_width()/2, v+0.003,
                            f'{v:.3f}', ha='center', va='bottom',
                            fontsize=7, fontweight='bold')
        ax_dep.axhline(0.05, color='#27AE60', lw=1.5, ls='--', label='Seuil ECE (0.05)')
        ax_dep.set_xticks(x)
        ax_dep.set_xticklabels([m[:4] for m in models], fontsize=7)
        ax_dep.set_ylabel('ECE ↓', fontsize=8)
        ax_dep.set_title('Calibration ECE\n(Guo et al. 2017)', fontsize=8, fontweight='bold')
        ax_dep.legend(fontsize=6); ax_dep.grid(axis='y', alpha=0.3)
    else:
        ax_dep.axis('off')
        ax_dep.text(0.5, 0.5, 'ECE\nnon disponible',
                    ha='center', va='center', fontsize=10, color='gray',
                    transform=ax_dep.transAxes)

    plt.savefig(str(figures_dir / '00_global_overview.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 00_global_overview.png")


# ============================================================================
# DECISION DASHBOARD — métriques de décision clinique
# ============================================================================
_DECISION_METRICS = [
    ('AUC',          'AUC ROC',          0.65, 0.55),
    ('Sensitivity',  'Sensitivity',       0.50, 0.40),
    ('Specificity',  'Specificity',       0.50, 0.40),
    ('MCC',          'MCC',               0.20, 0.10),
    ('Balanced_Acc', 'Balanced Accuracy', 0.65, 0.55),
]

def plot_decision_dashboard(df, figures_dir, target):
    """
    Image unique : 5 métriques de décision (AUC, Sens, Spec, MCC, BalAcc)
    + tableau pass/fail couleur pour chaque modèle et approche.
    """
    exps    = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    exp_ref = 'FULL' if 'FULL' in exps else exps[-1]
    models  = [m for m in MODEL_NAMES if m in df['Model'].unique()]

    def _bar_color(v, good_t, border_t):
        if v >= good_t:    return '#27AE60'
        if v >= border_t:  return '#F39C12'
        return '#E74C3C'

    fig = plt.figure(figsize=(24, 14))
    gs  = fig.add_gridspec(2, 5, height_ratios=[1.5, 1.0],
                           hspace=0.55, wspace=0.38,
                           top=0.88, bottom=0.04, left=0.04, right=0.97)
    fig.suptitle(
        f'Dashboard Décision — feat15 vs feat78  |  {target.upper()}  |  Exp. {exp_ref}\n'
        f'Ordre priorité : AUC (GO/NO-GO)  →  Sensitivity  →  MCC  →  Décision finale',
        fontsize=13, fontweight='bold'
    )

    # ── Ligne 1 : barplots par métrique ────────────────────────────────────
    for ci, (metric, label, good_t, border_t) in enumerate(_DECISION_METRICS):
        ax  = fig.add_subplot(gs[0, ci])
        x   = np.arange(len(models))
        bw  = 0.33

        for ji, (ak, base_col) in enumerate([('feat15', C_BASE), ('feat78', C_FEAT)]):
            vals = []
            for mn in models:
                r = df[(df['ApproachKey']==ak)&(df['Experiment']==exp_ref)&(df['Model']==mn)]
                vals.append(float(r[metric].values[0]) if not r.empty else 0.)
            colors = [_bar_color(v, good_t, border_t) for v in vals]
            offs   = (ji - 0.5) * bw
            bars   = ax.bar(x + offs, vals, bw, color=colors, alpha=0.88,
                            edgecolor='white',
                            label=APPROACH_LABELS[ak] if ci == 0 else '_nolegend_')
            for bar, v in zip(bars, vals):
                ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                        f'{v:.2f}', ha='center', va='bottom', fontsize=6.5, fontweight='bold')

        ax.axhline(good_t,   color='#27AE60', lw=1.8, ls='--', alpha=0.85)
        ax.axhline(border_t, color='#F39C12', lw=1.2, ls=':',  alpha=0.70)
        ax.set_xticks(x)
        ax.set_xticklabels([m[:4] for m in models], rotation=38, ha='right', fontsize=7)
        ax.set_ylim(0, 1.18)
        ax.set_title(f'{label} ↑', fontsize=9, fontweight='bold')
        ax.grid(axis='y', alpha=0.25)

    # Légende globale
    legend_patches = [
        mpatches.Patch(color='#27AE60', label='✅ Bon (≥ seuil vert)'),
        mpatches.Patch(color='#F39C12', label='⚠️ Borderline'),
        mpatches.Patch(color='#E74C3C', label='❌ Insuffisant'),
        mpatches.Patch(color=C_BASE,    label=APPROACH_LABELS['feat15']),
        mpatches.Patch(color=C_FEAT,    label=APPROACH_LABELS['feat78']),
    ]
    fig.legend(handles=legend_patches, loc='upper right',
               bbox_to_anchor=(0.97, 0.94), fontsize=8, ncol=5,
               framealpha=0.9)

    # ── Ligne 2 : tableau de décision ──────────────────────────────────────
    ax_tbl = fig.add_subplot(gs[1, :])
    ax_tbl.axis('off')
    ax_tbl.set_title(
        'Seuils : AUC≥0.65 | Sensitivity≥0.50 | Specificity≥0.50 | MCC≥0.20 | Bal.Acc≥0.65   '
        '(vert=bon · orange=borderline · rouge=insuffisant)',
        fontsize=8.5, fontweight='bold', pad=6
    )

    headers = ['Approche', 'Modèle', 'AUC ROC', 'Sensitivity', 'Specificity', 'MCC', 'Bal.Acc', 'DÉCISION']
    tbl_rows, tbl_colors = [], []

    for ak in ['feat15', 'feat78']:
        lbl = APPROACH_LABELS[ak]
        for mn in models:
            row_data = [lbl, mn]
            row_col  = ['#ECF0F1', '#ECF0F1']
            n_good = 0
            for metric, _, good_t, border_t in _DECISION_METRICS:
                r = df[(df['ApproachKey']==ak)&(df['Experiment']==exp_ref)&(df['Model']==mn)]
                v = float(r[metric].values[0]) if not r.empty else 0.
                row_data.append(f'{v:.3f}')
                if v >= good_t:
                    row_col.append('#D5F5E3'); n_good += 1
                elif v >= border_t:
                    row_col.append('#FDEBD0')
                else:
                    row_col.append('#FADBD8')
            if n_good >= 4:
                decision, dcol = '✅ Recommandé', '#D5F5E3'
            elif n_good >= 2:
                decision, dcol = '⚠️ Acceptable', '#FDEBD0'
            else:
                decision, dcol = '❌ Rejeté',     '#FADBD8'
            row_data.append(decision); row_col.append(dcol)
            tbl_rows.append(row_data); tbl_colors.append(row_col)

    tbl = ax_tbl.table(cellText=tbl_rows, colLabels=headers,
                       cellLoc='center', loc='center', bbox=[0, 0, 1, 1],
                       cellColours=tbl_colors)
    tbl.auto_set_font_size(False); tbl.set_fontsize(8.5)
    for col in range(len(headers)):
        tbl[(0, col)].set_facecolor('#1A3A4A')
        tbl[(0, col)].set_text_props(color='white', fontweight='bold')

    plt.savefig(str(figures_dir / 'decision_dashboard.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ decision_dashboard.png")


# ============================================================================
# MAIN
# ============================================================================
def run_target(target):
    print(f"\n{'='*65}")
    print(f"TARGET : {target.upper()}")
    print(f"{'='*65}")

    json15 = FEAT15_ROOT / target / f'results_{target}.json'
    json63 = FEAT63_ROOT / target / f'results_{target}.json'

    try:
        data15 = load_json(json15, f'baseline_ML_regression ({target})')
        data63 = load_json(json63, f'baseline_ML_regression_feature_eng ({target})')
    except FileNotFoundError as e:
        print(e)
        return

    m15 = extract_metrics(data15)
    m63 = extract_metrics(data63)

    if not m15 or not m63:
        print(f"❌ Données LOSO vides pour {target}.")
        return

    df = build_dataframe(m15, m63)

    out_dir     = OUT_ROOT / target
    figures_dir = out_dir / 'figures'
    out_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_dir / f'comparison_table_{target}.csv',
              index=False, float_format='%.4f')
    print(f"\n  ✅ comparison_table_{target}.csv ({len(df)} lignes)")

    print("\n── Figure globale ──")
    plot_global_overview(df, figures_dir, target)

    print("\n── Génération des figures (métriques classiques) ──")
    plot_barplot_metric(df, 'MAE',  f'MAE LOSO — feat15 vs feat78 ({target})',
                        '01_mae_barplot.png',  figures_dir, lower_is_better=True)
    plot_barplot_metric(df, 'R2',   f'R² LOSO — feat15 vs feat78 ({target})',
                        '02_r2_barplot.png',   figures_dir)
    plot_barplot_metric(df, 'RMSE', f'RMSE LOSO — feat15 vs feat78 ({target})',
                        '03_rmse_barplot.png', figures_dir, lower_is_better=True)
    plot_gain_heatmap(df, figures_dir)
    plot_radar(df, figures_dir)
    plot_summary_table(df, figures_dir)
    plot_best_per_exp(df, figures_dir)
    plot_f1mac_barplot(df, figures_dir, target)
    plot_auc_barplot(df, figures_dir, target)

    print("\n── Génération des figures (métriques professionnelles) ──")
    plot_sensitivity_specificity(df, figures_dir, target)
    plot_mcc_barplot(df, figures_dir, target)
    plot_ece_icc_comparison(df, figures_dir, target)
    plot_auc_bootstrap_ci(df, figures_dir, target)

    print("\n── Dashboard de décision ──")
    plot_decision_dashboard(df, figures_dir, target)

    print(f"\n── Rapports ──")
    generate_reports(df, out_dir, target)


def main():
    print("=" * 65)
    print("NeuroCap — Comparaison feat15 vs feat78 (Régression)")
    print("(lecture des results.json, sans ré-entraînement)")
    print("=" * 65)

    for target in TARGETS:
        run_target(target)

    print(f"\n{'='*65}")
    print(f"✅ Comparaison terminée")
    print(f"   {OUT_ROOT.relative_to(PROJECT_ROOT)}/")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()
