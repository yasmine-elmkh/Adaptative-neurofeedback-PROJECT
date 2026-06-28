# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:05


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.7296 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0826 | Erreur quadratique moyenne |
| R² | 0.0095 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5660 | 0.500 |
| PR-AUC | 0.5597 | 0.517 |
| Sensitivity (TPR) | 0.4497 | 0.500 |
| Specificity (TNR) | 0.6739 | 0.500 |
| PPV (Precision) | 0.5964 | — |
| NPV | 0.5334 | — |
| Balanced Accuracy | 0.5618 | 0.500 |
| MCC | 0.1267 | 0.000 |
| G-Mean | 0.5505 | 0.500 |
| F1 macro | 0.5541 | 0.500 |
| LR+ | 1.379 | >10 = très utile |
| LR− | 0.816 | <0.1 = très utile |
| Cohen κ | 0.1226 | 0.000 |
| Brier Score | 0.2815 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5654 | [0.5352, 0.5960]  ✅ |
| F1 macro | 0.4677 | [0.4429, 0.4943]  — |
| Sensitivity | 0.2038 | [0.1739, 0.2316]  — |
| Specificity | 0.8529 | [0.8274, 0.8786]  — |
| MCC | 0.0743 | [0.0219, 0.1226]  — |
| R² | 0.0089 | [-0.0148, 0.0347]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0095 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5650 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2436 | < 0.05 |
| MCE | 0.9011 | < 0.10 |
| Brier Score | 0.3130 | < 0.20 |
| Log-Loss | 0.8939 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0302 | proche 0 = pas de biais systématique |
| LoA lower | -6.0739 | limite inférieure d'accord |
| LoA upper | +6.0135 | limite supérieure d'accord |
| LoA width | ±6.0437 | < ±2 pts : excellent |
| % dans LoA | 99.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0427 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0350 | 0.1282 | 365.9% | 🔴 unstable |
| AUC ROC | 0.5743 | 0.0509 | 8.9% | 🟢 stable |
| MAE | 2.7292 | 0.2366 | 8.7% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5650 |
| CI 95% | [0.5352, 0.5947] |
| p-value | 0.000019 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.51 et 0.54


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:05*
