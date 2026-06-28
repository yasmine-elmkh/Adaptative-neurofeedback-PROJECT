# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 17:33


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5387 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9608 | Erreur quadratique moyenne |
| R² | 0.0862 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6354 | 0.500 |
| PR-AUC | 0.6158 | 0.517 |
| Sensitivity (TPR) | 0.5160 | 0.500 |
| Specificity (TNR) | 0.6450 | 0.500 |
| PPV (Precision) | 0.6083 | — |
| NPV | 0.5550 | — |
| Balanced Accuracy | 0.5805 | 0.500 |
| MCC | 0.1621 | 0.000 |
| G-Mean | 0.5769 | 0.500 |
| F1 macro | 0.5775 | 0.500 |
| LR+ | 1.453 | >10 = très utile |
| LR− | 0.750 | <0.1 = très utile |
| Cohen κ | 0.1601 | 0.000 |
| Brier Score | 0.2886 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6356 | [0.6215, 0.6497]  ✅ |
| F1 macro | 0.5776 | [0.5645, 0.5908]  ✅ |
| Sensitivity | 0.5161 | [0.4980, 0.5333]  — |
| Specificity | 0.6453 | [0.6283, 0.6620]  — |
| MCC | 0.1626 | [0.1364, 0.1887]  — |
| R² | 0.0863 | [0.0652, 0.1079]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0862 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6354 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2175 | < 0.05 |
| MCE | 0.3695 | < 0.10 |
| Brier Score | 0.2886 | < 0.20 |
| Log-Loss | 0.8710 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0692 | proche 0 = pas de biais systématique |
| LoA lower | -5.8712 | limite inférieure d'accord |
| LoA upper | +5.7328 | limite supérieure d'accord |
| LoA width | ±5.8020 | < ±2 pts : excellent |
| % dans LoA | 98.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1011 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0335 | 0.2282 | 681.9% | 🔴 unstable |
| AUC ROC | 0.6345 | 0.0937 | 14.8% | 🟢 stable |
| MAE | 2.5326 | 0.2297 | 9.1% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6341 |
| CI 95% | [0.6198, 0.6485] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:33*
