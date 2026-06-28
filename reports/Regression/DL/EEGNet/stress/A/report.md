# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet`  |  **Exp :** `A`  |  **Date :** 2026-06-20 01:58


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3893 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8808 | Erreur quadratique moyenne |
| R² | -0.0583 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5804 | 0.500 |
| PR-AUC | 0.5758 | 0.528 |
| Sensitivity (TPR) | 0.5175 | 0.500 |
| Specificity (TNR) | 0.6471 | 0.500 |
| PPV (Precision) | 0.6211 | — |
| NPV | 0.5455 | — |
| Balanced Accuracy | 0.5823 | 0.500 |
| MCC | 0.1656 | 0.000 |
| G-Mean | 0.5787 | 0.500 |
| F1 macro | 0.5783 | 0.500 |
| LR+ | 1.466 | >10 = très utile |
| LR− | 0.746 | <0.1 = très utile |
| Cohen κ | 0.1630 | 0.000 |
| Brier Score | 0.2632 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5717 | [0.5109, 0.6243]  ✅ |
| F1 macro | 0.3885 | [0.3703, 0.4050]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | -0.0593 | [-0.1213, -0.0040]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0583 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5736 | p=0.0040 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2690 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3038 | < 0.20 |
| Log-Loss | 0.9723 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.8121 | proche 0 = pas de biais systématique |
| LoA lower | -6.2359 | limite inférieure d'accord |
| LoA upper | +4.6116 | limite supérieure d'accord |
| LoA width | ±5.4237 | < ±2 pts : excellent |
| % dans LoA | 96.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0034 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0583 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5804 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3893 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 01:58*
