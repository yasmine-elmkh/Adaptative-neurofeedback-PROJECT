# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `FULL`  |  **Date :** 2026-06-20 02:29


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3661 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8594 | Erreur quadratique moyenne |
| R² | 0.1832 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6698 | 0.500 |
| PR-AUC | 0.6740 | 0.567 |
| Sensitivity (TPR) | 0.9593 | 0.500 |
| Specificity (TNR) | 0.3830 | 0.500 |
| PPV (Precision) | 0.6705 | — |
| NPV | 0.8780 | — |
| Balanced Accuracy | 0.6712 | 0.500 |
| MCC | 0.4333 | 0.000 |
| G-Mean | 0.6061 | 0.500 |
| F1 macro | 0.6613 | 0.500 |
| LR+ | 1.555 | >10 = très utile |
| LR− | 0.106 | <0.1 = très utile |
| Cohen κ | 0.3667 | 0.000 |
| Brier Score | 0.2504 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6642 | [0.5844, 0.7322]  ✅ |
| F1 macro | 0.6081 | [0.5471, 0.6705]  ✅ |
| Sensitivity | 0.6851 | [0.5920, 0.7685]  — |
| Specificity | 0.5351 | [0.4433, 0.6368]  — |
| MCC | 0.2229 | [0.1010, 0.3439]  — |
| R² | 0.1776 | [0.0635, 0.2833]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1832 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6698 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1902 | < 0.05 |
| MCE | 0.4992 | < 0.10 |
| Brier Score | 0.2588 | < 0.20 |
| Log-Loss | 0.7645 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2291 | proche 0 = pas de biais systématique |
| LoA lower | -5.3703 | limite inférieure d'accord |
| LoA upper | +5.8284 | limite supérieure d'accord |
| LoA width | ±5.5994 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2075 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1832 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6698 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3661 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:29*
