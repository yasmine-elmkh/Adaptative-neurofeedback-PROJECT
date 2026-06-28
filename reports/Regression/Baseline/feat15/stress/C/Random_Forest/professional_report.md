# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `C`  |  **Date :** 2026-06-21 18:32


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1857 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6132 | Erreur quadratique moyenne |
| R² | -0.2046 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4891 | 0.500 |
| PR-AUC | 0.4163 | 0.414 |
| Sensitivity (TPR) | 0.1910 | 0.500 |
| Specificity (TNR) | 0.8230 | 0.500 |
| PPV (Precision) | 0.4326 | — |
| NPV | 0.5903 | — |
| Balanced Accuracy | 0.5070 | 0.500 |
| MCC | 0.0179 | 0.000 |
| G-Mean | 0.3965 | 0.500 |
| F1 macro | 0.4763 | 0.500 |
| LR+ | 1.080 | >10 = très utile |
| LR− | 0.983 | <0.1 = très utile |
| Cohen κ | 0.0153 | 0.000 |
| Brier Score | 0.3165 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5085 | [0.4920, 0.5247]  — |
| F1 macro | 0.4953 | [0.4848, 0.5083]  — |
| Sensitivity | 0.1335 | [0.1195, 0.1499]  — |
| Specificity | 0.8944 | [0.8846, 0.9031]  — |
| MCC | 0.0396 | [0.0161, 0.0673]  — |
| R² | -0.2057 | [-0.2318, -0.1813]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2046 | p=0.8640 | ❌ ns |
| AUC ROC | 0.5087 | p=0.1200 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1803 | < 0.05 |
| MCE | 0.5933 | < 0.10 |
| Brier Score | 0.2507 | < 0.20 |
| Log-Loss | 0.8051 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1906 | proche 0 = pas de biais systématique |
| LoA lower | -4.9180 | limite inférieure d'accord |
| LoA upper | +5.2992 | limite supérieure d'accord |
| LoA width | ±5.1086 | < ±2 pts : excellent |
| % dans LoA | 95.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0006 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5589 | 0.8336 | 149.2% | 🔴 unstable |
| AUC ROC | 0.4997 | 0.0452 | 9.0% | 🟢 stable |
| MAE | 2.1856 | 0.6194 | 28.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5087 |
| CI 95% | [0.4922, 0.5252] |
| p-value | 0.299934 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.31


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:32*
