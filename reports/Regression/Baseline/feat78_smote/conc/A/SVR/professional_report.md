# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `A`  |  **Date :** 2026-06-21 15:57


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5794 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1096 | Erreur quadratique moyenne |
| R² | -0.0080 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6409 | 0.500 |
| PR-AUC | 0.6466 | 0.519 |
| Sensitivity (TPR) | 0.6382 | 0.500 |
| Specificity (TNR) | 0.5460 | 0.500 |
| PPV (Precision) | 0.6023 | — |
| NPV | 0.5835 | — |
| Balanced Accuracy | 0.5921 | 0.500 |
| MCC | 0.1850 | 0.000 |
| G-Mean | 0.5903 | 0.500 |
| F1 macro | 0.5919 | 0.500 |
| LR+ | 1.406 | >10 = très utile |
| LR− | 0.663 | <0.1 = très utile |
| Cohen κ | 0.1846 | 0.000 |
| Brier Score | 0.3002 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6408 | [0.6098, 0.6676]  ✅ |
| F1 macro | 0.5915 | [0.5654, 0.6149]  ✅ |
| Sensitivity | 0.6375 | [0.6027, 0.6732]  — |
| Specificity | 0.5461 | [0.5123, 0.5842]  — |
| MCC | 0.1844 | [0.1325, 0.2313]  — |
| R² | -0.0085 | [-0.0700, 0.0505]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0080 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6409 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2435 | < 0.05 |
| MCE | 0.3097 | < 0.10 |
| Brier Score | 0.3002 | < 0.20 |
| Log-Loss | 0.9869 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0921 | proche 0 = pas de biais systématique |
| LoA lower | -6.1865 | limite inférieure d'accord |
| LoA upper | +6.0022 | limite supérieure d'accord |
| LoA width | ±6.0943 | < ±2 pts : excellent |
| % dans LoA | 96.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1458 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0712 | 0.3088 | 433.8% | 🔴 unstable |
| AUC ROC | 0.6432 | 0.0857 | 13.3% | 🟢 stable |
| MAE | 2.5919 | 0.3366 | 13.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6359 |
| CI 95% | [0.6073, 0.6645] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.44 et 0.66


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 15:57*
