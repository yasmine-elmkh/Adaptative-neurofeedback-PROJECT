# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_Att`  |  **Exp :** `D`  |  **Date :** 2026-06-14 10:35


> 🟡 **Deployment Readiness Score : 65.3/100 — CONDITIONAL — Aide à la décision uniquement**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2809 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9292 | Erreur quadratique moyenne |
| R² | 0.1428 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7008 | 0.500 |
| PR-AUC | 0.6855 | 0.521 |
| Sensitivity (TPR) | 0.6549 | 0.500 |
| Specificity (TNR) | 0.6346 | 0.500 |
| PPV (Precision) | 0.6607 | — |
| NPV | 0.6286 | — |
| Balanced Accuracy | 0.6447 | 0.500 |
| MCC | 0.2894 | 0.000 |
| G-Mean | 0.6447 | 0.500 |
| F1 macro | 0.6447 | 0.500 |
| LR+ | 1.792 | >10 = très utile |
| LR− | 0.544 | <0.1 = très utile |
| Cohen κ | 0.2894 | 0.000 |
| Brier Score | 0.2554 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7003 | [0.6240, 0.7643]  ✅ |
| F1 macro | 0.6436 | [0.5779, 0.7040]  ✅ |
| Sensitivity | 0.6567 | [0.5541, 0.7406]  — |
| Specificity | 0.6331 | [0.5374, 0.7277]  — |
| MCC | 0.2897 | [0.1581, 0.4086]  — |
| R² | 0.1377 | [-0.0187, 0.2750]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1428 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7008 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1369 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2554 | < 0.20 |
| Log-Loss | 0.8967 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.5445 | proche 0 = pas de biais systématique |
| LoA lower | -6.1987 | limite inférieure d'accord |
| LoA upper | +5.1097 | limite supérieure d'accord |
| LoA width | ±5.6542 | < ±2 pts : excellent |
| % dans LoA | 93.1% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1068 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1428 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7008 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.2809 | 0.0000 | 0.0% | 🟢 stable |

**Stability Score global : 100.0/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 100.0 | 25% |
| Significativité (p-value) | 100.0 | 15% |
| Stabilité (CV) | 100.0 | 15% |
| Calibration (ECE) | 42.1 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 39.8 | 10% |

### **SCORE TOTAL : 65.3/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 10:35*
