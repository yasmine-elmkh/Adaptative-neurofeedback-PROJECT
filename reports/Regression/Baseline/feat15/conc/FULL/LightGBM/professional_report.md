# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 16:56


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5724 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0123 | Erreur quadratique moyenne |
| R² | 0.0541 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6255 | 0.500 |
| PR-AUC | 0.6269 | 0.540 |
| Sensitivity (TPR) | 0.8667 | 0.500 |
| Specificity (TNR) | 0.3310 | 0.500 |
| PPV (Precision) | 0.6037 | — |
| NPV | 0.6787 | — |
| Balanced Accuracy | 0.5989 | 0.500 |
| MCC | 0.2363 | 0.000 |
| G-Mean | 0.5356 | 0.500 |
| F1 macro | 0.5784 | 0.500 |
| LR+ | 1.296 | >10 = très utile |
| LR− | 0.403 | <0.1 = très utile |
| Cohen κ | 0.2056 | 0.000 |
| Brier Score | 0.2939 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6185 | [0.6036, 0.6329]  ✅ |
| F1 macro | 0.5491 | [0.5359, 0.5625]  ✅ |
| Sensitivity | 0.4199 | [0.4009, 0.4381]  — |
| Specificity | 0.7007 | [0.6822, 0.7190]  — |
| MCC | 0.1255 | [0.0973, 0.1508]  — |
| R² | 0.0546 | [0.0324, 0.0764]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0541 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6183 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2352 | < 0.05 |
| MCE | 0.3903 | < 0.10 |
| Brier Score | 0.3013 | < 0.20 |
| Log-Loss | 0.9212 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0359 | proche 0 = pas de biais systématique |
| LoA lower | -5.8682 | limite inférieure d'accord |
| LoA upper | +5.9401 | limite supérieure d'accord |
| LoA width | ±5.9041 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1331 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0082 | 0.1749 | 2134.4% | 🔴 unstable |
| AUC ROC | 0.6209 | 0.0682 | 11.0% | 🟢 stable |
| MAE | 2.5792 | 0.2481 | 9.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6183 |
| CI 95% | [0.6037, 0.6328] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:56*
