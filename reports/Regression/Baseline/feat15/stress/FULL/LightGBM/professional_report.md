# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 20:27


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1974 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6035 | Erreur quadratique moyenne |
| R² | -0.1957 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4890 | 0.500 |
| PR-AUC | 0.5166 | 0.524 |
| Sensitivity (TPR) | 0.7188 | 0.500 |
| Specificity (TNR) | 0.2698 | 0.500 |
| PPV (Precision) | 0.5201 | — |
| NPV | 0.4656 | — |
| Balanced Accuracy | 0.4943 | 0.500 |
| MCC | -0.0128 | 0.000 |
| G-Mean | 0.4404 | 0.500 |
| F1 macro | 0.4726 | 0.500 |
| LR+ | 0.984 | >10 = très utile |
| LR− | 1.042 | <0.1 = très utile |
| Cohen κ | -0.0117 | 0.000 |
| Brier Score | 0.3255 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5084 | [0.4940, 0.5226]  — |
| F1 macro | 0.4864 | [0.4767, 0.4958]  — |
| Sensitivity | 0.1597 | [0.1459, 0.1746]  — |
| Specificity | 0.8345 | [0.8248, 0.8437]  — |
| MCC | -0.0070 | [-0.0273, 0.0124]  — |
| R² | -0.1958 | [-0.2188, -0.1748]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1957 | p=0.4640 | ❌ ns |
| AUC ROC | 0.5085 | p=0.1280 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1837 | < 0.05 |
| MCE | 0.6054 | < 0.10 |
| Brier Score | 0.2520 | < 0.20 |
| Log-Loss | 0.7677 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4074 | proche 0 = pas de biais systématique |
| LoA lower | -4.6330 | limite inférieure d'accord |
| LoA upper | +5.4478 | limite supérieure d'accord |
| LoA width | ±5.0404 | < ±2 pts : excellent |
| % dans LoA | 96.6% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7036 | 1.4915 | 212.0% | 🔴 unstable |
| AUC ROC | 0.5613 | 0.0765 | 13.6% | 🟢 stable |
| MAE | 2.1973 | 0.5117 | 23.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5085 |
| CI 95% | [0.4946, 0.5224] |
| p-value | 0.229301 |
| Significatif | ❌ NON |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ❌ NON**

Le modèle n'apporte pas de bénéfice net par rapport aux stratégies 'traiter tous' ou 'ne traiter personne'.


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:27*
