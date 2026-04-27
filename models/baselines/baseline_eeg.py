"""
=============================================================================
NeuroCap – Baseline Machine Learning complet + sauvegarde des modèles finaux
Canal Fp2, validation LOSO, features extraites, métriques médicales
=============================================================================
Auteur      : Yasmine El Mkhantar
Encadrement : Monir El Azzouzi | Loubna El Rhali | Yassir Matrane
Structure   : Easy Medical Device — 2025-2026

=== RÔLE DU SCRIPT ===

Ce script exécute 3 étapes pour chaque expérience d'augmentation (A,B,C,D,FULL)
et chaque classifieur (SVM, Random Forest, XGBoost) :

  ÉTAPE 1 — Validation LOSO (Leave-One-Subject-Out)
    → Évalue la capacité de généralisation à un NOUVEAU sujet
    → Produit les métriques et visualisations dans outputs_baseline/

  ÉTAPE 2 — Évaluation sur Val/Test (NON augmentés)
    → NOUVEAU : évalue chaque modèle sur les données val et test
    → Ces données n'ont JAMAIS été vues pendant l'entraînement
    → Métriques sauvegardées dans le rapport final

  ÉTAPE 3 — Entraînement et sauvegarde du modèle final
    → Entraîne sur TOUTES les données de la MEILLEURE expérience
    → Sauvegarde dans baseline_models/ avec le scaler

=== CORRECTIONS PAR RAPPORT À LA VERSION PRÉCÉDENTE ===

1. ÉVALUATION VAL/TEST AJOUTÉE
   → La version précédente n'évaluait PAS sur val/test
   → Maintenant : chaque modèle est évalué sur features_val.npy et features_test.npy
   → Résultats inclus dans le rapport final

2. SÉLECTION EXPLICITE DE L'EXPÉRIENCE POUR LE MODÈLE FINAL
   → Avant : le modèle final était celui de la DERNIÈRE expérience (accident)
   → Maintenant : on choisit automatiquement la meilleure expérience par F1-score
   → L'utilisateur peut aussi forcer une expérience via BEST_EXP

3. MEILLEURE GESTION DE LA LOSO
   → Vérification que subject_ids contient bien >1 sujet unique
   → Gestion des cas où un fold contient une seule classe
   → Sauvegarde du nombre de folds effectifs vs total

4. RAPPORT COMPLET
   → Tableau comparatif ASCII dans le terminal
   → Fichier report_all.txt enrichi avec val/test et recommandation

=== CLASSIFIEURS UTILISÉS (CdC Section 2.4.1) ===

Phase 1 — SVM (Support Vector Machine)
  • Noyau RBF : projette les données dans un espace de haute dimension
  • C=1.0 : compromis régularisation/ajustement
  • gamma='scale' : adapte le noyau à la variance des données
  • probability=True : nécessaire pour predict_proba()
  • Avantage : bonne généralisation, < 1 ms en inférence
  • Référence : Sharma (2021, N°1), Saeed (2020, N°9)

Phase 2 — Random Forest
  • n_estimators=100 : 100 arbres de décision
  • max_depth=10 : limite la profondeur (évite le surapprentissage)
  • Avantage : robuste, interprétable (importances des features)
  • Performance : 86-94% sur EEG frontal (Samsa 2026, Vettivel 2018)

Phase 2 — XGBoost (eXtreme Gradient Boosting)
  • n_estimators=100 : 100 itérations de boosting
  • max_depth=6, learning_rate=0.1 : contrôle du surapprentissage
  • eval_metric='logloss' : perte logarithmique binaire
  • Avantage : très performant, gère les déséquilibres
  • Référence : Pandya (2025, N°13)

=== MÉTRIQUES MÉDICALES ===

| Métrique    | Formule               | Interprétation clinique                     |
|-------------|----------------------|---------------------------------------------|
| Accuracy    | (VP+VN)/Total        | Proportion totale de bonnes classifications |
| Precision   | VP/(VP+FP)           | Quand prédit Stress → vraiment Stress ?     |
| Recall      | VP/(VP+FN)           | Stress réels détectés ? (ne pas en rater)   |
| F1-score    | 2×P×R/(P+R)          | Moyenne harmonique (classes déséquilibrées) |
| Spécificité | VN/(VN+FP)           | Concentration bien identifiée ?             |
| AUC-ROC     | Aire sous courbe ROC | Discrimination globale (1=parfait, 0.5=aléa)|
=============================================================================
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Backend non-interactif pour serveur
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
                             confusion_matrix, roc_curve, auc, classification_report,
                             roc_auc_score)
from sklearn.preprocessing import StandardScaler
import os
import warnings
import joblib
from pathlib import Path
import json
import time

warnings.filterwarnings('ignore')

# ============================================================================
# STYLE ET COULEURS
# ============================================================================
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("Set2")
COLORS = {
    'SVM': '#E74C3C',
    'Random Forest': '#2980B9',
    'XGBoost': '#27AE60'
}

# ============================================================================
# PARAMÈTRES GLOBAUX
# ============================================================================

# Dossier contenant les features extraites par extract_features_for_baseline.py
FEATURES_DIR = Path(__file__).resolve().parent / 'datasets_features'

# Expériences d'augmentation à évaluer
EXPERIMENTS = ['A', 'B', 'C', 'D', 'FULL']

# Les 3 classifieurs (Phase 1-2 du CdC)
MODELS = {
    'SVM': SVC(
        kernel='rbf',        # Noyau gaussien (projection non-linéaire)
        C=1.0,               # Régularisation (1.0 = compromis par défaut)
        gamma='scale',       # γ = 1/(n_features × var(X))
        probability=True,    # Active predict_proba() (nécessaire pour AUC)
        random_state=42      # Reproductibilité
    ),
    'Random Forest': RandomForestClassifier(
        n_estimators=100,    # 100 arbres (consensus littérature)
        max_depth=10,        # Limite profondeur → réduit surapprentissage
        random_state=42
    ),
    'XGBoost': XGBClassifier(
        n_estimators=100,    # 100 itérations de boosting
        max_depth=6,         # Arbres moins profonds que RF
        learning_rate=0.1,   # Taux d'apprentissage (prudent)
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42,
        verbosity=0          # Supprime les messages XGBoost
    )
}

# Dossiers de sortie
OUTPUT_DIR = Path(__file__).resolve().parent / 'outputs_baseline'
MODEL_SAVE_ROOT = Path(__file__).resolve().parent / 'baseline_models'


# ============================================================================
# FONCTIONS DE CALCUL DES MÉTRIQUES
# ============================================================================

def compute_metrics(y_true, y_pred, y_proba=None):
    """
    Calcule les 6 métriques médicales pour une classification binaire.

    Gère le cas où la matrice de confusion est 1×1 (une seule classe dans y_true).
    Ce cas arrive quand un sujet LOSO n'a qu'un seul type d'époque
    (ex: uniquement concentration ou uniquement stress).

    Paramètres :
    - y_true : vrais labels (0=concentration, 1=stress)
    - y_pred : labels prédits
    - y_proba : probabilités de la classe positive (pour AUC)

    Retourne :
    - dict avec 6 métriques + indicateur de validité
    """
    cm = confusion_matrix(y_true, y_pred)

    # Gestion matrice 1×1 (une seule classe dans y_true ou y_pred)
    if cm.size == 1:
        val = cm[0, 0]
        unique_label = np.unique(y_true)[0]
        if unique_label == 1:
            tp, tn, fp, fn = val, 0, 0, 0
        else:
            tn, tp, fp, fn = val, 0, 0, 0
    else:
        tn, fp, fn, tp = cm.ravel()

    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, zero_division=0),
        'recall': recall_score(y_true, y_pred, zero_division=0),
        'f1': f1_score(y_true, y_pred, zero_division=0),
        'specificity': tn / (tn + fp) if (tn + fp) > 0 else 0.0,
        'valid': len(np.unique(y_true)) > 1  # True si les 2 classes sont présentes
    }

    if y_proba is not None:
        try:
            metrics['auc'] = roc_auc_score(y_true, y_proba)
        except ValueError:
            metrics['auc'] = 0.5  # AUC non calculable (une seule classe)
    else:
        metrics['auc'] = 0.5

    return metrics


def loso_cross_validation(X, y, subject_ids, model):
    """
    Validation croisée Leave-One-Subject-Out (LOSO).

    C'est le GOLD STANDARD pour l'EEG car elle évalue la capacité du modèle
    à généraliser à un sujet TOTALEMENT NOUVEAU (jamais vu pendant l'entraînement).

    Principe :
    - On a N sujets dans le train
    - Pour chaque sujet s (fold) :
      1. Train = tous les sujets SAUF s
      2. Test = sujet s uniquement
      3. StandardScaler fit sur train UNIQUEMENT (pas de data leakage)
      4. Entraîner le modèle sur train, évaluer sur test
    - Métriques finales = agrégation sur tous les folds

    Paramètres :
    - X : features (n_epochs, 15)
    - y : labels (n_epochs,)
    - subject_ids : identifiant du sujet pour chaque époque (n_epochs,)
    - model : instance sklearn non entraînée

    Retourne :
    - y_true_all : vrais labels agrégés
    - y_pred_all : prédictions agrégées
    - y_proba_all : probabilités agrégées
    - per_fold_metrics : liste de dicts (une métrique par fold)
    - global_metrics : dict des métriques globales
    """
    unique_subjects = np.unique(subject_ids)
    n_folds = len(unique_subjects)

    if n_folds < 2:
        print("      ⚠️  Moins de 2 sujets uniques → LOSO impossible")
        return [], [], [], [], {'accuracy': 0, 'f1': 0, 'auc': 0,
                                 'precision': 0, 'recall': 0, 'specificity': 0}

    y_true_all, y_pred_all, y_proba_all = [], [], []
    per_fold_metrics = []
    n_valid_folds = 0

    for fold_idx, test_subj in enumerate(unique_subjects):
        # Séparation train/test pour ce fold
        train_mask = subject_ids != test_subj
        test_mask = subject_ids == test_subj

        X_train, y_train = X[train_mask], y[train_mask]
        X_test, y_test = X[test_mask], y[test_mask]

        # Vérification : au moins 2 classes dans le train
        if len(np.unique(y_train)) < 2:
            # Skip ce fold (le modèle ne peut pas apprendre)
            fold_metrics = {
                'accuracy': 0, 'precision': 0, 'recall': 0,
                'f1': 0, 'specificity': 0, 'auc': 0.5,
                'n_samples': len(y_test), 'valid': False,
                'subject': int(test_subj)
            }
            per_fold_metrics.append(fold_metrics)
            continue

        # StandardScaler : fit sur train UNIQUEMENT (pas de data leakage)
        # Le scaler centre (µ→0) et réduit (σ→1) chaque feature
        # indépendamment, en utilisant les statistiques du train seul
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)  # Utilise les stats du TRAIN

        # Clone du modèle (nouvel objet avec mêmes hyperparamètres)
        model_clone = model.__class__(**model.get_params())
        model_clone.fit(X_train_scaled, y_train)

        # Prédictions
        y_pred = model_clone.predict(X_test_scaled)
        y_proba = None
        if hasattr(model_clone, 'predict_proba'):
            y_proba = model_clone.predict_proba(X_test_scaled)[:, 1]

        # Agrégation
        y_true_all.extend(y_test)
        y_pred_all.extend(y_pred)
        if y_proba is not None:
            y_proba_all.extend(y_proba)

        # Métriques par fold
        fold_metrics = compute_metrics(y_test, y_pred, y_proba)
        fold_metrics['n_samples'] = len(y_test)
        fold_metrics['subject'] = int(test_subj)
        per_fold_metrics.append(fold_metrics)

        if fold_metrics['valid']:
            n_valid_folds += 1

    # Métriques globales (agrégées sur tous les folds)
    if y_true_all:
        global_metrics = compute_metrics(
            y_true_all, y_pred_all,
            y_proba_all if y_proba_all else None
        )
    else:
        global_metrics = {'accuracy': 0, 'f1': 0, 'auc': 0,
                          'precision': 0, 'recall': 0, 'specificity': 0}

    global_metrics['n_folds_total'] = n_folds
    global_metrics['n_folds_valid'] = n_valid_folds

    return y_true_all, y_pred_all, y_proba_all, per_fold_metrics, global_metrics


# ============================================================================
# FONCTIONS DE VISUALISATION
# ============================================================================

def plot_confusion_matrix_normalized(y_true, y_pred, model_name, exp_name, save_dir):
    """Matrice de confusion normalisée (% par ligne = par classe réelle)."""
    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (1, 1):
        cm = np.array([[cm[0, 0], 0], [0, 0]])
    cm_norm = cm.astype('float') / (cm.sum(axis=1)[:, np.newaxis] + 1e-12)

    plt.figure(figsize=(6, 5))
    sns.heatmap(cm_norm, annot=True, fmt='.2%', cmap='Blues',
                xticklabels=['Concentration', 'Stress'],
                yticklabels=['Concentration', 'Stress'])
    plt.title(f'Matrice de confusion — {model_name} (Exp. {exp_name})')
    plt.ylabel('Vérité terrain')
    plt.xlabel('Prédiction')
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'confusion_matrix_norm.png'), dpi=150)
    plt.close()


def plot_roc_curve(y_true, y_proba, model_name, exp_name, save_dir):
    """Courbe ROC avec AUC (pouvoir discriminant indépendant du seuil)."""
    if y_proba is None or len(y_proba) == 0 or len(np.unique(y_true)) < 2:
        return
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(6, 5))
    plt.plot(fpr, tpr, lw=2, label=f'AUC = {roc_auc:.3f}',
             color=COLORS.get(model_name, '#27AE60'))
    plt.plot([0, 1], [0, 1], 'k--', lw=1)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Taux de faux positifs (1 - Spécificité)')
    plt.ylabel('Taux de vrais positifs (Sensibilité)')
    plt.title(f'Courbe ROC — {model_name} (Exp. {exp_name})')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'roc_curve.png'), dpi=150)
    plt.close()


def plot_fold_metrics(per_fold_metrics, model_name, exp_name, save_dir):
    """Métriques par sujet (fold) — montre la variance inter-sujets."""
    if not per_fold_metrics:
        return
    folds = np.arange(1, len(per_fold_metrics) + 1)
    acc = [m['accuracy'] for m in per_fold_metrics]
    f1 = [m['f1'] for m in per_fold_metrics]
    prec = [m['precision'] for m in per_fold_metrics]
    rec = [m['recall'] for m in per_fold_metrics]

    plt.figure(figsize=(12, 5))
    plt.plot(folds, acc, 'o-', label='Accuracy', color='#3498DB', linewidth=2)
    plt.plot(folds, prec, 's-', label='Precision', color='#E67E22', linewidth=2)
    plt.plot(folds, rec, 'd-', label='Recall (Sensibilité)', color='#2ECC71', linewidth=2)
    plt.plot(folds, f1, '^-', label='F1-score', color='#E74C3C', linewidth=2)
    plt.xlabel('Sujet test (fold LOSO)')
    plt.ylabel('Score')
    plt.title(f'Métriques par sujet — {model_name} (Exp. {exp_name})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim([-0.05, 1.05])
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'fold_metrics.png'), dpi=150)
    plt.close()


def save_classification_report(y_true, y_pred, model_name, exp_name, save_dir):
    """Rapport de classification textuel (precision/recall/F1 par classe)."""
    if len(np.unique(y_true)) < 2:
        with open(os.path.join(save_dir, 'classification_report.txt'), 'w') as f:
            f.write("Une seule classe présente — rapport non calculable.\n")
        return
    report = classification_report(y_true, y_pred,
                                    target_names=['Concentration', 'Stress'])
    cm = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = cm.ravel()
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0

    with open(os.path.join(save_dir, 'classification_report.txt'), 'w') as f:
        f.write(f"Classification Report — {model_name} (Exp. {exp_name})\n")
        f.write("=" * 55 + "\n\n")
        f.write(report)
        f.write(f"\nSpécificité (TNR) : {specificity:.4f}\n")
        f.write(f"\nMatrice de confusion :\n")
        f.write(f"  VP={tp}  FP={fp}\n")
        f.write(f"  FN={fn}  VN={tn}\n")


def save_metrics_csv(per_fold_metrics, global_metrics, save_dir):
    """Sauvegarde les métriques par fold en CSV + métriques globales en TXT."""
    if not per_fold_metrics:
        return
    df = pd.DataFrame(per_fold_metrics)
    df.index.name = 'fold'
    df.to_csv(os.path.join(save_dir, 'metrics_per_fold.csv'))

    with open(os.path.join(save_dir, 'global_metrics.txt'), 'w') as f:
        for k, v in global_metrics.items():
            if isinstance(v, float):
                f.write(f"{k}: {v:.4f}\n")
            else:
                f.write(f"{k}: {v}\n")


# ============================================================================
# ÉVALUATION SUR VAL/TEST (NOUVEAU)
# ============================================================================

def evaluate_on_split(model, scaler, split_name, features_dir):
    """
    Évalue un modèle entraîné sur un split (val ou test) NON augmenté.

    NOUVEAU : cette fonction n'existait pas dans la version précédente.
    Les modèles finaux doivent être évalués sur des données jamais vues
    ET jamais augmentées pour mesurer la généralisation réelle.

    Paramètres :
    - model : modèle sklearn/xgboost déjà entraîné
    - scaler : StandardScaler déjà fit sur les données d'entraînement
    - split_name : 'val' ou 'test'
    - features_dir : chemin vers le dossier datasets_features/

    Retourne :
    - dict de métriques (ou None si les fichiers n'existent pas)
    """
    feat_path = features_dir / f'features_{split_name}.npy'
    label_path = features_dir / f'labels_{split_name}.npy'

    if not feat_path.exists() or not label_path.exists():
        return None

    X = np.load(feat_path)
    y = np.load(label_path)

    if len(X) == 0:
        return None

    X_scaled = scaler.transform(X)
    y_pred = model.predict(X_scaled)
    y_proba = None
    if hasattr(model, 'predict_proba'):
        y_proba = model.predict_proba(X_scaled)[:, 1]

    metrics = compute_metrics(y, y_pred, y_proba)
    metrics['n_samples'] = len(y)
    return metrics


# ============================================================================
# FONCTION PRINCIPALE
# ============================================================================

def main():
    print("=" * 70)
    print("NeuroCap – Baseline Machine Learning complet")
    print("Validation LOSO + Évaluation Val/Test + Sauvegarde modèles finaux")
    print("Canal Fp2 | Classification binaire : Concentration vs Stress")
    print("=" * 70)

    # Vérification du dossier de features
    if not FEATURES_DIR.exists():
        print(f"\n❌ ERREUR : le dossier '{FEATURES_DIR}' n'existe pas.")
        print("   → Exécutez d'abord extract_features_for_baseline.py")
        return

    # Création des dossiers de sortie
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_SAVE_ROOT.mkdir(parents=True, exist_ok=True)

    # ================================================================
    # ÉTAPE 1 : VALIDATION LOSO POUR CHAQUE (EXPÉRIENCE, CLASSIFIEUR)
    # ================================================================
    # Stockage de TOUS les résultats
    all_results = {}
    val_test_results = {}

    for exp in EXPERIMENTS:
        feat_file = FEATURES_DIR / f'features_{exp}.npy'
        label_file = FEATURES_DIR / f'labels_{exp}.npy'
        sid_file = FEATURES_DIR / f'subject_ids_{exp}.npy'

        if not all(f.exists() for f in [feat_file, label_file, sid_file]):
            print(f"\n⚠️  Exp. {exp} : fichiers manquants — ignorée")
            continue

        X = np.load(feat_file)
        y = np.load(label_file)
        subject_ids = np.load(sid_file)

        print(f"\n{'='*60}")
        print(f"EXPÉRIENCE {exp}")
        print(f"{'='*60}")
        print(f"  Données : {len(X)} échantillons × {X.shape[1]} features")
        print(f"  Labels : {np.sum(y==0)} concentration | {np.sum(y==1)} stress")
        print(f"  Sujets LOSO : {len(np.unique(subject_ids))} sujets uniques")

        all_results[exp] = {}

        for model_name, model in MODELS.items():
            print(f"\n  ▶ {model_name}")

            # --- 1a. Validation LOSO ---
            t_start = time.time()
            y_true, y_pred, y_proba, per_fold_metrics, global_metrics = \
                loso_cross_validation(X, y, subject_ids, model)
            t_loso = time.time() - t_start

            all_results[exp][model_name] = {
                'acc': global_metrics['accuracy'],
                'f1': global_metrics['f1'],
                'auc': global_metrics.get('auc', 0.0),
                'precision': global_metrics['precision'],
                'recall': global_metrics['recall'],
                'specificity': global_metrics['specificity'],
                'n_folds_valid': global_metrics.get('n_folds_valid', 0),
                'n_folds_total': global_metrics.get('n_folds_total', 0)
            }

            print(f"    LOSO : Acc={global_metrics['accuracy']:.4f} | "
                  f"F1={global_metrics['f1']:.4f} | "
                  f"AUC={global_metrics.get('auc', 0):.4f} | "
                  f"Folds valides={global_metrics.get('n_folds_valid', 0)}/"
                  f"{global_metrics.get('n_folds_total', 0)} | "
                  f"Temps={t_loso:.1f}s")

            # --- 1b. Visualisations par (exp, model) ---
            out_dir = OUTPUT_DIR / exp / model_name.replace(' ', '_')
            out_dir.mkdir(parents=True, exist_ok=True)

            if y_true and len(np.unique(y_true)) > 1:
                plot_confusion_matrix_normalized(y_true, y_pred, model_name, exp, str(out_dir))
                if y_proba:
                    plot_roc_curve(y_true, y_proba, model_name, exp, str(out_dir))
            plot_fold_metrics(per_fold_metrics, model_name, exp, str(out_dir))
            if y_true:
                save_classification_report(y_true, y_pred, model_name, exp, str(out_dir))
            save_metrics_csv(per_fold_metrics, global_metrics, str(out_dir))

            # --- 1c. Évaluation sur Val/Test (NOUVEAU) ---
            # On entraîne un modèle sur TOUTES les données de l'expérience
            # puis on évalue sur val et test NON augmentés
            scaler_full = StandardScaler()
            X_scaled_full = scaler_full.fit_transform(X)
            model_for_eval = model.__class__(**model.get_params())
            model_for_eval.fit(X_scaled_full, y)

            val_metrics = evaluate_on_split(model_for_eval, scaler_full, 'val', FEATURES_DIR)
            test_metrics = evaluate_on_split(model_for_eval, scaler_full, 'test', FEATURES_DIR)

            key = f"{exp}_{model_name}"
            val_test_results[key] = {
                'val': val_metrics,
                'test': test_metrics
            }

            if val_metrics:
                print(f"    VAL  : Acc={val_metrics['accuracy']:.4f} | "
                      f"F1={val_metrics['f1']:.4f}")
            if test_metrics:
                print(f"    TEST : Acc={test_metrics['accuracy']:.4f} | "
                      f"F1={test_metrics['f1']:.4f}")

    # ================================================================
    # ÉTAPE 2 : COMPARAISON GLOBALE (graphiques et rapport)
    # ================================================================
    print(f"\n{'='*60}")
    print("COMPARAISON GLOBALE DES PERFORMANCES")
    print(f"{'='*60}")

    if not all_results:
        print("  Aucun résultat disponible.")
        return

    # Tableau comparatif dans le terminal
    print(f"\n{'Exp':>5} | {'Modèle':>15} | {'Acc':>7} | {'F1':>7} | {'AUC':>7} | "
          f"{'Prec':>7} | {'Recall':>7} | {'Spéc.':>7}")
    print("-" * 80)

    best_f1 = -1
    best_config = None

    for exp in EXPERIMENTS:
        if exp not in all_results:
            continue
        for model_name in MODELS:
            if model_name not in all_results[exp]:
                continue
            m = all_results[exp][model_name]
            print(f"{exp:>5} | {model_name:>15} | {m['acc']:>7.4f} | {m['f1']:>7.4f} | "
                  f"{m['auc']:>7.4f} | {m['precision']:>7.4f} | {m['recall']:>7.4f} | "
                  f"{m['specificity']:>7.4f}")

            if m['f1'] > best_f1:
                best_f1 = m['f1']
                best_config = (exp, model_name)

    if best_config:
        print(f"\n★ Meilleure configuration : {best_config[1]} sur Exp. {best_config[0]} "
              f"(F1={best_f1:.4f})")

    # --- Graphiques comparatifs ---
    _plot_comparison(all_results, EXPERIMENTS, list(MODELS.keys()), OUTPUT_DIR)

    # ================================================================
    # ÉTAPE 3 : SAUVEGARDE DES MODÈLES FINAUX
    # ================================================================
    # CORRECTION : on choisit EXPLICITEMENT la meilleure expérience
    # Au lieu de sauvegarder le dernier modèle de la boucle (accident)

    print(f"\n{'='*60}")
    print("SAUVEGARDE DES MODÈLES FINAUX")
    print(f"{'='*60}")

    if best_config is None:
        print("  Aucun modèle à sauvegarder (pas de résultats).")
        return

    best_exp = best_config[0]
    print(f"\n  Expérience sélectionnée pour les modèles finaux : {best_exp}")
    print(f"  (Meilleur F1-score LOSO global)")

    # Charger les données de la meilleure expérience
    X_best = np.load(FEATURES_DIR / f'features_{best_exp}.npy')
    y_best = np.load(FEATURES_DIR / f'labels_{best_exp}.npy')

    for model_name, model in MODELS.items():
        print(f"\n  ▶ Entraînement final {model_name} sur Exp. {best_exp} "
              f"({len(X_best)} échantillons)...")

        # Scaler final (fit sur toutes les données de l'expérience)
        scaler_final = StandardScaler()
        X_scaled_final = scaler_final.fit_transform(X_best)

        # Modèle final
        final_model = model.__class__(**model.get_params())
        final_model.fit(X_scaled_final, y_best)

        # Sauvegarde
        safe_name = model_name.replace(' ', '_')

        if model_name in ['SVM', 'Random Forest']:
            model_path = MODEL_SAVE_ROOT / f"{safe_name}_concentration_vs_stress.joblib"
            scaler_path = MODEL_SAVE_ROOT / f"{safe_name}_scaler.joblib"
            joblib.dump(final_model, model_path)
            joblib.dump(scaler_final, scaler_path)
        elif model_name == 'XGBoost':
            model_path = MODEL_SAVE_ROOT / f"{safe_name}_concentration_vs_stress.json"
            scaler_path = MODEL_SAVE_ROOT / f"{safe_name}_scaler.joblib"
            final_model.save_model(str(model_path))
            joblib.dump(scaler_final, scaler_path)

        print(f"    ✅ Modèle : {model_path.name}")
        print(f"    ✅ Scaler : {scaler_path.name}")

        # Évaluation du modèle final sur val/test
        val_m = evaluate_on_split(final_model, scaler_final, 'val', FEATURES_DIR)
        test_m = evaluate_on_split(final_model, scaler_final, 'test', FEATURES_DIR)
        if val_m:
            print(f"    VAL  → Acc={val_m['accuracy']:.4f} F1={val_m['f1']:.4f}")
        if test_m:
            print(f"    TEST → Acc={test_m['accuracy']:.4f} F1={test_m['f1']:.4f}")

    # ================================================================
    # ÉTAPE 4 : RAPPORT FINAL COMPLET
    # ================================================================
    _save_final_report(all_results, val_test_results, best_config, OUTPUT_DIR)

    print(f"\n{'='*70}")
    print("✅ Pipeline baseline ML terminé.")
    print(f"   Résultats LOSO      : {OUTPUT_DIR}/")
    print(f"   Modèles finaux      : {MODEL_SAVE_ROOT}/")
    print(f"   Rapport complet     : {OUTPUT_DIR / 'report_all.txt'}")
    print(f"   Résultats JSON      : {OUTPUT_DIR / 'results.json'}")
    print(f"{'='*70}")


# ============================================================================
# FONCTIONS AUXILIAIRES
# ============================================================================

def _plot_comparison(all_results, experiments, model_names, output_dir):
    """Génère les graphiques comparatifs (accuracy/F1 + AUC)."""
    exps_with_data = [e for e in experiments if e in all_results]
    if not exps_with_data:
        return

    # Matrices de résultats
    acc_matrix = np.zeros((len(model_names), len(exps_with_data)))
    f1_matrix = np.zeros((len(model_names), len(exps_with_data)))
    auc_matrix = np.zeros((len(model_names), len(exps_with_data)))

    for i, model in enumerate(model_names):
        for j, exp in enumerate(exps_with_data):
            if model in all_results.get(exp, {}):
                acc_matrix[i, j] = all_results[exp][model].get('acc', 0)
                f1_matrix[i, j] = all_results[exp][model].get('f1', 0)
                auc_matrix[i, j] = all_results[exp][model].get('auc', 0)

    # Figure 1 : Accuracy + F1
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    x = np.arange(len(exps_with_data))
    width = 0.25

    for i, model in enumerate(model_names):
        axes[0].bar(x + i * width, acc_matrix[i, :], width,
                    label=model, color=COLORS.get(model, '#7F8C8D'))
        axes[1].bar(x + i * width, f1_matrix[i, :], width,
                    label=model, color=COLORS.get(model, '#7F8C8D'))

    for ax, metric_name in zip(axes, ['Accuracy', 'F1-score']):
        ax.set_xticks(x + width)
        ax.set_xticklabels(exps_with_data)
        ax.set_ylabel(metric_name)
        ax.set_title(f'Comparaison des {metric_name.lower()}s (LOSO)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim([0, 1.05])

    plt.suptitle('Performances des classifieurs par expérience d\'augmentation',
                 fontsize=14)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(str(output_dir / 'comparison_accuracy_f1.png'), dpi=150)
    plt.close()

    # Figure 2 : AUC
    if np.any(auc_matrix > 0):
        plt.figure(figsize=(10, 6))
        for i, model in enumerate(model_names):
            plt.plot(exps_with_data, auc_matrix[i, :], 'o-', linewidth=2,
                     label=model, color=COLORS.get(model, '#7F8C8D'))
        plt.xlabel('Expérience')
        plt.ylabel('AUC')
        plt.title('Comparaison des AUC par expérience (LOSO)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.ylim([0.4, 1.05])
        plt.tight_layout()
        plt.savefig(str(output_dir / 'comparison_auc.png'), dpi=150)
        plt.close()


def _save_final_report(all_results, val_test_results, best_config, output_dir):
    """Sauvegarde le rapport complet (TXT + JSON)."""

    # --- Rapport texte ---
    with open(str(output_dir / 'report_all.txt'), 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("NeuroCap — Baseline ML — Rapport complet\n")
        f.write("Canal Fp2 | Concentration vs Stress | Validation LOSO\n")
        f.write("=" * 70 + "\n\n")

        # Résultats LOSO par expérience
        for exp in EXPERIMENTS:
            if exp not in all_results:
                continue
            f.write(f"Expérience {exp} :\n")
            for model_name in MODELS:
                if model_name not in all_results[exp]:
                    continue
                m = all_results[exp][model_name]
                f.write(f"  {model_name:15s}: "
                        f"Acc={m['acc']:.4f} F1={m['f1']:.4f} "
                        f"AUC={m['auc']:.4f} Prec={m['precision']:.4f} "
                        f"Recall={m['recall']:.4f} Spéc={m['specificity']:.4f}\n")

                # Val/Test
                key = f"{exp}_{model_name}"
                if key in val_test_results:
                    vt = val_test_results[key]
                    if vt.get('val'):
                        f.write(f"  {'':15s}  VAL  → Acc={vt['val']['accuracy']:.4f} "
                                f"F1={vt['val']['f1']:.4f}\n")
                    if vt.get('test'):
                        f.write(f"  {'':15s}  TEST → Acc={vt['test']['accuracy']:.4f} "
                                f"F1={vt['test']['f1']:.4f}\n")
            f.write("\n")

        # Recommandation
        if best_config:
            f.write(f"\n{'='*50}\n")
            f.write(f"★ RECOMMANDATION\n")
            f.write(f"{'='*50}\n")
            f.write(f"Meilleur modèle : {best_config[1]} sur Exp. {best_config[0]}\n")
            f.write(f"F1-score LOSO : {all_results[best_config[0]][best_config[1]]['f1']:.4f}\n")
            f.write(f"\nModèles sauvegardés dans baseline_models/ "
                    f"(entraînés sur Exp. {best_config[0]})\n")

    # --- Résultats JSON (pour exploitation programmatique) --- 
    json_results = {
        'loso': {},
        'val_test': {},
        'best_config': {'exp': best_config[0], 'model': best_config[1]} if best_config else None
    }
    for exp in all_results:
        json_results['loso'][exp] = {}
        for model_name in all_results[exp]:
            json_results['loso'][exp][model_name] = all_results[exp][model_name]

    for key, vt in val_test_results.items():
        json_results['val_test'][key] = {
            'val': vt.get('val'),
            'test': vt.get('test')
        }

    with open(str(output_dir / 'results.json'), 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, default=str)


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================
if __name__ == "__main__":
    main()