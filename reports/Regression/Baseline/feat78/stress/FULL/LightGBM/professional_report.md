# NeuroCap — Rapport Professionnel de Performance
**Target :** `stress`  |  **Modèle :** `LightGBM`  |  **Exp :** `FULL`  |  **Date :** 2026-06-22 00:30


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.1578 | Erreur absolue moyenne (0-10) |
| RMSE | 2.5448 | Erreur quadratique moyenne |
| R² | -0.1424 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5008 | 0.500 |
| PR-AUC | 0.4162 | 0.414 |
| Sensitivity (TPR) | 0.3471 | 0.500 |
| Specificity (TNR) | 0.6619 | 0.500 |
| PPV (Precision) | 0.4203 | — |
| NPV | 0.5894 | — |
| Balanced Accuracy | 0.5045 | 0.500 |
| MCC | 0.0094 | 0.000 |
| G-Mean | 0.4793 | 0.500 |
| F1 macro | 0.5019 | 0.500 |
| LR+ | 1.027 | >10 = très utile |
| LR− | 0.986 | <0.1 = très utile |
| Cohen κ | 0.0093 | 0.000 |
| Brier Score | 0.2775 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5073 | [0.4918, 0.5213]  — |
| F1 macro | 0.4884 | [0.4766, 0.4983]  — |
| Sensitivity | 0.1393 | [0.1247, 0.1528]  — |
| Specificity | 0.8695 | [0.8607, 0.8775]  — |
| MCC | 0.0116 | [-0.0115, 0.0340]  — |
| R² | -0.1422 | [-0.1602, -0.1254]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.1424 | p=0.3920 | ❌ ns |
| AUC ROC | 0.5076 | p=0.1580 | ❌ ns |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.1342 | < 0.05 |
| MCE | 0.6182 | < 0.10 |
| Brier Score | 0.2291 | < 0.20 |
| Log-Loss | 0.6696 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | +0.6662 | proche 0 = pas de biais systématique |
| LoA lower | -4.1479 | limite inférieure d'accord |
| LoA upper | +5.4804 | limite supérieure d'accord |
| LoA width | ±4.8142 | < ±2 pts : excellent |
| % dans LoA | 97.0% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0000 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.6774 | 1.6822 | 248.4% | 🔴 unstable |
| AUC ROC | 0.5098 | 0.0497 | 9.8% | 🟢 stable |
| MAE | 2.1575 | 0.4956 | 23.0% | 🟡 moderate |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.5076 |
| CI 95% | [0.4936, 0.5216] |
| p-value | 0.289823 |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-22 00:30*
