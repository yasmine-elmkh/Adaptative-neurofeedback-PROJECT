# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `D`  |  **Date :** 2026-06-21 19:23


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3257 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8188 | Erreur quadratique moyenne |
| R² | -0.4016 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.3708 | 0.500 |
| PR-AUC | 0.0115 | 0.015 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 1.0000 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.9851 | — |
| Balanced Accuracy | 0.5000 | 0.500 |
| MCC | 0.0000 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.4963 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.000 | <0.1 = très utile |
| Cohen κ | 0.0000 | 0.000 |
| Brier Score | 0.0151 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4765 | [0.4547, 0.4956]  — |
| F1 macro | 0.4912 | [0.4762, 0.5063]  — |
| Sensitivity | 0.2071 | [0.1832, 0.2308]  — |
| Specificity | 0.7825 | [0.7677, 0.7974]  — |
| MCC | -0.0114 | [-0.0426, 0.0188]  — |
| R² | -0.4007 | [-0.4429, -0.3611]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4016 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4760 | p=0.9900 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2379 | < 0.05 |
| MCE | 0.7491 | < 0.10 |
| Brier Score | 0.2891 | < 0.20 |
| Log-Loss | 0.9415 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3459 | proche 0 = pas de biais systématique |
| LoA lower | -5.1379 | limite inférieure d'accord |
| LoA upper | +5.8296 | limite supérieure d'accord |
| LoA width | ±5.4838 | < ±2 pts : excellent |
| % dans LoA | 96.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0022 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.2541 | 3.7015 | 295.2% | 🔴 unstable |
| AUC ROC | 0.5218 | 0.0674 | 12.9% | 🟢 stable |
| MAE | 2.3255 | 0.7038 | 30.3% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4760 |
| CI 95% | [0.4560, 0.4959] |
| p-value | 0.017989 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:23*
