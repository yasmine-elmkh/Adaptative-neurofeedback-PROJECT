# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet`  |  **Exp :** `B`  |  **Date :** 2026-06-20 01:59


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4273 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9753 | Erreur quadratique moyenne |
| R² | -0.1288 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5826 | 0.500 |
| PR-AUC | 0.5859 | 0.537 |
| Sensitivity (TPR) | 0.5000 | 0.500 |
| Specificity (TNR) | 0.6350 | 0.500 |
| PPV (Precision) | 0.6138 | — |
| NPV | 0.5226 | — |
| Balanced Accuracy | 0.5675 | 0.500 |
| MCC | 0.1357 | 0.000 |
| G-Mean | 0.5635 | 0.500 |
| F1 macro | 0.5622 | 0.500 |
| LR+ | 1.370 | >10 = très utile |
| LR− | 0.787 | <0.1 = très utile |
| Cohen κ | 0.1330 | 0.000 |
| Brier Score | 0.2620 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5996 | [0.5419, 0.6553]  ✅ |
| F1 macro | 0.3885 | [0.3703, 0.4050]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 1.0000 | [1.0000, 1.0000]  — |
| MCC | 0.0000 | [0.0000, 0.0000]  — |
| R² | -0.1299 | [-0.2099, -0.0608]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1288 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6019 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3038 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.3188 | < 0.20 |
| Log-Loss | 1.0800 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.0947 | proche 0 = pas de biais systématique |
| LoA lower | -6.5236 | limite inférieure d'accord |
| LoA upper | +4.3342 | limite supérieure d'accord |
| LoA width | ±5.4289 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0019 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1288 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5826 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4273 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 01:59*
