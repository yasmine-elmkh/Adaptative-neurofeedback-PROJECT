# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `D`  |  **Date :** 2026-06-21 17:25


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6548 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0720 | Erreur quadratique moyenne |
| R² | 0.0162 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6002 | 0.500 |
| PR-AUC | 0.5890 | 0.517 |
| Sensitivity (TPR) | 0.4395 | 0.500 |
| Specificity (TNR) | 0.7064 | 0.500 |
| PPV (Precision) | 0.6152 | — |
| NPV | 0.5412 | — |
| Balanced Accuracy | 0.5729 | 0.500 |
| MCC | 0.1511 | 0.000 |
| G-Mean | 0.5572 | 0.500 |
| F1 macro | 0.5628 | 0.500 |
| LR+ | 1.497 | >10 = très utile |
| LR− | 0.794 | <0.1 = très utile |
| Cohen κ | 0.1444 | 0.000 |
| Brier Score | 0.3010 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5993 | [0.5801, 0.6199]  ✅ |
| F1 macro | 0.5367 | [0.5198, 0.5554]  ✅ |
| Sensitivity | 0.3577 | [0.3337, 0.3846]  — |
| Specificity | 0.7594 | [0.7388, 0.7800]  — |
| MCC | 0.1276 | [0.0947, 0.1638]  — |
| R² | 0.0161 | [-0.0089, 0.0438]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0162 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5990 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2338 | < 0.05 |
| MCE | 0.4052 | < 0.10 |
| Brier Score | 0.3113 | < 0.20 |
| Log-Loss | 0.9576 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0244 | proche 0 = pas de biais systématique |
| LoA lower | -6.0465 | limite inférieure d'accord |
| LoA upper | +5.9976 | limite supérieure d'accord |
| LoA width | ±6.0220 | < ±2 pts : excellent |
| % dans LoA | 98.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1077 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0365 | 0.1624 | 444.9% | 🔴 unstable |
| AUC ROC | 0.6051 | 0.0583 | 9.6% | 🟢 stable |
| MAE | 2.6623 | 0.2244 | 8.4% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5990 |
| CI 95% | [0.5783, 0.6198] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:25*
