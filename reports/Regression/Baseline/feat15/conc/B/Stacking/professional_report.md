# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:13


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5857 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0931 | Erreur quadratique moyenne |
| R² | 0.0027 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6361 | 0.500 |
| PR-AUC | 0.6351 | 0.541 |
| Sensitivity (TPR) | 0.8136 | 0.500 |
| Specificity (TNR) | 0.3760 | 0.500 |
| PPV (Precision) | 0.6059 | — |
| NPV | 0.6311 | — |
| Balanced Accuracy | 0.5948 | 0.500 |
| MCC | 0.2120 | 0.000 |
| G-Mean | 0.5531 | 0.500 |
| F1 macro | 0.5829 | 0.500 |
| LR+ | 1.304 | >10 = très utile |
| LR− | 0.496 | <0.1 = très utile |
| Cohen κ | 0.1956 | 0.000 |
| Brier Score | 0.2946 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6207 | [0.6022, 0.6402]  ✅ |
| F1 macro | 0.5659 | [0.5480, 0.5848]  ✅ |
| Sensitivity | 0.4212 | [0.3939, 0.4456]  — |
| Specificity | 0.7376 | [0.7137, 0.7615]  — |
| MCC | 0.1670 | [0.1338, 0.2057]  — |
| R² | 0.0022 | [-0.0345, 0.0395]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0027 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6206 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2483 | < 0.05 |
| MCE | 0.3831 | < 0.10 |
| Brier Score | 0.3148 | < 0.20 |
| Log-Loss | 1.0414 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1683 | proche 0 = pas de biais systématique |
| LoA lower | -6.2228 | limite inférieure d'accord |
| LoA upper | +5.8862 | limite supérieure d'accord |
| LoA width | ±6.0545 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0536 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0443 | 0.1790 | 404.1% | 🔴 unstable |
| AUC ROC | 0.6382 | 0.0757 | 11.9% | 🟢 stable |
| MAE | 2.5914 | 0.2037 | 7.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6206 |
| CI 95% | [0.6001, 0.6411] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:13*
