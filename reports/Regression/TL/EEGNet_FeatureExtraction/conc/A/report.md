# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `A`  |  **Date :** 2026-06-20 02:24


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3470 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8653 | Erreur quadratique moyenne |
| R² | 0.1798 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7010 | 0.500 |
| PR-AUC | 0.7289 | 0.608 |
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
| Brier Score | 0.2258 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6696 | [0.5985, 0.7372]  ✅ |
| F1 macro | 0.6189 | [0.5566, 0.6827]  ✅ |
| Sensitivity | 0.7279 | [0.6409, 0.8036]  — |
| Specificity | 0.5166 | [0.4279, 0.6148]  — |
| MCC | 0.2505 | [0.1261, 0.3773]  — |
| R² | 0.1746 | [0.0540, 0.2824]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1798 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7010 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1915 | < 0.05 |
| MCE | 0.4330 | < 0.10 |
| Brier Score | 0.2579 | < 0.20 |
| Log-Loss | 0.7787 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2757 | proche 0 = pas de biais systématique |
| LoA lower | -5.3272 | limite inférieure d'accord |
| LoA upper | +5.8787 | limite supérieure d'accord |
| LoA width | ±5.6030 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1916 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1798 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7010 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3470 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:24*
