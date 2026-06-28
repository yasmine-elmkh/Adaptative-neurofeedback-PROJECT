# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `B`  |  **Date :** 2026-06-20 02:40


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4807 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9026 | Erreur quadratique moyenne |
| R² | -0.0743 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5941 | 0.500 |
| PR-AUC | 0.4467 | 0.375 |
| Sensitivity (TPR) | 0.6481 | 0.500 |
| Specificity (TNR) | 0.5000 | 0.500 |
| PPV (Precision) | 0.4375 | — |
| NPV | 0.7031 | — |
| Balanced Accuracy | 0.5741 | 0.500 |
| MCC | 0.1443 | 0.000 |
| G-Mean | 0.5693 | 0.500 |
| F1 macro | 0.5534 | 0.500 |
| LR+ | 1.296 | >10 = très utile |
| LR− | 0.704 | <0.1 = très utile |
| Cohen κ | 0.1351 | 0.000 |
| Brier Score | 0.2771 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5967 | [0.5442, 0.6585]  ✅ |
| F1 macro | 0.5558 | [0.5061, 0.6091]  ✅ |
| Sensitivity | 0.6513 | [0.5781, 0.7279]  — |
| Specificity | 0.5069 | [0.4481, 0.5696]  — |
| MCC | 0.1531 | [0.0592, 0.2515]  — |
| R² | -0.0808 | [-0.1849, -0.0005]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0743 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5941 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1754 | < 0.05 |
| MCE | 0.4636 | < 0.10 |
| Brier Score | 0.2744 | < 0.20 |
| Log-Loss | 0.7764 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9190 | proche 0 = pas de biais systématique |
| LoA lower | -4.4837 | limite inférieure d'accord |
| LoA upper | +6.3217 | limite supérieure d'accord |
| LoA width | ±5.4027 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0050 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0743 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5941 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4807 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:40*
