"""
=============================================================================
NeuroCap — Module de Métriques Professionnelles  (5 Niveaux)
metrics_professional.py
=============================================================================
Module PARTAGÉ utilisable par TOUS les pipelines NeuroCap :
  Baselines ML · Deep Learning · Transfer Learning · DANN · Fine-tuning

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NIVEAU 1 — Métriques cliniques complètes
  Sensitivity, Specificity, PPV, NPV, MCC, G-Mean,
  Balanced Accuracy, PR-AUC, LR+, LR−, Brier Score

NIVEAU 2 — Intervalles de confiance & tests statistiques
  Bootstrap 95% CI (N=500 tirages)
  Test de permutation  (p-value pour R² et AUC)
  Test de Wilcoxon signed-rank  (2 modèles, par fold LOSO)
  Test de Friedman + post-hoc Wilcoxon/Bonferroni  (k modèles)

NIVEAU 3 — Qualité clinique & incertitude de prédiction
  Calibration     : ECE, MCE, Brier Score, Reliability Diagram
  Bland-Altman    : biais systématique, Limits of Agreement (LoA)
  ICC(2,1)        : Intraclass Correlation Coefficient
  Conformal Pred. : intervalles à couverture garantie (split conformal)
  Incertitude RF  : std des arbres (ensemble uncertainty)
  Confiance       : score sigmoïde distance-au-seuil Low/High

NIVEAU 4 — Robustesse & stabilité
  Stability Analysis  : CV, std, min/max, variance inter-folds LOSO
  Bias-Variance       : décomposition MSE = Biais² + Variance + Bruit
  Per-Subject         : métriques individuelles par sujet LOSO
  Learning Curve      : R² / AUC vs nombre de sujets d'entraînement

NIVEAU 5 — Tests statistiques avancés
  Decision Curve Analysis (DCA) : Net Clinical Benefit vs seuil décision
  DeLong AUC CI       : intervalle analytique exact sur l'AUC
  Professional Report : rapport markdown complet exportable
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
UTILISATION :
  from src.models.metrics_professional import (
      compute_full_metrics, bootstrap_ci, permutation_test,
      calibration_analysis, bland_altman_analysis, icc,
      conformal_intervals, ensemble_uncertainty, confidence_score,
      run_wilcoxon_all_pairs, run_friedman_test,
      stability_analysis, bias_variance_decomposition,
      per_subject_metrics, learning_curve_loso,
      decision_curve_analysis, delong_auc_ci,
      generate_professional_report,
      plot_reliability_diagram, plot_bland_altman,
      plot_bootstrap_ci_bars, plot_full_confusion_matrix,
      plot_wilcoxon_heatmap, plot_per_subject_heatmap,
      plot_decision_curve,
  )
=============================================================================
"""

from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

from sklearn.metrics import (
    confusion_matrix, accuracy_score, f1_score, cohen_kappa_score,
    roc_auc_score, average_precision_score, precision_recall_curve,
    matthews_corrcoef, balanced_accuracy_score,
    mean_absolute_error, mean_squared_error, r2_score,
    brier_score_loss, log_loss,
)
from scipy import stats as sp_stats

warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTES PARTAGÉES
# ─────────────────────────────────────────────────────────────────────────────
THRESHOLD_DEFAULT = 5.0      # seuil Low (0-5) / High (5-10)
N_BOOTSTRAP       = 500      # tirages bootstrap (~0.3 s/modèle)
N_PERMUTATIONS    = 500      # permutations pour p-value
CONF_ALPHA        = 0.05     # niveau de signification (CI 95%)
CONF_K_SIGMOID    = 1.5      # pente sigmoïde confiance


# ═════════════════════════════════════════════════════════════════════════════
# ███  NIVEAU 1 — MÉTRIQUES CLINIQUES COMPLÈTES                           ███
# ═════════════════════════════════════════════════════════════════════════════

def bin_scores(scores: np.ndarray, threshold: float = THRESHOLD_DEFAULT) -> np.ndarray:
    """
    Score continu (0-10) → classe binaire.
      score < threshold  →  0  (Low)
      score ≥ threshold  →  1  (High)
    """
    return (np.clip(np.asarray(scores, dtype=float), 0, 10) >= threshold).astype(int)


