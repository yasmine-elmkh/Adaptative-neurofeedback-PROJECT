# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `C`  |  **Date :** 2026-06-21 21:48


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1597 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5520 | Erreur quadratique moyenne |
| R² | -0.1489 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4932 | 0.500 |
| PR-AUC | 0.2445 | 0.246 |
| Sensitivity (TPR) | 0.0134 | 0.500 |
| Specificity (TNR) | 0.9919 | 0.500 |
| PPV (Precision) | 0.3509 | — |
| NPV | 0.7548 | — |
| Balanced Accuracy | 0.5027 | 0.500 |
| MCC | 0.0237 | 0.000 |
| G-Mean | 0.1155 | 0.500 |
| F1 macro | 0.4416 | 0.500 |
| LR+ | 1.655 | >10 = très utile |
| LR− | 0.995 | <0.1 = très utile |
| Cohen κ | 0.0079 | 0.000 |
| Brier Score | 0.2105 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4869 | [0.4724, 0.5029]  — |
| F1 macro | 0.4769 | [0.4661, 0.4886]  — |
| Sensitivity | 0.1219 | [0.1073, 0.1369]  — |
| Specificity | 0.8707 | [0.8593, 0.8808]  — |
| MCC | -0.0101 | [-0.0322, 0.0141]  — |
| R² | -0.1500 | [-0.1691, -0.1307]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1489 | p=0.8660 | ❌ ns |
| AUC ROC | 0.4872 | p=0.9320 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1444 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2357 | < 0.20 |
| Log-Loss | 0.6971 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5835 | proche 0 = pas de biais systématique |
| LoA lower | -4.2864 | limite inférieure d'accord |
| LoA upper | +5.4534 | limite supérieure d'accord |
| LoA width | ±4.8699 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6811 | 1.6259 | 238.7% | 🔴 unstable |
| AUC ROC | 0.5152 | 0.0622 | 12.1% | 🟢 stable |
| MAE | 2.1595 | 0.4779 | 22.1% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4872 |
| CI 95% | [0.4710, 0.5035] |
| p-value | 0.122813 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 21:48*
