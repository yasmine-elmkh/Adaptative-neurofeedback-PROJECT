# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:03


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 3.2819 | Erreur absolue moyenne (0-10) |
| RMSE | 3.9208 | Erreur quadratique moyenne |
| R² | -0.6025 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.3216 | 0.500 |
| PR-AUC | 0.6038 | 0.719 |
| Sensitivity (TPR) | 0.9961 | 0.500 |
| Specificity (TNR) | 0.0150 | 0.500 |
| PPV (Precision) | 0.7212 | — |
| NPV | 0.6000 | — |
| Balanced Accuracy | 0.5055 | 0.500 |
| MCC | 0.0597 | 0.000 |
| G-Mean | 0.1222 | 0.500 |
| F1 macro | 0.4329 | 0.500 |
| LR+ | 1.011 | >10 = très utile |
| LR− | 0.261 | <0.1 = très utile |
| Cohen κ | 0.0158 | 0.000 |
| Brier Score | 0.2738 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.3808 | [0.3530, 0.4114]  — |
| F1 macro | 0.4058 | [0.3820, 0.4311]  — |
| Sensitivity | 0.3067 | [0.2741, 0.3388]  — |
| Specificity | 0.5226 | [0.4848, 0.5606]  — |
| MCC | -0.1750 | [-0.2221, -0.1233]  — |
| R² | -0.6052 | [-0.6880, -0.5199]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.6025 | p=1.0000 | ❌ ns |
| AUC ROC | 0.3817 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3975 | < 0.05 |
| MCE | 0.6615 | < 0.10 |
| Brier Score | 0.4381 | < 0.20 |
| Log-Loss | 1.4835 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5255 | proche 0 = pas de biais systématique |
| LoA lower | -7.0926 | limite inférieure d'accord |
| LoA upper | +8.1437 | limite supérieure d'accord |
| LoA width | ±7.6182 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0132 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6069 | 0.3206 | 52.8% | 🔴 unstable |
| AUC ROC | 0.3960 | 0.1369 | 34.6% | 🔴 unstable |
| MAE | 3.2437 | 0.4729 | 14.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.3817 |
| CI 95% | [0.3526, 0.4108] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:03*
