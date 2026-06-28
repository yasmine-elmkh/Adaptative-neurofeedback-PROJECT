"""
NeuroCap – Comparaison des 3 stratégies de Transfer Learning (RÉGRESSION)
=========================================================================
Lit les metrics.json de chaque stratégie × cible × expérience et produit :
  1. Tableaux MAE / R² / AUC par stratégie et expérience (conc + stress)
  2. Graphiques en barres groupées
  3. Heatmaps MAE et R²
  4. Identification de la meilleure stratégie
  5. Sauvegarde CSV

Chemins attendus :
  reports/Regression/TL/{stratégie}/{target}/{exp}/metrics.json
"""

import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
from pathlib import Path

# ── Paramètres ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]

OUTPUT_BASE = PROJECT_ROOT / "reports" / "Regression" / "TL"
OUT_DIR     = PROJECT_ROOT / "reports" / "Regression" / "TL" /"Comparaison_TL"
OUT_DIR.mkdir(parents=True, exist_ok=True)

STRATEGIES   = ["EEGNet_LayerReplacement", "EEGNet_FullFT", "EEGNet_FeatureExtraction"]
STRAT_LABELS = [
    "Layer Replacement\n(Olesen 2020)",
    "Full Fine-Tuning\n(Wan 2021)",
    "Feature Extraction\n(Prabhakar 2022)",
]
STRAT_SHORT  = ["LR", "FFT", "FE"]
TARGETS      = ["conc", "stress"]
EXPS         = ["A", "B", "C", "D", "FULL"]
COLORS       = ['#E74C3C', '#2980B9', '#27AE60']

# ── Chargement ─────────────────────────────────────────────────────────────────
print("=" * 80)
print("NeuroCap – Comparaison Transfer Learning Régression (3 stratégies × 2 cibles × 5 exp.)")
print("=" * 80)

# results[target][strat][exp] = dict métriques ou None
results = {t: {s: {e: None for e in EXPS} for s in STRATEGIES} for t in TARGETS}

for target in TARGETS:
    for strat in STRATEGIES:
        for exp in EXPS:
            mf = OUTPUT_BASE / strat / target / exp / "metrics.json"
            if mf.exists():
                with open(mf) as f:
                    results[target][strat][exp] = json.load(f)
                print(f"✓ {strat} – {target.upper()} – Exp. {exp}")
            else:
                print(f"✗ {strat} – {target.upper()} – Exp. {exp} : manquant")

any_result = any(
    results[t][s][e] for t in TARGETS for s in STRATEGIES for e in EXPS
)
if not any_result:
    print("\n❌ Aucun résultat. Exécutez d'abord les scripts TL régression.")
    import sys; sys.exit()

# ── Tableaux texte ─────────────────────────────────────────────────────────────
for target in TARGETS:
    print(f"\n{'='*80}")
    print(f"CIBLE : {target.upper()}")
    print(f"{'='*80}")

    for metric, title in [
        ('mae',         'MAE (↓ meilleur)'),
        ('r2',          'R² (↑ meilleur)'),
        ('auc_roc',     'AUC-ROC (↑ meilleur)'),
        ('sensitivity', 'Sensitivity (↑ meilleur)'),
        ('specificity', 'Specificity (↑ meilleur)'),
        ('mcc',         'MCC (↑ meilleur)'),
    ]:
        print(f"\n  {title}")
        print(f"  {'Stratégie':<12}", end="")
        for e in EXPS:
            print(f"{e:>10}", end="")
        print()
        print("  " + "-" * 62)
        for s, sl in zip(STRATEGIES, STRAT_SHORT):
            print(f"  {sl:<12}", end="")
            for e in EXPS:
                v = results[target][s][e].get(metric, 0) if results[target][s][e] else 0
                print(f"{v:10.4f}", end="")
            print()

# ── Meilleur global ────────────────────────────────────────────────────────────
def _composite_tl(r):
    """Score composite : AUC(40%) + Sensitivity(30%) + MCC(20%) + Specificity(10%)."""
    if r is None:
        return -999.
    return (0.40 * r.get('auc_roc', 0)
          + 0.30 * r.get('sensitivity', 0)
          + 0.20 * r.get('mcc', 0)
          + 0.10 * r.get('specificity', 0))

