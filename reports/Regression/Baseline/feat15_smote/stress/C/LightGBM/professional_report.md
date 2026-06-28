# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `C`  |  **Date :** 2026-06-21 18:43


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2325 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6682 | Erreur quadratique moyenne |
| R² | -0.2559 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5075 | 0.500 |
| PR-AUC | 0.4297 | 0.414 |
| Sensitivity (TPR) | 0.3941 | 0.500 |
| Specificity (TNR) | 0.6184 | 0.500 |
| PPV (Precision) | 0.4217 | — |
| NPV | 0.5910 | — |
| Balanced Accuracy | 0.5062 | 0.500 |
| MCC | 0.0126 | 0.000 |
| G-Mean | 0.4937 | 0.500 |
| F1 macro | 0.5059 | 0.500 |
| LR+ | 1.033 | >10 = très utile |
| LR− | 0.980 | <0.1 = très utile |
| Cohen κ | 0.0126 | 0.000 |
| Brier Score | 0.3105 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5072 | [0.4944, 0.5217]  — |
| F1 macro | 0.5061 | [0.4947, 0.5183]  — |
| Sensitivity | 0.3945 | [0.3757, 0.4142]  — |
| Specificity | 0.6184 | [0.6018, 0.6335]  — |
| MCC | 0.0130 | [-0.0100, 0.0374]  — |
| R² | -0.2572 | [-0.2884, -0.2301]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2559 | p=0.1760 | ❌ ns |
| AUC ROC | 0.5075 | p=0.1680 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2254 | < 0.05 |
| MCE | 0.5000 | < 0.10 |
| Brier Score | 0.3105 | < 0.20 |
| Log-Loss | 0.9089 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.6097 | proche 0 = pas de biais systématique |
| LoA lower | -4.4820 | limite inférieure d'accord |
| LoA upper | +5.7014 | limite supérieure d'accord |
| LoA width | ±5.0917 | < ±2 pts : excellent |
| % dans LoA | 96.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7189 | 1.1472 | 159.6% | 🔴 unstable |
| AUC ROC | 0.5177 | 0.0641 | 12.4% | 🟢 stable |
| MAE | 2.2322 | 0.5790 | 25.9% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5202 |
| CI 95% | [0.5039, 0.5365] |
| p-value | 0.014935 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:43*
