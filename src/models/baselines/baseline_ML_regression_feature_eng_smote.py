"""
=============================================================================
NeuroCap — Baseline ML Régression + SMOTE (feat78 — feature_eng.py)
baseline_ML_regression_feature_eng_smote.py
=============================================================================
MÊME MODÈLES DE RÉGRESSION que baseline_ML_regression_feature_eng.py
  SVR · Random Forest · XGBoost · LightGBM
  → prédisent le score CONTINU 0-10 (MAE, RMSE, R² maintenus)

STRUCTURE IDENTIQUE à baseline_ML_regression_smote.py — seules différences :
  - FEAT_PREFIX = 'feat78'
  - Features PRÉ-CALCULÉES (pas d'extraction à la volée)
  - Chemins : reports/Regression/Baseline/feat78_smote/

3 TECHNIQUES ANTI-IMBALANCE (identiques à baseline_ML_regression_smote.py) :

  ① sample_weight
     ratio = n_Low / n_High ≈ 2.45 pour stress
     [Ref 2] He & Garcia (2009). IEEE TKDE, 21(9), 1263-1284.

  ② SMOTE sur fold TRAIN uniquement
     y continu des synthétiques = tirage depuis distribution High originale
     [Ref 1] Chawla et al. (2002). JAIR, 16, 321-357.

  ③ Seuil Youden optimal
     seuil = argmax(Sensitivity + Specificity − 1) sur fold train
     [Ref 3] Youden (1950). Cancer, 3(1), 32-35.

SOURCE DES DONNÉES :
  Features/{conc,stress}/feat78_train_{exp}.npy  ← features pré-calculées
  Features/{conc,stress}/feat78_val.npy
  Features/{conc,stress}/feat78_test.npy
  Features/{conc,stress}/y_train_{exp}.npy
  Features/{conc,stress}/subject_ids_train_{exp}.npy

SORTIES :
  reports/Regression/Baseline/feat78_smote/{conc,stress}/
    comparison_all.png · smote_vs_baseline.png · results_{target}.json
  + par modèle/expérience :
    scatter_pred_true.png · residuals_distribution.png
    youden_roc.png · fold_metrics.png
    confusion_matrix_full.png · reliability_diagram.png
    bland_altman.png · bootstrap_ci.png · decision_curve.png
    professional_report.md

RÉFÉRENCES SCIENTIFIQUES :
[1] Chawla et al. (2002). SMOTE. JAIR, 16, 321-357.
[2] He & Garcia (2009). Imbalanced Data. IEEE TKDE, 21(9).
[3] Youden (1950). Diagnostic tests. Cancer, 3(1), 32-35.
[4] Chicco & Jurman (2020). MCC. BMC Genomics, 21:6.
[5] Lotte et al. (2018). EEG-BCI review. J.Neural Eng., 15.
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
from xgboost import XGBRegressor
import lightgbm as lgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (roc_curve as sk_roc_curve,
                             roc_auc_score, confusion_matrix, matthews_corrcoef)
import warnings, joblib, json, time
import optuna
from pathlib import Path
from sklearn.feature_selection import SelectKBest, mutual_info_regression
from sklearn.model_selection import KFold

warnings.filterwarnings('ignore')
optuna.logging.set_verbosity(optuna.logging.WARNING)
plt.style.use('seaborn-v0_8-whitegrid')

# ─── SMOTE ────────────────────────────────────────────────────────────────────
try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
    print("[INFO] imbalanced-learn disponible — SMOTE activé [Ref 1]")
except ImportError:
    HAS_SMOTE = False
    print("[WARNING] pip install imbalanced-learn  →  fallback sample_weight uniquement")

# ─── Chemins projet ──────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]
FEAT_ROOT    = PROJECT_ROOT / 'Features'
OUTPUT_ROOT  = PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline' / 'feat78_smote'
MODEL_ROOT   = PROJECT_ROOT / 'models'  / 'Regression' / 'Baseline' / 'feat78_smote'

# ─── Imports locaux ──────────────────────────────────────────────────────────
import sys
sys.path.insert(0, str(PROJECT_ROOT / 'src' / 'models'))
from metrics_professional import (
    compute_full_metrics, bootstrap_ci, permutation_test,
    calibration_analysis, bland_altman_analysis, icc,
    stability_analysis, per_subject_metrics,
    decision_curve_analysis, delong_auc_ci,
    generate_professional_report,
    run_wilcoxon_all_pairs, run_friedman_test,
    plot_full_confusion_matrix, plot_reliability_diagram, plot_bland_altman,
    plot_bootstrap_ci_bars, plot_wilcoxon_heatmap, plot_per_subject_heatmap,
    plot_decision_curve,
    THRESHOLD_DEFAULT, bin_scores,
)

# ─── Configuration ───────────────────────────────────────────────────────────
EXPERIMENTS  = ['A', 'B', 'C', 'D', 'FULL']
FEAT_PREFIX  = 'feat78'          # ← différence clé vs feat15
SUBJECT_NORM = True

TARGETS = {
    'conc':   'conc_score',
    'stress': 'stress_score',
}

# ─── RÉGRESSEURS avec hyperparamètres tuned ──────────────────────────────────
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

SMOTE_TARGETS = {'conc'}
N_FEATURES_SELECT = 25

OPTUNA_TRIALS = 10
USE_OPTUNA    = True

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
    X_out = X.copy().astype(np.float64)
    for s in np.unique(sids):
        mask = sids == s
        sc = StandardScaler()
        X_out[mask] = sc.fit_transform(X_out[mask])
    return np.nan_to_num(X_out, nan=0.0)


# ─────────────────────────────────────────────────────────────────────────────
# SEUIL YOUDEN (sur sortie de régression — échelle 0-10)
# [Ref 3] Youden (1950)
# ─────────────────────────────────────────────────────────────────────────────
def find_youden_threshold(y_true_bin, y_pred_continuous):
    """
    Seuil optimal J = argmax(Sensitivity + Specificity − 1).
    Calculé sur le fold TRAIN → pas de fuite vers le test.
    Le seuil est dans l'échelle 0-10 (même que y_pred).
    """
    if len(np.unique(y_true_bin)) < 2 or len(y_pred_continuous) < 4:
        return THRESHOLD_DEFAULT
    try:
        fpr, tpr, thresholds = sk_roc_curve(y_true_bin.astype(int), y_pred_continuous)
        j_idx = int(np.argmax(tpr - fpr))
        return float(np.clip(thresholds[j_idx], 1.0, 9.0))
    except Exception:
        return THRESHOLD_DEFAULT


# ─────────────────────────────────────────────────────────────────────────────
# OPTUNA — optimisation Bayésienne des hyperparamètres (identique à feature_eng.py)
# [Ref] Bergstra & Bengio (2012). Random Search for Hyper-Parameter Optimization.
# ─────────────────────────────────────────────────────────────────────────────
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
# LOSO avec SMOTE + sample_weight + seuil Youden
# ─────────────────────────────────────────────────────────────────────────────
def loso_cv_smote(X, y, sids, model, model_name='', target='conc'):
    """
    LOSO avec 3 techniques anti-imbalance.
    Les modèles restent des RÉGRESSEURS — MAE/RMSE/R² inchangés.

    Par fold :
      1. Séparation train/test stricte par sujet
      2. Normalisation StandardScaler
      3. Sélection des N_FEATURES_SELECT meilleures features (feat78 → top 25)
      4. SMOTE sur X_train → génère High synthétiques [Ref 1] (conc uniquement)
         y continu = tirage depuis distribution High originale
      4. sample_weight = n_Low/n_High sur données augmentées [Ref 2]
      5. Seuil Youden calculé sur prédictions fold TRAIN [Ref 3]
      6. Évaluation sur fold TEST avec seuil Youden
    """
    unique_s = np.unique(sids)
    if len(unique_s) < 2:
        empty = {'mae': 999., 'rmse': 999., 'r2': -99., 'n_folds': 0}
        return [], [], [], empty, {}, {}

    yt_all, yp_all, fold_metrics = [], [], []
    yt_per_subj: dict = {}
    yp_per_subj: dict = {}
    youden_thresholds = []
    smote_count = 0

    for ts in unique_s:
        tr_mask = sids != ts
        te_mask = sids == ts
        X_tr, y_tr = X[tr_mask], y[tr_mask]
        X_te, y_te = X[te_mask], y[te_mask]

        if len(X_tr) == 0 or len(X_te) == 0:
            continue

        sc = StandardScaler()
        X_tr_s = sc.fit_transform(X_tr)
        X_te_s = sc.transform(X_te)

        # ── Sélection des meilleures features (feat78 → top 25, LOSO-safe) ────
        # mutual_info_regression capture les dépendances non-linéaires (mieux que f_regression)
        k = min(N_FEATURES_SELECT, X_tr_s.shape[1])
        selector = SelectKBest(mutual_info_regression, k=k)
        X_tr_s = selector.fit_transform(X_tr_s, y_tr)
        X_te_s = selector.transform(X_te_s)

        y_tr_bin = bin_scores(y_tr, THRESHOLD_DEFAULT)
        n_high   = int(np.sum(y_tr_bin == 1))
        n_low    = int(np.sum(y_tr_bin == 0))

        # ── ① SMOTE sur fold TRAIN (conc uniquement) ──────────────────────────
        if HAS_SMOTE and n_high >= 6 and target in SMOTE_TARGETS:
            k_neighbors = min(5, n_high - 1)
            sm = SMOTE(random_state=42, k_neighbors=k_neighbors)
            X_aug, y_bin_aug = sm.fit_resample(X_tr_s, y_tr_bin)

            n_orig = len(X_tr)
            y_aug  = np.zeros(len(X_aug))
            y_aug[:n_orig] = y_tr

            y_high_dist = y_tr[y_tr_bin == 1]
            y_low_dist  = y_tr[y_tr_bin == 0]
            rng = np.random.default_rng(42 + int(ts))
            for i in range(n_orig, len(X_aug)):
                y_aug[i] = (rng.choice(y_high_dist) if y_bin_aug[i] == 1
                             else rng.choice(y_low_dist))

            smote_applied = True
            smote_count  += 1
        else:
            X_aug, y_aug = X_tr_s, y_tr
            smote_applied = False

        # ── ② sample_weight plafonné à 2.5 ───────────────────────────────────
        # sans plafond, stress très déséquilibré (ratio≈10) effondre Specificity et MCC
        # He & Garcia (2009) IEEE TKDE recommandent ratio ≤ 3.0
        y_aug_bin  = bin_scores(y_aug, THRESHOLD_DEFAULT)
        n_high_aug = int(np.sum(y_aug_bin == 1))
        n_low_aug  = int(np.sum(y_aug_bin == 0))
        ratio      = min(float(n_low_aug) / max(float(n_high_aug), 1.0), 2.5)
        sw = np.where(y_aug_bin == 1, ratio, 1.0)

        # Optuna sur données pre-SMOTE, puis fit sur données augmentées
        mc = _build_optimized_model(model_name, X_tr_s, y_tr)
        try:
            mc.fit(X_aug, y_aug, sample_weight=sw)
        except TypeError:
            mc.fit(X_aug, y_aug)

        y_pred_tr = mc.predict(X_tr_s)
        y_pred_te = mc.predict(X_te_s)

        # ── ③ Seuil Youden sur fold TRAIN ────────────────────────────────────
        youden = find_youden_threshold(y_tr_bin, y_pred_tr)
        youden_thresholds.append(youden)

        fm = compute_full_metrics(y_te, y_pred_te, threshold=youden)
        fm['n_samples']       = len(y_te)
        fm['subject']         = int(ts)
        fm['smote_applied']   = smote_applied
        fm['youden_thresh']   = youden
        fm['n_high_train']    = n_high
        fm['n_low_train']     = n_low
        fm['imbalance_ratio'] = float(n_low / max(n_high, 1))

        # Métriques à seuil=5.0 pour comparaison directe avec baseline_feat78
        fm_std = compute_full_metrics(y_te, y_pred_te, threshold=THRESHOLD_DEFAULT)
        fm['sensitivity_std5']       = fm_std.get('sensitivity', 0)
        fm['specificity_std5']       = fm_std.get('specificity', 0)
        fm['mcc_std5']               = fm_std.get('mcc', 0)
        fm['auc_roc_std5']           = fm_std.get('auc_roc', 0)

        fold_metrics.append(fm)
        yt_all.extend(y_te.tolist())
        yp_all.extend(y_pred_te.tolist())
        yt_per_subj[int(ts)] = list(y_te)
        yp_per_subj[int(ts)] = list(y_pred_te)

    if not yt_all:
        gm = {'mae': 999., 'rmse': 999., 'r2': -99.}
    else:
        global_youden = float(np.mean(youden_thresholds)) if youden_thresholds else THRESHOLD_DEFAULT
        gm = compute_full_metrics(np.array(yt_all), np.array(yp_all), threshold=global_youden)

        gm_std = compute_full_metrics(
            np.array(yt_all), np.array(yp_all), threshold=THRESHOLD_DEFAULT
        )
        gm['youden_mean']            = global_youden
        gm['youden_std']             = float(np.std(youden_thresholds)) if len(youden_thresholds) > 1 else 0.0
        gm['smote_folds']            = smote_count
        gm['sensitivity_std5']       = gm_std.get('sensitivity', 0)
        gm['specificity_std5']       = gm_std.get('specificity', 0)
        gm['mcc_std5']               = gm_std.get('mcc', 0)
        gm['auc_roc_std5']           = gm_std.get('auc_roc', 0)
        gm['balanced_accuracy_std5'] = gm_std.get('balanced_accuracy', 0)

    gm['n_folds'] = len(fold_metrics)
    return yt_all, yp_all, fold_metrics, gm, yt_per_subj, yp_per_subj


# ─────────────────────────────────────────────────────────────────────────────
# ÉVALUATION VAL / TEST (features pré-calculées — pas d'extraction à la volée)
# ─────────────────────────────────────────────────────────────────────────────
def eval_split(model, scaler, split, feat_dir, youden_thresh):
    fp = feat_dir / f'{FEAT_PREFIX}_{split}.npy'
    yp = feat_dir / f'y_{split}.npy'
    if not fp.exists() or not yp.exists():
        return None
    X = np.load(fp)
    y = np.load(yp)
    if len(X) == 0:
        return None
    Xs   = scaler.transform(X)
    yhat = model.predict(Xs)
    m    = compute_full_metrics(y, yhat, threshold=youden_thresh)
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
    lo = min(yt_a.min(), yp_a.min()) - 0.5
    hi = max(yt_a.max(), yp_a.max()) + 0.5
    ax.plot([lo, hi], [lo, hi], 'k--', lw=1.5, label='Parfait')
    ax.set_xlabel(f'{score_label} réel')
    ax.set_ylabel(f'{score_label} prédit')
    ax.set_title(f'Prédit vs Réel — {model_name} (Exp.{exp})\n'
                 f'MAE={mean_absolute_error(yt_a,yp_a):.3f}  R²={r2_score(yt_a,yp_a):.3f}')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
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
    axes[0].set_xlabel('Résidu (prédit − réel)')
    axes[0].set_ylabel('Fréquence')
    axes[0].set_title(f'μ={residuals.mean():.3f}  σ={residuals.std():.3f}')
    axes[1].scatter(np.array(yt), residuals, alpha=0.4, s=15,
                    color=COLORS.get(model_name, '#3498DB'))
    axes[1].axhline(0, color='red', lw=1.5, linestyle='--')
    axes[1].set_xlabel('Score réel')
    axes[1].set_ylabel('Résidu')
    axes[1].set_title('Résidus vs Score réel')
    plt.tight_layout()
    plt.savefig(str(out_dir / 'residuals_distribution.png'), dpi=150)
    plt.close()


def plot_youden_roc(yt, yp, model_name, exp, youden_thresh, out_dir):
    """Courbe ROC avec marqueur du seuil Youden et du seuil fixe 5.0."""
    yt_a = np.array(yt)
    yp_a = np.array(yp)
    y_bin = bin_scores(yt_a, THRESHOLD_DEFAULT)
    if len(np.unique(y_bin)) < 2:
        return

    fpr, tpr, _ = sk_roc_curve(y_bin, yp_a)
    from sklearn.metrics import auc as sk_auc
    auc_val = sk_auc(fpr, tpr)

    def get_sens_spec(thresh):
        yp_b = bin_scores(yp_a, thresh)
        tp = int(np.sum((yp_b == 1) & (y_bin == 1)))
        fp = int(np.sum((yp_b == 1) & (y_bin == 0)))
        tn = int(np.sum((yp_b == 0) & (y_bin == 0)))
        fn = int(np.sum((yp_b == 0) & (y_bin == 1)))
        return tp / max(tp + fn, 1), tn / max(tn + fp, 1)

    sens_y, spec_y = get_sens_spec(youden_thresh)
    sens_5, spec_5 = get_sens_spec(5.0)

    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr, color=COLORS.get(model_name, '#3498DB'), lw=2,
            label=f'AUC = {auc_val:.3f}')
    ax.fill_between(fpr, tpr, alpha=0.1, color=COLORS.get(model_name, '#3498DB'))
    ax.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Aléatoire')
    ax.scatter([1 - spec_5], [sens_5], marker='D', s=120, color='gray', zorder=4,
               label=f'Seuil=5.0  Sens={sens_5:.2f}  Spec={spec_5:.2f}')
    ax.scatter([1 - spec_y], [sens_y], marker='*', s=220, color='crimson', zorder=5,
               label=f'Youden={youden_thresh:.2f}  Sens={sens_y:.2f}  Spec={spec_y:.2f}')
    ax.set_xlabel('FPR (1 − Spécificité)')
    ax.set_ylabel('TPR (Sensibilité)')
    ax.set_title(f'ROC + Youden — {model_name} (Exp.{exp})  [feat78]')
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(out_dir / 'youden_roc.png'), dpi=150)
    plt.close()


def plot_folds(fold_metrics, model_name, exp, out_dir):
    if not fold_metrics:
        return
    folds = np.arange(1, len(fold_metrics) + 1)
    fig, axes = plt.subplots(2, 3, figsize=(18, 8))
    fig.suptitle(f'Métriques LOSO — {model_name} (Exp.{exp})  feat78 [SMOTE+sw+Youden]',
                 fontsize=11)
    specs = [
        (axes[0, 0], 'mae',         'MAE',         '#E74C3C', False),
        (axes[0, 1], 'r2',          'R²',           '#27AE60', False),
        (axes[0, 2], 'auc_roc',     'AUC (Youden)', '#F39C12', False),
        (axes[1, 0], 'sensitivity', 'Sensitivity',  '#E74C3C', True),
        (axes[1, 1], 'specificity', 'Specificity',  '#3498DB', True),
        (axes[1, 2], 'mcc',         'MCC',          '#27AE60', True),
    ]
    for ax, key, ylabel, color, show_std5 in specs:
        vals = [m.get(key, 0) for m in fold_metrics]
        ax.plot(folds, vals, 'o-', color=color, lw=2, markersize=5,
                label=f'Youden μ={np.mean(vals):.3f}')
        ax.axhline(np.mean(vals), color=color, lw=1.5, linestyle='--')
        if show_std5:
            key5  = key + '_std5'
            vals5 = [m.get(key5, 0) for m in fold_metrics]
            ax.plot(folds, vals5, 's:', color='gray', lw=1.2, markersize=4,
                    alpha=0.8, label=f'Seuil=5.0 μ={np.mean(vals5):.3f}')
        ax.set_xlabel('Sujet (fold)')
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel)
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(str(out_dir / 'fold_metrics.png'), dpi=150)
    plt.close()


def plot_comparison(results, target, out_dir):
    exps_ok = [e for e in EXPERIMENTS if e in results]
    if not exps_ok:
        return
    fig, axes = plt.subplots(1, 4, figsize=(24, 5))
    x = np.arange(len(exps_ok))
    w = 0.14
    for idx, (metric, ylabel, lower_is_better) in enumerate([
        ('mae',         'MAE ↓',         True),
        ('auc_roc',     'AUC ↑',         False),
        ('mcc',         'MCC ↑',         False),
        ('sensitivity', 'Sensitivity ↑', False),
    ]):
        ax = axes[idx]
        for i, mn in enumerate(MODELS):
            vals = [results[e].get(mn, {}).get(metric, 0) for e in exps_ok]
            ax.bar(x + i * w, vals, w, label=mn,
                   color=COLORS.get(mn, '#7F8C8D'), alpha=0.85)
        ax.set_xticks(x + w * 2.5)
        ax.set_xticklabels(exps_ok)
        ax.set_ylabel(ylabel)
        ax.set_title(ylabel)
        ax.legend(fontsize=7)
        ax.grid(alpha=0.3)
        if not lower_is_better:
            ax.set_ylim([-0.3, 1.15])
    plt.suptitle(
        f'NeuroCap — feat78 SMOTE+sample_weight+Youden — {target}\n'
        f'[Ref 1] Chawla 2002  [Ref 2] He&Garcia 2009  [Ref 3] Youden 1950',
        fontsize=11,
    )
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(str(out_dir / 'comparison_all.png'), dpi=150)
    plt.close()


def plot_comparison_smote_vs_baseline(results_smote, results_baseline, target, out_dir):
    """Barres hachurées = baseline feat78 · barres pleines = feat78 SMOTE."""
    exps_ok = [e for e in EXPERIMENTS
               if e in results_smote and e in (results_baseline or {})]
    if not exps_ok or not results_baseline:
        return
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    x = np.arange(len(exps_ok))
    w = 0.10
    for idx, (metric, ylabel) in enumerate([
        ('sensitivity', 'Sensitivity'),
        ('specificity', 'Specificity'),
        ('mcc',         'MCC'),
    ]):
        ax = axes[idx]
        for i, mn in enumerate(MODELS):
            vals_s = [results_smote[e].get(mn, {}).get(metric, 0) for e in exps_ok]
            vals_b = [results_baseline.get(e, {}).get(mn, {}).get(metric, 0)
                      for e in exps_ok]
            ax.bar(x + (2*i)*w,   vals_b, w, color=COLORS.get(mn, '#7F8C8D'),
                   alpha=0.4, hatch='//', label=f'{mn} baseline')
            ax.bar(x + (2*i+1)*w, vals_s, w, color=COLORS.get(mn, '#7F8C8D'),
                   alpha=0.9, label=f'{mn} SMOTE')
        ax.set_xticks(x + w * len(MODELS))
        ax.set_xticklabels(exps_ok)
        ax.set_ylabel(ylabel)
        ax.set_title(f'{ylabel}\n(hachure=baseline · plein=SMOTE)')
        ax.legend(fontsize=5, ncol=2)
        ax.grid(alpha=0.3)
        ax.set_ylim([0, 1.2])
    plt.suptitle(f'feat78 — Impact SMOTE+sample_weight+Youden vs Baseline — {target}',
                 fontsize=12)
    plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig(str(out_dir / 'smote_vs_baseline.png'), dpi=150)
    plt.close()


# ─────────────────────────────────────────────────────────────────────────────
# ANALYSE PROFESSIONNELLE (Niveaux 2-5)
# ─────────────────────────────────────────────────────────────────────────────
def run_professional_analysis(
    yt, yp, fold_metrics, yt_per_subj, yp_per_subj,
    mn, exp, out_dir, target, global_youden,
):
    yt_a = np.array(yt, dtype=float)
    yp_a = np.array(yp, dtype=float)
    result = {}

    print(f"      [Niv.2] Bootstrap CI (N=500)...", end=' ', flush=True)
    t0  = time.time()
    bci = bootstrap_ci(yt_a, yp_a, threshold=global_youden)
    pt  = permutation_test(yt_a, yp_a, threshold=global_youden)
    print(f"{time.time()-t0:.1f}s")
    result['bootstrap_ci'] = bci
    result['permutation']  = pt

    print(f"      [Niv.3] Calibration + Bland-Altman + ICC...", end=' ', flush=True)
    t0  = time.time()
    cal = calibration_analysis(yt_a, yp_a, threshold=global_youden)
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
    dl  = delong_auc_ci(bin_scores(yt_a, THRESHOLD_DEFAULT), yp_a)
    fm0 = compute_full_metrics(yt_a, yp_a, threshold=global_youden)
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
                               threshold=global_youden)
    plot_reliability_diagram(yt_a, yp_a, mn, out_dir / 'reliability_diagram.png')
    plot_bland_altman(yt_a, yp_a, mn, out_dir / 'bland_altman.png')
    plot_bootstrap_ci_bars(bci, mn, out_dir / 'bootstrap_ci.png')
    plot_decision_curve(dca, mn, out_dir / 'decision_curve.png')
    if psm.get('per_subject'):
        plot_per_subject_heatmap(psm, target, out_dir / 'per_subject_heatmap.png')

    print(f"      AUC={fm0.get('auc_roc',0):.4f}  "
          f"[{bci.get('auc_roc',{}).get('ci_lo',0):.3f},"
          f"{bci.get('auc_roc',{}).get('ci_hi',0):.3f}]  "
          f"p={pt.get('auc_roc',{}).get('p_value',1):.4f}")
    print(f"      Sens={fm0.get('sensitivity',0):.3f}  "
          f"Spec={fm0.get('specificity',0):.3f}  "
          f"MCC={fm0.get('mcc',0):.3f}  "
          f"Youden={global_youden:.3f}")
    return result


# ─────────────────────────────────────────────────────────────────────────────
# MAIN RUN_TARGET
# ─────────────────────────────────────────────────────────────────────────────
def run_target(target, baseline_results=None):
    feat_dir    = FEAT_ROOT  / target
    out_root    = OUTPUT_ROOT / target
    mdl_root    = MODEL_ROOT  / target
    score_label = TARGETS[target]

    if not feat_dir.exists():
        print(f"  [SKIP] {feat_dir} introuvable")
        return {}

    out_root.mkdir(parents=True, exist_ok=True)
    mdl_root.mkdir(parents=True, exist_ok=True)

    all_results  = {}
    best_r2      = -99.
    best_auc     = 0.0
    best_cfg     = None
    models_fold_r2:  dict = {mn: {} for mn in MODELS}
    models_fold_auc: dict = {mn: {} for mn in MODELS}

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

        y_bin_all = bin_scores(y, THRESHOLD_DEFAULT)
        n_low_g   = int(np.sum(y_bin_all == 0))
        n_high_g  = int(np.sum(y_bin_all == 1))

        print(f"\n{'='*70}")
        print(f"  {target.upper()}  Exp.{exp} | {X.shape[0]} epochs | "
              f"{X.shape[1]} features | {len(np.unique(sids))} sujets")
        print(f"  Imbalance : Low={n_low_g} ({100*n_low_g/len(y):.0f}%) "
              f"High={n_high_g} ({100*n_high_g/len(y):.0f}%)")
        print(f"  SMOTE={HAS_SMOTE} | sample_weight=ratio | threshold=Youden(auto)")
        print(f"{'='*70}")

        all_results[exp] = {}
        exp_fold_r2_all  = {}
        exp_fold_auc_all = {}

        for mn, model in MODELS.items():
            print(f"\n  ▶ {mn}")
            t0 = time.time()

            (yt, yp, fms, gm,
             yt_per_subj, yp_per_subj) = loso_cv_smote(X_loso, y, sids, model, mn, target=target)
            dt = time.time() - t0

            if not yt:
                continue

            youden_mean = gm.get('youden_mean', THRESHOLD_DEFAULT)
            smote_folds = gm.get('smote_folds', 0)

            print(f"    LOSO ({dt:.1f}s) | SMOTE={smote_folds}/{gm['n_folds']} folds | "
                  f"Youden={youden_mean:.3f} ± {gm.get('youden_std',0):.3f}")
            print(f"    [Youden]    MAE={gm['mae']:.4f}  R²={gm['r2']:.4f}  "
                  f"AUC={gm.get('auc_roc',0):.4f}  "
                  f"Sens={gm.get('sensitivity',0):.4f}  "
                  f"Spec={gm.get('specificity',0):.4f}  "
                  f"MCC={gm.get('mcc',0):.4f}")
            print(f"    [Seuil=5.0] "
                  f"Sens={gm.get('sensitivity_std5',0):.4f}  "
                  f"Spec={gm.get('specificity_std5',0):.4f}  "
                  f"MCC={gm.get('mcc_std5',0):.4f}  "
                  f"AUC={gm.get('auc_roc_std5',0):.4f}")

            od = out_root / exp / mn.replace(' ', '_')
            od.mkdir(parents=True, exist_ok=True)

            plot_scatter(yt, yp, mn, exp, score_label, od)
            plot_residuals(yt, yp, mn, exp, od)
            plot_youden_roc(yt, yp, mn, exp, youden_mean, od)
            plot_folds(fms, mn, exp, od)

            prof = run_professional_analysis(
                yt, yp, fms, yt_per_subj, yp_per_subj,
                mn, exp, od, target, youden_mean,
            )

            all_results[exp][mn] = {**gm, 'professional': prof}

            fold_r2  = [m.get('r2',      0) for m in fms]
            fold_auc = [m.get('auc_roc', 0) for m in fms]
            exp_fold_r2_all[mn]      = fold_r2
            exp_fold_auc_all[mn]     = fold_auc
            models_fold_r2[mn][exp]  = fold_r2
            models_fold_auc[mn][exp] = fold_auc

            # Val / Test avec seuil Youden
            Xb  = np.load(ff)
            sc  = StandardScaler()
            Xb_s = sc.fit_transform(Xb)
            y_bin_b = bin_scores(y, THRESHOLD_DEFAULT)
            n_h = int(np.sum(y_bin_b == 1))
            n_l = int(np.sum(y_bin_b == 0))
            sw_all = np.where(y_bin_b == 1, float(n_l) / max(n_h, 1), 1.0)
            mf = clone(model)
            try:
                mf.fit(Xb_s, y, sample_weight=sw_all)
            except TypeError:
                mf.fit(Xb_s, y)
            vm = eval_split(mf, sc, 'val',  feat_dir, youden_mean)
            tm = eval_split(mf, sc, 'test', feat_dir, youden_mean)
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
            wilcox_r2  = run_wilcoxon_all_pairs(exp_fold_r2_all,  metric='r2')
            wilcox_auc = run_wilcoxon_all_pairs(exp_fold_auc_all, metric='auc_roc')
            od_exp = out_root / exp
            od_exp.mkdir(parents=True, exist_ok=True)
            plot_wilcoxon_heatmap(wilcox_r2,  list(exp_fold_r2_all.keys()),
                                  'R²',  f'Exp.{exp} feat78 SMOTE', od_exp / 'wilcoxon_r2.png')
            plot_wilcoxon_heatmap(wilcox_auc, list(exp_fold_auc_all.keys()),
                                  'AUC', f'Exp.{exp} feat78 SMOTE', od_exp / 'wilcoxon_auc.png')
            all_results[exp]['_wilcoxon'] = {'r2': wilcox_r2, 'auc_roc': wilcox_auc}

    # Friedman global
    if best_cfg:
        best_exp = best_cfg[0]
        fold_r2_best = {mn: models_fold_r2[mn].get(best_exp, [])
                        for mn in MODELS if models_fold_r2[mn].get(best_exp)}
        if len(fold_r2_best) >= 3:
            friedman_result = run_friedman_test(fold_r2_best)
            p_f = friedman_result.get('p_value', 1)
            sig = '✅ p<0.05' if friedman_result.get('significant') else '❌ ns'
            print(f"\n  [Friedman] Exp.{best_exp}: p={p_f:.4f}  {sig}")
            all_results['_friedman'] = friedman_result

    # Tableau récapitulatif
    print(f"\n{'='*120}")
    print(f"{'Exp':>5}|{'Modèle':>15}|{'MAE':>8}|{'R²':>8}|"
          f"{'AUC(Y)':>8}|{'Sens(Y)':>8}|{'Spec(Y)':>8}|{'MCC(Y)':>8}|"
          f"{'Sens(5)':>8}|{'MCC(5)':>8}|{'Youden':>8}")
    print("-" * 120)
    for exp in EXPERIMENTS:
        if exp not in all_results:
            continue
        for mn in MODELS:
            if mn not in all_results[exp]:
                continue
            m     = all_results[exp][mn]
            print(f"{exp:>5}|{mn:>15}|{m['mae']:>8.4f}|{m['r2']:>8.4f}|"
                  f"{m.get('auc_roc',0):>8.4f}|{m.get('sensitivity',0):>8.4f}|"
                  f"{m.get('specificity',0):>8.4f}|{m.get('mcc',0):>8.4f}|"
                  f"{m.get('sensitivity_std5',0):>8.4f}|{m.get('mcc_std5',0):>8.4f}|"
                  f"{m.get('youden_mean',5.0):>8.3f}")

    if best_cfg:
        print(f"\n★ Meilleur R²  : {best_cfg[1]} Exp.{best_cfg[0]} (R²={best_r2:.4f})")
        print(f"★ Meilleur AUC : {best_auc:.4f}")

    plot_comparison(all_results, target, out_root)
    if baseline_results and target in baseline_results:
        plot_comparison_smote_vs_baseline(
            all_results, baseline_results[target], target, out_root
        )

    # JSON
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
            'config': {
                'smote':          HAS_SMOTE,
                'sample_weight':  'ratio=n_Low/n_High',
                'feat_prefix':    FEAT_PREFIX,
                'n_features':     78,
                'threshold_label': THRESHOLD_DEFAULT,
                'threshold_pred':  'youden_per_fold',
                'references': {
                    'SMOTE':         'Chawla et al. (2002) JAIR 16:321-357',
                    'sample_weight': 'He & Garcia (2009) IEEE TKDE 21(9)',
                    'youden':        'Youden (1950) Cancer 3(1):32-35',
                    'mcc_priority':  'Chicco & Jurman (2020) BMC Genomics 21:6',
                },
            },
        }, f, indent=2, default=str)
    print(f"\n  JSON : {json_path.relative_to(PROJECT_ROOT)}")

    _write_text_report(out_root, target, all_results, best_cfg, best_r2, best_auc)

    # Sauvegarder le meilleur modèle
    if best_cfg:
        be  = best_cfg[0]
        Xb  = np.load(feat_dir / f'{FEAT_PREFIX}_train_{be}.npy')
        yb  = np.load(feat_dir / f'y_train_{be}.npy')
        sc  = StandardScaler()
        Xb_s = sc.fit_transform(Xb)
        y_bin_b = bin_scores(yb, THRESHOLD_DEFAULT)
        n_h = int(np.sum(y_bin_b == 1))
        n_l = int(np.sum(y_bin_b == 0))
        if HAS_SMOTE and n_h >= 6:
            sm = SMOTE(random_state=42, k_neighbors=min(5, n_h-1))
            X_aug_b, y_bin_aug_b = sm.fit_resample(Xb_s, y_bin_b)
            y_aug_b = np.zeros(len(X_aug_b))
            y_aug_b[:len(yb)] = yb
            y_hd = yb[y_bin_b == 1]
            y_ld = yb[y_bin_b == 0]
            rng  = np.random.default_rng(42)
            for i in range(len(yb), len(X_aug_b)):
                y_aug_b[i] = rng.choice(y_hd) if y_bin_aug_b[i] == 1 else rng.choice(y_ld)
        else:
            X_aug_b, y_aug_b = Xb_s, yb
        y_aug_bin_b = bin_scores(y_aug_b, THRESHOLD_DEFAULT)
        n_h2 = int(np.sum(y_aug_bin_b == 1))
        n_l2 = int(np.sum(y_aug_bin_b == 0))
        sw_b = np.where(y_aug_bin_b == 1, float(n_l2) / max(n_h2, 1), 1.0)
        model = MODELS[best_cfg[1]]
        mf    = clone(model)
        try:
            mf.fit(X_aug_b, y_aug_b, sample_weight=sw_b)
        except TypeError:
            mf.fit(X_aug_b, y_aug_b)
        mn_safe = best_cfg[1].replace(' ', '_')
        joblib.dump(mf, mdl_root / f'{mn_safe}_{target}_feat78_smote.joblib')
        joblib.dump(sc, mdl_root / f'{mn_safe}_{target}_scaler_feat78_smote.joblib')
        print(f"  Modèle : {mn_safe}_{target}_feat78_smote.joblib")

    return all_results


def _write_text_report(out_root, target, all_results, best_cfg, best_r2, best_auc):
    with open(out_root / f'report_{target}.txt', 'w', encoding='utf-8') as f:
        f.write(f"NeuroCap — feat78 SMOTE+sample_weight+Youden — {target}\n")
        f.write("=" * 90 + "\n")
        f.write("Légende : (Y)=seuil Youden · (5)=seuil fixe 5.0\n")
        f.write("Refs : [1]Chawla2002  [2]He&Garcia2009  [3]Youden1950\n\n")
        f.write(f"{'Exp':>5}|{'Modèle':>15}|{'MAE':>8}|{'R²':>8}|"
                f"{'AUC(Y)':>8}|{'Sens(Y)':>8}|{'Spec(Y)':>8}|{'MCC(Y)':>8}|"
                f"{'Sens(5)':>8}|{'MCC(5)':>8}|{'Youden':>8}\n")
        f.write("-" * 90 + "\n")
        for exp in EXPERIMENTS:
            if exp not in all_results:
                continue
            for mn in MODELS:
                if mn not in all_results[exp]:
                    continue
                m     = all_results[exp][mn]
                f.write(f"{exp:>5}|{mn:>15}|{m['mae']:>8.4f}|{m['r2']:>8.4f}|"
                        f"{m.get('auc_roc',0):>8.4f}|{m.get('sensitivity',0):>8.4f}|"
                        f"{m.get('specificity',0):>8.4f}|{m.get('mcc',0):>8.4f}|"
                        f"{m.get('sensitivity_std5',0):>8.4f}|{m.get('mcc_std5',0):>8.4f}|"
                        f"{m.get('youden_mean',5.0):>8.3f}\n")
        if best_cfg:
            f.write(f"\n★ R²  : {best_cfg[1]} Exp.{best_cfg[0]} (R²={best_r2:.4f})\n")
            f.write(f"★ AUC : {best_auc:.4f}\n")


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 75)
    print("NeuroCap — feat78 Régression + SMOTE + sample_weight + Youden")
    print("Modèles : SVR · RF · XGBoost · LightGBM (régresseurs)")
    print("Features: 78 pré-calculées (PSD · Ratios · Hjorth · DWT · Texturales · NL)")
    print()
    print("Références :")
    print("  [1] Chawla et al. (2002) SMOTE       — JAIR 16:321-357")
    print("  [2] He & Garcia  (2009) Imbalanced   — IEEE TKDE 21(9)")
    print("  [3] Youden       (1950) Threshold    — Cancer 3(1):32-35")
    print("  [4] Chicco&Jurman(2020) MCC          — BMC Genomics 21:6")
    print("=" * 75)
    print(f"SMOTE  : {'actif' if HAS_SMOTE else 'désactivé (pip install imbalanced-learn)'}")
    print(f"Sorties: {OUTPUT_ROOT.relative_to(PROJECT_ROOT)}/")
    print()

    # Charger résultats baseline feat78 pour la figure comparative
    baseline_results = {}
    for target in ['conc', 'stress']:
        bp = (PROJECT_ROOT / 'reports' / 'Regression' / 'Baseline'
              / 'feat78' / target / f'results_{target}.json')
        if bp.exists():
            with open(bp) as f:
                data = json.load(f)
            baseline_results[target] = data.get('loso', {})
            print(f"  Baseline feat78 chargé pour {target} (comparaison activée)")
        else:
            print(f"  [INFO] Pas de baseline feat78 pour {target} — "
                  f"lancez baseline_ML_regression_feature_eng.py d'abord")

    for target in ['conc', 'stress']:
        print(f"\n{'#'*65}")
        print(f"# TARGET : {target.upper()}")
        print(f"{'#'*65}")
        run_target(target, baseline_results=baseline_results)

    print(f"\n{'='*75}")
    print("✅ Terminé")
    print(f"   Rapports : {OUTPUT_ROOT.relative_to(PROJECT_ROOT)}/")
    print(f"   Modèles  : {MODEL_ROOT.relative_to(PROJECT_ROOT)}/")
    print()
    print("PROCHAINE ÉTAPE :")
    print("   python src/models/baselines/compare_regression_features.py")


if __name__ == "__main__":
    main()
