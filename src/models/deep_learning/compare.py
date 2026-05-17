"""
NeuroCap – Comparaison unifiée des 17 architectures Deep Learning.
Lit les metrics.json de chaque modèle/expérience et génère :
  - Tableau récapitulatif CSV
  - Barplots comparatifs (accuracy, F1-macro, AUC)
  - Heatmaps (modèles × expériences)
  - Classement final pondéré
  - Comparaison des temps d'entraînement (expérience A seulement ET temps total)
"""

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_BASE = PROJECT_ROOT / "reports/deep_learning"
COMPARE_DIR = OUTPUT_BASE / "comparison"
COMPARE_DIR.mkdir(parents=True, exist_ok=True)

ALL_MODELS = [
    "CNN1D", "CNN2D", "CNN3D", "EEGNet", "TCN", "CNN_LSTM_Att", "CNN_GRU_Att",
    "LSTM_1L", "LSTM_2L", "BiLSTM_1L", "BiLSTM_2L",
    "GRU_1L", "GRU_2L", "BiGRU_1L", "BiGRU_2L",
    "LSTM_Att", "BiLSTM_Att", "GRU_Att", "BiGRU_Att",
]

EXPERIMENTS = ["A", "B", "C", "D", "FULL"]
METRICS_KEYS = ["accuracy", "f1_macro", "auc", "specificity", "pct_uncertain", "train_time_sec"]


def load_all_metrics():
    """Charge tous les metrics.json disponibles, et calcule le temps total par modèle."""
    rows = []
    for model in ALL_MODELS:
        total_time = 0.0
        for exp in EXPERIMENTS:
            mf = OUTPUT_BASE / "DL_outputs" / model / f"exp_{exp}" / "metrics.json"
            if mf.exists():
                with open(mf) as f:
                    m = json.load(f)
                m['model'] = model
                m['exp'] = exp
                m['source'] = 'standard'
                rows.append(m)
                total_time += m.get('train_time_sec', 0)
        # LOSO
        lf = OUTPUT_BASE / "DL_outputs" / model / "LOSO_exp_A" / "metrics.json"
        if lf.exists():
            with open(lf) as f:
                m = json.load(f)
            m['model'] = model
            m['exp'] = 'LOSO_A'
            m['source'] = 'LOSO'
            rows.append(m)
            total_time += m.get('train_time_sec', 0)
        # Sauvegarde temps total
        with open(COMPARE_DIR / f"{model}_total_time.json", "w") as f:
            json.dump({"model": model, "total_time_sec": total_time, "total_time_hours": total_time/3600}, f, indent=2)
    return pd.DataFrame(rows)


def plot_comparison_bars(df, metric, title, filename):
    """Barplot d'une métrique par modèle, coloré par expérience."""
    pivot = df.pivot_table(index='model', columns='exp', values=metric)
    pivot = pivot.reindex(ALL_MODELS).dropna(how='all')
    fig, ax = plt.subplots(figsize=(14, 6))
    pivot.plot(kind='bar', ax=ax, width=0.8)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel(metric.replace('_', ' ').title())
    ax.set_xlabel('')
    ax.legend(title='Expérience', bbox_to_anchor=(1.02, 1))
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / filename, dpi=150, bbox_inches='tight')
    plt.close()


def plot_heatmap(df, metric, title, filename):
    """Heatmap modèles × expériences pour une métrique donnée."""
    pivot = df.pivot_table(index='model', columns='exp', values=metric)
    pivot = pivot.reindex(ALL_MODELS).dropna(how='all')
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='YlOrRd', ax=ax,
                linewidths=0.5, vmin=0.4, vmax=1.0)
    ax.set_title(title, fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / filename, dpi=150, bbox_inches='tight')
    plt.close()


def compute_ranking(df):
    """Classement pondéré : 40% F1-macro + 30% AUC + 20% Accuracy + 10% (1 - incertitude)."""
    df_a = df[df['exp'] == 'A'].copy()
    if df_a.empty:
        df_a = df.copy()
    df_a['score'] = (
        0.40 * df_a['f1_macro'] +
        0.30 * df_a['auc'] +
        0.20 * df_a['accuracy'] +
        0.10 * (1 - df_a['pct_uncertain'] / 100)
    )
    ranking = df_a.sort_values('score', ascending=False)[
        ['model', 'accuracy', 'f1_macro', 'auc', 'specificity',
         'pct_uncertain', 'train_time_sec', 'score']
    ].reset_index(drop=True)
    ranking.index += 1
    ranking.index.name = 'Rang'
    return ranking


