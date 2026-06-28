# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `C`  |  **Date :** 2026-06-20 02:26


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3728 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8700 | Erreur quadratique moyenne |
| R² | 0.1772 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6920 | 0.500 |
| PR-AUC | 0.7297 | 0.608 |
| Sensitivity (TPR) | 0.9848 | 0.500 |
| Specificity (TNR) | 0.3882 | 0.500 |
| PPV (Precision) | 0.7143 | — |
| NPV | 0.9429 | — |
| Balanced Accuracy | 0.6865 | 0.500 |
| MCC | 0.4951 | 0.000 |
| G-Mean | 0.6183 | 0.500 |
| F1 macro | 0.6890 | 0.500 |
| LR+ | 1.610 | >10 = très utile |
| LR− | 0.039 | <0.1 = très utile |
| Cohen κ | 0.4167 | 0.000 |
| Brier Score | 0.2284 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6486 | [0.5728, 0.7185]  ✅ |
| F1 macro | 0.6035 | [0.5391, 0.6641]  ✅ |
| Sensitivity | 0.6638 | [0.5751, 0.7468]  — |
| Specificity | 0.5462 | [0.4514, 0.6408]  — |
| MCC | 0.2115 | [0.0817, 0.3315]  — |
| R² | 0.1711 | [0.0559, 0.2813]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1772 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6920 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1920 | < 0.05 |
| MCE | 0.5401 | < 0.10 |
| Brier Score | 0.2682 | < 0.20 |
| Log-Loss | 0.7882 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1457 | proche 0 = pas de biais systématique |
| LoA lower | -5.4851 | limite inférieure d'accord |
| LoA upper | +5.7766 | limite supérieure d'accord |
| LoA width | ±5.6309 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2396 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1772 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6920 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3728 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:26*
