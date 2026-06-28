# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 20:33


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2637 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7254 | Erreur quadratique moyenne |
| R² | -0.3103 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4909 | 0.500 |
| PR-AUC | 0.5198 | 0.524 |
| Sensitivity (TPR) | 0.5476 | 0.500 |
| Specificity (TNR) | 0.4408 | 0.500 |
| PPV (Precision) | 0.5188 | — |
| NPV | 0.4695 | — |
| Balanced Accuracy | 0.4942 | 0.500 |
| MCC | -0.0116 | 0.000 |
| G-Mean | 0.4913 | 0.500 |
| F1 macro | 0.4938 | 0.500 |
| LR+ | 0.979 | >10 = très utile |
| LR− | 1.026 | <0.1 = très utile |
| Cohen κ | -0.0116 | 0.000 |
| Brier Score | 0.3453 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5173 | [0.5035, 0.5315]  ✅ |
| F1 macro | 0.4979 | [0.4866, 0.5089]  — |
| Sensitivity | 0.1773 | [0.1606, 0.1940]  — |
| Specificity | 0.8352 | [0.8263, 0.8440]  — |
| MCC | 0.0150 | [-0.0072, 0.0372]  — |
| R² | -0.3102 | [-0.3403, -0.2826]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3103 | p=0.5420 | ❌ ns |
| AUC ROC | 0.5173 | p=0.0040 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2196 | < 0.05 |
| MCE | 0.6435 | < 0.10 |
| Brier Score | 0.2692 | < 0.20 |
| Log-Loss | 0.9082 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1087 | proche 0 = pas de biais systématique |
| LoA lower | -5.2292 | limite inférieure d'accord |
| LoA upper | +5.4466 | limite supérieure d'accord |
| LoA width | ±5.3379 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7482 | 0.9773 | 130.6% | 🔴 unstable |
| AUC ROC | 0.5324 | 0.0553 | 10.4% | 🟢 stable |
| MAE | 2.2637 | 0.5253 | 23.2% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5173 |
| CI 95% | [0.5032, 0.5313] |
| p-value | 0.016272 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.30


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:33*
