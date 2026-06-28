# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `D`  |  **Date :** 2026-06-20 02:46


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4762 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8988 | Erreur quadratique moyenne |
| R² | -0.0714 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5812 | 0.500 |
| PR-AUC | 0.5130 | 0.458 |
| Sensitivity (TPR) | 0.7626 | 0.500 |
| Specificity (TNR) | 0.3889 | 0.500 |
| PPV (Precision) | 0.5136 | — |
| NPV | 0.6594 | — |
| Balanced Accuracy | 0.5758 | 0.500 |
| MCC | 0.1619 | 0.000 |
| G-Mean | 0.5446 | 0.500 |
| F1 macro | 0.5515 | 0.500 |
| LR+ | 1.248 | >10 = très utile |
| LR− | 0.610 | <0.1 = très utile |
| Cohen κ | 0.1461 | 0.000 |
| Brier Score | 0.2876 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5899 | [0.5347, 0.6513]  ✅ |
| F1 macro | 0.5633 | [0.5181, 0.6170]  ✅ |
| Sensitivity | 0.6066 | [0.5329, 0.6771]  — |
| Specificity | 0.5507 | [0.4908, 0.6098]  — |
| MCC | 0.1514 | [0.0630, 0.2535]  — |
| R² | -0.0779 | [-0.1699, 0.0081]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0714 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5812 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1753 | < 0.05 |
| MCE | 0.4341 | < 0.10 |
| Brier Score | 0.2720 | < 0.20 |
| Log-Loss | 0.7658 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8697 | proche 0 = pas de biais systématique |
| LoA lower | -4.5564 | limite inférieure d'accord |
| LoA upper | +6.2958 | limite supérieure d'accord |
| LoA width | ±5.4261 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0051 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0714 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5812 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4762 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:46*
