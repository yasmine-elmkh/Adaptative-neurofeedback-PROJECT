# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `C`  |  **Date :** 2026-06-21 17:59


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4079 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8992 | Erreur quadratique moyenne |
| R² | -0.4827 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4886 | 0.500 |
| PR-AUC | 0.2603 | 0.273 |
| Sensitivity (TPR) | 0.4192 | 0.500 |
| Specificity (TNR) | 0.5660 | 0.500 |
| PPV (Precision) | 0.2666 | — |
| NPV | 0.7214 | — |
| Balanced Accuracy | 0.4926 | 0.500 |
| MCC | -0.0133 | 0.000 |
| G-Mean | 0.4871 | 0.500 |
| F1 macro | 0.4802 | 0.500 |
| LR+ | 0.966 | >10 = très utile |
| LR− | 1.026 | <0.1 = très utile |
| Cohen κ | -0.0125 | 0.000 |
| Brier Score | 0.3063 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4879 | [0.4712, 0.5037]  — |
| F1 macro | 0.4795 | [0.4660, 0.4919]  — |
| Sensitivity | 0.4182 | [0.3944, 0.4424]  — |
| Specificity | 0.5658 | [0.5513, 0.5805]  — |
| MCC | -0.0144 | [-0.0405, 0.0107]  — |
| R² | -0.4851 | [-0.5203, -0.4444]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4827 | p=0.9960 | ❌ ns |
| AUC ROC | 0.4886 | p=0.9120 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2641 | < 0.05 |
| MCE | 0.7278 | < 0.10 |
| Brier Score | 0.3063 | < 0.20 |
| Log-Loss | 0.9138 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +1.0081 | proche 0 = pas de biais systématique |
| LoA lower | -4.3201 | limite inférieure d'accord |
| LoA upper | +6.3363 | limite supérieure d'accord |
| LoA width | ±5.3282 | < ±2 pts : excellent |
| % dans LoA | 96.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.2490 | 2.2484 | 180.0% | 🔴 unstable |
| AUC ROC | 0.5189 | 0.1161 | 22.4% | 🟡 moderate |
| MAE | 2.4077 | 0.4438 | 18.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4875 |
| CI 95% | [0.4717, 0.5034] |
| p-value | 0.124244 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:59*
