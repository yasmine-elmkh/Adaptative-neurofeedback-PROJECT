"""
compare_all_models.py
=====================
Compare ALL model families (ML Baselines, Deep Learning, Transfer Learning)
on Concentration and Stress regression tasks.

Goal : decide which model to use in NeuroCap app.

Outputs (saved to reports/Regression/Comparaison_Globale/):
  - comparison_all_raw.csv          : all experiments
  - comparison_all_best.csv         : best exp per model
  - bar_MAE_R2_AUC_{target}.png     : grouped bar chart MAE / R² / AUC
  - f1_acc_{target}.png             : F1-macro + Balanced Accuracy
  - heatmap_{target}.png            : model × metric heat-map
  - radar_{target}.png              : radar chart top models
  - 7_criteria_{target}.png         : pass/fail for 7 clinical criteria
  - family_auc_{target}.png         : AUC distribution per family
  - recommendation.txt              : deployment recommendation
"""

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ─────────────────────────────── paths ────────────────────────────────────
ROOT = Path(__file__).resolve().parents[3]
REPORTS = ROOT / "reports" / "Regression"
OUT_DIR = REPORTS / "Comparaison_Globale"
OUT_DIR.mkdir(parents=True, exist_ok=True)

EXPS = ["A", "B", "C", "D"]
TARGETS = ["conc", "stress"]

ML_FEAT_DIRS = {
    "feat15":       REPORTS / "Baseline" / "feat15",
    "feat15_smote": REPORTS / "Baseline" / "feat15_smote",
    "feat78":       REPORTS / "Baseline" / "feat78",
    "feat78_smote": REPORTS / "Baseline" / "feat78_smote",
}

TL_STRATEGY_LABELS = {
    "EEGNet_LayerReplacement":  "TL-LayerRepl",
    "EEGNet_FullFT":            "TL-FullFT",
    "EEGNet_FeatureExtraction": "TL-FeatExtract",
}

FAMILY_COLORS = {
    "ML":  "#4C72B0",
    "DL":  "#DD8452",
    "TL":  "#55A868",
}

TARGET_FULL = {"conc": "Concentration", "stress": "Stress"}

# ── 7 critères cliniques : seuils pass / borderline / fail ────────────────
CRITERIA = [
    # (colonne,         label,              pass_fn,                    border_fn)
    ("auc_roc",         "AUC\n≥0.70",       lambda v: v >= 0.70,        lambda v: v >= 0.60),
    ("p_val",           "p-val\n<0.001",    lambda v: v < 0.001,        lambda v: v < 0.05),
    ("cv_r2",           "CV-R²\n≤5%",       lambda v: v <= 5.0,         lambda v: v <= 20.0),
    ("ece",             "ECE\n≤0.05",       lambda v: v <= 0.05,        lambda v: v <= 0.15),
    ("loa_width",       "LoA\n≤4pts",       lambda v: v <= 4.0,         lambda v: v <= 8.0),
    ("icc_val",         "ICC\n≥0.90",       lambda v: v >= 0.90,        lambda v: v >= 0.75),
    ("ci_width",        "CI-w\n≤0.05",      lambda v: v <= 0.05,        lambda v: v <= 0.10),
]

CRITERIA_REFS = [
    "Hosmer &\nLemeshow (2000)",
    "Ojala &\nGarriga (2010)",
    "Liao et al.\n(2018)",
    "Guo et al.\n(2017)",
    "Bland &\nAltman (1986)",
    "Koo &\nLi (2016)",
    "Efron &\nTibshirani (1994)",
]

# ──────────────────────────────── loaders ─────────────────────────────────

def _extract_7_criteria_dl_tl(data: dict) -> dict:
    """Extract the 7 clinical criteria from a DL/TL metrics.json dict."""
    bstrap = data.get("bootstrap", {}) or {}
    auc_b  = bstrap.get("auc_roc", {}) or {}
    ci_lo  = auc_b.get("ci_lo", np.nan)
    ci_hi  = auc_b.get("ci_hi", np.nan)

    cal   = data.get("calibration", {}) or {}
    ba    = data.get("bland_altman", {}) or {}
    icc_d = data.get("icc", {}) or {}
    stab  = (data.get("stability", {}) or {}).get("r2", {}) or {}
    perm  = (data.get("permutation", {}) or {}).get("auc_roc", {}) or {}

    return {
        "ci_width":  ci_hi - ci_lo if not (np.isnan(ci_lo) or np.isnan(ci_hi)) else np.nan,
        "ece":       cal.get("ece", np.nan),
        "loa_width": ba.get("loa_width", np.nan),
        "icc_val":   icc_d.get("icc", np.nan),
        "cv_r2":     stab.get("cv_pct", np.nan),
        "p_val":     perm.get("p_value", np.nan),
    }


def _extract_7_criteria_ml(prof: dict) -> dict:
    """Extract the 7 clinical criteria from ML professional sub-dict."""
    bci   = prof.get("bootstrap_ci", {}) or {}
    auc_b = bci.get("auc_roc", {}) or {}
    ci_lo = auc_b.get("ci_lo", np.nan)
    ci_hi = auc_b.get("ci_hi", np.nan)

    cal   = prof.get("calibration", {}) or {}
    ba    = prof.get("bland_altman", {}) or {}
    icc_d = prof.get("icc", {}) or {}
    stab  = (prof.get("stability", {}) or {}).get("r2", {}) or {}
    perm  = (prof.get("permutation", {}) or {}).get("auc_roc", {}) or {}

    return {
        "ci_width":  ci_hi - ci_lo if not (np.isnan(ci_lo) or np.isnan(ci_hi)) else np.nan,
        "ece":       cal.get("ece", np.nan),
        "loa_width": ba.get("loa_width", np.nan),
        "icc_val":   icc_d.get("icc", np.nan),
        "cv_r2":     stab.get("cv_pct", np.nan),
        "p_val":     perm.get("p_value", np.nan),
    }


