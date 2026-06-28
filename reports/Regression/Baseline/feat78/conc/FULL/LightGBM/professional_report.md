# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 18:09


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6467 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0572 | Erreur quadratique moyenne |
| R² | 0.0257 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6030 | 0.500 |
| PR-AUC | 0.6021 | 0.519 |
| Sensitivity (TPR) | 0.7608 | 0.500 |
| Specificity (TNR) | 0.3904 | 0.500 |
| PPV (Precision) | 0.5742 | — |
| NPV | 0.6017 | — |
| Balanced Accuracy | 0.5756 | 0.500 |
| MCC | 0.1630 | 0.000 |
| G-Mean | 0.5450 | 0.500 |
| F1 macro | 0.5640 | 0.500 |
| LR+ | 1.248 | >10 = très utile |
| LR− | 0.613 | <0.1 = très utile |
| Cohen κ | 0.1532 | 0.000 |
| Brier Score | 0.2901 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5998 | [0.5860, 0.6133]  ✅ |
| F1 macro | 0.5280 | [0.5152, 0.5412]  ✅ |
| Sensitivity | 0.3381 | [0.3218, 0.3560]  — |
| Specificity | 0.7681 | [0.7535, 0.7845]  — |
| MCC | 0.1174 | [0.0935, 0.1411]  — |
| R² | 0.0255 | [0.0071, 0.0446]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0257 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6000 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2200 | < 0.05 |
| MCE | 0.3479 | < 0.10 |
| Brier Score | 0.3044 | < 0.20 |
| Log-Loss | 0.9243 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0260 | proche 0 = pas de biais systématique |
| LoA lower | -6.0184 | limite inférieure d'accord |
| LoA upper | +5.9663 | limite supérieure d'accord |
| LoA width | ±5.9924 | < ±2 pts : excellent |
| % dans LoA | 98.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0938 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0233 | 0.1304 | 560.0% | 🔴 unstable |
| AUC ROC | 0.6080 | 0.0627 | 10.3% | 🟢 stable |
| MAE | 2.6562 | 0.2302 | 8.7% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6000 |
| CI 95% | [0.5853, 0.6146] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:09*
