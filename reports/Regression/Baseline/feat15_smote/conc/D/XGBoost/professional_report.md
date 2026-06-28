# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:39


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6667 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1181 | Erreur quadratique moyenne |
| R² | -0.0135 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5820 | 0.500 |
| PR-AUC | 0.5739 | 0.517 |
| Sensitivity (TPR) | 0.5163 | 0.500 |
| Specificity (TNR) | 0.5828 | 0.500 |
| PPV (Precision) | 0.5694 | — |
| NPV | 0.5301 | — |
| Balanced Accuracy | 0.5496 | 0.500 |
| MCC | 0.0993 | 0.000 |
| G-Mean | 0.5486 | 0.500 |
| F1 macro | 0.5484 | 0.500 |
| LR+ | 1.238 | >10 = très utile |
| LR− | 0.830 | <0.1 = très utile |
| Cohen κ | 0.0989 | 0.000 |
| Brier Score | 0.3126 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5826 | [0.5600, 0.6030]  ✅ |
| F1 macro | 0.5488 | [0.5308, 0.5674]  ✅ |
| Sensitivity | 0.5172 | [0.4914, 0.5421]  — |
| Specificity | 0.5829 | [0.5576, 0.6087]  — |
| MCC | 0.1002 | [0.0648, 0.1365]  — |
| R² | -0.0128 | [-0.0458, 0.0197]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0135 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5820 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2374 | < 0.05 |
| MCE | 0.4099 | < 0.10 |
| Brier Score | 0.3126 | < 0.20 |
| Log-Loss | 0.9586 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0282 | proche 0 = pas de biais systématique |
| LoA lower | -6.1405 | limite inférieure d'accord |
| LoA upper | +6.0840 | limite supérieure d'accord |
| LoA width | ±6.1122 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1111 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0583 | 0.2200 | 377.2% | 🔴 unstable |
| AUC ROC | 0.5807 | 0.0728 | 12.5% | 🟢 stable |
| MAE | 2.6769 | 0.2930 | 10.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5799 |
| CI 95% | [0.5589, 0.6008] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:39*
