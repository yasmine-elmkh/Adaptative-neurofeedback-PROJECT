"""
=============================================================================
NeuroCap — Comparaison Globale Baselines ML (Régression)
compare_baseline_global.py
=============================================================================
Charge les 4 approches × 5 modèles × 2 cibles × 5 expériences et produit
une comparaison unifiée avec score composite AUC/Sensitivity/MCC/Specificity.

4 APPROCHES :
  feat15        baseline_ML_regression.py
  feat15_smote  baseline_ML_regression_smote.py
  feat78        baseline_ML_regression_feature_eng.py
  feat78_smote  baseline_ML_regression_feature_eng_smote.py

5 MODÈLES : SVR | Random Forest | XGBoost | LightGBM | Stacking

SCORE COMPOSITE (sélection modèle) :
  0.40 × AUC  +  0.30 × Sensitivity  +  0.20 × MCC  +  0.10 × Specificity

SORTIES :
  reports/Regression/Baseline/Global_Comparison/{conc,stress}/
    01_ranking_composite.png        ← Top-20 combinations
    02_heatmap_approach_model.png   ← Heatmap 4×5 par métrique
    03_barplot_auc.png              ← AUC par modèle et approche
    04_barplot_sensitivity.png
    05_barplot_specificity.png
    06_barplot_mcc.png
    07_barplot_mae.png
    08_barplot_r2.png
    09_decision_dashboard.png       ← Tableau pass/fail 20 combinaisons
    10_radar_top5.png               ← Radar des 5 meilleures combinaisons
    11_boxplot_per_model.png        ← Distribution composite sur 5 expériences
    global_results_{target}.csv
  global_summary.txt                ← Résumé écrit
=============================================================================
"""

import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')

# ─── Chemins ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]
BASE_ROOT    = PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline'
OUT_ROOT     = BASE_ROOT / 'Global_Comparison'
OUT_ROOT.mkdir(parents=True, exist_ok=True)

APPROACH_ROOTS = {
    'feat15':       BASE_ROOT / 'feat15',
    'feat15_smote': BASE_ROOT / 'feat15_smote',
    'feat78':       BASE_ROOT / 'feat78',
    'feat78_smote': BASE_ROOT / 'feat78_smote',
}
APPROACH_LABELS = {
    'feat15':       'Baseline\n(15f)',
    'feat15_smote': 'SMOTE\n(15f)',
    'feat78':       'FeatEng\n(78f)',
    'feat78_smote': 'SMOTE+\n(78f)',
}
APPROACH_COLORS = {
    'feat15':       '#AED6F1',
    'feat15_smote': '#1A5276',
    'feat78':       '#A9DFBF',
    'feat78_smote': '#1E8449',
}

MODEL_NAMES = ['SVR', 'Random Forest', 'XGBoost', 'LightGBM', 'Stacking']
MODEL_COLORS = {
    'SVR':           '#E74C3C',
    'Random Forest': '#2980B9',
    'XGBoost':       '#27AE60',
    'LightGBM':      '#F39C12',
    'Stacking':      '#8E44AD',
}

TARGETS     = ['conc', 'stress']
EXPERIMENTS = ['A', 'B', 'C', 'D', 'FULL']

# Seuils décision (identiques DL + TL)
DECISION_CRITERIA = [
    ('AUC',         'AUC-ROC',       0.65, 0.55),
    ('Sensitivity', 'Sensitivity',   0.50, 0.40),
    ('Specificity', 'Specificity',   0.50, 0.40),
    ('MCC',         'MCC',           0.20, 0.10),
    ('Balanced_Acc','Balanced Acc',  0.65, 0.55),
]


# ─── Score composite ─────────────────────────────────────────────────────────
def composite(auc, sens, mcc, spec):
    return 0.40 * auc + 0.30 * sens + 0.20 * mcc + 0.10 * spec


# ─── Chargement JSON ─────────────────────────────────────────────────────────
def _extract(m: dict) -> dict:
    """Dict brut d'un modèle → métriques normalisées."""
    prof = m.get('professional', {})
    cal  = (prof.get('calibration') or m.get('calibration') or {})
    icc  = (prof.get('icc')         or m.get('icc')         or {})
    ba   = (prof.get('bland_altman')or m.get('bland_altman')or {})
    bci  = (prof.get('bootstrap_ci')or {})
    perm = (prof.get('permutation')  or {})
    return {
        'MAE':          float(m.get('mae',              999.)),
        'RMSE':         float(m.get('rmse',             999.)),
        'R2':           float(m.get('r2',               -99.)),
        'AUC':          float(m.get('auc_roc',            0.)),
        'Sensitivity':  float(m.get('sensitivity',        0.)),
        'Specificity':  float(m.get('specificity',        0.)),
        'MCC':          float(m.get('mcc',                0.)),
        'Balanced_Acc': float(m.get('balanced_accuracy',  0.)),
        'PR_AUC':       float(m.get('pr_auc',             0.)),
        'F1_macro':     float(m.get('f1_macro',           0.)),
        'ECE':          float(cal.get('ece',              0.)),
        'ICC':          float(icc.get('icc',              0.)),
        'LOA_width':    float(ba.get('loa_width',         0.)),
        'AUC_CI_lo':    float(bci.get('auc_roc', {}).get('ci_lo', 0.)),
        'AUC_CI_hi':    float(bci.get('auc_roc', {}).get('ci_hi', 0.)),
        'AUC_pval':     float(perm.get('auc_roc', {}).get('p_value', 1.)),
    }


