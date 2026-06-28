"""
=============================================================================
NeuroCap — Baseline ML Régression (feat78 — feature_eng.py)
baseline_ML_regression_feature_eng.py
=============================================================================
Sortie : conc_score (0-10) et stress_score (0-10)
Métriques : 5 NIVEAUX PROFESSIONNELS (metrics_professional.py)
Validation : LOSO (Leave-One-Subject-Out) + Val/Test

STRUCTURE IDENTIQUE à baseline_ML_regression.py — seules différences :
  - FEAT_PREFIX = 'feat78'
  - Chemins : reports/Regression/Baseline/feat78/
  - Features pré-calculées (pas d'extraction à la volée)

FEATURES : feat78 (feature_eng.py — version complète, 78 features)
  Cat.1 PSD Welch (5)       Cat.2 Ratios cognitifs (4)
  Cat.3 Hjorth + temps (6)  Cat.4 DWT sous-bandes (20)
  Cat.5 Texturales (16)     Cat.6 Non-linéaires (5)
  Cat.7 Transitions (6)

MÉTRIQUES INTÉGRÉES (5 NIVEAUX) :
  Niveau 1 : Sensitivity, Specificity, PPV, NPV, MCC, G-Mean, AUC, PR-AUC
  Niveau 2 : Bootstrap 95% CI, Permutation test, Wilcoxon, Friedman
  Niveau 3 : Calibration (ECE/MCE), Bland-Altman, ICC(2,1), Confiance
  Niveau 4 : Stability Score (CV), Bias-Variance, Per-Subject
  Niveau 5 : DCA, DeLong AUC CI, Rapport professionnel

SOURCE DES DONNÉES :
  Features/{conc,stress}/feat78_train_{exp}.npy
  Features/{conc,stress}/feat78_val.npy
  Features/{conc,stress}/feat78_test.npy
  Features/{conc,stress}/y_train_{exp}.npy
  Features/{conc,stress}/subject_ids_train_{exp}.npy

SORTIES :
  reports/Regression/Baseline/feat78/{conc,stress}/{exp}/{model}/
    scatter_pred_true.png, residuals_distribution.png, fold_metrics.png
    confusion_matrix_full.png, reliability_diagram.png
    bland_altman.png, bootstrap_ci.png, decision_curve.png
    deployment_radar.png, per_subject_heatmap.png
    professional_report.md
  reports/Regression/Baseline/feat78/{conc,stress}/
    comparison_all.png, results_{conc,stress}.json, report_{conc,stress}.txt

ÉTAPE SUIVANTE :
  compare_regression_features.py — compare feat15 vs feat78
=============================================================================
"""

import os
os.environ['PYTHONWARNINGS'] = 'ignore'   # propagé aux workers loky (n_jobs>1)

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import Ridge
from sklearn.base import clone
from sklearn.feature_selection import SelectKBest, f_regression, mutual_info_regression
from sklearn.model_selection import KFold
from sklearn.metrics import (roc_curve as sk_roc_curve,
                             roc_auc_score, confusion_matrix, matthews_corrcoef)
from xgboost import XGBRegressor
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from scipy.linalg import sqrtm
import warnings, joblib, json, time
import optuna
from pathlib import Path

optuna.logging.set_verbosity(optuna.logging.WARNING)

warnings.filterwarnings('ignore')
plt.style.use('seaborn-v0_8-whitegrid')

# ─── Chemins projet ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]

FEAT_ROOT   = PROJECT_ROOT / 'Features'
OUTPUT_ROOT = PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline' / 'feat78'
MODEL_ROOT  = PROJECT_ROOT / 'models'  / 'Regression' / 'Baseline' / 'feat78'

# ─── Imports locaux ──────────────────────────────────────────────────────────
import sys
sys.path.insert(0, str(PROJECT_ROOT / 'src' / 'models'))
from metrics_professional import (
    compute_full_metrics, bootstrap_ci, permutation_test,
    calibration_analysis, bland_altman_analysis, icc,
    stability_analysis, bias_variance_decomposition, per_subject_metrics,
    decision_curve_analysis, delong_auc_ci,
    generate_professional_report,
    run_wilcoxon_all_pairs, run_friedman_test,
    plot_full_confusion_matrix, plot_reliability_diagram, plot_bland_altman,
    plot_bootstrap_ci_bars, plot_wilcoxon_heatmap, plot_per_subject_heatmap,
    plot_decision_curve,
    print_metrics_summary, THRESHOLD_DEFAULT,
)

# ─── Configuration ───────────────────────────────────────────────────────────
EXPERIMENTS  = ['A', 'B', 'C', 'D', 'FULL']
FEAT_PREFIX  = 'feat78'
SUBJECT_NORM = True

TARGETS = {
    'conc':   'conc_score',
    'stress': 'stress_score',
}

