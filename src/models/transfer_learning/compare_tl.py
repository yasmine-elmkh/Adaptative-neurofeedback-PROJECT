"""
NeuroCap – Comparaison des 3 stratégies de Transfer Learning
Lit tous les metrics.json et produit :
  1. Tableau Accuracy/F1-macro/AUC par stratégie et expérience
  2. Graphiques en barres groupées
  3. Heatmap F1-macro
  4. Identification de la meilleure stratégie
  5. Sauvegarde CSV
"""

import json
from os import mkdir
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

# ============================================================================
# PARAMÈTRES
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUT_DIR = Path("reports/Comparaison_transfer_learning")
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_BASE = PROJECT_ROOT / "reports/transfer_learning/outputs_tl"
STRATEGIES = ["EEGNet_LayerReplacement", "EEGNet_FullFT", "EEGNet_FeatureExtraction"]
STRAT_LABELS = ["Layer Replacement\n(Olesen 2020)", "Full Fine-Tuning\n(Wan 2021)", "Feature Extraction\n(Prabhakar 2022)"]
STRAT_SHORT = ["LR", "FFT", "FE"]
EXPS = ["A", "B", "C", "D", "FULL"]
COLORS = ['#E74C3C', '#2980B9', '#27AE60']

results = {s: {e: None for e in EXPS} for s in STRATEGIES}

# ============================================================================
# CHARGEMENT
# ============================================================================
print("="*80)
print("NeuroCap – Comparaison Transfer Learning (3 stratégies × 5 expériences)")
print("="*80)

for strat in STRATEGIES:
    for exp in EXPS:
        mf = OUTPUT_BASE / strat / f"exp_{exp}" / "metrics.json"
        if mf.exists():
            with open(mf) as f: results[strat][exp] = json.load(f)
            print(f"✓ {strat} – Exp. {exp}")
        else:
            print(f"✗ {strat} – Exp. {exp} : manquant")

if not any(results[s][e] for s in STRATEGIES for e in EXPS):
    print("\n❌ Aucun résultat. Exécutez d'abord les scripts de TL.")
    exit()

# ============================================================================
# TABLEAUX
# ============================================================================
for metric, title in [('accuracy', 'Accuracy (%)'), ('f1_macro', 'F1-macro'), ('auc', 'AUC')]:
    print(f"\n{'='*80}\n{title}\n{'='*80}")
    print(f"{'Stratégie':<30}", end="")
    for e in EXPS: print(f"{e:>10}", end="")
    print(); print("-"*80)
    for s, sl in zip(STRATEGIES, STRAT_SHORT):
        print(f"{sl:<30}", end="")
        for e in EXPS:
            v = results[s][e][metric] if results[s][e] else 0
            if metric == 'accuracy': print(f"{v*100:9.2f}%", end="")
            else: print(f"{v:10.4f}", end="")
        print()

# Meilleur global
best_f1 = -1; best_s = None; best_e = None
for s in STRATEGIES:
    for e in EXPS:
        if results[s][e] and results[s][e]['f1_macro'] > best_f1:
            best_f1 = results[s][e]['f1_macro']; best_s = s; best_e = e

print(f"\n{'='*80}\n🏆 Meilleur : {best_s} – Exp. {best_e} → F1m={best_f1:.4f}\n{'='*80}")

# Par expérience
print("\nMeilleure stratégie par expérience :")
for e in EXPS:
    bf, bs = -1, None
    for s in STRATEGIES:
        if results[s][e] and results[s][e]['f1_macro'] > bf:
            bf = results[s][e]['f1_macro']; bs = s
    print(f"  Exp. {e} : {bs} ({bf:.4f})")

# ============================================================================
# GRAPHIQUES
# ============================================================================
# 1. F1-macro barplot
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(EXPS)); w = 0.25
for i, (s, c) in enumerate(zip(STRATEGIES, COLORS)):
    vals = [results[s][e]['f1_macro'] if results[s][e] else 0 for e in EXPS]
    bars = ax.bar(x + i*w, vals, w, label=STRAT_LABELS[i].replace('\n',' '), color=c)
    for bar, v in zip(bars, vals):
        if v > 0: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                           f'{v:.3f}', ha='center', va='bottom', fontsize=8)
ax.set_xticks(x + w); ax.set_xticklabels(EXPS)
ax.set_ylabel('F1-macro'); ax.set_title('Comparaison TL – F1-macro')
ax.legend(); ax.grid(axis='y', ls='--', alpha=0.7); ax.set_ylim([0, 1.1])
plt.tight_layout(); plt.savefig(OUT_DIR/"comparison_f1macro_tl.png", dpi=150); plt.close()
print(f"\n📊 comparison_f1macro_tl.png")

# 2. Accuracy barplot
fig, ax = plt.subplots(figsize=(12, 6))
for i, (s, c) in enumerate(zip(STRATEGIES, COLORS)):
    vals = [results[s][e]['accuracy']*100 if results[s][e] else 0 for e in EXPS]
    bars = ax.bar(x + i*w, vals, w, label=STRAT_LABELS[i].replace('\n',' '), color=c)
    for bar, v in zip(bars, vals):
        if v > 0: ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
                           f'{v:.1f}%', ha='center', va='bottom', fontsize=8)
ax.set_xticks(x + w); ax.set_xticklabels(EXPS)
ax.set_ylabel('Accuracy (%)'); ax.set_title('Comparaison TL – Accuracy (%)')
ax.legend(); ax.grid(axis='y', ls='--', alpha=0.7)
plt.tight_layout(); plt.savefig(OUT_DIR/"comparison_accuracy_tl.png", dpi=150); plt.close()
print(f"📊 comparison_accuracy_tl.png")

# 3. Heatmap
f1_matrix = np.zeros((len(STRATEGIES), len(EXPS)))
for i, s in enumerate(STRATEGIES):
    for j, e in enumerate(EXPS):
        f1_matrix[i, j] = results[s][e]['f1_macro'] if results[s][e] else 0
fig, ax = plt.subplots(figsize=(10, 5))
im = ax.imshow(f1_matrix, cmap='YlOrRd', aspect='auto', vmin=0, vmax=1)
ax.set_xticks(range(len(EXPS))); ax.set_yticks(range(len(STRATEGIES)))
ax.set_xticklabels(EXPS); ax.set_yticklabels(STRAT_SHORT)
for i in range(len(STRATEGIES)):
    for j in range(len(EXPS)):
        ax.text(j, i, f"{f1_matrix[i,j]:.3f}", ha="center", va="center",
                color="w" if f1_matrix[i,j]<0.5 else "k")
ax.set_title("Heatmap F1-macro – Transfer Learning")
fig.tight_layout(); plt.savefig(OUT_DIR/"heatmap_f1macro_tl.png", dpi=150); plt.close()
print(f"📊 heatmap_f1macro_tl.png")

# ============================================================================
# CSV
# ============================================================================
for metric in ['accuracy', 'f1_macro', 'auc']:
    df = pd.DataFrame(index=STRAT_SHORT, columns=EXPS)
    for i, s in enumerate(STRATEGIES):
        for e in EXPS:
            v = results[s][e][metric] if results[s][e] else 0
            df.loc[STRAT_SHORT[i], e] = v*100 if metric=='accuracy' else v
    df.to_csv(OUT_DIR / f"comparison_{metric}_tl.csv")
    print(f"📄 comparison_{metric}_tl.csv")

print("\n✅ Comparaison TL terminée.")