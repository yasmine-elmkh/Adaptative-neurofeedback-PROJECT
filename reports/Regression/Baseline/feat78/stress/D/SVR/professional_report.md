# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `D`  |  **Date :** 2026-06-21 22:04


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3170 | Erreur absolue moyenne (0-10) |
| RMSE | 2.7788 | Erreur quadratique moyenne |
| R² | -0.3622 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4924 | 0.500 |
| PR-AUC | 0.6429 | 0.647 |
| Sensitivity (TPR) | 0.9428 | 0.500 |
| Specificity (TNR) | 0.0702 | 0.500 |
| PPV (Precision) | 0.6498 | — |
| NPV | 0.4016 | — |
| Balanced Accuracy | 0.5065 | 0.500 |
| MCC | 0.0259 | 0.000 |
| G-Mean | 0.2573 | 0.500 |
| F1 macro | 0.4445 | 0.500 |
| LR+ | 1.014 | >10 = très utile |
| LR− | 0.814 | <0.1 = très utile |
| Cohen κ | 0.0161 | 0.000 |
| Brier Score | 0.3150 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4850 | [0.4648, 0.5061]  — |
| F1 macro | 0.4880 | [0.4721, 0.5038]  — |
| Sensitivity | 0.2409 | [0.2150, 0.2670]  — |
| Specificity | 0.7367 | [0.7206, 0.7526]  — |
| MCC | -0.0231 | [-0.0548, 0.0084]  — |
| R² | -0.3628 | [-0.4034, -0.3226]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.3622 | p=0.8600 | ❌ ns |
| AUC ROC | 0.4848 | p=0.9160 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2467 | < 0.05 |
| MCE | 0.6836 | < 0.10 |
| Brier Score | 0.2899 | < 0.20 |
| Log-Loss | 0.9235 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.4161 | proche 0 = pas de biais systématique |
| LoA lower | -4.9697 | limite inférieure d'accord |
| LoA upper | +5.8018 | limite supérieure d'accord |
| LoA width | ±5.3858 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0003 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.9709 | 1.8075 | 186.2% | 🔴 unstable |
| AUC ROC | 0.5027 | 0.0856 | 17.0% | 🟡 moderate |
| MAE | 2.3168 | 0.4489 | 19.4% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4848 |
| CI 95% | [0.4652, 0.5045] |
| p-value | 0.130130 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 22:04*