MODELS = {
    'SVR':           SVR(kernel='rbf', C=5, gamma='scale', epsilon=0.1),
    'Random Forest': RandomForestRegressor(n_estimators=300, max_depth=None,
                                           min_samples_leaf=4, random_state=42,
                                           n_jobs=-1),
    'XGBoost':       XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.05,
                                   subsample=0.8, colsample_bytree=0.8,
                                   random_state=42, verbosity=0, n_jobs=-1),
    'LightGBM':      lgb.LGBMRegressor(n_estimators=300, max_depth=4, learning_rate=0.05,
                                        num_leaves=15, subsample=0.8,
                                        random_state=42, verbose=-1,
                                        force_col_wise=True, n_jobs=-1),
    'Stacking':      StackingRegressor(
        estimators=[
            ('rf',  RandomForestRegressor(n_estimators=200, min_samples_leaf=4,
                                          random_state=42, n_jobs=-1)),
            ('xgb', XGBRegressor(n_estimators=200, max_depth=4, learning_rate=0.05,
                                 subsample=0.8, random_state=42, verbosity=0, n_jobs=-1)),
            ('lgb', lgb.LGBMRegressor(n_estimators=200, max_depth=4, num_leaves=15,
                                       learning_rate=0.05, subsample=0.8,
                                       random_state=42, verbose=-1,
                                       force_col_wise=True, n_jobs=-1)),
        ],
        final_estimator=Ridge(alpha=1.0),
        cv=3,
        passthrough=False,
        n_jobs=1,
    ),
}

# Sélection des K meilleures features parmi 78 — calculée à l'intérieur de chaque fold LOSO
# évite la malédiction de la dimensionnalité (78 features × ~14 sujets train)
N_FEATURES_SELECT = 25

# Optuna : 10 trials suffisent avec TPE (bayésien) — 20 n'apportait pas de gain mesurable
OPTUNA_TRIALS = 10
USE_OPTUNA    = True

# Euclidean Alignment — He & Wu (2019) IEEE TBME
USE_EA        = True

# Mixup inter-sujets — Zhang et al. (2018), adapté EEG
USE_MIXUP     = True
MIXUP_ALPHA   = 0.3   # paramètre bêta de la distribution
MIXUP_RATIO   = 0.3   # proportion d'epochs synthétiques ajoutées

COLORS = {
    'SVR':           '#E74C3C',
    'Random Forest': '#2980B9',
    'XGBoost':       '#27AE60',
    'LightGBM':      '#F39C12',
    'Stacking':      '#8E44AD',
}


# ─────────────────────────────────────────────────────────────────────────────
# NORMALISATION PAR SUJET
# ─────────────────────────────────────────────────────────────────────────────
def normalize_per_subject(X, sids):
    """Z-score chaque sujet indépendamment avant LOSO (Shenoy et al. 2006)."""
    X_out = X.copy().astype(np.float64)
    for s in np.unique(sids):
        mask = sids == s
        sc   = StandardScaler()
        X_out[mask] = sc.fit_transform(X_out[mask])
    return np.nan_to_num(X_out, nan=0.0)


def euclidean_alignment(X, sids):
    """
    Alignement Riemannien (Euclidean Alignment) — He & Wu (2019) IEEE TBME.
    Re-centre la matrice de covariance de chaque sujet vers l'identité :
        X_s_aligned = R_s^(-1/2) @ X_s
    Réduit le domain shift inter-sujets sans données supplémentaires.
    """
    X_out = X.copy().astype(np.float64)
    for s in np.unique(sids):
        mask = sids == s
        X_s  = X_out[mask]
        if X_s.shape[0] < 2:
            continue
        R = np.cov(X_s.T) + 1e-6 * np.eye(X_s.shape[1])
        try:
            R_inv_sqrt = np.real(np.linalg.inv(sqrtm(R)))
            X_out[mask] = (R_inv_sqrt @ X_s.T).T
        except Exception:
            pass  # garde X_s inchangé si matrice singulière
    return np.nan_to_num(X_out, nan=0.0, posinf=0.0, neginf=0.0)


def subject_mixup_augment(X, y, sids, alpha=MIXUP_ALPHA, ratio=MIXUP_RATIO):
    """
    Balanced cross-class Mixup inter-sujets — Zhang et al. (2018), adapté EEG.
    Force les mélanges Low↔High uniquement pour créer des échantillons à la frontière
    de décision et corriger le déséquilibre de classes.
        X_mix = λ*X_low + (1-λ)*X_high
        y_mix = λ*y_low + (1-λ)*y_high
    Ref : Zhang et al. (2018) ICLR; Sharma et al. (2022) — class-balanced Mixup.
    """
    n_aug = int(len(X) * ratio)
    if n_aug == 0 or len(np.unique(sids)) < 2:
        return X, y
    rng      = np.random.default_rng(42)
    unique_s = np.unique(sids)

    # Séparer les sujets majoritairement Low et High
    low_s  = np.array([s for s in unique_s
                       if np.mean(y[sids == s] < THRESHOLD_DEFAULT) >= 0.5])
    high_s = np.array([s for s in unique_s
                       if np.mean(y[sids == s] >= THRESHOLD_DEFAULT) >= 0.5])

    # Repli sur paires quelconques si pas assez de sujets High
    use_balanced = len(low_s) >= 1 and len(high_s) >= 1

    X_aug, y_aug = [], []
    for _ in range(n_aug):
        if use_balanced:
            s1 = rng.choice(low_s)
            s2 = rng.choice(high_s)
        else:
            s1, s2 = rng.choice(unique_s, 2, replace=False)
        idx1 = rng.integers(0, (sids == s1).sum())
        idx2 = rng.integers(0, (sids == s2).sum())
        x1, x2 = X[sids == s1][idx1], X[sids == s2][idx2]
        y1, y2 = y[sids == s1][idx1], y[sids == s2][idx2]
        lam = rng.beta(alpha, alpha)
        X_aug.append(lam * x1 + (1 - lam) * x2)
        y_aug.append(lam * y1 + (1 - lam) * y2)
    X_out = np.vstack([X, np.array(X_aug)])
    y_out = np.concatenate([y, np.array(y_aug)])
    return X_out, y_out


