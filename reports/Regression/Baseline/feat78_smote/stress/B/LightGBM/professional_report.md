# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `B`  |  **Date :** 2026-06-21 19:04


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2233 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6471 | Erreur quadratique moyenne |
| R² | -0.2361 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4829 | 0.500 |
| PR-AUC | 0.4072 | 0.414 |
| Sensitivity (TPR) | 0.2812 | 0.500 |
| Specificity (TNR) | 0.6846 | 0.500 |
| PPV (Precision) | 0.3863 | — |
| NPV | 0.5742 | — |
| Balanced Accuracy | 0.4829 | 0.500 |
| MCC | -0.0368 | 0.000 |
| G-Mean | 0.4387 | 0.500 |
| F1 macro | 0.4750 | 0.500 |
| LR+ | 0.891 | >10 = très utile |
| LR− | 1.050 | <0.1 = très utile |
| Cohen κ | -0.0357 | 0.000 |
| Brier Score | 0.3173 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4831 | [0.4663, 0.5007]  — |
| F1 macro | 0.4754 | [0.4606, 0.4893]  — |
| Sensitivity | 0.2819 | [0.2607, 0.3031]  — |
| Specificity | 0.6847 | [0.6666, 0.7030]  — |
| MCC | -0.0359 | [-0.0660, -0.0079]  — |
| R² | -0.2361 | [-0.2665, -0.2069]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2361 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4829 | p=0.9800 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2353 | < 0.05 |
| MCE | 0.5290 | < 0.10 |
| Brier Score | 0.3173 | < 0.20 |
| Log-Loss | 0.9246 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3516 | proche 0 = pas de biais systématique |
| LoA lower | -4.7913 | limite inférieure d'accord |
| LoA upper | +5.4945 | limite supérieure d'accord |
| LoA width | ±5.1429 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0009 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.8326 | 2.2592 | 271.3% | 🔴 unstable |
| AUC ROC | 0.5232 | 0.0500 | 9.6% | 🟢 stable |
| MAE | 2.2231 | 0.6297 | 28.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4673 |
| CI 95% | [0.4476, 0.4869] |
| p-value | 0.001086 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:04*
