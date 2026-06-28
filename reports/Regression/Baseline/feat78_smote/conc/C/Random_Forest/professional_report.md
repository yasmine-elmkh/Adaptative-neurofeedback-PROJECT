# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:42


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5232 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9309 | Erreur quadratique moyenne |
| R² | 0.1045 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6448 | 0.500 |
| PR-AUC | 0.6328 | 0.517 |
| Sensitivity (TPR) | 0.6268 | 0.500 |
| Specificity (TNR) | 0.5803 | 0.500 |
| PPV (Precision) | 0.6154 | — |
| NPV | 0.5921 | — |
| Balanced Accuracy | 0.6036 | 0.500 |
| MCC | 0.2073 | 0.000 |
| G-Mean | 0.6031 | 0.500 |
| F1 macro | 0.6036 | 0.500 |
| LR+ | 1.493 | >10 = très utile |
| LR− | 0.643 | <0.1 = très utile |
| Cohen κ | 0.2072 | 0.000 |
| Brier Score | 0.2722 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6447 | [0.6283, 0.6608]  ✅ |
| F1 macro | 0.6032 | [0.5887, 0.6181]  ✅ |
| Sensitivity | 0.6267 | [0.6071, 0.6469]  — |
| Specificity | 0.5797 | [0.5606, 0.6002]  — |
| MCC | 0.2066 | [0.1778, 0.2365]  — |
| R² | 0.1045 | [0.0808, 0.1287]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1045 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6448 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1830 | < 0.05 |
| MCE | 0.3039 | < 0.10 |
| Brier Score | 0.2722 | < 0.20 |
| Log-Loss | 0.8151 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0432 | proche 0 = pas de biais systématique |
| LoA lower | -5.7015 | limite inférieure d'accord |
| LoA upper | +5.7879 | limite supérieure d'accord |
| LoA width | ±5.7447 | < ±2 pts : excellent |
| % dans LoA | 98.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1540 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0492 | 0.2392 | 486.0% | 🔴 unstable |
| AUC ROC | 0.6399 | 0.1239 | 19.4% | 🟡 moderate |
| MAE | 2.5231 | 0.2426 | 9.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6423 |
| CI 95% | [0.6258, 0.6587] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.44 et 0.64


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:42*
