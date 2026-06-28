"""
visualize_regression.py
=======================
EMPLACEMENT : src/data/visualize_regression.py

OBJECTIF :
  Generer toutes les visualisations du pipeline de regression.
  Chaque etape du pipeline a son propre dossier de rapports.

PREREQUIS :
  Avoir execute pipeline_regression.py au moins une fois.
  data/Regression/ doit contenir preprocessed/, augmented/, features/

RAPPORTS GENERES :
  reports/Regression/
  ├── 01_preprocessing/
  │   ├── 01_signal_amplitude.png      Distribution amplitude conc vs stress
  │   ├── 02_score_distributions.png   Histogrammes y_conc et y_stress
  │   ├── 03_sample_epochs.png         Exemples d'epochs (4 niveaux / 4 taches)
  │   └── 04_subjects_overview.png     Epochs par sujet pour les deux datasets
  │
  ├── 02_split/
  │   ├── 01_split_sizes.png           Train/Val/Test N epochs et N sujets
  │   ├── 02_score_in_splits.png       Distribution des scores train vs val vs test
  │   └── 03_subjects_per_split.png    Quels sujets dans quel split
  │
  ├── 03_augmentation/
  │   ├── 01_dataset_growth.png        Taille du dataset par experience A/B/C/D/FULL
  │   ├── 02_score_propagation.png     Score y identique apres augmentation (sanity check)
  │   └── 03_signal_examples.png       Signal original vs augmente (bruit/DWT/warp)
  │
  └── 04_features/
      ├── 01_feature_count.png         feat15 vs feat78 (comparaison nombre features)
      ├── 02_top_correlations.png      Top 20 features les plus correlees au score
      ├── 03_feature_distributions.png Violins des 12 features les plus importantes
      └── 04_feat15_vs_feat78.png      Correlation feat15 vs feat78 (R² visuel)

UTILISATION :
  python src/data/visualize_regression.py
"""

import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
import seaborn as sns
from pathlib import Path
from scipy.stats import spearmanr

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT  = Path(__file__).resolve().parents[2]
PREP     = PROJECT / "data" / "Regression" / "preprocessed"
AUG      = PROJECT / "data" / "Regression" / "augmented"
FEAT     = PROJECT / "Features"
SCORE_C  = PROJECT / "data" / "Scoring" / "scored_concentration.csv"
SCORE_S  = PROJECT / "data" / "Scoring" / "scored_stress.csv"

REP_PREP = PROJECT / "reports" / "Regression" / "01_preprocessing"
REP_SPL  = PROJECT / "reports" / "Regression" / "02_split"
REP_AUG  = PROJECT / "reports" / "Regression" / "03_augmentation"
REP_FEAT = PROJECT / "reports" / "Regression" / "04_features"

for d in [REP_PREP, REP_SPL, REP_AUG, REP_FEAT]:
    d.mkdir(parents=True, exist_ok=True)

# Palette projet
C_CONC   = "#2196F3"
C_STRESS = "#F44336"
C_TRAIN  = "#4CAF50"
C_VAL    = "#FF9800"
C_TEST   = "#9C27B0"
LEVEL_COLORS = ["#90CAF9", "#42A5F5", "#1E88E5", "#0D47A1"]
TASK_COLORS  = ["#A5D6A7", "#FFA726", "#EF5350", "#AB47BC"]
EXP_COLORS   = ["#E3F2FD", "#90CAF9", "#42A5F5", "#1E88E5", "#0D47A1"]

EXPERIMENTS  = ['A', 'B', 'C', 'D', 'FULL']


def save(fig, folder: Path, name: str) -> None:
    path = folder / name
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"    -> {path.relative_to(PROJECT)}")


def npy_exists(*paths) -> bool:
    return all(Path(p).exists() for p in paths)


# ============================================================================
# ETAPE 1 — PREPROCESSING
# ============================================================================