print(f"\n{'='*80}")
print("MEILLEURS RÉSULTATS — Score composite (AUC×0.4 + Sens×0.3 + MCC×0.2 + Spec×0.1)")
print(f"{'='*80}")
for target in TARGETS:
    best_score = -999; best_s = None; best_e = None
    for s in STRATEGIES:
        for e in EXPS:
            sc = _composite_tl(results[target][s][e])
            if sc > best_score:
                best_score, best_s, best_e = sc, s, e
    r = results[target][best_s][best_e] if best_s else {}
    print(f"  {target.upper()} → {best_s} – Exp. {best_e}")
    if r:
        print(f"    Score={best_score:.4f}  AUC={r.get('auc_roc',0):.4f}  "
              f"Sens={r.get('sensitivity',0):.4f}  Spec={r.get('specificity',0):.4f}  "
              f"MCC={r.get('mcc',0):.4f}  R²={r.get('r2',0):.4f}")

print()
for target in TARGETS:
    print(f"\n  {target.upper()} — Meilleure stratégie par expérience (score composite) :")
    for e in EXPS:
        best_sc, best_s = -999, None
        for s in STRATEGIES:
            sc = _composite_tl(results[target][s][e])
            if sc > best_sc:
                best_sc, best_s = sc, s
        if best_s:
            r     = results[target][best_s][e]
            short = STRAT_SHORT[STRATEGIES.index(best_s)]
            print(f"    Exp. {e} : {short}  score={best_sc:.4f}  "
                  f"AUC={r.get('auc_roc',0):.4f}  Sens={r.get('sensitivity',0):.4f}  "
                  f"MCC={r.get('mcc',0):.4f}")


# ── Graphiques ─────────────────────────────────────────────────────────────────
def _barplot(metric: str, ylabel: str, title_suffix: str, filename: str, target: str):
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(EXPS))
    w = 0.25
    for i, (s, c) in enumerate(zip(STRATEGIES, COLORS)):
        vals = [
            results[target][s][e].get(metric, 0) if results[target][s][e] else 0
            for e in EXPS
        ]
        bars = ax.bar(x + i * w, vals, w,
                      label=STRAT_LABELS[i].replace('\n', ' '), color=c, alpha=0.85)
        for bar, v in zip(bars, vals):
            if v != 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + (0.002 if metric != 'mae' else 0.005),
                        f'{v:.3f}', ha='center', va='bottom', fontsize=7)
    ax.set_xticks(x + w)
    ax.set_xticklabels(EXPS)
    ax.set_ylabel(ylabel)
    ax.set_title(f'Comparaison TL Régression – {target.upper()} – {title_suffix}')
    ax.legend()
    ax.grid(axis='y', ls='--', alpha=0.4)
    plt.tight_layout()
    plt.savefig(OUT_DIR / filename, dpi=150)
    plt.close()
    print(f"📊 {filename}")


def _heatmap(metric: str, title: str, filename: str, target: str):
    matrix = np.zeros((len(STRATEGIES), len(EXPS)))
    for i, s in enumerate(STRATEGIES):
        for j, e in enumerate(EXPS):
            if results[target][s][e]:
                matrix[i, j] = results[target][s][e].get(metric, 0)
    fig, ax = plt.subplots(figsize=(10, 4))
    cmap = 'RdYlGn_r' if metric == 'mae' else 'RdYlGn'
    im = ax.imshow(matrix, cmap=cmap, aspect='auto', vmin=matrix.min(), vmax=matrix.max())
    ax.set_xticks(range(len(EXPS)))
    ax.set_yticks(range(len(STRATEGIES)))
    ax.set_xticklabels(EXPS)
    ax.set_yticklabels(STRAT_SHORT)
    plt.colorbar(im, ax=ax)
    for i in range(len(STRATEGIES)):
        for j in range(len(EXPS)):
            ax.text(j, i, f"{matrix[i, j]:.3f}", ha="center", va="center", fontsize=9,
                    color="white" if matrix[i, j] < (matrix.min() + matrix.max()) / 2 else "black")
    ax.set_title(f"Heatmap {title} – TL Régression – {target.upper()}")
    plt.tight_layout()
    plt.savefig(OUT_DIR / filename, dpi=150)
    plt.close()
    print(f"📊 {filename}")


