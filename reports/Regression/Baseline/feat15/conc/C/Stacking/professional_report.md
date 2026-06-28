# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:28


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
| Sensitivity (TPR) | 0.6390 | 0.500 |
| Specificity (TNR) | 0.5211 | 0.500 |
| PPV (Precision) | 0.5884 | — |
| NPV | 0.5740 | — |
| Balanced Accuracy | 0.5801 | 0.500 |
| MCC | 0.1613 | 0.000 |
| G-Mean | 0.5771 | 0.500 |
| F1 macro | 0.5795 | 0.500 |
| LR+ | 1.334 | >10 = très utile |
| LR− | 0.693 | <0.1 = très utile |
| Cohen κ | 0.1606 | 0.000 |
| Brier Score | 0.3171 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6020 | [0.5846, 0.6190]  ✅ |
| F1 macro | 0.5554 | [0.5410, 0.5706]  ✅ |
| Sensitivity | 0.4495 | [0.4285, 0.4721]  — |
| Specificity | 0.6766 | [0.6548, 0.6966]  — |
| MCC | 0.1293 | [0.1016, 0.1602]  — |
| R² | -0.0778 | [-0.1163, -0.0430]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0771 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6017 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2622 | < 0.05 |
| MCE | 0.3787 | < 0.10 |
| Brier Score | 0.3263 | < 0.20 |
| Log-Loss | 1.1290 | minimiser |

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
| AUC ROC | 0.5994 | 0.1102 | 18.4% | 🟡 moderate |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:28*
