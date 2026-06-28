# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 16:55


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
| AUC ROC | 0.6260 | 0.500 |
| PR-AUC | 0.6158 | 0.518 |
| Sensitivity (TPR) | 0.7015 | 0.500 |
| Specificity (TNR) | 0.4763 | 0.500 |
| PPV (Precision) | 0.5900 | — |
| NPV | 0.5976 | — |
| Balanced Accuracy | 0.5889 | 0.500 |
| MCC | 0.1827 | 0.000 |
| G-Mean | 0.5780 | 0.500 |
| F1 macro | 0.5855 | 0.500 |
| LR+ | 1.340 | >10 = très utile |
| LR− | 0.627 | <0.1 = très utile |
| Cohen κ | 0.1791 | 0.000 |
| Brier Score | 0.2835 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6229 | [0.6092, 0.6376]  ✅ |
| F1 macro | 0.5596 | [0.5465, 0.5715]  ✅ |
| Sensitivity | 0.4227 | [0.4061, 0.4409]  — |
| Specificity | 0.7210 | [0.7052, 0.7374]  — |
| MCC | 0.1502 | [0.1245, 0.1744]  — |
| R² | 0.0609 | [0.0387, 0.0829]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0604 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6228 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2162 | < 0.05 |
| MCE | 0.3629 | < 0.10 |
| Brier Score | 0.2963 | < 0.20 |
| Log-Loss | 0.9206 | minimiser |

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
| AUC ROC | 0.6481 | 0.0855 | 13.2% | 🟢 stable |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:55*
