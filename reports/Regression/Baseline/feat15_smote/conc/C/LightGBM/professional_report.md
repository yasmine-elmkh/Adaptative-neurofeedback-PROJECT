# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LightGBM`  |  **Exp :** `C`  |  **Date :** 2026-06-21 16:27


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5737 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0221 | Erreur quadratique moyenne |
| R² | 0.0480 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6169 | 0.500 |
| PR-AUC | 0.5956 | 0.517 |
| Sensitivity (TPR) | 0.5424 | 0.500 |
| Specificity (TNR) | 0.6216 | 0.500 |
| PPV (Precision) | 0.6050 | — |
| NPV | 0.5598 | — |
| Balanced Accuracy | 0.5820 | 0.500 |
| MCC | 0.1644 | 0.000 |
| G-Mean | 0.5807 | 0.500 |
| F1 macro | 0.5805 | 0.500 |
| LR+ | 1.433 | >10 = très utile |
| LR− | 0.736 | <0.1 = très utile |
| Cohen κ | 0.1634 | 0.000 |
| Brier Score | 0.2902 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6169 | [0.6008, 0.6331]  ✅ |
| F1 macro | 0.5805 | [0.5668, 0.5955]  ✅ |
| Sensitivity | 0.5426 | [0.5213, 0.5625]  — |
| Specificity | 0.6215 | [0.6006, 0.6424]  — |
| MCC | 0.1644 | [0.1372, 0.1937]  — |
| R² | 0.0479 | [0.0218, 0.0756]  ✅ |

### Tests de Permutation

| Métrique | Observé | p-value | Significatif |
|---|---|---|
| R² | 0.0480 | p=0.0000 | ✅ p<0.05 |
| AUC ROC | 0.6169 | p=0.0000 | ✅ p<0.05 |

## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2048 | < 0.05 |
| MCE | 0.3536 | < 0.10 |
| Brier Score | 0.2902 | < 0.20 |
| Log-Loss | 0.8916 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0284 | proche 0 = pas de biais systématique |
| LoA lower | -5.9521 | limite inférieure d'accord |
| LoA upper | +5.8953 | limite supérieure d'accord |
| LoA width | ±5.9237 | < ±2 pts : excellent |
| % dans LoA | 97.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1479 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0070 | 0.1987 | 2824.2% | 🔴 unstable |
| AUC ROC | 0.6128 | 0.0800 | 13.1% | 🟢 stable |
| MAE | 2.5883 | 0.2297 | 8.9% | 🟢 stable |

## Niveau 5 — Tests Statistiques Avancés (DCA & DeLong)


### AUC — Méthode DeLong (CI analytique exact)

| | Valeur |
|---|---|
| AUC | 0.6155 |
| CI 95% | [0.5987, 0.6323] |
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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-21 16:27*
