# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `D`  |  **Date :** 2026-06-21 17:07


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7240 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2875 | Erreur quadratique moyenne |
| R² | -0.1266 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5960 | 0.500 |
| PR-AUC | 0.5902 | 0.517 |
| Sensitivity (TPR) | 0.6080 | 0.500 |
| Specificity (TNR) | 0.5175 | 0.500 |
| PPV (Precision) | 0.5745 | — |
| NPV | 0.5520 | — |
| Balanced Accuracy | 0.5627 | 0.500 |
| MCC | 0.1260 | 0.000 |
| G-Mean | 0.5609 | 0.500 |
| F1 macro | 0.5625 | 0.500 |
| LR+ | 1.260 | >10 = très utile |
| LR− | 0.758 | <0.1 = très utile |
| Cohen κ | 0.1257 | 0.000 |
| Brier Score | 0.3340 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5957 | [0.5732, 0.6180]  ✅ |
| F1 macro | 0.5621 | [0.5445, 0.5803]  ✅ |
| Sensitivity | 0.6072 | [0.5806, 0.6336]  — |
| Specificity | 0.5176 | [0.4898, 0.5432]  — |
| MCC | 0.1253 | [0.0904, 0.1620]  — |
| R² | -0.1275 | [-0.1765, -0.0813]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1266 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5960 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2889 | < 0.05 |
| MCE | 0.4029 | < 0.10 |
| Brier Score | 0.3340 | < 0.20 |
| Log-Loss | 1.1548 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0983 | proche 0 = pas de biais systématique |
| LoA lower | -6.5400 | limite inférieure d'accord |
| LoA upper | +6.3434 | limite supérieure d'accord |
| LoA width | ±6.4417 | < ±2 pts : excellent |
| % dans LoA | 96.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1081 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.2061 | 0.3605 | 174.9% | 🔴 unstable |
| AUC ROC | 0.5817 | 0.1028 | 17.7% | 🟡 moderate |
| MAE | 2.7483 | 0.4004 | 14.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5941 |
| CI 95% | [0.5733, 0.6149] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.57


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:07*
