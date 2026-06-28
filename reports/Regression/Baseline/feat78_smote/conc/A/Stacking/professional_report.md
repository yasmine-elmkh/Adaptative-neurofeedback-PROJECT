# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Stacking`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:06


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 3.2607 | Erreur absolue moyenne (0-10) |
| RMSE | 3.9098 | Erreur quadratique moyenne |
| R² | -0.5935 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.2907 | 0.500 |
| PR-AUC | 0.0095 | 0.014 |
| Sensitivity (TPR) | 0.0000 | 0.500 |
| Specificity (TNR) | 0.9829 | 0.500 |
| PPV (Precision) | 0.0000 | — |
| NPV | 0.9857 | — |
| Balanced Accuracy | 0.4914 | 0.500 |
| MCC | -0.0156 | 0.000 |
| G-Mean | 0.0000 | 0.500 |
| F1 macro | 0.4921 | 0.500 |
| LR+ | 0.000 | >10 = très utile |
| LR− | 1.017 | <0.1 = très utile |
| Cohen κ | -0.0156 | 0.000 |
| Brier Score | 0.0254 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.2927 | [0.1906, 0.4161]  — |
| F1 macro | 0.4922 | [0.4897, 0.4945]  — |
| Sensitivity | 0.0000 | [0.0000, 0.0000]  — |
| Specificity | 0.9830 | [0.9758, 0.9894]  — |
| MCC | -0.0154 | [-0.0203, -0.0109]  — |
| R² | -0.5951 | [-0.6744, -0.5136]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.5935 | p=1.0000 | ❌ ns |
| AUC ROC | 0.2907 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.0340 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.0254 | < 0.20 |
| Log-Loss | 0.1514 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5201 | proche 0 = pas de biais systématique |
| LoA lower | -7.0776 | limite inférieure d'accord |
| LoA upper | +8.1178 | limite supérieure d'accord |
| LoA width | ±7.5977 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0127 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6192 | 0.3598 | 58.1% | 🔴 unstable |
| AUC ROC | 0.4780 | 0.0875 | 18.3% | 🟡 moderate |
| MAE | 3.2385 | 0.4824 | 14.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.3951 |
| CI 95% | [0.3658, 0.4244] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:06*
