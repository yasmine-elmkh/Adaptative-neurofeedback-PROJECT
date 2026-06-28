# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:25


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7106 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0771 | Erreur quadratique moyenne |
| R² | 0.0130 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5759 | 0.500 |
| PR-AUC | 0.5755 | 0.516 |
| Sensitivity (TPR) | 0.3147 | 0.500 |
| Specificity (TNR) | 0.7961 | 0.500 |
| PPV (Precision) | 0.6218 | — |
| NPV | 0.5216 | — |
| Balanced Accuracy | 0.5554 | 0.500 |
| MCC | 0.1261 | 0.000 |
| G-Mean | 0.5005 | 0.500 |
| F1 macro | 0.5241 | 0.500 |
| LR+ | 1.543 | >10 = très utile |
| LR− | 0.861 | <0.1 = très utile |
| Cohen κ | 0.1090 | 0.000 |
| Brier Score | 0.3038 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5753 | [0.5552, 0.5969]  ✅ |
| F1 macro | 0.5145 | [0.4965, 0.5323]  — |
| Sensitivity | 0.2898 | [0.2663, 0.3145]  — |
| Specificity | 0.8135 | [0.7943, 0.8333]  — |
| MCC | 0.1210 | [0.0884, 0.1571]  — |
| R² | 0.0128 | [-0.0092, 0.0349]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0130 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5753 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2145 | < 0.05 |
| MCE | 0.5793 | < 0.10 |
| Brier Score | 0.3070 | < 0.20 |
| Log-Loss | 0.9148 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0152 | proche 0 = pas de biais systématique |
| LoA lower | -6.0473 | limite inférieure d'accord |
| LoA upper | +6.0168 | limite supérieure d'accord |
| LoA width | ±6.0320 | < ±2 pts : excellent |
| % dans LoA | 99.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0664 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0399 | 0.1673 | 419.6% | 🔴 unstable |
| AUC ROC | 0.5879 | 0.0698 | 11.9% | 🟢 stable |
| MAE | 2.7159 | 0.2048 | 7.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5753 |
| CI 95% | [0.5544, 0.5962] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:25*