def _row(family, model_name, target, exp, data: dict, is_ml: bool = False) -> dict:
    auc  = data.get("auc_roc",     np.nan)
    sens = data.get("sensitivity", np.nan)
    mcc  = data.get("mcc",         np.nan)
    spec = data.get("specificity", np.nan)
    # Score composite : AUC×0.40 + Sens×0.30 + MCC×0.20 + Spec×0.10
    # [Fawcett 2006; Chicco & Jurman 2020; Fairclough 2009; Youden 1950]
    if all(not np.isnan(v) for v in (auc, sens, mcc, spec)):
        composite = (0.40 * max(auc, 0) + 0.30 * max(sens, 0)
                   + 0.20 * max(mcc, 0) + 0.10 * max(spec, 0))
    else:
        composite = np.nan
    base = {
        "family":            family,
        "model":             model_name,
        "target":            target,
        "exp":               exp,
        "mae":               data.get("mae", np.nan),
        "r2":                data.get("r2",  np.nan),
        "auc_roc":           auc,
        "accuracy":          data.get("accuracy", np.nan),
        "balanced_accuracy": data.get("balanced_accuracy", np.nan),
        "sensitivity":       sens,
        "specificity":       spec,
        "mcc":               mcc,
        "composite":         composite,
        "f1_macro":          data.get("f1_macro", np.nan),
        "f1_weighted":       data.get("f1_weighted", np.nan),
        "n_samples":         data.get("n_samples", np.nan),
    }

    if is_ml:
        crit = _extract_7_criteria_ml(data.get("professional", {}) or {})
    else:
        crit = _extract_7_criteria_dl_tl(data)

    base.update(crit)
    return base


def load_ml_baselines() -> list[dict]:
    rows = []
    for feat_name, feat_dir in ML_FEAT_DIRS.items():
        for target in TARGETS:
            result_file = feat_dir / target / f"results_{target}.json"
            if not result_file.exists():
                continue
            with open(result_file) as f:
                data = json.load(f)
            loso = data.get("loso", {})
            for exp in EXPS:
                if exp not in loso:
                    continue
                for model_name, metrics in loso[exp].items():
                    if model_name.startswith("_") or not isinstance(metrics, dict):
                        continue
                    if not isinstance(metrics.get("auc_roc"), (int, float)):
                        continue
                    rows.append(_row(
                        family=f"ML-{feat_name}",
                        model_name=f"{model_name} ({feat_name})",
                        target=target,
                        exp=exp,
                        data=metrics,
                        is_ml=True,
                    ))
    return rows


def load_dl_results() -> list[dict]:
    rows = []
    dl_dir = REPORTS / "DL"
    if not dl_dir.exists():
        return rows
    for arch_dir in sorted(dl_dir.iterdir()):
        if not arch_dir.is_dir():
            continue
        arch = arch_dir.name
        for target in TARGETS:
            for exp in EXPS:
                mfile = arch_dir / target / exp / "metrics.json"
                if not mfile.exists():
                    continue
                with open(mfile) as f:
                    data = json.load(f)
                rows.append(_row(
                    family="DL",
                    model_name=arch,
                    target=target,
                    exp=exp,
                    data=data,
                    is_ml=False,
                ))
    return rows


def load_tl_results() -> list[dict]:
    rows = []
    tl_dir = REPORTS / "TL"
    if not tl_dir.exists():
        return rows
    for strat_dir in sorted(tl_dir.iterdir()):
        if not strat_dir.is_dir():
            continue
        label = TL_STRATEGY_LABELS.get(strat_dir.name, strat_dir.name)
        for target in TARGETS:
            for exp in EXPS:
                mfile = strat_dir / target / exp / "metrics.json"
                if not mfile.exists():
                    continue
                with open(mfile) as f:
                    data = json.load(f)
                rows.append(_row(
                    family="TL",
                    model_name=label,
                    target=target,
                    exp=exp,
                    data=data,
                    is_ml=False,
                ))
    return rows


# ──────────────────────────── aggregation ─────────────────────────────────

def build_dataframe() -> pd.DataFrame:
    rows = load_ml_baselines() + load_dl_results() + load_tl_results()
    return pd.DataFrame(rows)


def best_per_model(df: pd.DataFrame) -> pd.DataFrame:
    """Meilleur exp par modèle, trié par score composite (AUC×0.4 + Sens×0.3 + MCC×0.2 + Spec×0.1)."""
    sort_col = "composite" if "composite" in df.columns else "auc_roc"
    return (
        df.sort_values(sort_col, ascending=False, na_position="last")
          .drop_duplicates(subset=["family", "model", "target"])
          .reset_index(drop=True)
    )


# ────────────────────────────── helpers ───────────────────────────────────

def _family_color(fam: str) -> str:
    if fam.startswith("ML"):
        return FAMILY_COLORS["ML"]
    return FAMILY_COLORS.get(fam, "#999999")


# ────────────────────────────── plots ─────────────────────────────────────

def plot_grouped_bars(best_df: pd.DataFrame, target: str):
    """3-panel bar chart: MAE, R², AUC — top 5 per family."""
    sub = best_df[best_df["target"] == target].copy()
    sub = sub.sort_values(["family", "auc_roc"], ascending=[True, False])
    sub = sub.groupby("family").head(5).reset_index(drop=True)

    labels = [f"{r.model}\n({r.exp})" for _, r in sub.iterrows()]
    x = np.arange(len(labels))

    fig, axes = plt.subplots(3, 1, figsize=(max(14, len(labels) * 0.8), 14),
                             sharex=True)
    fig.suptitle(f"Comparaison des modèles — {TARGET_FULL[target]}",
                 fontsize=14, fontweight="bold", y=0.98)

    panels = [
        ("mae",     "MAE ↓ (pts sur 0–10)", (1.8, 3.2)),
        ("r2",      "R² ↑",                  (-0.4, 0.45)),
        ("auc_roc", "AUC-ROC ↑",             (0.45, 0.85)),
    ]

    for ax, (metric, ylabel, ylim) in zip(axes, panels):
        vals  = sub[metric].values
        colors = [_family_color(f) for f in sub["family"]]
        bars  = ax.bar(x, vals, color=colors, edgecolor="white", linewidth=0.5, alpha=0.88)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_ylim(*ylim)
        ax.axhline(0, color="gray", linewidth=0.5, linestyle="--")
        if metric == "auc_roc":
            ax.axhline(0.5, color="red", linewidth=1, linestyle=":", label="aléatoire")
            ax.axhline(0.7, color="green", linewidth=1, linestyle="--", label="seuil acceptable")
            ax.legend(fontsize=8)
        for bar, val in zip(bars, vals):
            if not np.isnan(val):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                        f"{val:.3f}", ha="center", va="bottom", fontsize=7.5, rotation=45,
                        fontweight="bold")
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    patches = [mpatches.Patch(color=c, label=f) for f, c in FAMILY_COLORS.items()]
    fig.legend(handles=patches, loc="upper right", fontsize=9, framealpha=0.8)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    out = OUT_DIR / f"bar_MAE_R2_AUC_{target}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out.name}")


