# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 16:55


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5197 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9546 | Erreur quadratique moyenne |
| R² | 0.0900 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6435 | 0.500 |
| PR-AUC | 0.6319 | 0.528 |
| Sensitivity (TPR) | 0.8309 | 0.500 |
| Specificity (TNR) | 0.3969 | 0.500 |
| PPV (Precision) | 0.6063 | — |
| NPV | 0.6775 | — |
| Balanced Accuracy | 0.6139 | 0.500 |
| MCC | 0.2543 | 0.000 |
| G-Mean | 0.5743 | 0.500 |
| F1 macro | 0.6008 | 0.500 |
| LR+ | 1.378 | >10 = très utile |
| LR− | 0.426 | <0.1 = très utile |
| Cohen κ | 0.2329 | 0.000 |
| Brier Score | 0.2827 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6370 | [0.6233, 0.6501]  ✅ |
| F1 macro | 0.5545 | [0.5413, 0.5664]  ✅ |
| Sensitivity | 0.4066 | [0.3890, 0.4226]  — |
| Specificity | 0.7312 | [0.7152, 0.7475]  — |
| MCC | 0.1453 | [0.1217, 0.1688]  — |
| R² | 0.0902 | [0.0693, 0.1118]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0900 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6369 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2233 | < 0.05 |
| MCE | 0.3947 | < 0.10 |
| Brier Score | 0.2961 | < 0.20 |
| Log-Loss | 0.9089 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0282 | proche 0 = pas de biais systématique |
| LoA lower | -5.8195 | limite inférieure d'accord |
| LoA upper | +5.7631 | limite supérieure d'accord |
| LoA width | ±5.7913 | < ±2 pts : excellent |
| % dans LoA | 97.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1622 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0479 | 0.1471 | 307.3% | 🔴 unstable |
| AUC ROC | 0.6521 | 0.0631 | 9.7% | 🟢 stable |
| MAE | 2.5268 | 0.2329 | 9.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6369 |
| CI 95% | [0.6225, 0.6513] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:55*
