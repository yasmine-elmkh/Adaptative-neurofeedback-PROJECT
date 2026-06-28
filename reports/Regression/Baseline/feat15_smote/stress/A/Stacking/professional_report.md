# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `A`  |  **Date :** 2026-06-21 17:21


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2100 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6079 | Erreur quadratique moyenne |
| R² | -0.1998 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.3332 | 0.500 |
| PR-AUC | 0.0105 | 0.015 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 1.0000 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.9851 | — |
| Balanced Accuracy | 0.5000 | 0.500 |
| MCC | 0.0000 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.4963 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.000 | <0.1 = très utile |
| Cohen κ | 0.0000 | 0.000 |
| Brier Score | 0.0149 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.3320 | [0.2301, 0.4340]  — |
| F1 macro | 0.4963 | [0.4950, 0.4975]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | -0.2005 | [-0.2419, -0.1628]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1998 | p=1.0000 | ❌ ns |
| AUC ROC | 0.3332 | p=0.9980 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.0133 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.0149 | < 0.20 |
| Log-Loss | 0.1072 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8609 | proche 0 = pas de biais systématique |
| LoA lower | -3.9652 | limite inférieure d'accord |
| LoA upper | +5.6871 | limite supérieure d'accord |
| LoA width | ±4.8261 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0003 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.8521 | 2.2444 | 263.4% | 🔴 unstable |
| AUC ROC | 0.4929 | 0.0405 | 8.2% | 🟢 stable |
| MAE | 2.2097 | 0.5471 | 24.8% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4580 |
| CI 95% | [0.4304, 0.4856] |
| p-value | 0.002870 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ❌ NON**

Le modèle n'apporte pas de bénéfice net par rapport aux stratégies 'traiter tous' ou 'ne traiter personne'.


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:21*
