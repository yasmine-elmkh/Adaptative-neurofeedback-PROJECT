# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `D`  |  **Date :** 2026-06-20 02:58


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4712 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8652 | Erreur quadratique moyenne |
| R² | -0.0468 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5588 | 0.500 |
| PR-AUC | 0.3934 | 0.319 |
| Sensitivity (TPR) | 0.2391 | 0.500 |
| Specificity (TNR) | 0.8844 | 0.500 |
| PPV (Precision) | 0.4925 | — |
| NPV | 0.7123 | — |
| Balanced Accuracy | 0.5617 | 0.500 |
| MCC | 0.1591 | 0.000 |
| G-Mean | 0.4599 | 0.500 |
| F1 macro | 0.5555 | 0.500 |
| LR+ | 2.068 | >10 = très utile |
| LR− | 0.860 | <0.1 = très utile |
| Cohen κ | 0.1430 | 0.000 |
| Brier Score | 0.2303 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5549 | [0.5034, 0.6079]  ✅ |
| F1 macro | 0.4980 | [0.4536, 0.5435]  — |
| Sensitivity | 0.5369 | [0.4660, 0.6093]  — |
| Specificity | 0.4868 | [0.4314, 0.5453]  — |
| MCC | 0.0228 | [-0.0616, 0.1116]  — |
| R² | -0.0522 | [-0.1253, 0.0117]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0468 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5588 | p=0.0180 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1947 | < 0.05 |
| MCE | 0.5815 | < 0.10 |
| Brier Score | 0.2695 | < 0.20 |
| Log-Loss | 0.7395 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8121 | proche 0 = pas de biais systématique |
| LoA lower | -4.5796 | limite inférieure d'accord |
| LoA upper | +6.2039 | limite supérieure d'accord |
| LoA width | ±5.3917 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0046 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0468 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5588 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4712 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:58*
