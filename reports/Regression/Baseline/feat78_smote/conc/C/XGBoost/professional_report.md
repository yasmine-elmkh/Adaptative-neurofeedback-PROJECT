# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:44


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5051 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9347 | Erreur quadratique moyenne |
| R² | 0.1022 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6550 | 0.500 |
| PR-AUC | 0.6355 | 0.517 |
| Sensitivity (TPR) | 0.5710 | 0.500 |
| Specificity (TNR) | 0.6371 | 0.500 |
| PPV (Precision) | 0.6270 | — |
| NPV | 0.5816 | — |
| Balanced Accuracy | 0.6040 | 0.500 |
| MCC | 0.2083 | 0.000 |
| G-Mean | 0.6031 | 0.500 |
| F1 macro | 0.6029 | 0.500 |
| LR+ | 1.573 | >10 = très utile |
| LR− | 0.673 | <0.1 = très utile |
| Cohen κ | 0.2075 | 0.000 |
| Brier Score | 0.2722 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6549 | [0.6391, 0.6706]  ✅ |
| F1 macro | 0.6028 | [0.5884, 0.6169]  ✅ |
| Sensitivity | 0.5711 | [0.5517, 0.5906]  — |
| Specificity | 0.6369 | [0.6142, 0.6583]  — |
| MCC | 0.2082 | [0.1798, 0.2373]  — |
| R² | 0.1019 | [0.0784, 0.1271]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1022 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6550 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1847 | < 0.05 |
| MCE | 0.2796 | < 0.10 |
| Brier Score | 0.2722 | < 0.20 |
| Log-Loss | 0.8292 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0429 | proche 0 = pas de biais systématique |
| LoA lower | -5.7091 | limite inférieure d'accord |
| LoA upper | +5.7949 | limite supérieure d'accord |
| LoA width | ±5.7520 | < ±2 pts : excellent |
| % dans LoA | 98.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1591 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0536 | 0.1884 | 351.2% | 🔴 unstable |
| AUC ROC | 0.6586 | 0.0973 | 14.8% | 🟢 stable |
| MAE | 2.5030 | 0.2143 | 8.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6542 |
| CI 95% | [0.6379, 0.6706] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.44 et 0.66


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:44*
