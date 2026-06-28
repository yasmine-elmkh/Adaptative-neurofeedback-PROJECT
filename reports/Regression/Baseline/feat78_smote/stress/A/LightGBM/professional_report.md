# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `A`  |  **Date :** 2026-06-21 18:04


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1989 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6226 | Erreur quadratique moyenne |
| R² | -0.2134 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5019 | 0.500 |
| PR-AUC | 0.4184 | 0.414 |
| Sensitivity (TPR) | 0.3129 | 0.500 |
| Specificity (TNR) | 0.6935 | 0.500 |
| PPV (Precision) | 0.4189 | — |
| NPV | 0.5884 | — |
| Balanced Accuracy | 0.5032 | 0.500 |
| MCC | 0.0069 | 0.000 |
| G-Mean | 0.4659 | 0.500 |
| F1 macro | 0.4974 | 0.500 |
| LR+ | 1.021 | >10 = très utile |
| LR− | 0.991 | <0.1 = très utile |
| Cohen κ | 0.0067 | 0.000 |
| Brier Score | 0.3058 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5028 | [0.4758, 0.5264]  — |
| F1 macro | 0.4977 | [0.4745, 0.5183]  — |
| Sensitivity | 0.3133 | [0.2829, 0.3446]  — |
| Specificity | 0.6939 | [0.6691, 0.7199]  — |
| MCC | 0.0077 | [-0.0365, 0.0496]  — |
| R² | -0.2132 | [-0.2524, -0.1711]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2134 | p=0.8880 | ❌ ns |
| AUC ROC | 0.5019 | p=0.4400 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2249 | < 0.05 |
| MCE | 0.5705 | < 0.10 |
| Brier Score | 0.3058 | < 0.20 |
| Log-Loss | 0.8979 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3096 | proche 0 = pas de biais systématique |
| LoA lower | -4.7961 | limite inférieure d'accord |
| LoA upper | +5.4153 | limite supérieure d'accord |
| LoA width | ±5.1057 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0013 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7652 | 1.8799 | 245.7% | 🔴 unstable |
| AUC ROC | 0.4988 | 0.0804 | 16.1% | 🟡 moderate |
| MAE | 2.1989 | 0.5428 | 24.7% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4853 |
| CI 95% | [0.4576, 0.5130] |
| p-value | 0.297390 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:04*