def plot_f1_acc(best_df: pd.DataFrame, target: str):
    """2-panel bar chart: F1-macro + Balanced Accuracy — top 5 per family."""
    sub = best_df[best_df["target"] == target].copy()
    sub = sub.sort_values(["family", "auc_roc"], ascending=[True, False])
    sub = sub.groupby("family").head(5).reset_index(drop=True)

    labels = [f"{r.model}\n({r.exp})" for _, r in sub.iterrows()]
    x = np.arange(len(labels))

    fig, axes = plt.subplots(2, 1, figsize=(max(16, len(labels) * 0.85), 10),
                             sharex=True)
    fig.suptitle(f"F1-Score et Balanced Accuracy — {TARGET_FULL[target]}",
                 fontsize=14, fontweight="bold", y=0.99)

    panels = [
        ("f1_macro",         "F1-Score Macro ↑",   (0.40, 0.85)),
        ("balanced_accuracy","Balanced Accuracy ↑", (0.40, 0.85)),
    ]

    for ax, (metric, ylabel, ylim) in zip(axes, panels):
        vals   = sub[metric].values
        colors = [_family_color(f) for f in sub["family"]]
        bars   = ax.bar(x, vals, color=colors, edgecolor="white", linewidth=0.5, alpha=0.88)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_ylim(*ylim)
        ax.axhline(0.5, color="red", linewidth=1, linestyle=":", label="aléatoire (0.50)")
        ax.legend(fontsize=8)
        ax.yaxis.grid(True, alpha=0.3)
        ax.set_axisbelow(True)
        for bar, val in zip(bars, vals):
            if not np.isnan(val):
                offset = (ylim[1] - ylim[0]) * 0.015
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + offset,
                        f"{val:.3f}", ha="center", va="bottom", fontsize=7.5,
                        fontweight="bold", rotation=45)

    axes[-1].set_xticks(x)
    axes[-1].set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    patches = [mpatches.Patch(color=c, label=f) for f, c in FAMILY_COLORS.items()]
    fig.legend(handles=patches, loc="upper right", fontsize=9, framealpha=0.8,
               bbox_to_anchor=(0.99, 0.97))
    plt.tight_layout(rect=[0, 0, 0.97, 0.97])
    out = OUT_DIR / f"f1_acc_{target}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out.name}")


def plot_heatmap(best_df: pd.DataFrame, target: str):
    """Heatmap: models × 7 performance metrics, column-normalised."""
    sub = best_df[best_df["target"] == target].copy()
    sub = sub.sort_values("auc_roc", ascending=False)
    sub["label"] = sub.apply(lambda r: f"{r.model} ({r.exp}) [{r.family}]", axis=1)

    metric_cols   = ["mae", "r2", "auc_roc", "balanced_accuracy",
                     "sensitivity", "specificity", "mcc"]
    metric_labels = ["MAE↓", "R²↑", "AUC↑", "BalAcc↑",
                     "Sensitivity↑", "Specificity↑", "MCC↑"]

    mat  = sub[metric_cols].values.astype(float)
    norm = np.zeros_like(mat)
    for j in range(mat.shape[1]):
        col = mat[:, j]
        cmin, cmax = np.nanmin(col), np.nanmax(col)
        norm[:, j] = 0.5 if cmax == cmin else (col - cmin) / (cmax - cmin)
    norm[:, 0] = 1 - norm[:, 0]  # invert MAE

    fig, ax = plt.subplots(figsize=(10, max(8, len(sub) * 0.4)))
    im = ax.imshow(norm, aspect="auto", cmap="RdYlGn", vmin=0, vmax=1)
    ax.set_xticks(range(len(metric_labels)))
    ax.set_xticklabels(metric_labels, rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(len(sub)))
    ax.set_yticklabels(sub["label"], fontsize=8)
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            if not np.isnan(v):
                ax.text(j, i, f"{v:.3f}", ha="center", va="center", fontsize=7)
    plt.colorbar(im, ax=ax, fraction=0.02, pad=0.02,
                 label="Score normalisé (vert = meilleur)")
    ax.set_title(f"Heatmap modèles × métriques — {TARGET_FULL[target]}",
                 fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    out = OUT_DIR / f"heatmap_{target}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out.name}")


def plot_radar(best_df: pd.DataFrame, target: str, top_n: int = 6):
    """Radar chart for top-N models by AUC."""
    sub = best_df[best_df["target"] == target].copy()
    sub = sub.sort_values("auc_roc", ascending=False).head(top_n).reset_index(drop=True)

    cols       = ["mae", "r2", "auc_roc", "balanced_accuracy", "mcc"]
    cat_labels = ["MAE↓", "R²↑", "AUC↑", "Bal.Acc↑", "MCC↑"]
    N = len(cols)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={"polar": True})
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(cat_labels, fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0.25", "0.5", "0.75", "1.0"], fontsize=7, color="grey")

    cmap = plt.cm.get_cmap("tab10", top_n)
    for i, row in sub.iterrows():
        vals = []
        for col in cols:
            v = row[col]
            if col == "mae":
                v = 1 - np.clip(v / 3.5, 0, 1)
            elif col == "r2":
                v = np.clip((v + 0.5) / 1.0, 0, 1)
            else:
                v = np.clip(v, 0, 1)
            vals.append(v if not np.isnan(v) else 0)
        vals += vals[:1]
        label = f"{row.model} ({row.exp}) [{row.family}]"
        ax.plot(angles, vals, linewidth=2, label=label, color=cmap(i))
        ax.fill(angles, vals, alpha=0.07, color=cmap(i))

    ax.set_title(f"Radar Top-{top_n} — {TARGET_FULL[target]}",
                 fontsize=13, fontweight="bold", pad=20)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=8)
    plt.tight_layout()
    out = OUT_DIR / f"radar_{target}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out.name}")


