# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 17:00


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5724 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0123 | Erreur quadratique moyenne |
| R² | 0.0541 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6191 | 0.500 |
| PR-AUC | 0.6015 | 0.517 |
| Sensitivity (TPR) | 0.5520 | 0.500 |
| Specificity (TNR) | 0.5999 | 0.500 |
| PPV (Precision) | 0.5958 | — |
| NPV | 0.5563 | — |
| Balanced Accuracy | 0.5760 | 0.500 |
| MCC | 0.1520 | 0.000 |
| G-Mean | 0.5755 | 0.500 |
| F1 macro | 0.5752 | 0.500 |
| LR+ | 1.380 | >10 = très utile |
| LR− | 0.747 | <0.1 = très utile |
| Cohen κ | 0.1516 | 0.000 |
| Brier Score | 0.2879 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6193 | [0.6039, 0.6339]  ✅ |
| F1 macro | 0.5752 | [0.5627, 0.5869]  ✅ |
| Sensitivity | 0.5522 | [0.5357, 0.5705]  — |
| Specificity | 0.5999 | [0.5801, 0.6182]  — |
| MCC | 0.1522 | [0.1275, 0.1758]  — |
| R² | 0.0546 | [0.0324, 0.0764]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0541 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6191 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2062 | < 0.05 |
| MCE | 0.3537 | < 0.10 |
| Brier Score | 0.2879 | < 0.20 |
| Log-Loss | 0.8682 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0359 | proche 0 = pas de biais systématique |
| LoA lower | -5.8682 | limite inférieure d'accord |
| LoA upper | +5.9401 | limite supérieure d'accord |
| LoA width | ±5.9041 | < ±2 pts : excellent |
| % dans LoA | 97.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1331 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0082 | 0.1749 | 2134.4% | 🔴 unstable |
| AUC ROC | 0.6209 | 0.0622 | 10.0% | 🟢 stable |
| MAE | 2.5792 | 0.2481 | 9.6% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6183 |
| CI 95% | [0.6037, 0.6328] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:00*
