# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `EEGNet`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-20 02:22


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0644 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4478 | Erreur quadratique moyenne |
| R² | -0.0569 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5430 | 0.500 |
| PR-AUC | 0.5548 | 0.524 |
| Sensitivity (TPR) | 0.3409 | 0.500 |
| Specificity (TNR) | 0.6934 | 0.500 |
| PPV (Precision) | 0.5505 | — |
| NPV | 0.4886 | — |
| Balanced Accuracy | 0.5172 | 0.500 |
| MCC | 0.0366 | 0.000 |
| G-Mean | 0.4862 | 0.500 |
| F1 macro | 0.4972 | 0.500 |
| LR+ | 1.112 | >10 = très utile |
| LR− | 0.950 | <0.1 = très utile |
| Cohen κ | 0.0337 | 0.000 |
| Brier Score | 0.2856 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5325 | [0.5072, 0.5596]  ✅ |
| F1 macro | 0.4194 | [0.4101, 0.4292]  — |
| Sensitivity | 0.0053 | [0.0000, 0.0112]  — |
| Specificity | 0.9853 | [0.9784, 0.9916]  — |
| MCC | -0.0384 | [-0.0694, 0.0001]  — |
| R² | -0.0579 | [-0.0850, -0.0302]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1958 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2434 | < 0.20 |
| Log-Loss | 0.8177 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.4036 | proche 0 = pas de biais systématique |
| LoA lower | -5.1367 | limite inférieure d'accord |
| LoA upper | +4.3295 | limite supérieure d'accord |
| LoA width | ±4.7331 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0016 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.2812 | 0.4611 | 164.0% | 🔴 unstable |
| AUC ROC | 0.5543 | 0.0777 | 14.0% | 🟢 stable |
| MAE | 2.0644 | 0.6400 | 31.0% | 🔴 unstable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 02:22*
