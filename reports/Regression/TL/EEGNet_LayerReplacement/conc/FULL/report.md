# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `FULL`  |  **Date :** 2026-06-20 02:50


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3345 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7825 | Erreur quadratique moyenne |
| R² | 0.2265 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7019 | 0.500 |
| PR-AUC | 0.6816 | 0.535 |
| Sensitivity (TPR) | 0.8448 | 0.500 |
| Specificity (TNR) | 0.5050 | 0.500 |
| PPV (Precision) | 0.6622 | — |
| NPV | 0.7391 | — |
| Balanced Accuracy | 0.6749 | 0.500 |
| MCC | 0.3747 | 0.000 |
| G-Mean | 0.6531 | 0.500 |
| F1 macro | 0.6712 | 0.500 |
| LR+ | 1.707 | >10 = très utile |
| LR− | 0.307 | <0.1 = très utile |
| Cohen κ | 0.3571 | 0.000 |
| Brier Score | 0.2281 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6937 | [0.6248, 0.7620]  ✅ |
| F1 macro | 0.5918 | [0.5278, 0.6516]  ✅ |
| Sensitivity | 0.5578 | [0.4722, 0.6422]  — |
| Specificity | 0.6311 | [0.5402, 0.7277]  — |
| MCC | 0.1891 | [0.0605, 0.3108]  — |
| R² | 0.2218 | [0.1308, 0.3091]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2265 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7019 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1622 | < 0.05 |
| MCE | 0.4227 | < 0.10 |
| Brier Score | 0.2426 | < 0.20 |
| Log-Loss | 0.6928 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1052 | proche 0 = pas de biais systématique |
| LoA lower | -5.5676 | limite inférieure d'accord |
| LoA upper | +5.3573 | limite supérieure d'accord |
| LoA width | ±5.4625 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2554 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2265 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7019 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3345 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:50*
