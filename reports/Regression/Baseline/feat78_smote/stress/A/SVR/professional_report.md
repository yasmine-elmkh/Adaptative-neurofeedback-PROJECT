# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `A`  |  **Date :** 2026-06-21 17:39


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3263 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7977 | Erreur quadratique moyenne |
| R² | -0.3807 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5208 | 0.500 |
| PR-AUC | 0.3038 | 0.282 |
| Sensitivity (TPR) | 0.4243 | 0.500 |
| Specificity (TNR) | 0.6075 | 0.500 |
| PPV (Precision) | 0.2979 | — |
| NPV | 0.7289 | — |
| Balanced Accuracy | 0.5159 | 0.500 |
| MCC | 0.0291 | 0.000 |
| G-Mean | 0.5077 | 0.500 |
| F1 macro | 0.5063 | 0.500 |
| LR+ | 1.081 | >10 = très utile |
| LR− | 0.948 | <0.1 = très utile |
| Cohen κ | 0.0281 | 0.000 |
| Brier Score | 0.2952 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5216 | [0.4966, 0.5500]  — |
| F1 macro | 0.5065 | [0.4851, 0.5302]  — |
| Sensitivity | 0.4242 | [0.3829, 0.4683]  — |
| Specificity | 0.6079 | [0.5834, 0.6321]  — |
| MCC | 0.0295 | [-0.0123, 0.0755]  — |
| R² | -0.3811 | [-0.4461, -0.3220]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3807 | p=0.0480 | ✅ p<0.05 |
| AUC ROC | 0.5208 | p=0.0560 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2588 | < 0.05 |
| MCE | 0.6226 | < 0.10 |
| Brier Score | 0.2952 | < 0.20 |
| Log-Loss | 0.8698 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.9510 | proche 0 = pas de biais systématique |
| LoA lower | -4.2071 | limite inférieure d'accord |
| LoA upper | +6.1092 | limite supérieure d'accord |
| LoA width | ±5.1582 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.1306 | 2.3289 | 206.0% | 🔴 unstable |
| AUC ROC | 0.5239 | 0.1012 | 19.3% | 🟡 moderate |
| MAE | 2.3260 | 0.4522 | 19.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5207 |
| CI 95% | [0.4927, 0.5488] |
| p-value | 0.147896 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.28


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:39*
