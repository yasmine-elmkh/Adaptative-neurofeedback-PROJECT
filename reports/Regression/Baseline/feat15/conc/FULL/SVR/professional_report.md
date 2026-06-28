# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 16:40


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5943 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1311 | Erreur quadratique moyenne |
| R² | -0.0220 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6241 | 0.500 |
| PR-AUC | 0.6172 | 0.519 |
| Sensitivity (TPR) | 0.7171 | 0.500 |
| Specificity (TNR) | 0.4763 | 0.500 |
| PPV (Precision) | 0.5960 | — |
| NPV | 0.6098 | — |
| Balanced Accuracy | 0.5967 | 0.500 |
| MCC | 0.1995 | 0.000 |
| G-Mean | 0.5844 | 0.500 |
| F1 macro | 0.5929 | 0.500 |
| LR+ | 1.369 | >10 = très utile |
| LR− | 0.594 | <0.1 = très utile |
| Cohen κ | 0.1950 | 0.000 |
| Brier Score | 0.3042 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6229 | [0.6096, 0.6371]  ✅ |
| F1 macro | 0.5570 | [0.5446, 0.5690]  ✅ |
| Sensitivity | 0.4547 | [0.4366, 0.4732]  — |
| Specificity | 0.6737 | [0.6551, 0.6904]  — |
| MCC | 0.1314 | [0.1070, 0.1551]  — |
| R² | -0.0216 | [-0.0495, 0.0097]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0220 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6226 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2565 | < 0.05 |
| MCE | 0.3633 | < 0.10 |
| Brier Score | 0.3135 | < 0.20 |
| Log-Loss | 1.0559 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0069 | proche 0 = pas de biais systématique |
| LoA lower | -6.1444 | limite inférieure d'accord |
| LoA upper | +6.1307 | limite supérieure d'accord |
| LoA width | ±6.1375 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1781 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0759 | 0.2144 | 282.5% | 🔴 unstable |
| AUC ROC | 0.6504 | 0.0981 | 15.1% | 🟡 moderate |
| MAE | 2.6043 | 0.2607 | 10.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6226 |
| CI 95% | [0.6082, 0.6371] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:40*
