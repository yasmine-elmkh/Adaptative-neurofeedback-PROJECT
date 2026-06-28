# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet_FullFT`  |  **Exp :** `C`  |  **Date :** 2026-06-20 02:29


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3586 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8484 | Erreur quadratique moyenne |
| R² | 0.1895 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7149 | 0.500 |
| PR-AUC | 0.7304 | 0.581 |
| Sensitivity (TPR) | 0.9603 | 0.500 |
| Specificity (TNR) | 0.4066 | 0.500 |
| PPV (Precision) | 0.6914 | — |
| NPV | 0.8810 | — |
| Balanced Accuracy | 0.6835 | 0.500 |
| MCC | 0.4583 | 0.000 |
| G-Mean | 0.6249 | 0.500 |
| F1 macro | 0.6802 | 0.500 |
| LR+ | 1.618 | >10 = très utile |
| LR− | 0.098 | <0.1 = très utile |
| Cohen κ | 0.3966 | 0.000 |
| Brier Score | 0.2275 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6791 | [0.6045, 0.7472]  ✅ |
| F1 macro | 0.6162 | [0.5468, 0.6774]  ✅ |
| Sensitivity | 0.6123 | [0.5205, 0.7069]  — |
| Specificity | 0.6229 | [0.5260, 0.7165]  — |
| MCC | 0.2350 | [0.0984, 0.3586]  — |
| R² | 0.1837 | [0.0712, 0.2867]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.1895 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.7149 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1802 | < 0.05 |
| MCE | 0.5586 | < 0.10 |
| Brier Score | 0.2573 | < 0.20 |
| Log-Loss | 0.7591 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.0216 | proche 0 = pas de biais systématique |
| LoA lower | -5.5740 | limite inférieure d'accord |
| LoA upper | +5.6173 | limite supérieure d'accord |
| LoA width | ±5.5956 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.2715 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | 0.1895 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7149 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.3586 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:29*
