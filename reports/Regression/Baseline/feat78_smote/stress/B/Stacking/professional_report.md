# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `B`  |  **Date :** 2026-06-21 19:13


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3165 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8517 | Erreur quadratique moyenne |
| R² | -0.4346 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4963 | 0.500 |
| PR-AUC | 0.5592 | 0.572 |
| Sensitivity (TPR) | 0.9536 | 0.500 |
| Specificity (TNR) | 0.0516 | 0.500 |
| PPV (Precision) | 0.5730 | — |
| NPV | 0.4541 | — |
| Balanced Accuracy | 0.5026 | 0.500 |
| MCC | 0.0118 | 0.000 |
| G-Mean | 0.2217 | 0.500 |
| F1 macro | 0.4042 | 0.500 |
| LR+ | 1.005 | >10 = très utile |
| LR− | 0.901 | <0.1 = très utile |
| Cohen κ | 0.0058 | 0.000 |
| Brier Score | 0.3531 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4965 | [0.4796, 0.5126]  — |
| F1 macro | 0.4048 | [0.3928, 0.4166]  — |
| Sensitivity | 0.9536 | [0.9441, 0.9626]  — |
| Specificity | 0.0521 | [0.0419, 0.0633]  — |
| MCC | 0.0132 | [-0.0159, 0.0467]  — |
| R² | -0.4349 | [-0.4928, -0.3761]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4346 | p=0.9980 | ❌ ns |
| AUC ROC | 0.4963 | p=0.6640 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3123 | < 0.05 |
| MCE | 0.5088 | < 0.10 |
| Brier Score | 0.3531 | < 0.20 |
| Log-Loss | 1.2810 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8872 | proche 0 = pas de biais systématique |
| LoA lower | -4.4255 | limite inférieure d'accord |
| LoA upper | +6.1998 | limite supérieure d'accord |
| LoA width | ±5.3126 | < ±2 pts : excellent |
| % dans LoA | 95.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.9894 | 1.9281 | 194.9% | 🔴 unstable |
| AUC ROC | 0.5211 | 0.0595 | 11.4% | 🟢 stable |
| MAE | 2.3161 | 0.8725 | 37.7% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4930 |
| CI 95% | [0.4733, 0.5127] |
| p-value | 0.486122 |
| Significatif | ❌ NON |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:13*
