# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:04


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 3.2819 | Erreur absolue moyenne (0-10) |
| RMSE | 3.9208 | Erreur quadratique moyenne |
| R² | -0.6025 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.3888 | 0.500 |
| PR-AUC | 0.0114 | 0.014 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 0.9822 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.9857 | — |
| Balanced Accuracy | 0.4911 | 0.500 |
| MCC | -0.0160 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.4920 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.018 | <0.1 = très utile |
| Cohen κ | -0.0159 | 0.000 |
| Brier Score | 0.0286 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.3893 | [0.2541, 0.5179]  — |
| F1 macro | 0.4919 | [0.4894, 0.4941]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 0.9819 | [0.9743, 0.9886]  — |
| MCC | -0.0159 | [-0.0207, -0.0113]  — |
| R² | -0.6052 | [-0.6880, -0.5199]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.6025 | p=1.0000 | ❌ ns |
| AUC ROC | 0.3888 | p=0.9440 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.0361 | < 0.05 |
| MCE | 0.9258 | < 0.10 |
| Brier Score | 0.0286 | < 0.20 |
| Log-Loss | 0.1508 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5255 | proche 0 = pas de biais systématique |
| LoA lower | -7.0926 | limite inférieure d'accord |
| LoA upper | +8.1437 | limite supérieure d'accord |
| LoA width | ±7.6182 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0132 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6069 | 0.3206 | 52.8% | 🔴 unstable |
| AUC ROC | 0.4864 | 0.0452 | 9.3% | 🟢 stable |
| MAE | 3.2437 | 0.4729 | 14.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.3817 |
| CI 95% | [0.3526, 0.4108] |
| p-value | 0.000000 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:04*
