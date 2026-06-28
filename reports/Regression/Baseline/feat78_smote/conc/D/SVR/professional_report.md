# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:49


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5496 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0841 | Erreur quadratique moyenne |
| R² | 0.0085 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6453 | 0.500 |
| PR-AUC | 0.6338 | 0.517 |
| Sensitivity (TPR) | 0.5971 | 0.500 |
| Specificity (TNR) | 0.6077 | 0.500 |
| PPV (Precision) | 0.6199 | — |
| NPV | 0.5847 | — |
| Balanced Accuracy | 0.6024 | 0.500 |
| MCC | 0.2047 | 0.000 |
| G-Mean | 0.6024 | 0.500 |
| F1 macro | 0.6022 | 0.500 |
| LR+ | 1.522 | >10 = très utile |
| LR− | 0.663 | <0.1 = très utile |
| Cohen κ | 0.2046 | 0.000 |
| Brier Score | 0.2996 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6450 | [0.6238, 0.6656]  ✅ |
| F1 macro | 0.6019 | [0.5822, 0.6186]  ✅ |
| Sensitivity | 0.5972 | [0.5732, 0.6231]  — |
| Specificity | 0.6073 | [0.5794, 0.6297]  — |
| MCC | 0.2044 | [0.1651, 0.2377]  — |
| R² | 0.0069 | [-0.0348, 0.0499]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0085 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6453 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2449 | < 0.05 |
| MCE | 0.3539 | < 0.10 |
| Brier Score | 0.2996 | < 0.20 |
| Log-Loss | 1.0028 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0727 | proche 0 = pas de biais systématique |
| LoA lower | -6.1168 | limite inférieure d'accord |
| LoA upper | +5.9715 | limite supérieure d'accord |
| LoA width | ±6.0442 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1574 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0645 | 0.3384 | 524.5% | 🔴 unstable |
| AUC ROC | 0.6384 | 0.1011 | 15.8% | 🟡 moderate |
| MAE | 2.5601 | 0.3410 | 13.3% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6426 |
| CI 95% | [0.6224, 0.6628] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:49*
