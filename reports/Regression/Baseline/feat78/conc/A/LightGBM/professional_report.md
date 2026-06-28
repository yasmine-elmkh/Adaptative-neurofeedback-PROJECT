# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:07


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7343 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1714 | Erreur quadratique moyenne |
| R² | -0.0484 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5692 | 0.500 |
| PR-AUC | 0.5842 | 0.518 |
| Sensitivity (TPR) | 0.6187 | 0.500 |
| Specificity (TNR) | 0.5015 | 0.500 |
| PPV (Precision) | 0.5714 | — |
| NPV | 0.5504 | — |
| Balanced Accuracy | 0.5601 | 0.500 |
| MCC | 0.1210 | 0.000 |
| G-Mean | 0.5570 | 0.500 |
| F1 macro | 0.5595 | 0.500 |
| LR+ | 1.241 | >10 = très utile |
| LR− | 0.760 | <0.1 = très utile |
| Cohen κ | 0.1206 | 0.000 |
| Brier Score | 0.3019 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5682 | [0.5399, 0.5992]  ✅ |
| F1 macro | 0.5118 | [0.4854, 0.5381]  — |
| Sensitivity | 0.3197 | [0.2865, 0.3520]  — |
| Specificity | 0.7575 | [0.7238, 0.7891]  — |
| MCC | 0.0858 | [0.0370, 0.1365]  — |
| R² | -0.0494 | [-0.0882, -0.0062]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0484 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5682 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2498 | < 0.05 |
| MCE | 0.3980 | < 0.10 |
| Brier Score | 0.3239 | < 0.20 |
| Log-Loss | 0.9902 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0016 | proche 0 = pas de biais systématique |
| LoA lower | -6.2198 | limite inférieure d'accord |
| LoA upper | +6.2165 | limite supérieure d'accord |
| LoA width | ±6.2182 | < ±2 pts : excellent |
| % dans LoA | 98.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0615 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0980 | 0.1672 | 170.6% | 🔴 unstable |
| AUC ROC | 0.5749 | 0.0706 | 12.3% | 🟢 stable |
| MAE | 2.7394 | 0.2673 | 9.8% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5682 |
| CI 95% | [0.5385, 0.5979] |
| p-value | 0.000007 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:07*
