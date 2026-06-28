# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `C`  |  **Date :** 2026-06-21 18:39


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1857 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6132 | Erreur quadratique moyenne |
| R² | -0.2046 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4891 | 0.500 |
| PR-AUC | 0.4163 | 0.414 |
| Sensitivity (TPR) | 0.1651 | 0.500 |
| Specificity (TNR) | 0.8414 | 0.500 |
| PPV (Precision) | 0.4236 | — |
| NPV | 0.5880 | — |
| Balanced Accuracy | 0.5032 | 0.500 |
| MCC | 0.0086 | 0.000 |
| G-Mean | 0.3727 | 0.500 |
| F1 macro | 0.4649 | 0.500 |
| LR+ | 1.041 | >10 = très utile |
| LR− | 0.992 | <0.1 = très utile |
| Cohen κ | 0.0071 | 0.000 |
| Brier Score | 0.3195 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4888 | [0.4748, 0.5030]  — |
| F1 macro | 0.4646 | [0.4517, 0.4771]  — |
| Sensitivity | 0.1648 | [0.1497, 0.1793]  — |
| Specificity | 0.8411 | [0.8291, 0.8521]  — |
| MCC | 0.0079 | [-0.0188, 0.0342]  — |
| R² | -0.2057 | [-0.2318, -0.1813]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2046 | p=0.8640 | ❌ ns |
| AUC ROC | 0.4891 | p=0.9000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2385 | < 0.05 |
| MCE | 0.5439 | < 0.10 |
| Brier Score | 0.3195 | < 0.20 |
| Log-Loss | 0.9731 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1906 | proche 0 = pas de biais systématique |
| LoA lower | -4.9180 | limite inférieure d'accord |
| LoA upper | +5.2992 | limite supérieure d'accord |
| LoA width | ±5.1086 | < ±2 pts : excellent |
| % dans LoA | 95.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0006 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5589 | 0.8336 | 149.2% | 🔴 unstable |
| AUC ROC | 0.4952 | 0.0452 | 9.1% | 🟢 stable |
| MAE | 2.1856 | 0.6194 | 28.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5087 |
| CI 95% | [0.4922, 0.5252] |
| p-value | 0.299934 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.31


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:39*