def load_all() -> pd.DataFrame:
    rows = []
    for ak, root in APPROACH_ROOTS.items():
        for target in TARGETS:
            jf = root / target / f'results_{target}.json'
            if not jf.exists():
                print(f"  [SKIP] {ak}/{target} — fichier manquant")
                continue
            with open(jf, encoding='utf-8') as f:
                data = json.load(f)
            loso = data.get('loso', data)
            for exp, models in loso.items():
                if exp not in EXPERIMENTS:
                    continue
                for mn, m in models.items():
                    if mn.startswith('_') or mn not in MODEL_NAMES:
                        continue
                    met = _extract(m)
                    met['Composite'] = composite(
                        met['AUC'], met['Sensitivity'], met['MCC'], met['Specificity']
                    )
                    rows.append({
                        'Approach':    ak,
                        'ApproachLabel': APPROACH_LABELS[ak].replace('\n', ' '),
                        'Model':       mn,
                        'Target':      target,
                        'Experiment':  exp,
                        **met,
                    })
            print(f"  OK  {ak:20s} / {target}")
    return pd.DataFrame(rows)


# ─── Couleur décision ────────────────────────────────────────────────────────
def _bc(v, good, border):
    if v >= good:   return '#27AE60'
    if v >= border: return '#F39C12'
    return '#E74C3C'


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 1 — Ranking composite Top-20
# ─────────────────────────────────────────────────────────────────────────────
def plot_ranking(df: pd.DataFrame, target: str, out_dir: Path):
    sub = df[(df['Target'] == target) & (df['Experiment'] == 'FULL')].copy()
    if sub.empty:
        sub = df[df['Target'] == target].copy()
    if sub.empty:
        return
    sub = sub.sort_values('Composite', ascending=False).head(20).reset_index(drop=True)
    labels = [f"{r['ApproachLabel']} | {r['Model']}" for _, r in sub.iterrows()]
    vals   = sub['Composite'].values
    colors = [APPROACH_COLORS[r['Approach']] for _, r in sub.iterrows()]

    fig, ax = plt.subplots(figsize=(13, 9))
    bars = ax.barh(labels[::-1], vals[::-1], color=colors[::-1], alpha=0.88, edgecolor='white')
    for bar, v in zip(bars, vals[::-1]):
        ax.text(bar.get_width() + 0.004, bar.get_y() + bar.get_height() / 2,
                f'{v:.3f}', va='center', fontsize=8.5, fontweight='bold')
    ax.axvline(0.50, color='#27AE60', lw=1.5, ls='--', alpha=0.7, label='Seuil bon (0.50)')
    ax.axvline(0.35, color='#F39C12', lw=1.2, ls=':',  alpha=0.6, label='Seuil borderline (0.35)')
    ax.set_xlabel('Score composite  (AUC×0.4 + Sens×0.3 + MCC×0.2 + Spec×0.1)', fontsize=10)
    ax.set_title(f'Classement global Baselines — {target.upper()} — Exp. FULL\n'
                 f'Top-20 combinaisons approche × modèle', fontsize=12, fontweight='bold')
    # Légende approches
    patches = [mpatches.Patch(color=APPROACH_COLORS[k], label=APPROACH_LABELS[k].replace('\n',' '))
               for k in APPROACH_ROOTS]
    ax.legend(handles=patches, loc='lower right', fontsize=8.5, framealpha=0.85)
    ax.set_xlim(0, max(vals) * 1.15)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / '01_ranking_composite.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    01_ranking_composite.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 2 — Heatmap 4 approches × 5 modèles par métrique