for target in TARGETS:
    _barplot('mae',         'MAE (↓)',         'MAE',         f'comparison_mae_{target}.png',         target)
    _barplot('r2',          'R²  (↑)',          'R²',          f'comparison_r2_{target}.png',          target)
    _barplot('auc_roc',     'AUC-ROC (↑)',      'AUC-ROC',     f'comparison_auc_{target}.png',         target)
    _barplot('sensitivity', 'Sensitivity (↑)',  'Sensitivity', f'comparison_sensitivity_{target}.png', target)
    _barplot('specificity', 'Specificity (↑)',  'Specificity', f'comparison_specificity_{target}.png', target)
    _barplot('mcc',         'MCC (↑)',          'MCC',         f'comparison_mcc_{target}.png',         target)
    _heatmap('mae',         'MAE',      f'heatmap_mae_{target}.png',         target)
    _heatmap('r2',          'R²',       f'heatmap_r2_{target}.png',          target)
    _heatmap('auc_roc',     'AUC-ROC',  f'heatmap_auc_{target}.png',         target)
    _heatmap('sensitivity', 'Sensitivity', f'heatmap_sensitivity_{target}.png', target)
    _heatmap('mcc',         'MCC',      f'heatmap_mcc_{target}.png',         target)

# ── Graphique multi-cibles : MAE + R² côte à côte ─────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Comparaison Transfer Learning Régression – Toutes cibles', fontsize=13, fontweight='bold')
x = np.arange(len(EXPS)); w = 0.25

for row, target in enumerate(TARGETS):
    for col, (metric, ylabel) in enumerate([('mae', 'MAE (↓)'), ('r2', 'R² (↑)')]):
        ax = axes[row][col]
        for i, (s, c) in enumerate(zip(STRATEGIES, COLORS)):
            vals = [
                results[target][s][e].get(metric, 0) if results[target][s][e] else 0
                for e in EXPS
            ]
            ax.bar(x + i * w, vals, w,
                   label=STRAT_SHORT[i], color=c, alpha=0.85)
        ax.set_xticks(x + w)
        ax.set_xticklabels(EXPS, fontsize=9)
        ax.set_ylabel(ylabel)
        ax.set_title(f'{target.upper()} – {ylabel}', fontweight='bold')
        ax.legend(fontsize=8)
        ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(OUT_DIR / 'comparison_all_targets.png', dpi=150)
plt.close()
print("📊 comparison_all_targets.png")

# ── CSV ────────────────────────────────────────────────────────────────────────
rows = []
for target in TARGETS:
    for i, s in enumerate(STRATEGIES):
        for e in EXPS:
            r = results[target][s][e]
            rows.append({
                'target':   target,
                'strategy': STRAT_SHORT[i],
                'exp':      e,
                'mae':              r.get('mae', None)              if r else None,
                'rmse':             r.get('rmse', None)             if r else None,
                'r2':               r.get('r2', None)               if r else None,
                'auc_roc':          r.get('auc_roc', None)          if r else None,
                'sensitivity':      r.get('sensitivity', None)      if r else None,
                'specificity':      r.get('specificity', None)      if r else None,
                'mcc':              r.get('mcc', None)              if r else None,
                'balanced_accuracy':r.get('balanced_accuracy', None) if r else None,
                'ece':      (r.get('calibration') or {}).get('ece', None)      if r else None,
                'icc':      (r.get('icc') or {}).get('icc', None)              if r else None,
                'loa_width':(r.get('bland_altman') or {}).get('loa_width', None) if r else None,
                'composite':        _composite_tl(r)                if r else None,
            })

df = pd.DataFrame(rows)
df.to_csv(OUT_DIR / 'comparison_tl_regression.csv', index=False)
print("📄 comparison_tl_regression.csv")


# ── Dashboard de décision TL ────────────────────────────────────────────────
_TL_DECISION = [
    ('auc_roc',           'AUC ROC',          0.65, 0.55),
    ('sensitivity',       'Sensitivity',       0.50, 0.40),
    ('specificity',       'Specificity',        0.50, 0.40),
    ('mcc',               'MCC',               0.20, 0.10),
    ('balanced_accuracy', 'Balanced Accuracy', 0.65, 0.55),
]

def _bc(v, g, b):
    if v >= g:  return '#27AE60'
    if v >= b:  return '#F39C12'
    return '#E74C3C'


