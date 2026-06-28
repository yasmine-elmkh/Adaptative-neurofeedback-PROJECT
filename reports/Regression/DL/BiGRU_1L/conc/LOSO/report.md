# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `BiGRU_1L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 17:26


> 🔴 **Deployment Readiness Score : 30.1/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.5534 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1329 | Erreur quadratique moyenne |
| R² | -0.0231 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6064 | 0.500 |
| PR-AUC | 0.5988 | 0.515 |
| Sensitivity (TPR) | 0.5389 | 0.500 |
| Specificity (TNR) | 0.5739 | 0.500 |
| PPV (Precision) | 0.5733 | — |
| NPV | 0.5395 | — |
| Balanced Accuracy | 0.5564 | 0.500 |
| MCC | 0.1128 | 0.000 |
| G-Mean | 0.5561 | 0.500 |
| F1 macro | 0.5559 | 0.500 |
| LR+ | 1.265 | >10 = très utile |
| LR− | 0.803 | <0.1 = très utile |
| Cohen κ | 0.1126 | 0.000 |
| Brier Score | 0.3013 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6062 | [0.5774, 0.6386]  ✅ |
| F1 macro | 0.5551 | [0.5322, 0.5825]  ✅ |
| Sensitivity | 0.5391 | [0.5059, 0.5751]  — |
| Specificity | 0.5725 | [0.5388, 0.6083]  — |
| MCC | 0.1116 | [0.0656, 0.1678]  — |
| R² | -0.0248 | [-0.0834, 0.0406]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2262 | < 0.05 |
| MCE | 0.4524 | < 0.10 |
| Brier Score | 0.3013 | < 0.20 |
| Log-Loss | 1.0494 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.0137 | proche 0 = pas de biais systématique |
| LoA lower | -6.1562 | limite inférieure d'accord |
| LoA upper | +6.1289 | limite supérieure d'accord |
| LoA width | ±6.1425 | < ±2 pts : excellent |
| % dans LoA | 95.8% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.1882 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0441 | 0.3161 | 716.0% | 🔴 unstable |
| AUC ROC | 0.6211 | 0.0654 | 10.5% | 🟢 stable |
| MAE | 2.5379 | 0.4052 | 16.0% | 🟡 moderate |

**Stability Score global : 57.8/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 53.2 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 92.5 | 10% |

### **SCORE TOTAL : 30.1/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🟡 **Performance modérée. Recommander collecte de données supplémentaires.**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 17:26*
