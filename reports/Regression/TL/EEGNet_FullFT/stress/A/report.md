# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `A`  |  **Date :** 2026-06-20 02:37


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5194 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9524 | Erreur quadratique moyenne |
| R² | -0.1115 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5795 | 0.500 |
| PR-AUC | 0.5056 | 0.458 |
| Sensitivity (TPR) | 0.8788 | 0.500 |
| Specificity (TNR) | 0.2692 | 0.500 |
| PPV (Precision) | 0.5043 | — |
| NPV | 0.7241 | — |
| Balanced Accuracy | 0.5740 | 0.500 |
| MCC | 0.1839 | 0.000 |
| G-Mean | 0.4864 | 0.500 |
| F1 macro | 0.5167 | 0.500 |
| LR+ | 1.203 | >10 = très utile |
| LR− | 0.450 | <0.1 = très utile |
| Cohen κ | 0.1400 | 0.000 |
| Brier Score | 0.3115 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5866 | [0.5277, 0.6512]  ✅ |
| F1 macro | 0.5387 | [0.4942, 0.5892]  — |
| Sensitivity | 0.6763 | [0.6032, 0.7509]  — |
| Specificity | 0.4624 | [0.4053, 0.5184]  — |
| MCC | 0.1356 | [0.0445, 0.2286]  — |
| R² | -0.1193 | [-0.2310, -0.0275]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1115 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5795 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1977 | < 0.05 |
| MCE | 0.4516 | < 0.10 |
| Brier Score | 0.2876 | < 0.20 |
| Log-Loss | 0.8168 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +1.0301 | proche 0 = pas de biais systématique |
| LoA lower | -4.3992 | limite inférieure d'accord |
| LoA upper | +6.4594 | limite supérieure d'accord |
| LoA width | ±5.4293 | < ±2 pts : excellent |
| % dans LoA | 96.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0038 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1115 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5795 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5194 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:37*
