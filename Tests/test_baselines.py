"""
NeuroCap – Test Suite Baselines
================================
Évalue les modèles SVM / RF / XGBoost / LightGBM déjà entraînés
sur le jeu de test holdout.

Compare les deux jeux de features :
  • Baseline  : 15 features (PSD + ratios + Hjorth + power)
  • FeatEng   : ~80 features (+ DWT + entropies + texture)

Usage :
    cd EEG_project
    python Tests/test_baselines.py

Sorties :
    reports/Tests/baselines/
        ├── results_table.csv
        ├── comparison_barplot.png
        ├── confusion_matrices/   (une image par modèle × feature set)
        ├── roc_curves/
        └── decision_report.txt
"""

import sys
import warnings
import json
import time
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, f1_score, precision_score, recall_score,
    roc_auc_score, confusion_matrix, roc_curve, auc as sk_auc
)

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

# ============================================================================
# CHEMINS
# ============================================================================
PROJECT_ROOT = Path(__file__).resolve().parents[1]

FEAT_BASELINE_DIR = PROJECT_ROOT / 'features' / 'baseline' / 'datasets_features_extraction'
FEAT_ENG_DIR      = PROJECT_ROOT / 'Features' / 'Features_eng'

MODEL_BASELINE_DIR = PROJECT_ROOT / 'models' / 'Baseline'    / 'baseline_models'
MODEL_ENG_DIR      = PROJECT_ROOT / 'models' / 'baseline_FeatEng' / 'baseline_models'

REPORT_DIR = PROJECT_ROOT / 'reports' / 'Tests' / 'baselines'
REPORT_DIR.mkdir(parents=True, exist_ok=True)
(REPORT_DIR / 'confusion_matrices').mkdir(exist_ok=True)
(REPORT_DIR / 'roc_curves').mkdir(exist_ok=True)

CLASSIFIERS = ['SVM', 'Random_Forest', 'XGBoost', 'LightGBM']
FEAT_SETS   = {
    'Baseline-15f': (FEAT_BASELINE_DIR, MODEL_BASELINE_DIR),
    'FeatEng-80f':  (FEAT_ENG_DIR,      MODEL_ENG_DIR),
}

COLORS = {
    'SVM':           '#E74C3C',
    'Random_Forest': '#2980B9',
    'XGBoost':       '#27AE60',
    'LightGBM':      '#F39C12',
}

# ============================================================================
# CHARGEMENT DU MODÈLE
# ============================================================================
def load_model(clf_name: str, model_dir: Path):
    """Charge un modèle + scaler depuis le répertoire de modèles."""
    name = clf_name.replace(' ', '_')
    scaler_path = model_dir / f'{name}_scaler.joblib'
    if not scaler_path.exists():
        return None, None, "scaler introuvable"

    scaler = joblib.load(scaler_path)

    if clf_name == 'XGBoost':
        model_path = model_dir / f'{name}_concentration_vs_stress.json'
        if not model_path.exists():
            return None, None, "fichier modèle XGBoost introuvable"
        from xgboost import XGBClassifier
        model = XGBClassifier(verbosity=0)
        model.load_model(str(model_path))
    else:
        model_path = model_dir / f'{name}_concentration_vs_stress.joblib'
        if not model_path.exists():
            return None, None, "fichier modèle introuvable"
        model = joblib.load(model_path)

    return model, scaler, None


# ============================================================================
# ÉVALUATION
# ============================================================================
def compute_metrics(y_true, y_pred, y_proba=None):
    """Calcule les 8 métriques NeuroCap standard."""
    cm = confusion_matrix(y_true, y_pred)
    if cm.size == 4:
        tn, fp, fn, tp = cm.ravel()
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    else:
        specificity = 0.0

    m = {
        'accuracy':    accuracy_score(y_true, y_pred),
        'f1_macro':    f1_score(y_true, y_pred, average='macro',    zero_division=0),
        'f1_binary':   f1_score(y_true, y_pred, average='binary',   zero_division=0),
        'precision':   precision_score(y_true, y_pred, zero_division=0),
        'recall':      recall_score(y_true, y_pred, zero_division=0),
        'specificity': specificity,
        'auc':         0.5,
        'pct_uncertain': 0.0,
    }

    if y_proba is not None and len(np.unique(y_true)) > 1:
        try:
            m['auc'] = roc_auc_score(y_true, y_proba)
        except Exception:
            pass
        max_p = np.maximum(y_proba, 1 - y_proba)
        m['pct_uncertain'] = float(np.sum(max_p < 0.60) / len(y_true) * 100)

    return m


