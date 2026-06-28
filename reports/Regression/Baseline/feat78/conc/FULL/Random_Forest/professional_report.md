# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `Random Forest`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 18:04


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6697 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0476 | Erreur quadratique moyenne |
| R² | 0.0318 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5879 | 0.500 |
| PR-AUC | 0.5869 | 0.517 |
| Sensitivity (TPR) | 0.6542 | 0.500 |
| Specificity (TNR) | 0.4782 | 0.500 |
| PPV (Precision) | 0.5732 | — |
| NPV | 0.5635 | — |
| Balanced Accuracy | 0.5662 | 0.500 |
| MCC | 0.1345 | 0.000 |
| G-Mean | 0.5593 | 0.500 |
| F1 macro | 0.5642 | 0.500 |
| LR+ | 1.254 | >10 = très utile |
| LR− | 0.723 | <0.1 = très utile |
| Cohen κ | 0.1330 | 0.000 |
| Brier Score | 0.2783 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5877 | [0.5741, 0.6016]  ✅ |
| F1 macro | 0.5053 | [0.4922, 0.5181]  — |
| Sensitivity | 0.2874 | [0.2721, 0.3050]  — |
| Specificity | 0.7942 | [0.7783, 0.8082]  — |
| MCC | 0.0945 | [0.0686, 0.1191]  — |
| R² | 0.0318 | [0.0150, 0.0488]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0318 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5876 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2093 | < 0.05 |
| MCE | 0.3398 | < 0.10 |
| Brier Score | 0.3018 | < 0.20 |
| Log-Loss | 0.8935 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0116 | proche 0 = pas de biais systématique |
| LoA lower | -5.9854 | limite inférieure d'accord |
| LoA upper | +5.9621 | limite supérieure d'accord |
| LoA width | ±5.9738 | < ±2 pts : excellent |
| % dans LoA | 99.1% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0837 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0147 | 0.1457 | 993.4% | 🔴 unstable |
| AUC ROC | 0.5976 | 0.0619 | 10.4% | 🟢 stable |
| MAE | 2.6747 | 0.2372 | 8.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5876 |
| CI 95% | [0.5729, 0.6024] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.62


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:04*
