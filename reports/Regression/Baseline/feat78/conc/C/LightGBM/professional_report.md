# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `C`  |  **Date :** 2026-06-21 17:03


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7062 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1216 | Erreur quadratique moyenne |
| R² | -0.0158 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5752 | 0.500 |
| PR-AUC | 0.5706 | 0.521 |
| Sensitivity (TPR) | 0.7805 | 0.500 |
| Specificity (TNR) | 0.3328 | 0.500 |
| PPV (Precision) | 0.5597 | — |
| NPV | 0.5825 | — |
| Balanced Accuracy | 0.5567 | 0.500 |
| MCC | 0.1270 | 0.000 |
| G-Mean | 0.5097 | 0.500 |
| F1 macro | 0.5378 | 0.500 |
| LR+ | 1.170 | >10 = très utile |
| LR− | 0.660 | <0.1 = très utile |
| Cohen κ | 0.1153 | 0.000 |
| Brier Score | 0.3077 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5723 | [0.5563, 0.5919]  ✅ |
| F1 macro | 0.5072 | [0.4927, 0.5210]  — |
| Sensitivity | 0.3151 | [0.2976, 0.3340]  — |
| Specificity | 0.7535 | [0.7359, 0.7706]  — |
| MCC | 0.0762 | [0.0462, 0.1052]  — |
| R² | -0.0157 | [-0.0379, 0.0098]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0158 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5718 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2401 | < 0.05 |
| MCE | 0.3971 | < 0.10 |
| Brier Score | 0.3195 | < 0.20 |
| Log-Loss | 0.9751 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0293 | proche 0 = pas de biais systématique |
| LoA lower | -6.1481 | limite inférieure d'accord |
| LoA upper | +6.0894 | limite supérieure d'accord |
| LoA width | ±6.1187 | < ±2 pts : excellent |
| % dans LoA | 98.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0739 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0629 | 0.1419 | 225.7% | 🔴 unstable |
| AUC ROC | 0.5790 | 0.0514 | 8.9% | 🟢 stable |
| MAE | 2.7128 | 0.2569 | 9.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5718 |
| CI 95% | [0.5547, 0.5889] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.51 et 0.57


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:03*
