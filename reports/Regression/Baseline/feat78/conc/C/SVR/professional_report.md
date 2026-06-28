# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:33


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.8278 | Erreur absolue moyenne (0-10) |
| RMSE | 3.3444 | Erreur quadratique moyenne |
| R² | -0.1659 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5565 | 0.500 |
| PR-AUC | 0.5789 | 0.541 |
| Sensitivity (TPR) | 0.7463 | 0.500 |
| Specificity (TNR) | 0.3435 | 0.500 |
| PPV (Precision) | 0.5728 | — |
| NPV | 0.5346 | — |
| Balanced Accuracy | 0.5449 | 0.500 |
| MCC | 0.0982 | 0.000 |
| G-Mean | 0.5064 | 0.500 |
| F1 macro | 0.5332 | 0.500 |
| LR+ | 1.137 | >10 = très utile |
| LR− | 0.738 | <0.1 = très utile |
| Cohen κ | 0.0924 | 0.000 |
| Brier Score | 0.3396 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5472 | [0.5314, 0.5648]  ✅ |
| F1 macro | 0.5155 | [0.5010, 0.5287]  ✅ |
| Sensitivity | 0.3782 | [0.3580, 0.3969]  — |
| Specificity | 0.6796 | [0.6605, 0.6972]  — |
| MCC | 0.0606 | [0.0319, 0.0866]  — |
| R² | -0.1657 | [-0.1985, -0.1290]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1659 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5470 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2974 | < 0.05 |
| MCE | 0.4295 | < 0.10 |
| Brier Score | 0.3562 | < 0.20 |
| Log-Loss | 1.2234 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0484 | proche 0 = pas de biais systématique |
| LoA lower | -6.6035 | limite inférieure d'accord |
| LoA upper | +6.5066 | limite supérieure d'accord |
| LoA width | ±6.5550 | < ±2 pts : excellent |
| % dans LoA | 97.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0599 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.2214 | 0.1723 | 77.8% | 🔴 unstable |
| AUC ROC | 0.5785 | 0.0515 | 8.9% | 🟢 stable |
| MAE | 2.8256 | 0.1889 | 6.7% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5470 |
| CI 95% | [0.5297, 0.5642] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.51 et 0.54


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:33*
