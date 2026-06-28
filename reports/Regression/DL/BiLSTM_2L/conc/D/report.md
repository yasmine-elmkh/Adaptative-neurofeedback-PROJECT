# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiLSTM_2L`  |  **Exp :** `D`  |  **Date :** 2026-06-13 21:27


> 🟡 **Deployment Readiness Score : 60.1/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2071 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8692 | Erreur quadratique moyenne |
| R² | 0.1776 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7494 | 0.500 |
| PR-AUC | 0.7201 | 0.521 |
| Sensitivity (TPR) | 0.6637 | 0.500 |
| Specificity (TNR) | 0.6923 | 0.500 |
| PPV (Precision) | 0.7009 | — |
| NPV | 0.6545 | — |
| Balanced Accuracy | 0.6780 | 0.500 |
| MCC | 0.3558 | 0.000 |
| G-Mean | 0.6779 | 0.500 |
| F1 macro | 0.6774 | 0.500 |
| LR+ | 2.157 | >10 = très utile |
| LR− | 0.486 | <0.1 = très utile |
| Cohen κ | 0.3552 | 0.000 |
| Brier Score | 0.2396 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7505 | [0.6844, 0.8174]  ✅ |
| F1 macro | 0.6766 | [0.6151, 0.7391]  ✅ |
| Sensitivity | 0.6616 | [0.5757, 0.7453]  — |
| Specificity | 0.6949 | [0.5981, 0.7850]  — |
| MCC | 0.3564 | [0.2343, 0.4826]  — |
| R² | 0.1740 | [0.0247, 0.3174]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1776 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7494 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1941 | < 0.05 |
| MCE | 0.5948 | < 0.10 |
| Brier Score | 0.2396 | < 0.20 |
| Log-Loss | 0.8192 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4008 | proche 0 = pas de biais systématique |
| LoA lower | -5.9823 | limite inférieure d'accord |
| LoA upper | +5.1806 | limite supérieure d'accord |
| LoA width | ±5.5814 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1873 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1776 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7494 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2071 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 3.9 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 44.7 | 10% |

### **SCORE TOTAL : 60.1/100**

### **VERDICT : CONDITIONAL — Aide à la décision uniquement**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 21:27*
