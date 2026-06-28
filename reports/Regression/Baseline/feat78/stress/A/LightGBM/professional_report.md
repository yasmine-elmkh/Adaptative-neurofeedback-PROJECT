# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `A`  |  **Date :** 2026-06-21 18:48


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1915 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5788 | Erreur quadratique moyenne |
| R² | -0.1731 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5029 | 0.500 |
| PR-AUC | 0.6352 | 0.637 |
| Sensitivity (TPR) | 0.9618 | 0.500 |
| Specificity (TNR) | 0.0492 | 0.500 |
| PPV (Precision) | 0.6399 | — |
| NPV | 0.4235 | — |
| Balanced Accuracy | 0.5055 | 0.500 |
| MCC | 0.0265 | 0.000 |
| G-Mean | 0.2176 | 0.500 |
| F1 macro | 0.4284 | 0.500 |
| LR+ | 1.012 | >10 = très utile |
| LR− | 0.775 | <0.1 = très utile |
| Cohen κ | 0.0137 | 0.000 |
| Brier Score | 0.2994 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4790 | [0.4513, 0.5087]  — |
| F1 macro | 0.4685 | [0.4481, 0.4889]  — |
| Sensitivity | 0.1250 | [0.0970, 0.1539]  — |
| Specificity | 0.8461 | [0.8294, 0.8643]  — |
| MCC | -0.0369 | [-0.0761, 0.0063]  — |
| R² | -0.1743 | [-0.2113, -0.1393]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1731 | p=0.8620 | ❌ ns |
| AUC ROC | 0.4798 | p=0.9220 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1770 | < 0.05 |
| MCE | 0.9181 | < 0.10 |
| Brier Score | 0.2480 | < 0.20 |
| Log-Loss | 0.7423 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4804 | proche 0 = pas de biais systématique |
| LoA lower | -4.4868 | limite inférieure d'accord |
| LoA upper | +5.4477 | limite supérieure d'accord |
| LoA width | ±4.9672 | < ±2 pts : excellent |
| % dans LoA | 96.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0004 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6951 | 1.6988 | 244.4% | 🔴 unstable |
| AUC ROC | 0.4948 | 0.0580 | 11.7% | 🟢 stable |
| MAE | 2.1913 | 0.5088 | 23.2% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4798 |
| CI 95% | [0.4522, 0.5073] |
| p-value | 0.150199 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:48*
