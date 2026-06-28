# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-20 01:57


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5257 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0553 | Erreur quadratique moyenne |
| R² | 0.0269 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6760 | 0.500 |
| PR-AUC | 0.6883 | 0.566 |
| Sensitivity (TPR) | 0.7503 | 0.500 |
| Specificity (TNR) | 0.4951 | 0.500 |
| PPV (Precision) | 0.6594 | — |
| NPV | 0.6036 | — |
| Balanced Accuracy | 0.6227 | 0.500 |
| MCC | 0.2540 | 0.000 |
| G-Mean | 0.6095 | 0.500 |
| F1 macro | 0.6230 | 0.500 |
| LR+ | 1.486 | >10 = très utile |
| LR− | 0.504 | <0.1 = très utile |
| Cohen κ | 0.2507 | 0.000 |
| Brier Score | 0.2504 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6376 | [0.6124, 0.6664]  ✅ |
| F1 macro | 0.4575 | [0.4319, 0.4828]  — |
| Sensitivity | 0.1808 | [0.1542, 0.2085]  — |
| Specificity | 0.8738 | [0.8470, 0.8990]  — |
| MCC | 0.0755 | [0.0242, 0.1251]  — |
| R² | 0.0265 | [-0.0241, 0.0775]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3243 | < 0.05 |
| MCE | 0.4516 | < 0.10 |
| Brier Score | 0.3544 | < 0.20 |
| Log-Loss | 1.1896 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.8033 | proche 0 = pas de biais systématique |
| LoA lower | -6.5830 | limite inférieure d'accord |
| LoA upper | +4.9764 | limite supérieure d'accord |
| LoA width | ±5.7797 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0066 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0162 | 0.1798 | 1111.9% | 🔴 unstable |
| AUC ROC | 0.6720 | 0.1022 | 15.2% | 🟡 moderate |
| MAE | 2.5490 | 0.3124 | 12.3% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 01:57*
