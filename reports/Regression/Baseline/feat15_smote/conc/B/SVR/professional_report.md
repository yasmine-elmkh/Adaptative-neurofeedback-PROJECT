# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:04


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5840 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1143 | Erreur quadratique moyenne |
| R² | -0.0110 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6216 | 0.500 |
| PR-AUC | 0.6151 | 0.517 |
| Sensitivity (TPR) | 0.6291 | 0.500 |
| Specificity (TNR) | 0.5342 | 0.500 |
| PPV (Precision) | 0.5913 | — |
| NPV | 0.5734 | — |
| Balanced Accuracy | 0.5816 | 0.500 |
| MCC | 0.1640 | 0.000 |
| G-Mean | 0.5797 | 0.500 |
| F1 macro | 0.5814 | 0.500 |
| LR+ | 1.351 | >10 = très utile |
| LR− | 0.694 | <0.1 = très utile |
| Cohen κ | 0.1637 | 0.000 |
| Brier Score | 0.3027 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6211 | [0.6018, 0.6425]  ✅ |
| F1 macro | 0.5808 | [0.5639, 0.6009]  ✅ |
| Sensitivity | 0.6290 | [0.6050, 0.6523]  — |
| Specificity | 0.5334 | [0.5076, 0.5602]  — |
| MCC | 0.1631 | [0.1292, 0.2030]  — |
| R² | -0.0117 | [-0.0466, 0.0288]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0110 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6216 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2391 | < 0.05 |
| MCE | 0.3361 | < 0.10 |
| Brier Score | 0.3027 | < 0.20 |
| Log-Loss | 0.9858 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0324 | proche 0 = pas de biais systématique |
| LoA lower | -6.1371 | limite inférieure d'accord |
| LoA upper | +6.0723 | limite supérieure d'accord |
| LoA width | ±6.1047 | < ±2 pts : excellent |
| % dans LoA | 96.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1637 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0631 | 0.2270 | 359.4% | 🔴 unstable |
| AUC ROC | 0.6212 | 0.0660 | 10.6% | 🟢 stable |
| MAE | 2.5955 | 0.2890 | 11.1% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6209 |
| CI 95% | [0.6004, 0.6413] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.46 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:04*
