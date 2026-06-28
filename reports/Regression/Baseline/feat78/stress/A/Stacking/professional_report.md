# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `A`  |  **Date :** 2026-06-21 18:54


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1622 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5538 | Erreur quadratique moyenne |
| R² | -0.1505 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5123 | 0.500 |
| PR-AUC | 0.5264 | 0.521 |
| Sensitivity (TPR) | 0.8808 | 0.500 |
| Specificity (TNR) | 0.1584 | 0.500 |
| PPV (Precision) | 0.5320 | — |
| NPV | 0.5504 | — |
| Balanced Accuracy | 0.5196 | 0.500 |
| MCC | 0.0568 | 0.000 |
| G-Mean | 0.3735 | 0.500 |
| F1 macro | 0.4546 | 0.500 |
| LR+ | 1.047 | >10 = très utile |
| LR− | 0.752 | <0.1 = très utile |
| Cohen κ | 0.0404 | 0.000 |
| Brier Score | 0.3035 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4936 | [0.4668, 0.5209]  — |
| F1 macro | 0.4824 | [0.4618, 0.5031]  — |
| Sensitivity | 0.1491 | [0.1205, 0.1792]  — |
| Specificity | 0.8413 | [0.8226, 0.8586]  — |
| MCC | -0.0119 | [-0.0534, 0.0313]  — |
| R² | -0.1512 | [-0.1912, -0.1178]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1505 | p=0.3480 | ❌ ns |
| AUC ROC | 0.4934 | p=0.6460 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1470 | < 0.05 |
| MCE | 0.7308 | < 0.10 |
| Brier Score | 0.2373 | < 0.20 |
| Log-Loss | 0.6838 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.7059 | proche 0 = pas de biais systématique |
| LoA lower | -4.1057 | limite inférieure d'accord |
| LoA upper | +5.5175 | limite supérieure d'accord |
| LoA width | ±4.8116 | < ±2 pts : excellent |
| % dans LoA | 97.2% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6792 | 1.6200 | 238.5% | 🔴 unstable |
| AUC ROC | 0.5043 | 0.0782 | 15.5% | 🟡 moderate |
| MAE | 2.1620 | 0.4751 | 22.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4934 |
| CI 95% | [0.4656, 0.5211] |
| p-value | 0.640060 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:54*
