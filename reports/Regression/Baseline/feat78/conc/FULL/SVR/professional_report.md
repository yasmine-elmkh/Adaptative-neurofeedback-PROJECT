# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 17:30


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.8067 | Erreur absolue moyenne (0-10) |
| RMSE | 3.3332 | Erreur quadratique moyenne |
| R² | -0.1581 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5568 | 0.500 |
| PR-AUC | 0.5578 | 0.519 |
| Sensitivity (TPR) | 0.6419 | 0.500 |
| Specificity (TNR) | 0.4478 | 0.500 |
| PPV (Precision) | 0.5560 | — |
| NPV | 0.5372 | — |
| Balanced Accuracy | 0.5449 | 0.500 |
| MCC | 0.0915 | 0.000 |
| G-Mean | 0.5362 | 0.500 |
| F1 macro | 0.5422 | 0.500 |
| LR+ | 1.163 | >10 = très utile |
| LR− | 0.800 | <0.1 = très utile |
| Cohen κ | 0.0903 | 0.000 |
| Brier Score | 0.3389 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5543 | [0.5407, 0.5691]  ✅ |
| F1 macro | 0.5179 | [0.5059, 0.5286]  ✅ |
| Sensitivity | 0.3855 | [0.3691, 0.4023]  — |
| Specificity | 0.6751 | [0.6588, 0.6935]  — |
| MCC | 0.0633 | [0.0392, 0.0866]  — |
| R² | -0.1580 | [-0.1895, -0.1292]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1581 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5540 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2974 | < 0.05 |
| MCE | 0.4196 | < 0.10 |
| Brier Score | 0.3534 | < 0.20 |
| Log-Loss | 1.2205 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0146 | proche 0 = pas de biais systématique |
| LoA lower | -6.5482 | limite inférieure d'accord |
| LoA upper | +6.5190 | limite supérieure d'accord |
| LoA width | ±6.5336 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0857 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.2310 | 0.2352 | 101.8% | 🔴 unstable |
| AUC ROC | 0.5822 | 0.0595 | 10.2% | 🟢 stable |
| MAE | 2.8271 | 0.2424 | 8.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5540 |
| CI 95% | [0.5391, 0.5689] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.56


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:30*
