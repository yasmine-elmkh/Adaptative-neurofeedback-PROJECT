# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `A`  |  **Date :** 2026-06-20 02:30


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4854 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9179 | Erreur quadratique moyenne |
| R² | -0.0856 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5945 | 0.500 |
| PR-AUC | 0.4245 | 0.350 |
| Sensitivity (TPR) | 0.6424 | 0.500 |
| Specificity (TNR) | 0.5160 | 0.500 |
| PPV (Precision) | 0.4163 | — |
| NPV | 0.7286 | — |
| Balanced Accuracy | 0.5792 | 0.500 |
| MCC | 0.1515 | 0.000 |
| G-Mean | 0.5757 | 0.500 |
| F1 macro | 0.5547 | 0.500 |
| LR+ | 1.327 | >10 = très utile |
| LR− | 0.693 | <0.1 = très utile |
| Cohen κ | 0.1407 | 0.000 |
| Brier Score | 0.2760 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5952 | [0.5418, 0.6544]  ✅ |
| F1 macro | 0.5473 | [0.5013, 0.5997]  ✅ |
| Sensitivity | 0.6569 | [0.5838, 0.7264]  — |
| Specificity | 0.4890 | [0.4268, 0.5544]  — |
| MCC | 0.1416 | [0.0494, 0.2429]  — |
| R² | -0.0929 | [-0.2009, -0.0078]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0856 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5945 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1903 | < 0.05 |
| MCE | 0.4342 | < 0.10 |
| Brier Score | 0.2804 | < 0.20 |
| Log-Loss | 0.7900 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9929 | proche 0 = pas de biais systématique |
| LoA lower | -4.3910 | limite inférieure d'accord |
| LoA upper | +6.3769 | limite supérieure d'accord |
| LoA width | ±5.3839 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0045 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0856 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5945 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4854 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:30*
