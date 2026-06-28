# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `D`  |  **Date :** 2026-06-21 22:48


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0897 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4363 | Erreur quadratique moyenne |
| R² | -0.0471 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4843 | 0.500 |
| PR-AUC | 0.5043 | 0.524 |
| Sensitivity (TPR) | 0.8883 | 0.500 |
| Specificity (TNR) | 0.1220 | 0.500 |
| PPV (Precision) | 0.5270 | — |
| NPV | 0.4979 | — |
| Balanced Accuracy | 0.5051 | 0.500 |
| MCC | 0.0160 | 0.000 |
| G-Mean | 0.3292 | 0.500 |
| F1 macro | 0.4287 | 0.500 |
| LR+ | 1.012 | >10 = très utile |
| LR− | 0.916 | <0.1 = très utile |
| Cohen κ | 0.0106 | 0.000 |
| Brier Score | 0.2876 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4784 | [0.4592, 0.4992]  — |
| F1 macro | 0.4194 | [0.4142, 0.4249]  — |
| Sensitivity | 0.0026 | [0.0000, 0.0061]  — |
| Specificity | 0.9952 | [0.9928, 0.9976]  — |
| MCC | -0.0150 | [-0.0380, 0.0129]  — |
| R² | -0.0473 | [-0.0593, -0.0344]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0471 | p=0.9680 | ❌ ns |
| AUC ROC | 0.4779 | p=0.9840 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1270 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2249 | < 0.20 |
| Log-Loss | 0.6797 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1934 | proche 0 = pas de biais systématique |
| LoA lower | -4.5673 | limite inférieure d'accord |
| LoA upper | +4.9541 | limite supérieure d'accord |
| LoA width | ±4.7607 | < ±2 pts : excellent |
| % dans LoA | 96.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0007 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.4321 | 1.1837 | 273.9% | 🔴 unstable |
| AUC ROC | 0.4915 | 0.0508 | 10.3% | 🟢 stable |
| MAE | 2.0896 | 0.5525 | 26.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4779 |
| CI 95% | [0.4583, 0.4975] |
| p-value | 0.027260 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 22:48*
