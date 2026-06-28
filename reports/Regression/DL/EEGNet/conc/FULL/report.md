# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet`  |  **Exp :** `FULL`  |  **Date :** 2026-06-20 01:54


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4609 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0487 | Erreur quadratique moyenne |
| R² | 0.0715 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7512 | 0.500 |
| PR-AUC | 0.8451 | 0.719 |
| Sensitivity (TPR) | 0.9936 | 0.500 |
| Specificity (TNR) | 0.5574 | 0.500 |
| PPV (Precision) | 0.8516 | — |
| NPV | 0.9714 | — |
| Balanced Accuracy | 0.7755 | 0.500 |
| MCC | 0.6734 | 0.000 |
| G-Mean | 0.7442 | 0.500 |
| F1 macro | 0.8127 | 0.500 |
| LR+ | 2.245 | >10 = très utile |
| LR− | 0.012 | <0.1 = très utile |
| Cohen κ | 0.6331 | 0.000 |
| Brier Score | 0.1302 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6413 | [0.5653, 0.7122]  ✅ |
| F1 macro | 0.4452 | [0.3874, 0.5083]  — |
| Sensitivity | 0.1519 | [0.0936, 0.2188]  — |
| Specificity | 0.9139 | [0.8624, 0.9612]  — |
| MCC | 0.1008 | [-0.0310, 0.2191]  — |
| R² | 0.0667 | [-0.0643, 0.1884]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0715 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6421 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3057 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3451 | < 0.20 |
| Log-Loss | 1.0526 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.1338 | proche 0 = pas de biais systématique |
| LoA lower | -6.6934 | limite inférieure d'accord |
| LoA upper | +4.4258 | limite supérieure d'accord |
| LoA width | ±5.5596 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0272 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0715 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7512 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4609 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 01:54*
