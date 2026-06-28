# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 20:37


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
| AUC ROC | 0.5072 | 0.500 |
| PR-AUC | 0.4158 | 0.414 |
| Sensitivity (TPR) | 0.3588 | 0.500 |
| Specificity (TNR) | 0.6615 | 0.500 |
| PPV (Precision) | 0.4281 | — |
| NPV | 0.5937 | — |
| Balanced Accuracy | 0.5102 | 0.500 |
| MCC | 0.0210 | 0.000 |
| G-Mean | 0.4872 | 0.500 |
| F1 macro | 0.5081 | 0.500 |
| LR+ | 1.060 | >10 = très utile |
| LR− | 0.969 | <0.1 = très utile |
| Cohen κ | 0.0208 | 0.000 |
| Brier Score | 0.3044 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5073 | [0.4947, 0.5193]  — |
| F1 macro | 0.5082 | [0.4972, 0.5188]  — |
| Sensitivity | 0.3590 | [0.3437, 0.3748]  — |
| Specificity | 0.6616 | [0.6478, 0.6742]  — |
| MCC | 0.0213 | [-0.0008, 0.0420]  — |
| R² | -0.1789 | [-0.2007, -0.1603]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1793 | p=0.1500 | ❌ ns |
| AUC ROC | 0.5072 | p=0.1600 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2084 | < 0.05 |
| MCE | 0.5226 | < 0.10 |
| Brier Score | 0.3044 | < 0.20 |
| Log-Loss | 0.8734 | minimiser |

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
| AUC ROC | 0.5316 | 0.0741 | 13.9% | 🟢 stable |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:37*
