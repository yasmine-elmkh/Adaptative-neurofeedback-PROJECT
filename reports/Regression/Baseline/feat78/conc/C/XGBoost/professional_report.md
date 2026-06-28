# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `XGBoost`  |  **Exp :** `C`  |  **Date :** 2026-06-21 17:01


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6906 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0984 | Erreur quadratique moyenne |
| R² | -0.0007 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5777 | 0.500 |
| PR-AUC | 0.5725 | 0.517 |
| Sensitivity (TPR) | 0.5883 | 0.500 |
| Specificity (TNR) | 0.5298 | 0.500 |
| PPV (Precision) | 0.5728 | — |
| NPV | 0.5457 | — |
| Balanced Accuracy | 0.5591 | 0.500 |
| MCC | 0.1183 | 0.000 |
| G-Mean | 0.5583 | 0.500 |
| F1 macro | 0.5590 | 0.500 |
| LR+ | 1.251 | >10 = très utile |
| LR− | 0.777 | <0.1 = très utile |
| Cohen κ | 0.1183 | 0.000 |
| Brier Score | 0.2946 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5774 | [0.5607, 0.5963]  ✅ |
| F1 macro | 0.5111 | [0.4951, 0.5264]  — |
| Sensitivity | 0.3157 | [0.2956, 0.3345]  — |
| Specificity | 0.7622 | [0.7423, 0.7800]  — |
| MCC | 0.0869 | [0.0563, 0.1191]  — |
| R² | -0.0005 | [-0.0232, 0.0235]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0007 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5769 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2367 | < 0.05 |
| MCE | 0.3663 | < 0.10 |
| Brier Score | 0.3162 | < 0.20 |
| Log-Loss | 0.9592 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0304 | proche 0 = pas de biais systématique |
| LoA lower | -6.1037 | limite inférieure d'accord |
| LoA upper | +6.0429 | limite supérieure d'accord |
| LoA width | ±6.0733 | < ±2 pts : excellent |
| % dans LoA | 98.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0769 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0463 | 0.1230 | 265.9% | 🔴 unstable |
| AUC ROC | 0.5886 | 0.0507 | 8.6% | 🟢 stable |
| MAE | 2.6947 | 0.2385 | 8.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5769 |
| CI 95% | [0.5598, 0.5939] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.49 et 0.59


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 17:01*
