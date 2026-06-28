# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `D`  |  **Date :** 2026-06-20 02:27


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3826 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8923 | Erreur quadratique moyenne |
| R² | 0.1643 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6943 | 0.500 |
| PR-AUC | 0.7197 | 0.608 |
| Sensitivity (TPR) | 0.9924 | 0.500 |
| Specificity (TNR) | 0.3882 | 0.500 |
| PPV (Precision) | 0.7158 | — |
| NPV | 0.9706 | — |
| Balanced Accuracy | 0.6903 | 0.500 |
| MCC | 0.5112 | 0.000 |
| G-Mean | 0.6207 | 0.500 |
| F1 macro | 0.6932 | 0.500 |
| LR+ | 1.622 | >10 = très utile |
| LR− | 0.020 | <0.1 = très utile |
| Cohen κ | 0.4262 | 0.000 |
| Brier Score | 0.2303 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6502 | [0.5768, 0.7195]  ✅ |
| F1 macro | 0.5970 | [0.5367, 0.6572]  ✅ |
| Sensitivity | 0.7262 | [0.6330, 0.8052]  — |
| Specificity | 0.4778 | [0.3829, 0.5751]  — |
| MCC | 0.2110 | [0.0885, 0.3293]  — |
| R² | 0.1579 | [0.0445, 0.2708]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1643 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6943 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1883 | < 0.05 |
| MCE | 0.4977 | < 0.10 |
| Brier Score | 0.2681 | < 0.20 |
| Log-Loss | 0.8006 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2533 | proche 0 = pas de biais systématique |
| LoA lower | -5.4069 | limite inférieure d'accord |
| LoA upper | +5.9135 | limite supérieure d'accord |
| LoA width | ±5.6602 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1942 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1643 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6943 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3826 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:27*
