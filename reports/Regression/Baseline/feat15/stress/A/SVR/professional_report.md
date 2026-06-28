# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:59


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3876 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8598 | Erreur quadratique moyenne |
| R² | -0.4428 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4836 | 0.500 |
| PR-AUC | 0.4031 | 0.416 |
| Sensitivity (TPR) | 0.7223 | 0.500 |
| Specificity (TNR) | 0.2755 | 0.500 |
| PPV (Precision) | 0.4156 | — |
| NPV | 0.5817 | — |
| Balanced Accuracy | 0.4989 | 0.500 |
| MCC | -0.0024 | 0.000 |
| G-Mean | 0.4461 | 0.500 |
| F1 macro | 0.4508 | 0.500 |
| LR+ | 0.997 | >10 = très utile |
| LR− | 1.008 | <0.1 = très utile |
| Cohen κ | -0.0020 | 0.000 |
| Brier Score | 0.3687 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4933 | [0.4683, 0.5213]  — |
| F1 macro | 0.4786 | [0.4580, 0.4996]  — |
| Sensitivity | 0.4525 | [0.4102, 0.4940]  — |
| Specificity | 0.5372 | [0.5103, 0.5622]  — |
| MCC | -0.0094 | [-0.0487, 0.0347]  — |
| R² | -0.4436 | [-0.5140, -0.3857]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4428 | p=0.9420 | ❌ ns |
| AUC ROC | 0.4925 | p=0.6800 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2536 | < 0.05 |
| MCE | 0.6979 | < 0.10 |
| Brier Score | 0.3039 | < 0.20 |
| Log-Loss | 0.8778 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +1.1004 | proche 0 = pas de biais systématique |
| LoA lower | -4.0745 | limite inférieure d'accord |
| LoA upper | +6.2754 | limite supérieure d'accord |
| LoA width | ±5.1750 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.2425 | 2.4213 | 194.9% | 🔴 unstable |
| AUC ROC | 0.5299 | 0.0928 | 17.5% | 🟡 moderate |
| MAE | 2.3874 | 0.4327 | 18.1% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4925 |
| CI 95% | [0.4648, 0.5201] |
| p-value | 0.593405 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.26 et 0.28


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:59*
