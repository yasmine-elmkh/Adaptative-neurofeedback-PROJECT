# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:27


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6813 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0868 | Erreur quadratique moyenne |
| R² | 0.0068 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5860 | 0.500 |
| PR-AUC | 0.5783 | 0.517 |
| Sensitivity (TPR) | 0.6399 | 0.500 |
| Specificity (TNR) | 0.4978 | 0.500 |
| PPV (Precision) | 0.5772 | — |
| NPV | 0.5634 | — |
| Balanced Accuracy | 0.5689 | 0.500 |
| MCC | 0.1392 | 0.000 |
| G-Mean | 0.5644 | 0.500 |
| F1 macro | 0.5678 | 0.500 |
| LR+ | 1.274 | >10 = très utile |
| LR− | 0.723 | <0.1 = très utile |
| Cohen κ | 0.1383 | 0.000 |
| Brier Score | 0.2937 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5858 | [0.5665, 0.6067]  ✅ |
| F1 macro | 0.5289 | [0.5122, 0.5471]  ✅ |
| Sensitivity | 0.3480 | [0.3237, 0.3746]  — |
| Specificity | 0.7552 | [0.7335, 0.7771]  — |
| MCC | 0.1128 | [0.0790, 0.1457]  — |
| R² | 0.0070 | [-0.0203, 0.0319]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0068 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5855 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2368 | < 0.05 |
| MCE | 0.4037 | < 0.10 |
| Brier Score | 0.3120 | < 0.20 |
| Log-Loss | 0.9516 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0019 | proche 0 = pas de biais systématique |
| LoA lower | -6.0530 | limite inférieure d'accord |
| LoA upper | +6.0492 | limite supérieure d'accord |
| LoA width | ±6.0511 | < ±2 pts : excellent |
| % dans LoA | 98.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0949 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0492 | 0.1679 | 341.1% | 🔴 unstable |
| AUC ROC | 0.5806 | 0.0930 | 16.0% | 🟡 moderate |
| MAE | 2.6895 | 0.1927 | 7.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5855 |
| CI 95% | [0.5646, 0.6063] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:27*
