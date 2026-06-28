# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `A`  |  **Date :** 2026-06-21 18:08


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2070 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6085 | Erreur quadratique moyenne |
| R² | -0.2003 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.3967 | 0.500 |
| PR-AUC | 0.0152 | 0.015 |
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
| Brier Score | 0.0148 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.3937 | [0.2750, 0.5113]  — |
| F1 macro | 0.4963 | [0.4950, 0.4975]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | -0.2015 | [-0.2440, -0.1629]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2003 | p=1.0000 | ❌ ns |
| AUC ROC | 0.3967 | p=0.9780 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.0132 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.0148 | < 0.20 |
| Log-Loss | 0.1025 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9276 | proche 0 = pas de biais systématique |
| LoA lower | -3.8521 | limite inférieure d'accord |
| LoA upper | +5.7073 | limite supérieure d'accord |
| LoA width | ±4.7797 | < ±2 pts : excellent |
| % dans LoA | 96.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7945 | 1.8325 | 230.7% | 🔴 unstable |
| AUC ROC | 0.5271 | 0.0936 | 17.8% | 🟡 moderate |
| MAE | 2.2067 | 0.5394 | 24.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4546 |
| CI 95% | [0.4260, 0.4832] |
| p-value | 0.001839 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:08*
