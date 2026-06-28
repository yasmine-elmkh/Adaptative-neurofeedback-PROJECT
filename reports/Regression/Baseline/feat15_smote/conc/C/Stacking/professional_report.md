# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:30


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6709 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2144 | Erreur quadratique moyenne |
| R² | -0.0771 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6030 | 0.500 |
| PR-AUC | 0.5955 | 0.517 |
| Sensitivity (TPR) | 0.5987 | 0.500 |
| Specificity (TNR) | 0.5459 | 0.500 |
| PPV (Precision) | 0.5855 | — |
| NPV | 0.5594 | — |
| Balanced Accuracy | 0.5723 | 0.500 |
| MCC | 0.1447 | 0.000 |
| G-Mean | 0.5717 | 0.500 |
| F1 macro | 0.5723 | 0.500 |
| LR+ | 1.318 | >10 = très utile |
| LR− | 0.735 | <0.1 = très utile |
| Cohen κ | 0.1447 | 0.000 |
| Brier Score | 0.3169 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6032 | [0.5857, 0.6202]  ✅ |
| F1 macro | 0.5724 | [0.5581, 0.5880]  ✅ |
| Sensitivity | 0.5991 | [0.5793, 0.6184]  — |
| Specificity | 0.5457 | [0.5234, 0.5664]  — |
| MCC | 0.1450 | [0.1165, 0.1764]  — |
| R² | -0.0778 | [-0.1163, -0.0430]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0771 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6030 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2537 | < 0.05 |
| MCE | 0.3447 | < 0.10 |
| Brier Score | 0.3169 | < 0.20 |
| Log-Loss | 1.0670 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0533 | proche 0 = pas de biais systématique |
| LoA lower | -6.3533 | limite inférieure d'accord |
| LoA upper | +6.2468 | limite supérieure d'accord |
| LoA width | ±6.3001 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1188 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1430 | 0.2518 | 176.1% | 🔴 unstable |
| AUC ROC | 0.5980 | 0.0814 | 13.6% | 🟢 stable |
| MAE | 2.6850 | 0.2317 | 8.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6017 |
| CI 95% | [0.5848, 0.6186] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:30*
