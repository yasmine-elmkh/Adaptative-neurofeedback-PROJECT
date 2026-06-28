# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `A`  |  **Date :** 2026-06-20 02:25


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4858 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9070 | Erreur quadratique moyenne |
| R² | 0.1558 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6860 | 0.500 |
| PR-AUC | 0.7214 | 0.604 |
| Sensitivity (TPR) | 0.9771 | 0.500 |
| Specificity (TNR) | 0.3721 | 0.500 |
| PPV (Precision) | 0.7033 | — |
| NPV | 0.9143 | — |
| Balanced Accuracy | 0.6746 | 0.500 |
| MCC | 0.4644 | 0.000 |
| G-Mean | 0.6030 | 0.500 |
| F1 macro | 0.6734 | 0.500 |
| LR+ | 1.556 | >10 = très utile |
| LR− | 0.062 | <0.1 = très utile |
| Cohen κ | 0.3888 | 0.000 |
| Brier Score | 0.2260 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6465 | [0.5726, 0.7155]  ✅ |
| F1 macro | 0.5892 | [0.5194, 0.6493]  ✅ |
| Sensitivity | 0.5244 | [0.4327, 0.6232]  — |
| Specificity | 0.6635 | [0.5656, 0.7477]  — |
| MCC | 0.1894 | [0.0526, 0.3053]  — |
| R² | 0.1519 | [0.0656, 0.2366]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1558 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6860 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1745 | < 0.05 |
| MCE | 0.4606 | < 0.10 |
| Brier Score | 0.2635 | < 0.20 |
| Log-Loss | 0.7392 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1207 | proche 0 = pas de biais systématique |
| LoA lower | -5.8267 | limite inférieure d'accord |
| LoA upper | +5.5853 | limite supérieure d'accord |
| LoA width | ±5.7060 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1799 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1558 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6860 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4858 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:25*
