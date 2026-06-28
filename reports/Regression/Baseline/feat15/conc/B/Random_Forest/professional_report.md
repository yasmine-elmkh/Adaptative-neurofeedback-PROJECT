# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:11


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5378 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9602 | Erreur quadratique moyenne |
| R² | 0.0865 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6344 | 0.500 |
| PR-AUC | 0.6168 | 0.518 |
| Sensitivity (TPR) | 0.7280 | 0.500 |
| Specificity (TNR) | 0.4781 | 0.500 |
| PPV (Precision) | 0.5998 | — |
| NPV | 0.6206 | — |
| Balanced Accuracy | 0.6030 | 0.500 |
| MCC | 0.2131 | 0.000 |
| G-Mean | 0.5900 | 0.500 |
| F1 macro | 0.5989 | 0.500 |
| LR+ | 1.395 | >10 = très utile |
| LR− | 0.569 | <0.1 = très utile |
| Cohen κ | 0.2077 | 0.000 |
| Brier Score | 0.2749 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6317 | [0.6131, 0.6512]  ✅ |
| F1 macro | 0.5524 | [0.5352, 0.5708]  ✅ |
| Sensitivity | 0.3884 | [0.3629, 0.4132]  — |
| Specificity | 0.7518 | [0.7277, 0.7726]  — |
| MCC | 0.1502 | [0.1173, 0.1883]  — |
| R² | 0.0863 | [0.0571, 0.1149]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0865 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6317 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2177 | < 0.05 |
| MCE | 0.3296 | < 0.10 |
| Brier Score | 0.2936 | < 0.20 |
| Log-Loss | 0.8975 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0478 | proche 0 = pas de biais systématique |
| LoA lower | -5.8501 | limite inférieure d'accord |
| LoA upper | +5.7545 | limite supérieure d'accord |
| LoA width | ±5.8023 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1389 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0432 | 0.1554 | 359.9% | 🔴 unstable |
| AUC ROC | 0.6553 | 0.0674 | 10.3% | 🟢 stable |
| MAE | 2.5448 | 0.2049 | 8.1% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6317 |
| CI 95% | [0.6114, 0.6521] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:11*
