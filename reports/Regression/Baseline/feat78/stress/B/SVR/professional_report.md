# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `SVR`  |  **Exp :** `B`  |  **Date :** 2026-06-21 18:58


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.3629 | Erreur absolue moyenne (0-10) |
| RMSE | 2.8222 | Erreur quadratique moyenne |
| R² | -0.4051 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.4925 | 0.500 |
| PR-AUC | 0.7989 | 0.801 |
| Sensitivity (TPR) | 0.9913 | 0.500 |
| Specificity (TNR) | 0.0087 | 0.500 |
| PPV (Precision) | 0.8010 | — |
| NPV | 0.2000 | — |
| Balanced Accuracy | 0.5000 | 0.500 |
| MCC | 0.0002 | 0.000 |
| G-Mean | 0.0930 | 0.500 |
| F1 macro | 0.4514 | 0.500 |
| LR+ | 1.000 | >10 = très utile |
| LR− | 0.994 | <0.1 = très utile |
| Cohen κ | 0.0001 | 0.000 |
| Brier Score | 0.1942 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.4641 | [0.4436, 0.4857]  — |
| F1 macro | 0.4857 | [0.4702, 0.5019]  — |
| Sensitivity | 0.2650 | [0.2392, 0.2907]  — |
| Specificity | 0.7064 | [0.6902, 0.7230]  — |
| MCC | -0.0285 | [-0.0595, 0.0042]  — |
| R² | -0.4047 | [-0.4500, -0.3626]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.4051 | p=0.9960 | ❌ ns |
| AUC ROC | 0.4634 | p=1.0000 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2620 | < 0.05 |
| MCE | 0.6888 | < 0.10 |
| Brier Score | 0.3009 | < 0.20 |
| Log-Loss | 0.9535 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.5690 | proche 0 = pas de biais systématique |
| LoA lower | -4.8497 | limite inférieure d'accord |
| LoA upper | +5.9877 | limite supérieure d'accord |
| LoA width | ±5.4187 | < ±2 pts : excellent |
| % dans LoA | 96.4% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | -0.0004 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -1.0277 | 1.6681 | 162.3% | 🔴 unstable |
| AUC ROC | 0.4737 | 0.0663 | 14.0% | 🟢 stable |
| MAE | 2.3627 | 0.4275 | 18.1% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.4634 |
| CI 95% | [0.4436, 0.4832] |
| p-value | 0.000287 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 18:58*
