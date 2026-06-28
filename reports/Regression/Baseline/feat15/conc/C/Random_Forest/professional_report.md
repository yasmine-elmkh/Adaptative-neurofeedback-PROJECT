# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:24


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5794 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0161 | Erreur quadratique moyenne |
| R² | 0.0517 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6180 | 0.500 |
| PR-AUC | 0.6050 | 0.519 |
| Sensitivity (TPR) | 0.7326 | 0.500 |
| Specificity (TNR) | 0.4501 | 0.500 |
| PPV (Precision) | 0.5894 | — |
| NPV | 0.6098 | — |
| Balanced Accuracy | 0.5914 | 0.500 |
| MCC | 0.1908 | 0.000 |
| G-Mean | 0.5743 | 0.500 |
| F1 macro | 0.5856 | 0.500 |
| LR+ | 1.332 | >10 = très utile |
| LR− | 0.594 | <0.1 = très utile |
| Cohen κ | 0.1845 | 0.000 |
| Brier Score | 0.2876 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6153 | [0.5996, 0.6314]  ✅ |
| F1 macro | 0.5473 | [0.5341, 0.5628]  ✅ |
| Sensitivity | 0.3982 | [0.3797, 0.4207]  — |
| Specificity | 0.7262 | [0.7063, 0.7452]  — |
| MCC | 0.1314 | [0.1055, 0.1608]  — |
| R² | 0.0514 | [0.0254, 0.0769]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0517 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6152 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2188 | < 0.05 |
| MCE | 0.3468 | < 0.10 |
| Brier Score | 0.3008 | < 0.20 |
| Log-Loss | 0.9300 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0168 | proche 0 = pas de biais systématique |
| LoA lower | -5.9290 | limite inférieure d'accord |
| LoA upper | +5.8954 | limite supérieure d'accord |
| LoA width | ±5.9122 | < ±2 pts : excellent |
| % dans LoA | 97.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1432 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0035 | 0.1968 | 5628.5% | 🔴 unstable |
| AUC ROC | 0.6154 | 0.0891 | 14.5% | 🟢 stable |
| MAE | 2.5944 | 0.2138 | 8.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6152 |
| CI 95% | [0.5984, 0.6320] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:24*
