# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:41


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6989 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2772 | Erreur quadratique moyenne |
| R² | -0.1196 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6151 | 0.500 |
| PR-AUC | 0.5928 | 0.517 |
| Sensitivity (TPR) | 0.6175 | 0.500 |
| Specificity (TNR) | 0.5306 | 0.500 |
| PPV (Precision) | 0.5849 | — |
| NPV | 0.5642 | — |
| Balanced Accuracy | 0.5740 | 0.500 |
| MCC | 0.1486 | 0.000 |
| G-Mean | 0.5724 | 0.500 |
| F1 macro | 0.5738 | 0.500 |
| LR+ | 1.315 | >10 = très utile |
| LR− | 0.721 | <0.1 = très utile |
| Cohen κ | 0.1484 | 0.000 |
| Brier Score | 0.3192 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6152 | [0.5964, 0.6347]  ✅ |
| F1 macro | 0.5738 | [0.5551, 0.5903]  ✅ |
| Sensitivity | 0.6175 | [0.5923, 0.6424]  — |
| Specificity | 0.5307 | [0.5051, 0.5554]  — |
| MCC | 0.1487 | [0.1115, 0.1816]  — |
| R² | -0.1203 | [-0.1670, -0.0758]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1196 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6151 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2673 | < 0.05 |
| MCE | 0.3784 | < 0.10 |
| Brier Score | 0.3192 | < 0.20 |
| Log-Loss | 1.1170 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1629 | proche 0 = pas de biais systématique |
| LoA lower | -6.5794 | limite inférieure d'accord |
| LoA upper | +6.2537 | limite supérieure d'accord |
| LoA width | ±6.4165 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0673 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.1724 | 0.2674 | 155.2% | 🔴 unstable |
| AUC ROC | 0.6065 | 0.0777 | 12.8% | 🟢 stable |
| MAE | 2.7083 | 0.3489 | 12.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6136 |
| CI 95% | [0.5931, 0.6342] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:41*