# ─────────────────────────────────────────────────────────────────────────────
def plot_heatmap_grid(df: pd.DataFrame, target: str, out_dir: Path):
    METRICS = [
        ('Composite',  'Score Composite',   False),
        ('AUC',        'AUC-ROC',           False),
        ('Sensitivity','Sensitivity',        False),
        ('Specificity','Specificity',        False),
        ('MCC',        'MCC',               False),
        ('MAE',        'MAE',               True),   # inversé : rouge = élevé = mauvais
        ('R2',         'R²',                False),
    ]
    sub = df[(df['Target'] == target) & (df['Experiment'] == 'FULL')].copy()
    if sub.empty:
        sub = df[df['Target'] == target].copy()
    if sub.empty:
        return

    approaches = list(APPROACH_ROOTS.keys())
    models     = MODEL_NAMES
    n_metrics  = len(METRICS)

    fig, axes = plt.subplots(1, n_metrics, figsize=(4.2 * n_metrics, 4.5))
    fig.suptitle(f'Heatmap Globale Baselines — {target.upper()} — Exp. FULL\n'
                 f'4 approches × 5 modèles', fontsize=13, fontweight='bold', y=1.01)

    for ax, (col, title, inv) in zip(axes, METRICS):
        mat = np.full((len(approaches), len(models)), np.nan)
        for i, ak in enumerate(approaches):
            for j, mn in enumerate(models):
                row = sub[(sub['Approach'] == ak) & (sub['Model'] == mn)]
                if not row.empty:
                    mat[i, j] = row[col].values[0]
        cmap = 'RdYlGn_r' if inv else 'RdYlGn'
        im = ax.imshow(mat, cmap=cmap, aspect='auto',
                       vmin=np.nanmin(mat), vmax=np.nanmax(mat))
        ax.set_xticks(range(len(models)))
        ax.set_yticks(range(len(approaches)))
        ax.set_xticklabels([m[:5] for m in models], rotation=45, ha='right', fontsize=7)
        ax.set_yticklabels([APPROACH_LABELS[a].replace('\n',' ') for a in approaches], fontsize=7)
        for i in range(len(approaches)):
            for j in range(len(models)):
                v = mat[i, j]
                if not np.isnan(v):
                    ax.text(j, i, f'{v:.2f}', ha='center', va='center',
                            fontsize=7.5, fontweight='bold',
                            color='white' if abs(v - np.nanmean(mat)) > np.nanstd(mat) else 'black')
        ax.set_title(title, fontsize=9, fontweight='bold')
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    plt.tight_layout()
    plt.savefig(out_dir / '02_heatmap_approach_model.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    02_heatmap_approach_model.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURES 3-8 — Barplots groupés par métrique (approche = groupe, modèle = barre)
# ─────────────────────────────────────────────────────────────────────────────
def plot_barplot_metric(df: pd.DataFrame, target: str, out_dir: Path,
                        col: str, ylabel: str, filename: str, lower_is_better=False):
    sub = df[(df['Target'] == target) & (df['Experiment'] == 'FULL')].copy()
    if sub.empty:
        sub = df[df['Target'] == target].copy()
    if sub.empty:
        return

    approaches = [k for k in APPROACH_ROOTS if k in sub['Approach'].unique()]
    models     = [m for m in MODEL_NAMES  if m in sub['Model'].unique()]
    n_ap  = len(approaches)
    n_mod = len(models)
    w     = 0.8 / n_mod
    x     = np.arange(n_ap)

    fig, ax = plt.subplots(figsize=(max(10, 2.5 * n_ap), 5.5))
    for j, mn in enumerate(models):
        vals = []
        for ak in approaches:
            row = sub[(sub['Approach'] == ak) & (sub['Model'] == mn)]
            vals.append(row[col].values[0] if not row.empty else 0.)
        offset = (j - n_mod / 2 + 0.5) * w
        bars = ax.bar(x + offset, vals, w, label=mn,
                      color=MODEL_COLORS[mn], alpha=0.85, edgecolor='white')
        for bar, v in zip(bars, vals):
            if v != 0.:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + (0.003 if not lower_is_better else -0.003),
                        f'{v:.3f}', ha='center', va='bottom', fontsize=6.5)

    ax.set_xticks(x)
    ax.set_xticklabels([APPROACH_LABELS[a].replace('\n', ' ') for a in approaches], fontsize=9)
    ax.set_ylabel(ylabel, fontsize=10)
    ax.set_title(f'{ylabel} — Baselines {target.upper()} — Exp. FULL', fontsize=12, fontweight='bold')
    ax.legend(title='Modèle', bbox_to_anchor=(1.01, 1), loc='upper left', fontsize=8.5)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(out_dir / filename, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    {filename}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 9 — Dashboard décision : 20 combinaisons pass/fail
# ─────────────────────────────────────────────────────────────────────────────
def plot_decision_dashboard(df: pd.DataFrame, target: str, out_dir: Path):
    sub = df[(df['Target'] == target) & (df['Experiment'] == 'FULL')].copy()
    if sub.empty:
        sub = df[df['Target'] == target].copy()
    if sub.empty:
        return

    approaches = [k for k in APPROACH_ROOTS if k in sub['Approach'].unique()]
    models     = [m for m in MODEL_NAMES  if m in sub['Model'].unique()]
    combos     = [(ak, mn) for ak in approaches for mn in models]

    n_criteria = len(DECISION_CRITERIA)
    n_combos   = len(combos)

    fig = plt.figure(figsize=(28, max(14, n_combos * 0.55 + 5)))
    gs  = gridspec.GridSpec(2, n_criteria, height_ratios=[1.8, 1.0],
                            hspace=0.5, wspace=0.3,
                            top=0.88, bottom=0.04, left=0.03, right=0.97)
    fig.suptitle(
        f'Dashboard Décision — Baselines ML  |  {target.upper()}  |  Exp. FULL\n'
        f'Ordre priorité : AUC (GO/NO-GO) → Sensitivity → MCC → Décision finale',
        fontsize=13, fontweight='bold'
    )

    combo_labels = [f"{APPROACH_LABELS[ak].replace(chr(10),' ')} | {mn}"
                    for ak, mn in combos]

    for ci, (col, label, good_t, border_t) in enumerate(DECISION_CRITERIA):
        ax   = fig.add_subplot(gs[0, ci])
        vals = []
        for ak, mn in combos:
            row = sub[(sub['Approach'] == ak) & (sub['Model'] == mn)]
            vals.append(float(row[col].values[0]) if not row.empty else 0.)
        cols = [_bc(v, good_t, border_t) for v in vals]
        xpos = np.arange(n_combos)
        bars = ax.bar(xpos, vals, 0.7, color=cols, alpha=0.88, edgecolor='white')
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                    f'{v:.2f}', ha='center', va='bottom', fontsize=5, fontweight='bold')
        ax.axhline(good_t,   color='#27AE60', lw=1.8, ls='--', alpha=0.85)
        ax.axhline(border_t, color='#F39C12', lw=1.2, ls=':',  alpha=0.70)
        ax.set_xticks(xpos)
        ax.set_xticklabels([f"{APPROACH_LABELS[ak].replace(chr(10),' ')[:6]}|{mn[:4]}"
                            for ak, mn in combos],
                           rotation=60, ha='right', fontsize=5)
        ax.set_ylim(0, 1.18)
        ax.set_title(f'{label} ↑', fontsize=9, fontweight='bold')
        ax.grid(axis='y', alpha=0.25)

    legend_patches = [
        mpatches.Patch(color='#27AE60', label='✅ Bon'),
        mpatches.Patch(color='#F39C12', label='⚠️ Borderline'),
        mpatches.Patch(color='#E74C3C', label='❌ Insuffisant'),
    ]
    fig.legend(handles=legend_patches, loc='upper right',
               bbox_to_anchor=(0.97, 0.94), fontsize=9, ncol=3, framealpha=0.9)

    # Tableau de décision
    ax_tbl = fig.add_subplot(gs[1, :])
    ax_tbl.axis('off')
    ax_tbl.set_title(
        f'Seuils : AUC≥0.65 | Sensitivity≥0.50 | Specificity≥0.50 | MCC≥0.20 | Bal.Acc≥0.65'
        f'   (vert=bon · orange=borderline · rouge=insuffisant)',
        fontsize=8, fontweight='bold', pad=5
    )
    headers  = ['Approche', 'Modèle', 'AUC', 'Sensitivity', 'Specificity', 'MCC', 'Bal.Acc', 'Composite', 'DÉCISION']
    tbl_rows, tbl_colors = [], []
    for ak, mn in combos:
        row = sub[(sub['Approach'] == ak) & (sub['Model'] == mn)]
        if row.empty:
            continue
        r = row.iloc[0]
        trow  = [APPROACH_LABELS[ak].replace('\n', ' '), mn]
        tcolr = ['#ECF0F1', '#ECF0F1']
        n_good = 0
        for col, _, good_t, border_t in DECISION_CRITERIA:
            v = float(r[col])
            trow.append(f'{v:.3f}')
            if v >= good_t:
                tcolr.append('#D5F5E3'); n_good += 1
            elif v >= border_t:
                tcolr.append('#FDEBD0')
            else:
                tcolr.append('#FADBD8')
        trow.append(f'{float(r["Composite"]):.3f}')
        tcolr.append('#EAF2FF')
        if n_good >= 4:
            d, dc = '✅ Recommandé', '#D5F5E3'
        elif n_good >= 2:
            d, dc = '⚠️ Acceptable', '#FDEBD0'
        else:
            d, dc = '❌ Rejeté',     '#FADBD8'
        trow.append(d); tcolr.append(dc)
        tbl_rows.append(trow); tbl_colors.append(tcolr)

    if tbl_rows:
        tbl = ax_tbl.table(cellText=tbl_rows, colLabels=headers,
                           cellLoc='center', loc='center', bbox=[0, 0, 1, 1],
                           cellColours=tbl_colors)
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(6.5)
        for col in range(len(headers)):
            tbl[(0, col)].set_facecolor('#1A3A4A')
            tbl[(0, col)].set_text_props(color='white', fontweight='bold')

    plt.savefig(out_dir / '09_decision_dashboard.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    09_decision_dashboard.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 10 — Radar Top-5 combinaisons
# ─────────────────────────────────────────────────────────────────────────────
def plot_radar_top5(df: pd.DataFrame, target: str, out_dir: Path):
    sub = df[(df['Target'] == target) & (df['Experiment'] == 'FULL')].copy()
    if sub.empty:
        sub = df[df['Target'] == target].copy()
    if sub.empty:
        return

    top5 = sub.sort_values('Composite', ascending=False).head(5)
    RADAR_METRICS = ['AUC', 'Sensitivity', 'Specificity', 'MCC', 'Balanced_Acc', 'R2']
    # Normalise R² en 0-1 (si négatif → 0)
    N  = len(RADAR_METRICS)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    colors_radar = ['#E74C3C', '#2980B9', '#27AE60', '#F39C12', '#8E44AD']

    for i, (_, row) in enumerate(top5.iterrows()):
        values = []
        for m in RADAR_METRICS:
            v = float(row[m]) if m in row else 0.
            values.append(max(0., min(1., v)))  # clip [0, 1]
        values += values[:1]
        label = f"{APPROACH_LABELS[row['Approach']].replace(chr(10),' ')} | {row['Model']} (c={row['Composite']:.3f})"
        ax.plot(angles, values, 'o-', lw=2, color=colors_radar[i], label=label, markersize=4)
        ax.fill(angles, values, alpha=0.08, color=colors_radar[i])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(RADAR_METRICS, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.2, 0.4, 0.6, 0.8])
    ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8'], fontsize=7)
    ax.set_title(f'Radar Top-5 — Baselines {target.upper()} — Exp. FULL',
                 fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=8)
    plt.tight_layout()
    plt.savefig(out_dir / '10_radar_top5.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    10_radar_top5.png")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 11 — Boxplot score composite par modèle (distribution sur 5 expériences)
# ─────────────────────────────────────────────────────────────────────────────
def plot_boxplot_per_model(df: pd.DataFrame, target: str, out_dir: Path):
    sub = df[df['Target'] == target].copy()
    if sub.empty:
        return

    approaches = [k for k in APPROACH_ROOTS if k in sub['Approach'].unique()]
    models     = [m for m in MODEL_NAMES  if m in sub['Model'].unique()]

    fig, axes = plt.subplots(1, len(approaches),
                             figsize=(4.5 * len(approaches), 5.5), sharey=True)
    if len(approaches) == 1:
        axes = [axes]

    for ax, ak in zip(axes, approaches):
        data_plot = [sub[(sub['Approach'] == ak) & (sub['Model'] == mn)]['Composite'].values
                     for mn in models]
        bp = ax.boxplot(data_plot, patch_artist=True, widths=0.55,
                        medianprops=dict(color='black', lw=2))
        for patch, mn in zip(bp['boxes'], models):
            patch.set_facecolor(MODEL_COLORS[mn])
            patch.set_alpha(0.75)
        ax.set_xticks(range(1, len(models) + 1))
        ax.set_xticklabels(models, rotation=35, ha='right', fontsize=8)
        ax.set_title(APPROACH_LABELS[ak].replace('\n', ' '), fontsize=10, fontweight='bold')
        ax.axhline(0.50, color='#27AE60', lw=1.2, ls='--', alpha=0.7)
        ax.axhline(0.35, color='#F39C12', lw=1.0, ls=':',  alpha=0.6)
        ax.grid(axis='y', alpha=0.3)

    axes[0].set_ylabel('Score composite', fontsize=10)
    fig.suptitle(f'Distribution Score Composite par Modèle — {target.upper()}\n'
                 f'(5 expériences A/B/C/D/FULL)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(out_dir / '11_boxplot_per_model.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    11_boxplot_per_model.png")


# Couleurs composantes
_COMP_COLORS = {
    'auc_w':  '#2980B9',
    'sens_w': '#27AE60',
    'mcc_w':  '#F39C12',
    'spec_w': '#8E44AD',
}


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE 12 — Décomposition composite (stacked + métriques brutes)
# ─────────────────────────────────────────────────────────────────────────────
def plot_composite_stacked(df: pd.DataFrame, target: str, out_dir: Path):
    """
    Figure 2 panneaux :
      Haut : barres empilées des 4 contributions pondérées (AUC×0.4, Sens×0.3, MCC×0.2, Spec×0.1)
      Bas  : métriques brutes côte à côte (AUC, Sensitivity, MCC, Specificity)
    Permet d'argumenter le choix de l'approche et du modèle [Ferri et al. 2009].
    """
    sub = df[(df['Target'] == target) & (df['Experiment'] == 'FULL')].copy()
    if sub.empty:
        sub = df[df['Target'] == target].copy()
    if sub.empty:
        return

    sub['auc_w']  = (0.40 * sub['AUC'].clip(lower=0))
    sub['sens_w'] = (0.30 * sub['Sensitivity'].clip(lower=0))
    sub['mcc_w']  = (0.20 * sub['MCC'].clip(lower=0))
    sub['spec_w'] = (0.10 * sub['Specificity'].clip(lower=0))
    sub['label']  = sub['ApproachLabel'] + ' | ' + sub['Model']
    sub = sub.sort_values('Composite', ascending=False).reset_index(drop=True)

    n = len(sub)
    x = np.arange(n)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(18, n * 0.85), 13))
    fig.suptitle(
        f"Décomposition du Score Composite — Baselines ML  |  {target.upper()}  |  Exp. FULL\n"
        f"Score = AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10\n"
        f"[Fawcett 2006; Chicco & Jurman 2020; Fairclough 2009; Youden 1950]",
        fontsize=11, fontweight='bold'
    )

    # Panneau 1 : contributions empilées
    bottoms = np.zeros(n)
    for key, col, lbl in [
        ('auc_w',  'auc_w',  'AUC × 0.40  [Fawcett 2006]'),
        ('sens_w', 'sens_w', 'Sensitivity × 0.30  [Fairclough 2009]'),
        ('mcc_w',  'mcc_w',  'MCC × 0.20  [Chicco & Jurman 2020]'),
        ('spec_w', 'spec_w', 'Specificity × 0.10  [Youden 1950]'),
    ]:
        vals = sub[col].values
        ax1.bar(x, vals, bottom=bottoms, color=_COMP_COLORS[key],
                alpha=0.85, edgecolor='white', label=lbl)
        bottoms += vals
    for i, (comp, ap) in enumerate(zip(sub['Composite'], sub['Approach'])):
        ax1.text(i, comp + 0.008, f'{comp:.3f}', ha='center', va='bottom',
                 fontsize=6, fontweight='bold', color=APPROACH_COLORS.get(ap, '#333'))
    ax1.set_xticks(x)
    ax1.set_xticklabels(sub['label'], rotation=50, ha='right', fontsize=6.5)
    ax1.set_ylabel('Score composite (contributions pondérées)', fontsize=9)
    ax1.set_title('Contributions pondérées au score composite — toutes combinaisons (tri décroissant)', fontsize=10)
    ax1.axhline(0.50, color='#27AE60', lw=1.5, ls='--', alpha=0.7, label='Seuil bon (0.50)')
    ax1.axhline(0.35, color='#F39C12', lw=1.2, ls=':',  alpha=0.6, label='Seuil borderline (0.35)')
    ax1.set_ylim(0, min(1.0, sub['Composite'].max() * 1.22))
    ax1.legend(loc='upper right', fontsize=7.5, framealpha=0.85)
    ax1.grid(axis='y', alpha=0.25)

    # Panneau 2 : métriques brutes
    w = 0.20
    for j, (col, lbl, color) in enumerate([
        ('AUC',         'AUC-ROC',     _COMP_COLORS['auc_w']),
        ('Sensitivity', 'Sensitivity', _COMP_COLORS['sens_w']),
        ('MCC',         'MCC',         _COMP_COLORS['mcc_w']),
        ('Specificity', 'Specificity', _COMP_COLORS['spec_w']),
    ]):
        vals = sub[col].clip(lower=0).values
        offset = (j - 1.5) * w
        bars = ax2.bar(x + offset, vals, w, label=lbl, color=color, alpha=0.82, edgecolor='white')
        for bar, v in zip(bars, vals):
            if v > 0.01:
                ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                         f'{v:.2f}', ha='center', va='bottom', fontsize=4.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(sub['label'], rotation=50, ha='right', fontsize=6.5)
    ax2.set_ylabel('Valeur brute de la métrique', fontsize=9)
    ax2.set_title('Métriques brutes individuelles (AUC, Sensitivity, MCC, Specificity)', fontsize=10)
    ax2.axhline(0.50, color='gray', lw=1.0, ls='--', alpha=0.5)
    ax2.set_ylim(0, 1.15)
    ax2.legend(loc='upper right', fontsize=8, framealpha=0.85)
    ax2.grid(axis='y', alpha=0.25)

    plt.tight_layout()
    plt.savefig(out_dir / '12_composite_stacked.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"    12_composite_stacked.png")


# ─────────────────────────────────────────────────────────────────────────────
# EXPORT JSON
# ─────────────────────────────────────────────────────────────────────────────
def save_composite_json(df: pd.DataFrame, out_dir: Path):
    """
    Sauvegarde composite_scores.json + composite_summary.txt par target pour les baselines ML.
    """
    import json as _json

    for target in TARGETS:
        sub = df[(df['Target'] == target) & (df['Experiment'] == 'FULL')].copy()
        if sub.empty:
            sub = df[df['Target'] == target].copy()
        if sub.empty:
            continue
        sub = sub.sort_values('Composite', ascending=False).reset_index(drop=True)

        ranking = []
        for rank, (_, row) in enumerate(sub.iterrows(), 1):
            auc  = float(row['AUC'])
            sens = float(row['Sensitivity'])
            mcc  = float(row['MCC'])
            spec = float(row['Specificity'])
            ranking.append({
                "rank":     rank,
                "approach": row['Approach'],
                "model":    row['Model'],
                "exp":      row['Experiment'],
                "composite": round(float(row['Composite']), 4),
                "metrics": {
                    "AUC":          round(auc,  4),
                    "Sensitivity":  round(sens, 4),
                    "MCC":          round(mcc,  4),
                    "Specificity":  round(spec, 4),
                    "Balanced_Acc": round(float(row.get('Balanced_Acc', 0)), 4),
                    "MAE":          round(float(row.get('MAE', 0)), 4),
                    "R2":           round(float(row.get('R2', 0)), 4),
                },
                "weighted_contributions": {
                    "AUC_x040":         round(0.40 * max(auc,  0), 4),
                    "Sensitivity_x030": round(0.30 * max(sens, 0), 4),
                    "MCC_x020":         round(0.20 * max(mcc,  0), 4),
                    "Specificity_x010": round(0.10 * max(spec, 0), 4),
                },
                "formula": "AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10",
                "references": [
                    "Fawcett (2006) Pattern Recognit. Lett. 27(8):861-874",
                    "Chicco & Jurman (2020) BMC Genomics 21(1):6",
                    "Fairclough (2009) Interacting with Computers 21(1-2):133-145",
                    "Youden (1950) Cancer 3(1):32-35",
                    "Lotte et al. (2018) J. Neural Eng. 15(3):031005",
                    "Ferri et al. (2009) Pattern Recognit. Lett. 30(1):27-38",
                ],
            })

        out_sub = out_dir / target
        out_sub.mkdir(parents=True, exist_ok=True)

        json_path = out_sub / "composite_scores.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            _json.dump({
                "target": target, "family": "ML-Baseline",
                "composite_formula": "AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10",
                "ranking": ranking,
            }, f, indent=2, ensure_ascii=False)
        print(f"    composite_scores_{target}.json")

        lines = []
        lines.append("=" * 95)
        lines.append(f"NeuroCap — Score Composite Baselines ML — {target.upper()}")
        lines.append("Formule : AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10")
        lines.append("  AUC  (w=0.40) : threshold-free, recommandée EEG/BCI [Fawcett 2006; Lotte et al. 2018]")
        lines.append("  Sens (w=0.30) : FN coûteux en monitoring cognitif [Fairclough 2009]")
        lines.append("  MCC  (w=0.20) : utilise les 4 cellules de la matrice [Chicco & Jurman 2020]")
        lines.append("  Spec (w=0.10) : FP moins coûteux [Youden 1950]")
        lines.append("=" * 95)
        lines.append(f"\n{'Rg':<4} {'Approche':<22} {'Modèle':<17} {'Score':>7} │ "
                     f"{'AUC':>7} {'Sens':>7} {'MCC':>7} {'Spec':>7} │ "
                     f"{'AUC×0.4':>8} {'S×0.3':>7} {'M×0.2':>7} {'Sp×0.1':>7}")
        lines.append("─" * 95)
        for item in ranking[:25]:
            m  = item['metrics']
            wc = item['weighted_contributions']
            lines.append(
                f"  {item['rank']:<2} {item['approach']:<22} {item['model']:<17} {item['composite']:>7.4f} │ "
                f"{m['AUC']:>7.4f} {m['Sensitivity']:>7.4f} {m['MCC']:>7.4f} {m['Specificity']:>7.4f} │ "
                f"{wc['AUC_x040']:>8.4f} {wc['Sensitivity_x030']:>7.4f} "
                f"{wc['MCC_x020']:>7.4f} {wc['Specificity_x010']:>7.4f}"
            )
        if ranking:
            best = ranking[0]
            lines.append(f"\n★ MEILLEURE COMBINAISON : {best['approach']} | {best['model']}")
            lines.append(f"  Score composite = {best['composite']:.4f}")
            for k, v in best['metrics'].items():
                lines.append(f"  {k:<15}: {v:.4f}")
        txt_path = out_sub / "composite_summary.txt"
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"    composite_summary_{target}.txt")


