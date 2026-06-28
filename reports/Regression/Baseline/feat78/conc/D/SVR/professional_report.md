# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `D`  |  **Date :** 2026-06-21 17:08


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7703 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2657 | Erreur quadratique moyenne |
| R² | -0.1117 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5728 | 0.500 |
| PR-AUC | 0.5661 | 0.517 |
| Sensitivity (TPR) | 0.5618 | 0.500 |
| Specificity (TNR) | 0.5633 | 0.500 |
| PPV (Precision) | 0.5795 | — |
| NPV | 0.5455 | — |
| Balanced Accuracy | 0.5626 | 0.500 |
| MCC | 0.1251 | 0.000 |
| G-Mean | 0.5626 | 0.500 |
| F1 macro | 0.5624 | 0.500 |
| LR+ | 1.287 | >10 = très utile |
| LR− | 0.778 | <0.1 = très utile |
| Cohen κ | 0.1250 | 0.000 |
| Brier Score | 0.3287 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5728 | [0.5535, 0.5934]  ✅ |
| F1 macro | 0.5341 | [0.5180, 0.5522]  ✅ |
| Sensitivity | 0.3863 | [0.3624, 0.4108]  — |
| Specificity | 0.7118 | [0.6877, 0.7355]  — |
| MCC | 0.1036 | [0.0694, 0.1404]  — |
| R² | -0.1118 | [-0.1515, -0.0741]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1117 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5721 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2894 | < 0.05 |
| MCE | 0.4107 | < 0.10 |
| Brier Score | 0.3447 | < 0.20 |
| Log-Loss | 1.1775 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0617 | proche 0 = pas de biais systématique |
| LoA lower | -6.4624 | limite inférieure d'accord |
| LoA upper | +6.3391 | limite supérieure d'accord |
| LoA width | ±6.4007 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0823 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1876 | 0.2524 | 134.5% | 🔴 unstable |
| AUC ROC | 0.5850 | 0.0828 | 14.2% | 🟢 stable |
| MAE | 2.7754 | 0.1236 | 4.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5721 |
| CI 95% | [0.5511, 0.5931] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.57


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:08*