def compute_full_metrics(
    y_true: np.ndarray,
    y_pred_continuous: np.ndarray,
    threshold: float = THRESHOLD_DEFAULT,
) -> Dict:
    """
    Calcule TOUTES les métriques professionnelles depuis prédictions continues.

    RÉGRESSION   : mae, rmse, r2
    CLASSIF. BIN : accuracy, balanced_accuracy, sensitivity, specificity,
                   ppv, npv, f1_macro, f1_weighted, mcc, g_mean,
                   auc_roc, pr_auc, lr_plus, lr_minus, kappa, brier_score
    BRUT         : tp, tn, fp, fn, n_samples, pct_high

    Explications :
      Sensitivity  = TP/(TP+FN) → "parmi les vrais High, combien détecte-t-on ?"
      Specificity  = TN/(TN+FP) → "parmi les vrais Low, combien sont bien classés ?"
      PPV          = TP/(TP+FP) → "quand on dit High, a-t-on raison ?"
      NPV          = TN/(TN+FN) → "quand on dit Low, a-t-on raison ?"
      MCC          = métrique équitable même sous déséquilibre de classes
      G-Mean       = √(Sensitivity × Specificity) → équilibre Sens/Spec
      LR+          = Sensitivity/(1-Specificity) → vraisemblance positive
      LR−          = (1-Sensitivity)/Specificity → vraisemblance négative
      PR-AUC       = meilleur que ROC-AUC sous déséquilibre (cas stress 71% Low)
    """
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred_continuous, dtype=float)

    # Régression
    mae  = float(mean_absolute_error(yt, yp))
    rmse = float(np.sqrt(mean_squared_error(yt, yp)))
    r2   = float(r2_score(yt, yp))

    # Binarisation
    yt_b = bin_scores(yt, threshold)
    yp_b = bin_scores(yp, threshold)

    if len(np.unique(yt_b)) < 2:
        return _degenerate_metrics(mae, rmse, r2)

    cm = confusion_matrix(yt_b, yp_b, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    sensitivity  = _safe_div(tp, tp + fn)
    specificity  = _safe_div(tn, tn + fp)
    ppv          = _safe_div(tp, tp + fp)
    npv          = _safe_div(tn, tn + fn)
    g_mean       = float(np.sqrt(sensitivity * specificity))
    balanced_acc = float(balanced_accuracy_score(yt_b, yp_b))
    mcc          = float(matthews_corrcoef(yt_b, yp_b))
    kappa        = float(cohen_kappa_score(yt_b, yp_b))
    f1_macro     = float(f1_score(yt_b, yp_b, average='macro',    zero_division=0))
    f1_weighted  = float(f1_score(yt_b, yp_b, average='weighted', zero_division=0))
    accuracy     = float(accuracy_score(yt_b, yp_b))
    lr_plus      = _safe_div(sensitivity, 1 - specificity)
    lr_minus     = _safe_div(1 - sensitivity, specificity)

    try:
        auc_roc = float(roc_auc_score(yt_b, yp))
    except Exception:
        auc_roc = 0.5
    try:
        pr_auc = float(average_precision_score(yt_b, yp))
    except Exception:
        pr_auc = float(np.mean(yt_b))

    prob_high = _to_proba(yp, threshold, CONF_K_SIGMOID)
    try:
        brier = float(brier_score_loss(yt_b, prob_high))
    except Exception:
        brier = 0.25

    return {
        'mae': mae, 'rmse': rmse, 'r2': r2,
        'accuracy': accuracy, 'balanced_accuracy': balanced_acc,
        'sensitivity': sensitivity, 'specificity': specificity,
        'ppv': ppv, 'npv': npv,
        'f1_macro': f1_macro, 'f1_weighted': f1_weighted,
        'mcc': mcc, 'g_mean': g_mean,
        'auc_roc': auc_roc, 'pr_auc': pr_auc,
        'lr_plus': lr_plus, 'lr_minus': lr_minus,
        'kappa': kappa, 'brier_score': brier,
        'tp': int(tp), 'tn': int(tn), 'fp': int(fp), 'fn': int(fn),
        'n_samples': len(yt), 'pct_high': float(np.mean(yt_b)),
    }


# ═════════════════════════════════════════════════════════════════════════════
# ███  NIVEAU 2 — INTERVALLES DE CONFIANCE & TESTS STATISTIQUES           ███
# ═════════════════════════════════════════════════════════════════════════════

def bootstrap_ci(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_bootstrap: int = N_BOOTSTRAP,
    alpha: float = CONF_ALPHA,
    random_state: int = 42,
    threshold: float = THRESHOLD_DEFAULT,
) -> Dict:
    """
    Bootstrap IC (1-α) = 95% CI sur toutes les métriques clés.

    Principe :
      1. Tirer N=500 fois un échantillon de taille n avec remplacement
      2. Calculer chaque métrique sur l'échantillon tiré
      3. IC = [percentile(2.5%), percentile(97.5%)]

    Si le CI AUC inclut 0.50 → le modèle n'est PAS significativement
    meilleur que le hasard. Crucial pour la crédibilité commerciale.

    Retourne pour chaque métrique : {'mean', 'ci_lo', 'ci_hi', 'std'}
    """
    rng = np.random.default_rng(random_state)
    yt  = np.asarray(y_true, dtype=float)
    yp  = np.asarray(y_pred, dtype=float)
    n   = len(yt)
    yt_b = bin_scores(yt, threshold)

    metrics_boot: Dict[str, List[float]] = {
        k: [] for k in ['mae', 'rmse', 'r2', 'auc_roc', 'pr_auc',
                         'f1_macro', 'sensitivity', 'specificity',
                         'mcc', 'balanced_accuracy']
    }

    for _ in range(n_bootstrap):
        idx   = rng.integers(0, n, size=n)
        yt_s  = yt[idx];   yp_s  = yp[idx]
        ytb_s = yt_b[idx]; ypb_s = bin_scores(yp_s, threshold)

        metrics_boot['mae'].append(float(mean_absolute_error(yt_s, yp_s)))
        metrics_boot['rmse'].append(float(np.sqrt(mean_squared_error(yt_s, yp_s))))
        metrics_boot['r2'].append(float(r2_score(yt_s, yp_s)))

        if len(np.unique(ytb_s)) < 2:
            metrics_boot['auc_roc'].append(0.5)
            metrics_boot['pr_auc'].append(float(np.mean(ytb_s)))
            metrics_boot['f1_macro'].append(0.5)
            metrics_boot['sensitivity'].append(0.5)
            metrics_boot['specificity'].append(0.5)
            metrics_boot['mcc'].append(0.0)
            metrics_boot['balanced_accuracy'].append(0.5)
            continue

        try:
            metrics_boot['auc_roc'].append(float(roc_auc_score(ytb_s, yp_s)))
        except Exception:
            metrics_boot['auc_roc'].append(0.5)
        try:
            metrics_boot['pr_auc'].append(float(average_precision_score(ytb_s, yp_s)))
        except Exception:
            metrics_boot['pr_auc'].append(float(np.mean(ytb_s)))

        metrics_boot['f1_macro'].append(
            float(f1_score(ytb_s, ypb_s, average='macro', zero_division=0)))
        metrics_boot['mcc'].append(float(matthews_corrcoef(ytb_s, ypb_s)))
        metrics_boot['balanced_accuracy'].append(
            float(balanced_accuracy_score(ytb_s, ypb_s)))

        cm_ = confusion_matrix(ytb_s, ypb_s, labels=[0, 1])
        tn_, fp_, fn_, tp_ = cm_.ravel()
        metrics_boot['sensitivity'].append(_safe_div(tp_, tp_ + fn_))
        metrics_boot['specificity'].append(_safe_div(tn_, tn_ + fp_))

    lo_q = alpha / 2; hi_q = 1 - alpha / 2
    result = {}
    for k, vals in metrics_boot.items():
        arr = np.array(vals)
        result[k] = {
            'mean':  float(np.mean(arr)),
            'ci_lo': float(np.percentile(arr, lo_q * 100)),
            'ci_hi': float(np.percentile(arr, hi_q * 100)),
            'std':   float(np.std(arr)),
        }
    return result


def permutation_test(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    n_permutations: int = N_PERMUTATIONS,
    random_state: int = 42,
    threshold: float = THRESHOLD_DEFAULT,
) -> Dict:
    """
    Test de permutation pour R² et AUC.

    H₀ : les labels sont aléatoires → le modèle ne capture rien.
    H₁ : le modèle capture une relation réelle.
    p-value = P(métrique_permutée ≥ métrique_observée | H₀)
    p < 0.05 → résultat statistiquement significatif.

    Exemple :
      R²=0.116, p=0.004  → significatif ✅
      AUC=0.664, p=0.001 → significatif ✅
      R²=−0.010, p=0.521 → NON significatif ❌  (cas stress)
    """
    rng = np.random.default_rng(random_state)
    yt  = np.asarray(y_true, dtype=float)
    yp  = np.asarray(y_pred, dtype=float)
    ytb = bin_scores(yt, threshold)

    obs_r2  = float(r2_score(yt, yp))
    try:
        obs_auc = float(roc_auc_score(ytb, yp))
    except Exception:
        obs_auc = 0.5

    r2_perm, auc_perm = [], []
    for _ in range(n_permutations):
        yt_perm  = rng.permutation(yt)
        ytb_perm = bin_scores(yt_perm, threshold)
        r2_perm.append(float(r2_score(yt_perm, yp)))
        try:
            auc_perm.append(float(roc_auc_score(ytb_perm, yp)))
        except Exception:
            auc_perm.append(0.5)

    p_r2  = float(np.mean(np.array(r2_perm)  >= obs_r2))
    p_auc = float(np.mean(np.array(auc_perm) >= obs_auc))

    return {
        'r2':      {'observed': obs_r2,  'p_value': p_r2,
                    'significant': p_r2  < CONF_ALPHA, 'n_permutations': n_permutations},
        'auc_roc': {'observed': obs_auc, 'p_value': p_auc,
                    'significant': p_auc < CONF_ALPHA, 'n_permutations': n_permutations},
    }


def wilcoxon_pairwise(fold_vals_1: List[float], fold_vals_2: List[float]) -> Dict:
    """
    Test de Wilcoxon signed-rank entre 2 séries de métriques par fold LOSO.
    Usage : comparer RF vs SVR sur les R² des 11 folds de conc.

    Effect size = rank-biserial correlation r ∈ [−1, +1]
      |r| < 0.1  → effet négligeable
      |r| < 0.3  → petit effet
      |r| < 0.5  → effet modéré
      |r| ≥ 0.5  → grand effet
    """
    a = np.asarray(fold_vals_1, dtype=float)
    b = np.asarray(fold_vals_2, dtype=float)
    if len(a) < 5 or len(a) != len(b):
        return {'p_value': 1.0, 'statistic': 0.0, 'significant': False,
                'n_folds': len(a), 'note': 'insufficient_folds'}
    try:
        stat, p = sp_stats.wilcoxon(a, b, alternative='two-sided', zero_method='wilcox')
        return {
            'statistic':   float(stat),
            'p_value':     float(p),
            'significant': float(p) < CONF_ALPHA,
            'n_folds':     len(a),
            'effect_size': float(_rank_biserial(a, b)),
        }
    except Exception as e:
        return {'p_value': 1.0, 'statistic': 0.0, 'significant': False,
                'n_folds': len(a), 'note': str(e)}


def run_wilcoxon_all_pairs(
    models_fold_metrics: Dict[str, List[float]],
    metric: str = 'r2',
) -> Dict:
    """
    Tests de Wilcoxon entre toutes les paires de modèles pour une métrique.

    Args:
        models_fold_metrics : {'RF': [fold1_r2, fold2_r2, ...], 'SVR': [...], ...}
    Retourne : {'RF_vs_SVR': {'p_value': ..., 'significant': ..., ...}, ...}
    """
    results = {}
    names = list(models_fold_metrics.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            m1, m2 = names[i], names[j]
            results[f'{m1}_vs_{m2}'] = wilcoxon_pairwise(
                models_fold_metrics[m1], models_fold_metrics[m2])
    return results


def run_friedman_test(models_fold_metrics: Dict[str, List[float]]) -> Dict:
    """
    Test de Friedman (ANOVA non-paramétrique) pour k modèles.

    H₀ : tous les modèles sont équivalents.
    Si p < 0.05 → au moins un modèle diffère. Post-hoc Wilcoxon + Bonferroni.

    Interprétation :
      p < 0.05  → il existe des différences significatives entre modèles
      Post-hoc  → quelles paires spécifiques diffèrent
    """
    names  = list(models_fold_metrics.keys())
    arrays = [np.asarray(v, dtype=float) for v in models_fold_metrics.values()]
    min_len = min(len(a) for a in arrays)

    if min_len < 3 or len(arrays) < 3:
        return {'p_value': 1.0, 'significant': False, 'note': 'insufficient_data'}

    arrays_trim = [a[:min_len] for a in arrays]
    try:
        stat, p = sp_stats.friedmanchisquare(*arrays_trim)
    except Exception as e:
        return {'p_value': 1.0, 'significant': False, 'note': str(e)}

    result = {
        'statistic': float(stat), 'p_value': float(p),
        'significant': float(p) < CONF_ALPHA,
        'n_models': len(names), 'n_folds': min_len, 'post_hoc': {},
    }

    if float(p) < CONF_ALPHA:
        n_pairs    = len(names) * (len(names) - 1) / 2
        bonf_alpha = CONF_ALPHA / n_pairs
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                m1, m2 = names[i], names[j]
                try:
                    _, pij = sp_stats.wilcoxon(arrays_trim[i], arrays_trim[j],
                                               zero_method='wilcox')
                    result['post_hoc'][f'{m1}_vs_{m2}'] = {
                        'p_value':      float(pij),
                        'p_bonferroni': float(pij * n_pairs),
                        'significant':  float(pij) < bonf_alpha,
                    }
                except Exception:
                    result['post_hoc'][f'{m1}_vs_{m2}'] = {
                        'p_value': 1.0, 'significant': False}
    return result


# ═════════════════════════════════════════════════════════════════════════════
# ███  NIVEAU 3 — QUALITÉ CLINIQUE & INCERTITUDE DE PRÉDICTION            ███
# ═════════════════════════════════════════════════════════════════════════════

def calibration_analysis(
    y_true: np.ndarray,
    y_pred_continuous: np.ndarray,
    n_bins: int = 10,
    threshold: float = THRESHOLD_DEFAULT,
) -> Dict:
    """
    Calibration : "quand le système dit 70% de chance de High,
                   a-t-il raison 70% du temps ?"

    ECE (Expected Calibration Error) :
      ECE = Σ (nb_dans_bin/N) × |accuracy_bin − confidence_bin|
      Objectif commercial : ECE < 0.05

    MCE (Maximum Calibration Error) : pire bin
    Brier Score : MSE entre probabilité prédite et label réel (< 0.20)
    Reliability Diagram : diagonale = calibration parfaite
    """
    yt  = np.asarray(y_true, dtype=float)
    yp  = np.asarray(y_pred_continuous, dtype=float)
    ytb = bin_scores(yt, threshold)
    prob_high = _to_proba(yp, threshold, CONF_K_SIGMOID)

    try:
        brier   = float(brier_score_loss(ytb, prob_high))
        logloss = float(log_loss(ytb, np.clip(prob_high, 1e-7, 1-1e-7)))
    except Exception:
        brier = 0.25; logloss = np.log(2)

    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_accs, bin_confs, bin_counts = [], [], []
    for lo, hi in zip(bin_edges[:-1], bin_edges[1:]):
        mask = (prob_high >= lo) & (prob_high < hi)
        if mask.sum() == 0:
            bin_accs.append(0.0); bin_confs.append((lo+hi)/2); bin_counts.append(0)
            continue
        bin_accs.append(float(np.mean(ytb[mask])))
        bin_confs.append(float(np.mean(prob_high[mask])))
        bin_counts.append(int(mask.sum()))

    ba, bc, bn = np.array(bin_accs), np.array(bin_confs), np.array(bin_counts)
    n_total = len(yt)
    ece = float(np.sum(bn / n_total * np.abs(ba - bc)))
    mce = float(np.max(np.abs(ba - bc)))

    return {
        'ece': ece, 'mce': mce, 'brier_score': brier, 'log_loss': logloss,
        'reliability_diagram': {
            'bin_accuracies': ba.tolist(),
            'bin_confidences': bc.tolist(),
            'bin_counts': bn.tolist(),
        },
    }


def bland_altman_analysis(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """
    Analyse de Bland-Altman — standard médical pour valider un système de mesure.

    bias      = mean(y_pred − y_true)          ← biais systématique
    LoA lower = bias − 1.96 × std(diff)
    LoA upper = bias + 1.96 × std(diff)
    pct_within_loa = % points dans [LoA−, LoA+]  →  doit être ≥ 95%

    Interprétation clinique (échelle 0-10) :
      LoA width < ±2 pts  → accord clinique excellent
      LoA width < ±4 pts  → accord acceptable pour aide à la décision
      LoA width > ±4 pts  → usage autonome non recommandé
    """
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    diff = yp - yt
    mean = (yp + yt) / 2.0

    bias      = float(np.mean(diff))
    std_diff  = float(np.std(diff, ddof=1))
    loa_lower = bias - 1.96 * std_diff
    loa_upper = bias + 1.96 * std_diff
    pct_within = float(np.mean((diff >= loa_lower) & (diff <= loa_upper)) * 100)

    return {
        'bias': bias, 'std_diff': std_diff,
        'loa_lower': loa_lower, 'loa_upper': loa_upper,
        'loa_width': loa_upper - loa_lower,
        'pct_within_loa': pct_within,
        'mean_values': mean.tolist(),
        'differences': diff.tolist(),
        'clinical_acceptable': bool(pct_within >= 95.0),
    }


def icc(y_true: np.ndarray, y_pred: np.ndarray) -> Dict:
    """
    Intraclass Correlation Coefficient ICC(2,1).
    Two-way random, single measures, absolute agreement (Shrout & Fleiss 1979).

    Requis pour tout dispositif médical / certification CE / FDA.

    Interprétation (Koo & Mae, 2016) :
      < 0.50  → fiabilité insuffisante
      0.50-0.75 → fiabilité modérée
      0.75-0.90 → bonne fiabilité
      > 0.90    → excellente fiabilité (niveau requis médical)

    NeuroCap actuel : ICC ≈ 0.30-0.35 (préliminaire, acceptable pour aide décision)
    """
    yt = np.asarray(y_true, dtype=float)
    yp = np.asarray(y_pred, dtype=float)
    n  = len(yt)
    if n < 4:
        return {'icc': 0.0, 'interpretation': 'insufficient_data'}

    data       = np.column_stack([yt, yp])
    grand_mean = data.mean()
    row_means  = data.mean(axis=1)
    col_means  = data.mean(axis=0)

    ssb = 2 * np.sum((row_means - grand_mean) ** 2)
    ssr = n * np.sum((col_means  - grand_mean) ** 2)
    sst = np.sum((data - grand_mean) ** 2)
    sse = sst - ssb - ssr

    msb = ssb / (n - 1)
    msr = ssr / 1
    mse = max(sse / (n - 1), 1e-12)

    denom   = msb + msr + (2 * n - 2) * mse / n
    icc_val = float(np.clip((msb - mse) / denom if denom > 0 else 0.0, -1, 1))

    if   icc_val < 0.50: interp = 'insufficient (<0.50)'
    elif icc_val < 0.75: interp = 'moderate (0.50-0.75)'
    elif icc_val < 0.90: interp = 'good (0.75-0.90)'
    else:                interp = 'excellent (>0.90)'

    return {
        'icc': icc_val, 'interpretation': interp,
        'msb': float(msb), 'msr': float(msr), 'mse': float(mse), 'n_samples': n,
    }


def conformal_intervals(
    y_cal_true: np.ndarray,
    y_cal_pred: np.ndarray,
    y_test_pred: np.ndarray,
    alpha: float = CONF_ALPHA,
) -> Dict:
    """
    Split Conformal Prediction — garantie mathématique de couverture.

    GARANTIE : P(y_true ∈ [y_pred − q, y_pred + q]) ≥ 1 − α = 95%
    (sous hypothèse d'échangeabilité, sans supposer une distribution)

    Contrairement au bootstrap CI (approx.), cette garantie est exacte.
    C'est le standard recommandé pour les dispositifs médicaux (FDA guidance 2023).

    Étapes :
      1. Résidus de calibration : s_i = |y_cal_true_i − y_cal_pred_i|
      2. q = quantile des s_i au niveau (⌈(1-α)(n+1)⌉/n)
      3. Intervalle test : [y_test − q, y_test + q]
    """
    y_cal_t = np.asarray(y_cal_true, dtype=float)
    y_cal_p = np.asarray(y_cal_pred, dtype=float)
    y_test  = np.asarray(y_test_pred, dtype=float)

    n_cal = len(y_cal_t)
    if n_cal < 10:
        q    = float(np.std(y_cal_t) * 2)
        note = 'calibration_set_too_small'
    else:
        scores = np.abs(y_cal_t - y_cal_p)
        level  = min(np.ceil((1 - alpha) * (n_cal + 1)) / n_cal, 1.0)
        q      = float(np.quantile(scores, level))
        note   = 'ok'

    intervals = np.column_stack([y_test - q, y_test + q])
    return {
        'q': q, 'coverage_target': 1 - alpha,
        'intervals': intervals.tolist(),
        'interval_width': 2 * q,
        'n_calibration': n_cal, 'note': note,
    }


def ensemble_uncertainty(fitted_estimators: list, X_test: np.ndarray) -> Dict:
    """
    Incertitude épistémique pour modèles d'ensemble (RF / XGB / LGB).
    Utilise la dispersion des arbres individuels.

    std faible (< 0.5)   → le modèle est CONFIANT
    std élevé  (> 1.5)   → le modèle est INCERTAIN → afficher ⚠️ dans l'UI

    score de confiance = max(P(High), P(Low)) parmi les N arbres
      → 1.0 si tous les arbres sont d'accord
      → 0.5 si les arbres sont divisés 50/50
    """
    preds = np.array([tree.predict(X_test) for tree in fitted_estimators])
    mean_pred  = np.mean(preds, axis=0)
    std_pred   = np.std(preds,  axis=0)
    ci_lo      = np.percentile(preds, 2.5,  axis=0)
    ci_hi      = np.percentile(preds, 97.5, axis=0)
    pct_high   = np.mean(preds >= THRESHOLD_DEFAULT, axis=0)
    conf_score = np.maximum(pct_high, 1 - pct_high)

    return {
        'per_sample': {
            'mean': mean_pred.tolist(), 'std': std_pred.tolist(),
            'ci_lo': ci_lo.tolist(), 'ci_hi': ci_hi.tolist(),
            'conf_score': conf_score.tolist(),
        },
        'summary': {
            'mean_std':              float(np.mean(std_pred)),
            'pct_high_confidence':   float(np.mean(conf_score >= 0.75) * 100),
            'pct_uncertain':         float(np.mean(std_pred > 1.5) * 100),
            'n_estimators':          len(fitted_estimators),
        },
    }


def confidence_score(
    y_pred_continuous: np.ndarray,
    threshold: float = THRESHOLD_DEFAULT,
    k: float = CONF_K_SIGMOID,
) -> np.ndarray:
    """
    Score de confiance sigmoïde pour la classification Low/High.

    conf(x) = 1 / (1 + exp(−k × |x − threshold|))

      x = 4.9  → dist=0.1 → conf≈51%  (très incertain, proche du seuil)
      x = 3.0  → dist=2.0 → conf≈95%  (confiant : Low)
      x = 8.0  → dist=3.0 → conf≈98%  (confiant : High)

    Utilisé dans l'UI NeuroCap pour afficher "Concentré (98%)" ou "⚠️ Incertain (54%)"
    """
    yp   = np.asarray(y_pred_continuous, dtype=float)
    dist = np.abs(yp - threshold)
    return 1.0 / (1.0 + np.exp(-k * dist))


# ═════════════════════════════════════════════════════════════════════════════
# ███  NIVEAU 4 — ROBUSTESSE & STABILITÉ                                  ███
# ═════════════════════════════════════════════════════════════════════════════

def stability_analysis(fold_metrics_list: List[Dict]) -> Dict:
    """
    Analyse de stabilité des métriques à travers les folds LOSO.

    Pour chaque métrique (mae, rmse, r2), calcule :
      mean    : performance moyenne
      std     : écart-type inter-folds (faible = stable)
      cv      : coefficient de variation = std/|mean| × 100%
      iqr     : interquartile range
      min/max : valeurs extrêmes

    Stability Score (0-100) :
      score = 100 × (1 − mean_cv_normalized)
      > 80  → modèle très stable (déployable avec confiance)
      60-80 → modèle acceptable
      < 60  → instable → ne pas déployer sans investigation

    Un modèle avec AUC=0.70 mais CV=15% est MOINS fiable qu'un modèle
    avec AUC=0.65 et CV=5%.
    """
    if not fold_metrics_list:
        return {}

    metrics_keys = [k for k in fold_metrics_list[0].keys()
                    if k not in ('n_samples', 'subject')]

    result: Dict[str, Dict] = {}
    for key in metrics_keys:
        vals = np.array([m.get(key, np.nan) for m in fold_metrics_list],
                        dtype=float)
        vals = vals[~np.isnan(vals)]
        if len(vals) == 0:
            continue
        mean_val = float(np.mean(vals))
        std_val  = float(np.std(vals, ddof=1)) if len(vals) > 1 else 0.0
        cv       = float(abs(std_val / mean_val) * 100) if abs(mean_val) > 1e-6 else 0.0
        result[key] = {
            'mean':   mean_val,
            'std':    std_val,
            'cv_pct': cv,
            'min':    float(np.min(vals)),
            'max':    float(np.max(vals)),
            'iqr':    float(np.percentile(vals, 75) - np.percentile(vals, 25)),
            'n_folds': len(vals),
        }

    return result


def bias_variance_decomposition(
    y_true: np.ndarray,
    y_preds_multiple_runs: List[np.ndarray],
) -> Dict:
    """
    Décomposition Biais² − Variance − Bruit irréductible du MSE.

    MSE = Biais² + Variance + Bruit_irréductible

    Biais²   : erreur systématique du modèle (prédiction moyenne ≠ réalité)
    Variance : instabilité des prédictions (sensibilité aux données train)
    Bruit    : bruit irréductible des labels (auto-évaluation subjective 0-10)

    Usage : passer les prédictions de chaque fold LOSO comme y_preds_multiple_runs.

    Interprétation pour NeuroCap :
      Biais² élevé  → le modèle est mal adapté (under-fitting)
      Variance élevée → le modèle over-fit sur les sujets d'entraînement
      Bruit élevé   → la tâche est intrinsèquement difficile (labels bruités)
    """
    yt = np.asarray(y_true, dtype=float)
    preds = np.array([np.asarray(p, dtype=float) for p in y_preds_multiple_runs])
    # preds : shape (n_models/folds, n_samples)
    # Aligner les tailles
    min_n = min(len(yt), preds.shape[1])
    yt    = yt[:min_n]
    preds = preds[:, :min_n]

    mean_pred  = np.mean(preds, axis=0)             # E[ŷ] pour chaque exemple
    bias_sq    = float(np.mean((mean_pred - yt) ** 2))
    variance   = float(np.mean(np.var(preds, axis=0, ddof=1)))
    total_mse  = float(np.mean((preds - yt[None, :]) ** 2))
    noise_est  = max(total_mse - bias_sq - variance, 0.0)

    return {
        'total_mse':       total_mse,
        'bias_squared':    bias_sq,
        'variance':        variance,
        'irreducible_noise': noise_est,
        'pct_bias':        float(bias_sq   / total_mse * 100) if total_mse > 0 else 0,
        'pct_variance':    float(variance  / total_mse * 100) if total_mse > 0 else 0,
        'pct_noise':       float(noise_est / total_mse * 100) if total_mse > 0 else 0,
        'n_runs': len(y_preds_multiple_runs), 'n_samples': min_n,
        'interpretation': (
            'high_bias (under-fitting)'    if bias_sq > variance * 2 else
            'high_variance (over-fitting)' if variance > bias_sq * 2 else
            'balanced'
        ),
    }


def per_subject_metrics(
    subjects: List[int],
    yt_per_subject: Dict[int, List[float]],
    yp_per_subject: Dict[int, List[float]],
    threshold: float = THRESHOLD_DEFAULT,
) -> Dict:
    """
    Calcule les métriques MAE, R², AUC et Sensitivity/Specificity
    pour chaque sujet LOSO individuellement.

    Permet d'identifier :
      - Les sujets "faciles" (R² élevé → profil EEG typique)
      - Les sujets "difficiles" (R² négatif → profil EEG atypique)
      - Les outliers (AUC < 0.40 → le modèle prédit à l'envers pour ce sujet)

    Usage dans NeuroCap : alerter l'utilisateur si son profil est "atypique"
    et proposer une session de calibration personnalisée.
    """
    per_subj = {}
    for sid in subjects:
        yt = np.array(yt_per_subject.get(sid, []), dtype=float)
        yp = np.array(yp_per_subject.get(sid, []), dtype=float)
        if len(yt) < 3:
            per_subj[sid] = {'n_samples': len(yt), 'note': 'too_few_samples'}
            continue
        m = compute_full_metrics(yt, yp, threshold)
        m['subject_id'] = sid
        per_subj[sid] = m

    # Statistiques globales
    r2_vals  = [m['r2']      for m in per_subj.values() if 'r2'      in m]
    auc_vals = [m['auc_roc'] for m in per_subj.values() if 'auc_roc' in m]
    mae_vals = [m['mae']     for m in per_subj.values() if 'mae'     in m]

    best_subj  = max(per_subj, key=lambda s: per_subj[s].get('r2', -99),  default=None)
    worst_subj = min(per_subj, key=lambda s: per_subj[s].get('r2',  99),  default=None)

    return {
        'per_subject': per_subj,
        'summary': {
            'mean_r2':    float(np.mean(r2_vals))  if r2_vals  else 0.0,
            'mean_auc':   float(np.mean(auc_vals)) if auc_vals else 0.5,
            'mean_mae':   float(np.mean(mae_vals)) if mae_vals else 0.0,
            'std_r2':     float(np.std(r2_vals))   if r2_vals  else 0.0,
            'best_subject':  best_subj,
            'worst_subject': worst_subj,
            'pct_r2_positive': float(np.mean(np.array(r2_vals) > 0) * 100) if r2_vals else 0,
        },
    }


def learning_curve_loso(
    subjects: List[int],
    X_all: np.ndarray,
    y_all: np.ndarray,
    sids_all: np.ndarray,
    model_factory,
    metric: str = 'auc_roc',
    threshold: float = THRESHOLD_DEFAULT,
    min_subjects: int = 3,
) -> Dict:
    """
    Courbe d'apprentissage en fonction du nombre de sujets d'entraînement.
    Répond à : "combien de sujets faut-il pour avoir un AUC stable ?"

    Algorithme :
      Pour k = min_subjects, ..., N−1 sujets d'entraînement :
        Test sur le sujet restant (LOSO), entraîne sur k sujets aléatoires
        Répète 5 fois → moyenne et std pour k sujets

    Utilité commerciale :
      → Justifie combien de sujets collecter pour la prochaine version
      → Montre la courbe de saturation (au-delà de X sujets, gain marginal)
    """
    from sklearn.preprocessing import StandardScaler
    unique_s = np.array(subjects)
    n_s      = len(unique_s)
    rng      = np.random.default_rng(42)

    curve_means, curve_stds, k_values = [], [], []

    for k in range(min_subjects, n_s):
        fold_scores = []
        for _ in range(min(5, n_s - k)):
            # Choisir k sujets train, 1 sujet test
            perm      = rng.permutation(unique_s)
            train_s   = perm[:k]
            test_s    = perm[k]

            tr_mask   = np.isin(sids_all, train_s)
            te_mask   = sids_all == test_s
            if tr_mask.sum() < 5 or te_mask.sum() < 2:
                continue

            sc = StandardScaler()
            Xtr = sc.fit_transform(X_all[tr_mask])
            Xte = sc.transform(X_all[te_mask])
            ytr = y_all[tr_mask]
            yte = y_all[te_mask]

            try:
                m = model_factory()
                m.fit(Xtr, ytr)
                yp = m.predict(Xte)
                mets = compute_full_metrics(yte, yp, threshold)
                fold_scores.append(mets.get(metric, 0.0))
            except Exception:
                continue

        if fold_scores:
            k_values.append(k)
            curve_means.append(float(np.mean(fold_scores)))
            curve_stds.append(float(np.std(fold_scores)))

    return {
        'k_subjects': k_values,
        'means': curve_means,
        'stds':  curve_stds,
        'metric': metric,
        'saturation_k': _find_saturation(k_values, curve_means),
    }


# ═════════════════════════════════════════════════════════════════════════════
# ███  NIVEAU 5 — DÉPLOIEMENT RÉGLEMENTAIRE & CONFORMITÉ ($100K)          ███
# ═════════════════════════════════════════════════════════════════════════════

def decision_curve_analysis(
    y_true: np.ndarray,
    y_pred_continuous: np.ndarray,
    threshold_range: Tuple[float, float] = (0.1, 0.9),
    n_thresholds: int = 50,
    threshold_bin: float = THRESHOLD_DEFAULT,
) -> Dict:
    """
    Decision Curve Analysis (DCA) — Vickers & Elkin, 2006.
    Standard pour évaluer l'utilité clinique d'un système de décision.

    Net Clinical Benefit (NB) :
      NB(t) = TPR − FPR × (t / (1−t))
      t = seuil de probabilité à partir duquel on "intervient"

    Interprétation :
      NB > 0            → le modèle est utile (intervenir selon le modèle)
      NB > NB_all       → meilleur que "intervenir pour tous"
      NB > NB_none      → meilleur que "n'intervenir pour personne"
      Si la courbe est au-dessus de "Treat All", le modèle APPORTE une valeur.

    Pour NeuroCap : "intervenir" = alerter l'utilisateur / recommander une pause
    Seuil t = probabilité P(High) au-delà duquel on envoie une alerte.
    """
    yt  = np.asarray(y_true, dtype=float)
    yp  = np.asarray(y_pred_continuous, dtype=float)
    ytb = bin_scores(yt, threshold_bin)
    prob_high = _to_proba(yp, threshold_bin, CONF_K_SIGMOID)

    prevalence = float(np.mean(ytb))
    thresholds = np.linspace(threshold_range[0], threshold_range[1], n_thresholds)

    nb_model, nb_all, nb_none = [], [], []

    for t in thresholds:
        yp_bin = (prob_high >= t).astype(int)
        n = len(ytb)
        tp = float(np.sum((yp_bin == 1) & (ytb == 1)))
        fp = float(np.sum((yp_bin == 1) & (ytb == 0)))

        # Net benefit du modèle
        nb_m = (tp / n) - (fp / n) * (t / (1 - t + 1e-8))
        # Net benefit "traiter tout le monde"
        nb_a = prevalence - (1 - prevalence) * (t / (1 - t + 1e-8))

        nb_model.append(float(nb_m))
        nb_all.append(float(nb_a))
        nb_none.append(0.0)

    # Zone où le modèle est utile (NB > 0 ET > NB_all)
    nb_m_arr   = np.array(nb_model)
    nb_a_arr   = np.array(nb_all)
    useful_mask = (nb_m_arr > 0) & (nb_m_arr > nb_a_arr)
    t_range_useful = (
        float(thresholds[useful_mask][0])  if useful_mask.any() else None,
        float(thresholds[useful_mask][-1]) if useful_mask.any() else None,
    )

    return {
        'thresholds':          thresholds.tolist(),
        'nb_model':            nb_model,
        'nb_treat_all':        nb_all,
        'nb_treat_none':       nb_none,
        'prevalence':          prevalence,
        'useful_threshold_range': t_range_useful,
        'model_is_useful':     bool(useful_mask.any()),
    }


def delong_auc_ci(
    y_true_binary: np.ndarray,
    y_pred_score: np.ndarray,
    alpha: float = CONF_ALPHA,
) -> Dict:
    """
    Intervalle de confiance analytique de l'AUC — méthode DeLong (1988).
    Plus précis que le bootstrap pour l'AUC (formule exacte, pas d'approximation).

    Basé sur : DeLong, DeLong & Clarke-Pearson (1988)
    "Comparing the Areas under Two or More Correlated Receiver Operating
    Characteristic Curves: A Nonparametric Approach"

    Retourne : AUC, CI lo, CI hi, z-score, p-value (H₀: AUC=0.5)
    """
    yt = np.asarray(y_true_binary, dtype=float)
    yp = np.asarray(y_pred_score,  dtype=float)

    pos_mask = yt == 1
    neg_mask = yt == 0
    n_pos = pos_mask.sum()
    n_neg = neg_mask.sum()

    if n_pos == 0 or n_neg == 0:
        return {'auc': 0.5, 'ci_lo': 0.0, 'ci_hi': 1.0, 'p_value': 1.0,
                'note': 'single_class'}

    pos_scores = yp[pos_mask]
    neg_scores = yp[neg_mask]

    try:
        auc = float(roc_auc_score(yt, yp))
    except Exception:
        return {'auc': 0.5, 'ci_lo': 0.0, 'ci_hi': 1.0, 'p_value': 1.0}

    # Structural components for variance (DeLong method)
    Vx = np.array([
        np.mean((pos_scores[i] > neg_scores).astype(float) +
                0.5 * (pos_scores[i] == neg_scores).astype(float))
        for i in range(n_pos)
    ])
    Vy = np.array([
        np.mean((pos_scores > neg_scores[j]).astype(float) +
                0.5 * (pos_scores == neg_scores[j]).astype(float))
        for j in range(n_neg)
    ])

    var_auc = (np.var(Vx, ddof=1) / n_pos + np.var(Vy, ddof=1) / n_neg)
    se_auc  = float(np.sqrt(max(var_auc, 1e-10)))

    z_alpha = sp_stats.norm.ppf(1 - alpha / 2)
    ci_lo   = float(np.clip(auc - z_alpha * se_auc, 0, 1))
    ci_hi   = float(np.clip(auc + z_alpha * se_auc, 0, 1))

    # p-value H0: AUC = 0.5
    z_stat  = (auc - 0.5) / (se_auc + 1e-10)
    p_value = float(2 * (1 - sp_stats.norm.cdf(abs(z_stat))))

    return {
        'auc':         auc,
        'ci_lo':       ci_lo,
        'ci_hi':       ci_hi,
        'se':          se_auc,
        'z_stat':      float(z_stat),
        'p_value':     p_value,
        'significant': p_value < alpha,
        'method':      'DeLong 1988',
        'n_pos':       int(n_pos),
        'n_neg':       int(n_neg),
    }


def generate_professional_report(
    target: str,
    model_name: str,
    exp: str,
    full_metrics: Dict,
    bootstrap_results: Optional[Dict] = None,
    permutation_results: Optional[Dict] = None,
    stability_result: Optional[Dict] = None,
    calibration_result: Optional[Dict] = None,
    bland_altman_result: Optional[Dict] = None,
    icc_result: Optional[Dict] = None,
    delong_result: Optional[Dict] = None,
    dca_result: Optional[Dict] = None,
    bias_var_result: Optional[Dict] = None,
) -> str:
    """
    Génère un rapport professionnel complet en Markdown.
    Exportable en PDF / Word pour présentation commerciale / investisseurs.

    Couvre les 5 niveaux de métriques avec interprétations automatiques.
    """
    ts    = datetime.now().strftime('%Y-%m-%d %H:%M')
    lines = []

    def h1(t): lines.append(f'\n# {t}\n')
    def h2(t): lines.append(f'\n## {t}\n')
    def h3(t): lines.append(f'\n### {t}\n')
    def row(k, v, note=''): lines.append(f'| {k} | {v} | {note} |')
    def sep(): lines.append('|---|---|---|')

    lines.append(f'# NeuroCap — Rapport Professionnel de Performance')
    lines.append(f'**Target :** `{target}`  |  **Modèle :** `{model_name}`  '
                 f'|  **Exp :** `{exp}`  |  **Date :** {ts}\n')

    # ── Niveau 1 : Métriques cliniques ─────────────────────────────────────
    h2('Niveau 1 — Métriques Cliniques')
    h3('Régression')
    lines.append('| Métrique | Valeur | Interprétation |'); sep()
    row('MAE',  f"{full_metrics.get('mae',  0):.4f}", 'Erreur absolue moyenne (0-10)')
    row('RMSE', f"{full_metrics.get('rmse', 0):.4f}", 'Erreur quadratique moyenne')
    row('R²',   f"{full_metrics.get('r2',   0):.4f}", '1=parfait, 0=moyenne, <0=pire')

    h3('Classification Binée (Low:0-5 / High:5-10)')
    lines.append('| Métrique | Valeur | Baseline aléatoire |'); sep()
    row('AUC ROC',           f"{full_metrics.get('auc_roc',0):.4f}",          '0.500')
    row('PR-AUC',            f"{full_metrics.get('pr_auc',0):.4f}",           f"{full_metrics.get('pct_high',0.5):.3f}")
    row('Sensitivity (TPR)', f"{full_metrics.get('sensitivity',0):.4f}",      '0.500')
    row('Specificity (TNR)', f"{full_metrics.get('specificity',0):.4f}",      '0.500')
    row('PPV (Precision)',   f"{full_metrics.get('ppv',0):.4f}",              '—')
    row('NPV',               f"{full_metrics.get('npv',0):.4f}",              '—')
    row('Balanced Accuracy', f"{full_metrics.get('balanced_accuracy',0):.4f}",'0.500')
    row('MCC',               f"{full_metrics.get('mcc',0):.4f}",             '0.000')
    row('G-Mean',            f"{full_metrics.get('g_mean',0):.4f}",          '0.500')
    row('F1 macro',          f"{full_metrics.get('f1_macro',0):.4f}",        '0.500')
    row('LR+',               f"{full_metrics.get('lr_plus',0):.3f}",         '>10 = très utile')
    row('LR−',               f"{full_metrics.get('lr_minus',0):.3f}",        '<0.1 = très utile')
    row('Cohen κ',           f"{full_metrics.get('kappa',0):.4f}",           '0.000')
    row('Brier Score',       f"{full_metrics.get('brier_score',0):.4f}",     '< 0.20 objectif')

    # ── Niveau 2 : CI & Tests statistiques ─────────────────────────────────
    h2('Niveau 2 — Intervalles de Confiance (Bootstrap 95%)')
    if bootstrap_results:
        lines.append('| Métrique | Valeur | CI 95% | Significatif |'); sep()
        for k, label_k in [
            ('auc_roc', 'AUC ROC'), ('f1_macro', 'F1 macro'),
            ('sensitivity', 'Sensitivity'), ('specificity', 'Specificity'),
            ('mcc', 'MCC'), ('r2', 'R²'),
        ]:
            ci = bootstrap_results.get(k, {})
            m = ci.get('mean', 0); lo = ci.get('ci_lo', 0); hi = ci.get('ci_hi', 0)
            sig = '✅' if (k in ('auc_roc','f1_macro') and lo > 0.50) else \
                  ('✅' if (k == 'r2' and lo > 0.0) else '—')
            row(label_k, f'{m:.4f}', f'[{lo:.4f}, {hi:.4f}]  {sig}')
    else:
        lines.append('_Bootstrap CI non calculé pour ce modèle_\n')

    h3('Tests de Permutation')
    if permutation_results:
        lines.append('| Métrique | Observé | p-value | Significatif |'); sep()
        for k, label_k in [('r2', 'R²'), ('auc_roc', 'AUC ROC')]:
            res = permutation_results.get(k, {})
            sig = '✅ p<0.05' if res.get('significant', False) else '❌ ns'
            lines.append(f"| {label_k} | {res.get('observed', 0):.4f} "
                         f"| p={res.get('p_value', 1):.4f} | {sig} |")
    else:
        lines.append('_Tests de permutation non calculés_\n')

    # ── Niveau 3 : Qualité clinique ─────────────────────────────────────────
    h2('Niveau 3 — Qualité Clinique & Incertitude')
    if calibration_result:
        h3('Calibration')
        lines.append('| Métrique | Valeur | Objectif |'); sep()
        row('ECE',         f"{calibration_result.get('ece',0):.4f}",         '< 0.05')
        row('MCE',         f"{calibration_result.get('mce',0):.4f}",         '< 0.10')
        row('Brier Score', f"{calibration_result.get('brier_score',0):.4f}", '< 0.20')
        row('Log-Loss',    f"{calibration_result.get('log_loss',0):.4f}",    'minimiser')

    if bland_altman_result:
        h3('Bland-Altman (Accord Clinique)')
        lines.append('| Métrique | Valeur | Interprétation |'); sep()
        row('Biais',       f"{bland_altman_result.get('bias',0):+.4f}",           'proche 0 = pas de biais systématique')
        row('LoA lower',   f"{bland_altman_result.get('loa_lower',0):+.4f}",      'limite inférieure d\'accord')
        row('LoA upper',   f"{bland_altman_result.get('loa_upper',0):+.4f}",      'limite supérieure d\'accord')
        row('LoA width',   f"±{bland_altman_result.get('loa_width',0)/2:.4f}",    '< ±2 pts : excellent')
        row('% dans LoA',  f"{bland_altman_result.get('pct_within_loa',0):.1f}%", '≥ 95% requis')
        ok = bland_altman_result.get('clinical_acceptable', False)
        row('Accord clinique', '✅ OUI' if ok else '⚠️ NON', '')

    if icc_result:
        h3('ICC (Intraclass Correlation)')
        row('ICC(2,1)', f"{icc_result.get('icc',0):.4f}",
            icc_result.get('interpretation', ''))

    # ── Niveau 4 : Robustesse ───────────────────────────────────────────────
    h2('Niveau 4 — Robustesse & Stabilité')
    if stability_result:
        h3('Stabilité LOSO (Coefficient de Variation)')
        lines.append('| Métrique | Moyenne | Std | CV% | Interprétation |'); sep()
        for k, label_k in [('r2', 'R²'), ('auc_roc', 'AUC ROC'), ('mae', 'MAE')]:
            s = stability_result.get(k, {})
            if s:
                cv = s.get('cv_pct', 0)
                interp = '🟢 stable' if cv < 15 else '🟡 moderate' if cv < 30 else '🔴 unstable'
                lines.append(f"| {label_k} | {s.get('mean',0):.4f} | "
                              f"{s.get('std',0):.4f} | {cv:.1f}% | {interp} |")

    if bias_var_result:
        h3('Décomposition Biais-Variance')
        lines.append('| Composante | Valeur | % du MSE |'); sep()
        row('Biais²',    f"{bias_var_result.get('bias_squared',0):.4f}",
            f"{bias_var_result.get('pct_bias',0):.1f}%")
        row('Variance',  f"{bias_var_result.get('variance',0):.4f}",
            f"{bias_var_result.get('pct_variance',0):.1f}%")
        row('Bruit irréductible', f"{bias_var_result.get('irreducible_noise',0):.4f}",
            f"{bias_var_result.get('pct_noise',0):.1f}%")
        row('MSE total', f"{bias_var_result.get('total_mse',0):.4f}", '100%')
        lines.append(f"\n**Diagnostic : {bias_var_result.get('interpretation','')}**\n")

    # ── Niveau 5 : Tests statistiques avancés ──────────────────────────────
    h2('Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)')

    if delong_result:
        h3('AUC — Méthode DeLong (CI analytique exact)')
        lines.append('| | Valeur |'); lines.append('|---|---|')
        lines.append(f"| AUC | {delong_result.get('auc',0):.4f} |")
        lines.append(f"| CI 95% | [{delong_result.get('ci_lo',0):.4f}, "
                     f"{delong_result.get('ci_hi',0):.4f}] |")
        lines.append(f"| p-value | {delong_result.get('p_value',1):.6f} |")
        lines.append(f"| Significatif | {'✅ OUI' if delong_result.get('significant') else '❌ NON'} |")

    if dca_result:
        h3('Decision Curve Analysis (Utilité Clinique)')
        useful = dca_result.get('model_is_useful', False)
        t_range = dca_result.get('useful_threshold_range', (None, None))
        lines.append(f"**Modèle cliniquement utile : {'✅ OUI' if useful else '❌ NON'}**\n")
        if useful and t_range[0] is not None:
            lines.append(f"Zone d'utilité : seuil de décision entre "
                         f"{t_range[0]:.2f} et {t_range[1]:.2f}\n")
        else:
            lines.append("Le modèle n'apporte pas de bénéfice net par rapport aux "
                         "stratégies 'traiter tous' ou 'ne traiter personne'.\n")

    # ── Contexte & recommandations ──────────────────────────────────────────
    h2('Contexte & Recommandations')
    lines.append(
        '| Conditions | Valeur |\n|---|---|\n'
        f'| Nb électrodes | 1 (FP2 — préfrontal) |\n'
        f'| Protocole validation | LOSO cross-sujet (strict) |\n'
    )

    auc = full_metrics.get('auc_roc', 0.5)
    if auc >= 0.70:
        lines.append('\n✅ **Le modèle est performant pour un système mono-électrode.**\n')
    elif auc >= 0.60:
        lines.append('\n🟡 **Performance modérée. Recommander collecte de données supplémentaires.**\n')
    else:
        lines.append('\n🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**\n')

    lines.append(f'\n---\n*Rapport généré automatiquement par NeuroCap metrics_professional.py — {ts}*\n')
    return '\n'.join(lines)


# ═════════════════════════════════════════════════════════════════════════════
# ███  VISUALISATIONS PROFESSIONNELLES (5 NIVEAUX)                        ███
# ═════════════════════════════════════════════════════════════════════════════

def plot_reliability_diagram(
    y_true: np.ndarray, y_pred_continuous: np.ndarray,
    model_name: str, out_path: Optional[Path] = None,
    threshold: float = THRESHOLD_DEFAULT,
) -> None:
    """Reliability Diagram — calibration visuelle. Diagonale = parfait."""
    cal = calibration_analysis(y_true, y_pred_continuous, n_bins=10, threshold=threshold)
    rd  = cal['reliability_diagram']
    ba, bc, bn = (np.array(rd[k]) for k in
                  ('bin_accuracies', 'bin_confidences', 'bin_counts'))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 8),
                                    gridspec_kw={'height_ratios': [3, 1]})
    fig.suptitle(f'Reliability Diagram (Calibration) — {model_name}\n'
                 f"ECE={cal['ece']:.4f}  Brier={cal['brier_score']:.4f}  "
                 f"MCE={cal['mce']:.4f}", fontsize=10)
    ax1.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Calibration parfaite')
    mask = bn > 0
    if mask.any():
        ax1.plot(bc[mask], ba[mask], 'o-', color='#E74C3C', lw=2,
                 markersize=7, label=f'Modèle (ECE={cal["ece"]:.4f})')
        ax1.fill_between(bc[mask], ba[mask], bc[mask], alpha=0.15,
                         color='#E74C3C', label='Gap calibration')
    ax1.set_xlim(0, 1); ax1.set_ylim(0, 1)
    ax1.set_xlabel('Confiance prédite P(High)')
    ax1.set_ylabel('Fraction vrais High')
    ax1.legend(fontsize=9); ax1.grid(alpha=0.3)
    if bn.sum() > 0:
        ax2.bar(bc, bn / bn.sum(), width=0.08, color='#3498DB',
                alpha=0.7, edgecolor='white')
    ax2.set_xlabel('Confiance prédite'); ax2.set_ylabel('Fraction')
    ax2.set_xlim(0, 1); ax2.grid(alpha=0.3)
    plt.tight_layout()
    if out_path: plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
    plt.close()


def plot_bland_altman(
    y_true: np.ndarray, y_pred: np.ndarray,
    model_name: str, out_path: Optional[Path] = None,
) -> None:
    """Graphique de Bland-Altman — accord entre prédiction et réalité."""
    ba   = bland_altman_analysis(y_true, y_pred)
    means = np.array(ba['mean_values'])
    diffs = np.array(ba['differences'])

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(means, diffs, alpha=0.4, s=18, color='#2980B9')
    ax.axhline(ba['bias'],      color='#E74C3C', lw=2,   label=f"Biais={ba['bias']:+.3f}")
    ax.axhline(ba['loa_upper'], color='#F39C12', lw=1.5, linestyle='--',
               label=f"LoA+={ba['loa_upper']:+.3f}")
    ax.axhline(ba['loa_lower'], color='#F39C12', lw=1.5, linestyle='--',
               label=f"LoA−={ba['loa_lower']:+.3f}")
    ax.axhline(0, color='black', lw=0.8, linestyle=':')
    ax.fill_between([means.min(), means.max()],
                    ba['loa_lower'], ba['loa_upper'], alpha=0.08, color='#F39C12')
    ax.set_xlabel('Moyenne (prédit+réel)/2')
    ax.set_ylabel('Différence (prédit−réel)')
    acc = '✅' if ba['clinical_acceptable'] else '⚠️'
    ax.set_title(f'Bland-Altman — {model_name}\n'
                 f"LoA=[{ba['loa_lower']:+.2f}, {ba['loa_upper']:+.2f}]  "
                 f"{ba['pct_within_loa']:.1f}% dans limites  {acc}")
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    plt.tight_layout()
    if out_path: plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
    plt.close()


def plot_bootstrap_ci_bars(
    ci_results: Dict, model_name: str, out_path: Optional[Path] = None,
) -> None:
    """Barplot des métriques clés avec barres d'erreur Bootstrap 95% CI."""
    items = [
        ('auc_roc',          'AUC ROC',    '#E74C3C'),
        ('f1_macro',         'F1 macro',   '#27AE60'),
        ('sensitivity',      'Sensitivity','#2980B9'),
        ('specificity',      'Specificity','#8E44AD'),
        ('mcc',              'MCC',        '#F39C12'),
        ('balanced_accuracy','Bal.Acc.',   '#16A085'),
    ]
    labels  = [i[1] for i in items]
    colors  = [i[2] for i in items]
    means   = [ci_results.get(i[0], {}).get('mean',  0) for i in items]
    ci_lo   = [ci_results.get(i[0], {}).get('ci_lo', 0) for i in items]
    ci_hi   = [ci_results.get(i[0], {}).get('ci_hi', 0) for i in items]
    err_lo  = [max(0, m - lo) for m, lo in zip(means, ci_lo)]
    err_hi  = [max(0, hi - m) for m, hi in zip(means, ci_hi)]

    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(x, means, color=colors, alpha=0.8, edgecolor='white',
                  yerr=[err_lo, err_hi], capsize=5, error_kw={'lw': 2})
    ax.axhline(0.5, color='black', lw=1.2, linestyle='--', label='Baseline (0.5)')
    for bar, m, lo, hi in zip(bars, means, ci_lo, ci_hi):
        ax.text(bar.get_x() + bar.get_width()/2, m + 0.02,
                f'{m:.3f}\n[{lo:.2f},{hi:.2f}]',
                ha='center', va='bottom', fontsize=7.5, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Valeur'); ax.set_ylim(0, 1.15)
    ax.set_title(f'Bootstrap 95% CI (N={N_BOOTSTRAP}) — {model_name}')
    ax.legend(fontsize=9); ax.grid(alpha=0.3, axis='y')
    plt.tight_layout()
    if out_path: plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
    plt.close()


def plot_full_confusion_matrix(
    y_true: np.ndarray, y_pred_continuous: np.ndarray,
    model_name: str, out_path: Optional[Path] = None,
    threshold: float = THRESHOLD_DEFAULT,
) -> None:
    """Matrice de confusion annotée avec TOUTES les métriques cliniques."""
    yt_b = bin_scores(y_true, threshold)
    yp_b = bin_scores(y_pred_continuous, threshold)
    m    = compute_full_metrics(y_true, y_pred_continuous, threshold)
    cm   = confusion_matrix(yt_b, yp_b, labels=[0, 1])
    cm_n = cm.astype(float) / (cm.sum(axis=1, keepdims=True) + 1e-8)

    fig, (ax_cm, ax_t) = plt.subplots(1, 2, figsize=(12, 5),
                                       gridspec_kw={'width_ratios': [1, 1]})
    fig.suptitle(f'Analyse Clinique Complète — {model_name}', fontsize=12)

    im = ax_cm.imshow(cm_n, cmap='Blues', vmin=0, vmax=1)
    ax_cm.set_xticks([0, 1]); ax_cm.set_yticks([0, 1])
    ax_cm.set_xticklabels(['Low\n(prédit)', 'High\n(prédit)'], fontsize=11)
    ax_cm.set_yticklabels(['Low\n(réel)', 'High\n(réel)'], fontsize=11)
    for i in range(2):
        for j in range(2):
            ax_cm.text(j, i, f'{cm[i,j]}\n({cm_n[i,j]:.1%})',
                       ha='center', va='center', fontsize=12,
                       color='white' if cm_n[i,j] > 0.5 else 'black',
                       fontweight='bold')
    ax_cm.set_title('Matrice de confusion')
    plt.colorbar(im, ax=ax_cm, fraction=0.04)

    ax_t.axis('off')
    rows = [
        ('Sensitivity',      f"{m['sensitivity']:.4f}",      'vrais High détectés'),
        ('Specificity',      f"{m['specificity']:.4f}",      'vrais Low détectés'),
        ('PPV (Precision)',  f"{m['ppv']:.4f}",              'précision sur High'),
        ('NPV',              f"{m['npv']:.4f}",              'précision sur Low'),
        ('Bal. Accuracy',    f"{m['balanced_accuracy']:.4f}",'corrigée déséquilibre'),
        ('MCC',              f"{m['mcc']:.4f}",              '[-1,+1] 0=aléatoire'),
        ('G-Mean',           f"{m['g_mean']:.4f}",           '√(Sens×Spec)'),
        ('AUC ROC',          f"{m['auc_roc']:.4f}",          'discriminant continu'),
        ('PR-AUC',           f"{m['pr_auc']:.4f}",           'si déséquilibre'),
        ('LR+',              f"{m['lr_plus']:.3f}",          '>10 = très utile'),
        ('LR−',              f"{m['lr_minus']:.3f}",         '<0.1 = très utile'),
        ('Cohen κ',          f"{m['kappa']:.4f}",            'accord>hasard'),
    ]
    tbl = ax_t.table(cellText=rows, colLabels=['Métrique', 'Valeur', 'Description'],
                     cellLoc='center', loc='center', bbox=[0, 0, 1, 1])
    tbl.auto_set_font_size(False); tbl.set_fontsize(9)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor('#2C3E50'); cell.set_text_props(color='white', fontweight='bold')
        elif r % 2 == 0:
            cell.set_facecolor('#ECF0F1')
    plt.tight_layout()
    if out_path: plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
    plt.close()


def plot_wilcoxon_heatmap(
    wilcoxon_results: Dict, model_names: List[str],
    metric: str = '', title: str = '',
    out_path: Optional[Path] = None,
) -> None:
    """Heatmap p-values Wilcoxon — vert=significatif, rouge=pas de différence."""
    n = len(model_names)
    p_matrix = np.ones((n, n))
    for i in range(n):
        for j in range(n):
            if i == j: continue
            for key in [f'{model_names[i]}_vs_{model_names[j]}',
                        f'{model_names[j]}_vs_{model_names[i]}']:
                if key in wilcoxon_results:
                    p_matrix[i, j] = wilcoxon_results[key].get('p_value', 1.0)
                    break

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(p_matrix, cmap=plt.cm.RdYlGn_r, vmin=0, vmax=0.2)
    plt.colorbar(im, ax=ax, label='p-value')
    ax.set_xticks(range(n)); ax.set_yticks(range(n))
    ax.set_xticklabels(model_names, rotation=45, ha='right', fontsize=9)
    ax.set_yticklabels(model_names, fontsize=9)
    for i in range(n):
        for j in range(n):
            if i == j:
                ax.text(j, i, '─', ha='center', va='center', fontsize=12)
            else:
                p = p_matrix[i, j]
                s = '***' if p<0.001 else ('**' if p<0.01 else ('*' if p<0.05 else 'ns'))
                ax.text(j, i, f'{p:.3f}\n{s}', ha='center', va='center',
                        fontsize=8, color='white' if p < 0.05 else 'black')
    ax.set_title(f'Tests de Wilcoxon — {metric} {title}\nVert=p<0.05 (différence significative)')
    plt.tight_layout()
    if out_path: plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
    plt.close()


def plot_per_subject_heatmap(
    per_subject_result: Dict, target: str,
    out_path: Optional[Path] = None,
) -> None:
    """Heatmap des métriques par sujet LOSO — identifie les outliers."""
    ps = per_subject_result.get('per_subject', {})
    if not ps: return

    sids = sorted([s for s, v in ps.items() if 'r2' in v])
    if not sids: return

    metrics_show = ['r2', 'auc_roc', 'mae', 'sensitivity', 'specificity', 'mcc']
    data = np.array([[ps[s].get(m, np.nan) for m in metrics_show] for s in sids])

    fig, ax = plt.subplots(figsize=(10, max(4, len(sids) * 0.4 + 2)))
    im = ax.imshow(data.T, cmap='RdYlGn', aspect='auto')
    plt.colorbar(im, ax=ax)
    ax.set_xticks(range(len(sids)))
    ax.set_xticklabels([f'S{s}' for s in sids], fontsize=8)
    ax.set_yticks(range(len(metrics_show)))
    ax.set_yticklabels(metrics_show, fontsize=9)
    for i, sid in enumerate(sids):
        for j, m in enumerate(metrics_show):
            v = ps[sid].get(m, np.nan)
            if not np.isnan(v):
                ax.text(i, j, f'{v:.2f}', ha='center', va='center', fontsize=7)
    ax.set_title(f'Performance par Sujet LOSO — {target}\nVert=bon, Rouge=mauvais')
    plt.tight_layout()
    if out_path: plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
    plt.close()


def plot_decision_curve(
    dca_result: Dict, model_name: str,
    out_path: Optional[Path] = None,
) -> None:
    """Decision Curve Analysis — Net Clinical Benefit vs seuil de décision."""
    thresholds = np.array(dca_result['thresholds'])
    nb_model   = np.array(dca_result['nb_model'])
    nb_all     = np.array(dca_result['nb_treat_all'])

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(thresholds, nb_model, color='#E74C3C', lw=2.5, label=f'Modèle : {model_name}')
    ax.plot(thresholds, nb_all,   color='#3498DB', lw=1.5, linestyle='--',
            label='Traiter tous (Treat All)')
    ax.axhline(0, color='black', lw=1.2, linestyle='-', label='Ne traiter personne')

    # Zone d'utilité
    useful = (nb_model > 0) & (nb_model > nb_all)
    if useful.any():
        ax.fill_between(thresholds, nb_model, nb_all, where=useful,
                        alpha=0.2, color='#27AE60', label='Zone d\'utilité clinique')

    ax.set_xlabel('Seuil de probabilité de décision P(High)')
    ax.set_ylabel('Net Clinical Benefit')
    ax.set_xlim(thresholds[0], thresholds[-1])
    useful_flag = dca_result.get('model_is_useful', False)
    ax.set_title(f'Decision Curve Analysis — {model_name}\n'
                 f"{'✅ Cliniquement utile' if useful_flag else '❌ Pas de bénéfice net'}")
    ax.legend(fontsize=9); ax.grid(alpha=0.3)
    plt.tight_layout()
    if out_path: plt.savefig(str(out_path), dpi=150, bbox_inches='tight')
    plt.close()


def print_metrics_summary(metrics: Dict, title: str = '') -> None:
    """Affiche un résumé console des métriques — tous niveaux."""
    sep = '─' * 70
    print(f'\n{sep}')
    if title: print(f'  {title}'); print(sep)
    print(f"  Régression  : MAE={metrics.get('mae',0):.4f}  "
          f"RMSE={metrics.get('rmse',0):.4f}  R²={metrics.get('r2',0):.4f}")
    print(f"  Classif.    : Acc={metrics.get('accuracy',0):.4f}  "
          f"BalAcc={metrics.get('balanced_accuracy',0):.4f}  MCC={metrics.get('mcc',0):.4f}")
    print(f"  Sens/Spec   : Sensitivity={metrics.get('sensitivity',0):.4f}  "
          f"Specificity={metrics.get('specificity',0):.4f}")
    print(f"  PPV/NPV     : PPV={metrics.get('ppv',0):.4f}  NPV={metrics.get('npv',0):.4f}")
    print(f"  AUC         : ROC={metrics.get('auc_roc',0):.4f}  PR={metrics.get('pr_auc',0):.4f}")
    print(f"  F1          : macro={metrics.get('f1_macro',0):.4f}  "
          f"weighted={metrics.get('f1_weighted',0):.4f}")
    print(f"  LR          : LR+={metrics.get('lr_plus',0):.3f}  "
          f"LR−={metrics.get('lr_minus',0):.3f}  κ={metrics.get('kappa',0):.4f}")
    print(sep)


# ═════════════════════════════════════════════════════════════════════════════
# FONCTIONS UTILITAIRES INTERNES
# ═════════════════════════════════════════════════════════════════════════════

def _safe_div(num: float, den: float) -> float:
    return float(num / den) if abs(den) > 1e-10 else 0.0

def _to_proba(y_pred: np.ndarray, threshold: float, k: float) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-k * (y_pred - threshold)))

