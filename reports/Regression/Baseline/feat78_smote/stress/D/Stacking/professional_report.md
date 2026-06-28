# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `D`  |  **Date :** 2026-06-21 21:29


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4862 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0515 | Erreur quadratique moyenne |
| R² | -0.6426 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4101 | 0.500 |
| PR-AUC | 0.2143 | 0.257 |
| Sensitivity (TPR) | 0.1120 | 0.500 |
| Specificity (TNR) | 0.8066 | 0.500 |
| PPV (Precision) | 0.1669 | — |
| NPV | 0.7241 | — |
| Balanced Accuracy | 0.4593 | 0.500 |
| MCC | -0.0942 | 0.000 |
| G-Mean | 0.3005 | 0.500 |
| F1 macro | 0.4486 | 0.500 |
| LR+ | 0.579 | >10 = très utile |
| LR− | 1.101 | <0.1 = très utile |
| Cohen κ | -0.0912 | 0.000 |
| Brier Score | 0.3045 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4103 | [0.3899, 0.4291]  — |
| F1 macro | 0.4485 | [0.4348, 0.4617]  — |
| Sensitivity | 0.1119 | [0.0923, 0.1309]  — |
| Specificity | 0.8065 | [0.7929, 0.8205]  — |
| MCC | -0.0944 | [-0.1212, -0.0668]  — |
| R² | -0.6422 | [-0.6964, -0.5969]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.6426 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4101 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2749 | < 0.05 |
| MCE | 0.8073 | < 0.10 |
| Brier Score | 0.3045 | < 0.20 |
| Log-Loss | 1.1078 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3433 | proche 0 = pas de biais systématique |
| LoA lower | -5.6005 | limite inférieure d'accord |
| LoA upper | +6.2870 | limite supérieure d'accord |
| LoA width | ±5.9437 | < ±2 pts : excellent |
| % dans LoA | 95.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0049 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.1529 | 1.6927 | 146.8% | 🔴 unstable |
| AUC ROC | 0.5108 | 0.1080 | 21.1% | 🟡 moderate |
| MAE | 2.4859 | 0.9152 | 36.8% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.3981 |
| CI 95% | [0.3789, 0.4174] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 21:29*
