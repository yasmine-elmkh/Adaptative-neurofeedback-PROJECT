# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `C`  |  **Date :** 2026-06-20 02:43


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4626 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8900 | Erreur quadratique moyenne |
| R² | -0.0650 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5948 | 0.500 |
| PR-AUC | 0.4930 | 0.417 |
| Sensitivity (TPR) | 0.6722 | 0.500 |
| Specificity (TNR) | 0.5159 | 0.500 |
| PPV (Precision) | 0.4979 | — |
| NPV | 0.6878 | — |
| Balanced Accuracy | 0.5940 | 0.500 |
| MCC | 0.1869 | 0.000 |
| G-Mean | 0.5889 | 0.500 |
| F1 macro | 0.5808 | 0.500 |
| LR+ | 1.389 | >10 = très utile |
| LR− | 0.635 | <0.1 = très utile |
| Cohen κ | 0.1791 | 0.000 |
| Brier Score | 0.2743 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5909 | [0.5358, 0.6527]  ✅ |
| F1 macro | 0.5657 | [0.5160, 0.6154]  ✅ |
| Sensitivity | 0.6007 | [0.5290, 0.6749]  — |
| Specificity | 0.5593 | [0.4928, 0.6223]  — |
| MCC | 0.1540 | [0.0594, 0.2569]  — |
| R² | -0.0714 | [-0.1668, 0.0092]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0650 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5948 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1811 | < 0.05 |
| MCE | 0.3917 | < 0.10 |
| Brier Score | 0.2713 | < 0.20 |
| Log-Loss | 0.7629 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8692 | proche 0 = pas de biais systématique |
| LoA lower | -4.5392 | limite inférieure d'accord |
| LoA upper | +6.2776 | limite supérieure d'accord |
| LoA width | ±5.4084 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0052 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0650 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5948 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4626 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:43*
