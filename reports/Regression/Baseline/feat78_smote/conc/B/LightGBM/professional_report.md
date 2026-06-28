# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:20


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4926 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9225 | Erreur quadratique moyenne |
| R² | 0.1097 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6559 | 0.500 |
| PR-AUC | 0.6362 | 0.517 |
| Sensitivity (TPR) | 0.5299 | 0.500 |
| Specificity (TNR) | 0.6650 | 0.500 |
| PPV (Precision) | 0.6282 | — |
| NPV | 0.5697 | — |
| Balanced Accuracy | 0.5975 | 0.500 |
| MCC | 0.1964 | 0.000 |
| G-Mean | 0.5936 | 0.500 |
| F1 macro | 0.5943 | 0.500 |
| LR+ | 1.582 | >10 = très utile |
| LR− | 0.707 | <0.1 = très utile |
| Cohen κ | 0.1939 | 0.000 |
| Brier Score | 0.2769 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6559 | [0.6374, 0.6751]  ✅ |
| F1 macro | 0.5939 | [0.5748, 0.6126]  ✅ |
| Sensitivity | 0.5296 | [0.5040, 0.5549]  — |
| Specificity | 0.6647 | [0.6375, 0.6898]  — |
| MCC | 0.1959 | [0.1576, 0.2336]  — |
| R² | 0.1095 | [0.0792, 0.1418]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1097 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6559 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1965 | < 0.05 |
| MCE | 0.3512 | < 0.10 |
| Brier Score | 0.2769 | < 0.20 |
| Log-Loss | 0.8523 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0124 | proche 0 = pas de biais systématique |
| LoA lower | -5.7415 | limite inférieure d'accord |
| LoA upper | +5.7166 | limite supérieure d'accord |
| LoA width | ±5.7290 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2053 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0616 | 0.1995 | 323.6% | 🔴 unstable |
| AUC ROC | 0.6531 | 0.0901 | 13.8% | 🟢 stable |
| MAE | 2.4896 | 0.2112 | 8.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6535 |
| CI 95% | [0.6335, 0.6736] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.44 et 0.66


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:20*
