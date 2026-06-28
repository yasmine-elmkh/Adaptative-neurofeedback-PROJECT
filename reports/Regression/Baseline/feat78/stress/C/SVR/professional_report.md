# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `C`  |  **Date :** 2026-06-21 20:28


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3396 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8131 | Erreur quadratique moyenne |
| R² | -0.3960 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4982 | 0.500 |
| PR-AUC | 0.6261 | 0.634 |
| Sensitivity (TPR) | 0.8725 | 0.500 |
| Specificity (TNR) | 0.1420 | 0.500 |
| PPV (Precision) | 0.6381 | — |
| NPV | 0.3910 | — |
| Balanced Accuracy | 0.5072 | 0.500 |
| MCC | 0.0205 | 0.000 |
| G-Mean | 0.3520 | 0.500 |
| F1 macro | 0.4727 | 0.500 |
| LR+ | 1.017 | >10 = très utile |
| LR− | 0.898 | <0.1 = très utile |
| Cohen κ | 0.0167 | 0.000 |
| Brier Score | 0.3165 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4872 | [0.4732, 0.5030]  — |
| F1 macro | 0.4809 | [0.4697, 0.4935]  — |
| Sensitivity | 0.2807 | [0.2618, 0.3018]  — |
| Specificity | 0.6810 | [0.6682, 0.6931]  — |
| MCC | -0.0374 | [-0.0597, -0.0122]  — |
| R² | -0.3976 | [-0.4336, -0.3609]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3960 | p=0.6020 | ❌ ns |
| AUC ROC | 0.4875 | p=0.9620 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2553 | < 0.05 |
| MCE | 0.7196 | < 0.10 |
| Brier Score | 0.3001 | < 0.20 |
| Log-Loss | 0.9422 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5835 | proche 0 = pas de biais systématique |
| LoA lower | -4.8108 | limite inférieure d'accord |
| LoA upper | +5.9778 | limite supérieure d'accord |
| LoA width | ±5.3943 | < ±2 pts : excellent |
| % dans LoA | 96.3% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.0476 | 1.7825 | 170.1% | 🔴 unstable |
| AUC ROC | 0.5045 | 0.0727 | 14.4% | 🟢 stable |
| MAE | 2.3395 | 0.4079 | 17.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4875 |
| CI 95% | [0.4716, 0.5035] |
| p-value | 0.125163 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 20:28*
