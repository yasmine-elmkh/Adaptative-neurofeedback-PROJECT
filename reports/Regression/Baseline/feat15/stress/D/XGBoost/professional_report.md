# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `D`  |  **Date :** 2026-06-21 19:17


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2232 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6777 | Erreur quadratique moyenne |
| R² | -0.2648 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4656 | 0.500 |
| PR-AUC | 0.6887 | 0.719 |
| Sensitivity (TPR) | 0.9979 | 0.500 |
| Specificity (TNR) | 0.0088 | 0.500 |
| PPV (Precision) | 0.7205 | — |
| NPV | 0.6250 | — |
| Balanced Accuracy | 0.5034 | 0.500 |
| MCC | 0.0483 | 0.000 |
| G-Mean | 0.0939 | 0.500 |
| F1 macro | 0.4271 | 0.500 |
| LR+ | 1.007 | >10 = très utile |
| LR− | 0.234 | <0.1 = très utile |
| Cohen κ | 0.0097 | 0.000 |
| Brier Score | 0.2679 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4616 | [0.4414, 0.4822]  — |
| F1 macro | 0.4783 | [0.4649, 0.4937]  — |
| Sensitivity | 0.1425 | [0.1228, 0.1621]  — |
| Specificity | 0.8414 | [0.8280, 0.8550]  — |
| MCC | -0.0200 | [-0.0482, 0.0111]  — |
| R² | -0.2655 | [-0.2967, -0.2334]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2648 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4620 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1885 | < 0.05 |
| MCE | 0.8163 | < 0.10 |
| Brier Score | 0.2623 | < 0.20 |
| Log-Loss | 0.8254 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3888 | proche 0 = pas de biais systématique |
| LoA lower | -4.8044 | limite inférieure d'accord |
| LoA upper | +5.5821 | limite supérieure d'accord |
| LoA width | ±5.1933 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0013 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6954 | 1.2467 | 179.3% | 🔴 unstable |
| AUC ROC | 0.4919 | 0.0729 | 14.8% | 🟢 stable |
| MAE | 2.2230 | 0.6574 | 29.6% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4620 |
| CI 95% | [0.4419, 0.4821] |
| p-value | 0.000209 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:17*
