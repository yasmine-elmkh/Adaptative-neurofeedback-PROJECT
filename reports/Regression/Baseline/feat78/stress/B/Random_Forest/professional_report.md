# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `B`  |  **Date :** 2026-06-21 20:08


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0957 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4413 | Erreur quadratique moyenne |
| R² | -0.0513 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4729 | 0.500 |
| PR-AUC | 0.5358 | 0.560 |
| Sensitivity (TPR) | 0.9907 | 0.500 |
| Specificity (TNR) | 0.0141 | 0.500 |
| PPV (Precision) | 0.5610 | — |
| NPV | 0.5435 | — |
| Balanced Accuracy | 0.5024 | 0.500 |
| MCC | 0.0224 | 0.000 |
| G-Mean | 0.1182 | 0.500 |
| F1 macro | 0.3719 | 0.500 |
| LR+ | 1.005 | >10 = très utile |
| LR− | 0.661 | <0.1 = très utile |
| Cohen κ | 0.0053 | 0.000 |
| Brier Score | 0.3097 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4650 | [0.4432, 0.4831]  — |
| F1 macro | 0.4167 | [0.4116, 0.4218]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 0.9955 | [0.9928, 0.9979]  — |
| MCC | -0.0353 | [-0.0453, -0.0244]  — |
| R² | -0.0514 | [-0.0621, -0.0396]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0513 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4649 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1312 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2260 | < 0.20 |
| Log-Loss | 0.6837 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1846 | proche 0 = pas de biais systématique |
| LoA lower | -4.5871 | limite inférieure d'accord |
| LoA upper | +4.9564 | limite supérieure d'accord |
| LoA width | ±4.7718 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0014 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.4391 | 1.1687 | 266.2% | 🔴 unstable |
| AUC ROC | 0.4894 | 0.0483 | 9.9% | 🟢 stable |
| MAE | 2.0956 | 0.5503 | 26.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4649 |
| CI 95% | [0.4452, 0.4847] |
| p-value | 0.000508 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:08*
