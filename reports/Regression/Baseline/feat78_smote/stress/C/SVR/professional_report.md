# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `C`  |  **Date :** 2026-06-21 19:21


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3855 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8736 | Erreur quadratique moyenne |
| R² | -0.4567 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5055 | 0.500 |
| PR-AUC | 0.2759 | 0.277 |
| Sensitivity (TPR) | 0.4002 | 0.500 |
| Specificity (TNR) | 0.5907 | 0.500 |
| PPV (Precision) | 0.2725 | — |
| NPV | 0.7200 | — |
| Balanced Accuracy | 0.4955 | 0.500 |
| MCC | -0.0082 | 0.000 |
| G-Mean | 0.4862 | 0.500 |
| F1 macro | 0.4866 | 0.500 |
| LR+ | 0.978 | >10 = très utile |
| LR− | 1.015 | <0.1 = très utile |
| Cohen κ | -0.0079 | 0.000 |
| Brier Score | 0.3058 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5051 | [0.4886, 0.5210]  — |
| F1 macro | 0.4861 | [0.4738, 0.4994]  — |
| Sensitivity | 0.3994 | [0.3744, 0.4239]  — |
| Specificity | 0.5906 | [0.5778, 0.6049]  — |
| MCC | -0.0091 | [-0.0343, 0.0180]  — |
| R² | -0.4581 | [-0.4990, -0.4183]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4567 | p=0.4840 | ❌ ns |
| AUC ROC | 0.5055 | p=0.2720 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2727 | < 0.05 |
| MCE | 0.6742 | < 0.10 |
| Brier Score | 0.3058 | < 0.20 |
| Log-Loss | 0.9248 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9017 | proche 0 = pas de biais systématique |
| LoA lower | -4.4466 | limite inférieure d'accord |
| LoA upper | +6.2500 | limite supérieure d'accord |
| LoA width | ±5.3483 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.2443 | 2.5011 | 201.0% | 🔴 unstable |
| AUC ROC | 0.5222 | 0.0785 | 15.0% | 🟡 moderate |
| MAE | 2.3854 | 0.4789 | 20.1% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5041 |
| CI 95% | [0.4882, 0.5201] |
| p-value | 0.613209 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:21*
