# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:45


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4556 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8950 | Erreur quadratique moyenne |
| R² | 0.1264 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6685 | 0.500 |
| PR-AUC | 0.6478 | 0.517 |
| Sensitivity (TPR) | 0.5732 | 0.500 |
| Specificity (TNR) | 0.6526 | 0.500 |
| PPV (Precision) | 0.6381 | — |
| NPV | 0.5887 | — |
| Balanced Accuracy | 0.6129 | 0.500 |
| MCC | 0.2263 | 0.000 |
| G-Mean | 0.6116 | 0.500 |
| F1 macro | 0.6115 | 0.500 |
| LR+ | 1.650 | >10 = très utile |
| LR− | 0.654 | <0.1 = très utile |
| Cohen κ | 0.2251 | 0.000 |
| Brier Score | 0.2684 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6681 | [0.6528, 0.6848]  ✅ |
| F1 macro | 0.6111 | [0.5961, 0.6271]  ✅ |
| Sensitivity | 0.5733 | [0.5524, 0.5941]  — |
| Specificity | 0.6520 | [0.6297, 0.6730]  — |
| MCC | 0.2258 | [0.1967, 0.2566]  — |
| R² | 0.1257 | [0.0997, 0.1518]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1264 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6685 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1809 | < 0.05 |
| MCE | 0.3315 | < 0.10 |
| Brier Score | 0.2684 | < 0.20 |
| Log-Loss | 0.8274 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0245 | proche 0 = pas de biais systématique |
| LoA lower | -5.6991 | limite inférieure d'accord |
| LoA upper | +5.6502 | limite supérieure d'accord |
| LoA width | ±5.6746 | < ±2 pts : excellent |
| % dans LoA | 97.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2108 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.0763 | 0.1953 | 256.0% | 🔴 unstable |
| AUC ROC | 0.6700 | 0.0971 | 14.5% | 🟢 stable |
| MAE | 2.4591 | 0.2348 | 9.5% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6669 |
| CI 95% | [0.6507, 0.6830] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.43 et 0.67


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:45*
