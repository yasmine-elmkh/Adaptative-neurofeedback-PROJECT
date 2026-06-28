# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `D`  |  **Date :** 2026-06-21 21:22


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2249 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6858 | Erreur quadratique moyenne |
| R² | -0.2725 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4647 | 0.500 |
| PR-AUC | 0.3798 | 0.414 |
| Sensitivity (TPR) | 0.1847 | 0.500 |
| Specificity (TNR) | 0.7460 | 0.500 |
| PPV (Precision) | 0.3392 | — |
| NPV | 0.5644 | — |
| Balanced Accuracy | 0.4653 | 0.500 |
| MCC | -0.0818 | 0.000 |
| G-Mean | 0.3711 | 0.500 |
| F1 macro | 0.4409 | 0.500 |
| LR+ | 0.727 | >10 = très utile |
| LR− | 1.093 | <0.1 = très utile |
| Cohen κ | -0.0743 | 0.000 |
| Brier Score | 0.3243 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4648 | [0.4486, 0.4821]  — |
| F1 macro | 0.4411 | [0.4269, 0.4553]  — |
| Sensitivity | 0.1853 | [0.1666, 0.2031]  — |
| Specificity | 0.7457 | [0.7295, 0.7630]  — |
| MCC | -0.0813 | [-0.1102, -0.0532]  — |
| R² | -0.2727 | [-0.3017, -0.2452]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2725 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4647 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2473 | < 0.05 |
| MCE | 0.6345 | < 0.10 |
| Brier Score | 0.3243 | < 0.20 |
| Log-Loss | 0.9508 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3333 | proche 0 = pas de biais systématique |
| LoA lower | -4.8909 | limite inférieure d'accord |
| LoA upper | +5.5575 | limite supérieure d'accord |
| LoA width | ±5.2242 | < ±2 pts : excellent |
| % dans LoA | 96.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0022 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7035 | 1.2935 | 183.9% | 🔴 unstable |
| AUC ROC | 0.5194 | 0.0895 | 17.2% | 🟡 moderate |
| MAE | 2.2247 | 0.6533 | 29.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4294 |
| CI 95% | [0.4101, 0.4487] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 21:22*
