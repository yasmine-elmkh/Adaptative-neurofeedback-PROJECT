# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `D`  |  **Date :** 2026-06-20 02:45


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3711 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7900 | Erreur quadratique moyenne |
| R² | 0.2224 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6951 | 0.500 |
| PR-AUC | 0.6769 | 0.530 |
| Sensitivity (TPR) | 0.8522 | 0.500 |
| Specificity (TNR) | 0.4902 | 0.500 |
| PPV (Precision) | 0.6533 | — |
| NPV | 0.7463 | — |
| Balanced Accuracy | 0.6712 | 0.500 |
| MCC | 0.3699 | 0.000 |
| G-Mean | 0.6463 | 0.500 |
| F1 macro | 0.6657 | 0.500 |
| LR+ | 1.672 | >10 = très utile |
| LR− | 0.302 | <0.1 = très utile |
| Cohen κ | 0.3491 | 0.000 |
| Brier Score | 0.2332 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6973 | [0.6225, 0.7619]  ✅ |
| F1 macro | 0.6198 | [0.5520, 0.6862]  ✅ |
| Sensitivity | 0.6667 | [0.5757, 0.7512]  — |
| Specificity | 0.5751 | [0.4785, 0.6763]  — |
| MCC | 0.2429 | [0.1081, 0.3795]  — |
| R² | 0.2180 | [0.1210, 0.3128]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2224 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6951 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1393 | < 0.05 |
| MCE | 0.3418 | < 0.10 |
| Brier Score | 0.2334 | < 0.20 |
| Log-Loss | 0.6797 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1803 | proche 0 = pas de biais systématique |
| LoA lower | -5.2893 | limite inférieure d'accord |
| LoA upper | +5.6498 | limite supérieure d'accord |
| LoA width | ±5.4696 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2209 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2224 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6951 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3711 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:45*
