# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `A`  |  **Date :** 2026-06-21 17:14


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1849 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5929 | Erreur quadratique moyenne |
| R² | -0.1860 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5085 | 0.500 |
| PR-AUC | 0.4298 | 0.416 |
| Sensitivity (TPR) | 0.3866 | 0.500 |
| Specificity (TNR) | 0.6585 | 0.500 |
| PPV (Precision) | 0.4463 | — |
| NPV | 0.6012 | — |
| Balanced Accuracy | 0.5225 | 0.500 |
| MCC | 0.0463 | 0.000 |
| G-Mean | 0.5046 | 0.500 |
| F1 macro | 0.5214 | 0.500 |
| LR+ | 1.132 | >10 = très utile |
| LR− | 0.932 | <0.1 = très utile |
| Cohen κ | 0.0460 | 0.000 |
| Brier Score | 0.3043 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4963 | [0.4684, 0.5235]  — |
| F1 macro | 0.4891 | [0.4680, 0.5099]  — |
| Sensitivity | 0.1449 | [0.1188, 0.1709]  — |
| Specificity | 0.8628 | [0.8460, 0.8786]  — |
| MCC | 0.0101 | [-0.0334, 0.0531]  — |
| R² | -0.1869 | [-0.2295, -0.1451]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1860 | p=0.3280 | ❌ ns |
| AUC ROC | 0.4967 | p=0.5800 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1802 | < 0.05 |
| MCE | 0.7173 | < 0.10 |
| Brier Score | 0.2526 | < 0.20 |
| Log-Loss | 0.7945 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3451 | proche 0 = pas de biais systématique |
| LoA lower | -4.6931 | limite inférieure d'accord |
| LoA upper | +5.3832 | limite supérieure d'accord |
| LoA width | ±5.0381 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0004 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5871 | 0.8876 | 151.2% | 🔴 unstable |
| AUC ROC | 0.4863 | 0.0820 | 16.9% | 🟡 moderate |
| MAE | 2.1849 | 0.5237 | 24.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4967 |
| CI 95% | [0.4684, 0.5250] |
| p-value | 0.819906 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:14*
