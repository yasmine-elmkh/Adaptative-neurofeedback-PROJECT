# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:36


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5753 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0223 | Erreur quadratique moyenne |
| R² | 0.0478 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6136 | 0.500 |
| PR-AUC | 0.5904 | 0.519 |
| Sensitivity (TPR) | 0.7358 | 0.500 |
| Specificity (TNR) | 0.4409 | 0.500 |
| PPV (Precision) | 0.5864 | — |
| NPV | 0.6076 | — |
| Balanced Accuracy | 0.5883 | 0.500 |
| MCC | 0.1851 | 0.000 |
| G-Mean | 0.5695 | 0.500 |
| F1 macro | 0.5818 | 0.500 |
| LR+ | 1.316 | >10 = très utile |
| LR− | 0.599 | <0.1 = très utile |
| Cohen κ | 0.1784 | 0.000 |
| Brier Score | 0.2914 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6115 | [0.5907, 0.6305]  ✅ |
| F1 macro | 0.5506 | [0.5322, 0.5696]  ✅ |
| Sensitivity | 0.4133 | [0.3897, 0.4403]  — |
| Specificity | 0.7129 | [0.6865, 0.7352]  — |
| MCC | 0.1321 | [0.0952, 0.1657]  — |
| R² | 0.0478 | [0.0206, 0.0781]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0478 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6113 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2319 | < 0.05 |
| MCE | 0.3967 | < 0.10 |
| Brier Score | 0.3050 | < 0.20 |
| Log-Loss | 0.9422 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0474 | proche 0 = pas de biais systématique |
| LoA lower | -5.9714 | limite inférieure d'accord |
| LoA upper | +5.8766 | limite supérieure d'accord |
| LoA width | ±5.9240 | < ±2 pts : excellent |
| % dans LoA | 97.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1268 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0030 | 0.2002 | 6730.6% | 🔴 unstable |
| AUC ROC | 0.6310 | 0.0649 | 10.3% | 🟢 stable |
| MAE | 2.5882 | 0.2909 | 11.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6113 |
| CI 95% | [0.5907, 0.6320] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:36*
