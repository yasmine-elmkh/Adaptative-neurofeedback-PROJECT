# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `C`  |  **Date :** 2026-06-20 02:42


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3872 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8359 | Erreur quadratique moyenne |
| R² | 0.1966 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6866 | 0.500 |
| PR-AUC | 0.6499 | 0.530 |
| Sensitivity (TPR) | 0.7826 | 0.500 |
| Specificity (TNR) | 0.5294 | 0.500 |
| PPV (Precision) | 0.6522 | — |
| NPV | 0.6835 | — |
| Balanced Accuracy | 0.6560 | 0.500 |
| MCC | 0.3237 | 0.000 |
| G-Mean | 0.6437 | 0.500 |
| F1 macro | 0.6541 | 0.500 |
| LR+ | 1.663 | >10 = très utile |
| LR− | 0.411 | <0.1 = très utile |
| Cohen κ | 0.3160 | 0.000 |
| Brier Score | 0.2390 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6887 | [0.6101, 0.7587]  ✅ |
| F1 macro | 0.6311 | [0.5622, 0.6951]  ✅ |
| Sensitivity | 0.5971 | [0.5044, 0.6920]  — |
| Specificity | 0.6704 | [0.5721, 0.7600]  — |
| MCC | 0.2677 | [0.1306, 0.3916]  — |
| R² | 0.1916 | [0.1004, 0.2856]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1966 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6866 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1655 | < 0.05 |
| MCE | 0.4196 | < 0.10 |
| Brier Score | 0.2469 | < 0.20 |
| Log-Loss | 0.7296 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0086 | proche 0 = pas de biais systématique |
| LoA lower | -5.5627 | limite inférieure d'accord |
| LoA upper | +5.5799 | limite supérieure d'accord |
| LoA width | ±5.5713 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2544 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1966 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6866 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3872 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:42*
