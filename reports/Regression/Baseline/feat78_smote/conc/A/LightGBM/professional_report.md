# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:05


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5873 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0320 | Erreur quadratique moyenne |
| R² | 0.0417 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6156 | 0.500 |
| PR-AUC | 0.6072 | 0.517 |
| Sensitivity (TPR) | 0.5347 | 0.500 |
| Specificity (TNR) | 0.6061 | 0.500 |
| PPV (Precision) | 0.5919 | — |
| NPV | 0.5494 | — |
| Balanced Accuracy | 0.5704 | 0.500 |
| MCC | 0.1410 | 0.000 |
| G-Mean | 0.5693 | 0.500 |
| F1 macro | 0.5691 | 0.500 |
| LR+ | 1.357 | >10 = très utile |
| LR− | 0.768 | <0.1 = très utile |
| Cohen κ | 0.1403 | 0.000 |
| Brier Score | 0.2968 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6158 | [0.5863, 0.6430]  ✅ |
| F1 macro | 0.5693 | [0.5448, 0.5992]  ✅ |
| Sensitivity | 0.5348 | [0.4979, 0.5715]  — |
| Specificity | 0.6066 | [0.5684, 0.6437]  — |
| MCC | 0.1417 | [0.0927, 0.2019]  — |
| R² | 0.0414 | [-0.0072, 0.0877]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0417 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6156 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2340 | < 0.05 |
| MCE | 0.3280 | < 0.10 |
| Brier Score | 0.2968 | < 0.20 |
| Log-Loss | 0.9106 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0423 | proche 0 = pas de biais systématique |
| LoA lower | -5.9018 | limite inférieure d'accord |
| LoA upper | +5.9865 | limite supérieure d'accord |
| LoA width | ±5.9441 | < ±2 pts : excellent |
| % dans LoA | 98.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1564 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0198 | 0.2708 | 1370.6% | 🔴 unstable |
| AUC ROC | 0.6211 | 0.1008 | 16.2% | 🟡 moderate |
| MAE | 2.5983 | 0.2658 | 10.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6140 |
| CI 95% | [0.5848, 0.6431] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:05*
