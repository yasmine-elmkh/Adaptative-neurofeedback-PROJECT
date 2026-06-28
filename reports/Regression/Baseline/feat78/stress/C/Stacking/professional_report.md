# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `C`  |  **Date :** 2026-06-21 22:01


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1362 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5128 | Erreur quadratique moyenne |
| R² | -0.1139 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4928 | 0.500 |
| PR-AUC | 0.3090 | 0.311 |
| Sensitivity (TPR) | 0.1100 | 0.500 |
| Specificity (TNR) | 0.8936 | 0.500 |
| PPV (Precision) | 0.3185 | — |
| NPV | 0.6897 | — |
| Balanced Accuracy | 0.5018 | 0.500 |
| MCC | 0.0055 | 0.000 |
| G-Mean | 0.3136 | 0.500 |
| F1 macro | 0.4711 | 0.500 |
| LR+ | 1.034 | >10 = très utile |
| LR− | 0.996 | <0.1 = très utile |
| Cohen κ | 0.0045 | 0.000 |
| Brier Score | 0.2481 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4920 | [0.4766, 0.5077]  — |
| F1 macro | 0.4676 | [0.4575, 0.4785]  — |
| Sensitivity | 0.0867 | [0.0736, 0.1001]  — |
| Specificity | 0.9118 | [0.9034, 0.9201]  — |
| MCC | -0.0023 | [-0.0282, 0.0228]  — |
| R² | -0.1145 | [-0.1328, -0.0977]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1139 | p=0.6480 | ❌ ns |
| AUC ROC | 0.4922 | p=0.8200 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1410 | < 0.05 |
| MCE | 0.6640 | < 0.10 |
| Brier Score | 0.2337 | < 0.20 |
| Log-Loss | 0.7006 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4305 | proche 0 = pas de biais systématique |
| LoA lower | -4.4223 | limite inférieure d'accord |
| LoA upper | +5.2832 | limite supérieure d'accord |
| LoA width | ±4.8527 | < ±2 pts : excellent |
| % dans LoA | 96.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5940 | 1.4463 | 243.5% | 🔴 unstable |
| AUC ROC | 0.5215 | 0.0614 | 11.8% | 🟢 stable |
| MAE | 2.1360 | 0.4913 | 23.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4922 |
| CI 95% | [0.4759, 0.5085] |
| p-value | 0.347487 |
| Significatif | ❌ NON |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 22:01*
