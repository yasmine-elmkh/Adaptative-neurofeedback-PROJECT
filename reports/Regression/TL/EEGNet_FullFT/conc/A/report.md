# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `A`  |  **Date :** 2026-06-20 02:24


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3671 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8559 | Erreur quadratique moyenne |
| R² | 0.1852 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6924 | 0.500 |
| PR-AUC | 0.6880 | 0.571 |
| Sensitivity (TPR) | 0.9597 | 0.500 |
| Specificity (TNR) | 0.3763 | 0.500 |
| PPV (Precision) | 0.6723 | — |
| NPV | 0.8750 | — |
| Balanced Accuracy | 0.6680 | 0.500 |
| MCC | 0.4288 | 0.000 |
| G-Mean | 0.6010 | 0.500 |
| F1 macro | 0.6585 | 0.500 |
| LR+ | 1.539 | >10 = très utile |
| LR− | 0.107 | <0.1 = très utile |
| Cohen κ | 0.3618 | 0.000 |
| Brier Score | 0.2460 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6658 | [0.5909, 0.7337]  ✅ |
| F1 macro | 0.6112 | [0.5505, 0.6727]  ✅ |
| Sensitivity | 0.7006 | [0.6196, 0.7904]  — |
| Specificity | 0.5269 | [0.4299, 0.6177]  — |
| MCC | 0.2313 | [0.1165, 0.3522]  — |
| R² | 0.1795 | [0.0639, 0.2904]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1852 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6924 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1733 | < 0.05 |
| MCE | 0.4026 | < 0.10 |
| Brier Score | 0.2584 | < 0.20 |
| Log-Loss | 0.7709 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2675 | proche 0 = pas de biais systématique |
| LoA lower | -5.3183 | limite inférieure d'accord |
| LoA upper | +5.8534 | limite supérieure d'accord |
| LoA width | ±5.5858 | < ±2 pts : excellent |
| % dans LoA | 95.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1953 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1852 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6924 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3671 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:24*
