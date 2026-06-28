# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `A`  |  **Date :** 2026-06-21 18:15


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2475 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7027 | Erreur quadratique moyenne |
| R² | -0.2885 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5164 | 0.500 |
| PR-AUC | 0.4277 | 0.422 |
| Sensitivity (TPR) | 0.5188 | 0.500 |
| Specificity (TNR) | 0.5082 | 0.500 |
| PPV (Precision) | 0.4349 | — |
| NPV | 0.5914 | — |
| Balanced Accuracy | 0.5135 | 0.500 |
| MCC | 0.0266 | 0.000 |
| G-Mean | 0.5135 | 0.500 |
| F1 macro | 0.5099 | 0.500 |
| LR+ | 1.055 | >10 = très utile |
| LR− | 0.947 | <0.1 = très utile |
| Cohen κ | 0.0263 | 0.000 |
| Brier Score | 0.3347 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5082 | [0.4791, 0.5397]  — |
| F1 macro | 0.5034 | [0.4818, 0.5257]  — |
| Sensitivity | 0.2527 | [0.2177, 0.2894]  — |
| Specificity | 0.7557 | [0.7333, 0.7779]  — |
| MCC | 0.0088 | [-0.0336, 0.0543]  — |
| R² | -0.2904 | [-0.3468, -0.2335]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2885 | p=0.0780 | ❌ ns |
| AUC ROC | 0.5090 | p=0.2460 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2172 | < 0.05 |
| MCE | 0.7533 | < 0.10 |
| Brier Score | 0.2768 | < 0.20 |
| Log-Loss | 0.8743 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4518 | proche 0 = pas de biais systématique |
| LoA lower | -4.7722 | limite inférieure d'accord |
| LoA upper | +5.6758 | limite supérieure d'accord |
| LoA width | ±5.2240 | < ±2 pts : excellent |
| % dans LoA | 95.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0008 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.8641 | 1.7031 | 197.1% | 🔴 unstable |
| AUC ROC | 0.5225 | 0.0656 | 12.5% | 🟢 stable |
| MAE | 2.2473 | 0.4558 | 20.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5090 |
| CI 95% | [0.4811, 0.5369] |
| p-value | 0.526615 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.28


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:15*
