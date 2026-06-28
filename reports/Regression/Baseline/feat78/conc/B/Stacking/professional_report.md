# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:31


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7066 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1187 | Erreur quadratique moyenne |
| R² | -0.0139 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5773 | 0.500 |
| PR-AUC | 0.5766 | 0.517 |
| Sensitivity (TPR) | 0.4633 | 0.500 |
| Specificity (TNR) | 0.6533 | 0.500 |
| PPV (Precision) | 0.5881 | — |
| NPV | 0.5326 | — |
| Balanced Accuracy | 0.5583 | 0.500 |
| MCC | 0.1186 | 0.000 |
| G-Mean | 0.5502 | 0.500 |
| F1 macro | 0.5525 | 0.500 |
| LR+ | 1.336 | >10 = très utile |
| LR− | 0.822 | <0.1 = très utile |
| Cohen κ | 0.1158 | 0.000 |
| Brier Score | 0.3016 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5776 | [0.5571, 0.5983]  ✅ |
| F1 macro | 0.5114 | [0.4930, 0.5293]  — |
| Sensitivity | 0.3086 | [0.2851, 0.3318]  — |
| Specificity | 0.7741 | [0.7517, 0.7946]  — |
| MCC | 0.0933 | [0.0547, 0.1249]  — |
| R² | -0.0137 | [-0.0426, 0.0148]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0139 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5775 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2368 | < 0.05 |
| MCE | 0.3832 | < 0.10 |
| Brier Score | 0.3179 | < 0.20 |
| Log-Loss | 0.9961 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1050 | proche 0 = pas de biais systématique |
| LoA lower | -6.2152 | limite inférieure d'accord |
| LoA upper | +6.0052 | limite supérieure d'accord |
| LoA width | ±6.1102 | < ±2 pts : excellent |
| % dans LoA | 98.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0419 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0761 | 0.2138 | 280.7% | 🔴 unstable |
| AUC ROC | 0.5851 | 0.1112 | 19.0% | 🟡 moderate |
| MAE | 2.7176 | 0.2123 | 7.8% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5775 |
| CI 95% | [0.5566, 0.5984] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:31*
