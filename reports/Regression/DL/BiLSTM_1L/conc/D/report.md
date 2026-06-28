# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_1L`  |  **Exp :** `D`  |  **Date :** 2026-06-13 20:24


> 🟠 **Deployment Readiness Score : 57.9/100 — PROTOTYPE — R&D / validation uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3486 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1108 | Erreur quadratique moyenne |
| R² | 0.0332 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7002 | 0.500 |
| PR-AUC | 0.6729 | 0.521 |
| Sensitivity (TPR) | 0.5575 | 0.500 |
| Specificity (TNR) | 0.7308 | 0.500 |
| PPV (Precision) | 0.6923 | — |
| NPV | 0.6032 | — |
| Balanced Accuracy | 0.6441 | 0.500 |
| MCC | 0.2919 | 0.000 |
| G-Mean | 0.6383 | 0.500 |
| F1 macro | 0.6393 | 0.500 |
| LR+ | 2.071 | >10 = très utile |
| LR− | 0.605 | <0.1 = très utile |
| Cohen κ | 0.2859 | 0.000 |
| Brier Score | 0.2823 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6991 | [0.6198, 0.7766]  ✅ |
| F1 macro | 0.6373 | [0.5712, 0.7025]  ✅ |
| Sensitivity | 0.5577 | [0.4593, 0.6478]  — |
| Specificity | 0.7285 | [0.6303, 0.8141]  — |
| MCC | 0.2897 | [0.1537, 0.4168]  — |
| R² | 0.0259 | [-0.1914, 0.2077]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0332 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7002 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2301 | < 0.05 |
| MCE | 0.4571 | < 0.10 |
| Brier Score | 0.2823 | < 0.20 |
| Log-Loss | 1.0846 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.6923 | proche 0 = pas de biais systématique |
| LoA lower | -6.6503 | limite inférieure d'accord |
| LoA upper | +5.2658 | limite supérieure d'accord |
| LoA width | ±5.9581 | < ±2 pts : excellent |
| % dans LoA | 94.0% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0813 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0332 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7002 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3486 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 28.8 | 10% |

### **SCORE TOTAL : 57.9/100**

### **VERDICT : PROTOTYPE — R&D / validation uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 20:24*
