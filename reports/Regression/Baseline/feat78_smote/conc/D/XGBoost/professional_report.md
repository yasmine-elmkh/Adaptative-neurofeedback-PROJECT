# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `D`  |  **Date :** 2026-06-21 17:02


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5563 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0194 | Erreur quadratique moyenne |
| R² | 0.0496 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6259 | 0.500 |
| PR-AUC | 0.6144 | 0.517 |
| Sensitivity (TPR) | 0.5795 | 0.500 |
| Specificity (TNR) | 0.5932 | 0.500 |
| PPV (Precision) | 0.6041 | — |
| NPV | 0.5683 | — |
| Balanced Accuracy | 0.5863 | 0.500 |
| MCC | 0.1725 | 0.000 |
| G-Mean | 0.5863 | 0.500 |
| F1 macro | 0.5860 | 0.500 |
| LR+ | 1.424 | >10 = très utile |
| LR− | 0.709 | <0.1 = très utile |
| Cohen κ | 0.1724 | 0.000 |
| Brier Score | 0.2941 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6258 | [0.6064, 0.6450]  ✅ |
| F1 macro | 0.5858 | [0.5682, 0.6026]  ✅ |
| Sensitivity | 0.5792 | [0.5539, 0.6043]  — |
| Specificity | 0.5932 | [0.5670, 0.6179]  — |
| MCC | 0.1723 | [0.1377, 0.2061]  — |
| R² | 0.0488 | [0.0154, 0.0826]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0496 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6259 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2228 | < 0.05 |
| MCE | 0.4254 | < 0.10 |
| Brier Score | 0.2941 | < 0.20 |
| Log-Loss | 0.9116 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0133 | proche 0 = pas de biais systématique |
| LoA lower | -5.9324 | limite inférieure d'accord |
| LoA upper | +5.9057 | limite supérieure d'accord |
| LoA width | ±5.9190 | < ±2 pts : excellent |
| % dans LoA | 97.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1788 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0103 | 0.2508 | 2424.7% | 🔴 unstable |
| AUC ROC | 0.6213 | 0.0816 | 13.1% | 🟢 stable |
| MAE | 2.5749 | 0.3185 | 12.4% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6229 |
| CI 95% | [0.6024, 0.6433] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:02*
