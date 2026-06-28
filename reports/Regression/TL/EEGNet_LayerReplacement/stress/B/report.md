# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `B`  |  **Date :** 2026-06-20 02:54


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4765 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8772 | Erreur quadratique moyenne |
| R² | -0.0556 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5527 | 0.500 |
| PR-AUC | 0.4953 | 0.458 |
| Sensitivity (TPR) | 0.8182 | 0.500 |
| Specificity (TNR) | 0.2991 | 0.500 |
| PPV (Precision) | 0.4969 | — |
| NPV | 0.6604 | — |
| Balanced Accuracy | 0.5587 | 0.500 |
| MCC | 0.1359 | 0.000 |
| G-Mean | 0.4947 | 0.500 |
| F1 macro | 0.5150 | 0.500 |
| LR+ | 1.167 | >10 = très utile |
| LR− | 0.608 | <0.1 = très utile |
| Cohen κ | 0.1118 | 0.000 |
| Brier Score | 0.2937 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5655 | [0.5079, 0.6188]  ✅ |
| F1 macro | 0.5317 | [0.4814, 0.5809]  — |
| Sensitivity | 0.4864 | [0.3942, 0.5645]  — |
| Specificity | 0.5868 | [0.5266, 0.6457]  — |
| MCC | 0.0710 | [-0.0272, 0.1709]  — |
| R² | -0.0620 | [-0.1452, 0.0080]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0556 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5527 | p=0.0200 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1388 | < 0.05 |
| MCE | 0.4493 | < 0.10 |
| Brier Score | 0.2636 | < 0.20 |
| Log-Loss | 0.7325 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.7635 | proche 0 = pas de biais systématique |
| LoA lower | -4.6799 | limite inférieure d'accord |
| LoA upper | +6.2069 | limite supérieure d'accord |
| LoA width | ±5.4434 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0042 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0556 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5527 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4765 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:54*
