# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `B`  |  **Date :** 2026-06-21 20:12


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1693 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5537 | Erreur quadratique moyenne |
| R² | -0.1504 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4813 | 0.500 |
| PR-AUC | 0.4441 | 0.457 |
| Sensitivity (TPR) | 0.6922 | 0.500 |
| Specificity (TNR) | 0.2948 | 0.500 |
| PPV (Precision) | 0.4524 | — |
| NPV | 0.5322 | — |
| Balanced Accuracy | 0.4935 | 0.500 |
| MCC | -0.0142 | 0.000 |
| G-Mean | 0.4517 | 0.500 |
| F1 macro | 0.4633 | 0.500 |
| LR+ | 0.982 | >10 = très utile |
| LR− | 1.044 | <0.1 = très utile |
| Cohen κ | -0.0125 | 0.000 |
| Brier Score | 0.3175 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4886 | [0.4694, 0.5071]  — |
| F1 macro | 0.4673 | [0.4532, 0.4806]  — |
| Sensitivity | 0.1088 | [0.0916, 0.1274]  — |
| Specificity | 0.8700 | [0.8581, 0.8813]  — |
| MCC | -0.0290 | [-0.0587, 0.0008]  — |
| R² | -0.1503 | [-0.1749, -0.1252]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1504 | p=0.9600 | ❌ ns |
| AUC ROC | 0.4880 | p=0.8780 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1434 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2350 | < 0.20 |
| Log-Loss | 0.6938 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5392 | proche 0 = pas de biais systématique |
| LoA lower | -4.3539 | limite inférieure d'accord |
| LoA upper | +5.4323 | limite supérieure d'accord |
| LoA width | ±4.8931 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6611 | 1.5629 | 236.4% | 🔴 unstable |
| AUC ROC | 0.5047 | 0.0473 | 9.4% | 🟢 stable |
| MAE | 2.1691 | 0.4985 | 23.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4880 |
| CI 95% | [0.4684, 0.5076] |
| p-value | 0.230646 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:12*
