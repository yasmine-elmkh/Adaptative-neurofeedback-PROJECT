# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 19:40


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
| AUC ROC | 0.4833 | 0.500 |
| PR-AUC | 0.2648 | 0.282 |
| Sensitivity (TPR) | 0.4375 | 0.500 |
| Specificity (TNR) | 0.5347 | 0.500 |
| PPV (Precision) | 0.2696 | — |
| NPV | 0.7078 | — |
| Balanced Accuracy | 0.4861 | 0.500 |
| MCC | -0.0251 | 0.000 |
| G-Mean | 0.4837 | 0.500 |
| F1 macro | 0.4714 | 0.500 |
| LR+ | 0.940 | >10 = très utile |
| LR− | 1.052 | <0.1 = très utile |
| Cohen κ | -0.0234 | 0.000 |
| Brier Score | 0.3173 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4835 | [0.4702, 0.4964]  — |
| F1 macro | 0.4715 | [0.4618, 0.4816]  — |
| Sensitivity | 0.4377 | [0.4193, 0.4600]  — |
| Specificity | 0.5347 | [0.5218, 0.5471]  — |
| MCC | -0.0249 | [-0.0450, -0.0031]  — |
| R² | -0.5129 | [-0.5458, -0.4806]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.5132 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4833 | p=0.9940 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2725 | < 0.05 |
| MCE | 0.7547 | < 0.10 |
| Brier Score | 0.3173 | < 0.20 |
| Log-Loss | 0.9569 | minimiser |

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
| AUC ROC | 0.5198 | 0.1081 | 20.8% | 🟡 moderate |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:40*
