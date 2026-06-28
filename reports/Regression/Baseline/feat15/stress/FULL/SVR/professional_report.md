# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 19:27


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4356 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9288 | Erreur quadratique moyenne |
| R² | -0.5132 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4837 | 0.500 |
| PR-AUC | 0.4010 | 0.415 |
| Sensitivity (TPR) | 0.6526 | 0.500 |
| Specificity (TNR) | 0.3404 | 0.500 |
| PPV (Precision) | 0.4128 | — |
| NPV | 0.5797 | — |
| Balanced Accuracy | 0.4965 | 0.500 |
| MCC | -0.0072 | 0.000 |
| G-Mean | 0.4713 | 0.500 |
| F1 macro | 0.4673 | 0.500 |
| LR+ | 0.989 | >10 = très utile |
| LR− | 1.020 | <0.1 = très utile |
| Cohen κ | -0.0064 | 0.000 |
| Brier Score | 0.3703 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4842 | [0.4706, 0.4971]  — |
| F1 macro | 0.4710 | [0.4612, 0.4816]  — |
| Sensitivity | 0.4400 | [0.4215, 0.4626]  — |
| Specificity | 0.5322 | [0.5192, 0.5444]  — |
| MCC | -0.0251 | [-0.0456, -0.0034]  — |
| R² | -0.5129 | [-0.5458, -0.4806]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.5132 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4839 | p=0.9940 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2728 | < 0.05 |
| MCE | 0.7498 | < 0.10 |
| Brier Score | 0.3178 | < 0.20 |
| Log-Loss | 0.9582 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9959 | proche 0 = pas de biais systématique |
| LoA lower | -4.4028 | limite inférieure d'accord |
| LoA upper | +6.3947 | limite supérieure d'accord |
| LoA width | ±5.3988 | < ±2 pts : excellent |
| % dans LoA | 96.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.3073 | 2.3375 | 178.8% | 🔴 unstable |
| AUC ROC | 0.5352 | 0.0807 | 15.1% | 🟡 moderate |
| MAE | 2.4354 | 0.4373 | 18.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4839 |
| CI 95% | [0.4702, 0.4977] |
| p-value | 0.021830 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.28


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:27*
