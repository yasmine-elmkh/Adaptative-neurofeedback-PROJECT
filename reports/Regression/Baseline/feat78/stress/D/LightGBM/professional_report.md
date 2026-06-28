# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `D`  |  **Date :** 2026-06-21 23:00


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1545 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5446 | Erreur quadratique moyenne |
| R² | -0.1422 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5048 | 0.500 |
| PR-AUC | 0.4486 | 0.442 |
| Sensitivity (TPR) | 0.6843 | 0.500 |
| Specificity (TNR) | 0.3396 | 0.500 |
| PPV (Precision) | 0.4504 | — |
| NPV | 0.5762 | — |
| Balanced Accuracy | 0.5119 | 0.500 |
| MCC | 0.0252 | 0.000 |
| G-Mean | 0.4820 | 0.500 |
| F1 macro | 0.4853 | 0.500 |
| LR+ | 1.036 | >10 = très utile |
| LR− | 0.930 | <0.1 = très utile |
| Cohen κ | 0.0226 | 0.000 |
| Brier Score | 0.3147 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5062 | [0.4853, 0.5243]  — |
| F1 macro | 0.4870 | [0.4719, 0.5021]  — |
| Sensitivity | 0.1528 | [0.1316, 0.1751]  — |
| Specificity | 0.8459 | [0.8330, 0.8586]  — |
| MCC | -0.0016 | [-0.0340, 0.0303]  — |
| R² | -0.1425 | [-0.1684, -0.1175]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1422 | p=0.0660 | ❌ ns |
| AUC ROC | 0.5061 | p=0.2720 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1576 | < 0.05 |
| MCE | 0.5353 | < 0.10 |
| Brier Score | 0.2372 | < 0.20 |
| Log-Loss | 0.6988 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5769 | proche 0 = pas de biais systématique |
| LoA lower | -4.2812 | limite inférieure d'accord |
| LoA upper | +5.4349 | limite supérieure d'accord |
| LoA width | ±4.8581 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6602 | 1.6040 | 243.0% | 🔴 unstable |
| AUC ROC | 0.5289 | 0.0762 | 14.4% | 🟢 stable |
| MAE | 2.1544 | 0.4784 | 22.2% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5061 |
| CI 95% | [0.4864, 0.5258] |
| p-value | 0.542841 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 23:00*
