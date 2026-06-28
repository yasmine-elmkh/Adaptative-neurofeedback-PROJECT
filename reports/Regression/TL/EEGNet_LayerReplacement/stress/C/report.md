# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `C`  |  **Date :** 2026-06-20 02:57


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4762 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8958 | Erreur quadratique moyenne |
| R² | -0.0693 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5617 | 0.500 |
| PR-AUC | 0.4881 | 0.451 |
| Sensitivity (TPR) | 0.6359 | 0.500 |
| Specificity (TNR) | 0.5105 | 0.500 |
| PPV (Precision) | 0.5167 | — |
| NPV | 0.6302 | — |
| Balanced Accuracy | 0.5732 | 0.500 |
| MCC | 0.1467 | 0.000 |
| G-Mean | 0.5698 | 0.500 |
| F1 macro | 0.5671 | 0.500 |
| LR+ | 1.299 | >10 = très utile |
| LR− | 0.713 | <0.1 = très utile |
| Cohen κ | 0.1435 | 0.000 |
| Brier Score | 0.2754 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5741 | [0.5204, 0.6279]  ✅ |
| F1 macro | 0.5472 | [0.4989, 0.5939]  — |
| Sensitivity | 0.4812 | [0.4000, 0.5521]  — |
| Specificity | 0.6200 | [0.5638, 0.6827]  — |
| MCC | 0.0989 | [0.0023, 0.1906]  — |
| R² | -0.0752 | [-0.1518, -0.0047]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0693 | p=0.0040 | ✅ p<0.05 |
| AUC ROC | 0.5617 | p=0.0100 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1264 | < 0.05 |
| MCE | 0.5703 | < 0.10 |
| Brier Score | 0.2623 | < 0.20 |
| Log-Loss | 0.7393 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.7369 | proche 0 = pas de biais systématique |
| LoA lower | -4.7585 | limite inférieure d'accord |
| LoA upper | +6.2323 | limite supérieure d'accord |
| LoA width | ±5.4954 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0039 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0693 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.5617 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.4762 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:57*