def plot_7_criteria_status(best_df: pd.DataFrame, target: str, top_n: int = 15):
    """
    Heatmap pass/fail des 7 critères cliniques pour les top-N modèles.
    Vert = PASS, Orange = BORDERLINE, Rouge = FAIL, Gris = données manquantes.
    Références : Hosmer 2000, Ojala 2010, Liao 2018, Guo 2017,
                 Bland & Altman 1986, Koo 2016, Efron 1994.
    """
    sub = best_df[best_df["target"] == target].copy()
    sub = sub.sort_values("auc_roc", ascending=False).head(top_n).reset_index(drop=True)
    sub["label"] = sub.apply(lambda r: f"{r.model} ({r.exp}) [{r.family}]", axis=1)

    n_models  = len(sub)
    n_crit    = len(CRITERIA)
    col_keys  = [c[0] for c in CRITERIA]
    col_labels = [c[1] for c in CRITERIA]

    # Build colour matrix: 1=pass (green), 0.5=borderline (orange), 0=fail (red), nan=grey
    color_mat = np.full((n_models, n_crit), np.nan)
    val_mat   = np.full((n_models, n_crit), np.nan)

    for i, (_, row) in enumerate(sub.iterrows()):
        for j, (col, _, pass_fn, border_fn) in enumerate(CRITERIA):
            v = row.get(col, np.nan)
            if np.isnan(v):
                continue
            val_mat[i, j] = v
            if pass_fn(v):
                color_mat[i, j] = 1.0
            elif border_fn(v):
                color_mat[i, j] = 0.5
            else:
                color_mat[i, j] = 0.0

    # Custom colormap: red → orange → green  (with grey for NaN)
    from matplotlib.colors import LinearSegmentedColormap
    cmap_rg = LinearSegmentedColormap.from_list(
        "rg3", ["#d62728", "#ff7f0e", "#2ca02c"], N=256)
    cmap_rg.set_bad(color="#cccccc")

    fig, ax = plt.subplots(figsize=(max(10, n_crit * 1.5), max(8, n_models * 0.55)))

    masked = np.ma.masked_invalid(color_mat)
    im = ax.imshow(masked, aspect="auto", cmap=cmap_rg, vmin=0, vmax=1)

    # Annotations : valeur réelle
    for i in range(n_models):
        for j in range(n_crit):
            v  = val_mat[i, j]
            cv = color_mat[i, j]
            if np.isnan(v):
                ax.text(j, i, "N/A", ha="center", va="center", fontsize=7, color="#888888")
            else:
                col_key = col_keys[j]
                if col_key == "p_val":
                    txt = f"{v:.3f}" if v >= 0.001 else "<0.001"
                elif col_key in ("cv_r2", "loa_width"):
                    txt = f"{v:.1f}"
                else:
                    txt = f"{v:.3f}"
                fc = "white" if cv in (0.0, 1.0) else "black"
                ax.text(j, i, txt, ha="center", va="center", fontsize=7.5,
                        fontweight="bold", color=fc)

    ax.set_xticks(range(n_crit))
    ax.set_xticklabels(col_labels, fontsize=9)
    ax.set_yticks(range(n_models))
    ax.set_yticklabels(sub["label"], fontsize=8)

    # Add references as secondary x-axis
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    ax2.set_xticks(range(n_crit))
    ax2.set_xticklabels(CRITERIA_REFS, fontsize=6.5, rotation=15, ha="left")
    ax2.tick_params(length=0)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#2ca02c", label="PASS"),
        Patch(facecolor="#ff7f0e", label="BORDERLINE"),
        Patch(facecolor="#d62728", label="FAIL"),
        Patch(facecolor="#cccccc", label="N/A"),
    ]
    ax.legend(handles=legend_elements, loc="lower right",
              bbox_to_anchor=(1.0, -0.15), ncol=4, fontsize=8, framealpha=0.8)

    ax.set_title(f"Statut des 7 critères cliniques — {TARGET_FULL[target]}",
                 fontsize=12, fontweight="bold", pad=30)

    # Score total (nb de pass) per model
    pass_counts = np.sum(color_mat == 1.0, axis=1)
    for i, cnt in enumerate(pass_counts):
        ax.text(n_crit + 0.1, i, f"{int(cnt)}/7", va="center", fontsize=8,
                fontweight="bold", color="navy")
    ax.set_xlim(-0.5, n_crit + 0.4)

    plt.tight_layout()
    out = OUT_DIR / f"7_criteria_{target}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out.name}")


def plot_family_comparison(best_df: pd.DataFrame, target: str):
    """Strip plot: AUC distribution per family."""
    sub = best_df[best_df["target"] == target].copy()

    families = ["ML-feat15", "ML-feat15_smote", "ML-feat78", "ML-feat78_smote", "DL", "TL"]
    families = [f for f in families if f in sub["family"].values]

    fig, ax = plt.subplots(figsize=(12, 5))
    for i, fam in enumerate(families):
        vals = sub[sub["family"] == fam]["auc_roc"].dropna().values
        if len(vals) == 0:
            continue
        xj = np.random.normal(i, 0.06, size=len(vals))
        ax.scatter(xj, vals, color=_family_color(fam), alpha=0.55, s=30, zorder=3)
        ax.plot([i - 0.3, i + 0.3], [np.mean(vals)] * 2,
                color=_family_color(fam), linewidth=3, zorder=4)

    ax.set_xticks(range(len(families)))
    ax.set_xticklabels([f.replace("ML-", "") for f in families], fontsize=9)
    ax.axhline(0.5, color="red",   linewidth=1, linestyle=":", label="aléatoire (AUC=0.5)")
    ax.axhline(0.7, color="green", linewidth=1, linestyle="--", label="seuil acceptable (0.70)")
    ax.set_ylabel("AUC-ROC", fontsize=10)
    ax.set_title(f"Distribution AUC par famille — {TARGET_FULL[target]}",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.yaxis.grid(True, alpha=0.3)
    ax.set_axisbelow(True)
    plt.tight_layout()
    out = OUT_DIR / f"family_auc_{target}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {out.name}")


# ────────────────────────── recommendation ────────────────────────────────

