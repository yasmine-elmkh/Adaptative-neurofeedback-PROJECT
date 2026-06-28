# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:07


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5539 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0883 | Erreur quadratique moyenne |
| R² | 0.0058 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6514 | 0.500 |
| PR-AUC | 0.6345 | 0.517 |
| Sensitivity (TPR) | 0.5856 | 0.500 |
| Specificity (TNR) | 0.6230 | 0.500 |
| PPV (Precision) | 0.6246 | — |
| NPV | 0.5839 | — |
| Balanced Accuracy | 0.6043 | 0.500 |
| MCC | 0.2086 | 0.000 |
| G-Mean | 0.6040 | 0.500 |
| F1 macro | 0.6037 | 0.500 |
| LR+ | 1.553 | >10 = très utile |
| LR− | 0.665 | <0.1 = très utile |
| Cohen κ | 0.2081 | 0.000 |
| Brier Score | 0.2959 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6511 | [0.6302, 0.6716]  ✅ |
| F1 macro | 0.6037 | [0.5843, 0.6225]  ✅ |
| Sensitivity | 0.5860 | [0.5614, 0.6106]  — |
| Specificity | 0.6228 | [0.5962, 0.6485]  — |
| MCC | 0.2087 | [0.1698, 0.2469]  — |
| R² | 0.0048 | [-0.0366, 0.0484]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0058 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6514 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2347 | < 0.05 |
| MCE | 0.3124 | < 0.10 |
| Brier Score | 0.2959 | < 0.20 |
| Log-Loss | 1.0006 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1187 | proche 0 = pas de biais systématique |
| LoA lower | -6.1684 | limite inférieure d'accord |
| LoA upper | +5.9310 | limite supérieure d'accord |
| LoA width | ±6.0497 | < ±2 pts : excellent |
| % dans LoA | 96.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1042 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0662 | 0.3411 | 515.7% | 🔴 unstable |
| AUC ROC | 0.6429 | 0.0942 | 14.7% | 🟢 stable |
| MAE | 2.5597 | 0.3234 | 12.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6482 |
| CI 95% | [0.6281, 0.6683] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.44 et 0.64


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:07*
