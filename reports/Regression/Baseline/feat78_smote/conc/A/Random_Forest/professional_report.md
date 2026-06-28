# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:03


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5613 | Erreur absolue moyenne (0-10) |
| RMSE | 2.9974 | Erreur quadratique moyenne |
| R² | 0.0635 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6184 | 0.500 |
| PR-AUC | 0.6100 | 0.517 |
| Sensitivity (TPR) | 0.5592 | 0.500 |
| Specificity (TNR) | 0.5858 | 0.500 |
| PPV (Precision) | 0.5905 | — |
| NPV | 0.5543 | — |
| Balanced Accuracy | 0.5725 | 0.500 |
| MCC | 0.1449 | 0.000 |
| G-Mean | 0.5723 | 0.500 |
| F1 macro | 0.5720 | 0.500 |
| LR+ | 1.350 | >10 = très utile |
| LR− | 0.753 | <0.1 = très utile |
| Cohen κ | 0.1447 | 0.000 |
| Brier Score | 0.2883 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6190 | [0.5911, 0.6456]  ✅ |
| F1 macro | 0.5724 | [0.5476, 0.5972]  ✅ |
| Sensitivity | 0.5593 | [0.5220, 0.5942]  — |
| Specificity | 0.5867 | [0.5520, 0.6254]  — |
| MCC | 0.1460 | [0.0969, 0.1955]  — |
| R² | 0.0631 | [0.0200, 0.1020]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0635 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6184 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2064 | < 0.05 |
| MCE | 0.3415 | < 0.10 |
| Brier Score | 0.2883 | < 0.20 |
| Log-Loss | 0.8573 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0051 | proche 0 = pas de biais systématique |
| LoA lower | -5.8820 | limite inférieure d'accord |
| LoA upper | +5.8719 | limite supérieure d'accord |
| LoA width | ±5.8770 | < ±2 pts : excellent |
| % dans LoA | 98.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1609 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0117 | 0.2364 | 2020.0% | 🔴 unstable |
| AUC ROC | 0.6231 | 0.0860 | 13.8% | 🟢 stable |
| MAE | 2.5686 | 0.3086 | 12.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6165 |
| CI 95% | [0.5874, 0.6455] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:03*
