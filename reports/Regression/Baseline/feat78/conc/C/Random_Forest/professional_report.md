# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:59


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7029 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0766 | Erreur quadratique moyenne |
| R² | 0.0133 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5727 | 0.500 |
| PR-AUC | 0.5685 | 0.518 |
| Sensitivity (TPR) | 0.6771 | 0.500 |
| Specificity (TNR) | 0.4388 | 0.500 |
| PPV (Precision) | 0.5645 | — |
| NPV | 0.5584 | — |
| Balanced Accuracy | 0.5579 | 0.500 |
| MCC | 0.1193 | 0.000 |
| G-Mean | 0.5451 | 0.500 |
| F1 macro | 0.5535 | 0.500 |
| LR+ | 1.206 | >10 = très utile |
| LR− | 0.736 | <0.1 = très utile |
| Cohen κ | 0.1167 | 0.000 |
| Brier Score | 0.2830 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5709 | [0.5537, 0.5894]  ✅ |
| F1 macro | 0.4862 | [0.4714, 0.5005]  — |
| Sensitivity | 0.2564 | [0.2376, 0.2742]  — |
| Specificity | 0.8000 | [0.7805, 0.8171]  — |
| MCC | 0.0670 | [0.0359, 0.0948]  — |
| R² | 0.0132 | [-0.0059, 0.0330]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0133 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5707 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2235 | < 0.05 |
| MCE | 0.3673 | < 0.10 |
| Brier Score | 0.3097 | < 0.20 |
| Log-Loss | 0.9118 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0265 | proche 0 = pas de biais systématique |
| LoA lower | -6.0572 | limite inférieure d'accord |
| LoA upper | +6.0042 | limite supérieure d'accord |
| LoA width | ±6.0307 | < ±2 pts : excellent |
| % dans LoA | 99.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0615 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0301 | 0.1199 | 398.5% | 🔴 unstable |
| AUC ROC | 0.5846 | 0.0422 | 7.2% | 🟢 stable |
| MAE | 2.7067 | 0.2519 | 9.3% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5707 |
| CI 95% | [0.5536, 0.5879] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.51 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:59*
