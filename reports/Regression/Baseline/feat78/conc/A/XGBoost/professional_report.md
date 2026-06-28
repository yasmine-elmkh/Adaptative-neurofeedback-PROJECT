# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:06


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7022 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1148 | Erreur quadratique moyenne |
| R² | -0.0114 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5889 | 0.500 |
| PR-AUC | 0.5924 | 0.517 |
| Sensitivity (TPR) | 0.4558 | 0.500 |
| Specificity (TNR) | 0.7064 | 0.500 |
| PPV (Precision) | 0.6238 | — |
| NPV | 0.5485 | — |
| Balanced Accuracy | 0.5811 | 0.500 |
| MCC | 0.1672 | 0.000 |
| G-Mean | 0.5674 | 0.500 |
| F1 macro | 0.5721 | 0.500 |
| LR+ | 1.552 | >10 = très utile |
| LR− | 0.770 | <0.1 = très utile |
| Cohen κ | 0.1607 | 0.000 |
| Brier Score | 0.2969 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5888 | [0.5595, 0.6183]  ✅ |
| F1 macro | 0.5383 | [0.5118, 0.5646]  ✅ |
| Sensitivity | 0.3447 | [0.3104, 0.3781]  — |
| Specificity | 0.7832 | [0.7533, 0.8165]  — |
| MCC | 0.1419 | [0.0926, 0.1949]  — |
| R² | -0.0120 | [-0.0514, 0.0254]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0114 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5886 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2347 | < 0.05 |
| MCE | 0.3943 | < 0.10 |
| Brier Score | 0.3113 | < 0.20 |
| Log-Loss | 0.9491 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0045 | proche 0 = pas de biais systématique |
| LoA lower | -6.1027 | limite inférieure d'accord |
| LoA upper | +6.1116 | limite supérieure d'accord |
| LoA width | ±6.1072 | < ±2 pts : excellent |
| % dans LoA | 99.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0766 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0612 | 0.1757 | 286.8% | 🔴 unstable |
| AUC ROC | 0.5990 | 0.0579 | 9.7% | 🟢 stable |
| MAE | 2.7024 | 0.2300 | 8.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5886 |
| CI 95% | [0.5592, 0.6181] |
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


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:06*
