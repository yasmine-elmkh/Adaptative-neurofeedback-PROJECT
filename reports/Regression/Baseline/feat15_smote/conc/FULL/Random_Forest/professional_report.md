# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 16:57


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5676 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0023 | Erreur quadratique moyenne |
| R² | 0.0604 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6246 | 0.500 |
| PR-AUC | 0.6128 | 0.517 |
| Sensitivity (TPR) | 0.6274 | 0.500 |
| Specificity (TNR) | 0.5429 | 0.500 |
| PPV (Precision) | 0.5952 | — |
| NPV | 0.5763 | — |
| Balanced Accuracy | 0.5852 | 0.500 |
| MCC | 0.1709 | 0.000 |
| G-Mean | 0.5836 | 0.500 |
| F1 macro | 0.5850 | 0.500 |
| LR+ | 1.373 | >10 = très utile |
| LR− | 0.686 | <0.1 = très utile |
| Cohen κ | 0.1706 | 0.000 |
| Brier Score | 0.2820 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6248 | [0.6106, 0.6396]  ✅ |
| F1 macro | 0.5848 | [0.5721, 0.5979]  ✅ |
| Sensitivity | 0.6271 | [0.6098, 0.6464]  — |
| Specificity | 0.5428 | [0.5255, 0.5625]  — |
| MCC | 0.1705 | [0.1452, 0.1973]  — |
| R² | 0.0609 | [0.0387, 0.0829]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0604 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6246 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1937 | < 0.05 |
| MCE | 0.2948 | < 0.10 |
| Brier Score | 0.2820 | < 0.20 |
| Log-Loss | 0.8519 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0012 | proche 0 = pas de biais systématique |
| LoA lower | -5.8862 | limite inférieure d'accord |
| LoA upper | +5.8837 | limite supérieure d'accord |
| LoA width | ±5.8849 | < ±2 pts : excellent |
| % dans LoA | 97.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1598 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0143 | 0.1606 | 1122.1% | 🔴 unstable |
| AUC ROC | 0.6209 | 0.0581 | 9.4% | 🟢 stable |
| MAE | 2.5819 | 0.2445 | 9.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6228 |
| CI 95% | [0.6083, 0.6372] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:57*