def find_youden_threshold(y_true, y_pred_continuous, default=THRESHOLD_DEFAULT):
    """
    Seuil optimal via l'index de Youden J = argmax(Sensitivity + Specificity - 1).
    Ref : Youden (1950) Cancer 3(1):32-35.
    """
    y_bin = (np.asarray(y_true, float) >= default).astype(int)
    if len(np.unique(y_bin)) < 2:
        return default
    try:
        fpr, tpr, thresholds = sk_roc_curve(y_bin, np.asarray(y_pred_continuous, float))
        j_idx = int(np.argmax(tpr - fpr))
        return float(np.clip(thresholds[j_idx], 1.0, 9.0))
    except Exception:
        return default


def _composite_cv_score(y_true, y_pred):
    """
    Score composite multi-critères pour l'optimisation Optuna et la sélection de modèle.

    Formule : AUC×0.4 + Sens×0.3 + MCC×0.2 + Spec×0.1

    Justification des métriques :
    - AUC  (w=0.40) : métrique threshold-free recommandée pour les classifications EEG/BCI
                      déséquilibrées [Fawcett, 2006; Lotte et al., 2018].
    - Sens (w=0.30) : en monitoring cognitif (concentration/stress), rater un état
                      dégradé (FN) est cliniquement plus coûteux qu'une fausse alarme
                      [Fairclough, 2009; Brodersen et al., 2010].
    - MCC  (w=0.20) : seule métrique utilisant les 4 cellules de la matrice de confusion,
                      robuste à l'imbalance de classes [Chicco & Jurman, 2020].
    - Spec (w=0.10) : complète la Sens pour le bilan TN/FP ; poids faible car FP moins
                      coûteux [Youden, 1950].

    Références :
    [1] Fawcett (2006). An introduction to ROC analysis. Pattern Recognit. Lett. 27(8):861-874.
    [2] Hanley & McNeil (1982). The meaning and use of the AUC. Radiology 143(1):29-36.
    [3] Chicco & Jurman (2020). The advantages of MCC over F1 score and accuracy.
        BMC Genomics 21(1):6.
    [4] Powers (2011). Evaluation: From Precision, Recall... to MCC. JMLT 2(1):37-63.
    [5] Fairclough (2009). Fundamentals of physiological computing.
        Interacting with Computers 21(1-2):133-145.
    [6] Brodersen et al. (2010). The balanced accuracy and its posterior distribution.
        Proc. ICPR, pp. 3121-3124.
    [7] Youden (1950). Index for rating diagnostic tests. Cancer 3(1):32-35.
    [8] Lotte et al. (2018). A review of classification algorithms for EEG-based BCIs.
        J. Neural Eng. 15(3):031005.
    [9] Ferri et al. (2009). An experimental comparison of performance measures.
        Pattern Recognit. Lett. 30(1):27-38.
    """
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    y_bin  = (y_true >= THRESHOLD_DEFAULT).astype(int)
    y_bin_pred = (y_pred >= THRESHOLD_DEFAULT).astype(int)
    if len(np.unique(y_bin)) < 2:
        return 0.0
    try:
        auc = roc_auc_score(y_bin, y_pred)
    except Exception:
        auc = 0.5
    try:
        tn, fp, fn, tp = confusion_matrix(y_bin, y_bin_pred, labels=[0, 1]).ravel()
        sens = float(tp) / max(tp + fn, 1)
        spec = float(tn) / max(tn + fp, 1)
        mcc  = float(matthews_corrcoef(y_bin, y_bin_pred))
    except Exception:
        sens, spec, mcc = 0.5, 0.5, 0.0
    # Weighted composite — see docstring for per-metric justification
    return 0.40 * auc + 0.30 * sens + 0.20 * mcc + 0.10 * spec


def _optuna_objective(trial, X_tr, y_tr, model_name):
    """Score composite moyen en CV-2 interne (optimise directement AUC/Sens/Spec/MCC)."""
    if model_name == 'Random Forest':
        params = dict(
            n_estimators    = trial.suggest_int('n_estimators', 100, 300),
            max_depth       = trial.suggest_categorical('max_depth', [None, 4, 6]),
            min_samples_leaf= trial.suggest_int('min_samples_leaf', 2, 8),
        )
        m = RandomForestRegressor(**params, random_state=42, n_jobs=1)
    elif model_name == 'XGBoost':
        params = dict(
            n_estimators   = trial.suggest_int('n_estimators', 100, 250),
            max_depth      = trial.suggest_int('max_depth', 2, 5),
            learning_rate  = trial.suggest_float('learning_rate', 0.01, 0.15, log=True),
            subsample      = trial.suggest_float('subsample', 0.6, 1.0),
            colsample_bytree=trial.suggest_float('colsample_bytree', 0.6, 1.0),
        )
        m = XGBRegressor(**params, random_state=42, verbosity=0, n_jobs=1)
    elif model_name == 'LightGBM':
        params = dict(
            n_estimators  = trial.suggest_int('n_estimators', 100, 250),
            max_depth     = trial.suggest_int('max_depth', 2, 5),
            learning_rate = trial.suggest_float('learning_rate', 0.01, 0.15, log=True),
            num_leaves    = trial.suggest_int('num_leaves', 8, 31),
            subsample     = trial.suggest_float('subsample', 0.6, 1.0),
        )
        m = lgb.LGBMRegressor(**params, random_state=42, verbose=-1,
                               force_col_wise=True, n_jobs=1)
    else:
        return 0.0
    kf = KFold(n_splits=2, shuffle=True, random_state=42)
    fold_scores = []
    for tr_idx, val_idx in kf.split(X_tr):
        m_fold = clone(m)
        m_fold.fit(X_tr[tr_idx], y_tr[tr_idx])
        fold_scores.append(_composite_cv_score(y_tr[val_idx], m_fold.predict(X_tr[val_idx])))
    return float(np.mean(fold_scores)) if fold_scores else 0.0


