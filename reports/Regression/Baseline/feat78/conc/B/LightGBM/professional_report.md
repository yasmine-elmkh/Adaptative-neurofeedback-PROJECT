# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `B`  |  **Date :** 2026-06-21 16:28


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6983 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1086 | Erreur quadratique moyenne |
| R² | -0.0074 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5777 | 0.500 |
| PR-AUC | 0.5691 | 0.517 |
| Sensitivity (TPR) | 0.6304 | 0.500 |
| Specificity (TNR) | 0.4898 | 0.500 |
| PPV (Precision) | 0.5697 | — |
| NPV | 0.5530 | — |
| Balanced Accuracy | 0.5601 | 0.500 |
| MCC | 0.1215 | 0.000 |
| G-Mean | 0.5557 | 0.500 |
| F1 macro | 0.5590 | 0.500 |
| LR+ | 1.236 | >10 = très utile |
| LR− | 0.755 | <0.1 = très utile |
| Cohen κ | 0.1207 | 0.000 |
| Brier Score | 0.2988 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5773 | [0.5561, 0.5986]  ✅ |
| F1 macro | 0.5240 | [0.5055, 0.5422]  ✅ |
| Sensitivity | 0.3413 | [0.3168, 0.3662]  — |
| Specificity | 0.7534 | [0.7314, 0.7754]  — |
| MCC | 0.1037 | [0.0672, 0.1407]  — |
| R² | -0.0075 | [-0.0393, 0.0201]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0074 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.5772 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2369 | < 0.05 |
| MCE | 0.3788 | < 0.10 |
| Brier Score | 0.3174 | < 0.20 |
| Log-Loss | 0.9744 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0234 | proche 0 = pas de biais systématique |
| LoA lower | -6.1172 | limite inférieure d'accord |
| LoA upper | +6.0704 | limite supérieure d'accord |
| LoA width | ±6.0938 | < ±2 pts : excellent |
| % dans LoA | 98.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0881 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0631 | 0.1722 | 272.8% | 🔴 unstable |
| AUC ROC | 0.5976 | 0.0890 | 14.9% | 🟢 stable |
| MAE | 2.7064 | 0.2103 | 7.8% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5772 |
| CI 95% | [0.5562, 0.5981] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:28*
