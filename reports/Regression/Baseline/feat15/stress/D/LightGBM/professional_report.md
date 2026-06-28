# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `D`  |  **Date :** 2026-06-21 19:18


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3024 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7571 | Erreur quadratique moyenne |
| R² | -0.3410 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.3928 | 0.500 |
| PR-AUC | 0.0131 | 0.015 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 1.0000 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.9851 | — |
| Balanced Accuracy | 0.5000 | 0.500 |
| MCC | 0.0000 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.4963 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.000 | <0.1 = très utile |
| Cohen κ | 0.0000 | 0.000 |
| Brier Score | 0.0149 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4272 | [0.4067, 0.4463]  — |
| F1 macro | 0.4475 | [0.4338, 0.4614]  — |
| Sensitivity | 0.1245 | [0.1038, 0.1433]  — |
| Specificity | 0.7958 | [0.7810, 0.8100]  — |
| MCC | -0.0931 | [-0.1217, -0.0653]  — |
| R² | -0.3417 | [-0.3767, -0.3058]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3410 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4273 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2238 | < 0.05 |
| MCE | 0.8946 | < 0.10 |
| Brier Score | 0.2813 | < 0.20 |
| Log-Loss | 0.8737 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4633 | proche 0 = pas de biais systématique |
| LoA lower | -4.8645 | limite inférieure d'accord |
| LoA upper | +5.7911 | limite supérieure d'accord |
| LoA width | ±5.3278 | < ±2 pts : excellent |
| % dans LoA | 96.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0016 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.1941 | 3.7323 | 312.6% | 🔴 unstable |
| AUC ROC | 0.5114 | 0.0711 | 13.9% | 🟢 stable |
| MAE | 2.3022 | 0.6955 | 30.2% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4273 |
| CI 95% | [0.4078, 0.4467] |
| p-value | 0.000000 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:18*
