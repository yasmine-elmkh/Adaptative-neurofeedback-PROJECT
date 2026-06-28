# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:02


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6254 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0783 | Erreur quadratique moyenne |
| R² | 0.0122 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5961 | 0.500 |
| PR-AUC | 0.5789 | 0.517 |
| Sensitivity (TPR) | 0.5353 | 0.500 |
| Specificity (TNR) | 0.6026 | 0.500 |
| PPV (Precision) | 0.5907 | — |
| NPV | 0.5476 | — |
| Balanced Accuracy | 0.5690 | 0.500 |
| MCC | 0.1381 | 0.000 |
| G-Mean | 0.5680 | 0.500 |
| F1 macro | 0.5677 | 0.500 |
| LR+ | 1.347 | >10 = très utile |
| LR− | 0.771 | <0.1 = très utile |
| Cohen κ | 0.1375 | 0.000 |
| Brier Score | 0.3033 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5966 | [0.5656, 0.6249]  ✅ |
| F1 macro | 0.5678 | [0.5404, 0.5929]  ✅ |
| Sensitivity | 0.5352 | [0.4966, 0.5721]  — |
| Specificity | 0.6032 | [0.5668, 0.6431]  — |
| MCC | 0.1386 | [0.0828, 0.1888]  — |
| R² | 0.0114 | [-0.0372, 0.0564]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0122 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5961 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2285 | < 0.05 |
| MCE | 0.3549 | < 0.10 |
| Brier Score | 0.3033 | < 0.20 |
| Log-Loss | 0.9219 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0464 | proche 0 = pas de biais systématique |
| LoA lower | -6.0813 | limite inférieure d'accord |
| LoA upper | +5.9885 | limite supérieure d'accord |
| LoA width | ±6.0349 | < ±2 pts : excellent |
| % dans LoA | 97.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1213 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0341 | 0.2121 | 621.9% | 🔴 unstable |
| AUC ROC | 0.5970 | 0.0598 | 10.0% | 🟢 stable |
| MAE | 2.6355 | 0.2811 | 10.7% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5933 |
| CI 95% | [0.5637, 0.6229] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.56


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:02*
