# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 22:45


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1545 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5550 | Erreur quadratique moyenne |
| R² | -0.1515 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5101 | 0.500 |
| PR-AUC | 0.4172 | 0.414 |
| Sensitivity (TPR) | 0.3168 | 0.500 |
| Specificity (TNR) | 0.6859 | 0.500 |
| PPV (Precision) | 0.4160 | — |
| NPV | 0.5871 | — |
| Balanced Accuracy | 0.5014 | 0.500 |
| MCC | 0.0029 | 0.000 |
| G-Mean | 0.4662 | 0.500 |
| F1 macro | 0.4962 | 0.500 |
| LR+ | 1.009 | >10 = très utile |
| LR− | 0.996 | <0.1 = très utile |
| Cohen κ | 0.0028 | 0.000 |
| Brier Score | 0.2969 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5103 | [0.4976, 0.5233]  — |
| F1 macro | 0.4964 | [0.4855, 0.5076]  — |
| Sensitivity | 0.3170 | [0.3018, 0.3333]  — |
| Specificity | 0.6862 | [0.6738, 0.6998]  — |
| MCC | 0.0034 | [-0.0179, 0.0252]  — |
| R² | -0.1514 | [-0.1690, -0.1334]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1515 | p=0.2620 | ❌ ns |
| AUC ROC | 0.5101 | p=0.0620 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2015 | < 0.05 |
| MCE | 0.5247 | < 0.10 |
| Brier Score | 0.2969 | < 0.20 |
| Log-Loss | 0.8432 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3896 | proche 0 = pas de biais systématique |
| LoA lower | -4.5598 | limite inférieure d'accord |
| LoA upper | +5.3391 | limite supérieure d'accord |
| LoA width | ±4.9495 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6184 | 1.3869 | 224.3% | 🔴 unstable |
| AUC ROC | 0.5420 | 0.0643 | 11.9% | 🟢 stable |
| MAE | 2.1544 | 0.5292 | 24.6% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5104 |
| CI 95% | [0.4966, 0.5242] |
| p-value | 0.140259 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 22:45*