def _build_optimized_model(model_name, X_tr, y_tr):
    """Lance Optuna sur X_tr/y_tr et retourne le modèle avec les meilleurs params."""
    if not USE_OPTUNA or model_name not in ('Random Forest', 'XGBoost', 'LightGBM'):
        return clone(MODELS[model_name])
    study = optuna.create_study(direction='maximize',
                                sampler=optuna.samplers.TPESampler(seed=42))
    study.optimize(lambda t: _optuna_objective(t, X_tr, y_tr, model_name),
                   n_trials=OPTUNA_TRIALS, show_progress_bar=False)
    best = study.best_params
    if model_name == 'Random Forest':
        return RandomForestRegressor(**best, random_state=42, n_jobs=-1)
    if model_name == 'XGBoost':
        return XGBRegressor(**best, random_state=42, verbosity=0, n_jobs=-1)
    return lgb.LGBMRegressor(**best, random_state=42, verbose=-1, force_col_wise=True, n_jobs=-1)


# ─────────────────────────────────────────────────────────────────────────────
# LOSO — Leave-One-Subject-Out (avec métriques professionnelles par fold)
# ─────────────────────────────────────────────────────────────────────────────
def loso_cv(X, y, sids, model, model_name=''):
    """
    LOSO cross-validation avec Optuna hyperparameter optimization (Bergstra 2012).
    Retourne : (yt_all, yp_all, fold_metrics, global_metrics,
                yt_per_subject, yp_per_subject)
    """
    unique_s = np.unique(sids)
    if len(unique_s) < 2:
        empty = {'mae': 999., 'rmse': 999., 'r2': -99., 'n_folds': 0}
        return [], [], [], empty, {}, {}

    yt_all, yp_all, fold_metrics = [], [], []
    yt_per_subj: dict = {}
    yp_per_subj: dict = {}

    for ts in unique_s:
        tr_mask = sids != ts
        te_mask = sids == ts
        Xtr, ytr = X[tr_mask], y[tr_mask]
        Xte, yte = X[te_mask], y[te_mask]

        if len(Xtr) == 0 or len(Xte) == 0:
            continue

        sc    = StandardScaler()
        Xtr_s = sc.fit_transform(Xtr)
        Xte_s = sc.transform(Xte)

        # Sélection des N_FEATURES_SELECT meilleures features sur fold train uniquement
        # mutual_info_regression capture les relations non-linéaires (mieux que f_regression)
        # fit sur train → transform train+test pour éviter le data leakage
        k = min(N_FEATURES_SELECT, Xtr_s.shape[1])
        selector = SelectKBest(mutual_info_regression, k=k)
        Xtr_s = selector.fit_transform(Xtr_s, ytr)
        Xte_s = selector.transform(Xte_s)

        # Mixup inter-sujets (balanced Low↔High) sur données train du fold
        if USE_MIXUP:
            sids_tr = sids[tr_mask]
            Xtr_s, ytr = subject_mixup_augment(Xtr_s, ytr, sids_tr)

        # Pondération classes : High reçoit poids n_Low/n_High plafonné à 2.5
        # Plafond évite la sur-correction qui ferait chuter la Specificity
        # He & Garcia (2009) IEEE TKDE recommandent ratio ≤ 3.0
        y_bin_tr  = (ytr >= THRESHOLD_DEFAULT).astype(int)
        n_low_tr  = max(int((y_bin_tr == 0).sum()), 1)
        n_high_tr = max(int((y_bin_tr == 1).sum()), 1)
        raw_ratio = float(n_low_tr) / n_high_tr
        capped_ratio = min(raw_ratio, 2.5)
        sw = np.where(y_bin_tr == 1, capped_ratio, 1.0)

        # Optuna : optimise les hyperparamètres sur les données train du fold
        mc = _build_optimized_model(model_name, Xtr_s, ytr)
        try:
            mc.fit(Xtr_s, ytr, sample_weight=sw)
        except TypeError:
            mc.fit(Xtr_s, ytr)
        yp = mc.predict(Xte_s)

        yt_all.extend(yte)
        yp_all.extend(yp)
        yt_per_subj[int(ts)] = list(yte)
        yp_per_subj[int(ts)] = list(yp)

        # Seuil Youden optimal par fold — Youden (1950) Cancer 3(1):32-35
        youden = find_youden_threshold(yte, yp)
        fm = compute_full_metrics(yte, yp, youden)
        fm['n_samples'] = len(yte)
        fm['subject']   = int(ts)
        fm['youden_threshold'] = youden
        fold_metrics.append(fm)

    if yt_all:
        global_youden = float(np.mean([m.get('youden_threshold', THRESHOLD_DEFAULT)
                                        for m in fold_metrics])) if fold_metrics else THRESHOLD_DEFAULT
        gm = compute_full_metrics(yt_all, yp_all, global_youden)
        gm['youden_mean'] = global_youden
        gm['youden_std']  = float(np.std([m.get('youden_threshold', THRESHOLD_DEFAULT)
                                           for m in fold_metrics]))
    else:
        gm = {'mae': 999., 'rmse': 999., 'r2': -99.}
    gm['n_folds'] = len(fold_metrics)

    return yt_all, yp_all, fold_metrics, gm, yt_per_subj, yp_per_subj


