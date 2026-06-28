# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 23:13


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3248 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7989 | Erreur quadratique moyenne |
| R² | -0.3819 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4930 | 0.500 |
| PR-AUC | 0.5390 | 0.546 |
| Sensitivity (TPR) | 0.8134 | 0.500 |
| Specificity (TNR) | 0.1871 | 0.500 |
| PPV (Precision) | 0.5465 | — |
| NPV | 0.4542 | — |
| Balanced Accuracy | 0.5002 | 0.500 |
| MCC | 0.0006 | 0.000 |
| G-Mean | 0.3901 | 0.500 |
| F1 macro | 0.4594 | 0.500 |
| LR+ | 1.001 | >10 = très utile |
| LR− | 0.998 | <0.1 = très utile |
| Cohen κ | 0.0005 | 0.000 |
| Brier Score | 0.3615 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4941 | [0.4818, 0.5071]  — |
| F1 macro | 0.4951 | [0.4842, 0.5051]  — |
| Sensitivity | 0.2760 | [0.2588, 0.2935]  — |
| Specificity | 0.7142 | [0.7031, 0.7255]  — |
| MCC | -0.0098 | [-0.0317, 0.0102]  — |
| R² | -0.3829 | [-0.4128, -0.3569]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3819 | p=0.9540 | ❌ ns |
| AUC ROC | 0.4948 | p=0.7400 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2463 | < 0.05 |
| MCE | 0.7076 | < 0.10 |
| Brier Score | 0.2915 | < 0.20 |
| Log-Loss | 0.9221 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5296 | proche 0 = pas de biais systématique |
| LoA lower | -4.8575 | limite inférieure d'accord |
| LoA upper | +5.9167 | limite supérieure d'accord |
| LoA width | ±5.3871 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.0356 | 1.9197 | 185.4% | 🔴 unstable |
| AUC ROC | 0.4981 | 0.0534 | 10.7% | 🟢 stable |
| MAE | 2.3246 | 0.4367 | 18.8% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4948 |
| CI 95% | [0.4809, 0.5087] |
| p-value | 0.460670 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 23:13*