# ─────────────────────────────────────────────────────────────────────────────
# RÉSUMÉ TEXTE
# ─────────────────────────────────────────────────────────────────────────────
def write_summary(df: pd.DataFrame, path: Path):
    lines = []
    lines.append("=" * 80)
    lines.append("NeuroCap — Comparaison Globale Baselines ML (Régression)")
    lines.append("Score composite = AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10")
    lines.append("=" * 80)

    for target in TARGETS:
        lines.append(f"\n{'─'*60}")
        lines.append(f"  CIBLE : {target.upper()}")
        lines.append(f"{'─'*60}")

        sub = df[(df['Target'] == target) & (df['Experiment'] == 'FULL')].copy()
        if sub.empty:
            sub = df[df['Target'] == target].copy()
        if sub.empty:
            lines.append("  [PAS DE DONNÉES]")
            continue

        # Top-3 global
        top = sub.sort_values('Composite', ascending=False).head(3)
        lines.append("\n  TOP-3 COMBINAISONS (Exp. FULL) :")
        for rank, (_, row) in enumerate(top.iterrows(), 1):
            lines.append(
                f"    {rank}. {APPROACH_LABELS[row['Approach']].replace(chr(10),' '):22s} | "
                f"{row['Model']:15s} → "
                f"Score={row['Composite']:.3f}  AUC={row['AUC']:.3f}  "
                f"Sens={row['Sensitivity']:.3f}  Spec={row['Specificity']:.3f}  "
                f"MCC={row['MCC']:.3f}  MAE={row['MAE']:.3f}  R²={row['R2']:.3f}"
            )

        # Meilleur par modèle
        lines.append("\n  MEILLEUR PAR MODÈLE (Exp. FULL) :")
        for mn in MODEL_NAMES:
            ms = sub[sub['Model'] == mn]
            if ms.empty:
                continue
            best = ms.sort_values('Composite', ascending=False).iloc[0]
            lines.append(
                f"    {mn:15s} → {APPROACH_LABELS[best['Approach']].replace(chr(10),' '):22s} "
                f"Score={best['Composite']:.3f}  AUC={best['AUC']:.3f}  "
                f"Sens={best['Sensitivity']:.3f}  MCC={best['MCC']:.3f}"
            )

        # Décision
        lines.append("\n  DÉCISION (seuil : ≥3 critères validés = Recommandé) :")
        lines.append(f"  {'Approche':22s} {'Modèle':15s} AUC  Sens Spec MCC  BalAcc  Score   Décision")
        lines.append(f"  {'-'*85}")
        for ak in APPROACH_ROOTS:
            for mn in MODEL_NAMES:
                row = sub[(sub['Approach'] == ak) & (sub['Model'] == mn)]
                if row.empty:
                    continue
                r = row.iloc[0]
                criteria = [
                    r['AUC']          >= 0.65,
                    r['Sensitivity']  >= 0.50,
                    r['Specificity']  >= 0.50,
                    r['MCC']          >= 0.20,
                    r['Balanced_Acc'] >= 0.65,
                ]
                n_ok  = sum(criteria)
                dec   = '✅ Recommandé' if n_ok >= 4 else '⚠️ Acceptable' if n_ok >= 2 else '❌ Rejeté'
                lines.append(
                    f"  {APPROACH_LABELS[ak].replace(chr(10),' '):22s} {mn:15s} "
                    f"{'✓' if criteria[0] else '✗'}    "
                    f"{'✓' if criteria[1] else '✗'}   "
                    f"{'✓' if criteria[2] else '✗'}   "
                    f"{'✓' if criteria[3] else '✗'}   "
                    f"{'✓' if criteria[4] else '✗'}      "
                    f"{r['Composite']:.3f}   {dec}"
                )

    lines.append("\n" + "=" * 80)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"\n  Résumé → {path.relative_to(PROJECT_ROOT)}")
    print('\n'.join(lines))


