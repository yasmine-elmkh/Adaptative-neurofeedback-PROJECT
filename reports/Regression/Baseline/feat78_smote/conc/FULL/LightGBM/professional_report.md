# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 17:34


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5446 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9773 | Erreur quadratique moyenne |
| R² | 0.0760 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6353 | 0.500 |
| PR-AUC | 0.6139 | 0.517 |
| Sensitivity (TPR) | 0.5163 | 0.500 |
| Specificity (TNR) | 0.6595 | 0.500 |
| PPV (Precision) | 0.6183 | — |
| NPV | 0.5607 | — |
| Balanced Accuracy | 0.5879 | 0.500 |
| MCC | 0.1774 | 0.000 |
| G-Mean | 0.5835 | 0.500 |
| F1 macro | 0.5844 | 0.500 |
| LR+ | 1.516 | >10 = très utile |
| LR− | 0.733 | <0.1 = très utile |
| Cohen κ | 0.1749 | 0.000 |
| Brier Score | 0.2896 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6354 | [0.6218, 0.6490]  ✅ |
| F1 macro | 0.5844 | [0.5717, 0.5964]  ✅ |
| Sensitivity | 0.5165 | [0.4973, 0.5354]  — |
| Specificity | 0.6593 | [0.6400, 0.6750]  — |
| MCC | 0.1774 | [0.1520, 0.2016]  — |
| R² | 0.0760 | [0.0550, 0.0992]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0760 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6353 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2180 | < 0.05 |
| MCE | 0.3942 | < 0.10 |
| Brier Score | 0.2896 | < 0.20 |
| Log-Loss | 0.8896 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0390 | proche 0 = pas de biais systématique |
| LoA lower | -5.8744 | limite inférieure d'accord |
| LoA upper | +5.7964 | limite supérieure d'accord |
| LoA width | ±5.8354 | < ±2 pts : excellent |
| % dans LoA | 98.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1503 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0221 | 0.2424 | 1097.8% | 🔴 unstable |
| AUC ROC | 0.6348 | 0.1117 | 17.6% | 🟡 moderate |
| MAE | 2.5386 | 0.2377 | 9.4% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6339 |
| CI 95% | [0.6195, 0.6483] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:34*
