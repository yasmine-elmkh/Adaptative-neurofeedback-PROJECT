# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 22:52


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1454 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5444 | Erreur quadratique moyenne |
| R² | -0.1420 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5188 | 0.500 |
| PR-AUC | 0.4260 | 0.414 |
| Sensitivity (TPR) | 0.3273 | 0.500 |
| Specificity (TNR) | 0.6901 | 0.500 |
| PPV (Precision) | 0.4272 | — |
| NPV | 0.5923 | — |
| Balanced Accuracy | 0.5087 | 0.500 |
| MCC | 0.0184 | 0.000 |
| G-Mean | 0.4753 | 0.500 |
| F1 macro | 0.5041 | 0.500 |
| LR+ | 1.056 | >10 = très utile |
| LR− | 0.975 | <0.1 = très utile |
| Cohen κ | 0.0181 | 0.000 |
| Brier Score | 0.2927 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5187 | [0.5065, 0.5309]  ✅ |
| F1 macro | 0.5039 | [0.4934, 0.5153]  — |
| Sensitivity | 0.3273 | [0.3126, 0.3428]  — |
| Specificity | 0.6899 | [0.6759, 0.7025]  — |
| MCC | 0.0182 | [-0.0020, 0.0413]  — |
| R² | -0.1422 | [-0.1594, -0.1245]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1420 | p=0.0160 | ✅ p<0.05 |
| AUC ROC | 0.5188 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1930 | < 0.05 |
| MCE | 0.5018 | < 0.10 |
| Brier Score | 0.2927 | < 0.20 |
| Log-Loss | 0.8334 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3733 | proche 0 = pas de biais systématique |
| LoA lower | -4.5600 | limite inférieure d'accord |
| LoA upper | +5.3067 | limite supérieure d'accord |
| LoA width | ±4.9333 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6082 | 1.3631 | 224.1% | 🔴 unstable |
| AUC ROC | 0.5503 | 0.0772 | 14.0% | 🟢 stable |
| MAE | 2.1453 | 0.5124 | 23.9% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5123 |
| CI 95% | [0.4987, 0.5260] |
| p-value | 0.077155 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 22:52*
