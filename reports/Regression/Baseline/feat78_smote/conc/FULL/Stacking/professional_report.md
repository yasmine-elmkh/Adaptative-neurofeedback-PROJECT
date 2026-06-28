# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 17:37


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6628 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1620 | Erreur quadratique moyenne |
| R² | -0.0423 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6066 | 0.500 |
| PR-AUC | 0.5872 | 0.517 |
| Sensitivity (TPR) | 0.6321 | 0.500 |
| Specificity (TNR) | 0.5211 | 0.500 |
| PPV (Precision) | 0.5858 | — |
| NPV | 0.5694 | — |
| Balanced Accuracy | 0.5766 | 0.500 |
| MCC | 0.1542 | 0.000 |
| G-Mean | 0.5739 | 0.500 |
| F1 macro | 0.5761 | 0.500 |
| LR+ | 1.320 | >10 = très utile |
| LR− | 0.706 | <0.1 = très utile |
| Cohen κ | 0.1537 | 0.000 |
| Brier Score | 0.3073 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6069 | [0.5918, 0.6201]  ✅ |
| F1 macro | 0.5764 | [0.5631, 0.5886]  ✅ |
| Sensitivity | 0.6328 | [0.6158, 0.6498]  — |
| Specificity | 0.5210 | [0.5033, 0.5396]  — |
| MCC | 0.1548 | [0.1286, 0.1797]  — |
| R² | -0.0420 | [-0.0707, -0.0161]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0423 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6066 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2376 | < 0.05 |
| MCE | 0.3641 | < 0.10 |
| Brier Score | 0.3073 | < 0.20 |
| Log-Loss | 1.0072 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0587 | proche 0 = pas de biais systématique |
| LoA lower | -6.2558 | limite inférieure d'accord |
| LoA upper | +6.1384 | limite supérieure d'accord |
| LoA width | ±6.1971 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1104 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1062 | 0.2879 | 271.0% | 🔴 unstable |
| AUC ROC | 0.6044 | 0.1179 | 19.5% | 🟡 moderate |
| MAE | 2.6585 | 0.2911 | 11.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6046 |
| CI 95% | [0.5899, 0.6192] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.57


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:37*
