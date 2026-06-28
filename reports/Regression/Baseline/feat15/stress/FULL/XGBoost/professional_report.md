# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 20:25


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1694 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5855 | Erreur quadratique moyenne |
| R² | -0.1793 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5064 | 0.500 |
| PR-AUC | 0.4887 | 0.489 |
| Sensitivity (TPR) | 0.6242 | 0.500 |
| Specificity (TNR) | 0.3980 | 0.500 |
| PPV (Precision) | 0.4984 | — |
| NPV | 0.5250 | — |
| Balanced Accuracy | 0.5111 | 0.500 |
| MCC | 0.0228 | 0.000 |
| G-Mean | 0.4984 | 0.500 |
| F1 macro | 0.5035 | 0.500 |
| LR+ | 1.037 | >10 = très utile |
| LR− | 0.944 | <0.1 = très utile |
| Cohen κ | 0.0221 | 0.000 |
| Brier Score | 0.3188 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5260 | [0.5118, 0.5398]  ✅ |
| F1 macro | 0.5062 | [0.4956, 0.5177]  — |
| Sensitivity | 0.1922 | [0.1767, 0.2077]  — |
| Specificity | 0.8330 | [0.8227, 0.8422]  — |
| MCC | 0.0300 | [0.0086, 0.0506]  — |
| R² | -0.1789 | [-0.2007, -0.1603]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1793 | p=0.1500 | ❌ ns |
| AUC ROC | 0.5260 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1673 | < 0.05 |
| MCE | 0.7700 | < 0.10 |
| Brier Score | 0.2445 | < 0.20 |
| Log-Loss | 0.7443 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4198 | proche 0 = pas de biais systématique |
| LoA lower | -4.5809 | limite inférieure d'accord |
| LoA upper | +5.4205 | limite supérieure d'accord |
| LoA width | ±5.0007 | < ±2 pts : excellent |
| % dans LoA | 96.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6631 | 1.4465 | 218.1% | 🔴 unstable |
| AUC ROC | 0.5317 | 0.0825 | 15.5% | 🟡 moderate |
| MAE | 2.1693 | 0.5215 | 24.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5260 |
| CI 95% | [0.5119, 0.5400] |
| p-value | 0.000294 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:25*
