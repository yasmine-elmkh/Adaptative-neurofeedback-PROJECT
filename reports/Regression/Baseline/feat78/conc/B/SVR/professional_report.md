# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:09


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7385 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2470 | Erreur quadratique moyenne |
| R² | -0.0990 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5777 | 0.500 |
| PR-AUC | 0.5751 | 0.519 |
| Sensitivity (TPR) | 0.6854 | 0.500 |
| Specificity (TNR) | 0.4327 | 0.500 |
| PPV (Precision) | 0.5662 | — |
| NPV | 0.5601 | — |
| Balanced Accuracy | 0.5591 | 0.500 |
| MCC | 0.1222 | 0.000 |
| G-Mean | 0.5446 | 0.500 |
| F1 macro | 0.5542 | 0.500 |
| LR+ | 1.208 | >10 = très utile |
| LR− | 0.727 | <0.1 = très utile |
| Cohen κ | 0.1191 | 0.000 |
| Brier Score | 0.3288 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5740 | [0.5541, 0.5951]  ✅ |
| F1 macro | 0.5247 | [0.5067, 0.5426]  ✅ |
| Sensitivity | 0.3916 | [0.3690, 0.4175]  — |
| Specificity | 0.6825 | [0.6597, 0.7072]  — |
| MCC | 0.0774 | [0.0415, 0.1149]  — |
| R² | -0.0999 | [-0.1374, -0.0573]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0990 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5744 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2894 | < 0.05 |
| MCE | 0.4036 | < 0.10 |
| Brier Score | 0.3437 | < 0.20 |
| Log-Loss | 1.1681 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0597 | proche 0 = pas de biais systématique |
| LoA lower | -6.4240 | limite inférieure d'accord |
| LoA upper | +6.3045 | limite supérieure d'accord |
| LoA width | ±6.3642 | < ±2 pts : excellent |
| % dans LoA | 97.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0923 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1711 | 0.2804 | 163.8% | 🔴 unstable |
| AUC ROC | 0.5976 | 0.0750 | 12.6% | 🟢 stable |
| MAE | 2.7478 | 0.2151 | 7.8% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5744 |
| CI 95% | [0.5534, 0.5954] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:09*
