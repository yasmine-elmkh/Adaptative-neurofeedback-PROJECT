# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `B`  |  **Date :** 2026-06-20 02:26


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3783 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8644 | Erreur quadratique moyenne |
| R² | 0.1804 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6805 | 0.500 |
| PR-AUC | 0.6846 | 0.571 |
| Sensitivity (TPR) | 0.9597 | 0.500 |
| Specificity (TNR) | 0.3656 | 0.500 |
| PPV (Precision) | 0.6685 | — |
| NPV | 0.8718 | — |
| Balanced Accuracy | 0.6626 | 0.500 |
| MCC | 0.4192 | 0.000 |
| G-Mean | 0.5923 | 0.500 |
| F1 macro | 0.6516 | 0.500 |
| LR+ | 1.513 | >10 = très utile |
| LR− | 0.110 | <0.1 = très utile |
| Cohen κ | 0.3507 | 0.000 |
| Brier Score | 0.2474 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6672 | [0.5907, 0.7328]  ✅ |
| F1 macro | 0.5979 | [0.5331, 0.6610]  ✅ |
| Sensitivity | 0.6541 | [0.5642, 0.7362]  — |
| Specificity | 0.5445 | [0.4554, 0.6368]  — |
| MCC | 0.1998 | [0.0709, 0.3236]  — |
| R² | 0.1746 | [0.0628, 0.2775]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1804 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6805 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1859 | < 0.05 |
| MCE | 0.5136 | < 0.10 |
| Brier Score | 0.2590 | < 0.20 |
| Log-Loss | 0.7654 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1644 | proche 0 = pas de biais systématique |
| LoA lower | -5.4535 | limite inférieure d'accord |
| LoA upper | +5.7823 | limite supérieure d'accord |
| LoA width | ±5.6179 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2303 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1804 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.6805 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3783 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:26*
