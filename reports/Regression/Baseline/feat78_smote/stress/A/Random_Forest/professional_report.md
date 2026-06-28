# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `A`  |  **Date :** 2026-06-21 17:59


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1363 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5246 | Erreur quadratique moyenne |
| R² | -0.1244 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5249 | 0.500 |
| PR-AUC | 0.4481 | 0.414 |
| Sensitivity (TPR) | 0.1763 | 0.500 |
| Specificity (TNR) | 0.8620 | 0.500 |
| PPV (Precision) | 0.4742 | — |
| NPV | 0.5971 | — |
| Balanced Accuracy | 0.5191 | 0.500 |
| MCC | 0.0522 | 0.000 |
| G-Mean | 0.3898 | 0.500 |
| F1 macro | 0.4812 | 0.500 |
| LR+ | 1.277 | >10 = très utile |
| LR− | 0.956 | <0.1 = très utile |
| Cohen κ | 0.0421 | 0.000 |
| Brier Score | 0.2927 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5253 | [0.5028, 0.5497]  ✅ |
| F1 macro | 0.4811 | [0.4595, 0.5032]  — |
| Sensitivity | 0.1761 | [0.1523, 0.2014]  — |
| Specificity | 0.8626 | [0.8428, 0.8820]  — |
| MCC | 0.0528 | [0.0096, 0.0952]  — |
| R² | -0.1242 | [-0.1584, -0.0875]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1244 | p=0.0040 | ✅ p<0.05 |
| AUC ROC | 0.5249 | p=0.0220 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1919 | < 0.05 |
| MCE | 0.4323 | < 0.10 |
| Brier Score | 0.2927 | < 0.20 |
| Log-Loss | 0.8776 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1029 | proche 0 = pas de biais systématique |
| LoA lower | -4.8425 | limite inférieure d'accord |
| LoA upper | +5.0483 | limite supérieure d'accord |
| LoA width | ±4.9454 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0132 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5462 | 1.2143 | 222.3% | 🔴 unstable |
| AUC ROC | 0.4993 | 0.0920 | 18.4% | 🟡 moderate |
| MAE | 2.1363 | 0.5384 | 25.2% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5233 |
| CI 95% | [0.4955, 0.5512] |
| p-value | 0.100650 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.28 et 0.33


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:59*
