# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `C`  |  **Date :** 2026-06-21 18:41


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.2082 | Erreur absolue moyenne (0-10) |
| RMSE | 2.6266 | Erreur quadratique moyenne |
| R² | -0.2170 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4956 | 0.500 |
| PR-AUC | 0.4157 | 0.414 |
| Sensitivity (TPR) | 0.3201 | 0.500 |
| Specificity (TNR) | 0.6667 | 0.500 |
| PPV (Precision) | 0.4041 | — |
| NPV | 0.5813 | — |
| Balanced Accuracy | 0.4934 | 0.500 |
| MCC | -0.0138 | 0.000 |
| G-Mean | 0.4620 | 0.500 |
| F1 macro | 0.4892 | 0.500 |
| LR+ | 0.960 | >10 = très utile |
| LR− | 1.020 | <0.1 = très utile |
| Cohen κ | -0.0136 | 0.000 |
| Brier Score | 0.3127 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4953 | [0.4821, 0.5091]  — |
| F1 macro | 0.4891 | [0.4776, 0.5005]  — |
| Sensitivity | 0.3200 | [0.3036, 0.3376]  — |
| Specificity | 0.6665 | [0.6492, 0.6810]  — |
| MCC | -0.0141 | [-0.0363, 0.0093]  — |
| R² | -0.2181 | [-0.2468, -0.1928]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.2170 | p=0.4020 | ❌ ns |
| AUC ROC | 0.4956 | p=0.7640 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2228 | < 0.05 |
| MCE | 0.4999 | < 0.10 |
| Brier Score | 0.3127 | < 0.20 |
| Log-Loss | 0.9060 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4659 | proche 0 = pas de biais systématique |
| LoA lower | -4.6010 | limite inférieure d'accord |
| LoA upper | +5.5329 | limite supérieure d'accord |
| LoA width | ±5.0669 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6543 | 1.1161 | 170.6% | 🔴 unstable |
| AUC ROC | 0.5244 | 0.0683 | 13.0% | 🟢 stable |
| MAE | 2.2080 | 0.5578 | 25.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5057 |
| CI 95% | [0.4896, 0.5218] |
| p-value | 0.488028 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:41*
