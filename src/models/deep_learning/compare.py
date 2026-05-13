"""
NeuroCap – Comparaison unifiée des 17 architectures Deep Learning.
Lit les metrics.json de chaque modèle/expérience et génère :
  - Tableau récapitulatif CSV
  - Barplots comparatifs (accuracy, F1-macro, AUC)
  - Heatmaps (modèles × expériences)
  - Classement final pondéré
  - Comparaison temps d'entraînement
"""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_BASE = PROJECT_ROOT / "reports/deep_learning/DL_outputs"
COMPARE_DIR = OUTPUT_BASE / "_comparison"
COMPARE_DIR.mkdir(parents=True, exist_ok=True)

# Toutes les architectures (17)
ALL_MODELS = [
    "CNN1D", "CNN2D", "CNN3D", "EEGNet", "TCN", "CNN_LSTM",
    "LSTM_1L", "LSTM_2L", "BiLSTM_1L", "BiLSTM_2L",
    "GRU_1L", "GRU_2L", "BiGRU_1L", "BiGRU_2L",
    "LSTM_Att", "BiLSTM_Att", "GRU_Att", "BiGRU_Att",
]

EXPERIMENTS = ["A", "B", "C", "D", "FULL"]
METRICS_KEYS = ["accuracy", "f1_macro", "auc", "specificity", "pct_uncertain", "train_time_sec"]


def load_all_metrics():
    """Charge tous les metrics.json disponibles."""
    rows = []
    for model in ALL_MODELS:
        for exp in EXPERIMENTS:
            mf = OUTPUT_BASE / model / f"exp_{exp}" / "metrics.json"
            if mf.exists():
                with open(mf) as f:
                    m = json.load(f)
                m['model'] = model
                m['exp'] = exp
                m['source'] = 'standard'
                rows.append(m)
        
        # LOSO
        lf = OUTPUT_BASE / model / "LOSO_exp_A" / "metrics.json"
        if lf.exists():
            with open(lf) as f:
                m = json.load(f)
            m['model'] = model
            m['exp'] = 'LOSO_A'
            m['source'] = 'LOSO'
            rows.append(m)
    
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
    # Utiliser uniquement l'expérience A (données réelles)
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
    """Compare les temps d'entraînement par famille d'architecture."""
    df_a = df[df['exp'] == 'A'].copy()
    if df_a.empty:
        return
    
    df_a = df_a.sort_values('train_time_sec')
    
    colors = []
    for m in df_a['model']:
        if 'CNN' in m and 'LSTM' not in m and 'GRU' not in m:
            colors.append('#2ecc71')  # CNN = vert
        elif 'EEG' in m:
            colors.append('#3498db')  # EEGNet = bleu
        elif 'TCN' in m:
            colors.append('#9b59b6')  # TCN = violet
        elif 'Att' in m:
            colors.append('#e74c3c')  # Attention = rouge
        elif 'Bi' in m:
            colors.append('#e67e22')  # Bi = orange
        else:
            colors.append('#f39c12')  # RNN = jaune
    
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(df_a['model'], df_a['train_time_sec'], color=colors)
    ax.set_xlabel('Temps d\'entraînement (secondes)')
    ax.set_title('Temps d\'entraînement par architecture (Exp. A)', fontsize=14, fontweight='bold')
    
    for bar, val in zip(bars, df_a['train_time_sec']):
        ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height()/2,
                f'{val:.0f}s', va='center', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(COMPARE_DIR / 'training_times.png', dpi=150, bbox_inches='tight')
    plt.close()


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
    
    # 6. Temps d'entraînement
    plot_training_times(df_std)
    print(f"\n  ⏱️  training_times.png")
    
    # 7. Résumé LOSO
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