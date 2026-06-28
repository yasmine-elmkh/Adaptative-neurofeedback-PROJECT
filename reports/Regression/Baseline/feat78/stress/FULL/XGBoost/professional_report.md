# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `FULL`  |  **Date :** 2026-06-22 00:27


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1520 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5366 | Erreur quadratique moyenne |
| R² | -0.1351 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4983 | 0.500 |
| PR-AUC | 0.3077 | 0.307 |
| Sensitivity (TPR) | 0.1529 | 0.500 |
| Specificity (TNR) | 0.8604 | 0.500 |
| PPV (Precision) | 0.3264 | — |
| NPV | 0.6966 | — |
| Balanced Accuracy | 0.5067 | 0.500 |
| MCC | 0.0175 | 0.000 |
| G-Mean | 0.3627 | 0.500 |
| F1 macro | 0.4891 | 0.500 |
| LR+ | 1.095 | >10 = très utile |
| LR− | 0.985 | <0.1 = très utile |
| Cohen κ | 0.0156 | 0.000 |
| Brier Score | 0.2406 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4990 | [0.4841, 0.5122]  — |
| F1 macro | 0.4860 | [0.4756, 0.4957]  — |
| Sensitivity | 0.1236 | [0.1097, 0.1367]  — |
| Specificity | 0.8893 | [0.8821, 0.8974]  — |
| MCC | 0.0183 | [-0.0026, 0.0396]  — |
| R² | -0.1351 | [-0.1509, -0.1180]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1351 | p=0.6260 | ❌ ns |
| AUC ROC | 0.4994 | p=0.5380 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1298 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2284 | < 0.20 |
| Log-Loss | 0.6732 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.6179 | proche 0 = pas de biais systématique |
| LoA lower | -4.2044 | limite inférieure d'accord |
| LoA upper | +5.4402 | limite supérieure d'accord |
| LoA width | ±4.8223 | < ±2 pts : excellent |
| % dans LoA | 96.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6546 | 1.6284 | 248.8% | 🔴 unstable |
| AUC ROC | 0.5114 | 0.0457 | 8.9% | 🟢 stable |
| MAE | 2.1518 | 0.5004 | 23.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4994 |
| CI 95% | [0.4853, 0.5135] |
| p-value | 0.932865 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.88 et 0.88


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-22 00:27*