def generate_recommendation(best_df: pd.DataFrame) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append("  RECOMMANDATION DE DÉPLOIEMENT — NeuroCap App")
    lines.append("  Score composite : AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10")
    lines.append("  [Fawcett 2006; Chicco & Jurman 2020; Fairclough 2009; Youden 1950]")
    lines.append("=" * 80)

    best_by_target = {}

    for target in TARGETS:
        # Trier par composite (critère de sélection principal)
        sub = best_df[best_df["target"] == target].copy()
        sub = sub.sort_values("composite", ascending=False, na_position="last")

        lines.append(f"\n{'─'*80}")
        lines.append(f"  CIBLE : {TARGET_FULL[target].upper()}")
        lines.append(f"{'─'*80}")
        lines.append(f"\n  Top-10 modèles par score composite :\n")

        top10 = sub.head(10)
        lines.append(f"  {'Rg':<3} {'Famille':<18} {'Modèle':<22} {'Exp':<4}"
                     f"{'Comp':>6} {'AUC':>6} {'Sens':>6} {'MCC':>6} {'Spec':>6} {'R²':>7} {'MAE':>6}")
        lines.append(f"  {'-'*90}")
        for rank, (_, row) in enumerate(top10.iterrows(), 1):
            comp_str = f"{row.composite:.3f}" if not np.isnan(row.composite) else " N/A"
            lines.append(
                f"  {rank:<3} {str(row.family):<18} {str(row.model)[:21]:<22} {str(row.exp):<4}"
                f"{comp_str:>6} {row.auc_roc:>6.3f} {row.sensitivity:>6.3f}"
                f"{row.mcc:>6.3f} {row.specificity:>6.3f} {row.r2:>7.3f} {row.mae:>6.3f}"
            )

        best = sub.iloc[0]
        best_by_target[target] = best
        lines.append(f"\n  ★ MEILLEUR MODÈLE (composite) : {best.model} [{best.family}] — exp {best.exp}")
        lines.append(f"    Score composite : {best.composite:.4f}")
        lines.append(f"    AUC             : {best.auc_roc:.4f}")
        lines.append(f"    Sensitivity     : {best.sensitivity:.4f}")
        lines.append(f"    MCC             : {best.mcc:.4f}")
        lines.append(f"    Specificity     : {best.specificity:.4f}")
        lines.append(f"    R²              : {best.r2:.4f}")
        lines.append(f"    MAE             : {best.mae:.4f} pts (sur 0–10)")
        lines.append(f"    Balanced Acc    : {best.balanced_accuracy:.4f}")

        lines.append(f"\n  Critères cliniques (7 métriques) :")
        p_val   = best.get("p_val",    np.nan) if hasattr(best, "get") else getattr(best, "p_val",   np.nan)
        cv_r2   = best.get("cv_r2",    np.nan) if hasattr(best, "get") else getattr(best, "cv_r2",   np.nan)
        ece     = best.get("ece",      np.nan) if hasattr(best, "get") else getattr(best, "ece",     np.nan)
        loa_w   = best.get("loa_width",np.nan) if hasattr(best, "get") else getattr(best, "loa_width",np.nan)
        icc_v   = best.get("icc_val",  np.nan) if hasattr(best, "get") else getattr(best, "icc_val", np.nan)
        ci_w    = best.get("ci_width", np.nan) if hasattr(best, "get") else getattr(best, "ci_width",np.nan)
        crit_data = [
            ("AUC ≥ 0.65",  best.auc_roc, "✅" if best.auc_roc >= 0.65 else ("⚠️" if best.auc_roc >= 0.55 else "❌")),
            ("p < 0.001",   p_val,         "✅" if not np.isnan(p_val) and p_val < 0.001 else ("⚠️" if not np.isnan(p_val) and p_val < 0.05 else "❌" if not np.isnan(p_val) else "N/A")),
            ("CV-R² ≤ 5%",  cv_r2,        "✅" if not np.isnan(cv_r2) and cv_r2 <= 5.0 else ("⚠️" if not np.isnan(cv_r2) and cv_r2 <= 20.0 else "❌" if not np.isnan(cv_r2) else "N/A")),
            ("ECE ≤ 0.15",  ece,          "✅" if not np.isnan(ece) and ece <= 0.05 else ("⚠️" if not np.isnan(ece) and ece <= 0.15 else "❌" if not np.isnan(ece) else "N/A")),
            ("LoA ≤ 8pts",  loa_w,        "✅" if not np.isnan(loa_w) and loa_w <= 4.0 else ("⚠️" if not np.isnan(loa_w) and loa_w <= 8.0 else "❌" if not np.isnan(loa_w) else "N/A")),
            ("ICC ≥ 0.75",  icc_v,        "✅" if not np.isnan(icc_v) and icc_v >= 0.90 else ("⚠️" if not np.isnan(icc_v) and icc_v >= 0.75 else "❌" if not np.isnan(icc_v) else "N/A")),
            ("CI-AUC ≤ 0.10",ci_w,        "✅" if not np.isnan(ci_w) and ci_w <= 0.05 else ("⚠️" if not np.isnan(ci_w) and ci_w <= 0.10 else "❌" if not np.isnan(ci_w) else "N/A")),
        ]
        for name, val, status in crit_data:
            val_str = f"{val:.4f}" if isinstance(val, float) and not np.isnan(val) else "N/A"
            lines.append(f"    {status}  {name:<14} : {val_str}")

        if target == "stress":
            lines.append("\n  ⚠  ATTENTION — Modèle de stress :")
            lines.append("    L'électrode Fp2 capte la concentration (ρ≈0.47), pas le stress")
            lines.append("    amygdalien (ρ≈0.11). R²<0 et ICC≈0 → signal insuffisant en prod.")
            lines.append("    → Afficher un WARNING dans l'interface utilisateur.")

    # ── Résumé final dynamique ──────────────────────────────────────────────
    lines.append(f"\n{'='*80}")
    lines.append("  RÉSUMÉ FINAL — 2 MODÈLES RETENUS POUR NeuroCap")
    lines.append(f"{'='*80}")

    bc = best_by_target.get("conc")
    bs = best_by_target.get("stress")

    if bc is not None:
        lines.append(f"""
  ✅ MODÈLE 1 — CONCENTRATION : {bc.model} [{bc.family}] (exp {bc.exp})
     Score composite = {bc.composite:.4f}
     AUC={bc.auc_roc:.3f}  Sensitivity={bc.sensitivity:.3f}  MCC={bc.mcc:.3f}  Specificity={bc.specificity:.3f}
     R²={bc.r2:.3f}  MAE={bc.mae:.3f} pts
     → RECOMMANDÉ EN PRODUCTION
     → Usage : détection binaire Low/High concentration (seuil=5/10)
     → Justification composite : AUC(×0.40) + Sensitivity(×0.30) + MCC(×0.20) + Specificity(×0.10)
       [Fawcett 2006; Fairclough 2009; Chicco & Jurman 2020; Youden 1950]""")

    if bs is not None:
        auc_ok = bs.auc_roc >= 0.65
        r2_ok  = bs.r2 >= 0.0
        deploy = "CONDITIONNEL avec WARNING" if not (auc_ok and r2_ok) else "RECOMMANDÉ"
        lines.append(f"""
  ⚠️  MODÈLE 2 — STRESS : {bs.model} [{bs.family}] (exp {bs.exp})
     Score composite = {bs.composite:.4f}
     AUC={bs.auc_roc:.3f}  Sensitivity={bs.sensitivity:.3f}  MCC={bs.mcc:.3f}  Specificity={bs.specificity:.3f}
     R²={bs.r2:.3f}  MAE={bs.mae:.3f} pts
     → DÉPLOIEMENT {deploy}
     → L'électrode Fp2 ne capte pas le stress amygdalien (ρ≈0.11)
     → Afficher dans l'UI : \"Indicateur orientatif — non validé cliniquement\"
     → Alternative recommandée : ratio alpha/bêta frontal (proxy physiologique)""")

    lines.append(f"""
  BASELINE ML (référence) :
     Concentration : feat78_smote SVR/XGBoost — AUC≈0.65-0.67, Composite≈0.57
     Stress        : tous modèles ML — AUC≤0.52, Composite≤0.49 → inutilisable

  CONCLUSION : L'architecture DL (EEGNet) domine pour la concentration.
  Les modèles TL sont compétitifs mais légèrement inférieurs en composite.
  Pour le stress, aucun modèle n'atteint les seuils cliniques requis.
""")
    return "\n".join(lines)