def plot_decision_dashboard_tl(target):
    """
    Dashboard décision TL : 3 stratégies × 5 métriques + tableau pass/fail.
    Utilise l'expérience FULL si disponible, sinon la meilleure disponible.
    """
    # Choisir la meilleure expérience disponible
    exp_ref = None
    for e in ['FULL', 'D', 'C', 'B', 'A']:
        if any(results[target][s][e] for s in STRATEGIES):
            exp_ref = e
            break
    if exp_ref is None:
        print(f"  [SKIP] decision_dashboard_tl_{target}.png — aucun résultat")
        return

    fig = plt.figure(figsize=(20, 13))
    gs  = fig.add_gridspec(2, 5, height_ratios=[1.6, 1.0],
                           hspace=0.55, wspace=0.38,
                           top=0.88, bottom=0.04, left=0.05, right=0.97)
    fig.suptitle(
        f'Dashboard Décision — Transfer Learning (3 stratégies)  |  {target.upper()}  |  Exp. {exp_ref}\n'
        f'Ordre priorité : AUC (GO/NO-GO)  →  Sensitivity  →  MCC  →  Décision finale',
        fontsize=13, fontweight='bold'
    )

    for ci, (metric, label, good_t, border_t) in enumerate(_TL_DECISION):
        ax   = fig.add_subplot(gs[0, ci])
        x    = np.arange(len(STRATEGIES))
        vals = []
        for s in STRATEGIES:
            r = results[target][s][exp_ref]
            v = float(r.get(metric, 0.)) if r else 0.
            vals.append(v)
        cols = [_bc(v, good_t, border_t) for v in vals]
        bars = ax.bar(x, vals, 0.55, color=cols, alpha=0.88, edgecolor='white')
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.01,
                    f'{v:.3f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        ax.axhline(good_t,   color='#27AE60', lw=1.8, ls='--', alpha=0.85)
        ax.axhline(border_t, color='#F39C12', lw=1.2, ls=':',  alpha=0.70)
        ax.set_xticks(x)
        ax.set_xticklabels(STRAT_SHORT, fontsize=10, fontweight='bold')
        ax.set_ylim(0, 1.18)
        ax.set_title(f'{label} ↑', fontsize=10, fontweight='bold')
        ax.grid(axis='y', alpha=0.25)

    # Légende stratégies
    strat_patches = [mpatches.Patch(color=c, label=sl.replace('\n',' '))
                     for c, sl in zip(COLORS, STRAT_LABELS)]
    thresh_patches = [
        mpatches.Patch(color='#27AE60', label='✅ Bon (≥ seuil vert)'),
        mpatches.Patch(color='#F39C12', label='⚠️ Borderline'),
        mpatches.Patch(color='#E74C3C', label='❌ Insuffisant'),
    ]
    fig.legend(handles=thresh_patches, loc='upper right',
               bbox_to_anchor=(0.97, 0.93), fontsize=9, ncol=3, framealpha=0.9)

    # Tableau de décision
    ax_tbl = fig.add_subplot(gs[1, :])
    ax_tbl.axis('off')
    ax_tbl.set_title(
        'Seuils : AUC≥0.65 | Sensitivity≥0.50 | Specificity≥0.50 | MCC≥0.20 | Bal.Acc≥0.65',
        fontsize=9, fontweight='bold', pad=6
    )
    headers  = ['Stratégie', 'AUC ROC', 'Sensitivity', 'Specificity', 'MCC', 'Bal.Acc', 'DÉCISION']
    tbl_rows, tbl_colors = [], []
    for si, (s, sl) in enumerate(zip(STRATEGIES, STRAT_LABELS)):
        row_data = [sl.replace('\n', ' ')]
        row_col  = ['#ECF0F1']
        n_good   = 0
        r = results[target][s][exp_ref]
        for metric, _, good_t, border_t in _TL_DECISION:
            v = float(r.get(metric, 0.)) if r else 0.
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
    tbl.auto_set_font_size(False); tbl.set_fontsize(10)
    for col in range(len(headers)):
        tbl[(0, col)].set_facecolor('#1A3A4A')
        tbl[(0, col)].set_text_props(color='white', fontweight='bold')

    plt.savefig(str(OUT_DIR / f'decision_dashboard_{target}.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 decision_dashboard_{target}.png")


for target in TARGETS:
    plot_decision_dashboard_tl(target)


# ── Couleurs composantes (identiques DL + baseline) ──────────────────────────
_COMP_COLORS = {
    'auc_w':  '#2980B9',
    'sens_w': '#27AE60',
    'mcc_w':  '#F39C12',
    'spec_w': '#8E44AD',
}


def plot_composite_breakdown_tl(target):
    """
    Figure 2 panneaux par target :
      - Haut : barres empilées des 4 contributions pondérées (AUC×0.4, Sens×0.3, MCC×0.2, Spec×0.1)
               pour chaque stratégie TL × expérience
      - Bas  : métriques brutes côte à côte (AUC, Sensitivity, MCC, Specificity)
    Permet d'argumenter le choix de la stratégie TL [Ferri et al. 2009].
    """
    import matplotlib.patches as mpatches

    # Construire un DataFrame plat (stratégie × expérience)
    rows_plot = []
    for si, s in enumerate(STRATEGIES):
        for e in EXPS:
            r = results[target][s][e]
            if r is None:
                continue
            auc  = float(r.get('auc_roc', 0))
            sens = float(r.get('sensitivity', 0))
            mcc  = float(r.get('mcc', 0))
            spec = float(r.get('specificity', 0))
            rows_plot.append({
                'label':     f"{STRAT_SHORT[si]}-{e}",
                'strategy':  STRAT_SHORT[si],
                'exp':       e,
                'color_idx': si,
                'auc':  auc,  'sens': sens, 'mcc': mcc, 'spec': spec,
                'auc_w':  0.40 * max(auc, 0),
                'sens_w': 0.30 * max(sens, 0),
                'mcc_w':  0.20 * max(mcc, 0),
                'spec_w': 0.10 * max(spec, 0),
            })
    if not rows_plot:
        return
    import pandas as pd
    sub = pd.DataFrame(rows_plot)
    sub['composite'] = sub['auc_w'] + sub['sens_w'] + sub['mcc_w'] + sub['spec_w']
    sub = sub.sort_values('composite', ascending=False).reset_index(drop=True)

    n = len(sub)
    x = np.arange(n)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(max(14, n * 0.75), 12))
    fig.suptitle(
        f"Décomposition du Score Composite — Transfer Learning  |  {target.upper()}\n"
        f"Score = AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10\n"
        f"[Fawcett 2006; Chicco & Jurman 2020; Fairclough 2009; Youden 1950]",
        fontsize=11, fontweight='bold'
    )

    # Panneau 1 : stacked contributions
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
    for i, comp in enumerate(sub['composite']):
        ax1.text(i, comp + 0.008, f'{comp:.3f}', ha='center', va='bottom',
                 fontsize=7.5, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(sub['label'], rotation=45, ha='right', fontsize=8)
    ax1.set_ylabel('Score composite (contributions)', fontsize=9)
    ax1.set_title('Contributions pondérées au score composite (tri décroissant)', fontsize=10)
    ax1.axhline(0.50, color='#27AE60', lw=1.5, ls='--', alpha=0.7, label='Seuil bon (0.50)')
    ax1.axhline(0.35, color='#F39C12', lw=1.2, ls=':',  alpha=0.6, label='Seuil borderline (0.35)')
    ax1.set_ylim(0, min(1.0, sub['composite'].max() * 1.25))
    ax1.legend(loc='upper right', fontsize=7.5, framealpha=0.85)
    ax1.grid(axis='y', alpha=0.25)

    # Panneau 2 : métriques brutes
    w = 0.20
    for j, (col, lbl, color) in enumerate([
        ('auc',  'AUC-ROC',     _COMP_COLORS['auc_w']),
        ('sens', 'Sensitivity', _COMP_COLORS['sens_w']),
        ('mcc',  'MCC',         _COMP_COLORS['mcc_w']),
        ('spec', 'Specificity', _COMP_COLORS['spec_w']),
    ]):
        vals = sub[col].clip(lower=0).values
        offset = (j - 1.5) * w
        bars = ax2.bar(x + offset, vals, w, label=lbl, color=color, alpha=0.82, edgecolor='white')
        for bar, v in zip(bars, vals):
            if v > 0.01:
                ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                         f'{v:.2f}', ha='center', va='bottom', fontsize=5.5)
    ax2.set_xticks(x)
    ax2.set_xticklabels(sub['label'], rotation=45, ha='right', fontsize=8)
    ax2.set_ylabel('Valeur brute de la métrique', fontsize=9)
    ax2.set_title('Métriques brutes individuelles (AUC, Sensitivity, MCC, Specificity)', fontsize=10)
    ax2.axhline(0.50, color='gray', lw=1.0, ls='--', alpha=0.5)
    ax2.set_ylim(0, 1.15)
    ax2.legend(loc='upper right', fontsize=8, framealpha=0.85)
    ax2.grid(axis='y', alpha=0.25)

    plt.tight_layout()
    plt.savefig(OUT_DIR / f'composite_breakdown_{target}.png', dpi=150, bbox_inches='tight')
    plt.close()
    print(f"📊 composite_breakdown_{target}.png")


def save_composite_outputs_tl(target):
    """Sauvegarde composite_scores.json + composite_summary.txt pour le target TL."""
    ranking_json = []
    for si, s in enumerate(STRATEGIES):
        for e in EXPS:
            r = results[target][s][e]
            if r is None:
                continue
            auc  = float(r.get('auc_roc', 0))
            sens = float(r.get('sensitivity', 0))
            mcc  = float(r.get('mcc', 0))
            spec = float(r.get('specificity', 0))
            comp = 0.40 * max(auc, 0) + 0.30 * max(sens, 0) + 0.20 * max(mcc, 0) + 0.10 * max(spec, 0)
            ranking_json.append({
                "strategy": STRAT_SHORT[si],
                "strategy_full": STRAT_LABELS[si].replace('\n', ' '),
                "exp": e,
                "composite": round(comp, 4),
                "metrics": {
                    "AUC":          round(auc,  4),
                    "Sensitivity":  round(sens, 4),
                    "MCC":          round(mcc,  4),
                    "Specificity":  round(spec, 4),
                    "Balanced_Acc": round(float(r.get('balanced_accuracy', 0)), 4),
                    "MAE":          round(float(r.get('mae', 0)), 4),
                    "R2":           round(float(r.get('r2',  0)), 4),
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

    ranking_json.sort(key=lambda x: x['composite'], reverse=True)

    json_path = OUT_DIR / f'composite_scores_{target}.json'
    import json as _json
    with open(json_path, 'w', encoding='utf-8') as f:
        _json.dump({"target": target, "family": "TL",
                    "composite_formula": "AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10",
                    "ranking": ranking_json}, f, indent=2, ensure_ascii=False)
    print(f"📄 composite_scores_{target}.json")

    lines = []
    lines.append("=" * 90)
    lines.append(f"NeuroCap — Score Composite Transfer Learning — {target.upper()}")
    lines.append("Formule : AUC×0.40 + Sensitivity×0.30 + MCC×0.20 + Specificity×0.10")
    lines.append("  AUC  (w=0.40) : threshold-free, recommandée EEG/BCI [Fawcett 2006; Lotte et al. 2018]")
    lines.append("  Sens (w=0.30) : FN coûteux en monitoring cognitif [Fairclough 2009]")
    lines.append("  MCC  (w=0.20) : utilise les 4 cellules, robuste à l'imbalance [Chicco & Jurman 2020]")
    lines.append("  Spec (w=0.10) : FP moins coûteux [Youden 1950]")
    lines.append("=" * 90)
    lines.append(f"\n{'Rang':<5} {'Stratégie':<8} {'Exp':<5} {'Score':>7} │ "
                 f"{'AUC':>7} {'Sens':>7} {'MCC':>7} {'Spec':>7} │ "
                 f"{'AUC×0.4':>8} {'S×0.3':>7} {'M×0.2':>7} {'Sp×0.1':>7}")
    lines.append("─" * 90)
    for rank, item in enumerate(ranking_json, 1):
        m  = item['metrics']
        wc = item['weighted_contributions']
        lines.append(
            f"  {rank:<3} {item['strategy']:<8} {item['exp']:<5} {item['composite']:>7.4f} │ "
            f"{m['AUC']:>7.4f} {m['Sensitivity']:>7.4f} {m['MCC']:>7.4f} {m['Specificity']:>7.4f} │ "
            f"{wc['AUC_x040']:>8.4f} {wc['Sensitivity_x030']:>7.4f} "
            f"{wc['MCC_x020']:>7.4f} {wc['Specificity_x010']:>7.4f}"
        )
    if ranking_json:
        best = ranking_json[0]
        lines.append("\n" + "=" * 90)
        lines.append(f"★ MEILLEURE STRATÉGIE : {best['strategy_full']} — Exp. {best['exp']}")
        lines.append(f"  Score composite = {best['composite']:.4f}")
        for k, v in best['metrics'].items():
            lines.append(f"  {k:<15}: {v:.4f}")

    txt_path = OUT_DIR / f'composite_summary_{target}.txt'
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f"📄 composite_summary_{target}.txt")


for target in TARGETS:
    plot_composite_breakdown_tl(target)
    save_composite_outputs_tl(target)

print(f"\n✅ Comparaison TL Régression terminée.")
print(f"   Sorties : {OUT_DIR}")
