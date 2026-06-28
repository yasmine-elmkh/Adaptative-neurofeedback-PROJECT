# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:22


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7163 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1341 | Erreur quadratique moyenne |
| R² | -0.0239 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5919 | 0.500 |
| PR-AUC | 0.5765 | 0.519 |
| Sensitivity (TPR) | 0.7591 | 0.500 |
| Specificity (TNR) | 0.3867 | 0.500 |
| PPV (Precision) | 0.5722 | — |
| NPV | 0.5977 | — |
| Balanced Accuracy | 0.5729 | 0.500 |
| MCC | 0.1574 | 0.000 |
| G-Mean | 0.5418 | 0.500 |
| F1 macro | 0.5611 | 0.500 |
| LR+ | 1.238 | >10 = très utile |
| LR− | 0.623 | <0.1 = très utile |
| Cohen κ | 0.1478 | 0.000 |
| Brier Score | 0.2934 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5913 | [0.5698, 0.6126]  ✅ |
| F1 macro | 0.5605 | [0.5413, 0.5795]  ✅ |
| Sensitivity | 0.7588 | [0.7370, 0.7794]  — |
| Specificity | 0.3863 | [0.3593, 0.4136]  — |
| MCC | 0.1565 | [0.1177, 0.1938]  — |
| R² | -0.0251 | [-0.0551, 0.0050]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0239 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5919 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1926 | < 0.05 |
| MCE | 0.3537 | < 0.10 |
| Brier Score | 0.2934 | < 0.20 |
| Log-Loss | 0.9064 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0456 | proche 0 = pas de biais systématique |
| LoA lower | -6.0976 | limite inférieure d'accord |
| LoA upper | +6.1889 | limite supérieure d'accord |
| LoA width | ±6.1433 | < ±2 pts : excellent |
| % dans LoA | 98.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0642 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0640 | 0.1304 | 203.8% | 🔴 unstable |
| AUC ROC | 0.6224 | 0.0891 | 14.3% | 🟢 stable |
| MAE | 2.7086 | 0.2235 | 8.3% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5876 |
| CI 95% | [0.5667, 0.6085] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.57


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:22*