# ───────────────────────── FINAL DECISION DASHBOARD ──────────────────────

_GLOB_DECISION = [
    ("auc_roc",           "AUC ROC",          0.65, 0.55),
    ("sensitivity",       "Sensitivity",       0.50, 0.40),
    ("specificity",       "Specificity",       0.50, 0.40),
    ("mcc",               "MCC",               0.20, 0.10),
    ("balanced_accuracy", "Balanced Accuracy", 0.65, 0.55),
]


def plot_final_decision_dashboard(best_df: pd.DataFrame, target: str, top_n: int = 15):
    """
    Dashboard de décision finale (globale ML + DL + TL).
    Top-N modèles triés par AUC → Sensitivity → MCC.
    Produit 1 image : barplots par métrique + tableau pass/fail + podium top-3.
    """
    sub = best_df[best_df["target"] == target].copy()
    for col in ("sensitivity", "specificity", "mcc", "balanced_accuracy"):
        if col not in sub.columns:
            sub[col] = np.nan
    sub = sub.sort_values(["auc_roc", "sensitivity", "mcc"],
                          ascending=[False, False, False]).head(top_n).reset_index(drop=True)
    if sub.empty:
        print(f"  [SKIP] final_decision_dashboard_{target}.png — données manquantes")
        return

    n       = len(sub)
    labels  = [f"{r.model}\n[{r.family}]" for _, r in sub.iterrows()]
    fcolors = [_family_color(r.family) for _, r in sub.iterrows()]

    def _bc(v, g, b):
        if np.isnan(v): return '#CCCCCC'
        if v >= g:      return '#27AE60'
        if v >= b:      return '#F39C12'
        return '#E74C3C'

    fig = plt.figure(figsize=(28, 16))
    gs  = fig.add_gridspec(3, 5, height_ratios=[1.4, 1.4, 1.0],
                           hspace=0.60, wspace=0.38,
                           top=0.90, bottom=0.04, left=0.04, right=0.97)
    fig.suptitle(
        f'DASHBOARD DÉCISION FINALE — Tous modèles (ML + DL + TL)  |  {TARGET_FULL[target].upper()}\n'
        f'Top-{top_n} par AUC ROC → Sensitivity → MCC  |  '
        f'Seuils : AUC≥0.65  Sens≥0.50  Spec≥0.50  MCC≥0.20  BalAcc≥0.65',
        fontsize=13, fontweight='bold'
    )

    # ── Lignes 1-2 : barplots des 5 métriques (splitté en 2 lignes × 5 cols) ──
    for ci, (metric, label, good_t, border_t) in enumerate(_GLOB_DECISION):
        row_gs = 0 if ci < 5 else 1
        col_gs = ci if ci < 5 else ci - 5
        ax   = fig.add_subplot(gs[row_gs, col_gs])
        vals = [float(sub.loc[i, metric]) if not np.isnan(sub.loc[i, metric]) else 0.
                for i in range(n)]
        cols = [_bc(v, good_t, border_t) for v in vals]
        x    = np.arange(n)
        bars = ax.bar(x, vals, 0.7, color=cols, alpha=0.88, edgecolor='white')
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                    f'{v:.2f}', ha='center', va='bottom', fontsize=5.5, fontweight='bold')
        ax.axhline(good_t,   color='#27AE60', lw=1.8, ls='--', alpha=0.85,
                   label=f'Seuil bon ({good_t})')
        ax.axhline(border_t, color='#F39C12', lw=1.2, ls=':',  alpha=0.70)
        ax.set_xticks(x)
        ax.set_xticklabels([lb.split('\n')[0][:9] for lb in labels],
                           rotation=50, ha='right', fontsize=5.5)
        ax.set_ylim(0, 1.18)
        ax.set_title(f'{label} ↑', fontsize=9, fontweight='bold')
        ax.grid(axis='y', alpha=0.25)

    # Légende
    legend_patches = [
        mpatches.Patch(color='#27AE60', label='✅ Bon'),
        mpatches.Patch(color='#F39C12', label='⚠️ Borderline'),
        mpatches.Patch(color='#E74C3C', label='❌ Insuffisant'),
        mpatches.Patch(color=FAMILY_COLORS['ML'], label='ML'),
        mpatches.Patch(color=FAMILY_COLORS['DL'], label='DL'),
        mpatches.Patch(color=FAMILY_COLORS['TL'], label='TL'),
    ]
    fig.legend(handles=legend_patches, loc='upper right',
               bbox_to_anchor=(0.97, 0.94), fontsize=8, ncol=6, framealpha=0.9)

    # ── Ligne 3 : tableau de décision finale ──────────────────────────────
    ax_tbl = fig.add_subplot(gs[2, :])
    ax_tbl.axis('off')
    ax_tbl.set_title(
        'Tableau de décision finale — vert=bon · orange=borderline · rouge=insuffisant   '
        '| ✅ Recommandé = ≥4 métriques au-dessus du seuil bon',
        fontsize=8.5, fontweight='bold', pad=6
    )
    headers = ['#', 'Famille', 'Modèle', 'Exp', 'AUC ROC',
               'Sensitivity', 'Specificity', 'MCC', 'Bal.Acc', 'DÉCISION']
    tbl_rows, tbl_colors = [], []
    for rank, (idx, row) in enumerate(sub.iterrows(), 1):
        row_data = [str(rank), row.family, row.model[:22], str(row.exp)]
        row_col  = ['#ECF0F1', '#ECF0F1', '#ECF0F1', '#ECF0F1']
        n_good   = 0
        for metric, _, good_t, border_t in _GLOB_DECISION:
            v = row[metric] if not np.isnan(row[metric]) else 0.
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
        if rank == 1:
            d = '🥇 ' + d
        elif rank == 2:
            d = '🥈 ' + d
        elif rank == 3:
            d = '🥉 ' + d
        row_data.append(d); row_col.append(dc)
        tbl_rows.append(row_data); tbl_colors.append(row_col)

    tbl = ax_tbl.table(cellText=tbl_rows, colLabels=headers,
                       cellLoc='center', loc='center', bbox=[0, 0, 1, 1],
                       cellColours=tbl_colors)
    tbl.auto_set_font_size(False); tbl.set_fontsize(7.5)
    for col in range(len(headers)):
        tbl[(0, col)].set_facecolor('#1A3A4A')
        tbl[(0, col)].set_text_props(color='white', fontweight='bold')

    out = OUT_DIR / f'final_decision_dashboard_{target}.png'
    plt.savefig(str(out), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved: final_decision_dashboard_{target}.png")


# ─── Couleurs composantes (identiques DL + TL + baseline) ───────────────────
_COMP_COLORS = {
    'auc_w':  '#2980B9',
    'sens_w': '#27AE60',
    'mcc_w':  '#F39C12',
    'spec_w': '#8E44AD',
}


def plot_composite_breakdown_global(best_df: pd.DataFrame, target: str, top_n: int = 20):
    """
    Figure 2 panneaux — tous modèles (ML + DL + TL) :
      Haut : barres empilées des 4 contributions pondérées au score composite
      Bas  : métriques brutes (AUC, Sensitivity, MCC, Specificity)
    Permet d'argumenter le choix du meilleur modèle toutes familles [Ferri et al. 2009].
    """
    sub = best_df[best_df["target"] == target].copy()
    for col in ("auc_roc", "sensitivity", "specificity", "mcc"):
        if col not in sub.columns:
            sub[col] = np.nan
    sub = sub.dropna(subset=["composite"]).sort_values("composite", ascending=False).head(top_n).reset_index(drop=True)
    if sub.empty:
        return

    sub["auc_w"]  = (0.40 * sub["auc_roc"].clip(lower=0)).fillna(0)
    sub["sens_w"] = (0.30 * sub["sensitivity"].clip(lower=0)).fillna(0)
    sub["mcc_w"]  = (0.20 * sub["mcc"].clip(lower=0)).fillna(0)
    sub["spec_w"] = (0.10 * sub["specificity"].clip(lower=0)).fillna(0)

    n = len(sub)
    x = np.arange(n)
    labels = [f"{r.model[:16]}\n[{r.family}]" for _, r in sub.iterrows()]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(18, n * 0.9), 14))
    fig.suptitle(
        f"Décomposition du Score Composite — Tous modèles (ML + DL + TL)  |  {TARGET_FULL[target].upper()}\n"
        f"Score = AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10  |  Top-{top_n}\n"
        f"[Fawcett 2006; Chicco & Jurman 2020; Fairclough 2009; Youden 1950; Lotte et al. 2018]",
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
    for i, (comp, fam) in enumerate(zip(sub['composite'], sub['family'])):
        ax1.text(i, comp + 0.008, f'{comp:.3f}', ha='center', va='bottom',
                 fontsize=6.5, fontweight='bold',
                 color=FAMILY_COLORS.get(fam.split('-')[0], '#333333'))
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
    ax1.set_ylabel('Score composite (contributions pondérées)', fontsize=9)
    ax1.set_title('Contributions pondérées au score composite — tous modèles (tri décroissant)', fontsize=10)
    ax1.axhline(0.50, color='#27AE60', lw=1.5, ls='--', alpha=0.7, label='Seuil bon (0.50)')
    ax1.axhline(0.35, color='#F39C12', lw=1.2, ls=':',  alpha=0.6, label='Seuil borderline (0.35)')
    ax1.set_ylim(0, min(1.0, sub['composite'].max() * 1.22))
    ax1.legend(loc='upper right', fontsize=7.5, framealpha=0.85)
    ax1.grid(axis='y', alpha=0.25)
    # Indicateurs familles
    for i, fam in enumerate(sub['family']):
        fc = FAMILY_COLORS.get(fam.split('-')[0], '#999')
        ax1.add_patch(mpatches.Rectangle((i - 0.4, 0), 0.8, 0.012, color=fc, alpha=0.6, zorder=5))

    # Panneau 2 : métriques brutes
    w = 0.20
    for j, (col, lbl, color) in enumerate([
        ('auc_roc',     'AUC-ROC',     _COMP_COLORS['auc_w']),
        ('sensitivity', 'Sensitivity', _COMP_COLORS['sens_w']),
        ('mcc',         'MCC',         _COMP_COLORS['mcc_w']),
        ('specificity', 'Specificity', _COMP_COLORS['spec_w']),
    ]):
        vals = sub[col].clip(lower=0).fillna(0).values
        offset = (j - 1.5) * w
        bars = ax2.bar(x + offset, vals, w, label=lbl, color=color, alpha=0.82, edgecolor='white')
        for bar, v in zip(bars, vals):
            if v > 0.01:
                ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                         f'{v:.2f}', ha='center', va='bottom', fontsize=5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=45, ha='right', fontsize=7)
    ax2.set_ylabel('Valeur brute de la métrique', fontsize=9)
    ax2.set_title('Métriques brutes individuelles (AUC, Sensitivity, MCC, Specificity)', fontsize=10)
    ax2.axhline(0.50, color='gray', lw=1.0, ls='--', alpha=0.5)
    ax2.set_ylim(0, 1.15)
    ax2.legend(loc='upper right', fontsize=8, framealpha=0.85)
    ax2.grid(axis='y', alpha=0.25)
    family_patches = [mpatches.Patch(color=c, label=f) for f, c in FAMILY_COLORS.items()]
    ax2.legend(handles=ax2.get_legend_handles_labels()[0][:4]
               + family_patches, fontsize=7.5, framealpha=0.85, ncol=2)

    plt.tight_layout()
    out = OUT_DIR / f"composite_breakdown_{target}.png"
    plt.savefig(out, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: composite_breakdown_{target}.png")


def save_composite_outputs_global(best_df: pd.DataFrame):
    """
    Sauvegarde composite_scores.json + composite_summary.txt pour tous modèles (ML+DL+TL).
    Inclut les 4 métriques constitutives et les contributions pondérées.
    """
    ranking_json_all = {}

    for target in TARGETS:
        sub = best_df[best_df["target"] == target].copy()
        sub = sub.dropna(subset=["composite"]).sort_values("composite", ascending=False).reset_index(drop=True)

        ranking = []
        for rank, (_, row) in enumerate(sub.iterrows(), 1):
            auc  = float(row.get("auc_roc",     0) or 0)
            sens = float(row.get("sensitivity", 0) or 0)
            mcc  = float(row.get("mcc",         0) or 0)
            spec = float(row.get("specificity", 0) or 0)
            comp = float(row.get("composite",   0) or 0)
            ranking.append({
                "rank":    rank,
                "family":  row.get("family", ""),
                "model":   row.get("model",  ""),
                "exp":     row.get("exp",    ""),
                "composite": round(comp, 4),
                "metrics": {
                    "AUC":          round(auc,  4),
                    "Sensitivity":  round(sens, 4),
                    "MCC":          round(mcc,  4),
                    "Specificity":  round(spec, 4),
                    "Balanced_Acc": round(float(row.get("balanced_accuracy", 0) or 0), 4),
                    "MAE":          round(float(row.get("mae", 0) or 0), 4),
                    "R2":           round(float(row.get("r2",  0) or 0), 4),
                },
                "weighted_contributions": {
                    "AUC_x040":         round(0.40 * max(auc,  0), 4),
                    "Sensitivity_x030": round(0.30 * max(sens, 0), 4),
                    "MCC_x020":         round(0.20 * max(mcc,  0), 4),
                    "Specificity_x010": round(0.10 * max(spec, 0), 4),
                },
            })
        ranking_json_all[target] = ranking

    json_path = OUT_DIR / "composite_scores_all.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "composite_formula": "AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10",
            "references": [
                "Fawcett (2006) Pattern Recognit. Lett. 27(8):861-874",
                "Chicco & Jurman (2020) BMC Genomics 21(1):6",
                "Fairclough (2009) Interacting with Computers 21(1-2):133-145",
                "Youden (1950) Cancer 3(1):32-35",
                "Lotte et al. (2018) J. Neural Eng. 15(3):031005",
                "Ferri et al. (2009) Pattern Recognit. Lett. 30(1):27-38",
            ],
            "families": ["ML (feat15, feat15_smote, feat78, feat78_smote)", "DL (19 architectures)", "TL (3 stratégies)"],
            "results": ranking_json_all,
        }, f, indent=2, ensure_ascii=False)
    print(f"  Saved: composite_scores_all.json")

    # TXT
    lines = []
    lines.append("=" * 100)
    lines.append("NeuroCap — Score Composite GLOBAL (ML + DL + TL)")
    lines.append("Formule : AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10")
    lines.append("Justification :")
    lines.append("  AUC  (w=0.40) : threshold-free, recommandée EEG/BCI [Fawcett 2006; Lotte et al. 2018]")
    lines.append("  Sens (w=0.30) : FN coûteux en monitoring cognitif [Fairclough 2009; Brodersen et al. 2010]")
    lines.append("  MCC  (w=0.20) : utilise les 4 cellules de la matrice, robuste à l'imbalance [Chicco & Jurman 2020]")
    lines.append("  Spec (w=0.10) : FP moins coûteux que FN en détection cognitive [Youden 1950]")
    lines.append("  Choix multi-critères : Ferri et al. (2009) Pattern Recognit. Lett. — no single metric suffices")
    lines.append("=" * 100)

    for target in TARGETS:
        ranking = ranking_json_all.get(target, [])
        lines.append(f"\n{'─'*100}")
        lines.append(f"  CIBLE : {target.upper()}")
        lines.append(f"{'─'*100}")
        lines.append(f"\n  {'Rg':<4} {'Famille':<22} {'Modèle':<25} {'Exp':<5} {'Score':>7} │ "
                     f"{'AUC':>7} {'Sens':>7} {'MCC':>7} {'Spec':>7} │ "
                     f"{'AUC×0.4':>8} {'S×0.3':>7} {'M×0.2':>7} {'Sp×0.1':>7}")
        lines.append("  " + "─" * 97)
        for item in ranking[:20]:
            m  = item["metrics"]
            wc = item["weighted_contributions"]
            lines.append(
                f"  {item['rank']:<4} {item['family']:<22} {item['model'][:24]:<25} {item['exp']:<5} "
                f"{item['composite']:>7.4f} │ "
                f"{m['AUC']:>7.4f} {m['Sensitivity']:>7.4f} {m['MCC']:>7.4f} {m['Specificity']:>7.4f} │ "
                f"{wc['AUC_x040']:>8.4f} {wc['Sensitivity_x030']:>7.4f} "
                f"{wc['MCC_x020']:>7.4f} {wc['Specificity_x010']:>7.4f}"
            )
        if ranking:
            best = ranking[0]
            lines.append(f"\n  ★ MEILLEUR MODÈLE : [{best['family']}] {best['model']} — Exp. {best['exp']}")
            lines.append(f"    Score composite = {best['composite']:.4f}")
            for k, v in best["metrics"].items():
                lines.append(f"    {k:<15}: {v:.4f}")

    lines.append("\n" + "=" * 100)
    txt_path = OUT_DIR / "composite_summary_all.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("  Saved: composite_summary_all.txt")


