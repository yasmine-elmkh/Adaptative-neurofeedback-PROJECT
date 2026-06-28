# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:31


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5985 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1265 | Erreur quadratique moyenne |
| R² | -0.0190 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6222 | 0.500 |
| PR-AUC | 0.6159 | 0.517 |
| Sensitivity (TPR) | 0.6196 | 0.500 |
| Specificity (TNR) | 0.5539 | 0.500 |
| PPV (Precision) | 0.5980 | — |
| NPV | 0.5761 | — |
| Balanced Accuracy | 0.5867 | 0.500 |
| MCC | 0.1738 | 0.000 |
| G-Mean | 0.5858 | 0.500 |
| F1 macro | 0.5867 | 0.500 |
| LR+ | 1.389 | >10 = très utile |
| LR− | 0.687 | <0.1 = très utile |
| Cohen κ | 0.1736 | 0.000 |
| Brier Score | 0.3025 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6217 | [0.6021, 0.6427]  ✅ |
| F1 macro | 0.5860 | [0.5693, 0.6041]  ✅ |
| Sensitivity | 0.6190 | [0.5934, 0.6454]  — |
| Specificity | 0.5533 | [0.5284, 0.5791]  — |
| MCC | 0.1726 | [0.1391, 0.2088]  — |
| R² | -0.0195 | [-0.0569, 0.0207]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0190 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6222 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2399 | < 0.05 |
| MCE | 0.3399 | < 0.10 |
| Brier Score | 0.3025 | < 0.20 |
| Log-Loss | 0.9892 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0307 | proche 0 = pas de biais systématique |
| LoA lower | -6.1595 | limite inférieure d'accord |
| LoA upper | +6.0980 | limite supérieure d'accord |
| LoA width | ±6.1288 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1654 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0749 | 0.2536 | 338.5% | 🔴 unstable |
| AUC ROC | 0.6214 | 0.0746 | 12.0% | 🟢 stable |
| MAE | 2.6126 | 0.3027 | 11.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6210 |
| CI 95% | [0.6006, 0.6415] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:31*
