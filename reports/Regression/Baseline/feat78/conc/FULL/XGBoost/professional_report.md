# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 18:07


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6515 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0550 | Erreur quadratique moyenne |
| R² | 0.0271 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5926 | 0.500 |
| PR-AUC | 0.5898 | 0.517 |
| Sensitivity (TPR) | 0.5075 | 0.500 |
| Specificity (TNR) | 0.6203 | 0.500 |
| PPV (Precision) | 0.5881 | — |
| NPV | 0.5410 | — |
| Balanced Accuracy | 0.5639 | 0.500 |
| MCC | 0.1284 | 0.000 |
| G-Mean | 0.5611 | 0.500 |
| F1 macro | 0.5614 | 0.500 |
| LR+ | 1.336 | >10 = très utile |
| LR− | 0.794 | <0.1 = très utile |
| Cohen κ | 0.1272 | 0.000 |
| Brier Score | 0.2913 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5928 | [0.5784, 0.6063]  ✅ |
| F1 macro | 0.5301 | [0.5174, 0.5426]  ✅ |
| Sensitivity | 0.3445 | [0.3278, 0.3618]  — |
| Specificity | 0.7634 | [0.7485, 0.7787]  — |
| MCC | 0.1186 | [0.0931, 0.1429]  — |
| R² | 0.0271 | [0.0060, 0.0451]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0271 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5926 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2247 | < 0.05 |
| MCE | 0.3728 | < 0.10 |
| Brier Score | 0.3083 | < 0.20 |
| Log-Loss | 0.9294 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0232 | proche 0 = pas de biais systématique |
| LoA lower | -6.0113 | limite inférieure d'accord |
| LoA upper | +5.9649 | limite supérieure d'accord |
| LoA width | ±5.9881 | < ±2 pts : excellent |
| % dans LoA | 98.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0961 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0231 | 0.1445 | 624.8% | 🔴 unstable |
| AUC ROC | 0.6133 | 0.0673 | 11.0% | 🟢 stable |
| MAE | 2.6610 | 0.2263 | 8.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5926 |
| CI 95% | [0.5779, 0.6073] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:07*
