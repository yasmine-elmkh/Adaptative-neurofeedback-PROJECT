# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `C`  |  **Date :** 2026-06-21 21:44


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0828 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4337 | Erreur quadratique moyenne |
| R² | -0.0448 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4916 | 0.500 |
| PR-AUC | 0.4150 | 0.414 |
| Sensitivity (TPR) | 0.0719 | 0.500 |
| Specificity (TNR) | 0.9402 | 0.500 |
| PPV (Precision) | 0.4592 | — |
| NPV | 0.5892 | — |
| Balanced Accuracy | 0.5061 | 0.500 |
| MCC | 0.0242 | 0.000 |
| G-Mean | 0.2601 | 0.500 |
| F1 macro | 0.4244 | 0.500 |
| LR+ | 1.202 | >10 = très utile |
| LR− | 0.987 | <0.1 = très utile |
| Cohen κ | 0.0138 | 0.000 |
| Brier Score | 0.2755 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4795 | [0.4627, 0.4944]  — |
| F1 macro | 0.4293 | [0.4224, 0.4363]  — |
| Sensitivity | 0.0135 | [0.0082, 0.0188]  — |
| Specificity | 0.9900 | [0.9872, 0.9930]  — |
| MCC | 0.0150 | [-0.0106, 0.0422]  — |
| R² | -0.0453 | [-0.0547, -0.0365]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0448 | p=0.9060 | ❌ ns |
| AUC ROC | 0.4797 | p=0.9940 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1316 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2254 | < 0.20 |
| Log-Loss | 0.6860 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1726 | proche 0 = pas de biais systématique |
| LoA lower | -4.5859 | limite inférieure d'accord |
| LoA upper | +4.9310 | limite supérieure d'accord |
| LoA width | ±4.7584 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0003 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.4297 | 1.1579 | 269.5% | 🔴 unstable |
| AUC ROC | 0.5213 | 0.0582 | 11.2% | 🟢 stable |
| MAE | 2.0827 | 0.5440 | 26.1% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4797 |
| CI 95% | [0.4634, 0.4959] |
| p-value | 0.014301 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.70 et 0.75


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 21:44*
