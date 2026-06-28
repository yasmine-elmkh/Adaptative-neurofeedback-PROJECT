# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `C`  |  **Date :** 2026-06-21 20:49


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3082 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7961 | Erreur quadratique moyenne |
| R² | -0.3791 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5341 | 0.500 |
| PR-AUC | 0.2970 | 0.261 |
| Sensitivity (TPR) | 0.2072 | 0.500 |
| Specificity (TNR) | 0.8498 | 0.500 |
| PPV (Precision) | 0.3277 | — |
| NPV | 0.7521 | — |
| Balanced Accuracy | 0.5285 | 0.500 |
| MCC | 0.0674 | 0.000 |
| G-Mean | 0.4196 | 0.500 |
| F1 macro | 0.5259 | 0.500 |
| LR+ | 1.380 | >10 = très utile |
| LR− | 0.933 | <0.1 = très utile |
| Cohen κ | 0.0647 | 0.000 |
| Brier Score | 0.2500 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5338 | [0.5175, 0.5510]  ✅ |
| F1 macro | 0.5260 | [0.5126, 0.5399]  ✅ |
| Sensitivity | 0.2074 | [0.1867, 0.2282]  — |
| Specificity | 0.8497 | [0.8393, 0.8609]  — |
| MCC | 0.0675 | [0.0413, 0.0954]  — |
| R² | -0.3806 | [-0.4226, -0.3407]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3791 | p=0.7100 | ❌ ns |
| AUC ROC | 0.5341 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1994 | < 0.05 |
| MCE | 0.6019 | < 0.10 |
| Brier Score | 0.2500 | < 0.20 |
| Log-Loss | 0.8666 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.3709 | proche 0 = pas de biais systématique |
| LoA lower | -5.0615 | limite inférieure d'accord |
| LoA upper | +5.8032 | limite supérieure d'accord |
| LoA width | ±5.4323 | < ±2 pts : excellent |
| % dans LoA | 95.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7963 | 1.2201 | 153.2% | 🔴 unstable |
| AUC ROC | 0.5189 | 0.0940 | 18.1% | 🟡 moderate |
| MAE | 2.3081 | 0.7322 | 31.7% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5170 |
| CI 95% | [0.5005, 0.5334] |
| p-value | 0.043294 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.30


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:49*
