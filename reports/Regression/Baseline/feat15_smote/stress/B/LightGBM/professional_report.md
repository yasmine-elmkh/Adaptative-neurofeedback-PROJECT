# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `B`  |  **Date :** 2026-06-21 17:53


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2285 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6589 | Erreur quadratique moyenne |
| R² | -0.2471 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4873 | 0.500 |
| PR-AUC | 0.4076 | 0.414 |
| Sensitivity (TPR) | 0.3004 | 0.500 |
| Specificity (TNR) | 0.6816 | 0.500 |
| PPV (Precision) | 0.3998 | — |
| NPV | 0.5798 | — |
| Balanced Accuracy | 0.4910 | 0.500 |
| MCC | -0.0192 | 0.000 |
| G-Mean | 0.4525 | 0.500 |
| F1 macro | 0.4848 | 0.500 |
| LR+ | 0.943 | >10 = très utile |
| LR− | 1.026 | <0.1 = très utile |
| Cohen κ | -0.0187 | 0.000 |
| Brier Score | 0.3185 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4875 | [0.4693, 0.5064]  — |
| F1 macro | 0.4848 | [0.4684, 0.5001]  — |
| Sensitivity | 0.3003 | [0.2778, 0.3212]  — |
| Specificity | 0.6819 | [0.6622, 0.7000]  — |
| MCC | -0.0190 | [-0.0518, 0.0121]  — |
| R² | -0.2482 | [-0.2801, -0.2151]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2471 | p=0.9440 | ❌ ns |
| AUC ROC | 0.4873 | p=0.9060 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2370 | < 0.05 |
| MCE | 0.5197 | < 0.10 |
| Brier Score | 0.3185 | < 0.20 |
| Log-Loss | 0.9442 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3982 | proche 0 = pas de biais systématique |
| LoA lower | -4.7551 | limite inférieure d'accord |
| LoA upper | +5.5514 | limite supérieure d'accord |
| LoA width | ±5.1533 | < ±2 pts : excellent |
| % dans LoA | 96.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0004 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.9220 | 2.6597 | 288.5% | 🔴 unstable |
| AUC ROC | 0.5147 | 0.0676 | 13.1% | 🟢 stable |
| MAE | 2.2282 | 0.6273 | 28.2% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4814 |
| CI 95% | [0.4615, 0.5013] |
| p-value | 0.066508 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:53*
