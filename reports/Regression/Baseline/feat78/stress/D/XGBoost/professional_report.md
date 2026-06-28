# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `D`  |  **Date :** 2026-06-21 22:56


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1410 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5326 | Erreur quadratique moyenne |
| R² | -0.1314 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5065 | 0.500 |
| PR-AUC | 0.5306 | 0.527 |
| Sensitivity (TPR) | 0.9067 | 0.500 |
| Specificity (TNR) | 0.1184 | 0.500 |
| PPV (Precision) | 0.5336 | — |
| NPV | 0.5330 | — |
| Balanced Accuracy | 0.5126 | 0.500 |
| MCC | 0.0409 | 0.000 |
| G-Mean | 0.3277 | 0.500 |
| F1 macro | 0.4328 | 0.500 |
| LR+ | 1.029 | >10 = très utile |
| LR− | 0.788 | <0.1 = très utile |
| Cohen κ | 0.0262 | 0.000 |
| Brier Score | 0.3272 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4911 | [0.4720, 0.5117]  — |
| F1 macro | 0.4827 | [0.4688, 0.4979]  — |
| Sensitivity | 0.1270 | [0.1105, 0.1472]  — |
| Specificity | 0.8760 | [0.8638, 0.8879]  — |
| MCC | 0.0041 | [-0.0246, 0.0351]  — |
| R² | -0.1320 | [-0.1556, -0.1081]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1314 | p=0.3960 | ❌ ns |
| AUC ROC | 0.4913 | p=0.7840 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1539 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2358 | < 0.20 |
| Log-Loss | 0.6994 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5103 | proche 0 = pas de biais systématique |
| LoA lower | -4.3523 | limite inférieure d'accord |
| LoA upper | +5.3729 | limite supérieure d'accord |
| LoA width | ±4.8626 | < ±2 pts : excellent |
| % dans LoA | 97.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6311 | 1.5650 | 248.0% | 🔴 unstable |
| AUC ROC | 0.5065 | 0.0608 | 12.0% | 🟢 stable |
| MAE | 2.1409 | 0.4942 | 23.1% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4913 |
| CI 95% | [0.4715, 0.5110] |
| p-value | 0.385527 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 22:56*
