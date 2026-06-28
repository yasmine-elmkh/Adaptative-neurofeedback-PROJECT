# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `B`  |  **Date :** 2026-06-21 17:51


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3104 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7727 | Erreur quadratique moyenne |
| R² | -0.3561 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.3913 | 0.500 |
| PR-AUC | 0.0566 | 0.072 |
| Sensitivity (TPR) | 0.0205 | 0.500 |
| Specificity (TNR) | 0.9791 | 0.500 |
| PPV (Precision) | 0.0714 | — |
| NPV | 0.9275 | — |
| Balanced Accuracy | 0.4998 | 0.500 |
| MCC | -0.0006 | 0.000 |
| G-Mean | 0.1418 | 0.500 |
| F1 macro | 0.4923 | 0.500 |
| LR+ | 0.985 | >10 = très utile |
| LR− | 1.000 | <0.1 = très utile |
| Cohen κ | -0.0005 | 0.000 |
| Brier Score | 0.0834 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4439 | [0.4223, 0.4630]  — |
| F1 macro | 0.4689 | [0.4543, 0.4845]  — |
| Sensitivity | 0.1693 | [0.1475, 0.1916]  — |
| Specificity | 0.7818 | [0.7661, 0.7966]  — |
| MCC | -0.0546 | [-0.0837, -0.0235]  — |
| R² | -0.3573 | [-0.3958, -0.3208]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3561 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4445 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2428 | < 0.05 |
| MCE | 0.7378 | < 0.10 |
| Brier Score | 0.2936 | < 0.20 |
| Log-Loss | 0.9338 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5210 | proche 0 = pas de biais systématique |
| LoA lower | -4.8173 | limite inférieure d'accord |
| LoA upper | +5.8593 | limite supérieure d'accord |
| LoA width | ±5.3383 | < ±2 pts : excellent |
| % dans LoA | 95.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0006 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.1707 | 3.1945 | 272.9% | 🔴 unstable |
| AUC ROC | 0.5237 | 0.0609 | 11.6% | 🟢 stable |
| MAE | 2.3102 | 0.6642 | 28.8% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4445 |
| CI 95% | [0.4247, 0.4643] |
| p-value | 0.000000 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:51*
