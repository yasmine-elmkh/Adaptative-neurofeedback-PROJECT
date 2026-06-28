# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_LayerReplacement`  |  **Exp :** `B`  |  **Date :** 2026-06-20 02:32


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3642 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7848 | Erreur quadratique moyenne |
| R² | 0.2253 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7142 | 0.500 |
| PR-AUC | 0.6809 | 0.535 |
| Sensitivity (TPR) | 0.8276 | 0.500 |
| Specificity (TNR) | 0.5347 | 0.500 |
| PPV (Precision) | 0.6713 | — |
| NPV | 0.7297 | — |
| Balanced Accuracy | 0.6811 | 0.500 |
| MCC | 0.3812 | 0.000 |
| G-Mean | 0.6652 | 0.500 |
| F1 macro | 0.6792 | 0.500 |
| LR+ | 1.778 | >10 = très utile |
| LR− | 0.322 | <0.1 = très utile |
| Cohen κ | 0.3686 | 0.000 |
| Brier Score | 0.2246 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.7115 | [0.6375, 0.7796]  ✅ |
| F1 macro | 0.6447 | [0.5806, 0.7004]  ✅ |
| Sensitivity | 0.6140 | [0.5276, 0.6937]  — |
| Specificity | 0.6802 | [0.5859, 0.7767]  — |
| MCC | 0.2944 | [0.1655, 0.4080]  — |
| R² | 0.2205 | [0.1280, 0.3098]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.2253 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7142 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1575 | < 0.05 |
| MCE | 0.3860 | < 0.10 |
| Brier Score | 0.2355 | < 0.20 |
| Log-Loss | 0.6930 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0188 | proche 0 = pas de biais systématique |
| LoA lower | -5.4519 | limite inférieure d'accord |
| LoA upper | +5.4896 | limite supérieure d'accord |
| LoA width | ±5.4708 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2699 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.2253 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7142 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3642 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:32*
