# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `D`  |  **Date :** 2026-06-21 18:49


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4366 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9117 | Erreur quadratique moyenne |
| R² | -0.4956 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4863 | 0.500 |
| PR-AUC | 0.2648 | 0.276 |
| Sensitivity (TPR) | 0.4496 | 0.500 |
| Specificity (TNR) | 0.5449 | 0.500 |
| PPV (Precision) | 0.2735 | — |
| NPV | 0.7221 | — |
| Balanced Accuracy | 0.4973 | 0.500 |
| MCC | -0.0049 | 0.000 |
| G-Mean | 0.4950 | 0.500 |
| F1 macro | 0.4806 | 0.500 |
| LR+ | 0.988 | >10 = très utile |
| LR− | 1.010 | <0.1 = très utile |
| Cohen κ | -0.0046 | 0.000 |
| Brier Score | 0.3109 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4864 | [0.4665, 0.5072]  — |
| F1 macro | 0.4806 | [0.4670, 0.4955]  — |
| Sensitivity | 0.4498 | [0.4213, 0.4794]  — |
| Specificity | 0.5448 | [0.5281, 0.5623]  — |
| MCC | -0.0048 | [-0.0343, 0.0267]  — |
| R² | -0.4963 | [-0.5487, -0.4486]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4956 | p=0.9980 | ❌ ns |
| AUC ROC | 0.4863 | p=0.9080 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2697 | < 0.05 |
| MCE | 0.7329 | < 0.10 |
| Brier Score | 0.3109 | < 0.20 |
| Log-Loss | 0.9239 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +1.0531 | proche 0 = pas de biais systématique |
| LoA lower | -4.2683 | limite inférieure d'accord |
| LoA upper | +6.3744 | limite supérieure d'accord |
| LoA width | ±5.3213 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.3098 | 2.3915 | 182.6% | 🔴 unstable |
| AUC ROC | 0.5250 | 0.1105 | 21.0% | 🟡 moderate |
| MAE | 2.4364 | 0.4079 | 16.7% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4859 |
| CI 95% | [0.4663, 0.5055] |
| p-value | 0.157979 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:49*
