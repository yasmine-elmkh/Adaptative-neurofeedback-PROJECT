# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 23:03


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2580 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6707 | Erreur quadratique moyenne |
| R² | -0.2583 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5025 | 0.500 |
| PR-AUC | 0.2538 | 0.256 |
| Sensitivity (TPR) | 0.0971 | 0.500 |
| Specificity (TNR) | 0.8933 | 0.500 |
| PPV (Precision) | 0.2381 | — |
| NPV | 0.7424 | — |
| Balanced Accuracy | 0.4952 | 0.500 |
| MCC | -0.0137 | 0.000 |
| G-Mean | 0.2945 | 0.500 |
| F1 macro | 0.4744 | 0.500 |
| LR+ | 0.910 | >10 = très utile |
| LR− | 1.011 | <0.1 = très utile |
| Cohen κ | -0.0119 | 0.000 |
| Brier Score | 0.2461 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5025 | [0.4884, 0.5143]  — |
| F1 macro | 0.4742 | [0.4645, 0.4838]  — |
| Sensitivity | 0.0971 | [0.0842, 0.1092]  — |
| Specificity | 0.8930 | [0.8857, 0.9007]  — |
| MCC | -0.0142 | [-0.0356, 0.0058]  — |
| R² | -0.2587 | [-0.2826, -0.2379]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2583 | p=1.0000 | ❌ ns |
| AUC ROC | 0.5025 | p=0.3660 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2009 | < 0.05 |
| MCE | 0.6884 | < 0.10 |
| Brier Score | 0.2461 | < 0.20 |
| Log-Loss | 0.8286 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1774 | proche 0 = pas de biais systématique |
| LoA lower | -5.0460 | limite inférieure d'accord |
| LoA upper | +5.4008 | limite supérieure d'accord |
| LoA width | ±5.2234 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0014 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7093 | 1.1413 | 160.9% | 🔴 unstable |
| AUC ROC | 0.5290 | 0.0655 | 12.4% | 🟢 stable |
| MAE | 2.2580 | 0.5461 | 24.2% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4869 |
| CI 95% | [0.4730, 0.5007] |
| p-value | 0.062624 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 23:03*
