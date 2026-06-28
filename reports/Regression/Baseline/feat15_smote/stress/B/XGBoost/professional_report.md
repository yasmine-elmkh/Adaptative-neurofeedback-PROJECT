# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `B`  |  **Date :** 2026-06-21 17:52


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2145 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6535 | Erreur quadratique moyenne |
| R² | -0.2420 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4833 | 0.500 |
| PR-AUC | 0.4052 | 0.414 |
| Sensitivity (TPR) | 0.3028 | 0.500 |
| Specificity (TNR) | 0.6757 | 0.500 |
| PPV (Precision) | 0.3973 | — |
| NPV | 0.5785 | — |
| Balanced Accuracy | 0.4892 | 0.500 |
| MCC | -0.0228 | 0.000 |
| G-Mean | 0.4523 | 0.500 |
| F1 macro | 0.4835 | 0.500 |
| LR+ | 0.934 | >10 = très utile |
| LR− | 1.032 | <0.1 = très utile |
| Cohen κ | -0.0223 | 0.000 |
| Brier Score | 0.3134 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4833 | [0.4655, 0.5012]  — |
| F1 macro | 0.4832 | [0.4685, 0.4974]  — |
| Sensitivity | 0.3027 | [0.2809, 0.3241]  — |
| Specificity | 0.6754 | [0.6547, 0.6933]  — |
| MCC | -0.0232 | [-0.0518, 0.0072]  — |
| R² | -0.2426 | [-0.2739, -0.2110]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2420 | p=0.9960 | ❌ ns |
| AUC ROC | 0.4833 | p=0.9700 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2295 | < 0.05 |
| MCE | 0.5187 | < 0.10 |
| Brier Score | 0.3134 | < 0.20 |
| Log-Loss | 0.9067 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4912 | proche 0 = pas de biais systématique |
| LoA lower | -4.6203 | limite inférieure d'accord |
| LoA upper | +5.6027 | limite supérieure d'accord |
| LoA width | ±5.1115 | < ±2 pts : excellent |
| % dans LoA | 96.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0004 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7868 | 1.7617 | 223.9% | 🔴 unstable |
| AUC ROC | 0.5162 | 0.0763 | 14.8% | 🟢 stable |
| MAE | 2.2142 | 0.6089 | 27.5% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4772 |
| CI 95% | [0.4574, 0.4970] |
| p-value | 0.023790 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:52*
