# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `A`  |  **Date :** 2026-06-21 17:19


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2016 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6132 | Erreur quadratique moyenne |
| R² | -0.2046 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5057 | 0.500 |
| PR-AUC | 0.4227 | 0.414 |
| Sensitivity (TPR) | 0.3309 | 0.500 |
| Specificity (TNR) | 0.6884 | 0.500 |
| PPV (Precision) | 0.4286 | — |
| NPV | 0.5930 | — |
| Balanced Accuracy | 0.5097 | 0.500 |
| MCC | 0.0204 | 0.000 |
| G-Mean | 0.4773 | 0.500 |
| F1 macro | 0.5053 | 0.500 |
| LR+ | 1.062 | >10 = très utile |
| LR− | 0.972 | <0.1 = très utile |
| Cohen κ | 0.0200 | 0.000 |
| Brier Score | 0.3066 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5057 | [0.4823, 0.5299]  — |
| F1 macro | 0.5050 | [0.4828, 0.5264]  — |
| Sensitivity | 0.3310 | [0.3013, 0.3615]  — |
| Specificity | 0.6879 | [0.6631, 0.7139]  — |
| MCC | 0.0199 | [-0.0240, 0.0620]  — |
| R² | -0.2060 | [-0.2502, -0.1669]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2046 | p=0.2920 | ❌ ns |
| AUC ROC | 0.5057 | p=0.3340 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2186 | < 0.05 |
| MCE | 0.5212 | < 0.10 |
| Brier Score | 0.3066 | < 0.20 |
| Log-Loss | 0.8963 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4033 | proche 0 = pas de biais systématique |
| LoA lower | -4.6584 | limite inférieure d'accord |
| LoA upper | +5.4651 | limite supérieure d'accord |
| LoA width | ±5.0618 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0003 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7437 | 1.6358 | 219.9% | 🔴 unstable |
| AUC ROC | 0.4988 | 0.0715 | 14.3% | 🟢 stable |
| MAE | 2.2016 | 0.5221 | 23.7% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4971 |
| CI 95% | [0.4694, 0.5249] |
| p-value | 0.840187 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:19*
