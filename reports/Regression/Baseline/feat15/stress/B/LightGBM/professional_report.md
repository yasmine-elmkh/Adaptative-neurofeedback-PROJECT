# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `B`  |  **Date :** 2026-06-21 17:47


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2285 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6589 | Erreur quadratique moyenne |
| R² | -0.2471 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4159 | 0.500 |
| PR-AUC | 0.0598 | 0.071 |
| Sensitivity (TPR) | 0.0069 | 0.500 |
| Specificity (TNR) | 0.9965 | 0.500 |
| PPV (Precision) | 0.1333 | — |
| NPV | 0.9288 | — |
| Balanced Accuracy | 0.5017 | 0.500 |
| MCC | 0.0147 | 0.000 |
| G-Mean | 0.0832 | 0.500 |
| F1 macro | 0.4873 | 0.500 |
| LR+ | 1.999 | >10 = très utile |
| LR− | 0.997 | <0.1 = très utile |
| Cohen κ | 0.0062 | 0.000 |
| Brier Score | 0.0728 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4809 | [0.4618, 0.5008]  — |
| F1 macro | 0.4815 | [0.4656, 0.4963]  — |
| Sensitivity | 0.1597 | [0.1365, 0.1824]  — |
| Specificity | 0.8233 | [0.8084, 0.8377]  — |
| MCC | -0.0202 | [-0.0546, 0.0103]  — |
| R² | -0.2482 | [-0.2801, -0.2151]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2471 | p=0.9440 | ❌ ns |
| AUC ROC | 0.4814 | p=0.9600 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2021 | < 0.05 |
| MCE | 0.6612 | < 0.10 |
| Brier Score | 0.2654 | < 0.20 |
| Log-Loss | 0.8329 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3982 | proche 0 = pas de biais systématique |
| LoA lower | -4.7551 | limite inférieure d'accord |
| LoA upper | +5.5514 | limite supérieure d'accord |
| LoA width | ±5.1533 | < ±2 pts : excellent |
| % dans LoA | 96.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0004 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.9220 | 2.6597 | 288.5% | 🔴 unstable |
| AUC ROC | 0.5235 | 0.0756 | 14.4% | 🟢 stable |
| MAE | 2.2282 | 0.6273 | 28.2% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4814 |
| CI 95% | [0.4615, 0.5013] |
| p-value | 0.066508 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:47*
