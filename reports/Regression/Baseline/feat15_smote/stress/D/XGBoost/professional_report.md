# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `D`  |  **Date :** 2026-06-21 19:26


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2232 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6777 | Erreur quadratique moyenne |
| R² | -0.2648 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4791 | 0.500 |
| PR-AUC | 0.3987 | 0.414 |
| Sensitivity (TPR) | 0.3022 | 0.500 |
| Specificity (TNR) | 0.6986 | 0.500 |
| PPV (Precision) | 0.4145 | — |
| NPV | 0.5864 | — |
| Balanced Accuracy | 0.5004 | 0.500 |
| MCC | 0.0008 | 0.000 |
| G-Mean | 0.4594 | 0.500 |
| F1 macro | 0.4935 | 0.500 |
| LR+ | 1.002 | >10 = très utile |
| LR− | 0.999 | <0.1 = très utile |
| Cohen κ | 0.0007 | 0.000 |
| Brier Score | 0.3137 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4791 | [0.4600, 0.4984]  — |
| F1 macro | 0.4931 | [0.4777, 0.5097]  — |
| Sensitivity | 0.3015 | [0.2818, 0.3240]  — |
| Specificity | 0.6985 | [0.6798, 0.7185]  — |
| MCC | 0.0001 | [-0.0311, 0.0345]  — |
| R² | -0.2655 | [-0.2967, -0.2334]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2648 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4791 | p=0.9840 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2199 | < 0.05 |
| MCE | 0.6011 | < 0.10 |
| Brier Score | 0.3137 | < 0.20 |
| Log-Loss | 0.9264 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3888 | proche 0 = pas de biais systématique |
| LoA lower | -4.8044 | limite inférieure d'accord |
| LoA upper | +5.5821 | limite supérieure d'accord |
| LoA width | ±5.1933 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0013 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6954 | 1.2467 | 179.3% | 🔴 unstable |
| AUC ROC | 0.5057 | 0.0714 | 14.1% | 🟢 stable |
| MAE | 2.2230 | 0.6574 | 29.6% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4620 |
| CI 95% | [0.4419, 0.4821] |
| p-value | 0.000209 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:26*
