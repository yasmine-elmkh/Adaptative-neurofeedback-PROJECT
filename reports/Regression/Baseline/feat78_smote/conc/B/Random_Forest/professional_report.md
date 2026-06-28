# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:18


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5484 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9465 | Erreur quadratique moyenne |
| R² | 0.0950 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6386 | 0.500 |
| PR-AUC | 0.6206 | 0.517 |
| Sensitivity (TPR) | 0.6236 | 0.500 |
| Specificity (TNR) | 0.5852 | 0.500 |
| PPV (Precision) | 0.6169 | — |
| NPV | 0.5920 | — |
| Balanced Accuracy | 0.6044 | 0.500 |
| MCC | 0.2089 | 0.000 |
| G-Mean | 0.6041 | 0.500 |
| F1 macro | 0.6044 | 0.500 |
| LR+ | 1.503 | >10 = très utile |
| LR− | 0.643 | <0.1 = très utile |
| Cohen κ | 0.2089 | 0.000 |
| Brier Score | 0.2729 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6385 | [0.6163, 0.6596]  ✅ |
| F1 macro | 0.6039 | [0.5854, 0.6223]  ✅ |
| Sensitivity | 0.6231 | [0.5973, 0.6468]  — |
| Specificity | 0.5848 | [0.5576, 0.6112]  — |
| MCC | 0.2080 | [0.1712, 0.2448]  — |
| R² | 0.0950 | [0.0674, 0.1243]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0950 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6386 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1821 | < 0.05 |
| MCE | 0.3161 | < 0.10 |
| Brier Score | 0.2729 | < 0.20 |
| Log-Loss | 0.8145 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0228 | proche 0 = pas de biais systématique |
| LoA lower | -5.7531 | limite inférieure d'accord |
| LoA upper | +5.7988 | limite supérieure d'accord |
| LoA width | ±5.7760 | < ±2 pts : excellent |
| % dans LoA | 98.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1664 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0444 | 0.2073 | 466.8% | 🔴 unstable |
| AUC ROC | 0.6359 | 0.0994 | 15.6% | 🟡 moderate |
| MAE | 2.5512 | 0.2370 | 9.3% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6354 |
| CI 95% | [0.6151, 0.6558] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:18*
