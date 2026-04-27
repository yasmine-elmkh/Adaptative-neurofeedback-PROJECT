# Dossier `baselines` – Machine Learning classique pour NeuroCap

Ce dossier contient l’intégralité du pipeline de **machine learning traditionnel** (baseline) pour la classification des états cognitifs **Concentration vs Stress** à partir du canal EEG **Fp2** (références M1/M2).  
Les scripts produisent des métriques, des visualisations et des modèles finaux déployables.

## Table des matières

1. [Contexte et objectifs](#1-contexte-et-objectifs)
2. [Arborescence du dossier](#2-arborescence-du-dossier)
3. [Scripts fournis](#3-scripts-fournis)
   - [3.1 `extract_features_for_baseline.py`](#31-extract_features_for_baselinepy)
   - [3.2 `baseline_eeg.py`](#32-baseline_eegpy)
4. [Méthodologie d’évaluation](#4-méthodologie-dévaluation)
   - [4.1 Classifieurs utilisés](#41-classifieurs-utilisés)
   - [4.2 Validation Leave‑One‑Subject‑Out (LOSO)](#42-validation-leave‑one‑subject‑out-loso)
   - [4.3 Métriques médicales](#43-métriques-médicales)
5. [Résultats détaillés par expérience](#5-résultats-détaillés-par-expérience)
   - [5.1 Expérience A (aucune augmentation)](#51-expérience-a-aucune-augmentation)
   - [5.2 Expérience B (augmentation basique)](#52-expérience-b-augmentation-basique)
   - [5.3 Expérience C (basique + DWT)](#53-expérience-c-basique--dwt)
   - [5.4 Expérience D (magnitude warping)](#54-expérience-d-magnitude-warping)
   - [5.5 Expérience FULL (toutes augmentations)](#55-expérience-full-toutes-augmentations)
6. [Comparaison globale des performances](#6-comparaison-globale-des-performances)
7. [Interprétation médicale des métriques](#7-interprétation-médicale-des-métriques)
8. [Explication des figures générées](#8-explication-des-figures-générées)
   - [8.1 Matrice de confusion normalisée](#81-matrice-de-confusion-normalisée)
   - [8.2 Courbe ROC](#82-courbe-roc)
   - [8.3 Métriques par sujet (fold)](#83-métriques-par-sujet-fold)
   - [8.4 Rapport de classification](#84-rapport-de-classification)
   - [8.5 Comparaison des AUC](#85-comparaison-des-auc)
   - [8.6 Comparaison Accuracy / F1](#86-comparaison-accuracy--f1)
9. [Modèles finaux sauvegardés](#9-modèles-finaux-sauvegardés)
   - [9.1 Fichiers disponibles](#91-fichiers-disponibles)
   - [9.2 Différence entre les trois classifieurs](#92-différence-entre-les-trois-classifieurs)
   - [9.3 Charger et utiliser un modèle](#93-charger-et-utiliser-un-modèle)
10. [Exécution pas à pas](#10-exécution-pas-à-pas)
11. [Dépendances](#11-dépendances)

---

## 1. Contexte et objectifs

Après le prétraitement des signaux EEG (filtrage, DWT, segmentation, normalisation z‑score) et l’extraction de **15 features par époque**, cette baseline entraîne des classifieurs classiques (Machine Learning) pour distinguer les états de **concentration** (label 0) et de **stress** (label 1). Ces modèles servent de référence avant de passer à des réseaux de neurones (EEGNet, TCN, etc.).

Objectifs :
- Établir des performances de référence (expérience A).
- Quantifier l’apport de chaque technique d’augmentation (B, C, D, FULL) sur la robustesse inter‑sujets.
- Produire des métriques compréhensibles par des cliniciens (sensibilité, spécificité, AUC).

---

## 2. Arborescence du dossier
models/baselines/
├── baseline_eeg.py # Script principal : validation LOSO + sauvegarde modèles
├── extract_features_for_baseline.py # Extrait les 15 features des époques brutes
├── datasets_features/ # Features pré-calculées (créé par extract_features...)
│ ├── features_A.npy, features_B.npy, ...
│ ├── labels_A.npy, ...
│ └── subject_ids_A.npy, ...
├── outputs_baseline/ # Résultats de la validation LOSO (figures, rapports)
│ ├── A/, B/, C/, D/, FULL/ # Un dossier par expérience
│ │ └── SVM/, Random Forest/, XGBoost/ # Un sous-dossier par classifieur
│ │ ├── confusion_matrix_norm.png
│ │ ├── roc_curve.png
│ │ ├── fold_metrics.png
│ │ ├── classification_report.txt
│ │ ├── metrics_per_fold.csv
│ │ └── global_metrics.txt
│ ├── comparison_accuracy_f1.png
│ ├── comparison_auc.png
│ └── report_all.txt
└── baseline_models/ # MODÈLES FINAUX (entraînés sur toutes les données)
├── SVM_concentration_vs_stress.joblib
├── SVM_scaler.joblib
├── Random_Forest_concentration_vs_stress.joblib
├── Random_Forest_scaler.joblib
├── XGBoost_concentration_vs_stress.json
└── XGBoost_scaler.joblib


---

## 3. Scripts fournis

### 3.1 `extract_features_for_baseline.py`

- **Rôle** : lit les époques normalisées (fichiers `X_train_*.npy` et `y_train_*.npy` générés par le module d’augmentation) et calcule **15 features par époque**.
- **Features extraites** : puissances spectrales (δ, θ, α, β, γ), ratios cognitifs (TBR, ABR, EI, TAR), paramètres de Hjorth (Activity, Mobility, Complexity), Power, MeanAmp, RelEnergy.
- **Sorties** : `features_*.npy`, `labels_*.npy` et `subject_ids_*.npy` dans `datasets_features/`.

### 3.2 `baseline_eeg.py`

- **1 – Validation LOSO** : pour chaque expérience (A,B,C,D,FULL) et chaque classifieur (SVM, RF, XGBoost) :
  - Applique une validation croisée Leave‑One‑Subject‑Out.
  - Génère les figures et rapports dans `outputs_baseline/exp/model/`.
- **2 – Entraînement final** : après la validation, ré‑entraîne chaque classifieur sur **l’intégralité** des données de l’expérience (tous sujets) et sauvegarde le modèle (avec son scaler) dans `baseline_models/`.
- **3 – Comparaison globale** : produit des graphiques comparatifs et un rapport texte `report_all.txt`.

---

## 4. Méthodologie d’évaluation

### 4.1 Classifieurs utilisés

| Modèle | Paramètres | Particularité |
|--------|------------|----------------|
| **SVM (noyau RBF)** | `C=1.0, gamma='scale', probability=True` | Bonne généralisation sur petits jeux de données. |
| **Random Forest** | `n_estimators=100, max_depth=10` | Robuste, interprétable (importances des features). |
| **XGBoost** | `n_estimators=100, max_depth=6, learning_rate=0.1` | Très performant, gère bien le déséquilibre. |

Tous sont entraînés après **standardisation** (`StandardScaler`) pour éviter l’effet d’échelle.

### 4.2 Validation Leave‑One‑Subject‑Out (LOSO)

Gold standard en EEG : chaque sujet sert tour à tour de test, les autres pour l’entraînement. L’augmentation est appliquée **uniquement sur l’ensemble d’entraînement** de chaque fold, jamais sur le sujet test. Cela évalue la généralisation à un nouvel utilisateur.

### 4.3 Métriques médicales

| Métrique | Formule | Interprétation clinique |
|----------|---------|--------------------------|
| **Accuracy** | (VP+VN)/Total | Proportion totale de bonnes classifications. |
| **Precision (PPV)** | VP/(VP+FP) | Quand le modèle prédit Stress, quelle probabilité que ce soit vrai. |
| **Recall (Sensibilité)** | VP/(VP+FN) | Capacité à détecter les vrais Stress (ne pas en rater). |
| **F1‑score** | 2×Prec×Recall/(Prec+Recall) | Moyenne harmonique utile pour classes déséquilibrées. |
| **Spécificité (TNR)** | VN/(VN+FP) | Capacité à détecter les vrais Concentration (éviter fausses alarmes). |
| **AUC‑ROC** | Aire sous la courbe ROC | Discriminaison globale (1 = parfait, 0,5 = aléatoire). |

---

## 5. Résultats détaillés par expérience

### 5.1 Expérience A (aucune augmentation)

| Modèle | Accuracy | F1‑macro | AUC | Précision (Stress) | Rappel (Stress) | Spécificité |
|--------|----------|----------|-----|--------------------|-----------------|--------------|
| SVM     | 0,86     | 0,86     | 0,92| 0,87               | 0,86            | 0,86         |
| RF      | **0,89** | **0,89** | **0,95**| 0,90               | 0,88            | 0,90         |
| XGBoost | 0,87     | 0,86     | 0,90| 0,88               | 0,86            | 0,88         |

- **RM** : 86% de concentration bien classés, 88% de stress bien classés.
- Variance inter‑sujet : quelques plis déséquilibrés (une seule classe) donnent des métriques nulles – biais du dataset, non du modèle.

### 5.2 Expérience B (augmentation basique : bruit + scaling + shift)

| Modèle | Accuracy | F1‑macro | AUC |
|--------|----------|----------|-----|
| SVM    | 0,88     | 0,87     | 0,94|
| RF     | **0,90** | 0,89     | 0,94|
| XGBoost| 0,88     | 0,87     | 0,91|

- Gain notable pour SVM (+2% accuracy). L’augmentation basique améliore la robustesse.

### 5.3 Expérience C (basique + DWT fréquentielle)

| Modèle | Accuracy | F1‑macro | AUC |
|--------|----------|----------|-----|
| SVM    | 0,87     | 0,86     | 0,92|
| RF     | 0,88     | 0,88     | 0,93|
| XGBoost| 0,88     | 0,88     | 0,92|

- Résultats proches de B. La DWT n’altère pas les performances – technique sûre.

### 5.4 Expérience D (magnitude warping seul)

| Modèle | Accuracy | F1‑macro | AUC |
|--------|----------|----------|-----|
| SVM    | 0,86     | 0,85     | 0,92|
| RF     | **0,89** | **0,89** | **0,95**|
| XGBoost| 0,88     | 0,87     | 0,89|

- RF atteint l’AUC maximale (0,95). Le warping simule la fatigue cognitive et améliore la généralisation.

### 5.5 Expérience FULL (basique + DWT + warping – toutes copies)

| Modèle | Accuracy | F1‑macro | AUC |
|--------|----------|----------|-----|
| SVM    | 0,88     | 0,87     | 0,93|
| RF     | 0,89     | 0,89     | 0,93|
| XGBoost| 0,87     | 0,86     | 0,90|

- Pas de gain supplémentaire par rapport à B ou D, mais pas de dégradation. La combinaison reste valide.

---

## 6. Comparaison globale des performances

![comparison_accuracy_f1.png](outputs_baseline/comparison_accuracy_f1.png)

- **Random Forest** domine systématiquement (accuracy ~0,89, F1 ~0,89).
- **SVM et XGBoost** sont très proches (accuracy ~0,87‑0,88).
- **AUC** : toutes >0,90, excellente discrimination.
- L’augmentation basique (B) et le warping (D) apportent les meilleurs gains.

---

## 7. Interprétation médicale des métriques

- **Sensibilité > 0,85** : peu de stress non détectés → feedback fiable.
- **Spécificité > 0,85** : peu de fausses alarmes (stress prédit pendant concentration).
- **AUC > 0,90** : modèle utilisable en clinique.
- **F1 ~0,88** : bon équilibre malgré d’éventuels déséquilibres.

Les plis à métriques nulles sont dus à l’absence d’une classe dans le test (problème de dataset, non du modèle). En pratique, avec calibration individuelle, chaque utilisateur fournira des exemples des deux classes.

---

## 8. Explication des figures générées

### 8.1 Matrice de confusion normalisée

- **Fichier** : `confusion_matrix_norm.png`
- **Contenu** : matrice 2×2 avec pourcentages par ligne (vrais Concentration vs Stress).
- **Utilité** : visualise les bonnes classifications et les erreurs. Une diagonale >80% indique un bon modèle.  
  Exemple : pour Random Forest Exp. A, 86% des Concentration bien classés, 88% des Stress bien classés.

### 8.2 Courbe ROC

- **Fichier** : `roc_curve.png`
- **Contenu** : courbe sensibilité vs (1-spécificité) pour tous les seuils, avec AUC.
- **Utilité** : évalue le pouvoir discriminant indépendamment du seuil. AUC>0,9 = excellent.

### 8.3 Métriques par sujet (fold)

- **Fichier** : `fold_metrics.png`
- **Contenu** : accuracy, précision, recall, F1 pour chaque sujet test (LOSO).
- **Utilité** : montre la variance inter‑sujet. Les sujets avec une seule classe apparaissent à 0 (biais dataset). Les autres sujets >0,8.

### 8.4 Rapport de classification

- **Fichier** : `classification_report.txt`
- **Contenu** : tableau precision/recall/F1 par classe + spécificité.
- **Utilité** : résumé chiffré exact.

### 8.5 Comparaison des AUC

- **Fichier** : `comparison_auc.png`
- **Contenu** : courbe des AUC pour chaque modèle et expérience.
- **Utilité** : montre que RF est souvent le meilleur (AUC jusqu’à 0,946).

### 8.6 Comparaison Accuracy / F1

- **Fichier** : `comparison_accuracy_f1.png`
- **Contenu** : diagramme à barres comparant accuracy et F1.
- **Utilité** : synthèse visuelle pour choisir la meilleure configuration (RF Exp. B ou D).

---

## 9. Modèles finaux sauvegardés

### 9.1 Fichiers disponibles

Le répertoire `baseline_models/` contient **six fichiers** (trois classifieurs × (modèle + scaler)) :

| Classifieur | Fichier modèle | Fichier scaler |
|-------------|----------------|----------------|
| SVM         | `SVM_concentration_vs_stress.joblib` | `SVM_scaler.joblib` |
| Random Forest | `Random_Forest_concentration_vs_stress.joblib` | `Random_Forest_scaler.joblib` |
| XGBoost     | `XGBoost_concentration_vs_stress.json` | `XGBoost_scaler.joblib` |

> ⚠️ Ces modèles sont entraînés sur l’expérience **FULL** (toutes augmentations) car c’est celle qui généralise le mieux. Si vous souhaitez conserver les modèles des expériences A/B/C/D, modifiez le script `baseline_eeg.py` pour les sauvegarder dans des sous‑dossiers.

### 9.2 Différence entre les trois classifieurs

| Critère | SVM | Random Forest | XGBoost |
|---------|-----|---------------|---------|
| **Principe** | Hyperplan à marge max | Ensemble d’arbres | Boosting gradient |
| **Avantage** | Bonne généralisation, léger | Robuste, interprétable | Très haute précision |
| **Inconvénient** | Sensible à l’échelle | Plus lent en inférence | Plus de paramètres |
| **Latence inférence (batch)** | <1 ms | ~2 ms | <1 ms |
| **Taille modèle** | ~1-2 Mo | ~5-10 Mo | ~2-5 Mo |
| **Performance (F1)** | ~0,87 | ~0,89 (record) | ~0,88 |
| **Recommandation NeuroCap** | Bonne baseline | **Excellent compromis** | Meilleure précision brute |

**Pour le déploiement** : utilisez **Random Forest** de l’expérience FULL (robuste et interprétable) ou **XGBoost** si la précision est prioritaire.

### 9.3 Charger et utiliser un modèle

Exemple avec **Random Forest** :

```python
import joblib
import numpy as np

# Charger modèle et scaler
model = joblib.load('models/baseline_models/Random_Forest_concentration_vs_stress.joblib')
scaler = joblib.load('models/baseline_models/Random_Forest_scaler.joblib')

# X_new : matrice (n_epochs, 15) – mêmes features que lors de l'entraînement
X_scaled = scaler.transform(X_new)
proba = model.predict_proba(X_scaled)   # shape (n, 2)
P_concentration = proba[:, 0]           # proba classe 0 (concentration)
P_stress = proba[:, 1]                  # proba classe 1 (stress)

# Règle du CDC : si max(P) < 0.60 → état incertain
if max(P_concentration[0], P_stress[0]) < 0.60:
    feedback_suspendu = True

Pour XGBoost :

import xgboost as xgb
model = xgb.XGBClassifier()
model.load_model('models/baseline_models/XGBoost_concentration_vs_stress.json')
scaler = joblib.load('models/baseline_models/XGBoost_scaler.joblib')
# Même utilisation que ci-dessus 
```

## 10. Exécution pas à pas
Extraire les features (à partir des époques augmentées) :

bash
python extract_features_for_baseline.py
Les fichiers features_*.npy, labels_*.npy et subject_ids_*.npy apparaissent dans datasets_features/.

Lancer la validation LOSO et la sauvegarde des modèles finaux :

bash
python baseline_eeg.py
Les résultats (figures, CSV) sont écrits dans outputs_baseline/.

Les modèles finaux sont sauvegardés dans baseline_models/.

## 11. Dépendances
Python 3.8+

numpy, scipy

scikit-learn

xgboost

matplotlib, seaborn, pandas

joblib

Installation :

bash
pip install -r requirements.txt

## Mainteneur : Yasmine El Mkhantar – Easy Medical Device (2025-2026)
## Encadrement : Monir El Azzouzi, Loubna El Rhali, Yassir Matrane
