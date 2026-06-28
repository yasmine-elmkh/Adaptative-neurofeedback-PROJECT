# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet`  |  **Exp :** `D`  |  **Date :** 2026-06-20 02:03


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3342 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7819 | Erreur quadratique moyenne |
| R² | 0.0132 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5915 | 0.500 |
| PR-AUC | 0.5864 | 0.528 |
| Sensitivity (TPR) | 0.5482 | 0.500 |
| Specificity (TNR) | 0.5931 | 0.500 |
| PPV (Precision) | 0.6010 | — |
| NPV | 0.5402 | — |
| Balanced Accuracy | 0.5707 | 0.500 |
| MCC | 0.1413 | 0.000 |
| G-Mean | 0.5702 | 0.500 |
| F1 macro | 0.5694 | 0.500 |
| LR+ | 1.347 | >10 = très utile |
| LR− | 0.762 | <0.1 = très utile |
| Cohen κ | 0.1407 | 0.000 |
| Brier Score | 0.2675 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6058 | [0.5539, 0.6627]  ✅ |
| F1 macro | 0.4470 | [0.4098, 0.4852]  — |
| Sensitivity | 0.0701 | [0.0321, 0.1136]  — |
| Specificity | 0.9627 | [0.9403, 0.9833]  — |
| MCC | 0.0723 | [-0.0265, 0.1596]  — |
| R² | 0.0117 | [-0.0425, 0.0677]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0132 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6060 | p=0.0020 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2093 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2727 | < 0.20 |
| Log-Loss | 0.8272 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4590 | proche 0 = pas de biais systématique |
| LoA lower | -5.8429 | limite inférieure d'accord |
| LoA upper | +4.9250 | limite supérieure d'accord |
| LoA width | ±5.3840 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0156 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0132 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5915 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3342 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:03*
