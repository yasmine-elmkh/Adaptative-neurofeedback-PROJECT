# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `FULL`  |  **Date :** 2026-06-20 02:50


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4636 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8796 | Erreur quadratique moyenne |
| R² | -0.0574 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5846 | 0.500 |
| PR-AUC | 0.5127 | 0.458 |
| Sensitivity (TPR) | 0.7778 | 0.500 |
| Specificity (TNR) | 0.3846 | 0.500 |
| PPV (Precision) | 0.5168 | — |
| NPV | 0.6716 | — |
| Balanced Accuracy | 0.5812 | 0.500 |
| MCC | 0.1749 | 0.000 |
| G-Mean | 0.5469 | 0.500 |
| F1 macro | 0.5550 | 0.500 |
| LR+ | 1.264 | >10 = très utile |
| LR− | 0.578 | <0.1 = très utile |
| Cohen κ | 0.1563 | 0.000 |
| Brier Score | 0.2849 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5935 | [0.5396, 0.6525]  ✅ |
| F1 macro | 0.5463 | [0.5045, 0.5963]  ✅ |
| Sensitivity | 0.5959 | [0.5183, 0.6779]  — |
| Specificity | 0.5289 | [0.4698, 0.5948]  — |
| MCC | 0.1202 | [0.0335, 0.2239]  — |
| R² | -0.0639 | [-0.1538, 0.0177]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0574 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5846 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1613 | < 0.05 |
| MCE | 0.4666 | < 0.10 |
| Brier Score | 0.2669 | < 0.20 |
| Log-Loss | 0.7511 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8516 | proche 0 = pas de biais systématique |
| LoA lower | -4.5462 | limite inférieure d'accord |
| LoA upper | +6.2495 | limite supérieure d'accord |
| LoA width | ±5.3979 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0054 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0574 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5846 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4636 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:50*
