# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `D`  |  **Date :** 2026-06-21 23:08


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1482 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5301 | Erreur quadratique moyenne |
| R² | -0.1292 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4844 | 0.500 |
| PR-AUC | 0.4782 | 0.493 |
| Sensitivity (TPR) | 0.6122 | 0.500 |
| Specificity (TNR) | 0.3820 | 0.500 |
| PPV (Precision) | 0.4909 | — |
| NPV | 0.5029 | — |
| Balanced Accuracy | 0.4971 | 0.500 |
| MCC | -0.0060 | 0.000 |
| G-Mean | 0.4836 | 0.500 |
| F1 macro | 0.4895 | 0.500 |
| LR+ | 0.991 | >10 = très utile |
| LR− | 1.015 | <0.1 = très utile |
| Cohen κ | -0.0058 | 0.000 |
| Brier Score | 0.3095 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4908 | [0.4718, 0.5103]  — |
| F1 macro | 0.4675 | [0.4540, 0.4818]  — |
| Sensitivity | 0.0927 | [0.0758, 0.1110]  — |
| Specificity | 0.8998 | [0.8893, 0.9102]  — |
| MCC | -0.0113 | [-0.0413, 0.0202]  — |
| R² | -0.1295 | [-0.1531, -0.1048]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1292 | p=0.8360 | ❌ ns |
| AUC ROC | 0.4905 | p=0.8280 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1636 | < 0.05 |
| MCE | 0.7583 | < 0.10 |
| Brier Score | 0.2386 | < 0.20 |
| Log-Loss | 0.7213 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3638 | proche 0 = pas de biais systématique |
| LoA lower | -4.5442 | limite inférieure d'accord |
| LoA upper | +5.2718 | limite supérieure d'accord |
| LoA width | ±4.9080 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6085 | 1.4931 | 245.4% | 🔴 unstable |
| AUC ROC | 0.4957 | 0.0524 | 10.6% | 🟢 stable |
| MAE | 2.1481 | 0.5006 | 23.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4905 |
| CI 95% | [0.4708, 0.5101] |
| p-value | 0.342530 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 23:08*
