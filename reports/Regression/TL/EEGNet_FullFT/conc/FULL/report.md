# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `FULL`  |  **Date :** 2026-06-20 02:35


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3694 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8421 | Erreur quadratique moyenne |
| R² | 0.1930 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6752 | 0.500 |
| PR-AUC | 0.6489 | 0.525 |
| Sensitivity (TPR) | 0.7193 | 0.500 |
| Specificity (TNR) | 0.5728 | 0.500 |
| PPV (Precision) | 0.6508 | — |
| NPV | 0.6484 | — |
| Balanced Accuracy | 0.6461 | 0.500 |
| MCC | 0.2956 | 0.000 |
| G-Mean | 0.6419 | 0.500 |
| F1 macro | 0.6458 | 0.500 |
| LR+ | 1.684 | >10 = très utile |
| LR− | 0.490 | <0.1 = très utile |
| Cohen κ | 0.2938 | 0.000 |
| Brier Score | 0.2540 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6762 | [0.6039, 0.7441]  ✅ |
| F1 macro | 0.6263 | [0.5604, 0.6898]  ✅ |
| Sensitivity | 0.5966 | [0.5091, 0.6894]  — |
| Specificity | 0.6606 | [0.5694, 0.7488]  — |
| MCC | 0.2574 | [0.1297, 0.3820]  — |
| R² | 0.1876 | [0.0838, 0.2871]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1930 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6752 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1821 | < 0.05 |
| MCE | 0.3745 | < 0.10 |
| Brier Score | 0.2608 | < 0.20 |
| Log-Loss | 0.7622 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0291 | proche 0 = pas de biais systématique |
| LoA lower | -5.6122 | limite inférieure d'accord |
| LoA upper | +5.5541 | limite supérieure d'accord |
| LoA width | ±5.5832 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2681 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1930 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6752 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3694 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:35*
