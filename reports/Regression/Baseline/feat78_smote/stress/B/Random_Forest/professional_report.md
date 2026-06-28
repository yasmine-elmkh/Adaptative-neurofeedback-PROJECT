# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `B`  |  **Date :** 2026-06-21 18:56


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2005 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6006 | Erreur quadratique moyenne |
| R² | -0.1930 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4529 | 0.500 |
| PR-AUC | 0.3869 | 0.414 |
| Sensitivity (TPR) | 0.1037 | 0.500 |
| Specificity (TNR) | 0.8522 | 0.500 |
| PPV (Precision) | 0.3314 | — |
| NPV | 0.5738 | — |
| Balanced Accuracy | 0.4780 | 0.500 |
| MCC | -0.0646 | 0.000 |
| G-Mean | 0.2973 | 0.500 |
| F1 macro | 0.4219 | 0.500 |
| LR+ | 0.702 | >10 = très utile |
| LR− | 1.052 | <0.1 = très utile |
| Cohen κ | -0.0490 | 0.000 |
| Brier Score | 0.3282 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4535 | [0.4356, 0.4711]  — |
| F1 macro | 0.4219 | [0.4083, 0.4362]  — |
| Sensitivity | 0.1038 | [0.0892, 0.1186]  — |
| Specificity | 0.8524 | [0.8371, 0.8670]  — |
| MCC | -0.0642 | [-0.0958, -0.0316]  — |
| R² | -0.1932 | [-0.2182, -0.1670]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1930 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4529 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2688 | < 0.05 |
| MCE | 0.5428 | < 0.10 |
| Brier Score | 0.3282 | < 0.20 |
| Log-Loss | 0.9728 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0954 | proche 0 = pas de biais systématique |
| LoA lower | -4.9989 | limite inférieure d'accord |
| LoA upper | +5.1898 | limite supérieure d'accord |
| LoA width | ±5.0943 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0104 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7291 | 2.0848 | 286.0% | 🔴 unstable |
| AUC ROC | 0.4957 | 0.0623 | 12.6% | 🟢 stable |
| MAE | 2.2003 | 0.6415 | 29.2% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4362 |
| CI 95% | [0.4167, 0.4557] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:56*