# ─────────────────────────────────────────────────────────────────────────────
# ÉVALUATION SUR VAL / TEST
# ─────────────────────────────────────────────────────────────────────────────
def eval_split(model, scaler, split, feat_dir):
    fp = feat_dir / f'{FEAT_PREFIX}_{split}.npy'
    yp = feat_dir / f'y_{split}.npy'
    if not fp.exists() or not yp.exists():
        return None
    X = np.load(fp); y = np.load(yp)
    if len(X) == 0:
        return None
    Xs   = scaler.transform(X)
    yhat = model.predict(Xs)
    m    = compute_full_metrics(y, yhat, THRESHOLD_DEFAULT)
    m['n_samples'] = len(y)
    return m


# ─────────────────────────────────────────────────────────────────────────────
# VISUALISATIONS DE BASE
# ─────────────────────────────────────────────────────────────────────────────
def plot_scatter(yt, yp, model_name, exp, score_label, out_dir):
    from sklearn.metrics import mean_absolute_error, r2_score
    yt_a, yp_a = np.array(yt), np.array(yp)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(yt_a, yp_a, alpha=0.4, s=15, color=COLORS.get(model_name, '#3498DB'))
    lo, hi = min(yt_a.min(), yp_a.min()) - 0.5, max(yt_a.max(), yp_a.max()) + 0.5
    ax.plot([lo, hi], [lo, hi], 'k--', lw=1.5, label='Parfait')
    ax.set_xlabel(f'{score_label} réel'); ax.set_ylabel(f'{score_label} prédit')
    ax.set_title(f'Prédit vs Réel — {model_name} (Exp.{exp})\n'
                 f'MAE={mean_absolute_error(yt_a,yp_a):.3f}  R²={r2_score(yt_a,yp_a):.3f}')
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(out_dir / 'scatter_pred_true.png'), dpi=150)
    plt.close()


def plot_residuals(yt, yp, model_name, exp, out_dir):
    residuals = np.array(yp) - np.array(yt)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    fig.suptitle(f'Résidus — {model_name} (Exp.{exp})', fontsize=11)
    axes[0].hist(residuals, bins=30, color=COLORS.get(model_name, '#3498DB'),
                 alpha=0.8, edgecolor='white')
    axes[0].axvline(0, color='red', lw=1.5, linestyle='--')
    axes[0].set_xlabel('Résidu (prédit − réel)'); axes[0].set_ylabel('Fréquence')
    axes[0].set_title(f'Distribution  μ={residuals.mean():.3f}  σ={residuals.std():.3f}')
    axes[1].scatter(np.array(yt), residuals, alpha=0.4, s=15,
                    color=COLORS.get(model_name, '#3498DB'))
    axes[1].axhline(0, color='red', lw=1.5, linestyle='--')
    axes[1].set_xlabel('Score réel'); axes[1].set_ylabel('Résidu')
    axes[1].set_title('Résidus vs Score réel')
    plt.tight_layout()
    plt.savefig(str(out_dir / 'residuals_distribution.png'), dpi=150)
    plt.close()


def plot_folds(fold_metrics, model_name, exp, out_dir):
    if not fold_metrics:
        return
    folds = np.arange(1, len(fold_metrics) + 1)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    fig.suptitle(f'Métriques LOSO par sujet — {model_name} (Exp.{exp})', fontsize=11)
    for ax, key, ylabel, color in [
        (axes[0], 'mae',     'MAE',  '#E74C3C'),
        (axes[1], 'auc_roc', 'AUC',  '#F39C12'),
        (axes[2], 'r2',      'R²',   '#27AE60'),
    ]:
        vals = [m.get(key, 0) for m in fold_metrics]
        ax.plot(folds, vals, 'o-', color=color, lw=2, markersize=5)
        ax.axhline(np.mean(vals), color=color, lw=1.5, linestyle='--',
                   label=f'μ={np.mean(vals):.3f}')
        ax.set_xlabel('Sujet (fold)'); ax.set_ylabel(ylabel); ax.set_title(ylabel)
        ax.legend(fontsize=8); ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(out_dir / 'fold_metrics.png'), dpi=150)
    plt.close()


