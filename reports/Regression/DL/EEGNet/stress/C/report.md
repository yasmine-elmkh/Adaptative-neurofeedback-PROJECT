# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet`  |  **Exp :** `C`  |  **Date :** 2026-06-20 02:01


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3805 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8861 | Erreur quadratique moyenne |
| R² | -0.0621 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5744 | 0.500 |
| PR-AUC | 0.5774 | 0.528 |
| Sensitivity (TPR) | 0.4825 | 0.500 |
| Specificity (TNR) | 0.6471 | 0.500 |
| PPV (Precision) | 0.6044 | — |
| NPV | 0.5280 | — |
| Balanced Accuracy | 0.5648 | 0.500 |
| MCC | 0.1309 | 0.000 |
| G-Mean | 0.5587 | 0.500 |
| F1 macro | 0.5590 | 0.500 |
| LR+ | 1.367 | >10 = très utile |
| LR− | 0.800 | <0.1 = très utile |
| Cohen κ | 0.1280 | 0.000 |
| Brier Score | 0.2659 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6090 | [0.5551, 0.6624]  ✅ |
| F1 macro | 0.4066 | [0.3798, 0.4336]  — |
| Sensitivity | 0.0180 | [0.0000, 0.0413]  — |
| Specificity | 0.9962 | [0.9886, 1.0000]  — |
| MCC | 0.0694 | [-0.0392, 0.1536]  — |
| R² | -0.0627 | [-0.1270, -0.0040]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0621 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6103 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2732 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3006 | < 0.20 |
| Log-Loss | 0.9584 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.8373 | proche 0 = pas de biais systématique |
| LoA lower | -6.2570 | limite inférieure d'accord |
| LoA upper | +4.5824 | limite supérieure d'accord |
| LoA width | ±5.4197 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0036 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0621 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5744 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3805 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:01*
