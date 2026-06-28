# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:08


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7876 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1086 | Erreur quadratique moyenne |
| R² | -0.0073 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5201 | 0.500 |
| PR-AUC | 0.5240 | 0.519 |
| Sensitivity (TPR) | 0.8863 | 0.500 |
| Specificity (TNR) | 0.1827 | 0.500 |
| PPV (Precision) | 0.5395 | — |
| NPV | 0.5981 | — |
| Balanced Accuracy | 0.5345 | 0.500 |
| MCC | 0.0975 | 0.000 |
| G-Mean | 0.4025 | 0.500 |
| F1 macro | 0.4754 | 0.500 |
| LR+ | 1.085 | >10 = très utile |
| LR− | 0.622 | <0.1 = très utile |
| Cohen κ | 0.0709 | 0.000 |
| Brier Score | 0.2802 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5170 | [0.4879, 0.5470]  — |
| F1 macro | 0.3629 | [0.3428, 0.3825]  — |
| Sensitivity | 0.0548 | [0.0384, 0.0714]  — |
| Specificity | 0.9192 | [0.8972, 0.9404]  — |
| MCC | -0.0517 | [-0.1087, -0.0023]  — |
| R² | -0.0074 | [-0.0231, 0.0098]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0073 | p=0.0380 | ✅ p<0.05 |
| AUC ROC | 0.5163 | p=0.1440 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2578 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3198 | < 0.20 |
| Log-Loss | 0.8725 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0160 | proche 0 = pas de biais systématique |
| LoA lower | -6.1109 | limite inférieure d'accord |
| LoA upper | +6.0788 | limite supérieure d'accord |
| LoA width | ±6.0948 | < ±2 pts : excellent |
| % dans LoA | 99.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0104 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0477 | 0.0807 | 169.2% | 🔴 unstable |
| AUC ROC | 0.5180 | 0.0452 | 8.7% | 🟢 stable |
| MAE | 2.7874 | 0.2630 | 9.4% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5163 |
| CI 95% | [0.4862, 0.5464] |
| p-value | 0.288561 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.74 et 0.80


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:08*
