# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `CNN_GRU_Att`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-14 04:09


> 🔴 **Deployment Readiness Score : 33.7/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.4484 | Erreur absolue moyenne (0-10) |
| RMSE | 3.0697 | Erreur quadratique moyenne |
| R² | 0.0177 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.6323 | 0.500 |
| PR-AUC | 0.5956 | 0.515 |
| Sensitivity (TPR) | 0.5907 | 0.500 |
| Specificity (TNR) | 0.5986 | 0.500 |
| PPV (Precision) | 0.6099 | — |
| NPV | 0.5792 | — |
| Balanced Accuracy | 0.5946 | 0.500 |
| MCC | 0.1892 | 0.000 |
| G-Mean | 0.5946 | 0.500 |
| F1 macro | 0.5944 | 0.500 |
| LR+ | 1.471 | >10 = très utile |
| LR− | 0.684 | <0.1 = très utile |
| Cohen κ | 0.1891 | 0.000 |
| Brier Score | 0.2967 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.6322 | [0.6038, 0.6588]  ✅ |
| F1 macro | 0.5939 | [0.5684, 0.6193]  ✅ |
| Sensitivity | 0.5904 | [0.5566, 0.6279]  — |
| Specificity | 0.5981 | [0.5581, 0.6321]  — |
| MCC | 0.1885 | [0.1368, 0.2392]  — |
| R² | 0.0168 | [-0.0487, 0.0782]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2222 | < 0.05 |
| MCE | 0.3874 | < 0.10 |
| Brier Score | 0.2967 | < 0.20 |
| Log-Loss | 1.0645 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1906 | proche 0 = pas de biais systématique |
| LoA lower | -6.1978 | limite inférieure d'accord |
| LoA upper | +5.8166 | limite supérieure d'accord |
| LoA width | ±6.0072 | < ±2 pts : excellent |
| % dans LoA | 94.8% | ≥ 95% requis |
| Accord clinique | ⚠️ NON |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0985 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0117 | 0.2603 | 2232.7% | 🔴 unstable |
| AUC ROC | 0.6326 | 0.0970 | 15.3% | 🟡 moderate |
| MAE | 2.4534 | 0.4204 | 17.1% | 🟡 moderate |

**Stability Score global : 83.8/100 (excellent)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 66.1 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 96.7 | 10% |

### **SCORE TOTAL : 33.7/100**

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
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-14 04:09*
