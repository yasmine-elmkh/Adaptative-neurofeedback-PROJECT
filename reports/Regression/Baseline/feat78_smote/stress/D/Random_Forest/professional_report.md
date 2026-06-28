# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `D`  |  **Date :** 2026-06-21 21:20


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2729 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7111 | Erreur quadratique moyenne |
| R² | -0.2966 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4165 | 0.500 |
| PR-AUC | 0.3572 | 0.410 |
| Sensitivity (TPR) | 0.1004 | 0.500 |
| Specificity (TNR) | 0.8253 | 0.500 |
| PPV (Precision) | 0.2857 | — |
| NPV | 0.5686 | — |
| Balanced Accuracy | 0.4628 | 0.500 |
| MCC | -0.1041 | 0.000 |
| G-Mean | 0.2878 | 0.500 |
| F1 macro | 0.4109 | 0.500 |
| LR+ | 0.575 | >10 = très utile |
| LR− | 1.090 | <0.1 = très utile |
| Cohen κ | -0.0824 | 0.000 |
| Brier Score | 0.3434 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4171 | [0.4007, 0.4347]  — |
| F1 macro | 0.4108 | [0.3964, 0.4252]  — |
| Sensitivity | 0.1006 | [0.0863, 0.1162]  — |
| Specificity | 0.8251 | [0.8115, 0.8389]  — |
| MCC | -0.1041 | [-0.1339, -0.0765]  — |
| R² | -0.2962 | [-0.3230, -0.2705]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2966 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4165 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2902 | < 0.05 |
| MCE | 0.6438 | < 0.10 |
| Brier Score | 0.3434 | < 0.20 |
| Log-Loss | 1.0269 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1754 | proche 0 = pas de biais systématique |
| LoA lower | -5.1278 | limite inférieure d'accord |
| LoA upper | +5.4786 | limite supérieure d'accord |
| LoA width | ±5.3032 | < ±2 pts : excellent |
| % dans LoA | 96.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0118 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7581 | 1.5853 | 209.1% | 🔴 unstable |
| AUC ROC | 0.4821 | 0.0804 | 16.7% | 🟡 moderate |
| MAE | 2.2726 | 0.7278 | 32.0% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.3832 |
| CI 95% | [0.3640, 0.4024] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 21:20*
