# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `A`  |  **Date :** 2026-06-21 17:18


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
| AUC ROC | 0.4605 | 0.500 |
| PR-AUC | 0.2286 | 0.253 |
| Sensitivity (TPR) | 0.0137 | 0.500 |
| Specificity (TNR) | 0.9880 | 0.500 |
| PPV (Precision) | 0.2800 | — |
| NPV | 0.7472 | — |
| Balanced Accuracy | 0.5009 | 0.500 |
| MCC | 0.0069 | 0.000 |
| G-Mean | 0.1165 | 0.500 |
| F1 macro | 0.4385 | 0.500 |
| LR+ | 1.148 | >10 = très utile |
| LR− | 0.998 | <0.1 = très utile |
| Cohen κ | 0.0026 | 0.000 |
| Brier Score | 0.2072 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4580 | [0.4328, 0.4817]  — |
| F1 macro | 0.4476 | [0.4291, 0.4664]  — |
| Sensitivity | 0.0972 | [0.0720, 0.1229]  — |
| Specificity | 0.8415 | [0.8202, 0.8606]  — |
| MCC | -0.0793 | [-0.1172, -0.0436]  — |
| R² | -0.2005 | [-0.2419, -0.1628]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1998 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4580 | p=0.9960 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1323 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2344 | < 0.20 |
| Log-Loss | 0.6693 | minimiser |

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
| AUC ROC | 0.5070 | 0.0835 | 16.5% | 🟡 moderate |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:18*
