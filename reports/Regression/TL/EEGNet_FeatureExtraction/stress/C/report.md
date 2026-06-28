# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `C`  |  **Date :** 2026-06-20 02:34


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4593 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8798 | Erreur quadratique moyenne |
| R² | -0.0575 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5968 | 0.500 |
| PR-AUC | 0.5211 | 0.465 |
| Sensitivity (TPR) | 0.8806 | 0.500 |
| Specificity (TNR) | 0.2987 | 0.500 |
| PPV (Precision) | 0.5221 | — |
| NPV | 0.7419 | — |
| Balanced Accuracy | 0.5896 | 0.500 |
| MCC | 0.2176 | 0.000 |
| G-Mean | 0.5129 | 0.500 |
| F1 macro | 0.5407 | 0.500 |
| LR+ | 1.256 | >10 = très utile |
| LR− | 0.400 | <0.1 = très utile |
| Cohen κ | 0.1716 | 0.000 |
| Brier Score | 0.2993 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6023 | [0.5442, 0.6595]  ✅ |
| F1 macro | 0.5424 | [0.4955, 0.5929]  — |
| Sensitivity | 0.6074 | [0.5357, 0.6882]  — |
| Specificity | 0.5140 | [0.4584, 0.5790]  — |
| MCC | 0.1171 | [0.0293, 0.2149]  — |
| R² | -0.0637 | [-0.1631, 0.0217]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0575 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5968 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1925 | < 0.05 |
| MCE | 0.4587 | < 0.10 |
| Brier Score | 0.2720 | < 0.20 |
| Log-Loss | 0.7694 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9109 | proche 0 = pas de biais systématique |
| LoA lower | -4.4499 | limite inférieure d'accord |
| LoA upper | +6.2717 | limite supérieure d'accord |
| LoA width | ±5.3608 | < ±2 pts : excellent |
| % dans LoA | 97.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0057 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0575 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5968 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4593 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:34*
