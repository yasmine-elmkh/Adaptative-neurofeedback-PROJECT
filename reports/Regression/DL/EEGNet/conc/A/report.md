# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `EEGNet`  |  **Exp :** `A`  |  **Date :** 2026-06-20 01:45


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5928 | Erreur absolue moyenne (0-10) |
| RMSE | 3.2080 | Erreur quadratique moyenne |
| R² | -0.0281 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.7548 | 0.500 |
| PR-AUC | 0.8567 | 0.719 |
| Sensitivity (TPR) | 0.9103 | 0.500 |
| Specificity (TNR) | 0.5410 | 0.500 |
| PPV (Precision) | 0.8353 | — |
| NPV | 0.7021 | — |
| Balanced Accuracy | 0.7256 | 0.500 |
| MCC | 0.4924 | 0.000 |
| G-Mean | 0.7017 | 0.500 |
| F1 macro | 0.7411 | 0.500 |
| LR+ | 1.983 | >10 = très utile |
| LR− | 0.166 | <0.1 = très utile |
| Cohen κ | 0.4851 | 0.000 |
| Brier Score | 0.1578 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6456 | [0.5752, 0.7125]  ✅ |
| F1 macro | 0.4260 | [0.3702, 0.4838]  — |
| Sensitivity | 0.1334 | [0.0752, 0.1956]  — |
| Specificity | 0.9030 | [0.8458, 0.9515]  — |
| MCC | 0.0565 | [-0.0745, 0.1828]  — |
| R² | -0.0317 | [-0.1803, 0.0994]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0281 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6450 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.3450 | < 0.05 |
| MCE | 0.5359 | < 0.10 |
| Brier Score | 0.3625 | < 0.20 |
| Log-Loss | 1.2091 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -1.2683 | proche 0 = pas de biais systématique |
| LoA lower | -7.0570 | limite inférieure d'accord |
| LoA upper | +4.5205 | limite supérieure d'accord |
| LoA width | ±5.7888 | < ±2 pts : excellent |
| % dans LoA | 95.9% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0187 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0281 | 0.0000 | 0.0% | 🟢 stable |
| AUC ROC | 0.7548 | 0.0000 | 0.0% | 🟢 stable |
| MAE | 2.5928 | 0.0000 | 0.0% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


✅ **Le modèle est performant pour un système mono-électrode.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-20 01:45*
