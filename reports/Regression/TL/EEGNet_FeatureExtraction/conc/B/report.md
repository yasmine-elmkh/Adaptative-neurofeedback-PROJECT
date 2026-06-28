# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FeatureExtraction`  |  **Exp :** `B`  |  **Date :** 2026-06-20 02:25


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3527 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8365 | Erreur quadratique moyenne |
| R² | 0.1962 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6883 | 0.500 |
| PR-AUC | 0.6937 | 0.571 |
| Sensitivity (TPR) | 0.9597 | 0.500 |
| Specificity (TNR) | 0.3871 | 0.500 |
| PPV (Precision) | 0.6761 | — |
| NPV | 0.8780 | — |
| Balanced Accuracy | 0.6734 | 0.500 |
| MCC | 0.4384 | 0.000 |
| G-Mean | 0.6095 | 0.500 |
| F1 macro | 0.6653 | 0.500 |
| LR+ | 1.566 | >10 = très utile |
| LR− | 0.104 | <0.1 = très utile |
| Cohen κ | 0.3728 | 0.000 |
| Brier Score | 0.2459 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6672 | [0.5916, 0.7367]  ✅ |
| F1 macro | 0.5750 | [0.5126, 0.6373]  ✅ |
| Sensitivity | 0.6479 | [0.5580, 0.7349]  — |
| Specificity | 0.5063 | [0.4136, 0.6019]  — |
| MCC | 0.1558 | [0.0280, 0.2773]  — |
| R² | 0.1906 | [0.0829, 0.2942]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1962 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6883 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2115 | < 0.05 |
| MCE | 0.5074 | < 0.10 |
| Brier Score | 0.2618 | < 0.20 |
| Log-Loss | 0.7664 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2093 | proche 0 = pas de biais systématique |
| LoA lower | -5.3479 | limite inférieure d'accord |
| LoA upper | +5.7666 | limite supérieure d'accord |
| LoA width | ±5.5573 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2260 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1962 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6883 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3527 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:25*
