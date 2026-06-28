# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `B`  |  **Date :** 2026-06-21 17:49


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1960 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6096 | Erreur quadratique moyenne |
| R² | -0.2014 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4774 | 0.500 |
| PR-AUC | 0.3963 | 0.414 |
| Sensitivity (TPR) | 0.1361 | 0.500 |
| Specificity (TNR) | 0.8230 | 0.500 |
| PPV (Precision) | 0.3519 | — |
| NPV | 0.5743 | — |
| Balanced Accuracy | 0.4796 | 0.500 |
| MCC | -0.0549 | 0.000 |
| G-Mean | 0.3347 | 0.500 |
| F1 macro | 0.4364 | 0.500 |
| LR+ | 0.769 | >10 = très utile |
| LR− | 1.050 | <0.1 = très utile |
| Cohen κ | -0.0449 | 0.000 |
| Brier Score | 0.3288 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4774 | [0.4610, 0.4931]  — |
| F1 macro | 0.4363 | [0.4221, 0.4502]  — |
| Sensitivity | 0.1363 | [0.1184, 0.1540]  — |
| Specificity | 0.8229 | [0.8080, 0.8374]  — |
| MCC | -0.0548 | [-0.0867, -0.0265]  — |
| R² | -0.2023 | [-0.2283, -0.1779]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2014 | p=0.9960 | ❌ ns |
| AUC ROC | 0.4774 | p=0.9900 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2650 | < 0.05 |
| MCE | 0.5440 | < 0.10 |
| Brier Score | 0.3288 | < 0.20 |
| Log-Loss | 0.9849 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0567 | proche 0 = pas de biais systématique |
| LoA lower | -5.0576 | limite inférieure d'accord |
| LoA upper | +5.1710 | limite supérieure d'accord |
| LoA width | ±5.1143 | < ±2 pts : excellent |
| % dans LoA | 96.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0111 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7640 | 2.1739 | 284.5% | 🔴 unstable |
| AUC ROC | 0.5126 | 0.0602 | 11.8% | 🟢 stable |
| MAE | 2.1958 | 0.6436 | 29.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4544 |
| CI 95% | [0.4348, 0.4741] |
| p-value | 0.000006 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:49*
