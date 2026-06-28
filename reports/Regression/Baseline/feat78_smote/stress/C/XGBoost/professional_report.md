# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `C`  |  **Date :** 2026-06-21 20:36


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1778 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5952 | Erreur quadratique moyenne |
| R² | -0.1881 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5191 | 0.500 |
| PR-AUC | 0.4314 | 0.414 |
| Sensitivity (TPR) | 0.3417 | 0.500 |
| Specificity (TNR) | 0.6785 | 0.500 |
| PPV (Precision) | 0.4288 | — |
| NPV | 0.5934 | — |
| Balanced Accuracy | 0.5101 | 0.500 |
| MCC | 0.0212 | 0.000 |
| G-Mean | 0.4815 | 0.500 |
| F1 macro | 0.5067 | 0.500 |
| LR+ | 1.063 | >10 = très utile |
| LR− | 0.970 | <0.1 = très utile |
| Cohen κ | 0.0209 | 0.000 |
| Brier Score | 0.3005 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5184 | [0.5044, 0.5328]  ✅ |
| F1 macro | 0.5066 | [0.4952, 0.5189]  — |
| Sensitivity | 0.3416 | [0.3248, 0.3615]  — |
| Specificity | 0.6783 | [0.6619, 0.6925]  — |
| MCC | 0.0209 | [-0.0021, 0.0464]  — |
| R² | -0.1898 | [-0.2122, -0.1677]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1881 | p=0.2460 | ❌ ns |
| AUC ROC | 0.5191 | p=0.0040 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2075 | < 0.05 |
| MCE | 0.4441 | < 0.10 |
| Brier Score | 0.3005 | < 0.20 |
| Log-Loss | 0.8606 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4525 | proche 0 = pas de biais systématique |
| LoA lower | -4.5566 | limite inférieure d'accord |
| LoA upper | +5.4617 | limite supérieure d'accord |
| LoA width | ±5.0091 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5934 | 0.9864 | 166.2% | 🔴 unstable |
| AUC ROC | 0.5406 | 0.0707 | 13.1% | 🟢 stable |
| MAE | 2.1776 | 0.5657 | 26.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5093 |
| CI 95% | [0.4933, 0.5253] |
| p-value | 0.254408 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:36*
