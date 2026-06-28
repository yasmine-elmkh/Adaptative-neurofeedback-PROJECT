# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:13


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5454 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9839 | Erreur quadratique moyenne |
| R² | 0.0719 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6270 | 0.500 |
| PR-AUC | 0.6080 | 0.517 |
| Sensitivity (TPR) | 0.5306 | 0.500 |
| Specificity (TNR) | 0.6294 | 0.500 |
| PPV (Precision) | 0.6047 | — |
| NPV | 0.5566 | — |
| Balanced Accuracy | 0.5800 | 0.500 |
| MCC | 0.1606 | 0.000 |
| G-Mean | 0.5779 | 0.500 |
| F1 macro | 0.5780 | 0.500 |
| LR+ | 1.432 | >10 = très utile |
| LR− | 0.746 | <0.1 = très utile |
| Cohen κ | 0.1593 | 0.000 |
| Brier Score | 0.2883 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6274 | [0.6076, 0.6462]  ✅ |
| F1 macro | 0.5782 | [0.5599, 0.5953]  ✅ |
| Sensitivity | 0.5307 | [0.5056, 0.5560]  — |
| Specificity | 0.6299 | [0.6031, 0.6556]  — |
| MCC | 0.1612 | [0.1263, 0.1954]  — |
| R² | 0.0724 | [0.0404, 0.1035]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0719 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6270 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2037 | < 0.05 |
| MCE | 0.3582 | < 0.10 |
| Brier Score | 0.2883 | < 0.20 |
| Log-Loss | 0.8788 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0829 | proche 0 = pas de biais systématique |
| LoA lower | -5.9300 | limite inférieure d'accord |
| LoA upper | +5.7643 | limite supérieure d'accord |
| LoA width | ±5.8472 | < ±2 pts : excellent |
| % dans LoA | 97.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1125 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0282 | 0.1730 | 613.4% | 🔴 unstable |
| AUC ROC | 0.6280 | 0.0836 | 13.3% | 🟢 stable |
| MAE | 2.5474 | 0.2351 | 9.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6262 |
| CI 95% | [0.6058, 0.6467] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:13*
