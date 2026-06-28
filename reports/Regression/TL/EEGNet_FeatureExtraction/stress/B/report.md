# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `B`  |  **Date :** 2026-06-20 02:32


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4791 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8993 | Erreur quadratique moyenne |
| R² | -0.0718 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5993 | 0.500 |
| PR-AUC | 0.4942 | 0.428 |
| Sensitivity (TPR) | 0.7189 | 0.500 |
| Specificity (TNR) | 0.4615 | 0.500 |
| PPV (Precision) | 0.5000 | — |
| NPV | 0.6867 | — |
| Balanced Accuracy | 0.5902 | 0.500 |
| MCC | 0.1836 | 0.000 |
| G-Mean | 0.5760 | 0.500 |
| F1 macro | 0.5709 | 0.500 |
| LR+ | 1.335 | >10 = très utile |
| LR− | 0.609 | <0.1 = très utile |
| Cohen κ | 0.1711 | 0.000 |
| Brier Score | 0.2787 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5967 | [0.5468, 0.6559]  ✅ |
| F1 macro | 0.5503 | [0.5058, 0.6014]  ✅ |
| Sensitivity | 0.6319 | [0.5562, 0.7061]  — |
| Specificity | 0.5106 | [0.4562, 0.5720]  — |
| MCC | 0.1377 | [0.0535, 0.2338]  — |
| R² | -0.0787 | [-0.1804, 0.0054]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0718 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5993 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1909 | < 0.05 |
| MCE | 0.4622 | < 0.10 |
| Brier Score | 0.2762 | < 0.20 |
| Log-Loss | 0.7810 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9420 | proche 0 = pas de biais systématique |
| LoA lower | -4.4385 | limite inférieure d'accord |
| LoA upper | +6.3225 | limite supérieure d'accord |
| LoA width | ±5.3805 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0050 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0718 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5993 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4791 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:32*
