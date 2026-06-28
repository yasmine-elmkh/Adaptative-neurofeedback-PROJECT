# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `D`  |  **Date :** 2026-06-21 18:40


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
| AUC ROC | 0.4820 | 0.500 |
| PR-AUC | 0.4028 | 0.416 |
| Sensitivity (TPR) | 0.6961 | 0.500 |
| Specificity (TNR) | 0.2904 | 0.500 |
| PPV (Precision) | 0.4117 | — |
| NPV | 0.5725 | — |
| Balanced Accuracy | 0.4932 | 0.500 |
| MCC | -0.0146 | 0.000 |
| G-Mean | 0.4496 | 0.500 |
| F1 macro | 0.4514 | 0.500 |
| LR+ | 0.981 | >10 = très utile |
| LR− | 1.047 | <0.1 = très utile |
| Cohen κ | -0.0123 | 0.000 |
| Brier Score | 0.3814 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4860 | [0.4664, 0.5054]  — |
| F1 macro | 0.4754 | [0.4618, 0.4907]  — |
| Sensitivity | 0.4578 | [0.4294, 0.4875]  — |
| Specificity | 0.5280 | [0.5106, 0.5455]  — |
| MCC | -0.0128 | [-0.0419, 0.0189]  — |
| R² | -0.4963 | [-0.5487, -0.4486]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4956 | p=0.9980 | ❌ ns |
| AUC ROC | 0.4859 | p=0.9200 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2744 | < 0.05 |
| MCE | 0.7401 | < 0.10 |
| Brier Score | 0.3162 | < 0.20 |
| Log-Loss | 0.9373 | minimiser |

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
| AUC ROC | 0.5370 | 0.0889 | 16.6% | 🟡 moderate |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:40*
