# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `FULL`  |  **Date :** 2026-06-22 00:42


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1331 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5005 | Erreur quadratique moyenne |
| R² | -0.1029 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4848 | 0.500 |
| PR-AUC | 0.2458 | 0.253 |
| Sensitivity (TPR) | 0.0088 | 0.500 |
| Specificity (TNR) | 0.9920 | 0.500 |
| PPV (Precision) | 0.2727 | — |
| NPV | 0.7471 | — |
| Balanced Accuracy | 0.5004 | 0.500 |
| MCC | 0.0041 | 0.000 |
| G-Mean | 0.0936 | 0.500 |
| F1 macro | 0.4347 | 0.500 |
| LR+ | 1.107 | >10 = très utile |
| LR− | 0.999 | <0.1 = très utile |
| Cohen κ | 0.0012 | 0.000 |
| Brier Score | 0.2205 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4845 | [0.4693, 0.4970]  — |
| F1 macro | 0.4510 | [0.4428, 0.4593]  — |
| Sensitivity | 0.0517 | [0.0434, 0.0604]  — |
| Specificity | 0.9450 | [0.9393, 0.9508]  — |
| MCC | -0.0065 | [-0.0279, 0.0147]  — |
| R² | -0.1027 | [-0.1156, -0.0907]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1029 | p=0.9960 | ❌ ns |
| AUC ROC | 0.4847 | p=0.9840 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1474 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2325 | < 0.20 |
| Log-Loss | 0.7104 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2788 | proche 0 = pas de biais systématique |
| LoA lower | -4.5919 | limite inférieure d'accord |
| LoA upper | +5.1494 | limite supérieure d'accord |
| LoA width | ±4.8707 | < ±2 pts : excellent |
| % dans LoA | 96.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0003 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5380 | 1.3294 | 247.1% | 🔴 unstable |
| AUC ROC | 0.4925 | 0.0414 | 8.4% | 🟢 stable |
| MAE | 2.1329 | 0.5288 | 24.8% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4847 |
| CI 95% | [0.4707, 0.4988] |
| p-value | 0.033372 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ❌ NON**

Le modèle n'apporte pas de bénéfice net par rapport aux stratégies 'traiter tous' ou 'ne traiter personne'.


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-22 00:42*