def plot_training_times(df):
    """Compare les temps d'entraînement pour l'expérience A SEULE."""
    df_a = df[df['exp'] == 'A'].copy()
    if df_a.empty:
        return
    df_a = df_a.sort_values('train_time_sec')
    colors = []
    for m in df_a['model']:
        if 'CNN' in m and 'LSTM' not in m and 'GRU' not in m:
            colors.append('#2ecc71')
        elif 'EEG' in m:
            colors.append('#3498db')
        elif 'TCN' in m:
            colors.append('#9b59b6')
        elif 'Att' in m:
            colors.append('#e74c3c')
        elif 'Bi' in m:
            colors.append('#e67e22')
        else:
            colors.append('#f39c12')
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(df_a['model'], df_a['train_time_sec'], color=colors)
    ax.set_xlabel("Temps d'entraînement (secondes) – Expérience A uniquement")
    ax.set_title("Temps d'entraînement par architecture (Expérience A)", fontsize=14, fontweight='bold')
    for bar, val in zip(bars, df_a['train_time_sec']):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2, f'{val:.0f}s', va='center', fontsize=9)
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / 'training_times_expA.png', dpi=150, bbox_inches='tight')
    plt.close()


def plot_total_times():
    """Graphique : temps total d'exécution (5 expériences + LOSO) pour chaque modèle."""
    data = []
    for model in ALL_MODELS:
        tf = COMPARE_DIR / f"{model}_total_time.json"
        if tf.exists():
            with open(tf) as f:
                d = json.load(f)
                data.append((d["model"], d["total_time_sec"]))
    if not data:
        print("⚠ Aucun temps total trouvé. Lancez d'abord load_all_metrics().")
        return
    data.sort(key=lambda x: x[1], reverse=True)
    models, times = zip(*data)
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.barh(models, [t/3600 for t in times], color='#3498db')
    ax.set_xlabel("Temps total d'exécution (heures)")
    ax.set_title("Temps total d'exécution par architecture (5 expériences + LOSO)", fontsize=14, fontweight='bold')
    for bar, t in zip(bars, times):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2, f'{t/3600:.1f}h ({t:.0f}s)', va='center', fontsize=9)
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / 'total_execution_time.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  ⏱️  total_execution_time.png généré.")


def main():
    print("=" * 70)
    print("NeuroCap – Comparaison des 17 architectures DL")
    print("=" * 70)
    df = load_all_metrics()
    if df.empty:
        print("⚠ Aucune métrique trouvée. Lancez les entraînements d'abord.")
        return
    print(f"\n{len(df)} résultats chargés ({df['model'].nunique()} modèles, {df['exp'].nunique()} expériences)")
    # 1. CSV complet
    df_export = df[['model', 'exp', 'source'] + METRICS_KEYS].copy()
    df_export.to_csv(COMPARE_DIR / 'all_results.csv', index=False)
    print(f"\n✅ CSV : {COMPARE_DIR / 'all_results.csv'}")
    # 2. Standard experiments only
    df_std = df[df['source'] == 'standard']
    # 3. Barplots
    for metric, title, fname in [
        ('accuracy', 'Accuracy par modèle et expérience', 'barplot_accuracy.png'),
        ('f1_macro', 'F1-macro par modèle et expérience', 'barplot_f1_macro.png'),
        ('auc', 'AUC par modèle et expérience', 'barplot_auc.png'),
    ]:
        plot_comparison_bars(df_std, metric, title, fname)
        print(f"  📊 {fname}")
    # 4. Heatmaps
    for metric, title, fname in [
        ('f1_macro', 'Heatmap F1-macro (modèles × expériences)', 'heatmap_f1_macro.png'),
        ('auc', 'Heatmap AUC (modèles × expériences)', 'heatmap_auc.png'),
    ]:
        plot_heatmap(df_std, metric, title, fname)
        print(f"  🗺️  {fname}")
    # 5. Classement
    ranking = compute_ranking(df_std)
    ranking.to_csv(COMPARE_DIR / 'ranking.csv')
    print(f"\n📋 Classement final (Exp. A) :")
    print(ranking.to_string())
    # 6. Temps d'entraînement – Expérience A
    plot_training_times(df_std)
    print(f"\n  ⏱️  training_times_expA.png")
    # 7. Temps total (5 expériences + LOSO)
    plot_total_times()
    # 8. Résumé LOSO
    df_loso = df[df['source'] == 'LOSO']
    if not df_loso.empty:
        print(f"\n📋 Résultats LOSO (Exp. A) :")
        loso_summary = df_loso[['model', 'accuracy', 'f1_macro', 'auc', 'specificity', 'train_time_sec']]
        loso_summary = loso_summary.sort_values('f1_macro', ascending=False)
        print(loso_summary.to_string(index=False))
        loso_summary.to_csv(COMPARE_DIR / 'loso_results.csv', index=False)
    print(f"\n✅ Tous les résultats dans : {COMPARE_DIR}")


if __name__ == '__main__':
    main()