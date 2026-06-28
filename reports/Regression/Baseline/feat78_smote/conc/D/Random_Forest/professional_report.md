# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `D`  |  **Date :** 2026-06-21 17:00


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5584 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0167 | Erreur quadratique moyenne |
| R² | 0.0514 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6128 | 0.500 |
| PR-AUC | 0.6083 | 0.517 |
| Sensitivity (TPR) | 0.5999 | 0.500 |
| Specificity (TNR) | 0.5320 | 0.500 |
| PPV (Precision) | 0.5786 | — |
| NPV | 0.5538 | — |
| Balanced Accuracy | 0.5659 | 0.500 |
| MCC | 0.1322 | 0.000 |
| G-Mean | 0.5649 | 0.500 |
| F1 macro | 0.5659 | 0.500 |
| LR+ | 1.282 | >10 = très utile |
| LR− | 0.752 | <0.1 = très utile |
| Cohen κ | 0.1321 | 0.000 |
| Brier Score | 0.2955 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6126 | [0.5913, 0.6348]  ✅ |
| F1 macro | 0.5657 | [0.5469, 0.5835]  ✅ |
| Sensitivity | 0.5993 | [0.5732, 0.6243]  — |
| Specificity | 0.5325 | [0.5043, 0.5582]  — |
| MCC | 0.1320 | [0.0941, 0.1672]  — |
| R² | 0.0506 | [0.0191, 0.0815]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0514 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6128 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2237 | < 0.05 |
| MCE | 0.3651 | < 0.10 |
| Brier Score | 0.2955 | < 0.20 |
| Log-Loss | 0.8862 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0185 | proche 0 = pas de biais systématique |
| LoA lower | -5.9321 | limite inférieure d'accord |
| LoA upper | +5.8951 | limite supérieure d'accord |
| LoA width | ±5.9136 | < ±2 pts : excellent |
| % dans LoA | 98.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1659 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0074 | 0.2638 | 3551.9% | 🔴 unstable |
| AUC ROC | 0.5992 | 0.1011 | 16.9% | 🟡 moderate |
| MAE | 2.5737 | 0.3547 | 13.8% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6104 |
| CI 95% | [0.5898, 0.6310] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:00*
