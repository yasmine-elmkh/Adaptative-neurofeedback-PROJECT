# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `B`  |  **Date :** 2026-06-21 18:12


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3575 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8383 | Erreur quadratique moyenne |
| R² | -0.4211 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5151 | 0.500 |
| PR-AUC | 0.2838 | 0.272 |
| Sensitivity (TPR) | 0.4044 | 0.500 |
| Specificity (TNR) | 0.6081 | 0.500 |
| PPV (Precision) | 0.2787 | — |
| NPV | 0.7316 | — |
| Balanced Accuracy | 0.5062 | 0.500 |
| MCC | 0.0114 | 0.000 |
| G-Mean | 0.4959 | 0.500 |
| F1 macro | 0.4971 | 0.500 |
| LR+ | 1.032 | >10 = très utile |
| LR− | 0.979 | <0.1 = très utile |
| Cohen κ | 0.0109 | 0.000 |
| Brier Score | 0.2964 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5146 | [0.4935, 0.5359]  — |
| F1 macro | 0.4966 | [0.4824, 0.5138]  — |
| Sensitivity | 0.4040 | [0.3745, 0.4360]  — |
| Specificity | 0.6077 | [0.5916, 0.6242]  — |
| MCC | 0.0106 | [-0.0182, 0.0444]  — |
| R² | -0.4221 | [-0.4684, -0.3737]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4211 | p=0.0680 | ❌ ns |
| AUC ROC | 0.5151 | p=0.0560 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2546 | < 0.05 |
| MCE | 0.6513 | < 0.10 |
| Brier Score | 0.2964 | < 0.20 |
| Log-Loss | 0.8953 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9078 | proche 0 = pas de biais systématique |
| LoA lower | -4.3636 | limite inférieure d'accord |
| LoA upper | +6.1793 | limite supérieure d'accord |
| LoA width | ±5.2714 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.2161 | 2.5446 | 209.3% | 🔴 unstable |
| AUC ROC | 0.5272 | 0.0920 | 17.4% | 🟡 moderate |
| MAE | 2.3573 | 0.4454 | 18.9% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5133 |
| CI 95% | [0.4935, 0.5331] |
| p-value | 0.187434 |
| Significatif | ❌ NON |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:12*