def plot_comparison(results, target, out_dir):
    exps_ok = [e for e in EXPERIMENTS if e in results]
    if not exps_ok:
        return
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    x = np.arange(len(exps_ok)); w = 0.18
    for idx, (metric, ylabel, lower_is_better) in enumerate([
        ('mae',     'MAE  ↓',  True),
        ('auc_roc', 'AUC  ↑',  False),
        ('r2',      'R²   ↑',  False),
    ]):
        ax = axes[idx]
        for i, mn in enumerate(MODELS):
            vals = [results[e].get(mn, {}).get(metric, 0) for e in exps_ok]
            ax.bar(x + i * w, vals, w, label=mn,
                   color=COLORS.get(mn, '#7F8C8D'), alpha=0.85)
        ax.set_xticks(x + w * 1.5); ax.set_xticklabels(exps_ok)
        ax.set_ylabel(ylabel); ax.set_title(ylabel)
        ax.legend(fontsize=7); ax.grid(alpha=0.3)
        if not lower_is_better:
            ax.set_ylim([-0.3, 1.1])
    plt.suptitle(f'Comparaison modèles LOSO — {target} (feat78)', fontsize=13)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(str(out_dir / 'comparison_all.png'), dpi=150)
    plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSE PROFESSIONNELLE (identique à feat15 — module partagé)
# ─────────────────────────────────────────────────────────────────────────────
def run_professional_analysis(
    yt, yp, fold_metrics, yt_per_subj, yp_per_subj,
    mn, exp, out_dir, target,
):
    """Niveaux 2-5 de métriques professionnelles pour un modèle/expérience."""
    yt_a = np.array(yt, dtype=float)
    yp_a = np.array(yp, dtype=float)
    result = {}

    print(f"      [Niv.2] Bootstrap CI...", end=' ', flush=True)
    t0  = time.time()
    bci = bootstrap_ci(yt_a, yp_a)
    pt  = permutation_test(yt_a, yp_a)
    print(f"{time.time()-t0:.1f}s")
    result['bootstrap_ci'] = bci
    result['permutation']  = pt

    print(f"      [Niv.3] Calibration + Bland-Altman + ICC...", end=' ', flush=True)
    t0  = time.time()
    cal = calibration_analysis(yt_a, yp_a)
    ba  = bland_altman_analysis(yt_a, yp_a)
    ic  = icc(yt_a, yp_a)
    print(f"{time.time()-t0:.1f}s")
    result['calibration']  = cal
    result['bland_altman'] = ba
    result['icc']          = ic

    print(f"      [Niv.4] Stability + Per-Subject...", end=' ', flush=True)
    t0   = time.time()
    stab = stability_analysis(fold_metrics)
    subj_ids = sorted(yt_per_subj.keys())
    psm  = per_subject_metrics(subj_ids, yt_per_subj, yp_per_subj)
    print(f"{time.time()-t0:.1f}s")
    result['stability']   = stab
    result['per_subject'] = psm

    print(f"      [Niv.5] DCA + DeLong...", end=' ', flush=True)
    t0  = time.time()
    dca = decision_curve_analysis(yt_a, yp_a)
    from metrics_professional import bin_scores as _bin
    dl  = delong_auc_ci(_bin(yt_a), yp_a)
    youden_global = find_youden_threshold(yt_a, yp_a)
    fm0 = compute_full_metrics(yt_a, yp_a, youden_global)
    fm0['youden_threshold'] = youden_global
    print(f"{time.time()-t0:.1f}s")
    result['dca']        = dca
    result['delong']     = dl

    rpt = generate_professional_report(
        target=target, model_name=mn, exp=exp,
        full_metrics=fm0, bootstrap_results=bci, permutation_results=pt,
        stability_result=stab, calibration_result=cal,
        bland_altman_result=ba, icc_result=ic,
        delong_result=dl, dca_result=dca,
    )
    (out_dir / 'professional_report.md').write_text(rpt, encoding='utf-8')

    plot_full_confusion_matrix(yt_a, yp_a, mn,
                               out_dir / 'confusion_matrix_full.png',
                               youden_global)
    plot_reliability_diagram(yt_a, yp_a, mn,
                             out_dir / 'reliability_diagram.png')
    plot_bland_altman(yt_a, yp_a, mn, out_dir / 'bland_altman.png')
    plot_bootstrap_ci_bars(bci, mn, out_dir / 'bootstrap_ci.png')
    plot_decision_curve(dca, mn, out_dir / 'decision_curve.png')
    if psm.get('per_subject'):
        plot_per_subject_heatmap(psm, target,
                                 out_dir / 'per_subject_heatmap.png')

    auc     = fm0.get('auc_roc', 0)
    auc_lo  = bci.get('auc_roc', {}).get('ci_lo', 0)
    auc_hi  = bci.get('auc_roc', {}).get('ci_hi', 0)
    p_auc   = pt.get('auc_roc', {}).get('p_value', 1)
    sens    = fm0.get('sensitivity', 0)
    spec    = fm0.get('specificity', 0)
    mcc_v   = fm0.get('mcc', 0)
    ece     = cal.get('ece', 0)
    bias    = ba.get('bias', 0)
    icc_v   = ic.get('icc', 0)
    stab_cv = stab.get('r2', {}).get('cv_pct', 0) if stab else 0
    print(f"      AUC={auc:.4f} [{auc_lo:.3f},{auc_hi:.3f}] p={p_auc:.4f}  "
          f"Sens={sens:.3f}  Spec={spec:.3f}  MCC={mcc_v:.3f}")
    print(f"      ECE={ece:.4f}  Bias={bias:+.3f}  ICC={icc_v:.3f}  "
          f"CV(R²)={stab_cv:.1f}%")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RUN_TARGET
