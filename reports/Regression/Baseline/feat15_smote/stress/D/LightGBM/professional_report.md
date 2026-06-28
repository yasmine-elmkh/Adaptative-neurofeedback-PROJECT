# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `D`  |  **Date :** 2026-06-21 19:28


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3024 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7571 | Erreur quadratique moyenne |
| R² | -0.3410 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4413 | 0.500 |
| PR-AUC | 0.3658 | 0.414 |
| Sensitivity (TPR) | 0.2998 | 0.500 |
| Specificity (TNR) | 0.6389 | 0.500 |
| PPV (Precision) | 0.3695 | — |
| NPV | 0.5637 | — |
| Balanced Accuracy | 0.4693 | 0.500 |
| MCC | -0.0640 | 0.000 |
| G-Mean | 0.4376 | 0.500 |
| F1 macro | 0.4650 | 0.500 |
| LR+ | 0.830 | >10 = très utile |
| LR− | 1.096 | <0.1 = très utile |
| Cohen κ | -0.0631 | 0.000 |
| Brier Score | 0.3365 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4412 | [0.4234, 0.4579]  — |
| F1 macro | 0.4646 | [0.4499, 0.4788]  — |
| Sensitivity | 0.2994 | [0.2766, 0.3203]  — |
| Specificity | 0.6387 | [0.6188, 0.6579]  — |
| MCC | -0.0646 | [-0.0932, -0.0353]  — |
| R² | -0.3417 | [-0.3767, -0.3058]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3410 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4413 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2502 | < 0.05 |
| MCE | 0.7494 | < 0.10 |
| Brier Score | 0.3365 | < 0.20 |
| Log-Loss | 0.9905 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4633 | proche 0 = pas de biais systématique |
| LoA lower | -4.8645 | limite inférieure d'accord |
| LoA upper | +5.7911 | limite supérieure d'accord |
| LoA width | ±5.3278 | < ±2 pts : excellent |
| % dans LoA | 96.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0016 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.1941 | 3.7323 | 312.6% | 🔴 unstable |
| AUC ROC | 0.4929 | 0.0885 | 18.0% | 🟡 moderate |
| MAE | 2.3022 | 0.6955 | 30.2% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4273 |
| CI 95% | [0.4078, 0.4467] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:28*
