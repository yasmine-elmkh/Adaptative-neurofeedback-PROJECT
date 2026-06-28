# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `C`  |  **Date :** 2026-06-21 21:51


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1574 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5546 | Erreur quadratique moyenne |
| R² | -0.1512 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5051 | 0.500 |
| PR-AUC | 0.4213 | 0.414 |
| Sensitivity (TPR) | 0.3945 | 0.500 |
| Specificity (TNR) | 0.6280 | 0.500 |
| PPV (Precision) | 0.4282 | — |
| NPV | 0.5949 | — |
| Balanced Accuracy | 0.5112 | 0.500 |
| MCC | 0.0228 | 0.000 |
| G-Mean | 0.4977 | 0.500 |
| F1 macro | 0.5108 | 0.500 |
| LR+ | 1.060 | >10 = très utile |
| LR− | 0.964 | <0.1 = très utile |
| Cohen κ | 0.0227 | 0.000 |
| Brier Score | 0.2821 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5042 | [0.4898, 0.5198]  — |
| F1 macro | 0.4949 | [0.4827, 0.5075]  — |
| Sensitivity | 0.1560 | [0.1409, 0.1732]  — |
| Specificity | 0.8587 | [0.8471, 0.8699]  — |
| MCC | 0.0187 | [-0.0065, 0.0451]  — |
| R² | -0.1521 | [-0.1711, -0.1310]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1512 | p=0.4720 | ❌ ns |
| AUC ROC | 0.5046 | p=0.2700 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1391 | < 0.05 |
| MCE | 0.6913 | < 0.10 |
| Brier Score | 0.2324 | < 0.20 |
| Log-Loss | 0.6858 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.6313 | proche 0 = pas de biais systématique |
| LoA lower | -4.2209 | limite inférieure d'accord |
| LoA upper | +5.4834 | limite supérieure d'accord |
| LoA width | ±4.8522 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6905 | 1.6511 | 239.1% | 🔴 unstable |
| AUC ROC | 0.5168 | 0.0506 | 9.8% | 🟢 stable |
| MAE | 2.1572 | 0.4703 | 21.8% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5046 |
| CI 95% | [0.4882, 0.5209] |
| p-value | 0.584333 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 21:51*
