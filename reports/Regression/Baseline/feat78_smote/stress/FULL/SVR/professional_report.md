# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 21:36


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3354 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8090 | Erreur quadratique moyenne |
| R² | -0.3919 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5190 | 0.500 |
| PR-AUC | 0.2911 | 0.287 |
| Sensitivity (TPR) | 0.3929 | 0.500 |
| Specificity (TNR) | 0.6166 | 0.500 |
| PPV (Precision) | 0.2924 | — |
| NPV | 0.7158 | — |
| Balanced Accuracy | 0.5048 | 0.500 |
| MCC | 0.0089 | 0.000 |
| G-Mean | 0.4922 | 0.500 |
| F1 macro | 0.4989 | 0.500 |
| LR+ | 1.025 | >10 = très utile |
| LR− | 0.984 | <0.1 = très utile |
| Cohen κ | 0.0087 | 0.000 |
| Brier Score | 0.3015 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5190 | [0.5057, 0.5321]  ✅ |
| F1 macro | 0.4989 | [0.4887, 0.5099]  — |
| Sensitivity | 0.3928 | [0.3734, 0.4097]  — |
| Specificity | 0.6167 | [0.6052, 0.6292]  — |
| MCC | 0.0089 | [-0.0118, 0.0304]  — |
| R² | -0.3917 | [-0.4228, -0.3582]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3919 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5190 | p=0.0060 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2555 | < 0.05 |
| MCE | 0.6812 | < 0.10 |
| Brier Score | 0.3015 | < 0.20 |
| Log-Loss | 0.9220 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.8216 | proche 0 = pas de biais systématique |
| LoA lower | -4.4436 | limite inférieure d'accord |
| LoA upper | +6.0868 | limite supérieure d'accord |
| LoA width | ±5.2652 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.0946 | 2.0536 | 187.6% | 🔴 unstable |
| AUC ROC | 0.5287 | 0.0839 | 15.9% | 🟡 moderate |
| MAE | 2.3352 | 0.4414 | 18.9% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5190 |
| CI 95% | [0.5053, 0.5328] |
| p-value | 0.006727 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.26 et 0.28


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 21:36*
