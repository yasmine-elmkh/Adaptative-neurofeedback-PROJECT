# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:23


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4563 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0023 | Erreur quadratique moyenne |
| R² | 0.0604 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6739 | 0.500 |
| PR-AUC | 0.6624 | 0.517 |
| Sensitivity (TPR) | 0.6245 | 0.500 |
| Specificity (TNR) | 0.6206 | 0.500 |
| PPV (Precision) | 0.6381 | — |
| NPV | 0.6067 | — |
| Balanced Accuracy | 0.6226 | 0.500 |
| MCC | 0.2450 | 0.000 |
| G-Mean | 0.6226 | 0.500 |
| F1 macro | 0.6224 | 0.500 |
| LR+ | 1.646 | >10 = très utile |
| LR− | 0.605 | <0.1 = très utile |
| Cohen κ | 0.2449 | 0.000 |
| Brier Score | 0.2808 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6739 | [0.6582, 0.6882]  ✅ |
| F1 macro | 0.6225 | [0.6086, 0.6374]  ✅ |
| Sensitivity | 0.6251 | [0.6066, 0.6460]  — |
| Specificity | 0.6204 | [0.5993, 0.6415]  — |
| MCC | 0.2453 | [0.2172, 0.2751]  — |
| R² | 0.0603 | [0.0253, 0.0930]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0604 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6739 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2170 | < 0.05 |
| MCE | 0.3166 | < 0.10 |
| Brier Score | 0.2808 | < 0.20 |
| Log-Loss | 0.9428 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0680 | proche 0 = pas de biais systématique |
| LoA lower | -5.9516 | limite inférieure d'accord |
| LoA upper | +5.8156 | limite supérieure d'accord |
| LoA width | ±5.8836 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1664 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0046 | 0.2824 | 6077.5% | 🔴 unstable |
| AUC ROC | 0.6671 | 0.0911 | 13.7% | 🟢 stable |
| MAE | 2.4666 | 0.2709 | 11.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6711 |
| CI 95% | [0.6550, 0.6872] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.41 et 0.67


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:23*
