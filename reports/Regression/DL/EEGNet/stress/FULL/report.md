# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet`  |  **Exp :** `FULL`  |  **Date :** 2026-06-20 02:06


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4880 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1497 | Erreur quadratique moyenne |
| R² | -0.2650 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6022 | 0.500 |
| PR-AUC | 0.7094 | 0.667 |
| Sensitivity (TPR) | 0.7778 | 0.500 |
| Specificity (TNR) | 0.4167 | 0.500 |
| PPV (Precision) | 0.7273 | — |
| NPV | 0.4839 | — |
| Balanced Accuracy | 0.5972 | 0.500 |
| MCC | 0.2026 | 0.000 |
| G-Mean | 0.5693 | 0.500 |
| F1 macro | 0.5997 | 0.500 |
| LR+ | 1.333 | >10 = très utile |
| LR− | 0.533 | <0.1 = très utile |
| Cohen κ | 0.2014 | 0.000 |
| Brier Score | 0.2294 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5411 | [0.4880, 0.6013]  — |
| F1 macro | 0.3885 | [0.3703, 0.4050]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | -0.2644 | [-0.3639, -0.1712]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2650 | p=0.0040 | ✅ p<0.05 |
| AUC ROC | 0.5405 | p=0.0960 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3276 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3378 | < 0.20 |
| Log-Loss | 1.2803 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.4714 | proche 0 = pas de biais systématique |
| LoA lower | -6.9361 | limite inférieure d'accord |
| LoA upper | +3.9933 | limite supérieure d'accord |
| LoA width | ±5.4647 | < ±2 pts : excellent |
| % dans LoA | 96.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0009 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.2650 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6022 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4880 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:06*