def evaluate_on_test(model, scaler, feat_dir: Path):
    """Évalue le modèle sur features_test.npy + labels_test.npy."""
    fp = feat_dir / 'features_test.npy'
    lp = feat_dir / 'labels_test.npy'
    if not fp.exists() or not lp.exists():
        return None, "features_test.npy ou labels_test.npy introuvable"

    X = np.load(fp)
    y = np.load(lp)
    if len(X) == 0:
        return None, "jeu de test vide"

    X_s = scaler.transform(X)
    y_pred = model.predict(X_s)
    y_proba = None
    if hasattr(model, 'predict_proba'):
        proba = model.predict_proba(X_s)
        y_proba = proba[:, 1]

    m = compute_metrics(y, y_pred, y_proba)
    m['n_samples'] = len(y)
    m['y_true']    = y.tolist()
    m['y_pred']    = y_pred.tolist()
    m['y_proba']   = y_proba.tolist() if y_proba is not None else []
    return m, None


# ============================================================================
# VISUALISATIONS
# ============================================================================
def plot_confusion_matrix(y_true, y_pred, title: str, save_path: Path):
    cm  = confusion_matrix(y_true, y_pred)
    if cm.shape == (1, 1):
        cm = np.array([[cm[0, 0], 0], [0, 0]])
    cmn = cm.astype(float) / (cm.sum(1, keepdims=True) + 1e-12)

    plt.figure(figsize=(5, 4))
    sns.heatmap(cmn, annot=True, fmt='.1%', cmap='Blues',
                xticklabels=['Concentration', 'Stress'],
                yticklabels=['Concentration', 'Stress'])
    plt.title(title, fontsize=10)
    plt.xlabel('Prédiction'); plt.ylabel('Vérité')
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_roc_curve(y_true, y_proba, title: str, color: str, save_path: Path):
    if y_proba is None or len(y_proba) == 0 or len(np.unique(y_true)) < 2:
        return
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_auc = sk_auc(fpr, tpr)
    plt.figure(figsize=(5, 4))
    plt.plot(fpr, tpr, lw=2, color=color, label=f'AUC = {roc_auc:.3f}')
    plt.plot([0, 1], [0, 1], 'k--', lw=1)
    plt.xlabel('FPR'); plt.ylabel('TPR'); plt.title(title, fontsize=10)
    plt.legend(); plt.grid(alpha=0.3); plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


def plot_comparison_bars(df: pd.DataFrame, save_path: Path):
    """Barplot F1-MACRO, AUC, Accuracy comparant tous les modèles × feature sets."""
    metrics   = ['f1_macro', 'auc', 'accuracy']
    titles    = ['F1-MACRO (critère principal)', 'AUC', 'Accuracy']
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    x     = np.arange(len(df))
    width = 0.35

    for ax, metric, title in zip(axes, metrics, titles):
        ax.bar(x, df[metric], color=[COLORS.get(r.split('-')[0], '#7F8C8D') for r in df['model_feat']],
               alpha=0.85, width=width)
        ax.set_xticks(x)
        ax.set_xticklabels(df['model_feat'], rotation=45, ha='right', fontsize=8)
        ax.set_ylabel(metric.replace('_', ' ').upper())
        ax.set_title(title, fontsize=11)
        ax.set_ylim([0, 1.05])
        ax.axhline(0.80, color='green', ls='--', lw=1, alpha=0.5, label='Seuil 80%')
        ax.legend(fontsize=8)
        ax.grid(axis='y', alpha=0.3)

    fig.suptitle('NeuroCap – Comparaison Baselines (Test Holdout)', fontsize=13, fontweight='bold')
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


