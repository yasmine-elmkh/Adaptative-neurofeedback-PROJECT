# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 17:02


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6669 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2060 | Erreur quadratique moyenne |
| R² | -0.0714 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6068 | 0.500 |
| PR-AUC | 0.5990 | 0.517 |
| Sensitivity (TPR) | 0.6185 | 0.500 |
| Specificity (TNR) | 0.5255 | 0.500 |
| PPV (Precision) | 0.5827 | — |
| NPV | 0.5625 | — |
| Balanced Accuracy | 0.5720 | 0.500 |
| MCC | 0.1446 | 0.000 |
| G-Mean | 0.5701 | 0.500 |
| F1 macro | 0.5717 | 0.500 |
| LR+ | 1.304 | >10 = très utile |
| LR− | 0.726 | <0.1 = très utile |
| Cohen κ | 0.1443 | 0.000 |
| Brier Score | 0.3139 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6070 | [0.5924, 0.6225]  ✅ |
| F1 macro | 0.5713 | [0.5587, 0.5855]  ✅ |
| Sensitivity | 0.6181 | [0.6015, 0.6374]  — |
| Specificity | 0.5251 | [0.5078, 0.5450]  — |
| MCC | 0.1438 | [0.1186, 0.1723]  — |
| R² | -0.0709 | [-0.1053, -0.0372]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0714 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6068 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2510 | < 0.05 |
| MCE | 0.3493 | < 0.10 |
| Brier Score | 0.3139 | < 0.20 |
| Log-Loss | 1.0572 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0771 | proche 0 = pas de biais systématique |
| LoA lower | -6.3595 | limite inférieure d'accord |
| LoA upper | +6.2053 | limite supérieure d'accord |
| LoA width | ±6.2824 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0867 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1287 | 0.2139 | 166.2% | 🔴 unstable |
| AUC ROC | 0.5986 | 0.0550 | 9.2% | 🟢 stable |
| MAE | 2.6877 | 0.2732 | 10.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6056 |
| CI 95% | [0.5910, 0.6202] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:02*
