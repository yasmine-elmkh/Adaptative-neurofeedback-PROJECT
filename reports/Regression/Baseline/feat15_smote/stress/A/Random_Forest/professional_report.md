# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `A`  |  **Date :** 2026-06-21 17:16


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1391 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5298 | Erreur quadratique moyenne |
| R² | -0.1290 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5171 | 0.500 |
| PR-AUC | 0.4316 | 0.414 |
| Sensitivity (TPR) | 0.1894 | 0.500 |
| Specificity (TNR) | 0.8307 | 0.500 |
| PPV (Precision) | 0.4413 | — |
| NPV | 0.5920 | — |
| Balanced Accuracy | 0.5101 | 0.500 |
| MCC | 0.0259 | 0.000 |
| G-Mean | 0.3967 | 0.500 |
| F1 macro | 0.4782 | 0.500 |
| LR+ | 1.119 | >10 = très utile |
| LR− | 0.976 | <0.1 = très utile |
| Cohen κ | 0.0219 | 0.000 |
| Brier Score | 0.2976 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5170 | [0.4938, 0.5410]  — |
| F1 macro | 0.4776 | [0.4552, 0.4974]  — |
| Sensitivity | 0.1890 | [0.1610, 0.2145]  — |
| Specificity | 0.8304 | [0.8085, 0.8515]  — |
| MCC | 0.0250 | [-0.0234, 0.0679]  — |
| R² | -0.1300 | [-0.1626, -0.0954]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1290 | p=0.0320 | ✅ p<0.05 |
| AUC ROC | 0.5171 | p=0.0840 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2060 | < 0.05 |
| MCE | 0.4475 | < 0.10 |
| Brier Score | 0.2976 | < 0.20 |
| Log-Loss | 0.8747 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1123 | proche 0 = pas de biais systématique |
| LoA lower | -4.8425 | limite inférieure d'accord |
| LoA upper | +5.0671 | limite supérieure d'accord |
| LoA width | ±4.9548 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0083 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5573 | 1.1720 | 210.3% | 🔴 unstable |
| AUC ROC | 0.4924 | 0.0826 | 16.8% | 🟡 moderate |
| MAE | 2.1392 | 0.5501 | 25.7% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5015 |
| CI 95% | [0.4739, 0.5290] |
| p-value | 0.916575 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:16*
