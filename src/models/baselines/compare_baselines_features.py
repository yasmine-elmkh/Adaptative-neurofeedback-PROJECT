"""
=============================================================================
NeuroCap — Comparaison Baseline (15f) vs Feature Engineering (63f)
=============================================================================
Auteur      : Yasmine El Mkhantar
Encadrement : Monir El Azzouzi | Loubna El Rhali | Yassir Matrane

PRINCIPE :
  Ce script NE ré-entraîne RIEN.
  Il lit uniquement les results.json déjà produits par :
    - baseline_ML.py          → reports/Baseline/baselines_outputs/results.json
    - baseline_ML_feature_eng → reports/baseline_FeatEng/outputs_baseline/results.json

  Puis génère toutes les figures de comparaison.

SORTIES :
  reports/Comparison/
  ├── figures/
  │   ├── 01_f1macro_barplot.png       barplot F1-MACRO par exp × modèle
  │   ├── 02_accuracy_barplot.png      barplot Accuracy
  │   ├── 03_auc_barplot.png           barplot AUC
  │   ├── 04_gain_heatmap.png          heatmap ΔF1-MACRO (FeatEng − Baseline)
  │   ├── 05_radar_FULL.png            radar meilleur modèle chaque approche (Exp FULL)
  │   ├── 06_summary_table.png         tableau synthèse visuel
  │   └── 07_best_per_exp.png          meilleur modèle par expérience
  ├── comparison_table.csv
  ├── comparison_summary.txt
  └── comparison_latex.txt
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

# ============================================================================
# CHEMINS — adapter si nécessaire
# ============================================================================
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[2]   # EEG_project/

# Résultats déjà produits
BASELINE_JSON  = PROJECT_ROOT / 'reports' / 'Baseline'        / 'baselines_outputs'  / 'results.json'
FEATENG_JSON   = PROJECT_ROOT / 'reports' / 'baseline_FeatEng' / 'outputs_baseline'   / 'results.json'

# Sortie
OUT_DIR     = PROJECT_ROOT / 'reports' / 'Comparison_Baselines_Features'
FIGURES_DIR = OUT_DIR / 'figures'

EXPERIMENTS  = ['A', 'B', 'C', 'D', 'FULL']
MODEL_NAMES  = ['SVM', 'Random Forest', 'XGBoost', 'LightGBM']
APPROACH_LABELS = {
    'baseline':  'Baseline (15f)',
    'feateng':   'FeatEng (63f)',
}

# ── Palette cohérente ──────────────────────────────────────────────────────
C_BASE  = '#7FB3D3'   # bleu clair  → Baseline
C_FEAT  = '#1A5276'   # bleu foncé  → FeatEng
C_DELTA_POS = '#27AE60'
C_DELTA_NEG = '#E74C3C'

MODEL_COLORS = {
    'SVM':           '#E74C3C',
    'Random Forest': '#2980B9',
    'XGBoost':       '#27AE60',
    'LightGBM':      '#F39C12',
}

EXP_LABEL = {'A':'A\n(×2)','B':'B\n(×3)','C':'C\n(×4)','D':'D\n(×5)','FULL':'FULL\n(×5+)'}


# ============================================================================
# CHARGEMENT DES JSON
# ============================================================================

def load_json(path: Path, label: str) -> dict:
    if not path.exists():
        raise FileNotFoundError(
            f"❌ results.json introuvable pour {label} :\n   {path}\n"
            f"   → Lancez d'abord le script correspondant."
        )
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"  ✅ {label:20s} → {path}")
    return data


def extract_loso_metrics(json_data: dict) -> dict:
    """
    Normalise le JSON quel que soit son format interne.

    Retourne : { exp: { model_name: { acc, f1, f1_macro, auc, precision,
                                      recall, specificity, pct_uncertain } } }
    """
    raw = json_data.get('loso', json_data)  # certains JSON ont 'loso' comme clé racine

    out = {}
    for exp, models in raw.items():
        if exp not in EXPERIMENTS:
            continue
        out[exp] = {}
        for model_name, metrics in models.items():
            # Normaliser les clés (acc vs accuracy, f1_macro vs f1m …)
            m = {}
            m['accuracy']    = float(metrics.get('accuracy',    metrics.get('acc',   0)))
            m['f1']          = float(metrics.get('f1',          metrics.get('f1',    0)))
            m['f1_macro']    = float(metrics.get('f1_macro',    metrics.get('f1m',   0)))
            m['auc']         = float(metrics.get('auc',         0.5))
            m['precision']   = float(metrics.get('precision',   0))
            m['recall']      = float(metrics.get('recall',      0))
            m['specificity'] = float(metrics.get('specificity', 0))
            m['pct_uncertain'] = float(metrics.get('pct_uncertain', 0))
            out[exp][model_name] = m
    return out


# ============================================================================
# CONSTRUCTION DU DATAFRAME UNIFIÉ
# ============================================================================

def build_dataframe(base_metrics: dict, feat_metrics: dict) -> pd.DataFrame:
    rows = []
    for approach_key, metrics_dict in [('baseline', base_metrics),
                                        ('feateng',  feat_metrics)]:
        label = APPROACH_LABELS[approach_key]
        for exp, models in metrics_dict.items():
            for model_name, m in models.items():
                rows.append({
                    'Approach':      label,
                    'ApproachKey':   approach_key,
                    'Experiment':    exp,
                    'Model':         model_name,
                    'Accuracy':      m['accuracy'],
                    'F1_binary':     m['f1'],
                    'F1_MACRO':      m['f1_macro'],
                    'AUC':           m['auc'],
                    'Precision':     m['precision'],
                    'Recall':        m['recall'],
                    'Specificity':   m['specificity'],
                    'Pct_uncertain': m['pct_uncertain'],
                })

    df = pd.DataFrame(rows)

    # Calcul ΔF1-MACRO = FeatEng − Baseline (même exp × même modèle)
    base_df = df[df['ApproachKey'] == 'baseline'][['Experiment','Model','F1_MACRO']]
    feat_df = df[df['ApproachKey'] == 'feateng' ][['Experiment','Model','F1_MACRO']]
    merged  = feat_df.merge(base_df, on=['Experiment','Model'],
                            suffixes=('_feat','_base'))
    merged['Delta_F1m'] = merged['F1_MACRO_feat'] - merged['F1_MACRO_base']

    df = df.merge(merged[['Experiment','Model','Delta_F1m']],
                  on=['Experiment','Model'], how='left')
    return df


# ============================================================================
# FIGURE 1 — Barplot double (Baseline vs FeatEng) pour une métrique
# ============================================================================

def plot_barplot_metric(df: pd.DataFrame, metric: str,
                        title: str, filename: str):
    """
    Pour chaque expérience : 4 groupes (un par modèle),
    2 barres par groupe (Baseline clair / FeatEng foncé).
    """
    exps    = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models  = [m for m in MODEL_NAMES if m in df['Model'].unique()]
    n_mod   = len(models)
    n_exp   = len(exps)

    fig, axes = plt.subplots(1, n_exp, figsize=(3.8 * n_exp, 5.5), sharey=True)
    if n_exp == 1:
        axes = [axes]

    bar_w = 0.32
    x     = np.arange(n_mod)
    approach_keys = ['baseline', 'feateng']
    colors        = [C_BASE, C_FEAT]
    labels_leg    = [APPROACH_LABELS['baseline'], APPROACH_LABELS['feateng']]

    for ax, exp in zip(axes, exps):
        for j, (ak, col) in enumerate(zip(approach_keys, colors)):
            label_str = APPROACH_LABELS[ak]
            vals = []
            for mn in models:
                row = df[(df['ApproachKey'] == ak) &
                         (df['Experiment']  == exp) &
                         (df['Model']       == mn)]
                vals.append(float(row[metric].values[0]) if len(row) > 0 else 0.0)

            offset = (j - 0.5) * bar_w
            bars   = ax.bar(x + offset, vals, bar_w,
                            color=col, edgecolor='white',
                            linewidth=0.7, alpha=0.92,
                            label=label_str if exp == exps[0] else '_nolegend_')

            for bar, val in zip(bars, vals):
                if val > 0.02:
                    ax.text(bar.get_x() + bar.get_width() / 2,
                            bar.get_height() + 0.007,
                            f'{val:.3f}',
                            ha='center', va='bottom',
                            fontsize=6, rotation=50, color='#2C3E50')

        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=35, ha='right', fontsize=8)
        ax.set_title(EXP_LABEL.get(exp, exp), fontsize=11, fontweight='bold')
        ax.set_ylim([0, 1.18])
        ax.set_ylabel(metric if ax == axes[0] else '')
        ax.axhline(0.5, color='gray', lw=0.7, ls='--', alpha=0.4)
        ax.grid(axis='y', alpha=0.35)

    # Légende commune
    handles = [mpatches.Patch(color=c, label=l)
               for c, l in zip(colors, labels_leg)]
    fig.legend(handles=handles, loc='upper center', ncol=2,
               bbox_to_anchor=(0.5, 1.03), fontsize=10,
               frameon=True, edgecolor='#BDC3C7')
    fig.suptitle(title, fontsize=13, fontweight='bold', y=1.07)
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / filename), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ {filename}")


# ============================================================================
# FIGURE 4 — Heatmap ΔF1-MACRO
# ============================================================================

def plot_gain_heatmap(df: pd.DataFrame):
    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]

    # Construire la matrice pivot (modèle × exp)
    pivot = pd.DataFrame(index=models, columns=exps, dtype=float)
    for exp in exps:
        for mn in models:
            row = df[(df['ApproachKey'] == 'feateng') &
                     (df['Experiment']  == exp) &
                     (df['Model']       == mn)]
            if not row.empty and not pd.isna(row['Delta_F1m'].values[0]):
                pivot.loc[mn, exp] = round(float(row['Delta_F1m'].values[0]), 4)

    pivot = pivot.astype(float)
    vabs  = max(abs(pivot.values[~np.isnan(pivot.values)]).max(), 0.01)

    fig, ax = plt.subplots(figsize=(len(exps) * 1.8 + 1.5, len(models) * 1.1 + 1.5))
    sns.heatmap(
        pivot, ax=ax,
        cmap='RdYlGn', center=0, vmin=-vabs, vmax=vabs,
        annot=True, fmt='.4f', annot_kws={'size': 12, 'weight': 'bold'},
        linewidths=0.6, linecolor='white',
        cbar_kws={'label': 'ΔF1-MACRO  (FeatEng − Baseline)', 'shrink': 0.8}
    )
    ax.set_title(
        'Gain ΔF1-MACRO : Feature Engineering Avancé vs Baseline\n'
        '🟢 FeatEng meilleur    🔴 Baseline meilleur',
        fontsize=12, fontweight='bold', pad=14
    )
    ax.set_xlabel('Expérience d\'augmentation', fontsize=10)
    ax.set_ylabel('Classifieur', fontsize=10)
    ax.tick_params(axis='both', labelsize=10, rotation=0)
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / '04_gain_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 04_gain_heatmap.png")


# ============================================================================
# FIGURE 5 — Radar chart (Exp FULL, meilleur modèle chaque approche)
# ============================================================================

def plot_radar(df: pd.DataFrame, exp_ref='FULL'):
    metrics_r  = ['Accuracy', 'F1_MACRO', 'AUC', 'Precision', 'Recall', 'Specificity']
    N          = len(metrics_r)
    angles     = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles    += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    approach_styles = {
        'baseline': {'color': C_BASE,  'lw': 2.5, 'ls': '--'},
        'feateng':  {'color': C_FEAT,  'lw': 2.5, 'ls': '-'},
    }

    for ak, style in approach_styles.items():
        label = APPROACH_LABELS[ak]
        sub   = df[(df['ApproachKey'] == ak) & (df['Experiment'] == exp_ref)]
        if sub.empty:
            # fallback : dernière expérience disponible
            sub = df[df['ApproachKey'] == ak]
            if sub.empty:
                continue
            exp_ref_used = sub['Experiment'].iloc[-1]
            sub = df[(df['ApproachKey'] == ak) & (df['Experiment'] == exp_ref_used)]
        # Meilleur modèle par F1-MACRO
        best_row = sub.loc[sub['F1_MACRO'].idxmax()]
        vals     = [float(best_row[m]) for m in metrics_r]
        vals    += vals[:1]

        ax.plot(angles, vals, lw=style['lw'], ls=style['ls'],
                color=style['color'], label=f"{label}\n({best_row['Model']})")
        ax.fill(angles, vals, alpha=0.12, color=style['color'])

        # Annoter les valeurs
        for angle, val in zip(angles[:-1], vals[:-1]):
            ax.annotate(f'{val:.3f}',
                        xy=(angle, val),
                        xytext=(angle, val + 0.04),
                        fontsize=8, ha='center', color=style['color'],
                        fontweight='bold')

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics_r, fontsize=10)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(['0.25', '0.50', '0.75', '1.00'], fontsize=7, color='gray')
    ax.grid(alpha=0.4)
    ax.set_title(f'Radar — Meilleur modèle par approche\n(Exp {exp_ref}, LOSO)',
                 fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.15), fontsize=9,
              frameon=True, edgecolor='#BDC3C7')
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / '05_radar_FULL.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 05_radar_FULL.png")


# ============================================================================
# FIGURE 6 — Tableau synthèse visuel
# ============================================================================

def plot_summary_table(df: pd.DataFrame):
    """
    Tableau 2 colonnes (Baseline | FeatEng) × N lignes (exp × meilleur modèle).
    """
    exps    = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    records = []
    for exp in exps:
        for ak in ['baseline', 'feateng']:
            label = APPROACH_LABELS[ak]
            sub   = df[(df['ApproachKey'] == ak) & (df['Experiment'] == exp)]
            if sub.empty:
                continue
            best = sub.loc[sub['F1_MACRO'].idxmax()]
            records.append({
                'Exp':       exp,
                'Approche':  label,
                'Modèle':    best['Model'],
                'Accuracy':  f"{best['Accuracy']:.4f}",
                'F1-MACRO':  f"{best['F1_MACRO']:.4f}",
                'AUC':       f"{best['AUC']:.4f}",
                'ΔF1m':      (f"{best['Delta_F1m']:+.4f}"
                              if ak == 'feateng' and not pd.isna(best.get('Delta_F1m'))
                              else '—'),
            })

    df_tbl = pd.DataFrame(records)
    n_rows = len(df_tbl)

    fig, ax = plt.subplots(figsize=(13, max(3.5, n_rows * 0.55 + 1.5)))
    ax.axis('off')

    col_labels = ['Exp', 'Approche', 'Modèle',
                  'Accuracy', 'F1-MACRO', 'AUC', 'ΔF1m']
    cell_data  = df_tbl[col_labels].values.tolist()

    tbl = ax.table(
        cellText=cell_data,
        colLabels=col_labels,
        cellLoc='center',
        loc='center',
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    tbl.scale(1.15, 2.0)

    # En-tête
    for col in range(len(col_labels)):
        tbl[(0, col)].set_facecolor('#1A3A4A')
        tbl[(0, col)].set_text_props(color='white', fontweight='bold')

    # Colorier les lignes selon l'approche
    for row_idx, record in enumerate(cell_data, start=1):
        approach_val = record[1]
        bg = '#D6EAF8' if 'Baseline' in approach_val else '#D5F5E3'
        for col in range(len(col_labels)):
            tbl[(row_idx, col)].set_facecolor(bg)
            # Colorer ΔF1m en rouge/vert
            if col == 6 and record[6] not in ('—', ''):
                try:
                    delta_val = float(record[6])
                    tbl[(row_idx, col)].set_text_props(
                        color=C_DELTA_POS if delta_val >= 0 else C_DELTA_NEG,
                        fontweight='bold'
                    )
                except ValueError:
                    pass

    ax.set_title('Synthèse — Meilleur modèle par approche × expérience (LOSO)',
                 fontsize=12, fontweight='bold', pad=18)
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / '06_summary_table.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 06_summary_table.png")


# ============================================================================
# FIGURE 7 — Meilleur modèle par expérience (scatter + ligne)
# ============================================================================

def plot_best_per_exp(df: pd.DataFrame):
    """
    Pour chaque expérience, affiche le F1-MACRO du meilleur modèle
    de chaque approche → visualise la progression avec l'augmentation.
    """
    exps = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    x    = np.arange(len(exps))

    fig, axes = plt.subplots(1, 3, figsize=(17, 5))
    metrics_plot = [
        ('F1_MACRO',  'F1-MACRO', axes[0]),
        ('Accuracy',  'Accuracy', axes[1]),
        ('AUC',       'AUC',      axes[2]),
    ]

    for metric, ylabel, ax in metrics_plot:
        for ak, col, marker, ls in [
            ('baseline', C_BASE, 'o', '--'),
            ('feateng',  C_FEAT, 's', '-'),
        ]:
            label = APPROACH_LABELS[ak]
            vals  = []
            best_models = []
            for exp in exps:
                sub = df[(df['ApproachKey'] == ak) & (df['Experiment'] == exp)]
                if sub.empty:
                    vals.append(np.nan)
                    best_models.append('')
                else:
                    best_row = sub.loc[sub['F1_MACRO'].idxmax()]
                    vals.append(float(best_row[metric]))
                    best_models.append(best_row['Model'][:3])  # SVM / Ran / XGB / Lig

            vals_arr = np.array(vals, dtype=float)
            ax.plot(x, vals_arr, marker=marker, ls=ls, lw=2.2,
                    color=col, label=label, markersize=9, zorder=3)
            ax.fill_between(x, vals_arr, alpha=0.08, color=col)

            # Annoter le nom du meilleur modèle
            for xi, (val, bm) in enumerate(zip(vals_arr, best_models)):
                if not np.isnan(val) and bm:
                    ax.annotate(bm,
                                xy=(xi, val),
                                xytext=(0, 9),
                                textcoords='offset points',
                                ha='center', fontsize=7,
                                color=col, fontweight='bold')

        ax.set_xticks(x)
        ax.set_xticklabels([EXP_LABEL.get(e, e) for e in exps], fontsize=9)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_ylim([0.3, 1.08])
        ax.set_title(f'{ylabel} — meilleur modèle par expérience',
                     fontsize=10, fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(alpha=0.35)
        ax.axhline(0.5, color='gray', lw=0.7, ls=':', alpha=0.5)

    fig.suptitle('Évolution des performances avec l\'augmentation — '
                 'Baseline vs Feature Engineering',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(str(FIGURES_DIR / '07_best_per_exp.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  ✅ 07_best_per_exp.png")


# ============================================================================
# RAPPORT TEXTE + LATEX
# ============================================================================

def generate_reports(df: pd.DataFrame,
                     base_best: dict, feat_best: dict):
    """Génère comparison_summary.txt et comparison_latex.txt."""

    exps   = [e for e in EXPERIMENTS if e in df['Experiment'].unique()]
    models = [m for m in MODEL_NAMES  if m in df['Model'].unique()]

    # ── Rapport texte ─────────────────────────────────────────────────
    lines = [
        "=" * 72,
        "NeuroCap — Comparaison Baseline ML (15f) vs Feature Eng. (63f)",
        "=" * 72,
        "",
        "Protocole : LOSO (Leave-One-Subject-Out)",
        "Métrique principale : F1-MACRO",
        "",
        f"{'Approche':22s} {'Exp':6s} {'Modèle':16s} "
        f"{'Acc':>7s} {'F1m':>7s} {'AUC':>7s} {'ΔF1m':>9s}",
        "─" * 72,
    ]

    for exp in exps:
        for ak in ['baseline', 'feateng']:
            label = APPROACH_LABELS[ak]
            for mn in models:
                row = df[(df['ApproachKey'] == ak) &
                         (df['Experiment']  == exp) &
                         (df['Model']       == mn)]
                if row.empty:
                    continue
                r = row.iloc[0]
                delta = (f"{r['Delta_F1m']:+.4f}"
                         if ak == 'feateng' and not pd.isna(r.get('Delta_F1m'))
                         else '       —')
                lines.append(
                    f"{label:22s} {exp:6s} {mn:16s} "
                    f"{r['Accuracy']:>7.4f} {r['F1_MACRO']:>7.4f} "
                    f"{r['AUC']:>7.4f} {delta:>9s}"
                )
        lines.append("")

    # Meilleurs globaux
    lines += ["=" * 72, "MEILLEURS MODÈLES", "=" * 72]
    for ak in ['baseline', 'feateng']:
        label = APPROACH_LABELS[ak]
        sub   = df[df['ApproachKey'] == ak]
        if sub.empty:
            continue
        best = sub.loc[sub['F1_MACRO'].idxmax()]
        lines.append(
            f"  {label:22s} → {best['Model']:16s} | Exp {best['Experiment']} | "
            f"Acc={best['Accuracy']:.4f}  F1m={best['F1_MACRO']:.4f}  AUC={best['AUC']:.4f}"
        )

    # Gain global
    b_best = df[df['ApproachKey'] == 'baseline']['F1_MACRO'].max()
    f_best = df[df['ApproachKey'] == 'feateng' ]['F1_MACRO'].max()
    delta  = f_best - b_best
    winner = 'Feature Engineering Avancé (63f)' if delta > 0 else 'Baseline ML (15f)'
    lines += [
        "",
        f"  ΔF1-MACRO global (meilleur FeatEng − meilleur Baseline) : {delta:+.4f}",
        f"  → Approche recommandée : {winner}",
    ]
    if abs(delta) < 0.01:
        lines.append("  ⚠️  Gain < 0.01 : les deux approches sont équivalentes.")
        lines.append("     Préférer Baseline pour la latence embarquée (< 40 ms CdC).")
    lines.append("=" * 72)

    report_text = "\n".join(lines)
    (OUT_DIR / 'comparison_summary.txt').write_text(report_text, encoding='utf-8')
    print("  ✅ comparison_summary.txt")
    print("\n" + report_text)

    # ── Tableau LaTeX ─────────────────────────────────────────────────
    latex = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Comparaison LOSO : Baseline ML (15 features) vs"
        r" Feature Engineering Avancé (63 features)}",
        r"\label{tab:comparison_loso}",
        r"\small",
        r"\begin{tabular}{llccccr}",
        r"\hline",
        r"\textbf{Approche} & \textbf{Exp} & \textbf{Modèle} & "
        r"\textbf{Accuracy} & \textbf{F1-MACRO} & \textbf{AUC} & "
        r"$\boldsymbol{\Delta}$\textbf{F1m} \\",
        r"\hline",
    ]
    prev_exp = None
    for exp in exps:
        for ak in ['baseline', 'feateng']:
            lshort = '15f' if ak == 'baseline' else '63f'
            for mn in models:
                row = df[(df['ApproachKey'] == ak) &
                         (df['Experiment']  == exp) &
                         (df['Model']       == mn)]
                if row.empty:
                    continue
                r = row.iloc[0]
                delta_str = (f"{r['Delta_F1m']:+.4f}"
                             if ak == 'feateng' and not pd.isna(r.get('Delta_F1m'))
                             else '--')
                latex.append(
                    f"{lshort} & {exp} & {mn} & "
                    f"{r['Accuracy']:.4f} & {r['F1_MACRO']:.4f} & "
                    f"{r['AUC']:.4f} & {delta_str} \\\\"
                )
        latex.append(r"\hline")

    latex += [r"\end{tabular}", r"\end{table}"]
    (OUT_DIR / 'comparison_latex.txt').write_text("\n".join(latex), encoding='utf-8')
    print("  ✅ comparison_latex.txt")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 65)
    print("NeuroCap — Comparaison Baseline vs Feature Engineering")
    print("(lecture des results.json existants, sans ré-entraînement)")
    print("=" * 65)

    # Créer les dossiers de sortie
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    # ── Chargement des JSONs ───────────────────────────────────────────
    print("\nChargement des résultats :")
    try:
        base_json = load_json(BASELINE_JSON, 'Baseline ML (15f)')
        feat_json = load_json(FEATENG_JSON,  'FeatEng (63f)')
    except FileNotFoundError as e:
        print(e)
        return

    base_metrics = extract_loso_metrics(base_json)
    feat_metrics = extract_loso_metrics(feat_json)

    if not base_metrics:
        print("❌ Aucune donnée LOSO trouvée dans le JSON Baseline.")
        return
    if not feat_metrics:
        print("❌ Aucune donnée LOSO trouvée dans le JSON FeatEng.")
        return

    # ── DataFrame unifié ──────────────────────────────────────────────
    df = build_dataframe(base_metrics, feat_metrics)
    df.to_csv(OUT_DIR / 'comparison_table.csv', index=False, float_format='%.4f')
    print(f"\n  ✅ comparison_table.csv ({len(df)} lignes)")

    # ── Génération des figures ────────────────────────────────────────
    print("\n── Génération des figures ──")
    plot_barplot_metric(df, 'F1_MACRO',
                        'F1-MACRO LOSO — Baseline vs Feature Engineering',
                        '01_f1macro_barplot.png')
    plot_barplot_metric(df, 'Accuracy',
                        'Accuracy LOSO — Baseline vs Feature Engineering',
                        '02_accuracy_barplot.png')
    plot_barplot_metric(df, 'AUC',
                        'AUC LOSO — Baseline vs Feature Engineering',
                        '03_auc_barplot.png')
    plot_gain_heatmap(df)
    plot_radar(df, exp_ref='FULL')
    plot_summary_table(df)
    plot_best_per_exp(df)

    # ── Rapports texte + LaTeX ────────────────────────────────────────
    print("\n── Rapports texte et LaTeX ──")
    generate_reports(df,
                     base_metrics,
                     feat_metrics)

    print(f"\n{'='*65}")
    print(f"✅ Comparaison terminée")
    print(f"   Figures  : {FIGURES_DIR}/")
    print(f"   CSV      : {OUT_DIR / 'comparison_table.csv'}")
    print(f"   Rapport  : {OUT_DIR / 'comparison_summary.txt'}")
    print(f"   LaTeX    : {OUT_DIR / 'comparison_latex.txt'}")
    print(f"{'='*65}")


if __name__ == "__main__":
    main()