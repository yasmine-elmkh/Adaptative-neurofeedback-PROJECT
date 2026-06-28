# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `B`  |  **Date :** 2026-06-21 19:01


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2094 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6498 | Erreur quadratique moyenne |
| R² | -0.2386 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4811 | 0.500 |
| PR-AUC | 0.4032 | 0.414 |
| Sensitivity (TPR) | 0.2788 | 0.500 |
| Specificity (TNR) | 0.7036 | 0.500 |
| PPV (Precision) | 0.3991 | — |
| NPV | 0.5801 | — |
| Balanced Accuracy | 0.4912 | 0.500 |
| MCC | -0.0191 | 0.000 |
| G-Mean | 0.4429 | 0.500 |
| F1 macro | 0.4821 | 0.500 |
| LR+ | 0.941 | >10 = très utile |
| LR− | 1.025 | <0.1 = très utile |
| Cohen κ | -0.0184 | 0.000 |
| Brier Score | 0.3098 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4817 | [0.4631, 0.4986]  — |
| F1 macro | 0.4822 | [0.4674, 0.4973]  — |
| Sensitivity | 0.2790 | [0.2563, 0.3004]  — |
| Specificity | 0.7038 | [0.6871, 0.7230]  — |
| MCC | -0.0187 | [-0.0486, 0.0120]  — |
| R² | -0.2382 | [-0.2668, -0.2074]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2386 | p=1.0000 | ❌ ns |
| AUC ROC | 0.4811 | p=0.9860 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2176 | < 0.05 |
| MCE | 0.5890 | < 0.10 |
| Brier Score | 0.3098 | < 0.20 |
| Log-Loss | 0.9002 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4067 | proche 0 = pas de biais systématique |
| LoA lower | -4.7261 | limite inférieure d'accord |
| LoA upper | +5.5394 | limite supérieure d'accord |
| LoA width | ±5.1327 | < ±2 pts : excellent |
| % dans LoA | 95.5% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0010 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.7533 | 1.7560 | 233.1% | 🔴 unstable |
| AUC ROC | 0.5242 | 0.0605 | 11.5% | 🟢 stable |
| MAE | 2.2092 | 0.6487 | 29.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4687 |
| CI 95% | [0.4488, 0.4886] |
| p-value | 0.002068 |
| Significatif | ✅ OUI |

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 19:01*
