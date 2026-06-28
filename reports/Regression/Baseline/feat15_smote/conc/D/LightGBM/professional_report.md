# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `D`  |  **Date :** 2026-06-21 16:39


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6629 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1330 | Erreur quadratique moyenne |
| R² | -0.0232 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5854 | 0.500 |
| PR-AUC | 0.5746 | 0.517 |
| Sensitivity (TPR) | 0.5197 | 0.500 |
| Specificity (TNR) | 0.5939 | 0.500 |
| PPV (Precision) | 0.5782 | — |
| NPV | 0.5358 | — |
| Balanced Accuracy | 0.5568 | 0.500 |
| MCC | 0.1138 | 0.000 |
| G-Mean | 0.5556 | 0.500 |
| F1 macro | 0.5554 | 0.500 |
| LR+ | 1.280 | >10 = très utile |
| LR− | 0.809 | <0.1 = très utile |
| Cohen κ | 0.1132 | 0.000 |
| Brier Score | 0.3118 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5858 | [0.5647, 0.6063]  ✅ |
| F1 macro | 0.5557 | [0.5389, 0.5746]  ✅ |
| Sensitivity | 0.5200 | [0.4950, 0.5466]  — |
| Specificity | 0.5943 | [0.5672, 0.6206]  — |
| MCC | 0.1145 | [0.0805, 0.1536]  — |
| R² | -0.0225 | [-0.0549, 0.0100]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0232 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5854 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2392 | < 0.05 |
| MCE | 0.3610 | < 0.10 |
| Brier Score | 0.3118 | < 0.20 |
| Log-Loss | 0.9638 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0363 | proche 0 = pas de biais systématique |
| LoA lower | -6.1777 | limite inférieure d'accord |
| LoA upper | +6.1051 | limite supérieure d'accord |
| LoA width | ±6.1414 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1098 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0660 | 0.2256 | 341.7% | 🔴 unstable |
| AUC ROC | 0.5883 | 0.0766 | 13.0% | 🟢 stable |
| MAE | 2.6618 | 0.2792 | 10.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5839 |
| CI 95% | [0.5629, 0.6048] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.56


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:39*
