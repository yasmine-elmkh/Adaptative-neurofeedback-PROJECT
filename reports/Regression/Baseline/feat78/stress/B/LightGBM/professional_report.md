# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `B`  |  **Date :** 2026-06-21 20:15


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1888 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5793 | Erreur quadratique moyenne |
| R² | -0.1736 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4822 | 0.500 |
| PR-AUC | 0.5300 | 0.540 |
| Sensitivity (TPR) | 0.9477 | 0.500 |
| Specificity (TNR) | 0.0529 | 0.500 |
| PPV (Precision) | 0.5406 | — |
| NPV | 0.4623 | — |
| Balanced Accuracy | 0.5003 | 0.500 |
| MCC | 0.0013 | 0.000 |
| G-Mean | 0.2239 | 0.500 |
| F1 macro | 0.3917 | 0.500 |
| LR+ | 1.001 | >10 = très utile |
| LR− | 0.989 | <0.1 = très utile |
| Cohen κ | 0.0006 | 0.000 |
| Brier Score | 0.3542 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4791 | [0.4599, 0.4998]  — |
| F1 macro | 0.4734 | [0.4586, 0.4885]  — |
| Sensitivity | 0.1303 | [0.1101, 0.1509]  — |
| Specificity | 0.8488 | [0.8359, 0.8608]  — |
| MCC | -0.0267 | [-0.0566, 0.0051]  — |
| R² | -0.1736 | [-0.1990, -0.1463]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1736 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4791 | p=0.9920 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1554 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2405 | < 0.20 |
| Log-Loss | 0.7102 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5851 | proche 0 = pas de biais systématique |
| LoA lower | -4.3393 | limite inférieure d'accord |
| LoA upper | +5.5094 | limite supérieure d'accord |
| LoA width | ±4.9244 | < ±2 pts : excellent |
| % dans LoA | 97.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7110 | 1.6669 | 234.4% | 🔴 unstable |
| AUC ROC | 0.4966 | 0.0548 | 11.0% | 🟢 stable |
| MAE | 2.1886 | 0.4957 | 22.6% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4791 |
| CI 95% | [0.4594, 0.4988] |
| p-value | 0.037783 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:15*
