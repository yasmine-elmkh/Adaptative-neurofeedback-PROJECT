# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 16:58


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6669 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2060 | Erreur quadratique moyenne |
| R² | -0.0714 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6374 | 0.500 |
| PR-AUC | 0.6721 | 0.563 |
| Sensitivity (TPR) | 0.8249 | 0.500 |
| Specificity (TNR) | 0.3678 | 0.500 |
| PPV (Precision) | 0.6269 | — |
| NPV | 0.6199 | — |
| Balanced Accuracy | 0.5963 | 0.500 |
| MCC | 0.2181 | 0.000 |
| G-Mean | 0.5508 | 0.500 |
| F1 macro | 0.5870 | 0.500 |
| LR+ | 1.305 | >10 = très utile |
| LR− | 0.476 | <0.1 = très utile |
| Cohen κ | 0.2018 | 0.000 |
| Brier Score | 0.2987 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6059 | [0.5916, 0.6217]  ✅ |
| F1 macro | 0.5466 | [0.5337, 0.5599]  ✅ |
| Sensitivity | 0.4346 | [0.4186, 0.4529]  — |
| Specificity | 0.6759 | [0.6582, 0.6929]  — |
| MCC | 0.1137 | [0.0880, 0.1394]  — |
| R² | -0.0709 | [-0.1053, -0.0372]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0714 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6056 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2666 | < 0.05 |
| MCE | 0.3793 | < 0.10 |
| Brier Score | 0.3239 | < 0.20 |
| Log-Loss | 1.1217 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0771 | proche 0 = pas de biais systématique |
| LoA lower | -6.3595 | limite inférieure d'accord |
| LoA upper | +6.2053 | limite supérieure d'accord |
| LoA width | ±6.2824 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0867 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1287 | 0.2139 | 166.2% | 🔴 unstable |
| AUC ROC | 0.6049 | 0.0952 | 15.7% | 🟡 moderate |
| MAE | 2.6877 | 0.2732 | 10.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6056 |
| CI 95% | [0.5910, 0.6202] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:58*
