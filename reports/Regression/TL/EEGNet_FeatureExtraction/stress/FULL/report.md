# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `FULL`  |  **Date :** 2026-06-20 02:39


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4612 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8784 | Erreur quadratique moyenne |
| R² | -0.0565 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5784 | 0.500 |
| PR-AUC | 0.5078 | 0.458 |
| Sensitivity (TPR) | 0.8283 | 0.500 |
| Specificity (TNR) | 0.3547 | 0.500 |
| PPV (Precision) | 0.5206 | — |
| NPV | 0.7094 | — |
| Balanced Accuracy | 0.5915 | 0.500 |
| MCC | 0.2052 | 0.000 |
| G-Mean | 0.5420 | 0.500 |
| F1 macro | 0.5562 | 0.500 |
| LR+ | 1.284 | >10 = très utile |
| LR− | 0.484 | <0.1 = très utile |
| Cohen κ | 0.1750 | 0.000 |
| Brier Score | 0.2943 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5850 | [0.5284, 0.6481]  ✅ |
| F1 macro | 0.5521 | [0.5057, 0.6030]  ✅ |
| Sensitivity | 0.5700 | [0.4952, 0.6443]  — |
| Specificity | 0.5580 | [0.4962, 0.6225]  — |
| MCC | 0.1233 | [0.0292, 0.2207]  — |
| R² | -0.0626 | [-0.1535, 0.0185]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0565 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5784 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1764 | < 0.05 |
| MCE | 0.4879 | < 0.10 |
| Brier Score | 0.2695 | < 0.20 |
| Log-Loss | 0.7534 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8223 | proche 0 = pas de biais systématique |
| LoA lower | -4.5906 | limite inférieure d'accord |
| LoA upper | +6.2352 | limite supérieure d'accord |
| LoA width | ±5.4129 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0056 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0565 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5784 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4612 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:39*
