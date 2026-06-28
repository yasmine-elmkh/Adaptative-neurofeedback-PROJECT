# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:11


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5200 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9535 | Erreur quadratique moyenne |
| R² | 0.0907 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6405 | 0.500 |
| PR-AUC | 0.6309 | 0.521 |
| Sensitivity (TPR) | 0.7949 | 0.500 |
| Specificity (TNR) | 0.4252 | 0.500 |
| PPV (Precision) | 0.6004 | — |
| NPV | 0.6561 | — |
| Balanced Accuracy | 0.6100 | 0.500 |
| MCC | 0.2376 | 0.000 |
| G-Mean | 0.5814 | 0.500 |
| F1 macro | 0.6001 | 0.500 |
| LR+ | 1.383 | >10 = très utile |
| LR− | 0.482 | <0.1 = très utile |
| Cohen κ | 0.2232 | 0.000 |
| Brier Score | 0.2836 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6372 | [0.6172, 0.6555]  ✅ |
| F1 macro | 0.5560 | [0.5378, 0.5738]  ✅ |
| Sensitivity | 0.4067 | [0.3804, 0.4326]  — |
| Specificity | 0.7343 | [0.7118, 0.7575]  — |
| MCC | 0.1490 | [0.1134, 0.1823]  — |
| R² | 0.0911 | [0.0619, 0.1221]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0907 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6370 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2326 | < 0.05 |
| MCE | 0.3761 | < 0.10 |
| Brier Score | 0.2992 | < 0.20 |
| Log-Loss | 0.9318 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0692 | proche 0 = pas de biais systématique |
| LoA lower | -5.8574 | limite inférieure d'accord |
| LoA upper | +5.7191 | limite supérieure d'accord |
| LoA width | ±5.7882 | < ±2 pts : excellent |
| % dans LoA | 97.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1340 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0538 | 0.1581 | 293.9% | 🔴 unstable |
| AUC ROC | 0.6487 | 0.0764 | 11.8% | 🟢 stable |
| MAE | 2.5129 | 0.2149 | 8.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6370 |
| CI 95% | [0.6167, 0.6573] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:11*
