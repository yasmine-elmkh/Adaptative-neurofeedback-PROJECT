# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `FULL`  |  **Date :** 2026-06-21 20:35


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1670 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5722 | Erreur quadratique moyenne |
| R² | -0.1671 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5113 | 0.500 |
| PR-AUC | 0.4175 | 0.408 |
| Sensitivity (TPR) | 0.1279 | 0.500 |
| Specificity (TNR) | 0.8784 | 0.500 |
| PPV (Precision) | 0.4206 | — |
| NPV | 0.5933 | — |
| Balanced Accuracy | 0.5031 | 0.500 |
| MCC | 0.0093 | 0.000 |
| G-Mean | 0.3352 | 0.500 |
| F1 macro | 0.4522 | 0.500 |
| LR+ | 1.051 | >10 = très utile |
| LR− | 0.993 | <0.1 = très utile |
| Cohen κ | 0.0070 | 0.000 |
| Brier Score | 0.3208 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5113 | [0.4986, 0.5235]  — |
| F1 macro | 0.4517 | [0.4418, 0.4616]  — |
| Sensitivity | 0.1275 | [0.1170, 0.1387]  — |
| Specificity | 0.8784 | [0.8690, 0.8873]  — |
| MCC | 0.0088 | [-0.0127, 0.0308]  — |
| R² | -0.1672 | [-0.1878, -0.1492]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1671 | p=0.5680 | ❌ ns |
| AUC ROC | 0.5113 | p=0.0340 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2601 | < 0.05 |
| MCE | 0.4974 | < 0.10 |
| Brier Score | 0.3208 | < 0.20 |
| Log-Loss | 1.0029 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0486 | proche 0 = pas de biais systématique |
| LoA lower | -5.0895 | limite inférieure d'accord |
| LoA upper | +4.9923 | limite supérieure d'accord |
| LoA width | ±5.0409 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0004 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.5250 | 0.8122 | 154.7% | 🔴 unstable |
| AUC ROC | 0.5357 | 0.0782 | 14.6% | 🟢 stable |
| MAE | 2.1669 | 0.5361 | 24.7% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5164 |
| CI 95% | [0.5023, 0.5304] |
| p-value | 0.022147 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:35*
