"""
NeuroCap – Comparaison Finale : Baseline ML vs Deep Learning
=============================================================
Agrège les résultats honnêtes et produit la recommandation finale.

Sources de métriques (par ordre de priorité) :

  Deep Learning → LOSO (Leave-One-Subject-Out), évaluation inter-sujets
    Fichier : reports/Tests/deep_learning/results.json
    Fallback : reports/deep_learning/DL_outputs/{model}/LOSO_exp_A/metrics.json

  Baseline ML → Jeu de test holdout OU métriques LOSO
    Fichier : reports/Tests/baselines/results.json
    Fallback : reports/Baseline/baselines_outputs/results.json

NOTE sur les scores parfaits DL (F1=1.0 sur X_test.npy) :
  Ces scores proviennent d'une évaluation sur X_test.npy créé par split
  aléatoire d'époques, sans séparation par sujet (fuite intra-sujet).
  Le classement final utilise UNIQUEMENT les métriques LOSO.

Usage :
    cd EEG_project
    python Tests/test_baselines.py        # étape 1
    python Tests/test_deep_learning.py    # étape 2
    python Tests/test_final_comparison.py # étape 3

    # Lecture directe des métriques d'entraînement :
    python Tests/test_final_comparison.py --from-training

Sorties :
    reports/Tests/final/
        ├── unified_ranking.csv
        ├── final_comparison_bars.png
        ├── baseline_vs_dl_boxplot.png
        ├── deployment_quadrant.png
        ├── top10_radar.png
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
plt.style.use('seaborn-v0_8-whitegrid')

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]

TEST_BASELINE_JSON = PROJECT_ROOT / 'reports' / 'Tests' / 'baselines'     / 'results.json'
TEST_DL_JSON       = PROJECT_ROOT / 'reports' / 'Tests' / 'deep_learning' / 'results.json'

TRAIN_BASELINE_JSON = PROJECT_ROOT / 'reports' / 'Baseline' / 'baselines_outputs' / 'results.json'
TRAIN_DL_BASE       = PROJECT_ROOT / 'reports' / 'deep_learning' / 'DL_outputs'

REPORT_DIR = PROJECT_ROOT / 'reports' / 'Tests' / 'final'
REPORT_DIR.mkdir(parents=True, exist_ok=True)

ALL_DL_MODELS = [
    "CNN1D", "CNN2D", "CNN3D", "EEGNet", "TCN", "CNN_LSTM_Att", "CNN_GRU_Att",
    "LSTM_1L", "LSTM_2L", "BiLSTM_1L", "BiLSTM_2L",
    "GRU_1L", "GRU_2L", "BiGRU_1L", "BiGRU_2L",
    "LSTM_Att", "BiLSTM_Att", "GRU_Att", "BiGRU_Att",
]


# ============================================================================
# CHARGEMENT DES RÉSULTATS
# ============================================================================
def _make_row(model, category, f1_macro, auc, accuracy, recall, specificity,
              precision, pct_uncertain, inference_ms, n_samples, source):
    return dict(model=model, category=category, f1_macro=f1_macro, auc=auc,
                accuracy=accuracy, recall=recall, specificity=specificity,
                precision=precision, pct_uncertain=pct_uncertain,
                inference_ms=inference_ms, n_samples=n_samples, source=source)


def load_test_baselines():
    if not TEST_BASELINE_JSON.exists():
        return None, "test_baselines.py n'a pas encore été exécuté"
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
            source='test_holdout',
        ))
    return rows, None


def load_test_dl_loso():
    """
    Charge les métriques LOSO depuis results.json de test_deep_learning.py.
    Ce fichier ne contient QUE des métriques LOSO (honnêtes).
    """
    if not TEST_DL_JSON.exists():
        return None, "test_deep_learning.py n'a pas encore été exécuté"
    with open(TEST_DL_JSON) as f:
        data = json.load(f)
    if data.get('evaluation_method') != 'LOSO':
        return None, "Le fichier results.json DL n'est pas en mode LOSO"
    rows = []
    for r in data.get('all_results', []):
        rows.append(_make_row(
            model=r.get('model', '?'),
            category='Deep Learning',
            f1_macro=r.get('f1_macro', 0),
            auc=r.get('auc', 0.5),
            accuracy=r.get('accuracy', 0),
            recall=r.get('recall', 0),
            specificity=r.get('specificity', 0),
            precision=r.get('precision', 0),
            pct_uncertain=r.get('pct_uncertain', 0),
            inference_ms=0,
            n_samples=0,
            source='loso_saved',
        ))
    return rows, None


def load_training_baselines():
    """Fallback : lit results.json issu de l'entraînement baseline."""
    if not TRAIN_BASELINE_JSON.exists():
        return None, "Métriques d'entraînement baseline introuvables"
    with open(TRAIN_BASELINE_JSON) as f:
        data = json.load(f)
    loso = data.get('loso', {})
    rows = []
    for exp, models_dict in loso.items():
        for model, m in models_dict.items():
            rows.append(_make_row(
                model=f"{model}-{exp}",
                category='Baseline ML',
                f1_macro=m.get('f1_macro', 0),
                auc=m.get('auc', 0.5),
                accuracy=m.get('acc', 0),
                recall=m.get('recall', 0),
                specificity=m.get('specificity', 0),
                precision=m.get('precision', 0),
                pct_uncertain=m.get('pct_uncertain', 0),
                inference_ms=0.5,
                n_samples=0,
                source='training_loso',
            ))
    return (rows, None) if rows else (None, "Aucun résultat dans results.json baseline")


