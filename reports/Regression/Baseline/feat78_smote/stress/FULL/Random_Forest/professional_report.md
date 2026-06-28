# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 22:39


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1623 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5363 | Erreur quadratique moyenne |
| R² | -0.1348 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4790 | 0.500 |
| PR-AUC | 0.4003 | 0.413 |
| Sensitivity (TPR) | 0.0922 | 0.500 |
| Specificity (TNR) | 0.8937 | 0.500 |
| PPV (Precision) | 0.3790 | — |
| NPV | 0.5833 | — |
| Balanced Accuracy | 0.4930 | 0.500 |
| MCC | -0.0230 | 0.000 |
| G-Mean | 0.2871 | 0.500 |
| F1 macro | 0.4271 | 0.500 |
| LR+ | 0.868 | >10 = très utile |
| LR− | 1.016 | <0.1 = très utile |
| Cohen κ | -0.0158 | 0.000 |
| Brier Score | 0.3228 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4790 | [0.4656, 0.4911]  — |
| F1 macro | 0.4271 | [0.4178, 0.4365]  — |
| Sensitivity | 0.0925 | [0.0828, 0.1027]  — |
| Specificity | 0.8935 | [0.8843, 0.9024]  — |
| MCC | -0.0229 | [-0.0436, -0.0007]  — |
| R² | -0.1351 | [-0.1505, -0.1211]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1348 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4790 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2595 | < 0.05 |
| MCE | 0.5105 | < 0.10 |
| Brier Score | 0.3228 | < 0.20 |
| Log-Loss | 0.9772 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0480 | proche 0 = pas de biais systématique |
| LoA lower | -5.0186 | limite inférieure d'accord |
| LoA upper | +4.9227 | limite supérieure d'accord |
| LoA width | ±4.9707 | < ±2 pts : excellent |
| % dans LoA | 96.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0066 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.4868 | 0.8758 | 179.9% | 🔴 unstable |
| AUC ROC | 0.5182 | 0.0578 | 11.2% | 🟢 stable |
| MAE | 2.1624 | 0.5681 | 26.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4891 |
| CI 95% | [0.4754, 0.5029] |
| p-value | 0.121099 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 22:39*
