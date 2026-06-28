# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:39


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6989 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2772 | Erreur quadratique moyenne |
| R² | -0.1196 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6656 | 0.500 |
| PR-AUC | 0.7489 | 0.644 |
| Sensitivity (TPR) | 0.8635 | 0.500 |
| Specificity (TNR) | 0.3886 | 0.500 |
| PPV (Precision) | 0.7184 | — |
| NPV | 0.6118 | — |
| Balanced Accuracy | 0.6260 | 0.500 |
| MCC | 0.2885 | 0.000 |
| G-Mean | 0.5793 | 0.500 |
| F1 macro | 0.6298 | 0.500 |
| LR+ | 1.412 | >10 = très utile |
| LR− | 0.351 | <0.1 = très utile |
| Cohen κ | 0.2745 | 0.000 |
| Brier Score | 0.2548 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6138 | [0.5947, 0.6329]  ✅ |
| F1 macro | 0.5608 | [0.5438, 0.5774]  ✅ |
| Sensitivity | 0.4659 | [0.4420, 0.4907]  — |
| Specificity | 0.6681 | [0.6441, 0.6928]  — |
| MCC | 0.1366 | [0.1026, 0.1708]  — |
| R² | -0.1203 | [-0.1670, -0.0758]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1196 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6136 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2696 | < 0.05 |
| MCE | 0.3713 | < 0.10 |
| Brier Score | 0.3279 | < 0.20 |
| Log-Loss | 1.1773 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1629 | proche 0 = pas de biais systématique |
| LoA lower | -6.5794 | limite inférieure d'accord |
| LoA upper | +6.2537 | limite supérieure d'accord |
| LoA width | ±6.4165 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0673 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1724 | 0.2674 | 155.2% | 🔴 unstable |
| AUC ROC | 0.6210 | 0.0893 | 14.4% | 🟢 stable |
| MAE | 2.7083 | 0.3489 | 12.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6136 |
| CI 95% | [0.5931, 0.6342] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:39*
