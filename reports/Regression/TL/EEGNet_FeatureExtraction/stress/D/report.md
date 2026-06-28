# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `D`  |  **Date :** 2026-06-20 02:36


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4758 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8995 | Erreur quadratique moyenne |
| R² | -0.0720 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5923 | 0.500 |
| PR-AUC | 0.4234 | 0.354 |
| Sensitivity (TPR) | 0.6144 | 0.500 |
| Specificity (TNR) | 0.5341 | 0.500 |
| PPV (Precision) | 0.4196 | — |
| NPV | 0.7163 | — |
| Balanced Accuracy | 0.5742 | 0.500 |
| MCC | 0.1421 | 0.000 |
| G-Mean | 0.5728 | 0.500 |
| F1 macro | 0.5553 | 0.500 |
| LR+ | 1.319 | >10 = très utile |
| LR− | 0.722 | <0.1 = très utile |
| Cohen κ | 0.1344 | 0.000 |
| Brier Score | 0.2729 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5960 | [0.5396, 0.6522]  ✅ |
| F1 macro | 0.5496 | [0.4998, 0.6019]  — |
| Sensitivity | 0.6186 | [0.5451, 0.6903]  — |
| Specificity | 0.5185 | [0.4549, 0.5842]  — |
| MCC | 0.1323 | [0.0395, 0.2322]  — |
| R² | -0.0785 | [-0.1798, 0.0071]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0720 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5923 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1751 | < 0.05 |
| MCE | 0.4723 | < 0.10 |
| Brier Score | 0.2743 | < 0.20 |
| Log-Loss | 0.7765 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9241 | proche 0 = pas de biais systématique |
| LoA lower | -4.4688 | limite inférieure d'accord |
| LoA upper | +6.3170 | limite supérieure d'accord |
| LoA width | ±5.3929 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0051 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0720 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5923 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4758 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:36*
