# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `C`  |  **Date :** 2026-06-21 18:47


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3458 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8500 | Erreur quadratique moyenne |
| R² | -0.4328 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5178 | 0.500 |
| PR-AUC | 0.2897 | 0.262 |
| Sensitivity (TPR) | 0.2271 | 0.500 |
| Specificity (TNR) | 0.8262 | 0.500 |
| PPV (Precision) | 0.3163 | — |
| NPV | 0.7511 | — |
| Balanced Accuracy | 0.5266 | 0.500 |
| MCC | 0.0599 | 0.000 |
| G-Mean | 0.4331 | 0.500 |
| F1 macro | 0.5256 | 0.500 |
| LR+ | 1.306 | >10 = très utile |
| LR− | 0.936 | <0.1 = très utile |
| Cohen κ | 0.0586 | 0.000 |
| Brier Score | 0.2604 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5175 | [0.5007, 0.5341]  ✅ |
| F1 macro | 0.5255 | [0.5127, 0.5389]  ✅ |
| Sensitivity | 0.2269 | [0.2062, 0.2478]  — |
| Specificity | 0.8262 | [0.8148, 0.8377]  — |
| MCC | 0.0598 | [0.0344, 0.0865]  — |
| R² | -0.4348 | [-0.4783, -0.3939]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4328 | p=0.8880 | ❌ ns |
| AUC ROC | 0.5178 | p=0.0100 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2113 | < 0.05 |
| MCE | 0.6150 | < 0.10 |
| Brier Score | 0.2604 | < 0.20 |
| Log-Loss | 0.8994 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4707 | proche 0 = pas de biais systématique |
| LoA lower | -5.0389 | limite inférieure d'accord |
| LoA upper | +5.9804 | limite supérieure d'accord |
| LoA width | ±5.5097 | < ±2 pts : excellent |
| % dans LoA | 95.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.8869 | 1.1544 | 130.2% | 🔴 unstable |
| AUC ROC | 0.4945 | 0.0770 | 15.6% | 🟡 moderate |
| MAE | 2.3456 | 0.7032 | 30.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5067 |
| CI 95% | [0.4902, 0.5232] |
| p-value | 0.426651 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:47*
