# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `Random Forest`  |  **Exp :** `A`  |  **Date :** 2026-06-21 18:42


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.0828 | Erreur absolue moyenne (0-10) |
| RMSE | 2.4317 | Erreur quadratique moyenne |
| R² | -0.0431 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5017 | 0.500 |
| PR-AUC | 0.5324 | 0.531 |
| Sensitivity (TPR) | 0.9701 | 0.500 |
| Specificity (TNR) | 0.0370 | 0.500 |
| PPV (Precision) | 0.5323 | — |
| NPV | 0.5224 | — |
| Balanced Accuracy | 0.5035 | 0.500 |
| MCC | 0.0197 | 0.000 |
| G-Mean | 0.1894 | 0.500 |
| F1 macro | 0.3783 | 0.500 |
| LR+ | 1.007 | >10 = très utile |
| LR− | 0.809 | <0.1 = très utile |
| Cohen κ | 0.0075 | 0.000 |
| Brier Score | 0.3016 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4701 | [0.4436, 0.4992]  — |
| F1 macro | 0.4185 | [0.4103, 0.4269]  — |
| Sensitivity | 0.0017 | [0.0000, 0.0055]  — |
| Specificity | 0.9965 | [0.9930, 0.9993]  — |
| MCC | -0.0140 | [-0.0405, 0.0322]  — |
| R² | -0.0437 | [-0.0596, -0.0263]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0431 | p=0.7960 | ❌ ns |
| AUC ROC | 0.4704 | p=0.9820 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1291 | < 0.05 |
| MCE | 0.9500 | < 0.10 |
| Brier Score | 0.2249 | < 0.20 |
| Log-Loss | 0.6787 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.2076 | proche 0 = pas de biais systématique |
| LoA lower | -4.5423 | limite inférieure d'accord |
| LoA upper | +4.9575 | limite supérieure d'accord |
| LoA width | ±4.7499 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0007 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.4297 | 1.2242 | 284.9% | 🔴 unstable |
| AUC ROC | 0.5178 | 0.0696 | 13.4% | 🟢 stable |
| MAE | 2.0827 | 0.5599 | 26.9% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4704 |
| CI 95% | [0.4428, 0.4980] |
| p-value | 0.035862 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:42*