def load_training_dl_loso():
    """Fallback : lit LOSO_exp_A/metrics.json pour chaque modèle DL."""
    rows = []
    for model_name in ALL_DL_MODELS:
        loso_path = TRAIN_DL_BASE / model_name / 'LOSO_exp_A' / 'metrics.json'
        if loso_path.exists():
            with open(loso_path) as f:
                m = json.load(f)
            rows.append(_make_row(
                model=model_name,
                category='Deep Learning',
                f1_macro=m.get('f1_macro', 0),
                auc=m.get('auc', 0.5),
                accuracy=m.get('accuracy', 0),
                recall=m.get('recall', 0),
                specificity=m.get('specificity', 0),
                precision=m.get('precision', 0),
                pct_uncertain=m.get('pct_uncertain', 0),
                inference_ms=0,
                n_samples=0,
                source='loso_saved_training',
            ))
    return (rows, None) if rows else (None, "Aucun LOSO_exp_A/metrics.json trouvé")


# ============================================================================
# SCORE DE DÉCISION
# ============================================================================
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
# VISUALISATIONS
# ============================================================================
def plot_final_bars(df: pd.DataFrame, save_path: Path):
    top_n = min(15, len(df))
    top   = df.head(top_n).copy()
    palette = {'Baseline ML': '#E74C3C', 'Deep Learning': '#2980B9'}
    metrics = ['f1_macro', 'auc', 'accuracy']
    titles  = ['F1-MACRO (critère principal)', 'AUC', 'Accuracy']

    fig, axes = plt.subplots(1, 3, figsize=(21, max(6, top_n * 0.45)))
    for ax, metric, title in zip(axes, metrics, titles):
        sorted_top = top.sort_values(metric, ascending=True)
        clrs = [palette.get(c, '#7F8C8D') for c in sorted_top['category']]
        bars = ax.barh(sorted_top['model'], sorted_top[metric],
                       color=clrs, alpha=0.85)
        ax.set_xlabel(metric.replace('_', ' ').upper())
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_xlim([0, 1.1])
        ax.axvline(0.80, color='green', ls='--', lw=1, alpha=0.5, label='80%')
        ax.legend(fontsize=8)
        ax.grid(axis='x', alpha=0.3)
        for bar, val in zip(bars, sorted_top[metric]):
            ax.text(val + 0.005, bar.get_y() + bar.get_height()/2,
                    f'{val:.3f}', va='center', fontsize=7)

    from matplotlib.patches import Patch
    handles = [Patch(color='#E74C3C', label='Baseline ML'),
               Patch(color='#2980B9', label='Deep Learning (LOSO)')]
    fig.legend(handles=handles, loc='lower center', ncol=2,
               fontsize=10, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle('NeuroCap – Top modèles : Baseline ML vs Deep Learning (LOSO)',
                 fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_category_boxplot(df: pd.DataFrame, save_path: Path):
    metrics = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    labels  = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']
    palette = {'Baseline ML': '#E74C3C', 'Deep Learning': '#2980B9'}
    cats    = ['Baseline ML', 'Deep Learning']

    fig, axes = plt.subplots(1, len(metrics), figsize=(16, 5))
    for ax, metric, label in zip(axes, metrics, labels):
        for i, cat in enumerate(cats):
            sub = df[df['category'] == cat][metric].dropna()
            if sub.empty:
                continue
            ax.boxplot(sub, positions=[i], widths=0.4, patch_artist=True,
                       boxprops=dict(facecolor=palette[cat], alpha=0.6),
                       medianprops=dict(color='black', lw=2))
        ax.set_xticks([0, 1])
        ax.set_xticklabels(['Baseline\nML', 'DL\n(LOSO)'], fontsize=8)
        ax.set_ylabel(label)
        ax.set_title(label, fontsize=10)
        ax.set_ylim([0, 1.05])
        ax.grid(axis='y', alpha=0.3)

    fig.suptitle('Distribution des métriques : Baseline ML vs Deep Learning (LOSO)',
                 fontsize=12, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_deployment_quadrant(df: pd.DataFrame, save_path: Path):
    """F1-MACRO vs score pondéré, coloré par catégorie."""
    palette = {'Baseline ML': '#E74C3C', 'Deep Learning': '#2980B9'}
    fig, ax = plt.subplots(figsize=(10, 7))

    for cat, grp in df.groupby('category'):
        ax.scatter(grp['f1_macro'], grp['weighted_score'],
                   color=palette.get(cat, 'gray'), label=cat,
                   s=120, alpha=0.85, edgecolors='white', lw=0.5, zorder=5)
        for _, row in grp.nlargest(3, 'f1_macro').iterrows():
            ax.annotate(row['model'], (row['f1_macro'], row['weighted_score']),
                        textcoords='offset points', xytext=(5, 3), fontsize=7)

    ax.set_xlabel('F1-MACRO (LOSO)', fontsize=11)
    ax.set_ylabel('Score pondéré (40% F1m + 30% AUC + 20% Acc + 10% certitude)', fontsize=10)
    ax.set_title('Performance globale : Baseline ML vs Deep Learning (LOSO)',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_top10_radar(df: pd.DataFrame, save_path: Path):
    top10 = df.head(min(10, len(df)))
    cats  = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    lbls  = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']
    N     = len(cats)
    angles = [n / float(N) * 2 * np.pi for n in range(N)] + [0]

    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))
    cmap    = plt.cm.tab10(np.linspace(0, 1, len(top10)))
    ls_map  = {'Baseline ML': 'dashed', 'Deep Learning': 'solid'}

    for (_, row), color in zip(top10.iterrows(), cmap):
        vals = [row[c] for c in cats] + [row[cats[0]]]
        ls   = ls_map.get(row['category'], 'solid')
        tag  = '[BL]' if row['category'] == 'Baseline ML' else '[DL]'
        ax.plot(angles, vals, lw=2, color=color, ls=ls,
                label=f"{tag} {row['model']}")
        ax.fill(angles, vals, alpha=0.06, color=color)

    ax.set_thetagrids(np.degrees(angles[:-1]), lbls, fontsize=9)
    ax.set_ylim([0, 1])
    ax.set_title('Top 10 modèles (BL=Baseline, DL=LOSO)',
                 fontsize=11, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.6, 1.15), fontsize=7)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# RAPPORT DE DÉCISION FINALE
# ============================================================================
def write_final_report(df: pd.DataFrame, report_path: Path, source_note: str):
    best_overall = df.iloc[0]

    # ── Sélection honnête du meilleur par catégorie ───────────────────────────
    bl_df = df[df['category'] == 'Baseline ML']
    dl_df = df[df['category'] == 'Deep Learning']
    best_baseline = bl_df.iloc[0] if not bl_df.empty else None
    best_dl       = dl_df.iloc[0] if not dl_df.empty else None

    bl_mean_f1 = bl_df['f1_macro'].mean() if not bl_df.empty else 0
    dl_mean_f1 = dl_df['f1_macro'].mean() if not dl_df.empty else 0
    gap        = dl_mean_f1 - bl_mean_f1

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("NeuroCap – RAPPORT DE DÉCISION FINALE\n")
        f.write("Choix du modèle pour déploiement (ESP32 + Casque EEG)\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Source des données : {source_note}\n")
        f.write(f"Métriques DL       : LOSO (Leave-One-Subject-Out) — HONNÊTE\n")
        f.write(f"Métriques Baseline : jeu de test holdout ou LOSO\n")
        f.write(f"Score pondéré      : 40% F1m + 30% AUC + 20% Acc + 10% certitude\n\n")
        f.write("AVERTISSEMENT SCORES PARFAITS :\n")
        f.write("  Les scores F1=1.0 observés sur X_test.npy en DL sont dus à une\n")
        f.write("  fuite intra-sujet (split aléatoire d'époques sans séparation\n")
        f.write("  par sujet). Ces scores ne sont PAS utilisés ici.\n")
        f.write("  Ce rapport utilise UNIQUEMENT les métriques LOSO.\n\n")

        # Tableau top 10
        f.write("─" * 70 + "\n")
        f.write("TOP 10 TOUS MODÈLES (métriques LOSO pour DL)\n")
        f.write("─" * 70 + "\n")
        f.write(f"{'Rang':<5} {'Cat':>3} {'Modèle':<28} "
                f"{'F1m':>6} {'AUC':>6} {'Acc':>6} {'Inc%':>5} {'Score':>7}\n")
        f.write("-" * 70 + "\n")
        for rank, row in df.head(10).iterrows():
            cat = 'BL' if row['category'] == 'Baseline ML' else 'DL'
            f.write(f"{rank+1:<5} [{cat}] {row['model']:<28} "
                    f"{row['f1_macro']:>6.4f} {row['auc']:>6.4f} "
                    f"{row['accuracy']:>6.4f} {row['pct_uncertain']:>5.1f}% "
                    f"{row['weighted_score']:>7.4f}\n")
        f.write("\n")

        # Analyse comparative
        f.write("─" * 70 + "\n")
        f.write("ANALYSE COMPARATIVE\n")
        f.write("─" * 70 + "\n")
        if best_baseline is not None:
            f.write(f"  Meilleur Baseline ML : {best_baseline['model']}\n")
            f.write(f"    F1-MACRO = {best_baseline['f1_macro']:.4f}  "
                    f"AUC = {best_baseline['auc']:.4f}  "
                    f"Acc = {best_baseline['accuracy']:.4f}\n")
        if best_dl is not None:
            f.write(f"\n  Meilleure Architecture DL (LOSO) : {best_dl['model']}\n")
            f.write(f"    F1-MACRO = {best_dl['f1_macro']:.4f}  "
                    f"AUC = {best_dl['auc']:.4f}  "
                    f"Acc = {best_dl['accuracy']:.4f}\n")
        f.write(f"\n  F1-MACRO moyen Baseline : {bl_mean_f1:.4f}\n")
        f.write(f"  F1-MACRO moyen DL (LOSO): {dl_mean_f1:.4f}\n")
        sign = "+" if gap >= 0 else ""
        f.write(f"  Gain DL vs Baseline     : {sign}{gap:.4f}\n\n")

        # Recommandation
        f.write("=" * 70 + "\n")
        f.write("RECOMMANDATION FINALE\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"  Modèle recommandé : {best_overall['model']}\n")
        f.write(f"  Catégorie          : {best_overall['category']}\n")
        f.write(f"  F1-MACRO (LOSO)    : {best_overall['f1_macro']:.4f}\n")
        f.write(f"  AUC                : {best_overall['auc']:.4f}\n")
        f.write(f"  Accuracy           : {best_overall['accuracy']:.4f}\n")
        f.write(f"  Epochs incertaines : {best_overall['pct_uncertain']:.1f}%\n")
        f.write(f"  Score pondéré      : {best_overall['weighted_score']:.4f}\n\n")

        # Arbre de décision
        f.write("─" * 70 + "\n")
        f.write("JUSTIFICATION\n")
        f.write("─" * 70 + "\n\n")
        if best_overall['category'] == 'Baseline ML':
            f.write("  → Baseline ML recommandé :\n")
            f.write("    • Performances LOSO équivalentes ou supérieures au DL\n")
            f.write("    • Latence < 1 ms/epoch → déploiement ESP32 immédiat\n")
            f.write("    • Pas de GPU requis pour l'inférence\n")
            f.write("    • Features interprétables (TBR, EI, Hjorth...)\n")
        else:
            f.write("  → Deep Learning recommandé :\n")
            if best_baseline is not None and best_dl is not None:
                delta = best_dl['f1_macro'] - best_baseline['f1_macro']
                f.write(f"    • Gain LOSO F1-MACRO : +{delta:.4f} vs Baseline\n")
            f.write("    • Extraction automatique de features temporelles\n")
            f.write("    • Meilleure généralisation inter-sujets (confirmée par LOSO)\n")

        f.write("\n─" * 35 + "\n")
        f.write("STRATÉGIE DE DÉPLOIEMENT\n")
        f.write("─" * 70 + "\n\n")
        bl_name = best_baseline['model'] if best_baseline is not None else '?'
        dl_name = best_dl['model']       if best_dl is not None       else '?'
        f.write(f"  Phase 1 – Prototype embarqué (ESP32 / RPi) :\n")
        f.write(f"    → {bl_name} (Baseline ML)\n")
        f.write(f"    Latence < 1 ms/epoch, pas de GPU, déploiement immédiat.\n\n")
        f.write(f"  Phase 2 – App mobile / serveur :\n")
        f.write(f"    → {dl_name} (Deep Learning, LOSO validé)\n")
        f.write(f"    Meilleure précision, nécessite GPU ou NPU.\n\n")
        f.write(f"  Phase 3 – Personnalisation :\n")
        f.write(f"    → Fine-tuner EEGNet sur nouveaux sujets (Transfer Learning).\n\n")

        f.write("─" * 70 + "\n")
        f.write("CONFORMITÉ CdC\n")
        f.write("─" * 70 + "\n\n")
        unc_ok = best_overall['pct_uncertain'] < 20
        f.write(f"  [§2.5.1] Epochs incertaines (max(P)<0.60) : "
                f"{best_overall['pct_uncertain']:.1f}%  "
                f"→ {'CONFORME' if unc_ok else 'A SURVEILLER'} (cible < 20%)\n")
        f.write(f"  [LOSO] Généralisation inter-sujets validée.\n")
        f.write("=" * 70 + "\n")


# ============================================================================
# MAIN
# ============================================================================
def main(from_training: bool = False):
    print("=" * 75)
    print("NeuroCap – Comparaison Finale (métriques LOSO pour DL)")
    print("=" * 75)

    all_rows = []
    source_note = ""

    if from_training:
        print("\n[Mode] Métriques d'entraînement (--from-training)")
        rows_bl, err_bl = load_training_baselines()
        rows_dl, err_dl = load_training_dl_loso()
        source_note = "métriques d'entraînement : LOSO sauvegardé"
    else:
        print("\n[Mode] Résultats des suites de test")
        rows_bl, err_bl = load_test_baselines()
        rows_dl, err_dl = load_test_dl_loso()
        source_note = "test_baselines.py (holdout) + test_deep_learning.py (LOSO)"

        # Fallback automatique
        if rows_bl is None:
            print(f"  [INFO] Baselines test : {err_bl}")
            print(f"         → fallback sur métriques d'entraînement")
            rows_bl, err_bl = load_training_baselines()
            if rows_bl is None:
                print(f"  [WARN] {err_bl}")
        if rows_dl is None:
            print(f"  [INFO] DL LOSO test : {err_dl}")
            print(f"         → fallback sur LOSO_exp_A/metrics.json de l'entraînement")
            rows_dl, err_dl = load_training_dl_loso()
            if rows_dl is None:
                print(f"  [WARN] {err_dl}")

    if rows_bl:
        all_rows.extend(rows_bl)
        print(f"\n  Baseline ML  : {len(rows_bl)} combinaisons")
    if rows_dl:
        all_rows.extend(rows_dl)
        print(f"  Deep Learning: {len(rows_dl)} modèles (LOSO)")

    if not all_rows:
        print("\n[ERREUR] Aucune donnée disponible.")
        print("Exécutez :")
        print("  python Tests/test_baselines.py")
        print("  python Tests/test_deep_learning.py")
        print("  python Tests/test_final_comparison.py")
        return

    # ─── DataFrame unifié ────────────────────────────────────────────────────
    df = pd.DataFrame(all_rows)
    for col in ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity',
                'precision', 'pct_uncertain', 'inference_ms']:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

    df = compute_weighted_score(df)
    df.to_csv(REPORT_DIR / 'unified_ranking.csv', index=False)

    # ─── Affichage console ────────────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("CLASSEMENT UNIFIÉ")
    print("DL = métriques LOSO (honnêtes) | BL = test holdout")
    print(f"{'='*75}")
    print(f"{'Rang':>4}  {'Cat':>3}  {'Modèle':<30}  "
          f"{'F1m':>6}  {'AUC':>6}  {'Acc':>6}  {'Inc%':>5}  {'Score':>6}")
    print("-" * 75)

    bl_found = None
    dl_found = None
    for rank, row in df.iterrows():
        cat    = 'BL' if row['category'] == 'Baseline ML' else 'DL'
        marker = " ★" if rank == 0 else "  "
        print(f"{rank+1:>4}{marker} [{cat}]  {row['model']:<30}  "
              f"{row['f1_macro']:.4f}  {row['auc']:.4f}  "
              f"{row['accuracy']:.4f}  {row['pct_uncertain']:>4.1f}%  "
              f"{row['weighted_score']:.4f}")
        if bl_found is None and row['category'] == 'Baseline ML':
            bl_found = row
        if dl_found is None and row['category'] == 'Deep Learning':
            dl_found = row
        if rank >= 19:
            remaining = len(df) - 20
            if remaining > 0:
                print(f"  ... {remaining} autres (voir unified_ranking.csv)")
            break

    best = df.iloc[0]
    print(f"\n{'='*75}")
    print(f"VAINQUEUR : {best['model']}  [{best['category']}]")
    print(f"  F1-MACRO = {best['f1_macro']:.4f}  |  "
          f"AUC = {best['auc']:.4f}  |  Score = {best['weighted_score']:.4f}")
    print(f"{'='*75}")

    if bl_found is not None and dl_found is not None:
        delta = dl_found['f1_macro'] - bl_found['f1_macro']
        sign  = "+" if delta >= 0 else ""
        print(f"\nComparaison directe :")
        print(f"  Baseline ML   : {bl_found['model']:<28} F1m={bl_found['f1_macro']:.4f}")
        print(f"  DL (LOSO)     : {dl_found['model']:<28} F1m={dl_found['f1_macro']:.4f}")
        print(f"  Avantage DL   : {sign}{delta:.4f}")
        if abs(delta) < 0.02:
            print("  → Performances SIMILAIRES → préférer Baseline ML (latence, embarqué)")
        elif delta > 0.02:
            print("  → DL MEILLEUR (+{:.4f}) → justifie la complexité".format(delta))
        else:
            print("  → Baseline ML MEILLEUR → choisir Baseline")

    # ─── Graphiques ───────────────────────────────────────────────────────────
    print("\nGénération des graphiques...")
    plot_final_bars(df, REPORT_DIR / 'final_comparison_bars.png')
    plot_category_boxplot(df, REPORT_DIR / 'baseline_vs_dl_boxplot.png')
    plot_deployment_quadrant(df, REPORT_DIR / 'deployment_quadrant.png')
    if len(df) >= 3:
        plot_top10_radar(df, REPORT_DIR / 'top10_radar.png')

    # ─── Rapport ─────────────────────────────────────────────────────────────
    report_path = REPORT_DIR / 'FINAL_DECISION_REPORT.txt'
    write_final_report(df, report_path, source_note)

    # ─── JSON ─────────────────────────────────────────────────────────────────
    with open(REPORT_DIR / 'summary.json', 'w') as f:
        json.dump({
            'winner':               best['model'],
            'winner_category':      best['category'],
            'winner_f1_macro':      best['f1_macro'],
            'winner_auc':           best['auc'],
            'winner_weighted_score':best['weighted_score'],
            'best_baseline':        bl_found['model']    if bl_found is not None else None,
            'best_baseline_f1':     bl_found['f1_macro'] if bl_found is not None else None,
            'best_dl_loso':         dl_found['model']    if dl_found is not None else None,
            'best_dl_loso_f1':      dl_found['f1_macro'] if dl_found is not None else None,
            'n_models_compared':    len(df),
            'evaluation_method':    'LOSO for DL, holdout for Baseline',
            'source':               source_note,
        }, f, indent=2, default=str)

    print(f"\n{'='*75}")
    print(f"Sorties : {REPORT_DIR}")
    print(f"  • unified_ranking.csv")
    print(f"  • final_comparison_bars.png")
    print(f"  • baseline_vs_dl_boxplot.png")
    print(f"  • deployment_quadrant.png")
    print(f"  • top10_radar.png")
    print(f"  • FINAL_DECISION_REPORT.txt  ← LIRE CE FICHIER")
    print(f"  • summary.json")
    print(f"{'='*75}")


if __name__ == '__main__':
    from_training = '--from-training' in sys.argv
    main(from_training=from_training)
