# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `A`  |  **Date :** 2026-06-21 15:58


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6105 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1289 | Erreur quadratique moyenne |
| R² | -0.0205 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6107 | 0.500 |
| PR-AUC | 0.6154 | 0.517 |
| Sensitivity (TPR) | 0.5883 | 0.500 |
| Specificity (TNR) | 0.5357 | 0.500 |
| PPV (Precision) | 0.5758 | — |
| NPV | 0.5484 | — |
| Balanced Accuracy | 0.5620 | 0.500 |
| MCC | 0.1241 | 0.000 |
| G-Mean | 0.5614 | 0.500 |
| F1 macro | 0.5620 | 0.500 |
| LR+ | 1.267 | >10 = très utile |
| LR− | 0.769 | <0.1 = très utile |
| Cohen κ | 0.1241 | 0.000 |
| Brier Score | 0.3130 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6107 | [0.5813, 0.6399]  ✅ |
| F1 macro | 0.5616 | [0.5348, 0.5871]  ✅ |
| Sensitivity | 0.5876 | [0.5525, 0.6207]  — |
| Specificity | 0.5359 | [0.4989, 0.5759]  — |
| MCC | 0.1236 | [0.0707, 0.1750]  — |
| R² | -0.0223 | [-0.0782, 0.0320]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0205 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6107 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2643 | < 0.05 |
| MCE | 0.3949 | < 0.10 |
| Brier Score | 0.3130 | < 0.20 |
| Log-Loss | 0.9987 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0745 | proche 0 = pas de biais systématique |
| LoA lower | -6.2076 | limite inférieure d'accord |
| LoA upper | +6.0586 | limite supérieure d'accord |
| LoA width | ±6.1331 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1394 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0769 | 0.2555 | 332.1% | 🔴 unstable |
| AUC ROC | 0.6075 | 0.0764 | 12.6% | 🟢 stable |
| MAE | 2.6251 | 0.3206 | 12.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6096 |
| CI 95% | [0.5804, 0.6387] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 15:58*
