# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `SVR`  |  **Exp :** `A`  |  **Date :** 2026-06-21 15:57


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6105 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1289 | Erreur quadratique moyenne |
| R² | -0.0205 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6458 | 0.500 |
| PR-AUC | 0.7149 | 0.597 |
| Sensitivity (TPR) | 0.8541 | 0.500 |
| Specificity (TNR) | 0.3613 | 0.500 |
| PPV (Precision) | 0.6648 | — |
| NPV | 0.6254 | — |
| Balanced Accuracy | 0.6077 | 0.500 |
| MCC | 0.2500 | 0.000 |
| G-Mean | 0.5555 | 0.500 |
| F1 macro | 0.6028 | 0.500 |
| LR+ | 1.337 | >10 = très utile |
| LR− | 0.404 | <0.1 = très utile |
| Cohen κ | 0.2313 | 0.000 |
| Brier Score | 0.2779 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6094 | [0.5805, 0.6390]  ✅ |
| F1 macro | 0.5404 | [0.5141, 0.5674]  ✅ |
| Sensitivity | 0.4195 | [0.3822, 0.4549]  — |
| Specificity | 0.6817 | [0.6465, 0.7151]  — |
| MCC | 0.1047 | [0.0532, 0.1587]  — |
| R² | -0.0223 | [-0.0782, 0.0320]  — |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | -0.0205 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6096 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2690 | < 0.05 |
| MCE | 0.3886 | < 0.10 |
| Brier Score | 0.3239 | < 0.20 |
| Log-Loss | 1.0716 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0745 | proche 0 = pas de biais systématique |
| LoA lower | -6.2076 | limite inférieure d'accord |
| LoA upper | +6.0586 | limite supérieure d'accord |
| LoA width | ±6.1331 | < ±2 pts : excellent |
| % dans LoA | 96.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1394 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0769 | 0.2555 | 332.1% | 🔴 unstable |
| AUC ROC | 0.6543 | 0.1250 | 19.1% | 🟡 moderate |
| MAE | 2.6251 | 0.3206 | 12.2% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6096 |
| CI 95% | [0.5804, 0.6387] |
| p-value | 0.000000 |
| Significatif | ✅ OUI |

### Decision Curve Analysis (Utilité Clinique)

**Modèle cliniquement utile : ✅ OUI**

Zone d'utilité : seuil de décision entre 0.48 et 0.61


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 15:57*