def _rank_biserial(a: np.ndarray, b: np.ndarray) -> float:
    diff = a - b
    nz   = diff[diff != 0]
    if len(nz) == 0: return 0.0
    ranks  = sp_stats.rankdata(np.abs(nz))
    r_plus = np.sum(ranks[nz > 0])
    r_minus= np.sum(ranks[nz < 0])
    return float((r_plus - r_minus) / (len(nz) * (len(nz) + 1) / 2))

def _degenerate_metrics(mae: float, rmse: float, r2: float) -> Dict:
    return {
        'mae': mae, 'rmse': rmse, 'r2': r2,
        'accuracy': 1.0, 'balanced_accuracy': 0.5,
        'sensitivity': 0.0, 'specificity': 1.0,
        'ppv': 0.0, 'npv': 1.0, 'f1_macro': 0.0, 'f1_weighted': 0.0,
        'mcc': 0.0, 'g_mean': 0.0, 'auc_roc': 0.5, 'pr_auc': 0.0,
        'lr_plus': 0.0, 'lr_minus': 0.0, 'kappa': 0.0, 'brier_score': 0.25,
        'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0, 'n_samples': 0, 'pct_high': 0.0,
    }

def _find_saturation(k_vals: List[int], means: List[float]) -> Optional[int]:
    """Trouve le k où la courbe d'apprentissage se stabilise (gain < 1%)."""
    if len(means) < 3: return None
    for i in range(1, len(means) - 1):
        if abs(means[i] - means[i-1]) < 0.01 and abs(means[i+1] - means[i]) < 0.01:
            return k_vals[i]
    return None
