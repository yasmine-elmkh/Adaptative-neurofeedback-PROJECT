# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `FULL`  |  **Date :** 2026-06-20 03:01


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4577 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8719 | Erreur quadratique moyenne |
| R² | -0.0517 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6073 | 0.500 |
| PR-AUC | 0.4645 | 0.384 |
| Sensitivity (TPR) | 0.6145 | 0.500 |
| Specificity (TNR) | 0.5865 | 0.500 |
| PPV (Precision) | 0.4811 | — |
| NPV | 0.7091 | — |
| Balanced Accuracy | 0.6005 | 0.500 |
| MCC | 0.1955 | 0.000 |
| G-Mean | 0.6003 | 0.500 |
| F1 macro | 0.5908 | 0.500 |
| LR+ | 1.486 | >10 = très utile |
| LR− | 0.657 | <0.1 = très utile |
| Cohen κ | 0.1910 | 0.000 |
| Brier Score | 0.2602 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6073 | [0.5553, 0.6599]  ✅ |
| F1 macro | 0.5536 | [0.5066, 0.6028]  ✅ |
| Sensitivity | 0.5174 | [0.4381, 0.5988]  — |
| Specificity | 0.6016 | [0.5428, 0.6535]  — |
| MCC | 0.1153 | [0.0238, 0.2152]  — |
| R² | -0.0590 | [-0.1425, 0.0133]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0517 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6073 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1390 | < 0.05 |
| MCE | 0.4777 | < 0.10 |
| Brier Score | 0.2558 | < 0.20 |
| Log-Loss | 0.7222 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.7990 | proche 0 = pas de biais systématique |
| LoA lower | -4.6139 | limite inférieure d'accord |
| LoA upper | +6.2119 | limite supérieure d'accord |
| LoA width | ±5.4129 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0053 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0517 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6073 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4577 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 03:01*
