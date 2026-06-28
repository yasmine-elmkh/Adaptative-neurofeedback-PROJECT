# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 17:09


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5245 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0584 | Erreur quadratique moyenne |
| R² | 0.0250 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6583 | 0.500 |
| PR-AUC | 0.6468 | 0.518 |
| Sensitivity (TPR) | 0.6499 | 0.500 |
| Specificity (TNR) | 0.5802 | 0.500 |
| PPV (Precision) | 0.6245 | — |
| NPV | 0.6067 | — |
| Balanced Accuracy | 0.6151 | 0.500 |
| MCC | 0.2307 | 0.000 |
| G-Mean | 0.6141 | 0.500 |
| F1 macro | 0.6151 | 0.500 |
| LR+ | 1.548 | >10 = très utile |
| LR− | 0.603 | <0.1 = très utile |
| Cohen κ | 0.2305 | 0.000 |
| Brier Score | 0.2876 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6585 | [0.6454, 0.6733]  ✅ |
| F1 macro | 0.6152 | [0.6028, 0.6288]  ✅ |
| Sensitivity | 0.6501 | [0.6333, 0.6671]  — |
| Specificity | 0.5804 | [0.5612, 0.6001]  — |
| MCC | 0.2310 | [0.2061, 0.2581]  — |
| R² | 0.0253 | [-0.0038, 0.0543]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0250 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6583 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2222 | < 0.05 |
| MCE | 0.3043 | < 0.10 |
| Brier Score | 0.2876 | < 0.20 |
| Log-Loss | 0.9708 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0493 | proche 0 = pas de biais systématique |
| LoA lower | -6.0435 | limite inférieure d'accord |
| LoA upper | +5.9448 | limite supérieure d'accord |
| LoA width | ±5.9941 | < ±2 pts : excellent |
| % dans LoA | 95.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1636 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0355 | 0.2633 | 740.9% | 🔴 unstable |
| AUC ROC | 0.6518 | 0.0743 | 11.4% | 🟢 stable |
| MAE | 2.5301 | 0.2499 | 9.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6547 |
| CI 95% | [0.6405, 0.6688] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.43 et 0.66


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:09*
