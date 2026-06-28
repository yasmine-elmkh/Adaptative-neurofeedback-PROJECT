# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `B`  |  **Date :** 2026-06-21 17:18


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4172 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8917 | Erreur quadratique moyenne |
| R² | -0.4750 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4774 | 0.500 |
| PR-AUC | 0.3991 | 0.414 |
| Sensitivity (TPR) | 0.6523 | 0.500 |
| Specificity (TNR) | 0.3256 | 0.500 |
| PPV (Precision) | 0.4058 | — |
| NPV | 0.5701 | — |
| Balanced Accuracy | 0.4889 | 0.500 |
| MCC | -0.0231 | 0.000 |
| G-Mean | 0.4608 | 0.500 |
| F1 macro | 0.4574 | 0.500 |
| LR+ | 0.967 | >10 = très utile |
| LR− | 1.068 | <0.1 = très utile |
| Cohen κ | -0.0203 | 0.000 |
| Brier Score | 0.3661 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4782 | [0.4572, 0.4989]  — |
| F1 macro | 0.4679 | [0.4520, 0.4832]  — |
| Sensitivity | 0.4345 | [0.4062, 0.4641]  — |
| Specificity | 0.5305 | [0.5125, 0.5477]  — |
| MCC | -0.0316 | [-0.0619, 0.0001]  — |
| R² | -0.4765 | [-0.5250, -0.4308]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4750 | p=0.9960 | ❌ ns |
| AUC ROC | 0.4787 | p=0.9820 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2681 | < 0.05 |
| MCE | 0.7103 | < 0.10 |
| Brier Score | 0.3126 | < 0.20 |
| Log-Loss | 0.9175 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +1.0366 | proche 0 = pas de biais systématique |
| LoA lower | -4.2551 | limite inférieure d'accord |
| LoA upper | +6.3282 | limite supérieure d'accord |
| LoA width | ±5.2916 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.2604 | 2.3806 | 188.9% | 🔴 unstable |
| AUC ROC | 0.5247 | 0.0909 | 17.3% | 🟡 moderate |
| MAE | 2.4169 | 0.4480 | 18.5% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4787 |
| CI 95% | [0.4591, 0.4982] |
| p-value | 0.032129 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:18*
