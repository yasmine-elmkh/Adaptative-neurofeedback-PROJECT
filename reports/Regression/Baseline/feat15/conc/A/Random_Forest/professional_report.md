# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:01


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5796 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0017 | Erreur quadratique moyenne |
| R² | 0.0608 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6149 | 0.500 |
| PR-AUC | 0.5949 | 0.518 |
| Sensitivity (TPR) | 0.7259 | 0.500 |
| Specificity (TNR) | 0.4563 | 0.500 |
| PPV (Precision) | 0.5892 | — |
| NPV | 0.6078 | — |
| Balanced Accuracy | 0.5911 | 0.500 |
| MCC | 0.1894 | 0.000 |
| G-Mean | 0.5755 | 0.500 |
| F1 macro | 0.5858 | 0.500 |
| LR+ | 1.335 | >10 = très utile |
| LR− | 0.601 | <0.1 = très utile |
| Cohen κ | 0.1838 | 0.000 |
| Brier Score | 0.2804 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6121 | [0.5814, 0.6390]  ✅ |
| F1 macro | 0.5479 | [0.5223, 0.5716]  ✅ |
| Sensitivity | 0.3936 | [0.3577, 0.4294]  — |
| Specificity | 0.7339 | [0.7011, 0.7691]  — |
| MCC | 0.1354 | [0.0834, 0.1824]  — |
| R² | 0.0606 | [0.0181, 0.0977]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0608 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6113 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2048 | < 0.05 |
| MCE | 0.3326 | < 0.10 |
| Brier Score | 0.2954 | < 0.20 |
| Log-Loss | 0.8922 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0216 | proche 0 = pas de biais systématique |
| LoA lower | -5.9068 | limite inférieure d'accord |
| LoA upper | +5.8636 | limite supérieure d'accord |
| LoA width | ±5.8852 | < ±2 pts : excellent |
| % dans LoA | 98.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1336 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0092 | 0.2034 | 2217.2% | 🔴 unstable |
| AUC ROC | 0.6204 | 0.0752 | 12.1% | 🟢 stable |
| MAE | 2.5981 | 0.2984 | 11.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6113 |
| CI 95% | [0.5821, 0.6404] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:01*
