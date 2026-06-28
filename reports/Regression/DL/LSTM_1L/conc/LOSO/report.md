# NeuroCap — Rapport Professionnel de Performance
**Target :** `conc`  |  **Modèle :** `LSTM_1L`  |  **Exp :** `LOSO`  |  **Date :** 2026-06-13 06:15


> 🔴 **Deployment Readiness Score : 27.4/100 — NOT READY — Ne pas déployer**


## Niveau 1 — Métriques Cliniques


### Régression

| Métrique | Valeur | Interprétation |
|---|---|---|
| MAE | 2.6021 | Erreur absolue moyenne (0-10) |
| RMSE | 3.1559 | Erreur quadratique moyenne |
| R² | -0.0382 | 1=parfait, 0=moyenne, <0=pire |

### Classification Binée (Low:0-5 / High:5-10)

| Métrique | Valeur | Baseline aléatoire |
|---|---|---|
| AUC ROC | 0.5821 | 0.500 |
| PR-AUC | 0.5667 | 0.515 |
| Sensitivity (TPR) | 0.4434 | 0.500 |
| Specificity (TNR) | 0.6449 | 0.500 |
| PPV (Precision) | 0.5702 | — |
| NPV | 0.5217 | — |
| Balanced Accuracy | 0.5442 | 0.500 |
| MCC | 0.0901 | 0.000 |
| G-Mean | 0.5347 | 0.500 |
| F1 macro | 0.5378 | 0.500 |
| LR+ | 1.249 | >10 = très utile |
| LR− | 0.863 | <0.1 = très utile |
| Cohen κ | 0.0877 | 0.000 |
| Brier Score | 0.3019 | < 0.20 objectif |

## Niveau 2 — Intervalles de Confiance (Bootstrap 95%)

| Métrique | Valeur | CI 95% | Significatif |
|---|---|---|
| AUC ROC | 0.5821 | [0.5540, 0.6092]  ✅ |
| F1 macro | 0.5380 | [0.5128, 0.5654]  ✅ |
| Sensitivity | 0.4436 | [0.4099, 0.4786]  — |
| Specificity | 0.6453 | [0.6114, 0.6785]  — |
| MCC | 0.0908 | [0.0422, 0.1430]  — |
| R² | -0.0406 | [-0.0966, 0.0204]  — |

### Tests de Permutation

_Tests de permutation non calculés_


## Niveau 3 — Qualité Clinique & Incertitude


### Calibration

| Métrique | Valeur | Objectif |
|---|---|---|
| ECE | 0.2216 | < 0.05 |
| MCE | 0.3517 | < 0.10 |
| Brier Score | 0.3019 | < 0.20 |
| Log-Loss | 1.0457 | minimiser |

### Bland-Altman (Accord Clinique)

| Métrique | Valeur | Interprétation |
|---|---|---|
| Biais | -0.1742 | proche 0 = pas de biais systématique |
| LoA lower | -6.3525 | limite inférieure d'accord |
| LoA upper | +6.0040 | limite supérieure d'accord |
| LoA width | ±6.1783 | < ±2 pts : excellent |
| % dans LoA | 96.7% | ≥ 95% requis |
| Accord clinique | ✅ OUI |  |

### ICC (Intraclass Correlation)

| ICC(2,1) | 0.0713 | insufficient (<0.50) |

## Niveau 4 — Robustesse & Stabilité


### Stabilité LOSO (Coefficient de Variation)

| Métrique | Moyenne | Std | CV% | Interprétation |
|---|---|---|
| R² | -0.0700 | 0.3318 | 474.1% | 🔴 unstable |
| AUC ROC | 0.5869 | 0.1153 | 19.6% | 🟡 moderate |
| MAE | 2.5954 | 0.3974 | 15.3% | 🟡 moderate |

**Stability Score global : 55.0/100 (unstable)**


## Niveau 5 — Déploiement Réglementaire


### Score de Déployabilité Commerciale

| Critère | Score (0-100) | Poids |
|---|---|---|
| Performance AUC | 41.1 | 25% |
| Significativité (p-value) | 50.0 | 15% |
| Stabilité (CV) | 0.0 | 15% |
| Calibration (ECE) | 0.0 | 15% |
| Accord clinique (LoA) | 0.0 | 10% |
| Fiabilité ICC | 0.0 | 10% |
| CI 95% étroit | 96.6 | 10% |

### **SCORE TOTAL : 27.4/100**

### **VERDICT : NOT READY — Ne pas déployer**


## Contexte & Recommandations

| Conditions | Valeur |
|---|---|
| Nb électrodes | 1 (FP2 — préfrontal) |
| Protocole validation | LOSO cross-sujet (strict) |
| Budget commercial | $100,000 |
| Usage recommandé | Aide à la décision (non diagnostic autonome) |


🔴 **Performance insuffisante. Passer au Deep Learning (DANN/TL).**


---
*Rapport généré automatiquement par NeuroCap metrics_professional.py — 2026-06-13 06:15*
