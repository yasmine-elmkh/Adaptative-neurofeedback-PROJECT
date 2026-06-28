# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:37


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6629 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1330 | Erreur quadratique moyenne |
| R² | -0.0232 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5878 | 0.500 |
| PR-AUC | 0.5813 | 0.522 |
| Sensitivity (TPR) | 0.7813 | 0.500 |
| Specificity (TNR) | 0.3838 | 0.500 |
| PPV (Precision) | 0.5808 | — |
| NPV | 0.6163 | — |
| Balanced Accuracy | 0.5826 | 0.500 |
| MCC | 0.1804 | 0.000 |
| G-Mean | 0.5476 | 0.500 |
| F1 macro | 0.5697 | 0.500 |
| LR+ | 1.268 | >10 = très utile |
| LR− | 0.570 | <0.1 = très utile |
| Cohen κ | 0.1678 | 0.000 |
| Brier Score | 0.3128 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5842 | [0.5639, 0.6042]  ✅ |
| F1 macro | 0.5189 | [0.5012, 0.5380]  ✅ |
| Sensitivity | 0.3794 | [0.3547, 0.4034]  — |
| Specificity | 0.6859 | [0.6601, 0.7117]  — |
| MCC | 0.0685 | [0.0319, 0.1063]  — |
| R² | -0.0225 | [-0.0549, 0.0100]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0232 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5839 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2717 | < 0.05 |
| MCE | 0.3735 | < 0.10 |
| Brier Score | 0.3266 | < 0.20 |
| Log-Loss | 1.0304 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0363 | proche 0 = pas de biais systématique |
| LoA lower | -6.1777 | limite inférieure d'accord |
| LoA upper | +6.1051 | limite supérieure d'accord |
| LoA width | ±6.1414 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1098 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0660 | 0.2256 | 341.7% | 🔴 unstable |
| AUC ROC | 0.6076 | 0.0719 | 11.8% | 🟢 stable |
| MAE | 2.6618 | 0.2792 | 10.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5839 |
| CI 95% | [0.5629, 0.6048] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.56


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:37*