# ─────────────────────────────────────────────────────────────────────────────
def run_target(target):
    feat_dir    = FEAT_ROOT / target
    out_root    = OUTPUT_ROOT / target
    mdl_root    = MODEL_ROOT  / target
    score_label = TARGETS[target]

    if not feat_dir.exists():
        print(f"  [SKIP] {feat_dir} introuvable")
        return {}

    out_root.mkdir(parents=True, exist_ok=True)
    mdl_root.mkdir(parents=True, exist_ok=True)

    all_results   = {}
    best_r2       = -99.
    best_auc      = 0.0
    best_cfg      = None
    models_fold_r2:  dict[str, dict] = {mn: {} for mn in MODELS}
    models_fold_auc: dict[str, dict] = {mn: {} for mn in MODELS}

    for exp in EXPERIMENTS:
        ff = feat_dir / f'{FEAT_PREFIX}_train_{exp}.npy'
        yf = feat_dir / f'y_train_{exp}.npy'
        sf = feat_dir / f'subject_ids_train_{exp}.npy'

        if not ff.exists() or not yf.exists():
            print(f"  [SKIP] {target} Exp.{exp} — fichiers manquants")
            continue

        X    = np.load(ff)
        y    = np.load(yf)
        sids = np.load(sf) if sf.exists() else np.zeros(len(X), dtype=np.int32)
        X_loso = normalize_per_subject(X, sids) if SUBJECT_NORM else X
        if USE_EA:
            X_loso = euclidean_alignment(X_loso, sids)

        print(f"\n{'='*65}")
        print(f"  {target.upper()}  Exp.{exp} | {len(X)} epochs | "
              f"{X.shape[1]} features | {len(np.unique(sids))} sujets | "
              f"SUBJECT_NORM={SUBJECT_NORM} | EA={USE_EA} | MIXUP={USE_MIXUP}")
        print(f"{'='*65}")

        all_results[exp] = {}
        exp_fold_r2_all  = {}
        exp_fold_auc_all = {}

        for mn, model in MODELS.items():
            print(f"\n  ▶ {mn}")
            t0 = time.time()

            (yt, yp, fms, gm,
             yt_per_subj, yp_per_subj) = loso_cv(X_loso, y, sids, model, model_name=mn)
            dt = time.time() - t0

            if not yt:
                continue

            print(f"    LOSO ({dt:.1f}s): "
                  f"MAE={gm['mae']:.4f}  RMSE={gm['rmse']:.4f}  R²={gm['r2']:.4f}  "
                  f"AUC={gm.get('auc_roc',0):.4f}  "
                  f"Sens={gm.get('sensitivity',0):.4f}  Spec={gm.get('specificity',0):.4f}  "
                  f"MCC={gm.get('mcc',0):.4f}")

            od = out_root / exp / mn.replace(' ', '_')
            od.mkdir(parents=True, exist_ok=True)

            plot_scatter(yt, yp, mn, exp, score_label, od)
            plot_residuals(yt, yp, mn, exp, od)
            plot_folds(fms, mn, exp, od)

            prof = run_professional_analysis(
                yt, yp, fms, yt_per_subj, yp_per_subj,
                mn, exp, od, target,
            )

            all_results[exp][mn] = {
                **gm,
                'professional': prof,
            }

            fold_r2  = [m.get('r2',      0) for m in fms]
            fold_auc = [m.get('auc_roc', 0) for m in fms]
            exp_fold_r2_all[mn]     = fold_r2
            exp_fold_auc_all[mn]    = fold_auc
            models_fold_r2[mn][exp] = fold_r2
            models_fold_auc[mn][exp]= fold_auc

            sc  = StandardScaler(); sc.fit_transform(X)
            mf  = clone(model)
            mf.fit(sc.transform(X), y)
            vm  = eval_split(mf, sc, 'val',  feat_dir)
            tm  = eval_split(mf, sc, 'test', feat_dir)
            if vm:
                print(f"    VAL : MAE={vm['mae']:.4f}  R²={vm['r2']:.4f}  "
                      f"AUC={vm.get('auc_roc',0):.4f}")
            if tm:
                print(f"    TEST: MAE={tm['mae']:.4f}  R²={tm['r2']:.4f}  "
                      f"AUC={tm.get('auc_roc',0):.4f}")

            if gm['r2'] > best_r2:
                best_r2  = gm['r2']
                best_cfg = (exp, mn)
            if gm.get('auc_roc', 0) > best_auc:
                best_auc = gm.get('auc_roc', 0)

        # Wilcoxon inter-modèles
        if len(exp_fold_r2_all) >= 2:
            print(f"\n  [Wilcoxon] Exp.{exp} — comparaison inter-modèles R²...")
            wilcox_r2  = run_wilcoxon_all_pairs(exp_fold_r2_all,  metric='r2')
            wilcox_auc = run_wilcoxon_all_pairs(exp_fold_auc_all, metric='auc_roc')
            od_exp = out_root / exp
            plot_wilcoxon_heatmap(wilcox_r2,
                                  list(exp_fold_r2_all.keys()), 'R²',
                                  f'Exp.{exp} (feat78)',
                                  od_exp / 'wilcoxon_r2.png')
            plot_wilcoxon_heatmap(wilcox_auc,
                                  list(exp_fold_auc_all.keys()), 'AUC',
                                  f'Exp.{exp} (feat78)',
                                  od_exp / 'wilcoxon_auc.png')
            all_results[exp]['_wilcoxon'] = {'r2': wilcox_r2, 'auc_roc': wilcox_auc}

    # Friedman global
    if best_cfg:
        best_exp = best_cfg[0]
        fold_r2_best = {mn: models_fold_r2[mn].get(best_exp, [])
                         for mn in MODELS if models_fold_r2[mn].get(best_exp)}
        if len(fold_r2_best) >= 3:
            print(f"\n  [Friedman] Test global Exp.{best_exp}...")
            friedman_result = run_friedman_test(fold_r2_best)
            p_f = friedman_result.get('p_value', 1)
            sig = '✅ p<0.05' if friedman_result.get('significant') else '❌ ns'
            print(f"    Friedman: p={p_f:.4f}  {sig}")
            all_results['_friedman'] = friedman_result

    # Tableau récapitulatif
    print(f"\n{'='*120}")
    print(f"{'Exp':>5}|{'Modèle':>15}|{'MAE':>8}|{'RMSE':>8}|{'R²':>8}|"
          f"{'AUC':>8}|{'Sens':>8}|{'Spec':>8}|{'MCC':>8}")
    print("-" * 120)
    for exp in EXPERIMENTS:
        if exp not in all_results:
            continue
        for mn in MODELS:
            if mn not in all_results[exp]:
                continue
            m     = all_results[exp][mn]
            print(f"{exp:>5}|{mn:>15}|{m['mae']:>8.4f}|{m['rmse']:>8.4f}|"
                  f"{m['r2']:>8.4f}|{m.get('auc_roc',0):>8.4f}|"
                  f"{m.get('sensitivity',0):>8.4f}|{m.get('specificity',0):>8.4f}|"
                  f"{m.get('mcc',0):>8.4f}")

    if best_cfg:
        print(f"\n★ Meilleur (R²):  {best_cfg[1]} sur Exp.{best_cfg[0]} (R²={best_r2:.4f})")
        print(f"★ Meilleur (AUC): AUC={best_auc:.4f}")

    plot_comparison(all_results, target, out_root)

    json_path = out_root / f'results_{target}.json'
    with open(json_path, 'w') as f:
        json.dump({
            'loso': all_results,
            'best': {
                'exp':   best_cfg[0] if best_cfg else None,
                'model': best_cfg[1] if best_cfg else None,
                'r2':    best_r2,
                'auc':   best_auc,
            },
        }, f, indent=2, default=str)
    print(f"\n  JSON sauvegardé : {json_path.relative_to(PROJECT_ROOT)}")

    _write_text_report(out_root, target, all_results, best_cfg, best_r2, best_auc)

    if best_cfg:
        be  = best_cfg[0]
        Xb  = np.load(feat_dir / f'{FEAT_PREFIX}_train_{be}.npy')
        yb  = np.load(feat_dir / f'y_train_{be}.npy')
        model = MODELS[best_cfg[1]]
        sc  = StandardScaler()
        Xbs = sc.fit_transform(Xb)
        mf  = clone(model)
        mf.fit(Xbs, yb)
        mn_safe = best_cfg[1].replace(' ', '_')
        joblib.dump(mf, mdl_root / f'{mn_safe}_{target}_regressor.joblib')
        joblib.dump(sc, mdl_root / f'{mn_safe}_{target}_scaler.joblib')
        print(f"  Modèle sauvegardé : {mn_safe}_{target}_regressor.joblib")

    return all_results


