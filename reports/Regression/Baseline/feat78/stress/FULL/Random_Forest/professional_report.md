# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `FULL`  |  **Date :** 2026-06-22 00:23


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0855 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4297 | Erreur quadratique moyenne |
| R² | -0.0414 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4793 | 0.500 |
| PR-AUC | 0.4068 | 0.415 |
| Sensitivity (TPR) | 0.0809 | 0.500 |
| Specificity (TNR) | 0.9234 | 0.500 |
| PPV (Precision) | 0.4288 | — |
| NPV | 0.5858 | — |
| Balanced Accuracy | 0.5022 | 0.500 |
| MCC | 0.0079 | 0.000 |
| G-Mean | 0.2734 | 0.500 |
| F1 macro | 0.4265 | 0.500 |
| LR+ | 1.057 | >10 = très utile |
| LR− | 0.995 | <0.1 = très utile |
| Cohen κ | 0.0049 | 0.000 |
| Brier Score | 0.2676 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4798 | [0.4640, 0.4944]  — |
| F1 macro | 0.4179 | [0.4147, 0.4214]  — |
| Sensitivity | 0.0004 | [0.0000, 0.0013]  — |
| Specificity | 0.9988 | [0.9978, 0.9995]  — |
| MCC | -0.0114 | [-0.0227, 0.0043]  — |
| R² | -0.0413 | [-0.0486, -0.0340]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0414 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4800 | p=0.9960 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1230 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2236 | < 0.20 |
| Log-Loss | 0.6765 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.1737 | proche 0 = pas de biais systématique |
| LoA lower | -4.5765 | limite inférieure d'accord |
| LoA upper | +4.9240 | limite supérieure d'accord |
| LoA width | ±4.7502 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0005 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.4197 | 1.1678 | 278.3% | 🔴 unstable |
| AUC ROC | 0.4924 | 0.0440 | 8.9% | 🟢 stable |
| MAE | 2.0853 | 0.5615 | 26.9% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4800 |
| CI 95% | [0.4659, 0.4942] |
| p-value | 0.005600 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.30 et 0.30


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-22 00:23*
