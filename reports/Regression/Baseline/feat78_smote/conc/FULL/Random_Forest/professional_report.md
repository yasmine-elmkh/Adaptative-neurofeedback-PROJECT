# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 17:31


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5702 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9839 | Erreur quadratique moyenne |
| R² | 0.0718 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6272 | 0.500 |
| PR-AUC | 0.6061 | 0.517 |
| Sensitivity (TPR) | 0.6213 | 0.500 |
| Specificity (TNR) | 0.5520 | 0.500 |
| PPV (Precision) | 0.5977 | — |
| NPV | 0.5764 | — |
| Balanced Accuracy | 0.5867 | 0.500 |
| MCC | 0.1737 | 0.000 |
| G-Mean | 0.5856 | 0.500 |
| F1 macro | 0.5866 | 0.500 |
| LR+ | 1.387 | >10 = très utile |
| LR− | 0.686 | <0.1 = très utile |
| Cohen κ | 0.1735 | 0.000 |
| Brier Score | 0.2815 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6276 | [0.6134, 0.6408]  ✅ |
| F1 macro | 0.5869 | [0.5745, 0.6002]  ✅ |
| Sensitivity | 0.6219 | [0.6044, 0.6382]  — |
| Specificity | 0.5521 | [0.5331, 0.5687]  — |
| MCC | 0.1744 | [0.1497, 0.2007]  — |
| R² | 0.0719 | [0.0525, 0.0922]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0718 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6272 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1952 | < 0.05 |
| MCE | 0.3079 | < 0.10 |
| Brier Score | 0.2815 | < 0.20 |
| Log-Loss | 0.8445 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0005 | proche 0 = pas de biais systématique |
| LoA lower | -5.8496 | limite inférieure d'accord |
| LoA upper | +5.8485 | limite supérieure d'accord |
| LoA width | ±5.8490 | < ±2 pts : excellent |
| % dans LoA | 98.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1703 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0159 | 0.2606 | 1641.8% | 🔴 unstable |
| AUC ROC | 0.6254 | 0.1144 | 18.3% | 🟡 moderate |
| MAE | 2.5666 | 0.2716 | 10.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6249 |
| CI 95% | [0.6105, 0.6394] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:31*
