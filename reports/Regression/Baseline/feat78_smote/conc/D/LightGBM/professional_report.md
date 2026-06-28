# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `D`  |  **Date :** 2026-06-21 17:03


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5441 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0123 | Erreur quadratique moyenne |
| R² | 0.0541 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6286 | 0.500 |
| PR-AUC | 0.6061 | 0.517 |
| Sensitivity (TPR) | 0.5490 | 0.500 |
| Specificity (TNR) | 0.6177 | 0.500 |
| PPV (Precision) | 0.6054 | — |
| NPV | 0.5618 | — |
| Balanced Accuracy | 0.5834 | 0.500 |
| MCC | 0.1670 | 0.000 |
| G-Mean | 0.5823 | 0.500 |
| F1 macro | 0.5821 | 0.500 |
| LR+ | 1.436 | >10 = très utile |
| LR− | 0.730 | <0.1 = très utile |
| Cohen κ | 0.1662 | 0.000 |
| Brier Score | 0.2966 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6283 | [0.6090, 0.6482]  ✅ |
| F1 macro | 0.5818 | [0.5633, 0.5995]  ✅ |
| Sensitivity | 0.5485 | [0.5231, 0.5740]  — |
| Specificity | 0.6177 | [0.5921, 0.6411]  — |
| MCC | 0.1664 | [0.1294, 0.2015]  — |
| R² | 0.0529 | [0.0188, 0.0880]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0541 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6286 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2336 | < 0.05 |
| MCE | 0.3536 | < 0.10 |
| Brier Score | 0.2966 | < 0.20 |
| Log-Loss | 0.9257 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0084 | proche 0 = pas de biais systématique |
| LoA lower | -5.9136 | limite inférieure d'accord |
| LoA upper | +5.8967 | limite supérieure d'accord |
| LoA width | ±5.9052 | < ±2 pts : excellent |
| % dans LoA | 97.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1913 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0015 | 0.2518 | 16973.2% | 🔴 unstable |
| AUC ROC | 0.6250 | 0.0876 | 14.0% | 🟢 stable |
| MAE | 2.5560 | 0.2986 | 11.7% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6274 |
| CI 95% | [0.6070, 0.6479] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:03*
