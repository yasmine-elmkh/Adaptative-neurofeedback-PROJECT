# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `D`  |  **Date :** 2026-06-21 21:24


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2628 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7473 | Erreur quadratique moyenne |
| R² | -0.3314 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4760 | 0.500 |
| PR-AUC | 0.3892 | 0.414 |
| Sensitivity (TPR) | 0.3064 | 0.500 |
| Specificity (TNR) | 0.6710 | 0.500 |
| PPV (Precision) | 0.3967 | — |
| NPV | 0.5780 | — |
| Balanced Accuracy | 0.4887 | 0.500 |
| MCC | -0.0239 | 0.000 |
| G-Mean | 0.4534 | 0.500 |
| F1 macro | 0.4834 | 0.500 |
| LR+ | 0.931 | >10 = très utile |
| LR− | 1.034 | <0.1 = très utile |
| Cohen κ | -0.0234 | 0.000 |
| Brier Score | 0.3269 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4761 | [0.4587, 0.4945]  — |
| F1 macro | 0.4833 | [0.4683, 0.4980]  — |
| Sensitivity | 0.3065 | [0.2860, 0.3301]  — |
| Specificity | 0.6708 | [0.6538, 0.6904]  — |
| MCC | -0.0239 | [-0.0535, 0.0051]  — |
| R² | -0.3314 | [-0.3666, -0.2957]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3314 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4760 | p=0.9960 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2471 | < 0.05 |
| MCE | 0.7035 | < 0.10 |
| Brier Score | 0.3269 | < 0.20 |
| Log-Loss | 0.9810 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4017 | proche 0 = pas de biais systématique |
| LoA lower | -4.9258 | limite inférieure d'accord |
| LoA upper | +5.7291 | limite supérieure d'accord |
| LoA width | ±5.3275 | < ±2 pts : excellent |
| % dans LoA | 95.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0015 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.9160 | 2.0663 | 225.6% | 🔴 unstable |
| AUC ROC | 0.5104 | 0.0869 | 17.0% | 🟡 moderate |
| MAE | 2.2625 | 0.6721 | 29.7% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4447 |
| CI 95% | [0.4250, 0.4644] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ❌ NON**

Le modèle n'apporte pas de bénéfice net par rapport aux stratégies 'traiter tous' ou 'ne traiter personne'.


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 21:24*
