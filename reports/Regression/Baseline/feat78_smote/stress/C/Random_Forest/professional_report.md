# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `C`  |  **Date :** 2026-06-21 20:30


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1614 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5711 | Erreur quadratique moyenne |
| R² | -0.1661 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4946 | 0.500 |
| PR-AUC | 0.4231 | 0.414 |
| Sensitivity (TPR) | 0.1479 | 0.500 |
| Specificity (TNR) | 0.8637 | 0.500 |
| PPV (Precision) | 0.4338 | — |
| NPV | 0.5894 | — |
| Balanced Accuracy | 0.5058 | 0.500 |
| MCC | 0.0163 | 0.000 |
| G-Mean | 0.3574 | 0.500 |
| F1 macro | 0.4606 | 0.500 |
| LR+ | 1.085 | >10 = très utile |
| LR− | 0.987 | <0.1 = très utile |
| Cohen κ | 0.0128 | 0.000 |
| Brier Score | 0.3123 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4945 | [0.4791, 0.5093]  — |
| F1 macro | 0.4608 | [0.4491, 0.4726]  — |
| Sensitivity | 0.1481 | [0.1359, 0.1620]  — |
| Specificity | 0.8636 | [0.8521, 0.8751]  — |
| MCC | 0.0165 | [-0.0082, 0.0418]  — |
| R² | -0.1668 | [-0.1905, -0.1441]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1661 | p=0.8580 | ❌ ns |
| AUC ROC | 0.4946 | p=0.7660 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2380 | < 0.05 |
| MCE | 0.4578 | < 0.10 |
| Brier Score | 0.3123 | < 0.20 |
| Log-Loss | 0.9363 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1561 | proche 0 = pas de biais systématique |
| LoA lower | -4.8744 | limite inférieure d'accord |
| LoA upper | +5.1866 | limite supérieure d'accord |
| LoA width | ±5.0305 | < ±2 pts : excellent |
| % dans LoA | 95.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0007 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5065 | 0.8803 | 173.8% | 🔴 unstable |
| AUC ROC | 0.5010 | 0.0656 | 13.1% | 🟢 stable |
| MAE | 2.1612 | 0.6285 | 29.1% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5143 |
| CI 95% | [0.4979, 0.5308] |
| p-value | 0.088217 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.31


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:30*
