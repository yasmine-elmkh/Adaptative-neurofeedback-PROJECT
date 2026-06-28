# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet`  |  **Exp :** `D`  |  **Date :** 2026-06-20 01:51


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6327 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2170 | Erreur quadratique moyenne |
| R² | -0.0339 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7596 | 0.500 |
| PR-AUC | 0.8517 | 0.719 |
| Sensitivity (TPR) | 0.9231 | 0.500 |
| Specificity (TNR) | 0.5738 | 0.500 |
| PPV (Precision) | 0.8471 | — |
| NPV | 0.7447 | — |
| Balanced Accuracy | 0.7484 | 0.500 |
| MCC | 0.5422 | 0.000 |
| G-Mean | 0.7278 | 0.500 |
| F1 macro | 0.7658 | 0.500 |
| LR+ | 2.166 | >10 = très utile |
| LR− | 0.134 | <0.1 = très utile |
| Cohen κ | 0.5342 | 0.000 |
| Brier Score | 0.1541 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6273 | [0.5501, 0.6952]  ✅ |
| F1 macro | 0.4140 | [0.3581, 0.4753]  — |
| Sensitivity | 0.1084 | [0.0588, 0.1706]  — |
| Specificity | 0.9339 | [0.8846, 0.9797]  — |
| MCC | 0.0743 | [-0.0539, 0.2025]  — |
| R² | -0.0370 | [-0.2020, 0.0868]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0339 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6260 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3678 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3760 | < 0.20 |
| Log-Loss | 1.2475 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.3193 | proche 0 = pas de biais systématique |
| LoA lower | -7.0833 | limite inférieure d'accord |
| LoA upper | +4.4446 | limite supérieure d'accord |
| LoA width | ±5.7639 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0160 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0339 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7596 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.6327 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 01:51*
