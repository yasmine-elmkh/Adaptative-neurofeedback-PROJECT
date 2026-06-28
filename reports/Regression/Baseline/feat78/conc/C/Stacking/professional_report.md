# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `C`  |  **Date :** 2026-06-21 17:07


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7244 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1832 | Erreur quadratique moyenne |
| R² | -0.0562 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5678 | 0.500 |
| PR-AUC | 0.5631 | 0.519 |
| Sensitivity (TPR) | 0.6495 | 0.500 |
| Specificity (TNR) | 0.4657 | 0.500 |
| PPV (Precision) | 0.5670 | — |
| NPV | 0.5522 | — |
| Balanced Accuracy | 0.5576 | 0.500 |
| MCC | 0.1172 | 0.000 |
| G-Mean | 0.5500 | 0.500 |
| F1 macro | 0.5554 | 0.500 |
| LR+ | 1.216 | >10 = très utile |
| LR− | 0.753 | <0.1 = très utile |
| Cohen κ | 0.1158 | 0.000 |
| Brier Score | 0.3107 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5651 | [0.5473, 0.5826]  ✅ |
| F1 macro | 0.5073 | [0.4919, 0.5226]  — |
| Sensitivity | 0.3285 | [0.3069, 0.3480]  — |
| Specificity | 0.7326 | [0.7139, 0.7501]  — |
| MCC | 0.0668 | [0.0367, 0.0957]  — |
| R² | -0.0565 | [-0.0850, -0.0267]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0562 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5651 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2582 | < 0.05 |
| MCE | 0.4201 | < 0.10 |
| Brier Score | 0.3306 | < 0.20 |
| Log-Loss | 1.0669 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1304 | proche 0 = pas de biais systématique |
| LoA lower | -6.3649 | limite inférieure d'accord |
| LoA upper | +6.1041 | limite supérieure d'accord |
| LoA width | ±6.2345 | < ±2 pts : excellent |
| % dans LoA | 98.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0281 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1105 | 0.1731 | 156.7% | 🔴 unstable |
| AUC ROC | 0.5809 | 0.0413 | 7.1% | 🟢 stable |
| MAE | 2.7306 | 0.2371 | 8.7% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5651 |
| CI 95% | [0.5479, 0.5823] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.51 et 0.56


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:07*
