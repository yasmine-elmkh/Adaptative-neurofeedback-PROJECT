# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Stacking`  |  **Exp :** `B`  |  **Date :** 2026-06-21 20:23


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1446 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5232 | Erreur quadratique moyenne |
| R² | -0.1231 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4841 | 0.500 |
| PR-AUC | 0.6223 | 0.637 |
| Sensitivity (TPR) | 0.9848 | 0.500 |
| Specificity (TNR) | 0.0198 | 0.500 |
| PPV (Precision) | 0.6383 | — |
| NPV | 0.4265 | — |
| Balanced Accuracy | 0.5023 | 0.500 |
| MCC | 0.0174 | 0.000 |
| G-Mean | 0.1398 | 0.500 |
| F1 macro | 0.4062 | 0.500 |
| LR+ | 1.005 | >10 = très utile |
| LR− | 0.766 | <0.1 = très utile |
| Cohen κ | 0.0059 | 0.000 |
| Brier Score | 0.2964 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4849 | [0.4646, 0.5045]  — |
| F1 macro | 0.4567 | [0.4439, 0.4699]  — |
| Sensitivity | 0.0747 | [0.0592, 0.0902]  — |
| Specificity | 0.9082 | [0.8973, 0.9178]  — |
| MCC | -0.0273 | [-0.0553, 0.0007]  — |
| R² | -0.1227 | [-0.1442, -0.0994]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1231 | p=0.9620 | ❌ ns |
| AUC ROC | 0.4846 | p=0.9300 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1444 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2345 | < 0.20 |
| Log-Loss | 0.6993 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4341 | proche 0 = pas de biais systématique |
| LoA lower | -4.4381 | limite inférieure d'accord |
| LoA upper | +5.3064 | limite supérieure d'accord |
| LoA width | ±4.8723 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0002 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6135 | 1.5052 | 245.3% | 🔴 unstable |
| AUC ROC | 0.4978 | 0.0407 | 8.2% | 🟢 stable |
| MAE | 2.1445 | 0.5004 | 23.3% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4846 |
| CI 95% | [0.4649, 0.5043] |
| p-value | 0.125580 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:23*