def plot_radar(df: pd.DataFrame, save_path: Path):
    """Radar chart des 5 métriques principales pour chaque modèle."""
    cats   = ['f1_macro', 'auc', 'accuracy', 'recall', 'specificity']
    labels = ['F1-Macro', 'AUC', 'Accuracy', 'Recall', 'Specificité']
    N      = len(cats)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Prendre les 8 combinaisons disponibles
    for _, row in df.iterrows():
        values = [row[c] for c in cats]
        values += values[:1]
        clf = row['model_feat'].split('-')[0]
        ax.plot(angles, values, lw=2, label=row['model_feat'],
                color=COLORS.get(clf, '#7F8C8D'))
        ax.fill(angles, values, alpha=0.05, color=COLORS.get(clf, '#7F8C8D'))

    ax.set_thetagrids(np.degrees(angles[:-1]), labels, fontsize=9)
    ax.set_ylim([0, 1])
    ax.set_title('Radar – Baselines (Test Holdout)', fontsize=12, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.35, 1.1), fontsize=8)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 75)
    print("NeuroCap – Test Suite Baselines")
    print("Évaluation sur jeu de test holdout")
    print("=" * 75)

    all_results = []

    for feat_label, (feat_dir, model_dir) in FEAT_SETS.items():
        print(f"\n{'─'*60}")
        print(f"  Feature set : {feat_label}")
        print(f"  Features    : {feat_dir}")
        print(f"  Modèles     : {model_dir}")
        print(f"{'─'*60}")

        if not feat_dir.exists():
            print(f"  [SKIP] Répertoire features introuvable : {feat_dir}")
            continue
        if not model_dir.exists():
            print(f"  [SKIP] Répertoire modèles introuvable : {model_dir}")
            continue

        for clf_name in CLASSIFIERS:
            print(f"\n  ▶ {clf_name} [{feat_label}]")

            model, scaler, err = load_model(clf_name, model_dir)
            if err:
                print(f"    [SKIP] {err}")
                continue

            t0 = time.time()
            m, err = evaluate_on_test(model, scaler, feat_dir)
            elapsed = time.time() - t0

            if err:
                print(f"    [SKIP] {err}")
                continue

            label = f"{clf_name}-{feat_label}"
            m['model']      = clf_name
            m['feat_set']   = feat_label
            m['model_feat'] = label
            m['eval_time_sec'] = elapsed

            all_results.append(m)

            print(f"    Accuracy  = {m['accuracy']:.4f}")
            print(f"    F1-MACRO  = {m['f1_macro']:.4f}  ← critère principal")
            print(f"    AUC       = {m['auc']:.4f}")
            print(f"    Precision = {m['precision']:.4f}  Recall = {m['recall']:.4f}")
            print(f"    Spécif.   = {m['specificity']:.4f}")
            print(f"    Incertains= {m['pct_uncertain']:.1f}%  (CdC : max(P)<0.60)")
            print(f"    N samples = {m['n_samples']}  [eval en {elapsed:.2f}s]")

            # Figures individuelles
            safe = label.replace(' ', '_').replace('/', '_')
            plot_confusion_matrix(
                m['y_true'], m['y_pred'],
                f"{clf_name} – {feat_label}",
                REPORT_DIR / 'confusion_matrices' / f"{safe}_cm.png"
            )
            plot_roc_curve(
                m['y_true'], m['y_proba'] if m['y_proba'] else None,
                f"{clf_name} – ROC ({feat_label})",
                COLORS.get(clf_name, '#7F8C8D'),
                REPORT_DIR / 'roc_curves' / f"{safe}_roc.png"
            )

    if not all_results:
        print("\n[ERREUR] Aucun modèle évalué – vérifiez les chemins et relancez l'entraînement.")
        return

    # ─── DataFrame & CSV ──────────────────────────────────────────────────────
    cols_keep = ['model_feat', 'model', 'feat_set',
                 'accuracy', 'f1_macro', 'f1_binary',
                 'precision', 'recall', 'specificity',
                 'auc', 'pct_uncertain', 'n_samples', 'eval_time_sec']
    df = pd.DataFrame(all_results)
    for c in cols_keep:
        if c not in df.columns:
            df[c] = np.nan
    df = df[cols_keep].sort_values('f1_macro', ascending=False).reset_index(drop=True)

    df.to_csv(REPORT_DIR / 'results_table.csv', index=False)

    # ─── Score de décision pondéré (identique à compare.py DL) ────────────────
    # 40% F1-macro + 30% AUC + 20% Accuracy + 10% (1 – incertitude%)
    df['weighted_score'] = (
        0.40 * df['f1_macro']
        + 0.30 * df['auc']
        + 0.20 * df['accuracy']
        + 0.10 * (1 - df['pct_uncertain'] / 100)
    )
    df_ranked = df.sort_values('weighted_score', ascending=False).reset_index(drop=True)

    # ─── Affichage tableau final ──────────────────────────────────────────────
    print(f"\n{'='*75}")
    print("CLASSEMENT FINAL (jeu de test holdout)")
    print(f"{'='*75}")
    print(f"{'Rang':>4}  {'Modèle-FeatureSet':<32}  {'F1m':>6}  {'AUC':>6}  {'Acc':>6}  {'Inc%':>5}  {'Score':>6}")
    print("-" * 75)
    for rank, row in df_ranked.iterrows():
        marker = " ★" if rank == 0 else "  "
        print(f"{rank+1:>4}{marker} {row['model_feat']:<32}  "
              f"{row['f1_macro']:.4f}  {row['auc']:.4f}  "
              f"{row['accuracy']:.4f}  {row['pct_uncertain']:>4.1f}%  "
              f"{row['weighted_score']:.4f}")

    best = df_ranked.iloc[0]
    print(f"\n★ Meilleur modèle baseline : {best['model_feat']}")
    print(f"  F1-MACRO = {best['f1_macro']:.4f}  |  AUC = {best['auc']:.4f}  |  Score = {best['weighted_score']:.4f}")

    # ─── Comparaison Baseline vs FeatEng par classifieur ────────────────────
    print(f"\n{'─'*75}")
    print("IMPACT DU FEATURE ENGINEERING (ΔF1-MACRO)")
    print(f"{'─'*75}")
    for clf in CLASSIFIERS:
        rows_base = df[df['model_feat'] == f"{clf}-Baseline-15f"]
        rows_eng  = df[df['model_feat'] == f"{clf}-FeatEng-80f"]
        if rows_base.empty or rows_eng.empty:
            continue
        base_f1m = rows_base.iloc[0]['f1_macro']
        eng_f1m  = rows_eng.iloc[0]['f1_macro']
        delta    = eng_f1m - base_f1m
        sign     = "+" if delta >= 0 else ""
        winner   = "FeatEng" if delta > 0 else ("Baseline" if delta < 0 else "Egal")
        print(f"  {clf:<16} Baseline={base_f1m:.4f}  FeatEng={eng_f1m:.4f}  "
              f"Δ={sign}{delta:.4f}  → {winner}")

    # ─── Graphiques de synthèse ───────────────────────────────────────────────
    plot_comparison_bars(df_ranked, REPORT_DIR / 'comparison_barplot.png')
    plot_radar(df_ranked, REPORT_DIR / 'radar_chart.png')

    # ─── Rapport de décision ─────────────────────────────────────────────────
    report_path = REPORT_DIR / 'decision_report.txt'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("NeuroCap – Rapport de Décision Baselines\n")
        f.write("=" * 60 + "\n\n")
        f.write("Critère principal : F1-MACRO (équilibre Concentration/Stress)\n")
        f.write("Score pondéré     : 40% F1-macro + 30% AUC + 20% Acc + 10% certitude\n\n")
        f.write(f"{'Rang':<5} {'Modèle':<35} {'F1m':>6} {'AUC':>6} {'Acc':>6} {'Score':>7}\n")
        f.write("-" * 70 + "\n")
        for rank, row in df_ranked.iterrows():
            f.write(f"{rank+1:<5} {row['model_feat']:<35} "
                    f"{row['f1_macro']:>6.4f} {row['auc']:>6.4f} "
                    f"{row['accuracy']:>6.4f} {row['weighted_score']:>7.4f}\n")
        f.write("\n" + "=" * 60 + "\n")
        f.write(f"RECOMMANDATION : {best['model_feat']}\n")
        f.write(f"  F1-MACRO = {best['f1_macro']:.4f}\n")
        f.write(f"  AUC      = {best['auc']:.4f}\n")
        f.write(f"  Accuracy = {best['accuracy']:.4f}\n")
        f.write(f"  Incertains CdC = {best['pct_uncertain']:.1f}%\n\n")
        f.write("Avantages Baseline ML :\n")
        f.write("  + Interprétabilité : features spectrales lisibles\n")
        f.write("  + Latence ultra-faible (< 1 ms par epoch)\n")
        f.write("  + Déploiement embarqué possible (ESP32 / Raspberry Pi)\n")
        f.write("  + Pas besoin de GPU pour l'inférence\n")
        f.write("  + Moins de risque d'overfitting sur petits datasets\n")

    # ─── Sauvegarde JSON ──────────────────────────────────────────────────────
    results_json = []
    for r in all_results:
        r_save = {k: v for k, v in r.items() if k not in ('y_true', 'y_pred', 'y_proba')}
        results_json.append(r_save)
    with open(REPORT_DIR / 'results.json', 'w') as f:
        json.dump({
            'best': best['model_feat'],
            'best_f1_macro': best['f1_macro'],
            'best_weighted_score': best['weighted_score'],
            'all_results': results_json,
        }, f, indent=2, default=str)

    print(f"\n{'='*75}")
    print(f"Sorties sauvegardées dans : {REPORT_DIR}")
    print(f"  • results_table.csv")
    print(f"  • comparison_barplot.png")
    print(f"  • radar_chart.png")
    print(f"  • confusion_matrices/")
    print(f"  • roc_curves/")
    print(f"  • decision_report.txt")
    print(f"  • results.json")
    print(f"{'='*75}")


if __name__ == '__main__':
    main()
