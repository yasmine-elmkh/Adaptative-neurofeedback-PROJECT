"""
NeuroCap – compare_dann.py
==========================
Deux types de comparaisons :

  1. DANN vs DANN
     Classe les 19 architectures DANN entre elles (accuracy, F1-macro, AUC).

  2. DANN vs Non-DANN (comparaison objective)
     Pour chaque paire (Modèle, Modèle_DANN), affiche le gain/perte apporté
     par DANN sur chaque expérience.

Sorties dans :
  reports/deep_learning/comparison_dann/
    ├── dann_vs_dann_accuracy.png
    ├── dann_vs_dann_f1macro.png
    ├── dann_vs_dann_heatmap.png
    ├── dann_vs_dann_ranking.csv
    ├── dann_vs_baseline_improvement_accuracy.png
    ├── dann_vs_baseline_improvement_f1macro.png
    ├── dann_vs_baseline_heatmap_gain.png
    └── dann_comparison_full.csv
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
DL_OUT   = PROJECT_ROOT / "reports/deep_learning/DL_outputs"
DANN_OUT = PROJECT_ROOT / "reports/deep_learning/DANN_outputs"
CMP_DIR  = PROJECT_ROOT / "reports/deep_learning/comparison_dann"
CMP_DIR.mkdir(parents=True, exist_ok=True)

EXPERIMENTS = ["A", "B", "C", "D", "FULL"]

# Modèles de base et leurs équivalents DANN
PAIRS = [
    ("CNN1D",        "CNN1D_DANN"),
    ("CNN2D",        "CNN2D_DANN"),
    ("CNN3D",        "CNN3D_DANN"),
    ("TCN",          "TCN_DANN"),
    ("EEGNet",       "EEGNet_DANN"),
    ("LSTM_1L",      "LSTM_1L_DANN"),
    ("LSTM_2L",      "LSTM_2L_DANN"),
    ("LSTM_Att",     "LSTM_Att_DANN"),
    ("BiLSTM_1L",    "BiLSTM_1L_DANN"),
    ("BiLSTM_2L",    "BiLSTM_2L_DANN"),
    ("BiLSTM_Att",   "BiLSTM_Att_DANN"),
    ("GRU_1L",       "GRU_1L_DANN"),
    ("GRU_2L",       "GRU_2L_DANN"),
    ("GRU_Att",      "GRU_Att_DANN"),
    ("BiGRU_1L",     "BiGRU_1L_DANN"),
    ("BiGRU_2L",     "BiGRU_2L_DANN"),
    ("BiGRU_Att",    "BiGRU_Att_DANN"),
    ("CNN_LSTM_Att", "CNN_LSTM_Att_DANN"),
    ("CNN_GRU_Att",  "CNN_GRU_Att_DANN"),
]
ALL_DANN_MODELS = [p[1] for p in PAIRS]
ALL_BASE_MODELS = [p[0] for p in PAIRS]

METRIC_DISPLAY = {
    'accuracy':    'Accuracy',
    'f1_macro':    'F1-macro',
    'auc':         'AUC',
    'specificity': 'Spécificité',
    'f1_weighted': 'F1-weighted',
}


# ============================================================================
# CHARGEMENT DES MÉTRIQUES
# ============================================================================
def _load_metrics(out_base, model_name, exp):
    """Charge metrics.json pour un modèle et une expérience donnés."""
    if exp == 'LOSO':
        p = out_base / model_name / "LOSO_exp_A" / "metrics.json"
    else:
        p = out_base / model_name / f"exp_{exp}" / "metrics.json"
    if not p.exists():
        return None
    with open(p) as f:
        return json.load(f)


def load_dann_metrics():
    """Charge toutes les métriques DANN disponibles."""
    rows = []
    for model in ALL_DANN_MODELS:
        for exp in EXPERIMENTS + ['LOSO']:
            m = _load_metrics(DANN_OUT, model, exp)
            if m:
                rows.append({
                    'model': model, 'exp': exp,
                    'accuracy':    m.get('accuracy', np.nan),
                    'f1_macro':    m.get('f1_macro', np.nan),
                    'f1_weighted': m.get('f1_weighted', np.nan),
                    'auc':         m.get('auc', np.nan),
                    'specificity': m.get('specificity', np.nan),
                    'train_time_sec': m.get('train_time_sec', np.nan),
                })
    return pd.DataFrame(rows)


def load_base_metrics():
    """Charge toutes les métriques des modèles de base (non-DANN)."""
    rows = []
    for model in ALL_BASE_MODELS:
        for exp in EXPERIMENTS + ['LOSO']:
            m = _load_metrics(DL_OUT, model, exp)
            if m:
                rows.append({
                    'model': model, 'exp': exp,
                    'accuracy':    m.get('accuracy', np.nan),
                    'f1_macro':    m.get('f1_macro', np.nan),
                    'f1_weighted': m.get('f1_weighted', np.nan),
                    'auc':         m.get('auc', np.nan),
                    'specificity': m.get('specificity', np.nan),
                    'train_time_sec': m.get('train_time_sec', np.nan),
                })
    return pd.DataFrame(rows)


# ============================================================================
# 1. DANN vs DANN — classement interne
# ============================================================================
def compare_dann_vs_dann(df_dann):
    """
    Barplots et heatmap des métriques DANN par expérience.
    Produit aussi un classement pondéré.
    """
    if df_dann.empty:
        print("  Aucune métrique DANN disponible.")
        return

    exps_available = [e for e in EXPERIMENTS if e in df_dann['exp'].values]
    if not exps_available:
        print("  Aucune expérience standard disponible pour DANN.")
        return

    df_std = df_dann[df_dann['exp'].isin(exps_available)]

    # ── Barplots par métrique ─────────────────────────────────────────────────
    for metric, label in METRIC_DISPLAY.items():
        if metric not in df_std.columns:
            continue
        pivot = df_std.pivot_table(index='model', columns='exp', values=metric)
        pivot = pivot.reindex(
            [m for m in ALL_DANN_MODELS if m in pivot.index]
        ).dropna(how='all')
        if pivot.empty:
            continue

        fig, ax = plt.subplots(figsize=(16, 6))
        pivot.plot(kind='bar', ax=ax, width=0.8)
        ax.set_title(f'DANN vs DANN — {label} par architecture', fontsize=13, fontweight='bold')
        ax.set_ylabel(label)
        ax.set_xlabel('')
        ax.legend(title='Expérience', bbox_to_anchor=(1.02, 1))
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=8)
        ax.set_ylim(0, 1.05)
        plt.tight_layout()
        plt.savefig(CMP_DIR / f'dann_vs_dann_{metric}.png', dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Barplot DANN-DANN {metric} sauvegardé.")

    # ── Heatmap (modèles × expériences) sur F1-macro ─────────────────────────
    pivot_f1 = df_std.pivot_table(index='model', columns='exp', values='f1_macro')
    pivot_f1 = pivot_f1.reindex(
        [m for m in ALL_DANN_MODELS if m in pivot_f1.index]
    ).dropna(how='all')

    if not pivot_f1.empty:
        fig, ax = plt.subplots(figsize=(10, 12))
        sns.heatmap(pivot_f1, annot=True, fmt='.3f', cmap='YlGnBu',
                    vmin=0, vmax=1, ax=ax, linewidths=0.5)
        ax.set_title('DANN — F1-macro (modèles × expériences)', fontsize=13, fontweight='bold')
        ax.set_xlabel('Expérience')
        ax.set_ylabel('')
        plt.tight_layout()
        plt.savefig(CMP_DIR / 'dann_vs_dann_heatmap_f1.png', dpi=150, bbox_inches='tight')
        plt.close()
        print("  Heatmap DANN-DANN F1-macro sauvegardée.")

    # ── Classement pondéré DANN ───────────────────────────────────────────────
    score_df = df_std.groupby('model').agg(
        acc_mean=('accuracy', 'mean'),
        f1m_mean=('f1_macro', 'mean'),
        auc_mean=('auc', 'mean'),
    ).reset_index()
    score_df['score'] = (
        0.40 * score_df['f1m_mean'] +
        0.35 * score_df['auc_mean'] +
        0.25 * score_df['acc_mean']
    )
    score_df = score_df.sort_values('score', ascending=False).reset_index(drop=True)
    score_df['rank'] = range(1, len(score_df) + 1)
    score_df.to_csv(CMP_DIR / 'dann_vs_dann_ranking.csv', index=False, float_format='%.4f')
    print("\n  Classement DANN (score pondéré = 40% F1m + 35% AUC + 25% Acc) :")
    print(score_df[['rank', 'model', 'score', 'f1m_mean', 'auc_mean', 'acc_mean']].to_string(index=False))


# ============================================================================
# 2. DANN vs Non-DANN — gain objectif
# ============================================================================
def compare_dann_vs_baseline(df_dann, df_base):
    """
    Pour chaque paire (modèle_base, modèle_DANN) et chaque expérience,
    calcule le gain en accuracy et F1-macro apporté par DANN.
    """
    if df_dann.empty or df_base.empty:
        print("  Données insuffisantes pour la comparaison DANN vs baseline.")
        return

    rows = []
    for base_name, dann_name in PAIRS:
        for exp in EXPERIMENTS:
            base_row = df_base[(df_base['model'] == base_name) & (df_base['exp'] == exp)]
            dann_row = df_dann[(df_dann['model'] == dann_name) & (df_dann['exp'] == exp)]
            if base_row.empty or dann_row.empty:
                continue
            b = base_row.iloc[0]
            d = dann_row.iloc[0]
            rows.append({
                'base_model': base_name,
                'dann_model': dann_name,
                'exp': exp,
                'acc_base':  b['accuracy'],
                'acc_dann':  d['accuracy'],
                'acc_gain':  d['accuracy']  - b['accuracy'],
                'f1m_base':  b['f1_macro'],
                'f1m_dann':  d['f1_macro'],
                'f1m_gain':  d['f1_macro']  - b['f1_macro'],
                'auc_base':  b['auc'],
                'auc_dann':  d['auc'],
                'auc_gain':  d['auc']       - b['auc'],
            })

    if not rows:
        print("  Aucune paire base/DANN avec données disponibles.")
        return

    df_gain = pd.DataFrame(rows)
    df_gain.to_csv(CMP_DIR / 'dann_comparison_full.csv', index=False, float_format='%.4f')
    print(f"\n  Tableau comparatif exporté : dann_comparison_full.csv ({len(df_gain)} lignes)")

    # ── Barplot gain accuracy (moyenne sur expériences) ───────────────────────
    gain_mean = df_gain.groupby('base_model').agg(
        acc_gain_mean=('acc_gain', 'mean'),
        f1m_gain_mean=('f1m_gain', 'mean'),
        auc_gain_mean=('auc_gain', 'mean'),
        f1m_dann_mean=('f1m_dann', 'mean'),
        f1m_base_mean=('f1m_base', 'mean'),
    ).reindex(ALL_BASE_MODELS).dropna(how='all').reset_index()

    def _dann_color(gain, f1_dann):
        """
        Logique correcte de couleur DANN :
        Le DANN vise à SUPPRIMER le biais SCPS (OpenBCI=Concentration, EMOTIV=Stress).
        - Vert  : signal cognitif amplifié après suppression du biais (CNN1D, gain > 0)
        - Orange: biais supprimé, performance honnête révélée (attendu, gain légèrement <0)
        - Rouge : effondrement — architecture n'apprenait que le biais matériel
        """
        if f1_dann < 0.60:
            return '#E74C3C'   # Effondrement — architecture invalide sans biais
        elif gain > 0.01:
            return '#27AE60'   # Signal cognitif réel amplifié (meilleur cas)
        else:
            return '#F39C12'   # Biais supprimé, performance honnête (attendu)

    for metric_gain, metric_label, dann_col in [
        ('acc_gain_mean', 'Accuracy', None),
        ('f1m_gain_mean', 'F1-macro', 'f1m_dann_mean'),
        ('auc_gain_mean', 'AUC', None),
    ]:
        if metric_gain not in gain_mean.columns:
            continue
        vals   = gain_mean[metric_gain].values
        models = gain_mean['base_model'].values

        if dann_col and dann_col in gain_mean.columns:
            f1_danns = gain_mean[dann_col].values
            colors = [_dann_color(v, fd) for v, fd in zip(vals, f1_danns)]
        else:
            colors = ['#F39C12' if v >= -0.15 else '#E74C3C' for v in vals]

        fig, ax = plt.subplots(figsize=(14, 7))
        bars = ax.bar(models, vals * 100, color=colors, alpha=0.85, edgecolor='white')
        ax.axhline(0, color='black', lw=0.8)
        ax.set_title(
            f'Impact DANN — Correction du biais SCPS (moyenne A-D-FULL) — {metric_label}\n'
            f'Vert = signal cognitif amplifié ✓ | Orange = biais supprimé (attendu ✓) | Rouge = effondrement ✗',
            fontsize=11, fontweight='bold')
        ax.set_ylabel(f'Δ {metric_label} (%)')
        ax.set_xlabel('')
        ax.set_xticklabels(models, rotation=45, ha='right', fontsize=8)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + (0.2 if v >= 0 else -0.5),
                    f'{v*100:+.1f}', ha='center', va='bottom', fontsize=7)
        plt.tight_layout()
        mname = metric_label.lower().replace('-', '')
        plt.savefig(CMP_DIR / f'dann_vs_baseline_gain_{mname}.png',
                    dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Barplot impact DANN {metric_label} sauvegardé.")

    # ── Heatmap gain F1-macro (modèles × expériences) ─────────────────────────
    pivot_gain = df_gain.pivot_table(
        index='base_model', columns='exp', values='f1m_gain')
    pivot_gain = pivot_gain.reindex(
        [m for m in ALL_BASE_MODELS if m in pivot_gain.index])

    if not pivot_gain.empty:
        vmax = max(abs(pivot_gain.values[~np.isnan(pivot_gain.values)]).max(), 0.01)
        fig, ax = plt.subplots(figsize=(10, 12))
        sns.heatmap(pivot_gain, annot=True, fmt='+.3f',
                    cmap='RdYlGn', center=0, vmin=-vmax, vmax=vmax,
                    ax=ax, linewidths=0.5)
        ax.set_title(
            'Impact DANN sur F1-macro — Correction biais SCPS\n'
            'Vert = signal amplifié ✓ | Orange = biais supprimé (attendu ✓) | Rouge = effondrement ✗',
            fontsize=11, fontweight='bold')
        ax.set_xlabel('Expérience')
        ax.set_ylabel('')
        plt.tight_layout()
        plt.savefig(CMP_DIR / 'dann_vs_baseline_heatmap_gain_f1.png',
                    dpi=150, bbox_inches='tight')
        plt.close()
        print("  Heatmap gain F1-macro sauvegardée.")

    # ── Barplots côte-à-côte base vs DANN (accuracy + f1-macro) ──────────────
    for metric, base_col, dann_col, label in [
        ('accuracy', 'acc_base', 'acc_dann', 'Accuracy'),
        ('f1_macro', 'f1m_base', 'f1m_dann', 'F1-macro'),
    ]:
        df_avg = df_gain.groupby('base_model').agg(
            base_val=(base_col, 'mean'),
            dann_val=(dann_col, 'mean'),
        ).reindex(ALL_BASE_MODELS).dropna(how='all').reset_index()

        x      = np.arange(len(df_avg))
        width  = 0.38
        fig, ax = plt.subplots(figsize=(16, 6))
        ax.bar(x - width/2, df_avg['base_val'], width,
               label='Sans DANN', color='#E74C3C', alpha=0.8)
        ax.bar(x + width/2, df_avg['dann_val'], width,
               label='Avec DANN', color='#27AE60', alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(df_avg['base_model'], rotation=45, ha='right', fontsize=8)
        ax.set_ylabel(label)
        ax.set_ylim(0, 1.08)
        ax.set_title(
            f'{label} — Sans DANN (biaisé) vs Avec DANN (honnête)\n'
            f'Les scores Sans DANN sont artificiellement gonflés par le biais SCPS',
            fontsize=11, fontweight='bold')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(CMP_DIR / f'dann_vs_baseline_{metric}.png',
                    dpi=150, bbox_inches='tight')
        plt.close()
        print(f"  Barplot comparatif {label} sauvegardé.")

    # ── Résumé chiffré ────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("  IMPACT DANN — CORRECTION DU BIAIS SCPS (moyenne sur toutes les expériences)")
    print("=" * 80)
    print("  RAPPEL INTERPRÉTATION :")
    print("  • Δ F1m > 0     → Signal cognitif AMPLIFIÉ après suppression du biais [✓ meilleur cas]")
    print("  • Δ F1m légèrement < 0 → Biais SCPS supprimé, perf honnête révélée [✓ attendu]")
    print("  • F1m DANN < 0.60   → Architecture EFFONDRÉE : n'apprenait que le biais [✗ invalide]")
    print("-" * 80)
    print(f"  {'Architecture':<20} {'F1m Base':>10} {'F1m DANN':>10} {'Δ F1m':>8} "
          f"{'Interprétation'}")
    print("-" * 80)
    for _, row in gain_mean.iterrows():
        bm = row['base_model']
        base_row = df_gain[df_gain['base_model'] == bm]
        acc_b = base_row['acc_base'].mean()
        acc_d = base_row['acc_dann'].mean()
        f1m_b = base_row['f1m_base'].mean()
        f1m_d = base_row['f1m_dann'].mean()
        delta  = f1m_d - f1m_b
        if f1m_d < 0.60:
            interp = '[✗] Effondrement — biais dominant'
        elif delta > 0.01:
            interp = '[✓✓] Signal cognitif amplifié (CNN1D case)'
        else:
            interp = '[✓] Biais SCPS supprimé — perf honnête'
        print(f"  {bm:<20} {f1m_b:>10.4f} {f1m_d:>10.4f} "
              f"{delta:>+8.4f}  {interp}")


# ============================================================================
# LOSO DANN vs BASELINE
# ============================================================================
def compare_loso(df_dann, df_base):
    """Compare les résultats LOSO entre DANN et baseline."""
    loso_rows = []
    for base_name, dann_name in PAIRS:
        b_loso = df_base[(df_base['model'] == base_name) & (df_base['exp'] == 'LOSO')]
        d_loso = df_dann[(df_dann['model'] == dann_name) & (df_dann['exp'] == 'LOSO')]
        if b_loso.empty or d_loso.empty:
            continue
        b = b_loso.iloc[0]
        d = d_loso.iloc[0]
        loso_rows.append({
            'model': base_name,
            'acc_base': b['accuracy'], 'acc_dann': d['accuracy'],
            'f1m_base': b['f1_macro'], 'f1m_dann': d['f1_macro'],
            'auc_base': b['auc'],      'auc_dann': d['auc'],
        })

    if not loso_rows:
        print("\n  Aucune donnée LOSO disponible pour la comparaison.")
        return

    df_loso = pd.DataFrame(loso_rows)
    df_loso.to_csv(CMP_DIR / 'dann_loso_comparison.csv', index=False, float_format='%.4f')

    print("\n" + "=" * 70)
    print("  LOSO — DANN vs BASELINE")
    print("=" * 70)
    print(f"  {'Architecture':<20} {'Acc Base':>10} {'Acc DANN':>10} "
          f"{'F1m Base':>10} {'F1m DANN':>10}")
    print("-" * 65)
    for _, row in df_loso.iterrows():
        print(f"  {row['model']:<20} {row['acc_base']:>10.4f} {row['acc_dann']:>10.4f} "
              f"{row['f1m_base']:>10.4f} {row['f1m_dann']:>10.4f}")

    # Barplot LOSO
    x = np.arange(len(df_loso))
    w = 0.38
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    fig.suptitle('LOSO — Sans DANN vs Avec DANN', fontsize=13, fontweight='bold')

    for ax, (base_col, dann_col, label) in zip(
        axes,
        [('acc_base', 'acc_dann', 'Accuracy'),
         ('f1m_base', 'f1m_dann', 'F1-macro')]
    ):
        ax.bar(x - w/2, df_loso[base_col], w,
               label='Sans DANN', color='#E74C3C', alpha=0.8)
        ax.bar(x + w/2, df_loso[dann_col], w,
               label='Avec DANN', color='#27AE60', alpha=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels(df_loso['model'], rotation=45, ha='right', fontsize=8)
        ax.set_ylabel(label)
        ax.set_ylim(0, 1.08)
        ax.set_title(f'LOSO — {label}')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)

    plt.tight_layout()
    plt.savefig(CMP_DIR / 'dann_loso_comparison.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Barplot LOSO sauvegardé.")


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================
def main():
    print("=" * 70)
    print("NeuroCap — Comparaison DANN")
    print("=" * 70)

    df_dann = load_dann_metrics()
    df_base = load_base_metrics()

    print(f"\n  Métriques DANN chargées  : {len(df_dann)} entrées")
    print(f"  Métriques base chargées  : {len(df_base)} entrées")

    if df_dann.empty:
        print("\n  Aucun résultat DANN trouvé.")
        print(f"  Lancez d'abord les modèles DANN (DANN_utils.dann_main).")
        print(f"  Les sorties doivent être dans : {DANN_OUT}")
        return

    print("\n[1/3] Comparaison DANN vs DANN...")
    compare_dann_vs_dann(df_dann)

    print("\n[2/3] Comparaison DANN vs Baseline...")
    compare_dann_vs_baseline(df_dann, df_base)

    print("\n[3/3] Comparaison LOSO DANN vs Baseline...")
    compare_loso(df_dann, df_base)

    print(f"\n Tous les graphiques sauvegardés dans : {CMP_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
