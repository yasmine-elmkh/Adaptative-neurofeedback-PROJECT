"""
visualize_scoring.py
====================
EMPLACEMENT : src/data/scoring/visualize_scoring.py

OBJECTIF :
  Lire les CSV produits par concentration_scoring.py et stress_scoring.py,
  et generer des visualisations du dataset complet dans reports/scoring/merge/.

PREREQUIS :
  data/Scoring/scored_concentration.csv  (produit par concentration_scoring.py)
  data/Scoring/scored_stress.csv         (produit par stress_scoring.py)

VISUALISATIONS GENEREES :
  01_score_distributions.png   — histogrammes conc + stress cote a cote
  02_conc_by_level.png         — boxplot concentration par niveau (natural → highlevel)
  03_stress_by_task.png        — boxplot stress par tache (Relax / Arithmetic / Stroop / Mirror)
  04_conc_by_subject.png       — score moyen par sujet (concentration)
  05_stress_by_subject.png     — score moyen par sujet (stress)
  06_epochs_count.png          — nombre d'epochs par dataset / niveau / tache
  07_dataset_overview.png      — vue d'ensemble comparative des deux datasets

UTILISATION :
  python src/data/scoring/visualize_scoring.py
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from pathlib import Path

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT   = Path(__file__).resolve().parents[3]
SCORE_DIR = PROJECT / "data" / "Scoring"
REPORT    = PROJECT / "reports" / "scoring" / "merge"
REPORT.mkdir(parents=True, exist_ok=True)

# Palette coherente avec le reste du projet
PALETTE_CONC   = "#2196F3"   # bleu — concentration
PALETTE_STRESS = "#F44336"   # rouge — stress
LEVEL_COLORS   = ["#90CAF9", "#42A5F5", "#1E88E5", "#0D47A1"]
TASK_COLORS    = ["#A5D6A7", "#FFA726", "#EF5350", "#AB47BC"]


# ============================================================================
# UTILITAIRES
# ============================================================================
def save(fig, name: str) -> None:
    path = REPORT / name
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Sauvegarde → {path.relative_to(PROJECT)}")


def load_csvs():
    csv_conc   = SCORE_DIR / "scored_concentration.csv"
    csv_stress = SCORE_DIR / "scored_stress.csv"

    missing = []
    if not csv_conc.exists():
        missing.append(str(csv_conc))
    if not csv_stress.exists():
        missing.append(str(csv_stress))
    if missing:
        raise FileNotFoundError(
            "CSV manquants :\n" + "\n".join(missing) +
            "\nExecutez concentration_scoring.py et stress_scoring.py d'abord."
        )

    df_c = pd.read_csv(csv_conc)
    df_s = pd.read_csv(csv_stress)
    print(f"[CSV] concentration : {len(df_c)} epochs | stress : {len(df_s)} epochs")
    return df_c, df_s


# ============================================================================
# FIGURE 1 — Distributions globales des scores
# ============================================================================
def fig_score_distributions(df_c, df_s):
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Distributions des scores — Dataset NeuroCap", fontsize=14, fontweight='bold')

    # Concentration
    ax = axes[0]
    ax.hist(df_c['conc_score'], bins=30, color=PALETTE_CONC, edgecolor='white', alpha=0.85)
    ax.axvline(df_c['conc_score'].mean(), color='navy', linestyle='--', linewidth=1.5,
               label=f"Moyenne = {df_c['conc_score'].mean():.2f}")
    ax.set_title("Concentration (scored_concentration.csv)", fontsize=11)
    ax.set_xlabel("conc_score (0–10)")
    ax.set_ylabel("Nombre d'epochs")
    ax.legend()
    ax.set_xlim(0, 10)
    ax.text(0.97, 0.97, f"N = {len(df_c)}\nσ = {df_c['conc_score'].std():.2f}",
            transform=ax.transAxes, ha='right', va='top',
            fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    # Stress
    ax = axes[1]
    ax.hist(df_s['stress_score'], bins=30, color=PALETTE_STRESS, edgecolor='white', alpha=0.85)
    ax.axvline(df_s['stress_score'].mean(), color='darkred', linestyle='--', linewidth=1.5,
               label=f"Moyenne = {df_s['stress_score'].mean():.2f}")
    ax.set_title("Stress (scored_stress.csv)", fontsize=11)
    ax.set_xlabel("stress_score (0–10)")
    ax.set_ylabel("Nombre d'epochs")
    ax.legend()
    ax.set_xlim(0, 10)
    ax.text(0.97, 0.97, f"N = {len(df_s)}\nσ = {df_s['stress_score'].std():.2f}",
            transform=ax.transAxes, ha='right', va='top',
            fontsize=9, bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    plt.tight_layout()
    save(fig, "01_score_distributions.png")


# ============================================================================
# FIGURE 2 — Concentration par niveau cognitif
# ============================================================================
def fig_conc_by_level(df_c):
    level_order = ['natural', 'lowlevel', 'midlevel', 'highlevel']
    labels_fr   = ['Natural\n(0–2.5)', 'Lowlevel\n(2.5–5)', 'Midlevel\n(5–7.5)', 'Highlevel\n(7.5–10)']

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Dataset Concentration — Scores par niveau cognitif", fontsize=13, fontweight='bold')

    # Boxplot
    ax = axes[0]
    data_by_level = [df_c[df_c['level'] == lv]['conc_score'].values for lv in level_order]
    bp = ax.boxplot(data_by_level, patch_artist=True, notch=False,
                    medianprops=dict(color='white', linewidth=2))
    for patch, color in zip(bp['boxes'], LEVEL_COLORS):
        patch.set_facecolor(color)
    ax.set_xticklabels(labels_fr)
    ax.set_ylabel("conc_score (0–10)")
    ax.set_title("Boxplot par niveau")
    ax.set_ylim(0, 10)
    ax.grid(axis='y', alpha=0.3)

    # Nombre d'epochs et moyenne par niveau
    ax2 = axes[1]
    counts = [len(df_c[df_c['level'] == lv]) for lv in level_order]
    means  = [df_c[df_c['level'] == lv]['conc_score'].mean() for lv in level_order]
    bars = ax2.bar(labels_fr, counts, color=LEVEL_COLORS, edgecolor='white')
    for bar, mean, count in zip(bars, means, counts):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
                 f"moy={mean:.1f}\nN={count}", ha='center', fontsize=8)
    ax2.set_ylabel("Nombre d'epochs")
    ax2.set_title("Epochs et score moyen par niveau")
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save(fig, "02_conc_by_level.png")


# ============================================================================
# FIGURE 3 — Stress par tâche
# ============================================================================
def fig_stress_by_task(df_s):
    task_order  = ['Relax', 'Arithmetic', 'Mirror_image', 'Stroop']
    labels_fr   = ['Relax\n(repos)', 'Arithmetic\n(calcul)', 'Mirror\n(symétrie)', 'Stroop\n(interf.)']

    available = [t for t in task_order if t in df_s['task'].unique()]
    labels_av = [labels_fr[task_order.index(t)] for t in available]
    colors_av = [TASK_COLORS[task_order.index(t)] for t in available]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Dataset Stress — Scores par tâche", fontsize=13, fontweight='bold')

    # Boxplot
    ax = axes[0]
    data_by_task = [df_s[df_s['task'] == t]['stress_score'].values for t in available]
    bp = ax.boxplot(data_by_task, patch_artist=True, notch=False,
                    medianprops=dict(color='white', linewidth=2))
    for patch, color in zip(bp['boxes'], colors_av):
        patch.set_facecolor(color)
    ax.set_xticklabels(labels_av)
    ax.set_ylabel("stress_score (0–10)")
    ax.set_title("Boxplot par tâche")
    ax.set_ylim(0, 10)
    ax.grid(axis='y', alpha=0.3)

    # Nombre d'epochs et moyenne par tâche
    ax2 = axes[1]
    counts = [len(df_s[df_s['task'] == t]) for t in available]
    means  = [df_s[df_s['task'] == t]['stress_score'].mean() for t in available]
    bars = ax2.bar(labels_av, counts, color=colors_av, edgecolor='white')
    for bar, mean, count in zip(bars, means, counts):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 f"moy={mean:.1f}\nN={count}", ha='center', fontsize=8)
    ax2.set_ylabel("Nombre d'epochs")
    ax2.set_title("Epochs et score moyen par tâche")
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save(fig, "03_stress_by_task.png")


# ============================================================================
# FIGURE 4 — Score moyen par sujet (concentration)
# ============================================================================
def fig_conc_by_subject(df_c):
    subj_stats = df_c.groupby('subject')['conc_score'].agg(['mean', 'std', 'count']).reset_index()
    subj_stats = subj_stats.sort_values('subject')

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(subj_stats['subject'].astype(str), subj_stats['mean'],
           color=PALETTE_CONC, alpha=0.8, edgecolor='white')
    ax.errorbar(range(len(subj_stats)), subj_stats['mean'],
                yerr=subj_stats['std'], fmt='none', color='navy', capsize=3)

    for i, row in subj_stats.iterrows():
        ax.text(list(subj_stats['subject']).index(row['subject']),
                row['mean'] + row['std'] + 0.1,
                f"N={int(row['count'])}", ha='center', fontsize=7)

    ax.set_xlabel("Sujet")
    ax.set_ylabel("conc_score moyen ± std")
    ax.set_title("Concentration — Score moyen par sujet (OpenBCI, 15 sujets)", fontsize=12)
    ax.set_ylim(0, 10)
    ax.axhline(df_c['conc_score'].mean(), color='red', linestyle='--',
               linewidth=1, label=f"Moyenne globale = {df_c['conc_score'].mean():.2f}")
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    save(fig, "04_conc_by_subject.png")


# ============================================================================
# FIGURE 5 — Score moyen par sujet (stress)
# ============================================================================
def fig_stress_by_subject(df_s):
    subj_stats = df_s.groupby('subject')['stress_score'].agg(['mean', 'std', 'count']).reset_index()
    subj_stats = subj_stats.sort_values('subject')

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(subj_stats['subject'].astype(str), subj_stats['mean'],
           color=PALETTE_STRESS, alpha=0.8, edgecolor='white')
    ax.errorbar(range(len(subj_stats)), subj_stats['mean'],
                yerr=subj_stats['std'], fmt='none', color='darkred', capsize=3)

    for i, row in subj_stats.iterrows():
        ax.text(list(subj_stats['subject']).index(row['subject']),
                row['mean'] + row['std'] + 0.1,
                f"N={int(row['count'])}", ha='center', fontsize=7)

    ax.set_xlabel("Sujet")
    ax.set_ylabel("stress_score moyen ± std")
    ax.set_title("Stress — Score moyen par sujet (EMOTIV, 40 sujets)", fontsize=12)
    ax.set_ylim(0, 10)
    ax.axhline(df_s['stress_score'].mean(), color='navy', linestyle='--',
               linewidth=1, label=f"Moyenne globale = {df_s['stress_score'].mean():.2f}")
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    save(fig, "05_stress_by_subject.png")


# ============================================================================
# FIGURE 6 — Nombre d'epochs par dataset
# ============================================================================
def fig_epochs_count(df_c, df_s):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Volume de données — Epochs par dataset", fontsize=13, fontweight='bold')

    # Concentration : par niveau × tâche
    ax = axes[0]
    if 'task' in df_c.columns:
        pivot = df_c.groupby(['task', 'level']).size().unstack(fill_value=0)
        pivot = pivot.reindex(columns=['natural', 'lowlevel', 'midlevel', 'highlevel'],
                              fill_value=0)
        pivot.plot(kind='bar', ax=ax, color=LEVEL_COLORS, edgecolor='white')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=30, ha='right')
        ax.legend(['Natural', 'Lowlevel', 'Midlevel', 'Highlevel'], fontsize=8)
    else:
        counts = df_c['level'].value_counts().reindex(
            ['natural', 'lowlevel', 'midlevel', 'highlevel'], fill_value=0)
        ax.bar(counts.index, counts.values, color=LEVEL_COLORS, edgecolor='white')

    ax.set_title(f"Concentration (N={len(df_c)} epochs)")
    ax.set_ylabel("Nombre d'epochs")
    ax.grid(axis='y', alpha=0.3)

    # Stress : par tâche
    ax2 = axes[1]
    task_order = ['Relax', 'Arithmetic', 'Mirror_image', 'Stroop']
    available  = [t for t in task_order if t in df_s['task'].unique()]
    counts_s   = [len(df_s[df_s['task'] == t]) for t in available]
    colors_av  = [TASK_COLORS[task_order.index(t)] for t in available]
    bars = ax2.bar(available, counts_s, color=colors_av, edgecolor='white')
    for bar, count in zip(bars, counts_s):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                 str(count), ha='center', fontsize=9)
    ax2.set_title(f"Stress (N={len(df_s)} epochs)")
    ax2.set_ylabel("Nombre d'epochs")
    ax2.set_xticklabels(available, rotation=20, ha='right')
    ax2.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    save(fig, "06_epochs_count.png")


# ============================================================================
# FIGURE 7 — Vue d'ensemble comparative
# ============================================================================
def fig_dataset_overview(df_c, df_s):
    fig = plt.figure(figsize=(16, 8))
    fig.suptitle("NeuroCap — Vue d'ensemble des datasets scorés", fontsize=15, fontweight='bold')

    gs = gridspec.GridSpec(2, 4, figure=fig, hspace=0.45, wspace=0.4)

    # ── Score conc global (haut gauche) ──────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.hist(df_c['conc_score'], bins=20, color=PALETTE_CONC, alpha=0.85, edgecolor='white')
    ax1.set_title("Conc score\n(distribution)", fontsize=10)
    ax1.set_xlabel("score (0–10)")
    ax1.set_xlim(0, 10)
    ax1.axvline(df_c['conc_score'].mean(), color='navy', linestyle='--', linewidth=1.5)

    # ── Boxplot conc par niveau ────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1:3])
    level_order = ['natural', 'lowlevel', 'midlevel', 'highlevel']
    data_by_level = [df_c[df_c['level'] == lv]['conc_score'].values for lv in level_order]
    bp = ax2.boxplot(data_by_level, patch_artist=True,
                     medianprops=dict(color='white', linewidth=2))
    for patch, color in zip(bp['boxes'], LEVEL_COLORS):
        patch.set_facecolor(color)
    ax2.set_xticklabels(['Natural', 'Low', 'Mid', 'High'], fontsize=9)
    ax2.set_title("Conc score par niveau", fontsize=10)
    ax2.set_ylim(0, 10)
    ax2.grid(axis='y', alpha=0.3)

    # ── Stats conc (haut droite) ───────────────────────────────────
    ax3 = fig.add_subplot(gs[0, 3])
    ax3.axis('off')
    stats_c = [
        ["Sujets", str(df_c['subject'].nunique())],
        ["Epochs", str(len(df_c))],
        ["Moy. score", f"{df_c['conc_score'].mean():.2f}"],
        ["Std score", f"{df_c['conc_score'].std():.2f}"],
        ["Min / Max", f"{df_c['conc_score'].min():.1f} / {df_c['conc_score'].max():.1f}"],
        ["Appareils", "OpenBCI 8ch"],
        ["Fs", "200 Hz → 250 Hz"],
    ]
    table = ax3.table(cellText=stats_c, colLabels=["", "Concentration"],
                      loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.4)
    ax3.set_title("Résumé concentration", fontsize=10)

    # ── Score stress global (bas gauche) ──────────────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    ax4.hist(df_s['stress_score'], bins=20, color=PALETTE_STRESS, alpha=0.85, edgecolor='white')
    ax4.set_title("Stress score\n(distribution)", fontsize=10)
    ax4.set_xlabel("score (0–10)")
    ax4.set_xlim(0, 10)
    ax4.axvline(df_s['stress_score'].mean(), color='darkred', linestyle='--', linewidth=1.5)

    # ── Boxplot stress par tâche ───────────────────────────────────
    ax5 = fig.add_subplot(gs[1, 1:3])
    task_order  = ['Relax', 'Arithmetic', 'Mirror_image', 'Stroop']
    available   = [t for t in task_order if t in df_s['task'].unique()]
    data_by_task = [df_s[df_s['task'] == t]['stress_score'].values for t in available]
    colors_av   = [TASK_COLORS[task_order.index(t)] for t in available]
    bp2 = ax5.boxplot(data_by_task, patch_artist=True,
                      medianprops=dict(color='white', linewidth=2))
    for patch, color in zip(bp2['boxes'], colors_av):
        patch.set_facecolor(color)
    ax5.set_xticklabels([t.replace('_', '\n') for t in available], fontsize=9)
    ax5.set_title("Stress score par tâche", fontsize=10)
    ax5.set_ylim(0, 10)
    ax5.grid(axis='y', alpha=0.3)

    # ── Stats stress (bas droite) ──────────────────────────────────
    ax6 = fig.add_subplot(gs[1, 3])
    ax6.axis('off')
    stats_s = [
        ["Sujets", str(df_s['subject'].nunique())],
        ["Epochs", str(len(df_s))],
        ["Moy. score", f"{df_s['stress_score'].mean():.2f}"],
        ["Std score", f"{df_s['stress_score'].std():.2f}"],
        ["Min / Max", f"{df_s['stress_score'].min():.1f} / {df_s['stress_score'].max():.1f}"],
        ["Appareils", "EMOTIV Flex 32ch"],
        ["Fs", "128 Hz → 250 Hz"],
    ]
    table2 = ax6.table(cellText=stats_s, colLabels=["", "Stress"],
                       loc='center', cellLoc='center')
    table2.auto_set_font_size(False)
    table2.set_fontsize(9)
    table2.scale(1, 1.4)
    ax6.set_title("Résumé stress", fontsize=10)

    save(fig, "07_dataset_overview.png")


# ============================================================================
# POINT D'ENTREE
# ============================================================================
def main():
    print("=" * 60)
    print("NeuroCap — Visualisation Scoring (merge)")
    print(f"Sortie : reports/scoring/merge/")
    print("=" * 60)

    df_c, df_s = load_csvs()

    print("\n[1/7] Distribution globale des scores...")
    fig_score_distributions(df_c, df_s)

    print("[2/7] Concentration par niveau...")
    fig_conc_by_level(df_c)

    print("[3/7] Stress par tache...")
    fig_stress_by_task(df_s)

    print("[4/7] Score moyen par sujet (concentration)...")
    fig_conc_by_subject(df_c)

    print("[5/7] Score moyen par sujet (stress)...")
    fig_stress_by_subject(df_s)

    print("[6/7] Volume d'epochs par dataset...")
    fig_epochs_count(df_c, df_s)

    print("[7/7] Vue d'ensemble comparative...")
    fig_dataset_overview(df_c, df_s)

    print(f"\n✅ 7 figures sauvegardees dans reports/scoring/merge/")
    print(f"   01_score_distributions.png")
    print(f"   02_conc_by_level.png")
    print(f"   03_stress_by_task.png")
    print(f"   04_conc_by_subject.png")
    print(f"   05_stress_by_subject.png")
    print(f"   06_epochs_count.png")
    print(f"   07_dataset_overview.png")


if __name__ == '__main__':
    main()
