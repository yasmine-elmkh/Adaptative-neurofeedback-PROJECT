# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:19


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4946 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9060 | Erreur quadratique moyenne |
| R² | 0.1197 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6617 | 0.500 |
| PR-AUC | 0.6390 | 0.517 |
| Sensitivity (TPR) | 0.5497 | 0.500 |
| Specificity (TNR) | 0.6562 | 0.500 |
| PPV (Precision) | 0.6308 | — |
| NPV | 0.5770 | — |
| Balanced Accuracy | 0.6030 | 0.500 |
| MCC | 0.2068 | 0.000 |
| G-Mean | 0.6006 | 0.500 |
| F1 macro | 0.6007 | 0.500 |
| LR+ | 1.599 | >10 = très utile |
| LR− | 0.686 | <0.1 = très utile |
| Cohen κ | 0.2050 | 0.000 |
| Brier Score | 0.2716 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6614 | [0.6416, 0.6823]  ✅ |
| F1 macro | 0.6005 | [0.5821, 0.6179]  ✅ |
| Sensitivity | 0.5498 | [0.5241, 0.5755]  — |
| Specificity | 0.6557 | [0.6292, 0.6821]  — |
| MCC | 0.2064 | [0.1687, 0.2438]  — |
| R² | 0.1191 | [0.0906, 0.1475]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1197 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6617 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1977 | < 0.05 |
| MCE | 0.2844 | < 0.10 |
| Brier Score | 0.2716 | < 0.20 |
| Log-Loss | 0.8218 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0028 | proche 0 = pas de biais systématique |
| LoA lower | -5.6996 | limite inférieure d'accord |
| LoA upper | +5.6941 | limite supérieure d'accord |
| LoA width | ±5.6969 | < ±2 pts : excellent |
| % dans LoA | 98.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2060 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0737 | 0.1779 | 241.3% | 🔴 unstable |
| AUC ROC | 0.6583 | 0.0750 | 11.4% | 🟢 stable |
| MAE | 2.4886 | 0.1918 | 7.7% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6595 |
| CI 95% | [0.6396, 0.6795] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.44 et 0.66


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:19*
