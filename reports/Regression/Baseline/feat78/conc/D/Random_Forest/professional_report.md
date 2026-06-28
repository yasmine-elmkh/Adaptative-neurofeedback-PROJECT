# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `D`  |  **Date :** 2026-06-21 17:23


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6781 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0474 | Erreur quadratique moyenne |
| R² | 0.0319 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5916 | 0.500 |
| PR-AUC | 0.5838 | 0.517 |
| Sensitivity (TPR) | 0.5231 | 0.500 |
| Specificity (TNR) | 0.6295 | 0.500 |
| PPV (Precision) | 0.6020 | — |
| NPV | 0.5520 | — |
| Balanced Accuracy | 0.5763 | 0.500 |
| MCC | 0.1533 | 0.000 |
| G-Mean | 0.5739 | 0.500 |
| F1 macro | 0.5740 | 0.500 |
| LR+ | 1.412 | >10 = très utile |
| LR− | 0.758 | <0.1 = très utile |
| Cohen κ | 0.1519 | 0.000 |
| Brier Score | 0.2740 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5900 | [0.5701, 0.6122]  ✅ |
| F1 macro | 0.4847 | [0.4673, 0.5033]  — |
| Sensitivity | 0.2453 | [0.2251, 0.2670]  — |
| Specificity | 0.8163 | [0.7952, 0.8358]  — |
| MCC | 0.0748 | [0.0407, 0.1140]  — |
| R² | 0.0317 | [0.0119, 0.0544]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0319 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5899 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2182 | < 0.05 |
| MCE | 0.4011 | < 0.10 |
| Brier Score | 0.3019 | < 0.20 |
| Log-Loss | 0.8802 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0141 | proche 0 = pas de biais systématique |
| LoA lower | -5.9880 | limite inférieure d'accord |
| LoA upper | +5.9598 | limite supérieure d'accord |
| LoA width | ±5.9739 | < ±2 pts : excellent |
| % dans LoA | 99.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0726 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0182 | 0.1428 | 783.2% | 🔴 unstable |
| AUC ROC | 0.5900 | 0.0707 | 12.0% | 🟢 stable |
| MAE | 2.6842 | 0.2201 | 8.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5899 |
| CI 95% | [0.5690, 0.6107] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.51 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:23*
