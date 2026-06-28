# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `A`  |  **Date :** 2026-06-20 02:51


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5101 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9149 | Erreur quadratique moyenne |
| R² | -0.0834 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5142 | 0.500 |
| PR-AUC | 0.3616 | 0.361 |
| Sensitivity (TPR) | 0.5321 | 0.500 |
| Specificity (TNR) | 0.5471 | 0.500 |
| PPV (Precision) | 0.3990 | — |
| NPV | 0.6741 | — |
| Balanced Accuracy | 0.5396 | 0.500 |
| MCC | 0.0761 | 0.000 |
| G-Mean | 0.5395 | 0.500 |
| F1 macro | 0.5300 | 0.500 |
| LR+ | 1.175 | >10 = très utile |
| LR− | 0.855 | <0.1 = très utile |
| Cohen κ | 0.0738 | 0.000 |
| Brier Score | 0.2691 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5211 | [0.4677, 0.5804]  — |
| F1 macro | 0.5173 | [0.4697, 0.5665]  — |
| Sensitivity | 0.5434 | [0.4696, 0.6258]  — |
| Specificity | 0.5160 | [0.4571, 0.5744]  — |
| MCC | 0.0572 | [-0.0390, 0.1522]  — |
| R² | -0.0889 | [-0.1597, -0.0275]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0834 | p=0.0320 | ✅ p<0.05 |
| AUC ROC | 0.5142 | p=0.3120 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1528 | < 0.05 |
| MCE | 0.5656 | < 0.10 |
| Brier Score | 0.2696 | < 0.20 |
| Log-Loss | 0.7397 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8149 | proche 0 = pas de biais systématique |
| LoA lower | -4.6769 | limite inférieure d'accord |
| LoA upper | +6.3067 | limite supérieure d'accord |
| LoA width | ±5.4918 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0018 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0834 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5142 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5101 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:51*
