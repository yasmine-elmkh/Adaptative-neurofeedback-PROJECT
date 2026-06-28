# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `A`  |  **Date :** 2026-06-21 16:02


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6220 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0625 | Erreur quadratique moyenne |
| R² | 0.0223 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5994 | 0.500 |
| PR-AUC | 0.5925 | 0.517 |
| Sensitivity (TPR) | 0.5394 | 0.500 |
| Specificity (TNR) | 0.5721 | 0.500 |
| PPV (Precision) | 0.5745 | — |
| NPV | 0.5369 | — |
| Balanced Accuracy | 0.5557 | 0.500 |
| MCC | 0.1114 | 0.000 |
| G-Mean | 0.5555 | 0.500 |
| F1 macro | 0.5552 | 0.500 |
| LR+ | 1.260 | >10 = très utile |
| LR− | 0.805 | <0.1 = très utile |
| Cohen κ | 0.1112 | 0.000 |
| Brier Score | 0.2985 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6002 | [0.5715, 0.6271]  ✅ |
| F1 macro | 0.5554 | [0.5305, 0.5790]  ✅ |
| Sensitivity | 0.5400 | [0.5050, 0.5763]  — |
| Specificity | 0.5722 | [0.5339, 0.6080]  — |
| MCC | 0.1122 | [0.0618, 0.1594]  — |
| R² | 0.0222 | [-0.0237, 0.0646]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0223 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5994 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2240 | < 0.05 |
| MCE | 0.3937 | < 0.10 |
| Brier Score | 0.2985 | < 0.20 |
| Log-Loss | 0.8975 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0368 | proche 0 = pas de biais systématique |
| LoA lower | -6.0410 | limite inférieure d'accord |
| LoA upper | +5.9674 | limite supérieure d'accord |
| LoA width | ±6.0042 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1325 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0320 | 0.2000 | 625.3% | 🔴 unstable |
| AUC ROC | 0.5992 | 0.0626 | 10.5% | 🟢 stable |
| MAE | 2.6383 | 0.2490 | 9.4% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5965 |
| CI 95% | [0.5671, 0.6259] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.57


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:02*