# ─────────────────────────────────────────────────────────────────────────────
# CSV GLOBAL
# ─────────────────────────────────────────────────────────────────────────────
def save_csv(df: pd.DataFrame, target: str, out_dir: Path):
    cols = ['Approach', 'ApproachLabel', 'Model', 'Target', 'Experiment',
            'Composite', 'AUC', 'Sensitivity', 'Specificity', 'MCC',
            'Balanced_Acc', 'MAE', 'RMSE', 'R2', 'F1_macro', 'PR_AUC',
            'ECE', 'ICC', 'LOA_width', 'AUC_CI_lo', 'AUC_CI_hi', 'AUC_pval']
    cols_avail = [c for c in cols if c in df.columns]
    sub = df[df['Target'] == target].sort_values('Composite', ascending=False)
    sub[cols_avail].to_csv(out_dir / f'global_results_{target}.csv', index=False)
    print(f"    global_results_{target}.csv")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("NeuroCap — Comparaison Globale Baselines ML")
    print("=" * 70)

    print("\nChargement des JSON ...")
    df = load_all()

    if df.empty:
        print("\n❌ Aucun résultat trouvé. Lancez d'abord les 4 scripts baseline.")
        return

    print(f"\n{len(df)} lignes | "
          f"{df['Approach'].nunique()} approches | "
          f"{df['Model'].nunique()} modèles | "
          f"{df['Target'].nunique()} cibles\n")

    for target in TARGETS:
        out_dir = OUT_ROOT / target
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n── {target.upper()} ──────────────────────────────────────")
        plot_ranking(df, target, out_dir)
        plot_heatmap_grid(df, target, out_dir)
        plot_barplot_metric(df, target, out_dir, 'AUC',         'AUC-ROC (↑)',      '03_barplot_auc.png')
        plot_barplot_metric(df, target, out_dir, 'Sensitivity', 'Sensitivity (↑)',  '04_barplot_sensitivity.png')
        plot_barplot_metric(df, target, out_dir, 'Specificity', 'Specificity (↑)',  '05_barplot_specificity.png')
        plot_barplot_metric(df, target, out_dir, 'MCC',         'MCC (↑)',          '06_barplot_mcc.png')
        plot_barplot_metric(df, target, out_dir, 'MAE',         'MAE (↓)',          '07_barplot_mae.png',  lower_is_better=True)
        plot_barplot_metric(df, target, out_dir, 'R2',          'R² (↑)',           '08_barplot_r2.png')
        plot_decision_dashboard(df, target, out_dir)
        plot_radar_top5(df, target, out_dir)
        plot_boxplot_per_model(df, target, out_dir)
        plot_composite_stacked(df, target, out_dir)   # Fig 12 — NOUVEAU
        save_csv(df, target, out_dir)

    save_composite_json(df, OUT_ROOT)                 # JSON + TXT — NOUVEAU
    write_summary(df, OUT_ROOT / 'global_summary.txt')

    print(f"\n✅ Comparaison globale terminée.")
    print(f"   Sorties : {OUT_ROOT.relative_to(PROJECT_ROOT)}")


if __name__ == '__main__':
    main()
