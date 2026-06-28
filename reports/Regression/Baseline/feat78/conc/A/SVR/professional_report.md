# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `A`  |  **Date :** 2026-06-21 15:57


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.8083 | Erreur absolue moyenne (0-10) |
| RMSE | 3.3023 | Erreur quadratique moyenne |
| R² | -0.1368 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5623 | 0.500 |
| PR-AUC | 0.5684 | 0.517 |
| Sensitivity (TPR) | 0.4612 | 0.500 |
| Specificity (TNR) | 0.6512 | 0.500 |
| PPV (Precision) | 0.5855 | — |
| NPV | 0.5308 | — |
| Balanced Accuracy | 0.5562 | 0.500 |
| MCC | 0.1143 | 0.000 |
| G-Mean | 0.5480 | 0.500 |
| F1 macro | 0.5504 | 0.500 |
| LR+ | 1.322 | >10 = très utile |
| LR− | 0.827 | <0.1 = très utile |
| Cohen κ | 0.1116 | 0.000 |
| Brier Score | 0.3387 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5623 | [0.5337, 0.5918]  ✅ |
| F1 macro | 0.5248 | [0.4965, 0.5507]  — |
| Sensitivity | 0.3656 | [0.3311, 0.4031]  — |
| Specificity | 0.7195 | [0.6854, 0.7539]  — |
| MCC | 0.0908 | [0.0387, 0.1419]  — |
| R² | -0.1370 | [-0.1952, -0.0867]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1368 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5623 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2862 | < 0.05 |
| MCE | 0.4221 | < 0.10 |
| Brier Score | 0.3483 | < 0.20 |
| Log-Loss | 1.1723 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0709 | proche 0 = pas de biais systématique |
| LoA lower | -6.5442 | limite inférieure d'accord |
| LoA upper | +6.4025 | limite supérieure d'accord |
| LoA width | ±6.4733 | < ±2 pts : excellent |
| % dans LoA | 97.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0647 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.2046 | 0.3101 | 151.6% | 🔴 unstable |
| AUC ROC | 0.5787 | 0.0760 | 13.1% | 🟢 stable |
| MAE | 2.8154 | 0.2842 | 10.1% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5623 |
| CI 95% | [0.5325, 0.5920] |
| p-value | 0.000041 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.57


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 15:57*
