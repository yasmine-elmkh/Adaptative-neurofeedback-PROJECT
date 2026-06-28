"""
NeuroCap – Comparaison des 19 architectures DL (régression de score EEG).
Lit les metrics.json générés par DL_utils_regression et produit :
  - CSV récapitulatif par target (conc, stress)
  - Barplots comparatifs (MAE, R², AUC-ROC, F1-macro)
  - Heatmaps modèles × expériences
  - Classement pondéré (R², AUC, MAE, F1)
  - Temps d'entraînement par expérience et total
  - Résumé LOSO
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_BASE  = PROJECT_ROOT / "reports" / "Regression" / "DL"
COMPARE_DIR  = OUTPUT_BASE / "_comparison"
COMPARE_DIR.mkdir(parents=True, exist_ok=True)

ALL_MODELS = [
    "CNN1D", "CNN2D", "CNN3D", "EEGNet", "TCN",
    "CNN_LSTM_Att", "CNN_GRU_Att",
    "LSTM_1L", "LSTM_2L", "LSTM_Att",
    "BiLSTM_1L", "BiLSTM_2L", "BiLSTM_Att",
    "GRU_1L", "GRU_2L", "GRU_Att",
    "BiGRU_1L", "BiGRU_2L", "BiGRU_Att",
]
TARGETS      = ["conc", "stress"]
EXPERIMENTS  = ["A", "B", "C", "D", "FULL"]
METRICS_KEYS = ["mae", "rmse", "r2", "auc_roc", "f1_macro",
                "sensitivity", "specificity", "mcc", "balanced_accuracy",
                "train_time_sec"]


# ─── Chargement ───────────────────────────────────────────────────────────────
def load_all_metrics() -> pd.DataFrame:
    """Charge tous les metrics.json disponibles (standard + LOSO)."""
    rows = []
    total_times = {m: 0.0 for m in ALL_MODELS}

    for model in ALL_MODELS:
        for target in TARGETS:
            for exp in EXPERIMENTS:
                mf = OUTPUT_BASE / model / target / exp / "metrics.json"
                if not mf.exists():
                    continue
                with open(mf) as f:
                    m = json.load(f)
                rows.append({
                    "model": model, "target": target, "exp": exp, "source": "standard",
                    **{k: m.get(k, np.nan) for k in METRICS_KEYS},
                })
                total_times[model] += m.get("train_time_sec", 0)

            # LOSO
            lf = OUTPUT_BASE / model / target / "LOSO" / "metrics.json"
            if lf.exists():
                with open(lf) as f:
                    m = json.load(f)
                rows.append({
                    "model": model, "target": target, "exp": "LOSO", "source": "LOSO",
                    **{k: m.get(k, np.nan) for k in METRICS_KEYS},
                })
                total_times[model] += m.get("train_time_sec", 0)

    # Sauvegarde temps total par modèle
    for model, t in total_times.items():
        with open(COMPARE_DIR / f"{model}_total_time.json", "w") as f:
            json.dump({"model": model, "total_time_sec": t,
                       "total_time_hours": t / 3600}, f, indent=2)

    return pd.DataFrame(rows)


# ─── Graphiques ───────────────────────────────────────────────────────────────
def plot_comparison_bars(df, metric, target, title, filename):
    sub   = df[(df["target"] == target) & (df["source"] == "standard")]
    pivot = sub.pivot_table(index="model", columns="exp", values=metric)
    pivot = pivot.reindex(ALL_MODELS).dropna(how="all")
    if pivot.empty:
        return
    fig, ax = plt.subplots(figsize=(14, 6))
    pivot.plot(kind="bar", ax=ax, width=0.8)
    ax.set_title(title, fontsize=14, fontweight="bold")
    ax.set_ylabel(metric.upper())
    ax.set_xlabel("")
    ax.legend(title="Expérience", bbox_to_anchor=(1.02, 1))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / target / filename, dpi=150, bbox_inches="tight")
    plt.close()


def plot_heatmap(df, metric, target, title, filename):
    sub   = df[(df["target"] == target) & (df["source"] == "standard")]
    pivot = sub.pivot_table(index="model", columns="exp", values=metric)
    pivot = pivot.reindex(ALL_MODELS).dropna(how="all")
    if pivot.empty:
        return
    # MAE/RMSE : rouge = élevé = mauvais → colormap inversée
    cmap = "YlOrRd_r" if metric in ("mae", "rmse") else "YlOrRd"
    fig, ax = plt.subplots(figsize=(10, 9))
    sns.heatmap(pivot, annot=True, fmt=".3f", cmap=cmap,
                ax=ax, linewidths=0.5)
    ax.set_title(title, fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / target / filename, dpi=150, bbox_inches="tight")
    plt.close()


def compute_ranking(df, target) -> pd.DataFrame:
    """
    Classement composite : AUC×0.4 + Sensitivity×0.3 + MCC×0.2 + Specificity×0.1
    [Fawcett 2006; Chicco & Jurman 2020; Fairclough 2009; Youden 1950]
    """
    sub = df[(df["target"] == target) & (df["exp"] == "A")].copy()
    if sub.empty:
        sub = df[df["target"] == target].copy()
    if sub.empty:
        return pd.DataFrame()
    for col in ("auc_roc", "sensitivity", "specificity", "mcc", "balanced_accuracy"):
        if col not in sub.columns:
            sub[col] = 0.
    sub["composite"] = (0.40 * sub["auc_roc"]
                      + 0.30 * sub["sensitivity"]
                      + 0.20 * sub["mcc"]
                      + 0.10 * sub["specificity"])
    ranking = sub.sort_values("composite", ascending=False)[
        ["model", "composite", "auc_roc", "sensitivity", "specificity",
         "mcc", "balanced_accuracy", "mae", "rmse", "r2",
         "train_time_sec"]
    ].reset_index(drop=True)
    ranking.index += 1
    ranking.index.name = "Rang"
    return ranking


# Couleurs fixes des 4 composantes (cohérentes avec baseline + TL)
_COMP_COLORS = {
    'auc_w':  '#2980B9',
    'sens_w': '#27AE60',
    'mcc_w':  '#F39C12',
    'spec_w': '#8E44AD',
}


def plot_composite_breakdown_dl(df, target):
    """
    Figure à 2 panneaux :
      - Haut : barres empilées des 4 contributions pondérées au score composite
      - Bas  : métriques brutes (AUC, Sensitivity, Specificity, MCC) côte à côte

    Permet d'argumenter le choix de l'architecture en montrant comment chaque
    métrique contribue au score composite retenu [Ferri et al. 2009].
    """
    import matplotlib.patches as mpatches

    sub = df[(df["target"] == target) & (df["exp"] == "A")].copy()
    if sub.empty:
        sub = df[df["target"] == target].copy()
    if sub.empty:
        return

    for col in ("auc_roc", "sensitivity", "specificity", "mcc"):
        if col not in sub.columns:
            sub[col] = 0.

    sub["auc_w"]  = 0.40 * sub["auc_roc"].clip(lower=0)
    sub["sens_w"] = 0.30 * sub["sensitivity"].clip(lower=0)
    sub["mcc_w"]  = 0.20 * sub["mcc"].clip(lower=0)
    sub["spec_w"] = 0.10 * sub["specificity"].clip(lower=0)
    sub["composite"] = sub["auc_w"] + sub["sens_w"] + sub["mcc_w"] + sub["spec_w"]
    sub = sub.sort_values("composite", ascending=False).reset_index(drop=True)

    models = sub["model"].tolist()
    n = len(models)
    x = np.arange(n)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(16, n * 0.85), 12))
    fig.suptitle(
        f"Décomposition du Score Composite — 19 architectures DL  |  {target.upper()}  |  Exp. A\n"
        f"Score = AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10\n"
        f"[Fawcett 2006; Chicco & Jurman 2020; Fairclough 2009; Youden 1950]",
        fontsize=11, fontweight="bold"
    )

    # ── Panneau 1 : contributions empilées ─────────────────────────────────
    bottoms = np.zeros(n)
    for key, col, label in [
        ('auc_w',  'auc_w',  f'AUC × 0.40  [Fawcett 2006]'),
        ('sens_w', 'sens_w', f'Sensitivity × 0.30  [Fairclough 2009]'),
        ('mcc_w',  'mcc_w',  f'MCC × 0.20  [Chicco & Jurman 2020]'),
        ('spec_w', 'spec_w', f'Specificity × 0.10  [Youden 1950]'),
    ]:
        vals = sub[col].values
        ax1.bar(x, vals, bottom=bottoms, color=_COMP_COLORS[key],
                alpha=0.85, edgecolor='white', label=label)
        bottoms += vals

    for i, (comp, auc, sens, mcc, spec) in enumerate(zip(
            sub["composite"], sub["auc_roc"], sub["sensitivity"],
            sub["mcc"], sub["specificity"])):
        ax1.text(i, comp + 0.008, f'{comp:.3f}', ha='center', va='bottom',
                 fontsize=6.5, fontweight='bold')

    ax1.set_xticks(x)
    ax1.set_xticklabels(models, rotation=45, ha='right', fontsize=7.5)
    ax1.set_ylabel('Score composite (contributions pondérées)', fontsize=9)
    ax1.set_title('Contributions pondérées au score composite (tri décroissant)', fontsize=10)
    ax1.axhline(0.50, color='#27AE60', lw=1.5, ls='--', alpha=0.7, label='Seuil bon (0.50)')
    ax1.axhline(0.35, color='#F39C12', lw=1.2, ls=':',  alpha=0.6, label='Seuil borderline (0.35)')
    ax1.set_ylim(0, min(1.0, sub["composite"].max() * 1.25))
    ax1.legend(loc='upper right', fontsize=7.5, framealpha=0.85)
    ax1.grid(axis='y', alpha=0.25)

    # ── Panneau 2 : métriques brutes côte à côte ────────────────────────────
    metric_defs = [
        ('auc_roc',     'AUC-ROC',     _COMP_COLORS['auc_w']),
        ('sensitivity', 'Sensitivity', _COMP_COLORS['sens_w']),
        ('mcc',         'MCC',         _COMP_COLORS['mcc_w']),
        ('specificity', 'Specificity', _COMP_COLORS['spec_w']),
    ]
    w = 0.20
    for j, (col, label, color) in enumerate(metric_defs):
        vals = sub[col].clip(lower=0).values
        offset = (j - 1.5) * w
        bars = ax2.bar(x + offset, vals, w, label=label,
                       color=color, alpha=0.82, edgecolor='white')
        for bar, v in zip(bars, vals):
            if v > 0.01:
                ax2.text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + 0.005, f'{v:.2f}',
                         ha='center', va='bottom', fontsize=5.5)

    ax2.set_xticks(x)
    ax2.set_xticklabels(models, rotation=45, ha='right', fontsize=7.5)
    ax2.set_ylabel('Valeur brute de la métrique', fontsize=9)
    ax2.set_title('Métriques brutes individuelles (AUC, Sensitivity, MCC, Specificity)', fontsize=10)
    ax2.axhline(0.50, color='gray', lw=1.0, ls='--', alpha=0.5)
    ax2.set_ylim(0, 1.15)
    ax2.legend(loc='upper right', fontsize=8, framealpha=0.85)
    ax2.grid(axis='y', alpha=0.25)

    plt.tight_layout()
    (COMPARE_DIR / target).mkdir(exist_ok=True)
    plt.savefig(COMPARE_DIR / target / "composite_breakdown.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  composite_breakdown_{target}.png")


def save_composite_outputs_dl(df, target):
    """
    Sauvegarde le ranking composite en JSON et TXT pour argumentation du choix de modèle.
    Inclut les 4 métriques constitutives + contributions pondérées.
    """
    sub = df[(df["target"] == target) & (df["exp"] == "A")].copy()
    if sub.empty:
        sub = df[df["target"] == target].copy()
    if sub.empty:
        return

    for col in ("auc_roc", "sensitivity", "specificity", "mcc", "balanced_accuracy", "mae", "r2"):
        if col not in sub.columns:
            sub[col] = 0.

    sub["composite"] = (0.40 * sub["auc_roc"].clip(lower=0)
                      + 0.30 * sub["sensitivity"].clip(lower=0)
                      + 0.20 * sub["mcc"].clip(lower=0)
                      + 0.10 * sub["specificity"].clip(lower=0))
    sub = sub.sort_values("composite", ascending=False).reset_index(drop=True)

    # ── JSON ─────────────────────────────────────────────────────────────
    out_dir = COMPARE_DIR / target
    out_dir.mkdir(exist_ok=True)

    ranking_json = []
    for rank, (_, row) in enumerate(sub.iterrows(), 1):
        auc  = float(row.get("auc_roc", 0))
        sens = float(row.get("sensitivity", 0))
        mcc  = float(row.get("mcc", 0))
        spec = float(row.get("specificity", 0))
        ranking_json.append({
            "rank":    rank,
            "model":   row["model"],
            "target":  target,
            "exp":     row.get("exp", "A"),
            "composite": round(float(row["composite"]), 4),
            "metrics": {
                "AUC":         round(auc,  4),
                "Sensitivity": round(sens, 4),
                "MCC":         round(mcc,  4),
                "Specificity": round(spec, 4),
                "Balanced_Acc": round(float(row.get("balanced_accuracy", 0)), 4),
                "MAE":         round(float(row.get("mae", 0)), 4),
                "R2":          round(float(row.get("r2", 0)), 4),
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
            ],
        })

    json_path = out_dir / "composite_scores.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"target": target, "family": "DL",
                   "composite_formula": "AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10",
                   "ranking": ranking_json}, f, indent=2, ensure_ascii=False)
    print(f"  composite_scores_{target}.json")

    # ── TXT ──────────────────────────────────────────────────────────────
    lines = []
    lines.append("=" * 90)
    lines.append(f"NeuroCap — Score Composite DL — {target.upper()}")
    lines.append("Formule : AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10")
    lines.append("Justification par métrique :")
    lines.append("  AUC  (w=0.40) : threshold-free, recommandée pour EEG/BCI [Fawcett 2006; Lotte et al. 2018]")
    lines.append("  Sens (w=0.30) : FN coûteux en monitoring cognitif [Fairclough 2009; Brodersen et al. 2010]")
    lines.append("  MCC  (w=0.20) : seule métrique utilisant les 4 cellules de la matrice [Chicco & Jurman 2020]")
    lines.append("  Spec (w=0.10) : complète Sens, FP moins coûteux [Youden 1950]")
    lines.append("=" * 90)
    lines.append(f"\n{'Rang':<5} {'Architecture':<18} {'Score':>7} │ "
                 f"{'AUC':>7} {'Sens':>7} {'MCC':>7} {'Spec':>7} │ "
                 f"{'AUC×0.4':>8} {'S×0.3':>7} {'M×0.2':>7} {'Sp×0.1':>7}")
    lines.append("─" * 90)
    for item in ranking_json:
        m  = item["metrics"]
        wc = item["weighted_contributions"]
        lines.append(
            f"  {item['rank']:<3} {item['model']:<18} {item['composite']:>7.4f} │ "
            f"{m['AUC']:>7.4f} {m['Sensitivity']:>7.4f} {m['MCC']:>7.4f} {m['Specificity']:>7.4f} │ "
            f"{wc['AUC_x040']:>8.4f} {wc['Sensitivity_x030']:>7.4f} "
            f"{wc['MCC_x020']:>7.4f} {wc['Specificity_x010']:>7.4f}"
        )
    lines.append("\n" + "=" * 90)
    lines.append("★ MEILLEURE ARCHITECTURE : " + ranking_json[0]["model"] if ranking_json else "")
    if ranking_json:
        best = ranking_json[0]
        lines.append(f"  Score composite = {best['composite']:.4f}")
        for k, v in best["metrics"].items():
            lines.append(f"  {k:<15}: {v:.4f}")

    txt_path = out_dir / "composite_summary.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  composite_summary_{target}.txt")


# ─── Decision Dashboard DL ────────────────────────────────────────────────────
_DL_DECISION = [
    ("auc_roc",           "AUC ROC",          0.65, 0.55),
    ("sensitivity",       "Sensitivity",       0.50, 0.40),
    ("specificity",       "Specificity",       0.50, 0.40),
    ("mcc",               "MCC",               0.20, 0.10),
    ("balanced_accuracy", "Balanced Accuracy", 0.65, 0.55),
]
_MODEL_PALETTE = plt.cm.tab20.colors


def plot_decision_dashboard_dl(df, target):
    """
    Dashboard décision pour les 19 architectures DL.
    1 image : 5 barplots (AUC, Sens, Spec, MCC, BalAcc) + tableau pass/fail.
    """
    exp_ref = "A"
    sub = df[(df["target"] == target) & (df["exp"] == exp_ref)].copy()
    if sub.empty:
        sub = df[df["target"] == target].copy()
    if sub.empty:
        print(f"  [SKIP] decision_dashboard_{target}.png — pas de données")
        return

    for col in ("sensitivity", "specificity", "mcc", "balanced_accuracy"):
        if col not in sub.columns:
            sub[col] = 0.

    models = sub["model"].tolist()
    n      = len(models)
    colors_models = [_MODEL_PALETTE[i % 20] for i in range(n)]

    def _bc(v, g, b):
        if v >= g:  return '#27AE60'
        if v >= b:  return '#F39C12'
        return '#E74C3C'

    fig = plt.figure(figsize=(26, 15))
    gs  = fig.add_gridspec(2, 5, height_ratios=[1.5, 1.0],
                           hspace=0.55, wspace=0.35,
                           top=0.88, bottom=0.04, left=0.04, right=0.97)
    fig.suptitle(
        f'Dashboard Décision — 19 Architectures DL  |  {target.upper()}  |  Exp. {exp_ref}\n'
        f'Ordre priorité : AUC (GO/NO-GO)  →  Sensitivity  →  MCC  →  Décision finale',
        fontsize=13, fontweight='bold'
    )

    for ci, (metric, label, good_t, border_t) in enumerate(_DL_DECISION):
        ax   = fig.add_subplot(gs[0, ci])
        vals = [float(sub[sub["model"] == m][metric].values[0])
                if m in sub["model"].values else 0. for m in models]
        cols = [_bc(v, good_t, border_t) for v in vals]
        x    = np.arange(n)
        bars = ax.bar(x, vals, 0.7, color=cols, alpha=0.88, edgecolor='white')
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                    f'{v:.2f}', ha='center', va='bottom', fontsize=5.5, fontweight='bold')
        ax.axhline(good_t,   color='#27AE60', lw=1.8, ls='--', alpha=0.85)
        ax.axhline(border_t, color='#F39C12', lw=1.2, ls=':',  alpha=0.70)
        ax.set_xticks(x)
        ax.set_xticklabels([m[:7] for m in models], rotation=55, ha='right', fontsize=6)
        ax.set_ylim(0, 1.18)
        ax.set_title(f'{label} ↑', fontsize=9, fontweight='bold')
        ax.grid(axis='y', alpha=0.25)

    import matplotlib.patches as mpatches
    legend_patches = [
        mpatches.Patch(color='#27AE60', label='✅ Bon (≥ seuil vert)'),
        mpatches.Patch(color='#F39C12', label='⚠️ Borderline'),
        mpatches.Patch(color='#E74C3C', label='❌ Insuffisant'),
    ]
    fig.legend(handles=legend_patches, loc='upper right',
               bbox_to_anchor=(0.97, 0.94), fontsize=9, ncol=3, framealpha=0.9)

    # Tableau de décision
    ax_tbl = fig.add_subplot(gs[1, :])
    ax_tbl.axis('off')
    ax_tbl.set_title(
        'Seuils : AUC≥0.65 | Sensitivity≥0.50 | Specificity≥0.50 | MCC≥0.20 | Bal.Acc≥0.65   '
        '(vert=bon · orange=borderline · rouge=insuffisant)',
        fontsize=8.5, fontweight='bold', pad=6
    )
    headers  = ['Modèle', 'AUC ROC', 'Sensitivity', 'Specificity', 'MCC', 'Bal.Acc', 'DÉCISION']
    tbl_rows, tbl_colors = [], []
    for m in models:
        row_data = [m]
        row_col  = ['#ECF0F1']
        n_good   = 0
        for metric, _, good_t, border_t in _DL_DECISION:
            v = float(sub[sub["model"]==m][metric].values[0]) if m in sub["model"].values else 0.
            row_data.append(f'{v:.3f}')
            if v >= good_t:
                row_col.append('#D5F5E3'); n_good += 1
            elif v >= border_t:
                row_col.append('#FDEBD0')
            else:
                row_col.append('#FADBD8')
        if n_good >= 4:
            d, dc = '✅ Recommandé', '#D5F5E3'
        elif n_good >= 2:
            d, dc = '⚠️ Acceptable', '#FDEBD0'
        else:
            d, dc = '❌ Rejeté',     '#FADBD8'
        row_data.append(d); row_col.append(dc)
        tbl_rows.append(row_data); tbl_colors.append(row_col)

    tbl = ax_tbl.table(cellText=tbl_rows, colLabels=headers,
                       cellLoc='center', loc='center', bbox=[0, 0, 1, 1],
                       cellColours=tbl_colors)
    tbl.auto_set_font_size(False); tbl.set_fontsize(7.5)
    for col in range(len(headers)):
        tbl[(0, col)].set_facecolor('#1A3A4A')
        tbl[(0, col)].set_text_props(color='white', fontweight='bold')

    out_path = COMPARE_DIR / target / "decision_dashboard.png"
    plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  ✅ decision_dashboard_{target}.png")


def plot_ranking_bar(ranking, target):
    if ranking.empty:
        return
    colors = ["#27AE60" if i < 3 else "#3498DB" if i < 8 else "#95A5A6"
              for i in range(len(ranking))]
    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(ranking["model"][::-1], ranking["composite"][::-1],
                   color=colors[::-1])
    ax.set_xlabel("Score composite  (AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10)")
    ax.set_title(f"Classement – {target.upper()} (Exp. A)",
                 fontsize=14, fontweight="bold")
    for bar, val in zip(bars, ranking["composite"][::-1]):
        ax.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9)
    ax.set_xlim(0, 1.05)
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / target / "ranking_bar.png", dpi=150, bbox_inches="tight")
    plt.close()


def plot_training_times(df, target):
    """Temps d'entraînement pour l'expérience A (un target donné)."""
    sub = df[(df["target"] == target) & (df["exp"] == "A")].dropna(
        subset=["train_time_sec"])
    if sub.empty:
        return
    sub = sub.sort_values("train_time_sec")
    colors = []
    for m in sub["model"]:
        if "CNN" in m and "LSTM" not in m and "GRU" not in m:
            colors.append("#2ecc71")
        elif "EEG" in m:
            colors.append("#3498db")
        elif "TCN" in m:
            colors.append("#9b59b6")
        elif "Att" in m:
            colors.append("#e74c3c")
        elif "Bi" in m:
            colors.append("#e67e22")
        else:
            colors.append("#f39c12")
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(sub["model"], sub["train_time_sec"], color=colors)
    ax.set_xlabel("Temps d'entraînement (secondes) – Expérience A")
    ax.set_title(f"Temps d'entraînement – {target.upper()} (Exp. A)",
                 fontsize=14, fontweight="bold")
    for bar, val in zip(bars, sub["train_time_sec"]):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
                f"{val:.0f}s", va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / target / "training_times_expA.png",
                dpi=150, bbox_inches="tight")
    plt.close()


def plot_total_times():
    """Temps total par modèle (toutes expériences + LOSO + 2 targets)."""
    data = []
    for model in ALL_MODELS:
        tf = COMPARE_DIR / f"{model}_total_time.json"
        if tf.exists():
            with open(tf) as f:
                d = json.load(f)
            data.append((d["model"], d["total_time_sec"]))
    if not data:
        return
    data.sort(key=lambda x: x[1], reverse=True)
    models, times = zip(*data)
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(models, [t / 3600 for t in times], color="#3498db")
    ax.set_xlabel("Temps total (heures)")
    ax.set_title("Temps total par architecture (5 exp × 2 targets + LOSO)",
                 fontsize=14, fontweight="bold")
    for bar, t in zip(bars, times):
        ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
                f"{t/3600:.1f}h", va="center", fontsize=9)
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / "total_execution_time.png",
                dpi=150, bbox_inches="tight")
    plt.close()


def plot_mae_vs_r2(df, target):
    """Scatter MAE vs R² (Exp. A) pour comparer les architectures."""
    sub = df[(df["target"] == target) & (df["exp"] == "A")].dropna(
        subset=["mae", "r2"])
    if sub.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.scatter(sub["mae"], sub["r2"], s=80, color="#2980B9", alpha=0.8)
    for _, row in sub.iterrows():
        ax.annotate(row["model"], (row["mae"], row["r2"]),
                    textcoords="offset points", xytext=(5, 3), fontsize=8)
    ax.set_xlabel("MAE (↓ mieux)")
    ax.set_ylabel("R² (↑ mieux)")
    ax.set_title(f"MAE vs R² – {target.upper()} (Exp. A)",
                 fontsize=13, fontweight="bold")
    ax.axhline(0, color="gray", ls="--", lw=0.8)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / target / "mae_vs_r2.png",
                dpi=150, bbox_inches="tight")
    plt.close()


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("NeuroCap – Comparaison des 19 architectures DL (régression)")
    print("=" * 70)

    df = load_all_metrics()
    if df.empty:
        print("Aucune métrique disponible. Lancez les entraînements d'abord.")
        return

    print(f"\n{len(df)} résultats | "
          f"{df['model'].nunique()} modèles | "
          f"{df['target'].nunique()} cibles | "
          f"{df['exp'].nunique()} expériences")

    # CSV global
    df[["model", "target", "exp", "source"] + METRICS_KEYS].to_csv(
        COMPARE_DIR / "all_results.csv", index=False)
    print(f"\nCSV → {COMPARE_DIR / 'all_results.csv'}")

    for target in TARGETS:
        (COMPARE_DIR / target).mkdir(exist_ok=True)
        df_std = df[(df["target"] == target) & (df["source"] == "standard")]

        # Barplots + heatmaps
        for metric, label in [
            ("mae",     "MAE"),
            ("r2",      "R²"),
            ("auc_roc", "AUC-ROC"),
            ("f1_macro","F1-macro"),
        ]:
            plot_comparison_bars(df, metric, target,
                                 f"{label} par modèle – {target.upper()}",
                                 f"barplot_{metric}.png")
            plot_heatmap(df, metric, target,
                         f"Heatmap {label} – {target.upper()}",
                         f"heatmap_{metric}.png")
        print(f"\n{target.upper()} : barplots + heatmaps générés")

        # Classement
        ranking = compute_ranking(df, target)
        if not ranking.empty:
            ranking.to_csv(COMPARE_DIR / target / "ranking.csv")
            plot_ranking_bar(ranking, target)
            print(f"\nClassement {target.upper()} (Exp. A) :")
            print(ranking.head(10).to_string())

        # MAE vs R²
        plot_mae_vs_r2(df, target)

        # Temps entraînement Exp. A
        plot_training_times(df, target)
        print(f"  training_times_expA.png")

        # Dashboard de décision
        plot_decision_dashboard_dl(df, target)
        print(f"  decision_dashboard_{target}.png")

        # ── NOUVEAU : décomposition composite + exports JSON/TXT ─────────
        plot_composite_breakdown_dl(df, target)
        save_composite_outputs_dl(df, target)

        # LOSO
        df_loso = df[(df["target"] == target) & (df["source"] == "LOSO")]
        if not df_loso.empty:
            df_loso.to_csv(COMPARE_DIR / target / "loso_results.csv", index=False)
            print(f"\nLOSO {target.upper()} (top 5 composite) :")
            for col in ("auc_roc", "sensitivity", "specificity", "mcc"):
                if col not in df_loso.columns:
                    df_loso[col] = 0.
            df_loso["composite"] = (0.40 * df_loso["auc_roc"].clip(lower=0)
                                  + 0.30 * df_loso["sensitivity"].clip(lower=0)
                                  + 0.20 * df_loso["mcc"].clip(lower=0)
                                  + 0.10 * df_loso["specificity"].clip(lower=0))
            print(df_loso.sort_values("composite", ascending=False).head(5)[
                ["model", "composite", "auc_roc", "sensitivity", "mcc"]].to_string(index=False))

    # Temps total (tous targets confondus)
    plot_total_times()
    print(f"\nTemps total → total_execution_time.png")
    print(f"\nTous les résultats dans : {COMPARE_DIR}")


if __name__ == "__main__":
    main()
