# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 18:13


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7108 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1997 | Erreur quadratique moyenne |
| R² | -0.0673 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5815 | 0.500 |
| PR-AUC | 0.5786 | 0.519 |
| Sensitivity (TPR) | 0.6521 | 0.500 |
| Specificity (TNR) | 0.4734 | 0.500 |
| PPV (Precision) | 0.5716 | — |
| NPV | 0.5581 | — |
| Balanced Accuracy | 0.5627 | 0.500 |
| MCC | 0.1275 | 0.000 |
| G-Mean | 0.5556 | 0.500 |
| F1 macro | 0.5607 | 0.500 |
| LR+ | 1.238 | >10 = très utile |
| LR− | 0.735 | <0.1 = très utile |
| Cohen κ | 0.1261 | 0.000 |
| Brier Score | 0.3135 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5801 | [0.5661, 0.5947]  ✅ |
| F1 macro | 0.5214 | [0.5087, 0.5342]  ✅ |
| Sensitivity | 0.3532 | [0.3361, 0.3710]  — |
| Specificity | 0.7293 | [0.7129, 0.7457]  — |
| MCC | 0.0889 | [0.0637, 0.1143]  — |
| R² | -0.0675 | [-0.0963, -0.0398]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0673 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5801 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2671 | < 0.05 |
| MCE | 0.3908 | < 0.10 |
| Brier Score | 0.3305 | < 0.20 |
| Log-Loss | 1.1080 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1886 | proche 0 = pas de biais systématique |
| LoA lower | -6.4498 | limite inférieure d'accord |
| LoA upper | +6.0725 | limite supérieure d'accord |
| LoA width | ±6.2611 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0169 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1303 | 0.2357 | 180.9% | 🔴 unstable |
| AUC ROC | 0.6010 | 0.0970 | 16.1% | 🟡 moderate |
| MAE | 2.7210 | 0.2353 | 8.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5801 |
| CI 95% | [0.5653, 0.5948] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.57


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:13*
