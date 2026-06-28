# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `A`  |  **Date :** 2026-06-21 18:02


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1565 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5657 | Erreur quadratique moyenne |
| R² | -0.1612 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5329 | 0.500 |
| PR-AUC | 0.4506 | 0.414 |
| Sensitivity (TPR) | 0.2698 | 0.500 |
| Specificity (TNR) | 0.7756 | 0.500 |
| PPV (Precision) | 0.4592 | — |
| NPV | 0.6007 | — |
| Balanced Accuracy | 0.5227 | 0.500 |
| MCC | 0.0521 | 0.000 |
| G-Mean | 0.4574 | 0.500 |
| F1 macro | 0.5084 | 0.500 |
| LR+ | 1.202 | >10 = très utile |
| LR− | 0.941 | <0.1 = très utile |
| Cohen κ | 0.0483 | 0.000 |
| Brier Score | 0.2946 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5335 | [0.5101, 0.5577]  ✅ |
| F1 macro | 0.5090 | [0.4880, 0.5290]  — |
| Sensitivity | 0.2706 | [0.2433, 0.3003]  — |
| Specificity | 0.7762 | [0.7519, 0.7992]  — |
| MCC | 0.0537 | [0.0128, 0.0944]  — |
| R² | -0.1615 | [-0.2001, -0.1227]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1612 | p=0.0380 | ✅ p<0.05 |
| AUC ROC | 0.5329 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2033 | < 0.05 |
| MCE | 0.3754 | < 0.10 |
| Brier Score | 0.2946 | < 0.20 |
| Log-Loss | 0.8776 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2882 | proche 0 = pas de biais systématique |
| LoA lower | -4.7100 | limite inférieure d'accord |
| LoA upper | +5.2864 | limite supérieure d'accord |
| LoA width | ±4.9982 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0020 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5795 | 1.0240 | 176.7% | 🔴 unstable |
| AUC ROC | 0.5280 | 0.0553 | 10.5% | 🟢 stable |
| MAE | 2.1565 | 0.4866 | 22.6% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5148 |
| CI 95% | [0.4869, 0.5426] |
| p-value | 0.297907 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.28


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:02*
