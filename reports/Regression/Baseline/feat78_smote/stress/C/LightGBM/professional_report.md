# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `C`  |  **Date :** 2026-06-21 20:38


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1708 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5968 | Erreur quadratique moyenne |
| R² | -0.1895 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5224 | 0.500 |
| PR-AUC | 0.4449 | 0.414 |
| Sensitivity (TPR) | 0.3653 | 0.500 |
| Specificity (TNR) | 0.6622 | 0.500 |
| PPV (Precision) | 0.4330 | — |
| NPV | 0.5963 | — |
| Balanced Accuracy | 0.5137 | 0.500 |
| MCC | 0.0284 | 0.000 |
| G-Mean | 0.4918 | 0.500 |
| F1 macro | 0.5119 | 0.500 |
| LR+ | 1.081 | >10 = très utile |
| LR− | 0.959 | <0.1 = très utile |
| Cohen κ | 0.0281 | 0.000 |
| Brier Score | 0.2981 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5217 | [0.5083, 0.5364]  ✅ |
| F1 macro | 0.5115 | [0.4999, 0.5240]  — |
| Sensitivity | 0.3649 | [0.3478, 0.3852]  — |
| Specificity | 0.6619 | [0.6471, 0.6758]  — |
| MCC | 0.0277 | [0.0027, 0.0526]  — |
| R² | -0.1912 | [-0.2154, -0.1663]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1895 | p=0.0680 | ❌ ns |
| AUC ROC | 0.5224 | p=0.0040 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1974 | < 0.05 |
| MCE | 0.4455 | < 0.10 |
| Brier Score | 0.2981 | < 0.20 |
| Log-Loss | 0.8571 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4768 | proche 0 = pas de biais systématique |
| LoA lower | -4.5268 | limite inférieure d'accord |
| LoA upper | +5.4804 | limite supérieure d'accord |
| LoA width | ±5.0036 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6111 | 1.1031 | 180.5% | 🔴 unstable |
| AUC ROC | 0.5361 | 0.0542 | 10.1% | 🟢 stable |
| MAE | 2.1706 | 0.5645 | 26.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5261 |
| CI 95% | [0.5098, 0.5423] |
| p-value | 0.001687 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.30


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:38*