# ─────────────────────────────── main ─────────────────────────────────────

def main():
    print("\n Chargement des résultats...")
    df = build_dataframe()
    print(f"   {len(df)} lignes chargées (ML + DL + TL, tous exps)")

    best_df = best_per_model(df)
    print(f"   {len(best_df)} modèles uniques (meilleur exp par modèle)")

    df.to_csv(OUT_DIR / "comparison_all_raw.csv", index=False)
    best_df.to_csv(OUT_DIR / "comparison_all_best.csv", index=False)
    print(f"   Saved: comparison_all_raw.csv, comparison_all_best.csv")

    for target in TARGETS:
        print(f"\n Target : {TARGET_FULL[target]}")
        plot_grouped_bars(best_df, target)
        plot_f1_acc(best_df, target)
        plot_heatmap(best_df, target)
        plot_radar(best_df, target)
        plot_7_criteria_status(best_df, target)
        plot_family_comparison(best_df, target)
        plot_final_decision_dashboard(best_df, target)
        # ── NOUVEAU : décomposition composite ─────────────────────────────
        plot_composite_breakdown_global(best_df, target)

    # ── NOUVEAU : exports JSON + TXT composite ─────────────────────────────
    save_composite_outputs_global(best_df)

    reco = generate_recommendation(best_df)
    print("\n" + reco)
    (OUT_DIR / "recommendation.txt").write_text(reco, encoding="utf-8")
    print(f"\n  Saved: recommendation.txt")
    print(f"\n Tous les outputs dans : {OUT_DIR}\n")


if __name__ == "__main__":
    main()
