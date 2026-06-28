# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:25


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5413 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9771 | Erreur quadratique moyenne |
| R² | 0.0761 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6353 | 0.500 |
| PR-AUC | 0.6243 | 0.523 |
| Sensitivity (TPR) | 0.8082 | 0.500 |
| Specificity (TNR) | 0.3849 | 0.500 |
| PPV (Precision) | 0.5901 | — |
| NPV | 0.6469 | — |
| Balanced Accuracy | 0.5966 | 0.500 |
| MCC | 0.2139 | 0.000 |
| G-Mean | 0.5577 | 0.500 |
| F1 macro | 0.5824 | 0.500 |
| LR+ | 1.314 | >10 = très utile |
| LR− | 0.498 | <0.1 = très utile |
| Cohen κ | 0.1966 | 0.000 |
| Brier Score | 0.2891 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6326 | [0.6160, 0.6497]  ✅ |
| F1 macro | 0.5641 | [0.5495, 0.5779]  ✅ |
| Sensitivity | 0.4141 | [0.3920, 0.4330]  — |
| Specificity | 0.7431 | [0.7230, 0.7618]  — |
| MCC | 0.1661 | [0.1374, 0.1942]  — |
| R² | 0.0761 | [0.0509, 0.1047]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0761 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6324 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2230 | < 0.05 |
| MCE | 0.3731 | < 0.10 |
| Brier Score | 0.2982 | < 0.20 |
| Log-Loss | 0.9267 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0434 | proche 0 = pas de biais systématique |
| LoA lower | -5.8786 | limite inférieure d'accord |
| LoA upper | +5.7917 | limite supérieure d'accord |
| LoA width | ±5.8352 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1454 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0300 | 0.1915 | 637.7% | 🔴 unstable |
| AUC ROC | 0.6382 | 0.0742 | 11.6% | 🟢 stable |
| MAE | 2.5477 | 0.2111 | 8.3% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6324 |
| CI 95% | [0.6158, 0.6490] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.64


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:25*
