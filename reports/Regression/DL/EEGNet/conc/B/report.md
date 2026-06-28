# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet`  |  **Exp :** `B`  |  **Date :** 2026-06-20 01:46


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7364 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1986 | Erreur quadratique moyenne |
| R² | -0.0221 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5973 | 0.500 |
| PR-AUC | 0.5926 | 0.525 |
| Sensitivity (TPR) | 0.4123 | 0.500 |
| Specificity (TNR) | 0.7767 | 0.500 |
| PPV (Precision) | 0.6714 | — |
| NPV | 0.5442 | — |
| Balanced Accuracy | 0.5945 | 0.500 |
| MCC | 0.2019 | 0.000 |
| G-Mean | 0.5659 | 0.500 |
| F1 macro | 0.5754 | 0.500 |
| LR+ | 1.846 | >10 = très utile |
| LR− | 0.757 | <0.1 = très utile |
| Cohen κ | 0.1852 | 0.000 |
| Brier Score | 0.3071 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6014 | [0.5282, 0.6730]  ✅ |
| F1 macro | 0.5119 | [0.4465, 0.5773]  — |
| Sensitivity | 0.2877 | [0.2065, 0.3699]  — |
| Specificity | 0.8167 | [0.7387, 0.8826]  — |
| MCC | 0.1223 | [-0.0110, 0.2371]  — |
| R² | -0.0266 | [-0.1536, 0.0804]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0221 | p=0.0040 | ✅ p<0.05 |
| AUC ROC | 0.6013 | p=0.0060 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2976 | < 0.05 |
| MCE | 0.4663 | < 0.10 |
| Brier Score | 0.3257 | < 0.20 |
| Log-Loss | 0.9979 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4735 | proche 0 = pas de biais systématique |
| LoA lower | -6.6881 | limite inférieure d'accord |
| LoA upper | +5.7410 | limite supérieure d'accord |
| LoA width | ±6.2146 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0345 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0221 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5973 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.7364 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 01:46*
