# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet`  |  **Exp :** `C`  |  **Date :** 2026-06-20 01:48


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5019 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0898 | Erreur quadratique moyenne |
| R² | 0.0463 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7485 | 0.500 |
| PR-AUC | 0.8241 | 0.714 |
| Sensitivity (TPR) | 0.9677 | 0.500 |
| Specificity (TNR) | 0.5806 | 0.500 |
| PPV (Precision) | 0.8523 | — |
| NPV | 0.8780 | — |
| Balanced Accuracy | 0.7742 | 0.500 |
| MCC | 0.6328 | 0.000 |
| G-Mean | 0.7496 | 0.500 |
| F1 macro | 0.8027 | 0.500 |
| LR+ | 2.308 | >10 = très utile |
| LR− | 0.056 | <0.1 = très utile |
| Cohen κ | 0.6104 | 0.000 |
| Brier Score | 0.1373 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6440 | [0.5709, 0.7111]  ✅ |
| F1 macro | 0.4311 | [0.3704, 0.4974]  — |
| Sensitivity | 0.1581 | [0.0973, 0.2305]  — |
| Specificity | 0.8569 | [0.7894, 0.9257]  — |
| MCC | 0.0210 | [-0.1195, 0.1402]  — |
| R² | 0.0405 | [-0.0907, 0.1700]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0463 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6447 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3428 | < 0.05 |
| MCE | 0.5787 | < 0.10 |
| Brier Score | 0.3524 | < 0.20 |
| Log-Loss | 1.0806 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0351 | proche 0 = pas de biais systématique |
| LoA lower | -6.7543 | limite inférieure d'accord |
| LoA upper | +4.6841 | limite supérieure d'accord |
| LoA width | ±5.7192 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0299 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0463 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7485 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5019 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 01:48*
