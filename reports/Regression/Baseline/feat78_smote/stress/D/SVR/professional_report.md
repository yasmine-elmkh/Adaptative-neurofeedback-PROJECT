# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `D`  |  **Date :** 2026-06-21 20:52


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4199 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8907 | Erreur quadratique moyenne |
| R² | -0.4740 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4887 | 0.500 |
| PR-AUC | 0.2657 | 0.276 |
| Sensitivity (TPR) | 0.3103 | 0.500 |
| Specificity (TNR) | 0.6638 | 0.500 |
| PPV (Precision) | 0.2602 | — |
| NPV | 0.7163 | — |
| Balanced Accuracy | 0.4870 | 0.500 |
| MCC | -0.0247 | 0.000 |
| G-Mean | 0.4538 | 0.500 |
| F1 macro | 0.4860 | 0.500 |
| LR+ | 0.923 | >10 = très utile |
| LR− | 1.039 | <0.1 = très utile |
| Cohen κ | -0.0245 | 0.000 |
| Brier Score | 0.3068 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4890 | [0.4695, 0.5061]  — |
| F1 macro | 0.4863 | [0.4725, 0.5008]  — |
| Sensitivity | 0.3110 | [0.2846, 0.3368]  — |
| Specificity | 0.6637 | [0.6468, 0.6804]  — |
| MCC | -0.0241 | [-0.0527, 0.0060]  — |
| R² | -0.4755 | [-0.5223, -0.4341]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4740 | p=0.8860 | ❌ ns |
| AUC ROC | 0.4887 | p=0.8240 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2642 | < 0.05 |
| MCE | 0.7232 | < 0.10 |
| Brier Score | 0.3068 | < 0.20 |
| Log-Loss | 0.9717 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.6768 | proche 0 = pas de biais systématique |
| LoA lower | -4.8320 | limite inférieure d'accord |
| LoA upper | +6.1857 | limite supérieure d'accord |
| LoA width | ±5.5089 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0001 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.2185 | 2.2547 | 185.0% | 🔴 unstable |
| AUC ROC | 0.5004 | 0.0943 | 18.8% | 🟡 moderate |
| MAE | 2.4197 | 0.4120 | 17.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4894 |
| CI 95% | [0.4699, 0.5090] |
| p-value | 0.288820 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:52*
