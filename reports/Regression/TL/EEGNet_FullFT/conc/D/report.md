# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `D`  |  **Date :** 2026-06-20 02:31


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3558 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8460 | Erreur quadratique moyenne |
| R² | 0.1908 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6802 | 0.500 |
| PR-AUC | 0.6455 | 0.521 |
| Sensitivity (TPR) | 0.6726 | 0.500 |
| Specificity (TNR) | 0.6635 | 0.500 |
| PPV (Precision) | 0.6847 | — |
| NPV | 0.6509 | — |
| Balanced Accuracy | 0.6680 | 0.500 |
| MCC | 0.3358 | 0.000 |
| G-Mean | 0.6680 | 0.500 |
| F1 macro | 0.6679 | 0.500 |
| LR+ | 1.998 | >10 = très utile |
| LR− | 0.494 | <0.1 = très utile |
| Cohen κ | 0.3358 | 0.000 |
| Brier Score | 0.2548 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6799 | [0.6036, 0.7511]  ✅ |
| F1 macro | 0.6474 | [0.5833, 0.7087]  ✅ |
| Sensitivity | 0.6932 | [0.6061, 0.7768]  — |
| Specificity | 0.6036 | [0.5146, 0.6990]  — |
| MCC | 0.2982 | [0.1702, 0.4187]  — |
| R² | 0.1851 | [0.0746, 0.2867]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1908 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6802 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1615 | < 0.05 |
| MCE | 0.5225 | < 0.10 |
| Brier Score | 0.2531 | < 0.20 |
| Log-Loss | 0.7516 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1800 | proche 0 = pas de biais systématique |
| LoA lower | -5.3999 | limite inférieure d'accord |
| LoA upper | +5.7598 | limite supérieure d'accord |
| LoA width | ±5.5799 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2292 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1908 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6802 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3558 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:31*