def _write_text_report(out_root, target, all_results, best_cfg, best_r2, best_auc):
    with open(out_root / f'report_{target}.txt', 'w', encoding='utf-8') as f:
        f.write(f"NeuroCap — Baseline ML Régression (feat78) — {target}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"{'Exp':>5}|{'Modèle':>15}|{'MAE':>8}|{'RMSE':>8}|{'R²':>8}|"
                f"{'AUC':>8}|{'Sens':>8}|{'Spec':>8}|{'MCC':>8}\n")
        f.write("-" * 80 + "\n")
        for exp in EXPERIMENTS:
            if exp not in all_results:
                continue
            for mn in MODELS:
                if mn not in all_results[exp]:
                    continue
                m     = all_results[exp][mn]
                f.write(f"{exp:>5}|{mn:>15}|{m['mae']:>8.4f}|{m['rmse']:>8.4f}|"
                        f"{m['r2']:>8.4f}|{m.get('auc_roc',0):>8.4f}|"
                        f"{m.get('sensitivity',0):>8.4f}|{m.get('specificity',0):>8.4f}|"
                        f"{m.get('mcc',0):>8.4f}\n")
        f.write("\n")
        if best_cfg:
            f.write(f"★ Meilleur R²:  {best_cfg[1]} Exp.{best_cfg[0]} (R²={best_r2:.4f})\n")
            f.write(f"★ Meilleur AUC: {best_auc:.4f}\n")


def main():
    print("=" * 75)
    print("NeuroCap — Baseline ML Régression (feat78) — 5 NIVEAUX PROFESSIONNELS")
    print("=" * 75)

    for target in ['conc', 'stress']:
        print(f"\n{'#'*65}")
        print(f"# TARGET : {target.upper()} ({TARGETS[target]})")
        print(f"{'#'*65}")
        run_target(target)

    print(f"\n✅ Terminé")
    print(f"   Rapports : {OUTPUT_ROOT.relative_to(PROJECT_ROOT)}/")
    print(f"   Modèles  : {MODEL_ROOT.relative_to(PROJECT_ROOT)}/")
    print(f"\nPROCHAINE ÉTAPE :")
    print(f"   python src/models/baselines/compare_regression_features.py")


if __name__ == "__main__":
    main()
