# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `D`  |  **Date :** 2026-06-21 19:14


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2097 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6192 | Erreur quadratique moyenne |
| R² | -0.2102 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4723 | 0.500 |
| PR-AUC | 0.6729 | 0.703 |
| Sensitivity (TPR) | 0.9993 | 0.500 |
| Specificity (TNR) | 0.0008 | 0.500 |
| PPV (Precision) | 0.7028 | — |
| NPV | 0.3333 | — |
| Balanced Accuracy | 0.5001 | 0.500 |
| MCC | 0.0022 | 0.000 |
| G-Mean | 0.0289 | 0.500 |
| F1 macro | 0.4134 | 0.500 |
| LR+ | 1.000 | >10 = très utile |
| LR− | 0.846 | <0.1 = très utile |
| Cohen κ | 0.0002 | 0.000 |
| Brier Score | 0.2698 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4536 | [0.4325, 0.4726]  — |
| F1 macro | 0.4422 | [0.4305, 0.4537]  — |
| Sensitivity | 0.0591 | [0.0455, 0.0722]  — |
| Specificity | 0.9024 | [0.8910, 0.9120]  — |
| MCC | -0.0616 | [-0.0875, -0.0359]  — |
| R² | -0.2099 | [-0.2363, -0.1880]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2102 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4531 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1960 | < 0.05 |
| MCE | 0.9335 | < 0.10 |
| Brier Score | 0.2594 | < 0.20 |
| Log-Loss | 0.8234 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0940 | proche 0 = pas de biais systématique |
| LoA lower | -5.0369 | limite inférieure d'accord |
| LoA upper | +5.2249 | limite supérieure d'accord |
| LoA width | ±5.1309 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0182 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.9237 | 3.2116 | 347.7% | 🔴 unstable |
| AUC ROC | 0.5147 | 0.0599 | 11.6% | 🟢 stable |
| MAE | 2.2095 | 0.6799 | 30.8% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4531 |
| CI 95% | [0.4333, 0.4729] |
| p-value | 0.000003 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:14*