def viz_preprocessing():
    print("\n[01_preprocessing]")

    X_conc    = np.load(PREP / "X_conc.npy")
    y_conc    = np.load(PREP / "y_conc.npy")
    subs_conc = np.load(PREP / "subjects_conc.npy")
    X_str     = np.load(PREP / "X_stress.npy")
    y_str     = np.load(PREP / "y_stress.npy")
    subs_str  = np.load(PREP / "subjects_stress.npy")

    # ── 01 Distribution amplitude ─────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Preprocessing — Distribution d'amplitude (z-score)", fontsize=13, fontweight='bold')

    for ax, X, label, color in [
        (axes[0], X_conc, "Concentration (OpenBCI)", C_CONC),
        (axes[1], X_str,  "Stress (EMOTIV)",         C_STRESS),
    ]:
        flat = X.flatten()
        ax.hist(flat, bins=80, color=color, alpha=0.75, edgecolor='none')
        ax.axvline(flat.mean(), color='navy', linestyle='--', linewidth=1.5,
                   label=f"μ = {flat.mean():.3f}")
        ax.axvline(flat.std(),  color='gray', linestyle=':',  linewidth=1.2,
                   label=f"σ = {flat.std():.3f}")
        ax.set_xlabel("Amplitude (z-score)")
        ax.set_ylabel("Fréquence")
        ax.set_title(label)
        ax.set_xlim(-6, 6)
        ax.legend(fontsize=9)
        ax.text(0.97, 0.97, f"N epochs = {len(X)}\n{X.shape[1]} samples/epoch",
                transform=ax.transAxes, ha='right', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    plt.tight_layout()
    save(fig, REP_PREP, "01_signal_amplitude.png")

    # ── 02 Distribution des scores ────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Preprocessing — Distribution des scores de regression", fontsize=13, fontweight='bold')

    for ax, y, label, color in [
        (axes[0], y_conc, "conc_score (0–10)", C_CONC),
        (axes[1], y_str,  "stress_score (0–10)", C_STRESS),
    ]:
        ax.hist(y, bins=25, color=color, alpha=0.85, edgecolor='white')
        ax.axvline(y.mean(), color='navy', linestyle='--', linewidth=1.5,
                   label=f"μ = {y.mean():.2f}, σ = {y.std():.2f}")
        ax.set_xlabel(label)
        ax.set_ylabel("Nombre d'epochs")
        ax.set_title(label)
        ax.set_xlim(0, 10)
        ax.legend(fontsize=9)
        q = np.percentile(y, [25, 50, 75])
        ax.text(0.03, 0.97, f"Q25={q[0]:.1f}  Q50={q[1]:.1f}  Q75={q[2]:.1f}",
                transform=ax.transAxes, ha='left', va='top', fontsize=9,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    plt.tight_layout()
    save(fig, REP_PREP, "02_score_distributions.png")

    # ── 03 Exemples d'epochs ──────────────────────────────────────────────
    fig, axes = plt.subplots(2, 4, figsize=(16, 6), sharey=False)
    fig.suptitle("Preprocessing — Exemples d'epochs EEG (signal normalisé z-score)", fontsize=13, fontweight='bold')

    t = np.linspace(0, 4, 1000)

    # Concentration : 4 niveaux
    levels_code = [0, 1, 2, 3]
    level_names = ['Natural\n(0–2.5)', 'Lowlevel\n(2.5–5)', 'Midlevel\n(5–7.5)', 'Highlevel\n(7.5–10)']
    lvl_file = PREP / "levels_conc.npy"
    if lvl_file.exists():
        lvls = np.load(lvl_file)
        for col, (lv, name, color) in enumerate(zip(levels_code, level_names, LEVEL_COLORS)):
            mask = lvls == lv
            if mask.sum() == 0:
                continue
            idx = np.where(mask)[0][0]
            axes[0, col].plot(t, X_conc[idx], color=color, linewidth=0.8)
            axes[0, col].set_title(name, fontsize=9)
            axes[0, col].set_xlabel("Temps (s)")
            if col == 0:
                axes[0, col].set_ylabel("Concentration\n(amplitude z-score)")
            axes[0, col].set_xlim(0, 4)
    else:
        for col in range(4):
            idx = col * (len(X_conc) // 4)
            axes[0, col].plot(t, X_conc[idx], color=LEVEL_COLORS[col], linewidth=0.8)
            axes[0, col].set_xlabel("Temps (s)")

    # Stress : 4 taches
    df_s = pd.read_csv(SCORE_S) if SCORE_S.exists() else None
    tasks_order = ['Relax', 'Arithmetic', 'Mirror_image', 'Stroop']
    task_labels = ['Relax', 'Arithmetic', 'Mirror', 'Stroop']
    for col, (task, lbl, color) in enumerate(zip(tasks_order, task_labels, TASK_COLORS)):
        idx = col * (len(X_str) // 4)
        axes[1, col].plot(t, X_str[idx], color=color, linewidth=0.8)
        axes[1, col].set_title(lbl, fontsize=9)
        axes[1, col].set_xlabel("Temps (s)")
        if col == 0:
            axes[1, col].set_ylabel("Stress\n(amplitude z-score)")
        axes[1, col].set_xlim(0, 4)

    plt.tight_layout()
    save(fig, REP_PREP, "03_sample_epochs.png")

    # ── 04 Epochs par sujet ───────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    fig.suptitle("Preprocessing — Epochs par sujet", fontsize=13, fontweight='bold')

    for ax, subs, y, label, color in [
        (axes[0], subs_conc, y_conc, "Concentration (15 sujets)", C_CONC),
        (axes[1], subs_str,  y_str,  "Stress (40 sujets)",        C_STRESS),
    ]:
        unique_subs = np.unique(subs)
        counts = [np.sum(subs == s) for s in unique_subs]
        means  = [y[subs == s].mean() for s in unique_subs]

        bars = ax.bar(range(len(unique_subs)), counts, color=color, alpha=0.7, edgecolor='white')
        ax2  = ax.twinx()
        ax2.plot(range(len(unique_subs)), means, 'o--', color='navy',
                 linewidth=1.2, markersize=4, label="Score moyen")
        ax2.set_ylabel("Score moyen", color='navy')
        ax2.tick_params(axis='y', labelcolor='navy')
        ax2.set_ylim(0, 10)

        ax.set_xticks(range(len(unique_subs)))
        ax.set_xticklabels([str(s) for s in unique_subs], rotation=45, fontsize=7)
        ax.set_xlabel("Sujet")
        ax.set_ylabel("Nombre d'epochs")
        ax.set_title(label)
        ax2.legend(loc='upper right', fontsize=8)

    plt.tight_layout()
    save(fig, REP_PREP, "04_subjects_overview.png")


# ============================================================================
# ETAPE 2 — SPLIT
# ============================================================================

def viz_split():
    print("\n[02_split]")

    results = {}
    for ds in ['conc', 'stress']:
        d = {}
        for split in ['train_A', 'val', 'test']:
            xp = AUG / ds / f"X_{split}.npy"
            yp = AUG / ds / f"y_{split}.npy"
            if xp.exists():
                d[split] = {'X': np.load(xp), 'y': np.load(yp)}
        results[ds] = d

    # ── 01 Taille des splits ──────────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Split par sujet — Taille des ensembles train/val/test", fontsize=13, fontweight='bold')

    for ax, ds, title in [
        (axes[0], 'conc',   "Concentration"),
        (axes[1], 'stress', "Stress"),
    ]:
        d = results[ds]
        split_names  = []
        split_counts = []
        split_cols   = []
        for split, col, label in [
            ('train_A', C_TRAIN, 'Train (70%)'),
            ('val',     C_VAL,   'Val (15%)'),
            ('test',    C_TEST,  'Test (15%)'),
        ]:
            if split in d:
                split_names.append(label)
                split_counts.append(len(d[split]['y']))
                split_cols.append(col)

        bars = ax.bar(split_names, split_counts, color=split_cols, edgecolor='white', width=0.5)
        total = sum(split_counts)
        for bar, count in zip(bars, split_counts):
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + total * 0.01,
                    f"{count}\n({count/total*100:.0f}%)",
                    ha='center', fontsize=10)
        ax.set_ylabel("Nombre d'epochs")
        ax.set_title(title)
        ax.set_ylim(0, max(split_counts) * 1.2)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save(fig, REP_SPL, "01_split_sizes.png")

    # ── 02 Score dans chaque split ────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Split — Distribution des scores dans train / val / test", fontsize=13, fontweight='bold')

    split_colors = {'train_A': C_TRAIN, 'val': C_VAL, 'test': C_TEST}
    split_labels = {'train_A': 'Train', 'val': 'Val', 'test': 'Test'}

    for ax, ds, title, score_label in [
        (axes[0], 'conc',   "Concentration", "conc_score"),
        (axes[1], 'stress', "Stress",         "stress_score"),
    ]:
        d = results[ds]
        data_list  = []
        tick_labels = []
        colors_list = []
        for split in ['train_A', 'val', 'test']:
            if split in d:
                data_list.append(d[split]['y'])
                tick_labels.append(split_labels[split])
                colors_list.append(split_colors[split])

        bp = ax.boxplot(data_list, patch_artist=True, notch=False,
                        medianprops=dict(color='white', linewidth=2),
                        widths=0.5)
        for patch, color in zip(bp['boxes'], colors_list):
            patch.set_facecolor(color)
            patch.set_alpha(0.8)

        ax.set_xticklabels(tick_labels)
        ax.set_ylabel(score_label)
        ax.set_title(title)
        ax.set_ylim(0, 10)
        ax.grid(axis='y', alpha=0.3)

        # Moyennes
        for i, data in enumerate(data_list):
            ax.text(i + 1, data.mean() + 0.3, f"μ={data.mean():.2f}",
                    ha='center', fontsize=8, color='navy')

    plt.tight_layout()
    save(fig, REP_SPL, "02_score_in_splits.png")

    # ── 03 Histogrammes détaillés ─────────────────────────────────────────
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle("Split — Histogrammes détaillés par split et dataset", fontsize=13, fontweight='bold')

    for row, (ds, ds_label, score_label) in enumerate([
        ('conc',   "Concentration", "conc_score"),
        ('stress', "Stress",        "stress_score"),
    ]):
        d = results[ds]
        for col, (split, split_lbl, color) in enumerate([
            ('train_A', 'Train', C_TRAIN),
            ('val',     'Val',   C_VAL),
            ('test',    'Test',  C_TEST),
        ]):
            ax = axes[row, col]
            if split in d:
                y = d[split]['y']
                ax.hist(y, bins=20, color=color, alpha=0.8, edgecolor='white')
                ax.axvline(y.mean(), color='navy', linestyle='--', linewidth=1.5)
                ax.set_xlim(0, 10)
                ax.set_title(f"{ds_label} — {split_lbl}\n(N={len(y)}, μ={y.mean():.2f})")
                ax.set_xlabel(score_label)
                ax.set_ylabel("N epochs" if col == 0 else "")
            else:
                ax.text(0.5, 0.5, "Données\nmanquantes", ha='center', va='center',
                        transform=ax.transAxes, fontsize=11, color='gray')
                ax.set_title(f"{ds_label} — {split_lbl}")

    plt.tight_layout()
    save(fig, REP_SPL, "03_subjects_per_split.png")


# ============================================================================
# ETAPE 3 — AUGMENTATION
# ============================================================================

def viz_augmentation():
    print("\n[03_augmentation]")

    # ── 01 Croissance du dataset ──────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Augmentation — Volume de données par expérience", fontsize=13, fontweight='bold')

    exp_labels = {'A': 'A\n(original)', 'B': 'B\n(+bruit)', 'C': 'C\n(+DWT)',
                  'D': 'D\n(+warp)', 'FULL': 'FULL\n(A+B+C+D)'}

    for ax, ds, title, color in [
        (axes[0], 'conc',   "Concentration", C_CONC),
        (axes[1], 'stress', "Stress",        C_STRESS),
    ]:
        sizes = []
        labels = []
        for exp in EXPERIMENTS:
            p = AUG / ds / f"X_train_{exp}.npy"
            if p.exists():
                sizes.append(np.load(p).shape[0])
                labels.append(exp_labels[exp])

        bars = ax.bar(labels, sizes, color=color, alpha=0.75, edgecolor='white')
        for bar, n in zip(bars, sizes):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(sizes)*0.01,
                    f"{n}", ha='center', fontsize=10)
        if sizes:
            ax.axhline(sizes[0], color='gray', linestyle='--', linewidth=1,
                       label=f"Baseline A = {sizes[0]}")
        ax.set_ylabel("Nombre d'epochs train")
        ax.set_title(title)
        ax.legend(fontsize=8)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save(fig, REP_AUG, "01_dataset_growth.png")

    # ── 02 Propagation des scores ─────────────────────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Augmentation — Propagation des scores (sanity check)", fontsize=13, fontweight='bold')

    for ax, ds, title, color, score_label in [
        (axes[0], 'conc',   "Concentration", C_CONC,   "conc_score"),
        (axes[1], 'stress', "Stress",        C_STRESS, "stress_score"),
    ]:
        data_list, exp_names = [], []
        for exp in EXPERIMENTS:
            p = AUG / ds / f"y_train_{exp}.npy"
            if p.exists():
                data_list.append(np.load(p))
                exp_names.append(exp)

        bp = ax.boxplot(data_list, patch_artist=True, notch=False,
                        medianprops=dict(color='white', linewidth=2),
                        widths=0.5)
        for patch, c in zip(bp['boxes'], [EXP_COLORS[EXPERIMENTS.index(e)]
                                           for e in exp_names]):
            patch.set_facecolor(c)
            patch.set_alpha(0.9)

        ax.set_xticklabels(exp_names)
        ax.set_ylabel(score_label)
        ax.set_title(f"{title}\n(distribution identique = propagation correcte)")
        ax.set_ylim(0, 10)
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save(fig, REP_AUG, "02_score_propagation.png")

    # ── 03 Exemples de signaux augmentes ─────────────────────────────────
    fig, axes = plt.subplots(2, 5, figsize=(18, 6), sharey=False)
    fig.suptitle("Augmentation — Signal original vs augmenté (exemples)", fontsize=13, fontweight='bold')
    t = np.linspace(0, 4, 1000)

    for row, (ds, title, color) in enumerate([
        ('conc',   "Concentration", C_CONC),
        ('stress', "Stress",        C_STRESS),
    ]):
        ref_epoch = None
        for col, exp in enumerate(EXPERIMENTS):
            p = AUG / ds / f"X_train_{exp}.npy"
            if not p.exists():
                axes[row, col].set_visible(False)
                continue
            X = np.load(p)
            idx = 0
            if ref_epoch is None:
                ref_epoch = X[idx]
            axes[row, col].plot(t, X[idx], color=color, linewidth=0.7, alpha=0.85)
            if ref_epoch is not None and exp != 'A':
                diff = X[idx] - ref_epoch
                axes[row, col].fill_between(t, X[idx], ref_epoch,
                                             alpha=0.25, color='orange',
                                             label=f"Δ moy={np.abs(diff).mean():.3f}")
                axes[row, col].legend(fontsize=7, loc='upper right')
            axes[row, col].set_title(f"Exp {exp}" if row == 0 else "",
                                      fontsize=9)
            axes[row, col].set_xlabel("Temps (s)")
            if col == 0:
                axes[row, col].set_ylabel(f"{title}\namplitude (z-score)")
            axes[row, col].set_xlim(0, 4)

    plt.tight_layout()
    save(fig, REP_AUG, "03_signal_examples.png")


# ============================================================================
# ETAPE 4 — FEATURES
# ============================================================================

def _get_feature_names(n_feats: int) -> list:
    """Retourne des noms generiques ou depuis feature_eng si disponible."""
    try:
        sys.path.insert(0, str(PROJECT / "src" / "data"))
        from feature_eng import get_feature_names
        names = get_feature_names()
        return names[:n_feats]
    except Exception:
        return [f"feat_{i:02d}" for i in range(n_feats)]


def viz_features():
    print("\n[04_features]")

    # Charger feat78 et feat15 du split A (le plus representatif)
    datasets = {}
    for ds in ['conc', 'stress']:
        d = {}

        # feat78 pre-calculees
        p_feat78 = FEAT / ds / "feat78_train_A.npy"
        p_y      = FEAT / ds / "y_train_A.npy"
        if p_feat78.exists() and p_y.exists():
            d['feat78'] = {'X': np.load(p_feat78), 'y': np.load(p_y)}

        # feat15 : pre-calculees si disponibles, sinon calculees a la volee
        p_feat15 = FEAT / ds / "feat15_train_A.npy"
        if p_feat15.exists() and p_y.exists():
            d['feat15'] = {'X': np.load(p_feat15), 'y': np.load(p_y)}
        else:
            p_raw   = AUG / ds / "X_train_A.npy"
            p_raw_y = AUG / ds / "y_train_A.npy"
            if p_raw.exists() and p_raw_y.exists():
                try:
                    sys.path.insert(0, str(PROJECT / "src" / "data"))
                    from features_extraction import get_feature_vector
                    X_raw = np.load(p_raw)
                    y_raw = np.load(p_raw_y)
                    print(f"    feat15 calcul a la volee ({len(X_raw)} epochs)...")
                    feat15 = np.array([get_feature_vector(ep) for ep in X_raw],
                                      dtype=np.float32)
                    feat15 = np.nan_to_num(feat15, nan=0.0, posinf=0.0, neginf=0.0)
                    d['feat15'] = {'X': feat15, 'y': y_raw}
                except Exception as e:
                    print(f"    WARN: feat15 calcul echoue ({e})")

        datasets[ds] = d

    # ── 01 Comparaison feat15 vs feat78 ──────────────────────────────────
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.suptitle("Features — Comparaison feat15 vs feat78", fontsize=13, fontweight='bold')

    categories = {
        'PSD Welch (5)': 5,
        'Ratios cognitifs (5)': 5,
        'Hjorth + temps (6)': 6,
        'DWT sous-bandes (20)': 20,
        'Texturales (16)': 16,
        'Non-linéaires (5)': 5,
        'Transitions (6)': 6,
    }
    feat15_cats = {
        'PSD Welch (5)': 5,
        'Ratios cognitifs (5)': 4,
        'Hjorth + temps (6)': 3,
        'Power/Amp/RelE (3)': 3,
    }

    all_cats = list(categories.keys())
    counts63 = [categories[c] for c in all_cats]

    colors63 = plt.cm.Blues(np.linspace(0.4, 0.9, len(all_cats)))
    bars = ax.barh(all_cats, counts63, color=colors63, edgecolor='white')
    for bar, n in zip(bars, counts63):
        ax.text(n + 0.2, bar.get_y() + bar.get_height()/2,
                str(n), va='center', fontsize=10)

    ax.axvline(15, color='red', linestyle='--', linewidth=2,
               label='feat15 (seuil embarquable ESP32)')
    ax.axvline(63, color='navy', linestyle='--', linewidth=2,
               label='feat78 (total)')
    ax.set_xlabel("Nombre de features")
    ax.set_title("Répartition par catégorie — feat78 (78 features total)")
    ax.legend(fontsize=9)
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    save(fig, REP_FEAT, "01_feature_count.png")

    # ── 02 Top correlations avec les scores ───────────────────────────────
    for ds, title, score_label, color in [
        ('conc',   "Concentration", "conc_score", C_CONC),
        ('stress', "Stress",        "stress_score", C_STRESS),
    ]:
        if ds not in datasets or 'feat78' not in datasets[ds]:
            continue
        X = datasets[ds]['feat78']['X']
        y = datasets[ds]['feat78']['y']
        feat_names = _get_feature_names(X.shape[1])

        n_top = min(20, X.shape[1])
        corrs = np.array([spearmanr(X[:, i], y).statistic for i in range(X.shape[1])])
        top_idx = np.argsort(np.abs(corrs))[::-1][:n_top]

        fig, ax = plt.subplots(figsize=(11, 7))
        fig.suptitle(f"Features — Top {n_top} corrélations Spearman avec {score_label}",
                     fontsize=13, fontweight='bold')

        vals  = corrs[top_idx]
        names = [feat_names[i] if i < len(feat_names) else f"feat_{i}" for i in top_idx]
        bar_colors = [color if v > 0 else "#FF7043" for v in vals]

        bars = ax.barh(range(n_top), vals[::-1], color=bar_colors[::-1], edgecolor='white')
        ax.set_yticks(range(n_top))
        ax.set_yticklabels(names[::-1], fontsize=8)
        ax.axvline(0, color='black', linewidth=0.8)
        ax.set_xlabel("Corrélation Spearman r")
        ax.set_title(f"{title} (feat78, exp A)")
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        save(fig, REP_FEAT, f"02_top_correlations_{ds}.png")

    # ── 03 Distributions des features (top 12) ───────────────────────────
    for ds, title, score_label, color in [
        ('conc',   "Concentration", "conc_score", C_CONC),
        ('stress', "Stress",        "stress_score", C_STRESS),
    ]:
        if ds not in datasets or 'feat78' not in datasets[ds]:
            continue
        X = datasets[ds]['feat78']['X']
        y = datasets[ds]['feat78']['y']
        feat_names = _get_feature_names(X.shape[1])

        corrs = np.array([abs(spearmanr(X[:, i], y).statistic) for i in range(X.shape[1])])
        top12 = np.argsort(corrs)[::-1][:12]

        # Discretiser y en 3 bins pour colorer les violins
        y_bins = pd.cut(y, bins=3, labels=['Bas', 'Moyen', 'Haut'])

        fig, axes = plt.subplots(3, 4, figsize=(16, 10))
        fig.suptitle(f"Features — Distribution des 12 meilleures features ({title})",
                     fontsize=13, fontweight='bold')

        for i, feat_idx in enumerate(top12):
            ax = axes[i // 4, i % 4]
            name = feat_names[feat_idx] if feat_idx < len(feat_names) else f"feat_{feat_idx}"
            r    = spearmanr(X[:, feat_idx], y).statistic

            for cat, c in [('Bas', '#90CAF9'), ('Moyen', '#42A5F5'), ('Haut', '#0D47A1')]:
                mask = y_bins == cat
                ax.hist(X[mask, feat_idx], bins=20, color=c, alpha=0.6,
                        edgecolor='none', label=cat, density=True)
            ax.set_title(f"{name}\nr={r:.3f}", fontsize=8)
            ax.set_xlabel("Valeur", fontsize=7)
            if i % 4 == 0:
                ax.set_ylabel("Densité", fontsize=7)
            ax.tick_params(labelsize=7)
            if i == 0:
                ax.legend(fontsize=7)

        plt.tight_layout()
        save(fig, REP_FEAT, f"03_feature_distributions_{ds}.png")

    # ── 04 feat15 vs feat78 (corrélation croisée) ────────────────────────
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Features — Corrélation Spearman : feat15 vs feat78 avec le score",
                 fontsize=13, fontweight='bold')

    for ax, ds, title, color in [
        (axes[0], 'conc',   "Concentration", C_CONC),
        (axes[1], 'stress', "Stress",        C_STRESS),
    ]:
        d = datasets.get(ds, {})
        corrs = {}
        for prefix, label in [('feat15', 'feat15 (15)'), ('feat78', 'feat78 (78)')]:
            if prefix in d:
                X = d[prefix]['X']
                y = d[prefix]['y']
                c = np.array([abs(spearmanr(X[:, i], y).statistic) for i in range(X.shape[1])])
                corrs[label] = c

        if not corrs:
            ax.text(0.5, 0.5, "feat15 ou feat78\nmanquant", ha='center', va='center',
                    transform=ax.transAxes, fontsize=12, color='gray')
            continue

        labels  = list(corrs.keys())
        bp_data = [corrs[l] for l in labels]
        bp = ax.boxplot(bp_data, patch_artist=True, notch=False,
                        medianprops=dict(color='white', linewidth=2),
                        widths=0.4)
        box_colors = ['#90CAF9', '#1565C0']  # feat15 bleu clair, feat78 bleu fonce
        for box, c in zip(bp['boxes'], box_colors):
            box.set_facecolor(c)

        for i, data in enumerate(bp_data):
            ax.text(i + 1, data.max() + 0.01,
                    f"max={data.max():.3f}\nμ={data.mean():.3f}",
                    ha='center', fontsize=8)

        ax.set_xticklabels(labels)
        ax.set_ylabel("|r| Spearman avec le score")
        ax.set_title(f"{title}\n(|r| moyen feat15 vs feat78)")
        ax.set_ylim(0, max(max(d.max() for d in bp_data) * 1.25, 0.1))
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save(fig, REP_FEAT, "04_feat15_vs_feat78.png")


# ============================================================================
# POINT D'ENTREE
# ============================================================================

def main():
    print("=" * 65)
    print("NeuroCap — Visualisations Pipeline Regression")
    print(f"Sortie : reports/Regression/")
    print("=" * 65)

    missing = []
    if not (PREP / "X_conc.npy").exists():
        missing.append("data/Regression/preprocessed/  (manquant)")
    if not (AUG / "conc" / "X_train_A.npy").exists():
        missing.append("data/Regression/augmented/     (manquant)")

    if missing:
        print("\nERREUR — Donnees manquantes :")
        for m in missing:
            print(f"  {m}")
        print("\nExecutez d'abord :")
        print("  python src/data/pipeline_regression.py")
        return

    viz_preprocessing()
    viz_split()
    viz_augmentation()
    viz_features()

    print("\n" + "=" * 65)
    print("DONE — 13 figures generees")
    print("=" * 65)
    print("\n  reports/Regression/01_preprocessing/")
    print("    01_signal_amplitude.png")
    print("    02_score_distributions.png")
    print("    03_sample_epochs.png")
    print("    04_subjects_overview.png")
    print("\n  reports/Regression/02_split/")
    print("    01_split_sizes.png")
    print("    02_score_in_splits.png")
    print("    03_subjects_per_split.png")
    print("\n  reports/Regression/03_augmentation/")
    print("    01_dataset_growth.png")
    print("    02_score_propagation.png")
    print("    03_signal_examples.png")
    print("\n  reports/Regression/04_features/")
    print("    01_feature_count.png")
    print("    02_top_correlations_conc.png")
    print("    02_top_correlations_stress.png")
    print("    03_feature_distributions_conc.png")
    print("    03_feature_distributions_stress.png")
    print("    04_feat15_vs_feat78.png")


if __name__ == '__main__':
    main()
