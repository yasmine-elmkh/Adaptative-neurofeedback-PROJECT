# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `XGBoost`  |  **Exp :** `A`  |  **Date :** 2026-06-21 18:46


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1828 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5658 | Erreur quadratique moyenne |
| R² | -0.1613 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4938 | 0.500 |
| PR-AUC | 0.5222 | 0.524 |
| Sensitivity (TPR) | 0.7251 | 0.500 |
| Specificity (TNR) | 0.2812 | 0.500 |
| PPV (Precision) | 0.5258 | — |
| NPV | 0.4821 | — |
| Balanced Accuracy | 0.5032 | 0.500 |
| MCC | 0.0071 | 0.000 |
| G-Mean | 0.4516 | 0.500 |
| F1 macro | 0.4824 | 0.500 |
| LR+ | 1.009 | >10 = très utile |
| LR− | 0.977 | <0.1 = très utile |
| Cohen κ | 0.0065 | 0.000 |
| Brier Score | 0.3140 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4698 | [0.4445, 0.4974]  — |
| F1 macro | 0.4528 | [0.4352, 0.4729]  — |
| Sensitivity | 0.0932 | [0.0702, 0.1187]  — |
| Specificity | 0.8619 | [0.8441, 0.8794]  — |
| MCC | -0.0610 | [-0.0989, -0.0184]  — |
| R² | -0.1621 | [-0.1995, -0.1281]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1613 | p=0.8780 | ❌ ns |
| AUC ROC | 0.4701 | p=0.9820 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1812 | < 0.05 |
| MCE | 0.6522 | < 0.10 |
| Brier Score | 0.2472 | < 0.20 |
| Log-Loss | 0.7417 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4404 | proche 0 = pas de biais systématique |
| LoA lower | -4.5151 | limite inférieure d'accord |
| LoA upper | +5.3959 | limite supérieure d'accord |
| LoA width | ±4.9555 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0005 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6706 | 1.6180 | 241.3% | 🔴 unstable |
| AUC ROC | 0.5072 | 0.0716 | 14.1% | 🟢 stable |
| MAE | 2.1827 | 0.4987 | 22.8% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4701 |
| CI 95% | [0.4427, 0.4974] |
| p-value | 0.032097 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:46*
