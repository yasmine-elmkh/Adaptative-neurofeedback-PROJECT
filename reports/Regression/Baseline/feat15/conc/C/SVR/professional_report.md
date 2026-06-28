# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:14


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5935 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1275 | Erreur quadratique moyenne |
| R² | -0.0196 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6227 | 0.500 |
| PR-AUC | 0.6156 | 0.519 |
| Sensitivity (TPR) | 0.7533 | 0.500 |
| Specificity (TNR) | 0.4508 | 0.500 |
| PPV (Precision) | 0.5971 | — |
| NPV | 0.6284 | — |
| Balanced Accuracy | 0.6020 | 0.500 |
| MCC | 0.2145 | 0.000 |
| G-Mean | 0.5827 | 0.500 |
| F1 macro | 0.5956 | 0.500 |
| LR+ | 1.372 | >10 = très utile |
| LR− | 0.547 | <0.1 = très utile |
| Cohen κ | 0.2062 | 0.000 |
| Brier Score | 0.3073 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6209 | [0.6053, 0.6373]  ✅ |
| F1 macro | 0.5555 | [0.5409, 0.5698]  ✅ |
| Sensitivity | 0.4511 | [0.4312, 0.4711]  — |
| Specificity | 0.6749 | [0.6526, 0.6960]  — |
| MCC | 0.1291 | [0.0990, 0.1576]  — |
| R² | -0.0194 | [-0.0534, 0.0143]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0196 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6207 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2602 | < 0.05 |
| MCE | 0.3643 | < 0.10 |
| Brier Score | 0.3148 | < 0.20 |
| Log-Loss | 1.0571 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0174 | proche 0 = pas de biais systématique |
| LoA lower | -6.1479 | limite inférieure d'accord |
| LoA upper | +6.1131 | limite supérieure d'accord |
| LoA width | ±6.1305 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1705 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0754 | 0.2208 | 292.9% | 🔴 unstable |
| AUC ROC | 0.6464 | 0.0841 | 13.0% | 🟢 stable |
| MAE | 2.6060 | 0.2691 | 10.3% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6207 |
| CI 95% | [0.6039, 0.6374] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:14*
