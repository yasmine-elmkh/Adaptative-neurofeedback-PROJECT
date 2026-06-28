# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:38


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5753 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0223 | Erreur quadratique moyenne |
| R² | 0.0478 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6121 | 0.500 |
| PR-AUC | 0.5879 | 0.517 |
| Sensitivity (TPR) | 0.6067 | 0.500 |
| Specificity (TNR) | 0.5539 | 0.500 |
| PPV (Precision) | 0.5930 | — |
| NPV | 0.5679 | — |
| Balanced Accuracy | 0.5803 | 0.500 |
| MCC | 0.1607 | 0.000 |
| G-Mean | 0.5797 | 0.500 |
| F1 macro | 0.5803 | 0.500 |
| LR+ | 1.360 | >10 = très utile |
| LR− | 0.710 | <0.1 = très utile |
| Cohen κ | 0.1606 | 0.000 |
| Brier Score | 0.2890 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6123 | [0.5910, 0.6314]  ✅ |
| F1 macro | 0.5804 | [0.5623, 0.5966]  ✅ |
| Sensitivity | 0.6068 | [0.5825, 0.6331]  — |
| Specificity | 0.5541 | [0.5265, 0.5775]  — |
| MCC | 0.1611 | [0.1251, 0.1935]  — |
| R² | 0.0478 | [0.0206, 0.0781]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0478 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6121 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1989 | < 0.05 |
| MCE | 0.3232 | < 0.10 |
| Brier Score | 0.2890 | < 0.20 |
| Log-Loss | 0.8671 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0474 | proche 0 = pas de biais systématique |
| LoA lower | -5.9714 | limite inférieure d'accord |
| LoA upper | +5.8766 | limite supérieure d'accord |
| LoA width | ±5.9240 | < ±2 pts : excellent |
| % dans LoA | 97.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1268 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0030 | 0.2002 | 6730.6% | 🔴 unstable |
| AUC ROC | 0.6103 | 0.0739 | 12.1% | 🟢 stable |
| MAE | 2.5882 | 0.2909 | 11.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6113 |
| CI 95% | [0.5907, 0.6320] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:38*
