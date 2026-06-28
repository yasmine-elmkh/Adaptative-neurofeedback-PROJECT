# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 20:47


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
| AUC ROC | 0.5203 | 0.500 |
| PR-AUC | 0.2715 | 0.257 |
| Sensitivity (TPR) | 0.1467 | 0.500 |
| Specificity (TNR) | 0.8778 | 0.500 |
| PPV (Precision) | 0.2934 | — |
| NPV | 0.7483 | — |
| Balanced Accuracy | 0.5122 | 0.500 |
| MCC | 0.0320 | 0.000 |
| G-Mean | 0.3589 | 0.500 |
| F1 macro | 0.5017 | 0.500 |
| LR+ | 1.200 | >10 = très utile |
| LR− | 0.972 | <0.1 = très utile |
| Cohen κ | 0.0293 | 0.000 |
| Brier Score | 0.2491 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5203 | [0.5048, 0.5350]  ✅ |
| F1 macro | 0.5014 | [0.4906, 0.5119]  — |
| Sensitivity | 0.1462 | [0.1306, 0.1608]  — |
| Specificity | 0.8778 | [0.8699, 0.8859]  — |
| MCC | 0.0313 | [0.0092, 0.0530]  — |
| R² | -0.3102 | [-0.3403, -0.2826]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3103 | p=0.5420 | ❌ ns |
| AUC ROC | 0.5203 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2080 | < 0.05 |
| MCE | 0.6489 | < 0.10 |
| Brier Score | 0.2491 | < 0.20 |
| Log-Loss | 0.8781 | minimiser |

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
| AUC ROC | 0.5211 | 0.0714 | 13.7% | 🟢 stable |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:47*
