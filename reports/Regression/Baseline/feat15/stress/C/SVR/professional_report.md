# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `C`  |  **Date :** 2026-06-21 17:52


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4079 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8992 | Erreur quadratique moyenne |
| R² | -0.4827 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4876 | 0.500 |
| PR-AUC | 0.4019 | 0.414 |
| Sensitivity (TPR) | 0.6423 | 0.500 |
| Specificity (TNR) | 0.3599 | 0.500 |
| PPV (Precision) | 0.4147 | — |
| NPV | 0.5876 | — |
| Balanced Accuracy | 0.5011 | 0.500 |
| MCC | 0.0022 | 0.000 |
| G-Mean | 0.4808 | 0.500 |
| F1 macro | 0.4752 | 0.500 |
| LR+ | 1.003 | >10 = très utile |
| LR− | 0.994 | <0.1 = très utile |
| Cohen κ | 0.0020 | 0.000 |
| Brier Score | 0.3602 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4869 | [0.4707, 0.5018]  — |
| F1 macro | 0.4777 | [0.4658, 0.4893]  — |
| Sensitivity | 0.4400 | [0.4167, 0.4625]  — |
| Specificity | 0.5443 | [0.5293, 0.5589]  — |
| MCC | -0.0142 | [-0.0389, 0.0098]  — |
| R² | -0.4851 | [-0.5203, -0.4444]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4827 | p=0.9960 | ❌ ns |
| AUC ROC | 0.4875 | p=0.9320 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2678 | < 0.05 |
| MCE | 0.7258 | < 0.10 |
| Brier Score | 0.3138 | < 0.20 |
| Log-Loss | 0.9336 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +1.0081 | proche 0 = pas de biais systématique |
| LoA lower | -4.3201 | limite inférieure d'accord |
| LoA upper | +6.3363 | limite supérieure d'accord |
| LoA width | ±5.3282 | < ±2 pts : excellent |
| % dans LoA | 96.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.2490 | 2.2484 | 180.0% | 🔴 unstable |
| AUC ROC | 0.5263 | 0.1058 | 20.1% | 🟡 moderate |
| MAE | 2.4077 | 0.4438 | 18.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4875 |
| CI 95% | [0.4717, 0.5034] |
| p-value | 0.124244 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:52*
