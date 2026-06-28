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
| AUC ROC | 0.6331 | 0.500 |
| PR-AUC | 0.6145 | 0.517 |
| Sensitivity (TPR) | 0.5985 | 0.500 |
| Specificity (TNR) | 0.5830 | 0.500 |
| PPV (Precision) | 0.6059 | — |
| NPV | 0.5754 | — |
| Balanced Accuracy | 0.5907 | 0.500 |
| MCC | 0.1814 | 0.000 |
| G-Mean | 0.5907 | 0.500 |
| F1 macro | 0.5907 | 0.500 |
| LR+ | 1.435 | >10 = très utile |
| LR− | 0.689 | <0.1 = très utile |
| Cohen κ | 0.1814 | 0.000 |
| Brier Score | 0.2743 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6331 | [0.6146, 0.6527]  ✅ |
| F1 macro | 0.5910 | [0.5736, 0.6083]  ✅ |
| Sensitivity | 0.5991 | [0.5753, 0.6258]  — |
| Specificity | 0.5832 | [0.5572, 0.6088]  — |
| MCC | 0.1822 | [0.1472, 0.2166]  — |
| R² | 0.0863 | [0.0571, 0.1149]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0865 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6331 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1768 | < 0.05 |
| MCE | 0.2868 | < 0.10 |
| Brier Score | 0.2743 | < 0.20 |
| Log-Loss | 0.8186 | minimiser |

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
| AUC ROC | 0.6368 | 0.0672 | 10.5% | 🟢 stable |
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
