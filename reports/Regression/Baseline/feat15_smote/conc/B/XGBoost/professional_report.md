# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:12


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5200 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9535 | Erreur quadratique moyenne |
| R² | 0.0907 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6393 | 0.500 |
| PR-AUC | 0.6262 | 0.517 |
| Sensitivity (TPR) | 0.5482 | 0.500 |
| Specificity (TNR) | 0.6245 | 0.500 |
| PPV (Precision) | 0.6100 | — |
| NPV | 0.5634 | — |
| Balanced Accuracy | 0.5863 | 0.500 |
| MCC | 0.1730 | 0.000 |
| G-Mean | 0.5851 | 0.500 |
| F1 macro | 0.5849 | 0.500 |
| LR+ | 1.460 | >10 = très utile |
| LR− | 0.723 | <0.1 = très utile |
| Cohen κ | 0.1721 | 0.000 |
| Brier Score | 0.2819 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6396 | [0.6188, 0.6581]  ✅ |
| F1 macro | 0.5850 | [0.5672, 0.6014]  ✅ |
| Sensitivity | 0.5487 | [0.5236, 0.5746]  — |
| Specificity | 0.6243 | [0.6001, 0.6499]  — |
| MCC | 0.1734 | [0.1384, 0.2068]  — |
| R² | 0.0911 | [0.0619, 0.1221]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0907 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6393 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2034 | < 0.05 |
| MCE | 0.2968 | < 0.10 |
| Brier Score | 0.2819 | < 0.20 |
| Log-Loss | 0.8589 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0692 | proche 0 = pas de biais systématique |
| LoA lower | -5.8574 | limite inférieure d'accord |
| LoA upper | +5.7191 | limite supérieure d'accord |
| LoA width | ±5.7882 | < ±2 pts : excellent |
| % dans LoA | 97.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1340 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0538 | 0.1581 | 293.9% | 🔴 unstable |
| AUC ROC | 0.6464 | 0.0692 | 10.7% | 🟢 stable |
| MAE | 2.5129 | 0.2149 | 8.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6370 |
| CI 95% | [0.6167, 0.6573] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:12*
