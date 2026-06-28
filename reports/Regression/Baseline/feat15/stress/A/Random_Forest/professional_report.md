# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `A`  |  **Date :** 2026-06-21 17:13


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1391 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5298 | Erreur quadratique moyenne |
| R² | -0.1290 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5256 | 0.500 |
| PR-AUC | 0.6558 | 0.636 |
| Sensitivity (TPR) | 0.9041 | 0.500 |
| Specificity (TNR) | 0.1610 | 0.500 |
| PPV (Precision) | 0.6533 | — |
| NPV | 0.4896 | — |
| Balanced Accuracy | 0.5325 | 0.500 |
| MCC | 0.0964 | 0.000 |
| G-Mean | 0.3815 | 0.500 |
| F1 macro | 0.5004 | 0.500 |
| LR+ | 1.078 | >10 = très utile |
| LR− | 0.596 | <0.1 = très utile |
| Cohen κ | 0.0760 | 0.000 |
| Brier Score | 0.2755 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5012 | [0.4731, 0.5268]  — |
| F1 macro | 0.4596 | [0.4407, 0.4796]  — |
| Sensitivity | 0.0781 | [0.0566, 0.1005]  — |
| Specificity | 0.9094 | [0.8940, 0.9232]  — |
| MCC | -0.0200 | [-0.0611, 0.0226]  — |
| R² | -0.1300 | [-0.1626, -0.0954]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1290 | p=0.0320 | ✅ p<0.05 |
| AUC ROC | 0.5015 | p=0.4680 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1784 | < 0.05 |
| MCE | 0.6937 | < 0.10 |
| Brier Score | 0.2498 | < 0.20 |
| Log-Loss | 0.7895 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1123 | proche 0 = pas de biais systématique |
| LoA lower | -4.8425 | limite inférieure d'accord |
| LoA upper | +5.0671 | limite supérieure d'accord |
| LoA width | ±4.9548 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0083 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5573 | 1.1720 | 210.3% | 🔴 unstable |
| AUC ROC | 0.4973 | 0.0791 | 15.9% | 🟡 moderate |
| MAE | 2.1392 | 0.5501 | 25.7% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5015 |
| CI 95% | [0.4739, 0.5290] |
| p-value | 0.916575 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:13*
